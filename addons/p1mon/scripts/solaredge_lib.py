####################################################################
# SolarEdge lib for the Monitoring API V2.                         #
#                                                                  #
# Drop-in replacement for the V1 based solaredge_lib (originally   #
# based on solaredge 0.0.4 from Bert Outtier). V1 was retired by   #
# SolarEdge on 2026-11-03, requests now fail with HTTP 410.        #
#                                                                  #
# The public interface and the shape of the returned dicts are     #
# kept identical to the V1 version, so P1SolarEdgeReader.py and    #
# solaredge_shared_lib.py keep working with minimal changes.       #
#                                                                  #
# Credentials, V1 keys do NOT work with V2:                        #
#   * Homeowner -> Site Access (OAuth 2.0). Run                    #
#                  solaredge_v2_oauth_setup.py once, it writes     #
#                  OAUTH_FILE. The lib refreshes the token and     #
#                  stores the new (rotated) refresh token there.   #
#   * Installer -> Fleet Access API key, entered in the P1monitor  #
#                  API key field like before (sent as X-API-Key).  #
# If OAUTH_FILE exists it takes precedence over the API key.       #
####################################################################

import datetime
import json
import os
import tempfile
import time

import requests

try:
    from zoneinfo import ZoneInfo
except ImportError:  # python < 3.9
    ZoneInfo = None

########################################################
# constants                                            #
########################################################
BASEURL         = 'https://monitoringapi.solaredge.com/v2'
TOKEN_URL       = BASEURL + '/oauth2/token'
REQUEST_TIMEOUT = 20  # in seconds
OAUTH_FILE      = '/p1mon/data/solaredge_v2_oauth.json'

# Constants used by P1SolarEdgeReader.py, values are the V1 names, they
# are translated to V2 resolutions in RESOLUTION_MAP.
API_YEAR        = 'YEAR'
API_MONTH       = 'MONTH'
API_DAY         = 'DAY'
API_HOUR        = 'HOUR'
API_MINUTE      = 'QUARTER_OF_AN_HOUR'

RESOLUTION_MAP = {
    'YEAR'              : 'YEAR',
    'MONTH'             : 'MONTH',
    'DAY'               : 'DAY',
    'HOUR'              : 'HOUR',
    'QUARTER_OF_AN_HOUR': 'QUARTER_HOUR',   # renamed in V2
    'QUARTER_HOUR'      : 'QUARTER_HOUR',
}

# Maximum window per request in V2, kept slightly conservative where the
# documentation says "1 month" / "3 years".
MAX_WINDOW = {
    'QUARTER_HOUR': datetime.timedelta(hours=12),
    'HOUR'        : datetime.timedelta(hours=24),
    'DAY'         : datetime.timedelta(days=28),
    'MONTH'       : datetime.timedelta(days=1000),
    'YEAR'        : datetime.timedelta(days=3650),
}

# Every V2 call costs one credit and the Free tier allows 10 calls per
# minute, so calls are spaced. Set to 0 on a plan with a higher limit.
MIN_SECONDS_BETWEEN_CALLS = 6.5
MAX_RETRY_AFTER_SECONDS   = 120   # longer 429 waits (monthly quota) are raised, not slept
MAX_429_RETRIES           = 3

UNIT_TO_WH = { 'WH': 1.0, 'KWH': 1000.0, 'MWH': 1000000.0 }


class SolaredgeAuthError( Exception ):
    pass


def oauth_configured( oauth_file=None ):
    """True when an OAuth token file is present."""
    return os.path.isfile( oauth_file or OAUTH_FILE )


class Solaredge:

    #######################################################
    # class init function                                 #
    # site_token: Fleet Access API key, or None/'' when   #
    #             the OAuth file is used.                 #
    #######################################################
    def __init__( self, site_token=None, debug=False, oauth_file=None ):
        self.token       = site_token or ''
        self.debug       = debug      # print debug info
        self.oauth_file  = oauth_file or OAUTH_FILE
        self.oauth       = None       # dict with the OAuth data when in OAuth mode
        self._tz_cache   = {}         # site id -> ZoneInfo
        self._details    = {}         # site id -> site details dict
        self._last_call  = 0.0
        self.calls_made  = 0          # credits used by this object

        if oauth_configured( self.oauth_file ):
            self._load_oauth()
        elif not self.token:
            raise SolaredgeAuthError( "no Fleet Access API key and no OAuth file (" + self.oauth_file + ")" )


    #######################################################
    # OAuth helpers                                       #
    #######################################################
    def _load_oauth( self ):
        with open( self.oauth_file, 'r' ) as f:
            self.oauth = json.load( f )
        for key in ( 'client_id', 'client_secret', 'refresh_token' ):
            if not self.oauth.get( key ):
                raise SolaredgeAuthError( "OAuth file " + self.oauth_file + " misses '" + key + "'" )


    def _save_oauth( self ):
        # The refresh token is single use, the new one MUST be stored or the
        # next refresh fails. Write atomically and keep the file private.
        directory = os.path.dirname( self.oauth_file ) or '.'
        fd, tmp_path = tempfile.mkstemp( dir=directory, prefix='.solaredge_oauth_' )
        try:
            with os.fdopen( fd, 'w' ) as f:
                json.dump( self.oauth, f )
            os.chmod( tmp_path, 0o600 )
            os.replace( tmp_path, self.oauth_file )
        except Exception:
            if os.path.exists( tmp_path ):
                os.remove( tmp_path )
            raise


    def _refresh_access_token( self ):
        body = {
            'grant_type'   : 'refresh_token',
            'refresh_token': self.oauth['refresh_token'],
            'client_id'    : self.oauth['client_id'],
            'client_secret': self.oauth['client_secret'],
        }
        r = requests.post( TOKEN_URL, json=body, headers={ 'Accept': 'application/json' }, timeout=REQUEST_TIMEOUT )
        if r.status_code >= 400:
            raise SolaredgeAuthError( "OAuth token refresh failed (HTTP " + str( r.status_code ) +
                "). If the refresh token was unused for 14 days run solaredge_v2_oauth_setup.py again." )
        data = r.json()
        if not data.get( 'access_token' ):
            raise SolaredgeAuthError( "OAuth token refresh returned no access_token" )
        self.oauth['access_token'] = data['access_token']
        if data.get( 'refresh_token' ):
            self.oauth['refresh_token'] = data['refresh_token']
        expires_in = data.get( 'expires_in' )
        self.oauth['expires_at'] = ( time.time() + float( expires_in ) ) if expires_in else None
        self._save_oauth()


    def _auth_headers( self ):
        headers = { 'Accept': 'application/json' }
        if self.oauth is None:
            headers['X-API-Key'] = self.token
            return headers
        expires_at = self.oauth.get( 'expires_at' )
        if not self.oauth.get( 'access_token' ) or ( expires_at and time.time() >= float( expires_at ) - 120 ):
            self._refresh_access_token()
        headers['Authorization'] = 'Bearer ' + self.oauth['access_token']
        return headers


    #######################################################
    # one HTTP GET with pacing, 401 refresh and 429 wait  #
    #######################################################
    def _get( self, path, params=None ):
        url = BASEURL + '/' + path.lstrip('/')
        refreshed = False
        retries   = 0

        while True:
            wait = MIN_SECONDS_BETWEEN_CALLS - ( time.monotonic() - self._last_call )
            if wait > 0 and self.calls_made > 0:
                time.sleep( wait )

            headers = self._auth_headers()
            if self.debug:
                print( "[*] DEBUG : ", url, params )
            r = requests.get( url, params=params, headers=headers, timeout=REQUEST_TIMEOUT )
            self._last_call = time.monotonic()
            self.calls_made += 1

            if r.status_code == 401 and self.oauth is not None and not refreshed:
                refreshed = True
                self._refresh_access_token()
                continue

            if r.status_code == 429 and retries < MAX_429_RETRIES:
                retries += 1
                try:
                    retry_after = float( r.headers.get( 'Retry-After', 60 ) )
                except ValueError:
                    retry_after = 60.0
                if retry_after > MAX_RETRY_AFTER_SECONDS:
                    r.raise_for_status() # most likely the monthly credit quota is used up
                time.sleep( retry_after + 1 )
                continue

            r.raise_for_status()
            return r.json()


    #######################################################
    # site details, time zone and installation date       #
    #######################################################
    def _site_details( self, site_id ):
        if site_id not in self._details:
            self._details[site_id] = self._get( 'sites/' + str( site_id ) )
        return self._details[site_id]


    def _site_tz( self, site_id ):
        if site_id not in self._tz_cache:
            tz = None
            try:
                tz_name = self._site_details( site_id ).get( 'location', {} ).get( 'timezone' )
                if tz_name and ZoneInfo:
                    tz = ZoneInfo( tz_name )
            except Exception:
                tz = None
            if tz is None:
                tz = datetime.datetime.now().astimezone().tzinfo # local time of this machine
            self._tz_cache[site_id] = tz
        return self._tz_cache[site_id]


    #######################################################
    # get Wh values for multiple sites                    #
    # V2 has no bulk call, one request (series) per site  #
    # and per allowed time window.                        #
    # Returns the V1 structure:                           #
    # { 'sitesEnergy': { 'count': n, 'siteEnergyList': [  #
    #   { 'siteId': id, 'energyValues': { 'values': [     #
    #       { 'date': 'YYYY-MM-DD hh:mm:ss',              #
    #         'value': Wh or None } ] } } ] } }           #
    # 'date' is in the time zone of the site, like V1.    #
    #######################################################
    def get_energy( self,
        site_id_list,
        start_date,
        end_date,
        time_unit='DAY'
        ):

        resolution = RESOLUTION_MAP.get( time_unit )
        if resolution is None:
            raise ValueError( "unknown time_unit " + str( time_unit ) )

        site_list = list()

        for site_id in site_id_list:
            tz = self._site_tz( site_id )

            # V1 dates were inclusive, so end_date is the whole last day.
            start_local = datetime.datetime.strptime( start_date[:10], '%Y-%m-%d' ).replace( tzinfo=tz )
            end_local   = ( datetime.datetime.strptime( end_date[:10], '%Y-%m-%d' ) + datetime.timedelta( days=1 ) ).replace( tzinfo=tz )

            # no use to ask for the future, saves credits.
            now_local = datetime.datetime.now( tz )
            if end_local > now_local:
                end_local = now_local

            values = list()
            seen   = set()

            window_start = start_local.astimezone( datetime.timezone.utc )
            window_end   = end_local.astimezone( datetime.timezone.utc )
            step         = MAX_WINDOW[resolution]

            while window_start < window_end:
                chunk_end = min( window_start + step, window_end )
                params = {
                    'from'      : window_start.strftime( '%Y-%m-%dT%H:%M:%SZ' ),
                    'to'        : chunk_end.strftime(    '%Y-%m-%dT%H:%M:%SZ' ),
                    'resolution': resolution,
                    'unit'      : 'WH',
                }
                data = self._get( 'sites/' + str( site_id ) + '/energy', params )

                factor = UNIT_TO_WH.get( str( data.get( 'unit', 'WH' ) ).upper(), 1.0 )

                for item in data.get( 'values', [] ):
                    raw_ts   = item.get( 'timestamp' )
                    date_str = self._to_site_local_string( raw_ts, tz )
                    if date_str is None or raw_ts in seen:
                        continue # skip bad timestamps and the duplicate at a window border
                    seen.add( raw_ts ) # raw (UTC) key, the local time repeats once a year at the DST change.
                    value = item.get( 'value' )
                    values.append( { 'date': date_str, 'value': None if value is None else value * factor } )

                window_start = chunk_end

            values.sort( key=lambda v: v['date'] )
            site_list.append( { 'siteId': int( site_id ), 'unit': 'Wh', 'energyValues': { 'values': values } } )

        return { 'sitesEnergy': { 'count': len( site_list ), 'siteEnergyList': site_list } }


    @staticmethod
    def _to_site_local_string( timestamp, tz ):
        # V2 timestamps are ISO 8601. Convert to the local time of the site
        # as 'YYYY-MM-DD hh:mm:ss', the format V1 used.
        if not timestamp:
            return None
        try:
            dt = datetime.datetime.fromisoformat( str( timestamp ).replace( 'Z', '+00:00' ) )
        except ValueError:
            return None
        if dt.tzinfo is not None:
            dt = dt.astimezone( tz )
        return dt.strftime( '%Y-%m-%d %H:%M:%S' )


    #######################################################
    # get a time period for one site                      #
    # V2 has no dataPeriod, the installation date is      #
    # used as start date. Returns the V1 structure.       #
    #######################################################
    def get_data_period( self, site_id ):
        details = self._site_details( site_id )
        start   = str( details.get( 'installationDate' ) or '' )[:10]
        if not start:
            raise ValueError( "site " + str( site_id ) + " has no installationDate" )
        end = datetime.datetime.now( self._site_tz( site_id ) ).strftime( '%Y-%m-%d' )
        return { 'dataPeriod': { 'startDate': start, 'endDate': end } }


    #######################################################
    # get a list of all sites that relates to the token   #
    # Fleet Access: GET /sites. OAuth (Site Access) can   #
    # only see its own site, V2 has no list for that.     #
    # Returns the V1 structure.                           #
    #######################################################
    def get_site_list( self,
                    size=100,
                    start_index=0,
                    search_text="",
                    sort_property="",
                    sort_order='ASC',
                    status='Active,Pending'
                    ):

        if self.oauth is not None:
            site_id = self.oauth.get( 'site_id' )
            if not site_id:
                raise SolaredgeAuthError( "OAuth file has no site_id" )
            d = self._site_details( int( site_id ) )
            sites = [ d ]
        else:
            params = { 'page': start_index // max( size, 1 ) + 1, 'sites-in-page': max( 1, min( size, 1000 ) ) }
            if search_text:
                params['name'] = search_text
            sites = self._get( 'sites', params ).get( 'sites', {} ).get( 'site', [] )

        out = list()
        for s in sites:
            out.append( {
                'id'               : s.get( 'siteId' ),
                'name'             : s.get( 'name' ),
                'status'           : 'Active' if str( s.get( 'activationStatus', 'ACTIVE' ) ).upper() == 'ACTIVE' else 'Pending',
                'peakPower'        : s.get( 'peakPower' ),
                'installationDate' : s.get( 'installationDate' ),
                'location'         : s.get( 'location' ),
            } )
        return { 'sites': { 'count': len( out ), 'site': out } }
