# run manual with ./P1PowerProductionS0CounterSet

import const
import inspect
import os
import logger
import sys
import time
import datetime
import sqldb
import subprocess
#import psutil
import listOfPidByName

from dateutil.relativedelta import *

# programme name.
prgname = 'P1PowerProductionS0CounterSet'

rt_status_db        = sqldb.rtStatusDb()
config_db           = sqldb.configDB()
power_production_db = sqldb.powerProductionDB()
S0_POWERSOURCE      = 1

########################################################
# start of program                                     #
########################################################
def Main(argv): 

    my_pid = os.getpid()
    flog.info("Start van programma met process id " + str(my_pid) )
    pid_list, _process_list = listOfPidByName.listOfPidByName( prgname )
    #flog.debug( inspect.stack()[0][3] + ": pid list raw " + str(pid_list ) )
    #flog.debug( inspect.stack()[0][3] + ": process list raw " + str(_process_list ) )
    pid_list.remove( my_pid ) # remove own pid from the count
    #flog.debug( inspect.stack()[0][3] + ": pid list clean " + str(pid_list ) )
    if len( pid_list ) > 1: # more then 1 because the script is started from a shell
        msg_str = "Gestopt een andere versie van het programma is actief."
        writeLineToStatusFile( msg_str )
        flog.info( inspect.stack()[0][3] + ": " + msg_str )
        sys.exit(1)

     # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(1)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # open van status database
    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(2)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van power production database
    try:
        power_production_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(3)." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_POWERPRODUCTION_TAB + " succesvol geopend." )

    writeLineToStatusFile("Gestart")

    # check if the database contains records.
    if power_production_db.record_count() == 0: 
        writeLineToStatusFile("database is leeg. Gestopt.")
        flog.info("Stop van programma met process id " + str(os.getpid()))
        sys.exit(0)

    _id, config_timestamp, _label       = config_db.strget( 132, flog )
    _id, config_high_metervalue, _label = config_db.strget( 130, flog )
    _id, config_low_metervalue, _label  = config_db.strget( 131, flog )

    msg_str = "meterstand timestamp " + config_timestamp + " meterstand hoog tarief = " + config_high_metervalue + " meterstand laag tarief = " +  config_low_metervalue
    writeLineToStatusFile( msg_str )
    #timestamp = findRecordByTimestamp( config_timestamp, sqldb.INDEX_MINUTE )

    setCounterToZero( config_timestamp )

    flog.info( inspect.stack()[0][3]+": minuten tabel wordt verwerkt.")
    procesRecordByPeriod( config_timestamp, config_high_metervalue ,config_low_metervalue, sqldb.INDEX_MINUTE , "minuten" )
    flog.info( inspect.stack()[0][3]+": uren tabel wordt verwerkt.")
    procesRecordByPeriod( config_timestamp, config_high_metervalue ,config_low_metervalue, sqldb.INDEX_HOUR   , "uren"    )
    flog.info( inspect.stack()[0][3]+": dagen tabel wordt verwerkt.")
    procesRecordByPeriod( config_timestamp, config_high_metervalue ,config_low_metervalue, sqldb.INDEX_DAY    , "dagen"   )
    flog.info( inspect.stack()[0][3]+": maanden tabel wordt verwerkt.")
    procesRecordByPeriod( config_timestamp, config_high_metervalue ,config_low_metervalue, sqldb.INDEX_MONTH  , "maanden" )
    flog.info( inspect.stack()[0][3]+": jaren tabel wordt verwerkt.")
    procesRecordByPeriod( config_timestamp, config_high_metervalue ,config_low_metervalue, sqldb.INDEX_YEAR   , "jaren"   )

    writeLineToStatusFile("Succesvol gestopt.")
    flog.info("Stop van programma met process id " + str(os.getpid()))

########################################################
# period function to prevend rewriting the code        #
# multiple times                                       #
########################################################
def procesRecordByPeriod( timestamp , config_high_metervalue ,config_low_metervalue, period, label ):

    timestamp, records_count = findRecordByTimestamp( timestamp, period )
    msg_str = "Gestart met de " + label + " tabel." 
    writeLineToStatusFile( msg_str )
    if  timestamp != None:
        msg_str = "Timestamp " + str(timestamp) + " gevonden in de " + label + " tabel. " + str(records_count) + " record(s) om te verwerken."
        writeLineToStatusFile( msg_str )

        max_timestamp, _min_timestamp = findMinMaxTimestamp( period )

        if max_timestamp != None:
            writeLineToStatusFile( msg_str )
            updateCounterRecords( timestamp ,max_timestamp, config_high_metervalue, config_low_metervalue, period )
    else:
        msg_str = "geen records gevonden in de " + label + " tabel."
        writeLineToStatusFile( msg_str )

#########################################################
# de teller worden voor de aanpassingen op nul gezet om #
# dubbelingen te voorkomen                              #
#########################################################
def setCounterToZero( timestamp ):
    flog.info( inspect.stack()[0][3]+": gestart met  tijdstip "  + str(timestamp) )
    try:
        sql = "update " + const.DB_POWERPRODUCTION_TAB + " set \
            PRODUCTION_KWH_HIGH_TOTAL = 0,\
            PRODUCTION_KWH_LOW_TOTAL  = 0,\
            PRODUCTION_KWH_TOTAL      = 0\
            where POWER_SOURCE_ID = 1 and timestamp >= '" + str( timestamp ) + "'"
        power_production_db.excute( sql )
        msg_str = "Records worden op 0 gezet voor de periode vanaf " + str( timestamp )
        writeLineToStatusFile( msg_str )
        flog.info( msg_str )
    except Exception as e:
        flog.warning( inspect.stack()[0][3]+": sql probleem voor het op nul zeten van de tellers voor timestamp " + str( timestamp ) +  " -> " + str(e) )

 
########################################################
# Add the entered offset to the high, low and total    #
# counters, use period to select min, hour,day, month  #
# years.                                               #
########################################################
def updateCounterRecords( timestamp , max_timestamp, config_high_metervalue ,config_low_metervalue, period ):

    high_meter_value = float(config_high_metervalue)
    low_meter_value  = float(config_low_metervalue)
    ts_next          = datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S")

    if period == sqldb.INDEX_MINUTE:
        substr_index = 17
        timestamp_str_postfix = "00"
        timestamp_delta = datetime.timedelta( minutes=1 )
        period_text = "Minuut"
    elif period == sqldb.INDEX_HOUR:
        substr_index = 14
        timestamp_str_postfix = "00:00"
        timestamp_delta = datetime.timedelta( hours=1 )
        period_text = "Uur"
    elif period == sqldb.INDEX_DAY:
        substr_index = 11
        timestamp_str_postfix = "00:00:00"
        timestamp_delta = datetime.timedelta( days=1 )
        period_text = "Dag"
    elif period == sqldb.INDEX_MONTH:
        substr_index = 7
        timestamp_str_postfix = "-01 00:00:00"
        timestamp_delta = relativedelta(months=+1)
        period_text = "Maand"
    elif period == sqldb.INDEX_YEAR:
        substr_index = 4
        timestamp_str_postfix = "-01-01 00:00:00"
        timestamp_delta = relativedelta(months=+12)
        period_text = "Jaar"
    else:
        flog.warning( inspect.stack()[0][3]+": onbekend of verkeerd periode gekozen." )
        return None, None

    # debug code relativedelta
    """"
    while True:
        ts_next = datetime.strptime( str(ts_next), "%Y-%m-%d %H:%M:%S") + timestamp_delta
        period_timestamp = str(ts_next)[0:substr_index] + timestamp_str_postfix
        print ( ts_next, period_timestamp )

        time.sleep(1)
    """

    while True:

        period_timestamp = str(ts_next)[0:substr_index] + timestamp_str_postfix
        #print ( period_timestamp )

        record = power_production_db.get_timestamp_record( str(period_timestamp), period, S0_POWERSOURCE  )
        if record != None:
            high_meter_value = high_meter_value + float(record[3])
            low_meter_value  = low_meter_value  + float(record[4])

            # update the record whith the new values.
            try:
                sql_update = "update " + const.DB_POWERPRODUCTION_TAB + " set" +\
                " PRODUCTION_KWH_HIGH_TOTAL = " + str(high_meter_value) + \
                ", PRODUCTION_KWH_LOW_TOTAL = " + str(low_meter_value) + \
                ", PRODUCTION_KWH_TOTAL = "     + str(high_meter_value +low_meter_value ) + \
                " where TIMEPERIOD_ID = "       + str(period) +\
                " and POWER_SOURCE_ID = "       + str(S0_POWERSOURCE) +\
                " and timestamp = '"            + str(period_timestamp) + "'"
                power_production_db.excute( sql_update )
                #print ( sql_update )
                replaceLastLineInStatusFile ( period_text + " record voor tijdstip " + str(period_timestamp) + " verwerkt.")
            except Exception as e:
                flog.warning( inspect.stack()[0][3]+": sql error voor timestamp " + str(period_timestamp) +  " -> " + str(e) )

        if str(ts_next) >= max_timestamp:
            msg_str = period_text  + " update gereed." 
            writeLineToStatusFile( msg_str )
            flog.debug ( inspect.stack()[0][3] + ": " + msg_str )
            break

        ts_next = datetime.datetime.strptime( str(ts_next), "%Y-%m-%d %H:%M:%S") + timestamp_delta


########################################################
# find maximum and minium timestamps for an given      #
# periods                                              #
########################################################
def findMinMaxTimestamp( period ):
    try:
        sql_select = "select max(timestamp), min(timestamp) FROM " + const.DB_POWERPRODUCTION_TAB +\
                " where TIMEPERIOD_ID = " + str(period) +\
                " and POWER_SOURCE_ID = " + str(S0_POWERSOURCE)
        sql_select = " ".join ( sql_select.split() )
        flog.debug( inspect.stack()[0][3]+": sql = "  + sql_select )
        record = power_production_db.select_rec( sql_select ) 
        #print ( "rec", record )
        return str(record[0][0]), str(record[0][1])  # max timestamp, min timestamp
    except Exception as e:
        flog.warning( inspect.stack()[0][3]+": sql error -> " + str(e) )

    return None, None

########################################################
# check if the timestamp is available for the          #
# different  periods                                   #
########################################################
def findRecordByTimestamp( timestamp, period ):

    if period == sqldb.INDEX_MINUTE:
        substr_index = 17
        select_timestamp  = timestamp[0:substr_index]
    elif period == sqldb.INDEX_HOUR:
        substr_index = 13
        select_timestamp  = timestamp[0:substr_index]
    elif period == sqldb.INDEX_DAY:
        substr_index = 10
        select_timestamp  = timestamp[0:substr_index]
    elif period == sqldb.INDEX_MONTH:
        substr_index = 7
        select_timestamp  = timestamp[0:substr_index]
    elif period == sqldb.INDEX_YEAR:
        substr_index = 4
        select_timestamp  = timestamp[0:substr_index]
    else:
        flog.warning( inspect.stack()[0][3]+": onbekend of verkeerd periode gekozen." )
        return None, None

    try:
        sql_select = "select timestamp, count() FROM " + const.DB_POWERPRODUCTION_TAB +\
                " where TIMEPERIOD_ID = " + str(period) +\
                " and POWER_SOURCE_ID = " + str(S0_POWERSOURCE) + " and substr(timestamp,1," + str(substr_index) + ") >= '" + select_timestamp + "' order by timestamp asc limit 1"
        sql_select = " ".join ( sql_select.split() )
        flog.debug( inspect.stack()[0][3]+": sql = "  + sql_select )
        record = power_production_db.select_rec( sql_select ) 
        #print ( record )
        return str(record[0][0]), str(record[0][1])  # timestamp , number of records
    except Exception as e:
        flog.warning( inspect.stack()[0][3]+": sql error voor timestamp  " + timestamp +  " -> " + str(e) )

    return None, None

########################################################
# write to ramdisk file the progress                   #
# the file is emptied/re-created when the program      #
# starts.                                              #
########################################################
def writeLineToStatusFile( msg ):
    try:
        fp = open( const.FILE_POWERPRODUCTION_CNT_STATUS , "a" )
        t=time.localtime()
        msg_str = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + " " + msg + '\n'
        fp.write( msg_str )
        flog.debug( msg_str )
        fp.close()
    except Exception as e:
        flog.error( "status file schrijf fout: " + str(e) )

########################################################
# write to ramdisk file and change the last line       #
# the file is emptied/re-created when the program      #
# starts.                                              #
########################################################
def replaceLastLineInStatusFile( msg ):
    try:
        t=time.localtime()
        msg_str = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + " " + msg + '\n'
        
        fp = open( const.FILE_POWERPRODUCTION_CNT_STATUS , "r" )
        list_of_lines = fp.readlines()
        list_of_lines[ len(list_of_lines)-1 ] = msg_str
        fp.close()
        
        fp = open( const.FILE_POWERPRODUCTION_CNT_STATUS , "w" )
        for line in list_of_lines:
            fp.write( line )
        fp.close()

    except Exception as e:
        flog.error( "status file schrijf/lees fout: " + str(e) )

########################################################
# init                                                 #
########################################################
if __name__ == "__main__":
    global process_bg 
    try:
        os.umask( 0o002 )
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname)    
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )

        status_fp = open( const.FILE_POWERPRODUCTION_CNT_STATUS , "w")
        subprocess.run( ['sudo', 'chmod', '0666' , const.FILE_POWERPRODUCTION_CNT_STATUS ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        status_fp.close()

    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:"+str(e.args[0]))
        sys.exit(1)

    Main(sys.argv[1:])
