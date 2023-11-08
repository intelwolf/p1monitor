# run manual with ./P1WatermeterV2

import const
import datetime
import filesystem_lib
import inspect
import gpio
import logger
import os
import signal
import sys
import random
import time
import datetime
import sqldb
import multiprocessing
import process_lib
import util

# programme name.
prgname = 'P1WatermeterV2'

rt_status_db            = sqldb.rtStatusDb()
config_db               = sqldb.configDB()
watermeter_db           = sqldb.WatermeterDBV2()

gpioWaterPuls           = gpio.gpioDigtalInput()

timestamp               = util.mkLocalTimeString()

#timestamp_buffer_list   = [] 
prg_is_active           = True
mp_queue_1              = multiprocessing.Queue()

QUEUE_CMD_START  = "START"

def Main(argv): 
    global timestamp 

    # TODO test regels mogen weg.
    #x = datetime.datetime.strptime( "2022-06-24 22:11:03", "%Y-%m-%d %H:%M:%S")
    # y = datetime.timedelta( minutes=1 )
    # sys.exit()

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

    # open van watermeter database
    try:
        watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(3)." + const.FILE_DB_WATERMETERV2 + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

    filesystem_lib.set_file_permissions( filepath=const.FILE_DB_WATERMETERV2, permissions="664" )

    # database defrag 
    watermeter_db.defrag()
   
    # set proces gestart timestamp
    rt_status_db.timestamp( 98,flog )

    try:
        gpioWaterPuls.init( 97, config_db ,flog )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": GPIO pin voor watermeter niet te openen. " + str(e.args[0])  ) 

    setFileFlags()
    delete_records() 
    startBackgroundDeamon() 

    while True:

        _id, run_status, _label = config_db.strget( 96, flog )
        if int(run_status) == 0: # stop process
            flog.info(inspect.stack()[0][3]+": programma is niet als actief geconfigureerd, programma wordt gestopt.")
            stop()

        #flog.debug( inspect.stack()[0][3]+": loop " )
        checkAndInsertMinuteRecord()
        
        #check if GPIO pin is set or else wait for a valid pin
        while gpioWaterPuls.gpio_pin == None:
            flog.debug( inspect.stack()[0][3] + ": GPIO pin wordt opnieuw geprobeerd.") 
            time.sleep( 30 ) # wait to limit load
            try:
                gpioWaterPuls.init( 97, config_db ,flog )
            except:
                pass

        
        waitForPuls()
        

#######################################################
# set the file rights of the database files           #
#######################################################
def setFileFlags():
    util.setFile2user( const.FILE_DB_WATERMETERV2, 'p1mon' )
    _head,tail = os.path.split( const.FILE_DB_WATERMETERV2 )
    util.setFile2user( const.DIR_FILEDISK+tail, 'p1mon' )

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
        sql_select = "select sum(PULS_PER_TIMEUNIT), sum(VERBR_PER_TIMEUNIT), max(VERBR_IN_M3_TOTAAL) FROM " +\
            const.DB_WATERMETERV2_TAB +\
            " where TIMEPERIOD_ID = " + select_period +\
            " and substr(timestamp,1," + str(substr_index) + ") = '" + select_timestamp + "'"
        sql_select = " ".join ( sql_select.split() )
        flog.debug( inspect.stack()[0][3]+": sql select  = "  + sql_select )   
        rec = watermeter_db.select_rec( sql_select ) 

        if rec[0][0] != None:
            sql_replace = "replace into " + const.DB_WATERMETERV2_TAB + \
                " (TIMESTAMP, TIMEPERIOD_ID, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL )\
                   values ('"\
                   + replace_timestamp + "', " + replace_period + ", "\
                   + str(rec[0][0]) + ", " + str(rec[0][1]) + ", " + str(rec[0][2]) \
                   +  ")" 

            # 
            sql_replace = " ".join ( sql_replace.split() ) 
            #flog.debug( inspect.stack()[0][3]+": sql replace  = "  + sql_replace  )
            watermeter_db.excute( sql_replace )

    except Exception as e:
        flog.warning( inspect.stack()[0][3]+": sql error voor timestamp  " + timestamp +  " -> " + str(e) )

########################################################
# make remove / delete records from database           #
# ######################################################
def delete_records():

    timestamp = util.mkLocalTimeString()

    try:
        sql_del_str = "delete from " + const.DB_WATERMETERV2_TAB + \
        " where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_MINUTE ) + \
        " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=31)) + "'"
        flog.debug( inspect.stack()[0][3] + ": wissen van minuten. sql=" + sql_del_str ) 
        watermeter_db.excute( sql_del_str )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van oude minuten records gefaald: " + str(e) )

    try:
        sql_del_str = "delete from " + const.DB_WATERMETERV2_TAB + \
        " where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_HOUR ) + \
        " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096)) + "'"
        flog.debug( inspect.stack()[0][3] + ": wissen van uren. sql=" + sql_del_str ) 
        watermeter_db.excute( sql_del_str )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van oude minuten records gefaald: " + str(e) )

    
    """ 
    # removed in version 2.3.0
    # new standard retention is minutes 31 days, hours 1096 days, days, months, years unlimted. 
    try:
        sql_del_str = "delete from " + const.DB_WATERMETERV2_TAB + \
        " where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_DAY ) + \
        " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096)) + "'"
        flog.debug( inspect.stack()[0][3] + ": wissen van dagen. sql=" + sql_del_str ) 
        watermeter_db.excute( sql_del_str )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van oude minuten records gefaald: " + str(e) )
    """

########################################################
# make a minute record to prevent gaps in the data set #
# and prevent expensive dataset changes                #
# functie is run as a seperate process                 #
########################################################
def checkAndInsertMinuteRecord():
    #print( "## checkAndInsertMinuteRecord()" )

    dt = datetime.datetime.now()
    timestamp = datetime.datetime.strftime( dt , "%Y-%m-%d %H:%M:00")

    #print ("# " + str( dt.second  ) )
    try:
        #if dt.second == 0:
        if dt.second > 30: # limit work.

            flog.debug( inspect.stack()[0][3]+": leeg record aanmaken om een data gap te voorkomen." )
            timetamp_minus_one_minute =  datetime.datetime.strftime( dt - datetime.timedelta( minutes=1 ), "%Y-%m-%d %H:%M:00")
            #print (" timetamp_minus_one_minute = " + str(timetamp_minus_one_minute) )
            rec = watermeter_db.get_timestamp_record( timetamp_minus_one_minute, sqldb.INDEX_MINUTE )
            #print (" record minus one = " + str(rec) )
            #print ( "# " + str(rec) )

            if rec != None:
                #timestamp = datetime.strftime( dt , "%Y-%m-%d %H:%M:00")
                #sql = "insert into " + const.DB_WATERMETERV2_TAB + " (TIMESTAMP, TIMEPERIOD_ID, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL ) " +\
                #   " values ('" + timestamp + "'," + str(sqldb.INDEX_MINUTE) + ","  + str(rec[2]) + "," + str(rec[3]) + "," + str(rec[4]) + ")"

                sql = "insert into " + const.DB_WATERMETERV2_TAB + " (TIMESTAMP, TIMEPERIOD_ID, VERBR_IN_M3_TOTAAL ) " +\
                    " values ('" + timestamp + "'," + str(sqldb.INDEX_MINUTE) + "," + str(rec[4]) + ")"

                # check if there is no record 
                rec_exist = watermeter_db.get_timestamp_record( timestamp, sqldb.INDEX_MINUTE )
                if rec_exist == None:
                    #print ( "sql insert = " + sql )
                    watermeter_db.excute( sql )

                #rec_test = watermeter_db.get_timestamp_record( timestamp, sqldb.INDEX_MINUTE )
                #print ( "sql check = " + str(rec_test) )

                #print ("# update. water")

                replaceRecordForAPeriod( timestamp, sqldb.INDEX_HOUR )
                replaceRecordForAPeriod( timestamp, sqldb.INDEX_DAY )
                replaceRecordForAPeriod( timestamp, sqldb.INDEX_MONTH )
                replaceRecordForAPeriod( timestamp, sqldb.INDEX_YEAR )

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
            item = mp_queue_1.get( block=True, timeout=10 )
            if item == QUEUE_CMD_START:
                flog.debug ( inspect.stack()[0][3] + " queue lengte verminderd met 1, aantal entries = " + str( mp_queue_1.qsize()) )
                addMissingRecords()
                #print("# test")
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

    missing_records_count   = 0
    max_timestamp           = ""
    min_timestamp           = ""
    tic_process             = time.perf_counter()

    try:
        # Number of minutes calculated by finding the seconds and deviding by 60.
        # When count is biger then 0 we are missing some minutes.
        # count -1 is for the minute offset.
        sql = "select (strftime('%s',max(timestamp)) - strftime('%s',min(timestamp)))/60 - (count()-1), max(timestamp), min(timestamp) from " +\
        const.DB_WATERMETERV2_TAB + " where TIMEPERIOD_ID = " +\
        str(sqldb.INDEX_MINUTE)
        sql = " ".join ( sql.split() )
        flog.debug( inspect.stack()[0][3] + " sql =" + str(sql))
        rec = watermeter_db.select_rec( sql )
        missing_records_count   = rec[0][0] # number of minute records missing in the database.
        max_timestamp           = rec[0][1] # most current timestamp.
        min_timestamp           = rec[0][2] # oldest timestamp.
        #print ( sql )
    except Exception as e:
        flog.error( inspect.stack()[0][3]+": sql error voor record gap analyse op table " + const.DB_WATERMETERV2_TAB + " ->" + str(e) )

    flog.debug( inspect.stack()[0][3] + " aantal records in database dat ontbreekt = " + str(missing_records_count) +\
         " timestamp min = " + str(min_timestamp) + " timestamp max = " + str(max_timestamp))

    if missing_records_count == None:
        flog.debug( inspect.stack()[0][3] + ": gestopt geen records toegevoegd (database is leeg)." ) 
        return

    if missing_records_count < 1:
        flog.debug( inspect.stack()[0][3] + ": gestopt geen ontbrekende records." ) 
        return

    #flog.info( inspect.stack()[0][3] + ": gestart. process id = " + str(os.getpid()) ) # updated 2.0.0

    # build a set of records that are in the database
    if missing_records_count > 0:
        try:
            sql = "select timestamp from " + const.DB_WATERMETERV2_TAB + " where timeperiod_id = " +\
            str(sqldb.INDEX_MINUTE) +\
            " order by timestamp desc"
            sql = " ".join ( sql.split() )
            #print ( sql )
            timestamp_list_from_db = watermeter_db.select_rec( sql )
        
            timestamp_set_from_db = set()
            for i in range(len(timestamp_list_from_db)):
                ##print ( timestamp_list_from_db[i][0]  )
                timestamp_set_from_db.add( timestamp_list_from_db[i][0] )
            

            flog.debug( inspect.stack()[0][3] + " maximaal aantal records in database = " + str( len(timestamp_list_from_db) ) )
            #print ( "records in database dat ontbreekt=" + str( timestamp_list_from_db ) )
        except Exception as e:
            flog.error( inspect.stack()[0][3]+": sql error voor het vinden van ontbrekende records " + const.DB_WATERMETERV2_TAB + " ->" + str(e) )
    else:
        flog.info( inspect.stack()[0][3] + ": gestopt geen records toegevoegd (fase 1)." ) 
        return

    #print ( timestamp_list_from_db[0] )
    #print ( timestamp_list_from_db[len(timestamp_list_from_db)-1] )
    # sys.exit()

    # make a list of all possible timestamps 
    dt_tmp = datetime.datetime.strptime( min_timestamp, "%Y-%m-%d %H:%M:%S")
    all_possible_timestamps_set = set()
    while True:
        #print ("adding " + datetime.strftime( dt_tmp, "%Y-%m-%d %H:%M:%S") )
        #time.sleep(5)
        all_possible_timestamps_set.add ( str( dt_tmp ) )
        dt_tmp = dt_tmp + datetime.timedelta( minutes=1 )
        if datetime.strftime( dt_tmp, "%Y-%m-%d %H:%M:%S") > max_timestamp:
            break
    
    #print( all_possible_timestamps )
    flog.debug( inspect.stack()[0][3] + " maximaal aantal mogelijke timestamps = " + str( len( all_possible_timestamps_set) ) )

    #fiter_set = set()
    filter_set = all_possible_timestamps_set.difference( timestamp_set_from_db )
     
    #tic_filter = time.perf_counter()
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

    toc_filter = time.perf_counter()
    #print( all_possible_timestamps )
    flog.debug( inspect.stack()[0][3] + " aantal mogelijke timestamps na filtering = " + str( len(all_possible_timestamps) ) + f" totaal {toc_filter - tic_filter:0.4f} seconden" )
    """
    
    #print ( "all_possible_timestamps = " ,all_possible_timestamps)
    #print ("----")
    #print ( "filter_set = "              ,filter_set)
    #print ("----")
    all_possible_timestamps = list(filter_set)
    all_possible_timestamps.sort()
    #print ( "filter_list = "              ,filter_list)
    #print ("----")
    #print ("done")

    #sys.exit()

    if len( all_possible_timestamps ) < 1 :
        flog.info( inspect.stack()[0][3] + ": gestopt geen records toegevoegd (fase 2)." ) 
        return

    for ts_possible_timestamp in all_possible_timestamps:

        # first find the previous record
        ts_previous = datetime.datetime.strptime( ts_possible_timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta( minutes=1 )
        rec = watermeter_db.get_timestamp_record( str(ts_previous), sqldb.INDEX_MINUTE )

        try:

            #flog.debug( inspect.stack()[0][3] + " record om toe te voegen = " + ts_possible_timestamp )

            if rec != None:

                sql = "insert into " + const.DB_WATERMETERV2_TAB + \
                    " (TIMESTAMP, TIMEPERIOD_ID, VERBR_IN_M3_TOTAAL )\
                    values ('" + ts_possible_timestamp + "'," + str(sqldb.INDEX_MINUTE) + "," + str(rec[4]) + ")"
                watermeter_db.excute( sql )

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
    #flog.setLevel( logging.DBUG )

########################################################
# minute processing                                    #
########################################################
#def minuteProcessing( timestamp, tariff, puls_value_per_kwh ):
def minuteProcessing( timestamp, puls_value_per_liter ):
    
    rec_values = sqldb.WATERMETER_REC
    timestamp_min = timestamp[0:16]+":00"
   
    rec_values['TIMESTAMP']             = timestamp_min
    rec_values['TIMEPERIOD_ID']         = sqldb.INDEX_MINUTE
    rec_values['PULS_PER_TIMEUNIT']     = 1
    rec_values['VERBR_PER_TIMEUNIT']    = float( puls_value_per_liter )
    rec_values['VERBR_IN_M3_TOTAAL']    = float( puls_value_per_liter ) / 1000

    # first check if there is a record for the current timestamp if so update the record
    rec = watermeter_db.get_timestamp_record( timestamp_min, sqldb.INDEX_MINUTE )

    if rec != None: # there is an previous record for this timestamp, lets process this
        flog.debug(inspect.stack()[0][3]+": een bestaand record gevonden voor huidige timestamp " + timestamp_min )

        rec_values['PULS_PER_TIMEUNIT']   = rec_values['PULS_PER_TIMEUNIT']  + rec[2]
        rec_values['VERBR_PER_TIMEUNIT']  = rec_values['VERBR_PER_TIMEUNIT'] + rec[3]
        rec_values['VERBR_IN_M3_TOTAAL']  = rec_values['VERBR_IN_M3_TOTAAL'] + rec[4]
        
    else: # the record does not exist make the record
        flog.debug(inspect.stack()[0][3]+": GEEN bestaand record gevonden voor huidige timestamp, record maken voor timestamp " + timestamp_min )
        # try to find the last record to get the totals
        # SQL for previous record.

        sqlstr = "select VERBR_IN_M3_TOTAAL, TIMESTAMP from " + const.DB_WATERMETERV2_TAB + " where TIMEPERIOD_ID = " + \
        str( sqldb.INDEX_MINUTE ) + " and VERBR_IN_M3_TOTAAL > 0 order by timestamp desc limit 1"

        try:
            sqlstr = " ".join(sqlstr.split() )
            rec_values_set = watermeter_db.select_rec( sqlstr )
            if len( rec_values_set ) > 0:
                rec_values['VERBR_IN_M3_TOTAAL'] = rec_values_set[0][0] + rec_values['VERBR_IN_M3_TOTAAL']

        except Exception as e:
            flog.error( inspect.stack()[0][3]+": sql error(1) op table " + const.DB_WATERMETERV2_TAB + " ->" + str(e) )

    rec_values['VERBR_IN_M3_TOTAAL'] = format( rec_values['VERBR_IN_M3_TOTAAL'], '.6f')

    #watermeter_db.replace_rec_with_values( rec_values, sqldb.INDEX_MINUTE )
    watermeter_db.replace_rec_with_values( rec_values )
    flog.debug( inspect.stack()[0][3] + "replace record values = " + str(rec_values) )

########################################################
# wait until a puls is detected and proces the puls    #
########################################################
def waitForPuls():
    global gpioWaterPuls
    
    #if pulsSimulator( probility = 0.005 ) == True: # 
    if gpioWaterPuls.gpioWaitRead() == True:
        flog.debug(inspect.stack()[0][3]+": Start van verwerken van Watermeter pulsen, verwerking is actief.")

        rt_status_db.timestamp( 90, flog ) # set timestamp of puls detected
        timestamp = util.mkLocalTimeString()

        #flog.debug( inspect.stack()[0][3]+": water puls gedetecteerd." )
        _id, puls_value_per_liter, _label = config_db.strget( 98, flog ) 

        # process minute records
        minuteProcessing( timestamp, puls_value_per_liter )

        # add the other time periods
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_HOUR )
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_DAY )
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_MONTH )
        replaceRecordForAPeriod( timestamp, sqldb.INDEX_YEAR )

        # clean the database
        delete_records()

    else:
        try:
            # warning, the puls must be off to update the gpio pin.
            gpioWaterPuls.check_pin_from_db()
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
        cms_str = '/p1mon/scripts/P1DbCopy --watermeter2disk --forcecopy',
        use_shell=True,
        give_return_value=True,
        flog=flog
    )



########################################################
# copy from ram to (flash)disk if the file does not    #
# exist.                                               #
########################################################
def DiskRestore():
   #os.system("/p1mon/scripts/P1DbCopy.py --watermeter2ram") 1.8.0 upgrade
   process_lib.run_process( 
        cms_str = '/p1mon/scripts/P1DbCopy --watermeter2ram',
        use_shell=True,
        give_return_value=True,
        flog=flog
    )

def saveExit(signum, frame):
    flog.info( inspect.stack()[0][3] + " SIGINT ontvangen, gestopt." )
    signal.signal( signal.SIGINT, original_sigint )
    stop()

def stop():
    gpioWaterPuls.close()
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
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(1)
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT, saveExit )
    Main(sys.argv[1:])
