####################################################################
# shared lib for wifi functions                                    #
# !!! TODO migrate other scripts to this lib.                      #
####################################################################

import inspect
import subprocess
import shutil

WPA_SUPPLICANT_CONF_FILEPATH = '/etc/wpa_supplicant/wpa_supplicant.conf'

################################################################
# xxxxxxxxx                         #
################################################################
def list_wifi_ssid( flog=None, output_path=None ): #180ok
    
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
            flog.debug( inspect.stack()[0][3]+": geen wlan0 info gevonden ")
            return
    
        # write buffer to file.
        if output_path != None:
            try:
                fo = open( output_path + ".tmp", "w" )
                for x in ssid_list:
                    fo.write( x +"\n" )
                fo.close
                flog.debug( inspect.stack()[0][3]+": file weggeschreven naar " + output_path + ".tmp" )
                shutil.move( output_path + ".tmp", output_path)
            except Exception as e:
                flog.error( inspect.stack()[0][3]+": ssid buffer wegschrijven naar file "+str(e.args[0]) )

    except Exception as e:
        flog.error( inspect.stack()[0][3]+": Wifi probleem " + str(e) )