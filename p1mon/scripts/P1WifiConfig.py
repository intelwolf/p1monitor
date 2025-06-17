# run manual with ./P1WifiConfig

import const
import sys
import inspect
import logger
import argparse
import util
import time
import os
import pwd
import shutil
import sqldb
import wifi_lib
import nmcli_lib
import network_lib

prgname = 'P1WifiConfig'

rt_status_db  = sqldb.rtStatusDb()

def Main(argv): 


    flog.info("Start van programma.")
    my_pid = os.getpid()
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )


    parser = argparse.ArgumentParser(description="Configure the wifi network with the correct ESSID and WPA key.")
    parser.add_argument(
        '-e', '--essid', 
        required=False,
        help="use this essid and ignore the database."
        )
    parser.add_argument(
        '-w', '--wpakey',
        required=False,
        help="use this key and ignore the database"
        )
    parser.add_argument(
        '-c', '--configure',
        required=False,
        action="store_true",
        help="setup the wifi connection/device " + nmcli_lib.WIFI_IFNAME
        )
    parser.add_argument(
        '-d', '--deconfigure',
        required=False,
        action="store_true",
        help="remove the wifi connection/device " + nmcli_lib.WIFI_IFNAME
        )
    parser.add_argument(
        '-n', '--namesfile',
        required=False,
        help="write active ESSID's to file a file of choice"
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
        help="the IP4 address(es) for DNS ( for example 192.168.2.254,1.1.1.1)."
        )
    parser.add_argument(
        '-ip4dnsr', '--ip4dnsremove', 
        required=False,
        action="store_true",
        help="remove the IP4 address(es) for DNS."
        )

    args = parser.parse_args()

    wifi_essid  = args.essid
    wifi_key    = args.wpakey
    wifi_ip4    = args.ip4address
    wifi_ip4gateway = args.ip4gateway
    wifi_ip4dns = args.ip4dns
    
    #print( "args", args )

    if args.namesfile != None:
        try:
            wl = wifi_lib.WifiInfo( flog=flog )
            sorted_list = wl.list_wifi()
            write_file( filepath=str(args.namesfile), data_list=sorted_list )
            flog.info("Programma gereed.")
            sys.exit(0)
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": fatal error on option namesfile : "+ str(e.args[0]) )
            sys.exit(1)
        
    if args.deconfigure != False:  
        try:
            wlsw = wifi_lib.WifiConfigure( flog=flog )
            wlsw.unset()  
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    if args.configure != False:

        wldb = wifi_lib.ConfigFromDB( flog=flog )

        if wifi_key == None: 
            try:
                wifi_key = wldb.get_wpa_key()
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)

        if wifi_essid == None: 
            try:
                wifi_essid = wldb.get_essid()
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)

        if wifi_ip4 == None:
            try:
                wifi_ip4 = wldb.get_ip4()
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)
    
        if wifi_ip4gateway == None:
            try:
                wifi_ip4gateway = wldb.get_ip4gateway()
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)

        if wifi_ip4dns == None:
            try:
                dns_list = []
                dns_list.append (wldb.get_ip4dns())
                #wifi_ip4dns = wldb.get_ip4dns()
            except Exception as e:
                flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
                sys.exit(1)

        if wifi_essid != None:
            flog.debug( inspect.stack()[0][3] + ": used wifi essid = " + str(wifi_essid) ) 
            if (len(wifi_essid ) < 1):
                flog.critical( inspect.stack()[0][3] + ": fESSID must be set!" )
                sys.exit(1)

        if wifi_key != None:
            flog.debug( inspect.stack()[0][3] + ": used wifi key   = " + str(wifi_key) )  
            if (len(wifi_key) < 1):
                flog.critical( inspect.stack()[0][3] + ": ESSID must be set!" )
                sys.exit(1)

        try:
            wlsw = wifi_lib.WifiConfigure( flog=flog )
            wlsw.set( essid=wifi_essid, key=wifi_key, ip4=wifi_ip4, ip4gateway=wifi_ip4gateway, ip4dns=dns_list ) 
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)
    
        # set IP in status DB
        try:
            network_lib.update_ip_in_status_db(network_type=2, flog=flog)
        except Exception as e:
            flog.warning ( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
         
        sys.exit(0)

    if args.ip4address != None:
        try:
            wlsw = wifi_lib.WifiConfigure( flog=flog )
            wlsw.unset_ip4() # remove before setting
            wlsw.set_ip4( ip4=args.ip4address )
            network_lib.update_ip_in_status_db(network_type=2, flog=flog)
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    if args.ip4remove == True:
        wlsw = wifi_lib.WifiConfigure( flog=flog )
        wlsw.unset_ip4()
        network_lib.update_ip_in_status_db(network_type=2, flog=flog)

    if args.ip4dnsremove == True:
       wlsw = wifi_lib.WifiConfigure( flog=flog )
       wlsw.unset_ip4dns()
      

    if args.ip4dns != None:
        try:
            ip_dns_addresses = args.ip4dns.split(',')
            wlsw = wifi_lib.WifiConfigure( flog=flog )
            wlsw.set_dns( ip4_dns=ip_dns_addresses )
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    if args.ip4gateway != None:
        try:
            wlsw = wifi_lib.WifiConfigure( flog=flog )
            wlsw.set_ip4gw( ip4gw=args.ip4gateway )
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": fatal message : "+ str(e.args[0]) )
            sys.exit(1)

    sys.exit(0)

    # default message
    flog.warning( inspect.stack()[0][3] + ": no options selected, use -h for help.")
    sys.exit(0)


#######################################################
# write items to file, use a tmp file so we don't     #
# interfere with a file in use                        #
#######################################################
def write_file( filepath=None, data_list=None ): 

    if filepath != None:
        tmp_filename = filepath + ".tmp"
        try:
            fo = open( tmp_filename, "w" )
            for item in data_list:
                fo.write( item + "\n" )
            fo.close
            flog.debug( inspect.stack()[0][3]+": file written to " + str(filepath) )
            shutil.move( tmp_filename, filepath)
        except Exception as e:
            flog.error( inspect.stack()[0][3]+":  file error on " + str(filepath) + " message " + str(e.args[0]) )
    else:
        flog.warning ( inspect.stack()[0][3] + ": fatal no file path given, bad bad programmer." )

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG+prgname + ".log"
        util.setFile2user( logfile,'p1mon')
        flog = logger.fileLogger( logfile,prgname )
        #### aanpassen bij productie naar INFO
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(1)

    Main(sys.argv[1:])       



