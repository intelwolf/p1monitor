# run manual with ./P1SetWifi

import base64
import const
import crypto3
import sys
import inspect
import network_lib
#import getopt
import logger
import subprocess
import argparse
import util
import time
import os
import sqldb
import process_lib

prgname                     = 'P1SetWifi'
SERVICE                     = '/usr/sbin/service'
WPA_SUPPLICANT_CONFIG_FILE  = '/etc/wpa_supplicant/wpa_supplicant.conf'
WPA_SUPPLICANT_CONFIG       = '/etc/wpa_supplicant/'

config_db     = sqldb.configDB()
rt_status_db  = sqldb.rtStatusDb()

def setWpaSupplicantConfigFileRights():
    cmd_str = "/usr/bin/sudo chmod o+w " + WPA_SUPPLICANT_CONFIG +"; /usr/bin/sudo /usr/bin/touch " + WPA_SUPPLICANT_CONFIG_FILE + " ;/usr/bin/sudo /bin/chmod 660 "+WPA_SUPPLICANT_CONFIG_FILE+";/usr/bin/sudo /bin/chown p1mon:p1mon "+WPA_SUPPLICANT_CONFIG_FILE
    try:
        flog.debug(inspect.stack()[0][3]+": commando: "+cmd_str)
        _p = subprocess.Popen(cmd_str,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        #return_value=str(p.stdout.read())
    except Exception as _e:
        flog.info(inspect.stack()[0][3]+": wifi config file ("+WPA_SUPPLICANT_CONFIG_FILE+") niet wijzigen.")
        sys.exit(1) 
    time.sleep ( 1 ) # wait for completion.

def writeWpaSupplicantConfig(essid, psk):

    #print lines
    try:
        #os.system('/usr/bin/sudo rm '+ WPA_SUPPLICANT_CONFIG_FILE ) 1.8.0 upgrade
        process_lib.run_process( 
            cms_str='/usr/bin/sudo rm '+ WPA_SUPPLICANT_CONFIG_FILE,
            use_shell=True,
            give_return_value=True, 
            flog=flog 
        )

        # set file rights temporary to write file
        setWpaSupplicantConfigFileRights()

        fp = open(WPA_SUPPLICANT_CONFIG_FILE, 'w')
        fp.write('###############################\n')
        fp.write('# Gegenereerd door P1 monitor.#\n')
        fp.write('# op '+util.mkLocalTimeString()+'      #\n')
        fp.write('###############################\n')
        fp.write('country=NL\n')
        fp.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
        fp.write('update_config=1\n')
        fp.write('network={\n')
        fp.write('    scan_ssid=1\n')
        fp.write('    ssid="' + str(essid) + '"\n')
        fp.write('    psk="'  + psk.decode('utf-8') + '"\n')
        fp.write('}\n')
        fp.close()

        #restartWpaSupplicant()

    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": wifi config file schrijf fout, gestopt("+WPA_SUPPLICANT_CONFIG_FILE+") melding:"+str(e.args))
        sys.exit(1)    

def reconfigureWifi():
    cmd_str = "/usr/bin/sudo /sbin/wpa_cli -i wlan0 reconnect; /usr/bin/sudo /sbin/wpa_cli -i wlan0 reconfigure &"
    try:
        flog.debug(inspect.stack()[0][3]+": commando: "+cmd_str)
        _p = subprocess.Popen(cmd_str,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        #return_value=str(p.stdout.read())
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": wifi config file melding:"+str(e.args))
 
def stopWifi():
    cmd_str = "/usr/bin/sudo /sbin/wpa_cli -i wlan0 disconnect"
    try:
        flog.debug(inspect.stack()[0][3]+": commando: "+cmd_str)
        p = subprocess.Popen(cmd_str,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        flog.info(inspect.stack()[0][3]+": wifi netwerk gestopt.")
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": wifi gestopt fout, melding:"+str(e.args))

def Main(argv): 
    global config_db
    flog.info("Start van programma.")

    parser = argparse.ArgumentParser(description="Set het wpa wachtwoord voor een essid ESSID (\"MIJN WIFI\")")
    parser.add_argument('-e', '--essid', required=False)
    parser.add_argument('-k', '--key',   required=False)
    args = parser.parse_args()
    essid   = args.essid
    key     = args.key
    
    #try to read from database
    if ( essid == None or key == None ): 
        flog.info(inspect.stack()[0][3]+": Lees essid en wpa key uit database.")
         # open van config database
        try:    
            config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

        # open van status database
        try:    
            rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)     
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
            sys.exit(1)
        flog.info(inspect.stack()[0][3]+": database tabel: "+const.DB_STATUS_TAB+" succesvol geopend.")

        sqlstr = "select id, parameter from "+const.DB_CONFIG_TAB+" where id >=11 and id <=12 order by id asc"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        wifi_config=config_db.select_rec(sqlstr) 
        essid   	= str(wifi_config[0][1])
        crypto_key	= str(wifi_config[1][1])
        flog.debug(inspect.stack()[0][3]+": essid = "+essid+" crypto key = "+crypto_key)

        key = base64.standard_b64decode( crypto3.p1Decrypt(crypto_key,'wifipw') )

        flog.debug( inspect.stack()[0][3]+": decrypted key = " + key.decode( 'utf-8' ) )

        flog.info(inspect.stack()[0][3]+": Essid ("+essid+") en key uit database gehaald ")
        
    flog.info(inspect.stack()[0][3]+": ESSID = "+essid)
    if ( len(key.strip()) == 0 or len(essid.strip()) == 0 ):
        flog.info(inspect.stack()[0][3]+": ESSID en/of PSK ontbreekt, wifi wordt gestopt. ")
        stopWifi()
        sys.exit(0) 

    # change wpa_supplicant file
    writeWpaSupplicantConfig( essid, key )
    reconfigureWifi()

    #flog.info( inspect.stack()[0][3]+": wlan0 wordt herstart.")
    #network_lib.restart_network_device( device='wlan0', flog=flog )
    #time.sleep( 10 )

    sec_count = 0
    flog.debug(inspect.stack()[0][3]+": start van ip actief controle.")
    while (sec_count < 180):
    # try for maximum of 3 minutes (sleep is 5)
         buf = network_lib.get_nic_info( 'wlan0' )
         if buf['ip4'] != None:
             flog.info(inspect.stack()[0][3]+": Wifi actief op IP adres "+buf['ip4'])
             rt_status_db.strset(buf['ip4'],42,flog)
             sys.exit(0) # up and running wifi
         sec_count+=5
         time.sleep(5)
         flog.debug(inspect.stack()[0][3]+": wacht op activering van wifi voor "+str(sec_count)+" seconden.")
    flog.warning(inspect.stack()[0][3]+": Wifi is niet actief.") 
    rt_status_db.strset('onbekend',42,flog)

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG+prgname + ".log"
        util.setFile2user( logfile,'p1mon')
        flog = logger.fileLogger( logfile,prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(1)

    Main(sys.argv[1:])       
