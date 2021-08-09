##########################################################################
# code sharded between different Python script for the solar edge data   #
##########################################################################

import base64
import const
import crypto3
import datetime
import inspect
import json
import json_lib
import makeLocalTimeString


POWER_PRODUCTION_SOLAR_INDEX_REC = [
    '',     # 'TIMESTAMP'                   0
    0 ,     # 'TIMEPERIOD_ID'               1
    0 ,     # 'POWER_SOURCE_ID'             2
    0.0 ,   # 'PRODUCTION_KWH_HIGH'         3
    0.0 ,   # 'PRODUCTION_KWH_LOW'          4
    0.0 ,   # 'PRODUCTION_KWH_HIGH_TOTAL'   5
    0.0 ,   # 'PRODUCTION_KWH_LOW_TOTAL'    6
    0.0,    # 'PRODUCTION_KWH_TOTAL'        7
]

SQL_INDEX_NUMBERS = [ 20, 30, 40, 50, 60, 70, 80 , 90 ] # site base index numbers


def clean_config_db( config_db=None, flog=None ):

    flog.info( inspect.stack()[0][3] + " wissen van verouderde site configuratie items gestart.")

    try:
        config_set = load_list_of_sites_from_config_db( db=config_db, flog=flog )

        if config_set == []:
            flog.warning( inspect.stack()[0][3] + ": Configuratie van sites is leeg, niets uitgevoerd " )
            return

        #print ( config_set[0] )

        new_config_list = []
        for item in config_set:
            #print ( item ['SITE_ACTIVE'], item ['DB_DELETE'], item ['DB_INDEX'] )
            #flog.info( inspect.stack()[0][3] + "site (check)" + str(item) + " controle.")
            if item ['SITE_ACTIVE'] == True or item ['DB_DELETE'] == False:
                #flog.info( inspect.stack()[0][3] + "site (added)" + str(item) + " toegevoegd.")
                new_config_list.append( item )
      
        #flog.info( inspect.stack()[0][3] + "site (list)" + str(new_config_list) )
        save_list_of_sites_to_config_db( db=config_db, list_of_sites=new_config_list, flog=flog )

        #check_list = load_list_of_sites_from_config_db(db=config_db, flog=flog)
        #flog.info( inspect.stack()[0][3] + "site (list reread)" + str(check_list) )

        flog.info( inspect.stack()[0][3] + " wissen van verouderde site configuratie items gereed.")
    except Exception as e:
        flog.error ( inspect.stack()[0][3] + ": onverwachte fout -> " + str(e) )
        return

########################################################
# clean the database from entries that not in the      #
# configuration list                                   #
########################################################
def database_clean_up( db=None, flog=None , db_config=None ):

    try:
        config_set = load_list_of_sites_from_config_db( db_config, flog=flog )
        
        if config_set == []:
            flog.warning( inspect.stack()[0][3] + ": Configuratie van sites is leeg, niets uitgevoerd " )
            return

        # make a default list of datbase indexes we want to remove.
        list_to_delete = SQL_INDEX_NUMBERS.copy()

        #print ( list_to_delete  )

        # check the config file to remove items that are not in the config.
        for item in config_set:
            #print (item ['DB_INDEX'], item ['DB_DELETE'] )
            if item ['DB_DELETE'] == 'False':
                continue # skip, must noy be deleted.
            list_to_delete.remove( item ['DB_INDEX'] )

    except Exception as e:
        flog.error (inspect.stack()[0][3]+": onverwachte fout." )
        return

    # remove all records where there are no db index number.
    # 
    try:
        for db_idx in list_to_delete:
            sql = "delete from " + const.DB_POWERPRODUCTION_SOLAR_TAB + " where power_source_id = 1 and TIMEPERIOD_ID between " + str(db_idx+1) + " and " + str(db_idx+5)
            db.excute( sql )
            flog.info (inspect.stack()[0][3]+": records wissen met de db_index tussen "+ str(db_idx+1) + " en " + str(db_idx+5) )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van records met de db_index tussen "+ str(db_idx+1) + " en " + str(db_idx+5) + " gefaald. -> " + str(e) )
    
    db.defrag()


########################################################
# delete all record                                   #
########################################################
def delete_all_record(db=None, table=const.DB_POWERPRODUCTION_SOLAR_TAB, flog=None ):
    try:
        sql_del_str = "delete from " + table  + " where POWER_SOURCE_ID = 1"
        flog.debug( inspect.stack()[0][3] + ": wissen van alle records. sql=" + sql_del_str ) 
        db.excute( sql_del_str )
    except Exception as e:
        flog.warning (inspect.stack()[0][3]+": wissen van minuten records gefaald: " + str(e) )



########################################################
# delete record that are passed the retention time     #
# and that are active                                  #
########################################################
def clean_db_by_retention( db=None, flog=None,  table=const.DB_POWERPRODUCTION_SOLAR_TAB, site_list=None ):
    
    timestamp = makeLocalTimeString.makeLocalTimeString()

    for item in site_list:
        if item['SITE_ACTIVE'] != False:
            db_idx = item['DB_INDEX']
        else:
            continue

        try:
            sql_del_str = "delete from " + table  + \
            " where TIMEPERIOD_ID = " + \
            str( db_idx+1 ) + \
            " and POWER_SOURCE_ID = 1 " + \
            " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=31)) + "'"
            flog.debug( inspect.stack()[0][3] + ": wissen van minuten. sql=" + sql_del_str ) 
            db.excute( sql_del_str )
        except Exception as e:
            flog.warning (inspect.stack()[0][3]+": wissen van minuten records gefaald: " + str(e) )
        
        try:
            sql_del_str = "delete from " + table  + \
            " where TIMEPERIOD_ID = " + \
            str( db_idx+2 ) + \
            " and POWER_SOURCE_ID = 1 " + \
            " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096)) + "'"
            flog.debug( inspect.stack()[0][3] + ": wissen van uren. sql=" + sql_del_str ) 
            db.excute( sql_del_str )
        except Exception as e:
            flog.warning (inspect.stack()[0][3]+": wissen van uren records gefaald: " + str(e) )

        try:
            sql_del_str = "delete from " + table  + \
            " where TIMEPERIOD_ID = " + \
            str( db_idx+3 ) + \
            " and POWER_SOURCE_ID = 1 " + \
            " and timestamp < '" + str( datetime.datetime.strptime( timestamp, "%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096)) + "'"
            flog.debug( inspect.stack()[0][3] + ": wissen van dagen. sql=" + sql_del_str ) 
            db.excute( sql_del_str )
        except Exception as e:
            flog.warning (inspect.stack()[0][3]+": wissen van dag records gefaald: " + str(e) )

    db.defrag()


########################################################
# check if the site exist in the list                  #
########################################################
def find_id_in_list( site_id, list_of_sites ):
    for site in list_of_sites:
        #print ("## site=" + str(site['ID'])  )
        if int( site['ID'] ) == int(site_id):
             return True
    return False

########################################################
# get sql index from config file or throw an error     #
# when index does not exists                           #
########################################################
def read_db_index_from_list( site_id, list_of_sites ):
    for site in list_of_sites:
        #print ("## site=" + str(site['ID'])  )
        if int( site['ID'] ) == int(site_id):
             return site['DB_INDEX']
    raise Exception("DB index niet gevonden.")

#######################################################
# add dates to found site id's                        #
#######################################################
def arg_dates_function( solar_obj ,flog=None, list_of_sites=None, status_db=None ):

    #list_of_sites = solaredge_shared_lib.load_list_of_sites_from_config_db( db=config_db, flog=flog )
    
    for item in list_of_sites:
        try:
            #print( "item['ID'] = ", item['ID'] )
            try:
                data = solar_obj.get_data_period( item['ID'] )
                status_db.timestamp( 111, flog )
                #print ( "data = ", data )
                start_date = json_lib.json_extract( data, 'startDate' )
                end_date = json_lib.json_extract(   data, 'endDate' )
                flog.debug( inspect.stack()[0][3] + ": ID " + str( item['ID'] ) + " start datum = " + str(start_date[0]) + " eind datum = " + str(end_date[0]) )
                item['START_DATE'] = str(start_date[0]) 
                item['END_DATE']   = str(end_date[0]) 
            except Exception as e:
                status_db.timestamp( 112, flog )
                flog.warning( inspect.stack()[0][3] + ": JSON probleem tijdens het lezen van start en eind datum voor ID " + str( item['ID'] ) )
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": list datum -> " + str(e.args[0]) )

    return list_of_sites

    #print( list_of_sites )
    #solaredge_shared_lib.save_list_of_sites_to_config_db( config_db, list_of_sites, flog )


########################################################
# write sites to the config database                   #
########################################################
def save_list_of_sites_to_config_db( db, list_of_sites, flog ):
    try:
        #raise Exception("dummy")
        parsed = json.dumps( list_of_sites , sort_keys=True )
        db.strset( parsed , 140, flog )
        flog.debug(inspect.stack()[0][3]+": configuratie JSON " + str( parsed ) )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Solar Edge configuratie kan niet worden opgeslagen -> " + str(e.args[0]) )    


########################################################
# load sites from de the config database               #
########################################################
def load_list_of_sites_from_config_db( db, flog=None ):

    list_of_sites = []

    # read config, if any from config database.
    try:
        _id, json_str, _label = db.strget( 140, flog ) 
        flog.debug( inspect.stack()[0][3]+": configuratie JSON uit database: " + str( json_str ) )
        if len(json_str) < 10:
            raise Exception("geen valide configuratie gegevens.")
        list_of_sites = json.loads( json_str )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": Configuratie kan niet worden gelezen uit de configuratie database -> " + str(e.args[0]) )   

    return list_of_sites

##########################################################################
# generate SQL statment(s) for the powerproduction solar                 #
# records_list: the list with all the SQL record data                    #
# flog: the logger                                                       #
# SQL table name                                                         #
# first_idx, start index in the list if you want to process a subset.    #
# last_idx, last index in the list if you want to process a subset.      #
##########################################################################
def generate_sql_text( records_list, flog=None, table_name = const.DB_POWERPRODUCTION_SOLAR_TAB, first_idx=None, last_idx=None ):
    
    if len(records_list) == 0:
        return '' # nothing to do, prevent errors

    sql_script = ''
    try:
        _last_idx  = len( records_list )-1
        _first_idx = 0

        if first_idx != None:
            _first_idx = first_idx

        if last_idx != None:
            _last_idx = last_idx

        # sanity checks
        if _last_idx < _first_idx :
            tmp        = _last_idx
            _last_idx  = _first_idx
            _first_idx = tmp
            flog.warning( inspect.stack()[0][3]+": first index > last index, indexen omgedraait." )
        
        if _last_idx > len( records_list )-1:
            _last_idx = len( records_list )-1
            flog.warning( inspect.stack()[0][3]+": last index buiten bereik aangepast naar maximale waarde." )

        if _first_idx < 0:
            _first_idx = 0
            flog.warning( inspect.stack()[0][3]+": first index buiten bereik aangepast naar 0." )

        while _first_idx <= _last_idx:

            record = records_list[ _first_idx ]
            sqlstr = "replace into " + table_name + " ( TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH, PRODUCTION_KWH_LOW, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL ) values ('" + \
                         record[0] + "', " +\
                    str( record[1] ) + ", " +\
                    str( record[2] ) + ", " +\
                    str( record[3] ) + ", " +\
                    str( record[4] ) + ", " +\
                    str( record[5] ) + ", " +\
                    str( record[6] ) + ", " +\
                    str( record[7] ) +\
                    ");"

           # insert fault for testing 
           # if record[0] == '2019-01-01 00:00:00':
           #     sqlstr = "dummy;"

            sqlstr = " ".join( sqlstr.split() )
            sql_script = sql_script + sqlstr
            
            _first_idx += 1

    except Exception as e:
        flog.error( inspect.stack()[0][3]+": error ->" + str(e) )

    #print ( sql_script )
    return sql_script

##########################################################################
# totals calculation for high, low and total kWh values in               #
# do this in memory for performance and SQL simplicty                    #
##########################################################################
def recalculate_totals( records_list, total_high_offset=0 ,total_low_offset=0, flog=None  ):

    if len(records_list) == 0:
        return # nothing to do, prevent errors

    try:
        # set totals for first record
        records_list[0][5] = round( records_list[0][3], 3 ) + total_high_offset
        records_list[0][6] = round( records_list[0][4], 3 ) + total_low_offset
        records_list[0][7] = round( records_list[0][5] + records_list[0][6], 3 )

        idx=1
        while idx < len(records_list):
            records_list[idx][5] = round( records_list[idx-1][5] + records_list[idx][3], 3 )  # TOTAL HIGH
            records_list[idx][6] = round( records_list[idx-1][6] + records_list[idx][4], 3 )  # TOTAL LOW
            records_list[idx][7] = round( records_list[idx][5]   + records_list[idx][6], 3 )  # TOTAL HIGH + LOW
            idx += 1

    except Exception as e:
        flog.error( inspect.stack()[0][3]+": error ->" + str(e) )

########################################################
# get the encrypted API key from the config database.  #
# db points to the config sqlite database              #
########################################################
def read_api_key( db , flog=None ):
    #raise Exception("test exception.")
    _id, encoded_api_key, _label = db.strget( 139 ,flog )
    decoded_api_key = base64.standard_b64decode( crypto3.p1Decrypt( encoded_api_key, 'solaredgeapikey' )).decode('utf-8')
    return decoded_api_key



""" kept for reference no longer used
##########################################################################
# totals calculation for high, low and total kWh values in the database  #
# do this in memory for performance and SQL simplicty                    #
##########################################################################
def db_total_recalculate( db_object,  timeperiod_id=45, total_high_offset=0 ,total_low_offset=0, db_table=const.DB_POWERPRODUCTION_SOLAR_TAB, flog=None  ):

        sql_query = "select \
            TIMESTAMP,\
            PRODUCTION_KWH_HIGH,\
            PRODUCTION_KWH_LOW,\
            PRODUCTION_KWH_HIGH_TOTAL,\
            PRODUCTION_KWH_LOW_TOTAL,\
            PRODUCTION_KWH_TOTAL\
            from " + db_table + " where TIMEPERIOD_ID=" + str(timeperiod_id) + " and POWER_SOURCE_ID=1 order by TIMESTAMP"
        # load records into buffer
       
        records_list = []
        try:
            records = db_object.select_rec( sql_query )
            for record in records:
                records_list.append( list(record) )

        except Exception as e:
            flog.error( inspect.stack()[0][3]+": sql error fase 1 totaal aanpassing ->" + str(e) )

        if len(records_list) == 0:
            flog.warning( inspect.stack()[0][3]+": geen records gevonden voor TIMEPERIOD_ID=" + str(timeperiod_id) )
            return

        try:
            # set totals for first record
            records_list[0][3] = round( records_list[0][1], 3 ) + total_high_offset
            records_list[0][4] = round( records_list[0][2], 3 ) + total_low_offset
            records_list[0][5] = round( records_list[0][3] + records_list[0][4], 3 )

            idx=1
            while idx < len(records_list):
                #print ( idx )
                records_list[idx][3] = round( records_list[idx-1][3] + records_list[idx][1], 3 )  # TOTAL HIGH
                records_list[idx][4] = round( records_list[idx-1][4] + records_list[idx][2], 3 )  # TOTAL LOW
                records_list[idx][5] = round( records_list[idx][3]   + records_list[idx][4], 3 )  # TOTAL HIGH + LOW
                idx += 1

        except Exception as e:
            flog.error( inspect.stack()[0][3]+": sql error fase 2 totaal aanpassing ->" + str(e) )

        # update database.
        for record in records_list:
            try:
                sql_update = "UPDATE " + db_table +\
                " set PRODUCTION_KWH_HIGH_TOTAL=" + str(record[3]) +\
                ", PRODUCTION_KWH_LOW_TOTAL=" + str(record[4]) + \
                ", PRODUCTION_KWH_TOTAL=" + str(record[5]) + " WHERE TIMESTAMP='" + str(record[0])+ "' and TIMEPERIOD_ID=" + str(timeperiod_id) + " and POWER_SOURCE_ID=1;"
                flog.debug( inspect.stack()[0][3] + ": sql = " + sql_update )
                db_object.excute( sql_update )
            except Exception as e:
                flog.error( inspect.stack()[0][3]+": sql error fase 3 totaal aanpassing voor timestamp " +\
                     str(record[0]) + "en TIMEPERIOD_ID=" + str(timeperiod_id) + " -> " + str(e) )
"""