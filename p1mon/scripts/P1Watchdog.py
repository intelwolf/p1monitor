# run manual with ./P1Watchdog
import const
import crypto3
import crontab_lib
import filesystem_lib
import findProcessIdByName
import glob
import inspect
import json
import listOfPidByName
import logger
import network_lib
import network_time_lib
import os
import process_lib
import psutil
import random
import random
import shutil
import signal
import socket
import sqldb
import subprocess
import sys
import samba_lib
import system_info_lib
import systemid
import time
import urllib
import urllib.request
import util
import wifi_lib

prgname = 'P1Watchdog'

rt_status_db            = sqldb.rtStatusDb()
config_db               = sqldb.configDB()

net_time                = network_time_lib.NetworkTimeStatus()
p1_no_data_notification = False
next_version_timestamp  = 0 # if this value is < than utc do retry fetch remote version data.
next_duckdns_timestamp  = 0 # if this value is < than utc do retry to do an DuckDns update.
auto_import_is_active   = False # used as flag to see if import is running
msg_import_busy         = "SQL import loopt"

def MainProg():

    flog.info("Start van programma.")

    try:
        crontab_lib.set_crontab_logcleaner( flog=flog )
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": crontab log cleaner fout: " + str(e.args[0]) )
    flog.info(inspect.stack()[0][3]+": crontab log cleaner ge(re)activeerd." )

    # check_and_clean_log_folder() #clean the /var/log folder when the space is more then 80% 2.0.0 removed.

    DiskRestore()

    # open van status database
    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)     
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel: "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG, const.DB_CONFIG_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)." + const.FILE_DB_CONFIG +" ) melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    #dhcpconfig = network_lib.DhcpcdConfig(config_db=config_db, flog=flog )
    #dhcpconfig.set_config_from_db()
    #sys.exit()

    rt_status_db.timestamp( 17, flog )

    # lees systeem ID uit en zet deze in de config database. 
    # versleuteld om dat deze data in een back-up bestand terecht kan komen.
    try:  
        flog.info(inspect.stack()[0][3]+': System ID zetten in configuratie database: ' + str( systemid.getSystemId() ) )
        sysid_encrypted  = crypto3.p1Encrypt( systemid.getSystemId(),"sysid" ).encode('utf-8').decode('utf-8')
        config_db.strset( sysid_encrypted ,58, flog ) 
    except Exception as e:
        flog.warning(inspect.stack()[0][3]+": System ID zetten mislukt -> " + str(e.args[0]))

    # get WLAN SSID (init the wifi essids bij het starten)
    wifi_lib.list_wifi_ssid( output_path=const.FILE_WIFISSID, flog=flog )

    # set CPU info
    cpu_info = system_info_lib.get_cpu_info()
    rt_status_db.strset(cpu_info['CPU-model'],51,flog)
    rt_status_db.strset(cpu_info['Hardware'],52,flog)
    rt_status_db.strset(cpu_info['Revision'],53,flog)
    rt_status_db.strset(cpu_info['Pi-model'],55,flog)

    #init P1 new version check. Empty status records
    #rt_status_db.strset( '', 66,  flog )
    #rt_status_db.strset( '', 67,  flog )
    #rt_status_db.strset( '', 68,  flog )
    #rt_status_db.strset( '', 110, flog )

    check_for_new_p1monitor_version()
    get_cpu_temperature()
    DuckDNS()
    get_default_gateway()
    ntp_status()
    check_and_set_samba_mode( setforced=True )
    
    ## Internet IP adres
    rt_status_db.strset( network_lib.get_public_ip_address(),26,flog )
    ## DNS naamv van publieke adres
    #rt_status_db.strset(getHostname(getPublicIpAddress()),27,flog)
    rt_status_db.strset( network_lib.get_host_name_by_ip( network_lib.get_public_ip_address() ), 27, flog )
    ## is het Internet bereikbaar
    #if getInternetStatusByDnsServers():
    if network_lib.fqdn_ping( flog=flog ,info_messages=True):
        rt_status_db.strset("ja",24,flog)
        rt_status_db.timestamp(23,flog)
    else:
        rt_status_db.strset("nee",24,flog)
        flog.error(inspect.stack()[0][3]+": geen Internet verbinding.")     

    #sys.exit()

    # main loop
    cnt = 0
    while 1:

        # elke 10 sec acties
        if cnt%5 == 0:
            ## systeem gegevens updaten.
            rt_status_db.strset( system_info_lib.get_system_uptime(flog), 19, flog)
            ## cpu load
            rt_status_db.strset(str(psutil.cpu_percent(interval=None, percpu=False)),18,flog)
            ## ruimte vrij op ramdisk
            rt_status_db.strset( system_info_lib.get_disk_pct_used( const.DIR_RAMDISK), 21, flog  )
            ## RAMgebruik
            rt_status_db.strset( ram_used_percentage(),31,flog)
            ## CPU temperatuur
            get_cpu_temperature()
            ## controle of er nog P1 data binnen komt.
            check_for_p1port_data()
            ## Watermeter reset.
            checkWatermeterCounterSetRun()
            ## check if there is an autoimport file
            ## checkAutoImport() remove in version 2.4.0
            ## check P1PowerProductionS0 run or stop
            checkPowerProductionS0Run()
            ## checkWaterMeter run or stop
            check_water_meter_run()
            ## P1MQTT run or stop
            checkMQTTRun()
            ## P1MQTT run or stop
            checkP1SqlImportRun()
            ## P1SolarSetup / Runtime P1SolarEdge different tasks
            #flog.setLevel( logging.DEBUG )
            P1SolarSetup()
            P1SolarResetConfig()
            P1SolarReloadAllData()
            P1SolarReader()
            P1SolarFactoryReset()
            #flog.setLevel( logging.INFO )
            DuckDNS()
            P1NginxSetApiTokens()
            P1NginxConfigApi()
            P1NetworkConfig()
            DropboxAuthenticationRequest()
            check_upgrade_aide_save_run()
            export_db_to_excel_run()
            check_and_set_samba_mode( setforced=False )
            set_wifi( setforced=False )
            check_and_run_backup()
            run_patch()

            # debug dump 
            trigger_function(
                prg_name="sudo nohup /p1mon/scripts/in_ex_custom_www.sh export", 
                prg_parameters="> /dev/null 2>&1 &",
                db_config_index=195,
                db_config_parameter_index=196,
                start_msg="export custom www gestart.",
                stop_msg="export custom www gereed.",
                err_msg="export custom www gefaald.",
                timeout=120,
                use_python_launcer=False
            )

            # debug dump 
            trigger_function(
                prg_name="nohup /p1mon/scripts/debugdump.sh", 
                prg_parameters="> /dev/null 2>&1 &",
                db_config_index=191,
                db_config_parameter_index=192,
                start_msg="debug dump gestart.",
                stop_msg="debug dump gereed.",
                err_msg="debug dump gefaald.",
                timeout=500,
                use_python_launcer=False
            )

            # halt / poweroff van de Rpi
            trigger_function(
                prg_name="sudo", 
                prg_parameters="halt",
                db_config_index=190,
                start_msg="stoppen (halt) van Rpi gestart.",
                stop_msg="stoppen (halt) van Rpi gereed.",
                err_msg="stoppen (halt) van Rpi gefaald.",
                timeout=180,
                use_python_launcer=False,
                ignore_running_processes=True
            )

            # reboot van de Rpi
            trigger_function( 
                prg_name="sudo", 
                prg_parameters="reboot",
                db_config_index=189,
                start_msg="reboot van Rpi gestart.",
                stop_msg="reboot van Rpi gereed.",
                err_msg="reboot van Rpi gefaald.",
                timeout=180,
                use_python_launcer=False,
                ignore_running_processes=True
            )

            # database wissen
            trigger_function( 
                prg_name="nohup /p1mon/scripts/p1mon.sh cleardatabase > /dev/null 2>&1 &", 
                prg_parameters="",
                db_config_index=188,
                start_msg="wissen van database gestart.",
                stop_msg="wissen van database gereed.",
                err_msg="wissen van database gefaald.",
                use_python_launcer=False
            )

            # test email function.
            trigger_function( 
                prg_name="/p1mon/scripts/P1SmtpCopy", 
                prg_parameters="--testmail &",
                db_config_index=187,
                start_msg="test email gestart.",
                stop_msg="test email gereed.",
                err_msg="test email gefaald.",
                use_python_launcer=False
            )

            # kWh reset meter (S0).
            trigger_function( 
                prg_name="/p1mon/scripts/P1PowerProductionS0CounterSet", 
                prg_parameters="&",
                db_config_index=186,
                start_msg="reset van opgewekte energie meterstand(S0) gestart.",
                stop_msg="reset van opgewekte energie meterstand(S0) gestopt.",
                err_msg="reset van opgewekte energie meterstand(S0) gefaald.",
                timeout=500,
                use_python_launcer=False
             )

            # watermeter reset.
            trigger_function( 
                prg_name="/p1mon/scripts/P1WatermeterV2CounterSet",
                prg_parameters="&",
                db_config_index=185,
                start_msg="reset van watermeterstand gestart.",
                stop_msg="reset van watermeterstand gestopt.",
                err_msg="reset van watermeterstand gestart gefaald.",
                timeout=500,
                use_python_launcer=False
             )

            # Weather update.
            trigger_function( 
                prg_name="/p1mon/scripts/P1Weather", 
                prg_parameters="--recoverforced &",
                db_config_index=203,
                start_msg="Weer informatie gestart.",
                stop_msg="Weer informatie gereed.",
                err_msg="Weer informatie gefaald.",
                use_python_launcer=False
            )

            socat()

        # elke 60 sec acties
        if cnt%30 == 0:
            # check if we need to change the cron entries.
            check_cron_backup()

            wlan_info = network_lib.get_nic_info( 'wlan0' )
            lan_info  = network_lib.get_nic_info( 'eth0' )
            get_default_gateway()

            #get WLAN SSID
            wifi_lib.list_wifi_ssid( output_path=const.FILE_WIFISSID, flog=flog )
            ## get lan IP en Wifi adres
            if lan_info['ip4'] != None:
                rt_status_db.strset(lan_info['ip4'],20,flog)
                ## get LAN hostnaam
                #rt_status_db.strset(  getHostname(lan_info['ip4']),28,flog) 
                rt_status_db.strset( network_lib.get_host_name_by_ip( lan_info['ip4']), 28, flog )
            else:
                rt_status_db.strset('onbekend',20,flog)
            if wlan_info['ip4'] != None:
                rt_status_db.strset(wlan_info['ip4'],42,flog)
            else:
                rt_status_db.strset('onbekend',42,flog)
            if lan_info['mac'] != None:
                rt_status_db.strset( lan_info['mac'], 72, flog )
            else:
                rt_status_db.strset( 'onbekend', 72, flog )
            if wlan_info['mac'] != None:
                rt_status_db.strset( wlan_info['mac'], 73, flog )
            else:
                rt_status_db.strset( 'onbekend', 73, flog )

            ## besturingssysteem versie
            rt_status_db.strset( system_info_lib.get_os_version(), 22, flog )
            ## Python versie die we gebruiken.
            rt_status_db.strset( system_info_lib.get_python_version(), 25, flog )
            ## update the NTP network time status.
            ntp_status()

        # elke 300 sec acties
        if cnt%150 == 0:
            ## check for new P1 monitor version.
            check_for_new_p1monitor_version()
            ## clean download dir
            cleanDownload()
            ## clear /var/log als deze te vol is.
            ## check_and_clean_log_folder() 2.0.0 done by crontab

        # 900 sec processes (15 min)
        if cnt%450 == 0:
            # read data via de weather API
            update_weather_data()
            #run_dynamic_pricing()

        # 1800 sec processes (30 min)
        if cnt%900 == 0:
            run_dynamic_pricing()

        # elke 3600 sec acties
        if cnt%1800 == 0:
            ## Internet IP adres
            rt_status_db.strset( network_lib.get_public_ip_address(), 26, flog )

            ## DNS naam van publieke adres
            rt_status_db.strset( network_lib.get_host_name_by_ip( network_lib.get_public_ip_address() ), 27, flog)

            ## is het Internet bereikbaar
            if network_lib.fqdn_ping( flog=flog , info_messages=False):
                rt_status_db.strset("ja",24,flog)
                rt_status_db.timestamp(23,flog)
            else:
                rt_status_db.strset("nee",24,flog)
                flog.error(inspect.stack()[0][3]+": geen Internet verbinding.")  

        cnt+=1
        if cnt > 1800:
            cnt=1
        time.sleep(2) #DO NOT CHANGE!


def DiskRestore(): #180ok
    if not util.fileExist(const.FILE_SESSION):
        dummy,tail = os.path.split(const.FILE_SESSION)   
        try:
            shutil.copy2( const.DIR_FILEDISK+tail, const.FILE_SESSION )
            flog.info(inspect.stack()[0][3]+": "+const.DIR_FILEDISK+tail+" naar "+const.FILE_SESSION+" gekopieerd.")
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": kopie" + const.FILE_SESSION + " Melding: "+str(e) ) 

    cmd = "/p1mon/scripts/P1DbCopy --allcopy2ram" # 1.8.0 upgrade
    process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=True,
        flog=flog 
    )

def set_wifi( setforced=False ):

    try:
        _id, run_status, _label = config_db.strget( 183, flog )

        if int( run_status ) == 1 or setforced == True: # start process
            config_db.strset( 0, 183, flog ) # reset the flag to prevent an endless loop.

            cmd = "/p1mon/scripts/P1SetWifi &"
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
            )
            if r[2] > 0:
                flog.error(inspect.stack()[0][3]+" Wifi aanpassen gefaald.")

    except Exception as e:
        flog.error( inspect.stack()[0][3] + " Wifi onverwachte fout: " + str( e ) )
        config_db.strset( 0, 183, flog ) # fail save.

######################################################
# check and start or stop the socat systemd service  #
######################################################
def socat():
    try:
        _id, socat_is_on, _label = config_db.strget( 200, flog )
        parameter = "--disable"
        if int(socat_is_on) == 1:
            parameter = "--enable"
        # SOCAT P1 poort activate.
        trigger_function( 
            prg_name="/p1mon/scripts/P1SocatConfig",
            prg_parameters=parameter + " &",
            db_config_index=201,
            start_msg="socat service gestart.",
            stop_msg="socat service gestopt.",
            err_msg="socat service gefaald.",
            timeout=500,
            use_python_launcer=False
            )
            
    except Exception as e:
        flog.error( inspect.stack()[0][3] + " onverwachte fout: " + str( e ) )


###########################################################
# general use trigger fuction to start other processes    #
# TODO: refactor older functions to this general function #
###########################################################
def trigger_function(
    prg_name=None,
    prg_parameters="",
    db_config_index=None,
    db_config_parameter_index=None, # use this if the parameter is set in the database
    start_msg="start message onbekend",
    stop_msg="stop message onbekend",
    err_msg="fout message onbekend",
    timeout=30,
    use_python_launcer=True,
    ignore_running_processes=False
    ):

    #flog.setLevel( logger.logging.DEBUG )

    try:
        _id, needs_to_run_status, _label = config_db.strget( int(db_config_index), flog )
        
        if ignore_running_processes == False:
            pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        else:
            pid_list = [] # empty to ignore the processes already running

        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( needs_to_run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int( needs_to_run_status ) == 1 and len( pid_list ) == 0: # start process
            flog.info( inspect.stack()[0][3] + " " + prg_name + " " + prg_parameters + " " + start_msg )

            config_db.strset( '0', int(db_config_index), flog ) # reset run bit
            
            if use_python_launcer == True:
                cmd_prefix = "/p1mon/scripts/pythonlaunch.sh "
            else:
                cmd_prefix = ""

            if db_config_parameter_index != None:
                _id, parameter_by_index, _label = config_db.strget( int(db_config_parameter_index), flog )
            else:
                parameter_by_index = ""

            cmd = cmd_prefix + prg_name + " " +  parameter_by_index + " " + prg_parameters
            flog.debug( inspect.stack()[0][3] + " cmd = " +  cmd )
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=timeout
            )
            if r[2] > 0:
                flog.error(inspect.stack()[0][3] + " " + prg_name + " " + parameter_by_index + " " + prg_parameters + " " + err_msg )
            else:
                flog.info(inspect.stack()[0][3] + " " + prg_name + " " + parameter_by_index + " " + prg_parameters + " " +stop_msg )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + " " + prg_name + " " + parameter_by_index + " " + prg_parameters + " " + err_msg + " onverwachte fout: " + str( e ) )
        config_db.strset( '0', int(db_config_index), flog ) # reset run bit # fail save to stop

    #flog.setLevel( logger.logging.INFO )

def check_and_set_samba_mode( setforced=False ):

    try:
        _id, run_status, _label = config_db.strget( 182, flog )

        if int( run_status ) == 1 or setforced == True: # start process
            
            config_db.strset( 0, 182, flog ) # reset the flag to prevent an endless loop.

            flog.info( inspect.stack()[0][3] + ": SAMBA mode configuratie gestart" )
            _id, fileshare_mode,  _label = config_db.strget( 6, flog ) # read the fileshare modus from config db.

            mode = samba_lib.FILESHARE_MODE_OFF
            if fileshare_mode == "data":
                mode = samba_lib.FILESHARE_MODE_DATA
            elif fileshare_mode == "dev":
                mode = samba_lib.FILESHARE_MODE_DEV

            flog.info( inspect.stack()[0][3] + ": SAMBA mode " + str(mode) + " wordt geactiveerd.")
            samba = samba_lib.Samba( flog )
            samba.set_share_mode( fileshare_mode = mode )

            flog.info( inspect.stack()[0][3] + ": SAMBA mode configuratie gereed." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + " SAMBA onverwachte fout: " + str( e ) )


#############################################################
# get the dynamic pricing when this is enabeld idx 204 > 1  #
# means run and select the correct parameter.               #
#############################################################
def run_dynamic_pricing():
    try:
        prg_name = "/p1mon/scripts/P1DynamicPrices"

        _id, get_run_status, _label = config_db.strget( 204, flog )

        flog.debug( inspect.stack()[0][3] + ": needs_to_run_status =" + str(get_run_status) )
        if int( get_run_status ) > 0:

            prg_parameter = ""
            if int(get_run_status) == 1:
                prg_parameter = "--getapidata --energyzero"

            flog.debug( inspect.stack()[0][3] + ": P1DynamicPrices gestart met parameters " + prg_parameter )
            cmd = prg_name + " " + prg_parameter + " > /dev/null 2>&1 &"
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
            )
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )


def run_patch():
    try:

        prg_name = "P1Patcher"
        _id, needs_to_run_status, _label = config_db.strget( 194, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( needs_to_run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int( needs_to_run_status ) > 0 and len( pid_list ) < 1:
            flog.info( inspect.stack()[0][3] + ": P1Patcher gestart." )
            cmd = "/p1mon/scripts/" + prg_name + " > /dev/null 2>&1 &"
            flog.debug( inspect.stack()[0][3] + ": cmd =" +str(cmd) )
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
            )
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset( '0', 194, flog) # fail save to stop and suppres no integer settings


def check_cron_backup():
    try:
        _id, needs_to_run_status, _label = config_db.strget( 181, flog )
        if int( needs_to_run_status ) > 0:
            crontab_lib.update_crontab_backup( flog=flog )
        config_db.strset( "0", 181, flog ) # reset bit needs to run bit
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

def update_weather_data():

    try:
        # check if API key is set.
        _id, api_key, _label = config_db.strget( 13, flog )
        if len( api_key ) > 31: # possible valid API key
            cmd = "/p1mon/scripts/P1Weather --getweather"
            process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=False,
                flog=flog 
            )
        else:
           flog.error(inspect.stack()[0][3]+": weer API key is korter dan verwacht." )

    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(config API key)"+str(e))


########################################################
# update the network status and status database        #
########################################################
def ntp_status(): #180ok
    try:
        net_time.status()
        rt_status_db.strset( net_time.json() ,124,flog )
        #print ( net_time.json() )
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

def get_default_gateway(): #180ok
    try:
        result_list = network_lib.get_default_gateway()
        if result_list == []:
            raise ValueError('Geen default gateway data beschikbaar.')
        for rec in result_list:
            if rec['ip4'] == None:
                rec['ip4'] = 'onbekend'
        rt_status_db.strset( rec['ip4'], 122, flog )
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

########################################################
# config static Ip address when flags are set          #
########################################################
def P1NetworkConfig():
    try:
        _id, needs_to_run_status, _label = config_db.strget( 168, flog )
        if int( needs_to_run_status ) > 0: # start process
            flog.info( inspect.stack()[0][3] + ": dhcp daemon configuratie aanpassen gestart." )
            config_db.strset( '0', 168, flog ) # reset run bit
            dhcpconfig = network_lib.DhcpcdConfig(config_db=config_db, flog=flog )
            if dhcpconfig.set_config_from_db() == False:
                raise Exception( "dhcp configuratie aanpassen.")
            flog.info( inspect.stack()[0][3] + ": dhcp daemon configuratie aanpassen succesvol." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset( '0', 168, flog ) # reset run bit # fail save to stop


########################################################
# start set or reset the NGINX config file and install #
# or deinstall the Lets Encrypt certifcates            #
########################################################
def P1NginxConfigApi(): #180ok
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1NginxConfig" 
        #print( prg_name )

        _id, needs_to_run_status, _label = config_db.strget( 162, flog )
        flog.debug( inspect.stack()[0][3] + ": uitvoeren flag is " + str(needs_to_run_status) )
        if int( needs_to_run_status ) == 0:
            #flog.setLevel( logging.INFO )
            return # no need to run 

        config_db.strset( 0, 162, flog ) # reset the flag to prevent an endless loop.

        # reset flags to unkown.
        rt_status_db.strset( 2, 117, flog )
        rt_status_db.strset( 2, 118, flog )
        rt_status_db.strset( 2, 119, flog )

        _id, api_is_active, _label = config_db.strget( 163, flog )
        if int( api_is_active ) == 1 : # start process

            config_db.strset( 1, 161, flog ) # set needs to run status
            P1NginxSetApiTokens() # important tokens must exist, otherwise the nginx will fail
            
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --activatecert gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --activatecert 2>&1" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --activatecert gefaald." )
                rt_status_db.strset( 1, 117, flog )
            else:
                rt_status_db.strset( 0, 117, flog )

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --autorenewon gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --autorenewon  2>&1" 
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --autorenewon gefaald." )
                rt_status_db.strset( 1, 118, flog )
            else:
                rt_status_db.strset( 0, 118, flog )

            # wait 20 sec because Lets Encrypt takes more time or is still busy.
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --https gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --https 2>&1" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --https gefaald." )
                rt_status_db.strset( 1, 119, flog )
            else:
                rt_status_db.strset( 0, 119, flog )

        else:

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --autorenewoff gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --autorenewoff 2>&1" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --autorenewoff  gefaald." )
                rt_status_db.strset( 1, 118, flog )
            else:
                rt_status_db.strset( 0, 118, flog )

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --http gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --http  2>&1" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --http gefaald." )
                rt_status_db.strset( 1, 119, flog )
            else:
                rt_status_db.strset( 0, 119, flog )
            
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --deactivatecert gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --deactivatecert 2>&1" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --deactivatecert gefaald." )
                rt_status_db.strset( 1, 117, flog )
            else:
                rt_status_db.strset( 0, 117, flog )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 149, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )


########################################################
# start the process to generate or updated API tokens  #
########################################################
def P1NginxSetApiTokens():
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1NginxConfig" 
       
        _id, needs_to_run_status, _label = config_db.strget( 161, flog )

        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( needs_to_run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int( needs_to_run_status ) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 161, flog)

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --apitokens gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --apitokens 2>&1" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --apitokens gefaald." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 149, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )


"""
removed in version 2.4.0
#############################################################################
# 1: check if there is a export file to import with the extention zip.pu1a  #
# 2: rename the file to see if we have full access                          #
# 3: check if there is data in the database before doing a import.          #
# 4: start the import by running import script                              #
#############################################################################
def checkAutoImport(): #180ok
    global auto_import_is_active ,msg_import_busy 
    
    #flog.setLevel( logging.DEBUG )
    try:
        import_filename_zip         = const.DIR_FILEDISK  + const.EXPORT_PREFIX + "-" + const.P1_UPGRADE_ASSIST + ".zip"
        import_filename_zip_pu1a    = import_filename_zip + ".p1ua"
        import_filename_status      = const.DIR_RAMDISK + const.EXPORT_PREFIX + "-" + const.P1_UPGRADE_ASSIST + ".zip.status"
        
        flog.debug( inspect.stack()[0][3] + ":controle of het auto import bestand bestaat -> " + str( import_filename_zip_pu1a ) )

        if os.path.isfile( import_filename_zip_pu1a ):
            os.rename( import_filename_zip_pu1a, import_filename_zip )
            if os.path.isfile( import_filename_zip ):
                flog.info( inspect.stack()[0][3] + ":auto import gevonden en klaar voor import -> " + str( import_filename_zip) )
                rt_status_db.strset("gereed voor import",93,flog)
                rt_status_db.timestamp( 94,flog )
                return # not needed bug give the user 10 secs (cyle time to see the message)
            else:
                flog.error( inspect.stack()[0][3] + ": bestandnaam aanpassen van " + str( import_filename_zip_pu1a ) + " gefaald." )
        else:
            flog.debug( inspect.stack()[0][3] + ": geen import bestand gevonden-> " + str( import_filename_zip_pu1a ) )

        #check if we have data in the database
        if auto_import_is_active == False and os.path.isfile( import_filename_zip ) == True:
            flog.debug( inspect.stack()[0][3] + ": check if we have data in the database" )
            e_db_history_min = sqldb.SqlDb2()
            try:
                e_db_history_min.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_MIN_TAB)
                sqlstr = "select count() from " + const.DB_HISTORIE_MIN_TAB
                sqlstr=" ".join(sqlstr.split())
                flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
                rec_p = e_db_history_min.select_rec( sqlstr )
                flog.debug( inspect.stack()[0][3] + ": waarde van count record " + str(rec_p) )
                if int(rec_p[0][0]) < 2: # wait until there is 2 minutes of data available
                    msg = "wacht op slimme meter data"
                    rt_status_db.strset( msg, 93, flog )
                    rt_status_db.timestamp( 94,flog )
                    flog.info(inspect.stack()[0][3] + ": " + msg )
                    return # do noting until there is data
            except Exception as e:
                flog.critical(inspect.stack()[0][3]+": database niet te openen(4)." + const.FILE_DB_E_HISTORIE + ") melding:"+str(e.args[0]))
                return 

        if os.path.isfile( import_filename_zip ) == False and auto_import_is_active == True :
            msg = "SQL import gereed"
            rt_status_db.strset( msg, 93, flog )
            rt_status_db.timestamp( 94,flog )
            flog.info(inspect.stack()[0][3] + ": " + msg )
            auto_import_is_active = False
            #clean status file
            os.remove( import_filename_status )
            
        if os.path.isfile( import_filename_zip ):
            flog.debug( inspect.stack()[0][3] + ": import zipfile gevonden ->"  + str(import_filename_zip ) ) 
            if auto_import_is_active == False:
                rt_status_db.strset( "SQL import wordt gestart", 93, flog )
                rt_status_db.timestamp( 94,flog )
                auto_import_is_active = True
                rt_status_db.strset( "SQL import gestart", 93, flog )
                rt_status_db.timestamp( 94,flog )

                cmd = "/p1mon/scripts/P1SqlImport -i " + import_filename_zip + " > /dev/null 2>&1 &" 
                r = process_lib.run_process( 
                    cms_str = cmd,
                    use_shell=True,
                    give_return_value=True,
                    flog=flog,
                    timeout = None
                )
                if r[2] > 0:
                    msg = "P1SqlImport gefaalt"
                    flog.error(inspect.stack()[0][3] + msg  )
                    rt_status_db.strset( msg, 93, flog )
                    rt_status_db.timestamp( 94,flog )
       
        if auto_import_is_active == True:
                #update the status
                if len( msg_import_busy ) < 60:
                    msg_import_busy = msg_import_busy + "."
                flog.info(inspect.stack()[0][3] + ": " + msg_import_busy  )
                rt_status_db.strset( msg_import_busy , 93, flog )
                rt_status_db.timestamp( 94,flog )
                
    
        #print ( "auto_import_is_active =  " + str(auto_import_is_active) )
        #print (" os.path.isfile( import_filename_zip ) = " + str( os.path.isfile( import_filename_zip ) ) )
    except Exception as e:
        flog.error(inspect.stack()[0][3]+" Onverwachte fout: " + str( e ) )
    
    #flog.setLevel( logging.INFO )
"""


#########################################################
# start the process to export a DB to an Excel workbook #
#########################################################
def export_db_to_excel_run(): #180ok
    try:
        prg_name = "P1DbToXlsx" 
       
        _id, db_file_to_export, _label = config_db.strget( 172, flog )
        if len(db_file_to_export) > 0:
            needs_to_run_status = 1
        else:
            needs_to_run_status = 0

        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( needs_to_run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int( needs_to_run_status ) == 1 and len( pid_list) == 0: # start process

            config_db.strset( '', 172, flog )

            excel_filepath  = const.DIR_DOWNLOAD + db_file_to_export + ".xlsx"
            database        = const.DIR_RAMDISK  + db_file_to_export

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " gestart." )

            cmd = "/p1mon/scripts/"  + prg_name + ' --datebase ' + database + ' --output ' + excel_filepath
            #print ( cmd )

            proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            stdout, _stderr  = proc.communicate()
            returncode = int( proc.wait( timeout=60 ) )
            
            if returncode != 0:
                flog.error( inspect.stack()[0][3] + ": cmd: " + str( cmd ) + "stdout: " +  str( stdout.decode('utf-8').replace('\n', ' ') ))

            # remove the file after one hour / 3600 seconds.
            # in principle a fail save.
            filesystem_lib.rm_with_delay( filepath=excel_filepath , timeout=3600 )

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " gestopt." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset( '', 172, flog) # fail save to stop


##############################################
# run the P1UpgradeAide program in save mode #
##############################################
def check_upgrade_aide_save_run(): #180ok
    try:
        prg_name = "P1UpgradeAide" 
       
        _id, needs_to_run_status, _label = config_db.strget( 171, flog )

        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( needs_to_run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int( needs_to_run_status ) == 1 and len( pid_list) == 0: # start process

            config_db.strset( 0, 171, flog )

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --save gestart." )
            #if os.system('/p1mon/scripts/' + prg_name + ' --save 2>&1') > 0:
            #    flog.error( inspect.stack()[0][3] + prg_name + " --save gefaald." )

            cmd = "/p1mon/scripts/" + prg_name + " --save 2>&1" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                 flog.error( inspect.stack()[0][3] + prg_name + " --save gefaald." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset( 0, 171, flog) # fail save to stop


########################################################
# checks if the Sql database script must run or must   #
# run                                                  #
########################################################
def checkP1SqlImportRun(): #180ok

    #flog.setLevel( logging.DEBUG )

    try:
        prg_name = "P1SqlImport"
       
        _id, run_status, _label = config_db.strget( 137, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": P1SqlImport run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) > 0 and len( pid_list) == 0: # start process
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )
            cmd = "/p1mon/scripts/" + prg_name + " 2>&1 >/dev/null &" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " start gefaald." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

    #flog.setLevel( logging.INFO )


########################################################
# make an url text file so an php can redirect         #
########################################################
def DropboxAuthenticationRequest(): #180ok
    try:
        prg_name = 'P1DropBoxAuth'

        _id, run_status, _label = config_db.strget( 169, flog )

        if int( run_status ) == 1: # start process
            config_db.strset(0, 169, flog) 
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " gestart." )
            #if os.system('/p1mon/scripts/' + prg_name + ' --url 2>&1 >/dev/null &') > 0:
            #    flog.error( inspect.stack()[0][3] + prg_name + " gefaald." )

            cmd = "/p1mon/scripts/" + prg_name + " --url 2>&1 >/dev/null &" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " gefaald." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 169, flog) # fail save to stop


########################################################
# Update de DuckDNS entry for the FQDN and your public #
# IP adres                                             #
########################################################
def DuckDNS(): 
    #flog.setLevel( logging.DEBUG )
    global next_duckdns_timestamp 
    #print ( next_duckdns_timestamp  )

    try:
        prg_name = "P1DuckDns" 

        _id, run_status, _label = config_db.strget( 152, flog )
        _id, force_run,  _label = config_db.strget( 153, flog )

        if int( run_status ) == 1 or int( force_run ) == 1 : # start process

            if int( force_run ) == 1:
                next_duckdns_timestamp = 0     # else the force won't run if the timeout is set.
                config_db.strset( 0, 153, flog ) # reset the forced update.
                flog.info( inspect.stack()[0][3] + ": geforceerd gestart." )

            if next_duckdns_timestamp > util.getUtcTime():
                flog.debug( inspect.stack()[0][3] +" laatste update is minder dan zes uur geleden uitgevoerd, geen update uitgevoerd." )
                return

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " gestart." )
            r = process_lib.run_process( 
                cms_str = '/p1mon/scripts/' + prg_name + ' --update 2>&1 >/dev/null &',
                use_shell=True,
                give_return_value=True,
                flog=flog
                )
            if ( r[2] ) > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " gefaald." )

            else:
                 next_duckdns_timestamp = util.getUtcTime() + 21600 # update after 6 hour

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 153, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# Start the Solar Edge reader process to get periodic  #
# data from the api                                    #
########################################################
def P1SolarReader(): #180ok
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeReader" 
       
        _id, run_status, _label = config_db.strget( 141, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            #config_db.strset(0, 142, flog)
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " gestart." )

            r = process_lib.run_process( 
                cms_str = '/p1mon/scripts/' + prg_name + ' --update 2>&1 >/dev/null &',
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout = None
                )
            if ( r[2] ) > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " gefaald." )

        if int(run_status) == 0 and len(pid_list) > 0: # stop process.
            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestopt." )
            for pid in pid_list:
                flog.info(inspect.stack()[0][3] + ": pid = " + str(pid) + " wordt gestopt. ")
                os.kill( pid, signal.SIGINT ) # do a nice stop

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 141, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# reset to factory settings. Delete config and all)    #
# database data.                                       #
########################################################
def P1SolarFactoryReset():
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeSetup" 
       
        _id, run_status, _label = config_db.strget( 149, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset( 0, 149, flog )

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --genesis  gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " --genesis  2>&1 >/dev/null &" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
            )
            if r[2] > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --genesis gefaald." )
            
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 149, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )


########################################################
# reload the sqlite database with all the data the     #
# API can deliver                                      #
########################################################
def P1SolarReloadAllData(): #180ok
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeSetup" 
       
        _id, run_status, _label = config_db.strget( 142, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 142, flog)

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --reloadsites gestart." )
            cmd = "/p1mon/scripts/" + prg_name + " --reloadsites 2>&1 >/dev/null &" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
                )
            if ( r[2] ) > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --reloadsites gefaald." )
            
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 142, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# re-reads the sites from the API                      #
########################################################
def P1SolarResetConfig(): #180ok
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeSetup" 
       
        _id, run_status, _label = config_db.strget( 145, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 145, flog)

            cmd = "/p1mon/scripts/" + prg_name + " --removesites 2>&1 >/dev/null &" # 1.8.0 upgrade
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
                )
            if ( r[2] ) > 0:
                 flog.error( inspect.stack()[0][3] + prg_name + " --removesites gefaald." )
            else:
                flog.info( inspect.stack()[0][3] + ": " + prg_name + " --removesites gereed." )

            cmd = "/p1mon/scripts/" + prg_name + " --savesites 2>&1 >/dev/null &" 
            r = process_lib.run_process(
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
                )
            if ( r[2] ) > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --savesites gefaald." )
            else:
                flog.info( inspect.stack()[0][3] + ": " + prg_name + " --savesites gereed." )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 145, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# loads the solaredge config and deletes records from  #
# the database                                         #
########################################################
def P1SolarSetup(): #180ok

    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeSetup"
       
        _id, run_status, _label = config_db.strget( 144, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 144, flog)

            cmd = "/p1mon/scripts/" + prg_name + " --savesites 2>&1 >/dev/null &" 
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog
                )
            if ( r[2] ) > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --savesites gefaald." )
            else:
                flog.info( inspect.stack()[0][3] + ": " + prg_name + " --savesites gereed." )

            cmd = "/p1mon/scripts/" + prg_name + " --deletedb 2>&1 >/dev/null &"
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog
            )
            if ( r[2] ) > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --deletedb gefaald." )
            else:
                flog.info( inspect.stack()[0][3] + ": " + prg_name + " --deletedb gereed." )


    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 144, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# checks if the MQTT script must run or must be        #
# stopped                                              #
########################################################
def checkMQTTRun(): #180ok

    #flog.setLevel( logging.DEBUG )

    try:
        prg_name = "P1MQTT"

        _id, run_status, _label = config_db.strget( 135, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": P1MQTT run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " 2>&1 >/dev/null &" # 1.8.0 upgrade
            process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=False,
                flog=flog,
                timeout=None # needed to set to None for a process that keep running.
            )

        #########################################################################
        # fail save, the program self does also a check if it should be active. #
        #########################################################################
        if int( run_status ) == 0 and len( pid_list ) > 0: # stop process.
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " wordt gestopt." )
            for pid in pid_list:
                flog.info( inspect.stack()[0][3] + ": pid = " + str(pid) + " wordt gestopt.")
                os.kill( pid, signal.SIGINT ) # do a nice stop

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

    #flog.setLevel( logging.INFO )

########################################################
# checks if the watermeter script must run or must be  #
# stopped                                              #
########################################################
def check_water_meter_run(): #180ok
    try:
        #flog.setLevel( logger.logging.DEBUG )
        prg_name = "P1WatermeterV2"
       
        _id, run_status, _label = config_db.strget( 96, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug(inspect.stack()[0][3] + ": check_water_meter_run want to run status is = " + str(run_status) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process
            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " 2>&1 >/dev/null &" # 2.3.0 upgrade
            process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=False,
                flog=flog,
                timeout=None # needed to set to None for processes that keep running.
            )


        #########################################################################
        # fail save, the program self does also a check if it should be active. #
        #########################################################################
        if int(run_status) == 0 and len(pid_list) > 0: # stop process.
            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestopt." )
            for pid in pid_list:
                flog.info(inspect.stack()[0][3] + ": pid = " + str(pid) + " wordt gestopt. ")
                os.kill( pid, signal.SIGINT ) # do a nice stop

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
    #flog.setLevel( logger.logging.INFO )

########################################################
# checks if the S0 Power productions script must run   #
# or must be stopped                                   #
########################################################
def checkPowerProductionS0Run(): #180ok
    try:
        #flog.setLevel( logger.logging.DEBUG )
        prg_name = "P1PowerProductionS0"
       
        _id, run_status, _label = config_db.strget( 125, flog )
        pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
        flog.debug(inspect.stack()[0][3] + ": checkPowerProductionS0 want to run status is = " + str(run_status) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process
            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )

            cmd = "/p1mon/scripts/" + prg_name + " 2>&1 >/dev/null &" # 1.8.0 upgrade

            process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=False,
                flog=flog,
                timeout=None # needed to set to None for a process that keep running.
            )


        #########################################################################
        # fail save, the program self does also a check if it should be active. #
        #########################################################################
        if int(run_status) == 0 and len(pid_list) > 0: # stop process.
            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestopt." )
            for pid in pid_list:
                flog.info(inspect.stack()[0][3] + ": pid = " + str(pid) + " wordt gestopt. ")
                os.kill( pid, signal.SIGINT ) # do a nice stop

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

   #flog.setLevel( logger.logging.INFO )

def restartWatermeterProcess( reason = '??????' ):
    try:
        flog.info(inspect.stack()[0][3] + ": " + reason + " verzoek, herstart van de P1Watermeter" )
        flog.debug(inspect.stack()[0][3] +  str( findProcessIdByName.findProcessIdByName( 'P1Watermeter' )) )
        listOfProcessIds = findProcessIdByName.findProcessIdByName( 'P1Watermeter' )
        if len(listOfProcessIds) > 0:
            for elem in listOfProcessIds: # possibel more running processes.
                processID = elem['pid']
                processName = elem['name']
                flog.info(inspect.stack()[0][3] + ": processID=" + str( processID ) + " processName=" + str( processName )  + " wordt gestopt.")
                os.kill( processID, signal.SIGINT ) # do a nice stop

            #fail save stop
            time.sleep( 3 ) 
            listOfProcessIds = findProcessIdByName( 'P1Watermeter' )
            if len(listOfProcessIds) > 0: # check if still running
                flog.info(inspect.stack()[0][3] + ": processID=" + str( processID ) + " processName=" + str( processName )  + " wordt geforceerd gestopt.")
                os.kill( processID, signal.SIGTERM ) # do a not nice stop
        
        listOfProcessIds = findProcessIdByName( 'P1Watermeter' )
        if len(listOfProcessIds) == 0:
            flog.info(inspect.stack()[0][3] + ": herstart P1Watermeter wordt uitgevoerd." )
            cmd = "/p1mon/scripts/P1Watermeter &"
            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog 
                )
            if ( r[2] ) > 0:
                flog.error(inspect.stack()[0][3]+" herstart gefaald.")
        else:
            flog.warning( inspect.stack()[0][3] + ": P1Watermeter herstart niet uitgevoerd, process loopt nog" )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": Watermeter " + reason + " aanpassing gefaald door fout " + str(e) )

def checkWatermeterCounterSetRun(): #180ok
    # watermeter reset
    _config_id, reset_watermeter_is_on, _text = config_db.strget( 101,flog )
    if int(reset_watermeter_is_on) == 1:
        flog.info(inspect.stack()[0][3]+": watermeter reset wordt uitgevoerd.")
        rt_status_db.strset( 'proces start(watchdog)', 107, flog )

        cmd = "/p1mon/scripts/P1WatermeterCounterSet"
        r = process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog 
        )
        if ( r[2] ) > 0:
            rt_status_db.strset( 'proces gefaald (watchdog)', 107, flog )
            flog.error( inspect.stack()[0][3]+" Watermeterstand reset is gefaald." )

# Notification via email done via P1Notifier from version 1.7.0 and higher.
def check_for_p1port_data():  #180ok
    global p1_no_data_notification
    # version 1.5.0 higer increased to 45 seconds.
    # version 2.0.0 decreased to 30 seconds
    # version 2.1.0 increased to 45 seconds
    time_out = 45 # number of seconds before notification/ detection.

    try:
        _id, utc_str, _description, _index = rt_status_db.strget( 87, flog )

        try:
            utc = int( utc_str )
        except Exception as _e:
             return # if it is not a integer then the time is not set

        delta_time = abs( util.getUtcTime() - utc )
        #print( "delta_time = ", delta_time )

        if delta_time >= time_out:
            rt_status_db.strset( 0 ,123 ,flog) # no data
            flog.debug( inspect.stack()[0][3]+ ": P1 data timeout, data is niet actief." )
        else:
            rt_status_db.strset( 1 ,123 ,flog) # data seen within the timeframe
            flog.debug( inspect.stack()[0][3]+ ": P1 data is actief." )

    except Exception as e:
        flog.warning( inspect.stack()[0][3] + " P1 data check -> " + str(e) )
        # do nothing if timestamp is not correct.
        return

def get_cpu_temperature(): #2.0.0
    rt_status_db.strset( system_info_lib.get_cpu_temperature(), 69, flog )

########################################################
# checks there is a new P1 sofware version available   #
# by an https url request to www.ztatz.nl              #
########################################################
def check_for_new_p1monitor_version():  #180ok
    #flog.setLevel(logging.DEBUG)
    global next_version_timestamp
    random.seed() # change random time for retry

    _id, version_check_on, _label = config_db.strget(51,flog)
    if int(version_check_on) == 0: 
        flog.debug(inspect.stack()[0][3]+': controle op nieuwe versie staat uit.')
        next_version_timestamp = 0 # forces to read the version information on toggle.
        return

    # time out check.
    if next_version_timestamp > util.getUtcTime(): 
        flog.debug(inspect.stack()[0][3]+': nog ' + str ( abs( util.getUtcTime() - next_version_timestamp) ) + ' seconden te gaan voor volgende poging.')
        #flog.setLevel(logging.INFO)
        return

    try :
        # timeout in seconds
        socket.setdefaulttimeout( 5 )

        url = const.ZTATZ_P1_VERSION_URL
        #url =  "https://www.ztatz.nl/p1monitor/version-test.json
        request = urllib.request.Request( url + "?" + const.P1_VERSIE  )
        response = urllib.request.urlopen(request)
        data = json.loads( response.read().decode('utf-8') )
        if data[const.ZTATZ_P1_VERSION] != const.P1_VERSIE:
            flog.info(inspect.stack()[0][3]+': nieuwe versie ' + str(data[const.ZTATZ_P1_VERSION]) +\
            ' beschikbaar van de P1 monitor software met versie serienummer ' + str(data[const.ZTATZ_P1_SERIAL_VERSION]) + '.' )
            rt_status_db.strset( data[const.ZTATZ_P1_VERSION],              66,  flog )
            rt_status_db.strset( data[const.ZTATZ_P1_VERSION_TIMESTAMP],    67,  flog )
            rt_status_db.strset( data[const.ZTATZ_P1_VERSION_TEXT],         68,  flog )
            rt_status_db.strset( data[const.ZTATZ_P1_VERSION_DOWNLOAD_URL], 86,  flog )
            rt_status_db.strset( data[const.ZTATZ_P1_SERIAL_VERSION],       110, flog )
        else:
            flog.info(inspect.stack()[0][3]+': geen nieuwe versie aanwezig, huidige versie is '+ str(data[const.ZTATZ_P1_VERSION]) + ' met versie serienummer ' + str(data[const.ZTATZ_P1_SERIAL_VERSION]) )
            #init P1 new version check. Empty status records
            rt_status_db.strset( '', 66,  flog )
            rt_status_db.strset( '', 67,  flog )
            rt_status_db.strset( '', 68,  flog )
            rt_status_db.strset( '', 110, flog )
        
        next_version_timestamp = util.getUtcTime() + 82800 + random.randint(300, 3600) #82800 = 23 uur. random add 5 to 60 min before repeat.

    except Exception as e:
         flog.error(inspect.stack()[0][3]+': ophalen remote versie informatie gefaald -> ' + str(e) )

    # flog.setLevel(logging.INFO)

def databaseRam2Disk(): #180ok
    cmd = "/p1mon/scripts/P1DbCopy --allcopy2disk --forcecopy"
    process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=False,
        flog=flog 
    )
    # wait 10 sec to flush data,just to make sure.
    time.sleep( 10 )

def makeDebugDump( id ): #180ok
    cmd = '/p1mon/scripts/debugdump.sh '+ id + " &" 
    r = process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=True,
        flog=flog,
        timeout=None
        )
    if ( r[2] ) > 0:
        flog.error(inspect.stack()[0][3]+" debug dump gefaald.")



def check_and_run_backup(): #2.0.0

    prg_name = "P1Backup"
    _id, run_status, _label = config_db.strget( 184, flog )
    
    pid_list, _process_list = listOfPidByName.listOfPidByName( prg_name )
    flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

    if int( run_status ) == 1 and len( pid_list ) == 0: # start process
        try:

            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )

            cmd = "/p1mon/scripts/" + prg_name +" --forcebackup &" 
            process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=flog,
                timeout=None
            )
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": Onverwacht fout " + str(e) )

        config_db.strset( 0, 184, flog ) # reset the run flag

def cleanDownload(): #180ok
    for name in glob.glob(const.DIR_DOWNLOAD +'*.zip'):
        try:
            file_time_delta = int(util.getUtcTime() - os.path.getmtime(name))
            #print(file_time_delta)
            if ( file_time_delta > 86400 ): # erase after a day.
                os.remove(name)
                flog.warning(inspect.stack()[0][3]+': file '+name+' is ouder dan 1 dag en wordt verwijderd.')
            else:
                flog.debug(inspect.stack()[0][3]+': file '+name+ ' is jonger dan 1 dag ,geen actie.')
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": Onverwacht fout op file "+name+' '+str(e))

def ram_used_percentage(): #180ok
    try:
        return system_info_lib.get_ram_used_pct()
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": Ram gebruik uitlezen gefaald "+str(e))
        return "0"

def saveExit(signum, frame):
    #setFileFlags()
    signal.signal(signal.SIGINT, original_sigint)
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    os.umask( 0o002 )
    flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log", prgname )   
    flog.setLevel( logger.logging.INFO )
    flog.consoleOutputOn( True )
    original_sigint = signal.getsignal( signal.SIGINT )
    signal.signal( signal.SIGINT, saveExit )
    MainProg()