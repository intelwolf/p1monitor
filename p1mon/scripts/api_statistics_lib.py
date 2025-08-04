import apiconst
import apierror
import apiutil
import json
import falcon
import inspect
import const

from apiutil import p1_serializer, validate_timestamp, clean_timestamp_str, list_filter_to_str, validate_timestamp_by_length

class StatisticsHelp( object ):

    flog = None

    def on_get(self, req, resp ):

        self.flog.debug ( str( __name__ ) + " help data selected.")

        if req.path == apiconst.ROUTE_STATISTICS_HELP:
           
            self.flog.debug ( str(__name__) + " help data selected.")
            try:
                resp.text = ( json.dumps( apiconst.HELP_ROUTE_STATISTICS_JSON, sort_keys=True , indent=2 ) )
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


class Statistics( object ):
    
    flog     = None 
    database = None

    sqlstr_base_regular = "select \
    ID,\
    DATA_ID,\
    ACTIVE,\
    TIMESTAMP_START,\
    TIMESTAMP_STOP,\
    MODE,\
    VALUE,\
    UPDATED\
    from " + const.DB_STATISTICS_TAB + " ORDER BY ID"

    sqlstr_base_round = "select \
    ID,\
    DATA_ID,\
    ACTIVE,\
    TIMESTAMP_START,\
    TIMESTAMP_STOP,\
    MODE,\
    CAST(VALUE as INT),\
    UPDATED\
    from " + const.DB_STATISTICS_TAB + " ORDER BY ID"


    def on_get( self, req, resp ):
        """Handles all GET requests."""
        
        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        #print ( req.query_string )
        #print ( req.params )
        #print ( "req.path = ", req.path )

        json_data  = {
            apiconst.JSON_API_ID                : 0,
            apiconst.JSON_API_DATA_ID           : 0,
            apiconst.JSON_API_ACTIVE            : 0,
            apiconst.JSON_API_TIMESTAMP_START   : '',
            apiconst.JSON_API_TIMESTAMP_STOP    : '',
            apiconst.JSON_API_MODE              : 0,
            apiconst.JSON_API_VALUE             : 0,
            apiconst.JSON_API_UPDATED           : ''
        }

        # default sql string
        sqlstr = self.sqlstr_base_regular
        
        if req.path == apiconst.ROUTE_STATISTICS:
          
            self.flog.debug ( str(__name__) + " route " + req.path + " is selected.")
            
            # round ( default is off, on) whole number rounded up or down depending the fraction amount. 
            # json {default is array, object}
            v_json_mode = ''
            
          
            for key, value in req.params.items():
               # this only gives the first parameter when more are put in
                value = list_filter_to_str( value )
                
                key = key.lower()
                #print ( key, value )
               
                if key == apiconst.API_PARAMETER_JSON_TYPE:
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query json naar object type gezet." )

                if key == apiconst.API_PARAMETER_ROUND: # round to the nearest value
                    if value.lower() == 'on':
                        sqlstr = self.sqlstr_base_round
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": sql query round aangezet." )
           
            self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": SQL = " + sqlstr )

            try:
                # read database.
                records = self.database.select_rec( sqlstr )

                if v_json_mode ==  'object': 
                    # process records for JSON opjects
                    json_obj_data = [] 
                    for a in records:
                        new_dict = json_data.copy()
                        new_dict[ apiconst.JSON_API_ID ]                = a[0]
                        new_dict[ apiconst.JSON_API_DATA_ID ]           = a[1]
                        new_dict[ apiconst.JSON_API_ACTIVE ]            = a[2]
                        new_dict[ apiconst.JSON_API_TIMESTAMP_START ]   = a[3]
                        new_dict[ apiconst.JSON_API_TIMESTAMP_STOP  ]   = a[4]
                        new_dict[ apiconst.JSON_API_MODE ]              = a[5]
                        new_dict[ apiconst.JSON_API_VALUE ]             = a[6]
                        new_dict[ apiconst.JSON_API_UPDATED ]           = a[7]
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
