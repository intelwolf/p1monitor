import apiconst
import apierror
import apiutil
import const
import json
import falcon
import inspect
import os

from apiutil import list_filter_to_str, validate_timestamp_by_length


class WatermeterDigital( object ):

    flog     = None 
    database = None

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
    CAST( VERBR_PER_TIMEUNIT as INT ), \
    CAST( VERBR_IN_M3_TOTAAL as INT ) \
    from " + const.DB_WATERMETERV2_TAB 

    def on_get(self, req, resp, id = 0):
        """Handles all GET requests."""
        
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )
        #print ( 'id = ' +  str(id) )

        json_data  = {
            apiconst.JSON_TS_LCL                  : '',
            apiconst.JSON_TS_LCL_UTC              : 0,
            apiconst.JSON_API_PROD_PERIOD_ID      : 0,
            apiconst.JSON_API_WM_PULS_CNT         : 0,
            apiconst.JSON_API_WM_CNSMPTN_LTR      : 0,
            apiconst.JSON_API_WM_CNSMPTN_LTR_M3   : 0
        }

        #basepath, basename = os.path.split( req.path ) 
        #basepath, basename = os.path.split( basepath ) 


        int_id = 0 
        try:
            int_id = int(id)
        except Exception:
            err_str = "Index number is not a number! index used is = " + str(id) + " should be a number starting with 1."
            self.flog.error ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": " + err_str)
            raise falcon.HTTPError( 
                status=apierror.API_PARAMETER_ERROR['status'], 
                title=apierror.API_PARAMETER_ERROR['title'], 
                description=apierror.API_PARAMETER_ERROR['description'] +  apiutil.santize_html( err_str ),
                code=apierror.API_PARAMETER_ERROR['code']
            )

        base_index = 0
        ############################################
        # convert is to base index of the database #
        # now support for 5 digital water meters   #
        ############################################
        if int_id == 1:
            base_index = 11
        elif int_id == 2:
            base_index = 21
        elif int_id == 3:
            base_index = 31
        elif int_id == 4:
            base_index = 41
        elif int_id == 5:
            base_index = 51
        elif int_id == 5:
            base_index = 61

        if base_index < 11 or base_index > 61:
             raise Exception ("index number is not in use = " + str(id) )
        
        #print("base_index = ", base_index )

        basepath, basename = os.path.split( req.path ) 
        #print ( "basepath = ", basepath )
        #print ( "basename = ", basename ) 
        #print ( "apiconst.ROUTE_WATERMETER_DIGITAL_MIN = ", apiconst.ROUTE_WATERMETER_DIGITAL_MIN ) 
        
        # set period index 
        v_period_id = 0
        good_route = False
        if basepath + "/{id}" == apiconst.ROUTE_WATERMETER_DIGITAL_MIN:
            v_period_id = base_index
            good_route = True
        elif basepath + "/{id}" == apiconst.ROUTE_WATERMETER_DIGITAL_HOUR:
            v_period_id = base_index + 1
            good_route = True
        elif basepath  + "/{id}" == apiconst.ROUTE_WATERMETER_DIGITAL_DAY:
            v_period_id = base_index + 2
            good_route = True
        elif basepath  + "/{id}" == apiconst.ROUTE_WATERMETER_DIGITAL_MONTH:
            v_period_id = base_index + 3
            good_route = True
        elif basepath  + "/{id}" == apiconst.ROUTE_WATERMETER_DIGITAL_YEAR:
            v_period_id = base_index + 4
            good_route = True

        # default sql string
        sqlstr = self.sqlstr_base_regular

        #print("v_period_id = ", v_period_id  )
        #print("good_route = ", good_route  )

        if good_route == True: 
            
            #print("run query")

            # PARAMETERS
            # limit (of records)  {default = all, >0 }
            v_limit = '' #means all records
            # sort (on timestamp) {default is desc, asc}
            v_sort = "DESC"
            # round ( default is off, on) whole number rounded up or down depending the fraction amount. 
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
                        sqlstr =  self.sqlstr_base_round
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        #v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp " 
                        v_starttime = " and TIMESTAMP >= '" + value + "' order by timestamp " #BUGFIX by Aad.
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
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

            sqlstr = sqlstr + " where TIMEPERIOD_ID = " + str(v_period_id)  + v_starttime + v_rangetimestamp + v_sort + str(v_limit)

            #sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
            sqlstr = " ".join(sqlstr.split())
            #print( "# sqlstr=" + sqlstr) 

            #self.flog.debug( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read database.
                #print ("sql query start.")
                records = self.database.select_rec( sqlstr )
                #print ("records = ", records)

                if v_json_mode ==  'object': 
                    # process records for JSON objects
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
                #print("oops", _e)
                raise falcon.HTTPError( 
                    status=apierror.API_DB_ERROR['status'], 
                    title=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

    def set_flog( self , flog ):
        self.flog = flog

    def set_database( self , database ):
        self.database = database

    def is_integer( self, num ):
        return isinstance(num, int)


class WaterDigitalHelp( object ):

    flog = None 

    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        #self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        if req.path  == apiconst.ROUTE_WATERMETER_DIGITAL_MIN_HELP or \
            req.path == apiconst.ROUTE_WATERMETER_DIGITAL_HOUR_HELP or \
            req.path == apiconst.ROUTE_WATERMETER_DIGITAL_DAY_HELP  or \
            req.path == apiconst.ROUTE_WATERMETER_DIGITAL_MONTH_HELP or \
            req.path == apiconst.ROUTE_WATERMETER_DIGITAL_YEAR_HELP:
            
            self.flog.debug ( str(__name__) + " help data selected.")

            try:
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_WATERMETER_DIGITAL_MIN_HOUR_DAY_MONTH_YEAR_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                self.flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return 

    def set_flog(self , flog):
        self.flog = flog


# Deprecated remove in future versions 
class WaterHelp( object ):
   
    flog = None 

    def on_get(self, req, resp):
        """Handles all GET requests."""
        
        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        if req.path  == apiconst.ROUTE_WATERMETER_MIN_HELP_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_HOUR_HELP_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_DAY_HELP_V2  or \
            req.path == apiconst.ROUTE_WATERMETER_MONTH_HELP_V2 or \
            req.path == apiconst.ROUTE_WATERMETER_YEAR_HELP_V2:
            
            self.flog.debug ( str(__name__) + " help data selected.")

            try:
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_WATERMETER_MIN_HOUR_DAY_MONTH_YEAR_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                self.flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ),
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return 

    def set_flog( self , flog ):
        self.flog = flog

# Deprecated remove in future versions 
class Watermeter( object ):

    flog     = None 
    database = None

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
        
        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
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
            # round ( default is off, on) whole number rounded up or down depending the fraction amount. 
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
                        sqlstr =  self.sqlstr_base_round
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        #v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp " 
                        v_starttime = " and TIMESTAMP >= '" + value + "' order by timestamp " #BUGFIX by Aad.
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
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

            self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read database.
                records = self.database.select_rec( sqlstr )

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
                    title=apierror.API_DB_ERROR['title'], 
                    description=apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] + " query used: " + sqlstr) ), 
                    code=apierror.API_DB_ERROR['code'] 
                    )
               
            resp.status = falcon.HTTP_200  # This is the default status

    def set_flog( self , flog ):
        self.flog = flog

    def set_database( self , database ):
        self.database = database

  

