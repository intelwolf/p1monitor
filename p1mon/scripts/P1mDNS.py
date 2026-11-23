# run manual with ./P1NginxConfig

import argparse
import const
import filesystem_lib
import glob
import inspect
import logger
import os
import pwd
import re
import sqldb
import subprocess
import sys
import tempfile
import time

# programme name.
prgname = 'P1mDNS'
DEFAULT_MDNS_NAME = "p1monitor"
AVAHI_CONFIG_FILE = "/etc/avahi/avahi-daemon.conf"
HOSTNAME_AVAHI = "host-name="
AVAHI_CONFIG_FILE_TMP_EXT = '_avahi_config.tmp'

config_db    = sqldb.configDB()
rt_status_db = sqldb.rtStatusDb()

default_avahi_config_file =\
"""
# This file is part of avahi.
#
# avahi is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# avahi is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with avahi; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.

# See avahi-daemon.conf(5) for more information on this configuration
# file!

[server]
#host-name=foo
#domain-name=local
#browse-domains=0pointer.de, zeroconf.org
use-ipv4=yes
use-ipv6=yes
allow-interfaces=eth0,wlan0
#deny-interfaces=eth1
#check-response-ttl=no
#use-iff-running=no
#enable-dbus=yes
#disallow-other-stacks=no
#allow-point-to-point=no
#cache-entries-max=4096
#clients-max=4096
#objects-per-client-max=1024
#entries-per-entry-group-max=32
ratelimit-interval-usec=1000000
ratelimit-burst=1000

[wide-area]
enable-wide-area=yes

[publish]
#disable-publishing=no
#disable-user-service-publishing=no
#add-service-cookie=no
#publish-addresses=yes
publish-hinfo=no
publish-workstation=no
#publish-domain=yes
#publish-dns-servers=192.168.50.1, 192.168.50.2
#publish-resolv-conf-dns-servers=yes
#publish-aaaa-on-ipv4=yes
#publish-a-on-ipv6=no

[reflector]
#enable-reflector=no
#reflect-ipv=no
#reflect-filters=_airplay._tcp.local,_raop._tcp.local

[rlimits]
#rlimit-as=
#rlimit-core=0
#rlimit-data=8388608
#rlimit-fsize=0
#rlimit-nofile=768
#rlimit-stack=8388608
#rlimit-nproc=3

"""

def Main( argv ): 

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument( '-c', '--configure', 
        required=False,
        nargs='?', 
        const='',      # if configure is selected but has no value
        default=False, # if configure is not selected, not needed but what the heck.
        help="Configure by the value stored in the configuration database or the default hostname " + str(DEFAULT_MDNS_NAME) )

    parser.add_argument( '-d', '--default', 
        required=False,
        action="store_true",
        help="remove configuration and set to default system hostname.")
    
    parser.add_argument( '-s', '--status', 
        required=False,
        action="store_true",
        help="set the name of the mDNS name in the status database")

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Show help text and stop.')

    args = parser.parse_args()
    flog.debug( inspect.stack()[0][3] + ": args = " + str(args) )


    if args.configure != False:
        flog.info( inspect.stack()[0][3] + ": configure selected.")
        open_db()

        try: 
            buffer = read_avahi_config_file()
            #read database to see if an other name is set

            set_hostname = ""
            if len(args.configure) > 0:
                set_hostname = args.configure
            else:
                try:
                    _id, mDNS_config, _label = config_db.strget( 229, flog )
                    if len(mDNS_config) > 0:
                        set_hostname = mDNS_config.strip()
                except Exception as e:
                    flog.warning( inspect.stack()[0][3] + ": config database read error " + str(e.args[0]) )

            if len(set_hostname) == 0: 
                set_hostname = DEFAULT_MDNS_NAME

            flog.info( inspect.stack()[0][3] + ": setting mDNS name to " + str(set_hostname) + ".local" )
            
            clean_buffer = change_avahi_buffer(hostname=set_hostname, listbuffer=buffer)
            write_avahi_config_file( buffer=clean_buffer, file=AVAHI_CONFIG_FILE, flog=flog )
            config_file_fail_save()
            restart_avahi_daemon()
            time.sleep(3)  # wait for the daemon to restart
            set_mDNS_name_to_status_db()
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": stop: " + str(e.args[0]) )
            sys.exit(1)

        flog.info( inspect.stack()[0][3] + ": configure done.")
        sys.exit(0)


    if args.default != False:
        flog.info( inspect.stack()[0][3] + ": default configuration selected.")
        try: 
            open_db()
            write_default_config_file()
            restart_avahi_daemon()
            time.sleep(3)  # wait for the daemon to restart
            set_mDNS_name_to_status_db()
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": default failed stop: " + str(e.args[0]) )
            sys.exit(1)

        flog.info( inspect.stack()[0][3] + ": default configuration done.")
        sys.exit(0)


    if args.status != False:
        try: 
            open_db()
            set_mDNS_name_to_status_db(verbose=1)
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": status update stop: " + str(e.args[0]) )
            sys.exit(1)

        flog.info( inspect.stack()[0][3] + ": status update done.")
        sys.exit(0)

    # default message when nothing is selected
    flog.warning( inspect.stack()[0][3] + ": no options selected, use -h for help.")
    sys.exit(0)


#########################################################
# read the mDNS name from systemctl status avahi-daemon #
# and update the status database                        #
# verbose is do not show the status as output           #
#########################################################
def set_mDNS_name_to_status_db(verbose=0):

    mDNS_name = "??????"
    try:

        command_args = ["/usr/bin/systemctl","status", "avahi-daemon"]
        proc = subprocess.Popen(command_args, stdout=subprocess.PIPE)

        for line in proc.stdout:
            line_tmp = line.decode('utf-8').rstrip()
            if line_tmp.find('avahi-daemon: running') != -1: # found the correct line
                mDNS_name = re.sub(r'[^a-zA-Z0-9.]', '', line_tmp.split("[")[1]) # Remove all non-alphabet characters
                rt_status_db.strset( mDNS_name, 139, flog ) 

    except Exception as e:
        raise Exception("setting the status failed " + str(e.args)) 
    
    flog.info( inspect.stack()[0][3] + ": mDNS name is set to " + mDNS_name)


####################################################
# remove one or more temporary files               #
####################################################
def clean_tmp_files():
    files = glob.glob( tempfile.gettempdir() + '/*' + AVAHI_CONFIG_FILE_TMP_EXT )
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": tmp file  " + f + " could not be deleted: " + str(e.args) )
   
####################################################
# write config file and set file properties        #
# return true, all is well or false on a fatal or  #
# a disappointing result                           #
####################################################
def  write_avahi_config_file( buffer=None, file=None, flog=None ) -> bool:

    str_buffer = ""
    for x in buffer:
        str_buffer += x + "\n"

    # get rid of old tmp files if any.
    clean_tmp_files()

    tmp_file = filesystem_lib.generate_temp_filename() + AVAHI_CONFIG_FILE_TMP_EXT

    try:

        ##################################################################
        # maken temporary file so we can move the file to root ownership #
        ##################################################################
        try:
            fp = open( tmp_file, 'w')
            fp.write( str_buffer  )
            fp.close()
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": tmp config file write error (" + tmp_file  + ") message:" + str(e.args) )
            return False

        try:
            filesystem_lib.move_file_for_root_user( source_filepath=tmp_file, destination_filepath=AVAHI_CONFIG_FILE , permissions='644', copyflag=False, flog=flog )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": " + AVAHI_CONFIG_FILE + "could not be changed message:" + str(e.args) )
            return False
        
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": config file " + file + " message:" + str(e.args) )
        clean_tmp_files()
        return False
    
    return True


#############################################################################
# places the hostname in the buffer if the hostname is not None             #
# the buffer should not contain the hostname parameter                      #
#############################################################################
def change_avahi_buffer(hostname=None, listbuffer=None):
    #flog.debug( inspect.stack()[0][3] + ": hostname = " + str(hostname) + " listbuffer = " + str(listbuffer))

    if hostname != None:
        try:
            index = listbuffer.index('[server]')
            #print("String found at index", index)
            listbuffer.insert(index+1,HOSTNAME_AVAHI + str(hostname))
            return listbuffer
        except ValueError:
           pass

#############################################################################
# read avahi config file and remove the host parameter from the config file #
#############################################################################
def read_avahi_config_file():

    list_buffer = []
    try:
        with open( AVAHI_CONFIG_FILE, "r", encoding="utf-8") as file:
            for line in file:
                clean_line = line.strip()
                if clean_line.startswith(HOSTNAME_AVAHI):
                    flog.debug( inspect.stack()[0][3] + ": host-name found and not copied to buffer and that is good thing." )
                    pass
                else:
                    list_buffer.append(clean_line)

        return list_buffer
    
    except Exception as e:
        raise Exception("config file " + AVAHI_CONFIG_FILE + " read error") 
        

def open_db():

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database could not be opened " + const.FILE_DB_CONFIG + " message: " + str(e.args[0]) )
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database table " + const.DB_CONFIG_TAB + " successfully opened.")
    
    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database could not be opened " + const.FILE_DB_STATUS + " message: "+str(e.args[0]))
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database table " + const.DB_STATUS_TAB + " successfully opened.")


#############################################################################
# read check if there is an config file if not replace it with default one  #
#############################################################################
def config_file_fail_save():

    try:
        buffer = read_avahi_config_file()
        
        res = list(filter(lambda x: 'avahi' in x, buffer))
        #print(len(res))
        if len(res) > 1:  
            flog.info( inspect.stack()[0][3] + ": " + AVAHI_CONFIG_FILE + " validation succeeded.")
            return # all is well.
        else:
            raise Exception("config file " + AVAHI_CONFIG_FILE + " seems to be wrong ")    
    except Exception as e:

        flog.warning( inspect.stack()[0][3] + ": " + AVAHI_CONFIG_FILE + " validation failed, trying to recover.")
        # make a default standard config file
        try:
            write_default_config_file()
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": config file message: " + str(e.args) )
            clean_tmp_files()


#############################################################################
# write a default avahi config file, this uses the hostname of the rpi      #
# to set the <hostname>.local name                                          #
#############################################################################
def write_default_config_file():

    tmp_file = filesystem_lib.generate_temp_filename() + AVAHI_CONFIG_FILE_TMP_EXT

    ##################################################################
    # maken temporary file so we can move the file to root ownership #
    ##################################################################
    try:
        fp = open( tmp_file, 'w')
        fp.write( default_avahi_config_file  )
        fp.close()
    except Exception as e:
        raise Exception( "tmp config file write error (" + tmp_file  + ") message:" + str(e.args) )    
    
    try:
        filesystem_lib.move_file_for_root_user( source_filepath=tmp_file, destination_filepath=AVAHI_CONFIG_FILE , permissions='644', copyflag=False, flog=flog )
    except Exception as e:
        raise Exception(AVAHI_CONFIG_FILE + "could not be copied message:" + str(e.args))   
        
   
#############################################################################
# just restart the avahi daemon                                             #
#############################################################################
def restart_avahi_daemon():
  
    try:
        cmd = '/usr/bin/sudo systemctl restart avahi-daemon'
        subprocess.Popen( [ cmd ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": restart of avahi-daemon failed " + str(e.args) )
        return
    
    flog.info( inspect.stack()[0][3] + ": restart avahi-daemon done." )

    
########################################################
# init                                                 #
########################################################
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        filepath = const.DIR_FILELOG + prgname + ".log"
        try:
            filesystem_lib.set_file_permissions( filepath=filepath, permissions='664' )
            filesystem_lib.set_file_owners( filepath=filepath, owner_group='p1mon:p1mon' )
        except:
            pass # don nothing as when this fails, it still could work
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname) 
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)

    Main(sys.argv[1:])
