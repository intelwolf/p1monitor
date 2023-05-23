# run manual with ./P1DynamicPrices
import argparse
import const
import datetime
import filesystem_lib
import inspect
import logger
import os
import pwd
import pytz
import requests
import sqldb
import sys
import signal
import sqldb_pricing
import time
import util

prgname         = 'P1DynamicPrices'
#config_db       = sqldb.configDB()
rt_status_db    = sqldb.rtStatusDb()
price_db        = sqldb_pricing.PricingDb()
local_timezone  = pytz.timezone('Europe/Amsterdam')

DB_DAYS_RETENTION = 1096

def main(argv):

    my_pid = os.getpid()

    flog.info( "Start van programma met process id " + str(my_pid) )
    flog.info( inspect.stack()[0][3] + ": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser = argparse.ArgumentParser(add_help=False) # suppress default UK help text

    parser.add_argument('-h', '--help', 
        action='help', default=argparse.SUPPRESS,
        help='Laat dit bericht zien en stop.')

    parser.add_argument('-g', '--getapidata',
        required=False,
        action="store_true",
        help="lees de api data via het internet in." )
    
    parser.add_argument('-ez', '--energyzero',
        required=False,
        default=True,
        action="store_true",
        help="gebruik energyzero als bron." )
    
    parser.add_argument('-dor', '--deletedoldbrecords',
        required=False,
        default=False,
        action="store_true",
        help="verwijder database records die ouder zijn dan " + str( DB_DAYS_RETENTION ) + " dagen" )
    
    parser.add_argument('-dar', '--deletedallbrecords',
        required=False,
        default=False,
        action="store_true",
        help="verwijder all database records." )

    parser.add_argument('-f', '--forced',
        required=False,
        default=False,
        action="store_true",
        help="update de database onachte de aanwezig data.")

    args = parser.parse_args()


    ###################################
    # init stuff                      #
    ###################################

    """
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": database niet te openen(1)." + const.FILE_DB_CONFIG + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.debug(inspect.stack()[0][3] + ": database tabel " + const.DB_CONFIG_TAB + " succesvol geopend.")
    """

    try:
        price_db.init(const.FILE_DB_FINANCIEEL ,const.DB_ENERGIEPRIJZEN_UUR_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(2)." + const.FILE_DB_FINANCIEEL + ") melding:" + str(e.args[0]))
        sys.exit(1)
    flog.debug( inspect.stack()[0][3] + ": database tabel " + const.DB_ENERGIEPRIJZEN_UUR_TAB + " succesvol geopend.")

    # open van status database
    try:    
        rt_status_db.init( const.FILE_DB_STATUS,const.DB_STATUS_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(3)." + const.FILE_DB_STATUS + ") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.debug( inspect.stack()[0][3] + ": database tabel " + const.FILE_DB_STATUS + " succesvol geopend.")
   

    #######################################
    # processing args                     #
    #######################################
    if args.deletedallbrecords == True:
        clean_database(mode="all")
        sys.exit(0)

    if args.deletedoldbrecords == True:
        if clean_database() == True:
            flog.info( inspect.stack()[0][3] + ": database records die ouder zijn dan " + str( DB_DAYS_RETENTION ) + " dagen verwijderd." )
            sys.exit(0)
        else:
            flog.error( inspect.stack()[0][3] + ": probelemen met het verwijderen van oude database records." )
            sys.exit(1)
        

    if args.getapidata == True:

        clean_database()

        if args.forced == False:
            flog.debug( inspect.stack()[0][3] + ": controle of een update nodig is van de prijzen." )
          
            #if datetime.datetime.now().hour != 23: # failsave run a least every day after 23:00

            if verify_database_data( look_ahead_hours=1 ) != None: 
                if verify_database_data( look_ahead_hours=0 ) != None:  #failsave for current hour
                    # we already have the data needed.
                    flog.info( inspect.stack()[0][3] + ": prijs data is al aanwezig een update is niet nodig, gestopt." )
                    sys.exit(0)
            #else:
            #     flog.info( inspect.stack()[0][3] + ": geforceerde run nog naar debug zetten." )

        if args.energyzero == True:

            if process_energyzero() == True:
                flog.info( inspect.stack()[0][3] + ": energyzero data succesvol verwerkt." )
                rt_status_db.timestamp( 129,flog )
                sys.exit(0)
            else:
                flog.error( inspect.stack()[0][3] + ": energyzero data probleem." )
                sys.exit(1)

    flog.info( inspect.stack()[0][3] + ": gestopt zonder iets uit te voeren." )
    sys.exit(0)


################################################
# remove entries from the database             #
# mode = older then the retention time         #
# mode = all remove all records.               #
# return true is ok, false is an error occured #
################################################
def clean_database(mode="old"):
    timestr=util.mkLocalTimeString() 
    if mode == "old":
        sql_del_str = "delete from " + const.DB_ENERGIEPRIJZEN_UUR_TAB + " where timestamp < '"+\
        str(datetime.datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=DB_DAYS_RETENTION))+"'"
    if mode == "all":
        sql_del_str = "delete from " + const.DB_ENERGIEPRIJZEN_UUR_TAB

    sql_del_str = " ".join(sql_del_str.split())
    try:
        flog.debug(inspect.stack()[0][3]+": sql delete = " + sql_del_str)
        price_db.execute(sql_del_str)
        if mode == "all":
            flog.info(inspect.stack()[0][3]+": alle records zijn gewist.")
        return True
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen van records gefaald. Melding = " + str(e.args[0]) )
        return False

################################################
# get energyzero data via the API.             #
# return true is ok, false is an error occured #
################################################
def process_energyzero() -> bool:

    r_value = True

    json_data = get_data_from_energyzero_api( usage_typ=1, mode="today" )
    if json_data != None:
        if update_db(json_data=json_data, db_field="PRICE_KWH", message_label="kWh" ) == False:
            flog.error(inspect.stack()[0][3]+": update dag van kWh gefaald." ) 
            r_value = False
    else:
        r_value = False

    json_data = get_data_from_energyzero_api( usage_typ=1, mode="tommorow" )
    if json_data != None:
        if update_db(json_data=json_data, db_field="PRICE_KWH", message_label="kWh" ) == False:
            flog.error(inspect.stack()[0][3]+": update dag van kWh gefaald." )
            r_value = False
    else:
        r_value = False

    json_data = get_data_from_energyzero_api(usage_typ=3, mode="today")
    if json_data != None:
        if update_db(json_data=json_data, db_field="PRICE_GAS", message_label="gas" ) == False:
            flog.error(inspect.stack()[0][3]+": update dag van gas gefaald." )
            r_value = False
    else:
        r_value = False

    json_data = get_data_from_energyzero_api(usage_typ=3, mode="tommorow")
    if json_data != None:
        if update_db(json_data=json_data, db_field="PRICE_GAS", message_label="gas" ) == False:
            flog.error(inspect.stack()[0][3]+": update dag van gas gefaald. = " )
            r_value = False
    else:
        r_value = False

    return r_value

################################################
# update prices database                       #
# return true is ok, false is an error occured #
################################################
def update_db( json_data=None, db_field=None, message_label="onbekend" ):
    
    r_value = True
    if json_data != None:

        entries = json_data["Prices"]
        for entry in entries:

            local_datetime = utc_to_local_timestamp(entry["readingDate"][0:19])

            #print ("local_datetime = ", local_datetime )

            try:
                sqlstr = "insert into " + const.DB_ENERGIEPRIJZEN_UUR_TAB + " (TIMESTAMP," + db_field + ") values ('" + \
                str(local_datetime) + "'," +\
                str(entry["price"]) +\
                ");"
                sqlstr=" ".join(sqlstr.split())
                price_db.execute( sqlstr )
                flog.debug(inspect.stack()[0][3]+": sql " + message_label + " prijs(insert) = " + sqlstr )
            except Exception as e:
                flog.debug( inspect.stack()[0][3] + ": sql: " + sqlstr + " verwachte fout melding: "+ str(e) )
                try:
                    sqlstr = "update " + const.DB_ENERGIEPRIJZEN_UUR_TAB + " set " + db_field + " = " + str(entry["price"])\
                    + " where TIMESTAMP = '" + str(local_datetime) + "';"
                    sqlstr=" ".join(sqlstr.split())
                    flog.debug(inspect.stack()[0][3]+": sql " + message_label + " prijs(update) = " + sqlstr )
                    price_db.execute( sqlstr )
                except Exception as e:
                    flog.error(inspect.stack()[0][3]+": sql " + message_label + " prijs(update) = " + sqlstr + " melding:" + str(e) )
                    r_value = False

        start_date = end_date = None
        try:
            if (len(entries) > 2 ):
                start_date = utc_to_local_timestamp(entries[0]["readingDate"][0:19])
                end_date   = utc_to_local_timestamp(entries[len(entries)-1]["readingDate"][0:19])
            if (len(entries) == 1 ):
                start_date = end_date = utc_to_local_timestamp(entries[0]["readingDate"][0:19])

            if (start_date != None and  end_date != None):
                flog.info( inspect.stack()[0][3] + ": " + str(len(entries)) + " " + message_label + " prijzen verwerkt van " + str(start_date) + " tot " + str(end_date) + ".")
            
        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": datum informatie fout " + message_label + " melding: " + str(e))
            #flog.warning( inspect.stack()[0][3] + " json to debug " + str(entries))

        return r_value


################################################
# convert UTC to localtime                     #
################################################
def utc_to_local_timestamp(utc_time):
     try:
        timestamp_obj = datetime.datetime.strptime(utc_time,"%Y-%m-%dT%H:%M:%S")
        local_datetime = timestamp_obj.replace(tzinfo=pytz.utc)
        local_datetime = local_datetime.astimezone(local_timezone).strftime("%Y-%m-%d %H:%M:%S")
        return local_datetime
     except Exception as e:
         flog.error( inspect.stack()[0][3] + ": conversie mislukt fout melding: "+ str(e) )
         return utc_time

#########################################################
# check the database if the data should be updated      #
# returns the date of the record found or None if the   #
# record does not exists.                                #
# failure will return None                              #
#########################################################
def verify_database_data( look_ahead_hours=1 ):

    utc_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=look_ahead_hours)
    local_datetime = utc_now.replace(tzinfo=pytz.utc)
    local_datetime = local_datetime.astimezone(local_timezone).strftime("%Y-%m-%d %H:00:00")

    try:
        sqlstr = "select TIMESTAMP, PRICE_GAS, PRICE_KWH from " + const.DB_ENERGIEPRIJZEN_UUR_TAB +\
        " where TIMESTAMP = '" + local_datetime + "' and PRICE_GAS is not NULL and PRICE_KWH is not NULL;"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql select is = " + sqlstr )
        rec = price_db.select_rec( sqlstr )
        flog.debug(inspect.stack()[0][3]+": sql return record = " + str(rec) )
        try:
            if rec != None and len(rec) > 0:
                if len(str(rec[0][0])) > 0:
                    return str(rec[0][0]) #timestamp of the record found.
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": sql antwoord , fout melding: "+ str(e) )
            return None
        else:
            return None
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": sql: " + sqlstr + " fout melding: "+ str(e) )
        return None


#########################################################
# read time from API the timeformat is UTC              #
# Dutch summer time is UTC+2 and winter time is UCT + 1 #
# usage_types: 1=electric, 3=gas                        #
# return a json string                                  #
#########################################################
def get_data_from_energyzero_api(usage_typ=1, interval=4, btw=True, mode="today"):

    #current_local_time = datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
    #current_local_time_start = datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
    #current_local_time_stop  = datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")
    #print( current_local_time_start, " - " ,current_local_time_stop  )
    #print(datetime.datetime.now().date())

    if mode == "today":
        current_local_date_str = datetime.datetime.now().date().strftime("%Y-%m-%d 00:00:00")

    if mode == "tommorow":
        current_local_date_str = (datetime.datetime.now().date() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d 00:00:00")

    #print("## 1 ", current_local_date_str, " mode = ", mode )

    if time.daylight == 1: #DST is on
        utc_timestamp_start = datetime.datetime.strptime(current_local_date_str,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=2)
    else:
        utc_timestamp_start = datetime.datetime.strptime(current_local_date_str,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=1)
    
    utc_timestamp_stop = utc_timestamp_start + datetime.timedelta( seconds=86399 )

    # API use UTC timestamps
    payload = {
        'fromDate' : utc_timestamp_start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        'tillDate' : utc_timestamp_stop.strftime("%Y-%m-%dT%H:%M:%S.999Z"),
        'interval' : interval,
        'usageType': usage_typ,
        'inclBtw'  : btw
        }
    
    headers = {
        'user-agent': 'P1-monitor '+ const.P1_VERSIE 
        }

    # https://api.energyzero.nl/v1/energyprices?fromDate=2023-03-02T00%3A07%3A16.000Z&tillDate=2023-03-03T23%3A07%3A16.000Z&interval=4&usageType=3&inclBtw=True
    r = requests.get('https://api.energyzero.nl/v1/energyprices', params=payload, headers=headers, timeout=5)

    if r.status_code != requests.codes.ok:
        flog.critical(inspect.stack()[0][3]+": energyzero melding: " + str(e.args[0]))
        return None
    else:
        flog.debug(inspect.stack()[0][3]+": api query succesvol: " + str(r.url) )
        return r.json()

########################################################
# reset signals and close stuff                        #
########################################################
def saveExit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    print("SIGINT ontvangen, gestopt.")
    sys.exit(0)

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
    main(sys.argv[1:])