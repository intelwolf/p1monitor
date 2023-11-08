# run manual with ./P1UdpBroadcaster

#import argparse
#import base64
import const
import inspect
import logger
import json
import signal
import socket
import systemid
import sys
import sqldb
import time
import os
import util

#from logger import *
#from os import listdir, chmod
#from os.path import isfile,join
#from sqldb import configDB,rtStatusDb
#from util import *
#from time import sleep
#from systemid import getSystemId

prgname         = 'P1UdpBroadcaster'

config_db       = sqldb.configDB()
rt_status_db    = sqldb.rtStatusDb()

host_address    =  ( '<broadcast>', const.UDP_BASIC_API_PORT )
udpsocket       = socket.socket( socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP )

udpsocket.setsockopt( socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

program_is_active = -1

system_id = systemid.getSystemId()

def Main(argv): 
    flog.info("Start van programma.")
   
    # open van status database
    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # set start timestamp in status database
    rt_status_db.timestamp(70,flog) 

    loop_timeout = 6
    last_json_timestamp = ''
    from_file = const.DIR_RAMDISK + const.API_BASIC_JSON_PREFIX + system_id + const.API_BASIC_JSON_SUFFIX

    #program_is_active = isProgramActive()

    while True:
       
        if isProgramActive() == False: 
            time.sleep ( 10 )
            continue

        try:
            
            if os.path.isfile( from_file ):
               
                with open(  from_file, 'rb') as f:
                    file_data  = f.read()
                    jsondata = json.loads( file_data.decode('utf-8') )
                    
                    if ( last_json_timestamp != jsondata['TIMESTAMP_lOCAL'] ):
                        flog.debug(inspect.stack()[0][3]+": Data WEL verzonden timestamp json bestand is anders.")
                        last_json_timestamp = jsondata['TIMESTAMP_lOCAL']
                        udpsocket.sendto( file_data, host_address )
                        # set timestamp last send message status database
                        rt_status_db.timestamp(71,flog)
                    else:
                        flog.debug(inspect.stack()[0][3]+": Data NIET verzonden timestamp json bestand is gelijk.")
                    
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": Fout melding:"+str(e.args[0]))
       
        flog.debug(inspect.stack()[0][3]+": Wacht " + str(loop_timeout) + " seconden.")
        time.sleep ( loop_timeout )


def isProgramActive():
    # check if we are active
    global program_is_active
    _id, program_is_on ,_label = config_db.strget(55,flog)
    status = int(program_is_on)
    if status == 0:
        if program_is_active != status:
            flog.info(inspect.stack()[0][3]+": Deamon staat uit.")
            program_is_active = status
        return False
    else:
        if program_is_active != status:
            flog.info(inspect.stack()[0][3]+": Deamon staat aan.")
            program_is_active = status 
        return True


def saveExit( signum, frame ):
        signal.signal(signal.SIGINT, original_sigint)
        flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
        sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG+prgname+".log" 
        util.setFile2user(logfile,'p1mon')
        flog = logger.fileLogger( logfile,prgname )
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(10) #  error: no logging check file rights

    original_sigint = signal.getsignal( signal.SIGINT )
    signal.signal( signal.SIGINT, saveExit )
    Main( sys.argv[1:] )