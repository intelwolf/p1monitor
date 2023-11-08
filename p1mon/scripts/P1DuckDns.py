
# run manual with ./P1DuckDns

import argparse
import base64
import const
import crypto3
import inspect
import logger
import os
import pwd
import sqldb
import signal
import sys
import process_lib

# programme name.
prgname = 'P1DuckDns'

config_db = sqldb.configDB()

def Main( argv ): 

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument( '-u', '--update', 
        required=False, 
        action="store_true",
        help = "start de automatische update van publiek IP en DNS naam." )

    args = parser.parse_args()

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")


    ########################################################
    # update the local IP adres with the FQDN name from    #
    # the config database                                  #
    ########################################################
    if args.update == True:
        
        # read en decode the DuckDNS token
        try:
            _id, dynamic_dns,   _label = config_db.strget( 150, flog )
            _id, duckdns_token_encoded, _label = config_db.strget( 151, flog )

            #print ( duckdns_token_encoded )
            duckdns_token = base64.standard_b64decode( crypto3.p1Decrypt( duckdns_token_encoded, 'dckdckdns' )).decode('utf-8')

        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": configuratie gegevens fout (DuckDNS token) -> ." + str(e.args[0]) )
            sys.exit(1)

        # remove older status file when it exist.
        try:
            if os.path.exists( const.FILE_DUCKDNS_STATUS ):
                os.remove( const.FILE_DUCKDNS_STATUS )
        except Exception as e:
            flog.warning(inspect.stack()[0][3]+": status file " + const.FILE_DUCKDNS_STATUS + " probleem. " + str(e.args[0]) )

        #duckdns_token = duckdns_token + "x" 

        # execute the curl command to update the DuckDNS IP
        try:
            flog.debug(inspect.stack()[0][3]+": Parameters token=" + duckdns_token + " dns_name="  + dynamic_dns )

            cmd = 'echo url="https://www.duckdns.org/update?domains=' + dynamic_dns + '&token=' + duckdns_token + '&ip=" | curl -s -k -o ' +  const.FILE_DUCKDNS_STATUS + ' -K -'
            flog.debug (inspect.stack()[0][3]+": cmd = " + str(cmd ) )
            #if os.system( cmd ) > 0:
            #    flog.error(inspect.stack()[0][3]+" update gefaald")
            r = process_lib.run_process( 
                        cms_str = cmd,
                        use_shell=True,
                        give_return_value=True,
                        flog=flog 
             )
            if r[2] > 0:
                flog.error(inspect.stack()[0][3]+" update gefaald")

        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": update gefaald door -> " + str(e.args[0]) )
            sys.exit(1)

        # check if the command was excuted OK (KO) is not ok.
        try:
            f = open( const.FILE_DUCKDNS_STATUS, "r" )
            if f.mode == 'r':
                status =f.read().strip()
                if status == "OK":
                    flog.info(inspect.stack()[0][3]+": DNS naam: " +  dynamic_dns + " naar IP update is succesvol." )
                else:
                    flog.warning(inspect.stack()[0][3]+": DNS naam: " + dynamic_dns + " naar IP update is gefaald." )
            f.close()
        except Exception as e:
            flog.warning(inspect.stack()[0][3]+": status check probleem -> " + str(e.args[0]) )
            sys.exit(1)

        sys.exit(0)



    flog.warning(inspect.stack()[0][3]+": geen command line opties opgeven!" )
    sys.exit(1)


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
    global process_bg 
    try:
        os.umask( 0o002 )
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname)    
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])

