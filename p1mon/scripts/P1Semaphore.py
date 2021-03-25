#!/usr/bin/python3
import argparse
import const
import sys
import inspect
import os
import semaphore3

from logger import fileLogger, logging
from util import setFile2user
from os import umask

prgname = 'P1Semaphore'

def Main(argv): 
    flog.info("Start van programma.")

    parser = argparse.ArgumentParser(description="write semaphore file, dont add extention p1mon")
    parser.add_argument('-n', '--name', required=True)
    args = parser.parse_args()

    if args.name != None:
        semaphore3.writeSemaphoreFile( args.name, flog )
        flog.debug(inspect.stack()[0][3]+" semafoor file " + args.name + " gemaakt." )
    flog.info("Stop van programma.")

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG+prgname + ".log"
        setFile2user( logfile, 'p1mon' )
        flog = fileLogger(logfile,prgname)
        #### aanpassen bij productie
        flog.setLevel( logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str( e.args[0] ) )
        sys.exit(10) #  error: no logging check file rights

    Main( sys.argv[1:] )
