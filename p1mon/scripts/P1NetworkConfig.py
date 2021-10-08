#!/usr/bin/python3
import argparse
import const
import inspect
import listOfPidByName
import logger
import os
import pwd
import sqldb
import signal
#import subprocess
import sys
import network_lib
#import makeLocalTimeString

# programme name.
prgname = 'P1NetworkConfig'

config_db    = sqldb.configDB()
rt_status_db = sqldb.rtStatusDb() #TODO check of nog nodig
space_adjust = 43

def Main( argv ):

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument( '-h', '--help',
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument( '-dev', '--devicereload',
        required=False,
        choices=['eth0', 'wlan0' ],
        help="Maak de netwerk instellingen actief. Deze actie verbreekt de verbinding voor een paar seconden." )

    parser.add_argument( '-dgw', '--defaultgateway',
        required=False,
        action="store_true",
        help="stel de default gateways in, dit is meestal het adres van je router." )

    parser.add_argument( '-dns', '--dnsserver',
        required=False,
        action="store_true",
        help="stel het ip adres in van de dnsserver, dit is meestal het adres van je router." )

    parser.add_argument( '-f', '--forced',
        required=False,
        action="store_true",
        help="De optie wordt altijd uitgevoerd, bijvoorbeeld het aanmaken van een een configuratie bestand dat al bestaat." )

    parser.add_argument( '-rdgw', '--removedefaultgateway',
        required=False,
        action="store_true",
        help="verwijder default gateway." )

    parser.add_argument( '-rdns', '--removednsserver',
        required=False,
        action="store_true",
        help="verwijder het ip adres in van de dnsserver, dit is meestal het adres van je router." )

    parser.add_argument( '-ldhcp', '--reloaddhcp',
        required=False,
        action="store_true",
        help="Reload de DHCP deamon" )

    parser.add_argument( '-cdhcp', '--defaultdhcpconfig',
        required=False,
        action="store_true",
        help="Maak een dhcp deamon config file aan." )

    parser.add_argument( '-rsip', '--removestaticip',
        required=False,
        choices=['eth0', 'wlan0' ],
        help="verwijder het vaste IP adres voor het opgegeven device. Als DHCP actief is dan wordt er een DHCP adres toegewezen." )

    parser.add_argument( '-cdns', '--checkandrecoverdns',
        required=False,
        action="store_true",
        help="Controleerd of internet sites te bereiken zijn via een FQDN zo niet maakt een standaard DNS resolv configuratie aan" )

    parser.add_argument( '-sip', '--staticip',
        required=False,
        choices=['eth0', 'wlan0' ],
        help="stel een vast IP adress in voor het opgegeven device." )

    args = parser.parse_args()
    #print (args)

    ###################################
    # init stuff                      #
    ###################################


    #########################################################
    # all processes need to try to restore from disk to ram #
    #########################################################
    disk_to_ram_restore()

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init( const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(2)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    if args.defaultdhcpconfig == True:
        flog.info( inspect.stack()[0][3] + ": DHCP config file wordt aangemaakt.")
        cf = network_lib.ConfigFile()
        cf.init( filename=network_lib.DHCPCONFIG, flog=flog, device=None )
        if cf.write_default_dhcp_config_file( forced=args.forced, flog=flog) == False:
            flog.error( inspect.stack()[0][3] + ": DHCP config file kon niet worden gemaakt.")
            sys.exit( 1 )
        # make sure the resolv.config is generated.
        network_lib.regenerate_resolv_config( flog=flog ) 
        flog.info( inspect.stack()[0][3] + ": DHCP config file gereed.")
        sys.exit( 0 )

    if args.reloaddhcp == True:
        flog.info( inspect.stack()[0][3] + ": DHCP deamon herstart.")
        if network_lib.reload_dhcp_deamon == False:
             flog.error( inspect.stack()[0][3] + ": DHCP deamon herstart fout.")
             sys.exit( 1 )
        flog.info( inspect.stack()[0][3] + ": DHCP deamon herstart gereed.")
        sys.exit( 0 )

    if args.checkandrecoverdns == True:
        flog.info( inspect.stack()[0][3] + ": DNS check and recovery gestart.")
        if network_lib.fqdn_ping( flog=flog ) == True:
            flog.info( inspect.stack()[0][3] + ": DNS naar het internet werkt correct.")
        else:
            flog.info( inspect.stack()[0][3] + ": DNS was niet te bereiken, internet DNS configuratie wordt aangemaakt.")
            remove_dns()
            set_dns()
            network_lib.regenerate_resolv_config( flog=flog )
            flog.info( inspect.stack()[0][3] + ": internet DNS configuratie is aangemaakt.")

        if network_lib.fqdn_ping( flog=flog ) == True:
            flog.info( inspect.stack()[0][3] + ": internet DNS werkt correct.")
        else:
            flog.error( inspect.stack()[0][3] + ": internet was niet ter herstellen.")

        flog.info( inspect.stack()[0][3] + ": DNS check and recovery gereed.")
        sys.exit( 0 )

    if args.devicereload != None:
        flog.info( inspect.stack()[0][3] + ": Herstart/load van netwerk voor device " + str(args.devicereload) + " gestart.")
        if args.devicereload== 'wlan0':
            network_lib.restart_network_device( device='wlan0', flog=flog )
        else: 
            network_lib.restart_network_device( device='eth0', flog=flog )
        flog.info( inspect.stack()[0][3] + ": Herstart/load van netwerk voor device " + str(args.devicereload) + " gereed.")
        sys.exit( 0 )

    if args.removednsserver == True:
        remove_dns()
        network_lib.regenerate_resolv_config( flog=flog )
        sys.exit(0)

    if args.dnsserver == True:
        set_dns()
        network_lib.regenerate_resolv_config( flog=flog )
        sys.exit(0)

    if args.defaultgateway == True:
        flog.info( inspect.stack()[0][3] + ": Default gateway IP configureren gestart.") 

        try:
            _id, ip_address_router, _label = config_db.strget( 166, flog )
            # check if ip adress is syntax correct.
            if len(ip_address_router) > 0: #skip empty address.
                network_lib.is_valid_ip_adres( ip_address_router )
            else:
                flog.warning( inspect.stack()[0][3] + ": IP Default gateway is niet gezet, gestopt. " )
                sys.exit( 1 )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": IP adres router fout : " + str(e.args[0]) )
            sys.exit( 1 )

        flog.info( inspect.stack()[0][3] + ": Default gateway IP " + str( ip_address_router ) + " wordt toegevoegd.")

        #read config file into buffer
        cf = network_lib.ConfigFile()
        cf.init( filename=network_lib.DHCPCONFIG, flog=flog, device=None )

        # remove by tag
        cf.remove_line_by_tag( tag=network_lib.P1MON_ROUTER_TAG )
        
        line = (network_lib.P1MON_STATIC_ROUTER_TXT + str( ip_address_router)).ljust(space_adjust) + network_lib.P1MON_ROUTER_TAG
        cf.add_single_line_to_buffer( line )
        
        if cf.write_buffer_to_file() == False:
            flog.error( inspect.stack()[0][3] + ": gestopt config file " + network_lib.DHCPCONFIG + " was niet aan te passen." )
            sys.exit( 1 )
    
        flog.info( inspect.stack()[0][3] + ": Default gateway IP configureren gereed.") 
        sys.exit(0)

    if args.removedefaultgateway == True:
        flog.info( inspect.stack()[0][3] + ": Default gateway IP verwijderen gestart.") 

        #read config file into buffer
        cf = network_lib.ConfigFile()
        cf.init( filename=network_lib.DHCPCONFIG, flog=flog, device=None )

        # remove by tag
        cf.remove_line_by_tag( tag=network_lib.P1MON_ROUTER_TAG )

        if cf.write_buffer_to_file() == False:
            flog.error( inspect.stack()[0][3] + ": gestopt config file " + network_lib.DHCPCONFIG + " was niet aan te passen." )
            sys.exit( 1 )
    
        flog.info( inspect.stack()[0][3] + ": Default gateway IP verwijderen gereed.") 
        sys.exit(0)

    if args.staticip != None:
        flog.info( inspect.stack()[0][3] + ": static IP configureren gestart.") 
        # read IP adress from config
        try:
            if args.staticip == 'wlan0':
                _id, ip_address, _label = config_db.strget( 165, flog )
            else:
                _id, ip_address, _label = config_db.strget( 164, flog )
            # check if ip adress is syntax correct.
            network_lib.is_valid_ip_adres( ip_address )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": IP adres fout : " + str(e.args[0]) )
            sys.exit( 1 )

        flog.info( inspect.stack()[0][3] + ": static IP configureren voor " + str( args.staticip ) + " met ip adres " + str( ip_address) )
        
        #read config file into buffer
        cf = network_lib.ConfigFile()
        cf.init( filename=network_lib.DHCPCONFIG, flog=flog, device=args.staticip )

        # remove the entries in the config buffer by device
        cf.remove_entries_by_device()

        rec = network_lib.ip_config_record
        
        if args.staticip == 'wlan0':
            rec['interface'] = (rec['interface'] + str( args.staticip )).ljust(space_adjust) + network_lib.P1MON_INTERFACE_WLAN0_TAG
            rec['ip']        = (rec['ip'] + str( ip_address ) + "/24").ljust(space_adjust)   + network_lib.P1MON_IP_WLAN0_TAG
            #rec['router']    = (rec['router'] + str( ip_address_router )).ljust(space_adjust) + network_lib.P1MON_ROUTER_WLAN0_TAG
            #rec['domain']    = (rec['domain'] + str( ip_address_domain )).ljust(space_adjust) + network_lib.P1MON_DOMAIN_WLAN0_TAG
        else:
            rec['interface'] = (rec['interface'] + str( args.staticip )).ljust(space_adjust) + network_lib.P1MON_INTERFACE_ETH0_TAG
            rec['ip']        = (rec['ip'] + str( ip_address ) + "/24").ljust(space_adjust)   + network_lib.P1MON_IP_ETH0_TAG
            #rec['router']    = (rec['router'] + str( ip_address_router )).ljust(space_adjust) + network_lib.P1MON_ROUTER_ETH0_TAG
            #rec['domain']    = (rec['domain'] + str( ip_address_domain )).ljust(space_adjust) + network_lib.P1MON_DOMAIN_ETH0_TAG

        cf.add_record_to_buffer( record=rec )
        if cf.write_buffer_to_file() == False:
            flog.error( inspect.stack()[0][3] + ": gestopt config file " + network_lib.DHCPCONFIG + " was niet aan te passen." )
            sys.exit( 1 )
        
        # reconfigure the network device this takes a couple of seconds.
        #network_lib.restart_network_device( device=args.staticip, flog=flog )

        flog.info( inspect.stack()[0][3] + ": static IP configureren gereed.") 
        sys.exit(0)

    if args.removestaticip != None:

        flog.info( inspect.stack()[0][3] + ": static IP verwijderen gestart.") 
        #read config file into buffer
        cf = network_lib.ConfigFile()
        cf.init( filename=network_lib.DHCPCONFIG, flog=flog, device=args.removestaticip )
        
        # remove the entries in the config buffer by device
        cf.remove_entries_by_device()
        if cf.write_buffer_to_file() == False:
            flog.error( inspect.stack()[0][3] + ": gestopt config file " + network_lib.DHCPCONFIG + " was niet aan te passen." )
            sys.exit( 1 )

        flog.info( inspect.stack()[0][3] + ": static IP verwijderen gereed.") 
        sys.exit(0)

    flog.info( inspect.stack()[0][3] + ": gestopt zonder uitgevoerde acties, geef commandline opties op." )
    sys.exit ( 1 ) # should be an error when there are no options given.

def disk_to_ram_restore():
    os.system("/p1mon/scripts/P1DbCopy.py --allcopy2ram")


def remove_dns():
    flog.info( inspect.stack()[0][3] + ": DNS IP verwijderen gestart.") 

    #read config file into buffer
    cf = network_lib.ConfigFile()
    cf.init( filename=network_lib.DHCPCONFIG, flog=flog, device=None )

    # remove by tag
    cf.remove_line_by_tag( tag=network_lib.P1MON_DOMAIN_TAG )

    # add default DNS entries, we need some
    line = (network_lib.P1MON_STATIC_DOMAIN_TXT + \
            network_lib.DEFAULT_INET_DNS ).ljust(space_adjust) + " " + network_lib.P1MON_DOMAIN_TAG
    cf.add_single_line_to_buffer( line )

    if cf.write_buffer_to_file() == False:
        flog.error( inspect.stack()[0][3] + ": gestopt config file " + network_lib.DHCPCONFIG + " was niet aan te passen." )
        sys.exit( 1 )
    flog.info( inspect.stack()[0][3] + ": DNS IP verwijderen verwijderen gereed.") 


def set_dns( ):
    flog.info( inspect.stack()[0][3] + ": DNS IP configureren gestart.") 

    # read IP adress domain server (DNS) from config
    try:
        _id, ip_address_domain, _label = config_db.strget( 167, flog )
        # check if ip adress is syntax correct.
        if len( ip_address_domain ) > 0: #skip empty address.
            network_lib.is_valid_ip_adres( ip_address_domain )
        else:
            flog.warning( inspect.stack()[0][3] + ": IP adres domein (dns) is niet gezet, gestopt. " )
            sys.exit( 1 )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": IP adres domein (dns) fout : " + str(e.args[0]) )
        sys.exit( 1 )

    #read config file into buffer
    cf = network_lib.ConfigFile()
    cf.init( filename=network_lib.DHCPCONFIG, flog=flog, device=None )

    # remove by tag
    cf.remove_line_by_tag( tag=network_lib.P1MON_DOMAIN_TAG )

    if len(str( ip_address_domain )) != 0:
        ip_address_domain = ip_address_domain + " "

    line = (network_lib.P1MON_STATIC_DOMAIN_TXT + ip_address_domain + \
            network_lib.DEFAULT_INET_DNS ).ljust(space_adjust) + " " + network_lib.P1MON_DOMAIN_TAG
    cf.add_single_line_to_buffer( line )
    
    if cf.write_buffer_to_file() == False:
        flog.error( inspect.stack()[0][3] + ": gestopt config file " + network_lib.DHCPCONFIG + " was niet aan te passen." )
        sys.exit( 1 )
    
    flog.info( inspect.stack()[0][3] + ": DNS IP " + str( ip_address_domain ) + "wordt toegevoegd.")
    flog.info( inspect.stack()[0][3] + ": DNS IP configureren gereed.") 


########################################################
# close program when a signal is recieved.             #
########################################################
def saveExit(signum, frame):
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(0)

########################################################
# init                                                 #
########################################################
if __name__ == "__main__":
    global process_bg 
    try:
        os.umask( 0o002 )
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname)    
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])
