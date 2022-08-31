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

class P1PortTelegramHelp( object ):

    flog = None 

    def on_get(self, req, resp ):
        self.flog.debug ( str( __name__ ) + " help data selected.")
        try:
            resp.text = ( json.dumps( apiconst.HELP_ROUTE_P1_PORT_TELEGRAM, sort_keys=True , indent=2 ) ) 
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


class P1PortTelegram( object ):
 
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
            content = ""
            for i in range( 10 ):
                try:
                    with open( const.FILE_P1MSG ) as f:
                        content = f.read()
                        break
                except Exception:
                    #print( "wait" )
                    time.sleep( 0.1 ) 
                    continue
        
            record = []

            dt = datetime.datetime.now( datetime.timezone.utc )
            utc_time = dt.replace( tzinfo=datetime.timezone.utc )
            t=time.localtime()
            record.append( "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) ) 
            record.append( int( utc_time.timestamp() ) ) 
            if ( content != "" ):
                record.append( apiconst.API_STATUS_VALID )
            else:
                record.append( apiconst.API_STATUS_INVALID )
            record.append ( content )

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
                    apiconst.JSON_TS_LCL            : record[0],
                    apiconst.JSON_TS_LCL_UTC        : record[1],
                    apiconst.JSON_API_VALID_DATA    : record[2],
                    apiconst.JSON_API_P1_TELEGRAM   : record[3],
                }
                resp.text  = json.dumps( json_data  , ensure_ascii=False , sort_keys=True )
            else:
                resp.text = json.dumps( record, ensure_ascii=False )
            
            #print ( records )
        except Exception as _e:
            raise falcon.HTTPError( 
                status      = apierror.API_DB_ERROR['status'], 
                titel       = apierror.API_DB_ERROR['title'], 
                description = apierror.API_DB_ERROR['description'] + apiutil.santize_html( str(_e.args[0] ) ),
                code        = apierror.API_DB_ERROR['code'] 
                )
            
        resp.status = falcon.HTTP_200  # This is the default status

    def set_flog( self , flog ):
        self.flog = flog