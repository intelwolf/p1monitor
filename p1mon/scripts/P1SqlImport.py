# run manual with ./P1SqlImport
import argparse
import const
import crontab_lib
import inspect
import logger
import signal
import zipfile
import fnmatch
import datetime
import json
import os
import pwd
import subprocess
import sqldb
import sqldb_pricing
import sys
import systemid
import time
import crypto3
import util
import listOfPidByName
import process_lib


#from datetime import datetime, timedelta
#from util import setFile2user
##from listOfPidByName import listOfPidByName

prgname = 'P1SqlImport'

config_db                   = sqldb.configDB()
e_db_history_min            = sqldb.SqlDb2() 
e_db_financieel_dag         = sqldb.financieelDb()
e_db_financieel_maand       = sqldb.financieelDb()
e_db_financieel_jaar        = sqldb.financieelDb()
weer_db                     = sqldb.currentWeatherDB()
weer_history_db_uur         = sqldb.historyWeatherDB()
temperature_db              = sqldb.temperatureDB()
temperature_db              = sqldb.temperatureDB()
watermeter_db               = sqldb.WatermeterDBV2()
fase_db                     = sqldb.PhaseDB()
fase_db_min_max_dag         = sqldb.PhaseMaxMinDB()
power_production_db         = sqldb.powerProductionDB()
power_production_solar_db   = sqldb.powerProductionSolarDB()
price_db                    = sqldb_pricing.PricingDb()

no_status_messages    = False   # dont write to the status file. 

statusdata = {
   'records_processed_ok'  :  0,
   'records_processed_nok' :  0,
   'records_total'         :  0
}

def Main(argv):

    global no_status_messages

    my_pid = os.getpid()
    flog.info("Start van programma met process id " + str( my_pid ) )
    pid_list, _process_list = listOfPidByName.listOfPidByName( prgname )
    flog.debug( inspect.stack()[0][3] + ": pid list all (andere lopende proces id's) " + str( pid_list ) )
    #print ( pid_list )
    pid_list.remove( my_pid ) # remove own pid from the count
    flog.debug( inspect.stack()[0][3] + ": pid list clean (andere lopende proces id's) " + str( pid_list ) + " aantal processen = " + str(len( pid_list )) )
    if len( pid_list ) > 1:
        msg_str = "Gestopt een andere versie van het programma is actief."
        flog.info( inspect.stack()[0][3] + ": " + msg_str )
        sys.exit(1)

    timestart = time.time() # used te calculate the processing time.

    flog.info( inspect.stack()[0][3] +  ": Wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name  )

    parser = argparse.ArgumentParser( description = prgname )
    parser.add_argument( '-i' , '--importfile', help="Naam van het export bestand om te importeren.",     required=False  ) 
    parser.add_argument( '-rm', '--rmstatus',   help="Maak geen status bestand aan", action='store_true', required=False ) 

    args = parser.parse_args()
    no_status_messages = args.rmstatus # default False when set True

    initStatusFile()

    # open van config database
    try: 
        config_db.init( const.FILE_DB_CONFIG,const.DB_CONFIG_TAB )
    except Exception as e:
        msg = ": database niet te openen ("+ const.FILE_DB_CONFIG + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        stop( 2 ) 
    
    msg =  "database " + const.DB_CONFIG + " succesvol geopend."
    writeLineToStatusFile( msg )

    try:
        # update field from database, the cli switches overwrite the DB values!
        _id, importfile, _label = config_db.strget( 138,flog )
    except Exception as e:
        msg = "fout met lezen van import bestand uit database -> " + str(e) 
        writeLineToStatusFile( msg )
        flog.error(inspect.stack()[0][3]+": " + msg )
        stop( 2 ) 
        
    # check must be done after DB read of import filename
    if args.importfile != None:
        importfile = args.importfile

    if importfile == '':
        msg = "gestopt importfile ontbreekt."
        writeLineToStatusFile( msg )
        flog.error( inspect.stack()[0][3]+": " + msg )
        stop( 2 ) 

    try:
        extension = os.path.splitext( importfile )[1]
        print ( extension )
        msg = "ZIP file " + importfile + " gevonden."
        writeLineToStatusFile( msg )
        flog.info(inspect.stack()[0][3]+": " + msg )
        if extension != '.zip':
            msg = "Geen passend ZIP file gevonden, gestopt."
            writeLineToStatusFile( msg )
            flog.warning(inspect.stack()[0][3]+": " + msg)  
            stop( 3 ) 
    except Exception as e:
        msg = "Geen passend ZIP file gevonden, gestopt -> " + str(e)
        flog.error(inspect.stack()[0][3]+": " + msg )
        stop( 3 ) 

    openDatabases()

    try:
        zf = zipfile.ZipFile( importfile )
        _head,tail = os.path.split( importfile ) 
        msgToInfoLogAndStatusFile( "ZIP file " + tail + " succesvol geopend." )
    except Exception as e:
        msg = "ZIP file " + importfile + " probleem =>" + str(e)
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3]+": " + msg )  
        stop( 30 ) 

    # set file rights
    util.setFile2user( const.FILE_DB_E_FILENAME, 'p1mon' )
    util.setFile2user( const.FILE_DB_E_HISTORIE, 'p1mon' )
    util.setFile2user( const.FILE_DB_CONFIG, 'p1mon' )
    util.setFile2user( const.FILE_DB_STATUS, 'p1mon' )
    util.setFile2user( const.FILE_DB_FINANCIEEL, 'p1mon' ) 
    util.setFile2user( const.FILE_DB_WEATHER, 'p1mon' )
    util.setFile2user( const.FILE_DB_WEATHER_HISTORIE, 'p1mon' )
    util.setFile2user( const.FILE_DB_TEMPERATUUR_FILENAME, 'p1mon' )
    util.setFile2user( const.FILE_DB_WATERMETER, 'p1mon' )
    util.setFile2user( const.FILE_DB_WATERMETERV2, 'p1mon' )
    util.setFile2user( const.FILE_DB_POWERPRODUCTION,'p1mon')
    util.setFile2user( const.FILE_DB_PHASEINFORMATION, 'p1mon')
    msgToInfoLogAndStatusFile( "file rechten van database bestanden correct gezet." )

    dbIntegrityCheck( config_db,           const.FILE_DB_CONFIG )
    dbIntegrityCheck( e_db_history_min,    const.FILE_DB_E_HISTORIE )
    dbIntegrityCheck( e_db_financieel_dag, const.FILE_DB_FINANCIEEL )
    dbIntegrityCheck( weer_db,             const.FILE_DB_WEATHER )
    dbIntegrityCheck( weer_history_db_uur, const.FILE_DB_WEATHER_HISTORIE )
    dbIntegrityCheck( temperature_db,      const.FILE_DB_TEMPERATUUR_FILENAME )
    #dbIntegrityCheck( watermeter_db_uur,   const.FILE_DB_WATERMETER )
    dbIntegrityCheck( watermeter_db,       const.FILE_DB_WATERMETERV2 )
    dbIntegrityCheck( fase_db,             const.FILE_DB_PHASEINFORMATION )
    dbIntegrityCheck( power_production_db, const.FILE_DB_POWERPRODUCTION )

    try:
       
        for fname in zf.namelist():  #filter out the manifest file first
            if fname == const.FILE_EXPORT_MANIFEST[1:]:
                data = zf.read(const.FILE_EXPORT_MANIFEST[1:]).decode('utf-8')
                json_data = json.loads(data)
                statusdata['records_total']     = json_data['record_count']
                #statusdata['export_timestamp']  = str(json_data['timestamp'])
                msgToInfoLogAndStatusFile( "manifest is correct verwerkt uit ZIP file." )
                msgToInfoLogAndStatusFile( "aantal te importeren records " + str(statusdata['records_total']) + "." )
                msgToInfoLogAndStatusFile( "import bestand creatie datum " + str(json_data['timestamp']) + "." )
                break

    except Exception as e:
        msg = "manifest bestand is niet correct in ZIP file. -> " + str(e)
        writeLineToStatusFile( msg )
        flog.warning(inspect.stack()[0][3] + ": " + msg )

    # custom www folder
    try:
        #raise Exception("dummy exception voor test.")
        for fname in zf.namelist():
            if fname[:len(const.FILE_PREFIX_CUSTOM_UI)-1] == const.FILE_PREFIX_CUSTOM_UI[1:]:
                
                zf.extract(fname,'/') # komt dan terecht in /p1mon/var/tmp
                
                exportcode = fname[len(const.FILE_PREFIX_CUSTOM_UI)-1:-3]

                cmd = 'sudo tar -zxf ' + const.FILE_PREFIX_CUSTOM_UI + exportcode + '.gz -C ' + const.DIR_WWW_CUSTOM + " 2>/dev/null"
                # 1.8.0 upgrade
                r = process_lib.run_process( 
                    cms_str = cmd,
                    use_shell=True,
                    give_return_value=True,
                    flog=flog 
                )
                if r[2] > 0:
                    flog.error(inspect.stack()[0][3]+" custom www import gefaald.")
                    msg = "custom www bestanden konden niet worden verwerkt of waren niet aanwezig."
                    writeLineToStatusFile( msg )
                    flog.warning( inspect.stack()[0][3] + ": " + msg )
                else:
                    msgToInfoLogAndStatusFile( "custom www bestanden succesvol verwerkt." )

    except Exception as e:
        msg = "ZIP file verwerking probleem tijdens custom www verwerking -> " + str(e)
        writeLineToStatusFile( msg )
        flog.error(inspect.stack()[0][3]+": ZIP file verwerking ging mis tijdens custom www verwerking "+str(e))    

    try:

        for fname in zf.namelist():

            _head,tail = os.path.split(fname)
           
            #print ( "fname=", fname )
            #print ( "tail=", tail ) 
            #print ( "configuratie="   +str( tail.startswith( 'configuratie' ) ) )
            #print ( "financieel="      +str( tail.startswith( 'finacieel' ) ) )
            #print ( "historie="       +str( tail.startswith( 'historie' ) ) )
            #print ( "01_weer_historie="  +str( tail.startswith( '01_weer_historie' ) ) )
            #print ( "weer="           +str( tail.startswith( 'weer' ) ) )
            #print ( "manifest.json="  +str( tail.startswith( 'manifest.json' ) ) )
            #print ( "02_temperatuur="  +str( tail.startswith( '02_temperatuur' ) ) )
            #print ( "03_watermeter="  +str( tail.startswith( '03_watermeter' ) ) )

            #############################################
            if tail.startswith( const.DB_WATERMETERV2  ):
                processImportDataSet( const.DB_WATERMETERV2 , watermeter_db, zf, fname, 'replace into watermeter*' )
    
            ###########################################
            #elif tail.startswith( const.DB_WATERMETER ):
            #    processImportDataSet(  const.DB_WATERMETER  , watermeter_db_uur, zf, fname, 'replace into watermeter*' )

            ############################################
            elif tail.startswith( const.DB_TEMPERATURE ):
                processImportDataSet( const.DB_TEMPERATURE , temperature_db, zf, fname, 'replace into temperatuur*' )
                temperature_db.fix_missing_month_day( flog )

            ############################################
            elif tail.startswith( const.DB_E_HISTORIE_TAIL ):
                processImportDataSet( const.DB_E_HISTORIE_TAIL, e_db_history_min, zf, fname, 'replace into e_history*' )

            ############################################
            # the OR is fix from version 0.9.19 > to fix the typo in "finacieel" text
            elif tail.startswith( const.DB_FINANCIEEL ) or tail.startswith("finacieel"):
                #processImportDataSet( const.DB_FINANCIEEL, e_db_financieel_dag, zf, fname, 'replace into e_financieel*' )
                processImportDataSet( const.DB_FINANCIEEL, e_db_financieel_dag, zf, fname, 'replace into*' )

            ############################################
            elif tail.startswith( const.DB_CONFIG ):
                processImportDataSet( const.DB_CONFIG, config_db, zf, fname, 'update ' + const.DB_CONFIG_TAB + ' set PARAMETER=*' )

            ############################################
            elif tail.startswith( const.DB_WEER_HISTORY ):
                processImportDataSet( const.DB_WEER_HISTORY, weer_history_db_uur, zf, fname, 'replace into weer_history*' )

            ############################################
            elif tail.startswith( const.DB_WEER ):
                processImportDataSet( const.DB_WEER, weer_db, zf, fname, 'replace into weer*' )

            ############################################
            elif tail.startswith( const.DB_PHASEINFORMATION ):
                processImportDataSet( const.DB_PHASEINFORMATION, fase_db, zf, fname, 'replace into fase*' )

            ############################################
            elif tail.startswith( const.DB_POWERPRODUCTION ):
                 processImportDataSet( const.DB_POWERPRODUCTION, power_production_db, zf, fname, 'replace into ' + const.DB_POWERPRODUCTION_TAB + '*' )

    except Exception as e:
        msg = "ZIP file verwerking globale fout -> " + str(e)
        writeLineToStatusFile( msg )
        flog.error( inspect.stack()[0][3] + ": " + msg )

    zf.close 
    msgToInfoLogAndStatusFile( "alle data uit het ZIP bestand verwerkt." )

    msgToInfoLogAndStatusFile( 'Netwerkinstellingen wordt aangepast.' )
    config_db.strset( '1', 168, flog ) # set wachtdog flag.
    time.sleep ( 5 ) # give some time to proces 
    msgToInfoLogAndStatusFile( 'Netwerkinstellingen doorgeven aan Watchdog process.' )

    # lees systeem ID uit en zet deze in de config database. 
    # versleuteld om dat deze data in een back-up bestand terecht kan komen.
    try: 
        msgToInfoLogAndStatusFile( 'System ID zetten in configuratie database: ' + str( systemid.getSystemId() ) )
        #flog.info(inspect.stack()[0][3]+': System ID zetten in configuratie database: ' + str( systemid.getSystemId() ) )
        sysid_encrypted  = crypto3.p1Encrypt( systemid.getSystemId(),"sysid" ).encode('utf-8').decode('utf-8')
        config_db.strset( sysid_encrypted ,58, flog ) 
    except Exception as e:
        msg = " System ID zetten mislukt -> " + str(e.args[0])
        writeLineToStatusFile( msg )
        flog.warning( inspect.stack()[0][3] + ": " + msg )

    setSoftwareVersionInformation()

    msgToInfoLogAndStatusFile( 'WiFi wordt aangepast.' )
    cmd = "sudo /p1mon/scripts/P1SetWifi"
    r = process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=True,
        flog=flog 
    )
    if r[2] > 0:
        msg = "Wifi aanpassen gefaald."
        writeLineToStatusFile( msg )
        flog.error( inspect.stack()[0][3] + ": " + msg )
    else:
        msgToInfoLogAndStatusFile( 'WiFi aanpassingen gereed.' )

    msgToInfoLogAndStatusFile( 'CRON wordt aangepast.' )

    try:
        crontab_lib.update_crontab_backup( flog=flog )
        msgToInfoLogAndStatusFile( 'CRON aanpassingen gereed.' )
    except Exception as e:
        msg = "CRON update gefaald."
        writeLineToStatusFile( msg )
        flog.error( inspect.stack()[0][3] + ": " + msg )
        flog.error( inspect.stack()[0][3] + ": gefaald " + str(e) )

    msgToInfoLogAndStatusFile( 'Internet API wordt aangepast.' )
    _id, api_is_active, _label = config_db.strget( 163, flog ) 
    if int( api_is_active ) == 1:        # the Internet API is active process the changes, make https config and get certificates.
        config_db.strset( 1, 162, flog ) # set the flag so the watchdog processes the changes
        msgToInfoLogAndStatusFile( 'Internet API aanpassingen worden doorgevoerd, duur maximaal 60 sec.' )
        time.sleep(10)

    #make sure that all is copied to disk
    msgToInfoLogAndStatusFile( "Databases worden van RAM naar het SDHC kaartje geschreven." )
    cmd = "/p1mon/scripts/P1DbCopy --allcopy2disk --forcecopy" # 1.8.0 upgrade
    process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=False,
        flog=flog 
    )

    msgToInfoLogAndStatusFile( "Databases kopieren gereed." )

    msgToInfoLogAndStatusFile( "ZIP bestand wordt verwijderd." )
    try:
        time.sleep(1) # allow file to be unlocked.
        os.remove( importfile ) # remove uploaded file.
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": "+str(e))
        msg = "verwijderen van import bestand " + importfile + " gefaald."
        writeLineToStatusFile( msg )
        flog.error( inspect.stack()[0][3] + ": " + msg )

    msgToInfoLogAndStatusFile( 'Vaste IP adressen worden aangepast als deze actief zijn.' )
    config_db.strset( 3, 168, flog ) # set the flag so the watchdog processes the changes

    msgToInfoLogAndStatusFile( 'SAMBA fileshares worden gezet.' )
    config_db.strset( 1, 182, flog ) # set the flag so the watchdog processes the changes

    msgToInfoLogAndStatusFile( 'SOCAT aanpassingen, als deze actief is.' )
    config_db.strset( 1, 201, flog ) # set the flag so the watchdog processes the changes


    timestop = time.time()
    m, s = divmod( timestop - timestart , 60 ) # make minutes and seconds from total secs count
    msgToInfoLogAndStatusFile( "Gereed verwerkings tijd is " + '{:02d}:{:02d}.'.format( int(m), int(s) ) )

    stop( 0 )
    #############################
    # einde van verwerking.     #
    #############################


########################################################
# write to ramdisk file and the log for info entries   #
########################################################
def msgToInfoLogAndStatusFile( msg ):
    flog.info(msg)
    writeLineToStatusFile( msg )

########################################################
# write to ramdisk file the progress for lines that    #
# are replaced.                                        #
# forced = true means to write always                  #
# normaly only write when every 3 seconds              #
########################################################
def msgReplaceDb( db_name , forced=False ):

    if forced == False:
        now = datetime.datetime.utcnow()
        if int((now - datetime.datetime(1970, 1, 1)).total_seconds())%3 != 0:
            return

    # check if manifest data is not set or incomplete;
    try :
        pct_value = (statusdata['records_processed_ok']/statusdata['records_total']) * 100
    except Exception as e:
        pct_value  = -1 # there is an problem

    # change message according to status of percentage.
    if pct_value  == -1:
        msg = "totaal records ok=" + str( statusdata['records_processed_ok'] ) + " aantal defect="+\
            str( statusdata['records_processed_nok']  ) + ". (" + db_name  + ")."
        replaceLastLineInStatusFile( msg )
    else:
        msg = "totaal records ok=" + str( statusdata['records_processed_ok'] ) + " aantal defect=" +\
             str( statusdata['records_processed_nok']  ) +\
        ". "  + "Voorgang: " + "{:.0f}".format( pct_value  )+ "% (" + db_name  + ")."
        replaceLastLineInStatusFile( msg )

########################################################
# creates and wipes the status file                    #
########################################################
def initStatusFile():
    if no_status_messages == True:
        return
    try:    
        status_fp = open( const.FILE_SQL_IMPORT_STATUS, "w")
        #subprocess.run( ['sudo', 'chmod', '066' , const.FILE_WATERMETER_CNT_STATUS ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        subprocess.run( ['chmod', '066' , const.FILE_WATERMETER_CNT_STATUS ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        status_fp.close()
    except Exception as e:
        flog.error( "status file schrijf fout: " + str(e) )

########################################################
# write to ramdisk file the progress                   #
# the file is emptied/re-created when the program      #
# starts.                                              #
########################################################
def writeLineToStatusFile( msg ):

    if no_status_messages == True:
        return

    try:
        fp = open( const.FILE_SQL_IMPORT_STATUS, "a" )
        t=time.localtime()
        msg_str = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + " " + msg + '\n'
        fp.write( msg_str )
        flog.debug( msg_str )
        fp.close()
    except Exception as e:
        flog.error( "status file schrijf fout: " + str(e) )
        initStatusFile()

########################################################
# write to ramdisk file and change the last line       #
# the file is emptied/re-created when the program      #
# starts.                                              #
########################################################
def replaceLastLineInStatusFile( msg ):

    if no_status_messages == True:
        return

    try:
        t=time.localtime()
        msg_str = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + " " + msg + '\n'
        
        fp = open( const.FILE_SQL_IMPORT_STATUS , "r" )
        list_of_lines = fp.readlines()
        list_of_lines[ len(list_of_lines)-1 ] = msg_str
        fp.close()
        
        fp = open( const.FILE_SQL_IMPORT_STATUS , "w" )
        for line in list_of_lines:
            fp.write( line )
        fp.close()

    except Exception as e:
        flog.error( "status file schrijf/lees fout: " + str(e) )
        initStatusFile()

########################################################
# instert the sql lines from an export zip file        #
# starts.                                              #
########################################################
def processImportDataSet( db_tabel_name , db_pointer, zip_file, db_filename, sql_match_str ):

    #print ( "db_filename=", db_filename )
    #print ( "db_tabel_name=", db_tabel_name )
    #print ( "sql_match_str=", sql_match_str )

    try:

        msgToInfoLogAndStatusFile( db_tabel_name + " wordt verwerkt." )

        #raise Exception("test-excep")
        data = zip_file.read( db_filename ).decode('utf-8')
        if data == None:
            msgToInfoLogAndStatusFile( db_tabel_name + " tabel bevat geen records, niets verwerkt." )
            return # return and do noting if there is no data

        content = data.split('\n')
        content.remove("") # remove empty strings 

        #print ( content )

        msgToInfoLogAndStatusFile( db_tabel_name + " tabel bevat " + str(len(content)) + " import records." )
        writeLineToStatusFile( "" ) # make room for the dynamic line

        for sql in content:
        #if len( sql.strip() ) > 0: #clear empty string
            # check if valid SQL
            try:
                if fnmatch.fnmatch( sql, sql_match_str ):
                    #raise Exception("dummy exception voor test.")
                    db_pointer.insert_rec( sql )
                    statusdata['records_processed_ok'] += 1
                else:
                    statusdata['records_processed_nok'] += 1
                    flog.warning( inspect.stack()[0][3]+": SQL STATEMENT= " + sql )
            except Exception as e:
                statusdata['records_processed_nok'] =+ 1
                flog.error( inspect.stack()[0][3]+": " + db_tabel_name+ " probleem " + str(e) )

            msgReplaceDb( db_tabel_name )

        msgReplaceDb( db_tabel_name , forced=True ) # forces the last line
    except Exception as e:
        msg = "ernstige fout met database '" + db_tabel_name + "' data niet of niet geheel verwerkt -> " + str(e)
        writeLineToStatusFile( msg )
        flog.error( inspect.stack()[0][3] + ": " + msg )

#####################################################
# reorder and check database file integrity         #
#####################################################
def dbIntegrityCheck( db, db_filename ):
    try:
        db.defrag()
        db.integrity_check()
        _head,tail = os.path.split( db_filename ) 
        msg = "database integriteit " + tail + " correct."
        writeLineToStatusFile( msg )
        flog.info( inspect.stack()[0][3] + ": " + msg )
    except Exception as e:
        msg = "database bestand " + db_filename + " is corrupt. -> " + str(e)
        writeLineToStatusFile( msg )
        flog.critical( inspect.stack()[0][3]+": " + msg )
        stop( 1000 ) 

#####################################################
# set current P1 monitor version information        #
# This because the config data is imported from     #
# possible previous versions                        #
#####################################################
def setSoftwareVersionInformation():
    try:  
        sql = " update " + const.DB_CONFIG_TAB + " set parameter = '" + str( const.P1_VERSIE) + "' where id = 0"
        config_db.execute_rec( sql )
        #print( sql )
        msgToInfoLogAndStatusFile( "versie gezet: " + str( const.P1_VERSIE) )
        #flog.info( inspect.stack()[0][3] + ": versie gezet: " + str( const.P1_VERSIE) )
        #raise Exception("test-excep")

        sql = " update " + const.DB_CONFIG_TAB + " set parameter = '" + str( const.P1_PATCH_LEVEL) + "' where id = 128"
        config_db.execute_rec( sql )
        #print( sql )
        msgToInfoLogAndStatusFile( "patch level gezet: " + str( const.P1_PATCH_LEVEL) )
        #flog.info( inspect.stack()[0][3] + ": patch level gezet: " + str( const.P1_PATCH_LEVEL) )

        sql = " update " + const.DB_CONFIG_TAB + " set parameter = '" + str( const.P1_SERIAL_VERSION ) + "' where id = 133"
        config_db.execute_rec( sql )
        #print( sql )
        msgToInfoLogAndStatusFile( "versie serienummer gezet: " + str(const.P1_SERIAL_VERSION ) )
        #flog.info( inspect.stack()[0][3] + ": versie serienummer gezet: " + str(const.P1_SERIAL_VERSION ) )

    except Exception as e:
        msg = "Versie aanpassen gefaald "
        writeLineToStatusFile( msg  + str(e.args[0]) )
        flog.warning( inspect.stack()[0][3] + ": " + msg ) 

#####################################################
# open alle used sqlite database                    #
#####################################################
def openDatabases():

    # open van history database 
    try:
        e_db_history_min.init( const.FILE_DB_E_HISTORIE, const.DB_HISTORIE_MIN_TAB )
    except Exception as e:
        msg = ": database niet te openen(3)." + const.DB_HISTORIE_MIN_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 4 )

    msgToInfoLogAndStatusFile( "database " + const.DB_HISTORIE_MIN_TAB + " succesvol geopend." )

    # open van financieel database (dag interval)
    try:
        e_db_financieel_dag.init( const.FILE_DB_FINANCIEEL ,const.DB_FINANCIEEL_DAG_TAB )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_FINANCIEEL_DAG_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 5 )
        
    msgToInfoLogAndStatusFile( "database " + const.DB_FINANCIEEL_DAG_TAB + " succesvol geopend." )
   
    # open van weer database 
    try:
        weer_db.init(const.FILE_DB_WEATHER ,const.DB_WEATHER_TAB)
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_WEATHER_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 6 )
        
    msgToInfoLogAndStatusFile( "database " + const.DB_WEATHER_TAB + " succesvol geopend." )
  
    # open van weer history database 
    try:
        #weer_history_db_uur.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_HISTORIE_MIN_TAB)
        weer_history_db_uur.init(const.FILE_DB_WEATHER_HISTORIE ,const.DB_WEATHER_UUR_TAB) 
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_WEATHER_UUR_TA + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 7 )
        
    msgToInfoLogAndStatusFile( "database " + const.DB_WEATHER_UUR_TAB + " succesvol geopend." )

    # open van temperatuur database
    try:
        temperature_db.init(const.FILE_DB_TEMPERATUUR_FILENAME ,const.DB_TEMPERATUUR_TAB )
        # fix the datbase structure from version 0.8.18 onwards, remove in the future
        temperature_db.change_table( flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_TEMPERATUUR_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 8 )
        
    msgToInfoLogAndStatusFile( "database " + const.DB_TEMPERATUUR_TAB + " succesvol geopend." )

    """
    # open van watermeter databases (oud nodig voor import.)
    try:
        watermeter_db_uur.init( const.FILE_DB_WATERMETER, const.DB_WATERMETER_UUR_TAB, flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_WATERMETER_UUR_TAB+ ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 9 )
        
    msgToInfoLogAndStatusFile( "database " + const.DB_WATERMETER_UUR_TAB + " succesvol geopend." )
    

    try:
        watermeter_db_dag.init( const.FILE_DB_WATERMETER ,const.DB_WATERMETER_DAG_TAB , flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_WATERMETER_DAG_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 10 )

    msgToInfoLogAndStatusFile( "database " + const.DB_WATERMETER_DAG_TAB + " succesvol geopend." )

    try:
        watermeter_db_maand.init( const.FILE_DB_WATERMETER ,const.DB_WATERMETER_MAAND_TAB ,flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_WATERMETER_MAAND_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 11 )

    msgToInfoLogAndStatusFile( "database " + const.DB_WATERMETER_MAAND_TAB + " succesvol geopend." )

    try:
        watermeter_db_jaar.init( const.FILE_DB_WATERMETER ,const.DB_WATERMETER_JAAR_TAB, flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_WATERMETER_JAAR_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 12 )

    msgToInfoLogAndStatusFile( "database " + const.DB_WATERMETER_JAAR_TAB + " succesvol geopend." )
    """

    # open van watermeter V2 database 
    try:    
        watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_WATERMETERV2_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 13 )

    msgToInfoLogAndStatusFile( "database " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

    # open van fase database
    try:
        fase_db.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_REALTIME_TAB )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_FASE_REALTIME_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 14 )

    msgToInfoLogAndStatusFile( "database " + const.DB_FASE_REALTIME_TAB + " succesvol geopend." )

    # open van power production database kWh(S0)
    try:    
        power_production_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_TAB, flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_POWERPRODUCTION_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 15 )

    msgToInfoLogAndStatusFile( "database " + const.DB_POWERPRODUCTION_TAB + " succesvol geopend." )

    # open van power production database Solar
    try:
        power_production_solar_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_SOLAR_TAB, flog )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_POWERPRODUCTION_SOLAR_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 16 )

    msgToInfoLogAndStatusFile( "database " + const.DB_POWERPRODUCTION_SOLAR_TAB + " succesvol geopend." )

    # open van fase database voor min/max waarden.
    try:
        fase_db_min_max_dag.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_MINMAX_DAG_TAB )
    except Exception as e:
        msg = ": database niet te openen (" + const.DB_FASE_MINMAX_DAG_TAB + ") melding: " + str(e.args[0] )
        writeLineToStatusFile( msg )
        flog.critical(inspect.stack()[0][3] + ": " + msg )
        stop( 17 )

    msgToInfoLogAndStatusFile( "database " + const.DB_FASE_MINMAX_DAG_TAB + " succesvol geopend." )

#####################################################
# exit the program as clean as possible by closing  #
# alle files, etc.                                  #
# exit parameter is the exit code of the process    #
# exit.                                             #
#####################################################
def stop(exit=0):
    try: 
        config_db.strset('0', 137, None ) # run flag
        config_db.strset('', 138, None )  # file name to process
    except Exception as e:
        print ( "gefaald met het reset van de config id 137 (run flag) :" + str(e.args[0]) )
    sys.exit( exit )
    
#####################################################
# exit the program when recieving a signal          #
#####################################################
def saveExit(signum, frame):
    #setFileFlags()
    signal.signal(signal.SIGINT, original_sigint)
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    stop( 2000 ) 

#-------------------------------
if __name__ == "__main__":
    try: 
        os.umask( 0o002 )
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log", prgname)    
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )

        original_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, saveExit)

    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        stop( 1 )
    
    Main(sys.argv[1:])
