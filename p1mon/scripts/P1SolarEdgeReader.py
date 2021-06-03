#!/usr/bin/python3

import const
import datetime
import datetime_delta_lib
import inspect
import logger
import os
import power_tariff_lib
import pwd
import signal
import sqldb
import sys
import time
import time_slot_lib
import solaredge_lib
import solaredge_shared_lib
import makeLocalTimeString 

# programme name.
prgname = 'P1SolarEdgeReader'

config_db                   = sqldb.configDB()
rt_status_db                = sqldb.rtStatusDb()
power_production_solar_db   = sqldb.powerProductionSolarDB()

LOOP_TIMEOUT_IN_SEC         = 30

def Main( argv ): 

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    ###################################
    # init stuff                      #
    ###################################
    apikey   = ""     # API key decoded to a string
    api      = None   # Object to retrieve API based data

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.debug( inspect.stack()[0][3]+": database tabel " + const.DB_CONFIG_TAB + " succesvol geopend.")

    try:    
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": Database niet te openen(2)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info( inspect.stack()[0][3]+": database tabel " + const.DB_STATUS_TAB + " succesvol geopend.")

    # open van power production database for the solar data
    try:
        power_production_solar_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_SOLAR_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(3)." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_POWERPRODUCTION_SOLAR_TAB + " succesvol geopend." )

    # DEBUG TODO # LET OP DE TIMEPERIOD ID
    power_production_solar_db.excute("delete from powerproduction_solar where power_source_id=1 and TIMEPERIOD_ID = 41 and TIMESTAMP > '2010-03-13 14:00:00';")


    ######################################################
    # Main loop                                          #
    ######################################################
    time_out_in_seconds = 0 
    list_of_time_slots_solar = [[5,19],[20,34],[35,49],[50,59]] # start 5 minutes after the data should be uploaded and available from the API
    ts_selector              = time_slot_lib.time_slot_selector( flog=flog, time_slots_list=list_of_time_slots_solar )

    while True:
        time.sleep(time_out_in_seconds) 

        

        try:
            _id, smart_api_calls, _label = config_db.strget( 146, flog )
            if int(smart_api_calls) == 1:
                now = datetime.datetime.now()
                if now.hour < 6 or now.hour > 21:
                    flog.debug( inspect.stack()[0][3] + ": slimme updates staat aan, geen updates tijdens de nacht/donker uren." )
                    continue
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": slimme API calls configuratie fout -> " + str(e.args[0]) )


        tariff_index = int(1)
        try:
            _id, tariff_type, _label = config_db.strget( 143, flog ) 
            tariff_index = int(tariff_type)
            flog.debug(inspect.stack()[0][3]+": hoog/laag berekend tarief is " + str( tariff_index ) )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ":  hoog/laag berekend tarief kon niet worden gelezen, tarief hoog wordt gebruikt -> " + str(e.args[0]) ) 


        ######################################################
        # only process data in the 15 minute time slots.     #
        ######################################################
        #flog.setLevel( logger.logging.DEBUG )
        if ts_selector.timeslot() == True:
            
            #flog.setLevel( logger.logging.INFO )

            # get rid of inactive sites and such.
            solaredge_shared_lib.clean_config_db( config_db=config_db, flog=flog ) 

            meta_data = get_meta_site_data()
            flog.debug( inspect.stack()[0][3] + ": meta data set van actieve sites (basis)" + str( meta_data ) )

            # check if we any site(s) id's else stop.
            if len( meta_data ) == 0:
                flog.warning( inspect.stack()[0][3] + ": geen verwerking. Er zijn geen site(s) geconfigureerd." ) 
                continue

            meta_data = set_api_timestamps( meta_data )
            flog.debug( inspect.stack()[0][3] + ": meta data set van actieve sites (timestamp) " + str( meta_data ) )

            # get smallest start date from meta data, needed because we do one api calls for multiple sites that could have
            # different start dates 
            start_date = get_smalest_timestamp( meta_data )
            end_date = makeLocalTimeString.makeLocalTimeString( mode='short' ) # use current time for the end date in the API call.
            #flog.info( inspect.stack()[0][3] + ": gestart voor periode van " + start_date + " tot " + end_date )

            api_query_list_of_ids = get_site_ids( meta_data )
            #print( api_query_list_of_ids )
            #print ("#=", start_date, end_date )

            # DEBUG 
            #start_date = "2021-03-13"
            #end_date   = "2021-05-13"
            # end DBIG

            ######################################################
            # do check to see if parameter(s) or settings have   #
            # changed.                                           #
            ######################################################
            apikey, api = check_and_set_api_key( apikey=apikey, api=api )

            try:

                list_of_sites   = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
                date_list       = datetime_delta_lib.create_date_list( start_date, end_date, period = 'm', range=1, repeatdate=True )
                list_of_records = list()
                max_timestamp   = '1970-01-01 00:00:00' # used to check that er no double records in the list  

                #print( date_list )

                #######################################################
                # read in set of time limit multiple set from the API #
                #######################################################
                for date_set in date_list:
                    #print ("#=", date_set[0], date_set[1] )
                    data = api.get_energy( 
                    api_query_list_of_ids,
                    date_set[0], 
                    date_set[1], 
                    time_unit=solaredge_lib.API_MINUTE 
                    )
                    rt_status_db.timestamp( 111, flog )

                    #flog.info( inspect.stack()[0][3] + ": API CALL GESTART DEBUG VERWIJDEREN !" )

                    ###############################################################
                    # list of records contains the date for a specific site ID    #
                    ###############################################################
                    for idx in range( data['sitesEnergy']['count'] ):
    
                        #print ( "siteId[x] = ", data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                        #print ( "------------------------------")
                        try:
                            site_id = data['sitesEnergy']['siteEnergyList'][ idx ]['siteId']
                            flog.info( inspect.stack()[0][3] + ": gestart met minuut data voor site ID " +\
                                str( site_id ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                            db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                            data_set = data['sitesEnergy']['siteEnergyList'][ idx ]['energyValues']['values']
                            #print ( "data_set length() = ", len(data_set) )

                            for i in range( len(data_set) ):

                                kWh_value = data_set[i]['value']

                                if kWh_value == None:
                                    continue # there is no valid data for this timestamp.
                            
                                rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                                rec[0] = data_set[i]['date']                                  # TIMESTAMP
                                
                                if rec[0] <= max_timestamp:                                   # Make sure there is no double value in the list
                                    #flog.debug( inspect.stack()[0][3] + " skipped timestamp  " + str( rec[0] ) + " all ready processed.")
                                    continue
                                max_timestamp = rec[0] 

                                rec[1] = db_sql_index_number + 1                              # TIMEPERIOD_ID
                                rec[2] = 1                                                    # POWER_SOURCE_ID set to Solar Edge ID, default to 0.

                                #tariff_index = 0
                                if tariff_index == 0:
                                    rec[3] = round(  (kWh_value  / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = 0                                 # PRODUCTION_KWH_LOW
                                else:
                                    # get the low and high tariff pct's
                                    high_tariff_pct, low_tariff_pct = power_tariff_lib.get_hour_percentages( rec[0], tariff_set=tariff_index )
                                    # multiply by percentage and convert Wh to kWh.
                                    rec[3] = round( ( (kWh_value * high_tariff_pct) / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = round( ( (kWh_value * low_tariff_pct ) / 1000 ), 3 ) # PRODUCTION_KWH_LOW

                                #flog.debug( inspect.stack()[0][3] + " record added = : " + str( rec ) )

                                list_of_records.append ( rec.copy() )

                        except Exception as e:
                            rt_status_db.timestamp( 112, flog )
                            flog.warning( inspect.stack()[0][3] + ": probleem met laden data voor API minuut informatie -> " + str(e.args[0]) )

                    flog.debug( inspect.stack()[0][3] + " site ID = : " + str( data['sitesEnergy']['siteEnergyList'][idx]['siteId'] ) +\
                            " verwerkt. " +  str(len(list_of_records)) + " (ruwe) buffer regels" )

                ###############################################################
                # release API object                                          #
                ###############################################################
                # api = None 
                
                ###############################################################
                # get meta data voor the current site ID (tmp_meta_data)      #
                ###############################################################
                for m_data in get_meta_site_data():
                    if m_data['ID'] == data['sitesEnergy']['siteEnergyList'][ idx ]['siteId']:
                        tmp_meta_data = m_data
            
                #print( tmp_meta_data )

                ###############################################################
                # clean the list of records that are already in the database  #
                # based on the timestamp in the database                      #
                ###############################################################
               
                tmp_list_of_records = []
                for row in list_of_records:
                    if row[0] > tmp_meta_data['MAX_DB_TIMESTAMP']:
                        tmp_list_of_records.append ( row )

                list_of_records.clear()
                list_of_records = tmp_list_of_records.copy() # keep the var. name the same.

                flog.debug( inspect.stack()[0][3] + " site ID = : " + str( data['sitesEnergy']['siteEnergyList'][idx]['siteId'] ) +\
                    " verwerkt. " +  str(len(list_of_records)) + " daadwerkelijk te verwerken buffer regels." )


                if len( list_of_records) == 0:
                    flog.info( inspect.stack()[0][3] + ": geen nieuwe data van de API om te verwerken " )
                    continue # back to loop.


                #print ( len(tmp_list_of_records)  )
                ###############################################################
                # only continue the processing of the data if the buffer is   #
                # loaded                                                      #
                ###############################################################
                if len( list_of_records) != 0: # there is data, so process the rest

                    ##############################################
                    # determine the totals for the found site ID #
                    # set the totals of high, low en both        #
                    ##############################################
                    solaredge_shared_lib.recalculate_totals( list_of_records,
                        total_high_offset=tmp_meta_data['MAX_PRODUCTION_KWH_HIGH_TOTAL'] ,
                        total_low_offset=tmp_meta_data['MAX_PRODUCTION_KWH_LOW_TOTAL'], 
                        flog=flog )

                    flog.info( inspect.stack()[0][3] + ": minuut data wordt verwerkt." )
                    # Bulk processing is about 40% faster then record for record
                    try:
                        #raise Exception("TEST")
                        # make a string of SQL statements
                        sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog )
                        #print ( "sql_script=", sql_script )
                        power_production_solar_db.executescript( sql_script )
                    except Exception as e:
                        flog.warning( inspect.stack()[0][3] + ": bulk update gefaald, record voor record wordt verwerkt." + str(e.args[0]) )
                        # use failsave if the bulk fails.
                        idx = 0
                        while idx < len( list_of_records ):
                            sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog , first_idx=idx, last_idx=idx )
                            power_production_solar_db.executescript( sql_script )
                            idx += 1

                    
                    flog.info( inspect.stack()[0][3] + ": uur data wordt verwerkt." )
                    update_db( start_date=tmp_meta_data['MAX_DB_TIMESTAMP'] , end_date=end_date, base_period_id=tmp_meta_data['DB_INDEX'], period='h' )
                    
                    flog.info( inspect.stack()[0][3] + ": dag data wordt verwerkt." )
                    update_db( start_date=tmp_meta_data['MAX_DB_TIMESTAMP'] , end_date=end_date, base_period_id=tmp_meta_data['DB_INDEX'], period='d' )
                    
                    flog.info( inspect.stack()[0][3] + ": maand data wordt verwerkt." )
                    update_db( start_date=tmp_meta_data['MAX_DB_TIMESTAMP'], end_date=end_date, base_period_id=tmp_meta_data['DB_INDEX'], period='m' )
                    
                    flog.info( inspect.stack()[0][3] + ": jaar data wordt verwerkt." )
                    update_db( start_date=tmp_meta_data['MAX_DB_TIMESTAMP'] , end_date=end_date, base_period_id=tmp_meta_data['DB_INDEX'], period='y' )

                    # delete min, hour, day records passed the retention time.
                    flog.info( inspect.stack()[0][3] + ": verouderde data wordt verwijderd." )
                    list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
                    solaredge_shared_lib.clean_db_by_renention(db=power_production_solar_db, flog=flog, site_list=list_of_sites )
                    
                    flog.info( inspect.stack()[0][3] + ": gereed." )

            except Exception as e:
                rt_status_db.timestamp( 112, flog )
                flog.warning( inspect.stack()[0][3] + ": probleem met laden data -> " + str(e.args[0]) )

        #sys.exit()

        if time_out_in_seconds < LOOP_TIMEOUT_IN_SEC: # the timeout is inital set to zero (0) and now set to the normal looptime.
            time_out_in_seconds = LOOP_TIMEOUT_IN_SEC
        



###########################################################################
# get a list of site ID's from the metadata set                           #
###########################################################################
def get_site_ids( meta_data ):
    list_of_ids = list()
    for item in meta_data:
        list_of_ids.append( item['ID']) 
    return list_of_ids


###########################################################################
# get the smalest timestamp from the metadata set or the current          #
# timestamp if there is no meta data                                      #
###########################################################################
def get_smalest_timestamp( meta_data ):
    
    timestamp = makeLocalTimeString.makeLocalTimeString( mode='short' ) # use current time as possible smallest time
    
    for item in meta_data:
        if item['START_DATE'] < timestamp:
            timestamp = item['START_DATE']

    return timestamp


###########################################################################
# determine from the sql database what the newest date in the database is #
# to determine the timestamp range to get from the API.                   #
###########################################################################
def set_api_timestamps( meta_data ):
    for item in meta_data:
        #print ( item )
        try:
            sql_select = "select max(timestamp) from " + const.DB_POWERPRODUCTION_SOLAR_TAB +\
                    " where power_source_id=1 and TIMEPERIOD_ID = " + str( item['DB_INDEX']+1 ) #+1 is minutes
            record = power_production_solar_db.select_rec( sql_select )
            if record[0][0] != None:
                date = str( record[0][0] )[0:10]
                item['START_DATE'] = date
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": laatste SQL timestamp is niet te lezen." + str( e ) )
    
    return meta_data


##########################################################
# only read the active sites and return a list of active #
# sites with the atributes from the ENTRY dict.          #
##########################################################
def get_meta_site_data():

    ENTRY = {
        'START_DATE'                    : '',
        'DB_INDEX'                      : 0,
        "ID"                            : 0,
        'MAX_PRODUCTION_KWH_HIGH_TOTAL' : 0.0, 
        'MAX_PRODUCTION_KWH_LOW_TOTAL'  : 0.0,
        'MAX_PRODUCTION_KWH_TOTAL'      : 0.0,
        'MAX_DB_TIMESTAMP'              :'',
    }

    list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )

    api_query_set = list()

    for item in list_of_sites:
        try:
            try:
                # check if active else skip
                if item['SITE_ACTIVE'] == False:
                    flog.info( inspect.stack()[0][3] + ": site ID " + str( item['ID'] ) + " wordt niet verwerkt, site is niet actief." )
                    continue
                entry = ENTRY.copy()
                entry['START_DATE']         = item['START_DATE']
                entry['MAX_DB_TIMESTAMP']   = item['START_DATE']
                entry['DB_INDEX']           = item['DB_INDEX']
                entry['ID']                 = item['ID']
                api_query_set.append( entry )
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": probleem met laden van site ID " + str( item['ID'] ) + " -> " + str(e.args[0]) )
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": herladen van sites mislukt gestopt -> " + str(e.args[0]) )

    # DEBUG add a second index for testing 
    #entry = ENTRY.copy()
    #entry['START_DATE'] = item['START_DATE']
    #entry['DB_INDEX']   = 30
    #entry['ID']         = item['ID']
    #api_query_set.append( entry )

    #set values from the database if there are any values.

    for item in api_query_set:

        try:
            sql_select = "select TIMESTAMP, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL from " + const.DB_POWERPRODUCTION_SOLAR_TAB +\
                " where power_source_id=1 and TIMEPERIOD_ID = " + str(item['DB_INDEX']+1) + \
                " and timestamp == ( select max(timestamp) from " + const.DB_POWERPRODUCTION_SOLAR_TAB + \
                " where power_source_id=1 and TIMEPERIOD_ID = " + str(item['DB_INDEX']+1) + ");"
            #print ( sql_select )
            record = power_production_solar_db.select_rec( sql_select )
            if record != []:
                item['MAX_DB_TIMESTAMP']                = str(record[0][0])
                item['MAX_PRODUCTION_KWH_HIGH_TOTAL']   =  record[0][1]
                item['MAX_PRODUCTION_KWH_LOW_TOTAL']    =  record[0][2]
                item['MAX_PRODUCTION_KWH_TOTAL']        =  record[0][1] + record[0][2]
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": probleem met laden DB data -> " + str(e.args[0]) )


    return api_query_set


##########################################################
# replaces h,d,m or year records from minute datebase    #
##########################################################
def update_db( start_date, end_date ,base_period_id=20, period = 'h' ):

    flog.debug( inspect.stack()[0][3] + ": start_date=" + start_date + " end_date="  + end_date + " base_period_id=" + str(base_period_id) + " period=" + period)

    if period == 'h':
        base_period_id += 1
        substr_count = 14
        timestamp_suffix = ":00:00"
    elif period == 'd':
        substr_count = 11
        base_period_id += 2
        timestamp_suffix = " 00:00:00"
    elif period == 'm':
        substr_count = 8
        base_period_id += 3
        timestamp_suffix = "-01 00:00:00"
    elif period == 'y':
        substr_count = 5
        base_period_id += 4
        timestamp_suffix = "-01-01 00:00:00"

    try:
        #sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog )
        list_of_records = list()

        sql_select = "select distinct substr(TIMESTAMP,0," + str(substr_count) + ") from " +\
            const.DB_POWERPRODUCTION_SOLAR_TAB +\
            " where power_source_id=1 and TIMEPERIOD_ID = " + str(base_period_id) +\
            " and substr(TIMESTAMP,0," + str(substr_count) + ") >= '" + str(start_date)[0:substr_count-1] + "'"

        #flog.debug( inspect.stack()[0][3] + ": select SQL " + sql_select )

        records = power_production_solar_db.select_rec( sql_select )
        #print ( records )

        for timestamp in records:
            try:
                #print( timestamp[0] )
                sql_select = "select sum(production_kwh_high),sum(production_kwh_low), max(PRODUCTION_KWH_HIGH_TOTAL),\
                max(PRODUCTION_KWH_LOW_TOTAL), max(PRODUCTION_KWH_TOTAL) from powerproduction_solar\
                where power_source_id=1 and TIMEPERIOD_ID = " + str(base_period_id) + \
                " and substr(TIMESTAMP,0," + str(substr_count) + ") == '" + timestamp[0][0:substr_count-1] + "'"
                #print ( sql_select )

                record = power_production_solar_db.select_rec( sql_select )
                #print ( record )

                rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC
                rec[0] = str( timestamp[0] + timestamp_suffix  )
                rec[1] = str( base_period_id + 1 )
                rec[2] = 1
                rec[3] = record[0][0]
                rec[4] = record[0][1]
                rec[5] = record[0][2]
                rec[6] = record[0][3]
                rec[7] = record[0][4]
               
                list_of_records.append( rec.copy() )

            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": fout bij het inlezen van totaal waarde voor timestamp " + str(timestamp[0]) + " -> "+ str(e.args[0]) )


        #print("##", list_of_records )

        # Bulk processing is about 40% faster then record for record
        try:
            #raise Exception("TEST")
            # make a string of SQL statements
            sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog )
            #print ( "sql_script=", sql_script )
            power_production_solar_db.executescript( sql_script )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": bulk update gefaald, record voor record wordt verwerkt." + str(e.args[0]) )
            # use failsave if the bulk fails.
            idx = 0
            while idx < len( list_of_records ):
                sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog , first_idx=idx, last_idx=idx )
                power_production_solar_db.executescript( sql_script )
                idx += 1

    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": fout bij het inlezen van tijdspanne van records -> " + str(e.args[0]) )


########################################################
# check if the API key is changed and make an new API  #
# connection if necessary.                             #
########################################################
def check_and_set_api_key( apikey="", api=None ):

    try:
        apikey_from_config = solaredge_shared_lib.read_api_key( config_db )
        flog.debug( inspect.stack()[0][3] + ": solaredge_apikey=" + apikey_from_config )
        if apikey != apikey_from_config:
            apikey = apikey_from_config
            flog.debug( inspect.stack()[0][3] + ": solaredge api key is aangepast/ingesteld (" + apikey + ").")
            try:
                api = solaredge_lib.Solaredge( apikey , debug=False ) # debug is for the solaredge lib only.
                rt_status_db.timestamp( 111, flog ) # last time a Solar Edge Api call was made 
            except Exception as e:
                rt_status_db.timestamp( 112, flog ) # last time a Solar Edge API call failed
                flog.critical( inspect.stack()[0][3] + ": API key fout. melding: " + str(e.args[0]) )

    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": API key fout. melding: " + str(e.args[0]) )

    return apikey, api


########################################################
# close program when a signal is recieved.             #
########################################################
def saveExit(signum, frame):
    flog.info( inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    signal.signal(signal.SIGINT, original_sigint)
    sys.exit(0)

########################################################
# init                                                 #
########################################################
if __name__ == "__main__":
    global process_bg 
    try:
        os.umask( 0o002 )
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log" , prgname)    
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]))
        sys.exit(1)
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT, saveExit)
    Main(sys.argv[1:])           

