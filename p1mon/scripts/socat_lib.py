#################################
# socat support functions       #
#################################

from cmath import e
import util
import network_lib
import filesystem_lib
import process_lib

SOCATDEVICE                 ='/dev/socatcom1'
SOCATSERVICEFILE            = '/etc/systemd/system/socat.service'
SOCAT_TMP_EXT               = '_socat.tmp'
SOCAT_ENABLE_COMMAND_LIST   = [ 'sudo systemctl daemon-reload', 'sudo systemctl enable socat.service', 'sudo systemctl start socat.service' ]
SOCAT_DISABLE_COMMAND_LIST  = [ 'sudo systemctl disable socat.service', 'sudo systemctl stop socat.service', 'sudo systemctl daemon-reload' ]
SOCAT_IS_ACTIVE_COMMAND     = 'sudo systemctl is-active socat.service'

socat_service_file_template =\
"""
###P1HEADER###
[Unit]
Description=Socat Serial Loopback
After=network.target

[Service]
Type=simple
StandardOutput=inherit
StandardError=inherit
ExecStart=sudo /usr/bin/socat -T60 pty,link=###SOCATDEVICE##,rawer,group-late=dialout,mode=660 tcp:###SOCATREMOTEIP###:###SOCATREMOTEPORT###,retry=forever,interval=30
ExecStartPost=- sudo -u p1mon /p1mon/scripts/P1SocatConfig --succestimestamp 2>&1 >/dev/null
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target shutdown.target reboot.target halt.target
"""

class Socat():

    def __init__( self, statusdb=None, configdb=None, flog=None ):
        self.statusdb               = statusdb
        self.configdb               = configdb
        self.did_send_data          = False
        self.flog                   = flog
        self.socat_remote_ip        = None
        self.socat_remote_port      = None
        self.buffer                 = None
        self.tmp_service_file       = None

    ###################################################################
    # disable the service and update the systemd service file         #
    ###################################################################
    def disable_service( self ):
        self._execute_commands( command_list=SOCAT_DISABLE_COMMAND_LIST )

    ###################################################################
    # enable the service and update the systemd service file          #
    ###################################################################
    def enable_service( self ):
        self._read_config_from_db()
        self._create_service_file_buffer()
        self.tmp_service_file = filesystem_lib.generate_temp_filename() + SOCAT_TMP_EXT
        self._write_buffer()
        filesystem_lib.move_file_for_root_user( 
            source_filepath=self.tmp_service_file, 
            destination_filepath=SOCATSERVICEFILE, 
            permissions='644', 
            copyflag=False, 
            flog=self.flog
            )
        self._execute_commands( command_list=SOCAT_ENABLE_COMMAND_LIST)
        self._service_is_running()

    #############################################################
    # set the succes timestamp in the status database           #
    #############################################################
    def set_succes_timestamp( self ):
        self._set_status_timestamp_db( index=128 )


    ##################################################################
    # update the status db with the timestamp                        #
    # index = id in the config db                                    #
    # id 128 = succes timestamp                                      #
    ##################################################################
    def _set_status_timestamp_db( self, index=128 ):
        try:
            self.statusdb.timestamp( index, self.flog )
        except Exception as e:
            raise Exception( "status db timestamp fout " + str(e.args[0]) )

    #################################################################
    # check with sudo systemctl is-active is the service is running #
    # return True when running                                      #
    #################################################################
    def _service_is_running( self ):
        r = process_lib.run_process(cms_str=SOCAT_IS_ACTIVE_COMMAND,use_shell=True,give_return_value=True,flog=self.flog,timeout=9)
        if r[2] != 0:
            raise Exception( SOCAT_IS_ACTIVE_COMMAND + " fout " + str(r[1].decode("utf-8").strip() ) )
        else:
            if str(r[0].decode("utf-8").strip()) == 'active':
                self.set_succes_timestamp()

    ###################################################################
    # run the set of systemd commands to enable and start the service #
    ###################################################################
    def _execute_commands( self, command_list=None ):
        for cmd in command_list:
            r = process_lib.run_process(cms_str=cmd,use_shell=True,give_return_value=True,flog=self.flog,timeout=9)
            if r[2] != 0:
                raise Exception( cmd + " fout "  + str(r[1].decode("utf-8").strip() ) )
           
    ###################################################################
    # write the buffer to file                                        #
    ###################################################################
    def _write_buffer( self ):
        try:
            fp = open( self.tmp_service_file, 'w')
            fp.write( self.buffer )
            fp.close()
        except Exception as e:
            raise Exception( " tijdelijk config file schrijf fout, gestopt(" + self.tmp_service_file + ") melding:" + str( e.args ) )

    ###################################################################
    # read the config information from the config database            #
    ###################################################################
    def _read_config_from_db( self ):
        
        _id, ip, _label = self.configdb.strget( 198, self.flog )
        if len( ip.strip() ) == 0:
            raise Exception( "SOC remote IP adres is niet te lezen of niet gezet" )
        else:
            self.socat_remote_ip = ip

        try:
            network_lib.is_valid_ip_adres( ip_adress=self.socat_remote_ip)
        except Exception as e:
            raise Exception( "IP adres is niet correct " + str(e.args[0]))

        _id, port, _label = self.configdb.strget( 199, self.flog )
        if len( port.strip() ) == 0:
            raise Exception( "SOC remote poort nummer is niet te lezen of niet gezet" )
        else:
            self.socat_remote_port = port
            try:
                if int( self.socat_remote_port ) < 1 or int( self.socat_remote_port ) > 65353:
                    raise Exception( "opgegeven poort "  + str(port) )
            except Exception as e:
                raise Exception( "poort is niet correct " + str(e.args[0]))


    ###################################################################
    # create the service file from a template and change the dynamic  #
    # fields in the file                                              #
    ###################################################################
    def _create_service_file_buffer( self ):
        self.buffer = socat_service_file_template.replace( '###P1HEADER###', self._generate_header_string() )
        self.buffer = self.buffer.replace( '###SOCATDEVICE##'     , SOCATDEVICE )
        self.buffer = self.buffer.replace( '###SOCATREMOTEIP###'  , self.socat_remote_ip )
        self.buffer = self.buffer.replace( '###SOCATREMOTEPORT###', self.socat_remote_port )
        self.flog.debug( __class__.__name__  + ": service config buffer:\n" + str( self.buffer ) )


    ########################################################
    # header timestamp string                              #
    ########################################################
    def _generate_header_string( self ):
        str = \
    '###############################\n\
# Gegenereerd door P1-monitor.#\n\
# op '+ util.mkLocalTimeString() + '      #\n'+\
    '###############################\n'
        return str