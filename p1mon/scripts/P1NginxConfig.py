# run manual with ./P1NginxConfig

import argparse
import base64
import const
import crontab
import crypto3
import filesystem_lib
import glob
import inspect
import json
import listOfPidByName
import logger
import nginx_lib
import os
import pwd
import pathvalidate.argparse
import sqldb
import signal
import subprocess
import sys
import random
import tempfile
import util
import network_lib
import process_lib
import makeLocalTimeString

LETSENCRYPY_TAG = 'LetsEncrypt'
NGINX_TMP_EXT   = '_nginx.tmp'

base_443 =\
"""
# 1m is 1 megabyte storage for buffer and rate is request per second.
limit_req_zone $binary_remote_addr zone=apilimit:1m rate=5r/s; 

server {

###P1HEADER###

    # config to enable HSTS(HTTP Strict Transport Security)
    add_header Strict-Transport-Security 'max-age=63072000; includeSubdomains;' always;

    # Content Security Policy (CSP)
    add_header Content-Security-Policy "default-src 'none'; frame-src 'none'; frame-ancestors 'none';" always;

    # X-XSS-Protection
    add_header X-XSS-Protection "1; mode=block" always;

    # X-Frame-Options
    add_header X-Frame-Options "SAMEORIGIN" always;
    #add_header X-Frame-Options "DENY" always;

    # X-Content-Type-Options
    add_header X-Content-Type-Options nosniff always;

    # Referrer-Policy
    add_header Referrer-Policy "strict-origin" always;

    listen 443 ssl;

    server_name ###FQDN###;
    ssl_certificate     /etc/letsencrypt/live/###FQDN###/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/###FQDN###/privkey.pem;

    default_type application/json;
 
    location = /authorize_apikey {

        internal; if ( $api_realm = "" ) {
           return 403; # Forbidden
        }

        if ( $http_x_apikey = "" ) {
           return 401; # Unauthorized
        }

        return 204;
    }

    ##########################################
    # API aanpassingen                       # 
    # burst means buffer/queue n request     #
    # before returning an error 503          # 
    ##########################################
    location /api/ {

        limit_req zone=apilimit burst=5 nodelay; 

        include proxy_params; 

        if ($request_method = 'OPTIONS') { 
            add_header Access-Control-Allow-Headers "X-APIkey, 
            Authorization";
        }

        satisfy any; 

        auth_request /authorize_apikey; limit_except OPTIONS { 
            auth_basic "Restricted API ($api_realm)";

        }

        proxy_pass http://127.0.0.1:10721;
    }

    ##########################################
    # redirect on root request               #
    ##########################################
    location / { 
        return 404;
    }

}
"""

base_80 =\
""" 
server {

###P1HEADER###

    # X-XSS-Protection
    add_header X-XSS-Protection "1; mode=block" always;

    # X-Frame-Options
    add_header X-Frame-Options "SAMEORIGIN" always;

    # X-Content-Type-Options
    add_header X-Content-Type-Options nosniff always;

    # Referrer-Policy
    add_header Referrer-Policy "strict-origin" always;


###80REDIRECT###

    proxy_cache nginx_cache;

    listen 80;

    root /p1mon/www;
    index index.php index.html index.htm;

    server_name _;

    location / {
        # First attempt to serve request as file, then fastcgi_cache_lock on; # as directory, then fall back to displaying a 404.
        try_files $uri $uri/ =404;
    }

    ############################################
    # pass PHP scripts to FastCGI server       #
    ############################################
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_read_timeout 305;
    }

    ##########################################
    # API aanpassingen                       #
    ##########################################
    location /api/ {
        include proxy_params;
        proxy_pass http://127.0.0.1:10721;
    }

    ##########################################
    # cache aanpassingen                     #
    ##########################################
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        add_header Cache-Control "no-cache";
    }
}
"""

#########################################
# tag name to use is ###FQDN###         #
#########################################
base_80_redirect =\
"""
    #############################################
    # redirect http request from the internet   #
    # to the https processing. when the request #
    # is from the router do a redirect unless   #
    # it is een LetsEncrypt request then don't  #
    # redirect.                                 #
    #############################################

    # when set to 1 do a http to https redirect.
    set $redirect 0;

    #if from the gateway it is internet traffic.
    if ( ###REDIRECTMAP### ) {
        set $redirect 1;
    }

    # request from letsencrypt are not redirected to https
    # cancel any previous set redirects.
    if ( $uri ~ "^(.*)/(.well-known/acme-challenge)(.*)" ){
        set $redirect 0;
    }

    # http to https redirect
    if ( $redirect ) {
        return 307 https://###FQDN###;
    }
"""

# programme name.
prgname = 'P1NginxConfig'

config_db    = sqldb.configDB()
rt_status_db = sqldb.rtStatusDb()

def Main( argv ): 

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument( '-ac', '--activatecert', 
        required=False,
        action="store_true",
        help="maak een Lets Encrypt certificaat aan" )

    parser.add_argument( '-arn', '--autorenewon', 
        required=False,
        action="store_true",
        help="activeer het automatisch updaten van certificaten." )
    
    parser.add_argument( '-arf', '--autorenewoff', 
        required=False,
        action="store_true",
        help="deactiveer het automatisch updaten van certificaten." )

    parser.add_argument( '-at', '--apitokens',
        required=False,
        action="store_true",
        help="configureerde de API tokens, uit de configuratie database." )

    parser.add_argument( '-ci', '--certinfo',
        required=False,
        action="store_true",
        help="geeft de certificaat informatie weer en update de status database." )

    parser.add_argument( '-ch', '--createhttpconfigfile', 
        type=pathvalidate.argparse.sanitize_filepath_arg,
        required=False,
        help="schrijft een http config bestand naar het opgegeven path bv: /etc/nginx/sites-enabled/p1mon_80" )

    parser.add_argument( '-dc', '--deactivatecert', 
        required=False,
        action="store_true",
        help="verwijder alle bestaande Lets Encrypt certificaten" )

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument( '-hs', '--https',
        required=False,
        action="store_true",
        help="maak een HTTP en HTTPS configuratie bestand aan en herstart de webserver." )
    
    parser.add_argument( '-ht', '--http',
        required=False,
        action="store_true",
        help="maak een basis configuratie bestand met alleen HTTP (fabrieks instelling) en herstart de webserver." )

    parser.add_argument( '-g', '--gateway',
        required=False,
        action="store_true",
        help="configureer het config file voor de router/gatway. Nodig voor http naar https redirection." )

    parser.add_argument( '-r', '--renewcerts',
        required=False,
        action="store_true",
        help="renew alle certificaten die aangemaakt zijn" )

    args = parser.parse_args()

    ###################################
    # init stuff                      #
    ###################################

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(2)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")


    if args.createhttpconfigfile != None:
        filename = str( args.createhttpconfigfile )
        flog.info( inspect.stack()[0][3] + ": http config bestand  " + str(  filename ) + " wordt aangemaakt:" )
        create_default_p80_config_file( filename )

    #######################################
    # display and log cert info and write #
    # expire date to status file          #
    #######################################
    if args.certinfo == True:
        if cert_info() == False:
            sys.exit(1)
        sys.exit(0)

    #######################################
    # update the certificates when needed #
    #######################################
    if args.renewcerts == True:

        flog.info( inspect.stack()[0][3] + ": update van certificaten gestart." )
        try:
            cmd = '/usr/bin/sudo certbot renew'
            proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr  = proc.communicate( timeout=60 )
            exit_code       = int( proc.wait() )
            if exit_code == 0: # last succesfull try to renew the certificate.
                rt_status_db.strset( makeLocalTimeString.makeLocalTimeString(), 120, flog )
                cert_info() # update database with how long the cert is valid.
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": update van certificaten gefaald " + str(e.args) )
            sys.exit( 1 )

        flog.info( inspect.stack()[0][3] + ": antwoord van LetsEncrypt: "  + str( stdout.decode('utf-8').replace('\n', ' ') ) )
        nginx_restart()  # needed to read in a new recieved cert after an true renew. 
        sys.exit( 0 )

    #################################################
    # change crontab to start auto update off certs #
    #################################################
    if args.autorenewon == True:
        if set_cert_auto_renew( mode='on', flog=flog  ) == False:
            flog.error(inspect.stack()[0][3] + ": Automatische update activeren gefaald." )
            sys.exit( 1 )
        sys.exit( 0 )

    #################################################
    # change crontab to stop auto update off certs  #
    #################################################
    if args.autorenewoff == True:
        if set_cert_auto_renew( mode='off', flog=flog ) == False:
            flog.error(inspect.stack()[0][3] + ": Automatische update deactiveren gefaald." )
            sys.exit( 1 )
        sys.exit( 0 )

    ######################################################
    # create cert, update nginx config and reload NGINX  #
    ######################################################
    if args.activatecert == True:

        fqdn = None
        try:
            _id, fqdn, _label = config_db.strget( 150, flog )
            if len( fqdn.strip() ) == 0:
                raise Exception( "geen domain naam ingesteld." )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": FQDN (domain naam) is niet te lezen of niet gezet: " + str(e.args) )
            sys.exit(1) # things went wrong.

        email = None
        try:
            _id, email, _label = config_db.strget( 159, flog )
            if len( email.strip() ) == 0:
                raise Exception("geen email ingsteld voor LetsEncrypt!")
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": e-mail is niet te lezen of niet gezet: " + str(e.args) )
            sys.exit(1) # things went wrong.

        certbot_exit_code = 0
        try:
            #cmd = '/usr/bin/sudo certbot certonly -n --email '+ email + ' --agree-tos --no-eff-email --webroot -w /p1mon/www -d ' + fqdn
            cmd = '/usr/bin/sudo certbot certonly -v -n --email '+ email + ' --agree-tos --no-eff-email --webroot -w /p1mon/www/ -d ' + fqdn
            proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr  = proc.communicate( timeout=60 )
            certbot_exit_code = int( proc.wait() )
        except Exception as e:
            if stderr != None:
                flog.critical( inspect.stack()[0][3] + ": creatie van certificaat voor " + fqdn + " gefaald " +\
                    str( e.args)  + " fout melding " + str( stderr.decode('utf-8').replace('\n', ' ') ))

            sys.exit( 1 )

        flog.info( inspect.stack()[0][3] + ": antwoord van LetsEncrypt: "  + str( stdout.decode('utf-8').replace('\n', ' ') ) )

        ###############################################
        # set nginx config files with new certifcate  #
        # and reload NGINX                            #
        ###############################################
        if certbot_exit_code == 0: # only make change after en succesfull cerbot run.
            set_nginx_https_config()
       
        # normal exit
        sys.exit(0)

    ######################################################
    # delete cert, update nginx config and reload NGINX  #
    ######################################################
    if args.deactivatecert == True:

        fqdn_set = set() # set has unique values.
        try:
            cmd = '/usr/bin/sudo certbot certificates'
            proc = subprocess.Popen([ cmd ],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
            buf = proc.stdout.readlines()
            
            for item in buf: 
                value = item.decode('utf-8').strip()
                if value.find('Domains:') == 0:
                    #print( item.split()[1].decode('utf-8') )
                    fqdn_set.add( item.split()[1].decode('utf-8').strip() )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": certifcaat is niet te lezen of niet gezet: " + str(e.args) )
            sys.exit(1) # things went wrong.

        for fqdn in fqdn_set:
            #print ( fqdn )
            try:
                cmd = '/usr/bin/sudo certbot delete -n --cert-name ' + fqdn
                proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout, stderr  = proc.communicate( timeout=60)
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": verwijderen van het certificaat voor " + fqdn + "gefaald " + str(e.args) )

            flog.info( inspect.stack()[0][3] + ": antwoord van LetsEncrypt: "  + str( stdout.decode('utf-8').replace('\n', ' ') ) ) 

        
        if ( len(fqdn_set) == 0 ):
             flog.info( inspect.stack()[0][3] + ": geen geïnstalleerde certificaten gevonden." ) 

        ###############################################
        # set nginx config file                       #
        # and reload NGINX also handles the exit code #
        ###############################################
        set_default_p80_config()

    ######################################################
    # maken default gateway nginx map file for https     #
    # redirect                                           #
    ######################################################
    if args.gateway == True:
        make_nginx_conf()

        if check_nginx_configuration( flog=flog ) == False:
            flog.error( inspect.stack()[0][3] + ": gateway config bestands fout, gestopt!")
            sys.exit(1)

        nginx_restart()
        sys.exit(0)

    ########################################################
    # add the api tokens to the nginx configuration file   #
    ########################################################
    if args.apitokens == True:

        try:
            _id, crypto_data, _label = config_db.strget( 160, flog )
            full_json = base64.standard_b64decode( crypto3.p1Decrypt( crypto_data,'20210731apikey') )
            flog.debug( inspect.stack()[0][3]+": decrypted json = " + full_json.decode( 'utf-8' ) )

            tokens = [] 
            json_dict = json.loads( full_json )
            for item in json_dict:
                tokens.append( item['TOKEN'] )

        except Exception as e:
            flog.warning(inspect.stack()[0][3] +": inlezen van versleutelde tokens, Fout=" + str(e.args[0]) )	

        flog.debug( inspect.stack()[0][3]+": API token list  = " + str( tokens ) )

        buffer  = generate_header_string()
        buffer +=  '\nmap $http_x_apikey $api_realm {\n'
        buffer += '    default "";\n'
        for token in tokens:
            buffer += '    "' + token + '" "p1mon_api";\n'
        buffer += '}\n'

        #print( buffer )
        flog.debug( inspect.stack()[0][3] + ": api tokens:\n" + str( buffer ) )

        if write_buffer( buffer=buffer, file=nginx_lib.APIKEYFILE, flog=flog ) == False:
            sys.exit(1) # things went wrong.

        if check_nginx_configuration( flog=flog ) == False:
            flog.error( inspect.stack()[0][3] + ": api tokens bestands fout, gestopt!")
            sys.exit(0)

        nginx_restart()
        sys.exit(0)

    ########################################################
    # reset all the setting to factory setting and remove  #
    # https (443) settings                                 #
    ########################################################
    if args.http == True:
        make_nginx_conf() 
        set_default_p80_config()

    ###########################################################
    # change port 80 and 443 config so the lets encrypt certs #
    # are used and the redirection for de UI is in place.     #
    ###########################################################
    if args.https == True:
        make_nginx_conf() 
        set_nginx_https_config()

    flog.info( inspect.stack()[0][3] + ": gestopt zonder uitgevoerde acties, geef commandline opties op." )
    sys.exit ( 1 ) # should be an error when there are no options given.


#######################################
# make a default config file for to   #
# dertime the default gateway         #
#######################################
def make_nginx_conf():

    try:
        result_list = network_lib.get_default_gateway()
       
        for rec in result_list:
            def_gateway = rec['ip4']
            break
        network_lib.is_valid_ip_adres( def_gateway )

    except Exception as e:
        flog.warning(inspect.stack()[0][3] +": gatway uitlezen gefaald, Fout=" + str( e.args[0]) )	
        def_gateway = "192.168.1.1" # some default value for common used routers. kind of failsave


    buffer  = generate_header_string()
    buffer +=  '\ngeo $gateway {\n'
    buffer +=  '    default 0;\n'
    buffer +=  '    ' + def_gateway + ' 1;\n'
    buffer +=  '}\n\n'
    buffer +=  '\ngeo $not_rfc1918 {\n'
    buffer +=  '    default 1;\n'
    buffer +=  '    192.168.0.0/16 0;\n'
    buffer +=  '    172.16.0.0/12 0;\n'
    buffer +=  '    10.0.0.0/8 0;\n'
    buffer +=  '}\n'

    flog.debug( inspect.stack()[0][3] + ": gateway:\n" + str( buffer ) )

    if write_buffer( buffer=buffer, file=nginx_lib.DIVMAPSFILE, flog=flog ) == False:
        sys.exit(1) # things went wrong.


#######################################
# display and log cert info and write #
# expirty date to status file         #
# return True = ok                    #
#######################################
def cert_info():

    try:
        cmd = '/usr/bin/sudo certbot certificates'
        proc = subprocess.Popen([ cmd ],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        buf = proc.stdout.readlines()
        
        for item in buf: 
            value = item.decode('utf-8').strip()
            if len(value) != 0: 
                flog.info( inspect.stack()[0][3] +  ": " + value )
                if value.find('Expiry') == 0:
                    date = item.split()[2].decode('utf-8')
                    time = item.split()[3].decode('utf-8')[0:8]
                    rt_status_db.strset( str(date) + " " + str(time) , 121, flog )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": certifcaat is niet te lezen of niet gezet: " + str(e.args) )
        return False # things went wrong.

    return True


###########################################################
# create default http config file                         #
###########################################################
def create_default_p80_config_file( filename=None ):

    buffer = base_80.replace("###80REDIRECT###", '' )
    buffer = buffer.replace('###P1HEADER###', generate_header_string() )

    flog.debug( inspect.stack()[0][3] + ": port 80 config:\n" + str( buffer ) )

    #print( buffer )
    if write_buffer( buffer=buffer, file=filename, flog=flog ) == False:
        sys.exit(1) # things went wrong.

    sys.exit(0)


###########################################################
# set default (works always) http config file             #
###########################################################
def set_default_p80_config():

    buffer = base_80.replace( '###80REDIRECT###', base_80_redirect )
    buffer = buffer.replace( '###REDIRECTMAP###', '$gateway')
    buffer = buffer.replace('###P1HEADER###', generate_header_string() )
    buffer = buffer.replace( '###FQDN###', "www.google.com" )
    #buffer = buffer.replace( '###FQDN###', "pt2109.duckdns.org" )

    flog.debug( inspect.stack()[0][3] + ": port 80 config:\n" + str( buffer ) )

    #print( buffer )
    if write_buffer( buffer=buffer, file=nginx_lib.P80FILE, flog=flog ) == False:
        sys.exit(1) # things went wrong.

    ##################################################################
    # remove https file if exists, not needed in default http mode   #
    ##################################################################
    #cmd = '/usr/bin/sudo rm -f ' + nginx_lib.P443FILE
    #os.system( cmd ) # may fail silent. # 1.8.0 upgrade
    process_lib.run_process( 
        cms_str='/usr/bin/sudo rm -f ' + nginx_lib.P443FILE,
        use_shell=True,
        give_return_value=False,
        flog=flog 
        )

    if check_nginx_configuration( flog=flog ) == False:
        flog.error( inspect.stack()[0][3] + ": configuratie bestand fout, gestopt!")
        sys.exit(0)

    nginx_restart()

    # normal exit
    sys.exit(0)
    

###########################################################
# add auto renew to crontab                               #
###########################################################
def set_cert_auto_renew( mode='on' , flog=None ):

    try:
        cron = crontab.CronTab(user='p1mon')
        cron.remove_all( comment=LETSENCRYPY_TAG )
        cron.write()
    except Exception as e:
        flog.error(inspect.stack()[0][3] +": crontab kon niet worden geopend, gestopt. Fout="+str(e.args[0]) )	
        return False

    if mode == 'on':
        try:
            job = cron.new(command='/p1mon/scripts/P1NginxConfig --renewcerts >/dev/null 2>&1', comment=LETSENCRYPY_TAG)
            # be nice to LetsEncrypt and not DDOS with P1 monitor.
            hour = random.randint(0,6)
            min  = random.randint(0,59)
            job.setall( str( min ) , str( hour ), '*', '*', '*')
            cron.write()
            flog.info( inspect.stack()[0][3] + ": certficaat vernieuwing wordt elke dag om " + str( '{:02d}'.format( hour )) + ":" + str( '{:02d}'.format( min )) + " uitgevoerd." )
        except Exception as e:
            flog.error(inspect.stack()[0][3] +": crontab update fout=" + str(e.args[0]) )
            return False

    flog.debug(inspect.stack()[0][3] +": succes" )
    return True


###########################################################
# change port 80 and 443 config so the lets encrypt certs #
# are used and the redirection for de UI is in place.     #
###########################################################
def set_nginx_https_config():

    fqdn = None
    try:
        _id, fqdn, _label = config_db.strget( 150, flog )
        if len( fqdn.strip() ) == 0:
            raise Exception("geen domain naam ingsteld.")
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": FQDN (domain naam) is niet te lezen of niet gezet: " + str(e.args) )
        sys.exit(1) # things went wrong.

    flog.info( inspect.stack()[0][3] + ": config files aanpassen met FQDN " + str( fqdn ) )

    #############
    # port 80   #
    #############

    # this is normaly the internal IP adres of your inet router
    def_gateway_router_ip = None
    rec_list = network_lib.get_default_gateway()
    for rec in rec_list:
        def_gateway_router_ip = rec['ip4']

    if def_gateway_router_ip == None:
        flog.critical( inspect.stack()[0][3] + ": default gateway netwerk niet gevonden. -> " + str(rec_list) )
        sys.exit(1) # things went wrong.

    buffer = base_80.replace( '###80REDIRECT###', base_80_redirect )
    buffer = buffer.replace( '###REDIRECTMAP###', '$not_rfc1918' )
    buffer = buffer.replace( '###P1HEADER###',    generate_header_string() )
    buffer = buffer.replace( '###FQDN###', fqdn )

    flog.debug( inspect.stack()[0][3] + ": port 80 config:\n" + str( buffer ) )

    if write_buffer( buffer=buffer, file=nginx_lib.P80FILE, flog=flog ) == False:
        flog.critical( inspect.stack()[0][3] + ": poort 80 bestand fout " )
        sys.exit(1) # things went wrong.

    ############
    # port 443 #
    ############
    buffer = base_443.replace( '###P1HEADER###', generate_header_string() )
    buffer = buffer.replace( '###FQDN###', fqdn  )

    flog.debug( inspect.stack()[0][3] + ": port 443 config:\n" + str( buffer ) )

    if write_buffer( buffer=buffer, file=nginx_lib.P443FILE, flog=flog ) == False:
        flog.critical( inspect.stack()[0][3] + ": poort 443 bestand fout " )
        sys.exit(1) # things went wrong.

    # restart the Nginx webserver
    nginx_restart()

    if check_nginx_configuration( flog=flog ) == False:
        flog.error( inspect.stack()[0][3] + ": configuratie bestand fout, failsave wordt gestart.")
        # activate failsave
        flog.warning( inspect.stack()[0][3] + ": standaard configuratie bestand gemaakt als failsave.")
        make_nginx_conf() 
        set_default_p80_config()
        
    # normal exit
    flog.info( inspect.stack()[0][3] + ": config files aanpassen met FQDN " + str( fqdn ) + " gereed.")
    sys.exit(0)


###########################################################################
# restart or reload the nginx server                                      #
# The reload command keeps the Nginx server running as it reloads updated #
# configuration files. If Nginx notices a syntax error in any of the      #
# configuration files, the reload is aborted and the server keeps running #
# based on old config files. Reloading is safer than restarting Nginx.    #
###########################################################################
def nginx_restart( mode='reload' ):

    if mode == 'restart':
        mode = 'restart'
    else:
        mode = 'reload'
        prg_name ='nginx'
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.info( inspect.stack()[0][3] + ": " + prg_name + " aantal gevonden Nginx processen = " + str(len(pid_list) ) )
        if len( pid_list ) < 1:
            flog.warning( inspect.stack()[0][3] + ": nginx is niet actief forceer een restart." )
            mode = 'restart'

    proc = subprocess.Popen(['/usr/bin/sudo', 'systemctl', mode, 'nginx'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _stderr = proc.communicate( timeout=10 )
    exit_code       = int( proc.wait() )

    if exit_code > 0:
        flog.error( inspect.stack()[0][3] + ": nginx " + mode + " gefaald -> "  + str( stdout.decode('utf-8').replace('\n', ' ') ) )
        return False

    flog.info( inspect.stack()[0][3] + ": nginx " + mode + " succesvol." )
    return True


########################################
# return false, is configuration error #
########################################
def check_nginx_configuration( flog=None ) -> bool:

    proc = subprocess.Popen(['/usr/bin/sudo', 'nginx', '-t'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _stderr = proc.communicate( timeout=10 )
    exit_code = int( proc.wait() )

    if exit_code > 0:
        flog.error( inspect.stack()[0][3] + ": nginx configuratie controle gefaald -> "  + str( stdout.decode('utf-8').replace('\n', ' ') ) )
        return False

    flog.info( inspect.stack()[0][3] + ": nginx configuratie controle succesvol." )
    return True

####################################################
# remove one or more temporary files               #
####################################################
def clean_tmp_files():
    files = glob.glob( tempfile.gettempdir() + '/*' + NGINX_TMP_EXT )
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": tijdelijk bestand " + f + " kan niet worden gewist: " + str(e.args) )
   
####################################################
# write config file and set file properties        #
# return true, all is well or false on a fatal or  #
# a disappointing result                           #
####################################################
def write_buffer( buffer=None, file=None, flog=None ) -> bool:

    # get rid of old tmp files if any.
    clean_tmp_files()

    tmp_file = filesystem_lib.generate_temp_filename() + NGINX_TMP_EXT # changed in 1.8.0 temp filename from lib

    try:

        if os.path.exists( file ):
            # os.system( '/usr/bin/sudo rm ' + file ) 1.8.0 upgrade
            process_lib.run_process( 
                cms_str='/usr/bin/sudo rm ' + file,
                use_shell=True,
                give_return_value=False,
                flog=flog 
            )
    
        ##################################################################
        # maken temporary file so we can move the file to root ownership #
        ##################################################################
        try:
            fp = open( tmp_file, 'w')
            fp.write( buffer )
            fp.close()
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": tijdelijk config file schrijf fout, gestopt(" + file + ") melding:" + str(e.args) )
            return False

        ##################################################################
        # move the file to the nginx folder and set ownership and rights #
        ##################################################################
        if move_file_for_root_user( source=tmp_file, destination=file ) == False:
            return False

    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": config file schrijf fout, gestopt(" + file + ") melding:" + str(e.args) )
        clean_tmp_files()
        return False
    
    return True


# let op gebruik Excepties en geen status return.
################################################################
# move a file to the destination and set the rights to 644 and #
# ownership to root:root                                       #
# true is ok, false is fatal error                             #
################################################################
def move_file_for_root_user( source=None, destination=None ) -> bool:
    #cmd = '/usr/bin/sudo mv -f ' + source + ' ' + destination
    #print ( cmd )
    #if os.system( cmd ) > 0:
    #    flog.critical( inspect.stack()[0][3] + ": verplaatsen van file error " + source  )
    #    return False

    r = process_lib.run_process( 
        cms_str = '/usr/bin/sudo mv -f ' + source + ' ' + destination,
        use_shell=True,
        give_return_value=True,
        flog=flog 
        )
    if ( r[2] ) > 0:
        flog.critical( inspect.stack()[0][3] + ": verplaatsen van file error " + source  )
        return False

    #cmd = '/usr/bin/sudo chmod 600 ' + destination
    #print( cmd )
    #if os.system( cmd ) > 0:
    #    flog.warning( inspect.stack()[0][3] + ": file eigenaarschap fout. " + destination  )

    r = process_lib.run_process( 
        cms_str = '/usr/bin/sudo chmod 600 ' + destination,
        use_shell=True,
        give_return_value=True,
        flog=flog 
        )
    if ( r[2] ) > 0:
        flog.warning( inspect.stack()[0][3] + ": file eigenaarschap fout. " + destination  )

    #cmd = '/usr/bin/sudo chown root:root ' + destination
    #print( cmd )
    #if os.system( cmd ) > 0:
    #    flog.warning( inspect.stack()[0][3] + ": file rechten fout. " + destination  )

    r = process_lib.run_process(
        cms_str = '/usr/bin/sudo chown root:root ' + destination,
        use_shell=True,
        give_return_value=True,
        flog=flog 
        )
    if ( r[2] ) > 0:
        flog.warning( inspect.stack()[0][3] + ": file rechten fout. " + destination  )

    return True 

"""  naar filesystem_lib verplaatst in versie 1.8.0
##########################################################
# generate a tempory file name in the default tmp folder #
##########################################################
def generate_temp_filename() -> str:
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return os.path.join(tempfile.gettempdir(), random_string)
"""

########################################################
# header timestamp string                              #
########################################################
def generate_header_string():
    str = \
'    ###############################\n\
    # Gegenereerd door P1-monitor.#\n\
    # op '+ util.mkLocalTimeString() + '      #\n'+\
'    ###############################\n'
    return str

########################################################
# close program when a signal is recieved.             #
########################################################
def saveExit(signum, frame):
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(0)

########################################################
# init                                                 #
########################################################
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        filepath = const.DIR_FILELOG + prgname + ".log"
        try:
            filesystem_lib.set_file_permissions( filepath=filepath, permissions='664' )
            filesystem_lib.set_file_owners( filepath=filepath, owner_group='p1mon:p1mon' )
        except:
            pass # don nothing as when this fails, it still could work
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname) 
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])
