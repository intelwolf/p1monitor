import apiconst
import apierror
import apiutil
import const
import logging #needed for debugging
import json
import falcon
import inspect

class PhaseMinMaxHelp( object ):

    flog = None 

    def on_get(self, req, resp ):
        self.flog.debug ( str( __name__ ) + " help data selected.")
        try:
            resp.text = ( json.dumps( apiconst.HELP_ROUTE_POWER_PHASE_MINMAX_DAY_JSON, sort_keys=True , indent=2 ) ) 
        except Exception as _e:
            self.flog.error ( str( __class__.__name__ ) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
            raise falcon.HTTPError( 
                status=apierror.API_GENERAL_ERROR['status'], 
                title=apierror.API_GENERAL_ERROR['title'], 
                description=apierror.API_GENERAL_ERROR['description'] +  apiutil.santize_html( str(_e.args[0]) ), 
                code=apierror.API_GENERAL_ERROR['code'] 
                )
        return

    def set_flog( self , flog ):
        self.flog = flog


class PhaseMinMax( object ):
 
    flog     = None 
    database = None

    sqlstr_base_regular = "select \
    TIMESTAMP,\
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    MAX_VERBR_L1_KW * 1000,\
    MAX_VERBR_L2_KW * 1000,\
    MAX_VERBR_L3_KW * 1000,\
    MAX_GELVR_L1_KW * 1000,\
    MAX_GELVR_L2_KW * 1000,\
    MAX_GELVR_L3_KW * 1000,\
    MAX_L1_V,\
    MAX_L2_V,\
    MAX_L3_V,\
    MAX_L1_A,\
    MAX_L2_A,\
    MAX_L3_A,\
    MIN_VERBR_L1_KW * 1000, \
    MIN_VERBR_L2_KW * 1000, \
    MIN_VERBR_L3_KW * 1000, \
    MIN_GELVR_L1_KW * 1000, \
    MIN_GELVR_L2_KW * 1000, \
    MIN_GELVR_L3_KW * 1000, \
    MIN_L1_V,\
    MIN_L2_V,\
    MIN_L3_V,\
    MIN_L1_A,\
    MIN_L2_A,\
    MIN_L3_A \
    from " + const.DB_FASE_MINMAX_DAG_TAB

    sqlstr_base_round = "select \
    TIMESTAMP,\
    cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
    CAST ( MAX_VERBR_L1_KW * 1000 AS INT ),\
    CAST ( MAX_VERBR_L2_KW * 1000 AS INT ),\
    CAST ( MAX_VERBR_L3_KW * 1000 AS INT ),\
    CAST ( MAX_GELVR_L1_KW * 1000 AS INT ),\
    CAST ( MAX_GELVR_L2_KW * 1000 AS INT ),\
    CAST ( MAX_GELVR_L3_KW * 1000 AS INT ),\
    CAST ( MAX_L1_V AS INT ),\
    CAST ( MAX_L2_V AS INT ),\
    CAST ( MAX_L3_V AS INT ),\
    CAST ( MAX_L1_A AS INT ),\
    CAST ( MAX_L2_A AS INT ),\
    CAST ( MAX_L3_A AS INT ),\
    CAST ( MIN_VERBR_L1_KW * 1000 AS INT ),\
    CAST ( MIN_VERBR_L2_KW * 1000 AS INT ),\
    CAST ( MIN_VERBR_L3_KW * 1000 AS INT ),\
    CAST ( MIN_GELVR_L1_KW * 1000 AS INT ),\
    CAST ( MIN_GELVR_L2_KW * 1000 AS INT ),\
    CAST ( MIN_GELVR_L3_KW * 1000 AS INT ),\
    CAST ( MIN_L1_V AS INT ),\
    CAST ( MIN_L2_V AS INT ),\
    CAST ( MIN_L3_V AS INT ),\
    CAST ( MIN_L1_A AS INT ),\
    CAST ( MIN_L2_A AS INT ),\
    CAST ( MIN_L3_A AS INT ),\
    from " + const.DB_FASE_MINMAX_DAG_TAB


    def on_get(self, req, resp  ):
        """Handles all GET requests."""

        #self.flog.setLevel( logging.DEBUG )

        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        
        #print ( str(__class__.__name__) )
        #print ( req.query_string )
        #print ( 'req.params=' + str( req.params ) )
        #print ( 'req.path='   + str( req.path ) )
        #print ( apiconst.ROUTE_STATUS )

        json_data  = {
            apiconst.JSON_TS_LCL                    : '',
            apiconst.JSON_TS_LCL_UTC                : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L1_W_MAX  : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L2_W_MAX  : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L3_W_MAX  : 0,
            apiconst.JSON_API_PHS_PRDCTN_L1_W_MAX   : 0,
            apiconst.JSON_API_PHS_PRDCTN_L2_W_MAX   : 0,
            apiconst.JSON_API_PHS_PRDCTN_L3_W_MAX   : 0,
            apiconst.JSON_API_PHS_L1_V_MAX          : 0,
            apiconst.JSON_API_PHS_L2_V_MAX          : 0,
            apiconst.JSON_API_PHS_L3_V_MAX          : 0,
            apiconst.JSON_API_PHS_L1_A_MAX          : 0,
            apiconst.JSON_API_PHS_L2_A_MAX          : 0,
            apiconst.JSON_API_PHS_L3_A_MAX          : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L1_W_MIN  : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L2_W_MIN  : 0,
            apiconst.JSON_API_PHS_CNSMPTN_L3_W_MIN  : 0,
            apiconst.JSON_API_PHS_PRDCTN_L1_W_MIN   : 0,
            apiconst.JSON_API_PHS_PRDCTN_L2_W_MIN   : 0,
            apiconst.JSON_API_PHS_PRDCTN_L3_W_MIN   : 0,
            apiconst.JSON_API_PHS_L1_V_MIN          : 0,
            apiconst.JSON_API_PHS_L2_V_MIN          : 0,
            apiconst.JSON_API_PHS_L3_V_MIN          : 0,
            apiconst.JSON_API_PHS_L1_A_MIN          : 0,
            apiconst.JSON_API_PHS_L2_A_MIN          : 0,
            apiconst.JSON_API_PHS_L3_A_MIN          : 0
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
            value = apiutil.list_filter_to_str( value )
            
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
                    sqlstr = self.sqlstr_base_round
                    self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
            if key == apiconst.API_PARAMETER_STARTTIMESTAMP:
                    # parse timestamp
                    value =  apiutil.clean_timestamp_str( value )
                    if apiutil.validate_timestamp ( value ) == True:
                        v_starttime = "where TIMESTAMP >= '" + value + "' order by timestamp "
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query starttime is " +str(value) )
            if key == apiconst.API_PARAMETER_RANGETIMESTAMP:
                    # clear starttime where clause, there can only be one.
                    v_starttime = ''
                    if apiutil.validate_timestamp_by_length( value ) == True:
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

        sqlstr = sqlstr + v_starttime + v_rangetimestamp + v_sort + str(v_limit)
        #sqlstr = sqlstr +  v_starttime + v_sort + str(v_limit)
        sqlstr = " ".join(sqlstr.split())

        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

        try:
            # read datbase.
            records  = self.database.select_rec( sqlstr )
        
            if v_json_mode ==  'object': 
                # process records for JSON opjects
                json_obj_data = [] 
                #json_obj_data = {}
                for a in records:
                    new_dict = json_data.copy()
                    new_dict[ apiconst.JSON_TS_LCL ]                    = a[0]
                    new_dict[ apiconst.JSON_TS_LCL_UTC ]                = a[1]
                    new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L1_W_MAX ]  = a[2]
                    new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L2_W_MAX ]  = a[3]
                    new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L3_W_MAX ]  = a[4]
                    new_dict[ apiconst.JSON_API_PHS_PRDCTN_L1_W_MAX ]   = a[5]
                    new_dict[ apiconst.JSON_API_PHS_PRDCTN_L2_W_MAX ]   = a[6]
                    new_dict[ apiconst.JSON_API_PHS_PRDCTN_L3_W_MAX ]   = a[7]
                    new_dict[ apiconst.JSON_API_PHS_L1_V_MAX ]          = a[8]
                    new_dict[ apiconst.JSON_API_PHS_L2_V_MAX ]          = a[9]
                    new_dict[ apiconst.JSON_API_PHS_L3_V_MAX ]          = a[10]
                    new_dict[ apiconst.JSON_API_PHS_L1_A_MAX ]          = a[11]
                    new_dict[ apiconst.JSON_API_PHS_L2_A_MAX ]          = a[12]
                    new_dict[ apiconst.JSON_API_PHS_L3_A_MAX ]          = a[13]
                    new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L1_W_MIN ]  = a[14]
                    new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L2_W_MIN ]  = a[15]
                    new_dict[ apiconst.JSON_API_PHS_CNSMPTN_L3_W_MIN ]  = a[16]
                    new_dict[ apiconst.JSON_API_PHS_PRDCTN_L1_W_MIN ]   = a[17]
                    new_dict[ apiconst.JSON_API_PHS_PRDCTN_L2_W_MIN ]   = a[18]
                    new_dict[ apiconst.JSON_API_PHS_PRDCTN_L3_W_MIN ]   = a[19]
                    new_dict[ apiconst.JSON_API_PHS_L1_V_MIN ]          = a[20]
                    new_dict[ apiconst.JSON_API_PHS_L2_V_MIN ]          = a[21]
                    new_dict[ apiconst.JSON_API_PHS_L3_V_MIN ]          = a[22]
                    new_dict[ apiconst.JSON_API_PHS_L1_A_MIN ]          = a[23]
                    new_dict[ apiconst.JSON_API_PHS_L2_A_MIN ]          = a[24]
                    new_dict[ apiconst.JSON_API_PHS_L3_A_MIN]           = a[25]

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


    def set_flog( self , flog ):
        self.flog = flog

    def set_database( self , database ):
        self.database = database