import glob
import subprocess
import inspect
import io
import ipaddress
import os
import random
import string
import tempfile
import util 

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

DHCPCONFIG_HEADER_TAG     = "### NIET AANPASSEN P1-MONITOR ###"

DHCPCONFIG                = "/etc/dhcpcd.conf"
RESOLVCONFIG              = "/etc/resolv.conf"
CONFIG_TMP_EXT            = "_config.tmp"
DEFAULT_INET_DNS          = "1.1.1.1 8.8.8.8 9.9.9.9"

######################################
# well known DNS servers             #
#
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
    "www.schiphol.nl"\
]

DEFAULT_DHCP_CONFIG = \
"""
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

"""


#############################################
# p1 status record, used for proces status  #
# and such. keeps status                    #
#############################################
ip_config_record = {
    'interface' : P1MON_INTERFACE_TXT,      # device name
    'ip'        : P1MON_STATIC_IP_TXT      # ip4 address
}

class ConfigFile():
       
    ###########################################
    # init the class                          #
    ###########################################
    def init( self, filename, flog, device ):
        self.line_buffer = []
        self.filename = filename
        self.flog     = flog
        self.device   = device
        # read buffer
        self.read_file_into_buffer()

    ##########################################
    # read the file from disk into the temp  #
    # buffer.                                #
    ##########################################
    def read_file_into_buffer( self ):
        self.line_buffer = [] # empty the buffer
        try:
            with io.open( self.filename, "r", newline=None) as fd:
                for line in fd:
                    self.line_buffer.append( line.replace( '\n', '') )
        except Exception:
            self.flog.warning( inspect.stack()[0][3] + ": config file leesfout of bestaat niet." ) 
            self.line_buffer = []

        self.flog.debug( inspect.stack()[0][3] + ": buffer van configfiles " + str(self.line_buffer) )

    def remove_line_by_tag( self, tag=None ):
        tmp_list = []
        for i in self.line_buffer:
            if i.find( tag )!=-1:
                continue
            tmp_list.append( i )

        self.line_buffer = tmp_list.copy()

    ##########################################
    # remove the entries from the buffer     #
    ##########################################
    def remove_entries_by_device( self ):

        if self.device == 'wlan0':
            self.remove_line_by_tag( tag=P1MON_INTERFACE_WLAN0_TAG )
            self.remove_line_by_tag( tag=P1MON_IP_WLAN0_TAG )
        else:
            self.remove_line_by_tag( tag=P1MON_INTERFACE_ETH0_TAG  )
            self.remove_line_by_tag( tag=P1MON_IP_ETH0_TAG )

    ##################################################################
    # write the buffer to the config file                            #
    ##################################################################
    def write_buffer_to_file( self ):

        try:

            tmp_file = generate_temp_filename() + CONFIG_TMP_EXT

            ##################################################################
            # maken temporary file so we can move the file to root ownership #
            ##################################################################
            try:
                fp = open( tmp_file, 'w')
                for line in self.line_buffer:
                    fp.write( line + "\n" )
                    fp.flush()
                fp.close()

            except Exception as e:
                self.flog.critical( inspect.stack()[0][3] + ": tijdelijk config file schrijf fout, gestopt(" + tmp_file + ") melding:" + str(e.args) )
                return False
            self.flog.debug( inspect.stack()[0][3] + ": buffer naar file " + str(self.line_buffer) )

            ##################################################################
            # move the file to the correct folder                            #
            ##################################################################
            if move_file_for_root_user( source=tmp_file, destination=self.filename ,flog=self.flog ) == False:
                return False

        except Exception as e:
            self.flog.critical( inspect.stack()[0][3] + ": config file schrijf fout, gestopt(" + self.filename + ") melding:" + str(e.args) )
            clean_tmp_files( tmp_file, flog=self.flog ) 
            return False

        return True

    ##################################################################
    # add the date IP record to the line buffer                      #
    ##################################################################
    def add_record_to_buffer( self, record=None ):
        timestamp = util.mkLocalTimeString()
        self.line_buffer.append( record['interface']  + " " + timestamp )
        self.line_buffer.append( record['ip']         + " " + timestamp )

    def add_single_line_to_buffer(self, line=None , timestamp=True ):
        if timestamp == True:
            self.line_buffer.append( line + " " + util.mkLocalTimeString() )
        else:
            self.line_buffer.append( line )


    def empty_buffer(self):
         self.line_buffer = [] # empty the buffer

    #####################################################
    # write dhcpcd config file if it not exists of when #
    # the file does not have en P1-monitor header tag   #
    # forced will always overwrite the config file      #
    # the file does not have any settings. Only default #
    # DNS enteries.                                     #
    #####################################################
    def write_default_dhcp_config_file( self , forced=False , flog=None ):
 
        # check the current file when not forced
        if ( forced == False ):
            for i in self.line_buffer:
                if i.find( DHCPCONFIG_HEADER_TAG ) == 0: # P1-monitor TAG present
                    self.flog.info( inspect.stack()[0][3] + ": huidige bestand " + DHCPCONFIG + " is al door P1-monitor gemaakt. niets aangepast.")
                    return True

        self.empty_buffer()

        self.add_single_line_to_buffer( DHCPCONFIG_HEADER_TAG, timestamp=False )

        for line in DEFAULT_DHCP_CONFIG.splitlines( keepends=False ):
             self.line_buffer.append( line )

        line = P1MON_STATIC_DOMAIN_TXT + DEFAULT_INET_DNS + " " + P1MON_DOMAIN_TAG
        self.add_single_line_to_buffer( line )

        return self.write_buffer_to_file()
        

def fqdn_ping( flog=None ): 

    li = FQDN_LIST
    random.shuffle( li )

    for i in range(len(li)):

        try :

            cmd_str = "/bin/ping -c1 -W1 " + li[i]
            flog.debug ( inspect.stack()[0][3] + ": ping host is " + str( li[i]) )
            p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True )
            _stdout=subprocess.PIPE
            (output, _err) = p.communicate()
            _p_status = p.wait( timeout=5 )
            #print ( output, _err )
            for item in str(output).split("\n"):
                if "0% packet loss" in item:
                    flog.info ( inspect.stack()[0][3] + ": ping host " + str( li[i])  + " geeft antwoord." )
                    return True

        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": onverwacht fout =>  " +  str(e.args) )

    flog.error( inspect.stack()[0][3] + ": Geen van de internet sites geeft antwoord." )
    return False

def reload_dhcp_deamon(flog=None ):
    flog.info( inspect.stack()[0][3] + ":  DHCP deamon restart")
    try:
        cmd_str = "sudo systemctl daemon-reload; sleep 1; sudo systemctl restart dhcpcd"
        flog.debug( inspect.stack()[0][3] + ": cmd = " +  cmd_str )
        
        p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout=subprocess.PIPE
        (output, err) = p.communicate()
        p_status = p.wait(timeout=2)                   # wait max2 secs until the config file exist or quit after max 10 sec.
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": reload DHCP deamon fout " +  str(e.args) )
        return False


def regenerate_resolv_config( flog=None ):

    flog.info( inspect.stack()[0][3] + ":  resolv.conf regeneren. ")

    # move to backup
    FILE_BACKUP_EXT = ".p1mon.bak"
    if move_file_for_root_user( source=RESOLVCONFIG, destination=RESOLVCONFIG + FILE_BACKUP_EXT , flog=flog ) == False:
        flog.warning( inspect.stack()[0][3] + ": backup bestand " + RESOLVCONFIG + FILE_BACKUP_EXT + " is niet te maken.")

    try:
        cmd_str = "sudo resolvconf -u"
        flog.debug( inspect.stack()[0][3] + ": cmd = " +  cmd_str )
        #p = subprocess.Popen( cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout=subprocess.PIPE
        (output, err) = p.communicate()
        p_status = p.wait(timeout=10)                   # wait max 10 secs until the config file exist or quit after max 10 sec.
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": resolv.conf regeneren fout " +  str(e.args) )
        return False
    
    reload_dhcp_deamon( flog=flog )

    # if resolv.cong does not exist recover from backup 
    if not os.path.isfile( RESOLVCONFIG ):
        flog.warning( inspect.stack()[0][3] + ": resolv.conf is niet aangemaakt, recovery met vorige bestand." )
        move_file_for_root_user( source=RESOLVCONFIG + FILE_BACKUP_EXT, destination=RESOLVCONFIG, flog=flog )
        return False

    # we leave the backuo file as debug data and manual recovery.

    return True


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

################################################################
# move a file to the destination and set the rights to 644 and #
# ownership to root:root                                       #
# true is ok, false is fatal error                             #
################################################################
def move_file_for_root_user( source=None, destination=None , flog=None) -> bool:

    if not os.path.isfile( source ):
        flog.warning( inspect.stack()[0][3] + ": bestand " + source  + " niet gevonden.")
        return True

    cmd = '/usr/bin/sudo mv -f ' + source + ' ' + destination
    #print ( cmd )
    if os.system( cmd ) > 0:
        flog.critical( inspect.stack()[0][3] + ": verplaatsen van file error " + source  )
        return False

    cmd = '/usr/bin/sudo chmod 644 ' + destination
    #print( cmd )
    if os.system( cmd ) > 0:
        flog.warning( inspect.stack()[0][3] + ": file eigenaarschap fout. " + destination  )

    cmd = '/usr/bin/sudo chown root:root ' + destination
    #print( cmd )
    if os.system( cmd ) > 0:
        flog.warning( inspect.stack()[0][3] + ": file rechten fout. " + destination  )

    return True

####################################################
# remove one or more temporary files               #
####################################################
def clean_tmp_files( filename ,flog=None):
    files = glob.glob( filename.gettempdir() + '/*' + CONFIG_TMP_EXT )
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": tijdelijk bestand " + f + " kan niet worden gewist: " + str(e.args) )

##########################################################
# generate a tempory file name in the default tmp folder #
##########################################################
def generate_temp_filename() -> str:
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return os.path.join( tempfile.gettempdir(), random_string)

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
