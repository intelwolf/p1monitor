
import argparse
from genericpath import isdir
import const
import crypto_lib
import inspect
import filesystem_lib
import glob
import logger
import os
import pwd
import patch_lib
import sqldb
import signal
import sys
import time
#import network_lib
import subprocess

# programme name.
prgname   = 'P1Patcher'

config_db = sqldb.configDB()

data = {
    'patchfile':  '',
    'run_status': 0,
    'tmp_zip_filepath' : '',
    'tmp_extracted_folder' : '',
    'allow_unsinged_patches' : False
}

PATCH_FOLDER                = '/p1mon/var/patch'
TMP_PATCH_FOLDER            = '/tmp'
TMP_PATCH_FOLDER_EXTENTION  = '-patcher'

def Main( argv ):

    initStatusFile()

    my_pid = os.getpid()

    msg =": start van programma met process id " + str(my_pid)
    writeLineToStatusFile( msg )
    flog.info(inspect.stack()[0][3] + msg )

    msg = ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name
    writeLineToStatusFile( msg )
    flog.info(inspect.stack()[0][3] + msg )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument( '-h', '--help',
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument('-fname', '--filename',
         required=False,
         help='patch file om te verwerken.')

    parser.add_argument('-f'  , '--force',
            required=False, 
            action="store_true", # flag only
            help='forceer de uitvoering.')

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init( const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        msg = ": database niet te openen ("+ const.FILE_DB_CONFIG + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical( msg )
        stop( 1 )
    msg =": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend."
    writeLineToStatusFile( msg )
    flog.info(inspect.stack()[0][3] + msg )

    # update field from database, the cli switches overwrite the DB values!
    _id, data['patchfile']   ,_label = config_db.strget(193,flog)
    _id, data['run_status']  ,_label = config_db.strget(194,flog)

    args = parser.parse_args()
    #print( args )

    if args.force == True:
        data['run_status'] = 1 

    # check if we need to run.
    if int( data['run_status'] ) == 0:
        flog.info( inspect.stack()[0][3] + ": run status is 0, niets uitgevoerd " )
        sys.exit(0)
    
    # run status >0 means run
    # 1 means only allow sigend patch files
    # 2 means signed and unsignend will be processed 
    if int( data['run_status'] ) == 2:
        data['allow_unsinged_patches'] = True
        msg = ": Unsignend patches zijn toegestaan"
    else: 
        msg = ": Alleen signed patches zijn toegestaan"
    
    writeLineToStatusFile( msg )
    flog.info(inspect.stack()[0][3] + msg )

    if args.filename != None:
        data['patchfile'] = args.filename
    
    if len( data['patchfile'].strip()) == 0:
        msg = ": opgegeven patch bestand niet opgegeven, gestopt."
        writeLineToStatusFile( msg )
        flog.info(inspect.stack()[0][3] + msg )
        stop ( 2 )

    msg = ": opgegeven patch bestand " + data['patchfile']
    writeLineToStatusFile( msg )
    flog.info(inspect.stack()[0][3] + msg )

    # check if file is in the expected location
    if os.path.isfile( data['patchfile'] ) == False:
        msg = ": opgegeven patch bestand niet opgegeven niet gevonden, gestopt."
        writeLineToStatusFile( msg )
        flog.info( inspect.stack()[0][3] + msg )
        stop ( 3 )

    # detect sigend or non signen patch file

    data['tmp_zip_filepath'] = filesystem_lib.generate_temp_filename() + patch_lib.UNSIGNED_ZIP_EXTENTION
    
    _head, tail =  os.path.split( data['patchfile'])
    t=time.localtime()
    data['tmp_extracted_folder'] = TMP_PATCH_FOLDER + "/" + str(tail.split('.')[0]) + "%04d%02d%02d%02d%02d%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + TMP_PATCH_FOLDER_EXTENTION

    if patch_lib.UNSIGNED_ZIP_EXTENTION in data['patchfile'] and data['allow_unsinged_patches'] == True:
        if extract_unsigned_file(zip_source_filepath=data['patchfile'], extract_folderpath=data['tmp_extracted_folder']) == False:
            msg = ": extractie van zip file gefaald, gestopt."
            writeLineToStatusFile( msg )
            flog.info( inspect.stack()[0][3] + msg )
            stop ( 7 )

        if run_patch(extract_folderpath=data['tmp_extracted_folder']) == False:
            msg = ": uitvoeren van de patch gefaald."
            writeLineToStatusFile( msg )
            flog.info( inspect.stack()[0][3] + msg )
            stop ( 8 )

        msg = ": uitvoeren van de patch succesvol."
        writeLineToStatusFile( msg )
        flog.info( inspect.stack()[0][3] + msg )
        stop ( 0 )


    if patch_lib.SIGNED_ZIP_EXTENTION in data['patchfile'] :
        if extract_signed_file( source_filepath=data['patchfile'], destination_filepath=data['tmp_zip_filepath'] ) == False:
            msg = ": verificatie gefaald, gestopt."
            writeLineToStatusFile( msg )
            flog.info( inspect.stack()[0][3] + msg )
            stop ( 4 )

        if extract_unsigned_file(zip_source_filepath=data['tmp_zip_filepath'], extract_folderpath=data['tmp_extracted_folder']) == False:
            msg = ": extractie van zip file gefaald, gestopt."
            writeLineToStatusFile( msg )
            flog.info( inspect.stack()[0][3] + msg )
            stop ( 5 )

        if run_patch(extract_folderpath=data['tmp_extracted_folder']) == False:
            msg = ": uitvoeren van de patch gefaald."
            writeLineToStatusFile( msg )
            flog.info( inspect.stack()[0][3] + msg )
            stop ( 6 )

        msg = ": uitvoeren van de patch succesvol."
        writeLineToStatusFile( msg )
        flog.info( inspect.stack()[0][3] + msg )
        stop ( 0 )
    
    msg = ": geen patch uitgevoerd."
    writeLineToStatusFile( msg )
    flog.warning( inspect.stack()[0][3] + msg )
    stop ( 100 )



###################################################
# run the patch when the start file exist in the  #
# path and is excutable. return true when all is  #
# well.                                           #
###################################################
def run_patch( extract_folderpath=None ):
    flog.debug( inspect.stack()[0][3] + " extract_folderpath = " + str(extract_folderpath) )
    # find the folder with the starting executable patch_lib.PATCH_START_SCRIPT_NAME
    
    r=False
    try:
        path = extract_folderpath + "/**/" + patch_lib.PATCH_START_SCRIPT_NAME
        start_file_name = glob.glob( path , recursive = True)

        if len( start_file_name ) == 0: # there is no  start file
            raise Exception( patch_lib.PATCH_START_SCRIPT_NAME + " niet gevonden." )

        # check if file is executabel. 
        if os.access( start_file_name[0], os.X_OK ) == False:
             raise Exception( patch_lib.PATCH_START_SCRIPT_NAME + " is niet uitvoerbaar!" )

        # find folder and file to execute without the path.
        working_folder, file_to_excute =  os.path.split( start_file_name[0] )
       
        cmd = "cd " + working_folder + "; ./" + file_to_excute + " " + str( const.FILE_PATCH_STATUS )
        flog.debug( inspect.stack()[0][3] + " cmd =  " + str(cmd) )

        msg = ": aanpassingen worden doorgevoerd, dit kan even duren....."
        writeLineToStatusFile( msg )
        flog.info( inspect.stack()[0][3] + msg )

        try:
            proc = subprocess.Popen( [cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            stdout, stderr  = proc.communicate()
            #returncode = int( proc.wait( timeout=180 ) )
            returncode = int( proc.wait( timeout=900 ) ) # fixed by v2.2.0 patch
            #print ( stdout, stderr, returncode )
            if returncode != 0:
                raise Exception( "fout bij het uitvoeren van de patch." )
            else:
                for line in stdout.splitlines():
                    msg = " " + line.decode("utf-8").lstrip()
                    writeLineToStatusFile( msg )
                    flog.info( inspect.stack()[0][3] + msg )
            r=True # all is well.
        except Exception as e:
            msg = ": patch uitvoerings probleem " + str(e) + " (stderr) output " + str( stderr.decode("utf-8") )
            writeLineToStatusFile( msg )
            flog.info( inspect.stack()[0][3] + msg )
            raise Exception( msg )

    except Exception as e:
        flog.critical( inspect.stack()[0][3] + "start file " + str(e) )

    return r

#################################################
# when extraction is succesfull return true     #
#################################################
def extract_unsigned_file(zip_source_filepath=None, extract_folderpath=None):
    flog.debug( inspect.stack()[0][3] + " signed file " + str(zip_source_filepath) + " destination_filepath "  + str(zip_source_filepath) )

    cmd = "unzip -o -d " + extract_folderpath + " " + zip_source_filepath
    flog.debug( inspect.stack()[0][3] + " cmd =  " + str(cmd) )

    r=False
    try:
        proc = subprocess.Popen( [cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate()
        returncode = int( proc.wait(timeout=180) )
        #print ( stdout, stderr, returncode )
        if returncode != 0:
            raise Exception( "fout bij unzip opgetreden" )
        else:
            for line in stdout.splitlines():
                msg = " " + line.decode("utf-8").lstrip()
                writeLineToStatusFile( msg )
                flog.info( inspect.stack()[0][3] + msg )
        r=True # all is well.
    except Exception as e:
         flog.critical( inspect.stack()[0][3] + "unzip probleem " + str(e) + " (stderr) output " + str( stderr.decode("utf-8") ) )
         
    return r

##################################################
# when verification and extraction is succesfull #
# return true                                    #
##################################################
def extract_signed_file(source_filepath=None, destination_filepath=None ):
    flog.debug( inspect.stack()[0][3] + " sigend file " + str(source_filepath) + " destination_filepath "  + str(destination_filepath) )

    r=False
    ds=crypto_lib.DigitalSignature( debug=False )
    for idx in range( 1, len(crypto_lib.digital_signing_verify_keys_b64 )+1 ):
        try:
            flog.debug( inspect.stack()[0][3] + " probeer verfiy key " + str(str(idx)) + " "  + crypto_lib.digital_signing_verify_keys_b64[str(idx)])
            ds.verify_write_file( source_filepath=source_filepath, destination_filepath=destination_filepath, verify_key_b64=crypto_lib.digital_signing_verify_keys_b64[str(idx)] )
            msg = ": verificatie van digitale handtekening met index " + str(idx) + " succesvol."
            writeLineToStatusFile( msg )
            flog.info( inspect.stack()[0][3] + msg )
            r=True
            break
        except Exception as e:
            pass
    return r

########################################################
# creates and wipes the status file                    #
########################################################
def initStatusFile():
    try:

        # delete old log file
        if os.path.isfile( const.FILE_PATCH_STATUS ) == True:
            filesystem_lib.rm_with_delay( filepath=const.FILE_PATCH_STATUS, timeout=0, flog=flog )

        status_fp = open( const.FILE_PATCH_STATUS, "w")
        filesystem_lib.set_file_permissions( filepath=const.FILE_PATCH_STATUS, permissions='664' )
        status_fp.close()
    except Exception as e:
        flog.error( "status file schrijf fout: " + str(e) )

########################################################
# write to ramdisk file the progress                   #
# the file is emptied/re-created when the program      #
# starts.                                              #
########################################################
def writeLineToStatusFile( msg ):

    try:
        fp = open( const.FILE_PATCH_STATUS, "a" )
        t=time.localtime()
        msg_str = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + " " + msg + '\n'
        fp.write( msg_str )
        fp.close()
    except Exception as e:
        flog.error( "status file schrijf fout: " + str(e) )
        initStatusFile()

#####################################################
# exit the program as clean as possible by closing  #
# alle files, etc.                                  #
# exit parameter is the exit code of the process    #
# exit.                                             #
#####################################################
def stop( exit=0 ):
  
    # remove patch sourche filefolder
    head, _tail =  os.path.split( data['patchfile'])
    if os.path.isdir( head ) == True:
        filesystem_lib.rm_folder_with_delay( head, timeout=0, flog=flog )

    # remove tmp file, after 60 seconds.
    if os.path.isfile(  data['tmp_zip_filepath'] ) == True:
        filesystem_lib.rm_with_delay( filepath=data['tmp_zip_filepath'], timeout=60, flog=flog )

     # remove tmp extract folder, after 900 seconds.
     # the patch could be running longer
    if os.path.isdir( data['tmp_extracted_folder'] ) == True :
        filesystem_lib.rm_folder_with_delay( filepath=data['tmp_extracted_folder'], timeout=900, flog=flog )

    # delete old log file, clean up and save some ram.
    if os.path.isfile( const.FILE_PATCH_STATUS ) == True:
        filesystem_lib.rm_with_delay( filepath=const.FILE_PATCH_STATUS, timeout=900, flog=flog )

    # reset the run flag
    # this also used in the UI to stop reading the status log
    config_db.strset( 0, 194, flog) 

    sys.exit( exit )

########################################################
# close program when a signal is recieved.             #
########################################################
def saveExit(signum, frame):
    stop()
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(0)

########################################################
# init                                                 #
########################################################
if __name__ == "__main__":
    #global process_bg 

    logfile_path = const.DIR_FILELOG + prgname + ".log"
    try:
        # check if file exist, if so set rights and ownership
        if os.path.exists( logfile_path ) == True:
            filesystem_lib.set_file_owners( filepath=logfile_path )
            filesystem_lib.set_file_permissions( filepath=logfile_path, permissions='664' )
    except Exception as e:
        print ("fataal log file probleem:" + str(e.args[0]) )
        sys.exit(1)

    try:
        os.umask( 0o002 )
        flog = logger.fileLogger( logfile_path , prgname )
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])
