####################################################################
# shared lib for NetworkManager CLU tool nmcli                     #
####################################################################

import inspect
import subprocess
#from operator import itemgetter, attrgetter

WIFI_IFNAME             = 'wlan0 '
WIFI_NAME               = 'p1monWifi'
ETH_IFNAME              = 'eth0'
ETH_NAME                = 'p1monEthernet'
WIFI_DEFAULT_KEY_TYPE   = 'wpa-psk'
SUDO_CMD                = '/usr/bin/sudo'

#############################################################
# information functions                                     #
#############################################################
class Info():

    def __init__( self, flog=None ): 
        self.flog = flog

    def wifi_essid( self ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name
        sorted_list = []

        try:

            if self.flog != None:
                 self.flog.debug( FUNCTION_TAG + ": creating file with ESSID info.")

            cmd = SUDO_CMD + ' nmcli -t dev wifi list'
            output, err, status = run_os_process( cmd=cmd, flog=self.flog, hide_stdout=True, hide_stderr=True  )

            if self.flog != None:
                self.flog.debug( FUNCTION_TAG + ": essid data recieved ok from nmcli.")

        except Exception as e:
            msg = FUNCTION_TAG + ": cmd " + str( cmd ) + " failed " + str(e)
            raise Exception( msg ) 

        essid_list = set() # set because the items are unique.

        try:
            for line in output.splitlines():
                buffer = line.split(":")
                essid = buffer[7].strip()
                if len(essid) > 0: #skip essid that are not shown
                    essid_list.add( essid )
        except Exception as e:
            msg = FUNCTION_TAG + ": no ESSID data found" + str(e)
            raise Exception( msg ) 
         
        sorted_list = sorted( essid_list )

        return sorted_list

       
############################################################
# device manipulation functions                            #
############################################################
class Device():

    def __init__( self, flog=None ):   
        self.flog = flog

    #########################################################################
    # read connection UUID by device, connection name is tricky because of  #
    # the possibility of spaces in the name                                 #
    #########################################################################
    def get_connection_UUID_by_device( self, device=ETH_IFNAME ):

        FUNCTION_TAG =  __name__ + "."+ inspect.currentframe().f_code.co_name
        # sudo nmcli -t connection show
        # output NAME, UUID, TYPE, DEVICE  (name = connection name, device= eth0, wlan0, etc.)

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": device " + str(device) )

        cmd = SUDO_CMD + ' nmcli -t  connection show'

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": cmd " + str(cmd) )

        try:
            output, err, status = run_os_process( cmd=cmd, flog=self.flog ,hide_stderr=True, hide_stdout=True )

            list_of_lines = output.splitlines()    

            for line in list_of_lines:
                #print ( line )     
                buffer = line.split(":")
                if buffer[3] == device:
                    return buffer[1] #name of the connection
                
        except Exception as e:
            msg = FUNCTION_TAG + " : failed. Command " + str(cmd) + " message: " + str(e)
            if self.flog != None:
                 self.flog.error( msg)
            raise Exception( msg )

    #########################################################################
    # read settings by connection name, returns a list                      #
    #########################################################################
    def read_setting( self, name=None, setting=None ):

        FUNCTION_TAG =  __name__ + "."+ inspect.currentframe().f_code.co_name
         # nmcli -f ip4.address connection show p1monWifi

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": name "     + str(name) )
            self.flog.debug( FUNCTION_TAG + ": setting "  + str(setting) )

        cmd = SUDO_CMD + ' nmcli -t -f ' + str(setting) + ' connection show "' + str(name) + '"'

        #cmd = SUDO_CMD  + ' nmcli -t -f ipv4.dns,ipv4.addresses,ipv4.gateway con show p1monWifi'
        #cmd = SUDO_CMD  + ' nmcli -t -f ipv4.gateway con show p1monWifi'

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": cmd " + str(cmd) )

        list_output = []
        try:
            output, err, status = run_os_process( cmd=cmd, flog=self.flog ,hide_stderr=True, hide_stdout=True )
            #print( "#", output
            for line in output.splitlines():
                buffer = line.split(":")
                #print (buffer)
                item = buffer[1].strip()
                if len(item) > 0:
                    list_output.append( item )

                return list_output
        except Exception as e:
            msg = FUNCTION_TAG + " : failed. Command " + str(cmd) + " message: " + str(e)
            if self.flog != None:
                 self.flog.error( msg)
            raise Exception( msg )

    #########################################################################
    # change settings by connection name property must be a list            #
    #########################################################################
    def change_setting( self, name=None, setting=None, property=None ):

        FUNCTION_TAG =  __name__ + "."+ inspect.currentframe().f_code.co_name

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": name "     + str(name) )
            self.flog.debug( FUNCTION_TAG + ": setting "  + str(setting) )
            self.flog.debug( FUNCTION_TAG + ": property " + str(property ) )

        property = property or []
        if len(property) == 0:
            msg = "property is not a list or not set?"
            if self.flog != None:
                self.flog.debug( FUNCTION_TAG + ": cmd " + str(cmd) )
            raise Exception( msg )   

        concated_property = " ".join( property )
        cmd = SUDO_CMD + ' nmcli con modify id "' + str(name) + '" ' + str(setting) + ' "' + str(concated_property) + '"'

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": cmd " + str(cmd) )

        try:
            output, err, status = run_os_process( cmd=cmd, flog=self.flog )
        except Exception as e:
            msg = FUNCTION_TAG + " : failed. Command " + str(cmd) + " message: " + str(e)
            if self.flog != None:
                 self.flog.error( msg)
            raise Exception( msg )

    #########################################################################
    # set the connection down (status=false) or up (status=true)            #
    #########################################################################
    def connection_mode( self, name=None, active=True ):

        FUNCTION_TAG =  __name__ + "."+ inspect.currentframe().f_code.co_name

        if active == False: 
            mode = "down"
        else: 
            mode = "up"

        if self.flog != None:
             self.flog.info( FUNCTION_TAG + ": connection " + str(name) + " will be set to " + str(mode) )

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": name " + str(name) )
            self.flog.debug( FUNCTION_TAG + ": active " + str(active) )
            self.flog.debug( FUNCTION_TAG + ": mode" + str(mode) )
        
        cmd = SUDO_CMD + ' nmcli con ' + str(mode) + ' "' + str(name) + '"'
        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": cmd " + str(cmd) )
        try:
            output, err, status = run_os_process( cmd=cmd, flog=self.flog )
            if self.flog != None:
                self.flog.info( FUNCTION_TAG + ": connection " + str(name) + " is set to " + str(mode) )
        except Exception as e:
            msg = FUNCTION_TAG + " : failed. Command " + str(cmd) + " message: " + str(e)
            if self.flog != None:
                 self.flog.error( msg)
            raise Exception( msg )

    #########################################################################
    # check if the connection is active/present                             #
    # returns true on active/present connection                             #
    #########################################################################
    def is_active_connection( self, name=None ):

        FUNCTION_TAG =  __name__ + "."+ inspect.currentframe().f_code.co_name

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": check if connection " + str(name) + " exist.")

        cmd = SUDO_CMD + " nmcli -t connection show"
        try:
            output, err, status = run_os_process( cmd=cmd, flog=self.flog, hide_stdout=True, hide_stderr=True  )
            #print ( output )
            for line in output.splitlines():

                buffer = line.split(":")
                #print( buffer[0] )

                if buffer[0] == name:
                    if self.flog != None:
                        self.flog.debug( FUNCTION_TAG + ": connection " + str(name) + " exist.")
                    return True

            if self.flog != None:
                self.flog.debug( FUNCTION_TAG + ": connection " + str(name) + " does not exist.")
            return False
        
        except Exception as e:
            msg = FUNCTION_TAG + " : failed. Command " + str(cmd) + " message: " + str(e)
            if self.flog != None:
                self.flog.error( msg)
            raise Exception( msg )
        
    #########################################################################
    # remove the connection by name                                         #
    #########################################################################
    def remove_connection( self, name=None, uuid=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        identifier = None

        if name != None: 
            identifier = name
        elif uuid != None:
            identifier = uuid
        else:
            msg = FUNCTION_TAG + ": connection name or UUID is not set."
            if self.flog != None:
                self.flog.critical( msg )
            raise Exception( msg ) 

        if self.flog != None:
            self.flog.info( FUNCTION_TAG + ": removing connection " + str(identifier) )

        cmd = SUDO_CMD + ' nmcli connection delete ' + str(identifier)

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": cmd = " + str(cmd) )

        #self.run_os_process( cmd )
        run_os_process( cmd=cmd, flog=self.flog )

        if self.flog != None:
            self.flog.info( FUNCTION_TAG + ": connection with identifier " + str(identifier) + " successfully removed.")

    ######################################################################### 
    # setup the wifi connection, note if an connection all ready is setup   #
    # the profile will be added. Remove the profile before adding the       #
    # profile                                                               #
    # note DNS is a list of DNS servers                                     #
    #########################################################################
    def set_wifi( self, name=WIFI_NAME, wifi_essid=None, wifi_key=None, ifname=WIFI_IFNAME, key_type=WIFI_DEFAULT_KEY_TYPE, ip4gateway=None, ip4=None, ip4dns=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if wifi_essid == None or len(wifi_essid)==0:
            msg = FUNCTION_TAG + ": ESSID is not set!"
            if self.flog != None:
                self.flog.critical( msg )
            raise Exception( msg ) 

        if wifi_key == None or len(wifi_key) == 0:
            msg = FUNCTION_TAG + ": key is not set!"
            if self.flog != None:
                self.flog.critical( msg )
            raise Exception( msg ) 

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": essid = " + str(wifi_essid))
            self.flog.debug( FUNCTION_TAG + ": key = " + str(wifi_key))
            self.flog.debug( FUNCTION_TAG + ": ifname = " + str(ifname))
            self.flog.debug( FUNCTION_TAG + ": wifi_name = " + str(name))
            self.flog.debug( FUNCTION_TAG + ": key_type = " + str(key_type))
            if ip4gateway != None:
                self.flog.debug( FUNCTION_TAG + ": ip4 gateway = " + str(ip4gateway))
            else:
                self.flog.debug( FUNCTION_TAG + ": ip4 gateway not set")
            if ip4 != None:
                self.flog.debug( FUNCTION_TAG + ": ip4 address = " + str(ip4))
            else:
                self.flog.debug( FUNCTION_TAG + ": ip4 address is not set")

            ip4dns = ip4dns or []
            #print("#",len(ip4dns))

            if len(ip4dns) > 0:
                if  len(ip4dns[0]) > 0:
                    self.flog.debug( FUNCTION_TAG + ": ip4 DNS address(es) = " + str(ip4dns))
                else:
                    self.flog.debug( FUNCTION_TAG + ": ip4 DNS address(es) is not set")
                    #self.unset_dns( name=name )

            #command creation 
            cmd = SUDO_CMD + ' nmcli con add type wifi con-name ' + str(name) + ' ifname ' + str(ifname) + 'ssid "' + str(wifi_essid) + '" wifi-sec.psk "' + str(wifi_key) + '"' + ' wifi-sec.key-mgmt ' + str(WIFI_DEFAULT_KEY_TYPE) + ' ipv6.method "disabled"'

            # only add options when set.
            if ip4gateway != None :
                  if len(ip4gateway) > 0:
                    cmd = cmd + ' gw4 ' + str(ip4gateway)
            
            if ip4 != None:
                if len(ip4) > 0:
                    cmd = cmd + ' ip4 ' + str(ip4) + ' ipv4.method manual '
                else:
                    cmd = cmd + ' ipv4.method auto '

            if ip4dns != None:
                #print("#",len(ip4dns) ) 
                if len(ip4dns) > 0 :
                    if len(ip4dns[0]) > 0:
                        dns_servers = " ".join( ip4dns )
                        cmd = cmd + ' ipv4.dns "' + dns_servers + '" ipv4.ignore-auto-dns yes'

            if self.flog != None:
                self.flog.debug( FUNCTION_TAG + ": cmd = " + str(cmd) )

            if self.flog != None:
                self.flog.info( FUNCTION_TAG + ": adding connection " + str(name) + ".")

            run_os_process( cmd=cmd, flog=self.flog )

            #self.connection_mode( name=name, active=False )
            #self.connection_mode( name=name, active=True )

            if self.flog != None:
                self.flog.info( FUNCTION_TAG + ": connection " + str(name) + " successfully added.")


    ######################################################################### 
    # setup the ethernet connection, note if an connection all ready is     #
    # the profile will be added. Remove the profile before adding the       #
    # profile                                                               #
    # note DNS is a list of DNS servers                                     #
    #########################################################################
    def set_ethernet( self, name=ETH_NAME, ifname=ETH_IFNAME, ip4gateway=None, ip4=None, ip4dns=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if self.flog != None:
            self.flog.debug( FUNCTION_TAG + ": ifname = " + str(ifname))
            self.flog.debug( FUNCTION_TAG + ": ethernet_name = " + str(name))
            if ip4gateway !=None:  
                self.flog.debug( FUNCTION_TAG + ": ip4 gateway = " + str(ip4gateway))
            else:
                self.flog.debug( FUNCTION_TAG + ": ip4 gateway not set")
            if ip4 !=None:  
                self.flog.debug( FUNCTION_TAG + ": ip4 address = " + str(ip4))
            else:
                self.flog.debug( FUNCTION_TAG + ": ip4 address is not set")

            if len(ip4dns) > 0:
                if  len(ip4dns[0]) > 0:
                    self.flog.debug( FUNCTION_TAG + ": ip4 DNS address(es) = " + str(ip4dns))
                else:
                    self.flog.debug( FUNCTION_TAG + ": ip4 DNS address(es) is not set")
                    #self.unset_dns( name=name )

            #command creation 
            cmd = SUDO_CMD + ' nmcli con add type ethernet con-name ' + str(name) + ' ifname ' + str(ifname)  + ' ipv6.method "disabled"'

            # only add options when set.
            if ip4gateway != None :
                  if len(ip4gateway) > 0:
                    cmd = cmd + ' gw4 ' + str(ip4gateway)
            #if ip4 != None :
            #    if len(ip4) > 0:
            #        cmd = cmd + ' ip4 ' + str(ip4)

            if ip4 != None:
                if len(ip4) > 0:
                    cmd = cmd + ' ip4 ' + str(ip4) + ' ipv4.method manual '
                else:
                    cmd = cmd + ' ipv4.method auto '

            if ip4dns != None:    
                if len(ip4dns) > 0 :
                    if len(ip4dns[0]) > 0:
                        dns_servers = " ".join( ip4dns )
                        cmd = cmd + ' ipv4.dns "' + dns_servers + '" ipv4.ignore-auto-dns yes'

            if self.flog != None:
                self.flog.debug( FUNCTION_TAG + ": cmd = " + str(cmd) )

            if self.flog != None:
                self.flog.info( FUNCTION_TAG + ": adding connection " + str(name) + ".")
                

            run_os_process( cmd=cmd, flog=self.flog )

            if self.flog != None:
                self.flog.info( FUNCTION_TAG + ": connection " + str(name) + " successfully added.")

    ######################################################################### 
    # The reset will use                                                    #
    # the DHCP IPV4 dns supplied DNS server(s)                              #
    #########################################################################
    def unset_dns( self, name=None ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        #if self.flog != None:
        #    self.flog.info( FUNCTION_TAG + ": DNS is being reset for ", name )

        if self.is_active_connection( name=name ) == False:
            if self.flog != None:
                self.flog.info( FUNCTION_TAG + ": DNS for " + name + " is not reset, connection not active")
            return 

        if self.flog != None:
            self.flog.info( FUNCTION_TAG + ": DNS is reset to DHCP use.")

        self.change_setting( name=name, setting="ipv4.ignore-auto-dns", property=["no"] )
        self.change_setting( name=name, setting="ipv4.dns", property=[""] )

        self.connection_mode( name=name, active=False )
        self.connection_mode( name=name, active=True )


################################################
# util function for running OS processes       #
################################################
def run_os_process( cmd=None, flog=None, hide_stdout=False, hide_stderr=False ):

    FUNCTION_TAG =  __name__ + "."+ inspect.currentframe().f_code.co_name

    # run the OS command.
    # note it can take some seconds before the wifi is active 
    try:
        process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate( timeout=30 )

        if flog != None:
            if len(stdout)>0 and hide_stdout == False:
                flog.info( FUNCTION_TAG + ": nmcli respons = " + str(stdout).rstrip('\n') )
            if len(stderr)>0 and hide_stderr == False:
                flog.warning( FUNCTION_TAG + ": nmcli respons = " + str(stderr).rstrip('\n') )    
        
        if  process.returncode != 0:
            msg = "cmd failed on command "+ str(cmd)
            raise Exception( msg ) 
        
        return stdout, stderr, process.returncode 
        
    except Exception as e:
        msg = FUNCTION_TAG + " : process failed unexpected. Command " + str(cmd) + " message: " + str(e)
        if  flog != None:
            flog.error( msg )
            raise Exception( msg )
