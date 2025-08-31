# run manual with ./P1EthernetConfig

import const
import sys
import inspect
import logger
import argparse
import util
import os
import pwd
import ethernet_lib
import network_lib
import nmcli_lib
import filesystem_lib

prgname = 'P1EthernetConfig'

#rt_status_db  = sqldb.rtStatusDb()

def Main(argv): 

    flog.info("Start van programma.")
    #my_pid = os.getpid()
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description="Configure the Ethernet network.")
    parser.add_argument(
        '-c', '--configure',
        required=False,
        action="store_true",
        help="setup the Ethernet connection/device " + nmcli_lib.ETH_IFNAME
        )
    parser.add_argument(
        '-d', '--deconfigure',
        required=False,
        action="store_true",
        help="remove the Ethernet connection/device " + nmcli_lib.ETH_IFNAME
        )
    parser.add_argument(
        '-ip4', '--ip4address', 
        required=False,
        help="add the static IP4 address (for example 192.168.2.200)."
        )
    parser.add_argument(
        '-ip4r', '--ip4remove', 
        required=False,
        action="store_true",
        help="remove the static IP4 address including the IP4 gateway."
        )
    parser.add_argument(
        '-ip4gw', '--ip4gateway', 
        required=False,
        help="the IP4 address for the gateway (for example 192.168.2.254)."
        )
    parser.add_argument(
        '-ip4dns', '--ip4dns', 
        required=False,
        help="the IP4 address(es) for DNS (for example 192.168.2.254,1.1.1.1)."
        )
    parser.add_argument(
        '-ip4dnsr', '--ip4dnsremove', 
        required=False,
        action="store_true",
        help="remove the IP4 address(es) for DNS."
        )
    parser.add_argument(
        '-s', '--setupdefault',
        required=False,
        action="store_true",
        help="setup the Ethernet connection/device when no device is setup " + nmcli_lib.ETH_IFNAME
        )

    args = parser.parse_args()

    eth_ip4         = args.ip4address
    eth_ip4gateway  = args.ip4gateway
    eth_ip4dns      = args.ip4dns
    
    #print( "args", args )

    if args.setupdefault!= False:
        try:
            el_se = ethernet_lib.EthernetConfigure(flog=flog)
            if el_se.device_is_set() == False:
                el_se.set( ip4=None, ip4gateway=None, ip4dns=[] )
                flog.info( inspect.stack()[0][3] + ": device " + str( nmcli_lib.ETH_IFNAME) + " is setup." )
            else:
                flog.info( inspect.stack()[0][3] + ": device " + str( nmcli_lib.ETH_IFNAME) + " is already present, no action." )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    if args.deconfigure != False:  
        try:
            el_se = ethernet_lib.EthernetConfigure(flog=flog)
            el_se.unset()
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    if args.configure != False:

        eth_db = ethernet_lib.ConfigFromDB( flog=flog )

        if eth_ip4 == None:
            try:
                eth_ip4 = eth_db.get_ip4()
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)
    
        if eth_ip4gateway == None:
            try:
                eth_ip4gateway = eth_db.get_ip4gateway()
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)

        if eth_ip4dns == None:
            try:
                dns_list = []
                dns_list.append (eth_db.get_ip4dns())
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)
                
        try:
            el_se = ethernet_lib.EthernetConfigure(flog=flog)
            el_se.set( ip4=eth_ip4, ip4gateway=eth_ip4gateway, ip4dns=dns_list )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)
    
        # set IP in status DB
        try:
            network_lib.update_ip_in_status_db(network_type=1, flog=flog)
        except Exception as e:
            flog.warning ( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
         
        sys.exit(0)

    if args.ip4address != None:
        try:
            el_se = ethernet_lib.EthernetConfigure(flog=flog)
            el_se.unset_ip4() # remove before setting
            el_se.set_ip4( ip4=args.ip4address )
            network_lib.update_ip_in_status_db(network_type=1, flog=flog)
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    if args.ip4remove == True:
        el_se = ethernet_lib.EthernetConfigure(flog=flog)
        el_se.unset_ip4()
        network_lib.update_ip_in_status_db(network_type=1, flog=flog)

    if args.ip4dnsremove == True:
        el_se = ethernet_lib.EthernetConfigure(flog=flog)
        el_se.unset_ip4dns()

    if args.ip4dns != None:
        try:
            ip_dns_addresses = args.ip4dns.split(',')
            el_se = ethernet_lib.EthernetConfigure(flog=flog)
            el_se.set_dns( ip4_dns=ip_dns_addresses )
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    if args.ip4gateway != None:
        try:
            el_se = ethernet_lib.EthernetConfigure(flog=flog)
            el_se.set_ip4gw( ip4gw = args.ip4gateway )
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    sys.exit(0)

    # default message
    flog.warning( inspect.stack()[0][3] + ": no options selected, use -h for help.")
    sys.exit(0)


#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG+prgname + ".log"

        filesystem_lib.set_file_owners( filepath=logfile )
        filesystem_lib.set_file_permissions( filepath=logfile, permissions='664' )

        #util.setFile2user( logfile,'p1mon')
        flog = logger.fileLogger( logfile,prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(1)

    Main(sys.argv[1:])



