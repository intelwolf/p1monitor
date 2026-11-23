#!/usr/bin/env python3
####################################################################
# One time setup of SolarEdge Monitoring API V2 Site Access (OAuth) #
# for homeowners. Writes solaredge_lib.OAUTH_FILE (mode 600).       #
#                                                                   #
# Prepare (once):                                                   #
#  1. Sign in to https://developer.solaredge.com with your          #
#     mySolarEdge login and complete the developer profile (Free    #
#     tier is enough).                                              #
#  2. Create a Site Access application:                             #
#       Service      : Monitoring API                               #
#       Redirect URI : http://localhost:8080/oauth/callback         #
#       Scopes       : SITE_DATA (add DEVICE_DATA if you want it)   #
#     Copy the client id and the client secret (shown only once).   #
#                                                                   #
# Run:  ./solaredge_v2_oauth_setup.py --client-id YOUR_CLIENT_ID    #
#       [--owner p1mon]   (user that runs P1SolarEdgeReader)        #
####################################################################

import argparse
import getpass
import json
import os
import shutil
import sys
import time
from urllib.parse import parse_qsl, quote, urlencode, urlsplit

import requests

import solaredge_lib

AUTHORIZE_URL = 'https://connect.solaredge.com/authorize'
REDIRECT_URI  = 'http://localhost:8080/oauth/callback'


def main():
    p = argparse.ArgumentParser( description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter )
    p.add_argument( '--client-id', required=True )
    p.add_argument( '--scopes', default='SITE_DATA', help='space separated, default: SITE_DATA' )
    p.add_argument( '--redirect-uri', default=REDIRECT_URI, help='must match the application exactly' )
    p.add_argument( '--oauth-file', default=solaredge_lib.OAUTH_FILE )
    p.add_argument( '--owner', default=None, help='chown the token file to this user' )
    args = p.parse_args()

    secret = os.environ.get( 'SOLAREDGE_CLIENT_SECRET' ) or getpass.getpass( 'Client secret: ' )

    query = urlencode( { 'client_id': args.client_id, 'scope': args.scopes, 'redirect_uri': args.redirect_uri },
                       quote_via=quote ) # spaces as %20
    print( '\n1. Open this URL in a browser on any computer and approve access to your site:\n\n' + AUTHORIZE_URL + '?' + query )
    print( '\n2. The browser is then sent to ' + args.redirect_uri + ' which will show an error page,' )
    print( '   that is expected. Copy the FULL address from the address bar and paste it here.\n' )
    callback = input( 'Redirect URL: ' ).strip()

    params = dict( parse_qsl( urlsplit( callback ).query if '?' in callback or '://' in callback else callback.lstrip( '?' ) ) )
    if 'error' in params:
        sys.exit( 'Authorization failed: ' + params['error'] + ' ' + params.get( 'error_description', '' ) )
    code = params.get( 'code' )
    if not code:
        sys.exit( 'No code parameter found in the pasted URL.' )
    site_id = params.get( 'site_id' )

    r = requests.post( solaredge_lib.TOKEN_URL, headers={ 'Accept': 'application/json' }, timeout=20,
        json={ 'grant_type': 'authorization_code', 'code': code, 'client_id': args.client_id,
               'client_secret': secret, 'redirect_uri': args.redirect_uri } )
    if r.status_code >= 400:
        sys.exit( 'Token request failed (HTTP ' + str( r.status_code ) + '): ' + r.text[:300] )
    data = r.json()
    if not data.get( 'access_token' ) or not data.get( 'refresh_token' ):
        sys.exit( 'Token response did not contain an access and refresh token.' )

    content = {
        'client_id'    : args.client_id,
        'client_secret': secret,
        'access_token' : data['access_token'],
        'refresh_token': data['refresh_token'],
        'expires_at'   : time.time() + float( data['expires_in'] ) if data.get( 'expires_in' ) else None,
        'site_id'      : int( site_id ) if site_id and site_id.isdecimal() else None,
    }

    fd = os.open( args.oauth_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600 )
    with os.fdopen( fd, 'w' ) as f:
        json.dump( content, f )
    os.chmod( args.oauth_file, 0o600 )
    if args.owner:
        shutil.chown( args.oauth_file, user=args.owner )

    print( '\nSaved to ' + args.oauth_file + ' (site id ' + str( content['site_id'] ) + ').' )
    if content['site_id'] is None:
        print( 'WARNING: no site_id was in the redirect URL, add it to the file by hand.' )


if __name__ == '__main__':
    main()
