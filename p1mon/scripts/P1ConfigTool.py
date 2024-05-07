# run manual with ./P1ConfigTool
import argparse
import const
import filesystem_lib
import inspect
import logger
import os
import pwd
import sqldb
import sys
import signal


prgname         = 'P1ConfigTool'
config_db       = sqldb.configDB()


def main(argv):

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument('-ri', '--readindex',
        required=False,
        help="lees waarde van het configuratie item aan de hand van de opgeven index." )
    
    parser.add_argument('-wi', '--writeindex',
        required=False,
        help="schrijf de waarde van het configuratie item aan de hand van de opgeven index, is afhankelijk van writevalue." )
    
    parser.add_argument('-wv', '--writevalue',
        required=False,
        help="schrijf de waarde van het configuratie item aan de hand van de opgeven index, is afhankelijk van writeindex." )

    args = parser.parse_args()
    
    ###################################
    # init stuff                      #
    ###################################

    try:
        config_db.init( const.FILE_DB_CONFIG, const.DB_CONFIG_TAB )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
  
    #######################################
    # processing args                     #
    #######################################
    if args.readindex != None:
        try:
            # index, flog
            _id, value, _label = config_db.strget( str(args.readindex), flog )
            print ("#", str(value) )
            sys.exit(0)
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": readindex " + str( e.args[0] ))
            sys.exit(1)

    if args.writeindex != None and args.writevalue != None:
        try:
            # value, index, flog
            config_db.strset( str(args.writevalue), str(args.writeindex) , flog )
            sys.exit(0)
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": writeindex " + str( e.args ))
            sys.exit(1)

    
    sys.exit(1) # somthing went wrong 


########################################################
# reset signals and close stuff                        #
########################################################
def saveExit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    print("SIGINT ontvangen, gestopt.")
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
        flog.consoleOutputOn( False )
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    main(sys.argv[1:])