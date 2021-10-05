#!/usr/bin/python3
import const
import cpuinfo
import glob
import inspect
import network_lib
import sys
import hashlib
import json
import time
import subprocess
import urllib
import psutil
import string
import random
import platform
import socket
import os
import random
import struct
import shutil
import util
import urllib.request
import semaphore3
import signal
import systemid
import crypto3
import base64

from datetime import datetime, timedelta
from cpuinfo import getCpuInfo
from logger import logging,fileLogger
from sqldb import configDB, rtStatusDb, SqlDb2
from subprocess import check_output
from util import getUtcTime,fileExist,setFile2user
from semaphore3 import writeSemaphoreFile, readSemaphoreFiles
from findProcessIdByName import findProcessIdByName
from listOfPidByName import listOfPidByName

prgname = 'P1Watchdog'

rt_status_db            = rtStatusDb()
config_db               = configDB()
p1_no_data_notification = False
next_version_timestamp  = 0 # if this value is < than utc do retry fetch remote version data.
next_duckdns_timestamp  = 0 # if this value is < than utc do retry to do an DuckDns update.
auto_import_is_active   = False # used as flag to see if import is running
msg_import_busy         = "SQL import loopt"


def DiskRestore():
    if not util.fileExist(const.FILE_SESSION):
        dummy,tail = os.path.split(const.FILE_SESSION)   
        try:
            shutil.copy2(const.DIR_FILEDISK+tail, const.FILE_SESSION)
            flog.info(inspect.stack()[0][3]+": "+const.DIR_FILEDISK+tail+" naar "+const.FILE_SESSION+" gekopieerd.")
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": kopie"+const.FILE_SESSION+" Fout: "+str(e)) 
    os.system("/p1mon/scripts/P1DbCopy.py --allcopy2ram")

def MainProg():

    flog.info("Start van programma.")

    checkVarLogFolder() #clean the /var/log folder when the space is more then 80%

    DiskRestore()
   
    # open van status database
    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)     
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel: "+const.DB_STATUS_TAB+" succesvol geopend.")
    rt_status_db.timestamp(17,flog)
    
    # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # init van processen na een start
    # SAMBA aanpassen
    try:
        sqlstr = "select id, parameter from "+const.DB_CONFIG_TAB+" where id=6"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec_config=config_db.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": SAMBA status"+str(rec_config))
        setSambaMode(rec_config[0][1]) ##DEBUG TERUG ZETTEN
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

    # lees systeem ID uit en zet deze in de config database. 
    # versleuteld om dat deze data in een back-up bestand terecht kan komen.
    try:  
        flog.info(inspect.stack()[0][3]+': System ID zetten in configuratie database: ' + str( systemid.getSystemId() ) )
        sysid_encrypted  = crypto3.p1Encrypt( systemid.getSystemId(),"sysid" ).encode('utf-8').decode('utf-8')
        config_db.strset( sysid_encrypted ,58, flog ) 
    except Exception as e:
        flog.warning(inspect.stack()[0][3]+": System ID zetten mislukt -> " + str(e.args[0]))

    #get WLAN SSID (init the wifi essids bij het starten)
    getWlanSSID()
    getUptime()

    # set CPU info
    cpu_info = getCpuInfo()
    rt_status_db.strset(cpu_info['CPU-model'],51,flog)
    rt_status_db.strset(cpu_info['Hardware'],52,flog)
    rt_status_db.strset(cpu_info['Revision'],53,flog)
    rt_status_db.strset(cpu_info['Pi-model'],55,flog)

    # writeSemaphoreFile('debugdump' + '999',flog) # for debug only
    
    #init P1 new version check. Empty status records
    #rt_status_db.strset( '', 66,  flog )
    #rt_status_db.strset( '', 67,  flog )
    #rt_status_db.strset( '', 68,  flog )
    #rt_status_db.strset( '', 110, flog )

    checkForNewP1Version()
    getCpuTemperature()
    DuckDNS()
    getDefaultGateway()
  
    ## Internet IP adres
    rt_status_db.strset(getPublicIpAddress(),26,flog)
    ## DNS naamv van publieke adres
    rt_status_db.strset(getHostname(getPublicIpAddress()),27,flog)
    ## is het Internet bereikbaar
    if getInternetStatusByDnsServers():
        rt_status_db.strset("ja",24,flog)
        rt_status_db.timestamp(23,flog)
    else:
        rt_status_db.strset("nee",24,flog)
        flog.error(inspect.stack()[0][3]+": geen Internet verbinding.")     

    #sys.exit()

    # main loop
    cnt = 0
    while 1:
       
        # elke 2 sec. acties
        ## semafoor files verwerken

        list = semaphore3.readSemaphoreFiles(flog)
        #print ( list )
        if len(list) == 0:
            #flog.debug(inspect.stack()[0][3]+" geen semafoor files gevonden")
            pass
        else:
            for cmd in list:
                if cmd[:9] == 'debugdump': # nodig om file id uit de semafoor te halen
                    flog.info(inspect.stack()[0][3]+" debug dump gestart.")
                    makeDebugDump(cmd[9:-6])
                if cmd[:17] == 'custom_www_import': # nodig om file id uit de semafoor te halen
                    flog.info(inspect.stack()[0][3]+" import van custom www folder gestart.")
                    makeCustomWwwImport(cmd[17:-6])
                if cmd[:17] == 'custom_www_export': # nodig om file id uit de semafoor te halen
                    flog.info(inspect.stack()[0][3]+" export van custom www folder gestart.")
                    makeCustomWwwExport(cmd[17:-6]) 
                if cmd == 'backup.p1mon':
                    flog.info(inspect.stack()[0][3]+" backup.")
                    makeBackup()
                if cmd == 'cron.p1mon': #TODO nog nodig?
                    flog.info(inspect.stack()[0][3]+" P1Scheduler.")
                    if os.system('sudo -u p1mon /p1mon/scripts/P1Scheduler.py') > 0:
                        flog.error(inspect.stack()[0][3]+" chron update gefaald.")
                if cmd == 'halt.p1mon':
                    flog.info(inspect.stack()[0][3]+" poweroff.")
                    databaseRam2Disk()
                    if os.system('sudo /sbin/init 0') > 0:
                        flog.error(inspect.stack()[0][3]+" poweroff gefaald.")
                if cmd == 'reboot.p1mon':
                    flog.info(inspect.stack()[0][3]+" reboot.")
                    databaseRam2Disk()
                    if os.system('sudo /sbin/init 6') > 0:
                        flog.error(inspect.stack()[0][3]+" reboot gefaald.")
                if cmd == 'samba_uit.p1mon':
                    flog.info(inspect.stack()[0][3]+" SAMBA(bestand delen) service stoppen.")
                    setSambaMode(const.FILESHARE_MODE_UIT)
                if cmd == 'samba_data.p1mon':
                    flog.info(inspect.stack()[0][3]+" SAMBA(bestand delen) alleen data.")
                    setSambaMode(const.FILESHARE_MODE_DATA)            
                if cmd == 'samba_dev.p1mon':
                    flog.info(inspect.stack()[0][3]+" SAMBA(bestand delen) development.")
                    setSambaMode(const.FILESHARE_MODE_DEV)
                if cmd == 'wifi_aanpassen.p1mon':
                    flog.info(inspect.stack()[0][3]+" Wifi aanpassingen.")
                    #writeLanMacToDisk()
                    if os.system('sudo /p1mon/scripts/P1SetWifi.py') > 0: #TODO nog nodig? doen network lib. nog uitzoeken.
                        flog.error(inspect.stack()[0][3]+" Wifi aanpassen gefaald.")
                if cmd == 'upgrade_assist.p1mon':
                    flog.info(inspect.stack()[0][3]+" Upgrade assist save van data gestart")
                    if os.system('/p1mon/scripts/P1UpgradeAssist.py --save') > 0:
                        flog.error(inspect.stack()[0][3]+" Upgrade assist save gefaald.")
                if cmd == 'db_erase.p1mon':
                    flog.info(inspect.stack()[0][3]+" Database wordt gewist")
                    if os.system('/p1mon/scripts/p1mon.sh cleardatabase') > 0:
                        flog.error(inspect.stack()[0][3]+" Database wordt gewist gefaald.")
                #if cmd == 'watermeter_gpio.p1mon':
                #    restartWatermeterProcess( 'GPIO pin reset' )
                #if cmd == 'watermeter_import_data.p1mon':
                #    restartWatermeterProcess( 'import van data' )
                if cmd == 'email_test.p1mon':
                    if os.system('/p1mon/scripts/P1SmtpCopy.py --testmail') > 0:
                        flog.error(inspect.stack()[0][3]+" Sturen van test email is gefaald.") 
                if cmd == 'powerproduction_counter_reset.p1mon':
                    flog.info(inspect.stack()[0][3]+ "reset van opgewekte energie meterstand(S0) gestart.")
                    if os.system('/p1mon/scripts/P1PowerProductionS0CounterSet.py') > 0:
                        flog.error(inspect.stack()[0][3]+"reset van opgewekte energie meterstand(S0) gefaald.")
                    else:
                        flog.info(inspect.stack()[0][3]+ "reset van opgewekte energie meterstand(S0) gereed.")
                if cmd == 'watermeter_counter_reset.p1mon':
                    flog.info(inspect.stack()[0][3]+ "reset van opgewekte energie meterstand(S0) gestart.")
                    if os.system('/p1mon/scripts/P1WatermeterV2CounterSet.py') > 0:
                        flog.error(inspect.stack()[0][3]+"reset van watermeterstand gefaald.")
                    else:
                        flog.info(inspect.stack()[0][3]+ "reset van watermeterstand gereed.")



        # elke 10 sec acties
        if cnt%5 == 0:
            ## systeem gegevens updaten.
            rt_status_db.strset(getUptime(),19,flog)
            ## cpu load
            rt_status_db.strset(str(psutil.cpu_percent(interval=None, percpu=False)),18,flog)
            ## ruimte vrij op ramdisk
            rt_status_db.strset(getDiskPctUsed(const.DIR_RAMDISK),21,flog)
            ## RAMgebruik
            rt_status_db.strset(getRamUsedPct(),31,flog)
            ## CPU temperatuur
            getCpuTemperature()
            ## controle of er nog P1 data binnen komt.
            checkForP1Data()
            ## Watermeter reset.
            checkWatermeterCounterSetRun()
            ## check if there is an autoimport file
            checkAutoImport()
            ## check P1PowerProductionS0 run or stop
            checkPowerProductionS0Run()
            ## checkWaterMeter run or stop
            checkWaterMeter()
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

        # elke 60 sec acties
        if cnt%30 == 0:
            wlan_info = network_lib.get_nic_info( 'wlan0' )
            lan_info  = network_lib.get_nic_info( 'eth0' )
            getDefaultGateway()

            #get WLAN SSID
            getWlanSSID()
            ## get lan IP en Wifi adres
            if lan_info['ip4'] != None:
                rt_status_db.strset(lan_info['ip4'],20,flog)
                ## get LAN hostnaam
                rt_status_db.strset(getHostname(lan_info['ip4']),28,flog)
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
            rt_status_db.strset(getOsInfo(),22,flog)
            ## Python versie die we gebruiken.
            rt_status_db.strset(getPythonVersion(),25,flog)

        # elke 300 sec acties
        if cnt%150 == 0:
            ## check for new P1 monitor version.
            checkForNewP1Version()
            ## clean download dir
            cleanDownload()
            ## clear /var/log als deze te vol is.
            checkVarLogFolder()
            
         # elke 3600 sec acties
        if cnt%1800 == 0:
            ## Internet IP adres
            rt_status_db.strset(getPublicIpAddress(),26,flog)
            ## DNS naam van publieke adres
            rt_status_db.strset(getHostname(getPublicIpAddress()),27,flog)
            ## is het Internet bereikbaar
            if getInternetStatusByDnsServers():
                rt_status_db.strset("ja",24,flog)
                rt_status_db.timestamp(23,flog)
            else:
                rt_status_db.strset("nee",24,flog)
                flog.error(inspect.stack()[0][3]+": geen Internet verbinding.")  

        cnt+=1
        if cnt > 1800:
            cnt=1
        time.sleep(2) #DO NOT CHANGE!

def getDefaultGateway():
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

        prg_name = "P1NetworkConfig.py" 
       
        _id, needs_to_run_status, _label = config_db.strget( 168, flog )
        
        # fail save flag test so only the first 4 bits are set/used
        needs_to_run_status = ( int(needs_to_run_status) & 15 )

        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( needs_to_run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int( needs_to_run_status ) > 0 and len( pid_list) == 0: # start process

             # DEBUG TODO
            _id, needs_to_run_status, _label = config_db.strget( 168, flog )
            print ("# before=", needs_to_run_status )

            # when an dhcp deamon reload is needed do only once
            # and not for every options that need it. 
            do_dhcp_deamon_reload = False

            # etho ip changed 
            if ( int(needs_to_run_status) & 1 ) == 1: #eth0 has changed
                config_db.strset( int(needs_to_run_status) & 14, 168, flog ) # reset bit
                _id, eth0_ip, _label   = config_db.strget( 164, flog )
                if len(eth0_ip) == 0:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --removestaticip eth0 gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --removestaticip eth0 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --removestaticip eth0." )
                else:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --staticip eth0 gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --staticip eth0 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --staticip eth0." )

                if os.system('/p1mon/scripts/' + prg_name + ' --devicereload eth0 2>&1') > 0:
                    flog.error( inspect.stack()[0][3] + prg_name + " eth0 devicereload." )

            # wlan ip changed 
            if ( int(needs_to_run_status) & 2 ) == 2: #wlan0 has changed
                config_db.strset( int(needs_to_run_status) & 13, 168, flog ) # reset bit
                _id, wlan0_ip, _label  = config_db.strget( 165, flog )
                if len(wlan0_ip) == 0:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --removestaticip wlan0 gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --removestaticip wlan0 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --removestaticip wlan0." )
                else:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --staticip wlan0 gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --staticip wlan0 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --staticip wlan0." )

                if os.system('/p1mon/scripts/' + prg_name + ' --devicereload wlan0 2>&1') > 0:
                    flog.error( inspect.stack()[0][3] + prg_name + "  wlan0 device reload." )
                
                do_dhcp_deamon_reload = True

            # router/gateway has changed
            if ( int(needs_to_run_status) & 4 ) == 4: 
                config_db.strset( int(needs_to_run_status) & 11, 168, flog ) # reset bit
                _id, router_ip, _label = config_db.strget( 166, flog )
                if len( router_ip ) == 0:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --removedefaultgateway gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --removedefaultgateway 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --removedefaultgateway." )
                else:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --defaultgateway gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --defaultgateway 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --defaultgateway." )

                do_dhcp_deamon_reload = True

            # DNS has changed
            if ( int(needs_to_run_status) & 8 ) == 8: 
                config_db.strset( int(needs_to_run_status) & 7, 168, flog ) # reset bit
                _id, dns_ip, _label    = config_db.strget( 167, flog )
                if len( dns_ip ) == 0:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --removednsserver gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --removednsserver 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --removednsserver." )
                else:
                    flog.info( inspect.stack()[0][3] + ": " + prg_name + " --dnsserver gestart." )
                    if os.system('/p1mon/scripts/' + prg_name + ' --dnsserver 2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " --dnsserver." )

                do_dhcp_deamon_reload = True

            # DEBUG TODO
            _id, needs_to_run_status, _label = config_db.strget( 168, flog )
            print ( "# after=",needs_to_run_status )

            if do_dhcp_deamon_reload == True:
                if os.system('/p1mon/scripts/' + prg_name + ' --reloaddhcp  2>&1') > 0:
                        flog.error( inspect.stack()[0][3] + prg_name + " reloaddhcp" )

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 149, flog) # fail save to stop


########################################################
# start set or reset the NGINX config file and install #
# or deinstall the Lets Encrypt certifcates            #
########################################################
def P1NginxConfigApi():
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1NginxConfig.py" 

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
            if os.system('/p1mon/scripts/' + prg_name + ' --activatecert 2>&1') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --activatecert gefaald." )
                rt_status_db.strset( 1, 117, flog )
            else:
                rt_status_db.strset( 0, 117, flog )

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --autorenewon gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --autorenewon  2>&1') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --autorenewon gefaald." )
                rt_status_db.strset( 1, 118, flog )
            else:
                rt_status_db.strset( 0, 118, flog )

            # wait 20 sec because Lets Encrypt takes more time or is still busy.
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --https gestart." )
            if os.system('sleep 20; /p1mon/scripts/' + prg_name + ' --https 2>&1') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --https gefaald." )
                rt_status_db.strset( 1, 119, flog )
            else:
                rt_status_db.strset( 0, 119, flog )

        else:

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --autorenewoff gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --autorenewoff 2>&1') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --autorenewoff  gefaald." )
                rt_status_db.strset( 1, 118, flog )
            else:
                rt_status_db.strset( 0, 118, flog )

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --http gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --http  2>&1') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --http gefaald." )
                rt_status_db.strset( 1, 119, flog )
            else:
                rt_status_db.strset( 0, 119, flog )
            
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --deactivatecert gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --deactivatecert  2>&1') > 0:
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
        prg_name = "P1NginxConfig.py" 
       
        _id, needs_to_run_status, _label = config_db.strget( 161, flog )

        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( needs_to_run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int( needs_to_run_status ) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 161, flog)

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --apitokens gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --apitokens 2>&1') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --apitokens gefaald." )
            
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 149, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

# processing #####################
# 1: check if there is a export file to import with the extention zip.pu1a
# 2: rename the file to see if we have full access 
# 3: check if there is data in the database before doing a import.
# 4: start the import by running import script

def checkAutoImport():
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
            e_db_history_min = SqlDb2()
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
                cmd = "/p1mon/scripts/P1SqlImport.py -i " + import_filename_zip + " > /dev/null 2>&1 &"
                rt_status_db.strset( "SQL import gestart", 93, flog )
                rt_status_db.timestamp( 94,flog )
                if os.system( cmd ) > 0:
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

########################################################
# checks if the Sql database script must run or must   #
# run                                                  #
########################################################
def checkP1SqlImportRun():

    #flog.setLevel( logging.DEBUG )

    try:
        prg_name = "P1SqlImport.py" 
       
        _id, run_status, _label = config_db.strget( 137, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": P1SqlImport run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) > 0 and len( pid_list) == 0: # start process
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " start gefaald." )
                
        """
        #########################################################################
        # fail save, the program self does also a check if it should be active. #
        #########################################################################
        if int( run_status ) == 0 and len( pid_list ) > 0: # stop process.
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " wordt gestopt." )
            for pid in pid_list:
                flog.info( inspect.stack()[0][3] + ": pid = " + str(pid) + " wordt gestopt.")
                os.kill( pid, signal.SIGINT ) # do a nice stop
        """

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

    #flog.setLevel( logging.INFO )

########################################################
# make an url text file so an php can redirect         #
########################################################
def DropboxAuthenticationRequest():
    try:
        prg_name = 'P1DropBoxAuth.py'

        _id, run_status, _label = config_db.strget( 169, flog )

        if int( run_status ) == 1: # start process
            config_db.strset(0, 169, flog) 
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --url 2>&1 >/dev/null &') > 0:
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
        prg_name = "P1DuckDns.py" 

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
            if os.system('/p1mon/scripts/' + prg_name + ' --update 2>&1 >/dev/null &') > 0:
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
def P1SolarReader():
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeReader.py" 
       
        _id, run_status, _label = config_db.strget( 141, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            #config_db.strset(0, 142, flog)
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' 2>&1 >/dev/null &') > 0:
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
        prg_name = "P1SolarEdgeSetup.py" 
       
        _id, run_status, _label = config_db.strget( 149, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 149, flog)

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --http gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --http 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --http gefaald." )
            
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 149, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )


########################################################
# reload the sqlite database with all the data the     #
# API can deliver                                      #
########################################################
def P1SolarReloadAllData():
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeSetup.py" 
       
        _id, run_status, _label = config_db.strget( 142, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 142, flog)

            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --reloadsites gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' --reloadsites 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --reloadsites gefaald." )
            
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 142, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# re-reads the sites from the API                      #
########################################################
def P1SolarResetConfig():
    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeSetup.py" 
       
        _id, run_status, _label = config_db.strget( 145, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 145, flog)

            if os.system('/p1mon/scripts/' + prg_name + ' --removesites 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --removesites gefaald." )
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --removesites gereed." )

            if os.system('/p1mon/scripts/' + prg_name + ' --savesites 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --savesites gefaald." )
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --savesites gereed." )


    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 145, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# loads the solaredge config and deletes records from  #
# the database                                         #
########################################################
def P1SolarSetup():

    #flog.setLevel( logging.DEBUG )
    try:
        prg_name = "P1SolarEdgeSetup.py" 
       
        _id, run_status, _label = config_db.strget( 144, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": " + prg_name + " run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process

            config_db.strset(0, 144, flog)

            if os.system('/p1mon/scripts/' + prg_name + ' --savesites 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --savesites gefaald." )
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --savesites gereed." )

            if os.system('/p1mon/scripts/' + prg_name + ' --deletedb 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " --deletedb gefaald." )
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " --deletedb gereed." )


    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )
        config_db.strset(0, 144, flog) # fail save to stop
    
    #flog.setLevel( logging.INFO )

########################################################
# checks if the MQTT script must run or must be        #
# stopped                                              #
########################################################
def checkMQTTRun():

    #flog.setLevel( logging.DEBUG )

    try:
        prg_name = "P1MQTT.py" 
       
        _id, run_status, _label = config_db.strget( 135, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug( inspect.stack()[0][3] + ": P1MQTT run status is = " + str( run_status ) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process
            flog.info( inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' 2>&1 >/dev/null &') > 0:
                flog.error( inspect.stack()[0][3] + prg_name + " start gefaald." )
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
def checkWaterMeter():
    try:
        prg_name = "P1WatermeterV2.py" 
       
        _id, run_status, _label = config_db.strget( 96, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug(inspect.stack()[0][3] + ": checkWaterMeter want to run status is = " + str(run_status) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process
            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' 2>&1 >/dev/null &') > 0:
                flog.error(inspect.stack()[0][3] + prg_name + " start gefaald." )
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

########################################################
# checks if the S0 Power productions script must run   #
# or must be stopped                                   #
########################################################
def checkPowerProductionS0Run():
    try:
        prg_name = "P1PowerProductionS0.py" 
       
        _id, run_status, _label = config_db.strget( 125, flog )
        pid_list, _process_list = listOfPidByName( prg_name )
        flog.debug(inspect.stack()[0][3] + ": checkPowerProductionS0 want to run status is = " + str(run_status) + " aantal gevonden PID = " + str(len(pid_list) ) )

        if int(run_status) == 1 and len( pid_list) == 0: # start process
            flog.info(inspect.stack()[0][3] + ": " + prg_name + " wordt gestart." )
            if os.system('/p1mon/scripts/' + prg_name + ' 2>&1 >/dev/null &') > 0:
                flog.error(inspect.stack()[0][3] + prg_name + " start gefaald." )
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

def restartWatermeterProcess( reason = '??????' ):
    try:
        flog.info(inspect.stack()[0][3] + ": " + reason + " verzoek, herstart van de P1Watermeter.py" )
        flog.debug(inspect.stack()[0][3] +  str( findProcessIdByName( 'P1Watermeter.py' )) )
        listOfProcessIds = findProcessIdByName( 'P1Watermeter.py' )
        if len(listOfProcessIds) > 0:
            for elem in listOfProcessIds: # possibel more running processes.
                processID = elem['pid']
                processName = elem['name']
                flog.info(inspect.stack()[0][3] + ": processID=" + str( processID ) + " processName=" + str( processName )  + " wordt gestopt.")
                os.kill( processID, signal.SIGINT ) # do a nice stop

            #fail save stop
            time.sleep( 3 ) 
            listOfProcessIds = findProcessIdByName( 'P1Watermeter.py' )
            if len(listOfProcessIds) > 0: # check if still running
                flog.info(inspect.stack()[0][3] + ": processID=" + str( processID ) + " processName=" + str( processName )  + " wordt geforceerd gestopt.")
                os.kill( processID, signal.SIGTERM ) # do a not nice stop
        
        listOfProcessIds = findProcessIdByName( 'P1Watermeter.py' )
        if len(listOfProcessIds) == 0:
            flog.info(inspect.stack()[0][3] + ": herstart P1Watermeter.py wordt uitgevoerd." )
            if os.system('sudo -u p1mon /p1mon/scripts/P1Watermeter.py &') > 0:
                flog.error(inspect.stack()[0][3]+" herstart gefaald.")
        else:
            flog.warning( inspect.stack()[0][3] + ": P1Watermeter.py herstart niet uitgevoerd, process loopt nog" )   

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": Watermeter " + reason + " aanpassing gefaald door fout " + str(e) )

def checkWatermeterCounterSetRun():
    # watermeter reset
    _config_id, reset_watermeter_is_on, _text = config_db.strget( 101,flog )
    if int(reset_watermeter_is_on) == 1:
        flog.info(inspect.stack()[0][3]+": watermeter reset wordt uitgevoerd.")
        rt_status_db.strset( 'proces start(watchdog)', 107, flog )
        if os.system('/p1mon/scripts/P1WatermeterCounterSet.py') > 0:
            rt_status_db.strset( 'proces gefaald (watchdog)', 107, flog )
            flog.error(inspect.stack()[0][3]+" Watermeterstand reset is gefaald.")

def checkForP1Data():
    global p1_no_data_notification
    try:
        # to do check if enabled #TODO
        _id, on, _label = config_db.strget( 73, flog )
        if int(on) != 1:
            flog.debug(inspect.stack()[0][3]+": email voor controle op P1 data staat uit, geen actie.")  
            return 
    except:
        return
    
    # construct subject.
    _id, subject, _label = config_db.strget( 69, flog )
    if len( subject) < 1:
        subject =  const.DEFAULT_EMAIL_NOTIFICATION

    try:
        _id, utc_str, _description, _index = rt_status_db.strget( 87, flog )
        delta_time = abs( getUtcTime() - int( utc_str ) )
    except:
        # do nothing if timestamp is not correct.
        return
   
    time_out = 30 # number of seconds before notification.

    if delta_time >= time_out and p1_no_data_notification == False:
        subject_str = ' -subject "' + subject + ' (slimme meter data niet ontvangen)."'
        messagetext = ' -msgtext "Data uit de slimme meter komt niet meer binnen. Laatste slimme meter telegram ' + str(delta_time)+' seconden geleden ontvangen."'
        messagehtml = ' -msghtml "<p>Data uit de slimme meter komt niet meer binnen.</p><p>Laatste slimme meter telegram <b>' + str(delta_time)+'</b> seconden geleden ontvangen.</p>"'
        if os.system( '/p1mon/scripts/P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' ) > 0:
            flog.error(inspect.stack()[0][3]+" email notificatie P1 data ontbreekt is gefaald.")
        else:
            p1_no_data_notification = True
            flog.warning(inspect.stack()[0][3]+" email verstuurd dat er geen P1 data wordt ontvangen.")

    if delta_time < time_out and p1_no_data_notification == True:
            p1_no_data_notification = False
            subject_str = ' -subject "' + subject + ' (slimme meter data ontvangen.)."'
            messagetext = ' -msgtext "Data uit de slimme meter komt binnen. Laatste slimme meter telegram ' + str(delta_time)+' seconden geleden ontvangen."'
            messagehtml = ' -msghtml "<p>Data uit de slimme meter komt weer binnen.</p><p>Laatste slimme meter telegram <b>' + str(delta_time)+'</b> seconden geleden ontvangen.</p>"'
            if os.system( '/p1mon/scripts/P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' ) > 0:
                flog.error(inspect.stack()[0][3]+" email notificatie P1 data ontbreekt is gefaald.")
            flog.info(inspect.stack()[0][3]+" P1 data komt binnen, email verstuurd.")
    
    #print ( delta_time )

def checkVarLogFolder():
    if os.system( 'sudo /p1mon/scripts/logspacecleaner.sh >/dev/null 2>&1' ) > 0:
        flog.error(inspect.stack()[0][3]+" logspacecleaner.sh gefaald.")

def getCpuTemperature(): #P3 ok
    tfile = open('/sys/class/thermal/thermal_zone0/temp','r')
    temp = float(tfile.read())
    tfile.close()
    tempC = temp/1000
    rt_status_db.strset( str(tempC), 69, flog )

########################################################
# checks there is a new P1 sofware version available   #
# by an https url request to www.ztatz.nl              #
########################################################
def checkForNewP1Version(): #P3 ok
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
        #next_version_timestamp = util.getUtcTime() #TODO

    except Exception as e:
         flog.error(inspect.stack()[0][3]+': ophalen remote versie informatie gefaald -> ' + str(e) )
     
    #flog.setLevel(logging.INFO)


def databaseRam2Disk(): #P3 ok
    os.system("/p1mon/scripts/P1DbCopy.py --allcopy2disk --forcecopy")
    # wait 10 sec to flush data,just to make sure.
    time.sleep(10)

def makeDebugDump(id): #P3 ok
    #print id
    if os.system('sudo /p1mon/scripts/debugdump.sh '+ id ) > 0:
        flog.error(inspect.stack()[0][3]+" debug dump gefaald.")

def makeCustomWwwImport(id): #TODO 2021-03-07: wordt niet meer gebruikt door P1SqlImport.py controleren of deze code er uit kan 
    #print id
    if os.system('sudo /p1mon/scripts/in_ex_custom_www.sh import '+ const.FILE_PREFIX_CUSTOM_UI + id + ".gz" ) > 0:
        flog.error(inspect.stack()[0][3]+" custom www import gefaald.")

def makeCustomWwwExport(id): #P3 ok
    #print id
    if os.system('sudo /p1mon/scripts/in_ex_custom_www.sh export '+id) > 0:
        flog.error(inspect.stack()[0][3]+" custom www export gefaald.")

def makeBackup(): #P3 ok
    #os.system('/p1mon/scripts/P1Backup.py  --forcebackup yes &')
    os.system('/p1mon/scripts/P1Backup.py  --forcebackup  &')

def cleanDownload(): #P1 ok
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

# return how mutch ram is used in pct
def getRamUsedPct(): #P1 ok
    try:
        proc = subprocess.Popen(['/usr/bin/free','-k'], stdout=subprocess.PIPE)
        tmp = proc.stdout.read().decode('utf-8')
        mem_used = tmp.split('\n')[1].split()[3] 
        mem_total = tmp.split('\n')[1].split()[1] 
        #print ( mem_used  )
        #print ( mem_total )
        r = "{:10.1f}".format( (1 - float(mem_used)/float(mem_total) ) *100).strip()
        #print ( r )
        return r
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": Ram gebruik uitlezen gefaald "+str(e))
        return "0"

def setSambaMode(mode):
    flog.info(inspect.stack()[0][3]+" SAMBA mode="+mode)
    if mode == const.FILESHARE_MODE_DATA:
        if os.system('sudo /bin/rm /etc/samba/smb.conf;sudo /bin/ln /etc/samba/smb.conf.data /etc/samba/smb.conf; sudo /usr/sbin/service smbd restart') > 0:
            flog.error(inspect.stack()[0][3]+" SAMBA(bestand delen) alleen data gefaald.")
    if mode == const.FILESHARE_MODE_DEV:
            if os.system('sudo /bin/rm /etc/samba/smb.conf;sudo /bin/ln /etc/samba/smb.conf.dev /etc/samba/smb.conf;sudo /usr/sbin/service smbd restart') > 0:
                flog.error(inspect.stack()[0][3]+" SAMBA(bestand delen) development gefaald.")
    if mode == const.FILESHARE_MODE_UIT:
            if os.system('sudo /usr/sbin/service smbd stop') > 0:
                flog.error(inspect.stack()[0][3]+" SAMBA (bestand delen) service stoppen gefaald.")
      
def getWlanSSID(): #P1 ok
    try:

        p = subprocess.Popen("sudo iwlist wlan0 scan|grep ESSID:| sort | uniq", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = p.stdout.readlines()
        ssid_list=[]
        try:
            for line in output:
                ssid=line.decode('utf-8').split('"')[1]
                #print ( ssid  )
                if "\\x00" not in ssid: 
                    ssid_list.append(ssid)
            ssid_list.sort()
            #print ( ssid_list )
        except Exception as e:
            flog.debug(inspect.stack()[0][3]+": geen wlan0 info gevonden ")
            return
    
        #dump buffer naar bestand.
        try:
            fo = open(const.FILE_WIFISSID+".tmp", "w")
            for x in ssid_list:
                fo.write(x+"\n")
            fo.close
            flog.debug(inspect.stack()[0][3]+": file weggeschreven naar "+const.FILE_WIFISSID+".tmp")
            shutil.move(const.FILE_WIFISSID+".tmp", const.FILE_WIFISSID)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": ssid buffer wegschrijven naar file "+str(e.args[0]))  
        
    
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": Wifi probleem "+str(e))
   
def getHostname(ip): #P3 ok
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception as _e:
        return "onbekend"     
    
def getPublicIpAddress(): #P3 ok
    try:
        url = 'https://api.ipify.org/'
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        return str(response.read().decode('utf-8'))

    except Exception:
        return "onbekend"

def getPythonVersion(): #P3 ok
    try :
        return platform.python_version()
    except Exception:
        return "onbekend"

def getOsInfo(): #P3 ok
    try :
        return platform.platform(aliased=0, terse=0)
    except Exception as _e:
        return "onbekend"

def getInternetStatusByDnsServers(): #P3 ok
	r = False
	li = ["8.8.8.8",\
	"8.8.4.4",\
	"209.244.0.3",\
	"209.244.0.4",\
	"208.67.222.222",\
	"37.235.1.174",\
	"91.239.100.100"\
	]

	random.shuffle(li)
	for i in range(len(li)):
		try :
			hostname = li[i]
			p = subprocess.Popen(["/bin/ping", "-c1", "-W1", hostname], stdout=subprocess.PIPE).stdout.read()
			for item in str(p).split("\n"):
				if "0% packet loss" in item:
					return True
		except Exception as inst:
			print(type(inst))
			print(inst.args)
			print(inst)
		return r	

def getDiskPctUsed(path): #P3 ok
    try:
        r = float(str.replace(str(psutil.disk_usage(path)).split()[3].split('=')[1],')','')) 
        return str(r)
    except Exception as _e:
            #print ( str(e) )
            return "onbekend."

def getUptime(): #P3 Ok
    #flog.setLevel(logging.DEBUG)
    try:
        proc = subprocess.Popen(['/bin/cat','/proc/uptime'], stdout=subprocess.PIPE)
        tmp = proc.stdout.read().decode('utf-8')
        #secpassed = long(tmp.split()[0].split('.',1)[0])
        secpassed = int(tmp.split()[0].split('.',1)[0])
        #secpassed = secpassed + 180000
        days = int(secpassed/86400)
        flog.debug(inspect.stack()[0][3]+" raw secs ="+str(tmp)+" secs. cleaned="+str(secpassed)+" dagen verstreken="+str(days) )
        timestr = ''
        if days > 1:
            timestr =  str(days)+  " dagen "
        if days == 1:
            timestr =  str(days)+  " dag "    
        timestr = timestr+time.strftime("%H:%M:%S", time.gmtime(secpassed) )
        flog.debug(inspect.stack()[0][3]+" uptime is: "+timestr)
        return timestr
    except Exception as e:
            flog.error(inspect.stack()[0][3]+" geen uptime gevonden? error="+str(e))
            return "onbekend."

def saveExit(signum, frame):
    #setFileFlags()
    signal.signal(signal.SIGINT, original_sigint)
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    os.umask( 0o002 )
    flog = fileLogger( const.DIR_FILELOG + prgname + ".log", prgname )   
    flog.setLevel( logging.INFO )
    flog.consoleOutputOn(True)
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    MainProg()