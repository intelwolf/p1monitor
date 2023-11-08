# run manual with ./P1Db.py

import const
import inspect
import datetime
import signal
import shutil
import logger
import os
import sys
import sqldb
import sqldb_pricing
import time
import util
import phase_shared_lib
import data_struct_lib
import process_lib
import util
import financial_lib

prgname = 'P1Db'

rt_status_db          = sqldb.rtStatusDb()
config_db             = sqldb.configDB()
e_db_serial           = sqldb.SqlDb1()
e_db_history_min      = sqldb.SqlDb2()
e_db_history_uur      = sqldb.SqlDb3()
e_db_history_dag      = sqldb.SqlDb4()
e_db_history_maand    = sqldb.SqlDb4()
e_db_history_jaar     = sqldb.SqlDb4()
e_db_financieel_dag   = sqldb.financieelDb()
e_db_financieel_maand = sqldb.financieelDb()
e_db_financieel_jaar  = sqldb.financieelDb()
watermeter_db         = sqldb.WatermeterDBV2()
fase_db               = sqldb.PhaseDB()
fase_db_min_max_dag   = sqldb.PhaseMaxMinDB()
price_db              = sqldb_pricing.PricingDb()

VERBR_KWH_181           = 0.0
VERBR_KWH_182           = 0.0
GELVR_KWH_281           = 0.0
GELVR_KWH_282           = 0.0
VERBR_KWH_X             = 0.0
GELVR_KWH_X             = 0.0
TARIEFCODE              = ''
ACT_VERBR_KW_170        = 0.0
ACT_GELVR_KW_270        = 0.0
VERBR_GAS_2421          = 0.0
timestamp               = 'x'
timestamp_min_one       = ''

def Main():
    global timestamp
    phasemaxmin = data_struct_lib.phase_db_min_max_record

    financial_costs = financial_lib.Cost2Database()

    flog.info("Start van programma.")

    DiskRestore()

    # open van status database
    try:    
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van seriele database
    try:
        e_db_serial.init(const.FILE_DB_E_FILENAME ,const.DB_SERIAL_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_E_FILENAME+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_SERIAL_TAB+" succesvol geopend.")

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

    # open van watermeter database
    try:    
        watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(12)." + const.FILE_DB_WATERMETERV2 + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

    # open van fase database
    try:
        fase_db.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_REALTIME_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+" database niet te openen(13)." + const.FILE_DB_PHASEINFORMATION + ") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_FASE_REALTIME_TAB + " succesvol geopend.")

    # open van fase database voor min/max waarden.
    try:
        fase_db_min_max_dag.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_MINMAX_DAG_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+" database niet te openen(14)." + const.FILE_DB_PHASEINFORMATION + ") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_FASE_MINMAX_DAG_TAB + " succesvol geopend.")

    try:
        price_db.init(const.FILE_DB_FINANCIEEL ,const.DB_ENERGIEPRIJZEN_UUR_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(15)." + const.FILE_DB_FINANCIEEL + ") melding:" + str(e.args[0]))
        sys.exit(1)
    flog.debug( inspect.stack()[0][3] + ": database tabel " + const.DB_ENERGIEPRIJZEN_UUR_TAB + " succesvol geopend.")

    # defrag databases
    e_db_history_min.defrag()
    flog.info(inspect.stack()[0][3]+": database bestand "+const.FILE_DB_E_HISTORIE+" gedefragmenteerd.")
    e_db_financieel_dag.defrag()
    flog.info(inspect.stack()[0][3]+": database bestand "+const.FILE_DB_FINANCIEEL+" gedefragmenteerd.")
    fase_db.defrag()
    flog.info(inspect.stack()[0][3]+": database bestand "+const.FILE_DB_PHASEINFORMATION+" gedefragmenteerd.")

    #flog.setLevel( logging.DEBUG )
    #flog.consoleOutputOn( True )

    setFileFlags()

    flog.info(inspect.stack()[0][3]+": hoofd programma loop gestart.")
    rt_status_db.timestamp(6,flog)
    #updateWeaterData()
    backupData()

    #sys.exit(0)
    #print "###### ->day =" + str( floatX3( float( datetime.now().timetuple().tm_yday)/365 )*100) 

   
    financial_costs.init( 
        financial_db=e_db_financieel_dag, 
        kwh_gas_db=e_db_history_min, 
        watermeter_db=watermeter_db, 
        config_db=config_db,
        status_db=rt_status_db,
        flog=flog )

    pauze_tijd_hoofdloop = 1
    while 1:

        #flog.setLevel( logging.DEBUG )
        #flog.consoleOutputOn( True )
        #tarifSwitcher()
        #flog.setLevel( logging.INFO )
        #flog.consoleOutputOn( False )

        secswaiting = serialDataAvailable()
        if secswaiting > 59:
            powerUsedPerMin()
            updateDbMin()
            updateDbHour()
            updateDbDay()
            updateDbMonth()
            updateDbYear()
            updateGas()
            #flog.setLevel( logger.logging.DEBUG )
            financial_costs.execute( timestamp=timestamp )
            #flog.setLevel( logger.logging.INFO )
            
            #flog.setLevel( logging.DEBUG ) 
            phase_shared_lib.write_phase_min_max_day_values_to_db( minmaxrec=phasemaxmin, configdb=config_db, phasedb=fase_db, flog=flog, timestamp=timestamp)
            #flog.setLevel( logging.INFO ) 

            #if isMod(timestamp,1) == True: # only once per min to prevent load.
            #    powerSwitcher()
            #    tarifSwitcher()
                
            if util.isMod( timestamp, 15 ) == True:
                backupData()
                cleanDb()

            #flog.setLevel(logging.INFO)
     
            
        else: # niet aanpassen!
            pauze_tijd_hoofdloop = abs(60-secswaiting)/2
            if pauze_tijd_hoofdloop < 10:
                pauze_tijd_hoofdloop = 5
        flog.debug(inspect.stack()[0][3]+": pauze_tijd_hoofdloop="+str(pauze_tijd_hoofdloop))
        time.sleep(pauze_tijd_hoofdloop)
        #sys.exit(1)

# functions 

def updateGas():
    
    timestamp_dag = timestamp[0:10]
    timestamp_yesterday    = str(datetime.datetime.strptime(timestamp,"%Y-%m-%d %H:%M") - datetime.timedelta(minutes=1440))[0:10]
    #print(timestamp_dag)
    #print(timestamp_yesterday)
    min_gas_value=max_gas_value=0
    max_value_from_yesterday = 0
    
    # Algorithm to find time window.
    #find max date from yesterday (start date),
    # if no date found for yesterday find minimum date for today (start date).
    # Find last record from today
    # subtract value from last record from today from start date 

    try:
        sqlstr = "select verbr_GAS_2421 from "+const.DB_HISTORIE_MIN_TAB+\
        " where timestamp = (select max(timestamp) from "+const.DB_HISTORIE_MIN_TAB+\
        " where substr(timestamp,1,10) = '"+timestamp_yesterday+"' and verbr_GAS_2421 > 0)"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec=e_db_history_min.select_rec(sqlstr)
        if len(rec) > 0:
            min_gas_value = rec[0][0]
            max_value_from_yesterday = min_gas_value
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
    except Exception as e:
        flog.warning(inspect.stack()[0][3]+": sql error(1)"+str(e))

    if len(rec) == 0 : # no record found for yesterday
        flog.debug(inspect.stack()[0][3]+": Geen start record gevonden voor GISTEREN ("+str(timestamp_yesterday)+")")
        try:
            sqlstr = "select verbr_GAS_2421 from "+const.DB_HISTORIE_MIN_TAB+\
            " where timestamp = (select min(timestamp) from "+const.DB_HISTORIE_MIN_TAB+\
            " where substr(timestamp,1,10) = '"+timestamp_dag+"' and verbr_GAS_2421 > 0)"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
            rec=e_db_history_min.select_rec(sqlstr)
            flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
            if len(rec) > 0:
                min_gas_value = rec[0][0]
            else:
                flog.debug(inspect.stack()[0][3]+": Geen start record gevonden voor VANDAAG ("+str(timestamp_yesterday)+"). Gestopt met verwerken GAS records.")
                return
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e))
    #else:
    #    min_gas_value = rec[0][0]
    
    # find max value for today
    
    try:
        sqlstr = "select verbr_GAS_2421 from "+const.DB_HISTORIE_MIN_TAB+\
        " where timestamp = (select max(timestamp) from "+const.DB_HISTORIE_MIN_TAB+\
        " where substr(timestamp,1,10) = '"+timestamp_dag+"')"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
        rec=e_db_history_min.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))
    
    if len(rec) > 0:
        max_gas_value = rec[0][0]
    else:
        flog.error(inspect.stack()[0][3]+": Geen stop record gevonden voor VANDAAG ("+str(timestamp_yesterday)+"). Gestopt met verwerken GAS records.")
        return
    
    VERBR_GAS_X = max_gas_value - min_gas_value
    flog.debug(inspect.stack()[0][3]+": min_gas_value="+str(min_gas_value)+" max_gas_value="+str(max_gas_value)+" VERBR_GAS_X="+str(VERBR_GAS_X))
    
    # failsafe verbruik kan nooit negatief zijn
    if VERBR_GAS_X  < 0:
        VERBR_GAS_X  = 0
    flog.debug(inspect.stack()[0][3]+": min_gas_value="+str(min_gas_value)+" max_gas_value="+str(max_gas_value)+" VERBR_GAS_X="+str(VERBR_GAS_X))
    
    # update day GAS record
    try:
        sqlstr = "update "+const.DB_HISTORIE_DAG_TAB+" set verbr_gas_x ="+str(VERBR_GAS_X)+" where timestamp = '"+timestamp_dag+" 00:00:00'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(4)="+sqlstr)
        e_db_history_dag.update_rec(sqlstr)        
    except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(4)"+str(e)) 
    
    # status update
    #gas waarde van de dag
    rt_status_db.strset( str(VERBR_GAS_X), 44, flog )
    
    # select all records from this month
    try:
        sqlstr = "select sum(VERBR_GAS_X) from "+const.DB_HISTORIE_DAG_TAB+" where substr(timestamp,1,7) = '"+timestamp_dag[0:7]+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(5)="+sqlstr)
        rec=e_db_history_dag.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(5)"+str(e))

    if len(rec) > 0:
        # update month GAS record
        try:
            sqlstr = "update "+const.DB_HISTORIE_MAAND_TAB+" set verbr_gas_x ="+str(rec[0][0])+" where timestamp = '"+timestamp_dag[0:7]+"-01 00:00:00'"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(6)="+sqlstr)
            e_db_history_maand.update_rec(sqlstr)        
        except Exception as e:
                flog.error(inspect.stack()[0][3]+": sql error(6)"+str(e))

    # select all records from this year
    try:
        sqlstr = "select sum(VERBR_GAS_X) from "+const.DB_HISTORIE_MAAND_TAB+" where substr(timestamp,1,4) = '"+timestamp_dag[0:4]+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(7)="+sqlstr)
        rec=e_db_history_maand.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(7)"+str(e))

    if len(rec) > 0:
        # update year GAS record
        try:
            sqlstr = "update "+const.DB_HISTORIE_JAAR_TAB+" set verbr_gas_x ="+str(rec[0][0])+" where timestamp = '"+timestamp_dag[0:4]+"-01-01 00:00:00'"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(6)="+sqlstr)
            e_db_history_jaar.update_rec(sqlstr)        
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(6)"+str(e))
            
    #flog.setLevel(logging.DEBUG)
    # update GAS values hour (this is repeated because of low update frequency of gas measurement).
    #flog.setLevel(logging.DEBUG)
    timestamp_hour     = int(timestamp[11:13])
    buffer             = [0] * 24
    delta_buffer     = [0] * 24
    flog.debug(inspect.stack()[0][3]+": hoogste waarde van gisteren is = "+str(max_value_from_yesterday))
    for t in range(0, timestamp_hour+1):
        hour_timestamp = timestamp_dag+" "+'{:02d}'.format(t)
        #flog.debug(inspect.stack()[0][3]+": uur verwerking voor = "+str(hour_timestamp));
        try:
            sqlstr = "select timestamp, verbr_gas_2421 from e_history_min where timestamp = (select max(timestamp) from e_history_min where substr(timestamp,1,13) = '"+hour_timestamp+"')" 
            sqlstr = " ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(6)="+sqlstr)
            rec = e_db_history_min.select_rec(sqlstr)
            if len(rec) > 0:
                flog.debug(inspect.stack()[0][3]+": waarde record"+str(rec))
                buffer[t] = rec[0][1]
                if t == 0:
                    if max_value_from_yesterday != 0:
                        delta_buffer[t] = round(abs(max_value_from_yesterday - buffer[t]),4)
                else:
                    if buffer[t-1] != 0: # only process sane values
                        delta_buffer[t] = round(abs(buffer[t-1] - buffer[t]),4)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(7)"+str(e))
    
    try:
        for u in range(0, timestamp_hour+1):
            hour_timestamp = timestamp_dag+" "+'{:02d}'.format(u)
            sqlstr = "update "+const.DB_HISTORIE_UUR_TAB+" set verbr_gas_x ="+str(delta_buffer[u])+" where timestamp = '"+hour_timestamp+":00:00'"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(6)="+sqlstr)
            e_db_history_uur.update_rec(sqlstr)    
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql update error(8)"+str(e))
    #print buffer
    #print delta_buffer
    #flog.setLevel(logging.INFO)

def setFileFlags():
    util.setFile2user(const.FILE_DB_E_FILENAME,'p1mon')
    util.setFile2user(const.FILE_DB_E_HISTORIE,'p1mon')
    util.setFile2user(const.FILE_DB_CONFIG,'p1mon')
    util.setFile2user(const.FILE_DB_STATUS,'p1mon')
    util.setFile2user(const.FILE_DB_FINANCIEEL,'p1mon')
    util.setFile2user(const.FILE_DB_WEATHER,'p1mon')
    util.setFile2user(const.FILE_DB_WEATHER_HISTORIE,'p1mon')
    util.setFile2user(const.FILE_DB_TEMPERATUUR_FILENAME,'p1mon')
    util.setFile2user(const.FILE_DB_WATERMETER,'p1mon')
    util.setFile2user(const.FILE_DB_PHASEINFORMATION,'p1mon')

    _dummy,tail = os.path.split(const.FILE_DB_E_FILENAME)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split(const.FILE_DB_E_HISTORIE)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split(const.FILE_DB_CONFIG)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split(const.FILE_DB_STATUS)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split(const.FILE_DB_FINANCIEEL)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split(const.FILE_DB_WEATHER)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split(const.FILE_DB_WEATHER_HISTORIE)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon') 
    _dummy,tail = os.path.split(const.FILE_DB_TEMPERATUUR_FILENAME)
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split( const.FILE_DB_WATERMETERV2 )
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    _dummy,tail = os.path.split( const.FILE_DB_PHASEINFORMATION )
    util.setFile2user(const.DIR_FILEDISK+tail,'p1mon')

def cleanDb():
    timestr=util.mkLocalTimeString() 
    # minuten records verwijderen
    sql_del_str = "delete from "+const.DB_HISTORIE_MIN_TAB+" where timestamp <  '"+\
    str(datetime.datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=31))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql="+sql_del_str)
        e_db_history_min.del_rec(sql_del_str)     
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen min. recs,delete gefaald. Melding="+str(e.args[0]))

    # uur records verwijderen
    sql_del_str = "delete from "+const.DB_HISTORIE_UUR_TAB+" where timestamp <  '"+\
    str(datetime.datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql="+sql_del_str)
        e_db_history_uur.del_rec(sql_del_str)     
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen uur recs,delete gefaald. Melding="+str(e.args[0]))

    # removed in version 2.3.0
    # new standard retention is minutes 31 days, hours 1096 days, days, months, years unlimted.
    """
    # dagen records verwijderen
    sql_del_str = "delete from "+const.DB_HISTORIE_DAG_TAB+" where timestamp <  '"+\
    str(datetime.datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - datetime.timedelta(days=1096))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql="+sql_del_str)
        e_db_history_dag.del_rec(sql_del_str)     
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen dag recs,delete gefaald. Melding="+str(e.args[0]))
    """
    
def backupFile(filename):
    try:
        file_sec_delta = util.file_delta_timestamp(filename ,const.DIR_FILEDISK)
        if file_sec_delta > 0 or file_sec_delta== -1:
            shutil.copy2(filename, const.DIR_FILEDISK)
            flog.info(inspect.stack()[0][3]+": "+filename+" naar "+const.DIR_FILEDISK+" gekopieerd.")
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": data backup "+filename+" Fout: "+str(e))

def backupData():
    #setFileFlags()
    flog.debug(inspect.stack()[0][3]+": Gestart")
    cmd = "/p1mon/scripts/P1DbCopy --allcopy2disk --forcecopy" # 1.8.0
    process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=False,
        flog=flog
    )


    rt_status_db.timestamp(29,flog)
    flog.debug(inspect.stack()[0][3]+": Gereed")

def DiskRestore():
    cmd = "/p1mon/scripts/P1DbCopy --allcopy2ram" # 1.8.0
    process_lib.run_process( 
        cms_str = cmd,
        use_shell=True,
        give_return_value=False,
        flog=flog 
    )

def updateDbYear():
    timestamp_jaar = timestamp[0:4]+"-01-01 00:00:00"
    try:
        sqlstr= "select timestamp, VERBR_KWH_X, GELVR_KWH_X from "+const.DB_HISTORIE_JAAR_TAB+" where timestamp = '"+timestamp_jaar+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec=e_db_history_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

    if len(rec) > 0: # record bestaat al dus een update van het record
        flog.debug(inspect.stack()[0][3]+": jaar record voor timestamp="+timestamp_jaar+" bestaat we doen een update.")
        try:
            sqlstr = "update "+const.DB_HISTORIE_JAAR_TAB+\
            " set VERBR_KWH_181="+str(VERBR_KWH_181)+", \
            VERBR_KWH_182="+str(VERBR_KWH_182)+", \
            GELVR_KWH_281="+str(GELVR_KWH_281)+", \
            GELVR_KWH_282="+str(GELVR_KWH_282)+", \
            VERBR_KWH_X="+str(rec[0][1]+VERBR_KWH_X)+", \
            GELVR_KWH_X="+str(rec[0][2]+GELVR_KWH_X)+", \
            VERBR_GAS_2421="+str(VERBR_GAS_2421)+ \
            " where timestamp = '"+timestamp_jaar+"'"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
            e_db_history_jaar.update_rec(sqlstr)        
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))       

    else: # record bestaat niet dus een insert van een nieuwe record
        flog.debug(inspect.stack()[0][3]+": jaar record voor timestamp="+timestamp_jaar+" bestaat NIET, record wordt gemaakt.")
        try:
            sqlstr= "insert into "+const.DB_HISTORIE_JAAR_TAB+" (timestamp, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X, VERBR_GAS_2421)\
            values ('"+timestamp_jaar+"',"+\
            str(VERBR_KWH_181)+","+\
            str(VERBR_KWH_182)+","+\
            str(GELVR_KWH_281)+","+\
            str(GELVR_KWH_282)+","+\
            str(VERBR_KWH_X)+","+\
            str(GELVR_KWH_X)+","+\
            str(VERBR_GAS_2421)+")"
            ")"   
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
            e_db_history_jaar.insert_rec(sqlstr)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e)) 
    rt_status_db.timestamp(15,flog)

# wegschrijven van maand waarde
def updateDbMonth():
    timestamp_maand = timestamp[0:7]+"-01 00:00:00"
    try:
        sqlstr= "select timestamp, VERBR_KWH_X, GELVR_KWH_X from "+const.DB_HISTORIE_MAAND_TAB+" where timestamp = '"+timestamp_maand+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec=e_db_history_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

    if len(rec) > 0: # record bestaat al dus een update van het record
        flog.debug(inspect.stack()[0][3]+": maand record voor timestamp="+timestamp_maand+" bestaat we doen een update.")
        try:
            sqlstr = "update "+const.DB_HISTORIE_MAAND_TAB+\
            " set VERBR_KWH_181="+str(VERBR_KWH_181)+", \
            VERBR_KWH_182="+str(VERBR_KWH_182)+", \
            GELVR_KWH_281="+str(GELVR_KWH_281)+", \
            GELVR_KWH_282="+str(GELVR_KWH_282)+", \
            VERBR_KWH_X="+str(rec[0][1]+VERBR_KWH_X)+", \
            GELVR_KWH_X="+str(rec[0][2]+GELVR_KWH_X)+", \
            VERBR_GAS_2421="+str(VERBR_GAS_2421)+ \
            " where timestamp = '"+timestamp_maand+"'"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
            e_db_history_maand.update_rec(sqlstr)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))       

    else: # record bestaat niet dus een insert van een nieuwe record
        flog.debug(inspect.stack()[0][3]+": maand record voor timestamp="+timestamp_maand+" bestaat NIET, record wordt gemaakt.")
        try:
            sqlstr= "insert into "+const.DB_HISTORIE_MAAND_TAB+" (timestamp, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X , VERBR_GAS_2421)\
            values ('"+timestamp_maand+"',"+\
            str(VERBR_KWH_181)+","+\
            str(VERBR_KWH_182)+","+\
            str(GELVR_KWH_281)+","+\
            str(GELVR_KWH_282)+","+\
            str(VERBR_KWH_X)+","+\
            str(GELVR_KWH_X)+","+\
            str(VERBR_GAS_2421)+")"
            ")"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
            e_db_history_maand.insert_rec(sqlstr)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e))

    rt_status_db.timestamp(14,flog)

# wegschrijven van dag waarde
def updateDbDay():
    timestamp_dag = timestamp[0:10]+" 00:00:00"

    try:
        sqlstr= "select timestamp, VERBR_KWH_X, GELVR_KWH_X from "+const.DB_HISTORIE_DAG_TAB+" where timestamp = '"+timestamp_dag+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec=e_db_history_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))
 
    if len(rec) > 0: # record bestaat al dus een update van het record
        flog.debug(inspect.stack()[0][3]+": dag record voor timestamp="+timestamp_dag+" bestaat we doen een update.")
        try:
            sqlstr = "update "+const.DB_HISTORIE_DAG_TAB+\
            " set VERBR_KWH_181="+str(VERBR_KWH_181)+", \
            VERBR_KWH_182="+str(VERBR_KWH_182)+", \
            GELVR_KWH_281="+str(GELVR_KWH_281)+", \
            GELVR_KWH_282="+str(GELVR_KWH_282)+", \
            VERBR_KWH_X="+str(rec[0][1]+VERBR_KWH_X)+", \
            GELVR_KWH_X="+str(rec[0][2]+GELVR_KWH_X)+", \
            VERBR_GAS_2421="+str(VERBR_GAS_2421)+"  \
            where timestamp = '"+timestamp_dag+"'"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
            e_db_history_dag.update_rec(sqlstr)      
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))       

    else: # record bestaat niet dus een insert van een nieuwe record
        flog.debug(inspect.stack()[0][3]+": dag record voor timestamp="+timestamp_dag+" bestaat NIET, record wordt gemaakt.")
        try:
            sqlstr= "insert into "+const.DB_HISTORIE_DAG_TAB+" (timestamp, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X ,VERBR_GAS_2421)\
            values ('"+timestamp_dag+"',"+\
            str(VERBR_KWH_181)+","+\
            str(VERBR_KWH_182)+","+\
            str(GELVR_KWH_281)+","+\
            str(GELVR_KWH_282)+","+\
            str(VERBR_KWH_X)+","+\
            str(GELVR_KWH_X)+","+\
            str(VERBR_GAS_2421)+")"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
            e_db_history_dag.insert_rec(sqlstr)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e)) 
    rt_status_db.timestamp(13,flog)

# wegschrijven van uur waarde
def updateDbHour():
    timestamp_uur = timestamp[0:13]+":00:00"

    try:
        sqlstr= "select timestamp, VERBR_KWH_X, GELVR_KWH_X from "+const.DB_HISTORIE_UUR_TAB+" where timestamp = '"+timestamp_uur+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec=e_db_history_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van bestaande record="+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

    if len(rec) > 0: # record bestaat al dus een update van het record
        flog.debug(inspect.stack()[0][3]+": uur record voor timestamp="+timestamp_uur+" bestaat we doen een update.")
        try:
            sqlstr = "update "+const.DB_HISTORIE_UUR_TAB+\
            " set VERBR_KWH_181="+str(VERBR_KWH_181)+", \
            VERBR_KWH_182="+str(VERBR_KWH_182)+", \
            GELVR_KWH_281="+str(GELVR_KWH_281)+", \
            GELVR_KWH_282="+str(GELVR_KWH_282)+", \
            VERBR_KWH_X="+str(rec[0][1]+VERBR_KWH_X)+", \
            GELVR_KWH_X="+str(rec[0][2]+GELVR_KWH_X)+", \
            TARIEFCODE='"+str(TARIEFCODE)+"', \
            VERBR_GAS_2421="+str(VERBR_GAS_2421)+" \
            where timestamp = '"+timestamp_uur+"'"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
            e_db_history_uur.update_rec(sqlstr)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))       

    else: # record bestaat niet dus een insert van een nieuwe record
        flog.debug(inspect.stack()[0][3]+": uur record voor timestamp="+timestamp_uur+" bestaat NIET, record wordt gemaakt.")
        try:
            sqlstr= "insert into "+const.DB_HISTORIE_UUR_TAB+" (timestamp, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X, TARIEFCODE, VERBR_GAS_2421)\
            values ('"+timestamp_uur+"',"+\
            str(VERBR_KWH_181)+","+\
            str(VERBR_KWH_182)+","+\
            str(GELVR_KWH_281)+","+\
            str(GELVR_KWH_282)+","+\
            str(VERBR_KWH_X)+","+\
            str(GELVR_KWH_X)+",'"+\
            str(TARIEFCODE)+"', "+\
            str(VERBR_GAS_2421)+")"
            sqlstr=" ".join(sqlstr.split())
            flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
            e_db_history_uur.insert_rec(sqlstr)
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e))   
    rt_status_db.timestamp(12,flog)

# wegschrijven van minuut waarde
def updateDbMin():
    try:
        sqlstr= "insert or replace into " + const.DB_HISTORIE_MIN_TAB + " values (\
        '"+timestamp+":00',\
        '"+str(VERBR_KWH_181)+"',\
        '"+str(VERBR_KWH_182)+"',\
        '"+str(GELVR_KWH_281)+"',\
        '"+str(GELVR_KWH_282)+"',\
        '"+str(VERBR_KWH_X)+"',\
        '"+str(GELVR_KWH_X)+"',\
        '"+str(TARIEFCODE)+"',\
        '"+str(ACT_VERBR_KW_170)+"',\
        '"+str(ACT_GELVR_KW_270)+"',\
        '"+str(VERBR_GAS_2421)+"')"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
        e_db_history_min.insert_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": Succesvol gegevens in e-history db (1min) geplaatst met timestamp "+\
            timestamp+":00")
        rt_status_db.timestamp(7,flog)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

def powerUsedPerMin():  
    #global verbr_kwh_totaal, gelvr_kwh_totaal,verbr_kwh_x, gelvr_kwh_x,\
    #tariefcode,act_verbr_kw, act_gelvr_kw, timestamp, timestamp_min_one

    global VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X, \
            TARIEFCODE, ACT_VERBR_KW_170, ACT_GELVR_KW_270, VERBR_GAS_2421, timestamp, timestamp_min_one

    try:
        sqlstr = "select min(timestamp) from " + const.DB_SERIAL_TAB + " where record_verwerkt=0"
        rec_serial=e_db_serial.select_rec(sqlstr)
        timestamp            = str(rec_serial[0][0])[0:16]
        timestamp_min_one    = str(datetime.datetime.strptime(timestamp,"%Y-%m-%d %H:%M") - datetime.timedelta(minutes=1))[0:16]
        flog.debug(inspect.stack()[0][3]+": timestamp nog niet verwerkte oudste record in serieele database ="+timestamp+" vorige minuut ="+timestamp_min_one)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(find timestamp)"+str(e))

    try:
        # huidige te verwerken minuut bepalen
        sqlstr="select max(verbr_kwh_181),max(verbr_kwh_182),max(gelvr_kwh_281),\
        max(gelvr_kwh_282), tariefcode, avg(act_verbr_kw_170),avg(act_gelvr_kw_270) \
        ,substr(timestamp,1,16), max(verbr_gas_2421) from "+const.DB_SERIAL_TAB+\
        " where substr(timestamp,1,16) = '"+timestamp+"'"
        sqlstr = " ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        recs_serial_now=e_db_serial.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": Serial inhoud van verwerkt minuut is ="+str(recs_serial_now))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

    try:
        # huidige -1 minuut te verwerken minuut lezen
        sqlstr="select max(verbr_kwh_181),max(verbr_kwh_182),max(gelvr_kwh_281),\
        max(gelvr_kwh_282), tariefcode, avg(act_verbr_kw_170),avg(act_gelvr_kw_270) \
        ,substr(timestamp,1,16), max(verbr_gas_2421) from "+const.DB_SERIAL_TAB+\
        " where substr(timestamp,1,16) = '"+timestamp_min_one+"'"
        sqlstr = " ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
        recs_serial_old=e_db_serial.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": Serial inhoud van verwerkt minuut(-1) is ="+str(recs_serial_old))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": probleem met record van een minuut(-1)"+str(e))

    try:
        VERBR_KWH_181       = recs_serial_now[0][0]
        VERBR_KWH_182       = recs_serial_now[0][1]
        GELVR_KWH_281       = recs_serial_now[0][2]
        GELVR_KWH_282       = recs_serial_now[0][3]
        VERBR_KWH_X         = (VERBR_KWH_181 + VERBR_KWH_182) - (recs_serial_old[0][0]+recs_serial_old[0][1])
        GELVR_KWH_X         = (GELVR_KWH_281 + GELVR_KWH_282) - (recs_serial_old[0][2]+recs_serial_old[0][3])
        TARIEFCODE          = recs_serial_now[0][4]
        ACT_VERBR_KW_170    = recs_serial_now[0][5]
        ACT_GELVR_KW_270    = recs_serial_now[0][6]
        VERBR_GAS_2421      = recs_serial_now[0][8]
        #print(VERBR_GAS_2421)

    except Exception as e:
        # geen vorige record we zetten de gevonden delta op nul
        VERBR_KWH_X = 0
        GELVR_KWH_X = 0
        flog.warning( inspect.stack()[0][3]+": geen vorige record gevonden voor minuut =" + timestamp_min_one )

    # failsafe verbruik kan nooit negatief zijn
    if VERBR_KWH_X < 0:
        VERBR_KWH_X = 0
    if GELVR_KWH_X <0:
        GELVR_KWH_X = 0

    flog.debug(inspect.stack()[0][3]+": [*]verbr_kw sinds vorige min ="+str(VERBR_KWH_X))
    flog.debug(inspect.stack()[0][3]+": [*]gelvr_kw sinds vorige min ="+str(GELVR_KWH_X))

    try:
        sqlstr = "update " + const.DB_SERIAL_TAB+\
        " set record_verwerkt=1 where substr(timestamp,1,16) = '"+\
        timestamp+"'"
        sqlstr = " ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": Update serieel record verwerkt. sql="+sqlstr)
        e_db_serial.update_rec(sqlstr)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))

# geeft het aantal seconden terug tussen de meeste recente record
# en het oudste nog niet verwerkte record.
def serialDataAvailable(): 
    try:
        sqlstr = "select strftime('%s',max(timestamp)) - strftime('%s',min(timestamp)) from " + const.DB_SERIAL_TAB + " where record_verwerkt=0"
        sqlstr = " ".join(sqlstr.split())
        #flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        recs_serial=e_db_serial.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van record="+str(recs_serial))
        if recs_serial[0][0] == None:
            flog.debug(inspect.stack()[0][3]+": fout bij lezen van tabel "+const.DB_SERIAL_TAB)
            return 0
        flog.debug(inspect.stack()[0][3]+": Tijd tussen oudste en jongste record is "\
        +str(abs(60-recs_serial[0][0]))+" seconden")
        return recs_serial[0][0]
    except Exception as e:
        flog.warning(inspect.stack()[0][3]+": e-serial db kan niet worden gelezen, fout: "+str(e))
        return 0

def saveExit(signum, frame):   
        signal.signal(signal.SIGINT, original_sigint)
        backupData()
        flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, data gekopieerd en gestopt.")
        sys.exit(0)

#-------------------------------
if __name__ == "__main__":

    try:
        os.umask( 0o002 )
        flog = logger.fileLogger( const.DIR_FILELOG + prgname + ".log", prgname )    
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
        sys.exit(1)
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT,  saveExit )
    Main()
