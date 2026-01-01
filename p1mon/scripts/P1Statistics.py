# run manual with ./P1Statistics

import argparse
import const
import filesystem_lib
import inspect
import logger
import os
import pwd
import signal
import sqlite_lib
import sqldb
import sys
import sqldb_statistic # see tab for details
import time 
import json
from beautifultable import BeautifulTable


# programme name.
prgname = 'P1Statistics'
statistics_db   = sqldb_statistic.StatisticDb()
e_db_history    = sqldb.SqlDb2()
watermeter_db   = sqldb.WatermeterDBV2()
rt_status_db    = sqldb.rtStatusDb()

def Main( argv ):

    my_pid = os.getpid()

    parser = argparse.ArgumentParser(description='help information')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
    action='help', default=argparse.SUPPRESS,
    help='Calculate the aggregate functions (AVG,MAX,MIN,SUM) configured in the database or list the content to the screen.')

    parser.add_argument( '-p', '--process', 
    required=False,
    action="store_true",
    help="calculate the set statistics."
    )

    parser.add_argument( '-c', '--configure', 
    required=False,
    action="store_true",
    help="read mutated records from the status DB and update the configuration database"
    )

    parser.add_argument( '-l', '--list', 
    required=False,
    action="store_true",
    help="list all records in the database."
    )
    
    parser.add_argument( '-s', '--silent', 
    required=False,
    action="store_true",
    help="only log message from warning and above"
    )
    
    args = parser.parse_args()

    if args.silent:
        flog.setLevel( logger.logging.WARNING )


    flog.info( prgname + " start with process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": executed as user  -> " + pwd.getpwuid( os.getuid() ).pw_name )

    if args.list:
        list_database_content()
        flog.info( inspect.stack()[0][3] + ": " + prgname + " done.")
        sys.exit(0)

    if args.process:
        open_statistic_database()
        open_kwh_gas_database()
        open_water_database()
        x = range(1, 5)
        for n in x: # check all aggregate functions.
            calc_kwh_gas(mode=n)
            calc_water(mode=n)
        flog.info( inspect.stack()[0][3] + ": " + prgname + " done.")
        sys.exit(0)

    if args.configure:
        open_status_database() 
        open_statistic_database()
        try:
            update_db_config()
            rt_status_db.strset("", 138, flog) # clear the updates/inserts and deletes from the status file
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": update from database failed -> " + str(e) )
            sys.exit(1)

        flog.info( inspect.stack()[0][3] + ": " + prgname + " done.")
        sys.exit(0)
   
    flog.info( inspect.stack()[0][3] + ": done, no options selected, a waste of CPU cycles.")
    sys.exit(1)

###########################################################
# delete records no longer needed by the DELETE field     #
# set to 1.                                               # 
###########################################################
def delete_config_record(rec=None):
    flog.debug( inspect.stack()[0][3] + ": deletion of record = " + str( rec) )
    try:
        sql_delete = "delete from " + const.DB_STATISTICS_TAB + " where ID=" + str(rec['ID']) 
        flog.debug ( inspect.stack()[0][3] + ": sql_update -> " + str(  sql_delete ))
        statistics_db.execute( sql_delete )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": deletion for record with ID " + str(rec['DATA_ID']) + " failed. " + str(e) )
    flog.info( inspect.stack()[0][3] + ": deletion for record with ID " + str(rec['DATA_ID']) + " successful.")


###########################################################
# Create new records for aggregated functions             #
###########################################################
def insert_config_record(rec=None):
    flog.debug( inspect.stack()[0][3] + ": insert of record = " + str( rec) )
    try:
        sql_insert = "insert into " + const.DB_STATISTICS_TAB +  " (DATA_ID, ACTIVE, TIMESTAMP_START, TIMESTAMP_STOP, MODE) values (" + str(rec['DATA_ID']) + "," + str(rec['ACTIVE']) + ",'" + str(rec['TIMESTAMP_START']) + "','" + str(rec['TIMESTAMP_STOP']) + "'," + str(rec['MODE']) + ");"
        flog.debug ( inspect.stack()[0][3] + ": sql_update -> " + str( sql_insert ))
        statistics_db.execute( sql_insert )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": insert for new record failed. " + str(e) )
    flog.info( inspect.stack()[0][3] + ": insert for new record successful.")


###########################################################
# update and existing record by its ID number             #
###########################################################
def update_config_record(rec=None):

    try:
        flog.debug( inspect.stack()[0][3] + ": update of record = " + str( rec) )
        sql_update = "update " + const.DB_STATISTICS_TAB + " SET DATA_ID=" + str(rec['DATA_ID']) + ", ACTIVE=" + str(rec['ACTIVE']) + ", TIMESTAMP_START='" + str(rec['TIMESTAMP_START'])  + "', TIMESTAMP_STOP='" + str(rec['TIMESTAMP_STOP']) + "', MODE=" + str(rec['MODE']) + " where ID=" + str(rec['ID']) 
        flog.debug ( inspect.stack()[0][3] + ": sql_update -> " + str( sql_update ))
        statistics_db.execute( sql_update )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": update for record with ID " + str(rec['DATA_ID']) + " failed. " + str(e) )
    flog.info( inspect.stack()[0][3] + ": update for record with ID " + str(rec['DATA_ID']) + " successful.")


###########################################################
# read json records from the status DB and execute these  #
###########################################################
def update_db_config():
 
    # read JSON from status database to see if any update are pending
    try:
        _id, json_array, _label, _security = rt_status_db.strget( idn=138, flog=flog )
        flog.debug( inspect.stack()[0][3] + ": JSON from status DB = " + str( json_array ) )
        try:
            array = json.loads( json_array )
        except ValueError as e:
            flog.debug( inspect.stack()[0][3] + ": no JSON or valid JSON found ,this can be normal = " + str( e) )
            return
            
    except Exception as e:
        raise Exception("sql error on getting JSON from status table " + str(e) )

    try:
        flog.debug( inspect.stack()[0][3] + ": JSON = " + str(array) )
        for record in array: 
            #print( "record = ", record["ID"] )
            #print( record.get("ID"))

            if record.get("ID"):
                if record.get("DELETE") == 1:
                    delete_config_record(rec=record) # don't update a record destined for deletion 
                else:
                    update_config_record(rec=record)

            if record.get("temp_id"):
                insert_config_record(rec=record)

    except Exception as e:
        raise Exception("sql error on getting JSON from status table " + str(e) )

###########################################################
# select the data with the aggregate function and update  #
# the static table for water data                         #
###########################################################
def calc_water(mode=1): 
    
    #flog.setLevel( logger.logging.DEBUG )
    aggregate = get_aggregate_function(mode=mode)

    # get if any active statics records that are active 
    try:
        select_sql = "select DATA_ID, TIMESTAMP_START, TIMESTAMP_STOP from " + const.DB_STATISTICS_TAB + " WHERE MODE == " + str(mode) + " and ACTIVE == 1 and DATA_ID >14 and DATA_ID <20"
        flog.debug ( inspect.stack()[0][3] + ": sql: " + str(select_sql) )
   
        recs = statistics_db.select_rec( select_sql )
        flog.debug ( inspect.stack()[0][3] + ": sql query records found : " + str(recs) )
        if len(recs) > 0: # some records are active 

            for rec in recs:

                sql_timestamp_start = ""
                sql_timestamp_stop = "" 

                #flog.debug ( inspect.stack()[0][3] + ": record: " + str(rec) )
                if rec[1] != None:
                    sql_timestamp_start = str(rec[1]).strip()
                if rec[2] != None:
                    sql_timestamp_stop = str(rec[2]).strip()
                sql_table_name = get_table_name( data_id = int(rec[0]) )

                if len(sql_timestamp_start) > 3:
                        sql_timestamp_start = " and TIMESTAMP <= '" + str(sql_timestamp_start) + "'"
             
                if len(sql_timestamp_stop) > 3:
                     sql_timestamp_stop = " and TIMESTAMP <= '" + str(sql_timestamp_stop) + "'"

                #print ( int(rec[0]) )
                timeperiod_id = get_timeperiod_id(index=int(rec[0]))

                try:
                   
                    #sql_query = "select " + aggregate + "(VERBR_PER_TIMEUNIT) from " + const.DB_WATERMETERV2_TAB + " where timeperiod_id = " + timeperiod_id + sql_timestamp_start + sql_timestamp_stop
                    sql_query = "select " + aggregate + "(VERBR_PER_TIMEUNIT) from " + const.DB_WATERMETERV2_TAB + " where " + timeperiod_id + sql_timestamp_start + sql_timestamp_stop
                    flog.debug ( inspect.stack()[0][3] + ": sql_query -> " + str(sql_query ) )
                    rec_aggregate = watermeter_db.select_rec( sql_query )
                    #print ( rec_aggregate )

                    value = rec_aggregate[0][0]
                    if value == None:
                        value = 0  # reset the value if no data is found, otherwise the data is misunderstood

                    update_statistic_db(value=str(value), data_id=str(int(rec[0])), mode=mode) 

                except Exception as e:
                    flog.warning( inspect.stack()[0][3] + ": sql update error average record for table " + str(sql_table_name) + " ." + str(e) )

    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": sql error on getting statistic table records -> " + str(e) )
    
    #flog.setLevel( logger.logging.INFO )

###########################################################
# select the data with the aggregate function and update  #
# the static table with kwh and gas data                  #
###########################################################
def calc_kwh_gas(mode=1): 
    
    aggregate = get_aggregate_function(mode=mode)

    # get if any active statics records that are active 
    try:
        select_sql = "select DATA_ID, TIMESTAMP_START, TIMESTAMP_STOP from " + const.DB_STATISTICS_TAB + " WHERE MODE == " + str(mode) + " and ACTIVE == 1 and DATA_ID >0 and DATA_ID <15"
        flog.debug ( inspect.stack()[0][3] + ": sql: " + str(select_sql) )
   
        recs = statistics_db.select_rec( select_sql  )
        flog.debug ( inspect.stack()[0][3] + ": sql query records found : " + str(recs) )
        if len(recs) > 0: # some records are active 

            for rec in recs:

                sql_timestamp_start = ""
                sql_timestamp_stop = "" 

                #flog.debug ( inspect.stack()[0][3] + ": record: " + str(rec) )
                if rec[1] != None:
                    sql_timestamp_start = str(rec[1]).strip()
                if rec[2] != None:
                    sql_timestamp_stop = str(rec[2]).strip()
                sql_table_name = get_table_name( data_id = int(rec[0]) )

                if len(sql_timestamp_start) > 3:
                    sql_timestamp_start = " where timestamp >= '" + str(sql_timestamp_start) + "'"
                    if len(sql_timestamp_stop) > 3:
                        sql_timestamp_stop = " and TIMESTAMP <= '" + str(sql_timestamp_stop) + "'"
                else:
                    if len(sql_timestamp_stop) > 3:
                     sql_timestamp_stop = " where TIMESTAMP <= '" + str(sql_timestamp_stop) + "'"

                #print ( int(rec[0]) )
                field = get_db_fields_kwh_gas(index=int(rec[0]))

                try:
                    sql_query = "select " + aggregate + "(" + field + ") from " + sql_table_name + sql_timestamp_start + sql_timestamp_stop 
                    flog.debug ( inspect.stack()[0][3] + ": sql_query -> " + str(sql_query ) )
                    rec_aggregate = e_db_history.select_rec( sql_query )

                    flog.debug ( inspect.stack()[0][3] + ": rec_aggregate sql query records found : " + str(rec_aggregate) )

                    value = rec_aggregate[0][0]
                    if value == None:
                        value = 0  # reset the value if no data is found, otherwise the data is misunderstood
                    
                    update_statistic_db(value=str(value), data_id=str(int(rec[0])), mode=mode)

                except Exception as e:
                    flog.warning( inspect.stack()[0][3] + ": sql query error average record for table " + str(sql_table_name) + " ." + str(e) )

    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": sql error on getting statistic table records -> " + str(e) )


#############################################################
# SQL reusable update function                              #
#############################################################   
def update_statistic_db(value=None, data_id=None, mode=None):

    try:
        sql_update = "update " + const.DB_STATISTICS_TAB + " SET value = " + str(value) + ", UPDATED = '" + mkLocalTimeString() + "' where data_id == " + str(data_id) + " and mode == " + str(mode)
        flog.debug ( inspect.stack()[0][3] + ": sql_update -> " + str(sql_update ))
        statistics_db.execute( sql_update )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": sql update error average record for table " + str(sql_update) + " ." + str(e) )


########################################################
# generates a timestamp string of the current date and #
# and time in the format yyyy-mm-dd hh:mm:ss           #
########################################################
def mkLocalTimeString(): 
    t=time.localtime()
    return "%04d-%02d-%02d %02d:%02d:%02d"\
    % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)


########################################################
# get database index for the water table               #
########################################################
def get_timeperiod_id(index=0):

    ret_value = "INDEX_ERROR" 

    """
    timeperiod_id_indexed = {
        15:  "11",
        16:  "12"
        17:  "13",
        18:  "14",
        19:  "15",
    }
    """
    timeperiod_id_indexed = {
        15:  "timeperiod_id = 11 or timeperiod_id == 21",
        16:  "timeperiod_id = 12 or timeperiod_id == 22",
        17:  "timeperiod_id = 13 or timeperiod_id == 23",
        18:  "timeperiod_id = 14 or timeperiod_id == 24",
        19:  "timeperiod_id = 15 or timeperiod_id == 25"
    }

    try:
        ret_value = timeperiod_id_indexed[index]
    except Exception:
        pass

    return ret_value


########################################################
# get database field name needed                       #
########################################################
def get_db_fields_kwh_gas(index=0):

    ret_value = "FIELD_NOT_FOUND" 

    field_indexed = {
        1:  "VERBR_KWH_X",
        2:  "VERBR_KWH_X",
        3:  "VERBR_KWH_X",
        4:  "VERBR_KWH_X",
        5:  "VERBR_KWH_X",
        6:  "GELVR_KWH_X",
        7:  "GELVR_KWH_X",
        8:  "GELVR_KWH_X",
        6:  "GELVR_KWH_X",
        7:  "GELVR_KWH_X",
        9:  "GELVR_KWH_X",
        10: "GELVR_KWH_X",
        11: "VERBR_GAS_X",
        12: "VERBR_GAS_X",
        13: "VERBR_GAS_X",
        14: "VERBR_GAS_X"
    }

    try:
        ret_value = field_indexed[index]
    except Exception:
        pass

    return ret_value


########################################################
# get aggregate function by, index                     #
# on error "NO_TABEL_FOUND" is returned                #
########################################################
def get_aggregate_function( mode=1 ):

    ret_value = "FUNCTION_ERROR" 

    function_indexed = {
        1: "AVG",
        2: "MAX",
        3: "MIN",
        4: "SUM",
    }

    try:
        ret_value = function_indexed[mode]
    except Exception:
        pass

    return ret_value


########################################################
# get table name by, index                             #
# on error "NO_TABEL_FOUND" is returned                #
########################################################
def get_table_name( data_id=0 ):

    ret_value = "NO_TABEL_FOUND" 

    tab_indexed = {
        1: "e_history_min",
        2: "e_history_uur",
        3: "e_history_dag",
        4: "e_history_maand",
        5: "e_history_jaar",
        6: "e_history_min",
        7: "e_history_uur",
        8: "e_history_dag",
        9: "e_history_maand",
        10: "e_history_jaar",
        11: "e_history_uur",
        12: "e_history_dag",
        13: "e_history_maand",
        14: "e_history_jaar",
    }

    try:
        ret_value = tab_indexed[data_id]
    except Exception:
        pass

    return ret_value
    

########################################################
# Open the water information database                  #
########################################################
def open_water_database():
    try:
        watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database could not be opened." + const.FILE_DB_WATERMETERV2 + " message: " + str(e.args[0]) )

   
########################################################
# Open the kWh/Gas database                            #
########################################################
def open_kwh_gas_database():
    try:
        e_db_history.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_MIN_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database could not be opened." + const.FILE_DB_E_HISTORIE + " message: " + str(e.args[0]) )
        

#############################################################
# Open the statistic database and fill with default records #
#############################################################
def open_statistic_database():
    try:
        statistics_db.init( const.FILE_DB_STATISTICS, const.DB_STATISTICS_TAB , flog=flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database could not be opened." + const.FILE_DB_STATISTICS + " message: " + str(e.args[0]) )
        sys.exit(1)


#############################################################
# Open the status database                                  #
#############################################################
def open_status_database():
    try:
        rt_status_db.init( const.FILE_DB_STATUS, const.DB_STATUS_TAB , flog=flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database could not be opened." + const.FILE_DB_STATUS + " message: " + str(e.args[0]) )
        sys.exit(1)


###########################################################
# list the database to the screen                         #
###########################################################
def list_database_content():
    
    table = BeautifulTable()
    #table = BeautifulTable(maxwidth=130)

    slib = sqlite_lib.SqliteUtil()
    slib.init( db_pathfile=const.FILE_DB_STATISTICS, flog=flog )

    sql_query = slib.query_str( table=const.DB_STATISTICS_TAB, flog=flog, sortindex=1 ) 

    #rows_header_list = []
    records = slib.select_rec( sql_query )
    for rec in records:
        records_list = []
        for field in rec:
            records_list.append(field)
        #print ( records_list )
        table.rows.append( records_list) 
        #rows_header_list.append(str(len(table.rows)))

    if (len( records) ) != 0:
        list_of_columns = slib.table_structure_info(const.DB_STATISTICS_TAB)
        list_of_headers = []
        for idx, c in enumerate( list_of_columns ):
                list_of_headers.append(c['column_name']) 
        table.columns.header = list_of_headers
        #table.rows.header = rows_header_list
        table.set_style(BeautifulTable.STYLE_COMPACT)
        table.columns.width = [4,9,8,21,21,6,12,21]
        table.border.top = '_'
        table.border.bottom = '-'
        table.rows.separator = '-'
        print(table)
    else:
         print("No records in database, feeling depressed.")

#ALTER TABLE statistics DROP COLUMN SYSTEM_DEFAULT

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
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname ) 
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )

    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])


