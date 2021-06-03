#!/usr/bin/python3
import const
import inspect
import signal
import shutil
import os
import sys
import time

from sqldb import  rtStatusDb,configDB,SqlDb1,SqlDb2,SqlDb3,SqlDb4,financieelDb,WatermeterDBV2
from logger import fileLogger,logging
from util import fileExist, setFile2user, daysPerMonth,isMod, fileChanged, mkLocalTimeString, getUtcTime
from datetime import datetime, timedelta
#from gpiozero import LED
from gpio import gpioDigtalOutput
from datetime import date

prgname = 'P1Db'

rt_status_db          = rtStatusDb()
config_db             = configDB()

e_db_serial           = SqlDb1()
e_db_history_min      = SqlDb2()
e_db_history_uur      = SqlDb3()
e_db_history_dag      = SqlDb4()
e_db_history_maand    = SqlDb4()
e_db_history_jaar     = SqlDb4()
e_db_financieel_dag   = financieelDb()
e_db_financieel_maand = financieelDb()
e_db_financieel_jaar  = financieelDb()
watermeter_db         = WatermeterDBV2()

#watermeter_db_uur     = WatermeterDB()
#watermeter_db_dag     = WatermeterDB()
#watermeter_db_maand   = WatermeterDB()
#watermeter_db_jaar    = WatermeterDB()


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
#powerswitcher_active    = False
#powerswitcher_last_action_utc_timestamp = 0
#powerswitcher_forced_on = 0 

#tarifwitcher_forced_on  = False
#tarifwitcher_is_active  = False

#gpioPowerSwitcher       = gpioDigtalOutput()
#gpioTarifSwitcher       = gpioDigtalOutput()

def Main():
    global timestamp
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
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(3)." + const.FILE_DB_WATERMETERV2 + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

    # defrag databases
    e_db_history_min.defrag()
    flog.info(inspect.stack()[0][3]+": database bestand "+const.FILE_DB_E_HISTORIE+" gedefragmenteerd.")
    e_db_financieel_dag.defrag()
    flog.info(inspect.stack()[0][3]+": database bestand "+const.FILE_DB_FINANCIEEL+" gedefragmenteerd.")

    #flog.setLevel( logging.DEBUG )
    #flog.consoleOutputOn( True )

    setFileFlags()

    flog.info(inspect.stack()[0][3]+": hoofd programma loop gestart.")
    rt_status_db.timestamp(6,flog)
    updateWeaterData()
    backupData()
    
    #print( getCpuInfo() )
    #sys.exit(0)
    #print "###### ->day =" + str( floatX3( float( datetime.now().timetuple().tm_yday)/365 )*100) 

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
            updateDbDayMoney()
            updateDbMonthMoney()
            updateDbYearMoney() #TODO

            #if isMod(timestamp,1) == True: # only once per min to prevent load.
            #    powerSwitcher()
            #    tarifSwitcher()
                
            if isMod(timestamp,15) == True:
                updateWeaterData()
                #ePrediction()
                backupData()
                cleanDb()
                #pauze_tijd_hoofdloop=11
        
            #flog.setLevel(logging.INFO)

        else: # niet aanpassen!
            pauze_tijd_hoofdloop = abs(60-secswaiting)/2
            if pauze_tijd_hoofdloop < 10:
                pauze_tijd_hoofdloop = 5
        flog.debug(inspect.stack()[0][3]+": pauze_tijd_hoofdloop="+str(pauze_tijd_hoofdloop))
        time.sleep(pauze_tijd_hoofdloop)
        #sys.exit(1)

# functions 

def updateWeaterData():
    #flog.setLevel(logging.DEBUG)
    #flog.consoleOutputOn(True) 
    try:
        # check if API key is set.
        sqlstr = "select id, parameter from "+const.DB_CONFIG_TAB+" where id=13"
        sqlstr=" ".join(sqlstr.split())
        #flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr);
        config=config_db.select_rec(sqlstr)    
        #flog.debug(inspect.stack()[0][3]+": waarde config record"+str(config))
        if len(config[0][1]) > 31: #valid API key, process.
            os.system('/p1mon/scripts/P1Weather.py')
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(config API key)"+str(e))
        return    
    #flog.setLevel(logging.INFO)
    #flog.consoleOutputOn(False) 

def updateGas():
    
    timestamp_dag = timestamp[0:10]
    timestamp_yesterday    = str(datetime.strptime(timestamp,"%Y-%m-%d %H:%M") - timedelta(minutes=1440))[0:10]
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
    
def updateDbYearMoney():
    #flog.setLevel( logging.DEBUG )
    #flog.consoleOutputOn( True )
    try:
        sqlstr = "select sum(verbr_p), sum(verbr_d), sum(gelvr_p), sum(gelvr_d) ,sum(gelvr_gas), sum(verbr_water) from "+\
        const.DB_FINANCIEEL_MAAND_TAB+" where substr(timestamp,1,4) = '"+timestamp[0:4]+"'"   
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec=e_db_financieel_maand.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van maandkosten record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

    verbr_p=verbr_d=gelvr_p=gelvr_d=verbr_gas=verbr_water=0
    if rec[0][0] != None:
        verbr_p = rec[0][0]
    if rec[0][1] != None:
        verbr_d = rec[0][1]
    if rec[0][2] != None:
        gelvr_p = rec[0][2]
    if rec[0][3] != None:
        gelvr_d = rec[0][3]
    if rec[0][4] != None:
        verbr_gas = rec[0][4]
    if rec[0][5] != None:
        verbr_water = rec[0][5] 

    flog.debug(inspect.stack()[0][3]+": kosten verbruik piek zijn " + str(verbr_p) )
    flog.debug(inspect.stack()[0][3]+": kosten verbruik dal zijn "  + str(verbr_d) )
    flog.debug(inspect.stack()[0][3]+": opbrengsten piek zijn "     + str(gelvr_p) )
    flog.debug(inspect.stack()[0][3]+": opbrengsten dal zijn "      + str(gelvr_d) )
    flog.debug(inspect.stack()[0][3]+": kosten gas zijn "           + str(verbr_gas) )
    flog.debug(inspect.stack()[0][3]+": kosten water zijn "         + str(verbr_water) )

    #update record
    try:
        sqlstr = "insert or replace into "+const.DB_FINANCIEEL_JAAR_TAB+" values ('"\
        +timestamp[0:4]+"-01-01 00:00:00',"\
        +str(verbr_p)+","\
        +str(verbr_d)+","\
        +str(gelvr_p)+","\
        +str(gelvr_d)+","\
        +str(verbr_gas)+","\
        +str(verbr_water)+")"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
        e_db_financieel_jaar.insert_rec(sqlstr)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e))

    #flog.setLevel( logging.INFO )

def updateDbMonthMoney():
    #flog.setLevel( logging.DEBUG )
    #flog.consoleOutputOn( True )
    try:
        sqlstr = "select sum(verbr_p), sum(verbr_d), sum(gelvr_p), sum(gelvr_d) ,sum(gelvr_gas), sum(verbr_water) from "+\
        const.DB_FINANCIEEL_DAG_TAB+" where substr(timestamp,1,7) = '"+timestamp[0:7]+"'"   
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec=e_db_financieel_dag.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van dagkosten record"+str(rec))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))

    verbr_p=verbr_d=gelvr_p=gelvr_d=verbr_gas=verbr_water=0

    if rec[0][0] != None:
        verbr_p = rec[0][0]
    if rec[0][1] != None:
        verbr_d = rec[0][1]
    if rec[0][2] != None:
        gelvr_p = rec[0][2]
    if rec[0][3] != None:
        gelvr_d = rec[0][3]
    if rec[0][4] != None:
        verbr_gas = rec[0][4]
    if rec[0][5] != None:
        verbr_water = rec[0][5]    

    flog.debug(inspect.stack()[0][3]+": kosten verbruik piek zijn " + str(verbr_p) )
    flog.debug(inspect.stack()[0][3]+": kosten verbruik dal zijn "  + str(verbr_d) )
    flog.debug(inspect.stack()[0][3]+": opbrengsten piek zijn "     + str(gelvr_p) )
    flog.debug(inspect.stack()[0][3]+": opbrengsten dal zijn "      + str(gelvr_d) )
    flog.debug(inspect.stack()[0][3]+": kosten gas zijn "           + str(verbr_gas) )
    flog.debug(inspect.stack()[0][3]+": kosten water zijn "         + str(verbr_water) )
    
    #update record
    try:
        sqlstr = "insert or replace into "+const.DB_FINANCIEEL_MAAND_TAB+" values ('"\
        +timestamp[0:7]+"-01 00:00:00',"\
        +str(verbr_p)+","\
        +str(verbr_d)+","\
        +str(gelvr_p)+","\
        +str(gelvr_d)+","\
        +str(verbr_gas)+","\
        +str(verbr_water)+")"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
        e_db_financieel_maand.insert_rec(sqlstr)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e))

    #flog.setLevel( logging.INFO )

def updateDbDayMoney():
    timestamp_dag = timestamp[0:10]
   
    # tariefcode P
    try:
        sqlstr = "select sum(VERBR_KWH_X), sum(GELVR_KWH_X) from "+\
        const.DB_HISTORIE_MIN_TAB+" where substr(timestamp,1,10) = '"+\
        timestamp_dag+"' and tariefcode = 'P'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        rec_p=e_db_history_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van piektarief record"+str(rec_p))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))
    # tariefcode D
    try:
        sqlstr = "select sum(VERBR_KWH_X), sum(GELVR_KWH_X) from "+\
        const.DB_HISTORIE_MIN_TAB+" where substr(timestamp,1,10) = '"+\
        timestamp_dag+"' and tariefcode = 'D'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(2)="+sqlstr)
        rec_d=e_db_history_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van daltarief record"+str(rec_d))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(2)"+str(e))
    
    
    #select verbr_GAS_X from e_history_dag where timestamp = '2017-06-18 00:00:00'
    try:
        sqlstr = "select verbr_GAS_X from "+\
        const.DB_HISTORIE_DAG_TAB+\
        " where substr(timestamp,1,10) = '"+\
        timestamp_dag+"'"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(3)="+sqlstr)
        rec_gas=e_db_history_uur.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van gas record"+str(rec_gas))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(3)"+str(e))

    #flog.setLevel( logging.DEBUG )
    #flog.consoleOutputOn( True )

    try:
        verbr_per_timeunit = 0.0
        sql = "select sum(VERBR_PER_TIMEUNIT) from " + const.DB_WATERMETERV2_TAB + " where TIMEPERIOD_ID=13 and timestamp = '" + timestamp_dag + " 00:00:00'"
        #print ( "#0 = ", sql )

        verbr_per_timeunit_tmp = watermeter_db.select_rec( sql )[0][0] 

        if verbr_per_timeunit_tmp == None:
            verbr_per_timeunit = 0 # fix to prevent errors when water measuring is not used.
        else:
            verbr_per_timeunit = float( verbr_per_timeunit_tmp )

        #print ( '#1 = ', verbr_per_timeunit )
        #if  verbr_per_timeunit == None:
        #    verbr_per_timeunit = 0 # fix to prevent errors when water measuring is not used.

        verbr_per_timeunit = verbr_per_timeunit/1000 # convert liter to m3 because cost is done per m3
        flog.debug(inspect.stack()[0][3]+": liters water voor vandaag " + str( verbr_per_timeunit) )
    except Exception as e:
        flog.error( inspect.stack()[0][3]+": uren water verbruik error " + str(e) )

    # tarieven
    try:
        sqlstr = "select id, parameter from "+const.DB_CONFIG_TAB+\
        " where id <=5 or id=15 or id=16 or id=103 or id=104 order by id asc"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(4)="+sqlstr)
        rec_config=config_db.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": waarde van tarieven record"+str(rec_config))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(4)"+str(e))


    # vastrecht per dag
    e_vastrecht = float(rec_config[5][1])/daysPerMonth(timestamp_dag)
    flog.debug(inspect.stack()[0][3]+": Elektriciteit vastrecht per dag is "+str(e_vastrecht)+" per maand is "+rec_config[5][1])
    g_vastrecht = float(rec_config[7][1])/daysPerMonth(timestamp_dag)
    flog.debug(inspect.stack()[0][3]+": Gas vastrecht per dag is "+str(g_vastrecht)+" per maand is "+rec_config[7][1])
    w_vastrecht = float(rec_config[8][1])/daysPerMonth(timestamp_dag)
    flog.debug(inspect.stack()[0][3]+": Water vastrecht per dag is "+str(w_vastrecht)+" per maand is "+rec_config[8][1])

    try:
        verbr_p = (rec_p[0][0]*float(rec_config[2][1]))
    except Exception as e:
        verbr_p = 0
    try:
        verbr_d = (rec_d[0][0]*float(rec_config[1][1]))+e_vastrecht
    except Exception as e:
        verbr_d = 0
    try:     
        gelvr_p = rec_p[0][1]*float(rec_config[4][1])
    except Exception as e:
        gelvr_p = 0
    try:
        gelvr_d =rec_d[0][1]*float(rec_config[3][1])
    except Exception as e:
        gelvr_d = 0
    try:
        verbr_gas =(rec_gas[0][0]*float(rec_config[6][1]))+g_vastrecht
    except Exception as e:
        verbr_gas = 0
    try:
        verbr_water = ( verbr_per_timeunit * float(rec_config[9][1]) ) + w_vastrecht
    except Exception as e:
        print(str(e))
        verbr_water = 0
    
    flog.debug(inspect.stack()[0][3]+": kosten verbruik piek zijn " + str(verbr_p)   )
    flog.debug(inspect.stack()[0][3]+": kosten verbruik dal zijn "  + str(verbr_d)   )
    flog.debug(inspect.stack()[0][3]+": opbrengsten piek zijn "     + str(gelvr_p)   )
    flog.debug(inspect.stack()[0][3]+": opbrengsten dal zijn "      + str(gelvr_d)   )
    flog.debug(inspect.stack()[0][3]+": kosten gas zijn "           + str(verbr_gas) )
    flog.debug(inspect.stack()[0][3]+": kosten water zijn "         + str(verbr_water) )
    
    #update record
    try:
        sqlstr = "insert or replace into "+\
        const.DB_FINANCIEEL_DAG_TAB+" values ('"\
        +timestamp[0:10]+" 00:00:00',"\
        +str(verbr_p)+","\
        +str(verbr_d)+","\
        +str(gelvr_p)+","\
        +str(gelvr_d)+","\
        +str(verbr_gas)+","\
        +str(verbr_water)+")"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(5)="+sqlstr)
        e_db_financieel_dag.insert_rec(sqlstr)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": sql error(5)"+str(e))

    #flog.setLevel( logging.INFO )

def setFileFlags():
    setFile2user(const.FILE_DB_E_FILENAME,'p1mon')
    setFile2user(const.FILE_DB_E_HISTORIE,'p1mon')
    setFile2user(const.FILE_DB_CONFIG,'p1mon')
    setFile2user(const.FILE_DB_STATUS,'p1mon')
    setFile2user(const.FILE_DB_FINANCIEEL,'p1mon')
    setFile2user(const.FILE_DB_WEATHER,'p1mon')
    setFile2user(const.FILE_DB_WEATHER_HISTORIE,'p1mon')
    setFile2user(const.FILE_DB_TEMPERATUUR_FILENAME,'p1mon')
    setFile2user(const.FILE_DB_WATERMETER,'p1mon')

    dummy,tail = os.path.split(const.FILE_DB_E_FILENAME)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    dummy,tail = os.path.split(const.FILE_DB_E_HISTORIE)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    dummy,tail = os.path.split(const.FILE_DB_CONFIG)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    dummy,tail = os.path.split(const.FILE_DB_STATUS)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    dummy,tail = os.path.split(const.FILE_DB_FINANCIEEL)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    dummy,tail = os.path.split(const.FILE_DB_WEATHER)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    dummy,tail = os.path.split(const.FILE_DB_WEATHER_HISTORIE)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon') 
    dummy,tail = os.path.split(const.FILE_DB_TEMPERATUUR_FILENAME)
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    dummy,tail = os.path.split( const.FILE_DB_WATERMETERV2 )
    setFile2user(const.DIR_FILEDISK+tail,'p1mon')
    
def cleanDb():
    timestr=mkLocalTimeString() 
    # minuten records verwijderen
    sql_del_str = "delete from "+const.DB_HISTORIE_MIN_TAB+" where timestamp <  '"+\
    str(datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - timedelta(days=31))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql="+sql_del_str)
        e_db_history_min.del_rec(sql_del_str)     
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen min. recs,delete gefaald. Melding="+str(e.args[0]))

    # uur records verwijderen
    sql_del_str = "delete from "+const.DB_HISTORIE_UUR_TAB+" where timestamp <  '"+\
    str(datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - timedelta(days=1096))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql="+sql_del_str)
        e_db_history_uur.del_rec(sql_del_str)     
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen uur recs,delete gefaald. Melding="+str(e.args[0]))

    # dagen records verwijderen
    sql_del_str = "delete from "+const.DB_HISTORIE_DAG_TAB+" where timestamp <  '"+\
    str(datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - timedelta(days=1096))+"'"
    try:
        flog.debug(inspect.stack()[0][3]+": sql="+sql_del_str)
        e_db_history_dag.del_rec(sql_del_str)     
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen dag recs,delete gefaald. Melding="+str(e.args[0]))

def saveExit(signum, frame):   
        signal.signal(signal.SIGINT, original_sigint)
        backupData()
        flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, data gekopieerd en gestopt.")
        sys.exit(0)

def backupFile(filename):
    try:
        file_sec_delta = fileChanged(filename ,const.DIR_FILEDISK)
        if file_sec_delta > 0 or file_sec_delta== -1:     
            shutil.copy2(filename, const.DIR_FILEDISK)
            flog.info(inspect.stack()[0][3]+": "+filename+" naar "+const.DIR_FILEDISK+" gekopieerd.")
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": data backup "+filename+" Fout: "+str(e))

def backupData():
    #setFileFlags()
    flog.debug(inspect.stack()[0][3]+": Gestart")
    os.system("/p1mon/scripts/P1DbCopy.py --allcopy2disk --forcecopy")
    rt_status_db.timestamp(29,flog)
    flog.debug(inspect.stack()[0][3]+": Gereed")

def DiskRestore():
    os.system("/p1mon/scripts/P1DbCopy.py --allcopy2ram")        

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
        sqlstr = "select min(timestamp) from "+const.DB_SERIAL_TAB+" where record_verwerkt=0"
        rec_serial=e_db_serial.select_rec(sqlstr)
        timestamp            = str(rec_serial[0][0])[0:16]
        timestamp_min_one    = str(datetime.strptime(timestamp,"%Y-%m-%d %H:%M") - timedelta(minutes=1))[0:16]
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
        flog.warning(inspect.stack()[0][3]+": geen vorige record gevonden voor minuut ="+timestamp_min_one)

    # failsafe verbruik kan nooit negatief zijn
    if VERBR_KWH_X < 0:
        VERBR_KWH_X = 0
    if GELVR_KWH_X <0:
        GELVR_KWH_X = 0

    flog.debug(inspect.stack()[0][3]+": [*]verbr_kw sinds vorige min ="+str(VERBR_KWH_X))
    flog.debug(inspect.stack()[0][3]+": [*]gelvr_kw sinds vorige min ="+str(GELVR_KWH_X))

    try:
        sqlstr = "update "+const.DB_SERIAL_TAB+\
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
        sqlstr = "select strftime('%s',max(timestamp)) - strftime('%s',min(timestamp)) from "+const.DB_SERIAL_TAB+" where record_verwerkt=0"
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

#-------------------------------
if __name__ == "__main__":

    try:
        os.umask( 0o002 )
        flog = fileLogger( const.DIR_FILELOG + prgname + ".log", prgname )    
        #### aanpassen bij productie
        flog.setLevel( logging.INFO )
        flog.consoleOutputOn( True ) 
    except Exception as e:
        print ("critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
        sys.exit(1)
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT,  saveExit)
    Main()       
