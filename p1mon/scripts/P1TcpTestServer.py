# run manual with ./P1TcpTestServer

import const
import filesystem_lib
import inspect
import logger
import os
import pwd
import sys
import socket
import time

# programme name.
prgname = 'P1TcpTestServer'

def Main( argv ):

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 2223         # Port to listen on (non-privileged ports are > 1023)

    flog.info( inspect.stack()[0][3] + ": adres is " + str(HOST) + " via poort " + str(PORT) )

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    flog.info( inspect.stack()[0][3] + ": server succesfull start sending dummy data, when connected." )
                    while True:
                        conn.sendall( get_p1_data_encoded() )
                        flog.info( inspect.stack()[0][3] + ": send data. warning test data" )
                        time.sleep( 10 )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": server error " + str(e.args[0]) + " restart server in 1 seconds." )
            time.sleep( 1 )

def get_p1_data_encoded():

    data =\
"""
/ISK5\2M550E-1013

1-3:0.2.8(50)
0-0:1.0.0(240616101321S)
0-0:96.1.1(4530303533303037353139373634303139)
1-0:1.8.1(003450.903*kWh)
1-0:1.8.2(003369.859*kWh)
1-0:2.8.1(002560.690*kWh)
1-0:2.8.2(005695.083*kWh)
0-0:96.14.0(0001)
1-0:1.7.0(00.000*kW)
1-0:2.7.0(00.221*kW)
0-0:96.7.21(00010)
0-0:96.7.9(00007)
1-0:99.97.0(5)(0-0:96.7.19)(191122053729W)(0000000282*s)(210518105917S)(0000000469*s)(210611152104S)(0000002774*s)(220902151412S)(0000000243*s)(230320153228W)(0000002632*s)
1-0:32.32.0(00014)
1-0:32.36.0(00045)
0-0:96.13.0()
1-0:32.7.0(233.8*V)
1-0:31.7.0(001*A)
1-0:21.7.0(00.000*kW)
1-0:22.7.0(00.219*kW)
0-1:24.1.0(003)
0-1:96.1.0(4730303634303032303134343233383230)
0-1:24.2.1(211123154959W)(01421.163*m3)
0-1:24.2.1(170108160000W)(15835.795*m3)
!BF27
"""

    return data.encode('utf-8')


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

