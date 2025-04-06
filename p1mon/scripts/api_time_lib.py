import apiconst
import apierror
import apiutil
import const
import datetime
import logging #needed for debugging
import json
import falcon
import inspect
import time
import urllib.request
import datetime_lib

class DateTimeHelp( object ):

    flog = None 

    def on_get(self, req, resp ):
        self.flog.debug ( str( __name__ ) + " help data selected.")
        try:
            resp.text = ( json.dumps( apiconst.HELP_ROUTE_DATETIME, sort_keys=True , indent=2 ) ) 
            #resp.status = falcon.HTTP_200  # This is the default status
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


class DateTime( object ):
 
    flog = None 

    def on_get(self, req, resp  ):
        """Handles all GET requests."""

        #self.flog.setLevel( logging.DEBUG )

        self.flog.debug ( str(__name__) + " route " + req.path + " selected.")
        
        #print ( str(__class__.__name__) )
        #print ( req.query_string )
        #print ( 'req.params=' + str( req.params ) )
        #print ( 'req.path='   + str( req.path ) )
        #print ( apiconst.ROUTE_STATUS )

        try:
            record = [] #buffer for values
             
            inet_datatime_str, inet_datetime_utc = self.get_inet_timestamp()
            os_datatime_str, os_datetime_utc = self.get_os_timestamp()

            time_variance = inet_datetime_utc - os_datetime_utc 

            record.append( os_datatime_str )    # JSON_API_SYSTEM_DT
            record.append( os_datetime_utc )   # JSON_API_SYSTEM_DT_UTC
            record.append( inet_datatime_str )  # JSON_API_INET_DT 
            record.append( inet_datetime_utc ) # JSON_API_INET_DT_UTC
            record.append( time_variance )      # JSON_API_VARIANCE
         
            # PARAMETERS
            v_json_mode = ''

            for key, value in req.params.items():
            # this only gives the first parameter when more are put in
                value = apiutil.list_filter_to_str( value )
            
                key = key.lower()
                #print ( key, value )
               
                if key == apiconst.API_PARAMETER_JSON_TYPE:
                    if value.lower() == 'object':
                        v_json_mode = 'object'
                        self.flog.debug ( __class__.__name__ + ":" + inspect.stack()[0][3] + ": json naar object type gezet." )


            if v_json_mode == 'object':
                json_data  = {
                    apiconst.JSON_API_SYSTEM_DT        : record[0],
                    apiconst.JSON_API_SYSTEM_DT_UTC    : record[1],
                    apiconst.JSON_API_INET_DT          : record[2],
                    apiconst.JSON_API_INET_DT_UTC      : record[3],
                    apiconst.JSON_API_VARIANCE         : record[4]
                }
                resp.text  = json.dumps( json_data, ensure_ascii=False , sort_keys=True )
            else:
                resp.text = json.dumps( record, ensure_ascii=False )
            
            #print ( records )
        except Exception as _e:
            raise falcon.HTTPError( 
                status      = apierror.API_DB_ERROR['status'], 
                title       = apierror.API_DB_ERROR['title'], 
                description = apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] ) ),
                code        = apierror.API_DB_ERROR['code'] 
                )
    
        resp.status = falcon.HTTP_200  # This is the default status
        #self.flog.setLevel( logging.INFO )
        
    def set_flog( self , flog ):
        self.flog = flog

    def get_os_timestamp(self):
        return datetime_lib.get_os_timestamp( self.flog )

    def get_inet_timestamp(self):
        return datetime_lib.get_inet_timestamp( self.flog )

