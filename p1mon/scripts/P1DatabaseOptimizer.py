# run manual with ./P1NginxConfig

import argparse
import base64
import const
import calendar
import datetime
import filesystem_lib
import glob
import inspect
import logger
import listOfPidByName
import os
import pwd
import pathlib
import sqldb
import signal
import sqlite_lib
import sys
import shutil
import time
import uuid

help_text_1 =\
"""
Het uitvoeren van dit script op de ram folder terwijl de P1 monitor actief is niet toegestaan. 
De kans dat er data verloren gaat of de database corrupt raakt is erg groot.
Stop de P1-monitor en voer het commando opnieuw in.
Start en stoppen van de P1 monitor via de commando’s ./p1mon.sh stop en ./p1mon.sh start in de folder /p1mon/scripts.
"""

# programme name.
prgname = 'P1DatabaseOptimizer'

OLDEST_TIMESTAMP_TABLES = "2014-01-01 00:00:00"

t=time.localtime()
RECOVERY_EXTENTION = "%04d%02d%02d%02d%02d%02d"% (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec) + const.FILE_DB_RECOVERY_EXT
FULL_RECOVERY_FOLDER = const.DIR_RECOVERY + "FULL-" + "%04d%02d%02d%02d%02d%02d"% (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

def Main( argv ):

    base_folder = None

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
    action='help', default=argparse.SUPPRESS,
    help='Dit programma probeert database bestanden te herstellen zover dat mogelijk is. Als database bestanden daadwerkelijke corrupt zijn dan kan de optie --forced worden gebruikt.')

    parser.add_argument( '-d', '--diskdatafolder', 
    required=False,
    action="store_true",
    help="verwerkt de database folder " + const.DIR_FILEDISK 
    )

    parser.add_argument( '-r', '--ramdatafolder', 
    required=False,
    action="store_true",
    help="verwerk database folder " + const.DIR_RAMDISK
    )

    parser.add_argument( '-rrf', '--removerecoveryfiles', 
    required=False,
    action="store_true",
    help="wis alle recovery bestanden in " + const.DIR_RECOVERY
    )

    parser.add_argument( '-fdb', '--forceddatabase',
    required=False,
    action="store_true",
    help="forceer een gehele nieuwe database set met data die nog te redden is (looptijd is 3 tot 6 min.)"
    )

    parser.add_argument( '-rgd', '--removegasdata', 
    required=False,
    action="store_true",
    help="verwijder alle historische gas data inclusief de financiele data. Gevaarlijk!"
    )

    parser.add_argument( '-ws', '--watermeterschema', 
    required=False,
    action="store_true",
    help="Verhelp een fout in de watermeter tabel schema."
    )

    parser.add_argument( '-cu', '--cleanup', 
    required=False,
    action="store_true",
    help="Wis verouderde data."
    )


    args = parser.parse_args()

    if args.removerecoveryfiles:
        remove_all_recovery_files()
        flog.info( inspect.stack()[0][3] + ": gereed.")
        sys.exit(0)

    if args.diskdatafolder:
        base_folder = const.DIR_FILEDISK 
    
    if args.ramdatafolder:
        base_folder = const.DIR_RAMDISK

    if base_folder == None:
        flog.warning( inspect.stack()[0][3] + ": Geen database folder ingesteld, gebruik -d or -r flags. Program stop." )
        sys.exit(1)

    if args.removegasdata:

        try:
            make_recovery_copy( base_folder=base_folder, filepath=const.FILE_DB_E_HISTORIE ) 
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": recovery file probleem, gestopt. melding:" + str(e.args[0]) )
            sys.exit(1)

        remove_gas_data( base_folder=base_folder )
        flog.info( inspect.stack()[0][3] + ": gereed.")
        sys.exit(0)

    if args.watermeterschema:
        watermeter_schema_fix ( base_folder=base_folder , flog=flog )
        flog.info( inspect.stack()[0][3] + ": gereed.")
        sys.exit(0)

    if args.cleanup:
        all_recovery_copy( base_folder=base_folder )
        clean_databases( base_folder = base_folder )
        flog.info( inspect.stack()[0][3] + ": gereed.")
        sys.exit(0)


    flog.info( inspect.stack()[0][3] + ": database folder " + str(base_folder) +  " wordt gebruikt." )

    timediffernce = check_for_valid_time()
    if ( timediffernce == 0 ):
        flog.warning( inspect.stack()[0][3] + ": systeem tijd lijkt niet correct te staan, gestopt." )

    #check if recovery folder exist, when not create the folder
    try:
        check_recovery_folder()
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": recovery folder probleem, gestopt. melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": recovery files in " + const.DIR_RECOVERY + "<DB bestand> met de extentie ." +str(RECOVERY_EXTENTION) )


    if args.forceddatabase:
        # when the live database is used, do a check ik the process is not running

        if base_folder == const.DIR_RAMDISK:
            flog.info( inspect.stack()[0][3] + ": controle of de P1-monitor actief is." )

            list_of_process_names = ["P1SerReader.py","P1Db.py","P1Watchdog.py","P1DropBoxDeamon.py","P1UdpBroadcaster.py","P1UdpDaemon.py","P1Notifier.py","P1WatermeterV2.py","P1GPIO.py","P1PowerProductionS0.py","P1SolarEdgeReader.py"]

            list_off_pids = []
            for name in list_of_process_names:
                pid_list, _process_list = listOfPidByName.listOfPidByName( name )
                if len(pid_list) > 0:
                    list_off_pids.append( pid_list )
            
            if len(list_off_pids) > 0:
                print( help_text_1 )
                flog.warning( inspect.stack()[0][3] + ": gestopt omdat de P1-monitor nog actief is, er zijn " + str(len(list_off_pids)) + " process(en) actief.")
                sys.exit(1)

        # make a copy of the files that will nbe processed.
        all_recovery_copy( base_folder=base_folder )

        # make a session specific subfolder for forced recovery
        try:
            check_recovery_folder( filepath=FULL_RECOVERY_FOLDER )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": full recovery folder probleem, gestopt. melding:" + str(e.args[0]) )
            sys.exit(1)
        flog.info( inspect.stack()[0][3] + ": full recovery files in " + FULL_RECOVERY_FOLDER  )

     
        flog.info( inspect.stack()[0][3] + ": maak nieuwe database bestanden en tabellen.")
        # create empty databases for all in use 
        sdb = sqlite_lib.SqlDatabase()
        sdb.init(flog=flog)
        sdb.create_all_database( db_pathfile = FULL_RECOVERY_FOLDER )

        flog.info( inspect.stack()[0][3] + ": exporten van data naar SQL commando's, geduld!")

        # needs mulitple calls 
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_CONFIG,               flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_STATUS,               flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_FINANCIEEL,           flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_E_FILENAME,           flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_E_HISTORIE,           flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_WEATHER,              flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_WEATHER_HISTORIE,     flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_TEMPERATUUR_FILENAME, flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_PHASEINFORMATION,     flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_POWERPRODUCTION,      flog=flog )
        export_create_database( base_folder=base_folder, db_file=const.FILE_DB_WATERMETERV2,         flog=flog )
        
        flog.info( inspect.stack()[0][3] + ": importeren van SQL commando's naar nieuwe databases gestart.")
        import_sql( filepath=FULL_RECOVERY_FOLDER, flog=flog ) 
        flog.info( inspect.stack()[0][3] + ": importeren van SQL commando's naar nieuwe databases gereed.")

        # copying from tmp folder to ram or disk (as selected )
        files = [ f.path for f in os.scandir(FULL_RECOVERY_FOLDER) if f.is_file() ]
        for dbfile_source in files:

            destination_dbfile = base_folder + os.path.basename( dbfile_source )

            try:
                total_records = count_records_in_db( dbfile_source )

                if total_records > 0:
                    flog.info( inspect.stack()[0][3] + ": " + str(dbfile_source)  + " bevat totaal " + str(total_records) + " records")
                    shutil.copy2( dbfile_source, destination_dbfile  )
                    flog.info( inspect.stack()[0][3] + ": kopieren van  " + str(dbfile_source)  + " naar " + str(destination_dbfile) + " succesvol.")
                else:
                    flog.warning( inspect.stack()[0][3] + ": " + str(dbfile_source)  + " bevat geen records, geen actie uitgevoerd.")

            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": kopieren van  " + str(dbfile_source)  + " naar " + str(destination_dbfile) + " gefaald. -> "+ str(e.args[0]) )
 
        flog.info( inspect.stack()[0][3] + ": gereed.")




###############################################
# count all records of all tables             #
###############################################
def count_records_in_db( db_pathfile=None ):

    sqlutil = sqlite_lib.SqliteUtil()
    sqlutil.init( db_pathfile=db_pathfile, flog=flog )

    table_list = sqlutil.list_tables_in_database()
    total_record_cnt = 0

    for tab in table_list:
        total_record_cnt = total_record_cnt + int(sqlutil.count_records(tab))

    return total_record_cnt

##################################################
# watermeter tabel has faulty schema             #
# was "TIMESTAMP TEXT     TEXT NOT NULL" must be #
# "TIMESTAMP TEXT  NOT NULL"                     #
# finance tables, normaly not used               #
##################################################
def watermeter_schema_fix( base_folder=None, flog=None ):

    watermeter_db = sqldb.WatermeterDBV2()
    watermeter_db_old = sqldb.WatermeterDBV2()

    filename = base_folder + os.path.basename( const.FILE_DB_WATERMETERV2 )
    flog.info( inspect.stack()[0][3] + ": controle van watermeter schema voor file " + str(filename))
    su = sqlite_lib.SqliteUtil()
    su.init( db_pathfile=filename, flog=flog )
    tab_struct = su.table_structure_info( table=const.DB_WATERMETERV2_TAB )
    if len(tab_struct) == 0:
        flog.info( inspect.stack()[0][3] + "tabel "+ const.DB_WATERMETERV2_TAB + " bestaat niet of is niet te lezen." ) 
        return
    
    # get column types
    column_type_list = []
    for idx, c in enumerate( tab_struct ):
        column_type_list.append(c['column_type'])

    try:
        #print( column_type_list[0] )
        if str(column_type_list[0]).strip() == "TEXT":
            flog.info( inspect.stack()[0][3] + " type niet gevonden, geen actie ondernomen tabel is in orde." ) 
            return
        # fault exists, fixing it.

        try:
            make_recovery_copy( base_folder=base_folder, filepath=const.FILE_DB_WATERMETERV2 ) 
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": recovery file probleem, gestopt. melding:" + str(e.args[0]) )
            sys.exit(1)

        tmp_db_filename = random_filename()
       
        try:
            watermeter_db.init( tmp_db_filename, const.DB_WATERMETERV2_TAB, flog )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": Database niet te openen " + tmp_db_filename + " melding:" + str(e.args[0]) )
            return
        flog.info( inspect.stack()[0][3] + ": tijdelijk database tabel " + const.DB_WATERMETERV2_TAB + " succesvol aangemaakt in " +str(tmp_db_filename) )

        # open file 
        try:
            watermeter_db_old.init( filename , const.DB_WATERMETERV2_TAB, flog )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": Database niet te openen " + filename  + " melding:" + str(e.args[0]) )
            return
        flog.info( inspect.stack()[0][3] + ": bestaande database " + filename  + " succesvol geopend." )

        tmp_db_export_filename = random_filename(filename_ext=".sql")
        try:
            flog.info( inspect.stack()[0][3] + ": database export gestart." )
            watermeter_db_old.sql2file( tmp_db_export_filename )
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": Database niet te exporten " + filename  + " melding:" + str(e.args[0]) )
            return
        flog.info( inspect.stack()[0][3] + ": database succesvol exportereerd." )

        # fill the new database.
        try:
            su = sqlite_lib.SqliteUtil()
            su.init(db_pathfile=tmp_db_filename, flog=flog)
                
            flog.info( inspect.stack()[0][3] + ": import " + str(tmp_db_export_filename) + " wordt verwerkt, geduld aub.")
            with open( tmp_db_export_filename, mode='r', encoding="utf-8") as f:
                sqldata_lines = f.read()
                # SQL script skips faulty lines!
                su.executescript( sqldata_lines ) 
                flog.info( inspect.stack()[0][3] + ":import is succesvol verwerkt.")
        except Exception as e:
             flog.error( inspect.stack()[0][3] + ": Database niet te importeren " + tmp_db_export_filename  + " melding:" + str(e.args[0]) )
             return
        
        # remove tmp import SQL file
        os.remove( tmp_db_export_filename)

        # rename old database file
        try:
            filesystem_lib.set_file_permissions( filepath=filename, permissions='664' )
            filesystem_lib.set_file_owners( filepath=filename, owner_group='p1mon:p1mon')
            os.rename( filename, filename+ str(".dboptimized") )
        except Exception as e:
             flog.warning( inspect.stack()[0][3] + ": naam wijzigen van database " + str(filename) + " gefaald " + " melding:" + str(e.args[0]) )

        #copy database
        try:
            shutil.copy2( tmp_db_filename, filename )
            flog.info( inspect.stack()[0][3] + ": db file " + str(tmp_db_filename) + " naar file " + str(filename) + " gekopieerd." )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": renaming of database " + str(filename) + " failed " + " melding:" + str(e.args[0]) )
            return

    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": onverwachte fout -> " + str(e.args[0]) )
        return


###############################################
# removes gas data from the historie and      #
# finance tables, normaly not used            #
###############################################
def remove_gas_data( base_folder=None ):

        history_list = ['update e_history_min set verbr_gas_2421 = 0', 'update e_history_uur set verbr_gas_2421 = 0,verbr_gas_x=0','update e_history_dag set verbr_gas_2421 = 0,verbr_gas_x=0','update e_history_maand set verbr_gas_2421 = 0,verbr_gas_x=0','update e_history_jaar set verbr_gas_2421 = 0,verbr_gas_x=0']
        finance_list = ['update e_financieel_dag set gelvr_gas = 0','update e_financieel_maand set gelvr_gas = 0','update e_financieel_jaar set gelvr_gas = 0']

        filename = base_folder + os.path.basename( const.FILE_DB_E_HISTORIE )
        flog.info( inspect.stack()[0][3] + ": gas data verwijderen gestart. voor file " + str(filename))
        try:

            # gas history
            dbase = dbase=sqldb.SqlDb2()
            dbase.init( filename, const.DB_HISTORIE_MIN_TAB )
            for cmd in history_list:
                try:
                    dbase.execute( cmd )
                    flog.info( inspect.stack()[0][3] + " commando '" + str(cmd) + "' uitgevoerd.")
                except Exception as e:
                    flog.error( inspect.stack()[0][3] + ": verwerking gestopt voor commando '" + str(cmd) + "' -> "+ str(e.args[0]) )
            dbase.close_db()

            #finance
            filename = base_folder + os.path.basename( const.FILE_DB_FINANCIEEL )
            flog.info( inspect.stack()[0][3] + ": gas data verwijderen gestart. voor file " + str(filename))
            dbase=sqldb.financieelDb() 
            dbase.init( filename, const.DB_FINANCIEEL_DAG_TAB )
            for cmd in finance_list:
                try:
                    dbase.execute( cmd )
                    flog.info( inspect.stack()[0][3] + " commando '" + str(cmd) + "' uitgevoerd.")
                except Exception as e:
                    flog.error( inspect.stack()[0][3] + ": verwerking gestopt voor commando '" + str(cmd) + "' -> "+ str(e.args[0]) )
            dbase.close_db()

        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": onverwachte fout -> "+ str(e.args[0]) )


###############################################
# import the SQL files into the databases.    #
###############################################
def import_sql( filepath=None, flog=None ):
    #print( "filepath = ",filepath  )

    subfolders = [ f.path for f in os.scandir(filepath) if f.is_dir() ]
    for folder in subfolders:
        db_file = folder + ".db"
        #print( "db_file = ", db_file )

        files = [ f.path for f in os.scandir(folder) if f.is_file() ]
        for sqlfile in files:
            #print( "sqlfile =" ,sqlfile )

            tmp_db_file_name = random_filename(filename_ext=".tmp.db")
            #print ("tmp_db_file_name = ", tmp_db_file_name  )

            try:
                # copy to ram to speed up the operation
                shutil.copy2( db_file, tmp_db_file_name )

                su = sqlite_lib.SqliteUtil()
                su.init( db_pathfile=tmp_db_file_name, flog=flog )
                #print( "table list ",su.list_tables_in_database() )

                flog.info( inspect.stack()[0][3] + ": " + str(sqlfile) + " wordt verwerkt, geduld aub.")
                with open( sqlfile, mode='r', encoding="utf-8") as f:
                    sqldata_lines = f.read()
                    # SQL script skips faulty lines!
                    su.executescript( sqldata_lines ) 
                    #flog.info( inspect.stack()[0][3] + ": " + str(sqlfile) + " is verwerkt.")

                # copy back from ram to disk (flash)
                shutil.copy2( tmp_db_file_name, db_file, )
                os.remove( tmp_db_file_name )

            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": SQL fout op tabel '" + str(os.path.basename(sqlfile)).replace('.SQL','') + "' in database '" + os.path.basename(db_file) + "' -> " + str(e.args[0]))



###############################################
# create SQL statments en write them to files #
###############################################
def export_create_database( base_folder=None,  db_file=None, flog=None ):

    db_pathfile = base_folder + os.path.basename( db_file )

    # create a folder with the database name in the recovery folder to hold the exported 
    # SQL files. 
    sqlfiles_folder_per_db = FULL_RECOVERY_FOLDER + "/" + os.path.splitext( os.path.basename( db_file ))[0]

    #print ( sqlfiles_folder_per_db )
    filesystem_lib.create_folder( filepath=sqlfiles_folder_per_db , flog=flog )
    filesystem_lib.set_file_permissions( filepath=sqlfiles_folder_per_db, permissions='774' )
    filesystem_lib.set_file_owners( filepath=sqlfiles_folder_per_db, owner_group='p1mon:p1mon')

    sqlutil = sqlite_lib.SqliteUtil()
    sqlutil.init( db_pathfile=db_pathfile, flog=flog )

    table_list = sqlutil.list_tables_in_database()
    record_cnt = 0

    for tab in table_list:
        #print( "dbfile = " , db_pathfile, " tab = ", tab, "sqlfiles_folder_per_db = ", sqlfiles_folder_per_db  ) 
        try:
            filepath = sqlfiles_folder_per_db + "/" + tab + ".SQL"
            s2f = sqlite_lib.Sql2File()
            s2f.init( db_pathfile=db_pathfile, table=tab, filename=filepath, flog=flog )
            record_cnt = record_cnt + s2f.execute()
            flog.info ( inspect.stack()[0][3]+ ": " + str( record_cnt) +" records van tabel " + tab + " uit database " + str(os.path.basename( db_file )) + " gelezen." )
            #print( sqlfiles_folder_per_db +".sql" )
        except Exception as e:
            flog.error( inspect.stack()[0][3]+ ": export probleem met tabel " + tab  + " uit database " + str(os.path.basename( db_file )) + " -> " + str(e) )


#################################################
# just a colllection function for easy use      #
#################################################
def clean_databases( base_folder = None ):
    process_by_database( base_folder=base_folder, dbase=sqldb.financieelDb(),      db_file=const.FILE_DB_FINANCIEEL,           db_tab=const.DB_FINANCIEEL_DAG_TAB,  flog=flog )
    process_by_database( base_folder=base_folder, dbase=sqldb.SqlDb1(),            db_file=const.FILE_DB_E_FILENAME,           db_tab=const.DB_SERIAL_TAB,          flog=flog )
    process_by_database( base_folder=base_folder, dbase=sqldb.SqlDb2(),            db_file=const.FILE_DB_E_HISTORIE,           db_tab=const.DB_HISTORIE_MIN_TAB,    flog=flog )
    process_by_database( base_folder=base_folder, dbase=sqldb.currentWeatherDB(),  db_file=const.FILE_DB_WEATHER,              db_tab=const.DB_WEATHER_TAB,         flog=flog, delete_mode=1 )
    process_by_database( base_folder=base_folder, dbase=sqldb.historyWeatherDB(),  db_file=const.FILE_DB_WEATHER_HISTORIE,     db_tab=const.DB_WEATHER_UUR_TAB,     flog=flog )
    process_by_database( base_folder=base_folder, dbase=sqldb.temperatureDB(),     db_file=const.FILE_DB_TEMPERATUUR_FILENAME, db_tab=const.DB_TEMPERATUUR_TAB,     flog=flog )
    process_by_database( base_folder=base_folder, dbase=sqldb.PhaseDB(),           db_file=const.FILE_DB_PHASEINFORMATION,     db_tab=const.DB_FASE_REALTIME_TAB,   flog=flog )
    process_by_database( base_folder=base_folder, dbase=sqldb.powerProductionDB(), db_file=const.FILE_DB_POWERPRODUCTION,      db_tab=const.DB_POWERPRODUCTION_TAB, flog=flog, mode=1)
    process_by_database( base_folder=base_folder, dbase=sqldb.WatermeterDBV2(),    db_file=const.FILE_DB_WATERMETERV2,         db_tab=const.DB_WATERMETERV2_TAB,    flog=flog, mode=1)


#################################################
# function for cleaning and updating the        #
# database.                                     #
# mode 0 do DB init without file log (flog)     #
# mode 1 do DB init with file log (flog)        #
# delete_mode see: delete_with_timestamp()      #
#################################################
def process_by_database( base_folder=None, dbase=None, db_file=None, db_tab=None, flog=None, mode=0, delete_mode=0 ):

    filename = base_folder + os.path.basename( db_file )

    flog.info( inspect.stack()[0][3] + ": database " + filename +  " controle gestart." )

    if ( os.path.isfile(filename)):

        try:
            make_recovery_copy( base_folder=base_folder, filepath=filename )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": verwerking gestopt voor " + str(filename)  + " melding:" + str(e.args[0]) )

        try:
            if mode == 0:
                dbase.init( filename, db_tab )
            else:
                dbase.init( filename, db_tab, flog) 
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": database niet te openen " + str(filename)  + " melding:" + str(e.args[0]) )
            flog.warning( inspect.stack()[0][3] + ": database wordt verder verwerkt " + str(filename) )
            return 

        sqlutil = sqlite_lib.SqliteUtil()
        sqlutil.init( db_pathfile=filename, flog=flog )

        table_list = sqlutil.list_tables_in_database()

        for tab in table_list:
            delete_with_timestamp( database=dbase, table=tab, timestamp=OLDEST_TIMESTAMP_TABLES, mode=delete_mode)

    else:
        flog.warning( inspect.stack()[0][3] + ": " + str(filename) + " niet gevonden, geen acties uitgevoerd." )


#######################################################
# delete records older then the expected rentention   #
# time.                                               #
# mode is none, use normal timestamp notation         #
# mode is 1, means table uses epoch timestamp         #
#######################################################
def delete_with_timestamp(database=None, table=None, timestamp=OLDEST_TIMESTAMP_TABLES, mode=None ):

    if mode == 1:
        t=datetime.datetime( 
            int(OLDEST_TIMESTAMP_TABLES[0:4]),
            int(OLDEST_TIMESTAMP_TABLES[5:7]),
            int(OLDEST_TIMESTAMP_TABLES[8:10]),
            int(OLDEST_TIMESTAMP_TABLES[11:13]),
            int(OLDEST_TIMESTAMP_TABLES[14:16]),
            int(OLDEST_TIMESTAMP_TABLES[17:19]),
            )
        
        epoc_timestr = str(calendar.timegm(t.timetuple()))

        sql_delete = "delete FROM " + table + " where TIMESTAMP < '" + epoc_timestr + "'"
        sql_select = "select TIMESTAMP FROM " + table + " where TIMESTAMP < '" + epoc_timestr + "' or length(TIMESTAMP) < 8 "

    else:
        sql_delete = "delete FROM " + table + " where TIMESTAMP < '" + str(timestamp) + "'"
        sql_select = "select TIMESTAMP FROM " + table + " where TIMESTAMP < '" + str(timestamp) + "' or length(TIMESTAMP) != 19"


    #print ( sql_delete )
    #print ( sql_select )
    
    try:
        rec = database.select_rec(sql_select)
        if (rec != None):
            if len(rec) > 0:
                database.execute( sql_delete )
                flog.info( inspect.stack()[0][3] + ": " + str(len(rec)) + " records ouder dan " + str(timestamp)  + " uit tabel " + str(table) + " gewist (hersteld).")
            else:
                flog.info( inspect.stack()[0][3] + ": geen records gevonden die ouder zijn dan " + str(timestamp)  + " in tabel " + str(table) + " (ok)." )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": sql gefaald " + str(sql_delete)  + " melding:" + str(e.args[0]) )
    

#######################################################
# make a copy of the database file to the recovery    #
# folder, add a timestamp to the copy                 #
#######################################################
def make_recovery_copy( base_folder=None, filepath=None ):
    try:
        filename = pathlib.PurePath( filepath ).name
        source = base_folder +  filename 
        destination = const.DIR_RECOVERY + filename + RECOVERY_EXTENTION
        shutil.copy2( source, destination )
        flog.info( inspect.stack()[0][3] + ": recovery bestand " + str(destination) + " gemaakt." )
    except Exception as e:
        raise Exception ("recovery copy gefaald voor bestand " + str( source) )

#######################################################
# make a copy of all the db files to the recovery     #
# folder, add a timestamp to the copy                 #
#######################################################
def all_recovery_copy( base_folder=None ):
    sqldb = sqlite_lib.SqlDatabase()
    sqldb.init( flog=flog )
      
    for db_file_name in sqldb.list_of_all_db_file():
        try:
            make_recovery_copy( base_folder=base_folder, filepath=db_file_name )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": onverwacht fout op database " + str(db_file_name)  + " melding:" + str(e.args[0]) )


#######################################################
# create recovery folder when it not exists and set   #
# ownership / folder privilges                        #
#######################################################
def check_recovery_folder( filepath=const.DIR_RECOVERY ):
    filesystem_lib.create_folder( filepath=filepath, flog=flog )
    filesystem_lib.set_file_permissions( filepath=filepath, permissions='777' ) #TODO rechten aanpassen naar wat nodig is
    filesystem_lib.set_file_owners( filepath=filepath, owner_group='p1mon:p1mon')

########################################################
# try to check if the system time could be right       #
# if the current time is larger then the oldest file   #
# in scripts folder then the time should be right      #
# return the difference of seconds of the oldest file  #
# or return 0 if the time is wrong                     #
########################################################
def check_for_valid_time():

    # return 0 # test

    timestamp = 0
    for file in glob.glob( const.DIR_SCRIPTS + "*.py" ):
        ftimestamp = int(os.path.getmtime(file))
        if (ftimestamp > timestamp):
                timestamp = ftimestamp

    difference = int(time.time()) - timestamp 
    if ( difference > 0 ):
        return difference

    return 0 # time seems to be off

#######################################################
# clear the folder with previous backup files         #
#######################################################
def remove_all_recovery_files():
    for pathfile in glob.glob( const.DIR_RECOVERY + "*"  + const.FILE_DB_RECOVERY_EXT):
        try:
            os.remove( pathfile )
            flog.info ( inspect.stack()[0][3] + ": recovery file " + str(pathfile) + " gewist.")
        except Exception as e:
            flog.warning ( inspect.stack()[0][3] + ": recovery file kan niet worden gewist. melding:" + str(e.args[0]) )

    for path in glob.glob( const.DIR_RECOVERY + "FULL-*"):
        try:
            shutil.rmtree( path)
            flog.info ( inspect.stack()[0][3] + ": recovery folder " + str( path ) + " gewist.")
        except Exception as e:
            flog.warning ( inspect.stack()[0][3] + ": recovery folder kan niet worden gewist. melding:" + str(e.args[0]) )

########################################################
# close program when a signal is recieved.             #
########################################################
def saveExit(signum, frame):
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(0)

#######################################################
# create a randop filename in a (ram) filesystem      #
#######################################################
def random_filename( folder="/p1mon/mnt/ramdisk/", filename_prefix="dboptiomizer.", filename_ext=".db"):

    filename = folder
    if filename_prefix != None:
        filename = filename + filename_prefix
    filename = filename + str(uuid.uuid4())
    if filename_ext != None:
        filename = filename + filename_ext
 
    return filename

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

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])




"""
#######################################################
# check if a record can be read,deleted and insterted #
# first check on a temp file                          #
#######################################################
def check_crud( database=None, table=None):

    #sqlutil = sqlite_lib.SqliteUtil()
    #sqlutil.init( db_pathfile=filename, flog=flog )

    # step one get the oldest record in the table if any 
    sql_select = "select MIN(TIMESTAMP) FROM " + table
    print( sql_select )
    try:
        rec = database.select_rec(sql_select)
        if (rec != None):
            if len(rec) > 0:
                timestamp = str(rec[0][0])
                flog.info( inspect.stack()[0][3] + ": select succesvol op tabel " + str(table) )
                sql_delete = "delete FROM " + table + " where TIMESTAMP = '" + str(timestamp) + "'"
                sql_insert = "insert INTO tabel"
                print( sql_delete  )
               
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": sql gefaald " + str(sql_delete)  + " melding:" + str(e.args[0]) )
"""

