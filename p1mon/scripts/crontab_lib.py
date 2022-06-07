####################################################################
# shared lib for cron tab functions                                #
# !!! TODO migrate other scripts to this lib.                      #
####################################################################
import const
import inspect
import os
import pwd
import subprocess

PROCESS_TIMEOUT  = 10
CRONTAB_TMP_FILE = 'crontab.tmp'
CRONTAB_PATH = '/var/spool/cron/crontabs'

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