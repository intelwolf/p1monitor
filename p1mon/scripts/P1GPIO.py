#!/usr/bin/python3
import argparse
import apiconst
import base64
import const
import crypto3
import inspect
import json
import signal
import sys
import time 
import os

from sqldb import configDB, rtStatusDb, SqlDb1
from logger import fileLogger, logging
from util import setFile2user, getUtcTime
from gpio import gpioDigtalOutput
from datetime import datetime

prgname             = 'P1GPIO'
config_db           = configDB()
rt_status_db        = rtStatusDb()
e_db_serial         = SqlDb1()
gpioPowerSwitcher   = gpioDigtalOutput()
gpioTarifSwitcher   = gpioDigtalOutput()

powerswitcher_active                    = False
powerswitcher_last_action_utc_timestamp = 0
powerswitcher_forced_on                 = 0 

tarifwitcher_forced_on                  = False
tarifwitcher_is_active                  = False

# Status velden.
# timestamp process gestart                           DB status index =  99 

def Main(argv): 
    flog.info("Start van programma.")
   
    # open van status database      
    try:    
        rt_status_db.init( const.FILE_DB_STATUS, const.DB_STATUS_TAB )
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van config database      
    try:
        config_db.init( const.FILE_DB_CONFIG, const.DB_CONFIG_TAB )
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # open van seriele database
    try:
        e_db_serial.init(const.FILE_DB_E_FILENAME ,const.DB_SERIAL_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_E_FILENAME+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_SERIAL_TAB+" succesvol geopend.")

    # set proces gestart timestamp
    rt_status_db.timestamp( 99, flog )

    try:
        gpioPowerSwitcher.init( 85, config_db ,flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": GPIO pin voor tarief schakelaar niet te openen. " + str(e.args[0])  ) 
        sys.exit( 1 )

    try:
        gpioTarifSwitcher.init( 95, config_db ,flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": GPIO pin voor tarief schakelaar niet te openen. " + str(e.args[0])  ) 
        sys.exit( 1 )

    while True:
        #flog.setLevel( logging.DEBUG )
        powerSwitcher()
        tarifSwitcher()
        #flog.setLevel( logging.INFO )

        time.sleep( 15 )


# powerswitcher working
# when the average value for becoming active is reached the on state will be active
# when the average value for becoming deactived is reached the state will be deactivited
# on status can be read from status.db id 83 0 is inactive >0 is active. GPIO pin is active or inactive
# last switch timestamp is status.db id 84.
def powerSwitcher():
    global powerswitcher_active, powerswitcher_last_action_utc_timestamp, powerswitcher_forced_on
    
    try:
        #force powerswitcher force on (1) or (0) automatic.
        #powerswitcher_forced_on_read = 0
        _id, powerswitcher_forced_on_read, _label = config_db.strget( 87, flog )
        if int( powerswitcher_forced_on_read ) == 1:
            if powerswitcher_forced_on == 0:
                flog.info( inspect.stack()[0][3] + ": powerswitcher geforceerd aangezet." )
                powerswitcher_forced_on = 1
                rt_status_db.strset( 0, 83 , flog )
                rt_status_db.timestamp( 84, flog )
                gpioPowerSwitcher.gpioOn( True )
            flog.debug( inspect.stack()[0][3] + ": powerswitcher geforceerd aangezet." )
            return # no other actions needed or possible.
        else:
             if powerswitcher_forced_on == 1:
                flog.info( inspect.stack()[0][3] + ": powerswitcher geforceerd uitgezet." )
                powerswitcher_forced_on = 0
                gpioPowerSwitcher.gpioOn( False )
                rt_status_db.timestamp( 84, flog )
                rt_status_db.strset( 0, 83 , flog ) 


        #power switcher is active.
        _id, powerswitcher_is_on, _label = config_db.strget( 86, flog )
        if int(powerswitcher_is_on) == 0:
            flog.debug( inspect.stack()[0][3] + ": powerswitcher staat uit." )
            gpioPowerSwitcher.gpioOn( False ) # make sure we switch off the load when not active.
            powerswitcher_active = False
            powerswitcher_last_action_utc_timestamp = 0
            rt_status_db.strset( 0, 83 , flog ) 
            return

        #default values. as failsave.
        on_threshold_watt       = 1000
        off_threshold_watt      = 500
        on_threshold_minutes    = 2
        off_threshold_minutes   = 2
        on_minimum_time         = 0
        off_minimum_time        = 0
        
        # read config information.
        _id, on_threshold_watt,     _label = config_db.strget( 81,flog )
        _id, off_threshold_watt,    _label = config_db.strget( 82,flog )
        _id, on_threshold_minutes,  _label = config_db.strget( 83,flog )
        _id, off_threshold_minutes, _label = config_db.strget( 84,flog ) 
        _id, on_minimum_time,       _label = config_db.strget( 88,flog )
        _id, off_minimum_time,      _label = config_db.strget( 89,flog )

        flog.debug( inspect.stack()[0][3]+": on_threshold_watt=" + str(on_threshold_watt) + ' off_threshold_watt=' + str(off_threshold_watt) + " on_threshold_minutes=" + str(on_threshold_minutes) + " off_threshold_minutes=" + str(off_threshold_minutes) + " on_minimum_time=" + str(on_minimum_time) + " off_minimum_time=" + str(off_minimum_time) )

        #check for on hold time
        if (powerswitcher_active == True) and ( powerswitcher_last_action_utc_timestamp + ( int(on_minimum_time)  * 60 ) > getUtcTime() ):
            flog.debug( inspect.stack()[0][3]+": aan minimum tijd is nog geldig, geen actie, output blijft aan.")
            return

        if (powerswitcher_active == False ) and ( powerswitcher_last_action_utc_timestamp + ( int(off_minimum_time)  * 60 ) > getUtcTime() ):
            flog.debug( inspect.stack()[0][3]+": uit minimum tijd is nog geldig, geen actie, output blijft uit.")
            return

        if powerswitcher_active == False: 
            watt_producing = powerSwitcherSql( on_threshold_minutes )
            #watt_producing = 600
            if watt_producing == None:
                return
            if watt_producing >= int( on_threshold_watt ):
                powerswitcher_active = True
                gpioPowerSwitcher.gpioOn( True )
                powerswitcher_last_action_utc_timestamp = getUtcTime()
                rt_status_db.strset( watt_producing, 83, flog ) # watt value uses to activate the switcher
                rt_status_db.timestamp( 84, flog )
                flog.info( inspect.stack()[0][3]+": Ingeschakeld op een vermogen van " + str(watt_producing) + " watt." )
        else:
            watt_producing = powerSwitcherSql( off_threshold_minutes )
            if watt_producing == None:
                return
            if watt_producing <= int( off_threshold_watt ):
                powerswitcher_active = False
                gpioPowerSwitcher.gpioOn( False )
                powerswitcher_last_action_utc_timestamp = getUtcTime()
                rt_status_db.strset( 0, 83 , flog ) 
                rt_status_db.timestamp( 84, flog ) 
                flog.info( inspect.stack()[0][3]+": Uitgeschakeld op een vermogen van " + str(watt_producing) + " watt." )
    except Exception as e:
        flog.error( inspect.stack()[0][3]+": onverwachte fout " + str(e) )

def powerSwitcherSql( minute_value ):
    r = None
    try:
        sqlstr = "select round( avg( ACT_GELVR_KW_270 * 1000) ) from " + const.DB_SERIAL + " where timestamp > \
                datetime( (select max(timestamp) from " + const.DB_SERIAL + " ) , '-" + str(minute_value) + " minutes' );"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(powerSwitcher)=" + sqlstr )
        avg_rec=e_db_serial.select_rec( sqlstr )
        r = int(avg_rec[0][0])
        flog.debug( inspect.stack()[0][3] + ": waarde record" + str(avg_rec) )
    except Exception as e:
            flog.error( inspect.stack()[0][3]+": (powerSwitcher )" + str(e) )
    if r == None:
        flog.warning( inspect.stack()[0][3]+ ": PowerSwitcher sql query is mislukt." )
    return r

# tarif switcher 
# last switch timestamp is status.db id 89, status on=1,0=of on status id 88
# 1: check if forced is on and enable or disable GPIO.
# 2: check if user enabled or disabled the tarif switcher, GPIO to off when not selected.
# 3: check on the tarif mode, if not active GPIO to off
# 4: check if the timestamp is part of the two time windows's if not,  GPIO to off
def tarifSwitcher():
    global tarifwitcher_forced_on, tarifwitcher_is_active

    flog.debug( inspect.stack()[0][3] + ": Tarief switcher start" )
 
    try:
        #force powerswitcher force on (1) or (0) automatic.
        #powerswitcher_forced_on_read = 0
        _id, powerswitcher_forced_on_read, _label = config_db.strget( 92, flog )
        if int( powerswitcher_forced_on_read ) == 1:
            if tarifwitcher_forced_on == 0:
                flog.info( inspect.stack()[0][3] + ": tarief switcher geforceerd aangezet." )
                tarifwitcher_forced_on = 1
                rt_status_db.strset( 1, 89 , flog )
                rt_status_db.timestamp( 88, flog )
                gpioTarifSwitcher.gpioOn( True )
            flog.debug( inspect.stack()[0][3] + ": tarief switcher geforceerd aangezet." )
            return # no other actions needed or possible.
        else:
             if tarifwitcher_forced_on == 1:
                flog.info( inspect.stack()[0][3] + ": tarief switcher geforceerd uitgezet." )
                tarifwitcher_forced_on = 0
                gpioTarifSwitcher.gpioOn( False )
                rt_status_db.strset( 0, 89 , flog )
                rt_status_db.timestamp( 88, flog )

        #check if tarif switcher is active.
        _id, tarifswitcher_is_on, _label = config_db.strget( 90, flog )
        if int( tarifswitcher_is_on ) == 0:
            tarifwitcher_is_active = False
            flog.debug( inspect.stack()[0][3] + ": tarief switcher staat uit." )
            gpioTarifSwitcher.gpioOn( False ) # make sure we switch off the load when not active.
            rt_status_db.strset( 0, 89 , flog )
            #rt_status_db.timestamp( 88, flog )
            return
        flog.debug( inspect.stack()[0][3] + ": tarief switcher staat aan." )

        #check on tarif mode. 
        _id, tarif_mode_activ, _label, _security  = rt_status_db.strget( 85, flog )
        _id, tarif_mode_set,    _label = config_db.strget( 91, flog )
        if tarif_mode_activ.upper() != tarif_mode_set.upper():
            flog.debug( inspect.stack()[0][3] + ": huidige tarief " + tarif_mode_activ.upper() + " komt NIET overeen met ingestelde schakel tarief " + str(tarif_mode_set).upper() )
            gpioTarifSwitcher.gpioOn( False ) # make sure we switch off the load when not active.
            rt_status_db.strset( 0, 89 , flog )
            rt_status_db.timestamp( 88, flog )
            if tarifwitcher_is_active == True:
                flog.info( inspect.stack()[0][3] + ": tarief schakelaar is niet meer actief (uitgezet) op tarief wissel." )
            tarifwitcher_is_active = False
            return
        flog.debug( inspect.stack()[0][3] + ": huidige tarief " + tarif_mode_activ.upper() + " komt overeen met ingestelde schakel tarief "+ str(tarif_mode_set).upper() )
        
        flog.debug( inspect.stack()[0][3] + ": tijds windows 1 actief = " + str( checkTimeWindow( 93 ) ) )
        flog.debug( inspect.stack()[0][3] + ": tijds windows 2 actief = " + str( checkTimeWindow( 94 ) ) )

        if checkTimeWindow( 93 ) == True or checkTimeWindow( 94 ) == True:
            flog.debug( inspect.stack()[0][3] + ": tarifwitcher_is_active flag = " + str(tarifwitcher_is_active) )
            if tarifwitcher_is_active ==  False:
                tarifwitcher_is_active  = True
                gpioTarifSwitcher.gpioOn( True )
                rt_status_db.strset( 1, 89, flog )
                rt_status_db.timestamp( 88, flog )
                flog.info( inspect.stack()[0][3] + ": tarief schakelaar is actief (aangezet)." )
        else:
            if tarifwitcher_is_active ==  True:
                tarifwitcher_is_active  = False
                gpioTarifSwitcher.gpioOn( False )
                rt_status_db.strset( 0, 89 , flog )
                rt_status_db.timestamp( 88, flog )
                flog.info( inspect.stack()[0][3] + ": tarief schakelaar is niet meer actief (uitgezet)." )

    except Exception as e:
        flog.error( inspect.stack()[0][3]+": onverwachte fout " + str(e) )
    #return False

# When timestamp is in timewindow return True, else False
def checkTimeWindow( db_config_id ):

    # reading from database the timestring
    _id, raw_timestring , _label = config_db.strget( db_config_id , flog )
    flog.debug( inspect.stack()[0][3] + ": Raw timestring on id " + str( db_config_id ) + " is " + str( raw_timestring ) )
    try:
        p = raw_timestring.split( '.' )
        hh1 = int(p[0])
        mm1 = int(p[1])
        hh2 = int(p[2])
        mm2 = int(p[3])
        t1_in_min = ( int(p[0])*60 ) + int(p[1])
        t2_in_min = ( int(p[2])*60 ) + int(p[3])
        now = datetime.now()
        
        t_current = int((now.hour*60) + now.minute)
        # t_current = 1379 #DEBUG
        # check if time 1 < 2 
        flog.debug( inspect.stack()[0][3] + ": Decoded timestamp -> tijd 1 " + str( hh1 ) + ":" + str(mm1) + " tijd 2 " + str( hh2 ) + ":" + str(mm2) \
            + " t1 in min = " + str( t1_in_min ) + " t2 in min = " + str( t2_in_min ) + " huidige dag minuten = " + str(t_current) )
        #print ( date.today().weekday() )
        #print ( p[date.today().weekday() + 4] ) 
        if int( p[datetime.today().weekday() + 4] ) == 0:
            flog.debug( inspect.stack()[0][3] + ": Dag is niet actief in de timestamp." )
            return False
        flog.debug( inspect.stack()[0][3] + ": Dag komt overeen in de timestamp." )
        # timetamp t1 < t2
        if t1_in_min <= t2_in_min:
            flog.debug( inspect.stack()[0][3] + " check op t1 <= t2" )
            if t1_in_min <= t_current and t2_in_min >= t_current:
                flog.debug( inspect.stack()[0][3] + ": Huidige tijd ligt tussen t1 en t2 (t1 <= t2)" )
                return True
            flog.debug( inspect.stack()[0][3] + ": Huidige tijd ligt niet tussen t1 en t2 (t1 <= t2)" )    
        # timetamp t1 >= t2
        if t1_in_min >= t2_in_min:
            flog.debug( inspect.stack()[0][3] + " check op t1 >= t2" )
            if t_current >= t1_in_min:
                flog.debug( inspect.stack()[0][3] + ": Huidige tijd ligt tussen t1 en 00:00 (t1 >= t2)" )
                return True
            if t_current <= t2_in_min:
                flog.debug( inspect.stack()[0][3] + ": Huidige tijd ligt tussen  00:00 en t2 (t1 >= t2)" )
                return True
        
    except Exception as e:
        flog.error( inspect.stack()[0][3]+": onverwachte fout " + str(e) )
    return False

def saveExit(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    gpioTarifSwitcher.close()
    gpioPowerSwitcher.close()
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    try:
        logfile = const.DIR_FILELOG + prgname + ".log" 
        setFile2user( logfile,'p1mon' )
        flog = fileLogger( logfile,prgname )    
        #### aanpassen bij productie
        flog.setLevel( logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str( e.args[0] ) )
        sys.exit(10) #  error: no logging check file rights

    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])