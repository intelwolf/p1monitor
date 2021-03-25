#!/usr/bin/python3
import argparse
import os
import sys
import const
import zlib
import inspect
import signal
import zipfile
import datetime
import getopt
import json
import pwd
import shutil
import subprocess
import util

from semaphore3 import writeSemaphoreFile
from sqldb import *
from logger import *
from util import mkLocalTimeString,setFile2user
from datetime import datetime, timedelta
from shutil import *
from os     import umask
from subprocess import run

prgname = 'P1SqlExport'

config_db             = configDB()
e_db_history_min      = SqlDb2() 
e_db_history_uur      = SqlDb3() 
e_db_history_dag      = SqlDb4() 
e_db_history_maand    = SqlDb4() 
e_db_history_jaar     = SqlDb4() 
e_db_financieel_dag   = financieelDb()
e_db_financieel_maand = financieelDb()
e_db_financieel_jaar  = financieelDb()
weer_db               = currentWeatherDB()
weer_history_db_uur   = historyWeatherDB()
weer_history_db_dag   = historyWeatherDB()
weer_history_db_maand = historyWeatherDB()
weer_history_db_jaar  = historyWeatherDB()
temperature_db        = temperatureDB()
#watermeter_db_uur     = WatermeterDB()
#watermeter_db_dag     = WatermeterDB()
#watermeter_db_maand   = WatermeterDB()
#watermeter_db_jaar    = WatermeterDB()
watermeter_db         = WatermeterDBV2()
fase_db               = PhaseDB()
power_production_db   = powerProductionDB()

#e_db_financieel_dag_voorspel= financieelDb()

statusdata = {
   'status_code' : 'ok',
   'status_text' : 'bezig',
   'progress_pct':  0,
   'commando_recieved' : '',
   'record_count': 0
}


def updateStatusPct(filename, pct, record_cnt):
    statusdata['progress_pct'] = pct
    statusdata['record_count'] = record_cnt
    writeStatusFile(filename)
    flog.debug(inspect.stack()[0][3]+": record count=" + str(record_cnt) )
    #time.sleep(0.3) #debug

def writeStatusFile(filename):
    try: 
        fo = open(filename, "w")
        fo.write(json.dumps(statusdata))
        fo.close()
    except Exception as e:
         flog.error(inspect.stack()[0][3]+": Status file kan niet worden weggeschreven -> "+str(e))
     
def writeManifestFile():
    flog.debug(inspect.stack()[0][3]+": Manifest file " + const.FILE_EXPORT_MANIFEST + " maken.")
    try:    
        manifestdata = {
            'timestamp': util.mkLocalTimeString(),
            'record_count': statusdata['record_count']
        }
        fo = open(const.FILE_EXPORT_MANIFEST, "w")
        fo.write(json.dumps(manifestdata))
        fo.close() 
        util.setFile2user(const.FILE_EXPORT_MANIFEST,'p1mon')  
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": manifest bestand kon niet worden weggeschreven -> "+str(e))

def Main(argv):             
    flog.info("Start van programma " + prgname + ".")
    flog.info(inspect.stack()[0][3]+": wordt uitgevoerd als user -> "+pwd.getpwuid( os.getuid() ).pw_name)
    timestart = time.time()
    exportcode = ''
    global statusfile
    record_cnt = 0

    parser = argparse.ArgumentParser( description="...." )                              
    parser.add_argument( '-e'   , '--exportid',                         required=True  ) 
    parser.add_argument( '-f'   , '--filename',                         required=False ) 
    parser.add_argument( '-rm'  , '--rmstatus', action='store_true',    required=False ) 

    args = parser.parse_args()
    if args.exportid != None:
        exportcode = args.exportid

    if exportcode == '':
        print (prgname+'.py -e <exportcode id>')
        flog.error("gestopt export code ontbreekt.")
        sys.exit(2)
    
    #print 'exportcodeis ', exportcode
    #return
    
    writeSemaphoreFile('custom_www_export' + exportcode,flog)

    #timestamp = mkLocalTimestamp();
    zipfilename = const.DIR_EXPORT  + const.EXPORT_PREFIX + exportcode + ".zip"
    statusfile  = const.DIR_RAMDISK + const.EXPORT_PREFIX + exportcode + ".status"
    updateStatusPct(statusfile, 2, record_cnt)
    
    # open van config database      
    try:    
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(3)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # open van history database (1 min interval)       
    try:    
        e_db_history_min.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_MIN_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(4)."+const.FILE_DB_E_HISTORIE+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_HISTORIE_MIN_TAB+" (minuut) succesvol geopend.")
    
    # open van history database (1 uur interval)       
    try:    
        e_db_history_uur.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_UUR_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(5)."+const.FILE_DB_E_HISTORIE+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_HISTORIE_UUR_TAB+" succesvol geopend.")

    # open van history database (dag interval)  
    try:    
        e_db_history_dag.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_DAG_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(6)."+const.FILE_DB_E_HISTORIE+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_HISTORIE_DAG_TAB+" succesvol geopend.")

    # open van history database (maand interval)  
    try:    
        e_db_history_maand.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_MAAND_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(7)."+const.FILE_DB_E_HISTORIE+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_HISTORIE_MAAND_TAB+" succesvol geopend.")
  
   # open van history database (jaar interval)  
    try:    
        e_db_history_jaar.init(const.FILE_DB_E_HISTORIE,const.DB_HISTORIE_JAAR_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(8)."+const.FILE_DB_E_HISTORIE+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_HISTORIE_JAAR_TAB+" succesvol geopend.")

    # open van financieel database (dag interval)
    try:    
        e_db_financieel_dag.init(const.FILE_DB_FINANCIEEL ,const.DB_FINANCIEEL_DAG_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(9)."+const.FILE_DB_FINANCIEEL+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_FINANCIEEL_DAG_TAB+" succesvol geopend.")
    
    # open van financieel database (maand interval)
    try:    
        e_db_financieel_maand.init(const.FILE_DB_FINANCIEEL ,const.DB_FINANCIEEL_MAAND_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(10)."+const.FILE_DB_FINANCIEEL+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_FINANCIEEL_MAAND_TAB+" succesvol geopend.")

	 # open van financieel database (jaar interval)
    try:    
        e_db_financieel_jaar.init(const.FILE_DB_FINANCIEEL ,const.DB_FINANCIEEL_JAAR_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(11)."+const.FILE_DB_FINANCIEEL+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_FINANCIEEL_JAAR_TAB+" succesvol geopend.")

    # open van huidige weer database
    try:    
        weer_db.init(const.FILE_DB_WEATHER ,const.DB_WEATHER_TAB)    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(12)."+const.FILE_DB_WEATHER+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_TAB+" succesvol geopend.")

    # open van weer database voor historische weer uur      
    try:
       weer_history_db_uur.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_UUR_TAB)
    except Exception as e:
       flog.critical(inspect.stack()[0][3]+": database niet te openen(4)."+const.DB_WEATHER_UUR_TAB+" melding:"+str(e.args[0]))
       sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_UUR_TAB+" succesvol geopend.")
    
    # open van weer database voor historische weer dag      
    try:
        weer_history_db_dag.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_DAG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(5)."+const.DB_WEATHER_DAG_TAB+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_DAG_TAB+" succesvol geopend.")

    # open van weer database voor historische weer maand      
    try:
        weer_history_db_maand.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_MAAND_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(6)."+const.DB_WEATHER_MAAND_TAB+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_MAAND_TAB+" succesvol geopend.")

    # open van weer database voor historische weer jaar      
    try:
       weer_history_db_jaar.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_JAAR_TAB)
    except Exception as e:
       flog.critical(inspect.stack()[0][3]+": database niet te openen(7)."+const.DB_WEATHER_JAAR_TAB+") melding:"+str(e.args[0]))
       sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_JAAR_TAB+" succesvol geopend.")

    # open van temperatuur database
    try:    
        temperature_db.init(const.FILE_DB_TEMPERATUUR_FILENAME ,const.DB_TEMPERATUUR_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_TEMPERATUUR_FILENAME+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_TEMPERATUUR_TAB +" succesvol geopend.")

    # open van watermeter database
    try:    
        watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(20)." + const.FILE_DB_WATERMETERV2 + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

    """
    # open van watermeter databases
    try:    
        watermeter_db_uur.init( const.FILE_DB_WATERMETER, const.DB_WATERMETER_UUR_TAB, flog )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)." + const.FILE_DB_WATERMETER + ") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_WATERMETER_UUR_TAB + " succesvol geopend." )

    try:    
        watermeter_db_dag.init( const.FILE_DB_WATERMETER ,const.DB_WATERMETER_DAG_TAB , flog )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)." + const.FILE_DB_WATERMETER + ") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_WATERMETER_DAG_TAB + " succesvol geopend." )

    try:    
        watermeter_db_maand.init( const.FILE_DB_WATERMETER ,const.DB_WATERMETER_MAAND_TAB ,flog )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)." + const.FILE_DB_WATERMETER + ") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_WATERMETER_MAAND_TAB + " succesvol geopend." )

    try:    
        watermeter_db_jaar.init( const.FILE_DB_WATERMETER ,const.DB_WATERMETER_JAAR_TAB, flog )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)." + const.FILE_DB_WATERMETER + ") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_WATERMETER_JAAR_TAB  + " succesvol geopend." )
    """

    # open van fase database      
    try:
        fase_db.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_REALTIME_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+" database niet te openen(1)." + const.FILE_DB_PHASEINFORMATION + ") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel: " + const.DB_FASE_REALTIME_TAB + " succesvol geopend.")

    # open van power production database      
    try:    
        power_production_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(1)." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_POWERPRODUCTION_TAB + " succesvol geopend." )

    updateStatusPct(statusfile,3, record_cnt)

    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_POWERPRODUCTION )
    record_cnt = record_cnt + power_production_db.sql2file(  const.DIR_EXPORT + const.DB_POWERPRODUCTION + exportcode)
    updateStatusPct(statusfile, 10, record_cnt)
    flog.info(inspect.stack()[0][3]+": kWh levering sql gexporteerd.")

    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_PHASEINFORMATION )
    record_cnt = record_cnt + fase_db.sql2file(  const.DIR_EXPORT + const.DB_PHASEINFORMATION + exportcode)
    updateStatusPct(statusfile, 20, record_cnt)
    flog.info(inspect.stack()[0][3]+": fase date sql gexporteerd.")

    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_E_HISTORIE )
    record_cnt = record_cnt + e_db_history_min.sql2file(  const.DIR_EXPORT + const.DB_E_HISTORIE + exportcode)
    updateStatusPct(statusfile, 25, record_cnt)
    record_cnt = record_cnt + e_db_history_uur.sql2file(  const.DIR_EXPORT + const.DB_E_HISTORIE + exportcode)
    updateStatusPct(statusfile, 27, record_cnt)
    record_cnt = record_cnt + e_db_history_dag.sql2file(  const.DIR_EXPORT + const.DB_E_HISTORIE + exportcode)
    updateStatusPct(statusfile, 28, record_cnt)
    record_cnt = record_cnt + e_db_history_maand.sql2file(const.DIR_EXPORT + const.DB_E_HISTORIE + exportcode)
    updateStatusPct(statusfile, 29, record_cnt)
    record_cnt = record_cnt + e_db_history_jaar.sql2file( const.DIR_EXPORT + const.DB_E_HISTORIE + exportcode)
    flog.info(inspect.stack()[0][3]+": historie sql gexporteerd.")
    updateStatusPct(statusfile, 30, record_cnt)
    
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_FINANCIEEL )
    record_cnt = record_cnt + e_db_financieel_dag.sql2file( const.DIR_EXPORT + const.DB_FINANCIEEL + exportcode )
    updateStatusPct(statusfile, 31, record_cnt)
    record_cnt = record_cnt + e_db_financieel_maand.sql2file( const.DIR_EXPORT + const.DB_FINANCIEEL + exportcode )
    updateStatusPct(statusfile, 32, record_cnt)
    record_cnt = record_cnt + e_db_financieel_jaar.sql2file( const.DIR_EXPORT + const.DB_FINANCIEEL + exportcode )
    flog.info(inspect.stack()[0][3]+": financieel sql gexporteerd.")
    updateStatusPct(statusfile, 33, record_cnt) 
    
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_CONFIG )
    record_cnt = record_cnt + config_db.sql2file(const.DIR_EXPORT + const.DB_CONFIG + exportcode)
    flog.info(inspect.stack()[0][3]+": configuratie sql gexporteerd.")
    updateStatusPct(statusfile, 40, record_cnt) 
    
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_WEER  )
    record_cnt = record_cnt + weer_db.sql2file(const.DIR_EXPORT + const.DB_WEER + exportcode)
    flog.info(inspect.stack()[0][3]+": weer sql gexporteerd.")
    updateStatusPct(statusfile, 42 ,record_cnt) 
    
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_WEER_HISTORY )
    record_cnt = record_cnt + weer_history_db_uur.sql2file(const.DIR_EXPORT + const.DB_WEER_HISTORY + exportcode)
    updateStatusPct(statusfile, 50, record_cnt)
    record_cnt = record_cnt + weer_history_db_dag.sql2file(const.DIR_EXPORT + const.DB_WEER_HISTORY + exportcode)
    updateStatusPct(statusfile, 52 ,record_cnt )
    record_cnt = record_cnt + weer_history_db_maand.sql2file(const.DIR_EXPORT + const.DB_WEER_HISTORY + exportcode)
    updateStatusPct(statusfile, 54, record_cnt)
    record_cnt = record_cnt + weer_history_db_jaar.sql2file(const.DIR_EXPORT + const.DB_WEER_HISTORY + exportcode)
    updateStatusPct(statusfile, 56 , record_cnt)
    flog.info(inspect.stack()[0][3]+": weer historie sql gexporteerd.")
    updateStatusPct(statusfile, 58, record_cnt) 
    
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_TEMPERATURE )
    record_cnt = record_cnt + temperature_db.sql2file(const.DIR_EXPORT + const.DB_TEMPERATURE + exportcode )
    flog.info(inspect.stack()[0][3]+": temperatuur sql gexporteerd.")
    updateStatusPct(statusfile, 60, record_cnt)

    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_WATERMETERV2 )
    record_cnt = record_cnt + watermeter_db.sql2file( const.DIR_EXPORT + const.DB_WATERMETERV2 + exportcode )
    updateStatusPct(statusfile, 70, record_cnt)

    """
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_WATERMETER )
    record_cnt = record_cnt + watermeter_db_uur.sql2file( const.DIR_EXPORT + const.DB_WATERMETER + exportcode )
    updateStatusPct(statusfile, 70, record_cnt)
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_WATERMETER )
    record_cnt = record_cnt + watermeter_db_dag.sql2file( const.DIR_EXPORT + const.DB_WATERMETER + exportcode )
    updateStatusPct(statusfile, 72, record_cnt)
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_WATERMETER )
    record_cnt = record_cnt + watermeter_db_maand.sql2file( const.DIR_EXPORT + const.DB_WATERMETER + exportcode )
    updateStatusPct(statusfile, 73, record_cnt)
    flog.info(inspect.stack()[0][3]+": verwerken van " + const.DB_WATERMETER )
    record_cnt = record_cnt + watermeter_db_jaar.sql2file( const.DIR_EXPORT + const.DB_WATERMETER + exportcode )
    flog.info(inspect.stack()[0][3]+": watermeter sql gexporteerd.")
    updateStatusPct(statusfile, 74, record_cnt)
    """


    # /p1mon/www/custom aan archief toevoegen
     # check of export file gereed is
    if args.rmstatus == False:
        done_file =  const.FILE_PREFIX_CUSTOM_UI + exportcode + '.done'
        flog.info(inspect.stack()[0][3]+": controle of export gereed is door op file " +  done_file + " te zoeken.")
        cnt = 0
        while os.path.isfile( done_file ) == False:
            if cnt > 300: #fail save to prevent endless loop ,300 is 5 min.
                flog.error(inspect.stack()[0][3]+": timeout for het maken van een custom back-up!, is de folder te groot?")
                break 
            time.sleep(1)
            cnt += 1
    
    zf = zipfile.ZipFile(zipfilename, mode='w')
    

    try:
        flog.info(inspect.stack()[0][3]+": custom www aan zip file toevoegen")
        zf.write(const.FILE_PREFIX_CUSTOM_UI + exportcode + ".gz", compress_type=zipfile.ZIP_STORED) # geen nut om gz te zippen.
        os.remove(const.FILE_PREFIX_CUSTOM_UI + exportcode + ".gz")
        os.remove ( done_file )
        updateStatusPct(statusfile, 80, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": custom UI aan zip file toevoegen gefaald")

    try:
        flog.info(inspect.stack()[0][3]+": historie sql aan zip file toevoegen")
        zf.write(const.DIR_EXPORT + const.DB_E_HISTORIE + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_E_HISTORIE + exportcode)
        updateStatusPct(statusfile, 82 ,record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": historie sql aan zip file toevoegen gefaald")

    try:
        flog.info(inspect.stack()[0][3]+": financieel sql aan zip file toevoegen")
        zf.write(const.DIR_EXPORT + const.DB_FINANCIEEL + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_FINANCIEEL + exportcode)
        updateStatusPct(statusfile, 84, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": financieel sql aan zip file toevoegen gefaald")

    try:
        flog.info(inspect.stack()[0][3]+": configuratie sql aan zip file toevoegen")
        zf.write(const.DIR_EXPORT + const.DB_CONFIG + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_CONFIG + exportcode)
        updateStatusPct(statusfile, 86, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": configuratie sql aan zip file toevoegen gefaald")

    try:
        flog.info(inspect.stack()[0][3]+": huidige weer sql aan zip file toevoegen")
        zf.write(const.DIR_EXPORT + const.DB_WEER + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_WEER + exportcode)
        updateStatusPct(statusfile, 88 ,record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": huidige weer sql aan zip file toevoegen gefaald: "+str(e))
     
    try:
        flog.info(inspect.stack()[0][3]+": historie weer sql aan zip file toevoegen")
        zf.write(const.DIR_EXPORT + const.DB_WEER_HISTORY + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_WEER_HISTORY + exportcode)
        updateStatusPct(statusfile, 90 ,record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": historie weer sql aan zip file toevoegen gefaald: "+str(e))
     
    try:
        flog.info(inspect.stack()[0][3]+": temperatuur sql aan zip file toevoegen.")
        zf.write(const.DIR_EXPORT + const.DB_TEMPERATURE + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_TEMPERATURE + exportcode)
        updateStatusPct(statusfile, 92, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": temperatuur sql aan zip file toevoegen gefaald: "+str(e))

    try:
        flog.info(inspect.stack()[0][3]+": status file toevoegen")
        writeManifestFile()
        zf.write(const.FILE_EXPORT_MANIFEST, compress_type=zipfile.ZIP_DEFLATED) 
        os.remove(const.FILE_EXPORT_MANIFEST)
        updateStatusPct(statusfile, 93, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": custom UI aan zip file toevoegen gefaald")

    try:
        flog.info(inspect.stack()[0][3]+": watermeter sql aan zip file toevoegen.")
        zf.write(const.DIR_EXPORT +  const.DB_WATERMETERV2 + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_WATERMETERV2 + exportcode)
        updateStatusPct(statusfile, 94, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": watermeter sql aan zip file toevoegen gefaald")

    try:
        flog.info(inspect.stack()[0][3]+": fase data sql aan zip file toevoegen.")
        zf.write(const.DIR_EXPORT +  const.DB_PHASEINFORMATION + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_PHASEINFORMATION + exportcode)
        updateStatusPct(statusfile, 95, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": fase data sql aan zip file toevoegen gefaald")

    try:
        flog.info(inspect.stack()[0][3]+": kWh levering data sql aan zip file toevoegen.")
        zf.write(const.DIR_EXPORT +  const.DB_POWERPRODUCTION + exportcode, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(const.DIR_EXPORT + const.DB_POWERPRODUCTION + exportcode)
        updateStatusPct(statusfile, 96, record_cnt) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": kWh levering data sql aan zip file toevoegen gefaald")

    zf.close()
    flog.info(inspect.stack()[0][3]+": zipfile "+zipfilename+" gereed.")
    # move to download dir in web tree
    flog.info(inspect.stack()[0][3]+": zip file naar folder kopieren")

    if args.filename != None:
        downloadfilename = args.filename
    else:
        downloadfilename = "/p1mon/www/download/" + const.EXPORT_PREFIX + exportcode + ".zip"

    flog.info( inspect.stack()[0][3] + ": zip file naar folder kopieren ->" + downloadfilename )
    shutil.move( zipfilename, downloadfilename )
    
    try:
        subprocess.run( ['sudo', 'chmod', '0666', downloadfilename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        flog.info( inspect.stack()[0][3] + ": zip file rechten aangepast voor bestand " + downloadfilename )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": zip file rechten waren niet aan te passen voor bestand " + downloadfilename )
    
    statusdata['status_text'] = 'gereed'
    statusdata['status_code'] = 'klaar'
    updateStatusPct(statusfile, 100, record_cnt)
    
    #setFile2user(downloadfilename,'p1mon')
    #setFile2user(statusfile,'p1mon')
    
    if args.rmstatus == True:
        flog.info(inspect.stack()[0][3]+": geforceerd verwijderen van status bestand " + statusfile )
        try:
            os.remove( statusfile )
        except:
            pass
    else:
        backgroundcommand = '(sleep 7200;rm ' + downloadfilename + ' && rm ' + statusfile + ' > /dev/null 2>&1)&'
        flog.info(inspect.stack()[0][3]+": verwijderen van tijdelijke bestanden ->"+backgroundcommand )
        os.system( backgroundcommand )
    
    timestop = time.time()  
    flog.info( inspect.stack()[0][3] + ": Gereed verwerkings tijd is " + f"{timestop - timestart:0.2f} seconden." ) 
    
#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        flog = fileLogger( const.DIR_FILELOG + prgname + ".log", prgname )    
        #### aanpassen bij productie
        flog.setLevel( logging.INFO )
        flog.consoleOutputOn(True) 
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
        sys.exit(1)

    Main(sys.argv[1:]) 
