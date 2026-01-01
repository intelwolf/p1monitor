################################################
# processing of water records to database      #
################################################
import inspect
import const 
import time
import datetime

class P1Water2Database():

    
    ###########################################
    # init the class                          #
    ###########################################
    def __init__( self, water_database=None, serialdb=None, flog=None ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name 
        self.flog           = flog
        self.water_database = water_database
        self.serialdb       = serialdb
        self.INDEX_MINUTE  = 21
        self.INDEX_HOUR    = 22
        self.INDEX_DAY     = 23
        self.INDEX_MONTH   = 24
        self.INDEX_YEAR    = 25
        self.flog.debug( FUNCTION_TAG + ": init done.")
        self.SANITY_LITERS = 100 # when we process more than this amount per minute something goes wrong!

    ###############################################
    # read the serial records with the timestamp  #
    # and process the second values to minute     #
    # values                                      #
    ###############################################
    def process_serial_data(self, timestamp=None, timestamp_min_one=None ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name 

        liter_per_minute = 0
        
        try:
            self.flog.debug( FUNCTION_TAG + ": start processing for timestamp " + str(timestamp) + " - " + timestamp_min_one)

            ######################################################
            # get current and last minute to determine the delta #
            ######################################################

            # current minute
            try:
                sqlstr="select max(VERBR_WATER) from "+ const.DB_SERIAL_TAB + " where substr(timestamp,1,16) = '" + timestamp + "'"
                sqlstr = " ".join(sqlstr.split())
                self.flog.debug( FUNCTION_TAG + ": select data from serial DB current minute =" + str(sqlstr))
                rec_current=self.serialdb.select_rec(sqlstr)
                self.flog.debug( FUNCTION_TAG + ": content current minute =" + str(rec_current))
            except Exception as e:
                self.flog.error( FUNCTION_TAG + ": sql error for sql " +  str(sqlstr) + " -> " + str(e) )
                return 
            
            # previous minute
            try:
                sqlstr="select max(VERBR_WATER) from "+ const.DB_SERIAL_TAB + " where substr(timestamp,1,16) = '" + timestamp_min_one + "'"
                sqlstr = " ".join(sqlstr.split())
                self.flog.debug( FUNCTION_TAG + ": select data from serial DB previous minute =" + str(sqlstr))
                rec_previous=self.serialdb.select_rec(sqlstr)
                self.flog.debug( FUNCTION_TAG + ": content previous minute =" + str(rec_previous))
            except Exception as e:
                self.flog.error( FUNCTION_TAG + ": sql error for sql " +  str(sqlstr) + " -> " + str(e) )
                return 

            if rec_current[0][0] == None or rec_previous[0][0] == None: 
                self.flog.warning( FUNCTION_TAG + ": current or previous minute does not have a value. noting to do :(.")
                return 
            
            try:
                liter_per_minute = int( (float(rec_current[0][0])*1000) - (float(rec_previous[0][0])*1000) ) 
                self.flog.debug( FUNCTION_TAG + ": liter water delta is = " + str(liter_per_minute))
                if liter_per_minute > self.SANITY_LITERS:
                    self.flog.warning( FUNCTION_TAG + ": sanity warning more than " + str(self.SANITY_LITERS) + " are measured!, not processed.") 
                    return
            except Exception as e:
                self.flog.warning( FUNCTION_TAG + ": calculating liter between two timestamp problem. -> " + str(e) )
                return 

            try:
                if liter_per_minute != None:

                    if liter_per_minute < 0: 
                        raise Exception("Negative value for water usage?")
                    
                    sql_replace = "replace into " + const.DB_WATERMETERV2_TAB + \
                        " (TIMESTAMP, TIMEPERIOD_ID, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL )\
                        values ('"\
                        + timestamp + ":00'," + str(self.INDEX_MINUTE) + ", '0'" + "," + str(liter_per_minute) + "," + str(rec_current[0][0]) +  ")" 

                    sql_replace = " ".join ( sql_replace.split() ) 
                    self.flog.debug( FUNCTION_TAG + ": min to hour total sql =" + str(sql_replace))
                    
                    self.water_database.excute( sql_replace )   
            except Exception as e:
                    self.flog.warning( FUNCTION_TAG + ": inserting record in water database problem -> " + str(e) )
                    return 
         
        except Exception as e:
            self.flog.critical( FUNCTION_TAG + ": fatal processing water from serial records : "+ str(e.args[0]) )

        # minutes to hour
        self. _process_by_index( timestamp=timestamp, source_idx=self.INDEX_MINUTE ) 
        self. _process_by_index( timestamp=timestamp, source_idx=self.INDEX_HOUR ) 
        self. _process_by_index( timestamp=timestamp, source_idx=self.INDEX_DAY ) 
        self. _process_by_index( timestamp=timestamp, source_idx=self.INDEX_MONTH )
       

    ##################################################
    # read records from a period and insert the next #
    # into the next period                           #
    ##################################################
    def _process_by_index( self, timestamp=None, source_idx=None ):
       
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name 
   
        timestamp_slice = 0

        destination_idx = None
        if int(source_idx) == self.INDEX_MINUTE:
            timestamp_slice = 13
            destination_idx = self.INDEX_HOUR
            timestamp_str = timestamp[0:timestamp_slice]
            timestamp_sql = timestamp_str + ":00:00"
        elif source_idx == self.INDEX_HOUR:
            timestamp_slice = 10
            destination_idx = self.INDEX_DAY
            timestamp_str = timestamp[0:timestamp_slice]
            timestamp_sql = timestamp_str + " 00:00:00"
        elif source_idx == self.INDEX_DAY:
            timestamp_slice = 7
            destination_idx = self.INDEX_MONTH
            timestamp_str = timestamp[0:timestamp_slice]
            timestamp_sql = timestamp_str + "-01 00:00:00"
        elif source_idx == self.INDEX_MONTH:
            timestamp_slice = 4
            destination_idx = self.INDEX_YEAR
            timestamp_str = timestamp[0:timestamp_slice]
            timestamp_sql = timestamp_str + "-01-01 00:00:00"

        rec = None
        timestamp_str = timestamp[0:timestamp_slice]

        # Example: select sum(VERBR_PER_TIMEUNIT), max(VERBR_IN_M3_TOTAAL) from watermeter where TIMEPERIOD_ID = 21 and substr(timestamp,1,13) = '2025-12-07 16' 
        try:      
            sqlstr = "select sum(VERBR_PER_TIMEUNIT), max(VERBR_IN_M3_TOTAAL) from "+ const.DB_WATERMETERV2_TAB + " where TIMEPERIOD_ID = " + str(source_idx) + " and substr(timestamp,1," + str(timestamp_slice) + ") = '" + str(timestamp_str)  + "'"
            sqlstr = " ".join(sqlstr.split())
            self.flog.debug( FUNCTION_TAG + ": sql for selecting sum and max values " +  str(sqlstr) )
            rec=self.water_database.select_rec(sqlstr)
            self.flog.debug( FUNCTION_TAG + ": content sum and max =" + str(rec))

        except Exception as e:
            self.flog.error( FUNCTION_TAG + ": sql error for sql " +  str(sqlstr) + " -> " + str(e) )
            return 

        

        try:  
            if rec!= None:

                if rec[0][1] == const.NOT_SET:
                    self.flog.warning( FUNCTION_TAG + ": MAX value is set to default NOT SET value: " + str(const.NOT_SET) + " nothing processed." )
                    return
                
                sql_replace = "replace into " + const.DB_WATERMETERV2_TAB + \
                    " (TIMESTAMP, TIMEPERIOD_ID, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL )\
                    values ('"\
                    + timestamp_sql + "'," + str(destination_idx) + ", '0'" + "," + str(rec[0][0]) + "," + str(rec[0][1]) +  ")" 
                sql_replace = " ".join ( sql_replace.split() ) 
                self.flog.debug( FUNCTION_TAG + ": total sql = " + str(sql_replace))
                self.water_database.excute( sql_replace ) 
        except Exception as e:
            self.flog.warning( FUNCTION_TAG + ": inserting record in water database problem -> " + str(e)  + " sql = " + sql_replace)
        

    ########################################################
    # make remove / delete records from database           #
    # ######################################################
    def delete_records( self ):

        #timestamp = util.mkLocalTimeString()
        t=time.localtime()
        timestamp =  "%04d-%02d-%02d %02d:%02d:%02d"% (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

        try:
            sql_del_str = "delete from " + const.DB_WATERMETERV2_TAB +  " where TIMEPERIOD_ID = " + str(self.INDEX_MINUTE) + " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=31)) + "'"
            self.flog.debug( inspect.stack()[0][3] + ": deleting minute values. sql=" + sql_del_str ) 
            self.water_database.excute( sql_del_str )
        except Exception as e:
            self.flog.warning (inspect.stack()[0][3]+": deleting of minute values failed : " + str(e) )

        try:
            sql_del_str = "delete from " + const.DB_WATERMETERV2_TAB +  " where TIMEPERIOD_ID = " + str(self.INDEX_HOUR) + " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096)) + "'"
            self.flog.debug( inspect.stack()[0][3] + ": deleting hour values. sql=" + sql_del_str ) 
            self.water_database.excute( sql_del_str )
        except Exception as e:
            self.flog.warning (inspect.stack()[0][3]+": deleting of hour values failed : " + str(e) )

                 