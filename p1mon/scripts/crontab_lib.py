####################################################################
# shared lib for cron tab functions                                #
# !!! TODO migrate other scripts to this lib.                      #
####################################################################
import const
import crontab
import inspect
import os
import pwd
import subprocess
import sqldb

PROCESS_TIMEOUT  = 10
CRONTAB_TMP_FILE = 'crontab.tmp'
CRONTAB_PATH = '/var/spool/cron/crontabs'
FTP_BACKUP_CRONLABEL  = 'FTPbackup'
LOG_CLEANER_CRONLABEL = 'Logcleaner'

def set_crontab_logcleaner( flog=None ):
    try:
        
        try:
            my_cron = crontab.CronTab( user='p1mon' )
        except Exception as e:
            msg = inspect.stack()[0][3]+": crontab kon niet worden gestart, gestopt. Fout=" + str(e.args[0])
            raise Exception( msg )

        deleteJob( my_cron, LOG_CLEANER_CRONLABEL, flog=flog ) 
        job = my_cron.new( command='/p1mon/scripts/logspacecleaner.sh >/dev/null 2>&1', comment=LOG_CLEANER_CRONLABEL )
        job.setall( '*/5 * * * *')
        my_cron.write()

    except Exception as e:
         raise Exception( "error in logcleaner setup " + str(e) )

def update_crontab_backup( flog=None ):

    config_db = sqldb.configDB()

    try:
        # open van config database
        try:
            config_db.init( const.FILE_DB_CONFIG, const.DB_CONFIG_TAB )
        except Exception as e:
            msg = inspect.stack()[0][3] + ": database niet te openen(2)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0])
            raise Exception( msg )
        flog.debug( inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

        try:
            my_cron = crontab.CronTab( user='p1mon' )
        except Exception as e:
            msg = inspect.stack()[0][3]+": crontab kon niet worden gestart, gestopt. Fout="+str(e.args[0])
            raise Exception( msg )

         #check add or to remove
        _id, do_ftp_backup, _label = config_db.strget( 36,flog )
        _id, do_dbx_backup, _label = config_db.strget( 49,flog )
    
        # do some casting....comparing strings is a pain
        do_ftp_backup = int( do_ftp_backup )
        do_dbx_backup = int( do_dbx_backup )
        if do_ftp_backup == 1 or do_dbx_backup == 1:
            parameter = 1
        else:
            parameter = 0

        if int(parameter) == 0:
            flog.info(inspect.stack()[0][3]+": FTP backup staat uit, crontab wordt gewist")
            deleteJob( my_cron, FTP_BACKUP_CRONLABEL, flog=flog )
        else:
            _id,parameter,_label = config_db.strget( 37, flog )
            flog.info(inspect.stack()[0][3]+": cron parameters uit config database=" + parameter)
            parts = parameter.split(':')
            if len(parts) != 5:
                msg = inspect.stack()[0][3] +": tijd velden niet correct, gestopt."
                raise Exception( msg )

            deleteJob( my_cron, FTP_BACKUP_CRONLABEL, flog=flog )
        try:

            job = my_cron.new( command='/p1mon/scripts/P1Backup >/dev/null 2>&1', comment=FTP_BACKUP_CRONLABEL )
            job.setall( str(parts[0]), str(parts[1]), str(parts[2]), str(parts[3]), str(parts[4]))
            my_cron.write()
        except Exception as e:
            msg = inspect.stack()[0][3] + ": crontab backup kon niet worden ingesteld, gestopt! Fout=" + str(e.args[0])
            raise Exception( msg )

    except Exception as e:
         raise Exception( "error in update_crontab_backup " + str(e) )


def deleteJob( cron, job_id, flog=None ):
    try:
        cron.remove_all( comment=job_id )
        cron.write()
    except Exception as _e:
        flog.debug(inspect.stack()[0][3]+": crontab bevat geen commando met het label " + ftp_backup_cronlabel+" geen fout.")


#########################################
# make a crontab file if this not exits #
# for the current user                  # 
#########################################
def empty_crontab(flog=None):

    status_str = ""
    returncode = 1

    try:
        filepath = CRONTAB_PATH + "/" + pwd.getpwuid( os.getuid() ).pw_name
        flog.debug('filepath =   ' + str( filepath  ) )

        # check if crontab exist, contains entries
        cmd = 'sudo ls /var/spool/cron/crontabs/p1mon | wc -l'
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout=PROCESS_TIMEOUT )
        returncode = int( proc.wait() )

        if returncode != 0:
             raise Exception( str( stderr.decode('utf-8') .replace('\n\n', '\n')) )

        try:
            crontab_content = str( stdout.decode('utf-8') .replace('\n\n', '\n'))
            flog.debug('crontab content  ' + str( crontab_content ) )
        except Exception:
            pass

        if int(crontab_content) == 0:
            flog.info("crontab bestand bestaat niet.")
            # maak een leeg bestand aan. 
            cmd = 'crontab < /dev/null'
            proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            stdout, stderr  = proc.communicate( timeout=PROCESS_TIMEOUT )
            returncode = int( proc.wait() )
            
            if returncode != 0:
             raise Exception( str( stderr.decode('utf-8') .replace('\n\n', '\n')) )
            
            flog.info("leeg crontab bestand aangemaakt.")

        else:
            flog.info("crontab bestand bestaat, geen aanpassingen uitgevoerd.")

    except Exception as e:
        flog.error(inspect.stack()[0][3] + str(e) )
        status_str = str(e)

    flog.debug( "status: " + str( [status_str, int( returncode) ]) )
    return [ status_str, int( returncode) ]


#############################################
# copy the content to the crontab file      #
# return code > 0 means trouble             #
#############################################
def restore_from_file( source_pathfile=None, flog=None ):

    status_str = ""
    returncode = 1

    try:

        if source_pathfile == None:
            raise Exception( "Geen bron bestand opgegeven!")

        flog.debug('restore van crontab van bestand ' + str( source_pathfile ) + " voor user " + pwd.getpwuid( os.getuid() ).pw_name )

        cmd = '/usr/bin/crontab ' + source_pathfile
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout=PROCESS_TIMEOUT )
        returncode = int( proc.wait() )

    except Exception as e:
        flog.error(inspect.stack()[0][3] + str(e) )
        status_str = str(e)

    flog.debug( "status: " + str( [status_str, int( returncode) ]) )
    return [ status_str, int( returncode) ]


#############################################
# list the content from the user en copy    #
# the content to the file                   #
# return code > 0 means trouble             #
#############################################
def save_to_file( destination_pathfile=None, flog=None ):

    status_str = ""
    returncode = 1

    try:

        if destination_pathfile == None:
            raise Exception( "Geen doel bestand opgegeven!")

        flog.debug('save van crontab inhoud naar ' + str( destination_pathfile ) + " voor user " + pwd.getpwuid( os.getuid() ).pw_name )

        cmd = '/usr/bin/crontab -l'
        proc = subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        stdout, stderr  = proc.communicate( timeout=PROCESS_TIMEOUT )
        returncode = int( proc.wait() )
      
        if returncode != 0:
             raise Exception( str( stderr.decode('utf-8') .replace('\n\n', '\n')) )

        try:
            crontab_content = str( stdout.decode('utf-8') .replace('\n\n', '\n'))
            flog.debug('crontab content  ' + str( crontab_content ) )
        except Exception:
            pass

        fp = open( destination_pathfile  , "w" )
        fp.write( crontab_content )
        fp.close()

    except Exception as e:
        #flog.error(inspect.stack()[0][3] + str(e) )
        status_str = str(e)

    flog.debug( "status: " + str( [status_str, int( returncode) ]) )
    return [ status_str, int( returncode) ]