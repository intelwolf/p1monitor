# run manual with ./P1NetworkConfig

import argparse
import const
import inspect
import filesystem_lib
import logger
import os
import pwd
import sqldb
import signal
import sys
import network_lib
import process_lib

# programme name.
prgname = 'P1NetworkConfig'

config_db    = sqldb.configDB()
#rt_status_db = sqldb.rtStatusDb() # remove in 1.8.0
space_adjust = 43

def Main( argv ):

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument( '-h', '--help',
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument( '-dev', '--devicereload',
        required=False,
        choices=['eth0', 'wlan0' ],
        help="Maak de netwerk instellingen actief. Deze actie verbreekt de verbinding voor een paar seconden." )

    """
    parser.add_argument( '-dgw', '--defaultgateway',
        required=False,
        action="store_true",
        help="stel de default gateways in, dit is meestal het adres van je router." )

    parser.add_argument( '-dns', '--dnsserver',
        required=False,
        action="store_true",
        help="stel het ip adres in van de dnsserver, dit is meestal het adres van je router." )
    """

    """
    parser.add_argument( '-f', '--forced',
        required=False,
        action="store_true",
        help="De optie wordt altijd uitgevoerd, bijvoorbeeld het aanmaken van een een configuratie bestand dat al bestaat." )
    """

    parser.add_argument('-fp', '--filepath', 
        required=False,
        help="gebruik dit path en filename voor opties die dit ondersteunen." )

    """
    parser.add_argument( '-rdgw', '--removedefaultgateway',
        required=False,
        action="store_true",
        help="verwijder default gateway." )

    parser.add_argument( '-rdns', '--removednsserver',
        required=False,
        action="store_true",
        help="verwijder het ip adres in van de dnsserver, dit is meestal het adres van je router." )
    """

    parser.add_argument( '-ldhcp', '--reloaddhcp',
        required=False,
        action="store_true",
        help="Reload de DHCP daemon" )

    parser.add_argument( '-cdhcp', '--defaultdhcpconfig',
        required=False,
        action="store_true",
        help="Maak een dhcp daemon config file aan." )

    """
    parser.add_argument( '-rsip', '--removestaticip',
        required=False,
        choices=['eth0', 'wlan0' ],
        help="verwijder het vaste IP adres voor het opgegeven device. Als DHCP actief is dan wordt er een DHCP adres toegewezen." )
    """

    """
    parser.add_argument( '-cdns', '--checkandrecoverdns',
        required=False,
        action="store_true",
        help="Controleerd of internet sites te bereiken zijn via een FQDN zo niet maakt een standaard DNS resolv configuratie aan" )
    """
    
    """
    parser.add_argument( '-sip', '--staticip',
        required=False,
        choices=['eth0', 'wlan0' ],
        help="stel een vast IP adress in voor het opgegeven device." )
    """

    args = parser.parse_args()
    #print (args)

    #########################################################
    # all processes need to try to restore from disk to ram #
    #########################################################
    disk_to_ram_restore()

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init( const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    """
    try:
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(2)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")
    """

    if args.defaultdhcpconfig == True:
        if args.filepath != None:
            filepath = args.filepath
        else:
            filepath = network_lib.DHCPCONFIG
        flog.info( inspect.stack()[0][3] + ": DHCP config file wordt aangemaakt op de locatie " + str(filepath) )
        dhcpconfig = network_lib.DhcpcdConfig( filename=filepath, config_db=config_db, flog=flog )
        dhcpconfig.set_config_from_data()
        flog.info( inspect.stack()[0][3] + ": DHCP config file gereed.")
        sys.exit( 0 )

    if args.reloaddhcp == True:
        flog.info( inspect.stack()[0][3] + ": DHCP deamon herstart.")
        if network_lib.reload_dhcp_deamon( flog=flog ) == False:
             flog.error( inspect.stack()[0][3] + ": DHCP deamon herstart fout.")
             sys.exit( 1 )
        flog.info( inspect.stack()[0][3] + ": DHCP deamon herstart gereed.")
        sys.exit( 0 )

    if args.devicereload != None:
        flog.info( inspect.stack()[0][3] + ": Herstart/load van netwerk voor device " + str(args.devicereload) + " gestart.")
        if args.devicereload== 'wlan0':
            network_lib.restart_network_device( device='wlan0', flog=flog )
        else: 
            network_lib.restart_network_device( device='eth0', flog=flog )
        flog.info( inspect.stack()[0][3] + ": Herstart/load van netwerk voor device " + str(args.devicereload) + " gereed.")
        sys.exit( 0 )


    flog.info( inspect.stack()[0][3] + ": gestopt zonder uitgevoerde acties, geef commandline opties op." )
    sys.exit ( 1 ) # should be an error when there are no options given.

def disk_to_ram_restore():
    process_lib.run_process( 
        cms_str='/p1mon/scripts/P1DbCopy --allcopy2ram',
        use_shell=True,
        give_return_value=True,
        flog=flog 
        )

########################################################
# close program when a signal is recieved.             #
########################################################
def saveExit(signum, frame):
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
