# run manual with ./P1Backup

import argparse
import const
import inspect
import logger
import os
import os.path
import pathlib
import shutil
import sys
import systemid
import sqldb
import time
import util
import process_lib

prgname = 'P1Backup'
exportfile_base = '/p1mon/www/download/p1mon-sql-export'
config_db       = sqldb.configDB()
rt_status_db    = sqldb.rtStatusDb()

def Main(argv): 
    flog.info("Start van programma.")

    parser = argparse.ArgumentParser(description="options: -fb" )
    parser.add_argument('-fb', '--forcebackup',    required=False, action="store_true" )
    args = parser.parse_args()
    
    # open van status database
    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(2)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")
    
    _id, do_ftp_backup ,_label = config_db.strget(36,flog)
    _id, do_dbx_backup ,_label = config_db.strget(49,flog)
    parameter = 0
    # do some casting....comparing strings is a pain
    do_ftp_backup = int(do_ftp_backup)
    do_dbx_backup = int(do_dbx_backup)

    flog.debug(inspect.stack()[0][3]+": ftp backup="+str(do_ftp_backup)+ " Dropbox back-up="+ str(do_dbx_backup))

    # if one of the backup options is on make an export file
    if do_ftp_backup == 1 or do_dbx_backup == 1:
        parameter = 1
    else:
        flog.info(inspect.stack()[0][3]+": Backup staat uit, geen back-up gestart")

    if args.forcebackup == True: # force backup, forget preference.
        flog.info(inspect.stack()[0][3]+": geforceerde back-up gestart.")
        parameter = 1
    
    if int(parameter) == 1:
        flog.debug(inspect.stack()[0][3]+": export file wordt gemaakt.")
        file_tmp_id = str( util.getUtcTime() ) + "-" + systemid.getSystemId()
        cmd = "/p1mon/scripts/P1SqlExport -e " + file_tmp_id
        flog.debug( inspect.stack()[0][3] + ": export commando is ->" + str(cmd ))

        r = process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog,
            timeout=None
        )
        if r[2] > 0:
            flog.error(inspect.stack()[0][3]+": export van file gefaald, gestopt.")
            sys.exit(3)

        # wait for the export to complete for max 3 minutes
        export_file = exportfile_base + file_tmp_id + '.zip'
        for i in range( 300 ):
            if util.fileExist( export_file ):
                flog.info( inspect.stack()[0][3]+": export file " + export_file + " gevonden. ")
                break
            time.sleep(1)
            if i > 180:
                flog.error(inspect.stack()[0][3]+": export file " + export_file + " niet gevonden, gestopt.")
                sys.exit(4)

        #export_file = exportfile_base + file_tmp_id + '.zip'
        #if util.fileExist( export_file ) == False:
           # flog.error(inspect.stack()[0][3]+": export file " + export_file + " niet gevonden, gestopt.")
           # sys.exit(4)

        # update config database with current name of backup file.
        config_db.strset(export_file,33, flog)
        
    if do_dbx_backup == 1:
        # do dropbox back-up 
        flog.info(inspect.stack()[0][3]+": Dropbox backup gestart")
        try:
            # try to clean old files
            clean_old_files()

            if len ( os.listdir( const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP ) ) > 10 :
                flog.critical(inspect.stack()[0][3]+": Dropbox backup bestand niet gekopierd, te veel bestanden in ram buffer.")
            else:
                flog.debug(inspect.stack()[0][3]+": copy export file naar lokale dropbox folder: " + export_file )
                shutil.copy2(export_file, const.DIR_DBX_LOCAL+const.DBX_DIR_BACKUP)
                _head,tail = os.path.split( export_file ) 
                util.setFile2user(const.DIR_DBX_LOCAL+const.DBX_DIR_BACKUP+'/'+tail,'p1mon')
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": Dropbox back-up. melding:" + str( e.args[0]) )
    
    if do_ftp_backup == 1:
        flog.info(inspect.stack()[0][3]+": FTP backup gestart")
        cmd = "/p1mon/scripts/P1FtpCopy"
        flog.debug( inspect.stack()[0][3] + ": export commando is ->" + str(cmd ))
        r = process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog,
            timeout=None
        )
        if r[2] > 0:
            flog.error(inspect.stack()[0][3]+": ftp backup gefaald, gestopt.")
            sys.exit(5)
    
    flog.info("programma is succesvol gestopt.")
    sys.exit(0) # all is well.

################################################################
# remove files from the DBX backup folder that are older than  #
# 7200 seconds.                                                #
################################################################
def clean_old_files():
    path = const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP

    # define the path
    currentDirectory = pathlib.Path( path )

    for currentFile in currentDirectory.iterdir():
        delta_secs =  abs( util.getUtcTime()  - int(os.path.getctime( currentFile )) )
        #print ( "Delta " + str(currentFile), " ", str( delta_secs ))
        if delta_secs > 7200: #remove files that are older then 2 hours, to prevent daylight saving problems 
            flog.info( inspect.stack()[0][3]+": verouderde bestand " + str(currentFile) +\
                 " wordt verwijderd. Bestand is " + str(delta_secs ) + " seconden oud." )
            os.remove( currentFile )
        else:
            flog.debug( inspect.stack()[0][3]+": bestand " + str(currentFile) +\
                 " wordt NIET verwijderd. Bestand is " + str(delta_secs ) + " seconden oud." )


#-------------------------------
if __name__ == "__main__":
    try:
        logfile = const.DIR_FILELOG+prgname+".log" 
        util.setFile2user(logfile,'p1mon')
        flog = logger.fileLogger(logfile,prgname)
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn(True)
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
        sys.exit(10) #  error: no logging check file rights

    Main(sys.argv[1:])
