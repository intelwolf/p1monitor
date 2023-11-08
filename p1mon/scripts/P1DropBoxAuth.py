# run manual with ./P1DropBoxAuth

import argparse
import const
import crypto3
import dropbox_lib
import inspect
import logger
import os
import pwd
import sqldb
import sys
import filesystem_lib
import util

prgname   = 'P1DropBoxAuth'
config_db = sqldb.configDB()

# generates an url (-u) to get auth token or give a acces token -(t) based on an authorisation token from the dropbox website.
# beware the url generated auth token can only be used ONCE to generate a access token!
# "ERROR" when bad things happen, inspect logfile.

def Main(argv): 

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )


    parser = argparse.ArgumentParser( add_help=False ) # suppress default UK help text
    parser = argparse.ArgumentParser( description = "-t <token> ,-u (geef authenticatie url) of -d wis tijdelijke bestand." )

    parser.add_argument('-t', '--token',      required=False )
    parser.add_argument('-u', '--url',        required=False, action='store_true' )
    parser.add_argument('-d', '--deletefile', required=False, action='store_true' )
    parser.add_argument('-a', '--addhyphen',  required=False, action='store_true' )

    args = parser.parse_args()
  
    flog.debug ( inspect.stack()[0][3]+": args " + str(args) )

    auth_flow = dropbox_lib.AUTHFLOW

    ###################################################
    # this is a fix if the token starts with a hyphen #
    ###################################################
    if args.addhyphen == True and args.token != None:
        args.token = "-" + args.token

    if args.token != None:
        flog.debug ( inspect.stack()[0][3]+": token gestart." )
        try:

            flog.debug ( inspect.stack()[0][3]+": cli token is = " + str( args.token ) )

            # open van config database
            try:
                config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
            except Exception as e:
                flog.critical(inspect.stack()[0][3]+": database niet te openen(2)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
                sys.exit(1)
            flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

            flog.debug ( inspect.stack()[0][3]+": cli token =" + str(args.token) )

            oauth_result = auth_flow.finish( args.token )

            flog.debug ( inspect.stack()[0][3]+": oauth_result = " + str(oauth_result) )
            flog.debug ( inspect.stack()[0][3]+": oauth_result.access_token  = " + str(oauth_result.access_token) )
            flog.debug ( inspect.stack()[0][3]+": oauth_result.refresh_token = " + str(oauth_result.refresh_token) )

            access_token_crypt  = crypto3.p1Encrypt( str(oauth_result.access_token),  dropbox_lib.CRYPT_KEY_ACCESS  )
            refresh_token_crypt = crypto3.p1Encrypt( str(oauth_result.refresh_token), dropbox_lib.CRYPT_KEY_REFRESH )

            flog.debug ( inspect.stack()[0][3]+": oauth_result.access_token_crypt  = " + str( access_token_crypt ) )
            flog.debug ( inspect.stack()[0][3]+": oauth_result.refresh_token_crypt = " + str( refresh_token_crypt ) )

            config_db.strset( access_token_crypt,  47,  flog )
            config_db.strset( refresh_token_crypt, 170, flog )

            print ( 'OK' )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": authenticatie gefaald melding:"+str(e.args[0])+ ". Is het authenticatie token al niet een keer gebruikt?")
            print ('ERROR')
            flog.error("Programma gestopt.")
            sys.exit(1)

    if args.url == True:
        flog.debug ( inspect.stack()[0][3]+": redirect url gestart." )
        try:
            print ( auth_flow.start() )
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": url generatie gefaald melding:"+str(e.args[0]))
            print ('ERROR')    
        return

    flog.info("Programma gestopt.")
    sys.exit(0)

def remove_url_redirect_file( filePath = None ):
    try:
        if os.path.exists(filePath):
            os.remove( filePath )
            flog.debug (inspect.stack()[0][3]+": bestand  " + filePath + " gewist" )
    except Exception as e:
        flog.warning(inspect.stack()[0][3]+": onverwacht fout: " + str(e.args[0]) )


#-------------------------------
if __name__ == "__main__":
    try:
        logfile = const.DIR_FILELOG + prgname + ".log"
        flog = logger.fileLogger( logfile, prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        # never set this on
        flog.consoleOutputOn( False )

        # try to set rights, this may fail when run by www-data
        # that is not a problem
        try:
            filesystem_lib.set_file_permissions( filepath=logfile, permissions='664' )
        except:
            pass
        try:
            filesystem_lib.set_file_owners( filepath=logfile )
        except:
            pass

    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(10) #  error: no logging check file rights

    Main(sys.argv[1:])
