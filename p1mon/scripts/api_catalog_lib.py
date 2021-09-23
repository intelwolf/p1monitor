import apiconst
import apierror
import apiutil
import const
import json
import falcon
import inspect
import network_lib

class CatalogHelp( object ):
    
    def on_get(self, req, resp):
        self.flog.debug ( str(__name__) + " help data selected.")
        try:
            
            resp.text = ( json.dumps( apiconst.HELP_ROUTE_CATALOG_JSON, sort_keys=True , indent=2 ) )
        except Exception as _e:
            self.flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request on " + \
            apiconst.ROUTE_CATALOG_HELP  + " failed , reason:" + str(_e.args[0]))
            raise falcon.HTTPError( 
                status=apierror.API_GENERAL_ERROR['status'], 
                title=apierror.API_GENERAL_ERROR['title'], 
                description=apierror.API_GENERAL_ERROR['description'] + apiutil.santize_html( str(_e.args[0]) ), 
                code=apierror.API_GENERAL_ERROR['code'] 
                )

    def set_flog( self , flog ):
        self.flog = flog

class Catalog( object ):
    
    flog = None 

    def on_get(self, req, resp):
        
        #print ( req.path )

        try:
            # get IP adress
            ipadress = '<IP adres niet gevonden>'
            result = network_lib.get_nic_info(nic='eth0')
            if result['result_ok'] == True and result['ip4'] != None: 
                ipadress = result['ip4']
            else:
                result = network_lib.get_nic_info(nic='wlan0')
                if result['result_ok'] == True and result['ip4'] != None: 
                    ipadress = result['ip4']
        
            json_obj_data = [] 
            with open( const.DIR_SCRIPTS + 'apiconst.py' ) as search:
                for line in search:
                    line = line.rstrip()  # remove '\n' at end of line
                   
                    if line.startswith('ROUTE_'):  # add ROUTE entries 
                        #if '_HELP' in line or '{id}' in line or '{power_source_id}' in line: # remove HELP ROUTES & id's routes
                        if '_HELP' in line or '{id}' in line: # remove HELP ROUTES & id's routes
                            continue
                        
                        #print ( line )
                        route = line.split('=')[1].replace("'","").replace("/{power_source_id}","").strip()
                        json_obj_data.append( ipadress + route )

                #json_obj_data.sort() #sort the routes

                json_obj_data_routes = [] 

                for route in json_obj_data: 
                    json_obj_data_routes.append( route )
                    help_route = route.replace("/{db_index}","").strip()
                    json_obj_data_routes.append( help_route + '/help')

                for idx in range( len( json_obj_data_routes ) ): 
                    if 'help' in json_obj_data_routes[ idx ]: # skip help lines.
                        continue
                    if apiconst.BASE_POWERPRODUCTION_SOLAR in json_obj_data_routes[ idx ]:
                        json_obj_data_routes[idx] = json_obj_data_routes[idx].replace("/{db_index}","/1/{db_index}").strip()

            #print ( json_obj_data_routes )
            json_obj_data_routes.sort()

            resp.text = json.dumps( json_obj_data_routes, ensure_ascii=False )   
            resp.status = falcon.HTTP_200  # This is the default status
        
        except Exception as _e:
                self.flog.error ( str(__class__.__name__) + ":" + inspect.stack()[0][3] + ": help request failed , reason:" + str(_e.args[0]))
                raise falcon.HTTPError( 
                    status=apierror.API_GENERAL_ERROR['status'], 
                    title=apierror.API_GENERAL_ERROR['title'], 
                    description=apierror.API_GENERAL_ERROR['description'] +  apiutil.santize_html( str(_e.args[0]) ), 
                    code=apierror.API_GENERAL_ERROR['code'] 
                    )
        return     
        
    def set_flog( self , flog ):
        self.flog = flog