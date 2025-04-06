# run manual with ./P1SetTime

import argparse
import const
import datetime_lib
import filesystem_lib
import inspect
import logger
import os
import pwd
import signal
import sys
import process_lib

# programme name.
prgname = 'P1SetTime'

def Main( argv ):

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
    action='help', default=argparse.SUPPRESS,
    help='Set de tijd van het besturingssysteem.')

    parser.add_argument( '-i', '--internet', 
    required=False,
    action="store_true",
    help="Set tijd van besturingssysteem via het internet."
    )

    parser.add_argument( '-v', '--variatie', 
    required=False,
    help="Set tijd alleen als het verschil tussen de tijd van het besturingssysteem  groter is dan het opgeven aantal seconden"
    )

    args = parser.parse_args()
  
    if args.internet:
        time_set_is = set_internet_time( variance = args.variatie)
    	
        flog.info( inspect.stack()[0][3] + ": gereed, tijd succesvol aangepast naar " + (time_set_is))
        sys.exit(0)

    
    flog.info( inspect.stack()[0][3] + ": geen opties geselecteerd gereed.")


################################################
# set the system time with the date command    #
# get the time from the internet source        #
# if variance is set to not None only update   #
# when the time difference is larger then      #
# variance in seconds.                         #
################################################    
def set_internet_time( variance=None ):

    try:
        # get time from the internet
        inet_datetime_str, inet_datetime_utc = datetime_lib.get_inet_timestamp( flog=flog )
        flog.debug( inspect.stack()[0][3] + ": internet tijd is" + str(inet_datetime_str) )
        
        if variance != None:
            flog.debug( inspect.stack()[0][3] + ": verschil is tijd is gezet op " + str(int(variance)) )
            os_datetime_str, os_datetime_utc = datetime_lib.get_os_timestamp( flog=flog )

            if abs(inet_datetime_utc - os_datetime_utc) < int(variance):
                flog.info( inspect.stack()[0][3] + ": tijd niet aangepast, het verschil is te klein, variatie is ingesteld op " +str(variance) + " seconden.") 
                return os_datetime_str

        #set datetime 
        cmd = '/usr/bin/sudo /usr/bin/date -s "' + str(inet_datetime_str) + '"'
        r = process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog 
        )
        if r[2] > 0:
            flog.error( inspect.stack()[0][3] + cmd  + "  gefaald." )
            raise Exception("tijd zetten met date -s gefaald.") 

        os_datetime_str, _os_datetime_utc = datetime_lib.get_os_timestamp( flog=flog )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": fatale fout by het zetten van de tijd via het internet -> " + str(e))
        sys.exit(1)

    return os_datetime_str

########################################################
# close program when a signal is received.             #
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
