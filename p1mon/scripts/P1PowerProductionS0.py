# run manual with ./P1PowerProductionS0

import const
import datetime
import filesystem_lib
import inspect
import gpio
import os
import signal
import logger
import sqldb
import multiprocessing
import sys
import random
import time
import sqldb
import process_lib
import util

# programme name.
prgname = 'P1PowerProductionS0'

rt_status_db            = sqldb.rtStatusDb()
config_db               = sqldb.configDB()
power_production_db     = sqldb.powerProductionDB()

gpioPowerS0Puls         = gpio.gpioDigtalInput()

timestamp               = util.mkLocalTimeString() 

#timestamp_buffer_list   = []
prg_is_active           = True
S0_POWERSOURCE          = 1
mp_queue_1              = multiprocessing.Queue()

QUEUE_CMD_START  = "START"

def Main(argv): 
    global timestamp 

    my_pid = os.getpid()
    flog.info("Start van programma met process id " + str(my_pid) )

    DiskRestore()
    
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

    filesystem_lib.set_file_permissions(filepath=const.FILE_DB_POWERPRODUCTION, permissions="664" )

    # database defrag 
    power_production_db.defrag()
   
    # set proces gestart timestamp
    rt_status_db.timestamp( 108,flog )
    
    try:
        gpioPowerS0Puls.init( 126, config_db ,flog )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": GPIO pin voor tarief schakelaar niet te openen. " + str(e.args[0])  ) 

    setFileFlags()
    deleteRecords()

    # one time message for log
    #if prgIsActive(flog) == False:
    #    flog.info(inspect.stack()[0][3]+": programma is niet als actief geconfigureerd , wordt niet uitgevoerd.")

    startBackgroundDeamon()

    while True:

        #while prgIsActive( flog ) == False: # sleep function in prgIsActive()!
        #    continue

        _id, run_status, _label = config_db.strget( 125, flog )
        if int(run_status) == 0: # stop process
            flog.info(inspect.stack()[0][3]+": programma is niet als actief geconfigureerd, programma wordt gestopt.")
            stop()

        #flog.debug( inspect.stack()[0][3]+": loop " )
        checkAndInsertMinuteRecord()

        #check if GPIO pin is set or else wait for a valid pin
        while gpioPowerS0Puls.gpio_pin == None:
            flog.debug( inspect.stack()[0][3] + ": GPIO pin wordt opnieuw geprobeerd.") 
            time.sleep( 30 ) # wait to limit load
            try:
                gpioPowerS0Puls.init( 126, config_db ,flog )
            except:
                pass

        waitForPuls()


def setFileFlags():
    util.setFile2user( const.FILE_DB_POWERPRODUCTION, 'p1mon' )
    _head,tail = os.path.split( const.FILE_DB_POWERPRODUCTION )
    util.setFile2user( const.DIR_FILEDISK+tail,'p1mon' )

########################################################
# inserts or replaces a record for the given           #
# timestamp, the value for the next higer timestamp    #
# is read by a select, when there is no value the      #
# replace will not be done                             #
########################################################
def replaceRecordForAPeriod( timestamp, period ):

    if period == sqldb.INDEX_HOUR:
        substr_index = 13
        select_timestamp  = timestamp[0:substr_index]
        replace_timestamp = timestamp[0:substr_index] + ":00:00"
        select_period     = str(sqldb.INDEX_MINUTE)
        replace_period    = str(sqldb.INDEX_HOUR)
    elif period == sqldb.INDEX_DAY:
        substr_index = 10
        select_timestamp  = timestamp[0:substr_index]
        replace_timestamp = timestamp[0:substr_index] + " 00:00:00"
        select_period     = str(sqldb.INDEX_HOUR )
        replace_period    = str(sqldb.INDEX_DAY )
    elif period == sqldb.INDEX_MONTH:
        substr_index = 7
        select_timestamp  = timestamp[0:substr_index]
        replace_timestamp = timestamp[0:substr_index] + "-01 00:00:00"
        select_period     = str(sqldb.INDEX_DAY )
        replace_period    = str(sqldb.INDEX_MONTH )
    elif period == sqldb.INDEX_YEAR:
        substr_index = 4
        select_timestamp  = timestamp[0:substr_index]
        replace_timestamp = timestamp[0:substr_index] + "-01-01 00:00:00"
        select_period     = str(sqldb.INDEX_MONTH )
        replace_period    = str(sqldb.INDEX_YEAR )
    else:
        flog.warning( inspect.stack()[0][3]+": onbekend of verkeerd periode gekozen." )
        return

    try:
        sql_select = "select sum(PRODUCTION_KWH_HIGH),sum(PRODUCTION_KWH_LOW),sum(PULS_PER_TIMEUNIT_HIGH),sum(PULS_PER_TIMEUNIT_LOW),\
             max(PRODUCTION_KWH_HIGH_TOTAL),max(PRODUCTION_KWH_LOW_TOTAL),max(PRODUCTION_KWH_TOTAL),sum(PRODUCTION_PSEUDO_KW)\
            FROM " + const.DB_POWERPRODUCTION_TAB +\
            " where TIMEPERIOD_ID = " + select_period +\
            " and POWER_SOURCE_ID = " + str(S0_POWERSOURCE) + " and substr(timestamp,1," + str(substr_index) + ") = '" + select_timestamp + "'"
        sql_select = " ".join ( sql_select.split() )
        flog.debug( inspect.stack()[0][3]+": sql select  = "  + sql_select )   
        rec = power_production_db.select_rec( sql_select ) 

        if rec[0][0] != None:
            sql_replace = "replace into " + const.DB_POWERPRODUCTION_TAB + \
                " (TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, \
                   PRODUCTION_KWH_HIGH, PRODUCTION_KWH_LOW, PULS_PER_TIMEUNIT_HIGH, PULS_PER_TIMEUNIT_LOW,\
                   PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL, PRODUCTION_PSEUDO_KW )\
                   values ('"\
                   + replace_timestamp + "', " + replace_period + ", " + str(S0_POWERSOURCE) + ", "\
                   + str(rec[0][0]) + ", " + str(rec[0][1]) + ", " + str(rec[0][2]) + ", " + str(rec[0][3]) + ", "\
                   + str(rec[0][4]) + ", " + str(rec[0][5]) + ", " + str(rec[0][6]) + ", " + str(rec[0][7])\
                   +  ")" 

            sql_replace = " ".join ( sql_replace.split() ) 
            flog.debug( inspect.stack()[0][3]+": sql replace  = "  + sql_replace  )
            power_production_db.excute( sql_replace )


    except Exception as e:
        flog.warning( inspect.stack()[0][3]+": sql error voor timestamp  " + timestamp +  " -> " + str(e) )

########################################################
# make remove / delete records from database           #
# ######################################################
def deleteRecords():

    timestamp = util.mkLocalTimeString()

    try:
        sql_del_str = "delete from " + const.DB_POWERPRODUCTION_TAB  + \
        " where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_MINUTE ) + \
        " and POWER_SOURCE_ID = " + \
        str( S0_POWERSOURCE ) + \
        " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=31)) + "'"
        flog.debug( inspect.stack()[0][3] + ": wissen van minuten. sql=" + sql_del_str ) 
        power_production_db.excute( sql_del_str )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van oude minuten records gefaald: " + str(e) )


    try:
        sql_del_str = "delete from " + const.DB_POWERPRODUCTION_TAB  + \
        " where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_HOUR ) + \
        " and POWER_SOURCE_ID = " + \
        str( S0_POWERSOURCE ) + \
        " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096)) + "'"
        flog.debug( inspect.stack()[0][3] + ": wissen van uren. sql=" + sql_del_str ) 
        power_production_db.excute( sql_del_str )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van oude minuten records gefaald: " + str(e) )

    try:
        sql_del_str = "delete from " + const.DB_POWERPRODUCTION_TAB  + \
        " where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_DAY ) + \
        " and POWER_SOURCE_ID = " + \
        str( S0_POWERSOURCE ) + \
        " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096)) + "'"
        flog.debug( inspect.stack()[0][3] + ": wissen van dagen. sql=" + sql_del_str ) 
        power_production_db.excute( sql_del_str )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van oude minuten records gefaald: " + str(e) )

########################################################
# make a minute record to prevent gaps in the data set #
# and prevent expensive dataset changes                #
# functie is run as a seperate process                 #
########################################################
def checkAndInsertMinuteRecord():
    dt = datetime.datetime.now()
    timestamp = datetime.datetime.strftime( dt , "%Y-%m-%d %H:%M:00")

    #print ("# " + str( dt.second  ) )
    try:
        if dt.second > 30: #limit the work load
            
            flog.debug( inspect.stack()[0][3]+": leeg record aanmaken om een data gap te voorkomen." )
            timetamp_minus_one_minute = datetime.datetime.strftime( dt - datetime.timedelta( minutes=1 ), "%Y-%m-%d %H:%M:00")
            #print (" timetamp_minus_one_minute = " + str(timetamp_minus_one_minute) )
            rec = power_production_db.get_timestamp_record( timetamp_minus_one_minute, sqldb.INDEX_MINUTE, S0_POWERSOURCE )
            #print (" record minus one = " + str(rec) )

            if rec != None:
                #timestamp = datetime.strftime( dt , "%Y-%m-%d %H:%M:00")
                sql = "insert into " + const.DB_POWERPRODUCTION_TAB + " (TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL )\
                     values ('" + timestamp + "'," + str(sqldb.INDEX_MINUTE) + "," + str(S0_POWERSOURCE) + "," + str(rec[7]) + "," + str(rec[8]) + "," + str(rec[9]) + ")"

                #print ( sql )

                # check if there is no record 
                rec_exist = power_production_db.get_timestamp_record( timestamp, sqldb.INDEX_MINUTE, S0_POWERSOURCE )
                if rec_exist == None:
                    #print ( "sql insert = " + sql )
                    power_production_db.excute( sql )

                #rec_test = power_production_db.get_timestamp_record( timestamp, sqldb.INDEX_MINUTE, S0_POWERSOURCE )
                #print ( "sql check = " + str(rec_test) )

                #print ("# update. power "+timestamp)

                replaceRecordForAPeriod( timestamp, sqldb.INDEX_HOUR )
                replaceRecordForAPeriod( timestamp, sqldb.INDEX_DAY )
                replaceRecordForAPeriod( timestamp, sqldb.INDEX_MONTH )
                replaceRecordForAPeriod( timestamp, sqldb.INDEX_YEAR )

                # clean the database
                deleteRecords()

            # check if there are any gaps in the database records
            mp_queue_1.put( QUEUE_CMD_START )

    except Exception as e:
        flog.warning( inspect.stack()[0][3]+": sql insert error voor timestamp  " + timestamp +  " -> " + str(e) )

#######################################################
# background process for handeling missing records in #
# the database. The process is started by the command #
# mp_queue_1.put( QUEUE_CMD_START )                   #
#######################################################
def backgroundDaemon():
    while True:

        try:
            item = mp_queue_1.get(block=True, timeout=10 )
            #print (item)
            if item == QUEUE_CMD_START:
                flog.debug ( inspect.stack()[0][3] + " queue lengte verminderd met 1, aantal entries = " + str( mp_queue_1.qsize()) )
                addMissingRecords()
                
            # remove older request from queue to prevent overload.
            while mp_queue_1.qsize() > 0:
                mp_queue_1.get_nowait() 

            flog.debug ( inspect.stack()[0][3] +" queue lengte na verwerking = " + str(mp_queue_1.qsize()) + "." )

        except:
            time.sleep( 1 )

#######################################################
# starting of deamon background process               #
#######################################################
def startBackgroundDeamon():
    p = multiprocessing.Process( target=backgroundDaemon )
    p.daemon=True
    p.start()
    p.join(timeout=0)

########################################################
# check if there are gaps in the database en add       #
# missing records if any                               #
# function is run as a seperate process                #
# ######################################################
def addMissingRecords():

    #flog.setLevel( logging.DEBUG )

    #print("# addMissingRecords()") 
    missing_records_count   = 0
    max_timestamp           = ""
    min_timestamp           = ""
    tic_process             = time.perf_counter()

    try:
        # Number of minutes calculated by finding the seconds and deviding by 60.
        # When count is biger then 0 we are missing some minutes.
        # count -1 is for the minute offset.
        sql = "select (strftime('%s',max(timestamp)) - strftime('%s',min(timestamp)))/60 - (count()-1), max(timestamp), min(timestamp) from " +\
        const.DB_POWERPRODUCTION_TAB + " where TIMEPERIOD_ID = " +\
        str(sqldb.INDEX_MINUTE) + " and POWER_SOURCE_ID = " + str(S0_POWERSOURCE)
        sql = " ".join ( sql.split() )
        flog.debug( inspect.stack()[0][3] + " SQL = " + sql )

        rec = power_production_db.select_rec( sql )
        missing_records_count   = rec[0][0] # number of minute records missing in the database.
        max_timestamp           = rec[0][1] # most current timestamp.
        min_timestamp           = rec[0][2] # oldest timestamp.
        #print ( sql )
    except Exception as e:
            flog.error( inspect.stack()[0][3]+": sql error voor record gap analyse op table " + const.DB_POWERPRODUCTION_TAB + " ->" + str(e) )

    flog.debug( inspect.stack()[0][3] + " aantal records in database dat ontbreekt = " + str(missing_records_count) +\
         " timestamp min = " + str(min_timestamp) + " timestamp max = " + str(max_timestamp))

    if missing_records_count == None:
        flog.debug( inspect.stack()[0][3] + ": gestopt geen records toegevoegd (database is leeg)." ) 
        return

    if missing_records_count < 1:
        flog.debug( inspect.stack()[0][3] + ": gestopt geen ontbrekende records." ) 
        return

    #flog.info( inspect.stack()[0][3] + ": gestart. process id = " + str(os.getpid()) )

    # build a set of records that are in the database
    if missing_records_count > 0:
        try:
            sql = "select timestamp from " + const.DB_POWERPRODUCTION_TAB + " where timeperiod_id = " +\
            str(sqldb.INDEX_MINUTE) +\
            " and power_source_id = " +\
            str(S0_POWERSOURCE) +\
            " order by timestamp desc"
            sql = " ".join ( sql.split() )
            #print ( sql )
            timestamp_list_from_db = power_production_db.select_rec( sql )

            timestamp_set_from_db = set()
            for i in range(len(timestamp_list_from_db)):
                #print ( timestamp_list_from_db[i][0]  )
                timestamp_set_from_db.add( timestamp_list_from_db[i][0] )

            #print ( timestamp_list_from_db )
            flog.debug( inspect.stack()[0][3] + " maximaal aantal records in database = " + str( len(timestamp_list_from_db) ) )
            #print ( "records in database dat ontbreekt=" + str( timestamp_list_from_db ) )
        except Exception as e:
            flog.error( inspect.stack()[0][3]+": sql error voor het vinden van ontbrekende records " + const.DB_POWERPRODUCTION_TAB + " ->" + str(e) )
    else:
        flog.info( inspect.stack()[0][3] + ": gestopt geen records toegevoegd (fase 1)." ) 
        return


    #print ( timestamp_list_from_db[0] )
    #print ( timestamp_list_from_db[len(timestamp_list_from_db)-1] )
    # sys.exit()

    # make a list of all possible timestamps 
    # dt_tmp = datetime.strptime( min_timestamp, "%Y-%m-%d %H:%M:%S")
    dt_tmp = datetime.strptime( min_timestamp, "%Y-%m-%d %H:%M:%S")
    all_possible_timestamps_set = set()
    while True:
        #print ("adding " + datetime.strftime( dt_tmp, "%Y-%m-%d %H:%M:%S") )
        #time.sleep(5)
        #all_possible_timestamps.append( str( dt_tmp ) )
        all_possible_timestamps_set.add ( str( dt_tmp ) )
        #all_possible_timestamps.add( str(dt_tmp)  )
        dt_tmp = dt_tmp + datetime.timedelta( minutes=1 )
        if datetime.datetime.strftime( dt_tmp, "%Y-%m-%d %H:%M:%S") > max_timestamp:
            #all_possible_timestamps.pop() # remove current timestamp
            flog.debug( inspect.stack()[0][3] + " all_possible_timestamps_set gestopt op timestamp = " + str( dt_tmp) )
            break
    
    #print( all_possible_timestamps )
    flog.debug( inspect.stack()[0][3] + " maximaal aantal mogelijke timestamps = " + str( len( all_possible_timestamps_set) ) )

    #print ( "# all_possible_timestamps_set count = ",len(all_possible_timestamps_set))
    #print ( "# timestamp_set_from_db = count "      ,len(timestamp_set_from_db))

    #fiter_set = set()
    filter_set = all_possible_timestamps_set.difference( timestamp_set_from_db )

    #print( all_possible_timestamps[0], all_possible_timestamps[len(all_possible_timestamps)-1] )
    #print ( all_possible_timestamps )
    # filter out de records that are in the database
    """
    for ts_db in timestamp_list_from_db: 
        str_db_ts = str( ts_db[0] )
        try:
            all_possible_timestamps.remove( str_db_ts )
        except:
            pass

    #print( all_possible_timestamps )
    flog.debug( inspect.stack()[0][3] + " aantal mogelijke timestamps na filtering = " + str( len(all_possible_timestamps) ) )
    """

    all_possible_timestamps = list(filter_set)
    all_possible_timestamps.sort()

    #print ( "# all_possible_timestamps = "              ,all_possible_timestamps)

    if len( all_possible_timestamps ) < 1 :
        flog.info( inspect.stack()[0][3] + ": gestopt geen records toegevoegd (fase 2)." ) 
        return

    for ts_possible_timestamp in all_possible_timestamps:

        # first find the previous record
        ts_previous = datetime.strptime( ts_possible_timestamp, "%Y-%m-%d %H:%M:%S")- datetime.timedelta( minutes=1 )
        rec = power_production_db.get_timestamp_record( str(ts_previous), sqldb.INDEX_MINUTE, S0_POWERSOURCE )

        try:

            #flog.debug( inspect.stack()[0][3] + " record om toe te voegen = " + ts_possible_timestamp )

            if rec != None:
                sql = "insert into " + const.DB_POWERPRODUCTION_TAB + \
                    " (TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL )\
                    values ('" + ts_possible_timestamp + "'," + str(sqldb.INDEX_MINUTE) + "," + str(S0_POWERSOURCE) + ","\
                    + str(rec[7]) + "," + str(rec[8]) + "," + str(rec[7]+rec[8]) + ")"
                
                power_production_db.excute( sql )
                

        except Exception as e:
                flog.warning( inspect.stack()[0][3]+": sql insert error op table " + const.DB_POWERPRODUCTION_TAB + " ->" + str(e) )

    # make a set ist of missing records per period
    set_of_timestamps_hour   = set()
    set_of_timestamps_day    = set()
    set_of_timestamps_month  = set()
    set_of_timestamps_year   = set()

    for ts in all_possible_timestamps:
        set_of_timestamps_year.add(  ts[0:4]  + "-01-01 00:00:00" )
        set_of_timestamps_month.add( ts[0:7]  + "-01 00:00:00" )
        set_of_timestamps_day.add(   ts[0:10] + " 00:00:00" )
        set_of_timestamps_hour.add(  ts[0:13] + ":00:00" )

    #print ( len(set_of_timestamps_year) )
    #print ( len(set_of_timestamps_month) )
    #print ( len(set_of_timestamps_day) )
    #print ( len(set_of_timestamps_hour) )

    for ts in set_of_timestamps_hour:
        replaceRecordForAPeriod( ts, sqldb.INDEX_HOUR )
    for ts in set_of_timestamps_day:
        replaceRecordForAPeriod( ts, sqldb.INDEX_DAY )
    for ts in set_of_timestamps_month:
        replaceRecordForAPeriod( ts, sqldb.INDEX_MONTH )
    for ts in set_of_timestamps_year:
        replaceRecordForAPeriod( ts, sqldb.INDEX_YEAR )

    toc_process = time.perf_counter()
    flog.info( inspect.stack()[0][3] + ": invoegen van " + str(len(all_possible_timestamps)) + \
        " ontbrekende minuut records duurde " + f"totaal {toc_process - tic_process:0.4f} seconden" + \
            " process id = " + str(os.getpid()) )

    #flog.setLevel( logging.INFO )

########################################################
# minute processing                                    #
########################################################
def minuteProcessing( timestamp, tariff, puls_value_per_kwh ):
    
    rec_values = sqldb.POWER_PRODUCTION_REC
    timestamp_min = timestamp[0:16]+":00"
    #timestamp_min_minus_one = str( datetime.strptime(timestamp_min, "%Y-%m-%d %H:%M:%S") - timedelta(minutes=1 ) )
    #print( "timestamp=" +  timestamp  + " timestamp_min_minus_one=" + timestamp_min_minus_one )

    rec_values['TIMESTAMP']             = timestamp_min
    rec_values['TIMEPERIOD_ID']         = sqldb.INDEX_MINUTE
    rec_values['POWER_SOURCE_ID']       = S0_POWERSOURCE
    rec_values['PRODUCTION_KWH_TOTAL']  = 0
    rec_values['PRODUCTION_PSEUDO_KW']  = 0

    if ( tariff == 'P' ):
        rec_values['PRODUCTION_KWH_HIGH']       = float(puls_value_per_kwh)
        rec_values['PULS_PER_TIMEUNIT_HIGH']    = 1
        rec_values['PRODUCTION_KWH_HIGH_TOTAL'] = float(puls_value_per_kwh)
        rec_values['PRODUCTION_KWH_LOW']        = 0.0
        rec_values['PULS_PER_TIMEUNIT_LOW']     = 0.0
        rec_values['PRODUCTION_KWH_LOW_TOTAL']  = 0.0
    else:
        rec_values['PRODUCTION_KWH_HIGH']       = 0.0
        rec_values['PULS_PER_TIMEUNIT_HIGH']    = 0.0
        rec_values['PRODUCTION_KWH_HIGH_TOTAL'] = 0.0
        rec_values['PRODUCTION_KWH_LOW']        = float(puls_value_per_kwh)
        rec_values['PULS_PER_TIMEUNIT_LOW']     = 1
        rec_values['PRODUCTION_KWH_LOW_TOTAL']  = float(puls_value_per_kwh)

    # first check if there is a record for the current timestamp if so update the record
    rec = power_production_db.get_timestamp_record( timestamp_min, sqldb.INDEX_MINUTE, S0_POWERSOURCE )

    if rec != None: # there is an previous record for this timestamp, lets process this
        flog.debug(inspect.stack()[0][3]+": een bestaand record gevonden voor huidige timestamp " + timestamp_min )

        rec_values['PRODUCTION_KWH_HIGH']       = rec_values['PRODUCTION_KWH_HIGH']       + rec[3]
        rec_values['PULS_PER_TIMEUNIT_HIGH']    = rec_values['PULS_PER_TIMEUNIT_HIGH']    + rec[5]
        rec_values['PRODUCTION_KWH_HIGH_TOTAL'] = rec_values['PRODUCTION_KWH_HIGH_TOTAL'] + rec[7]
        
        rec_values['PRODUCTION_KWH_LOW']        = rec_values['PRODUCTION_KWH_LOW']       + rec[4]
        rec_values['PULS_PER_TIMEUNIT_LOW']     = rec_values['PULS_PER_TIMEUNIT_LOW']    + rec[6]
        rec_values['PRODUCTION_KWH_LOW_TOTAL']  = rec_values['PRODUCTION_KWH_LOW_TOTAL'] + rec[8] 

    else: # the record does not exist make the record
        flog.debug(inspect.stack()[0][3]+": GEEN bestaand record gevonden voor huidige timestamp, record maken voor timestamp " + timestamp_min )
        # try to find the last record to get the totals
        # SQL for previous record.

        sqlstr_high = "select PRODUCTION_KWH_HIGH_TOTAL, TIMESTAMP from powerproduction where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_MINUTE ) + \
        " and POWER_SOURCE_ID = " + \
        str( S0_POWERSOURCE ) + \
        " and PRODUCTION_KWH_HIGH_TOTAL > 0 order by timestamp desc limit 1"
        
        sqlstr_low = "select PRODUCTION_KWH_LOW_TOTAL, TIMESTAMP from powerproduction where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_MINUTE ) + \
        " and POWER_SOURCE_ID = " + \
        str( S0_POWERSOURCE ) + \
        " and PRODUCTION_KWH_LOW_TOTAL > 0 order by timestamp desc limit 1"

        try:
            sqlstr_high = " ".join (sqlstr_high.split() )
            rec_values_set_high = power_production_db.select_rec( sqlstr_high )
            if len( rec_values_set_high ) > 0:
                rec_values['PRODUCTION_KWH_HIGH_TOTAL'] = rec_values_set_high[0][0] + rec_values['PRODUCTION_KWH_HIGH']

            sqlstr_low = " ".join(sqlstr_low.split())
            rec_values_set_low = power_production_db.select_rec( sqlstr_low )
            if len( rec_values_set_low ) > 0:
                rec_values['PRODUCTION_KWH_LOW_TOTAL']  = rec_values_set_low[0][0] + rec_values['PRODUCTION_KWH_LOW']
        except Exception as e:
            flog.error( inspect.stack()[0][3]+": sql error(1) op table " + const.DB_POWERPRODUCTION_TAB + " ->" + str(e) )


    #print( rec_values )
    rec_values['PRODUCTION_KWH_TOTAL'] = rec_values['PRODUCTION_KWH_HIGH_TOTAL'] + rec_values['PRODUCTION_KWH_LOW_TOTAL']

    # calculate peseudo kilo watt, devide by 3600 to get the second value
    # format ( m3_val, '.4f' )
    if ( tariff == 'P' ):
        rec_values['PRODUCTION_PSEUDO_KW'] = rec_values['PRODUCTION_KWH_HIGH']
    else:
        rec_values['PRODUCTION_PSEUDO_KW'] = rec_values['PRODUCTION_KWH_LOW']  

    # limit number of digits te ease processing. 
    # and convert to Watt
    rec_values['PRODUCTION_PSEUDO_KW'] =  format( rec_values['PRODUCTION_PSEUDO_KW'] * 16.66, '.6f' ) 

    power_production_db.replace_rec_with_values( rec_values, sqldb.INDEX_MINUTE, S0_POWERSOURCE )

########################################################
# wait until a puls is detected and proces the puls    #
########################################################
def waitForPuls():
    global gpioPowerS0Puls
    
    #if pulsSimulator( probility = 0.05 ) == True:
    if gpioPowerS0Puls.gpioWaitRead() == True:
        flog.debug(inspect.stack()[0][3]+": Start van verwerken van S0 pulsen, verwerking is actief.")

        rt_status_db.timestamp( 109, flog ) # set timestamp of puls detected
        timestamp = util.mkLocalTimeString()

        #flog.debug( inspect.stack()[0][3]+": S0 puls gedetecteerd." )
        _id, puls_value_per_kwh, _label = config_db.strget( 127, flog )
        #puls_value_per_kwh = 1 #debug
         
        # get HIGH of LOW tariff P or D
        _id, tariff, _label, _security = rt_status_db.strget( 85, flog )
        #tariff = 'P'

        #store in buffer database and proces.
        #timestamp_buffer_list.append( [timestamp, puls_value_per_kwh,tariff ])

        # process minute records
        minuteProcessing( timestamp, tariff, puls_value_per_kwh )

        # add the other time periods
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_HOUR )
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_DAY )
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_MONTH )
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_YEAR )

    else:
        try:
            # warning, the puls must be off to update the gpio pin.
            gpioPowerS0Puls.check_pin_from_db()
            #flog.warning( inspect.stack()[0][3] + "## loop check"  ) 
        except:
            pass

def pulsSimulator(probility = 0.2 ):
    #flog.warning( inspect.stack()[0][3] + " is actief."  ) 
    time.sleep(1)
    if random.randrange(100) < probility*100:
        return True
    else:
        return False

########################################################
# copy to (flash)disk forced                           #
########################################################
def backupData():
    flog.debug( inspect.stack()[0][3] + ": Gestart" )
    process_lib.run_process( 
        cms_str='/p1mon/scripts/P1DbCopy --powerproduction2disk --forcecopy',
        use_shell=True,
        give_return_value=False,
        flog=flog 
        )

########################################################
# copy from ram to (flash)disk if the file does not    #
# exist.                                               #
########################################################
def DiskRestore():
   process_lib.run_process(
        cms_str='/p1mon/scripts/P1DbCopy --powerproduction2ram',
        use_shell=True,
        give_return_value=False,
        flog=flog 
        )

def saveExit(signum, frame):
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    signal.signal(signal.SIGINT, original_sigint)
    stop()

def stop():
    gpioPowerS0Puls.close()
    backupData()
    sys.exit(0)


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
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:"+str(e.args[0]))
        sys.exit(1)
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT, saveExit )
    Main(sys.argv[1:])
