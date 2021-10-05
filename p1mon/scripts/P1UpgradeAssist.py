#!/usr/bin/python3
import argparse
import const
import crypto3
import glob
import inspect
import os.path
import string
import sys
import subprocess
import shutil
import os

from logger import *
from util import setFile2user
from subprocess import check_output
from sqldb import SqlDb1
from util import getUtcTime
from makeLocalTimestamp import makeLocalTimestamp

# P1 version 0.9.11 cleaned the serial database of unprocessed records to avoid double processing.
# P1 version 0.9.13 status.db wordt niet meer gekopieerd.
# P1 version 0.9.15 complete change not backward compatible.

prgname = 'P1UpgradeAssist'
wifi_config_file = '/etc/wpa_supplicant/wpa_supplicant.conf'
usb_list = [ 'sda1', 'sdb1' , 'sdc1' , 'sdd1' ]
P1UAEXT = '.p1ua'
#usb_list = [ 'sda1', 'sdb1' ]
CRYPTO_SEED = "upgradeassist2019"
BACKUP_FILE="/p1mon/var/tmp/custom-www-export-"

def Main(argv): 
    msg = "Start van programma."
    flog.info(msg)
    writeStatus( msg )
    
    parser = argparse.ArgumentParser(description="wegschrijven en lezen van data van externe USB drive/stick voor upgrades.", usage='%(prog)s --save of --restore')
    parser.add_argument('-s', '--save'   , required=False, action="store_true" )
    parser.add_argument('-r,','--restore', required=False, action="store_true" )
    args = parser.parse_args()

    if args.save == True:
        save( )
        sys.exit(0)
    if args.restore == True:
        restore()
        sys.exit(0)
    
    msg = "Gestopt omdat er geen valide parameters zijn opgegeven."
    flog.warning( msg ) 
    writeStatus( msg )
    print ( parser.print_help() )
    exit(1)

def save( ):
    msg = "Veiligstellen van gegevens gestart" 
    flog.info( msg)
    writeStatus( msg )
  
    usb_drive = checkForExistingUsedDrive()

    if usb_drive == None: #No drive found that is previously used.
        usb_drive = findUsableUsbDevice()

    umountUSB( usb_drive )
    if mountUSB( usb_drive ) == 0:
        initUsbFolders()
        ###################
        # wifi data copy: #
        ###################
        #copyFile( wifi_config_file, const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_WIFI , P1UAEXT )
        try:
            with open( wifi_config_file, 'r') as w_file:
                data = w_file.read()
        
            #print ( data )
            result = crypto3.p1Encrypt( str(data), CRYPTO_SEED )
            #print ( result )
       
            _path, file = os.path.split( wifi_config_file )
            wifi_fp = open( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_WIFI + "/" + file + P1UAEXT , "w")
            wifi_fp.write( result )
            wifi_fp.close()

            flog.info( "Wifi data gekopierd naar file: ." + const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_WIFI + "/" + file + P1UAEXT ) 

        except Exception as e:
            flog.error( inspect.stack()[0][3] +  ": probleem met het verwerken van de wifi data: "  + str(e) )
        
        #################
        # database copy #
        #################
        for name in glob.glob( const.DIR_RAMDISK + "/*.db" ):
            #writeStatus( name  )
            #if name == "/p1mon/mnt/ramdisk/status.db":
            #    msg = "status database" + name + " wordt bewust niet gekopieerd."
            #    writeStatus(  msg )
            #    continue
            if name == const.FILE_DB_CONFIG: # vanaf versie 0.9.15 alleen nog het config bestand voor wifi e.d.
                msg = "status database" + name + " wordt gekopieerd."
                flog.info ( inspect.stack()[0][3] + msg )
                writeStatus(  msg )
                copyFile( name, const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_DATA, P1UAEXT )

        ##########################
        # export van sql data    #
        ##########################
        try:
            msg = "Start van SQL export dit duurt op een Pi3 maximaal een paar minuten, geduld aub!"
            flog.info ( inspect.stack()[0][3] + msg )
            writeStatus( msg )
            exportfilename = const.DIR_VAR + const.EXPORT_PREFIX + "-" + const.P1_UPGRADE_ASSIST + ".zip"
            cmd = "/p1mon/scripts/P1SqlExport.py -e " + makeLocalTimestamp() + " -f " + exportfilename + " --rmstatus"
            if os.system( cmd ) > 0:
                msg = "Export door P1SqlExport gefaald."
                flog.error( inspect.stack()[0][3] + msg )
                writeStatus( msg )
            else:    
                copyFile( exportfilename, const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_DATA, P1UAEXT )
                isVerfiedRemoveOfFile ( exportfilename )
                msg = "Export door P1SqlExport succesvol."
                flog.info ( inspect.stack()[0][3] + msg )
                writeStatus( msg )
                
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": P1SqlExport melding:" + str( e.args[0] ) )

        umountUSB( usb_drive )
        msg = "USB device " + str( usb_drive ) + " unmount uitgevoerd."
        flog.info( msg )
        writeStatus( msg )
        msg = "Verwerking gereed."
        writeStatus( msg )
        msg = "Ga naar het systeem menu en stop de Rpi voor het vervangen van het SDHC kaartje."
        writeStatus( msg )
        sys.exit( 0 )
    else:
        msg = "USB device " + str( usb_drive ) + " niet te mounten, gestopt."
        flog.error( msg )
        writeStatus( msg )
        msg = "Verwerking gefaald."
        writeStatus( msg )
        sys.exit(1)

def restore():
    flog.info("Herstellen van gegevens gestart.")
    # check of there is a USB drive with data 
    usb_drive = checkForExistingUsedDrive()
    data_is_processed_flag = False

    if usb_drive != None: # we have a backup 
        flog.info( "Drive " + str(usb_drive) + " bevat mogelijke backup data." )

        # copy data to folder with .p1ua extention. 
        # this is done te make sure we can erease the data on the USB stick.
        # after the succesfull erease the extention is remove

        try:

            # process WIFI config data
            flog.info( "Wifi data verwerken." ) 
            for name in glob.glob( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_WIFI + "/*.p1ua" ):
                
                #print (name)
                 # read en decode 
                with open( name, 'r') as w_file:
                    data = w_file.read()
                #print ('crypted data' ) 
                #print ( data ) 
                result_decrypt = crypto3.p1Decrypt( data, CRYPTO_SEED )
                #print ('result_decrypt' )
                #print ( result_decrypt )

                #print ( 'wifi_config_file')
                #print ( wifi_config_file )

                wifi_fp = open( wifi_config_file , "w")
                wifi_fp.write( result_decrypt )
                wifi_fp.write ('\n')
                wifi_fp.close()
                flog.info( "Wifi bestand " + wifi_config_file + P1UAEXT + " gekopierd." )  
                #sys.exit(0)

                subprocess.run( ['sudo', 'chmod', '0660' , wifi_config_file ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
                flog.info( "Wifi bestand " + wifi_config_file + " verwerkt" )
                
                if isVerfiedRemoveOfFile( name ) == True:
                    flog.info( "Wifi bestand " + name + " is gewist." )
                    data_is_processed_flag =  True # we have processed some data and removed the file to prevent endless loop/reboot


        except Exception as e:
            data_is_processed_flag = False
            flog.error( inspect.stack()[0][3] +  ": probleem met het verwerken van de wifi data: "  + str(e) )

        try:
            flog.info( "Database SQL data verwerken." ) 
            # process Database data
            # if there is a SQL export we don't use the *.db files
            # print ( glob.glob( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_DATA + "/" + const.EXPORT_PREFIX + "*.p1ua") )
            
            for name in glob.glob( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_DATA + "/" + const.EXPORT_PREFIX + "*.p1ua"):
                _path, file = os.path.split( name )
                copyFile( name , const.DIR_FILEDISK  ) # to p1mon normal data folder
                flog.info( "SQL export bestand " + file + " gekopierd." ) 
                if isVerfiedRemoveOfFile ( name ) == True:
                    flog.info( "SQL export bestand " + name + " gewist." ) 
                
                # set file rights
                subprocess.run( ['sudo', 'chmod', '0664' , const.DIR_FILEDISK + file ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
                flog.info( "Data bestand " + const.DIR_FILEDISK + file + " verwerkt." )
                #data_is_processed_flag = True # we have processed some data
            
            
            flog.info( "Database datafiles verwerken." ) 
            for name in glob.glob( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_DATA + "/*db.p1ua" ):
                _path, file = os.path.split( name )
                source = const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_DATA + '/' + file
                copyFile( source , const.DIR_FILEDISK )
                flog.info( "Database bestand " + source + " gekopierd." ) 

                if isVerfiedRemoveOfFile( source ) == True:
                    # rename file
                    filename_no_ext, _file_extension = os.path.splitext( source )
                    _path, source_filename                  = os.path.split( source  )
                    #print ( const.DIR_FILEDISK + source_filename )
                    #print ( const.DIR_FILEDISK + source_filename )
                    #print ( filename_no_ext )
                    _path, dest_filename = os.path.split( filename_no_ext  )
                    #print ( dest_filename )
                    #print ( const.DIR_FILEDISK + dest_filename )
        
                    os.rename ( const.DIR_FILEDISK + source_filename , const.DIR_FILEDISK + dest_filename )
                    # set file rights
                    subprocess.run( ['sudo', 'chmod', '0664' , const.DIR_FILEDISK + dest_filename ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
                    flog.info( "Data bestand " + const.DIR_FILEDISK + dest_filename + " verwerkt." )
                    data_is_processed_flag = True # we have processed some data

        except Exception as e:
            flog.error( inspect.stack()[0][3] +  ": probleem met het verwerken van de database data: "  + str(e) )
            data_is_processed_flag = False


        umountUSB( usb_drive )
   
    if data_is_processed_flag == False:
        flog.info( "Geen data gevonden op de USB drive(s) niets uitgevoerd." )   
    else:

        flog.info( "cron jobs worden aangemaakt uit de database." )
        # const.FILE_DB_CONFIG split for filename
        _head,tail = os.path.split( const.FILE_DB_CONFIG ) 
        copyFile( const.DIR_FILEDISK + tail, const.DIR_RAMDISK ) #disk to ram, scripts uses ram location
        
        if os.system('sudo -u p1mon /p1mon/scripts/P1Scheduler.py') > 0:
            flog.error(inspect.stack()[0][3]+" cron jobs update gefaald.")
        time.sleep(2)

        flog.info( "Filesysteem wordt vergroot naar de maximale ruimte van de SDHC kaart." )
        _cp = subprocess.run( [ 'sudo raspi-config --expand-rootfs' ], shell=True, check=True )
        #print( _cp.stdout )
        #print( _cp.stderr )
        #print( _cp.returncode )
        time.sleep( 2 )

        ############################################################################
        # make a (possible empty) api tokens file. this is needed if the p1mon_443 #
        # file exist nginx fails if the token file is missing. This also makes     #
        # sure that nginx is reloaded or restarted if it is not running            #
        ############################################################################
        if os.system('sudo -u p1mon /p1mon/scripts/P1NginxConfig.py --apitokens' ) > 0:
            msg = "Nginx API tokens update gefaald."
            flog.error( inspect.stack()[0][3] + ": " + msg )

        if os.system('sudo -u p1mon /p1mon/scripts/P1NginxConfig.py --gateway' ) > 0:
            msg = "Nginx gateway update gefaald."
            flog.error( inspect.stack()[0][3] + ": " + msg )

        flog.info( "file system sync uitvoeren." )
        if os.system('sudo sync' ) > 0:
                flog.warning(inspect.stack()[0][3]+" file system sync gefaald.")


        flog.info( "Data herstelt vanaf de USB drive. Er wordt een reboot uitgevoerd." )
        time.sleep( 5 )
        subprocess.run( ['sudo', '/sbin/reboot' ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        time.sleep( 30 ) # failsave to make sure the reboot is done and no other scripts are started. 
    
# False is not removed, True file is removed 
def isVerfiedRemoveOfFile( filename ):
    try:
        if os.path.isfile (filename) == False:
            return True # only do work when there is a file
    except Exception as _e: 
        pass
    try:
        os.remove( filename )
        if os.path.isfile (filename):
            return False
    except Exception as e:
        flog.warning('isVerfiedRemoveOfFile: Wissen van file probleem ' + str( e ) )
        return False
    return True

def writeStatus( msg ):
    try:
        fp = open( const.FILE_UPGRADE_ASSIST_STATUS , "a")
        t=time.localtime()
        fp.write( "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + " " + msg + '\n' )
        fp.close()
    except Exception as e:
        flog.error( "status file schrijf fout: " + str(e) )

def findUsableUsbDevice():
    for usb in usb_list:
        umountUSB ( usb )  #failsave unmount when there is still a mount lingering
        if mountUSB( usb ) == 0:
            # check if this is a valid destination.
            # first check if this is image backup, if so skip.
            flog.debug( "Controle op valide USB device gestart voor device " + str( usb ) )
            isImageDrive = False
            for name in glob.glob( const.DIR_UPGRADE_ASSIST_USB_MOUNT + "/*" ):
                if name == const.DIR_UPGRADE_ASSIST_USB_MOUNT + '/bootcode.bin' or name == const.DIR_UPGRADE_ASSIST_USB_MOUNT + '/kernel.img':
                    isImageDrive = True
                    break
            if isImageDrive == True:
                msg =  "USB device " + str( usb ) + " is een image device die niet kan worden gebruikt."
                flog.info( msg )
                writeStatus( msg )
                continue # try next device
            else:
                return usb
    return None 

def initUsbFolders():
    # found a device
    # check on folders and make them if the do not exits.
    try:
        os.mkdir( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST )
        msg = "folder " + const.DIR_UPGRADE_ASSIST_USB_MOUNT+const.DIR_UPGRADE_ASSIST + " bestaat niet aangemaakt."
        flog.info( msg )
        writeStatus( msg )
    except FileExistsError:
        msg = "folder " + const.DIR_UPGRADE_ASSIST_USB_MOUNT+const.DIR_UPGRADE_ASSIST + " bestaat al niet aangemaakt."
        flog.info( msg )
        writeStatus( msg )

    try:
        os.mkdir( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_DATA )
        msg = "folder " + const.DIR_UPGRADE_ASSIST_USB_MOUNT+const.DIR_UPGRADE_ASSIST_DATA + " bestaat niet aangemaakt." 
        flog.info( msg )
        writeStatus( msg )
    except FileExistsError:
        msg = "folder " + const.DIR_UPGRADE_ASSIST_USB_MOUNT+const.DIR_UPGRADE_ASSIST_DATA + " bestaat al niet aangemaakt."
        flog.info( msg )
        writeStatus( msg )
           
    try:
        os.mkdir( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST_WIFI )
        msg = "folder " + const.DIR_UPGRADE_ASSIST_USB_MOUNT+const.DIR_UPGRADE_ASSIST_WIFI + " bestaat niet aangemaakt."
        flog.info( msg )
        writeStatus( msg )
    except FileExistsError:
        msg = "folder " + const.DIR_UPGRADE_ASSIST_USB_MOUNT+const.DIR_UPGRADE_ASSIST_WIFI + " bestaat al niet aangemaakt."
        flog.info( msg )
        writeStatus( msg )

# check if one of the drives has the root folder /p1monitor
def checkForExistingUsedDrive():
    for usb in usb_list:
        msg = "Controle op eerder gebruikt drive " + str (usb) + " gestart."
        flog.info( msg )
        writeStatus( msg )
        umountUSB ( usb )  #failsave unmount when there is still a mount lingering
        if mountUSB( usb ) == 0:
            if os.path.isdir( const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_UPGRADE_ASSIST ):
                msg = "Folder " + const.DIR_UPGRADE_ASSIST + " bestaat op device " + str( usb )
                flog.info( msg )
                writeStatus( msg )
                return usb
    return None

def copyFile(sourcefile, destination , ext='' ):
    
    #print ( destination )
    #print ( file )

    try:
        _path, file = os.path.split( sourcefile )
        dest = os.path.normpath( destination + '/' + file + ext )
        shutil.copy2( sourcefile, dest ) 
        #setFile2user(destinationfolder + file, 'p1mon')
        msg = sourcefile + " naar " + dest + " gekopieerd."
        flog.info(inspect.stack()[0][3]+": " + msg)
        writeStatus( msg )
    except Exception as e:
        msg = ": kopie " + sourcefile + " naar " + dest + " fout: " + str(e)
        flog.error(inspect.stack()[0][3] +  msg )
        writeStatus( msg )

def umountUSB( device ):
    try:
        flog.debug('start van unmount van usb drive/stick ' + str( device ) )
        status = subprocess.run( ['sudo', 'umount', const.DIR_UPGRADE_ASSIST_USB_MOUNT ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        #flog.debug( "umountUSB return status: " + str(status) )
        #print( status.returncode )
        return int( status.returncode )
    except Exception as e:
        msg = ": unmount gefaald van " + const.DIR_UPGRADE_ASSIST_USB_MOUNT + " " + str(e)
        flog.error(inspect.stack()[0][3] + msg )
        writeStatus( msg )
        return 1

def mountUSB( device ):
    try:
        flog.debug('start van mount van usb drive/stick ' + str( device ) )
        dev_str = '/dev/' + str( device )
        status = subprocess.run( ['sudo', 'mount', '-t', 'vfat', '-o', 'uid=p1mon,gid=p1mon', dev_str, const.DIR_UPGRADE_ASSIST_USB_MOUNT ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        flog.debug( "mountUSB return status: " + str(status) )
        #print( status.returncode  )
        return int( status.returncode )
    except Exception as e:
        msg = ": mount van USB gefaald " + str(e)
        flog.error(inspect.stack()[0][3] + msg )
        writeStatus( msg )
        return 1

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG+prgname+".log"
        setFile2user( logfile, 'p1mon' )
        flog = fileLogger( logfile, prgname )
        #### aanpassen bij productie
        flog.setLevel( logging.INFO )
        flog.consoleOutputOn( True )
        status_fp = open( const.FILE_UPGRADE_ASSIST_STATUS , "w")
        subprocess.run( ['sudo', 'chmod', '0666' , const.FILE_UPGRADE_ASSIST_STATUS ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        status_fp.close()

    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit( 1 ) #  error: no logging check file rights

    Main( sys.argv[1:] )

