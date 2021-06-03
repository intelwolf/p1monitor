import apiconst
import apierror
import apiutil
import const
import logging
import json
import falcon
import inspect
import os
import solaredge_shared_lib

from apiutil import p1_serializer, validate_timestamp, clean_timestamp_str, list_filter_to_str, validate_timestamp_by_length

class powerProductionSolarHelp( object ):

    flog = None 

    def on_get(self, req, resp ):
        self.flog.debug ( str( __name__ ) + " help data selected.")
        try:
            resp.text = ( json.dumps( apiconst.HELP_ROUTE_POWER_PRODUCTION_SOLAR_MIN_DAY_MONTH_YEAR_JSON, sort_keys=True , indent=2 ) ) 
        except Exception as _e:
            self.flog.error ( str( __class__.__name__ ) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
            raise falcon.HTTPError( 
                status=apierror.API_GENERAL_ERROR['status'], 
                title=apierror.API_GENERAL_ERROR['title'], 
                description=apierror.API_GENERAL_ERROR['description'] + str(_e.args[0]), 
                code=apierror.API_GENERAL_ERROR['code'] 
                )
        return

    def set_flog( self , flog ):
        self.flog = flog


class powerProductionSolar( object ):
 
    flog     = None 
    database = None

    sqlstr_base_regular = "select \
    TIMESTAMP,\
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    TIMEPERIOD_ID,\
    POWER_SOURCE_ID,\
    PRODUCTION_KWH_HIGH,\
    PRODUCTION_KWH_LOW,\
    PRODUCTION_KWH_HIGH_TOTAL,\
    PRODUCTION_KWH_LOW_TOTAL,\
    PRODUCTION_KWH_TOTAL from " + const.DB_POWERPRODUCTION_SOLAR_TAB

    sqlstr_base_round = "select \
    TIMESTAMP,\
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    TIMEPERIOD_ID,\
    POWER_SOURCE_ID,\
    CAST( PRODUCTION_KWH_HIGH as INT ),\
    CAST( PRODUCTION_KWH_LOW as INT ),\
    CAST( PRODUCTION_KWH_HIGH_TOTAL as INT ),\
    CAST( PRODUCTION_KWH_LOW_TOTAL as INT ),\
    CAST( PRODUCTION_KWH_TOTAL as INT ) from " + const.DB_POWERPRODUCTION_SOLAR_TAB

    def on_get(self, req, resp, power_source_id = 0 , db_index=0 ):
        """Handles all GET requests."""

        #self.flog.setLevel( logging.DEBUG )

        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        
        #print ( str(__class__.__name__) )
        #print ( req.query_string )
        #print ( 'req.params=' + str( req.params ) )
        #print ( 'req.path='   + str( req.path ) )
        #print ( apiconst.ROUTE_STATUS )
        #print ( 'power_source_id =' +  str(power_source_id)  )
        #print( type(power_source_id) )
        #print ( apiconst.ROUTE_POWERPRODUCTION_SOLAR_YEAR )

        #clean the path of the power_source_id for easy processing.

        try:
            power_source_id = int(power_source_id)
        except Exception as _e:
            self.flog.error ( str( __class__.__name__ ) + ":" + inspect.stack()[0][3] + ": " + str(_e.args[0]) )
            raise falcon.HTTPError( 
                    status=apierror.API_PARAMETER_ERROR['status'], 
                    title=apierror.API_PARAMETER_ERROR['title'], 
                    description=apierror.API_PARAMETER_ERROR['description'] + " power_source_id must be a number > 0 " + str(_e.args[0]), 
                    code=apierror.API_PARAMETER_ERROR['code']
                    )

        # find the basepath so we can set the min,hour,day,month or year
        basepath, basename = os.path.split( req.path ) 
        basepath, basename = os.path.split( basepath ) 
        check_path = basepath + "/{power_source_id}/{db_index}" 

        #################################################################################
        # power_source_id is not used, could be in the future to switch database/tables #
        #################################################################################
        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": check_path = " +str(check_path) )

        db_index = int(db_index)

        if db_index not in solaredge_shared_lib.SQL_INDEX_NUMBERS:
            err_str = 'database index must be a value in the range ' + str( solaredge_shared_lib.SQL_INDEX_NUMBERS )
            self.flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
            raise falcon.HTTPError( 
                status=apierror.API_PARAMETER_ERROR['status'], 
                title=apierror.API_PARAMETER_ERROR['title'], 
                description=apierror.API_PARAMETER_ERROR['description'] + err_str, 
                code=apierror.API_PARAMETER_ERROR['code'] 
            )

        if check_path == apiconst.ROUTE_POWERPRODUCTION_SOLAR_MIN:
                    db_index += 1
        elif check_path == apiconst.ROUTE_POWERPRODUCTION_SOLAR_HOUR:
                    db_index += 2
        elif check_path == apiconst.ROUTE_POWERPRODUCTION_SOLAR_DAY:
                    db_index += 3
        elif check_path == apiconst.ROUTE_POWERPRODUCTION_SOLAR_MONTH:
                    db_index += 4
        elif check_path == apiconst.ROUTE_POWERPRODUCTION_SOLAR_YEAR:
                    db_index += 5

        json_data  = {
            apiconst.JSON_TS_LCL               : '',
            apiconst.JSON_TS_LCL_UTC           : 0,
            apiconst.JSON_API_PROD_PERIOD_ID   : 0,
            apiconst.JSON_API_PROD_PWR_SRC_ID  : 0,
            apiconst.JSON_API_PROD_KWH_H       : 0,
            apiconst.JSON_API_PROD_KWH_L       : 0,
            apiconst.JSON_API_PROD_KWH_TOTAL_H : 0,
            apiconst.JSON_API_PROD_KWH_TOTAL_L : 0,
            apiconst.JSON_API_PROD_KWH_TOTAL   : 0
        }

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
                    self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query" +str(v_limit) )
                except Exception as _e:
                    err_str = 'limit value not ok, value used is ' + str(value)
                    self.flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
                    raise falcon.HTTPError( 
                        status=apierror.API_PARAMETER_ERROR['status'], 
                        title=apierror.API_PARAMETER_ERROR['title'], 
                        description=apierror.API_PARAMETER_ERROR['description'] + err_str, 
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
                    sqlstr = self.sqlstr_base_round
                    self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )

            if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                # clear range where clause, there can only be one.
                v_rangetimestamp = '' 
                # parse timestamp
                if validate_timestamp_by_length( value ) == True:
                    v_starttime = " and TIMESTAMP >= '" + value + "' order by timestamp "
                    self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
                else:
                    raise falcon.HTTPError( 
                        status=apierror.API_TIMESTAMP_ERROR['status'], 
                        title=apierror.API_TIMESTAMP_ERROR['title'], 
                        description=apierror.API_TIMESTAMP_ERROR['description'] + str(value),
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
                        description=apierror.API_TIMESTAMP_ERROR['description'] + str(value),
                        code=apierror.API_TIMESTAMP_ERROR['code'] 
                    )

        #json_main_data_set = [] 
       
        sqlstr = sqlstr + " where TIMEPERIOD_ID = " + str( db_index )  + " and POWER_SOURCE_ID = 1 " + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
        sqlstr = " ".join(sqlstr.split())

        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

        #print ( sqlstr )

        try:
            # read datbase.
            records = self.database.select_rec( sqlstr )
            #print ( records )

            if v_json_mode == 'object': 
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
                    new_dict[ apiconst.JSON_API_PROD_KWH_TOTAL_H ] = a[6]
                    new_dict[ apiconst.JSON_API_PROD_KWH_TOTAL_L ] = a[7]
                    new_dict[ apiconst.JSON_API_PROD_KWH_TOTAL ]   = a[8]
                    json_obj_data.append( new_dict )

                #self.flog.setLevel( logging.INFO )
                resp.text = json.dumps( json_obj_data , ensure_ascii=False , sort_keys=True )

            else:

                #self.flog.setLevel( logging.INFO )
                resp.text = json.dumps( records, ensure_ascii=False )

        except Exception as _e:
            raise falcon.HTTPError( 
                status=apierror.API_DB_ERROR['status'], 
                titel=apierror.API_DB_ERROR['title'], 
                description=apierror.API_DB_ERROR['description'] + str(_e.args[0] + " query used: " + sqlstr), 
                code=apierror.API_DB_ERROR['code'] 
                )

        resp.status = falcon.HTTP_200  # This is the default status

    def set_flog( self , flog ):
        self.flog = flog

    def set_database( self , database ):
        self.database = database