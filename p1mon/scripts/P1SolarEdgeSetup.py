# run manual with ./P1SolarEdgeSetup

import argparse
import const
import data_struct_lib
import datetime_delta_lib
import datetime
import json_lib
import inspect
import makeLocalTimeString
import logger
import os
import pwd
import power_tariff_lib
import solaredge_lib
import solaredge_shared_lib
import sqldb
import signal
import sys
import time

# programme name.
prgname = 'P1SolarEdgeSetup'

config_db                   = sqldb.configDB()
rt_status_db                = sqldb.rtStatusDb()
power_production_solar_db   = sqldb.powerProductionSolarDB()

def Main( argv ): 

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')
    parser.add_argument( '-ss',  '--savesites', 
        required=False, action="store_true" ,
        help = "lees en bewaar alle site ID's van API key." )
    parser.add_argument( '-rs',  '--removesites', 
        required=False, 
        action="store_true",
        help = " wis alle site IDs van de API key" )
    parser.add_argument( '-ds',   '--datessites', 
        required=False, action="store_true",
        help="lees de start en eind datum in van alle 'sites, heeft een configuratie nodig (zie savesites)." )
    parser.add_argument( '-rl',  '--reloadsites',
        required=False, 
        action="store_true",
        help="lees alle SolarEdge kWh waarden in en overschrijf de database." )
    parser.add_argument( '-ddb',  '--deletedb',
        required=False,
        action="store_true",
        help="Wis alle energie data van de sites die als gewist zijn gemarkeerd." )
    parser.add_argument( '-g',  '--genesis',
        required=False,
        action="store_true",
        help="Wis alle data en configuratie (fabrieks instelling)." )

    args = parser.parse_args()

    ###################################
    # init stuff                      #
    ###################################

    ####################################
    # open van config status database  #
    ####################################
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    try:    
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(2)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    ########################################################
    # reset all the setting to factory settings and delete #
    # all the data                                         #
    ########################################################
    if args.genesis == True:

        try: # clear the configuration
            config_db.strset( "" , 140, flog )
            flog.info( inspect.stack()[0][3] + ": configuratie van sites gewist." )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": configuratie van sites kan niet worden gewist -> " + str(e.args[0]) )
        
        try: # reset all the option to factory set
            config_db.strset( ""  , 139, flog ) # API key delete.
            config_db.strset( "0" , 141, flog ) # processing is not active.
            config_db.strset( "0" , 142, flog ) # reload data off.
            config_db.strset( "1" , 143, flog ) # tariff mode.
            config_db.strset( "0" , 144, flog ) # don't get site info.
            config_db.strset( "0" , 145, flog ) # solar reset info.
            config_db.strset( "1" , 146, flog ) # smart update mode.
            flog.info( inspect.stack()[0][3] + ": fabrieks instellingen herstelt." )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": configuratie van sites kan niet worden gewist -> " + str(e.args[0]) )

        # open van power production database for the solar data
        try:
            power_production_solar_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_SOLAR_TAB, flog )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": Database niet te openen." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
            sys.exit(1)
        flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_POWERPRODUCTION_SOLAR_TAB + " succesvol geopend." )

        solaredge_shared_lib.delete_all_record(db=power_production_solar_db, table=const.DB_POWERPRODUCTION_SOLAR_TAB, flog=flog )

        flog.info( inspect.stack()[0][3] + ": Wissen van database en configuratie afgerond." ) 

        sys.exit( 0 )


    #######################################################
    # delete the records from the sqlite database when    #
    # marked voor deleting                                #
    #######################################################
    if args.deletedb == True:
     
        # get rid of inactive sites and such.
        solaredge_shared_lib.clean_config_db( config_db=config_db, flog=flog ) 

        list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )

        # open van power production database for the solar data
        try:
            power_production_solar_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_SOLAR_TAB, flog )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": Database niet te openen." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
            sys.exit(1)
        flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_POWERPRODUCTION_SOLAR_TAB + " succesvol geopend." )

        for item in list_of_sites:
            try:
                if item['DB_DELETE']: 
                    timeperiod_id = int( item['DB_INDEX'] )
                    sql_del = "delete from " + const.DB_POWERPRODUCTION_SOLAR_TAB +\
                         " where power_source_id=1 and TIMEPERIOD_ID between " + str( timeperiod_id) + " and " + str( timeperiod_id + 5)
                    power_production_solar_db.excute( sql_del )
                    flog.info( inspect.stack()[0][3] + ": Database delete uitgevoerd voor site id " + str( item['ID'] ) + " en DB index " + str(item['DB_INDEX']) )
            except Exception as e:
                flog.error( inspect.stack()[0][3] + ": Database delete gefaald voor site id " + str( item['ID'] ) )
        

        solaredge_shared_lib.database_clean_up( db=power_production_solar_db, flog=flog, db_config=config_db )

        flog.info( inspect.stack()[0][3] + ": Wissen van energie data van de sites die als gewist zijn gemarkeerd gereed." ) 

        sys.exit( 0 )

    #########################################
    # get solaredge API key from config DB  #
    #########################################
    try:
        solaredge_apikey = solaredge_shared_lib .read_api_key( config_db )
        solar_edge = solaredge_lib.Solaredge( solaredge_apikey, debug=False ) # debug is for the solaredge lib only.
        rt_status_db.timestamp( 111, flog )
        flog.debug( inspect.stack()[0][3] + ": solaredge_apikey=" + solaredge_apikey )
    except Exception as e:
        rt_status_db.timestamp( 112, flog )
        flog.critical( inspect.stack()[0][3] + ": API key fout. melding: " + str(e.args[0]) )
        sys.exit(1)

    #######################################################
    # try to reload all the data from sites from the      #
    # config set. do this for multipele sites             #
    #######################################################
    if args.reloadsites == True:
        
        flog.info( inspect.stack()[0][3]+" optie reload sites gestart" )

        # get rid of inactive sites and such.
        solaredge_shared_lib.clean_config_db( config_db=config_db, flog=flog ) 

        """"
        print ( "weekend 2021-04-18 09:00:00=",power_tariff_lib.get_hour_percentages('2021-04-18 09:00:00', tariff_set=1 ) )
        print ( "week 2021-04-19 09:00:00="   ,power_tariff_lib.get_hour_percentages('2021-04-19 09:00:00', tariff_set=1 ) )
        print ( "week 2021-04-19 07:00:00="   ,power_tariff_lib.get_hour_percentages('2021-04-19 07:00:00', tariff_set=1 ) )
        print ( "week 2021-04-19 06:00:00="   ,power_tariff_lib.get_hour_percentages('2021-04-19 06:00:00', tariff_set=1 ) )
        print ( "week 2021-04-19 06:00:00="   ,power_tariff_lib.get_hour_percentages('2021-04-19 06:00:00', tariff_set=1 ) )
        print ( "week 2021-04-19 21:00:00="   ,power_tariff_lib.get_hour_percentages('2021-04-19 21:00:00', tariff_set=1 ) )
        print ( "week 2021-04-19 21:00:00="   ,power_tariff_lib.get_hour_percentages('2021-04-19 21:00:00', tariff_set=2 ) )
        print ( "week 2021-04-19 23:00:00="   ,power_tariff_lib.get_hour_percentages('2021-04-19 23:00:00', tariff_set=2 ) )
        sys.exit()
        """
        # open van power production database for the solar data
        try:
            power_production_solar_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_SOLAR_TAB, flog )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": Database niet te openen." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
            sys.exit(1)
        flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_POWERPRODUCTION_SOLAR_TAB + " succesvol geopend." )

        tariff_index = int(1)
        try:
            id, tariff_type, _label = config_db.strget( 143, flog ) 
            tariff_index = int(tariff_type)
            flog.debug(inspect.stack()[0][3]+": hoog/laag berekend tarief is " + str( tariff_index ) )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ":  hoog/laag berekend tarief kon niet worden gelezen, tarief hoog wordt gebruikt -> " + str(e.args[0]) ) 

        # refresh the dates
        list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
        list_of_sites = solaredge_shared_lib.arg_dates_function( solar_edge, flog=flog, list_of_sites=list_of_sites, status_db=rt_status_db )
        solaredge_shared_lib.save_list_of_sites_to_config_db( config_db, list_of_sites, flog ) 

        end_date   = makeLocalTimeString.makeLocalTimeString( mode='short' ) # use current time for the end date in the API call.
        start_date = makeLocalTimeString.makeLocalTimeString( mode='short' )

        # cleaned set of valid site id's to use in the API call, set used to make sure id's are unique.
        api_query_set_of_ids = set()

        for item in list_of_sites:
            try:
               
                try:
                    # check if active else skip
                    if item['SITE_ACTIVE'] == False:
                        flog.info( inspect.stack()[0][3] + ": site ID " + str( item['ID'] ) + " wordt niet verwerkt, site is niet actief." )
                        continue

                    if len(item['START_DATE']) != 10: #not a valid date length, probably not set. So skip. 
                         flog.info( inspect.stack()[0][3] + ": site ID " + str( item['ID'] ) + " wordt verwerkt niet , datum niet correct." )
                         continue

                    # determine start date  (smalest date) and list of ID's to feth from API.
                    # end date will allways be the current date 
                    if item['START_DATE'] < start_date: 
                        start_date = item['START_DATE']

                    api_query_set_of_ids.add( item['ID'] )
                    
                except Exception as e:
                    flog.warning( inspect.stack()[0][3] + ": probleem met herladen van site ID " + str( item['ID'] ) + " -> " + str(e.args[0]) )
            except Exception as e:
                flog.error( inspect.stack()[0][3] + ": herladen van sites mislukt gestopt -> " + str(e.args[0]) )
                sys.exit( 1 )

        # make list from a set to sort
        api_query_list_of_ids = list( api_query_set_of_ids )
        api_query_list_of_ids.sort()

        # check if we any site(s) id's else stop.
        if len(api_query_set_of_ids) == 0:
            flog.warning( inspect.stack()[0][3] + ": gestopt er zijn geen site(s) geconfigureerd." ) 
            sys.exit(1)

        #print( "api_query_set_of_ids" ,api_query_set_of_ids )
        

        ############################################################
        # start API calls                                          #
        ############################################################

        ############################################################
        # request to the API are done for al site id's in the list #
        # when dates exceed the maximum date range then multiple   #
        # API calls must be made.                                  #
        # the largest time frame for the sites is used to make     #
        # sure al data is recieved                                 #
        # the SolarEdge API has the following max date ranges      #
        # QUARTER_OF_AN_HOUR or HOUR is one month.                 #
        # DAY MONTH, YEAR is one year.                             #
        # P1 Monitor retention is:                                 #
        # - MIN (QUARTER_OF_AN_HOUR) 31 days                       #
        # - HOUR, DAY 1096 DAYS(3 year )                           #
        # - MONTH, YEAR UNLIMTED                                   #
        ############################################################


        flog.info( inspect.stack()[0][3] + ": herladen van site ID's " + str( api_query_list_of_ids ) +\
        " gestart voor periode van " + start_date + " tot " + end_date )

        #power_production_solar_db.excute('delete from powerproduction_solar') #TODO DEBUG

        ##########################################################################
        # YEAR processing, no date changes                                       #
        # there is no maximum period limit in the year range.                    #
        ##########################################################################
        tic = time.perf_counter()
        list_of_records = list()
        # start_date = "2016-10-25" #DEBUG om range fouten te testen
        try:
            
            data = solar_edge.get_energy( 
                api_query_list_of_ids,
                start_date, 
                end_date, 
                time_unit=solaredge_lib.API_YEAR  # DIFF
                )
            rt_status_db.timestamp( 111, flog )
            
            for idx in range( data['sitesEnergy']['count'] ):

                #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                list_of_records.clear() 

                try:
                    site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                    flog.info( inspect.stack()[0][3] + ": gestart met jaar data voor site ID " + str( site_id  ) )
                    db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                    data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                    #print ( "data_set = ", data_set )

                    for i in range( len(data_set) ):

                        kWh_value = data_set[i]['value']

                        if kWh_value == None:
                            continue # there is no valid data for this timestamp.
                    
                        rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                        rec[0] = data_set[i]['date'][:4]+"-01-01 00:00:00" # TIMESTAMP
                            
                        #flog.info( str(rec) )

                        rec[1] = db_sql_index_number + 5                              # TIMEPERIOD_ID
                        rec[2] = 1                                                    # POWER_SOURCE_ID set to Solar Edge ID, default to 0.

                        #tariff_index = 1
                        if tariff_index == 0:
                            rec[3] = round(  (kWh_value  / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
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
                    flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor jaar informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

                # set the totals of high, low en both
                solaredge_shared_lib.recalculate_totals( list_of_records )

                # make a string of SQL statements
                sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog )

                # power_production_solar_db.excute('delete from powerproduction_solar')
                #####################

                # Bulk processing is about 40% faster then record for record
                try:
                    power_production_solar_db.executescript( sql_script )
                except Exception as e:
                    flog.warning( inspect.stack()[0][3] + ": bulk update jaar gefaald, record voor record worden verwerkt." + str(e.args[0]) )
                    idx = 0

                    while idx < len( list_of_records ):
                        sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog , first_idx=idx, last_idx=idx )
                        power_production_solar_db.executescript( sql_script )
                        idx += 1

            toc = time.perf_counter()
            flog.info( inspect.stack()[0][3] + ": " + str( len(list_of_records) ) + " jaar records verwerkt in " + f"{toc - tic:0.3f} seconden." )

        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor jaar informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )


        ##########################################################################
        # MONTH processing, no date changes                                      #
        # there is no maximum period limit in the MONTH range.                   #
        ##########################################################################
        tic = time.perf_counter()
        list_of_records = list()
        # start_date = "2016-10-25" #DEBUG om range fouten te testen
        try:
            
            data = solar_edge.get_energy( 
                api_query_list_of_ids,
                start_date, 
                end_date, 
                time_unit=solaredge_lib.API_MONTH  #DIFF
                )
            rt_status_db.timestamp( 111, flog )
            
            for idx in range( data['sitesEnergy']['count'] ):

                #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                list_of_records.clear()

                try:
                    site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                    flog.info( inspect.stack()[0][3] + ": gestart met maand data voor site ID " + str( site_id  ) )
                    db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                    data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                    #print ( "data_set = ", data_set )

                    for i in range( len(data_set) ):

                        kWh_value = data_set[i]['value']

                        if kWh_value == None:
                            continue # there is no valid data for this timestamp.
                    
                        rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                        rec[0] = data_set[i]['date'][:7]+"-01 00:00:00" # TIMESTAMP
                            
                        #flog.info( str(rec) )

                        rec[1] = db_sql_index_number + 4                              # TIMEPERIOD_ID
                        rec[2] = 1                                                    # POWER_SOURCE_ID set to Solar Edge ID, default to 0.

                        #tariff_index = 2
                        if tariff_index == 0:
                            rec[3] = round(  (kWh_value  / 1000 ), 3 ) # PRODUCTION_KWH_HIGH
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
                    flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor maand informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

                # set the totals of high, low en both
                solaredge_shared_lib.recalculate_totals( list_of_records )

                # make a string of SQL statements
                sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog )

                # power_production_solar_db.excute('delete from powerproduction_solar')
                #####################

                # Bulk processing is about 40% faster then record for record
                try:
                    power_production_solar_db.executescript( sql_script )
                except Exception as e:
                    flog.warning( inspect.stack()[0][3] + ": bulk update maand gefaald, record voor record worden verwerkt." + str(e.args[0]) )
                
                    idx = 0
                    while idx < len( list_of_records ):
                        sql_script = solaredge_shared_lib.generate_sql_text ( list_of_records, flog , first_idx=idx, last_idx=idx )
                        power_production_solar_db.executescript( sql_script )
                        idx += 1

            toc = time.perf_counter()
            flog.info( inspect.stack()[0][3] + ": " + str( len(list_of_records) ) + " maand records verwerkt in " + f"{toc - tic:0.3f} seconden." )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor maand informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

        #sys.exit()

        ##########################################################################
        # DAY processing, date changes needed                                    #
        # there is a maximum period limit in the day for one YEAR                #
        ##########################################################################

        tic = time.perf_counter()
        list_of_records = list()
        max_timestamp = '1970-01-01 00:00:00' # used to check that er no double records in the list 
        # limit range to dates that exceed the rentention period.
        # delete_limited_date = ( datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')
        try:
            date_list = datetime_delta_lib.create_date_list( start_date, end_date, period = 'y', range=1, repeatdate=True )

            for date_set in date_list:
                #print("####################", date_set[0], date_set[1] )
                #continue

                # start_date = "2016-10-25" #DEBUG om range fouten te testen
            
                data = solar_edge.get_energy( 
                    api_query_list_of_ids,
                    date_set[0], 
                    date_set[1], 
                    time_unit=solaredge_lib.API_DAY  #DIFF
                    )
                rt_status_db.timestamp( 111, flog )

                for idx in range( data['sitesEnergy']['count'] ):
 
                    #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                    list_of_records.clear()

                    try:
                        site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                        flog.info( inspect.stack()[0][3] + ": gestart met dag data voor site ID " + str( site_id ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                        db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
                        data_set = data['sitesEnergy']['siteEnergyList'][idx ]['energyValues']['values']
                        #print ( "data_set = ", data_set )

                        for i in range( len(data_set) ):

                            kWh_value = data_set[i]['value']

                            if kWh_value == None:
                                continue # there is no valid data for this timestamp.
                        
                            rec = solaredge_shared_lib.POWER_PRODUCTION_SOLAR_INDEX_REC

                            #rec[0] = data_set[i]['date']                                  # TIMESTAMP
                            
                            rec[0] = data_set[i]['date'][:10]+" 00:00:00" # TIMESTAMP
                            
                            #flog.info( str(rec) )

                            if rec[0] <= max_timestamp:                                   # Make sure there is no double value in the list
                                flog.debug( inspect.stack()[0][3] + " skipped timestamp  " + str( rec[0] ) + " all ready processed.")
                                continue
                            max_timestamp = rec[0] 

                            rec[1] = db_sql_index_number + 3                              # TIMEPERIOD_ID
                            rec[2] = 1                                                    # POWER_SOURCE_ID set to Solar Edge ID, default to 0.

                            #tariff_index = 1
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
                        flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor dag informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

                    # set the totals of high, low and both
                    solaredge_shared_lib.recalculate_totals( list_of_records )

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

                    # power_production_solar_db.excute('delete from powerproduction_solar')
                    #####################

                    #Bulk processing is about 40% faster then record for record.
                    try:
                        power_production_solar_db.executescript( sql_script )
                    
                    except Exception as e:
                        flog.warning( inspect.stack()[0][3] + ": bulk update maand gefaald, record voor record worden verwerkt." + str(e.args[0]) )

                        idx = 0 # do fail save
                        while idx < len( clean_list ):
                            sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog , first_idx=idx, last_idx=idx )
                            power_production_solar_db.executescript( sql_script )
                            idx += 1

            toc = time.perf_counter()
            flog.info( inspect.stack()[0][3] + ": " + str( len(clean_list) ) + " dag records verwerkt in " + f"{toc - tic:0.3f} seconden." )

        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor dag informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

       

        ##########################################################################
        # HOUR processing, date changes needed                                   #
        # there is a maximum period limit in the HOUR range of one month         #
        ##########################################################################

        tic = time.perf_counter()
        list_of_records = list()
        max_timestamp = '1970-01-01 00:00:00' # used to check that er no double records in the list 
        # limit range to dates that exceed the rentention period.
        # delete_limited_date = ( datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')
        try:
            date_list = datetime_delta_lib.create_date_list( start_date, end_date, period = 'm', range=1, repeatdate=True )

            for date_set in date_list:
                #print("####################", date_set[0], date_set[1] )
                #continue

                # start_date = "2016-10-25" #DEBUG om range fouten te testen
            
                data = solar_edge.get_energy( 
                    api_query_list_of_ids,
                    date_set[0], 
                    date_set[1], 
                    time_unit=solaredge_lib.API_HOUR  #DIFF
                    )
                rt_status_db.timestamp( 111, flog )



                for idx in range( data['sitesEnergy']['count'] ):
 
                    #print ( "siteId[x] = ",  data['sitesEnergy']['siteEnergyList'][idx]['siteId'])
                    list_of_records.clear()
                    try:
                        site_id = data['sitesEnergy']['siteEnergyList'][idx]['siteId']
                        flog.info( inspect.stack()[0][3] + ": gestart met uur data voor site ID " + str( site_id ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                        db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
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
                        flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor uur informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

                    # set the totals of high, low en both
                    solaredge_shared_lib.recalculate_totals( list_of_records )

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

                    #power_production_solar_db.excute('delete from powerproduction_solar')
                    #####################

                    #Bulk processing is about 40% faster then record for record.
                    try:
                        power_production_solar_db.executescript( sql_script )
                    except Exception as e:
                        flog.warning( inspect.stack()[0][3] + ": bulk update uur gefaald, record voor record worden verwerkt." + str(e.args[0]) )
                        idx = 0 #do failsave
                        while idx < len( clean_list ):
                            sql_script = solaredge_shared_lib.generate_sql_text ( clean_list, flog , first_idx=idx, last_idx=idx )
                            power_production_solar_db.executescript( sql_script )
                            idx += 1

            toc = time.perf_counter()
            flog.info( inspect.stack()[0][3] + ": " + str( len(clean_list) ) + " uur records verwerkt in " + f"{toc - tic:0.3f} seconden." )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor uur informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )


        ##########################################################################
        # MINUTE processing, date range changes needed                           #
        # there is a maximum period limit in the HOUR range of one month         #
        ##########################################################################

        tic = time.perf_counter()
        list_of_records = list()
        max_timestamp = '1970-01-01 00:00:00' # used to check that er no double records in the list 
        # limit range to dates that exceed the rentention period.
        # delete_limited_date = ( datetime.strptime(end_date,"%Y-%m-%d") - datetime.timedelta(days=1096) ).strftime('%Y-%m-%d')
        try:

            date_list = datetime_delta_lib.create_date_list( start_date, end_date, period = 'm', range=1, repeatdate=True )

            for date_set in date_list:
                #print("####################", date_set[0], date_set[1] )
                #continue

                # start_date = "2016-10-25" #DEBUG om range fouten te testen
            
                data = solar_edge.get_energy( 
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
                        flog.info( inspect.stack()[0][3] + ": gestart met minuut data voor site ID " + str( site_id ) + " voor periode " +  str(date_set[0]) + " - "  + str(date_set[1]))
                        db_sql_index_number = solaredge_shared_lib.read_db_index_from_list( site_id, list_of_sites )
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
                        flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor minuut informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

                    # set the totals of high, low en both
                    solaredge_shared_lib.recalculate_totals( list_of_records )

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
            flog.warning( inspect.stack()[0][3] + ": probleem met herladen data voor minuten informatie " + str( item['ID'] ) + " -> " + str(e.args[0]) )

        # end of reloadsites function.
        sys.exit( 0 )

    #####################################################
    # get the number of sites belonging by the API key  #
    # add the content to a JSON dict and save the       #
    # result to the config database.                    #
    #####################################################
    if args.savesites == True:

        flog.info( inspect.stack()[0][3] + ": sitelist aanvraag gestart.")

        # get rid of inactive sites and such.
        solaredge_shared_lib.clean_config_db( config_db=config_db, flog=flog ) 

        list_of_sites = list()
        list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
       
        try:
            data = solar_edge.get_site_list()
            flog.debug( inspect.stack()[0][3] + ": data van de API =" + str( data ))
            rt_status_db.timestamp( 111, flog )
            json_id_list = json_lib.json_extract( data, 'id' ) # find al site id's (could be more then 1).
            json_id_list.sort()

        except Exception as e:
            rt_status_db.timestamp( 112, flog )
            flog.critical( inspect.stack()[0][3] + ": JSON probleem tijdens het lezen " + str(e.args[0]) )
            sys.exit(1)

        if json_id_list == []:
            flog.warning( inspect.stack()[0][3] + ": API key heeft geen sites, gestopt." )
            sys.exit(1)
        flog.debug(inspect.stack()[0][3]+": gevonden sites id's " + str( json_id_list ) )

        #debug
        #json_id_list.append( 1 ) #TODO remove for prod.
        #json_id_list.append( 100 ) #TODO
        """
        json_id_list.append( 1 )
        json_id_list.append( 100 )
        json_id_list.append( 3 )
        json_id_list.append( 200 )
        json_id_list.append( 33333 )
        json_id_list.append( 4 )
        json_id_list.append( 41 )
        json_id_list.append( 42 )
        """

        # check if there is an entry with the site ID in the list of sites
        # if not add the entry.

        #print( "## json_id_list=" + str(json_id_list) )

        for id in json_id_list:

            if solaredge_shared_lib.find_id_in_list( id, list_of_sites ) == False:
                #print( "#id add=" + str(id) )
                # site does not exist
                se_data = data_struct_lib.solaredge_site_config
                se_data_copy = se_data.copy() # make copy of the object
                se_data_copy['ID'] = id
                se_data_copy['SITE_ACTIVE'] = True
                #se_data_copy ['P1MON_DB_INDEX_BASE'] = 30 #TEST
                list_of_sites.append( se_data_copy  )
                
                flog.info(inspect.stack()[0][3]+": site id toegevoegd -> " + str(id) )

                # sort the list by ID nummber
                list_of_sites = sorted( list_of_sites, key = lambda item: item['ID'] )
            else:
                flog.debug(inspect.stack()[0][3]+": site id " + str(id) + " niet toegevoegd omdat deze al bestaat.")

        #json_id_list.remove( id )


        # check if the entries in de site list have a SQL DB index number
        # the Solar Edge SQL DB index range is 20 - 90 with an increment of 10 
        # make a buffer of available numbers.
        sql_index_numbers_buffer = solaredge_shared_lib.SQL_INDEX_NUMBERS

        # remove numbers from buffer when already used.
        for item in list_of_sites:
            try:
                sql_index_numbers_buffer.remove( item['DB_INDEX'] ) # removes from predefined list
            except:
                pass

        # add first free sql index number to list of Solar Edge site ID's
        for item in list_of_sites:
            if item['DB_INDEX'] == 0:
                try:
                    item['DB_INDEX'] = sql_index_numbers_buffer[0]
                    del sql_index_numbers_buffer[0]
                except:
                    flog.warning( inspect.stack()[0][3] + ": toevoegen van SQL index gefaald voor Solar Edge site ID " + str(se_data_copy['ID']) )

        #print ( sql_index_numbers_buffer )
        #print ( list_of_sites )

        solaredge_shared_lib.save_list_of_sites_to_config_db( config_db, list_of_sites, flog ) 
        # also set the dates with a call to the API
        list_of_sites = solaredge_shared_lib.arg_dates_function( solar_edge, flog=flog, list_of_sites=list_of_sites, status_db=rt_status_db )
        solaredge_shared_lib.save_list_of_sites_to_config_db( config_db, list_of_sites, flog ) 

        #flog.info( inspect.stack()[0][3] + ": volgende site id's zijn gevonden: "  + str( json_id_list ) )

        # end of sitelist function
        sys.exit( 0 )

    ################################################
    # delete the config                            #
    # add the content to a JSON dict and save the  #
    # result to the config database.               #
    ################################################
    if args.removesites == True:
        try:
            config_db.strset( "" , 140, flog )
        except Exception as e:
            flog.critical( inspect.stack()[0][3] + ": configuratie van sites kan niet worden gewist -> " + str(e.args[0]) )
            sys.exit( 1)

        flog.info (inspect.stack()[0][3]+": configuratie van sites gewist." )
        sys.exit( 0 ) 

    ##################################################
    # add start and end dates to the found site id's #
    ##################################################
    if args.datessites == True:

        # get rid of inactive sites and such.
        solaredge_shared_lib.clean_config_db( config_db=config_db, flog=flog ) 

        list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
        list_of_sites = solaredge_shared_lib.arg_dates_function( solar_edge, flog=flog , list_of_sites=list_of_sites, status_db=rt_status_db)
        solaredge_shared_lib.save_list_of_sites_to_config_db( config_db, list_of_sites, flog ) 
        rt_status_db.timestamp( 111, flog )
        sys.exit( 0 )

    flog.info( inspect.stack()[0][3] + ": gestopt zonder uitgevoerde acties, geef commandline opties op." )
    sys.exit ( 1 ) # should be an error when there are no options given.

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
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])

