# run manual with ./P1Notifier

from typing import Counter
import const
import inspect
import logger
import os
import p1_port_shared_lib
import phase_shared_lib
import power_shared_lib
import pwd
import signal
import sqldb
import sys
import time
import util

prgname = 'P1Notifier'

rt_status_db        = sqldb.rtStatusDb()
config_db           = sqldb.configDB()
fase_db_min_max_dag = sqldb.PhaseMaxMinDB()
e_db_serial         = sqldb.SqlDb1()

def Main( argv ):
    my_pid = os.getpid()
    flog.info( "Start van programma met process id " + str( my_pid ) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    # open databases
    # open van status database
    try:
        rt_status_db.init( const.FILE_DB_STATUS,const.DB_STATUS_TAB )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_STATUS + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel: " + const.DB_STATUS_TAB + " succesvol geopend." )
   
    # open van config database
    try:
        config_db.init( const.FILE_DB_CONFIG, const.DB_CONFIG_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # open van fase database voor min/max waarden.
    try:
        fase_db_min_max_dag.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_MINMAX_DAG_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+" database niet te openen(3)." + const.FILE_DB_PHASEINFORMATION + ") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_FASE_MINMAX_DAG_TAB + " succesvol geopend.")

    # open van seriele database
    try:
        e_db_serial.init( const.FILE_DB_E_FILENAME ,const.DB_SERIAL_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(4)." + const.FILE_DB_E_FILENAME + ") melding:" + str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_SERIAL_TAB + " succesvol geopend.")

    # set start timestamp
    rt_status_db.timestamp( 126, flog )

    # init functions
    p1_port_notification    = p1_port_shared_lib.P1PortDataNotification( statusdb=rt_status_db, configdb=config_db, flog=flog )
    fase_max_min_notication = phase_shared_lib.VoltageMinMaxNotification( configdb=config_db, phasedb=fase_db_min_max_dag, flog=flog )
    power_nottification     = power_shared_lib.WattTresholdNotification( configdb=config_db, serialdb=e_db_serial, flog=flog)

    # init run
    p1_port_notification.run()
    fase_max_min_notication.run()
    power_nottification.run() 

    timer = 0
    while True:

       # default run time is every 10 sec
        flog.debug(inspect.stack()[0][3]+": elke 10 seconden acties uitvoeren.")  
        p1_port_notification.run()

        #flog.setLevel( logger.logging.DEBUG )
        #power_nottification.run()
        #p1_port_notification.run()
        #fase_max_min_notication.run()
        #flog.setLevel( logger.logging.INFO )

        if timer%3 == 0: # every 30 seconds
            fase_max_min_notication.run()
            power_nottification.run()

        timer += 1
        time.sleep( 10 ) # don't change!
        if timer > 10000:
            timer = 0 # events are at once a day = 8640 with a 10 sec loop time

def saveExit( signum, frame ):
    signal.signal( signum, original_sigint )
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG + prgname + ".log"
        util.setFile2user( logfile, 'p1mon' )
        flog = logger.fileLogger( logfile, prgname )
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )

    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit( 1 ) #  error: no logging check file rights

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT, saveExit )
    Main(sys.argv[1:])
    

