# run manual with ./P1DropBoxDeamon

import const
import dropbox_lib
import filesystem_lib
import inspect
import logger
import signal
import sqldb
import systemid
import os
import sys
import time
import util



from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

prgname         = 'P1DropBoxDeamon'
config_db       = sqldb.configDB()
rt_status_db    = sqldb.rtStatusDb()

files_backup   = [] 
files_data     = [] 

systemid = systemid.getSystemId()

def Main(argv):

    global files_backup, files_data

    flog.info("Start van programma.")
    local_dbx_folders = []
   
    # do an intial clean to fix problems after a restart.
    try:
        filesystem_lib.clear_folder_by_age( rootfolder=const.DIR_DBX_LOCAL, age_in_seconds=7205, flog=flog)
    except Exception as e:
        flog.warning(inspect.stack()[0][3]+": wissen van mogelik oude bestanden gefaald melding -> " + str(e.args[0]) )

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
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # set start timestamp in status database
    rt_status_db.timestamp(65,flog)

    # local folder to process
    local_dbx_folders.append( const.DIR_DBX_LOCAL )
    local_dbx_folders.append( const.DIR_DBX_LOCAL+const.DBX_DIR_DATA )  
    local_dbx_folders.append( const.DIR_DBX_LOCAL+const.DBX_DIR_BACKUP ) 

    # check local folder 
    createCheckFolder(const.DIR_DBX_LOCAL)
    for folder in local_dbx_folders:
         createCheckFolder(folder)
    
    # open DropBox session / access
   
    dbx = dropbox_lib.authenticate_dbx( flog=flog, config_db=config_db, rt_status_db=rt_status_db )
    #print( dbx.users_get_current_account() )
    #print( dbx.check_and_refresh_access_token() )
    #dbx.close()
    #print( dbx.users_get_current_account() )
    #dropbox_lib.connection_is_valid( dbx=dbx, flog=flog )
    #sys.exit()

    loop_timeout = 2

    while True:

        # dropbox data and backup switches.
        _id, drop_box_backup_on ,_label = config_db.strget(49,flog)
        _id, drop_box_data_on   ,_label = config_db.strget(50,flog)

        file_count = fill_file_list_buffer()

        try:
            filesystem_lib.clear_folder_by_age( rootfolder=const.DIR_DBX_LOCAL, age_in_seconds=7205, flog=flog)
        except Exception as e:
            flog.warning(inspect.stack()[0][3]+": wissen van mogelik oude bestanden gefaald melding -> " + str(e.args[0]) )

        """ # removed in version 2.4.2 replace by filesystem_lib.clear_folder_by_age
        if int(drop_box_backup_on) == 0: 
            for filename in files_backup: 
                flog.info(inspect.stack()[0][3]+": failsave wissen van back-up bestanden.")
                try:
                    os.remove(const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP + '/' + filename)
                except Exception as _e:
                    pass
        
        if int(drop_box_data_on) == 0: 
            for filename in files_backup: 
                flog.info(inspect.stack()[0][3]+": failsave wissen van data bestanden.")
                try:
                    os.remove(const.DIR_DBX_LOCAL + const.DBX_DIR_DATA + '/' + filename)
                except Exception as _e:
                    pass
        """

        if int(drop_box_backup_on) == 0 and int(drop_box_data_on) == 0: 
            flog.debug(inspect.stack()[0][3]+": Dropbox staat uit, wacht 30 seconden.")
            time.sleep(30)
            continue

        if file_count > 0: #something to do.
            flog.debug(inspect.stack()[0][3]+": " + str(file_count) + " bestand(en) gevonden om te verwerken.")
            if dropbox_lib.connection_is_valid( dbx=dbx, flog=flog ) == False:
                #dbx = AuthenticateDropBox()
                dbx = dropbox_lib.authenticate_dbx(flog=flog, config_db=config_db, rt_status_db=rt_status_db )

        if dbx == None: 
            flog.error(inspect.stack()[0][3]+": Dropbox authenticatie gefaald en gestopt.")
            rt_status_db.strset('Authenticatie gefaald en gestopt.',62,flog) 
            time.sleep(10)
            continue

        """
        listing=listDbxFolder( dbx, const.DBX_DIR_BACKUP )
        files_list = []
        for _k, v in listing.items():
            print ( _k, v )
        return
        """
        #flog.setLevel( logging.DEBUG )
        #######################
        # back-up files check #
        #######################
        for filename in files_backup: 

            from_file = const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP + '/' + filename
            to_file   = const.DBX_DIR_BACKUP + '/' + filename

            if validFilePermissions( from_file ) == False:
                flog.error(inspect.stack()[0][3]+": geen bestands rechten op bestand > "+from_file+ " wordt genegeerd.")
                continue

            try:
                return_value_copy = copyDbxFile( dbx, from_file, to_file  )
            except Exception as e:
                flog.error(inspect.stack()[0][3]+  "copyDbxFile onverwachte fout.")

            if True == return_value_copy:
                rt_status_db.timestamp( 60,flog )
                try:
                    os.remove(const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP + '/' + filename)
                except OSError as e:  ## if failed, report it back to the user ##
                    flog.error(inspect.stack()[0][3]+ const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP + '/' + filename + " was niet te verwijderen." + e.strerror)
                rt_status_db.timestamp( 61,flog )
                rt_status_db.strset('bestand naar Dropbox gekopieerd.',62,flog)
                flog.info(inspect.stack()[0][3]+": backup bestand "+ from_file + " gekopierd.")
            else:
                rt_status_db.strset('Dropbox copy gefaald.',62,flog)
                if dropbox_lib.connection_is_valid( dbx=dbx, flog=flog ) == False:
                    dbx = dropbox_lib.authenticate_dbx(flog=flog, config_db=config_db, rt_status_db=rt_status_db )
                    #dbx = AuthenticateDropBox() 

            # remove files that are beyond the max count of backup files.
            listing = listDbxFolder( dbx, const.DBX_DIR_BACKUP ) 

            _id, max_files ,_label = config_db.strget(48,flog)
            max_files = int(max_files)

            flog.debug(inspect.stack()[0][3]+": maximum back-up bestanden is " + str(max_files) + " aantal Dropbox bestanden is " + str( len(listing)))
            max_backup_files = int(max_files) 
            if len(listing) >  max_backup_files and max_files != 0: # is no cleaning.:
                flog.debug(inspect.stack()[0][3]+": wissen van files omdat de grenswaarde van maximaal aantal files is bereikt, "+ str(len(listing)) + " files gevonden.")

                files_list = []
                for _k, v in listing.items():
                    files_list.append ( [str(v.client_modified), str(v.path_display)] )
            
                files_list.sort()  # sort oldest files first

                for x in range( len(listing) - max_backup_files ):
                    flog.info(inspect.stack()[0][3]+": bestand wordt gewist -> " + str( files_list[x][1] ) )
                    deleteDbxFile( dbx, files_list[x][1] )

        #flog.setLevel( logging.INFO )

        ####################
        # data files check #
        ####################
        for filename in files_data: 

            from_file = const.DIR_DBX_LOCAL + const.DBX_DIR_DATA + '/' + filename
            to_file   = const.DBX_DIR_DATA + '/' + filename

            if validFilePermissions( from_file ) == False:
                flog.error(inspect.stack()[0][3]+": geen bestands rechten op bestand > "+from_file+ " wordt genegeerd.")
                continue

            return_value_copy = copyDbxFile( dbx, from_file, to_file  )
            
            if True == return_value_copy:
                rt_status_db.timestamp( 63,flog )
                try:
                    os.remove(const.DIR_DBX_LOCAL + const.DBX_DIR_DATA+ '/' + filename)
                except OSError as e:  ## if failed, report it back to the user ##
                    flog.error(inspect.stack()[0][3]+ const.DIR_DBX_LOCAL + const.DBX_DIR_DATA + '/' + filename + " was niet te verwijderen." + e.strerror)
                rt_status_db.strset('data gekopieerd.',64,flog)
                flog.debug(inspect.stack()[0][3]+": data bestand "+ from_file + " gekopierd.")
            else:
                rt_status_db.strset('data copy gefaald.',64,flog )
                if dropbox_lib.connection_is_valid( dbx=dbx, flog=flog ) == False:
                    dbx = dropbox_lib.authenticate_dbx(flog=flog, config_db=config_db, rt_status_db=rt_status_db )
                    #dbx = AuthenticateDropBox() 

        ###############################
        # scan for data request files #
        ###############################
        #flog.setLevel( logging.DEBUG )
        listing = listDbxFolder( dbx, const.DBX_DIR_DATA )
        for _k, v in listing.items():
            if v.path_display.find( const.DBX_REQ_DATA ) > 0:
                if v.path_display.find( systemid ) > 0 or v.path_display.find( const.SYSTEM_ID_DEFAULT ) > 0:
                    flog.debug(inspect.stack()[0][3]+" DB verzoek bestand "+ v.path_display + " gevonden, en gewist")
                    deleteDbxFile(dbx, v.path_display)
                    copySqlToDbx( dbx, const.FILE_DB_E_FILENAME )
                    copySqlToDbx( dbx, const.FILE_DB_E_HISTORIE )
                    copySqlToDbx( dbx, const.FILE_DB_CONFIG )
                    copySqlToDbx( dbx, const.FILE_DB_STATUS )
                    copySqlToDbx( dbx, const.FILE_DB_FINANCIEEL )
                    copySqlToDbx( dbx, const.FILE_DB_WEATHER )
                    copySqlToDbx( dbx, const.FILE_DB_WEATHER_HISTORIE )
                    copySqlToDbx( dbx, const.FILE_DB_WEER_FILENAME  )
                    copySqlToDbx( dbx, const.FILE_DB_TEMPERATUUR_FILENAME  )
                    copySqlToDbx( dbx, const.FILE_DB_WATERMETERV2 )
                    copySqlToDbx( dbx, const.FILE_DB_PHASEINFORMATION )
                    copySqlToDbx( dbx, const.FILE_DB_POWERPRODUCTION )

        #flog.setLevel( logging.INFO )

        time.sleep( loop_timeout ) # by nice to your cpu cycles

        #######################
        # files not processed #
        #######################
        file_count = fill_file_list_buffer()
        if file_count > 2: # problem files are not copied or not deleted.
            delay = 30
            flog.warning(inspect.stack()[0][3]+" bestanden gevonden die niet te wissen waren of niet gekopierd. Vertraagde verwerking van " + \
                str( delay ) + " seconden actief.")
            time.sleep( delay  )
        
        


def copySqlToDbx(dbx, sqlfilepath ):
    _head,tail = os.path.split( sqlfilepath ) 
    to_file   = const.DBX_DIR_DATA + '/' + 'sqldb-' + systemid + '-' + tail
    try:
        copyDbxFile( dbx, sqlfilepath, to_file  )
    except Exception as e:
        flog.error( inspect.stack()[0][3]+": file "+ to_file + " is niet te kopieren, fout=" + str(e.args[0]) ) 

def validFilePermissions(filename):
    try:
        fp = open(filename,"r+")
        fp.close()
        return True
    except PermissionError:
        return False


def fill_file_list_buffer():
    global files_backup, files_data
    files_backup = [f for f in os.listdir( const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP ) \
            if os.path.isfile(os.path.join( const.DIR_DBX_LOCAL + const.DBX_DIR_BACKUP, f ))]
    files_data =   [f for f in os.listdir( const.DIR_DBX_LOCAL + const.DBX_DIR_DATA )\
            if os.path.isfile(os.path.join( const.DIR_DBX_LOCAL + const.DBX_DIR_DATA, f ))]
    file_count = len(files_backup) + len(files_data)
    return file_count


def deleteDbxFile(dbx, file):
    flog.debug(inspect.stack()[0][3]+": probeer file " + file + " te verwijderen.")
    try:
        dbx.files_delete( file )
        flog.debug(inspect.stack()[0][3]+": file " + file + " verwijderd.")
    except Exception as e:
         flog.error(inspect.stack()[0][3]+": file "+ file + " is niet te wissen " + str(e.args[0]))
       

def listDbxFolder( dbx, folder ):
    try:
        res = dbx.files_list_folder(folder)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": folder inhoud is niet te lezen voor folder " + folder + " -> " + str(e))
        rt_status_db.strset('Fout: Dropbox folder is niet te lezen.',62,flog)
        return {}
    else:
        rv = {}
        for entry in res.entries:
            rv[entry.name] = entry
        return rv


def copyDbxFile(dbx, from_file, to_file):
    r = True

    with open(from_file, 'rb') as f:
        flog.debug(inspect.stack()[0][3]+": copy " + from_file + " naar dropbox als " + to_file )
        try:
            dbx.files_upload(f.read(), to_file , mode=WriteMode('overwrite'))
        except ApiError as e:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (e.error.is_path() and
                e.error.get_path().reason.is_insufficient_space()):
                flog.critical(inspect.stack()[0][3]+": copy " + from_file + " naar dropbox als " + to_file + " gefaald, te weining ruimte." )
                r = False
            elif e.user_message_text:
                flog.critical(inspect.stack()[0][3]+": copy " + from_file + " naar dropbox als " + to_file + " gefaald. -> " + str(e))
                r = False
        except Exception as e: 
               flog.critical(inspect.stack()[0][3]+": copy " + from_file + " naar dropbox als " + to_file + " gefaald. -> " + str(e))
    return r      


# return True is ok, False is not ok.
def createCheckFolder(folder):
    r = True
    if os.path.isdir(folder) == False: 
        try:  
            os.mkdir(folder)
        except OSError:  
            flog.error(inspect.stack()[0][3]+": folder %s aanmaken gefaald" % folder)
            r =False
        else:  
            flog.debug(inspect.stack()[0][3]+": folder %s succesvol aangemaakt." % folder)
    try:  
        util.setFile2user( folder, 'p1mon' )
        os.chmod( folder, 0o774) 
    except Exception as e: 
        flog.error(inspect.stack()[0][3]+": " + folder + "rechten zijn niet aan te passen ->" + str(e.args[0]))
    return r


def isDropBoxFolders(dbx, folder):
    try:
        dbx.files_get_metadata(folder)
        flog.debug(inspect.stack()[0][3]+": dropbox folder "+folder+" bestaat.")
    except Exception as _e:
        # folder does not exist make, the folder
        try:
            dbx.files_create_folder(folder)
            flog.info(inspect.stack()[0][3]+": dropbox folder "+folder+" gemaakt.")
        except Exception as _e:
            flog.critical(inspect.stack()[0][3]+": folder "+folder+" niet te maken")


def saveExit( signum, frame ):   
        signal.signal(signal.SIGINT, original_sigint)
        flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
        sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG + prgname+".log"
        util.setFile2user( logfile,'p1mon' )
        flog = logger.fileLogger(logfile,prgname)
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn(True)
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(10) #  error: no logging check file rights

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT, saveExit )
    Main(sys.argv[1:])