####################################################################
# shared lib for wifi functions > V3.0.0                           #
####################################################################

import base64
import const
import inspect
import sqldb
import crypto_lib
import nmcli_lib

CRYPTO_SEED_WIFI                = 'wifipw'
WPA_SUPPLICANT_CONF_FILEPATH    = '/etc/wpa_supplicant/wpa_supplicant.conf'

####################################################
# set wifi netwerk with parameters                 #
####################################################
class WifiConfigure():

    def __init__( self, essid=None, key=None, flog=None ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name 
        self.flog = flog

    ############################################################
    # set up an wifi configuration essid and key are mandatory #
    ############################################################
    def set(self ,essid=None, key=None, ip4=None, ip4gateway=None, ip4dns=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if self.flog != None:
            self.flog.info( FUNCTION_TAG + ": configuration of Wifi started.")

        if essid == None or len(essid)==0 :
            msg = FUNCTION_TAG + ": ESSID is not set!"
            self.flog.critical( msg )
            raise Exception( msg ) 

        if key == None or len(key)==0:
            msg = FUNCTION_TAG + ": key is not set!"
            self.flog.critical( msg )
            raise Exception( msg ) 

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": essid = " + essid)
            self.flog.debug( FUNCTION_TAG + ": key = " + key)

        nmcli = nmcli_lib.Device( flog=self.flog )
    
        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == True: # check if the connection is set, only then remove
            nmcli.remove_connection( name=nmcli_lib.WIFI_NAME ) # needed to make sure there is only one connection 

        nmcli.set_wifi( wifi_essid=essid, wifi_key=key, ip4=ip4, ip4gateway=ip4gateway, ip4dns=ip4dns  )
       

    ############################################################
    # remove the wifi connection                               #
    ############################################################
    def unset(self) :

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name
        nmcli = nmcli_lib.Device( flog=self.flog )

        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == False:
            if self.flog != None:
                self.flog.warning( FUNCTION_TAG + ": connection " + str(nmcli_lib.WIFI_NAME) + " is not active, stopped." )
            return
        
        nmcli.remove_connection( name=nmcli_lib.WIFI_NAME )

    ###########################################################
    # set the ip4 address                                     #
    ###########################################################
    def set_ip4( self, ip4=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if self.flog != None:
            self.flog.info( FUNCTION_TAG + ": configuration of IP4 address is started " + str(ip4) )

        nmcli = nmcli_lib.Device( flog=self.flog )
        
        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == False:
            if self.flog != None:
                self.flog.warning( FUNCTION_TAG + ": connection " + str(nmcli_lib.WIFI_NAME) + " is not active, stopped." )
            return

        list_ip4 = [ ip4 ]
        nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting= "ip4", property=list_ip4 )   

        # needs reset to make new IP active
        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": resetting connection to activate new IP address " + str(ip4) )
        
        nmcli.connection_mode(name=nmcli_lib.WIFI_NAME, active=False)
        nmcli.connection_mode(name=nmcli_lib.WIFI_NAME, active=True)

    ##########################################################
    # set the ip4 gateway, can only be set if IP4 address is #
    # set                                                    #
    ##########################################################
    def set_ip4gw( self, ip4gw=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": configuration of IP4 gateway started " + str(ip4gw) )

        nmcli = nmcli_lib.Device( flog=self.flog )
        
        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == False:
            if ( self.flog != None ):
                self.flog.warning( FUNCTION_TAG + ": connection " + str(nmcli_lib.WIFI_NAME) + " is not active, stopped." )
            return
    
        # Gateway can only be set if ip4 is set, check if IP4 address is set
        list_output = nmcli.read_setting( name=nmcli_lib.WIFI_NAME, setting="ipv4.addresses" )
        #list_output = nmcli.read_setting( name=nmcli_lib.WIFI_NAME, setting="address-data" )
        
        #print ("##",list_output )
        if (len(list_output) == 0 ):
            if ( self.flog != None ):
                self.flog.warning( FUNCTION_TAG + ": ip4 is not set this is mandatory, stopped." )
            return

        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": configuration of IP4 gateway started for address " + str(ip4gw) )

        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == False:
            if ( self.flog != None ):
                self.flog.warning( FUNCTION_TAG + ": connection " + str(nmcli_lib.WIFI_NAME) + " is not active, stopped." )
            return

        list_ip4fgw = [ ip4gw ]
        nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting= "gw4", property=list_ip4fgw )   

        # needs reset to make new gateway active
        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": resetting connection to activate new IP address for gateway " + str(ip4gw) )
        nmcli.connection_mode(name=nmcli_lib.WIFI_NAME, active=False)
        nmcli.connection_mode(name=nmcli_lib.WIFI_NAME, active=True)

    #########################################################
    # set the dns servers                                   #
    #########################################################
    def set_dns( self, ip4_dns=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": configuration of dns started for IP4 DNS addresses " + str(ip4_dns) )

        nmcli = nmcli_lib.Device( flog=self.flog )

        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == False:
            if ( self.flog != None ):
                self.flog.warning( FUNCTION_TAG + ": connection " + str(nmcli_lib.WIFI_NAME) + " is not active, stopped." )
            return
            
        nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting= "ipv4.ignore-auto-dns yes ipv4.dns", property=ip4_dns )
        # needs reset to make DNS active
        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": resetting connection to activate DNS setting" )
        nmcli.connection_mode(name=nmcli_lib.WIFI_NAME, active=False)
        nmcli.connection_mode(name=nmcli_lib.WIFI_NAME, active=True)
 
    def unset_ip4( self ):
         
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": removal of ipv4 address and gateway started." )

        nmcli = nmcli_lib.Device( flog=self.flog )

        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == False:
            if ( self.flog != None ):
                self.flog.warning( FUNCTION_TAG + ": connection " + str(nmcli_lib.WIFI_NAME) + " is not active, stopped." )
            return

        nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting="ipv4.method", property=["auto"] )
        nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting="ipv4.gateway", property=[""] )
        nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting="ipv4.address", property=[""] )
        nmcli.connection_mode( name=nmcli_lib.WIFI_NAME, active=False )
        nmcli.connection_mode( name=nmcli_lib.WIFI_NAME, active=True )

        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": removal of ipv4 address and gateway done." )


    def unset_ip4dns(self):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": removal of ipv4 DNS address(es) started." )

        nmcli = nmcli_lib.Device( flog=self.flog )

        if nmcli.is_active_connection( name=nmcli_lib.WIFI_NAME ) == False:
            if ( self.flog != None ):
                self.flog.warning( FUNCTION_TAG + ": connection " + str(nmcli_lib.WIFI_NAME) + " is not active, stopped." )
            return

        #nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting="ipv4.ignore-auto-dns", property=["no"] )
        #nmcli.change_setting( name=nmcli_lib.WIFI_NAME, setting="ipv4.dns", property=[""] )
        #nmcli.connection_mode( name=nmcli_lib.WIFI_NAME, active=False )
        #nmcli.connection_mode( name=nmcli_lib.WIFI_NAME, active=True )
        nmcli.unset_dns(name=nmcli_lib.WIFI_NAME)

        if ( self.flog != None ):
            self.flog.info( FUNCTION_TAG + ": removal of ipv4 DNS address(es) done." )



#######################################################
# read config from db or set ESSID and key from cli   #
#######################################################
class ConfigFromDB():
    
    config_db = sqldb.configDB()
   
    def __init__( self, flog=None ):

        #raise Exception( "TEST of RAISE" )   
    
        self.flog           = flog
        self.essid          = None
        self.encrypted_key  = None
        self.decrypted_key  = None
        self.ip4            = None
        self.ip4gw          = None
        self.ip4dns         = None
    
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if ( self.flog != None ):
            self.flog.debug( FUNCTION_TAG + ": read ESSID and wpa key from the database.")

         # open van config database
        try:    
            self.config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
        except Exception as e:
            msg = FUNCTION_TAG + ": database could not be opened." + const.FILE_DB_CONFIG + " Message:" + str(e.args[0] )
            if ( self.flog != None ):
                self.flog.critical( msg )
                raise Exception( msg) 
        
        if ( self.flog != None ):
            self.flog.debug( FUNCTION_TAG + ": database table " + const.DB_CONFIG_TAB +  " successfully opened." )

        try:

            sqlstr = "select id, parameter from " + const.DB_CONFIG_TAB + " where id =11 or id=12 or id=165 or id=223 or id=224 order by id asc"

            sqlstr = " ".join( sqlstr.split() )
            if ( self.flog != None ):
                self.flog.debug( FUNCTION_TAG + ": sql = " + sqlstr )
        
            wifi_config_recs = self.config_db.select_rec( sqlstr ) 

            #print( wifi_config_recs ) 

            self.essid   	    = str(wifi_config_recs[0][1])
            self.encrypted_key	= str(wifi_config_recs[1][1])
            self.ip4            = str(wifi_config_recs[2][1])
            self.ip4gw          = str(wifi_config_recs[3][1])
            self.ip4dns         = str(wifi_config_recs[4][1])

            #if ( self.flog != None ):
            if ( True ):
                self.flog.debug( FUNCTION_TAG + ": ESSID = " +  str(self.essid)  +"  crypto key = " + self.encrypted_key)
                self.flog.debug( FUNCTION_TAG + ": crypto key = " + str(self.encrypted_key) )
                self.flog.debug( FUNCTION_TAG + ": IP4 address = " + str(self.ip4) )
                self.flog.debug( FUNCTION_TAG + ": IP4 gateway address = " + str(self.ip4gw) )
                self.flog.debug( FUNCTION_TAG + ": IP4 DNS address = " + str(self.ip4dns) )

        except Exception as e:
             msg = FUNCTION_TAG + "fatal sql query error on query " + sqlstr + ". Message:" + str(e.args[0])
             self.flog.critical( msg ) 
             raise Exception( msg)  


    def get_wpa_key(self):
         
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        try:
            cb = crypto_lib.CryptoBase64()
            self.decrypted_key = base64.standard_b64decode(cb.p1Decrypt( cipher_text=self.encrypted_key, seed=CRYPTO_SEED_WIFI )).decode( 'utf-8' )
        
            if ( self.flog != None ):
              
                self.flog.debug(  FUNCTION_TAG + ": decrypted key = " + self.decrypted_key )

        except Exception as e:
             msg = FUNCTION_TAG + " decryption of wpa key failed.  Message:" + str(e.args[0])
             if ( self.flog != None ):
                self.flog.critical( msg )   
                raise Exception( msg) 
             
        return self.decrypted_key

    def get_essid(self):
        return self.essid
    
    def get_ip4(self):
        return self.ip4
    
    def get_ip4gateway(self):
        return self.ip4gw
    
    def get_ip4dns(self):
        return self.ip4dns


#######################################################
# Wifi information functions                          #
#######################################################
class WifiInfo():

    def __init__( self, flog=None ):
        self.flog = flog

    def list_wifi( self ):
        try:
            info = nmcli_lib.Info(flog=self.flog)
            sorted_list = info.wifi_essid()
            return sorted_list 
        except Exception as e:
             raise Exception( str(e) )