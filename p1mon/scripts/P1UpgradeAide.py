# run manual with ./P1UpgradeAide

import argparse
import const
import crontab_lib
import crypto3
import crypto_lib
import filesystem_lib
import glob
import inspect
import logger
import letsencrypt_lib
import network_lib
import nginx_lib
import os
import pathlib
import pwd
import random
import string
import sqlite_lib
import sqldb
import sys
import subprocess
import shutil
import time
import util
import usb_drive_lib
import wifi_lib
import process_lib

prgname = 'P1UpgradeAide'

CRYPTO_SEED        = "c2f98c974dd733342e43d414e6779e4e12186bc1a5d54dc90c23e6ad"
AIDE_EXT_IGNORE    = '.ignore'
AIDE_EXT_DONE      = '.done'
AIDE_EXT_RESTORE   = '.restore'
AIDE_EXT_BUSY      = '.busy'
AIDE_EXT_CRYPTO    = '.crypto'
AIDE_EXT_VERIFY    = '.verify'

AIDE_DIR_DATABASE           = '/db'
AIDE_DIR_WIFI               = '/wifi'
AIDE_DIR_CRONTAB            = '/cron'
AIDE_DIR_NGINX              = '/nginx'
#AIDE_DIR_NGINX_SITES_ENABELD = '/sites-enabled'
#AIDE_DIR_NGINX_CONFD        = '/conf.d'
AIDE_DIR_DHCP               = '/dhcp'
AIDE_DIR_DNS                = '/dns'
AIDE_DIR_LENCRYPT           = '/letsencrypt'
AIDE_DIR_WWW                = '/www'

AIDE_LETSENCRYPT_FILE       = 'le-config'
AIDE_NGINX_CONFIG           = 'nginx_config'

AIDE_MIN_USB_SPACE_MB = 500 # the minium of free space needed in MB.

FILES_NGINX_CRYPTO = [ nginx_lib.APIKEYFILE ]
FILES_NGINX_NON_CRYPTO = [ nginx_lib.P80FILE, nginx_lib.P443FILE, nginx_lib.DIVMAPSFILE ]

def Main( argv ):
    my_pid = os.getpid()

    msg = "Start van programma met process id " + str(my_pid) + " en als user -> " + pwd.getpwuid( os.getuid() ).pw_name
    flog.info( msg )
    write_status_to_file( msg )

    parser = argparse.ArgumentParser(description="wegschrijven en lezen van data van externe USB drive/stick voor upgrades.",)
    parser.add_argument('-s', '--save',
        required=False,
        action="store_true",
        help="Save een kopie van alle data en configuratie van het SDHC kaartje naar de USB stick."
        )
    parser.add_argument('-r','--restore',
        required=False,
        action="store_true",
        help="Restore de data en configuratie van USB stick naar het SDHC kaartje."
        )
    parser.add_argument('-u','--unmount',
        required=False,
        action="store_true",
        help="Unmount mount point." + const.DIR_USB_MOUNT
        )
    parser.add_argument('-m','--mount',
        required=False,
        action="store_true",
        help="mount mount point." + const.DIR_USB_MOUNT
        )
    parser.add_argument( '-b', '--reboot',
        required=False,
        action="store_true",
        help="reboot de Rpi na een restore. standaard staat deze optie uit." )

    args = parser.parse_args()

    if args.save == True:
        save( )
        sys.exit(0)
    if args.restore == True:
        restore( args=args )
        sys.exit(0)
    if args.unmount == True:
        unmount()
        sys.exit(0)
    if args.mount == True:
        mount()
        sys.exit(0)

    msg = "Gestopt omdat er geen valide parameters zijn opgegeven."
    flog.warning( msg ) 
    write_status_to_file( msg )
    sys.exit( 1 )


def restore( args=None ):

    flog.info ( inspect.stack()[0][3] + ": Herstellen van gegevens gestart." )

    try:

        #################################################
        # check for a USB drive that is used previously #
        # if so use that drive                          #
        #################################################
        usb_device = check_for_used_aide_drive( flog=flog )

        path_base = const.DIR_USB_MOUNT + const.DIR_USB_ROOT + const.DIR_UPGRADE_AIDE

        base_usb_pathfile = None
        for folder_name in glob.glob( path_base + "/*" + AIDE_EXT_RESTORE ):
            base_usb_pathfile = folder_name
            break  # only use one.

        if base_usb_pathfile == None:
            flog.info ( inspect.stack()[0][3] + " geen folder gevonden op de drive. gestopt" )
            sys.exit( 0 )

        flog.info ( inspect.stack()[0][3] + ": USB path " + str ( base_usb_pathfile ) + " gevonden." )

        # change the restore folder to busy
        # this is import to make sure we run this only once.
        rename_pathfile = base_usb_pathfile.rpartition('.')[0] + AIDE_EXT_BUSY
        os.rename( base_usb_pathfile, rename_pathfile )
        flog.info( inspect.stack()[0][3] + ": folder " + base_usb_pathfile + " gewijzigt naar " +  rename_pathfile )
        base_usb_pathfile = rename_pathfile

        flog.info ( inspect.stack()[0][3] + ": USB path " + str ( base_usb_pathfile ) + " wordt gebruikt." )

        if not os.path.exists( base_usb_pathfile ):
            raise Exception( "restore naar busy folder naam aanpassing gefaald." )

        # step 1: copy the database files from USB to RAM & DISK.
        db_usb_path_file = base_usb_pathfile + AIDE_DIR_DATABASE

        for source_file_name in glob.glob( db_usb_path_file + "/*.db" ):
            
            destination_file_data = const.DIR_FILEDISK + pathlib.PurePath( source_file_name ).name
            destination_file_ram  = const.DIR_RAMDISK + pathlib.PurePath( source_file_name ).name
            try:
                shutil.copy2( source_file_name, destination_file_data )
                flog.info ( inspect.stack()[0][3] + ": bestand " + str( source_file_name ) + " gekopieerd naar " + destination_file_data )
            except Exception as e:
                 flog.warning ( inspect.stack()[0][3] + ": database bestand " + str( source_file_name ) + " naar sdhc probleem -> " + str(e) )

            try:
                shutil.copy2( source_file_name, destination_file_ram )
                flog.info ( inspect.stack()[0][3] + ": bestand " + str( source_file_name ) + " gekopieerd naar " + destination_file_ram )
            except Exception as e:
                 flog.warning ( inspect.stack()[0][3] + ": database bestand " + str( source_file_name ) + " naar ram probleem -> " + str(e) )

        # step 1.1 restore the socat config, when enabled.
        socat_restore()

        # step 2 copy wifi config files
        try:
            wifi_usb_pathfile = base_usb_pathfile + AIDE_DIR_WIFI
            wifi_pathfile = wifi_usb_pathfile + "/" + pathlib.PurePath( wifi_lib.WPA_SUPPLICANT_CONF_FILEPATH ).name + AIDE_EXT_CRYPTO

            #raise Exception( "TEST" )

            if os.path.exists( wifi_pathfile ):

                #print( "#", wifi_pathfile )
                copy_and_crypto_file(
                    mode='decrypt',
                    source_pathfile=wifi_pathfile, 
                    destination_pathfile=wifi_lib.WPA_SUPPLICANT_CONF_FILEPATH,
                    flog=flog,
                    cryptoseed=CRYPTO_SEED,
                )

                flog.info( inspect.stack()[0][3] + ": bestand " + pathlib.PurePath( wifi_pathfile ).name + " decrypted en gekopieerd naar " + wifi_lib.WPA_SUPPLICANT_CONF_FILEPATH )

            else:
                flog.info( inspect.stack()[0][3] + ": Geen wifi configuratie gevonden -> " +  wifi_pathfile )

        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": Probleem met WiFi configuratie, probeer dit te herstellen door de WiFi opnieuw in te stellen -> " + str(e) )

        # step 3 copy DHCP config files
        try:
            #raise Exception( "TEST" )
            dhcp_usb_pathfile = base_usb_pathfile + AIDE_DIR_DHCP + "/" + pathlib.PurePath( network_lib.DHCPCONFIG ).name 
            filesystem_lib.move_file_for_root_user( source_filepath=dhcp_usb_pathfile, destination_filepath=network_lib.DHCPCONFIG, permissions='644', copyflag=True )
            flog.info( inspect.stack()[0][3] + ": DHCP configuratie " + pathlib.PurePath( dhcp_usb_pathfile ).name + " gekopieerd." )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": Probleem met DHCP configuratie, probeer dit te herstellen door het netwerk opnieuw in te stellen -> " + str(e) )

        # step 4 copy DNS config files
        try:
            #raise Exception( "TEST" )
            dns_usb_pathfile = base_usb_pathfile + AIDE_DIR_DNS+ "/" + pathlib.PurePath( network_lib.RESOLVCONFIG ).name
            #print ( dns_usb_pathfile , network_lib.DHCPCONFIG,)
            filesystem_lib.move_file_for_root_user( source_filepath=dns_usb_pathfile, destination_filepath=network_lib.RESOLVCONFIG, permissions='644', copyflag=True )
            flog.info( inspect.stack()[0][3] + ": DNS configuratie " + pathlib.PurePath( dns_usb_pathfile ).name + " gekopieerd." )

        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": probleem met DNS configuratie, probeer dit te herstellen door het netwerk opnieuw in te stellen -> " + str(e) )
           
        # step 5 copy crontab config files
        try:

            crontab_usb_pathfile = base_usb_pathfile + AIDE_DIR_CRONTAB + "/" + pathlib.PurePath( crontab_lib.CRONTAB_TMP_FILE ).name
            flog.debug ( inspect.stack()[0][3] +": cron USB file = " + crontab_usb_pathfile )
            status_text, status_code = crontab_lib.restore_from_file( source_pathfile=crontab_usb_pathfile, flog=flog )
            
            if status_code != 0:
                raise Exception( status_text )

            flog.info( inspect.stack()[0][3] + ": crontab configuratie " + pathlib.PurePath( crontab_usb_pathfile ).name + " gekopieerd." )

        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": probleem met crontab configuratie -> " + str(e) )


        # step 6 let's encrypt restore
        # this must be done for the NGINX restore
        try:
            le_usb_filepath = base_usb_pathfile + AIDE_DIR_LENCRYPT  + '/' + AIDE_LETSENCRYPT_FILE + AIDE_EXT_CRYPTO 
            tmp_ram_file = generate_temp_ram_filename() + '.' + prgname 

            flog.debug ( "source file = " + le_usb_filepath )
            if not os.path.exists( le_usb_filepath ):
                 raise Exception( 'geen data gevonden.' )

            # decrypt the tar file
            c = crypto_lib.P1monCrypto()
            c.init( flog=flog )
            c.set_symmetric_key( seed=CRYPTO_SEED )
            c.decrypt_file( source_pathfile=le_usb_filepath , destination_pathfile=tmp_ram_file )

            flog.info( inspect.stack()[0][3] + ": Lets Encrypt bestand succesvol decrypted.") 

            copy_and_decompress( source_pathfile=tmp_ram_file, flog=flog, gzip=False )

            flog.info( inspect.stack()[0][3] + ": Lets Encrypt is hersteld.")

        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": probleem met Lets Encrypt -> " + str(e) )

        # remove tmp file
        remove_file( pathfile=tmp_ram_file, flog=flog )

        # step 7 restore nginx config files
        # warning nginx is dependent on Let's Encrypt.
        try:
            tmp_ram_file = generate_temp_ram_filename() + '.' + prgname 
            nginx_usb_filepath = base_usb_pathfile + AIDE_DIR_NGINX + '/' +AIDE_NGINX_CONFIG + AIDE_EXT_CRYPTO

            if not os.path.exists( nginx_usb_filepath ):
                 raise Exception( 'geen NGINX configuartie gevonden!' )

            flog.debug ( inspect.stack()[0][3] +": NGINX crypto bestand " + nginx_usb_filepath + " gevonden.")

            # decrypt the tar file
            c = crypto_lib.P1monCrypto()
            c.init( flog=flog )
            c.set_symmetric_key( seed=CRYPTO_SEED )
            c.decrypt_file( source_pathfile=nginx_usb_filepath , destination_pathfile=tmp_ram_file )

            flog.info( inspect.stack()[0][3] + ": NGINX bestand succesvol decrypted.")

            copy_and_decompress( source_pathfile=tmp_ram_file, flog=flog, gzip=False )

            flog.info( inspect.stack()[0][3] + ": wegschrijven van NGINX configuratie succesvol.")

            # sync the filesystem, this could speed up the unmount 
            flog.info( inspect.stack()[0][3] + ": filesystem buffers update. Dit kan enkele seconden (10-120) duren, geduld aub." )
            filesystem_lib.file_system_sync()

            cmd = "/usr/bin/sudo nginx -t "
            proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
            stdout, stderr  = proc.communicate()
            returncode = int( proc.wait( timeout=60 ) )

            if returncode != 0:
                flog.warning( inspect.stack()[0][3] +": NGINX stdout " + str(stdout) )
                flog.warning( inspect.stack()[0][3] +": NGINX stderr " + str(stderr) )
                raise Exception( 'NGINX configuratie lijkt niet correct!' )
            else:
                flog.info( inspect.stack()[0][3] + ": NGINX configuratie is getest is correct.")

        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": probleem met NGINX configuratie -> " + str(e) )

        # step 8 restore UI-web custom data
        try:
            www_custom_usb_filepath = base_usb_pathfile  + AIDE_DIR_WWW + '/' + pathlib.PurePath( const.DIR_WWW_CUSTOM ).name + ".gz"
            
            flog.debug ( "source file = " + www_custom_usb_filepath )
            if not os.path.exists( www_custom_usb_filepath ):
                 raise Exception( 'geen eigen data gevonden.' )

            copy_and_decompress( source_pathfile=www_custom_usb_filepath, flog=flog, gzip=True )

            flog.info( inspect.stack()[0][3] + ": eigen gemaakte webpagina's zijn hersteld.")

        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": probleem met eigen gemaakte webpagina's -> " + str(e) )

 




        # change the restore folder to done status.
        rename_pathfile = base_usb_pathfile.rpartition('.')[0] + AIDE_EXT_DONE
        os.rename( base_usb_pathfile,  rename_pathfile )
        flog.info( inspect.stack()[0][3] + ": folder " + base_usb_pathfile + " gewijzigt naar " +  rename_pathfile )

        # sync the filesystem, this could speed up the unmount 
        flog.info( inspect.stack()[0][3] + ": filesystem buffers update. Dit kan enkele seconden (10-120) duren, geduld aub." )
        filesystem_lib.file_system_sync()

        # step 9 unmount USB
        flog.info( inspect.stack()[0][3] + ": Drive wordt un-mounted. Dit kan tot 60 seconden in beslag nemen. Geduld aub." )
        status_text, status_code = usb_drive_lib.unmount_device( flog=flog, timeout=60 )
        if status_code != 0:
            raise Exception( "USB drive is niet te un-mounten, dit duidt op een drive probleem." )

        try:
            filesystem_lib.expand_rootfs()
        except Exception as e:
            flog.warning( inspect.stack()[0][3] +": probleem met het vergroten van het filesysteem -> " + str(e) )

        flog.info( inspect.stack()[0][3] +"Data herstelt vanaf de USB drive." )

        if args.reboot == True:
           
            flog.info( inspect.stack()[0][3] +" Reboot van Raspberry Pi wordt uitgevoerd." )
            time.sleep( 5 )
            try :
                cmd_str = '/usr/bin/sudo /sbin/reboot'
                p = subprocess.Popen( cmd_str, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True )
                _p_status = p.wait( timeout=30 )
            except Exception as _e:
                raise Exception( "Reboot niet gelukt, voer deze met de hand uit." )

    except Exception as e:
        flog.error( str(e) )
        flog.critical( inspect.stack()[0][3] + ": Verwerking gefaald en gestopt!" ) 
        sys.exit(1)


#######################################
# make folder with restore data       #
#######################################
def save( ):

    msg = "Veiligstellen van gegevens gestart." 
    flog.info( msg)
    write_status_to_file( msg )
    
    #print( usb_drive_lib.mount_device( flog=flog ) )
    #print( check_for_used_aide_drive( flog=flog ) )
    #check_for_used_drive( device_list=USB_LIST, flog=None )
    #print( find_usable_usb_device( flog=flog ) )
    #sys.exit()

    try:

        #################################################
        # check for a USB drive that is used previously #
        # if so use that drive                          #
        #################################################
        usb_device = check_for_used_aide_drive( flog=flog )

        if usb_device == None: #No drive found that is previously used.
            usb_device = find_usable_usb_device( flog=flog )
        else:
            msg = "Eerder gevonden drive " + str( usb_device ) + " gevonden."
            flog.info( msg)
            write_status_to_file( msg )

        if usb_device == None: # no drive found.
            msg = "Geen geschikte USB drive gevonden."
            raise Exception( msg )

        # failsave unmount when there is still a mount lingering
        status_text, status_code = usb_drive_lib.unmount_device( flog=flog )
        if status_code != 0:
            msg = "USB drive is niet te un-mounten, dit duidt op een drive probleem."
            raise Exception( msg )

        # mount the drive that is found.
        status_text, status_code = usb_drive_lib.mount_device( device=usb_device, flog=flog )

        if status_code != 0:
            msg = "USB device " + str( usb_device ) + " niet te mounten, gestopt. reden -> " + str( status_text )
            raise Exception( msg )

        path_base = const.DIR_USB_MOUNT + const.DIR_USB_ROOT + const.DIR_UPGRADE_AIDE

        # check for space on the usb drive. If there is not enough space remove 
        # older restore folders with the .ingnore or .done extentions.
        sizedata = filesystem_lib.filepath_use( usb_drive_lib.MOUNTPOINT, unit='M' )
        # check inore files
        if sizedata ['space_free'] < AIDE_MIN_USB_SPACE_MB:
            msg = "Er is minder dan " + str(AIDE_MIN_USB_SPACE_MB) + " MB ruimte op de USB, probeer ruimte te maken."
            write_status_to_file( msg )
            flog.info( msg )
            for folder_name in glob.glob( path_base + "/*" + AIDE_EXT_IGNORE ) + glob.glob( path_base + "/*" + AIDE_EXT_DONE ):
                shutil.rmtree( folder_name, ignore_errors=True )
                msg = "folder " + str(folder_name) + " verwijderd."
                write_status_to_file( msg )
                flog.info( msg )
                # check if there is enough room
                sizedata = filesystem_lib.filepath_use( usb_drive_lib.MOUNTPOINT, unit='M' )
                if sizedata ['space_free'] > AIDE_MIN_USB_SPACE_MB:
                    break # stop when there is enough room.
        
        # check if there is now enough space on the drive
        sizedata = filesystem_lib.filepath_use( usb_drive_lib.MOUNTPOINT, unit='M' )
        if sizedata ['space_free'] < AIDE_MIN_USB_SPACE_MB:
            msg = "onvoldoende ruimte op de drive. Wis bestanden of gebruik een andere drive."
            raise Exception( msg )

        # make the base folder on the drive when it not exists
        os.makedirs( path_base, exist_ok=True )

        # check if base path exits.
        if not os.path.exists( path_base ):
            msg = "folder " + path_base + " kon niet worden aangemaakt"
            raise Exception( msg )

        ###########################################################################
        # Folders have a status:                                                  #
        # done: restore performed                                                 #
        # ignore: ready folder that is not used. There may only be one restore    #
        # folder. When a new restore folder is made existing restore folders will #
        # be renamed to ignore.                                                   #
        # restore: folder that will be used in the next restore action            #
        ###########################################################################

        # step 1: check if there are any folder with the restore extention
        # rename these to .ignore there can only be one :)

        for folder_name in glob.glob( path_base + "/*" + AIDE_EXT_RESTORE ):
            new_folder_name = os.path.splitext( folder_name )[0] + AIDE_EXT_IGNORE 
            os.rename( folder_name , new_folder_name )
            msg = "hernoemen van niet gebruikte restore folder " + folder_name + " naar " + new_folder_name 
            write_status_to_file( msg )
            flog.warning( msg )

        # step 2: create the restore folder.
        # create new restore folder
        t=time.localtime()
        restore_folder_only = "%04d%02d%02d%02d%02d%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + AIDE_EXT_RESTORE
        restore_path_folder = const.DIR_USB_MOUNT + const.DIR_USB_ROOT + const.DIR_UPGRADE_AIDE + "/" + restore_folder_only 
        flog.debug ( "restore_path_folder = " + restore_path_folder )

        # make the base and subfolders
        # the use of sub-folder is te avoid 
        # namespace colisions
        os.makedirs( restore_path_folder, exist_ok=True )
        if not os.path.exists( restore_path_folder ):
            msg = "folder " + restore_path_folder + " kon niet worden aangemaakt"
            raise Exception( msg )

        # make restore subfolders
        restore_path_db = restore_path_folder + AIDE_DIR_DATABASE
        os.makedirs( restore_path_db, exist_ok=True )
        
        restore_path_wifi = restore_path_folder + AIDE_DIR_WIFI 
        os.makedirs( restore_path_wifi, exist_ok=True )

        restore_path_dhcp = restore_path_folder + AIDE_DIR_DHCP
        os.makedirs( restore_path_dhcp, exist_ok=True )

        restore_path_dns = restore_path_folder + AIDE_DIR_DNS 
        os.makedirs( restore_path_dns, exist_ok=True )

        restore_path_cron = restore_path_folder + AIDE_DIR_CRONTAB
        os.makedirs( restore_path_cron, exist_ok=True )

        restore_path_nginx = restore_path_folder + AIDE_DIR_NGINX
        os.makedirs( restore_path_nginx, exist_ok=True )

        restore_path_letsencrypt = restore_path_folder + AIDE_DIR_LENCRYPT
        os.makedirs( restore_path_letsencrypt, exist_ok=True )
        
        restore_path_www = restore_path_folder + AIDE_DIR_WWW
        os.makedirs( restore_path_www, exist_ok=True )

        # step 3: copy the database files from ram to USB
        for file_name in glob.glob( const.DIR_RAMDISK + "/*.db" ):
            destination_file = restore_path_db + "/" + pathlib.PurePath( file_name ).name 
            shutil.copy2( file_name, destination_file )
            flog.debug ( "bestand " + file_name + " gekopieerd naar " + destination_file )
            msg = "bestand " + pathlib.PurePath( file_name ).name + " gekopieerd naar folder " + restore_path_db + " op de usb drive."
            write_status_to_file( msg )
            flog.info( msg )

        # step 4: copy wifi config files
        try:
            destination_filename_wifi = restore_path_wifi + "/" + pathlib.PurePath( wifi_lib.WPA_SUPPLICANT_CONF_FILEPATH ).name + AIDE_EXT_CRYPTO
            copy_and_crypto_file(
                mode='encrypt',
                source_pathfile=wifi_lib.WPA_SUPPLICANT_CONF_FILEPATH, 
                destination_pathfile=destination_filename_wifi,
                flog=flog,
                cryptoseed=CRYPTO_SEED,
                )

            msg = "bestand " + pathlib.PurePath( wifi_lib.WPA_SUPPLICANT_CONF_FILEPATH ).name + " gekopieerd naar folder " + restore_path_wifi + " op de usb drive."
            write_status_to_file( msg )
            flog.info( msg )

        except Exception as e:
            flog.error( "Wifi configuratie niet te kopiëren (" + wifi_lib.WPA_SUPPLICANT_CONF_FILEPATH + ") ->" + str(e) )
            write_status_to_file( str(e) )

            #raise Exception( str(e) )

        # step 5 copy dhcp config file
        destination_file = restore_path_dhcp + "/" + pathlib.PurePath( network_lib.DHCPCONFIG ).name 
        flog.debug ( "source file =" + network_lib.DHCPCONFIG + " destination_file = " + destination_file )
        shutil.copy2( network_lib.DHCPCONFIG, destination_file )
        msg = "bestand " + pathlib.PurePath( network_lib.DHCPCONFIG ).name + " gekopieerd naar folder " + restore_path_dhcp + " op de usb drive."
        write_status_to_file( msg )
        flog.info( msg )

        # step 6 save dns file
        destination_file = restore_path_dns + "/" + pathlib.PurePath( network_lib.RESOLVCONFIG ).name 
        flog.debug ( "source file =" + network_lib.RESOLVCONFIG + " destination_file = " + destination_file )
        shutil.copy2( network_lib.RESOLVCONFIG , destination_file )
        msg = "bestand " + pathlib.PurePath( network_lib.RESOLVCONFIG ).name + " gekopieerd naar folder " + restore_path_dns + " op de usb drive."
        write_status_to_file( msg )
        flog.info( msg )

        # step 7 save crontab file
        try:
            # fail save so there is a least an empty crontab file
            crontab_lib.empty_crontab( flog=flog )

            destination_file = restore_path_cron + "/" + crontab_lib.CRONTAB_TMP_FILE 
            flog.debug ( "cron destination_file = " + destination_file )
            status_text, status_code = crontab_lib.save_to_file( destination_pathfile=destination_file, flog=flog )

            if status_code != 0:
                raise Exception( status_text )
            msg = "crontab voor gebruiker " + pwd.getpwuid( os.getuid() ).pw_name + " gekopieerd naar bestand " + restore_path_cron
            write_status_to_file( msg )
            flog.info( msg )

        except Exception as e:
            write_status_to_file( str(e) )
            raise Exception( 'crontab informatie niet te kopiëren.')

        # step 8 save nginx files
        destination_file = restore_path_nginx + "/" + AIDE_NGINX_CONFIG
        tmp_ram_file = generate_temp_ram_filename() + '.' + prgname 
        save_nginx( destination_pathfile=tmp_ram_file, flog=flog )

        msg = "Let's NGINX folders naar tar file geschreven."
        write_status_to_file( msg )
        flog.info( msg )

        # encrypt the tar file
        c = crypto_lib.P1monCrypto()
        c.init( flog=flog )
        c.set_symmetric_key( seed=CRYPTO_SEED )
        c.encrypt_file( source_pathfile=tmp_ram_file, destination_pathfile=tmp_ram_file+AIDE_EXT_CRYPTO  )

        msg = "NGINX tar file versleuteld."
        write_status_to_file( msg )
        flog.info( msg )

        shutil.copy2( tmp_ram_file + AIDE_EXT_CRYPTO, destination_file + AIDE_EXT_CRYPTO)
        msg = "bestand " + pathlib.PurePath( destination_file ).name + AIDE_EXT_CRYPTO + " versleuteld en gekopieerd naar folder " + restore_path_nginx + " op de usb drive."
        write_status_to_file( msg )
        flog.info( msg )

        # remove tmp files
        remove_file( pathfile=tmp_ram_file + AIDE_EXT_CRYPTO, flog=flog )
        remove_file( pathfile=tmp_ram_file, flog=flog )

        # step 9 save UI-web custom data.
        destination_file = restore_path_www + "/" + pathlib.PurePath( const.DIR_WWW_CUSTOM ).name + ".gz"
        flog.debug ( "source file =" + const.DIR_WWW_CUSTOM + " destination_file = " + destination_file )
        copy_and_compress( source_pathfile=const.DIR_WWW_CUSTOM, destination_pathfile=destination_file, flog=flog )
        msg = "eigen gemaakt webpagina's UI gekopieerd naar bestand " + destination_file
        write_status_to_file( msg )
        flog.info( msg )

        # step 10 let's encrypt save.
        destination_file = restore_path_letsencrypt + '/' + AIDE_LETSENCRYPT_FILE

        tmp_ram_file = generate_temp_ram_filename() + '.' + prgname 
        save_letsencrypt( destination_pathfile=tmp_ram_file, flog=flog )

        msg = "Let's Encrypt folders naar tar file geschreven."
        write_status_to_file( msg )
        flog.info( msg )

        # encrypt the tar file
        c = crypto_lib.P1monCrypto()
        c.init( flog=flog )
        c.set_symmetric_key( seed=CRYPTO_SEED )
        c.encrypt_file( source_pathfile=tmp_ram_file, destination_pathfile=tmp_ram_file + AIDE_EXT_CRYPTO  )

        msg = "Let's Encrypt tar file versleuteld."
        write_status_to_file( msg )
        flog.info( msg )

        shutil.copy2( tmp_ram_file + AIDE_EXT_CRYPTO, destination_file + AIDE_EXT_CRYPTO)
        msg = "bestand " + pathlib.PurePath( destination_file ).name + AIDE_EXT_CRYPTO + " versleuteld en gekopieerd naar folder " + restore_path_letsencrypt + " op de usb drive."
        write_status_to_file( msg )
        flog.info( msg )

        # remove tmp files
        remove_file( pathfile=tmp_ram_file + AIDE_EXT_CRYPTO, flog=flog )
        remove_file( pathfile=tmp_ram_file, flog=flog )

        # sync the filesystem, this could speed up the unmount 
        msg = "Filesystem buffers update. Dit kan enkele seconden (10-120) duren, geduld aub."
        write_status_to_file( msg )
        flog.info( msg )
        filesystem_lib.file_system_sync()

        #######################################
        # verification of data where possible #
        #######################################

        # step 11 verfication
        msg = "Verficatie van database gestart."
        write_status_to_file( msg )
        flog.info( msg )

        tmp_ram_filepath = generate_temp_ram_filename() + AIDE_EXT_VERIFY 
        flog.debug ( "tmp ram filename voor verficatie is  =" + tmp_ram_filepath )

        for db_filename in glob.glob( restore_path_db + "/*.db" ):
            shutil.copy2( db_filename , tmp_ram_filepath )

            db = sqlite_lib.SqliteUtil()
            db.init( db_pathfile=tmp_ram_filepath, flog=flog )
            db.integrity_check()
            msg = "database " + db_filename + " integriteit in orde"
            write_status_to_file( msg )
            flog.info( msg )

            tables = db.list_tables_in_database()
            for table in tables:
                count =  db.count_records( table )
                if int(count) > 0:
                    msg = "tabel " + str(table) + " bevat " + str(count) + " records."
                    write_status_to_file( msg )
                    flog.info( msg )
                else:
                    msg = "tabel " + str(table) + " bevat geen records. Dit kan op een probleem duiden."
                    write_status_to_file( msg )
                    flog.warning ( msg )

            db.close()
        
        # remove tmp file
        remove_file( pathfile=tmp_ram_filepath, flog=flog )
        
        # do space check to inform the user
        try:
            sizedata = filesystem_lib.filepath_use( usb_drive_lib.MOUNTPOINT, unit='M' )
            msg = "USB drive heeft nog " + str(sizedata ['space_free']) + " MB (" + str(sizedata ['pct_free']) + "%) ruimte beschikbaar."
            write_status_to_file( msg )
            flog.info( msg )
        except Exception as e:
            print ( e  )
            flog.debug ( inspect.stack()[0][3] + "drive size check " + str(e) )
            #pass # do nothing on failure

        # step 12 unmount USB
        msg = "Drive wordt un-mounted. Dit kan tot 60 seconden in beslag nemen. Geduld aub."
        write_status_to_file( msg )
        flog.info( msg )
        status_text, status_code = usb_drive_lib.unmount_device( flog=flog, timeout=60 )
        if status_code != 0:
            msg = "USB drive is niet te un-mounten, dit duidt op een drive probleem."
            raise Exception( msg )

    except Exception as e:

        flog.error( str(e) )
        write_status_to_file( str(e) )

        msg = "Verwerking gefaald en gestopt!"
        write_status_to_file( msg )
        flog.critical( msg )
        sys.exit(1)

    msg = "kopie naar drive succesvol. "
    write_status_to_file( msg )
    flog.info( msg )
    msg = "De volgend keer dat de P1-monitor wordt gestart wordt deze back-up automatisch teruggezet naar het SDHC kaartje. Verwijder de USB stick niet!"
    write_status_to_file( msg )
    flog.info( msg )
    sys.exit(0)


#######################################
# unmount van standaard mount point   #
#######################################
def unmount():
    try:
        status_text, status_code = usb_drive_lib.unmount_device( flog=flog )
        if status_code != 0:
            raise Exception( "Unmount gefaald -> " + str( status_text ) )
    except Exception as e:
        flog.warning( " unmount gefaald -> " + str(e) )
        sys.exit(1)
    flog.info("Unmount van " + usb_drive_lib.MOUNTPOINT +" succesvol uitgevoerd.")
    sys.exit( 0 )


#######################################
# mount van standaard mount point     #
#######################################
def mount():
    try:
        status_text, status_code = usb_drive_lib.mount_device( flog=flog )
        if status_code != 0:
            raise Exception( "mount gefaald -> " + str( status_text ) )
    except Exception as e:
        flog.warning( " mount gefaald -> " + str(e) )
        sys.exit(1)
    flog.info("mount van " + usb_drive_lib.MOUNTPOINT +" succesvol uitgevoerd.")
    sys.exit( 0 )


######################
##### functions ######
######################

#############################################
# socat install                             #
# only run after the DB config file is      #
# copied to the ram.                        #
#############################################
def socat_restore():
    flog.info( inspect.stack()[0][3] + ": socat activering gestart." )
    config_db = sqldb.configDB()
    # open van config database
    try: 
        config_db.init( const.FILE_DB_CONFIG, const.DB_CONFIG_TAB )
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": Verwerking gefaald en gestopt!" ) 
        return

    try:
        _id, socat_is_active, _label = config_db.strget( 200, flog )
        if ( int(socat_is_active) == 1):
            flog.info( inspect.stack()[0][3] + ": socat is actief, service wordt geinstalleerd." )
            cmd = '/p1mon/scripts/P1SocatConfig --enable'
            flog.debug ( inspect.stack()[0][3] + ": cmd =" + cmd )
            proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
            _stdout, _stderr  = proc.communicate( timeout=30 )
            returncode = int( proc.wait() )
            #print ( stdout, stderr)
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": socat activering gefaald." + str(e) )
        return

#############################################
# remove a file                             #
#############################################
def remove_file( pathfile=None, flog=None ):
    # remove tmp file
    try:
        if os.path.exists( pathfile ):
            os.remove( pathfile )
    except Exception as e:
        msg = "verwijderen van bestand " + pathfile + " niet gelukt -> " + str(e)
        write_status_to_file( msg )
        flog.warning( msg )


######################################################
# files are added to a tar archive                   #
# the file is tempory stored in ram to improve speed #
# and to make sure that only the encrypted file is   #
# written to ram.                                    #
######################################################
def save_nginx( destination_pathfile=None, flog=None ):
    flog.debug ( inspect.stack()[0][3] + ": source file = " + destination_pathfile )

    folder_list = nginx_lib.RESTORE_FOLDERS
    for idx, folder in enumerate( folder_list ):

        # -C / prevents error feedback Removing leading `/' from member names
        # remove the leading slash from source

        if folder.startswith('/'):
            folder = folder[1:]

        #print ( idx, ",", folder)
        if idx == 0:
            cmd = "/usr/bin/sudo /bin/tar -cf " + destination_pathfile + " -C / " + folder
        else:
            cmd = "/usr/bin/sudo /bin/tar --append --file=" + destination_pathfile + " -C / " + folder 

        flog.debug ( inspect.stack()[0][3] + ": cmd =" + cmd )

        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout=30 )
        returncode = int( proc.wait() )
        #print ( stdout, stderr)
        if returncode != 0:
            raise Exception( 'copy van ' + folder + ' gefaald.' )
        
        msg = "NGINX folder " + str( folder) + " gekopieerd."
        write_status_to_file( msg )
        flog.info( msg )


######################################################
# files are added to a tar archive                   #
# the file is tempory stored in ram to improve speed #
# and to make sure that only the encrypted file is   #
# written to ram.                                    #
######################################################
def save_letsencrypt( destination_pathfile=None, flog=None ):
    flog.debug ( inspect.stack()[0][3] + ": source file = " + destination_pathfile )

    folders_list = letsencrypt_lib.RESTORE_FOLDERS

    for idx, folder in enumerate(folders_list):
        
        # -C / prevents error feedback Removing leading `/' from member names
        # remove the leading slash from source 
        if folder.startswith('/'):
            folder = folder[1:]
        #print ( idx, ",", folder)
        if idx == 0:
            cmd = "/usr/bin/sudo /bin/tar -cf " + destination_pathfile + " -C / " + folder
        else:
           cmd = "/usr/bin/sudo /bin/tar --append --file=" + destination_pathfile + " -C / " + folder 

        flog.debug ( "cmd =" + cmd )
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
        _stdout, _stderr  = proc.communicate( timeout=30 )
        returncode = int( proc.wait() )
        #print ( stdout, stderr)
        if returncode != 0:
           # raise Exception( 'copy van ' + folder + ' gefaald.' ) # change in 1.8.0
           msg = 'copy van ' + folder + ' gefaald.  Dit kan op een probleem duiden.'
           write_status_to_file( msg )
           flog.error( msg )

        msg = "Lets Encrypt folder " + str( folder) + " gekopieerd."
        write_status_to_file( msg )
        flog.info( msg )

    ### TEST for restore 
    #c.decrypt_file( source_pathfile=tmp_ram_file + AIDE_EXT_CRYPTO, destination_pathfile=tmp_ram_file + ".debug" )

##########################################################
# generate a tempory file name in the default tmp folder #
##########################################################
def generate_temp_ram_filename() -> str:
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return os.path.join( const.DIR_RAMDISK, random_string)

###############################################
# decompress and copy the source file         #
###############################################
def copy_and_decompress( source_pathfile=None, flog=None, gzip=False ):

    try:
        if gzip == False:
            cmd = "/usr/bin/sudo /bin/tar -xf " + source_pathfile + " -C / "
        else:
            cmd = "/usr/bin/sudo /bin/tar -zxf " + source_pathfile + " -C / "

        flog.debug ( "cmd =" + cmd )
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout=30 )
        returncode = int( proc.wait() )
        #print ( stdout, stderr)
        if returncode != 0:
            raise Exception( 'copy van ' + source_pathfile + ' gefaald.' )

    except Exception as e:
        raise Exception( str(e) )

###############################################
# compress and copy the source file           #
###############################################
def copy_and_compress( source_pathfile=None, destination_pathfile=None, flog=None ):

    try:
        # -C / prevents error feedback Removing leading `/' from member names
        # remove the leading slash from source 
        if source_pathfile.startswith('/'):
            source_pathfile = source_pathfile[1:]

        cmd = "/usr/bin/sudo /bin/tar -zcf " + destination_pathfile + " -C / " + source_pathfile
        flog.debug ( "cmd =" + cmd )
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout=30 )
        returncode = int( proc.wait() )
        
        if returncode != 0:
            raise Exception( 'copy van ' + source_pathfile + ' gefaald.' )

    except Exception as e:
        raise Exception( str(e) )

###############################################
# set the file permissions via octal notation #
# example '644' as rw+r+r                     #
###############################################
def set_file_permissions( filepath=None, permissions=None, flog=None ):
    flog.debug ( "filepath = " + filepath + " permissions = " + permissions )
    cmd = '/usr/bin/sudo chmod ' + permissions + ' ' + filepath
   
    #if os.system( cmd ) > 0:
    #     flog.warning( inspect.stack()[0][3] + ": file eigenaarschap fout. " + filepath )
    r = process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=True,
        flog=flog 
        )
    if ( r[2] ) > 0:
        flog.warning( inspect.stack()[0][3] + ": file eigenaarschap fout. " + filepath )

##########################################
# get the file permissions in the octal  #
# format                                 #
##########################################
def file_permissions( filepath=None ):
    return str( oct(os.stat( filepath).st_mode & 0o777 )[2:])

############################################
# copies and encrypted or decrypted a file #
############################################
def copy_and_crypto_file( mode='e' ,source_pathfile=None, destination_pathfile=None, flog=None, cryptoseed=None ):
   
    try:
        with open( source_pathfile, 'r' ) as w_file:
            data = w_file.read()

        #flog.debug ( "source data " + str(data) ) 

        if mode == 'encrypt':
            result = crypto3.p1Encrypt( str(data), cryptoseed )
        elif mode == 'decrypt':
            result = crypto3.p1Decrypt( str(data), cryptoseed )
        else:
            raise Exception( " geen goed crypto mode opgegeven, valide opties (encrypt of decrypt)." )

        #flog.debug ( "destination data " + str( result )  )

        destination = destination_pathfile
        fp = open( destination  , "w" )
        fp.write( result )
        fp.close()

        flog.debug ( "bestand " + source_pathfile + " versleuteld en gekopieerd naar " + destination ) 

    except Exception as e:
        raise Exception( str(e) )

############################################
# find an USB drive that can be used       #
# return device name or None for no drive  #
# check for drive that may containt a      #
# bootable image                           #
############################################
def find_usable_usb_device( usb_list=usb_drive_lib.USB_LIST, flog=None ):
    for usb in usb_list:
        usb_drive_lib.unmount_device( flog=flog ) #failsave unmount when there is still a mount lingering

        status_text, status_code = usb_drive_lib.mount_device( device=usb, flog=flog )

        if status_code == 0:
            # check if this is a valid destination.
            # first check if this is image backup, if so skip.
            flog.debug( "Controle op valide USB device gestart voor device " + str( usb ) )
            isImageDrive = False
            for name in glob.glob( const.DIR_USB_MOUNT  + "/*" ):
                if name == const.DIR_USB_MOUNT  + '/bootcode.bin' or name == const.DIR_USB_MOUNT + '/kernel.img':
                    isImageDrive = True
                    break
            if isImageDrive == True:
                msg =  "USB device " + str( usb ) + " is een image device die niet kan worden gebruikt."
                flog.info( msg )
                write_status_to_file( msg )
                continue # try next device
            else:
                return usb
    return None

############################################
# check all possible drives if there is a  #
# folder on the drive then return the      #
# device name                              #
# return device name or None for no drive  #
############################################
def check_for_used_aide_drive( usb_list=usb_drive_lib.USB_LIST, flog=None ):
    for usb in usb_list:
        msg = "Controle op eerder gebruikt drive " + str (usb) + " gestart."
        flog.info( msg )
        write_status_to_file( msg )
        usb_drive_lib.unmount_device( flog=flog ) #failsave unmount when there is still a mount lingering
        status_text, status_code = usb_drive_lib.mount_device( device=usb, flog=flog )
        if status_code == 0:
            path = const.DIR_UPGRADE_ASSIST_USB_MOUNT + const.DIR_USB_ROOT + const.DIR_UPGRADE_AIDE
            flog.debug ( "controle op path: " + path )
            if os.path.isdir( path ):
                msg = "Folder " + path + " bestaat op device " + str( usb )
                flog.info( msg )
                write_status_to_file( msg )
                return usb
    return None

############################################
# write log to status file that is used by #
# the web interface                        #
############################################
def write_status_to_file( msg ):
    try:
        fp = open( const.FILE_UPGRADE_AIDE_STATUS, "a")
        t = time.localtime()
        fp.write( "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + " " + msg + '\n' )
        fp.close()
    except Exception as e:
        flog.error( "status file schrijf fout: " + str(e) )


#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG + prgname + ".log"
        util.setFile2user( logfile, 'p1mon' )
        flog = logger.fileLogger( logfile, prgname )
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )

        status_fp = open( const.FILE_UPGRADE_AIDE_STATUS, "w" )
        subprocess.run( ['sudo', 'chmod', '0666' , const.FILE_UPGRADE_AIDE_STATUS ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        status_fp.close()

    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit( 1 ) #  error: no logging check file rights

    Main( sys.argv[1:] )

