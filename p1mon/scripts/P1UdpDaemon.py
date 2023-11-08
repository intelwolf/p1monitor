# run manual with ./P1UdpDaemon

import const
import inspect
import logger
import json
import os
import signal
import sqldb
import socket
import sys
import time
import process_lib
import util

# programme name.
prgname = 'P1UdpDaemon'
# bind all IP
HOST = '0.0.0.0'
# Listen on Port
PORT = 30721
#Size of receive buffer
BUFFER_SIZE = 1024

# Create a UDP/IP socket
udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

temperature_db  = sqldb.temperatureDB()
rt_status_db    = sqldb.rtStatusDb()
config_db       = sqldb.configDB()

timestamp_last_backup = util.getUtcTime()

def Main(argv): 
    flog.info("Start van programma.")
    last_seq_id = -1

    DiskRestore()
    
     # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(3)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # open van status database
    try:    
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van temperatuur database
    try:    
        temperature_db.init(const.FILE_DB_TEMPERATUUR_FILENAME ,const.DB_TEMPERATUUR_TAB )
        temperature_db.cleanDb(flog)
        temperature_db.defrag()
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_TEMPERATUUR_FILENAME+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_TEMPERATUUR_TAB +" succesvol geopend.")

    # set start timestamp in status database
    rt_status_db.timestamp(56,flog)

    try:
        # Bind the socket to the host and port
        udpsocket.bind((HOST, PORT))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": UDP ontvanger niet te starten , gestopt -> " + str(e) )
        sys.exit(1)

    # one time message for log
    if prgIsActive(flog) == False:
        flog.info(inspect.stack()[0][3]+": programma is niet als actief geconfigureerd , wordt niet uitgevoerd.")

    # fix problem with primary key.
    temperature_db.change_table( flog )
    temperature_db.fix_missing_month_day( flog )

    # main loop blocked recieving of UDP packages / messages
    while True:
         # check if we are using this program (uses config db!)
        while prgIsActive(flog) == False:
            continue
        # backup data to flash every ~15 min.
        if abs( timestamp_last_backup - util.getUtcTime() ) > 900:
            backup_data()

        # Receive BUFFER_SIZE bytes data
        data = udpsocket.recvfrom(BUFFER_SIZE)
        if data:

            t = time.localtime()
            timestamp = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
           
            flog.debug( inspect.stack()[0][3] + ": ontvangen udp message = " + str(data[0]) )

            # process json
            try:

                #print ( data )

                jsondata = json.loads( data[0].decode('utf-8') )

                # record id index codes
                # secs      = 10
                # min.      = 11
                # hour      = 12
                # days      = 13
                # months    = 14
                # years     = 15
                
                #timestamp = datetime.datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')

                #timestamp = "2020-09-01 00:01:02"
                # process secs values, data every 5 secs or so.
                if jsondata['id'] != 'ztatz_dt':
                    flog.warning(inspect.stack()[0][3]+": id van json data is niet correct :"+jsondata['id'] )
                else:

                    if  last_seq_id == jsondata['seq']:
                        flog.debug(inspect.stack()[0][3]+": dubbele volgorde id gevonden, wordt genegeerd. seq id=:"+str(jsondata['seq']) )
                        continue
                    last_seq_id =  jsondata['seq']

                    temperature_db.replace(timestamp,\
                    10, \
                    jsondata['t_in'], \
                    jsondata['t_in_avg'],\
                    0,\
                    0,\
                    jsondata['t_out'], \
                    jsondata['t_out_avg'],\
                    0,\
                    0,\
                    flog )

                    # process minutes values.
                    # returns avg, min, max(in), avg, min, max(out) 
                    temp_list = temperature_db.selectAMM( timestamp[:16],10,flog )
                    temperature_db.replace(timestamp[:16]+":00",\
                    11, \
                    0, \
                    temp_list[0][0],\
                    temp_list[0][0],\
                    temp_list[0][0],\
                    0,\
                    temp_list[0][3],\
                    temp_list[0][3],\
                    temp_list[0][3],\
                    flog )

                    # process hour values.
                    # returns avg, min, max(in), avg, min, max(out) 
                    temp_list = temperature_db.selectAMM( timestamp[:13],11,flog )
                    temperature_db.replace(timestamp[:13]+":00:00",\
                    12, \
                    0, \
                    temp_list[0][0],\
                    temp_list[0][1],\
                    temp_list[0][2],\
                    0,\
                    temp_list[0][3],\
                    temp_list[0][4],\
                    temp_list[0][5],\
                    flog )

                    #flog.setLevel( logging.DEBUG )
                    # process day values.
                    # returns avg, min, max(in), avg, min, max(out) 
                    temp_list = temperature_db.selectAMM( timestamp[:10],12,flog )
                    temperature_db.replace(timestamp[:10]+" 00:00:00",\
                    13, \
                    0, \
                    temp_list[0][0],\
                    temp_list[0][1],\
                    temp_list[0][2],\
                    0,\
                    temp_list[0][3],\
                    temp_list[0][4],\
                    temp_list[0][5],\
                    flog )
                    

                    # process month values.
                    # returns avg, min, max(in), avg, min, max(out) 
                    temp_list = temperature_db.selectAMM( timestamp[:7],13,flog )
                    temperature_db.replace(timestamp[:7]+"-01 00:00:00",\
                    14, \
                    0, \
                    temp_list[0][0],\
                    temp_list[0][1],\
                    temp_list[0][2],\
                    0,\
                    temp_list[0][3],\
                    temp_list[0][4],\
                    temp_list[0][5],\
                    flog )
                    #flog.setLevel( logging.INFO )

                    # process year values.
                    # returns avg, min, max(in), avg, min, max(out) 
                    temp_list = temperature_db.selectAMM( timestamp[:4],14,flog )
                    temperature_db.replace(timestamp[:4]+"-01-01 00:00:00",\
                    15, \
                    0, \
                    temp_list[0][0],\
                    temp_list[0][1],\
                    temp_list[0][2],\
                    0,\
                    temp_list[0][3],\
                    temp_list[0][4],\
                    temp_list[0][5],\
                    flog )

                    # set process timestamp in status database
                    rt_status_db.timestamp(58,flog)

                    #clean_database
                    temperature_db.cleanDb(flog)
                   

            except Exception as e:
                flog.error(inspect.stack()[0][3]+": json fout melding:"+str(e.args) )

def prgIsActive( flog ):
    _config_id, status, _text = config_db.strget( 44,flog )
    if status == "0":
        flog.debug(inspect.stack()[0][3]+": programma is niet als actief geconfigureerd, pauzeer.")
        time.sleep( 30 )
        return False
    else:
        return True

def setFileFlags():
    util.setFile2user(const.FILE_DB_TEMPERATUUR_FILENAME,'p1mon')
    dummy,tail = os.path.split(const.FILE_DB_TEMPERATUUR_FILENAME)   
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')

def backup_data():
    global timestamp_last_backup
    # set backup timestamp in status database
    rt_status_db.timestamp(57,flog)
    timestamp_last_backup = util.getUtcTime()
    #setFileFlags()
    flog.debug(inspect.stack()[0][3]+": Gestart")
    process_lib.run_process( 
        cms_str='/p1mon/scripts/P1DbCopy --temperature2disk --forcecopy',
        use_shell=True,
        give_return_value=True, 
        flog=flog 
        )

    #backupFile(const.FILE_DB_TEMPERATUUR_FILENAME)
    #setFileFlags()
    rt_status_db.timestamp(29,flog)
    flog.debug(inspect.stack()[0][3]+": Gereed")

def DiskRestore():
    # kopieren van bestaande database file van flash storage naar ramdisk
    # als deze nog niet al op de ramdisk staat
    process_lib.run_process( 
        cms_str='/p1mon/scripts/P1DbCopy --allcopy2ram',
        use_shell=True,
        give_return_value=True,
        flog=flog 
        )


def saveExit(signum, frame):
        signal.signal( signal.SIGINT, original_sigint )
        udpsocket.close()
        backup_data()
        flog.info( inspect.stack()[0][3] + " SIGINT ontvangen, gestopt." )
        sys.exit(0)

#-------------------------------
if __name__ == "__main__":

    try:
        os.umask( 0o002 )
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname)    
        flog.setLevel( logger.logging.INFO )
        #flog.setLevel( logging.DEBUG )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(1)

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT, saveExit)
    Main(sys.argv[1:])
