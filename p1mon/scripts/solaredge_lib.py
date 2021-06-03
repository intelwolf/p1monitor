####################################################################
# solaredge lib based on solaredge version 0.0.4 from Bert Outtier #
####################################################################

import requests

########################################################
# constants                                            #
########################################################
BASEURL         = 'https://monitoringapi.solaredge.com'
REQUEST_TIMEOUT = 10  # in seconds
API_YEAR        = 'YEAR'
API_MONTH       = 'MONTH'
API_DAY         = 'DAY'
API_HOUR        = 'HOUR'
API_MINUTE      = 'QUARTER_OF_AN_HOUR'

# requests.get('http://www.google.com', timeout=(5, 14))
# https://requests.readthedocs.io/en/master/

class Solaredge:

    #######################################################
    # class init function                                 #
    #######################################################
    def __init__(self, site_token, debug=False):
        self.token = site_token
        self.debug = debug      # print debug info


    #######################################################
    # get Wh values for multiple sites                    #
    #######################################################
    def get_energy(self, 
        site_id_list, 
        start_date, 
        end_date, 
        time_unit='DAY'
        ):

        sites_id = ','.join(map(str, site_id_list )) 

        url = urljoin( BASEURL, "sites", sites_id , "energy")

        # this API does not support specific minute values, only
        # per day items. so YYYY--MM-DD is fine, YYYY-MM-DD hh:mm:ss 
        # does not work.

        params = {
            'api_key':      self.token,
            'startDate':    start_date[:10], # failsave on input slice
            'endDate':      end_date[:10],   # failsave on input slice
            'timeUnit':     time_unit
        }

        if self.debug:
            print("[*] DEBUG : ", url, params )
        
        r = requests.get( url, params, timeout=REQUEST_TIMEOUT )
        r.raise_for_status()
        return r.json()


    #######################################################
    # get a time period for one site                      #
    # site_id_list list of site identifiers               #
    # returns a JSON dict                                 #
    #######################################################
    def get_data_period(self, 
        site_id
        ):
        
        #sites_id = ','.join( map(str, site_id_list )) 

        url = urljoin(BASEURL, "site", site_id, "dataPeriod")

        params = {
            'api_key': self.token
        }

        if self.debug:
            print("[*] DEBUG : ", url, params )

        r = requests.get( url, params, timeout=REQUEST_TIMEOUT )
        r.raise_for_status()
        return r.json()


    #######################################################
    # get a list of all sites that relates to the token   #
    #######################################################
    def get_site_list(self, 
                    size=100, 
                    start_index=0, 
                    search_text="", 
                    sort_property="",
                    sort_order='ASC', 
                    status='Active,Pending' 
                    ):

        url = urljoin( BASEURL, "sites", "list")

        params = {
            'api_key': self.token,
            'size': size,
            'startIndex': start_index,
            'sortOrder': sort_order,
            'status': status
        }

        if search_text:
            params['searchText'] = search_text

        if sort_property:
            params['sortProperty'] = sort_property

        if self.debug:
            print("[*] DEBUG : ", url, params )
        r = requests.get( url, params, timeout=REQUEST_TIMEOUT )
        r.raise_for_status()
        return r.json()


###########################################################
# support functions                                       #
###########################################################

###########################################################
# Join terms together with forward slashes                #
###########################################################
def urljoin(*parts):
    # first strip extra forward slashes (except http:// and the likes) and
    # create list
    part_list = []
    for part in parts:
        p = str(part)
        if p.endswith('//'):
            p = p[0:-1]
        else:
            p = p.strip('/')
        part_list.append(p)
    # join everything together
    url = '/'.join(part_list)
    return url