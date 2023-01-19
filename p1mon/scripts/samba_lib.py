
####################################################################
# samba file server lib                                            #
# service --status-all shows running services                      #
####################################################################
import filesystem_lib
import glob
import inspect
import process_lib
import os
import tempfile
import time
import util

SAMBA_TMP_EXT        = '_samba.tmp'
SAMBA_CONFIG_FILE    = '/etc/samba/smb.conf'
SAMBA_PRIVATE_FOLDER = '/run/samba/private'
SAMBA_LOG_FOLDER     = '/run/samba'
FILESHARE_MODE_OFF   = 'uit'
FILESHARE_MODE_DATA  = "data"
FILESHARE_MODE_DEV   = "dev"

class Samba:

    #######################################################
    # class init function                                 #
    #######################################################
    def __init__(self, flog=None):
        self.flog = flog
        self.__make_ram_folders()

    ########################################################
    # set the possible file shares and stop or restart the #
    # SAMBA services                                       #
    # return true when all is well or throw an exception   #
    ########################################################
    def set_share_mode( self, fileshare_mode = FILESHARE_MODE_OFF ):

        if fileshare_mode == FILESHARE_MODE_OFF:
            self.stop_server()
            self.flog.debug( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": service gestopt." )
            return True

        buffer = smbd_base_config
        buffer = buffer.replace( '###P1HEADER###', self.__generate_header_string() )
        buffer = buffer.replace( '###LOGFOLDER###', SAMBA_LOG_FOLDER )
        buffer = buffer.replace( '###PRIVATEFOLDER###', SAMBA_PRIVATE_FOLDER )

        if fileshare_mode == FILESHARE_MODE_DATA:
            buffer = buffer.replace( '###P1MONDATASHARE###', smbd_config_p1mon_data )
            buffer = buffer.replace( '###P1MONSHARE###', '' )
            self.flog.debug( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": buffer =\n "  + buffer )
            if self.__write_buffer( buffer=buffer, file=SAMBA_CONFIG_FILE ) == False:
                self.flog.error( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": configuratie file fout voor de /data share." )
                return False

            self.restart_server()
            self.flog.debug( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": service gestart met /data share." )
            return True

        if fileshare_mode == FILESHARE_MODE_DEV:
            buffer = buffer.replace( '###P1MONSHARE###', smbd_config_p1mon )
            buffer = buffer.replace( '###P1MONDATASHARE###', smbd_config_p1mon_data )
            self.flog.debug( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": buffer =\n "  + buffer )
            
            if self.__write_buffer( buffer=buffer, file=SAMBA_CONFIG_FILE ) == False:
                self.flog.error( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": configuratie file fout voor /data en /p1mon shares." )
                return False

            self.restart_server()
            self.flog.debug( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": service gestart met /data en /p1mon share." )
            return True


    def start_server( self ):
        self.flog.info( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": " + "Server wordt gestart." )
        self.__run_process( cmd="start" )
        self.__run_process( cmd="start", service="nmbd" )
      

    def stop_server( self ):
        self.flog.info( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": " + "Server wordt gestopt." )
        self.__run_process( cmd="stop" )
        self.__run_process( cmd="stop", service="nmbd" )
        

    def restart_server( self ):
        self.flog.info( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": " + "Server wordt herstart." )
        self.__run_process( cmd="restart" )
        self.__run_process( cmd="restart", service="nmbd" )


    def __make_ram_folders( self ):
        try:
            filesystem_lib.create_folder( SAMBA_PRIVATE_FOLDER )
        except Exception as e:
            self.flog.critical( __class__.__name__ + ":" + inspect.stack()[0][3] + ": samba folder " + SAMBA_PRIVATE_FOLDER + " kan niet worden aangemaakt. " + str(e.args) )

    ########################################################
    # header timestamp string                              #
    ########################################################
    def __generate_header_string( self ):
        str = \
'###############################\n\
# Gegenereerd door P1-monitor.#\n\
# op '+ util.mkLocalTimeString() + '      #\n'+\
'###############################\n'
        return str

    def __run_process( self, cmd=None, service="smbd" ):
        cmd = "sudo systemctl " + str( cmd ) + " " + str( service )
        r = process_lib.run_process( 
                        cms_str = cmd,
                        use_shell=True,
                        give_return_value=True,
                        flog=self.flog,
                        timeout=None
        )
        if r[2] > 0:
            self.flog.error(inspect.stack()[0][3]+" Server " + str(cmd) + " gefaald.")
        self.flog.debug( __class__.__name__ + ":" + inspect.stack()[0][3] +  ": " + "cmd = " + cmd )

    ####################################################
    # remove one or more temporary files               #
    ####################################################
    def __clean_tmp_files( self ):
        files = glob.glob( tempfile.gettempdir() + '/*' + SAMBA_TMP_EXT )
        for f in files:
            try:
                os.remove( f )
            except Exception as e:
                self.flog.warning( __class__.__name__ + ":" + inspect.stack()[0][3] + ": tijdelijk bestand " + f + " kan niet worden gewist: " + str(e.args) )

    ####################################################
    # write config file and set file properties        #
    # return true, all is well or false on a fatal or  #
    # a disappointing result                           #
    ####################################################
    def __write_buffer( self, buffer=None, file=None ) -> bool:

        # get rid of old tmp files if any.
        self.__clean_tmp_files()

        tmp_file = filesystem_lib.generate_temp_filename() + SAMBA_TMP_EXT

        try:

            if os.path.exists( file ):
                # os.system( '/usr/bin/sudo rm ' + file ) 1.8.0 upgrade
                process_lib.run_process( 
                    cms_str='/usr/bin/sudo rm ' + file,
                    use_shell=True,
                    give_return_value=False,
                    flog=self.flog 
                )

            ##################################################################
            # maken temporary file so we can move the file to root ownership #
            ##################################################################
            try:
                fp = open( tmp_file, 'w')
                fp.write( buffer )
                fp.close()
            except Exception as e:
                self.flog.critical( __class__.__name__ + ":" + inspect.stack()[0][3] + ": config file schrijf fout, gestopt(" + file + ") melding:" + str(e.args) )
                return False

            ##################################################################
            # move the file to the nginx folder and set ownership and rights #
            ##################################################################
            #move_file_for_root_user( source_filepath=None, destination_filepath=None , permissions='644', copyflag=False, flog=None ):
           
            if filesystem_lib.move_file_for_root_user( source_filepath=tmp_file, destination_filepath=file, flog=self.flog ) == False:
                    return False
           
        except Exception as e:
            self.flog.critical( inspect.stack()[0][3] + ": config file schrijf fout, gestopt(" + file + ") melding:" + str(e.args) )
            self.clean_tmp_files()
            return False
        
        return True


smbd_config_p1mon =\
"""
[p1mon]
    path = /p1mon
    browsable = yes
    writeable = yes
    guest ok = yes
"""

smbd_config_p1mon_data =\
"""
[p1mondata]
    path = /p1mon/data
    browsable = yes
    read only = yes
    guest ok = yes
"""

smbd_base_config =\
"""

###P1HEADER###

[global]
    guest account = nobody

dns proxy = no

log file = ###LOGFOLDER###/log.%m

max log size = 1000

logging = syslog@1 ###LOGFOLDER###/log.%m

panic action = /usr/share/samba/panic-action %d

encrypt passwords = true

passdb backend = tdbsam
obey pam restrictions = yes

unix password sync = yes

passwd program = /usr/bin/passwd %u
passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .

pam password change = yes

map to guest = bad user

# p1mon special redirect so writes go to ram and not flash disk.
#private dir = /var/log/samba/private
private dir = ###PRIVATEFOLDER###

[homes]
    comment = Home Directories
    browseable = no
    read only = yes
    create mask = 0700
    directory mask = 0700
    valid users = %S
###P1MONSHARE###
###P1MONDATASHARE###

"""
