# run manual with ./P1Weather
import argparse
import base64
import const
import datetime
import crypto3
import graaddagen_lib
import json
import inspect
import logger
import os
import signal
import sys
import sqldb
import pwd
import time
import datetime
import urllib.request
import util

prgname = 'P1Weather'
logfilename = const.DIR_FILELOG + prgname + '.log'
weather_api_language = 'nl'

rt_status_db            = sqldb.rtStatusDb()
config_db               = sqldb.configDB()
weer_db                 = sqldb.currentWeatherDB()
weer_history_db_uur     = sqldb.historyWeatherDB()
weer_history_db_dag     = sqldb.historyWeatherDB()
weer_history_db_maand   = sqldb.historyWeatherDB()
weer_history_db_jaar    = sqldb.historyWeatherDB()

def Main():

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument( '-r', '--recover',
        required=False,
        action="store_true",
        help="recover wordt alleen uitgevoerd als de graaddagen nog niet eerder gezet zijn." )

    parser.add_argument( '-rf', '--recoverforced', 
        required=False,
        action="store_true",
        help="recoverforced (re)set de graaddagen altijd." )

    parser.add_argument( '-g', '--getweather',
        required=False,
        action="store_true",
        help="lees de de laaste weerdata van de bron en update de database." )

    args = parser.parse_args()

    # open van config database
    # door ander cli opties nodig

    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    if args.getweather == True:
        # open van status database 
        try:
            rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

        # open van weer database voor huidige weer
        try:
            weer_db.init(const.FILE_DB_WEATHER ,const.DB_WEATHER_TAB)
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": database niet te openen(3)."+const.DB_WEATHER_TAB+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_TAB+" succesvol geopend.")

        # open van weer database voor historische weer uur      
        try:
            weer_history_db_uur.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_UUR_TAB)
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": database niet te openen(4)."+const.DB_WEATHER_UUR_TAB+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_UUR_TAB+" succesvol geopend.")

        # open van weer database voor historische weer dag      
        try:
            weer_history_db_dag.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_DAG_TAB)
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": database niet te openen(5)."+const.DB_WEATHER_DAG_TAB+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_DAG_TAB+" succesvol geopend.")

        # open van weer database voor historische weer maand      
        try:
            weer_history_db_maand.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_MAAND_TAB)
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": database niet te openen(6)."+const.DB_WEATHER_MAAND_TAB+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_MAAND_TAB+" succesvol geopend.")

        # open van weer database voor historische weer jaar      
        try:
            weer_history_db_jaar.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_JAAR_TAB)
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": database niet te openen(7)."+const.DB_WEATHER_JAAR_TAB+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_JAAR_TAB+" succesvol geopend.")

        setFileFlags()

        api_parameters = getUrlParameters()
        if api_parameters[0] == False:
            flog.error(inspect.stack()[0][3]+": gestopt fout gevonden in API parameters.")
            return

        timestamp, process_status, output = getWeatherFromApi(api_parameters[1],api_parameters[2])
        flog.info(inspect.stack()[0][3]+": gebruikte stad id -> " + api_parameters[1] )
        flog.info(inspect.stack()[0][3]+": API URL succes="+str(process_status)+" timestamp="+str(timestamp))
        flog.info(inspect.stack()[0][3]+": API output=" + str(output))

        # housekeeping remove old records
        if process_status == True: 
            # process history data
            updateHistory(output)

            # determine timestamp of records to remove
            deleteFromDb( timestamp - 2764800 ) # 2764800 = is 32 days * 86400 secs
            deleteFromHistoryDb()

            #update status timestamp processed weather information
            os.environ['TZ'] = 'Europe/Amsterdam'
            time.tzset()
            rt_status_db.timestamp(45,flog)

            flog.info("API data succesvol verwerkt.")
            sys.exit(0)
        else:
            flog.warning("API data kon niet worden opgehaald.")
            sys.exit(1)

    if args.recover == True:
        roomtemperature_from_db = get_graaddagen_roomtemperature( db=config_db, flog=flog )
        rgd = graaddagen_lib.RecoveryGraaddagen( room_temperature=roomtemperature_from_db, flog=flog )
        if rgd.check_if_set() == False:
            rgd.run()
        else:
            flog.info( inspect.stack()[0][3] + ": graaddagen lijken gezet te zijn." )
        sys.exit(0)

    if args.recoverforced == True:
        roomtemperature_from_db = get_graaddagen_roomtemperature( db=config_db, flog=flog )
        rgd = graaddagen_lib.RecoveryGraaddagen( room_temperature=roomtemperature_from_db, flog=flog )
        rgd.run()
        sys.exit(0)

    flog.warning( inspect.stack()[0][3] + ": geen commandline opties opgegeven. " )
    sys.exit(1)


###############################
# functions                   #
###############################

def get_graaddagen_roomtemperature( db=None, flog=None ):
    try:
        #raise Exception( "TESTget_graadagen_roomtemperature") 
        _id, roomtemperature, _label = config_db.strget( 202, flog )
        return float(roomtemperature)

    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": probleem met het lezen van de kamer temperatuur gebruik de standaard waarde " +\
             str( graaddagen_lib.DEFAULT_ROOM_TEMPERATURE ) + " graden Celsius." )
        return float(graaddagen_lib.DEFAULT_ROOM_TEMPERATURE)


def updateHistory(record ):
    #flog.setLevel(logging.DEBUG)
    flog.debug(inspect.stack()[0][3]+": UTC input epoch = "+str(record['timestamp']))
    # find epoc window for this timestamp yyyy-mm-dd hh:00 and yyyy-mm-dd hh:59 in UTC time

    roomtemperature_from_db = get_graaddagen_roomtemperature( db=config_db, flog=flog )
    
    t=time.gmtime(record['timestamp'])
    timestamp_start = "%04d-%02d-%02d %02d:00:00"%(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
    timestamp_stop = "%04d-%02d-%02d %02d:59:00"%(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)

    #convert back to epoc seconds local time
    os.environ['TZ']='UTC'
    time.tzset()

    epoch_start = int(time.mktime(time.strptime(timestamp_start, '%Y-%m-%d %H:%M:%S')))
    epoch_stop     = epoch_start+3599 # plus one hour
    t=time.gmtime(epoch_start)
    timestamp_start = "%04d-%02d-%02d %02d:%02d:%02d"%(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    t=time.gmtime(epoch_stop)
    timestamp_stop = "%04d-%02d-%02d %02d:%02d:%02d"%(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

    flog.debug(inspect.stack()[0][3]+": UTC start time="+timestamp_start+"(epoch="+str(epoch_start)+")")
    flog.debug(inspect.stack()[0][3]+": UTC stop  time="+timestamp_stop +"(epoch="+str(epoch_stop) +")")

    try:
        sqlstr = "select \
        min(temperature), avg(temperature),  max(temperature),\
        min(pressure),    avg(pressure),     max(pressure),\
        min(humidity),    avg(humidity),     max(humidity),\
        min(wind_speed),  avg(wind_speed),   max(wind_speed),\
        min(wind_degree), avg(wind_degree),  max(wind_degree)\
        from " + const.DB_WEATHER_TAB + " where timestamp >= " \
        + str(epoch_start) + " and timestamp <= " + str(epoch_stop)
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(4)="+sqlstr)
        rec_select = weer_db.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde weer record" + str(rec_select) )
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(select weer)"+str(e))
        return

    #sanity check
    santity_treshold = -1000
    try:
        rec_list = list(rec_select[0])
        
        # wind degree
        if rec_list[14] < santity_treshold:  # max degree
            rec_list[14]  = 0
        if rec_list[13] < santity_treshold:
             rec_list[13] = rec_list[14] # equals to max degree
        if rec_list[12] < santity_treshold:
             rec_list[12] = rec_list[13] # equals to max degree
            
        # wind speed
        if rec_list[11] < santity_treshold:  # max wind speed
            rec_list[11]  = 0
        if rec_list[10] < santity_treshold:
             rec_list[10] = rec_list[11] # equals to max wind speed
        if rec_list[9] < santity_treshold:
             rec_list[9]  = rec_list[10] # equals to max wind speed
            
        # humidity
        if rec_list[8] < santity_treshold:  # max humidity
            rec_list[8]  = 0
        if rec_list[7] < santity_treshold:
             rec_list[7] = rec_list[8] # equals to humidity
        if rec_list[6] < santity_treshold:
             rec_list[6]  = rec_list[7] # equals to humidity

        # pressure
        if rec_list[5] < santity_treshold:  # max pressure
            rec_list[5]  = 0
        if rec_list[4] < santity_treshold:
             rec_list[4] = rec_list[5] # equals to pressure
        if rec_list[3] < santity_treshold:
             rec_list[3]  = rec_list[4] # equals to pressure
             
         # temperature
        if rec_list[2] < santity_treshold:  # max temperature
            raise NameError(' Temperatuur waarde fout.')
        if rec_list[1] < santity_treshold:
            raise NameError(' Temperatuur waarde fout.')
        if rec_list[0] < santity_treshold:
             raise NameError(' Temperatuur waarde fout.')
             
        rec_select =  [tuple(rec_list)] # copy back, tuples are not mutable.
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": waarde weer record" + str(rec_list) )
        flog.error(inspect.stack()[0][3]+": integriteits check"+str(e))
        return
    
    #flog.setLevel(logging.logging.INFO)

    time_offset = 3600
    if util.is_dst(): #summer time compensation. 
       time_offset+=3600    
    t=time.gmtime(record['timestamp']+time_offset)
    timestamp_update = "%04d-%02d-%02d %02d:00:00"%(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour)
    flog.debug(inspect.stack()[0][3]+": timestamp update  uur = " + str(timestamp_update) )


    #############################################################
    # calculate the graaddagen based on the avg measured values #
    #############################################################
    try:
        avg_graaddagen =  round( graaddagen_lib.calculate( room_temperature=roomtemperature_from_db , avg_day_temperature = rec_select[0][1], timestring=timestamp_update) / 24, 3)
        flog.debug( inspect.stack()[0][3]+  ": gemiddelde uur temperatuur = " + str(round(rec_select[0][1],2)) + " gewogen graaddagen = "  + str(avg_graaddagen))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": graaddagen probleem " + str(e) )
        return

    # tuple wrangling
    select_tmp  = []
    select_tmp.append( ( *rec_select[0], avg_graaddagen ) )
    #print ( select_tmp  )
    #print( rec_select[0][1] )

    insertWeatherHistory(select_tmp, record['city_id'], record['city'],\
    timestamp_update, const.DB_WEATHER_UUR_TAB, weer_history_db_uur )

    # update day records.
    # select from hour records
    try:
        sqlstr = "select \
        min(temperature_min), avg(temperature_avg), max(temperature_max),\
        min(pressure_min),    avg(pressure_avg),    max(pressure_max),\
        min(humidity_min),    avg(humidity_avg),    max(humidity_max),\
        min(wind_speed_min),  avg(wind_speed_avg),  max(wind_speed_max),\
        min(wind_degree_min), avg(wind_degree_avg), max(wind_degree_max)\
        from "+const.DB_WEATHER_UUR_TAB+" where substr(timestamp,1,10) = '" + timestamp_update[0:10]+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(4)="+sqlstr)
        rec_select_day = weer_history_db_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde weer record" + str(rec_select_day) )
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": waarde weer record" + str(rec_select_day) )
        flog.error(inspect.stack()[0][3]+": sql error(select weer)"+str(e))
        return

    #########################################################
    # calculate the graaddagen based on the avg hour values #
    #########################################################
    try:
        avg_graaddagen = graaddagen_lib.calculate( avg_day_temperature = rec_select_day[0][1], timestring=timestamp_update )
        flog.info( inspect.stack()[0][3]+  ": gemiddelde dag temperatuur = " + str(round(rec_select_day[0][1],2)) + " gewogen graaddagen = "  + str(avg_graaddagen))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": graaddagen probleem " + str(e) )
        return

    #print ( rec_select_day )
    # tuple wrangling 
    select_day  = []
    select_day.append( ( *rec_select_day[0], avg_graaddagen ) )
    #print ( select_day )


    # update weather day records.
    insertWeatherHistory( select_day, record['city_id'], record['city'],\
    timestamp_update[0:10]+' 00:00:00', const.DB_WEATHER_DAG_TAB, weer_history_db_dag )
    #flog.setLevel( logging.logging.INFO )

    # select from day records
    try:
        sqlstr = "select \
        min(temperature_min), avg(temperature_avg), max(temperature_max),\
        min(pressure_min),    avg(pressure_avg),    max(pressure_max),\
        min(humidity_min),    avg(humidity_avg),    max(humidity_max),\
        min(wind_speed_min),  avg(wind_speed_avg),  max(wind_speed_max),\
        min(wind_degree_min), avg(wind_degree_avg), max(wind_degree_max), sum(degree_days)\
        from " + const.DB_WEATHER_DAG_TAB + " where substr(timestamp,1,7) = '" + timestamp_update[0:7]+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(5)="+sqlstr)
        rec_select_month = weer_history_db_dag.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde weer record" + str(rec_select_month) )
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": waarde weer record" + str(rec_select_month) )
        flog.error(inspect.stack()[0][3]+": sql error(select weer)"+str(e))
        return

 
    insertWeatherHistory(rec_select_month, record['city_id'], record['city'],\
    timestamp_update[0:7]+'-01 00:00:00', const.DB_WEATHER_MAAND_TAB, weer_history_db_maand )

    # select from month records
    try:
        sqlstr = "select \
        min(temperature_min), avg(temperature_avg), max(temperature_max),\
        min(pressure_min),    avg(pressure_avg),    max(pressure_max),\
        min(humidity_min),    avg(humidity_avg),    max(humidity_max),\
        min(wind_speed_min),  avg(wind_speed_avg),  max(wind_speed_max),\
        min(wind_degree_min), avg(wind_degree_avg), max(wind_degree_max), sum(degree_days)\
        from "+const.DB_WEATHER_MAAND_TAB+" where substr(timestamp,1,4) = '" + timestamp_update[0:4]+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(5)="+sqlstr)
        rec_select_year = weer_history_db_dag.select_rec(sqlstr)    
        flog.debug(inspect.stack()[0][3]+": waarde weer record" + str(rec_select_year) )
    except Exception as e:
        flog.debug(inspect.stack()[0][3]+": waarde weer record" + str(rec_select_year) )
        flog.error(inspect.stack()[0][3]+": sql error(select weer)"+str(e))
        return

    insertWeatherHistory(rec_select_year, record['city_id'], record['city'],\
    timestamp_update[0:4]+'-01-01 00:00:00', const.DB_WEATHER_JAAR_TAB, weer_history_db_jaar )


def insertWeatherHistory( rec_buffer, city_id, city, timestamp, database_tab, datebase_file ):
    try:
        sqlstr = "insert or replace into "+database_tab+ " \
       (TIMESTAMP,\
        CITY_ID,\
        CITY,\
        TEMPERATURE_MIN,\
        TEMPERATURE_AVG,\
        TEMPERATURE_MAX,\
        PRESSURE_MIN,\
        PRESSURE_AVG,\
        PRESSURE_MAX,\
        HUMIDITY_MIN,\
        HUMIDITY_AVG,\
        HUMIDITY_MAX,\
        WIND_SPEED_MIN, \
        WIND_SPEED_AVG, \
        WIND_SPEED_MAX, \
        WIND_DEGREE_MIN, \
        WIND_DEGREE_AVG, \
        WIND_DEGREE_MAX, \
        DEGREE_DAYS \
        ) values (" +\
        "'"    +str(timestamp)            +"',"+ \
                str(city_id)            +"," + \
        "'"    +str(city).replace("'","''")  +"',"+ \
                str(rec_buffer[0][0])    +"," + \
                str(rec_buffer[0][1])    +"," + \
                str(rec_buffer[0][2])    +"," + \
                str(rec_buffer[0][3])    +"," + \
                str(round(rec_buffer[0][4],0))+"," + \
                str(rec_buffer[0][5])    +"," + \
                str(rec_buffer[0][6])    +"," + \
                str(round(rec_buffer[0][7],0))+"," + \
                str(rec_buffer[0][8])    +"," + \
                str(rec_buffer[0][9])    +"," + \
                str(round(rec_buffer[0][10],1))+"," + \
                str(rec_buffer[0][11])    +"," + \
                str(round(rec_buffer[0][12],0))+"," + \
                str(round(rec_buffer[0][13],0))+"," + \
                str(round(rec_buffer[0][14],0))+"," + \
                str( rec_buffer[0][15] )+ \
        ")"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(insert)="+sqlstr)
        datebase_file.insert_rec(sqlstr) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql(insert)=" + sqlstr + " sql error(insert) " + str(e))
        return False
    return True
        
def setFileFlags():
    util.setFile2user(const.FILE_DB_WEER_FILENAME,'p1mon')
    _head,tail = os.path.split(const.FILE_DB_WEER_FILENAME)   
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    
    util.setFile2user(const.FILE_DB_WEATHER_HISTORIE,'p1mon')
    _head,tail = os.path.split(const.FILE_DB_WEATHER_HISTORIE)   
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    util.setFile2user(logfilename,'p1mon')

# return ok=True, error=False    
def deleteFromDb(delete_timestamp):
    try:
        sqlstr = "delete from "+const.DB_WEATHER_TAB+" where timestamp <"+str(delete_timestamp)
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
        weer_db.del_rec(sqlstr)
        weer_db.defrag()
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))
        return False    
    return True    

def deleteFromHistoryDb():
    timestr=util.mkLocalTimeString()
    # uur records verwijderen
    sql_del_str = "delete from "+const.DB_WEATHER_UUR_TAB+" where timestamp <  '"+str(datetime.datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql delete="+sql_del_str)
        weer_history_db_uur.del_rec(sql_del_str)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen uur recs,delete gefaald. Melding="+str(e))
    
    # dag records verwijderen
    sql_del_str = "delete from "+const.DB_WEATHER_DAG_TAB+" where timestamp <  '"+str(datetime.datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql delete="+sql_del_str)
        weer_history_db_dag.del_rec(sql_del_str)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen dag recs,delete gefaald. Melding="+str(e))
    
# return value timestamp current on failure or weather timestamp on succes.
# False is failure, True is succesfully added record.    
def getWeatherFromApi( api_id, api_key):
    #flog.setLevel( logger.logging.DEBUG )
    rt_status_db.strset( "weer data ophalen", 80, flog )
    rt_status_db.timestamp( 81, flog )
    api_timestamp = int(time.time())
    result = { # -9999 & space betekend data niet beschikbaar in API
    "timestamp":' ', 
    "city_id":'-9999',
    "city":' ',
    "temperature":'-9999',
    "description":' ',
    "weather_icon":' ',
    "pressure":'-9999',
    "humidity":'-9999',
    "wind_speed":'-9999',
    "wind_direction":'-9999',
    "clouds":'-9999',
    "weather_id":'-9999'
    }

    try:
        _id, language_index, _label = config_db.strget( 148, flog )
        if int(language_index) == 1:
            weather_api_language = 'en'
        elif int(language_index) == 2:
            weather_api_language = 'fr'
        else:
            weather_api_language = 'nl'
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": taal error" + str(e) )

    try:
        url = 'https://api.openweathermap.org/data/2.5/weather?id='+ api_id \
        +'&units=metric&lang=' + weather_api_language + '&appid=' + api_key
        flog.debug(inspect.stack()[0][3]+": API URL "+url)
        #print ( urllib.request.urlopen(url).read().decode('utf-8') )
        #sys.exit()
        output = json.loads( urllib.request.urlopen(url).read().decode('utf-8') )
        flog.debug(inspect.stack()[0][3]+": API output "+str(output))
    except Exception as e:
        
        if "401" in str(e): #   API key problem no or wrong API key
            rt_status_db.strset( "401 fout: API key is niet correct.", 80, flog )
        elif "404" in str(e): # a wrong API request. You specify wrong city name, ZIP-code or city ID. 
            rt_status_db.strset( "404 fout: Verkeerde API aanvraag, naam, id, oid.", 80, flog )
        elif "429" in str(e):
            rt_status_db.strset( "429 fout: meer dan 60 API aanvragen per minuut.", 80, flog )
        elif "429" in str(e):
             rt_status_db.strset( "Fout: " + str(e), 80, flog )

        # set de status timestamp
        rt_status_db.timestamp( 81, flog )
        flog.error(inspect.stack()[0][3]+": URL error"+str(e))
        return api_timestamp, False, result

    try: 
        result['timestamp'] = output['dt']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": timestamp data niet beschikaar in api.")
    try: 
        result['city_id'] = output['id']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": stad id data niet beschikaar in api.")
    try: 
        result['city'] = output['name']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": city naam data niet beschikaar in api.")
    try: 
        result['temperature'] = output['main']['temp']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": temperatuur data niet beschikaar in api.")
    try: 
        result['description'] = output['weather'][0]['description']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": beschrijving weer data niet beschikaar in api.")
    try: 
        result['weather_icon'] = output['weather'][0]['icon']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": weer icon data niet beschikaar in api.")     
    try: 
        result['pressure'] = output['main']['pressure']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": luchtdruk data niet beschikaar in api.") 
    try: 
        result['humidity'] = output['main']['humidity']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": luchtdvochtigheid data niet beschikaar in api.") 
    try: 
        result['wind_speed'] = output['wind']['speed']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": windsnelheid data niet beschikaar in api.")   
    try: 
        result['wind_direction']= output['wind']['deg']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wind richting data niet beschikaar in api.")   
    try: 
        result['clouds'] = output['clouds']['all']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": bewolkings data niet beschikaar in api.")
    try: 
        result['weather_id'] = output['weather'][0]['id']
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": weer type data niet beschikaar in api.")

    try:
        sqlstr = "insert or replace into "+const.DB_WEATHER_TAB+" values (" +\
        "'"+str(result['timestamp'])                +"',"+ \
            str(result['city_id'])                  +"," + \
         "'"+str(result['city'].replace("'","''")) +"',"+ \
            str(result['temperature'])      +"," + \
        "'"+str(result['description'])      +"',"+ \
        "'"+str(result['weather_icon'])     +"',"+ \
             str(result['pressure'])        +"," + \
             str(result['humidity'])        +"," + \
             str(result['wind_speed'])      +"," + \
             str(result['wind_direction'])  +"," + \
             str(result['clouds'])          +"," + \
             str(result['weather_id'])      +\
        ")"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(insert) = "+sqlstr )
        weer_db.insert_rec(sqlstr) 
        api_timestamp = result['timestamp']
    except Exception as e:
        rt_status_db.strset( "Fout: database is niet aan te passen", 80, flog )
        rt_status_db.timestamp( 81, flog )
        flog.error(inspect.stack()[0][3]+": sql error(insert)"+str(e))
        return api_timestamp, False, result

    rt_status_db.strset( "API data succesvol verwerkt.", 80, flog )
    rt_status_db.timestamp( 81, flog )
    #flog.setLevel( logger.logging.INFO )
    return api_timestamp,True,result


def getUrlParameters():
    # get config values
    api_key = 0
    api_id     = 0
    r         = True
    
    try:
        sqlstr = "select id, parameter from "+const.DB_CONFIG_TAB+" where id=13 or id=25 order by id asc"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        config=config_db.select_rec(sqlstr)    
        flog.debug(inspect.stack()[0][3]+": waarde config record"+str(config))
        api_key = config[0][1]
        api_id = config[1][1]
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))
        r = False
    
    #decode api_key
    
    try:
        decoded_api_key = base64.standard_b64decode(crypto3.p1Decrypt(api_key,'weatherapikey')).decode('utf-8')
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": api decodering gefaald. coded password=" +\
            api_key + " Gestopt. melding:" + str(e.args[0]) )
        r = False
    flog.info("Password decryptie ok.")
    flog.debug("Decoded api key = " + api_key )

    """
    flog.debug(inspect.stack()[0][3]+": decoded api key "+decoded_api_key)
    if all(c in string.printable for c in decoded_api_key) == False:
        flog.error(inspect.stack()[0][3]+": password decodering gefaald. Decode_api_key="+decoded_api_key)
        r = False
    else:
        flog.info("Password decryptie ok.")
    """

    return r, api_id, decoded_api_key
    
def saveExit(signum, frame):   
        signal.signal(signal.SIGINT, original_sigint)
        flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
        sys.exit(0)

#-------------------------------
if __name__ == "__main__":

    try:
        flog = logger.fileLogger( logfilename,prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
        sys.exit(1)
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main()
