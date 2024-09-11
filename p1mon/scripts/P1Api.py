# used by gunicorn see p1mon.sh script

import apiconst
import apierror
import apiutil
import const
import falcon
import inspect
import json
import logger
import os
import sqldb
import sqldb_pricing
import sys
import api_phaseminmax_lib
import api_solarpower_lib
import api_catalog_lib
import api_p1_port_lib
import api_weather_history_lib
import api_financial_lib

from apiutil import p1_serializer, validate_timestamp, clean_timestamp_str, list_filter_to_str, validate_timestamp_by_length

# INIT
prgname = 'P1Api'
e_db_serial                 = sqldb.SqlDb1()
e_db_history_sqldb2         = sqldb.SqlDb2() # min
e_db_history_uur_sqldb3     = sqldb.SqlDb3() # hour
e_db_history_uur_sqldb4     = sqldb.SqlDb4() # day,month, year
rt_status_db                = sqldb.rtStatusDb()
config_db                   = sqldb.configDB()
e_db_financieel             = sqldb.financieelDb()
weer_history_db             = sqldb.historyWeatherDB()
weer_db                     = sqldb.currentWeatherDB()
temperature_db              = sqldb.temperatureDB()
watermeter_db               = sqldb.WatermeterDBV2()
fase_db                     = sqldb.PhaseDB()
power_production_db         = sqldb.powerProductionDB()
fase_db_min_max_dag         = sqldb.PhaseMaxMinDB()
price_db                    = sqldb_pricing.PricingDb()

try:
    os.umask( 0o002 )
    flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log", prgname )
    flog.setLevel( logger.logging.INFO )
    flog.consoleOutputOn( True ) 
except Exception as e:
    print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
    sys.exit(1)


flog.info("Start van programma.")

# Create the Falcon application object
# app = falcon.API()
app = falcon.App()
app.set_error_serializer( p1_serializer )

# open databases
# open van seriele database
try:
     e_db_serial.init(const.FILE_DB_E_FILENAME ,const.DB_SERIAL_TAB)
except Exception as e:
    flog.critical( str(__name__)  + " database niet te openen(1)."+const.FILE_DB_E_FILENAME+") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__)  + ": database tabel "+const.DB_SERIAL_TAB+" succesvol geopend." )

# open van power + gas history database (1 min interval)
try:
    e_db_history_sqldb2.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_MIN_TAB) 
except Exception as e:
    flog.critical( str(__name__) + ": database niet te openen(2)." + const.FILE_DB_E_HISTORIE + ") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_HISTORIE_MIN_TAB + " (minuut) succesvol geopend." )

# open van history database (1 uur interval)
try:
    e_db_history_uur_sqldb3.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_UUR_TAB)    
except Exception as e:
    flog.critical( str(__name__) + ": database niet te openen(3)." + const.FILE_DB_E_HISTORIE + ") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_HISTORIE_UUR_TAB + " succesvol geopend." )

# open van history database (dag , maand, year interval)
try:
    e_db_history_uur_sqldb4.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_DAG_TAB)    
except Exception as e:
    flog.critical( str(__name__) + ": database niet te openen(4)." + const.FILE_DB_E_HISTORIE+") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_HISTORIE_DAG_TAB + " succesvol geopend." )

# open van status database      
try:    
    rt_status_db.init( const.FILE_DB_STATUS,const.DB_STATUS_TAB )
except Exception as e:
    flog.critical( str(__name__) +  ": Database niet te openen(5)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_STATUS_TAB + " succesvol geopend." )

 # open van config database      
try:
    config_db.init( const.FILE_DB_CONFIG,const.DB_CONFIG_TAB )
except Exception as e:
    flog.critical( str(__name__) + ": database niet te openen(6)."+const.FILE_DB_CONFIG+") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

# open van financieel database
try:
    e_db_financieel.init( const.FILE_DB_FINANCIEEL , const.DB_FINANCIEEL_DAG_TAB )
except Exception as e:
    flog.critical( str(__name__) + ": database niet te openen(7)." + const.FILE_DB_FINANCIEEL + ") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel "+const.DB_FINANCIEEL_DAG_TAB+" succesvol geopend." )

# open van weer database voor historische weer dag      
try:
    weer_history_db.init( const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_DAG_TAB )
except Exception as e:
    flog.critical( str(__name__) + ": database niet te openen(8)." + const.DB_WEATHER_DAG_TAB + ") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel "+const.DB_WEATHER_DAG_TAB + " succesvol geopend.")

# open van weer database voor huidige weer      
try:
    weer_db.init(const.FILE_DB_WEATHER ,const.DB_WEATHER_TAB)
except Exception as e:
    flog.critical( str(__name__) + ": database niet te openen(9)." + const.DB_WEATHER_TAB + ") melding:"+str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_WEATHER_TAB + " succesvol geopend." )

 # open van temperatuur database
try:    
    temperature_db.init(const.FILE_DB_TEMPERATUUR_FILENAME ,const.DB_TEMPERATUUR_TAB )
except Exception as e:
    flog.critical( str(__name__) + ": Database niet te openen(10)." + const.FILE_DB_TEMPERATUUR_FILENAME+") melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel "+const.DB_TEMPERATUUR_TAB  + " succesvol geopend." )

# open van watermeter V2 database
try:
    watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
except Exception as e:
    flog.critical( str(__name__) + ": Database niet te openen(11)." + const.FILE_DB_WATERMETERV2 + " melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

# open van fase database
try:
    fase_db.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_REALTIME_TAB )
    fase_db.defrag()
except Exception as e:
    flog.critical( str(__name__) + " database niet te openen(12)." + const.FILE_DB_PHASEINFORMATION + ") melding:"+str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_FASE_REALTIME_TAB + " succesvol geopend.")

# open van power production database
try:
    power_production_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_TAB, flog )
except Exception as e:
    flog.critical( str(__name__) + ": Database niet te openen(13)." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_POWERPRODUCTION_TAB + " succesvol geopend." )

# open van fase database voor min/max waarden.
try:
    fase_db_min_max_dag.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_MINMAX_DAG_TAB )
except Exception as e:
    flog.critical( str(__name__) + " database niet te openen(14)." + const.FILE_DB_PHASEINFORMATION + ") melding:"+str(e.args[0]) )
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_FASE_MINMAX_DAG_TAB + " succesvol geopend.")

try:
    price_db.init(const.FILE_DB_FINANCIEEL ,const.DB_ENERGIEPRIJZEN_UUR_TAB)
except Exception as e:
    flog.critical(inspect.stack()[0][3]+": Database niet te openen(15)." + const.FILE_DB_FINANCIEEL + ") melding:" + str(e.args[0]))
    sys.exit(1)
flog.info( str(__name__) + ": database tabel " + const.DB_ENERGIEPRIJZEN_UUR_TAB + " succesvol geopend.")


#TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ********************************************************************************************
##############################################################################################
# BELANGRIJK ALLE ROUTES NAAR api_solarpower_lib e.d omzetten als een route wordt aangepast. #
# TEVENS ALLE HULP ROUTES IN EEN APARTE ROUTE FUNCTIE ZETTEN.                                #
# TEMPLATE VOOR Function() en FunctionHelp() zie Catalog en CatalogHelp() als voorbeeld      #
##############################################################################################
# ********************************************************************************************

catalog_resource = api_catalog_lib.Catalog()
catalog_resource.set_flog( flog )
app.add_route( apiconst.ROUTE_CATALOG, catalog_resource )

catalog_resource_help = api_catalog_lib.CatalogHelp()
catalog_resource_help.set_flog( flog )
app.add_route( apiconst.ROUTE_CATALOG_HELP, catalog_resource_help )

power_production_solar_resource = api_solarpower_lib.powerProductionSolar()
power_production_solar_resource.set_flog( flog )
power_production_solar_resource.set_database( power_production_db )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_MIN ,       power_production_solar_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_HOUR,       power_production_solar_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_DAY,        power_production_solar_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_MONTH,      power_production_solar_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_YEAR,       power_production_solar_resource )

power_production_solar_resource_help = api_solarpower_lib.powerProductionSolarHelp()
power_production_solar_resource_help.set_flog( flog )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_MIN_HELP,   power_production_solar_resource_help )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_HOUR_HELP,  power_production_solar_resource_help )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_DAY_HELP,   power_production_solar_resource_help )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_MONTH_HELP, power_production_solar_resource_help )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_SOLAR_YEAR_HELP,  power_production_solar_resource_help )

# added in version 1.7.0
phase_min_max_resource =  api_phaseminmax_lib.PhaseMinMax()
phase_min_max_resource.set_flog( flog )
phase_min_max_resource.set_database( fase_db_min_max_dag )
app.add_route( apiconst.ROUTE_PHASE_MINMAX_DAY, phase_min_max_resource )

phase_min_max_resource_help = api_phaseminmax_lib.PhaseMinMaxHelp()
phase_min_max_resource_help.set_flog( flog )
app.add_route( apiconst.ROUTE_PHASE_MINMAX_DAY_HELP, phase_min_max_resource_help )

# added in version 1.7.0
p1_port_telegram = api_p1_port_lib.P1PortTelegram()
p1_port_telegram.set_flog( flog )
app.add_route( apiconst.ROUTE_P1_PORT_TELEGRAM, p1_port_telegram )

p1_port_telegram_help = api_p1_port_lib.P1PortTelegramHelp()
p1_port_telegram_help.set_flog( flog )
app.add_route( apiconst.ROUTE_P1_PORT_TELEGRAM_HELP, p1_port_telegram_help )

# added/changed in version 2.1.0
weather_history = api_weather_history_lib.WeatherHistory()
weather_history.set_flog( flog )
weather_history.set_database( weer_history_db )
app.add_route( apiconst.ROUTE_WEATHER_HOUR,       weather_history )
app.add_route( apiconst.ROUTE_WEATHER_DAY,        weather_history )
app.add_route( apiconst.ROUTE_WEATHER_MONTH,      weather_history )
app.add_route( apiconst.ROUTE_WEATHER_YEAR,       weather_history )

weather_history_help = api_weather_history_lib.WeatherHistoryHelp()
weather_history_help.set_flog( flog )
app.add_route( apiconst.ROUTE_WEATHER_HOUR_HELP,  weather_history_help )
app.add_route( apiconst.ROUTE_WEATHER_DAY_HELP,   weather_history_help )
app.add_route( apiconst.ROUTE_WEATHER_MONTH_HELP, weather_history_help )
app.add_route( apiconst.ROUTE_WEATHER_YEAR_HELP,  weather_history_help )

# added/changed in version 2.2.0
financial = api_financial_lib.Financial()
financial.set_flog( flog )
financial.set_database( e_db_financieel )
app.add_route( apiconst.ROUTE_FINANCIAL_DAY,        financial )
app.add_route( apiconst.ROUTE_FINANCIAL_MONTH,      financial )
app.add_route( apiconst.ROUTE_FINANCIAL_YEAR,       financial )

financial_help = api_financial_lib.FinancialHelp()
financial_help.set_flog( flog )
app.add_route( apiconst.ROUTE_FINANCIAL_DAY_HELP,   financial_help )
app.add_route( apiconst.ROUTE_FINANCIAL_MONTH_HELP, financial_help )
app.add_route( apiconst.ROUTE_FINANCIAL_YEAR_HELP,  financial_help )

financial_dynamic_tariff = api_financial_lib.FinancialDynamicTariff()
financial_dynamic_tariff.set_flog( flog )
financial_dynamic_tariff.set_database( e_db_financieel )
app.add_route( apiconst.ROUTE_FINANCIAL_DYNAMIC_TARIFF, financial_dynamic_tariff )

financial_dynamic_tariff_help = api_financial_lib.FinancialDynamicTariffHelp()
financial_dynamic_tariff_help.set_flog( flog )
app.add_route( apiconst.ROUTE_FINANCIAL_DYNAMIC_TARIFF_HELP, financial_dynamic_tariff_help )



################ alles hierdonder nog omzetten !!!!!!!!!!! naar api_lib_nnnnn functies. 

class PowerProductionS0( object ):

    sqlstr_base_regular = "select \
    TIMESTAMP,\
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    TIMEPERIOD_ID,\
    POWER_SOURCE_ID,\
    PRODUCTION_KWH_HIGH,\
    PRODUCTION_KWH_LOW,\
    PULS_PER_TIMEUNIT_HIGH,\
    PULS_PER_TIMEUNIT_LOW,\
    PRODUCTION_KWH_HIGH_TOTAL,\
    PRODUCTION_KWH_LOW_TOTAL,\
    PRODUCTION_KWH_TOTAL,\
    PRODUCTION_PSEUDO_KW from " + const.DB_POWERPRODUCTION_TAB

    sqlstr_base_round = "select \
    TIMESTAMP,\
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    TIMEPERIOD_ID,\
    POWER_SOURCE_ID,\
    CAST( PRODUCTION_KWH_HIGH as INT ),\
    CAST( PRODUCTION_KWH_LOW as INT ),\
    CAST( PULS_PER_TIMEUNIT_HIGH as INT ),\
    CAST( PULS_PER_TIMEUNIT_LOW as INT ),\
    CAST( PRODUCTION_KWH_HIGH_TOTAL as INT ),\
    CAST( PRODUCTION_KWH_LOW_TOTAL as INT ),\
    CAST( PRODUCTION_KWH_TOTAL as INT ),\
    CAST( PRODUCTION_PSEUDO_KW as INT ) from " + const.DB_POWERPRODUCTION_TAB

    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL               : '',
            apiconst.JSON_TS_LCL_UTC           : 0,
            apiconst.JSON_API_PROD_PERIOD_ID   : 0,
            apiconst.JSON_API_PROD_PWR_SRC_ID  : 0,
            apiconst.JSON_API_PROD_KWH_H       : 0,
            apiconst.JSON_API_PROD_KWH_L       : 0,
            apiconst.JSON_API_PROD_PULS_CNT_H  : 0,
            apiconst.JSON_API_PROD_PULS_CNT_L  : 0,
            apiconst.JSON_API_PROD_KWH_TOTAL_H : 0,
            apiconst.JSON_API_PROD_KWH_TOTAL_L : 0,
            apiconst.JSON_API_PROD_KWH_TOTAL   : 0,
            apiconst.JSON_API_PROD_W_PSEUDO    : 0
        }

        if  req.path == apiconst.ROUTE_POWERPRODUCTION_S0_MIN_HELP   or \
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_HOUR_HELP  or \
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_DAY_HELP   or \
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_MONTH_HELP or\
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_YEAR_HELP:
            
            flog.debug ( str( __name__ ) + " help data selected.")
            try:
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_POWER_PRODUCTION_MIN_DAY_MONTH_YEAR_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str( __class__.__name__ ) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return

        # set period index 
        v_period_id = 0
        if req.path == apiconst.ROUTE_POWERPRODUCTION_S0_MIN:
            v_period_id = " 11 "
        elif req.path == apiconst.ROUTE_POWERPRODUCTION_S0_HOUR:
            v_period_id = " 12 "
        elif req.path == apiconst.ROUTE_POWERPRODUCTION_S0_DAY:
            v_period_id = " 13 "
        elif req.path == apiconst.ROUTE_POWERPRODUCTION_S0_MONTH:
            v_period_id = " 14 "
        elif req.path == apiconst.ROUTE_POWERPRODUCTION_S0_YEAR:
            v_period_id = " 15 "


        if  req.path == apiconst.ROUTE_POWERPRODUCTION_S0_MIN   or \
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_HOUR  or \
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_DAY   or \
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_MONTH or\
            req.path == apiconst.ROUTE_POWERPRODUCTION_S0_YEAR :
            
            # default sql string
            sqlstr = self.sqlstr_base_regular

            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
            # rangetimestamp 
            v_rangetimestamp = ''

            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html ( err_str ), 
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )

                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )

                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )

                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = self.sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )

                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " and TIMESTAMP >= '" + value + "' order by timestamp "
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value)) ,
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

                if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if validate_timestamp_by_length( value ) == True:
                        #print( "key=" + key + " value=" + value ) 
                        v_rangetimestamp = " and substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

            sqlstr = sqlstr + " where TIMEPERIOD_ID = " + v_period_id + " and POWER_SOURCE_ID = 1 " + v_starttime + v_rangetimestamp + v_sort + str(v_limit)

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  =  power_production_db.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]               = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]           = a[1]
                        new_dict[ apiconst.JSON_API_PROD_PERIOD_ID ]   = a[2]
                        new_dict[ apiconst.JSON_API_PROD_PWR_SRC_ID ]  = a[3]
                        new_dict[ apiconst.JSON_API_PROD_KWH_H ]       = a[4]
                        new_dict[ apiconst.JSON_API_PROD_KWH_L ]       = a[5]
                        new_dict[ apiconst.JSON_API_PROD_PULS_CNT_H ]  = a[6]
                        new_dict[ apiconst.JSON_API_PROD_PULS_CNT_L ]  = a[7]
                        new_dict[ apiconst.JSON_API_PROD_KWH_TOTAL_H ] = a[8]
                        new_dict[ apiconst.JSON_API_PROD_KWH_TOTAL_L ] = a[9]
                        new_dict[ apiconst.JSON_API_PROD_KWH_TOTAL ]   = a[10]
                        new_dict[ apiconst.JSON_API_PROD_W_PSEUDO ]    = a[11]
                        json_obj_data.append( new_dict )

                    
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                    
                    resp.text = json.dumps( records, ensure_ascii=False )

                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                    titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                    code=apierror.API_DB_ERROR['code'] 
                    )

            resp.status = falcon.HTTP_200  # This is the default status

power_production_power_s0_resource  = PowerProductionS0()

app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_MIN ,       power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_MIN_HELP,   power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_HOUR,       power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_HOUR_HELP,  power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_DAY,        power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_DAY_HELP,   power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_MONTH,      power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_MONTH_HELP, power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_YEAR,       power_production_power_s0_resource )
app.add_route( apiconst.ROUTE_POWERPRODUCTION_S0_YEAR_HELP,  power_production_power_s0_resource )


class IndoorTemperature( object ):
    
    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    RECORD_ID, \
    TEMPERATURE_1, \
    TEMPERATURE_1_MIN, \
    TEMPERATURE_1_AVG, \
    TEMPERATURE_1_MAX, \
    TEMPERATURE_2, \
    TEMPERATURE_2_MIN, \
    TEMPERATURE_2_AVG, \
    TEMPERATURE_2_MAX \
    from temperatuur where RECORD_ID = "

  
    sqlstr_base_round  = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    RECORD_ID, \
    CAST( TEMPERATURE_1 as INT ), \
    CAST( TEMPERATURE_1_MIN as INT ), \
    CAST( TEMPERATURE_1_AVG as INT ), \
    CAST( TEMPERATURE_1_MAX as INT ), \
    CAST( TEMPERATURE_2 as INT), \
    CAST( TEMPERATURE_2_MIN as INT ), \
    CAST( TEMPERATURE_2_AVG as INT ), \
    CAST( TEMPERATURE_2_MAX as INT ) \
    from temperatuur where RECORD_ID = "


    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                : '',
            apiconst.JSON_TS_LCL_UTC            : 0,
            apiconst.JSON_API_RM_TMPRTR_RCRD_ID : 0,
            apiconst.JSON_API_RM_TMPRTR_IN      : 0,  
            apiconst.JSON_API_RM_TMPRTR_IN_L    : 0,
            apiconst.JSON_API_RM_TMPRTR_IN_A    : 0,
            apiconst.JSON_API_RM_TMPRTR_IN_H    : 0,
            apiconst.JSON_API_RM_TMPRTR_OUT     : 0,
            apiconst.JSON_API_RM_TMPRTR_OUT_L   : 0,
            apiconst.JSON_API_RM_TMPRTR_OUT_A   : 0,
            apiconst.JSON_API_RM_TMPRTR_OUT_H   : 0
        }

        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_HELP or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_MIN_HELP  or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_HOUR_HELP or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_DAY_HELP  or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_MONTH_HELP or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_YEAR_HELP:
            
            flog.debug ( str(__name__) + " help data selected.")
            try:
                
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_INDOOR_TEMPERATURE_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     
            

        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE:
            sqlstr_base_regular = self.sqlstr_base_regular + '10 '
            sqlstr_base_round   = self.sqlstr_base_round   + '10 '
        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_MIN:
            sqlstr_base_regular = self.sqlstr_base_regular + '11 '
            sqlstr_base_round   = self.sqlstr_base_round   + '11 '
        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_HOUR:
            sqlstr_base_regular = self.sqlstr_base_regular + '12 '
            sqlstr_base_round   = self.sqlstr_base_round   + '12 '
        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_DAY:
            sqlstr_base_regular = self.sqlstr_base_regular + '13 '
            sqlstr_base_round   = self.sqlstr_base_round   + '13 '    
        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_MONTH:
            sqlstr_base_regular = self.sqlstr_base_regular + '14 '
            sqlstr_base_round   = self.sqlstr_base_round   + '14 '
        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_YEAR:
            sqlstr_base_regular = self.sqlstr_base_regular + '15 '
            sqlstr_base_round   = self.sqlstr_base_round   + '15 '

        # default sql string
        sqlstr  = sqlstr_base_regular
        
        if req.path == apiconst.ROUTE_INDOOR_TEMPERATURE or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_MIN or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_HOUR or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_DAY or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_MONTH or \
            req.path == apiconst.ROUTE_INDOOR_TEMPERATURE_YEAR:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
             # rangetimestamp 
            v_rangetimestamp = ''

            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ), 
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                """
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                        # parse timestamp
                        value =  clean_timestamp_str( value )
                        if validate_timestamp ( value ) == True:
                            v_starttime = " and TIMESTAMP >= '" + value + "' order by timestamp "
                            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )

            sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)
            """

                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " and TIMESTAMP >= '" + value + "' order by timestamp "
                        #v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if validate_timestamp_by_length( value ) == True:
                        #print( "key=" + key + " value=" + value ) 
                        v_rangetimestamp = " and substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

            sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
            #print( "# sqlstr=" + sqlstr) 


            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records =  temperature_db.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]            = a[1]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_RCRD_ID ] = a[2]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_IN ]      = a[3]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_IN_L ]    = a[4]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_IN_A ]    = a[5]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_IN_H ]    = a[6]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_OUT ]     = a[7]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_OUT_L ]   = a[8]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_OUT_A ]   = a[9]
                        new_dict[ apiconst.JSON_API_RM_TMPRTR_OUT_H ]   = a[10]
                        json_obj_data.append( new_dict )

                    
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                   
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                   titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ),
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

indoor_temperature_resource = IndoorTemperature()
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE,            indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_HELP,       indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_MIN,        indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_MIN_HELP,   indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_HOUR,       indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_HOUR_HELP,  indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_DAY,        indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_DAY_HELP,   indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_MONTH,      indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_MONTH_HELP, indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_YEAR,       indoor_temperature_resource )
app.add_route( apiconst.ROUTE_INDOOR_TEMPERATURE_YEAR_HELP,  indoor_temperature_resource )


class CurrentWeather( object ):
    
    sqlstr_base_regular =  "select \
    datetime( TIMESTAMP, 'unixepoch', 'localtime' ), \
    TIMESTAMP, \
    CITY_ID, \
    CITY, \
    TEMPERATURE, \
    DESCRIPTION, \
    WEATHER_ICON, \
    PRESSURE, \
    HUMIDITY, \
    WIND_SPEED, \
    WIND_DEGREE, \
    CLOUDS, \
    WEATHER_ID from "

    sqlstr_base_round =  "select \
    datetime( TIMESTAMP, 'unixepoch', 'localtime' ), \
    TIMESTAMP, \
    CITY_ID, \
    CITY, \
    CAST( TEMPERATURE as INT ), \
    DESCRIPTION, \
    WEATHER_ICON, \
    PRESSURE, \
    HUMIDITY, \
    CAST( WIND_SPEED as INT ), \
    WIND_DEGREE, \
    CLOUDS, \
    WEATHER_ID from "


    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL              : '',
            apiconst.JSON_TS_LCL_UTC          : 0,
            apiconst.JSON_API_CTY_ID          : 0,
            apiconst.JSON_API_CTY_NM          : '',
            apiconst.JSON_API_WTHR_TMPRTR     : 0,
            apiconst.JSON_API_WTHR_DSCRPTN    : 0,
            apiconst.JSON_API_WTHR_ICON       : '',
            apiconst.JSON_API_WTHR_PRSSR      : 0,
            apiconst.JSON_API_WTHR_HMDTY      : 0,
            apiconst.JSON_API_WTHR_WND_SPD    : 0,
            apiconst.JSON_API_WTHR_WND_DGRS   : 0,
            apiconst.JSON_API_WTHR_CLDS       : 0,
            apiconst.JSON_API_WTHR_WEATHER_ID : 0 
        }

        if req.path == apiconst.ROUTE_WEATHER_CURRENT_HELP:
            
            flog.debug ( str(__name__) + " help data selected.")
            try:
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_WEATHER_CURRENT_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request on " + \
                apiconst.ROUTE_WEATHER_CURRENT_HELP  + " failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     
            

        if req.path == apiconst.ROUTE_WEATHER_CURRENT:
            sqlstr_base_regular = self.sqlstr_base_regular + 'weer '
            sqlstr_base_round   = self.sqlstr_base_round   + 'weer '
        
        # default sql string
        sqlstr  = sqlstr_base_regular

        if req.path == apiconst.ROUTE_WEATHER_CURRENT:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
        
            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ), 
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                        # parse timestamp
                        value =  clean_timestamp_str( value )
                        if validate_timestamp ( value ) == True:
                            v_starttime = " where datetime( TIMESTAMP, 'unixepoch', 'localtime' ) >= '" + value + "' order by timestamp "
                            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )

            sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  = weer_db.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]              = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]          = a[1]
                        new_dict[ apiconst.JSON_API_CTY_ID ]          = a[2] 
                        new_dict[ apiconst.JSON_API_CTY_NM ]          = a[3]
                        new_dict[ apiconst.JSON_API_WTHR_TMPRTR ]     = a[4]
                        new_dict[ apiconst.JSON_API_WTHR_DSCRPTN ]    = a[5]
                        new_dict[ apiconst.JSON_API_WTHR_ICON ]       = a[6]
                        new_dict[ apiconst.JSON_API_WTHR_PRSSR ]      = a[7]
                        new_dict[ apiconst.JSON_API_WTHR_HMDTY ]      = a[8]
                        new_dict[ apiconst.JSON_API_WTHR_WND_SPD ]    = a[9]
                        new_dict[ apiconst.JSON_API_WTHR_WND_DGRS ]   = a[10]
                        new_dict[ apiconst.JSON_API_WTHR_CLDS ]       = a[11]
                        new_dict[ apiconst.JSON_API_WTHR_WEATHER_ID ] = a[12]
                        json_obj_data.append( new_dict )

                    
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                   
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                   titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

current_weather_resource  = CurrentWeather()
app.add_route( apiconst.ROUTE_WEATHER_CURRENT,      current_weather_resource )
app.add_route( apiconst.ROUTE_WEATHER_CURRENT_HELP, current_weather_resource )


class PowerGasHistoryDayMonthYear( object ):
    
    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    VERBR_KWH_181, \
    VERBR_KWH_182, \
    GELVR_KWH_281, \
    GELVR_KWH_282, \
    VERBR_KWH_X, \
    GELVR_KWH_X, \
    VERBR_GAS_2421, \
    VERBR_GAS_X from " 

    sqlstr_base_round = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    CAST( VERBR_KWH_181 as INT ), \
    CAST( VERBR_KWH_182 as INT ), \
    CAST( GELVR_KWH_281 as INT ), \
    CAST( GELVR_KWH_282 as INT ), \
    CAST( VERBR_KWH_X as INT ), \
    CAST( GELVR_KWH_X as INT ), \
    CAST( VERBR_GAS_2421 as INT ), \
    CAST( VERBR_GAS_X as INT )  \
    from " 

    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                 : '',
            apiconst.JSON_TS_LCL_UTC             : 0,
            apiconst.JSON_API_CNSMPTN_KWH_L      : 0,
            apiconst.JSON_API_CNSMPTN_KWH_H      : 0,
            apiconst.JSON_API_PRDCTN_KWH_L       : 0,
            apiconst.JSON_API_PRDCTN_KWH_H       : 0,
            apiconst.JSON_API_CNSMPTN_DLT_KWH    : 0,
            apiconst.JSON_API_PRDCTN_DLT_KWH     : 0,
            apiconst.JSON_API_CNSMPTN_GAS_M3     : 0,
            apiconst.JSON_API_CNSMPTN_GAS_DLT_M3 : 0
        }

        if req.path == apiconst.ROUTE_POWER_GAS_DAY_HELP or \
            req.path == apiconst.ROUTE_POWER_GAS_MONTH_HELP or \
            req.path == apiconst.ROUTE_POWER_GAS_YEAR_HELP:
            
            flog.debug ( str(__name__) + " help data selected.")
            try:
               
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_POWER_GAS_DAY_MONTH_YEAR_JSON , sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     
            

        if req.path == apiconst.ROUTE_POWER_GAS_DAY:
            sqlstr_base_regular = self.sqlstr_base_regular + 'e_history_dag '
            sqlstr_base_round   = self.sqlstr_base_round   + 'e_history_dag '
        if req.path == apiconst.ROUTE_POWER_GAS_MONTH:
            sqlstr_base_regular = self.sqlstr_base_regular + 'e_history_maand '
            sqlstr_base_round   = self.sqlstr_base_round   + 'e_history_maand '
        if req.path == apiconst.ROUTE_POWER_GAS_YEAR:
            sqlstr_base_regular = self.sqlstr_base_regular + 'e_history_jaar '
            sqlstr_base_round   = self.sqlstr_base_round   + 'e_history_jaar '

        # default sql string
        sqlstr  = sqlstr_base_regular
        

        if req.path == apiconst.ROUTE_POWER_GAS_DAY or \
            req.path == apiconst.ROUTE_POWER_GAS_MONTH or \
            req.path == apiconst.ROUTE_POWER_GAS_YEAR:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
            # rangetimestamp 
            v_rangetimestamp = ''

            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ), 
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if validate_timestamp_by_length( value ) == True:
                        #print( "key=" + key + " value=" + value ) 
                        v_rangetimestamp = "where substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

            sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
            #print( "# sqlstr=" + sqlstr) 

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  =  e_db_history_uur_sqldb4.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                 = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]             = a[1]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_L ]      = a[2]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_H ]      = a[3]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_L ]       = a[4]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_H ]       = a[5]
                        new_dict[ apiconst.JSON_API_CNSMPTN_DLT_KWH ]    = a[6]
                        new_dict[ apiconst.JSON_API_PRDCTN_DLT_KWH ]     = a[7]
                        new_dict[ apiconst.JSON_API_CNSMPTN_GAS_M3 ]     = a[8]
                        new_dict[ apiconst.JSON_API_CNSMPTN_GAS_DLT_M3 ] = a[9]
                        json_obj_data.append( new_dict )

                   
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                   titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr)) ,
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

power_gas_history_day_month_year_resource  = PowerGasHistoryDayMonthYear()
app.add_route( apiconst.ROUTE_POWER_GAS_DAY,        power_gas_history_day_month_year_resource )
app.add_route( apiconst.ROUTE_POWER_GAS_DAY_HELP,   power_gas_history_day_month_year_resource )
app.add_route( apiconst.ROUTE_POWER_GAS_MONTH,      power_gas_history_day_month_year_resource )
app.add_route( apiconst.ROUTE_POWER_GAS_MONTH_HELP, power_gas_history_day_month_year_resource )
app.add_route( apiconst.ROUTE_POWER_GAS_YEAR,       power_gas_history_day_month_year_resource )
app.add_route( apiconst.ROUTE_POWER_GAS_YEAR_HELP,  power_gas_history_day_month_year_resource )


class PowerGasHistoryHour( object ):
    
    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    VERBR_KWH_181, \
    VERBR_KWH_182, \
    GELVR_KWH_281, \
    GELVR_KWH_282, \
    VERBR_KWH_X, \
    GELVR_KWH_X, \
    TARIEFCODE , \
    VERBR_GAS_2421, \
    VERBR_GAS_X from " 

    sqlstr_base_round = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    CAST( VERBR_KWH_181 as INT ), \
    CAST( VERBR_KWH_182 as INT ), \
    CAST( GELVR_KWH_281 as INT ), \
    CAST( GELVR_KWH_282 as INT ), \
    CAST( VERBR_KWH_X as INT), \
    CAST( GELVR_KWH_X as INT), \
    TARIEFCODE , \
    CAST( VERBR_GAS_2421 as INT ), \
    CAST( VERBR_GAS_X as INT )  \
    from " 

    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                 : '',
            apiconst.JSON_TS_LCL_UTC             : 0,
            apiconst.JSON_API_CNSMPTN_KWH_L      : 0,
            apiconst.JSON_API_CNSMPTN_KWH_H      : 0,
            apiconst.JSON_API_PRDCTN_KWH_L       : 0,
            apiconst.JSON_API_PRDCTN_KWH_H       : 0,
            apiconst.JSON_API_CNSMPTN_DLT_KWH    : 0,
            apiconst.JSON_API_PRDCTN_DLT_KWH     : 0,
            apiconst.JSON_API_TRFCD              : 0,
            apiconst.JSON_API_CNSMPTN_GAS_M3     : 0,
            apiconst.JSON_API_CNSMPTN_GAS_DLT_M3 : 0
        }

        if req.path == apiconst.ROUTE_POWER_GAS_HOUR_HELP:
            
            flog.debug ( str(__name__) + " help data selected.")
            try:
                
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_POWER_GAS_HOUR_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request on " + \
                apiconst.ROUTE_POWER_GAS_HOUR_HELP  + " failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return

        if req.path == apiconst.ROUTE_POWER_GAS_HOUR:
            sqlstr_base_regular = self.sqlstr_base_regular + 'e_history_uur '
            sqlstr_base_round   = self.sqlstr_base_round   + 'e_history_uur '
        
        # default sql string
        sqlstr  = sqlstr_base_regular

        if req.path == apiconst.ROUTE_POWER_GAS_HOUR:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
            # rangetimestamp 
            v_rangetimestamp = ''
        
            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ),
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value)),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if validate_timestamp_by_length( value ) == True:
                        #print( "key=" + key + " value=" + value ) 
                        v_rangetimestamp = "where substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

            sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
            #print( "# sqlstr=" + sqlstr) 

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  = e_db_history_uur_sqldb3.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                 = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]             = a[1]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_L ]      = a[2]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_H ]      = a[3]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_L ]       = a[4]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_H ]       = a[5]
                        new_dict[ apiconst.JSON_API_CNSMPTN_DLT_KWH ]    = a[6]
                        new_dict[ apiconst.JSON_API_PRDCTN_DLT_KWH ]     = a[7]
                        new_dict[ apiconst.JSON_API_TRFCD ]              = a[8]
                        new_dict[ apiconst.JSON_API_CNSMPTN_GAS_M3 ]     = a[9]
                        new_dict[ apiconst.JSON_API_CNSMPTN_GAS_DLT_M3 ] = a[10]
                        json_obj_data.append( new_dict )

                    
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                    
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                   titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ),
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

power_gas_history_hour_resource  = PowerGasHistoryHour()
app.add_route( apiconst.ROUTE_POWER_GAS_HOUR,        power_gas_history_hour_resource )
app.add_route( apiconst.ROUTE_POWER_GAS_HOUR_HELP,   power_gas_history_hour_resource )


# range option done 2020-08-16
class PowerGasHistoryMin( object ):

    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    VERBR_KWH_181, \
    VERBR_KWH_182, \
    GELVR_KWH_281, \
    GELVR_KWH_282, \
    VERBR_KWH_X, \
    GELVR_KWH_X, \
    TARIEFCODE , \
    ACT_VERBR_KW_170, \
    ACT_GELVR_KW_270, \
    VERBR_GAS_2421 from " 


    sqlstr_base_round = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    CAST( VERBR_KWH_181 as INT ), \
    CAST( VERBR_KWH_182 as INT ), \
    CAST( GELVR_KWH_281 as INT ), \
    CAST( GELVR_KWH_282 as INT ), \
    CAST( VERBR_KWH_X as INT ), \
    CAST( GELVR_KWH_X as INT ), \
    TARIEFCODE , \
    CAST( ACT_VERBR_KW_170 as INT ), \
    CAST( ACT_GELVR_KW_270 as INT ), \
    CAST( VERBR_GAS_2421 as INT ) \
    from "

    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                : '',
            apiconst.JSON_TS_LCL_UTC            : 0,
            apiconst.JSON_API_CNSMPTN_KWH_L     : 0,
            apiconst.JSON_API_CNSMPTN_KWH_H     : 0,
            apiconst.JSON_API_PRDCTN_KWH_L      : 0,
            apiconst.JSON_API_PRDCTN_KWH_H      : 0,
            apiconst.JSON_API_CNSMPTN_DLT_KWH   : 0,
            apiconst.JSON_API_PRDCTN_DLT_KWH    : 0,
            apiconst.JSON_API_TRFCD             : 0,
            apiconst.JSON_API_CNSMPTN_KW        : 0,
            apiconst.JSON_API_PRDCTN_KW         : 0,
            apiconst.JSON_API_CNSMPTN_GAS_M3    : 0,
        }

        if req.path == apiconst.ROUTE_POWER_GAS_MIN_HELP:
            
            flog.debug ( str(__name__) + " help data selected.")
            try:
               
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_POWER_GAS_MIN_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request on " + \
                apiconst.ROUTE_POWER_GAS_MIN_HELP + " failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     
            

        if req.path == apiconst.ROUTE_POWER_GAS_MIN:
            #sqlstr_base_regular = self.sqlstr_base_regular + 'e_history_min '
            #sqlstr_base_round   = self.sqlstr_base_round   + 'e_history_min '
            sqlstr_base_regular = self.sqlstr_base_regular + const.DB_HISTORIE_MIN_TAB + " "
            sqlstr_base_round   = self.sqlstr_base_round   + const.DB_HISTORIE_MIN_TAB + " "

        # default sql string
        sqlstr  = sqlstr_base_regular

        if req.path == apiconst.ROUTE_POWER_GAS_MIN:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
            # rangetimestamp 
            v_rangetimestamp = ''

            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ),
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if validate_timestamp_by_length( value ) == True:
                        #print( "key=" + key + " value=" + value ) 
                        v_rangetimestamp = "where substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

            sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
            #print( "# sqlstr=" + sqlstr) 

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  = e_db_history_sqldb2.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]            = a[1]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_L ]     = a[2]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_H ]     = a[3]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_L ]      = a[4]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_H ]      = a[5]
                        new_dict[ apiconst.JSON_API_CNSMPTN_DLT_KWH ]   = a[6]
                        new_dict[ apiconst.JSON_API_PRDCTN_DLT_KWH ]    = a[7]
                        new_dict[ apiconst.JSON_API_TRFCD ]             = a[8]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KW ]        = a[9]
                        new_dict[ apiconst.JSON_API_PRDCTN_KW ]         = a[10]
                        new_dict[ apiconst.JSON_API_CNSMPTN_GAS_M3 ]    = a[11]
                        json_obj_data.append( new_dict )

                    
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                   
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                    titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] +  apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ),
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

power_gas_history_min_resource = PowerGasHistoryMin()
app.add_route( apiconst.ROUTE_POWER_GAS_MIN,        power_gas_history_min_resource )
app.add_route( apiconst.ROUTE_POWER_GAS_MIN_HELP,   power_gas_history_min_resource )


"""
class Financial( object ):

    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    VERBR_P, \
    VERBR_D, \
    GELVR_P, \
    GELVR_D, \
    GELVR_GAS, \
    VERBR_WATER from "

    sqlstr_base_round = "select \
    TIMESTAMP, \
    cast( strftime('%s', TIMESTAMP, 'utc' ) AS Integer ), \
    CAST( VERBR_P as INT ), \
    CAST( VERBR_D as INT ), \
    CAST( GELVR_P as INT ), \
    CAST( GELVR_D as INT ), \
    CAST( GELVR_GAS as INT ), \
    CAST( VERBR_WATER as INT ) from "

    def on_get(self, req, resp):
        ## Handles all GET requests.
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                : '',
            apiconst.JSON_TS_LCL_UTC            : 0,
            apiconst.JSON_API_FNCL_CNSMPTN_E_H  : 0,
            apiconst.JSON_API_FNCL_CNSMPTN_E_L  : 0,
            apiconst.JSON_API_FNCL_PRDCTN_E_H   : 0,
            apiconst.JSON_API_FNCL_PRDCTN_E_L   : 0,
            apiconst.JSON_API_FNCL_CNSMPTN_GAS  : 0,
            apiconst.JSON_API_FNCL_CNSMPTN_WATER: 0
        }

        if req.path == apiconst.ROUTE_FINANCIAL_DAY_HELP or \
            req.path == apiconst.ROUTE_FINANCIAL_MONTH_HELP or \
                req.path == apiconst.ROUTE_FINANCIAL_YEAR_HELP:
            flog.debug ( str(__name__) + " help data selected.")
            try:
                
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_FINANCIAL_DAY_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + str(_e.args[0]), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return
            

        if req.path == apiconst.ROUTE_FINANCIAL_DAY:
            sqlstr_base_regular = self.sqlstr_base_regular + const.DB_FINANCIEEL_DAG_TAB # 'e_financieel_dag' 
            sqlstr_base_round   = self.sqlstr_base_round   + const.DB_FINANCIEEL_DAG_TAB # 'e_financieel_dag' 
        if req.path == apiconst.ROUTE_FINANCIAL_MONTH:
            sqlstr_base_regular = self.sqlstr_base_regular + const.DB_FINANCIEEL_MAAND_TAB #e_financieel_maand'
            sqlstr_base_round   = self.sqlstr_base_round   + const.DB_FINANCIEEL_MAAND_TAB #e_financieel_maand'
        if req.path == apiconst.ROUTE_FINANCIAL_YEAR:
            sqlstr_base_regular = self.sqlstr_base_regular + const.DB_FINANCIEEL_JAAR_TAB # 'e_financieel_jaar'
            sqlstr_base_round   = self.sqlstr_base_round   + const.DB_FINANCIEEL_JAAR_TAB # 'e_financieel_jaar'

        # default sql string
        sqlstr  = sqlstr_base_regular

        if req.path == apiconst.ROUTE_FINANCIAL_DAY or req.path == apiconst.ROUTE_FINANCIAL_MONTH or req.path == apiconst.ROUTE_FINANCIAL_YEAR:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
            # rangetimestamp 
            v_rangetimestamp = ''
            
            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ),
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
            

        
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                        # parse timestamp
                        value =  clean_timestamp_str( value )
                        if validate_timestamp ( value ) == True:
                            v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )

            sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)
        
            
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if validate_timestamp_by_length( value ) == True:
                        #print( "key=" + key + " value=" + value ) 
                        v_rangetimestamp = " where substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

            sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
            #print( "# sqlstr=" + sqlstr) 

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  = e_db_financieel.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                    = a[0]   
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]                = a[1] 
                        new_dict[ apiconst.JSON_API_FNCL_CNSMPTN_E_H ]      = a[2]
                        new_dict[ apiconst.JSON_API_FNCL_CNSMPTN_E_L ]      = a[3]
                        new_dict[ apiconst.JSON_API_FNCL_PRDCTN_E_H ]       = a[4]
                        new_dict[ apiconst.JSON_API_FNCL_PRDCTN_E_L ]       = a[5] 
                        new_dict[ apiconst.JSON_API_FNCL_CNSMPTN_GAS ]      = a[6]
                        new_dict[ apiconst.JSON_API_FNCL_CNSMPTN_WATER ]    = a[7] 
                        json_obj_data.append( new_dict )

                    
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                    titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ),
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status


financial_resource = Financial()
app.add_route( apiconst.ROUTE_FINANCIAL_DAY,        financial_resource )
app.add_route( apiconst.ROUTE_FINANCIAL_DAY_HELP,   financial_resource )
app.add_route( apiconst.ROUTE_FINANCIAL_MONTH,      financial_resource )
app.add_route( apiconst.ROUTE_FINANCIAL_MONTH_HELP, financial_resource )
app.add_route( apiconst.ROUTE_FINANCIAL_YEAR,       financial_resource )
app.add_route( apiconst.ROUTE_FINANCIAL_YEAR_HELP,  financial_resource )
"""

class Status( object ):

    sqlstr_base_regular = 'select ID,STATUS,LABEL,SECURITY from status '

    def on_get( self, req, resp, id = 'all' ):
        """Handles all GET requests."""

        #print ( str(__class__.__name__) )
        #print ( req.query_string )
        #print ( 'req.params=' + str( req.params ) )
        #print ( 'req.path='   + str( req.path ) )
        #print ( apiconst.ROUTE_STATUS )
        #print ( 'id='         +  id )

        json_data  = {
            apiconst.JSON_API_STTS_ID  : 0,
            apiconst.JSON_API_STTS     : '',
            apiconst.JSON_API_STTS_LBL : '',
            apiconst.JSON_API_SCRTY    : 0
        }

        id = id.lower()
        #print ( id )

        if req.path.endswith('/help'):
            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": help aanpassen wegens id en help in path." )
            id = 'help'

        if id == 'help':
            try:
               
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_STATUS_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] +  apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     
        elif id == 'all':
            sqlstr = self.sqlstr_base_regular + 'order by id'
        else:
            try:
                sqlstr = self.sqlstr_base_regular +' where id = '+ str( abs(int( id, 10 )) ) # no negative numbers.
                flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" + sqlstr )
            except Exception as _e:
                    err_str = 'id value not ok, value used is ' + str( id )
                    flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                    raise falcon.HTTPError( 
                        status=apierror.API_PARAMETER_ERROR['status'], 
                        title=apierror.API_PARAMETER_ERROR['title'], 
                        description=apierror.API_PARAMETER_ERROR['description'] +  apiutil.santize_html( err_str ),
                        code=apierror.API_PARAMETER_ERROR['code'] 
                    )
    
        v_json_mode = ''
            
        for key, value in req.params.items():
            # this only gives the first parameter when more are put in
            value = list_filter_to_str( value )
            key = key.lower()
            #print ( key, value )
               
            if key == apiconst.API_PARAMETER_JSON_TYPE:     
                if value.lower() == 'object':
                    v_json_mode = 'object'
                    flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
               
        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

        try:
            # read datbase.
            records  = rt_status_db.select_rec( sqlstr )

            if v_json_mode ==  'object': 
                # process records for JSON opjects
                json_obj_data = [] 
                for a in records:
                    new_dict = json_data.copy()
                    new_dict[ apiconst.JSON_API_STTS_ID ]  = a[0] 
                    new_dict[ apiconst.JSON_API_STTS ]     = a[1] 
                    new_dict[ apiconst.JSON_API_STTS_LBL ] = a[2]
                    new_dict[ apiconst.JSON_API_SCRTY ]    = a[3]
                      
                    json_obj_data.append( new_dict )

                resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
            else:
                
                resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
        except Exception as _e:
            raise falcon.HTTPError( 
                status=apierror.API_DB_ERROR['status'], 
                titel=apierror.API_DB_ERROR['title'], 
                description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ),
                code=apierror.API_DB_ERROR['code'] 
                )
               
        resp.status = falcon.HTTP_200  # This is the default status

status_resource = Status()
app.add_route( apiconst.ROUTE_STATUS,         status_resource )
app.add_route( apiconst.ROUTE_STATUS_HELP,    status_resource )
app.add_route( apiconst.ROUTE_STATUS_ID,      status_resource )
app.add_route( apiconst.ROUTE_STATUS_ID_HELP, status_resource )

 
class Config( object ):
    
    sqlstr_base_regular = 'select ID,PARAMETER,LABEL from config '
   
    def on_get( self, req, resp, id = 'all' ):
        """Handles all GET requests."""

        #print ( str(__class__.__name__) )
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )
        #print ( apiconst.ROUTE_STATUS )

        json_data  = {
            apiconst.JSON_API_CNFG_ID    : 0,
            apiconst.JSON_API_CNFG_PRMTR : '',
            apiconst.JSON_API_CNFG_LABEL : ''
        }

        id = id.lower()
        #print ( id )

        if req.path.endswith('/help'):
            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": help aanpassen wegens id en help in path." )
            id = 'help'

        if id == 'help':
            try:
                
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_CONFIG_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     
        elif id == 'all':
            sqlstr = self.sqlstr_base_regular + 'order by id'
        else:
            try:
                sqlstr = self.sqlstr_base_regular +' where id = '+ str( abs(int( id, 10 )) ) # no negative numbers.
                flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" + sqlstr )
            except Exception as _e:
                    err_str = 'id value not ok, value used is ' + str( id )
                    flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                    raise falcon.HTTPError( 
                        status=apierror.API_PARAMETER_ERROR['status'], 
                        title=apierror.API_PARAMETER_ERROR['title'], 
                        description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ),
                        code=apierror.API_PARAMETER_ERROR['code'] 
                    )
    
        v_json_mode = ''
            
        for key, value in req.params.items():
            # this only gives the first parameter when more are put in
            value = list_filter_to_str( value )
            key = key.lower()
            #print ( key, value )
               
            if key == apiconst.API_PARAMETER_JSON_TYPE:     
                if value.lower() == 'object':
                    v_json_mode = 'object'
                    flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
               
        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

        try:
            # read datbase.
            records  = config_db.select_rec( sqlstr )

            if v_json_mode ==  'object': 
                # process records for JSON opjects
                json_obj_data = [] 
                for a in records:
                    new_dict = json_data.copy()
                    new_dict[ apiconst.JSON_API_CNFG_ID ]    = a[0] 
                    new_dict[ apiconst.JSON_API_CNFG_PRMTR ] = a[1] 
                    new_dict[ apiconst.JSON_API_CNFG_LABEL ] = a[2]
                      
                    json_obj_data.append( new_dict )

                resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
            else:
                
                resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
        except Exception as _e:
            raise falcon.HTTPError( 
                status=apierror.API_DB_ERROR['status'], 
                titel=apierror.API_DB_ERROR['title'], 
                description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                code=apierror.API_DB_ERROR['code'] 
                )
               
        resp.status = falcon.HTTP_200  # This is the default status

config_resource = Config()
app.add_route( apiconst.ROUTE_CONFIG,         config_resource )
app.add_route( apiconst.ROUTE_CONFIG_HELP,    config_resource )
app.add_route( apiconst.ROUTE_CONFIG_ID,      config_resource )
app.add_route( apiconst.ROUTE_CONFIG_ID_HELP, config_resource )

class SmartMeter( object ):

    sqlstr_base_regular = "select \
        TIMESTAMP, \
        cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
        RECORD_VERWERKT, \
        VERBR_KWH_181, \
        VERBR_KWH_182, \
        GELVR_KWH_281, \
        GELVR_KWH_282, \
        TARIEFCODE, \
        CAST( ACT_VERBR_KW_170 * 1000 AS INT), \
        CAST( ACT_GELVR_KW_270 * 1000 AS INT), \
        VERBR_GAS_2421 \
        from " + const.DB_SERIAL_TAB + " "
    
    sqlstr_base_round = "select \
        TIMESTAMP, \
        CAST(strftime('%s', TIMESTAMP, 'utc' ) AS INT), \
        RECORD_VERWERKT, \
        CAST( VERBR_KWH_181 as INT ), \
        CAST( VERBR_KWH_182 as INT ), \
        CAST( GELVR_KWH_281 as INT), \
        CAST( GELVR_KWH_282 as INT ), \
        TARIEFCODE, \
        CAST(ACT_VERBR_KW_170 * 1000 AS INT), \
        CAST(ACT_GELVR_KW_270 * 1000 AS INT), \
        CAST( VERBR_GAS_2421 as INT ) \
        from " + const.DB_SERIAL_TAB + " "
    

    def on_get(self, req, resp):
        """Handles all GET requests."""

        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL             : '',
            apiconst.JSON_TS_LCL_UTC         : 0,
            apiconst.JSON_API_REC_PRCSSD     : 0,
            apiconst.JSON_API_CNSMPTN_KWH_L  : 0,
            apiconst.JSON_API_CNSMPTN_KWH_H  : 0,
            apiconst.JSON_API_PRDCTN_KWH_L   : 0,
            apiconst.JSON_API_PRDCTN_KWH_H   : 0,
            apiconst.JSON_API_TRFCD          : '',
            apiconst.JSON_API_CNSMPTN_W      : 0,
            apiconst.JSON_API_PRDCTN_W       : 0,
            apiconst.JSON_API_CNSMPTN_GAS_M3 : 0
        }

        if req.path == apiconst.ROUTE_SMARTMETER_HELP:
            try:
               
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_SMARTMETER_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request on " + \
                apiconst.ROUTE_SMARTMETER_HELP  + " failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     

        # default sql string
        sqlstr = self.sqlstr_base_regular

        if req.path == apiconst.ROUTE_SMARTMETER:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
        
            
            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ),
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = self.sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                        # parse timestamp
                        value =  clean_timestamp_str( value )
                        if validate_timestamp ( value ) == True:
                            v_starttime = "where TIMESTAMP >= '" + value + "' order by timestamp "
                            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )

            sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  = e_db_serial.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]             = a[0] 
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]         = a[1] 
                        new_dict[ apiconst.JSON_API_REC_PRCSSD ]     = a[2]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_L ]  = a[3]
                        new_dict[ apiconst.JSON_API_CNSMPTN_KWH_H ]  = a[4]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_L ]   = a[5]
                        new_dict[ apiconst.JSON_API_PRDCTN_KWH_H ]   = a[6]
                        new_dict[ apiconst.JSON_API_TRFCD ]          = a[7]
                        new_dict[ apiconst.JSON_API_CNSMPTN_W ]      = a[8]
                        new_dict[ apiconst.JSON_API_PRDCTN_W ]       = a[9]
                        new_dict[ apiconst.JSON_API_CNSMPTN_GAS_M3 ] = a[10]
                        json_obj_data.append( new_dict )

                    
                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                    
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                    titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

smartmeter_resource = SmartMeter()
app.add_route( apiconst.ROUTE_SMARTMETER,      smartmeter_resource )
app.add_route( apiconst.ROUTE_SMARTMETER_HELP, smartmeter_resource )

class Watermeter( object ):

    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    TIMEPERIOD_ID, \
    PULS_PER_TIMEUNIT, \
    VERBR_PER_TIMEUNIT, \
    VERBR_IN_M3_TOTAAL \
    from " + const.DB_WATERMETERV2_TAB

    sqlstr_base_round = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    TIMEPERIOD_ID, \
    CAST( PULS_PER_TIMEUNIT as INT ), \
    CAST(VERBR_PER_TIMEUNIT as INT ), \
    CAST( VERBR_IN_M3_TOTAAL as INT ) \
    from " + const.DB_WATERMETERV2_TAB 


    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                  : '',
            apiconst.JSON_TS_LCL_UTC              : 0,
            apiconst.JSON_API_PROD_PERIOD_ID      : 0,
            apiconst.JSON_API_WM_PULS_CNT         : 0,
            apiconst.JSON_API_WM_CNSMPTN_LTR      : 0,
            apiconst.JSON_API_WM_CNSMPTN_LTR_M3   : 0
        }

        if req.path  == apiconst.ROUTE_WATERMETER_MIN_HELP_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_HOUR_HELP_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_DAY_HELP_V2  or \
            req.path == apiconst.ROUTE_WATERMETER_MONTH_HELP_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_YEAR_HELP_V2:
            
            flog.debug ( str(__name__) + " help data selected.")
            try:
               
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_WATERMETER_MIN_HOUR_DAY_MONTH_YEAR_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return 

        # set period index 
        v_period_id = 0
        if req.path == apiconst.ROUTE_WATERMETER_MIN_V2:
            v_period_id = " 11 "
        elif req.path == apiconst.ROUTE_WATERMETER_HOUR_V2:
            v_period_id = " 12 "
        elif req.path == apiconst.ROUTE_WATERMETER_DAY_V2:
            v_period_id = " 13 "
        elif req.path == apiconst.ROUTE_WATERMETER_MONTH_V2:
            v_period_id = " 14 "
        elif req.path == apiconst.ROUTE_WATERMETER_YEAR_V2:
            v_period_id = " 15 "

        # default sql string
        sqlstr = self.sqlstr_base_regular

        if req.path  == apiconst.ROUTE_WATERMETER_MIN_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_HOUR_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_DAY_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_MONTH_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_YEAR_V2:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
            # rangetimestamp 
            v_rangetimestamp = ''

            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ), 
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:    
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:     
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr =  self.sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        #v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp " 
                        v_starttime = " and TIMESTAMP >= '" + value + "' order by timestamp " #BUGFIX by Aad.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if validate_timestamp_by_length( value ) == True:
                        #print( "key=" + key + " value=" + value ) 
                        #v_rangetimestamp = " where substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                        v_rangetimestamp = " and substr(timestamp,1," +  str(len(value)) + ") = '" + value + "' order by timestamp "
                    else:
                        raise falcon.HTTPError( 
                            status=apierror.API_TIMESTAMP_ERROR['status'], 
                            title=apierror.API_TIMESTAMP_ERROR['title'], 
                            description=apierror.API_TIMESTAMP_ERROR['description'] + apiutil.santize_html( str(value) ),
                            code=apierror.API_TIMESTAMP_ERROR['code'] 
                        )

            sqlstr = sqlstr + " where TIMEPERIOD_ID = " + v_period_id  + v_starttime + v_rangetimestamp + v_sort + str(v_limit)

            #sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
            #print( "# sqlstr=" + sqlstr) 

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records = watermeter_db.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]            = a[1]
                        new_dict[ apiconst.JSON_API_PROD_PERIOD_ID ]    = a[2]
                        new_dict[ apiconst.JSON_API_WM_PULS_CNT ]       = a[3]
                        new_dict[ apiconst.JSON_API_WM_CNSMPTN_LTR ]    = a[4]
                        new_dict[ apiconst.JSON_API_WM_CNSMPTN_LTR_M3 ] = a[5]

                        json_obj_data.append( new_dict )

                    resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                   titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

watermeter_resource = Watermeter()
app.add_route( apiconst.ROUTE_WATERMETER_MIN_V2,        watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_MIN_HELP_V2,   watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_HOUR_V2,       watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_HOUR_HELP_V2,  watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_DAY_V2,        watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_DAY_HELP_V2,   watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_MONTH_V2,      watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_MONTH_HELP_V2, watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_YEAR_V2,       watermeter_resource )
app.add_route( apiconst.ROUTE_WATERMETER_YEAR_HELP_V2,  watermeter_resource )


class Phase( object ):

    sqlstr_base_regular = "select \
        TIMESTAMP, \
        cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
        VERBR_L1_KW * 1000, \
        VERBR_L2_KW * 1000, \
        VERBR_L3_KW * 1000, \
        GELVR_L1_KW * 1000, \
        GELVR_L2_KW * 1000, \
        GELVR_L3_KW * 1000, \
        L1_V, \
        L2_V, \
        L3_V, \
        L1_A, \
        L2_A, \
        L3_A \
        FROM " + const.DB_FASE_REALTIME_TAB + " "

    sqlstr_base_round = "select \
        TIMESTAMP, \
        cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
        CAST( VERBR_L1_KW * 1000 as INT ), \
        CAST( VERBR_L2_KW * 1000 as INT ), \
        CAST( VERBR_L3_KW * 1000 as INT ), \
        CAST( GELVR_L1_KW * 1000 as INT ), \
        CAST( GELVR_L2_KW * 1000 as INT ), \
        CAST( GELVR_L3_KW * 1000 as INT ), \
        CAST( L1_V as INT ), \
        CAST( L2_V as INT ), \
        CAST( L3_V as INT ), \
        CAST( L1_A as INT ), \
        CAST( L2_A as INT ), \
        CAST( L3_A as INT )  \
        FROM " + const.DB_FASE_REALTIME_TAB + " "
    
    def on_get(self, req, resp):
        """Handles all GET requests."""

        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                : '',
            apiconst.JSON_TS_LCL_UTC            : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L1_W  : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L2_W  : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L3_W  : 0,
            apiconst.JSON_API_PHS_PRDCTN_L1_W   : 0,
            apiconst.JSON_API_PHS_PRDCTN_L2_W   : 0,
            apiconst.JSON_API_PHS_PRDCTN_L3_W   : 0,
            apiconst.JSON_API_PHS_L1_V          : 0,
            apiconst.JSON_API_PHS_L2_V          : 0,
            apiconst.JSON_API_PHS_L3_V          : 0,
            apiconst.JSON_API_PHS_L1_A          : 0,
            apiconst.JSON_API_PHS_L2_A          : 0,
            apiconst.JSON_API_PHS_L3_A          : 0
        }

        if req.path == apiconst.ROUTE_PHASE_HELP:
            try:
                
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_PHASE_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request on " + \
                apiconst.ROUTE_PHASE_HELP  + " failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     

        # default sql string
        sqlstr = self.sqlstr_base_regular

        if req.path == apiconst.ROUTE_PHASE:
            
            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction ammount. 
            # json {default is array, object}
            v_json_mode = ''
            # starttime  =
            v_starttime = ' order by timestamp '
        
            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
                if key ==  apiconst.API_PARAMETER_LIMIT:
                    try:
                        v_limit = ' limit '+ str( abs(int( value, 10 )) ) # no negative numbers.
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'],
                            title=apierror.API_PARAMETER_ERROR['title'],
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ),
                            code=apierror.API_PARAMETER_ERROR['code']
                        )
                if key == apiconst.API_PARAMETER_SORT:
                    if value.lower() == 'asc':
                        v_sort = "ASC"
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = self.sqlstr_base_round
                        flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                        # parse timestamp
                        value =  clean_timestamp_str( value )
                        if validate_timestamp ( value ) == True:
                            v_starttime = "where TIMESTAMP >= '" + value + "' order by timestamp "
                            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )

            sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)

            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records  = fase_db.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    #json_obj_data = {}
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                = a[0] 
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]            = a[1] 
                        new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L1_W ]  = a[2]
                        new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L2_W ]  = a[3]
                        new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L3_W ]  = a[4]
                        new_dict[ apiconst.JSON_API_PHS_PRDCTN_L1_W ]   = a[5]
                        new_dict[ apiconst.JSON_API_PHS_PRDCTN_L2_W ]   = a[6]
                        new_dict[ apiconst.JSON_API_PHS_PRDCTN_L3_W ]   = a[7]
                        new_dict[ apiconst.JSON_API_PHS_L1_V ]          = a[8]
                        new_dict[ apiconst.JSON_API_PHS_L2_V ]          = a[9]
                        new_dict[ apiconst.JSON_API_PHS_L3_V ]          = a[10]
                        new_dict[ apiconst.JSON_API_PHS_L1_A ]          = a[11]
                        new_dict[ apiconst.JSON_API_PHS_L2_A ]          = a[12]
                        new_dict[ apiconst.JSON_API_PHS_L3_A ]          = a[13]
                        json_obj_data.append( new_dict )
                    
                    resp.text  = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )
                else:
                    resp.text = json.dumps( records, ensure_ascii=False )
                
                #print ( records )
            except Exception as _e:
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                   titel=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

phase_resource = Phase()
app.add_route( apiconst.ROUTE_PHASE,       phase_resource )
app.add_route( apiconst.ROUTE_PHASE_HELP , phase_resource )
