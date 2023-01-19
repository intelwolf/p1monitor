####################################################################
# shared lib for filessytem util                                   #
# some functiions need sudo rights                                 #
####################################################################

import math
import psutil
import os
import subprocess
import random
import string
import tempfile
import process_lib

FILEPATH_SIZE = {
    'space_total' : 0,
    'space_used'  : 0,
    'space_free'  : 0,
    'pct_used'    : 0.0,
    'pct_free'    : 0.0,
    'unit'        : 'B' # B=Bytes, K=1024 / B, M = 1024000 / B, G= 1024000000 / b
}


def create_folder( filepath=None , flog=None ):
    try :
        cmd = "/usr/bin/sudo mkdir -p " + filepath
        process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog
        )
    except Exception as e:
         raise Exception ( "folder fout. " + str(e) )

##########################################################
# generate a tempory file name in the default tmp folder #
########################################################## 
def generate_temp_filename() -> str:
    random_string = ''.join( random.choices(string.ascii_uppercase + string.digits, k=16) )
    return os.path.join( tempfile.gettempdir(), random_string )


#################################################
# remove a folder and content after the timeout #
# in seconds                                    #
#################################################
def rm_folder_with_delay( filepath=None, timeout=3600, flog=None ):
        cmd = "/bin/sleep " + str(timeout) +" && /usr/bin/sudo /bin/rm --recursive --force " + filepath + " &"
        #os.system( cmd )
        process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog,
            timeout = None
        )



################################################
# remove a file after the seconds parameter    #
# time has pased                               #
################################################
def rm_with_delay( filepath=None, timeout=3600, flog=None ):
        cmd = "/bin/sleep " + str(timeout) +" && /usr/bin/sudo /bin/rm --force " + filepath + " &"
        #os.system( cmd )
        process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog,
            timeout = None
        )


###############################################
# get the file permissions via octal notation #
# example '644' as rw+r+r                     #
###############################################
def get_file_permissions( filepath=None ) -> string:
    mask = oct(os.stat(filepath).st_mode)[-3:]
    return str(mask)


###############################################
# set the file permissions via octal notation #
# example '644' as rw+r+r                     #
###############################################
def set_file_permissions( filepath=None, permissions=None ):
    try :
        cmd_str = '/usr/bin/sudo chmod ' + permissions + ' ' + filepath
        p = subprocess.Popen( cmd_str, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True )
        _p_status = p.wait( timeout=30 )
    except Exception as e:
         raise Exception ( "file rechten fout. " + str(e) )


###############################################
# set the file owner and group                #
# example 'p1mon:root' as                     #
###############################################
def set_file_owners( filepath=None, owner_group='p1mon:p1mon'):
    try :
        cmd_str = '/usr/bin/sudo chown ' + owner_group + ' ' + filepath
        p = subprocess.Popen( cmd_str, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True )
        _p_status = p.wait( timeout=30 )
    except Exception as e:
         raise Exception ( "file owner:group fout. " + str(e) )


################################################
# expand the SDHC card to maximum size         #
# a reboot is necessary to activate this       #
################################################
def expand_rootfs(): 
    try :
        cmd_str = '/usr/bin/sudo raspi-config --expand-rootfs'
        p = subprocess.Popen( cmd_str, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True )
        _p_status = p.wait( timeout=30 )
    except Exception as _e:
        #print ("error ", str(_e))
        pass

################################################
# sync filesytem buffers to device             #
################################################
def file_system_sync():
    try :
        cmd_str = "/bin/sync"
        p = subprocess.Popen( cmd_str, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True )
        #_stdout=subprocess.PIPE
        #output, _err = p.communicate()
        _p_status = p.wait( timeout=30 )
    except Exception as _e:
        #print ("error ", str(_e))
        pass

################################################################
# move a file to the destination and set the rights to 644 and #
# ownership to root:root                                       #
# the copy flag does a copy and not a move                     #
# OS user must have SUDO priviliges                            #
################################################################
def move_file_for_root_user( source_filepath=None, destination_filepath=None , permissions='644', copyflag=False, flog=None ):

    #print ( source_filepath, destination_filepath , permissions )

    if not os.path.isfile( source_filepath ):
        raise Exception( "bestand " + source_filepath  + " niet gevonden." )

    if copyflag == False:
        cmd = '/usr/bin/sudo mv -f ' + source_filepath + ' ' + destination_filepath
    else:
        cmd = '/usr/bin/sudo cp -f ' + source_filepath + ' ' + destination_filepath

    #print ( cmd )
    #if os.system( cmd ) > 0:
    #    raise Exception ( "verplaatsen van file error " + source_filepath  )
    r = process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=True,
        flog=flog 
    )
    if r[2] > 0:
         raise Exception ( "verplaatsen van file error " + source_filepath  )

    cmd = '/usr/bin/sudo chmod ' + permissions + ' ' + destination_filepath
    #print( cmd )
    #if os.system( cmd ) > 0:
    #    raise Exception ( "file eigenaarschap fout. " + destination_filepath )
    r = process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=True,
        flog=flog 
    )
    if r[2] > 0:
         raise Exception ( "file eigenaarschap fout. " + destination_filepath )

    cmd = '/usr/bin/sudo chown root:root ' + destination_filepath
    #print( cmd )
    #if os.system( cmd ) > 0:
    #    raise Exception ( "file rechten fout. " + destination_filepath )
    r = process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=True,
        flog=flog 
    )
    if r[2] > 0:
        raise Exception ( "file rechten fout. " + destination_filepath )

######################################################
# get the size of used filepath values are retured   #
# in the dict.                                       #
######################################################
def filepath_use( filepath, unit='B' ):

    r = FILEPATH_SIZE
    try:

        #raise("!TEST!")

        parts = str(psutil.disk_usage( filepath )).split()
        r['unit'] = unit
        r['space_total'] = int(parts[0].split('=')[1].replace(',',''))
        r['space_used']  = int(parts[1].split('=')[1].replace(',',''))
        r['space_free']  = int(parts[2].split('=')[1].replace(',',''))
        r['pct_used'] =  round( float( r['space_used'] / r['space_total'] * 100) , 1 )
        r['pct_free'] =  round( 100 - r['pct_used'], 1 )

        # unit conversion
        divider = 1
        if unit == 'K':
            divider =  1024
        elif unit == 'M':
            divider =  1024000
        elif unit == 'G':
            divider =  1024000000

        r['space_total'] = math.floor( r['space_total'] / divider )
        r['space_used']  = math.floor( r['space_used'] / divider )
        r['space_free']  = math.floor( r['space_free'] / divider )

    
    except Exception as e:
            raise Exception( "geen data gevonden " + str(e) )
    
    return r