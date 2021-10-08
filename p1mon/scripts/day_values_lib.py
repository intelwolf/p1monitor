####################################################
# day values etc,                                  #
####################################################

import const
import data_struct_lib
import inspect
import util
import sys

class dayMinMaxkW():

    def init( self, dbstatus=None, dbserial=None, flog=None ):
        self.dbstatus = dbstatus
        self.dbserial = dbserial
        self.flog     = flog
        self.kw_max_min = data_struct_lib.kw_min_max_record
        self._reset_data_set()

    ##############################################################
    # 1: read from max en min values from the serial database    #
    # 2: determine the timestamp for the values that are changed #
    # 3: update the DB fields that are changed                   #
    ##############################################################
    def kWupdateStatusDb( self) :

        # 0: current timestamps
        timestr=util.mkLocalTimeString()
        daytime_start_str = timestr[0:10]+" 00:00:00"
        daytime_end_str   = timestr[0:10]+" 23:59:59"

        #daytime_start_str = "2021-01-15 00:00:00"

        # force update when the day changes
        #sql = self.__create_sql_timestamp( 
        #            db_field='act_verbr_KW_170', 
        #            timestart=daytime_start_str, 
        #           timestop=daytime_end_str, 
        #            value=self.kw_max_min['max_verbr_KW_170'] ) 

        #rec_time = self.dbserial.select_rec( sql  )

        #print ( rec_time[0][0][0:10], timestr[0:10] )
        #if str(rec_time[0][0][0:10]) != timestr[0:10]: # an other day is upon us.
        #    self.flog.info( inspect.stack()[0][3] + ": Dag wissel gevonden vorige datum was " +   )
        #    self._reset_data_set()
        if len(str( self.kw_max_min['max_verbr_KW_170_timestamp'] )) > 9: # check that the time is set
            if str( self.kw_max_min['max_verbr_KW_170_timestamp'][0:10]) != timestr[0:10]: # an other day is upon us.
                self.flog.info( inspect.stack()[0][3] + ": Dag wissel gevonden vorige datum was " + self.kw_max_min['max_verbr_KW_170_timestamp'][0:10] )
                self._reset_data_set()
        
        #print( self.kw_max_min )

        try:
            sql_str = " select max(act_verbr_KW_170), min(act_verbr_KW_170), max(act_gelvr_KW_270), min(act_gelvr_KW_270) \
            from " + const.DB_SERIAL_TAB + " where timestamp >='" \
            + daytime_start_str + "' and timestamp <='" + daytime_end_str + "'"
            sql_str = " ".join(sql_str.split())

            self.flog.debug( inspect.stack()[0][3]+": SQL kw waarden=" + sql_str )

            rec_kw_waarden = self.dbserial.select_rec( sql_str )
 
            if rec_kw_waarden[0][0] > self.kw_max_min['max_verbr_KW_170']:
                self.kw_max_min['max_verbr_KW_170']        = rec_kw_waarden[0][0]
                self.kw_max_min['max_verbr_KW_170_change'] = True
            
            if rec_kw_waarden[0][1] < self.kw_max_min['min_verbr_KW_170']:
                self.kw_max_min['min_verbr_KW_170']        = rec_kw_waarden[0][1]
                self.kw_max_min['min_verbr_KW_170_change'] = True

            if rec_kw_waarden[0][2] > self.kw_max_min['max_gelvr_KW_270']:
                self.kw_max_min['max_gelvr_KW_270'] = rec_kw_waarden[0][2]
                self.kw_max_min['max_gelvr_KW_270_change'] = True
            
            if rec_kw_waarden[0][3] < self.kw_max_min['min_gelvr_KW_270']:
                self.kw_max_min['min_gelvr_KW_270'] = rec_kw_waarden[0][3]
                self.kw_max_min['min_gelvr_KW_270_change'] = True

        except Exception as e:
            self.flog.error(inspect.stack()[0][3]+": waarde query = "+ str(e.args[0]) )
            return

        # update timestamps and values when needed.
        try:

            if self.kw_max_min['max_verbr_KW_170_change'] == True:
                sql = self.__create_sql_timestamp( 
                    db_field='act_verbr_KW_170', 
                    timestart=daytime_start_str, 
                    timestop=daytime_end_str, 
                    value=self.kw_max_min['max_verbr_KW_170'] ) 
                #print ( sql )
                rec_time = self.dbserial.select_rec( sql  )

                # update the status database
                self.dbstatus.strset( str( self.kw_max_min['max_verbr_KW_170']), 1 ,self.flog )
                self.dbstatus.strset( rec_time[0][0], 2, self.flog )
                self.kw_max_min['max_verbr_KW_170_change']    = False
                self.kw_max_min['max_verbr_KW_170_timestamp'] = str(rec_time[0][0])
                self.flog.info(inspect.stack()[0][3]+": max_verbr_KW_170 aangepast naar " + str( self.kw_max_min['max_verbr_KW_170']) + " kW. Voor tijdstip " + str(self.kw_max_min['max_verbr_KW_170_timestamp']) )


            if self.kw_max_min['min_verbr_KW_170_change'] == True:
                sql = self.__create_sql_timestamp( 
                    db_field='act_verbr_KW_170', 
                    timestart=daytime_start_str, 
                    timestop=daytime_end_str, 
                    value=self.kw_max_min['min_verbr_KW_170'] ) 
                #print ( sql )
                rec_time = self.dbserial.select_rec( sql  )

                # update the status database
                self.dbstatus.strset( str(self.kw_max_min['min_verbr_KW_170']), 113 ,self.flog )
                self.dbstatus.strset( rec_time[0][0], 114, self.flog )
                self.kw_max_min['min_verbr_KW_170_change']    = False
                self.kw_max_min['min_verbr_KW_170_timestamp'] = str(rec_time[0][0])
                self.flog.info(inspect.stack()[0][3]+": min_verbr_KW_170 aangepast naar " + str( self.kw_max_min['min_verbr_KW_170'] ) + " kW. Voor tijdstip " + self.kw_max_min['min_verbr_KW_170_timestamp'] )


            if self.kw_max_min['max_gelvr_KW_270_change'] == True:
                sql = self.__create_sql_timestamp( 
                    db_field='act_gelvr_KW_270', 
                    timestart=daytime_start_str, 
                    timestop=daytime_end_str, 
                    value=self.kw_max_min['max_gelvr_KW_270'] )
                #print ( sql )
                rec_time = self.dbserial.select_rec( sql  )
            
                # update the status database
                self.dbstatus.strset( str( self.kw_max_min['max_gelvr_KW_270']), 3 ,self.flog )
                self.dbstatus.strset( rec_time[0][0], 4, self.flog )
                self.kw_max_min['max_gelvr_KW_270_change']    = False
                self.kw_max_min['max_gelvr_KW_270_timestamp'] = str(rec_time[0][0])
                self.flog.info(inspect.stack()[0][3]+": max_gelvr_KW_270 aangepast naar " + str( self.kw_max_min['max_gelvr_KW_270']) + " kW. Voor tijdstip " + str(self.kw_max_min['max_gelvr_KW_270_timestamp']) )
            
            if self.kw_max_min['min_gelvr_KW_270_change'] == True:
                sql = self.__create_sql_timestamp( 
                    db_field='act_gelvr_KW_270', 
                    timestart=daytime_start_str, 
                    timestop=daytime_end_str, 
                    value=self.kw_max_min['min_gelvr_KW_270'] ) 
                #print ( sql )
                rec_time = self.dbserial.select_rec( sql  )

                # update the status database
                self.dbstatus.strset( str( self.kw_max_min['min_gelvr_KW_270']), 115 ,self.flog )
                self.dbstatus.strset( rec_time[0][0], 116, self.flog )
                self.kw_max_min['min_gelvr_KW_270_change']    = False
                self.kw_max_min['min_gelvr_KW_270_timestamp'] = str(rec_time[0][0])
                self.flog.info(inspect.stack()[0][3]+": min_gelvr_KW_270 aangepast.naar " + str( self.kw_max_min['min_gelvr_KW_270']) + " kW. Voor tijdstip " + str(self.kw_max_min['min_gelvr_KW_270_timestamp']) )

        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": Melding= "+ str (e.args[0]) )
            return

    ###############################################################
    # reset change flags to force an update by setting it to true #
    ###############################################################
    def _reset_data_set( self, value=True ):
        self.kw_max_min['max_verbr_KW_170_change'] = value
        self.kw_max_min['min_verbr_KW_170_change'] = value
        self.kw_max_min['max_gelvr_KW_270_change'] = value
        self.kw_max_min['min_gelvr_KW_270_change'] = value
        self.kw_max_min['max_verbr_KW_170']        = 0.0
        self.kw_max_min['min_verbr_KW_170']        = const.NOT_SET
        self.kw_max_min['max_gelvr_KW_270']        = 0.0
        self.kw_max_min['min_gelvr_KW_270']        = const.NOT_SET


    #############################################
    # make the reused SQL string                #
    ############################################3
    def __create_sql_timestamp(self, db_field=None, timestart=None, timestop=None, value=None ):

        sql = "select min(timestamp) from " + const.DB_SERIAL_TAB +\
        " where timestamp >='" + timestart + "' and timestamp <= '"\
        + timestop + "' and " + db_field + " = " + str( value )
        sql = " ".join( sql.split() )
        return sql
