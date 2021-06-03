#!/usr/bin/python3
import sys
import serial
import time
import const
import apiconst
import collections
import inspect
import json
import signal
import string
import os
import psutil
import PyCRC
import random
import shutil
import systemid
import util
import cpuinfo
import subprocess

from sqldb import SqlDb1, rtStatusDb, configDB, temperatureDB, WatermeterDBV2, PhaseDB
from logger import logging,fileLogger
from util import fileExist,setFile2user,getUtcTime,cleanDigitStr,alwaysPlus,mkLocalTimeString,isMod
from datetime import datetime, timedelta
from PyCRC.CRC16 import CRC16
from systemid import getSystemId
from cpuinfo import getCpuInfo
from os import umask

temperature_db     = temperatureDB()
e_db_serial        = SqlDb1()
rt_status_db       = rtStatusDb()
config_db          = configDB()
#watermeter_db_dag  = WatermeterDB()
watermeter_db      = WatermeterDBV2()
fase_db            = PhaseDB()

#GasStructure = collections.namedtuple('gastructure','previous_gas_value, previous_timestamp, current_gas_value, current_timestamp')

# codering meter standen Nederland. 
# 1.8.1 Meterstand dal/nacht voor verbruikte energie
# 1.8.2 Meterstand piek/dag voor verbruikte energie
# 2.8.1 Meterstand dal/nacht voor teruggeleverde energie
# 2.8.2 Meterstand piek/dag voor teruggeleverde energie

verbrk_kwh_181      = const.NOT_SET 
verbrk_kwh_182      = const.NOT_SET
gelvr_kwh_281       = const.NOT_SET
gelvr_kwh_282       = const.NOT_SET
act_verbr_kw_170    = const.NOT_SET
act_gelvr_kw_270    = const.NOT_SET
gas_verbr_m3_2421   = const.NOT_SET

# Gas per m3
g2h_previous_gas_value 	= const.NOT_SET 
g2h_previous_timestamp 	= const.NOT_SET

temperature_in          = const.NOT_SET
temperature_out         = const.NOT_SET
watermeters_count_total = const.NOT_SET

tarief_code                 = ''
prgname                     = 'P1SerReader'
daytime_start_str           = ''
daytime_end_str             = ''
serial_buffer               = []
dev_dummy_gas_value         = 0
gas_present_in_serial_data  = False 
timestamp_last_insert       = 0
timestamp_last_gas_update   = 0
p1_record_is_ok             = 1
gas_record_prefix_number    = '1'
p1_crc_check_is_on          = True
system_id = systemid.getSystemId()
# 0  NL verwerking van E velden 
# 1: BE verwerking van de E velden 181/182 en 281/282 geinverteerde hoog/laag waarde. 0-0:96.14.0 tarief is ook ewijzigd. 
day_night_mode = 0 
# list of serial devices tried to use
ser_devices_list = [ "/dev/ttyUSB0" , "/dev/ttyUSB1" ]

#DEBUG
DUMMY_3PHASE_DATA      = False  ######### DEZE OP FALSE ZETTEN BIJ PRODUCTIE CODE!!!!

# 1 van deze op true zetten voor debug werkzaamheden, er mag maar 1 op true staan
DUMMY_GAS_MODE_2421    = False ######### DEZE OP FALSE ZETTEN BIJ PRODUCTIE CODE!!!!
DUMMY_GAS_MODE_2430    = False ######### DEZE OP FALSE ZETTEN BIJ PRODUCTIE CODE!!!!
DUMMY_GAS_MODE_2423    = False ######### DEZE OP FALSE ZETTEN BIJ PRODUCTIE CODE!!!!

DUMMY_GAS_TIME_ELAPSED = 300 # sec. die verstreken moet zijn voor volgend gas record in dummy mode.

#Set COM port config
ser1 = serial.Serial()
#ser1.baudrate = 9600
#ser1.bytesize=serial.SEVENBITS
#ser1.parity=serial.PARITY_EVEN
#ser1.stopbits=serial.STOPBITS_ONE
# version 1.3.0 changed to te most used settings
ser1.baudrate = 115200
ser1.bytesize=8
ser1.parity="N"
ser1.stopbits=1

ser1.xonxoff = 0 # changed from version 0.9.2 onwards
ser1.rtscts = 0 
ser1.timeout = 1 
ser1.port=ser_devices_list[0]

phase_db_record = {
    'timestamp'          : "",
    'consumption_L1_kW'  : 0, 
    'consumption_L2_kW'  : 0,
    'consumption_L3_kW'  : 0,
    'production_L1_kW'   : 0,
    'production_L2_kW'   : 0,
    'production_L3_kW'   : 0,
    'L1_V'               : 0,
    'L2_V'               : 0,
    'L3_V'               : 0,
    'L1_A'               : 0,
    'L2_A'               : 0,
    'L3_A'               : 0,
}

 # Data structure for remote services
json_data  = {
    apiconst.JSON_TS_LCL                : '',               # local time in format yyyy-mm-dd hh:mm:ss mkLocalTimeString()
    apiconst.JSON_TS_LCL_UTC            : '',               # utc timestamp getUtcTime()
    apiconst.JSON_API_API_STTS          : 'production',     # options are production=ok, test, deprecated = will be removed in future version.
    apiconst.JSON_API_VRSN              : const.API_BASIC_VERSION, # id /number will be used in file name.
    apiconst.JSON_API_CNSMPTN_KWH_L     : '',               # consumption of KWH during low (dal) period.
    apiconst.JSON_API_CNSMPTN_KWH_H     : '',               # consumption of KWH during high (piek) period.
    apiconst.JSON_API_PRDCTN_KWH_L      : '',               # production of KWH during low (dal) period.
    apiconst.JSON_API_PRDCTN_KWH_H      : '',               # production of KWH during high (piek) period.
    apiconst.JSON_API_TRFCD             : '',               # peak or low period.
    apiconst.JSON_API_CNSMPTN_KW        : '',               # the consumption in Watt now.
    apiconst.JSON_API_PRDCTN_KW         : '',               # the production in Watt now.
    apiconst.JSON_API_CNSMPTN_GAS_M3    : '',               # consumption of gas in M3.
    apiconst.JSON_API_SFTWR_VRSN        : const.P1_VERSIE,  # software version of P1 software
    apiconst.JSON_API_SYSTM_ID          : system_id,        # system ID that is hardware specfic and unique
    apiconst.JSON_API_RM_TMPRTR_IN      : '',               # room temperature input
    apiconst.JSON_API_RM_TMPRTR_OUT     : '',               # room temperature output
    apiconst.JSON_API_WM_CNSMPTN_LTR_M3 : ''                # consumption of water in M3.
}

def clearPhaseDictionary():
    global phase_db_record
    for key in phase_db_record:
        phase_db_record[key] = const.NOT_SET 

def updateJsonData():
    global json_data
    global verbrk_kwh_181, verbrk_kwh_182, gelvr_kwh_281, gelvr_kwh_282, \
           tarief_code, act_verbr_kw_170, act_gelvr_kw_270, gas_verbr_m3_2421

   #convert dutch tarif code to English Dal = Low, Peak = High 
    if tarief_code == 'P': 
        tarief_code = 'HIGH'
    else: 
        tarief_code = "LOW" # there are only two options (D/P)

    json_data[ apiconst.JSON_TS_LCL ]                   = str(util.mkLocalTimeString())
    json_data[ apiconst.JSON_TS_LCL_UTC ]               = util.getUtcTime()
    json_data[ apiconst.JSON_API_CNSMPTN_KWH_L ]        = float( verbrk_kwh_181 )
    json_data[ apiconst.JSON_API_CNSMPTN_KWH_H ]        = float( verbrk_kwh_182 )
    json_data[ apiconst.JSON_API_PRDCTN_KWH_L ]         = float( gelvr_kwh_281 )
    json_data[ apiconst.JSON_API_PRDCTN_KWH_H ]         = float( gelvr_kwh_282 )
    json_data[ apiconst.JSON_API_TRFCD ]                = str( tarief_code )
    json_data[ apiconst.JSON_API_CNSMPTN_KW ]           = float( act_verbr_kw_170 )
    json_data[ apiconst.JSON_API_PRDCTN_KW ]            = float( act_gelvr_kw_270 )
    json_data[ apiconst.JSON_API_CNSMPTN_GAS_M3 ]       = float( gas_verbr_m3_2421 )
    json_data[ apiconst.JSON_API_RM_TMPRTR_IN ]         = float( temperature_in )
    json_data[ apiconst.JSON_API_RM_TMPRTR_OUT ]        = float( temperature_out )
    json_data[ apiconst.JSON_API_WM_CNSMPTN_LTR_M3 ]    = float( watermeters_count_total )

def main_prod():
    global ser1
    global serial_buffer
    global dev_dummy_gas_value
    global p1_record_is_ok

    clearPhaseDictionary()
    
    last_crc_check_timestamp = 0
    crc_error_cnt = 0

    flog.info("Start van programma.") 

    DiskRestore()

    # open van seriele database      
    try:
        e_db_serial.init(const.FILE_DB_E_FILENAME ,const.DB_SERIAL_TAB)        
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+" database niet te openen(1)."+const.FILE_DB_E_FILENAME+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel: "+const.DB_SERIAL_TAB+" succesvol geopend.")

    # defrag van database
    e_db_serial.defrag()
    flog.info(inspect.stack()[0][3]+": database bestand "+const.DB_SERIAL_TAB+" gedefragmenteerd.")

    # open van status database      
    try:    
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)     
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
        sys.exit(1)

    flog.info(inspect.stack()[0][3]+": database tabel: "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van config database
    try:    
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(3)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
        sys.exit(1)

    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")

    # open van temperatuur database
    try:
        temperature_db.init(const.FILE_DB_TEMPERATUUR_FILENAME ,const.DB_TEMPERATUUR_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_TEMPERATUUR_FILENAME+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_TEMPERATUUR_TAB +" succesvol geopend.")

    """
    # open van watermeter stand
    try:
        watermeter_db_dag.init( const.FILE_DB_WATERMETER ,const.DB_WATERMETER_DAG_TAB, flog )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)." + const.FILE_DB_WATERMETER + ") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_WATERMETER_DAG_TAB  + " succesvol geopend." )
    """

    # open van watermeter database
    try:    
        watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(3)." + const.FILE_DB_WATERMETERV2 + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

    # open van fase database
    try:
        fase_db.init( const.FILE_DB_PHASEINFORMATION ,const.DB_FASE_REALTIME_TAB )
        fase_db.defrag()
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+" database niet te openen(1)." + const.FILE_DB_PHASEINFORMATION + ") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel: " + const.DB_FASE_REALTIME_TAB + " succesvol geopend.")

    #setFileFlags()
    backupData()

    while checkSerial() == False:
        flog.critical(inspect.stack()[0][3]+": seriele poort niet gevonden, is de kabel aangesloten?" )
        time.sleep(10)

    # reset gas per uur waarde als we starten.
    rt_status_db.strset("0", 50, flog)

    rt_status_db.timestamp(5,flog)
    #read serial settings from status DB
    serCheckCnt = 0
    checkDbConfigSettings()
    checkGasTelgramPrefix()
    flog.info(inspect.stack()[0][3]+": P1 poort instelling baudrate=" + str(ser1.baudrate)+" bytesize=" +str(ser1.bytesize)+" pariteit="+str(ser1.parity)+" stopbits="+str(ser1.stopbits))
    #serOpen(ser1)
    #ser1.flushInput()

    # read GAS value from status database
    if DUMMY_GAS_MODE_2421 == True or DUMMY_GAS_MODE_2423 == True or DUMMY_GAS_MODE_2430 == True:
        sqlstr = "select status from "+const.DB_STATUS_TAB +" where id =43"
        gas_dummy_val_rec=rt_status_db.select_rec(sqlstr)
        dev_dummy_gas_value=float(gas_dummy_val_rec[0][0])
        print("DUMMY GAS STAAT AAN IS DIT CORRECT?\r")
        flog.warning(inspect.stack()[0][3]+" #############################################")
        flog.warning(inspect.stack()[0][3]+": Dummy gas waarde staat aan met een interval van "+str(DUMMY_GAS_TIME_ELAPSED)+" seconden. Zet uit voor productie!")
        flog.warning(inspect.stack()[0][3]+" #### DUMMY GAS STAAT AAN IS DIT CORRECT? ####")
    else:
        try:
            rt_status_db.strset(0,43,flog) # reset dummy gas value
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": Melding="+str(e.args[0]))

    # check for dummy 3Phase data
    if DUMMY_3PHASE_DATA == True:
        print("DUMMY 3 FASE DATA STAAT AAN IS DIT CORRECT?\r")
        flog.warning(inspect.stack()[0][3]+" #############################################")
        flog.warning(inspect.stack()[0][3]+": Dummy 3 fase waarde staat aan. Zet uit voor productie!")
        flog.warning(inspect.stack()[0][3]+" #### DUMMY 3 FASE STAAT AAN IS DIT CORRECT? ####")


    # read crc check settings from config
    checkCRCsettings()

    #print ( 'delta 1 ='+str(abs(timestamp_last_insert - getUtcTime())) )
    while True:
        try:
            #print ('ser1.In_waiting='+str(ser1.in_waiting))
            if ser1.in_waiting > 1:

                try:
                    line = ser1.readline().decode('utf-8')
                    #flog.debug(inspect.stack()[0][3]+": line = " + line +" length=" + str(len(line))) 

                    #line = filter(lambda x: x in string.printable, line_raw ).rstrip()[0:1024]
                    #flog.debug(inspect.stack()[0][3]+": line filtered = " + str(line_raw ) ) 
                except:
                    flog.warning(inspect.stack()[0][3]+": lezen van serieele poort mislukt.")

                serial_buffer.append( line )
                #flog.debug(inspect.stack()[0][3]+": [** V2.0]serial buffer bytes waiting = " + str(ser1.inWaiting()) ) 

                #the benthouse BUG has 78 lines
                if len(serial_buffer) > 250: # normale size less then a 100 lines
                    flog.warning(inspect.stack()[0][3]+": serieele buffer te groot, gewist! Buffer lengte was "+str(len(serial_buffer)))
                    del serial_buffer[:]

                #print  ( serial_buffer )
                #print ( "[*]len="+str(len(serial_buffer)) )

                if line[:1] == '!':
                    #flog.debug(inspect.stack()[0][3]+": serial buffer "+str(serial_buffer))	

                    if DUMMY_3PHASE_DATA == True:
                        phase3StubInstert( line )

                    #flog.setLevel(logging.DEBUG)
                    if DUMMY_GAS_MODE_2421 == True or DUMMY_GAS_MODE_2423 == True or DUMMY_GAS_MODE_2430 == True:
                        gasStubInstert(line)
                    #print ( serial_buffer ##DEBUG )
                    #flog.setLevel(logging.INFO)

                    #print('delta(1)='+str( abs(timestamp_last_insert - getUtcTime())))
                    # rate limitingen of inserts, some smart meters send more then every 10 sec. a telegram.
                    if abs(timestamp_last_insert - getUtcTime()) < 9: # 9 or 10 sec interval is ok.
                        #flog.debug("Te snel een nieuw telegram ontvangen. genegeerd.")
                        del serial_buffer[:]
                        #print('delta(2)='+str( abs(timestamp_last_insert - getUtcTime())))
                        continue

                    #serial_buffer[-1] = "!0F9B"  #DEBUG
                    #print ( "[*] p1 crc check = " + str(p1_crc_check_is_on) )

                    # check for meters that supply a crc value.
                    if len(serial_buffer[ len(serial_buffer)-1 ]) > 3 and p1_crc_check_is_on == True: # crc telegrams are 7 chars minimal (5+ cr\lf)

                        # check for telegrams with a CRC attached 
                        crc_read = str(serial_buffer[ len(serial_buffer)-1 ][1:5])
                        #flog.debug("CRC in telegram gevonden -> "+crc_read)
                        #print ('[*] crc waarde') 
                        #print crc_read

                        save_crc = serial_buffer[ len(serial_buffer)-1 ]
                        serial_buffer[ len(serial_buffer)-1 ] = '!' # only process to ! not the crc itself
                        strvar = ''.join(serial_buffer)
                        calc_crc = str('{0:0{1}X}'.format(CRC16().calculate( strvar ),4))
                        #flog.debug("Berekende CRC uit telegram -> "+calc_crc )

                        #flog.debug(inspect.stack()[0][3]+": serial buffer "+str(serial_buffer))	

                        if ( crc_read == calc_crc ):
                            #flog.debug("CRC is in orde.")
                            #restore CRC to received data
                            serial_buffer[ len(serial_buffer)-1 ] = save_crc
                        else:
                            crc_error_cnt = crc_error_cnt+1
                            #flog.debug("CRC van telegram komt niet overeen. CRC telegram ("+crc_read+"), berekende CRC ("+calc_crc+") niet verwerkt.")
                            del serial_buffer[:]
                            continue

                    #flog.debug(inspect.stack()[0][3]+": serial buffer "+str(serial_buffer))
                    #flog.setLevel(logging.DEBUG)
                    #print('verwerk seriele data.')
                    getCurrentRoomTemperature()
                    getCurrentWatermeterCount()
                    parseSerBuffer()
                    #flog.setLevel(logging.INFO)

            else:
                #print ( 'delta='+str(abs(timestamp_last_insert - getUtcTime())) )
                time.sleep(1)
                serCheckCnt = serCheckCnt + 1
                if serCheckCnt > 30: 
                    #print "serial interval check"
                    #flog.info(inspect.stack()[0][3]+": serial interval check.")
                    #checkSerial()
                    checkDbConfigSettings()
                    checkGasTelgramPrefix()
                    # read crc check settings from config
                    checkCRCsettings()
                    serCheckCnt=0

                if abs(timestamp_last_insert - getUtcTime()) > 51: # 51 secs (are 5 telegrams)
                    #print "P1 data to late!"
                    if p1_record_is_ok == 1:
                        flog.warning(inspect.stack()[0][3]+": geen P1 record te lezen.")
                    p1_record_is_ok = 0
                    rt_status_db.strset(str(p1_record_is_ok),46,flog) # P1 data is not ok recieved
                    # check if serial device is changed.
                    #checkSerial()
                    #ser1.close

                #print abs(last_crc_check_timestamp - getUtcTime()) , " cnt=", crc_error_cnt
                #crc error messages, if any.
                if p1_crc_check_is_on == True:
                    if abs(last_crc_check_timestamp - getUtcTime()) > 900:  #check every 15 minutes, to limit log entries.
                        last_crc_check_timestamp = getUtcTime()
                        if crc_error_cnt > 0: 
                            flog.warning("aantal P1 telegram crc fouten gevonden in de afgelopen minuut = " + str(crc_error_cnt))
                            crc_error_cnt = 0

        except Exception as inst:
            flog.warning(inspect.stack()[0][3]+": fout bij het wachten op seriele gegevens. Error="+str(inst))
            checkSerial()
            time.sleep(1)

def writeJsonToRamdisk():
    #flog.setLevel(logging.DEBUG)
    updateJsonData()
    try:
        filename = const.DIR_RAMDISK  + const.API_BASIC_JSON_PREFIX + system_id + const.API_BASIC_JSON_SUFFIX
        flog.debug(inspect.stack()[0][3]+": json output =" + json.dumps(json_data , sort_keys=True ) + " naar bestand " + filename)
        with open(filename, 'w') as outfile:
            json.dump(json_data , outfile, sort_keys=True )
        util.setFile2user(filename,'p1mon') # to make sure we can process the file
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": wegschrijven data naar ramdisk is mislukt. melding:"+str(e.args[0]))

    #flog.setLevel(logging.INFO)	

def writeToDropBox():
    #flog.setLevel(logging.DEBUG)
    _id, parameter, _label = config_db.strget(50,flog) # is Dropbox is on or off 
    if int(parameter) == 0: # dropbox sharing is off
        return # do nothing

    try:
        filename = const.DIR_DBX_LOCAL + const.DBX_DIR_DATA + '/' + const.API_BASIC_JSON_PREFIX + system_id + const.API_BASIC_JSON_SUFFIX
        flog.debug(inspect.stack()[0][3]+": json output =" + json.dumps(json_data , sort_keys=True ) + " naar bestand " + filename)
        with open(filename, 'w') as outfile:
            json.dump(json_data , outfile, sort_keys=True )
        util.setFile2user(filename,'p1mon') # to make sure we can process the file
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": wegschrijven data naar Dropbox is mislukt. melding:"+str(e.args[0]))

    #flog.setLevel(logging.INFO)

def existSerialDevice( tty ):
    cmd_str = "ls " + tty + " 2> /dev/null| wc -l"
    try:
        flog.debug( inspect.stack()[0][3]+": commando: " + cmd_str )
        p = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        #return_value=str( p.stdout.read() )
        #print ( int.from_bytes ( return_value , byteorder='big' )  )
        if int( p.communicate()[0].decode('utf-8') ) == 1:
            return True
        #result = p.communicate()[0]
        #print ( int( p.communicate()[0].decode('utf-8') ) )

    except Exception as e:
            flog.error( inspect.stack()[0][3] + ": controle onverwacht gefaald door fout ->  " + str(e.args) )
    return False

#forced, forces to open port
def checkSerial():
    global ser1

    #existSerialDevice( ser_devices[0] )
    #existSerialDevice( ser_devices[1] )
    #return

    for tty in ser_devices_list:

        if existSerialDevice( tty ): # check if device is known to the os.
            #print ( ser1.name ) 
            #print ( ser1.is_open )

            # close port to make sur, we don't get a warning
            try:
                ser1.port = tty
                ser1.close()
            except serial.SerialException as e:
                flog.warning( inspect.stack()[0][3] + ": serial port " + tty + " sluiten fout -> " + str(e.args))
                
            try:
                ser1.port = tty
                ser1.open()
                flog.info( inspect.stack()[0][3] + ": serial port " + tty + " succesvol geopend." )
                rt_status_db.strset( str(tty), 92, flog)
                return True

            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": serial port niet te openen ("+ser1.port+") is de USB serial kabel aangesloten? melding:"+str(e.args) )
        else:
            flog.debug( inspect.stack()[0][3] + ": serial port " + tty + " is niet aanwezig" )
    
    return False

def phase3StubInstert (line ):
    #voeg een 3 fase regels in, alleen voor ontwikkeling!!!
    try:
        flog.debug(inspect.stack()[0][3]+": 3 phase dummy string toevoegen.")

        tmp = random.uniform( -4, 4 )
        if ( tmp > 0 ):
            act_verbr_kw_l1 = tmp
            act_gelvr_kw_l1 = 0
        else:
            act_verbr_kw_l1 = 0
            act_gelvr_kw_l1 = tmp * -1
        
        tmp = random.uniform( -4, 4 )
        if ( tmp > 0 ):
            act_verbr_kw_l2 = tmp
            act_gelvr_kw_l2 = 0
        else:
            act_verbr_kw_l2 = 0
            act_gelvr_kw_l2 = tmp * -1
        
        tmp = random.uniform( -4, 4 )
        if ( tmp > 0 ):
            act_verbr_kw_l3 = tmp
            act_gelvr_kw_l3 = 0
        else:
            act_verbr_kw_l3 = 0
            act_gelvr_kw_l3 = tmp * -1

        del serial_buffer[len(serial_buffer)-1] # remove last ! line to add records.
        
        # add consumption phase kW
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:21.7.0(' + '{0:06.3f}'.format( act_verbr_kw_l1 )+ '*kW)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:41.7.0(' + '{0:06.3f}'.format( act_verbr_kw_l2 )+ '*kW)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:61.7.0(' + '{0:06.3f}'.format( act_verbr_kw_l3 )+ '*kW)\r\n'))
        serial_buffer.append( line_1 )

        # add production phase kW
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:22.7.0(' + '{0:06.3f}'.format( act_gelvr_kw_l1 )+ '*kW)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:42.7.0(' + '{0:06.3f}'.format( act_gelvr_kw_l2 )+ '*kW)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:62.7.0(' + '{0:06.3f}'.format( act_gelvr_kw_l3 )+ '*kW)\r\n'))
        serial_buffer.append( line_1 )

        #add phase voltage
        l1_v = random.uniform( 225, 235 )
        l2_v = random.uniform( 225, 235 )
        l3_v = random.uniform( 225, 235 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:32.7.0(' + '{0:03.1f}'.format( l1_v )+ '*V)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:52.7.0(' + '{0:03.1f}'.format( l2_v )+ '*V)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:72.7.0(' + '{0:03.1f}'.format( l3_v )+ '*V)\r\n'))
        serial_buffer.append( line_1 )

        # add phase amparage
        l1_a = ((act_verbr_kw_l1 + act_gelvr_kw_l1) * 1000) / l1_v
        l2_a = ((act_verbr_kw_l2 + act_gelvr_kw_l2) * 1000) / l2_v
        l3_a = ((act_verbr_kw_l3 + act_gelvr_kw_l3) * 1000) / l3_v
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:31.7.0(' + '{0:03.0f}'.format( l1_a ) + '*A)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:51.7.0(' + '{0:03.0f}'.format( l2_a ) + '*A)\r\n'))
        serial_buffer.append( line_1 )
        line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:71.7.0(' + '{0:03.0f}'.format( l3_a ) + '*A)\r\n'))
        serial_buffer.append( line_1 )

        serial_buffer.append( line ) # replace last line with ! character 
        #print ( serial_buffer )

        flog.warning(inspect.stack()[0][3]+": fase test regel toegevoegd aan telegram: " + \
          " L1: " + '{0:06.3f}'.format( act_verbr_kw_l1 ) + "kW " + '{0:03.1f}'.format( l1_v ) + "V " + '{0:03.0f}'.format( l1_a ) + "A "\
          " L2: " + '{0:06.3f}'.format( act_verbr_kw_l2 ) + "kW " + '{0:03.1f}'.format( l2_v ) + "V " + '{0:03.0f}'.format( l2_a ) + "A "\
          " L3: " + '{0:06.3f}'.format( act_verbr_kw_l3 ) + "kW " + '{0:03.1f}'.format( l3_v ) + "V " + '{0:03.0f}'.format( l3_a ) + "A "
             )

    except Exception as inst:
        print( type(inst) )
        print( inst.args )
        print( inst )

def gasStubInstert( line):
	#voeg een dummy gas record in alleen voor ontwikkeling!!!
	try:
		global serial_buffer
		global dev_dummy_gas_value
		global timestamp_last_gas_update

		#dev_dummy_gas_value = dev_dummy_gas_value + random.uniform(0, 0.0005) #0.0005
		if getUtcTime() - timestamp_last_gas_update > DUMMY_GAS_TIME_ELAPSED:
			dev_dummy_gas_value = dev_dummy_gas_value + random.uniform(0.0, 0.4)  #only update after elapsed time
			#dev_dummy_gas_value = dev_dummy_gas_value + 0.1
			#dev_dummy_gas_value = dev_dummy_gas_value + 0.0
			timestamp_last_gas_update = getUtcTime()
		#print ("dev_dummy_gas_value="+str(dev_dummy_gas_value))
		#print ( '{0:09.3f}'.format(dev_dummy_gas_value) )
		flog.debug(inspect.stack()[0][3]+": gas dummy string toevoegen.")
		del serial_buffer[len(serial_buffer)-1]
		
		if  DUMMY_GAS_MODE_2421 == True:
			line_1 = ''.join( filter(lambda x: x in string.printable, '0-1:24.2.1(170108160000W)('+'{0:09.3f}'.format(dev_dummy_gas_value)+'*m3)\r\n')).rstrip()[0:1024]
			serial_buffer.append( line_1 )
			#serial_buffer.append( '0-1:24.2.1(700101010000W)(00000000)' )
			#flog.debug(inspect.stack()[0][3]+": dummy gas waarde = "+line_1)
			flog.warning(inspect.stack()[0][3]+": test gas regel toegevoegd aan telegram: " + line_1 )
        
		if  DUMMY_GAS_MODE_2423 == True: #(voor Belgie)
			line_1 = ''.join( filter(lambda x: x in string.printable, '0-1:24.2.3(190830073458S)('+'{0:09.3f}'.format(dev_dummy_gas_value)+'*m3)\r\n')).rstrip()[0:1024]
			serial_buffer.append( line_1 )
			#serial_buffer.append( '0-1:24.2.1(700101010000W)(00000000)' )
			#flog.debug(inspect.stack()[0][3]+": dummy gas waarde = "+line_1)
			flog.warning(inspect.stack()[0][3]+": test gas regel toegevoegd aan telegram: " + line_1 )

        #if DUMMY_GAS_MODE_2421 == True or DUMMY_GAS_MODE_2423 == True or DUMMY_GAS_MODE_2430 == True:

		if DUMMY_GAS_MODE_2430 == True:
			line_1 = ''.join( filter(lambda x: x in string.printable, '0-1:24.3.0(121030140000)(00)(60)(1)(0-1:24.2.1)(m3)\r\n')).rstrip()[0:1024]
			line_2 = ''.join( filter(lambda x: x in string.printable, '('+'{0:09.3f}'.format(dev_dummy_gas_value)+')')).rstrip()[0:1024]
			serial_buffer.append( line_1 )
			serial_buffer.append( line_2 )
			flog.debug(inspect.stack()[0][3]+": dummy gas waarde = "+line_1)
			flog.warning(inspect.stack()[0][3]+": test gas regel 1 toegevoegd aan telegram: " + line_1 )
			flog.warning(inspect.stack()[0][3]+": test gas regel 2 toegevoegd aan telegram: " + line_2 )
			flog.debug(inspect.stack()[0][3]+": "+line_2)
			
		serial_buffer.append( line )
	except Exception as inst:
		print(type(inst))
		print(inst.args)
		print(inst)

def parseSerBuffer():
    global serial_buffer
    global verbrk_kwh_181, verbrk_kwh_182, gelvr_kwh_281, gelvr_kwh_282, \
           tarief_code, act_verbr_kw_170, act_gelvr_kw_270, gas_verbr_m3_2421
    global gas_present_in_serial_data
    #global act_verbr_kw_21, act_verbr_kw_41, act_verbr_kw_61, act_gelvr_kw_22, act_gelvr_kw_42, act_gelvr_kw_62
    global phase_db_record

    gas_present_in_serial_data = False 

   #dump buffer naar bestand voor user interface
    try:
        #print "write"
        fo = open(const.FILE_P1MSG+".tmp", "w")     
        for item in serial_buffer:
            filtered_string = ''.join( filter(lambda x: x in string.printable, item) ).rstrip()[0:1024]
            #print ( filtered_string )
            fo.write("%s\n" % filtered_string )
        fo.close
        shutil.move(const.FILE_P1MSG+".tmp", const.FILE_P1MSG)
        flog.debug(inspect.stack()[0][3]+": file weggeschreven naar "+const.FILE_P1MSG)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": p1 berichten buffer wegschrijven naar file "+str(e.args[0]))  

    # verwerk een voor een de regels

    #content = []
    while len(serial_buffer) > 0:
        line = serial_buffer.pop(0)
        #print len(line)
        if len(line) < 1: # we don't do empty lines
            continue
        try:
            buf = line.split('(')
            #print("#### "+str(buf))
            #print("#### "+str(buf[0]))
            if len(buf) < 2: # verwijder velden die niet interessant zijn
                continue 
            if buf[0] == '0-0:96.1.1': # verwijder slimme meter header 
                continue
            if buf[0] == '0-'+str(gas_record_prefix_number)+':24.2.3':
                content = buf[2].split(')')
                content = content[0].split('*')
                gas_verbr_m3_2421 = cleanDigitStr(content[0])
                #print (gas_verbr_m3_2421)
                gas_present_in_serial_data = True
            #if buf[0] == '0-1:24.2.1':
            if buf[0] == '0-'+str(gas_record_prefix_number)+':24.2.1':
                content = buf[2].split(')')
                content = content[0].split('*')
                gas_verbr_m3_2421 = cleanDigitStr(content[0])
                #print (gas_verbr_m3_2421)
                gas_present_in_serial_data = True
            #if buf[0] == '0-1:24.3.0':
            if buf[0] == '0-'+str(gas_record_prefix_number)+':24.3.0':
                line_tmp = serial_buffer.pop(0)
                #print(str(line_tmp))
                buf_tmp =  line_tmp.split('(')
                #print(str(buf_tmp))
                gas_verbr_m3_2421 = cleanDigitStr(buf_tmp[1])
                #print(gas_verbr_m3_2421)
                gas_present_in_serial_data = True
            elif buf[0] == '1-0:1.8.1': 
                content = buf[1].split('*') 
                verbrk_kwh_181=cleanDigitStr(content[0])
            elif buf[0] == '1-0:1.8.2': 
                content = buf[1].split('*') 
                verbrk_kwh_182=cleanDigitStr(content[0])
            elif buf[0] == '1-0:2.8.1': 
                content = buf[1].split('*') 
                gelvr_kwh_281=cleanDigitStr(content[0])
            elif buf[0] == '1-0:2.8.2': 
                content = buf[1].split('*') 
                gelvr_kwh_282=cleanDigitStr(content[0])
            elif buf[0] == '1-0:1.7.0':
                content = buf[1].split('*') 
                act_verbr_kw_170=cleanDigitStr(content[0])
            elif buf[0] == '1-0:2.7.0':
                content = buf[1].split('*')
                act_gelvr_kw_270=cleanDigitStr(content[0])
            elif buf[0] == '0-0:96.14.0':    
                content = buf[1].split(')')
                tarief_code=cleanDigitStr(content[0])
            elif buf[0] == '1-0:21.7.0': 
                content = buf[1].split('*')
                #act_verbr_kw_21 = cleanDigitStr(content[0])
                phase_db_record['consumption_L1_kW'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:41.7.0': 
                content = buf[1].split('*')
                #act_verbr_kw_41 = cleanDigitStr(content[0])
                phase_db_record['consumption_L2_kW'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:61.7.0': 
                content = buf[1].split('*')
                #act_verbr_kw_61 = cleanDigitStr(content[0])
                phase_db_record['consumption_L3_kW'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:22.7.0': 
                content = buf[1].split('*')
                #act_gelvr_kw_22 = cleanDigitStr(content[0])
                phase_db_record['production_L1_kW'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:42.7.0': 
                content = buf[1].split('*')
                #act_gelvr_kw_42 = cleanDigitStr(content[0])
                phase_db_record['production_L2_kW'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:62.7.0': 
                content = buf[1].split('*')
                #act_gelvr_kw_62 = cleanDigitStr(content[0])
                phase_db_record['production_L3_kW'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:32.7.0': 
                content = buf[1].split('*')
                phase_db_record['L1_V'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:52.7.0': 
                content = buf[1].split('*')
                phase_db_record['L2_V'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:72.7.0': 
                content = buf[1].split('*')
                phase_db_record['L3_V'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:31.7.0': 
                content = buf[1].split('*')
                phase_db_record['L1_A'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:51.7.0': 
                content = buf[1].split('*')
                phase_db_record['L2_A'] = cleanDigitStr(content[0])
            elif buf[0] == '1-0:71.7.0': 
                content = buf[1].split('*')
                phase_db_record['L3_A'] = cleanDigitStr(content[0])
            if tarief_code == '0002':
                tarief_code = 'P'
            if tarief_code == '0001':
                tarief_code = 'D'

        except Exception as e:
            flog.error(inspect.stack()[0][3]+": fout in P1 data. Regel="+\
            line+" melding:"+str(e.args[0]))
    
    """
    print ( phase_db_record['L1_V'] )
    print ( phase_db_record['L2_V'] )
    print ( phase_db_record['L3_V'] )
    print ( phase_db_record['L1_A'] )
    print ( phase_db_record['L2_A'] )
    print ( phase_db_record['L3_A'] )
    """

    """
    flog.info(inspect.stack()[0][3]+" Gevonden waarden zijn"+\
        " verbrk_kwh_181="      + str( verbrk_kwh_181    )+\
        " verbrk_kwh_182="      + str( verbrk_kwh_182    )+\
        " gelvr_kwh_281="       + str( gelvr_kwh_281     )+\
        " gelvr_kwh_282="       + str( gelvr_kwh_282     )+\
        " tarief_code="         + str( tarief_code       )+\
        " act_verbr_kw_170="    + str( act_verbr_kw_170  )+\
        " act_gelvr_kw_270="    + str( act_gelvr_kw_270  )+
        " gas_verbr_m3_2421="   + str( gas_verbr_m3_2421 )+\
        " act_verbr_kw_21="     + str( act_verbr_kw_21   )+\
        " act_verbr_kw_41="     + str( act_verbr_kw_41   )
   )
   """
   
    if day_night_mode == 1: 
        flog.debug( inspect.stack()[0][3] + " Dag en nacht tarief staat op mode 1: Belgie" )
        tmp = verbrk_kwh_181
        verbrk_kwh_181 = verbrk_kwh_182
        verbrk_kwh_182 = tmp
        tmp = gelvr_kwh_281
        gelvr_kwh_281 = gelvr_kwh_282
        gelvr_kwh_282 = tmp 
        if tarief_code == 'P': # wisselen van tarief code 00002 is piek in NL maar dal in Belgie.  0001 is dal in NL maar piek in Belgie.
            tarief_code = 'D'
        else: 
            tarief_code = 'P'

    if day_night_mode == 0: 
        flog.debug( inspect.stack()[0][3] + " Dag en nacht tarief staat op mode 0: Nederland" )
 
    #flog.setLevel(logging.DEBUG)
    if recordSanityOk() == True:
        # schrijf Dal/Piek naar status database
        rt_status_db.strset( str(tarief_code), 85, flog ) 
        insertDbRecord()
        writeJsonToRamdisk()
        writeToDropBox()
        if gas_present_in_serial_data == True:
            instertDbGasValue()
        phaseValuesToStatusDb()
        phaseValuesToPhaseDb()
        clearPhaseDictionary()
    else:
        flog.error(inspect.stack()[0][3]+": p1 bericht verworpen wegens fout.")
    #flog.setLevel(logging.INFO)

   #clean the buffer
    del serial_buffer[:]
    verbrk_kwh_181=verbrk_kwh_182=gelvr_kwh_281=gelvr_kwh_282=\
        tarief_code=act_verbr_kw_170=act_gelvr_kw_270=gas_verbr_m3_2421=const.NOT_SET
        #act_verbr_kw_21=act_verbr_kw_41=act_verbr_kw_61=act_gelvr_kw_22=act_gelvr_kw_42=act_gelvr_kw_62 = const.NOT_SET

def phaseValuesToPhaseDb():
    global phase_db_record
    phase_db_record['timestamp'] = mkLocalTimeString()

    # only add data when fase info is set to on.
    if config_db.strget( 119 ,flog )[1] == "1": 
        try:
            
            sqlstr = "insert or replace into " + const.DB_FASE_REALTIME_TAB + " (TIMESTAMP, VERBR_L1_KW,VERBR_L2_KW,VERBR_L3_KW,GELVR_L1_KW,GELVR_L2_KW,GELVR_L3_KW,L1_V,L2_V,L3_V,L1_A,L2_A,L3_A) VALUES ('" + \
                str( phase_db_record['timestamp'] )         + "'," + \
                str( phase_db_record['consumption_L1_kW'] ) + "," + \
                str( phase_db_record['consumption_L2_kW'] ) + "," + \
                str( phase_db_record['consumption_L3_kW'] ) + "," + \
                str( phase_db_record['production_L1_kW'] )  + "," + \
                str( phase_db_record['production_L2_kW'] )  + "," + \
                str( phase_db_record['production_L3_kW'] )  + "," + \
                str( phase_db_record['L1_V'] )              + ", " + \
                str( phase_db_record['L2_V'] )              + ", " + \
                str( phase_db_record['L3_V'] )              + ", " + \
                str( phase_db_record['L1_A'] )              + ", " + \
                str( phase_db_record['L2_A'] )              + ", " + \
                str( phase_db_record['L3_A'] )              + ")"
            
            sqlstr = " ".join( sqlstr.split() )
            flog.debug( inspect.stack()[0][3] + ": SQL =" + str(sqlstr) )
            fase_db.insert_rec(sqlstr)
        
        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": Insert gefaald. Melding=" + str(e.args[0]) )

    try:
        if ( int( phase_db_record['timestamp'][14:16] )%5 ) == 0: # delete every 5 minutes and not every record to limit DB load and fragmentaion.
            #records verwijderen 
            sql_del_str = "delete from " + const.DB_FASE_REALTIME_TAB + " where timestamp <  '"+\
            str( datetime.strptime( phase_db_record['timestamp'], "%Y-%m-%d %H:%M:%S") - timedelta(days=7))+"'"
            flog.debug( inspect.stack()[0][3] + ": sql=" + sql_del_str )
            fase_db.del_rec(sql_del_str)
    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": verwijderen fase records ,delete gefaald. Melding=" + str(e.args[0]) )

def phaseValuesToStatusDb():
    global phase_db_record

    try:
        
        if float( phase_db_record['consumption_L1_kW'] ) != const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['consumption_L1_kW'] ) ,74, flog )
        else:
            rt_status_db.strset( '0.0' ,74, flog )
            phase_db_record['consumption_L1_kW'] = 0

        if float( phase_db_record['consumption_L2_kW'] ) !=  const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['consumption_L2_kW'] ) ,75, flog )

        else:
            rt_status_db.strset( '0.0' ,75, flog )
            phase_db_record['consumption_L2_kW'] = 0

        if float( phase_db_record['consumption_L3_kW'] ) !=  const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['consumption_L3_kW'] ) ,76, flog )
        else:
            rt_status_db.strset( '0.0' ,76, flog )
            phase_db_record['consumption_L3_kW'] = 0

        if float( phase_db_record['production_L1_kW'] ) !=  const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['production_L1_kW'] ) ,77, flog )
        else:
            rt_status_db.strset( '0.0' ,77, flog )
            phase_db_record['production_L1_kW'] = 0

        if float( phase_db_record['production_L2_kW'] ) !=  const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['production_L2_kW'] ) ,78, flog )
        else:
            rt_status_db.strset( '0.0' ,78, flog )
            phase_db_record['production_L2_kW'] = 0

        if float( phase_db_record['production_L3_kW'] ) !=  const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['production_L3_kW'] ) ,79, flog )
        else:
            rt_status_db.strset( '0.0' ,79, flog )
            phase_db_record['production_L3_kW'] = 0

        if float( phase_db_record['L1_V'] ) != const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['L1_V'] ) ,103, flog )
        else:
            rt_status_db.strset( '0.0' ,103, flog )
            phase_db_record['L1_V'] = 0

        if float( phase_db_record['L2_V'] ) != const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['L2_V'] ) ,104, flog )
        else:
            rt_status_db.strset( '0.0' ,104, flog )
            phase_db_record['L2_V'] = 0

        if float( phase_db_record['L3_V'] ) != const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['L3_V'] ) ,105, flog )
        else:
            rt_status_db.strset( '0.0' ,105, flog )
            phase_db_record['L3_V'] = 0

        if float( phase_db_record['L1_A'] ) != const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['L1_A'] ) ,100, flog )
        else:
            rt_status_db.strset( '0.0' ,100, flog )
            phase_db_record['L1_A'] = 0

        if float( phase_db_record['L2_A'] ) != const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['L2_A'] ) ,101, flog )
        else:
            rt_status_db.strset( '0.0' ,101, flog )
            phase_db_record['L2_A'] = 0

        if float( phase_db_record['L3_A'] ) != const.NOT_SET:
            rt_status_db.strset( float( phase_db_record['L3_A'] ) ,102, flog )
        else:
            rt_status_db.strset( '0.0' ,102, flog )
            phase_db_record['L3_A'] = 0

        rt_status_db.timestamp( 106, flog ) # update timestamp of phase values in status database.

    except Exception as e:
            flog.error( inspect.stack()[0][3] + ": probleem met update van fase data naar status database =" + str(e.args[0]) )
    """
    print ( phase_db_record )
    print ( rt_status_db.strget( 100 ,flog ) )
    print ( rt_status_db.strget( 101 ,flog ) )
    print ( rt_status_db.strget( 102 ,flog ) )
    print ( rt_status_db.strget( 103 ,flog ) )
    print ( rt_status_db.strget( 104 ,flog ) )
    print ( rt_status_db.strget( 105 ,flog ) )
    print ( rt_status_db.strget( 106 ,flog ) )
   # sys.exit()
    """

def checkCRCsettings():
	global p1_crc_check_is_on
	if config_db.strget(45,flog)[1] == "0":
		p1_crc_check_is_on = False
	else:
		p1_crc_check_is_on = True

def instertDbGasValue():
	global g2h_previous_gas_value 
	global g2h_previous_timestamp
	try:
		rt_status_db.strset(str(float(gas_verbr_m3_2421)),43,flog)
	except Exception as e:
		flog.error(inspect.stack()[0][3]+": Melding="+str(e.args[0]))
	
	# calculate gas/hour value.
	try:
		#print ( 'run version ='+str(int(time.time()))+ ' delta ='+str(int(time.time() - g2h_previous_timestamp)) )
		if g2h_previous_timestamp == const.NOT_SET: # first run
			g2h_previous_timestamp 	= int(time.time())
			g2h_previous_gas_value 	= gas_verbr_m3_2421
			return

		#print ( '--------------------0' )
		#print ( gas_verbr_m3_2421 )


		if g2h_previous_gas_value != gas_verbr_m3_2421:
			#flog.setLevel( logging.DEBUG )
			#print ( '--------------------1' )
			#print ( g2h_previous_gas_value )
			#print ( gas_verbr_m3_2421 )
			gas_delta = abs( float(g2h_previous_gas_value) - float(gas_verbr_m3_2421) )
			time_delta = abs( int(g2h_previous_timestamp) - int(time.time()) )
			flog.debug( inspect.stack()[0][3] + ": gas waarde verschild met vorige meting=" + str(gas_delta) )
			flog.debug( inspect.stack()[0][3] + ": seconden verstreken met vorige meting=" + str(time_delta) )
			gas_m2hour = (gas_delta / time_delta) * 3600
			flog.debug( inspect.stack()[0][3] + ": gas per uur (berekend) =" + str(gas_m2hour ) )

			rt_status_db.strset(str(float(gas_m2hour)),50,flog)

			g2h_previous_timestamp 	= int(time.time())
			g2h_previous_gas_value  = gas_verbr_m3_2421

			#flog.setLevel( logging.INFO )

	except Exception as e:
            flog.error(inspect.stack()[0][3]+": gas per uur fout -> "+str(e))
	#print ( '--------------------2' )
	#print ( g2h_previous_gas_value )
	#print ( g2h_previous_timestamp )
	#print ( g2h_current_gas_value )
	#print ( g2h_current_timestamp) 

def checkGasTelgramPrefix():
    global gas_record_prefix_number
    try:
        gas_config_rec = config_db.strget(38, flog)
        if str(gas_config_rec[1]) != gas_record_prefix_number:
            gas_record_prefix_number = str(gas_config_rec[1])
            flog.info(inspect.stack()[0][3]+": gas telegram records gewijzigd naar "+gas_record_prefix_number)
        else:
            flog.debug(inspect.stack()[0][3]+": gas telegram records niet gewijzigd. huidige waarde "+gas_record_prefix_number)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": gas telegram prefix record niet gewijzigd."+str(e))

def checkDbConfigSettings():
    global ser1
    global day_night_mode 
    # 7 P1 poort baudrate
    # 8 P1 poort bytesize
    # 9 P1 poort pariteit
    # 10 P1 poort stopbits
    flog.debug(inspect.stack()[0][3]+": check if serial values changed.")
    updateNeeded = False 
    try:
        sqlstr = "select id, parameter from "+const.DB_CONFIG_TAB+" where id >=7 and id <=10 order by id asc"
        sqlstr=" ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql(1)="+sqlstr)
        ser_config=config_db.select_rec(sqlstr)    
        flog.debug(inspect.stack()[0][3]+": waarde van serial config record"+str(ser_config))
       
        if ser1.baudrate != int(ser_config[0][1]):
            flog.debug(inspect.stack()[0][3]+": baudrate is differend")
            #ser1.baudrate = int(ser_config[0][1])
            updateNeeded = True
            
        if ser1.bytesize != int(ser_config[1][1]):
            flog.debug(inspect.stack()[0][3]+": byte size is differend")
            #ser1.bytesize = int(ser_config[1][1])
            updateNeeded = True
            
        if ser1.parity != ser_config[2][1]:    
            flog.debug(inspect.stack()[0][3]+": paritiy is differend")
            updateNeeded = True

        if ser1.stopbits != int(ser_config[3][1]):    
            flog.debug(inspect.stack()[0][3]+": stop bits is differend")
            #ser1.stopbits = int(ser_config[3][1])
            updateNeeded = True  
            
        if updateNeeded == True:
            flog.info(inspect.stack()[0][3]+":  P1 poort wordt aangepast van -> baudrate=" + str(ser1.baudrate)+" bytesize=" +str(ser1.bytesize)+" pariteit="+str(ser1.parity)+" stopbits="+str(ser1.stopbits))
            
            #log.debug(inspect.stack()[0][3]+": restarting serial port.")
            #if restart:
            #    serClose(ser1)
            #    time.sleep(5) # give it some time.
                
            ser1.baudrate = int(ser_config[0][1])
            ser1.bytesize = int(ser_config[1][1])
            
            ser1.parity=serial.PARITY_EVEN #default value
            if ser_config[2][1] == "E":        
                ser1.parity=serial.PARITY_EVEN  
            if ser_config[2][1] == "O":
                ser1.parity=serial.PARITY_ODD 
            if ser_config[2][1] == "N":
                ser1.parity=serial.PARITY_NONE
            #if ser_config[2][1] == "M":
            #    ser1.parity=serial.PARITY_MARK 
            #if ser_config[2][1] == "S":
            #    ser1.parity=serial.PARITY_SPACE
                
            ser1.stopbits = int(ser_config[3][1])
            
            flog.info(inspect.stack()[0][3]+":  P1 poort aangegepast naar -> baudrate=" + str(ser1.baudrate)+" bytesize=" +str(ser1.bytesize)+" pariteit="+str(ser1.parity)+" stopbits="+str(ser1.stopbits))
            ser1.flushInput()
            
    except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error(1)"+str(e))
    
    try:
        _id, parameter, _label = config_db.strget( 78,flog )
        if int( parameter ) != day_night_mode:
            day_night_mode = int( parameter )
            flog.info(inspect.stack()[0][3]+": dag nacht mode aangepast met de waarde " + str( day_night_mode )  + ". Mode 0 is Nederland, Mode 1 is Belgie.")
    except Exception as e:
            flog.error(inspect.stack()[0][3]+": sql error( config )"+str(e))        

def fileChanged( src_file, dst_dir ):
    # geef secs verschil terug van bestand
    try :
        statinfo_src = os.stat(src_file)
        _head,tail = os.path.split(src_file)   
        statinfo_dst = os.stat(dst_dir+"/"+tail)
        return int(abs(statinfo_src.st_mtime - statinfo_dst.st_mtime))   
    except Exception as _e:
        return int(-1)

def backupData():
    try:
        file_sec_delta = fileChanged(const.FILE_DB_E_FILENAME ,const.DIR_FILEDISK)
        if file_sec_delta > 60  or file_sec_delta == -1:
            flog.debug(inspect.stack()[0][3]+": Gestart")     
            os.system("/p1mon/scripts/P1DbCopy.py --serialcopy2disk --forcecopy")
            rt_status_db.timestamp(41,flog)
            flog.debug(inspect.stack()[0][3]+": Gereed")
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": data backup fout: "+str(e))	

def DiskRestore():
    os.system("/p1mon/scripts/P1DbCopy.py --allcopy2ram")

def checkMaxKwDag():
    global daytime_start_str, daytime_end_str
    # vind de maximale waarden van deze dag
    try:
        sql_str = " select max(act_verbr_KW_170), max(act_gelvr_KW_270) \
        from "+const.DB_SERIAL_TAB+" where timestamp >='" \
        +daytime_start_str+"' and timestamp <='"+daytime_end_str+"'"
        sql_str = " ".join(sql_str.split())
        flog.debug(inspect.stack()[0][3]+": SQL kw waarden="+sql_str)
        rec_kw_waarden = e_db_serial.select_rec(sql_str)
        rt_status_db.strset(str(rec_kw_waarden[0][0]),1,flog)
        rt_status_db.strset(str(rec_kw_waarden[0][1]),3,flog)
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": Melding="+str(e.args[0]))
       
    # vind tijdstippen van de maximale waarden van deze dag
    try:
        # tijdstip bepalen verbruikt.
        sql_time = "select min(timestamp) from "+const.DB_SERIAL_TAB+\
        " where timestamp >='"+daytime_start_str+"' and timestamp <= '"\
        +daytime_end_str+"' and act_verbr_KW_170 = "+str(rec_kw_waarden[0][0])    
        sql_time = " ".join(sql_time.split())
        flog.debug(inspect.stack()[0][3]+": SQL kw waarden="+sql_time)
        
        rec_time = e_db_serial.select_rec(sql_time)
        if float(rec_kw_waarden[0][0]) == 0.0:
            rt_status_db.strset(daytime_start_str,2,flog)
        else:    
            rt_status_db.strset(rec_time[0][0],2,flog)

        # tijdstip bepalen geleverd.
        sql_time = "select min(timestamp) from "+const.DB_SERIAL_TAB+\
        " where timestamp >='"+daytime_start_str+"' and timestamp <= '"\
        +daytime_end_str+"' and act_gelvr_KW_270 = "+str(rec_kw_waarden[0][1])                                                                  
        sql_time = " ".join(sql_time.split())
        flog.debug(inspect.stack()[0][3]+": SQL kw waarden="+sql_time)
        
        rec_time = e_db_serial.select_rec(sql_time)
        if float(rec_kw_waarden[0][1]) == 0.0:
            rt_status_db.strset(daytime_start_str,4,flog)
        else:   
            rt_status_db.strset(rec_time[0][0],4,flog)    
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": Melding="+str(e.args[0]))

def maxKWhDagWaarde():
    try:
        sqlstr = "select verbr_kwh_181,verbr_kwh_182,gelvr_kwh_281,gelvr_kwh_282 \
        from "+const.DB_SERIAL_TAB+" where timestamp = \
        (select min(timestamp) from "+const.DB_SERIAL_TAB+\
        " where timestamp >= '"+daytime_start_str+"'and  timestamp <= '"+daytime_end_str+"')"
        sqlstr = " ".join(sqlstr.split())
        flog.debug(inspect.stack()[0][3]+": sql="+sqlstr)   
        start_van_dag_waarde=e_db_serial.select_rec(sqlstr)
        flog.debug(inspect.stack()[0][3]+": record="+str(start_van_dag_waarde))
        
        rt_status_db.strset(alwaysPlus(float(verbrk_kwh_181)- float(start_van_dag_waarde[0][0])),8,flog)
        rt_status_db.strset(alwaysPlus(float(verbrk_kwh_182)- float(start_van_dag_waarde[0][1])),9,flog)
        rt_status_db.strset(alwaysPlus(float(gelvr_kwh_281) - float(start_van_dag_waarde[0][2])),10,flog)
        rt_status_db.strset(alwaysPlus(float(gelvr_kwh_282) - float(start_van_dag_waarde[0][3])),11,flog) 
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": serial e-buffer kwH waarden vorige dag gefaald. Melding="+str(e.args[0]))

def insertDbRecord():
	global daytime_start_str, daytime_end_str
	global gas_verbr_m3_2421
	global timestamp_last_insert
	global p1_record_is_ok
	
	"""
	# rate limitingen of inserts, some smart meters send more then every 10 sec. a telegram.
	if abs(timestamp_last_insert - getUtcTime()) < 9: # 9 or 10 sec interval is ok.
		#flog.warning("TEST tijd kleiner dan 9 seconden skip")
		#print('delta='+str( abs(timestamp_last_insert - getUtcTime())))
		return
	"""
	
	try:
		timestr=mkLocalTimeString()  
		#timestr_min=timestr[0:16]+":00"
		if gas_present_in_serial_data == False:
			gas_verbr_m3_2421 = 0
		daytime_start_str = timestr[0:10]+" 00:00:00"
		daytime_end_str   = timestr[0:10]+" 23:59:59"
		flog.debug("[START] instertDbRecord: timestamp nieuwe record="+timestr)
		flog.debug("instertDbRecord Dag start="+daytime_start_str+" Dag einde="+daytime_end_str)
                  
		sqlstr ="insert or replace into "+const.DB_SERIAL_TAB+\
		" values (\
		'"+timestr+"',\
		'"+"0"+"',\
		'"+str(verbrk_kwh_181)+"', \
		'"+str(verbrk_kwh_182)+"', \
		'"+str(gelvr_kwh_281)+"', \
		'"+str(gelvr_kwh_282)+"', \
		'"+str(tarief_code)+"', \
		'"+str(act_verbr_kw_170)+"', \
		'"+str(act_gelvr_kw_270)+"',\
		'"+str(gas_verbr_m3_2421)+"')"
		sqlstr = " ".join(sqlstr.split())
		flog.debug(inspect.stack()[0][3]+": (1)serial e-buffer insert: sql="+sqlstr)
		e_db_serial.insert_rec(sqlstr)
 		# timestamp telegram processed
		rt_status_db.timestamp(16,flog)                         # Timestring + Daylight saving.
		rt_status_db.strset( str(getUtcTime()), 87 , flog  )    # UTC time
		p1_record_is_ok = 1
		rt_status_db.strset(str(p1_record_is_ok),46,flog) # P1 data is ok recieved
		timestamp_last_insert = getUtcTime()
		#print(timestamp_last_insert)
		if isMod(timestr,15) == True:
			backupData()

	except Exception as e:
		flog.error(inspect.stack()[0][3]+": Insert gefaald. Melding="+str(e.args[0]))

	# max waarden bijwerken
	checkMaxKwDag()

	# dag waarden KWH verbruikt bijwerken
	maxKWhDagWaarde()

	#clean serial buffer. alles wat ouder is dan zeven dagen verwijderen
	sql_del_str = "delete from "+const.DB_SERIAL_TAB+" where timestamp <  '"+\
	str(datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - timedelta(days=7))+"' and record_verwerkt=1"
	try:
		flog.debug(inspect.stack()[0][3]+": serial e-buffer delete: sql="+sql_del_str)
		e_db_serial.del_rec(sql_del_str)
	except Exception as e:
		flog.error(inspect.stack()[0][3]+": delete gefaald. Melding="+str(e.args[0]))

def recordSanityOk():
	global verbrk_kwh_181, verbrk_kwh_182, gelvr_kwh_281, gelvr_kwh_282, \
		tarief_code, act_verbr_kw_170, act_gelvr_kw_270, gas_verbr_m3_2421

	recordIsOk = True
	#tarief_code = '000' #debug

	if gas_present_in_serial_data == True:
		if gas_verbr_m3_2421 == const.NOT_SET:
			flog.warning(inspect.stack()[0][3]+": Gefaald op gas verbruikt (24.2.1), waarde was "+str(gas_verbr_m3_2421))
			recordIsOk = False

	if verbrk_kwh_181 == const.NOT_SET:
		flog.warning(inspect.stack()[0][3]+": Gefaald op dal/nacht voor verbruikte energie(1.8.1), waarde was "+str(verbrk_kwh_181))
		recordIsOk = False

	if verbrk_kwh_182 == const.NOT_SET:
		flog.warning(inspect.stack()[0][3]+": Gefaald op piek/dag voor verbruikte energie(1.8.2), waarde was "+str(verbrk_kwh_182))
		recordIsOk = False

	if gelvr_kwh_281 == const.NOT_SET:
		flog.warning(inspect.stack()[0][3]+": Gefaald op dal/nacht  voor geleverde energie(2.8.1), waarde was "+str(gelvr_kwh_281))
		recordIsOk = False

	if gelvr_kwh_282 == const.NOT_SET:
		flog.warning(inspect.stack()[0][3]+": Gefaald op piek/dag voor geleverde energie(2.8.2), waarde was "+str(gelvr_kwh_282))
		recordIsOk = False

	if tarief_code  != 'P' and tarief_code  != 'D':
		flog.warning(inspect.stack()[0][3]+": Gefaald op tariefcode, verwachte P of D, waarde was "+str(tarief_code))
		recordIsOk = False

	if act_verbr_kw_170 == const.NOT_SET:
		flog.warning(inspect.stack()[0][3]+": Gefaald op actueel verbruikt vermogen, waarde was "+str(act_verbr_kw_170))
		recordIsOk = False

	if act_gelvr_kw_270 == const.NOT_SET:
		flog.warning(inspect.stack()[0][3]+": Gefaald op actueel geleverd vermogen, waarde was "+str(act_gelvr_kw_270))
		recordIsOk = False

    #controle op verwacht format van fields
    #print ( "[**]"+str(len(verbrk_kwh_181)) )
    #print ( "[***]"+str(len(act_verbr_kw_170)) )

    #print ( '[*******]'+len(str(verbrk_kwh_181)) )
    #sys.exit(0)
    #print ( len(str(verbrk_kwh_181)) )
	if gas_present_in_serial_data == True:
		if len(str(gas_verbr_m3_2421)) < 8 or len(str(gas_verbr_m3_2421)) > 12:
			flog.warning(inspect.stack()[0][3]+": Gefaald op gas verbruikt (24.2.1) (lengte), waarde was "+str(gas_verbr_m3_2421))
			recordIsOk = False

	if len(str(verbrk_kwh_181)) < 9 or len(str(verbrk_kwh_181)) > 10:
		flog.warning(inspect.stack()[0][3]+": Gefaald op dal/nacht format (1.8.1) (lengte), waarde was "+str(verbrk_kwh_181))
		recordIsOk = False

	if len(str(verbrk_kwh_182)) < 9  or len(str(verbrk_kwh_182)) > 10:
		flog.warning(inspect.stack()[0][3]+": Gefaald op piek/dag format (1.8.2) (lengte), waarde was "+str(verbrk_kwh_182))
		recordIsOk = False

	if len(str(gelvr_kwh_281)) < 9  or len(str(gelvr_kwh_281)) > 10:
		flog.warning(inspect.stack()[0][3]+": Gefaald op dal/nacht format (2.8.1) (lengte), waarde was "+str(gelvr_kwh_281))
		recordIsOk = False

	if len(str(gelvr_kwh_282)) < 9 or len(str(gelvr_kwh_282)) > 10:
		flog.warning(inspect.stack()[0][3]+": Gefaald op piek/dag format (2.8.2) (lengte), waarde was "+str(gelvr_kwh_282))
		recordIsOk = False

	if len(str(act_verbr_kw_170)) < 6 or len(str(act_verbr_kw_170)) > 7:
		flog.warning(inspect.stack()[0][3]+": Gefaald op actueel verbruikt vermogen format (1.7.0) (lengte), waarde was "+str(act_verbr_kw_170))
		recordIsOk = False
	
	if len(str(act_gelvr_kw_270)) < 6 or len(str(act_gelvr_kw_270)) > 7:
		flog.warning(inspect.stack()[0][3]+": Gefaald op actueel geleverd vermogen format (2.7.0) (lengte), waarde was "+str(act_gelvr_kw_270))
		recordIsOk = False

	return recordIsOk    

def getCurrentRoomTemperature():
    global temperature_in, temperature_out
    sqlstr = "select TEMPERATURE_1_AVG, TEMPERATURE_2_AVG FROM temperatuur where record_id = 10 order by timestamp desc limit 1"
    try:  
        temperature_in  = 0 # failsave if there is no data
        temperature_out =0 # failsave if there is no data
        list = temperature_db.select_rec(sqlstr)
        temperature_in  = list[0][0]
        temperature_out = list[0][1]
    except Exception as e:
        flog.debug(inspect.stack()[0][3]+": DB lezen van temperatuur (kamer) melding:"+str(e.args[0]))

def getCurrentWatermeterCount():
    global watermeters_count_total
    try:
        _id, is_water_active, _label = config_db.strget( 96, flog )
       
        if int( is_water_active ) == 0: # return
            flog.debug( inspect.stack()[0][3] + ": water meting staat uit. " )
            return
        
        watermeters_count_total = 0 # failsave if there is no data
        _timestamp, _utc, _puls_per_timeunit, _verbr_per_timeunit, verbr_in_m3_total = watermeter_db.select_one_record() 
        if verbr_in_m3_total != None:
            watermeters_count_total = round( float(verbr_in_m3_total), 3 )
            #print ( watermeters_count_total )
    except Exception as e:
        pass #stop without complaining
        #flog.warning( inspect.stack()[0][3] + ": probleem bij het lezen van de watermeter stand -> " + str(e.args[0]) )

def saveExit(signum, frame):
    #setFileFlags()
    signal.signal(signal.SIGINT, original_sigint)
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    os.umask( 0o002 )
    flog = fileLogger( const.DIR_FILELOG+prgname+".log", prgname )   
    flog.setLevel( logging.INFO )
    flog.consoleOutputOn( True )
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    main_prod()

