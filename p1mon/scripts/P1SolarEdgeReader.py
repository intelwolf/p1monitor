# run manual with ./P1SolarEdgeReader

import const
import datetime
import datetime_delta_lib
import filesystem_lib
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
from dateutil.relativedelta import relativedelta

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
    flog.info( inspect.stack()[0][3]+": database tabel " + const.DB_CONFIG_TAB + " succesvol geopend.")

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

    filesystem_lib.set_file_permissions(filepath=const.FILE_DB_POWERPRODUCTION, permissions="664" )

    # power_production_solar_db.excute("delete from powerproduction_solar where power_source_id=1 and TIMEPERIOD_ID = 41 and TIMESTAMP > '2010-03-13 14:00:00';")

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

        """
        tariff_index = int(1)
        try:
            _id, tariff_type, _label = config_db.strget( 143, flog ) 
            tariff_index = int(tariff_type)
            flog.debug(inspect.stack()[0][3]+": hoog/laag berekend tarief is " + str( tariff_index ) )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ":  hoog/laag berekend tarief kon niet worden gelezen, tarief hoog wordt gebruikt -> " + str(e.args[0]) ) 
        """

        ######################################################
        # only process data in the 15 minute time slots.     #
        ######################################################
        #flog.setLevel( logger.logging.DEBUG )
        if ts_selector.timeslot() == True:
        #if True:
            
            #flog.setLevel( logger.logging.INFO )

            # get rid of inactive sites and such.
            solaredge_shared_lib.clean_config_db( config_db=config_db, flog=flog ) 

            meta_data = get_meta_site_data()
            flog.debug( inspect.stack()[0][3] + ": meta data set van actieve sites (basis)" + str( meta_data ) )

            # check if we any site(s) id's else stop.
            if len( meta_data ) == 0:
                flog.warning( inspect.stack()[0][3] + ": geen verwerking. Er zijn geen site(s) geconfigureerd." ) 
                continue

            tariff_index = int(1)
            try:
                _id, tariff_type, _label = config_db.strget( 143, flog ) 
                tariff_index = int(tariff_type)
                flog.debug(inspect.stack()[0][3]+": hoog/laag berekend tarief is " + str( tariff_index ) )
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ":  hoog/laag berekend tarief kon niet worden gelezen, tarief hoog wordt gebruikt -> " + str(e.args[0]) ) 

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
            # end DEBUG

            ######################################################
            # do check to see if parameter(s) or settings have   #
            # changed.                                           #
            ######################################################
            apikey, api = check_and_set_api_key( apikey=apikey, api=api )

            ######################################################
            # minute processing                                  #
            ######################################################
            tic = time.perf_counter()
            list_of_records = list()
            max_timestamp   = '1970-01-01 00:00:00' # used to check that er no double records in the list 
            # limit range to dates that exceed the rentention period.
            # delete_limited_date = ( datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')
            try:

                list_of_sites   = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
                date_list       = datetime_delta_lib.create_date_list( start_date, end_date, period = 'm', range=1, repeatdate=True )
                flog.debug( inspect.stack()[0][3] + ": date_list=" + str( date_list) )

                for date_set in date_list:

                    # start_date = "2016-10-25" #DEBUG om range fouten te testen
                    flog.debug( inspect.stack()[0][3] + ": start date=" + str( date_set[0]) + " stop date=" + str( date_set[1]) )

                    data = api.get_energy( 
                        api_query_list_of_ids,
                        date_set[0], 
                        date_set[1], 
                        time_unit=solaredge_lib.API_MINUTE #DIFF
                        )
                    rt_status_db.timestamp( 111, flog )

                    for idx in range( data['sitesEnergy']['count'] ):
    
                        #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                        list_of_records.clear()

                        try:
                            site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                            db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                            flog.info( inspect.stack()[0][3] + ": gestart met minuut data voor site ID " + str( site_id ) +\
                                 " met DB index " +  str( db_sql_index_number ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                            data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                            #print ( "data_set = ", data_set )

                            for i in range( len(data_set) ):

                                kWh_value = data_set[i]['value']

                                if kWh_value == None:
                                    continue # there is no valid data for this timestamp.
                            
                                rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                                rec[0] = data_set[i]['date'][:16]+":00" # TIMESTAMP
                                
                                #flog.info( str(rec) )
                                
                                if rec[0] <= max_timestamp:                                   # Make sure there is no double value in the list
                                    flog.debug( inspect.stack()[0][3] + " skipped timestamp  " + str( rec[0] ) + " all ready processed.")
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

                                flog.debug( inspect.stack()[0][3] + " record added = : " + str( rec ) )

                                list_of_records.append ( rec.copy() )

                        except Exception as e:
                            rt_status_db.timestamp( 112, flog )
                            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor minuut informatie " + str( site_id ) + " -> " + str(e.args[0]) )

                        ####################################################
                        # find previous total values from the SQL database #
                        ####################################################

                        tmp_total_high_offset = 0
                        tmp_total_low_offset  = 0
                        try:
                            start_date_from_api = str( list_of_records[0][0] ) # the oldest timestamp from the API
                            db_index_number_tmp = str( db_sql_index_number + 1 ) # MINUTE
                            
                            sql_timestamp = "select timestamp, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB +\
                                 " where power_source_id=1 and TIMEPERIOD_ID=" + db_index_number_tmp +\
                                 " and timestamp == ( select max(timestamp) from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB + \
                                 " where power_source_id=1 and TIMEPERIOD_ID=" +\
                                 db_index_number_tmp + " and timestamp < '" + start_date_from_api + "')"
                            
                            #flog.debug( inspect.stack()[0][3] + ": sql = " + sql_timestamp )
                            record = power_production_solar_db.select_rec( sql_timestamp )
                            tmp_total_high_offset = float(record[0][1])
                            tmp_total_low_offset  = float(record[0][2])
                            flog.debug( inspect.stack()[0][3] + ": tmp_total_high_offset = " + str(tmp_total_high_offset) +\
                                                                 " tmp_total_low_offset=" + str(tmp_total_low_offset) )
                        except Exception as e:
                            flog.info( inspect.stack()[0][3] + ": geen eerder record gevonden voor totaal waarden, 0 wordt gebruikt als waarde." )

                        ##############################################
                        # determine the totals for the found site ID #
                        # set the totals of high, low en both        #
                        ##############################################
                        solaredge_shared_lib.recalculate_totals( list_of_records,
                            total_high_offset=tmp_total_high_offset ,
                            total_low_offset=tmp_total_low_offset, 
                            flog=flog )

                        # delete records from list that are to old
                        delete_limited_date = ( datetime.datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=31) ).strftime('%Y-%m-%d')

                        clean_list = list()
                        for rec in list_of_records:
                            if rec[0][0:10] < delete_limited_date:
                                continue
                            else:
                                clean_list.append ( rec )

                        list_of_records.clear() # give memory back

                        # make a string of SQL statements
                        sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog )

                        #print( sql_script )
                        #power_production_solar_db.excute('delete from powerproduction_solar')
                        #####################

                        #Bulk processing is about 40% faster then record for record.
                        try:
                            power_production_solar_db.executescript( sql_script )
                        except Exception as e:
                            flog.warning( inspect.stack()[0][3] + ": bulk update minuten gefaald, record voor record worden verwerkt." + str(e.args[0]) )

                            idx = 0
                            while idx < len( clean_list ):
                                sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog , first_idx=idx, last_idx=idx )
                                power_production_solar_db.executescript( sql_script )
                                idx += 1

                toc = time.perf_counter()
                flog.info( inspect.stack()[0][3] + ": " + str( len(clean_list) ) + " minuten records verwerkt in " + f"{toc - tic:0.3f} seconden." )
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor minuten informatie " + str( site_id ) + " -> " + str(e.args[0]) )


            ######################################################
            # hour processing                                    #
            ######################################################
            tic = time.perf_counter()
            list_of_records = list()
            max_timestamp   = '1970-01-01 00:00:00' # used to check that er no double records in the list 
            # limit range to dates that exceed the rentention period.
            # delete_limited_date = ( datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')
            try:

                list_of_sites   = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
                date_list       = datetime_delta_lib.create_date_list( start_date, end_date, period = 'm', range=1, repeatdate=True )
                flog.debug( inspect.stack()[0][3] + ": date_list=" + str( date_list) )

                for date_set in date_list:

                    # start_date = "2016-10-25" #DEBUG om range fouten te testen
                    flog.debug( inspect.stack()[0][3] + ": start date=" + str( date_set[0]) + " stop date=" + str( date_set[1]) )

                    data = api.get_energy( 
                        api_query_list_of_ids,
                        date_set[0], 
                        date_set[1], 
                        time_unit=solaredge_lib.API_HOUR #DIFF
                        )
                    rt_status_db.timestamp( 111, flog )

                    for idx in range( data['sitesEnergy']['count'] ):
    
                        #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                        list_of_records.clear()

                        try:
                            site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                            db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                            flog.info( inspect.stack()[0][3] + ": gestart met uur data voor site ID " + str( site_id ) +\
                                 " met DB index " +  str( db_sql_index_number ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                            data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                            #print ( "data_set = ", data_set )

                            for i in range( len(data_set) ):

                                kWh_value = data_set[i]['value']

                                if kWh_value == None:
                                    continue # there is no valid data for this timestamp.
                            
                                rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                                rec[0] = data_set[i]['date'][:13]+":00:00" # TIMESTAMP
                                
                                #flog.info( str(rec) )
                                
                                if rec[0] <= max_timestamp:                                   # Make sure there is no double value in the list
                                    flog.debug( inspect.stack()[0][3] + " skipped timestamp  " + str( rec[0] ) + " all ready processed.")
                                    continue
                                max_timestamp = rec[0] 

                                rec[1] = db_sql_index_number + 2                              # TIMEPERIOD_ID 
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

                                flog.debug( inspect.stack()[0][3] + " record added = : " + str( rec ) )

                                list_of_records.append ( rec.copy() )

                        except Exception as e:
                            rt_status_db.timestamp( 112, flog )
                            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor minuut informatie " + str( site_id ) + " -> " + str(e.args[0]) )

                        ####################################################
                        # find previous total values from the SQL database #
                        ####################################################
                        tmp_total_high_offset = 0
                        tmp_total_low_offset  = 0
                        try:
                            start_date_from_api = str( list_of_records[0][0] ) # the oldest timestamp from the API
                            db_index_number_tmp = str( db_sql_index_number + 2 ) # HOUR
                            
                            sql_timestamp = "select timestamp, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB +\
                                 " where power_source_id=1 and TIMEPERIOD_ID=" + db_index_number_tmp +\
                                 " and timestamp == ( select max(timestamp) from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB + \
                                 " where power_source_id=1 and TIMEPERIOD_ID=" +\
                                 db_index_number_tmp + " and timestamp < '" + start_date_from_api + "')"
                            
                            #flog.debug( inspect.stack()[0][3] + ": sql = " + sql_timestamp )
                            record = power_production_solar_db.select_rec( sql_timestamp )
                            tmp_total_high_offset = float(record[0][1])
                            tmp_total_low_offset  = float(record[0][2])
                            flog.debug( inspect.stack()[0][3] + ": tmp_total_high_offset = " + str(tmp_total_high_offset) +\
                                                                 " tmp_total_low_offset=" + str(tmp_total_low_offset) )
                        except Exception as e:
                            flog.info( inspect.stack()[0][3] + ": geen eerder record gevonden voor totaal waarden, 0 wordt gebruikt als waarde." )

                        ##############################################
                        # determine the totals for the found site ID #
                        # set the totals of high, low en both        #
                        ##############################################
                        solaredge_shared_lib.recalculate_totals( list_of_records,
                            total_high_offset=tmp_total_high_offset ,
                            total_low_offset=tmp_total_low_offset, 
                            flog=flog )

                        # delete records from list that are to old
                        delete_limited_date = ( datetime.datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')

                        clean_list = list()
                        for rec in list_of_records:
                            if rec[0][0:10] < delete_limited_date:
                                continue
                            else:
                                clean_list.append ( rec )

                        list_of_records.clear() # give memory back

                        # make a string of SQL statements
                        sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog )

                        #Bulk processing is about 40% faster then record for record.
                        try:
                            power_production_solar_db.executescript( sql_script )
                        except Exception as e:
                            flog.warning( inspect.stack()[0][3] + ": bulk update uur gefaald, record voor record worden verwerkt." + str(e.args[0]) )

                            idx = 0
                            while idx < len( clean_list ):
                                sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog , first_idx=idx, last_idx=idx )
                                power_production_solar_db.executescript( sql_script )
                                idx += 1

                toc = time.perf_counter()
                flog.info( inspect.stack()[0][3] + ": " + str( len(clean_list) ) + " uur records verwerkt in " + f"{toc - tic:0.3f} seconden." )
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor uur informatie " + str( site_id ) + " -> " + str(e.args[0]) )


            ######################################################
            # day processing                                     #
            ######################################################
            tic = time.perf_counter()
            list_of_records = list()
            max_timestamp   = '1970-01-01 00:00:00' # used to check that er no double records in the list 
            # limit range to dates that exceed the rentention period.
            # delete_limited_date = ( datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')
            try:

                list_of_sites   = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
                date_list       = datetime_delta_lib.create_date_list( start_date, end_date, period = 'y', range=1, repeatdate=True )
                flog.debug( inspect.stack()[0][3] + ": date_list=" + str( date_list) )
                for date_set in date_list:

                    # start_date = "2016-10-25" #DEBUG om range fouten te testen
                    flog.debug( inspect.stack()[0][3] + ": start date=" + str( date_set[0]) + " stop date=" + str( date_set[1]) )

                    data = api.get_energy( 
                        api_query_list_of_ids,
                        date_set[0], 
                        date_set[1], 
                        time_unit=solaredge_lib.API_DAY #DIFF
                        )
                    rt_status_db.timestamp( 111, flog )

                    for idx in range( data['sitesEnergy']['count'] ):
    
                        #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                        list_of_records.clear()

                        try:
                            site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                            db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                            flog.info( inspect.stack()[0][3] + ": gestart met dag data voor site ID " + str( site_id ) +\
                                 " met DB index " +  str( db_sql_index_number ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                            data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                            #print ( "data_set = ", data_set )

                            for i in range( len(data_set) ):

                                kWh_value = data_set[i]['value']

                                if kWh_value == None:
                                    continue # there is no valid data for this timestamp.
                            
                                rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                                rec[0] = data_set[i]['date'][:10]+" 00:00:00" # TIMESTAMP
                                
                                #flog.info( str(rec) )
                                
                                if rec[0] <= max_timestamp:                                   # Make sure there is no double value in the list
                                    flog.debug( inspect.stack()[0][3] + " skipped timestamp  " + str( rec[0] ) + " all ready processed.")
                                    continue
                                max_timestamp = rec[0] 

                                rec[1] = db_sql_index_number + 3                              # TIMEPERIOD_ID 
                                rec[2] = 1                                                    # POWER_SOURCE_ID set to Solar Edge ID, default to 0.

                                #tariff_index = 0
                                if tariff_index == 0:
                                    rec[3] = round(  (kWh_value  / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = 0                                 # PRODUCTION_KWH_LOW
                                else:
                                    # get the low and high tariff pct's
                                    high_tariff_pct, low_tariff_pct = power_tariff_lib.get_day_percentages( rec[0] )
                                    # multiply by percentage and convert Wh to kWh.
                                    rec[3] = round( ( (kWh_value * high_tariff_pct) / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = round( ( (kWh_value * low_tariff_pct ) / 1000 ), 3 ) # PRODUCTION_KWH_LOW

                                flog.debug( inspect.stack()[0][3] + " record added = : " + str( rec ) )

                                list_of_records.append ( rec.copy() )

                        except Exception as e:
                            rt_status_db.timestamp( 112, flog )
                            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor dag informatie " + str( site_id ) + " -> " + str(e.args[0]) )

                        ####################################################
                        # find previous total values from the SQL database #
                        ####################################################
                        tmp_total_high_offset = 0
                        tmp_total_low_offset  = 0
                        try:
                            start_date_from_api = str( list_of_records[0][0] ) # the oldest timestamp from the API
                            db_index_number_tmp = str( db_sql_index_number + 3 ) # DAY
                            
                            sql_timestamp = "select timestamp, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB +\
                                 " where power_source_id=1 and TIMEPERIOD_ID=" + db_index_number_tmp +\
                                 " and timestamp == ( select max(timestamp) from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB + \
                                 " where power_source_id=1 and TIMEPERIOD_ID=" +\
                                 db_index_number_tmp + " and timestamp < '" + start_date_from_api + "')"
                            
                            #flog.debug( inspect.stack()[0][3] + ": sql = " + sql_timestamp )
                            record = power_production_solar_db.select_rec( sql_timestamp )
                            tmp_total_high_offset = float(record[0][1])
                            tmp_total_low_offset  = float(record[0][2])
                            flog.debug( inspect.stack()[0][3] + ": tmp_total_high_offset = " + str(tmp_total_high_offset) +\
                                                                 " tmp_total_low_offset=" + str(tmp_total_low_offset) )
                        except Exception as e:
                            flog.info( inspect.stack()[0][3] + ": geen eerder record gevonden voor totaal waarden, 0 wordt gebruikt als waarde." )

                        ##############################################
                        # determine the totals for the found site ID #
                        # set the totals of high, low en both        #
                        ##############################################
                        solaredge_shared_lib.recalculate_totals( list_of_records,
                            total_high_offset=tmp_total_high_offset ,
                            total_low_offset=tmp_total_low_offset, 
                            flog=flog )

                        # delete records from list that are to old
                        delete_limited_date = ( datetime.datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')

                        clean_list = list()
                        for rec in list_of_records:
                            if rec[0][0:10] < delete_limited_date:
                                continue
                            else:
                                clean_list.append ( rec )

                        list_of_records.clear() # give memory back

                        # make a string of SQL statements
                        sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog )

                        #Bulk processing is about 40% faster then record for record.
                        try:
                            power_production_solar_db.executescript( sql_script )
                        except Exception as e:
                            flog.warning( inspect.stack()[0][3] + ": bulk update dag gefaald, record voor record worden verwerkt." + str(e.args[0]) )

                            idx = 0
                            while idx < len( clean_list ):
                                sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog , first_idx=idx, last_idx=idx )
                                power_production_solar_db.executescript( sql_script )
                                idx += 1

                toc = time.perf_counter()
                flog.info( inspect.stack()[0][3] + ": " + str( len(clean_list) ) + " dag records verwerkt in " + f"{toc - tic:0.3f} seconden." )
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor dag informatie " + str( site_id ) + " -> " + str(e.args[0]) )


            ######################################################
            # month processing                                   #
            ######################################################
            tic = time.perf_counter()
            list_of_records = list()
            max_timestamp   = '1970-01-01 00:00:00' # used to check that er no double records in the list 
           
            try:

                list_of_sites   = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )

                date_list = []
                date_set  = []
                date_set.append ( ( datetime.datetime.now() - relativedelta( months=1 )).strftime('%Y-%m-01') )
                date_set.append ( end_date[0:7]+"-01" )
                date_list.append( date_set )

                flog.debug( inspect.stack()[0][3] + ": date_list=" + str( date_list) )

                for date_set in date_list:

                    # start_date = "2016-10-25" #DEBUG om range fouten te testen
                    flog.debug( inspect.stack()[0][3] + ": start date=" + str( date_set[0]) + " stop date=" + str( date_set[1]) )

                    data = api.get_energy( 
                        api_query_list_of_ids,
                        date_set[0], 
                        date_set[1], 
                        time_unit=solaredge_lib.API_MONTH #DIFF
                        )
                    rt_status_db.timestamp( 111, flog )

                    for idx in range( data['sitesEnergy']['count'] ):
    
                        #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                        list_of_records.clear()

                        try:
                            site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                            db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                            flog.info( inspect.stack()[0][3] + ": gestart met maand data voor site ID " + str( site_id ) +\
                                 " met DB index " +  str( db_sql_index_number ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                            data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                            #print ( "data_set = ", data_set )

                            for i in range( len(data_set) ):

                                kWh_value = data_set[i]['value']

                                if kWh_value == None:
                                    continue # there is no valid data for this timestamp.
                            
                                rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                                rec[0] = data_set[i]['date'][:7]+"-01 00:00:00" # TIMESTAMP
                                
                                #flog.info( str(rec) )
                                
                                if rec[0] <= max_timestamp:                                   # Make sure there is no double value in the list
                                    flog.debug( inspect.stack()[0][3] + " skipped timestamp  " + str( rec[0] ) + " all ready processed.")
                                    continue
                                max_timestamp = rec[0] 

                                rec[1] = db_sql_index_number + 4                              # TIMEPERIOD_ID 
                                rec[2] = 1                                                    # POWER_SOURCE_ID set to Solar Edge ID, default to 0.

                                if tariff_index == 0:
                                    rec[3] = round(  ( kWh_value  / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = 0                                 # PRODUCTION_KWH_LOW
                                else:
                                    # get the low and high tariff pct's
                                    high_tariff_pct, low_tariff_pct = power_tariff_lib.get_month_percentages( rec[0] )
                                    # multiply by percentage and convert Wh to kWh.
                                    rec[3] = round( ( (kWh_value * high_tariff_pct) / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = round( ( (kWh_value * low_tariff_pct ) / 1000 ), 3 ) # PRODUCTION_KWH_LOW

                                flog.debug( inspect.stack()[0][3] + " record added = : " + str( rec ) )

                                list_of_records.append ( rec.copy() )

                        except Exception as e:
                            rt_status_db.timestamp( 112, flog )
                            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor maand informatie " + str( site_id ) + " -> " + str(e.args[0]) )

                        ####################################################
                        # find previous total values from the SQL database #
                        ####################################################
                        tmp_total_high_offset = 0
                        tmp_total_low_offset  = 0
                        try:
                            start_date_from_api = str( list_of_records[0][0]   ) # the oldest timestamp from the API
                            db_index_number_tmp = str( db_sql_index_number + 4 ) # MONTH
                            
                            sql_timestamp = "select timestamp, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB +\
                                 " where power_source_id=1 and TIMEPERIOD_ID=" + db_index_number_tmp +\
                                 " and timestamp == ( select max(timestamp) from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB + \
                                 " where power_source_id=1 and TIMEPERIOD_ID=" +\
                                 db_index_number_tmp + " and timestamp < '" + start_date_from_api + "')"
                            
                            #flog.debug( inspect.stack()[0][3] + ": sql = " + sql_timestamp )
                            record = power_production_solar_db.select_rec( sql_timestamp )
                            tmp_total_high_offset = float(record[0][1])
                            tmp_total_low_offset  = float(record[0][2])
                            flog.debug( inspect.stack()[0][3] + ": tmp_total_high_offset = " + str(tmp_total_high_offset) +\
                                                                 " tmp_total_low_offset=" + str(tmp_total_low_offset) )
                        except Exception as e:
                            flog.info( inspect.stack()[0][3] + ": geen eerder record gevonden voor totaal waarden, 0 wordt gebruikt als waarde." )

                        ##############################################
                        # determine the totals for the found site ID #
                        # set the totals of high, low en both        #
                        ##############################################
                        solaredge_shared_lib.recalculate_totals( list_of_records,
                            total_high_offset=tmp_total_high_offset ,
                            total_low_offset=tmp_total_low_offset, 
                            flog=flog )

                        # make a string of SQL statements
                        sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog) 

                        #Bulk processing is about 40% faster then record for record.
                        try:
                            power_production_solar_db.executescript( sql_script )
                        except Exception as e:
                            flog.warning( inspect.stack()[0][3] + ": bulk update maand gefaald, record voor record worden verwerkt." + str(e.args[0]) )

                            idx = 0
                            while idx < len( clean_list ):
                                sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog , first_idx=idx, last_idx=idx )
                                power_production_solar_db.executescript( sql_script )
                                idx += 1

                toc = time.perf_counter()
                flog.info( inspect.stack()[0][3] + ": " + str( len( list_of_records ) ) + " maand records verwerkt in " + f"{toc - tic:0.3f} seconden." )
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor maand informatie " + str( site_id ) + " -> " + str(e.args[0]) )


            
            ######################################################
            # year processing                                    #
            ######################################################
            tic = time.perf_counter()
            list_of_records = list()
            max_timestamp   = '1970-01-01 00:00:00' # used to check that er no double records in the list 
           
            try:

                list_of_sites   = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )

                date_list = []
                date_set  = []
                date_set.append ( ( datetime.datetime.now() - relativedelta( years=1 )).strftime('%Y-01-01') )
                date_set.append ( end_date[0:4]+"-01-01" )
                date_list.append( date_set )

                flog.debug( inspect.stack()[0][3] + ": date_list=" + str( date_list) )

                for date_set in date_list:

                    # start_date = "2016-10-25" #DEBUG om range fouten te testen
                    flog.debug( inspect.stack()[0][3] + ": start date=" + str( date_set[0]) + " stop date=" + str( date_set[1]) )

                    data = api.get_energy( 
                        api_query_list_of_ids,
                        date_set[0], 
                        date_set[1], 
                        time_unit=solaredge_lib.API_YEAR #DIFF
                        )
                    rt_status_db.timestamp( 111, flog )

                    for idx in range( data['sitesEnergy']['count'] ):
    
                        #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                        list_of_records.clear()

                        try:
                            site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                            db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                            flog.info( inspect.stack()[0][3] + ": gestart met jaar data voor site ID " + str( site_id ) +\
                                 " met DB index " +  str( db_sql_index_number ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                            data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                            #print ( "data_set = ", data_set )

                            for i in range( len(data_set) ):

                                kWh_value = data_set[i]['value']

                                if kWh_value == None:
                                    continue # there is no valid data for this timestamp.
                            
                                rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                                rec[0] = data_set[i]['date'][:4]+"-01-01 00:00:00" # TIMESTAMP
                                
                                #flog.info( str(rec) )
                                
                                if rec[0] <= max_timestamp:                                   # Make sure there is no double value in the list
                                    flog.debug( inspect.stack()[0][3] + " skipped timestamp  " + str( rec[0] ) + " all ready processed.")
                                    continue
                                max_timestamp = rec[0] 

                                rec[1] = db_sql_index_number + 5                              # TIMEPERIOD_ID 
                                rec[2] = 1                                                    # POWER_SOURCE_ID set to Solar Edge ID, default to 0.

                                if tariff_index == 0:
                                    rec[3] = round(  ( kWh_value  / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = 0                                 # PRODUCTION_KWH_LOW
                                else: 
                                    # get the low and high tariff pct's
                                    high_tariff_pct, low_tariff_pct = power_tariff_lib.get_year_percentages( rec[0] )
                                    # multiply by percentage and convert Wh to kWh.
                                    rec[3] = round( ( (kWh_value * high_tariff_pct) / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
                                    rec[4] = round( ( (kWh_value * low_tariff_pct ) / 1000 ), 3 ) # PRODUCTION_KWH_LOW

                                flog.debug( inspect.stack()[0][3] + " record added = : " + str( rec ) )

                                list_of_records.append ( rec.copy() )

                        except Exception as e:
                            rt_status_db.timestamp( 112, flog )
                            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor jaar informatie " + str( site_id ) + " -> " + str(e.args[0]) )

                        ####################################################
                        # find previous total values from the SQL database #
                        ####################################################
                        tmp_total_high_offset = 0
                        tmp_total_low_offset  = 0
                        try:
                            start_date_from_api = str( list_of_records[0][0]   ) # the oldest timestamp from the API
                            db_index_number_tmp = str( db_sql_index_number + 5 ) # YEAR
                            
                            sql_timestamp = "select timestamp, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB +\
                                 " where power_source_id=1 and TIMEPERIOD_ID=" + db_index_number_tmp +\
                                 " and timestamp == ( select max(timestamp) from " +\
                                 const.DB_POWERPRODUCTION_SOLAR_TAB + \
                                 " where power_source_id=1 and TIMEPERIOD_ID=" +\
                                 db_index_number_tmp + " and timestamp < '" + start_date_from_api + "')"
                            
                            #flog.debug( inspect.stack()[0][3] + ": sql = " + sql_timestamp )
                            record = power_production_solar_db.select_rec( sql_timestamp )
                            tmp_total_high_offset = float(record[0][1])
                            tmp_total_low_offset  = float(record[0][2])
                            flog.debug( inspect.stack()[0][3] + ": tmp_total_high_offset = " + str(tmp_total_high_offset) +\
                                                                 " tmp_total_low_offset=" + str(tmp_total_low_offset) )
                        except Exception as e:
                            flog.info( inspect.stack()[0][3] + ": geen eerder record gevonden voor totaal waarden, 0 wordt gebruikt als waarde." )

                        ##############################################
                        # determine the totals for the found site ID #
                        # set the totals of high, low en both        #
                        ##############################################
                        solaredge_shared_lib.recalculate_totals( list_of_records,
                            total_high_offset=tmp_total_high_offset ,
                            total_low_offset=tmp_total_low_offset, 
                            flog=flog )

                        # make a string of SQL statements
                        sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog )

                        #Bulk processing is about 40% faster then record for record.
                        try:
                            power_production_solar_db.executescript( sql_script )
                        except Exception as e:
                            flog.warning( inspect.stack()[0][3] + ": bulk update jaar gefaald, record voor record worden verwerkt." + str(e.args[0]) )

                            idx = 0
                            while idx < len( clean_list ):
                                sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog , first_idx=idx, last_idx=idx )
                                power_production_solar_db.executescript( sql_script )
                                idx += 1

                toc = time.perf_counter()
                flog.info( inspect.stack()[0][3] + ": " + str( len( list_of_records ) ) + " jaar records verwerkt in " + f"{toc - tic:0.3f} seconden." )
            except Exception as e:
                flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor jaar informatie " + str( site_id ) + " -> " + str(e.args[0]) )
           
            # delete min, hour, day records passed the retention time.
            flog.info( inspect.stack()[0][3] + ": verouderde data wordt verwijderd." )
            list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
            solaredge_shared_lib.clean_db_by_retention(db=power_production_solar_db, flog=flog, site_list=list_of_sites )

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
# get the smalest timestamp from the metadata set to yesterday            #
# if there is no metadata                                                 #
###########################################################################
def get_smalest_timestamp( meta_data ):

    yesterday = ( datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    for item in meta_data:
        if item['START_DATE'] < yesterday:
            timestamp = item['START_DATE']
    return yesterday


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
                api = None
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
    signal.signal( signal.SIGINT, original_sigint )
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
    signal.signal( signal.SIGINT, saveExit )
    Main(sys.argv[1:])