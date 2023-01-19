#################################
# graad dagen lib               #
#################################
import const
import sqldb
import utiltimestamp

DEFAULT_ROOM_TEMPERATURE = 18.0


###############################################################
# try to update the graaddagen from available historical data #
###############################################################
class RecoveryGraaddagen():

    weer_history_db_uur     = sqldb.historyWeatherDB()
    weer_history_db_dag     = sqldb.historyWeatherDB()
    weer_history_db_maand   = sqldb.historyWeatherDB()
    weer_history_db_jaar    = sqldb.historyWeatherDB()

    def __init__( self, room_temperature=DEFAULT_ROOM_TEMPERATURE, flog=None ):
        self.flog = flog
        self.room_temperature = room_temperature

        # open van weer database voor historische weer uur
        try:
            self.weer_history_db_uur.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_UUR_TAB)
        except Exception as e:
            self.flog.critical( str(__class__.__name__) + ": database niet te openen(4)." + const.DB_WEATHER_UUR_TAB + ") melding:" + str(e.args[0]) )
            return
        self.flog.debug( str(__class__.__name__) + ": database tabel " + const.DB_WEATHER_UUR_TAB + " succesvol geopend." )

        # open van weer database voor historische weer dag
        try:
            self.weer_history_db_dag.init( const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_DAG_TAB)
        except Exception as e:
            self.flog.critical( str(__class__.__name__) + ": database niet te openen(5)." + const.DB_WEATHER_DAG_TAB + ") melding:" + str(e.args[0]) )
            return
        self.flog.debug( str(__class__.__name__) + ": database tabel "+const.DB_WEATHER_DAG_TAB + " succesvol geopend." )

        # open van weer database voor historische weer maand
        try:
            self.weer_history_db_maand.init(const.FILE_DB_WEATHER_HISTORIE, const.DB_WEATHER_MAAND_TAB)
        except Exception as e:
            self.flog.critical( str(__class__.__name__) + ": database niet te openen(6)."+const.DB_WEATHER_MAAND_TAB+") melding:"+str(e.args[0]) )
            return
        self.flog.debug( str(__class__.__name__) + ": database tabel " + const.DB_WEATHER_MAAND_TAB + " succesvol geopend.")

        # open van weer database voor historische weer jaar
        try:
            self.weer_history_db_jaar.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_JAAR_TAB)
        except Exception as e:
            self.flog.critical( str(__class__.__name__) + ": database niet te openen(7)."+const.DB_WEATHER_JAAR_TAB+") melding:"+str(e.args[0]) )
            return
        self.flog.debug( str(__class__.__name__) + ": database tabel " + const.DB_WEATHER_JAAR_TAB + " succesvol geopend." )

    ######################################################################
    # update DEGREE_DAYS column in the database. use the avg temperature #
    # stored in the database as reference                                #
    # only when avg temperature data is available a restore is possible  #
    ######################################################################
    def run( self ):

        self.flog.info( str(__class__.__name__) + ": Herstel van graaddagen gegevens gestart. Verwacht verwerkingstijd is ongeveer 1 minuut. Geduld aub." )
        self.flog.info( str(__class__.__name__) + ": Berekening gebaseerd op de ingestelde kamertemperatuur van " + str(self.room_temperature) + " graden Celsius " )
        
        # hour processing
        self.flog.info( str(__class__.__name__) + ": Herstel van uurgegevens gestart." )
        hour_records = self._get_avg_temperature_from_db( db=self.weer_history_db_uur, db_table_name=const.DB_WEATHER_UUR_TAB )
        for record in hour_records:
            try:
                graaddagen = calculate( avg_day_temperature=record[1], room_temperature=self.room_temperature,  timestring=record[0] )
                self._update_db_record( db=self.weer_history_db_uur, db_table_name=const.DB_WEATHER_UUR_TAB, timestamp=record[0], graaddagen=(round(graaddagen/24,3)) )
            except Exception as e:
                self.flog.warning( str(__class__.__name__) + ": update van graaddagen voor uur " +str(record[0]) + " " + str(e) ) 
        self.flog.info( str(__class__.__name__) + ": Herstel van uurgegevens gereed." )


        # day processing
        self.flog.info( str(__class__.__name__) + ": Herstel van daggegevens gestart." )
        day_records = self._get_avg_temperature_from_db( db=self.weer_history_db_dag, db_table_name=const.DB_WEATHER_DAG_TAB )
        for record in day_records:
            try:
                graaddagen =  calculate( avg_day_temperature=record[1], room_temperature=self.room_temperature, timestring=record[0] )
                self._update_db_record( db=self.weer_history_db_dag, db_table_name=const.DB_WEATHER_DAG_TAB, timestamp=record[0], graaddagen=graaddagen )
            except Exception as e:
                self.flog.warning( str(__class__.__name__) + ": update van graaddagen voor dag " +str(record[0][0:10]) + " " + str(e) ) 

        self.flog.info( str(__class__.__name__) + ": Herstel van daggegevens gereed." )


        # month processing
        # add all day graaddagen for the months that exist in the database
        self.flog.info( str(__class__.__name__) + ": Herstel van maandgegevens gestart." )
        timestamps = self._get_avg_temperature_from_db( db=self.weer_history_db_maand, db_table_name=const.DB_WEATHER_MAAND_TAB )
        # sum van dag waarden ophalen en dan een update doen van de maand tabel
        for timestamp in timestamps:
            sql_timestamp = str(timestamp[0][0:7])
            try:
                # update weer_history_uur set DEGREE_DAYS = 100 where TIMESTAMP = "2022-10-21 18:00:00"
                sqlstr = "update " + const.DB_WEATHER_MAAND_TAB +\
                         " set DEGREE_DAYS = (select round(sum(DEGREE_DAYS),3) from " + const.DB_WEATHER_DAG_TAB +\
                         " where substr(TIMESTAMP,1,7) = '" + sql_timestamp +  "') where substr(TIMESTAMP,1,7) = '" + sql_timestamp  + "'"
                sqlstr=" ".join( sqlstr.split() )
                self.flog.debug( str(__class__.__name__) + ": sql(update)=" + sqlstr)
                self.weer_history_db_maand.execute( sqlstr )
            except Exception as e:
                self.flog.warning( str(__class__.__name__) + ": update van graaddagen voor maand " +str(sql_timestamp) + " " + str(e) )
        self.flog.info( str(__class__.__name__) + ": Herstel van maandgegevens gereed." )
        

        # year processing
        # add all day graaddagen for the months that exist in the database
        self.flog.info( str(__class__.__name__) + ": Herstel van jaargegevens gestart." )
        timestamps = self._get_avg_temperature_from_db( db=self.weer_history_db_jaar, db_table_name=const.DB_WEATHER_JAAR_TAB )
        # sum van maand waarden ophalen en dan een update doen van de jaar tabel
        for timestamp in timestamps:
            sql_timestamp = str(timestamp[0][0:4])
            try:
                # update weer_history_uur set DEGREE_DAYS = 100 where TIMESTAMP = "2022-10-21 18:00:00"
                sqlstr = "update " + const.DB_WEATHER_JAAR_TAB +\
                         " set DEGREE_DAYS = (select round(sum(DEGREE_DAYS),3) from " + const.DB_WEATHER_MAAND_TAB +\
                         " where substr(TIMESTAMP,1,4) = '" + sql_timestamp +  "') where substr(TIMESTAMP,1,4) = '" + sql_timestamp  + "'"
                sqlstr=" ".join( sqlstr.split() )
                self.flog.debug( str(__class__.__name__) + ": sql(update)=" + sqlstr)
                self.weer_history_db_jaar.execute( sqlstr )
            except Exception as e:
                self.flog.warning( str(__class__.__name__) + ": update van graaddagen voor jaar " +str(sql_timestamp) + " " + str(e) )
        self.flog.info( str(__class__.__name__) + ": Herstel van jaargegevens gereed." ) 

        self.flog.info( str(__class__.__name__) + ": Herstel van graadagen gegevens gereed." )

    ######################################################################
    # sum the days in the database is > 0 then the values                #
    # are set before.                                                    #
    ######################################################################
    def check_if_set( self ):
        #select sum(degree_days) from weer_history_dag;
        try:
            # update weer_history_uur set DEGREE_DAYS = 100 where TIMESTAMP = "2022-10-21 18:00:00"
            sqlstr = "select sum(degree_days) from " + const.DB_WEATHER_DAG_TAB
            sqlstr=" ".join( sqlstr.split() )
            self.flog.debug( str(__class__.__name__) + ": sql =" + sqlstr)
            recs = self.weer_history_db_dag.select_rec( sqlstr )
            #print ( float(recs[0][0]) )
            if float(recs[0][0]) > 5:
                self.flog.info( str(__class__.__name__) + ": voldoende graadagen gevonden in de database.")
                return True
        except Exception as e:
            self.flog.error( str(__class__.__name__) + ": sql error bij het bepalen van of graadagen gezet zijn" + str(e) )

        return False


    ############################
    # internal class functions #
    ############################

    def _update_db_record( self, db=None, db_table_name=None, timestamp=None,  graaddagen=0):
        try:
            # update weer_history_uur set DEGREE_DAYS = 100 where TIMESTAMP = "2022-10-21 18:00:00"
            sqlstr = "update " + db_table_name + " set DEGREE_DAYS = " + str(graaddagen) + " where TIMESTAMP = '" + str(timestamp) + "'"
            sqlstr=" ".join( sqlstr.split() )
            self.flog.debug( str(__class__.__name__) + ": sql(update)=" + sqlstr)
            db.execute( sqlstr )
        except Exception as e:
            self.flog.error( str(__class__.__name__) + ": sql error(update van graaddagen)" + str(e) )
            return


    def _get_avg_temperature_from_db( self, db=None, db_table_name=None ):
        try:
            sqlstr = "select TIMESTAMP, TEMPERATURE_AVG from " + db_table_name
            sqlstr=" ".join(sqlstr.split())
            self.flog.debug( str(__class__.__name__) + ": sql(4)="+sqlstr)
            recs = db.select_rec( sqlstr )
            return recs
        except Exception as e:
            self.flog.error( str(__class__.__name__) + ": sql error(select timestamps en gemiddelde temperatuur)" + str(e) )
            return



####################### non class functions #######################

################################################
# calculate the graaddagen with three decimals #
# avg_day_temparture - the room_temperature    #
# for the nummer of graaddagen.                #
# when timestring is valid = not None          #
# depending on the month the values are        #
# multiplied by a value this called            #
# weighted graaddagen                          #
################################################
def calculate( avg_day_temperature=0, room_temperature=DEFAULT_ROOM_TEMPERATURE,  timestring=None ) -> float:

    try:
       
        #raise Exception( "TEST from calculate") 
        #print("# calc avg_day_temparture = ", avg_day_temparture )
        delta_temp = room_temperature - float(avg_day_temperature)
        #print("# calc delta_temp = ", delta_temp )

        if delta_temp < 0:
            return 0.0

        ##########################################
        # weighted degree days  values           #
        # month 4 - 9           value * 0.8      #
        # month 3 and 10        value * 1        #
        # month 11,12,1 and 2   value * 1.1      #
        ##########################################

        if timestring != None:
           
            t =utiltimestamp.utiltimestamp( timestring=timestring )
            if t.santiycheck() == False:
                raise Exception( "timestamp is niet correct") 
            month = int(t.getparts()[1])

            weight = 1.1 # default value 
            if month >=4 and month <=9:
                weight = 0.8
            if month == 3 or month == 10:
                weight = 1
        
        r = round( delta_temp * weight, 3 )
        #print ( "return value = " + str(r) )
       
        return r
    except Exception as e:
        raise Exception("onverwachte fout " + str(e) )