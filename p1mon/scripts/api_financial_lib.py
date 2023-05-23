import apiconst
import apierror
import apiutil
import const
import json
import falcon
import inspect

from apiutil import list_filter_to_str, validate_timestamp_by_length

class FinancialDynamicTariffHelp( object ):

    def on_get(self, req, resp ):
        self.flog.debug ( str( __name__ ) + " help data selected.")

        if req.path == apiconst.ROUTE_FINANCIAL_DYNAMIC_TARIFF_HELP:
            self.flog.debug ( str(__name__) + " help data selected.")
            try:
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_FINANCIAL_DYNAMIC_TARIFF_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                self.flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + str(_e.args[0]), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return

    def set_flog( self , flog ):
        self.flog = flog

class FinancialDynamicTariff( object ):

    flog     = None 
    database = None

    sqlstr_base_regular = "select \
    TIMESTAMP, \
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    PRICE_KWH, \
    PRICE_GAS from "
   
    sqlstr_base_round = "select \
    TIMESTAMP, \
    cast( strftime('%s', TIMESTAMP, 'utc' ) AS Integer ), \
    CAST( PRICE_KWH as INT ), \
    CAST( PRICE_GAS as INT ) from "

    def on_get(self, req, resp):
        ## Handles all GET requests.
        
        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( req.path )

        json_data  = {
            apiconst.JSON_TS_LCL                : '',
            apiconst.JSON_TS_LCL_UTC            : 0,
            apiconst.JSON_API_FNCL_DYN_TRFF_KWH : 0,
            apiconst.JSON_API_FNCL_DYN_TRFF_GAS : 0
        }

        sqlstr_base_regular = self.sqlstr_base_regular + const.DB_ENERGIEPRIJZEN_UUR_TAB 
        sqlstr_base_round   = self.sqlstr_base_round   + const.DB_ENERGIEPRIJZEN_UUR_TAB  

        # default sql string
        sqlstr = sqlstr_base_regular

        if req.path == apiconst.ROUTE_FINANCIAL_DYNAMIC_TARIFF:
            
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
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
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

            self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                #records  = e_db_financieel.select_rec( sqlstr )
                records = self.database.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_TS_LCL ]                    = a[0]
                        new_dict[ apiconst.JSON_TS_LCL_UTC ]                = a[1] 
                        new_dict[ apiconst.JSON_API_FNCL_DYN_TRFF_KWH ]     = a[2]
                        new_dict[ apiconst.JSON_API_FNCL_DYN_TRFF_GAS ]     = a[3]
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

class FinancialHelp( object ):

    def on_get(self, req, resp ):
        self.flog.debug ( str( __name__ ) + " help data selected.")

        if req.path == apiconst.ROUTE_FINANCIAL_DAY_HELP or \
            req.path == apiconst.ROUTE_FINANCIAL_MONTH_HELP or \
                req.path == apiconst.ROUTE_FINANCIAL_YEAR_HELP:
            self.flog.debug ( str(__name__) + " help data selected.")
            try:
                
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_FINANCIAL_DAY_JSON, sort_keys=True , indent=2 ) )
            except Exception as _e:
                self.flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] + str(_e.args[0]), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
            return

    def set_flog( self , flog ):
        self.flog = flog

class Financial( object ):

    flog     = None 
    database = None

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
        
        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
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
        sqlstr = sqlstr_base_regular

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
                """"
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                        # parse timestamp
                        value =  clean_timestamp_str( value )
                        if validate_timestamp ( value ) == True:
                            v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
                            flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )

            sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)
            """
                if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # clear range where clause, there can only be one.
                    v_rangetimestamp = '' 
                    # parse timestamp
                    if validate_timestamp_by_length( value ) == True:
                        v_starttime = " where TIMESTAMP >= '" + value + "' order by timestamp "
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

            self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read datbase.
                #records  = e_db_financieel.select_rec( sqlstr )
                records = self.database.select_rec( sqlstr )

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
    
    def set_flog( self , flog ):
        self.flog = flog

    def set_database( self , database ):
        self.database = database
