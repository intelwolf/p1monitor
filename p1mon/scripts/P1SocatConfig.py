# run manual with ./P1SocatConfig

import argparse
import const
import filesystem_lib
import inspect
import logger
import os
import pwd
import sqldb
import signal
import sys
import socat_lib

# programme name.
prgname = 'P1SocatConfig'

config_db    = sqldb.configDB()
rt_status_db = sqldb.rtStatusDb()

def Main( argv ):

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument( '-e', '--enable', 
        required=False,
        action="store_true",
        help="activeer de socat service." )
    
    parser.add_argument( '-d', '--disable',
        required=False,
        action="store_true",
        help="deactiveer de socat service." )
    
    parser.add_argument( '-st', '--succestimestamp',
        required=False,
        action="store_true",
        help="schrijf de succesvolle start timestamp naar de status database." )
    
    parser.add_argument( '-ft', '--failtimestamp',
        required=False,
        action="store_true",
        help="schrijf de timestamp van het falen naar de status database." )
    
    parser.add_argument( '-s', '--status',
        required=False,
        action="store_true",
        help="scontroleer de status en update de status database." )

    args = parser.parse_args()

    ###################################
    # init stuff                      #
    ###################################

    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3] + ": database tabel " + const.DB_CONFIG_TAB + " succesvol geopend.")

    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(2)." + const.FILE_DB_STATUS + ") melding:" + str(e.args[0]))
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_STATUS_TAB + " succesvol geopend.")

    if args.enable == True:
        try:
            flog.info( "enable gestart" )
            socat = socat_lib.Socat(statusdb=rt_status_db, configdb=config_db, flog=flog)
            socat.enable_service()
        except Exception as e:
            flog.critical( inspect.stack()[0][3]+": socat service was niet te activeren " + str(e.args[0]))
            sys.exit(1)
        flog.info( inspect.stack()[0][3] + ": socat service succesvol gestart." )
        sys.exit(0)


    if args.disable == True:
        try:
            flog.info( "disable gestart" )
            socat = socat_lib.Socat( statusdb=rt_status_db, configdb=config_db, flog=flog )
            socat.disable_service()
        except Exception as e:
            flog.critical( inspect.stack()[0][3]+": socat service was niet te deactiveren " + str(e.args[0]))
            sys.exit(1)
        flog.info( inspect.stack()[0][3] + ": socat service succesvol gestopt." )
        sys.exit(0)


    if args.succestimestamp == True:
        try:
            flog.info( "succestimestamp gestart" )
            socat = socat_lib.Socat( statusdb=rt_status_db, configdb=config_db, flog=flog )
            socat.set_succes_timestamp()
        except Exception as e:
            flog.critical( inspect.stack()[0][3]+": socat succesvolle start timestamp niet naar status database weg te schrijven" + str(e.args[0]))
            sys.exit(1)
        flog.info( inspect.stack()[0][3] + ": socat succesvolle start timestamp naar status database geschreven." )
        sys.exit(0)


    flog.warning( inspect.stack()[0][3] + ": geen commandline opties opgegeven. " )
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
