import glob
import subprocess
import inspect
import io
import ipaddress
import os
import random
#import string
import socket
#import tempfile
import util 
import urllib
import process_lib
import filesystem_lib
import data_struct_lib

# note the entries won't work with space
# between entries like x = y, x=y is ok.
P1MON_INTERFACE_TXT       = "interface "
P1MON_STATIC_IP_TXT       = "static ip_address="
P1MON_STATIC_ROUTER_TXT   = "static routers="
P1MON_STATIC_DOMAIN_TXT   = "static domain_name_servers="
P1MON_ETH0_TXT            = "eth0"
P1MON_WLAN0_TXT           = "wlan0"

# Warning every tag must by unique!
P1MON_INTERFACE_ETH0_TAG  = "#P1MON_ETH0_INTERFACE"
P1MON_IP_ETH0_TAG         = "#P1MON_ETH0_IP"
P1MON_INTERFACE_WLAN0_TAG = "#P1MON_WLAN0_INTERFACE"
P1MON_IP_WLAN0_TAG        = "#P1MON_WLAN0_IP"
P1MON_ROUTER_TAG          = "#P1MON_ROUTER"
P1MON_DOMAIN_TAG          = "#P1MON_DNS"

#DHCPCONFIG_HEADER_TAG     = "### NIET AANPASSEN P1-MONITOR ###"

DHCPCONFIG                = "/etc/dhcpcd.conf"
RESOLVCONFIG              = "/etc/resolv.conf"
CONFIG_TMP_EXT            = "_config.tmp"
DEFAULT_INET_DNS          = "8.8.8.8" 

FQDN_LIST= [
    "www.google.nl",\
    "www.google.com",\
    "youTube.com",\
    "facebook.com",\
    "wikipedia.org",\
    "amazon.com",\
    "nu.nl",\
    "nos.nl",\
    "ad.nl",\
    "live.com",\
    "bol.com",\
    "netflix.com"\
]


DEFAULT_DHCP_CONFIG_V2 = \
"""

###P1MONHEADERTAG###

# Inform the DHCP server of our hostname for DDNS.
hostname

# Use the hardware address of the interface for the Client ID.
clientid

# Persist interface configuration when dhcpcd exits.
persistent

# Rapid commit support.
# Safe to enable by default because it requires the equivalent option set
# on the server to actually work.
option rapid_commit

# A list of options to request from the DHCP server.
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes

# Respect the network MTU. This is applied to DHCP routes.
option interface_mtu

# A ServerID is required by RFC2131.
require dhcp_server_identifier

# generate Stable Private IPv6 Addresses based from the DUID
slaac private

###MODIFICATIONTIMESTAMP###

###ETH0INTERFACE###
###ETH0STATICIP###
###ETH0STATICROUTER###
###ETH0STATICDNS###

###WLAN0INTERFACE###
###WLAN0STATICIP###
###WLAN0STATICROUTER###
###WLAN0STATICDNS###

"""

class DhcpcdConfig():

    ###########################################
    # init the class                          #
    ###########################################
    def __init__( self, filename=DHCPCONFIG, config_db=None, flog=None):
        self.filename  = filename
        self.flog      = flog
        self.config_db = config_db

    #########################################################################
    # create an dhcpcd.conf file from the data in the config data structure #
    #########################################################################
    def set_config_from_data( self, config=data_struct_lib.dhcpcd_config ) -> bool:
        try:
            buffer = self.__create_config_buffer( config=config )
            if self.__write_buffer_to_file( buffer=buffer ) == False:
                raise Exception( "file " + self.filename + " schrijven mislukt.")
            return True
        except Exception as e:
            self.flog.error( __class__.__name__ + ": fout -> " +  str(e.args) )
            return False

    #########################################################################
    # when using a static IP the DNS must be set because the DHCP request   #
    # will not be made. If the DNS is not set the default DNS server will   #
    # be used                                                               #
    #########################################################################
    def static_config_check( self, config=None ):
        try:
            if len(config['domain_name_servers_ip4']) >0:
                return True #DNS is set so noting to do.

            if len( config['eth0_static_ip4'] ) > 0 and len(config['domain_name_servers_ip4']) == 0 :
                config['domain_name_servers_ip4'] = P1MON_STATIC_DOMAIN_TXT + DEFAULT_INET_DNS
                self.config_db.strset( DEFAULT_INET_DNS ,167, self.flog ) 
                return True # no need to set DNS again because it is shared with eth0 en wlan0

            if len( config['wlan0_static_ip4'] ) > 0 and len(config['domain_name_servers_ip4']) == 0 :
                config['domain_name_servers_ip4'] = P1MON_STATIC_DOMAIN_TXT + DEFAULT_INET_DNS
                self.config_db.strset( DEFAULT_INET_DNS ,167, self.flog ) 
                return True

        except Exception as e:
            self.flog.critical( __class__.__name__ + ": gefaald: " + str(e.args[0]) )
            return False


    #########################################################################
    # create an dhcpcd.conf file from the data in the config database and   #
    # triger the update of the dhcp daemon                                  #
    #########################################################################
    def set_config_from_db( self ):
        try:
            config = self.__get_config_from_db()

            if self.static_config_check( config=config ) == False:
                self.flog.error( __class__.__name__ + ": DNS controle gefaald." )
                return False
            
            buffer = self.__create_config_buffer( config=config )
         
            if self.__write_buffer_to_file( buffer=buffer ) == False:
                 return False

            if reload_dhcp_deamon( flog=self.flog ) == False:
                return False

        except Exception as e:
            return False

        return True

    #########################################################################
    # reading the config data from the database and fill data structure     #
    #########################################################################
    def __get_config_from_db( self ) -> data_struct_lib.dhcpcd_config:

        try:
            config = data_struct_lib.dhcpcd_config

            # read static IP for eth0
            _id, eth0_ip, _label = self.config_db.strget( 164, self.flog )
            if len( eth0_ip ) == 0:
                config['eth0_static_ip4'] = '' 
            else:
                try:
                    is_valid_ip_adres( eth0_ip )
                    config['eth0_static_ip4'] = P1MON_STATIC_IP_TXT + eth0_ip + "/24"
                    self.flog.info( __class__.__name__ + ": IP adres eth0 aangepast naar " + P1MON_STATIC_IP_TXT + eth0_ip + "/24" )
                except Exception as e:
                    self.flog.critical( __class__.__name__ + ": IP adres eth0 fout : " + str(e.args[0]) )
                    raise Exception( "file " + self.filename + " IP adres eth0 fout")

            _id, wlan0_ip, _label = self.config_db.strget( 165, self.flog )
            if len( wlan0_ip ) == 0:
                config['wlan0_static_ip4'] = ''
            else:
                try:
                    is_valid_ip_adres( wlan0_ip )
                    config['wlan0_static_ip4'] = P1MON_STATIC_IP_TXT + wlan0_ip + "/24"
                    self.flog.info( __class__.__name__ + ": IP adres wlan0 aangepast naar " + P1MON_STATIC_IP_TXT + wlan0_ip + "/24" )
                except Exception as e:
                    self.flog.critical( __class__.__name__ + ": IP adres wanl0 fout : " + str(e.args[0]) )
                    raise Exception( "file " + self.filename + " IP adres wanl0 fout")

            _id, router, _label = self.config_db.strget( 166, self.flog )
            if len( router ) == 0:
                config['routers_ip4'] = ''
            else:
                try:
                    is_valid_ip_adres( router )
                    config['routers_ip4'] = P1MON_STATIC_ROUTER_TXT + router
                    self.flog.info( __class__.__name__ + ": IP adres router aangepast naar " + P1MON_STATIC_ROUTER_TXT + router )
                except Exception as e:
                    self.flog.critical( __class__.__name__ + ": IP adres router/gateway fout : " + str(e.args[0]) )
                    raise Exception( "file " + self.filename + " IP adres router/gateway fout")

            _id, dns, _label = self.config_db.strget( 167, self.flog )
            if len( dns ) == 0:
                config['domain_name_servers_ip4'] = ''
            else:
                try:
                    is_valid_ip_adres( dns )
                    config['domain_name_servers_ip4'] = P1MON_STATIC_DOMAIN_TXT + dns
                    self.flog.info( __class__.__name__ + ": IP adres DNS aangepast naar " + P1MON_STATIC_DOMAIN_TXT + dns )
                except Exception as e:
                    self.flog.critical( __class__.__name__ + ": IP adres dns fout : " + str(e.args[0]) )
                    raise Exception( "file " + self.filename + " IP adres dns fout.")

        except Exception as e:
            self.flog.critical( __class__.__name__ + ": gefaald: " + str(e.args[0]) )
            raise Exception(  str(e.args[0]) )

        return config

    ##################################################################
    # write the buffer to the config file                            #
    ##################################################################
    def __write_buffer_to_file( self, buffer=None ):

        try:

            tmp_file = filesystem_lib.generate_temp_filename() + CONFIG_TMP_EXT

            ##################################################################
            # maken temporary file so we can move the file to root ownership #
            ##################################################################
            try:
                fp = open( tmp_file, 'w')
                for line in buffer.splitlines():
                    fp.write( line + "\n" )
                    fp.flush()
                fp.close()

            except Exception as e:
                self.flog.critical( __class__.__name__ + + ": tijdelijk config file schrijf fout, gestopt(" + tmp_file + ") melding:" + str(e.args) )
                return False
            self.flog.debug( __class__.__name__ + ": buffer naar file " + str( buffer) )

            ##################################################################
            # move the file to the correct folder                            #
            ##################################################################
            if filesystem_lib.move_file_for_root_user( source_filepath=tmp_file, destination_filepath=self.filename , permissions='644', copyflag=False, flog=self.flog ):
                return False

        except Exception as e:
            self.flog.critical( __class__.__name__ + ": config file schrijf fout, gestopt(" + self.filename + ") melding:" + str(e.args) )
            filesystem_lib.rm_with_delay( filepath=tmp_file, timeout=5, flog=self.flog )
            return False

        return True


    ########################################################
    # make a string buffer that contains the DHCPCD.conf   #
    # file.                                                #
    ########################################################
    def __create_config_buffer( self, config=None ) -> str:
        try:
            buffer = DEFAULT_DHCP_CONFIG_V2.replace( "###MODIFICATIONTIMESTAMP###", self.__generate_header_string() )
            #buffer = buffer.replace( "###MODIFICATIONTIMESTAMP###", self.__generate_header_string() )

            ##################################################################
            # header flags will be set if any data is set for that interface #
            # false means remove place holder in buffer template             #
            ##################################################################
            write_eth0_interace_header  = False 
            write_wlan0_interace_header = False

            #########################################################################
            # reading the config data from the database en replace the placeholders #
            #########################################################################

            if len( config['eth0_static_ip4'] ) == 0:
                buffer = buffer.replace( "###ETH0STATICIP###\n", '' )
            else:
                buffer = buffer.replace( "###ETH0STATICIP###", config['eth0_static_ip4'] )
                write_eth0_interace_header = True

            if len( config['wlan0_static_ip4'] ) == 0:
                buffer = buffer.replace( "###WLAN0STATICIP###\n", '' )
            else:
                buffer = buffer.replace( "###WLAN0STATICIP###", config['wlan0_static_ip4'] )
                write_wlan0_interace_header = True

            if len( config['routers_ip4'] ) == 0:
                buffer = buffer.replace( "###ETH0STATICROUTER###\n", '' )
                buffer = buffer.replace( "###WLAN0STATICROUTER###\n", '' )
            else:
                buffer = buffer.replace( "###WLAN0STATICROUTER###", config['routers_ip4'] )
                buffer = buffer.replace( "###ETH0STATICROUTER###", config['routers_ip4'] )
                write_wlan0_interace_header = True
                write_eth0_interace_header = True

            if len( config['domain_name_servers_ip4'] ) == 0:
                buffer = buffer.replace( "###ETH0STATICDNS###\n", '' )
                buffer = buffer.replace( "###WLAN0STATICDNS###\n", '' )
            else:
                buffer = buffer.replace( "###WLAN0STATICDNS###", config['domain_name_servers_ip4'] )
                buffer = buffer.replace( "###ETH0STATICDNS###",  config['domain_name_servers_ip4'] )
                write_wlan0_interace_header = True
                write_eth0_interace_header = True

            if ( write_eth0_interace_header ):
                buffer = buffer.replace( "###ETH0INTERFACE###", P1MON_INTERFACE_TXT + P1MON_ETH0_TXT )
            else:
                buffer = buffer.replace( "###ETH0INTERFACE###\n", '' )

            if ( write_wlan0_interace_header ):
                buffer = buffer.replace( "###WLAN0INTERFACE###", P1MON_INTERFACE_TXT + P1MON_WLAN0_TXT )
            else:
                buffer = buffer.replace( "###WLAN0INTERFACE###\n", '' )

        except Exception as e:
            self.flog.error( __class__.__name__ + ": fout -> " +  str(e.args) )
            raise Exception( __class__.__name__ + " fout -> " +  str(e.args) )

        return buffer


    ########################################################
    # header timestamp string                              #
    ########################################################
    def __generate_header_string( self ):
        str = \
    '###############################\n\
# Gegenereerd door P1-monitor.#\n\
# op '+ util.mkLocalTimeString() + '      #\n'+\
    '###############################\n'
        return str

def fqdn_ping( flog=None, info_messages=True ):

    li = FQDN_LIST
    random.shuffle( li )

    for i in range( len(li) ):

        try :

            cmd_str = "/bin/ping -c1 -W1 -4 " + li[i]
            flog.debug ( inspect.stack()[0][3] + ": ping host is " + str( li[i]) )
            p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True )
            _stdout=subprocess.PIPE
            (output, _err) = p.communicate()
            _p_status = p.wait( timeout=5 )
            #print ( output, _err )
            for item in str(output).split("\n"):
                if "0% packet loss" in item:
                    if info_messages == True:
                        flog.info ( inspect.stack()[0][3] + ": ping host " + str( li[i])  + " geeft antwoord." )
                    return True

        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": onverwacht fout =>  " +  str(e.args) )

    flog.warning( inspect.stack()[0][3] + ": Geen van de internet sites geeft antwoord." )
    return False

def reload_dhcp_deamon( flog=None ):
    flog.info( inspect.stack()[0][3] + ": DHCP deamon restart")
    try:
        cmd_str = "sudo systemctl daemon-reload; sleep 1; sudo systemctl restart dhcpcd"
        flog.debug( inspect.stack()[0][3] + ": cmd = " +  cmd_str )
        
        p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout=subprocess.PIPE
        (output, err) = p.communicate()
        p_status = p.wait(timeout=2)
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": reload DHCP deamon fout " +  str(e.args) )
        return False

################################################################
# get the hostname from an IP address                          #
################################################################
def get_host_name_by_ip( ip ): #180ok
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception as _e:
        return "onbekend"

################################################################
# get the public id adres by using an interne service          #
################################################################
def get_public_ip_address():
    try:
        #url = 'https://api.ipify.org/'
        url = 'https://api64.ipify.org/' # changed in version 2.1.0 
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        return str(response.read().decode('utf-8'))

    except Exception:
        return "onbekend"

################################################################
# restarts the device given so the IP changes are made         #
################################################################
def restart_network_device( device=None, flog=None ):
    # sudo ifconfig wlan0 down && sleep 5 && sudo ifconfig wlan0 up

    try:
        flog.info( inspect.stack()[0][3] + ": netwerk device " + str(device) + " herstart. Dit duurt even geduld!")
        cmd_str = "sudo ifconfig " + str(device) + " down && sleep 5 && sudo ifconfig " + str(device) + " up &"
        flog.debug( inspect.stack()[0][3] + ": cmd = " +  cmd_str )
        p = subprocess.Popen( cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ) 
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": device " + str(device) + "restart fout " +  str(e.args) )
        return False
    return True

##########################################
# check the syntax of IP address         #
##########################################
def is_valid_ip_adres( ip_adress=None ):
    if len( ip_adress.strip() ) == 0:
        raise Exception( "IP adres niet gezet!")
    try:
        ipaddress.ip_address( ip_adress )
    except Exception:
        raise Exception("IP adres: " + str( ip_adress ))

##########################################
# read the default gateway and return a  #
# list with named attributes             #
##########################################
def get_default_gateway():

    result_list = []

    result = {
    "ip4":None, 
    "device":None,
    }
    try :
        p = subprocess.Popen([ 'ip route show' ],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 

        buf = p.stdout.readlines()
        for item in buf: 
            value = item.decode('utf-8')
            if value.find('default') == 0:
                rec = result.copy()
                rec["ip4"]    = item.split()[2].decode('utf-8')
                rec["device"] = item.split()[4].decode('utf-8')
                result_list.append( rec )
    except Exception:
        pass

    return result_list
    # how to use ################
    # for rec in result_list:
    #    print( rec['ip4'] )
    #############################

#def getNicInfo(nic="eth0"):
def get_nic_info(nic="eth0"):
    result = {
    "ip4":None, 
    "ip6":None,
    "mac":None,
    "result_ok":True
    }
    cmd_str = "/sbin/ifconfig -a "+nic
    try:
        p = subprocess.Popen(cmd_str,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        buf = p.stdout.readlines()
        for item in buf: 
            #print ( item )
            value = item.decode('utf-8')
            if value.find('inet ') != -1: # trailing space is important for difference with ip4/ip6
                result['ip4'] = value.split()[1].upper()
            if value.find('inet6') != -1:
                result['ip6'] = item.split()[1].upper().decode('utf-8')
            if value.find('ether') != -1:
                result['mac'] = item.split()[1].upper().decode('utf-8')
    except Exception as _e:
        print ( _e )
        result['result_ok'] = False
    return result


""" wordt niet meer gebruikt ter referentie
def regenerate_resolv_config( flog=None ):

    flog.info( inspect.stack()[0][3] + ": resolv.conf regeneren. ")

    # move to backup
    FILE_BACKUP_EXT = ".p1mon.bak"
    #if move_file_for_root_user( source=RESOLVCONFIG, destination=RESOLVCONFIG + FILE_BACKUP_EXT , flog=flog ) == False:
    #    flog.warning( inspect.stack()[0][3] + ": backup bestand " + RESOLVCONFIG + FILE_BACKUP_EXT + " is niet te maken.")

    if filesystem_lib.move_file_for_root_user( source_filepath=RESOLVCONFIG, destination_filepath=RESOLVCONFIG + FILE_BACKUP_EXT, flog=flog ):
        flog.warning( inspect.stack()[0][3] + ": backup bestand " + RESOLVCONFIG + FILE_BACKUP_EXT + " is niet te maken.")

    try:
        cmd_str = "sudo resolvconf -u"
        flog.debug( inspect.stack()[0][3] + ": cmd = " +  cmd_str )
        #p = subprocess.Popen( cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout=subprocess.PIPE
        (output, err) = p.communicate()
        p_status = p.wait(timeout=10)
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": resolv.conf regeneren fout " +  str(e.args) )
        return False
    
    # if resolv.conf does not exist recover from backup 
    if not os.path.isfile( RESOLVCONFIG ):
        flog.warning( inspect.stack()[0][3] + ": resolv.conf is niet aangemaakt, recovery met vorige bestand." )
        #move_file_for_root_user( source=RESOLVCONFIG + FILE_BACKUP_EXT, destination=RESOLVCONFIG, flog=flog )
        filesystem_lib.move_file_for_root_user( source_filepath=RESOLVCONFIG + FILE_BACKUP_EXT, destination_filepath=RESOLVCONFIG, copyflag=True, flog=flog )
        return False
    # we leave the backup file as debug data and manual recovery.

    return True
"""