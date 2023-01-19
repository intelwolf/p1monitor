import apiconst
import apierror
import apiutil
#import const
#import logging
import json
import falcon
import inspect
#import os
#import solaredge_shared_lib

from apiutil import p1_serializer, validate_timestamp, clean_timestamp_str, list_filter_to_str, validate_timestamp_by_length

class WeatherHistoryHelp( object ):

    flog = None

    def on_get(self, req, resp ):
        self.flog.debug ( str( __name__ ) + " help data selected.")

        if req.path == apiconst.ROUTE_WEATHER_HOUR_HELP or \
            req.path == apiconst.ROUTE_WEATHER_DAY_HELP  or \
            req.path == apiconst.ROUTE_WEATHER_MONTH_HELP or \
            req.path == apiconst.ROUTE_WEATHER_YEAR_HELP:
            
            self.flog.debug ( str(__name__) + " help data selected.")
            try:
                
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_WEATHER_DAY_MONTH_YEAR_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                self.flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0] ) ), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return     

    def set_flog( self , flog ):
        self.flog = flog



class WeatherHistory( object ):
    
    flog     = None 
    database = None

    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer),\
    CITY_ID, \
    CITY, \
    TEMPERATURE_MIN, \
    TEMPERATURE_AVG, \
    TEMPERATURE_MAX, \
    PRESSURE_MIN, \
    PRESSURE_AVG, \
    PRESSURE_MAX, \
    HUMIDITY_MIN, \
    HUMIDITY_AVG, \
    HUMIDITY_MAX, \
    WIND_SPEED_MIN, \
    WIND_SPEED_AVG, \
    WIND_SPEED_MAX, \
    WIND_DEGREE_MIN, \
    WIND_DEGREE_AVG,\
    WIND_DEGREE_MAX, \
    DEGREE_DAYS \
    from "


    sqlstr_base_round  = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer),\
    CITY_ID,\
    CITY, \
    CAST( TEMPERATURE_MIN as INT ), \
    CAST( TEMPERATURE_AVG as INT ), \
    CAST( TEMPERATURE_MAX as INT ), \
    PRESSURE_MIN, \
    PRESSURE_AVG, \
    PRESSURE_MAX, \
    HUMIDITY_MIN, \
    HUMIDITY_AVG, \
    HUMIDITY_MAX, \
    CAST( WIND_SPEED_MIN as INT ), \
    CAST( WIND_SPEED_AVG as INT ), \
    CAST( WIND_SPEED_MAX as INT ), \
    CAST( WIND_DEGREE_MIN as INT ), \
    CAST( WIND_DEGREE_AVG as INT ), \
    CAST( WIND_DEGREE_MAX as INT ), \
    CAST( DEGREE_DAYS as INT )  \
    from "


    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                 : '',
            apiconst.JSON_TS_LCL_UTC             : 0,
            apiconst.JSON_API_CTY_ID             : 0,
            apiconst.JSON_API_CTY_NM             : 0,
            apiconst.JSON_API_TMPRTR_L           : 0,
            apiconst.JSON_API_TMPRTR_A           : 0,
            apiconst.JSON_API_TMPRTR_H           : 0,
            apiconst.JSON_API_PRSSR_L            : 0,
            apiconst.JSON_API_PRSSR_A            : 0,
            apiconst.JSON_API_PRSSR_H            : 0,
            apiconst.JSON_API_HUMIDITY_L         : 0,
            apiconst.JSON_API_HUMIDITY_A         : 0,
            apiconst.JSON_API_HUMIDITY_H         : 0,
            apiconst.JSON_API_WND_SPD_L          : 0,
            apiconst.JSON_API_WND_SPD_A          : 0,
            apiconst.JSON_API_WND_SPD_H          : 0,
            apiconst.JSON_API_WND_DGRS_L         : 0,
            apiconst.JSON_API_WND_DGRS_A         : 0,
            apiconst.JSON_API_WND_DGRS_H         : 0,
            apiconst.JSON_DGR_DYS                : 0
        }

        if req.path == apiconst.ROUTE_WEATHER_HOUR:
            sqlstr_base_regular = self.sqlstr_base_regular + 'weer_history_uur '
            sqlstr_base_round   = self.sqlstr_base_round   + 'weer_history_uur '
        if req.path == apiconst.ROUTE_WEATHER_DAY:
            sqlstr_base_regular = self.sqlstr_base_regular + 'weer_history_dag '
            sqlstr_base_round   = self.sqlstr_base_round   + 'weer_history_dag '
        if req.path == apiconst.ROUTE_WEATHER_MONTH:
            sqlstr_base_regular = self.sqlstr_base_regular + 'weer_history_maand '
            sqlstr_base_round   = self.sqlstr_base_round   + 'weer_history_maand '
        if req.path == apiconst.ROUTE_WEATHER_YEAR:
            sqlstr_base_regular = self.sqlstr_base_regular + 'weer_history_jaar '
            sqlstr_base_round   = self.sqlstr_base_round   + 'weer_history_jaar '

        # default sql string
        sqlstr  = sqlstr_base_regular
        

        if req.path == apiconst.ROUTE_WEATHER_HOUR or \
            req.path == apiconst.ROUTE_WEATHER_DAY or \
            req.path == apiconst.ROUTE_WEATHER_MONTH or \
            req.path == apiconst.ROUTE_WEATHER_YEAR:
            
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
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                    except Exception as _e:
                        err_str = 'limit value not ok, value used is ' + str(value)
                        self.flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                        raise falcon.HTTPError( 
                            status=apierror.API_PARAMETER_ERROR['status'], 
                            title=apierror.API_PARAMETER_ERROR['title'], 
                            description=apierror.API_PARAMETER_ERROR['description'] + apiutil.santize_html( err_str ), 
                            code=apierror.API_PARAMETER_ERROR['code'] 
                        )
                if key == apiconst.API_PARAMETER_SORT:
                    if value.lower() == 'asc':
                        v_sort = "ASC" 
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query sort naar asc gezet." )
                if key == apiconst.API_PARAMETER_JSON_TYPE:
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )
                if key == apiconst.API_PARAMETER_ROUND: # round to the nearst value
                    if value.lower() == 'on':
                        sqlstr = sqlstr_base_round
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                        # parse timestamp
                        value =  clean_timestamp_str( value )
                        if validate_timestamp ( value ) == True:
                            v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                            self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )

            sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)

            self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                records = self.database.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]         = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]     = a[1]
                        new_dict[ apiconst.JSON_API_CTY_ID ]     = a[2]
                        new_dict[ apiconst.JSON_API_CTY_NM ]     = a[3]
                        new_dict[ apiconst.JSON_API_TMPRTR_L ]   = a[4]
                        new_dict[ apiconst.JSON_API_TMPRTR_A ]   = a[5]
                        new_dict[ apiconst.JSON_API_TMPRTR_H ]   = a[6]
                        new_dict[ apiconst.JSON_API_PRSSR_L ]    = a[7]
                        new_dict[ apiconst.JSON_API_PRSSR_A ]    = a[8]
                        new_dict[ apiconst.JSON_API_PRSSR_H ]    = a[9]
                        new_dict[ apiconst.JSON_API_HUMIDITY_L ] = a[10]
                        new_dict[ apiconst.JSON_API_HUMIDITY_A ] = a[11]
                        new_dict[ apiconst.JSON_API_HUMIDITY_H ] = a[12]
                        new_dict[ apiconst.JSON_API_WND_SPD_L ]  = a[13]
                        new_dict[ apiconst.JSON_API_WND_SPD_A ]  = a[14]
                        new_dict[ apiconst.JSON_API_WND_SPD_H ]  = a[15]
                        new_dict[ apiconst.JSON_API_WND_DGRS_L ] = a[16]
                        new_dict[ apiconst.JSON_API_WND_DGRS_A ] = a[17]
                        new_dict[ apiconst.JSON_API_WND_DGRS_H ] = a[18]
                        new_dict[ apiconst.JSON_DGR_DYS ]        = a[19]
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

    def set_flog( self , flog ):
        self.flog = flog

    def set_database( self , database ):
        self.database = database
