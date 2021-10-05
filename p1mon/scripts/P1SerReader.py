#!/usr/bin/python3
import apiconst
import const
import data_struct_lib
import day_values_lib
import inspect
import logger
from PyCRC.CRC16 import CRC16
import subprocess
import systemid
import sqldb
import serial
import signal
import sys
import os
import p1_port_shared_lib
import p1_telegram_test_lib
import time
import util

temperature_db     = sqldb.temperatureDB()
e_db_serial        = sqldb.SqlDb1()
rt_status_db       = sqldb.rtStatusDb()
config_db          = sqldb.configDB()
watermeter_db      = sqldb.WatermeterDBV2()
fase_db            = sqldb.PhaseDB()

prgname                     = 'P1SerReader'
serial_buffer               = []
dev_dummy_gas_value         = 0
timestamp_last_gas_update   = 0
system_id = systemid.getSystemId()

# list of serial devices tried to use
ser_devices_list = [ "/dev/ttyUSB0" , "/dev/ttyUSB1" ]

###################################################################################
# let op deze optie geef veel foutmelding en in de log deze kunnen geen kwaad     #
###################################################################################
DUMMY_1SEC_PROCCESSING = False  ######### DEZE OP FALSE ZETTEN BIJ PRODUCTIE CODE!!!!
DUMMY_3PHASE_DATA      = False  ######### DEZE OP FALSE ZETTEN BIJ PRODUCTIE CODE!!!!

# zet deze op p1_telegram_test_lib.NO_GAS_TEST om de test uit te zetten.
#gas_test_mode=p1_telegram_test_lib.DUMMY_GAS_MODE_2421
gas_test_mode=p1_telegram_test_lib.NO_GAS_TEST

#Set COM port config
ser1 = serial.Serial()

ser1.baudrate = 115200
ser1.bytesize = 8
ser1.parity   = "N"
ser1.stopbits = 1

ser1.xonxoff = 0 # changed from version 0.9.2 onwards
ser1.rtscts  = 0
ser1.timeout = 1
ser1.port    = ser_devices_list[0]

base_p1_data     = data_struct_lib.p1_data_base_record
phase_db_record  = data_struct_lib.phase_db_record 
json_data        = data_struct_lib.json_basic
processing_speed = data_struct_lib.p1_processing_speed
p1_status        = data_struct_lib.p1_status_record

p1_status['timestamp_last_insert']  = util.getUtcTime() 
p1_status['day_night_mode']         = 0  # default NL, 1 is Belgium

day_values = day_values_lib.dayMinMaxkW()

def main_prod():

    global ser1
    global serial_buffer
    global processing_speed 
    
    stub_serial_buffer = [] # for stub testing only

    p1_port_shared_lib.clear_data_buffer( buffer=phase_db_record )

    flog.info("Start van programma.")

    # make sure as first program to run that ram is filled with the 
    # last data from persistent memory (disk)
    p1_port_shared_lib.disk_restore_from_disk_to_ram() 

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

    # only make object when tests are active
    if DUMMY_3PHASE_DATA == True or gas_test_mode != p1_telegram_test_lib.NO_GAS_TEST:
        flog.warning(inspect.stack()[0][3]+": test functies geactiveerd ! " )
        p1_test = p1_telegram_test_lib.p1_telegram()
        p1_test.init( flog, configdb=config_db )

    # sets the rate limiting to 1 record per 10 secs or maximum speed processing of P1 telegrams
    p1_port_shared_lib.set_p1_processing_speed( p1_processing=processing_speed , config_db=config_db, flog=flog )

    p1_port_shared_lib.backup_data_to_disk_by_timestamp( statusdb=rt_status_db, flog=flog )

    while check_serial() == False:
        flog.critical(inspect.stack()[0][3]+": seriele poort niet gevonden, is de kabel aangesloten?" )
        time.sleep(10)

    # reset gas per uur waarde als we starten.
    rt_status_db.strset( "0", 50, flog )

    rt_status_db.timestamp( 5,flog )
    #read serial settings from status DB
    serCheckCnt = 0
    check_serial_db_config_settings()
    p1_port_shared_lib.get_country_day_night_mode( status=p1_status ,configdb=config_db, flog=flog )

    p1_port_shared_lib.get_gas_telgram_prefix( status=p1_status ,configdb=config_db, flog=flog )

    flog.info(inspect.stack()[0][3]+": P1 poort instelling baudrate=" + str(ser1.baudrate)+" bytesize=" +str(ser1.bytesize)+" pariteit="+str(ser1.parity)+" stopbits="+str(ser1.stopbits))
    #serOpen(ser1)
    #ser1.flushInput()

    # read GAS value from status database
    #if DUMMY_GAS_MODE_2421 == True or DUMMY_GAS_MODE_2423 == True or DUMMY_GAS_MODE_2430 == True:
    if gas_test_mode > 0:
        print("DUMMY GAS STAAT AAN IS DIT CORRECT?\r")
        flog.warning(inspect.stack()[0][3]+" #############################################")
        flog.warning(inspect.stack()[0][3]+": Dummy gas waarde staat aan met een interval van "+str(p1_test.gas_interval())+" seconden. Zet uit voor productie!")
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

     # check for dummy 3Phase data
    if DUMMY_1SEC_PROCCESSING== True:
        print("DUMMY 1 SECONDEN VERWERKING STAAT AAN?\r")
        flog.warning(inspect.stack()[0][3]+" #############################################")
        flog.warning(inspect.stack()[0][3]+": 1 seconden verwerking staat aan. Zet uit voor productie!")
        flog.warning(inspect.stack()[0][3]+" #### DUMMY 1 SECONDEN  STAAT AAN IS DIT CORRECT? ####")

    # read crc check settings from config
    p1_port_shared_lib.get_P1_crc( status=p1_status ,configdb=config_db, flog=flog )

    # set intial FQDN
    p1_port_shared_lib.fqdn_from_config( verbose=True, configdb=config_db, data_set=json_data, flog=flog )

  
    day_values.init( dbstatus=rt_status_db, dbserial=e_db_serial, flog=flog )

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
                    flog.warning(inspect.stack()[0][3] + ": serieele buffer te groot, gewist! Buffer lengte was " + str( len(serial_buffer) ) )
                    del serial_buffer[:]

                #print  ( serial_buffer )
                #print ( "[*]len="+str(len(serial_buffer)) )

                if line[:1] == '!':
                    #flog.debug(inspect.stack()[0][3]+": serial buffer "+str(serial_buffer))    

                    if DUMMY_3PHASE_DATA == True:
                        #phase3StubInstert( line )
                        p1_test.phase3_stub_instert ( line=line, serialbuffer=serial_buffer )

                    #if DUMMY_GAS_MODE_2421 == True or DUMMY_GAS_MODE_2423 == True or DUMMY_GAS_MODE_2430 == True:
                    if gas_test_mode > 0:
                        #gasStubInstert(line)
                        p1_test.gas_stub_instert( line=line, serialbuffer=serial_buffer, gasmode=gas_test_mode )

                    #flog.info(inspect.stack()[0][3] + " step 0")

                    if processing_speed['max_processing_speed'] == False:
                        
                        # rate limiting of inserts, some smart meters send more then every 10 sec. a telegram.
                        if abs( p1_status['timestamp_last_insert'] - util.getUtcTime()) < 9: # 9 or 10 sec interval is ok.
                            #flog.debug("Te snel een nieuw telegram ontvangen. genegeerd.")
                            del serial_buffer[:]
                            continue

                    #serial_buffer[-1] = "!0F9B"  #DEBUG
                    #print ( "[*] p1 crc check = " + str(p1_crc_check_is_on) )

                    #flog.info(inspect.stack()[0][3] + " step 1")

                    # check for meters that supply a crc value.
                    if len(serial_buffer[ len(serial_buffer)-1 ]) > 3 and p1_status['p1_crc_check_is_on'] == True: # crc telegrams are 7 chars minimal (5+ cr\lf)

                        # check for telegrams with a CRC attached 
                        crc_read = str(serial_buffer[ len(serial_buffer)-1 ][1:5])
                        #flog.debug("CRC in telegram gevonden -> "+crc_read)
                        #print ('[*] crc waarde') 
                        #print crc_read

                        save_crc = serial_buffer[ len(serial_buffer)-1 ]
                        serial_buffer[ len(serial_buffer)-1 ] = '!' # only process to ! not the crc itself
                        strvar = ''.join(serial_buffer)

                        #CRC16().calculate

                        calc_crc = str('{0:0{1}X}'.format(CRC16().calculate( strvar ),4))
                        #flog.debug("Berekende CRC uit telegram -> "+calc_crc )

                        #flog.debug(inspect.stack()[0][3]+": serial buffer "+str(serial_buffer))

                        if ( crc_read == calc_crc ):
                            #flog.debug("CRC is in orde.")
                            #restore CRC to received data
                            serial_buffer[ len(serial_buffer)-1 ] = save_crc
                        else:
                            p1_status['crc_error_cnt'] = p1_status['crc_error_cnt'] + 1
                            #flog.debug("CRC van telegram komt niet overeen. CRC telegram ("+crc_read+"), berekende CRC ("+calc_crc+") niet verwerkt.")
                            del serial_buffer[:]
                            continue

                    #flog.debug(inspect.stack()[0][3]+": serial buffer "+str(serial_buffer))
                    #flog.setLevel(logging.DEBUG)
                    #print('verwerk seriele data.')
                    if DUMMY_1SEC_PROCCESSING == True:
                        stub_serial_buffer = serial_buffer.copy()

                    json_data[apiconst.JSON_API_RM_TMPRTR_IN] ,json_data[apiconst.JSON_API_RM_TMPRTR_OUT] =\
                         p1_port_shared_lib.current_room_temperature( temperaturedb=temperature_db, flog=flog )
                    json_data[apiconst.JSON_API_WM_CNSMPTN_LTR_M3] =\
                         p1_port_shared_lib.current_watermeter_count( configdb=config_db, waterdb=watermeter_db, flog=flog)
                    #print (  serial_buffer )
                    #parseSerBuffer( data_set=base_p1_data, status=p1_status, phase_db_rec=phase_db_record )
                    p1_port_shared_lib.write_p1_telegram_to_ram( buffer=serial_buffer, flog=flog ) 

                    p1_port_shared_lib.parse_serial_buffer( 
                        serialbuffer=serial_buffer, 
                        data_set=base_p1_data, 
                        status=p1_status, 
                        phase_db_rec=phase_db_record, 
                        flog=flog 
                        )
                    update_data_set( 
                        data_set=base_p1_data, 
                        status=p1_status, 
                        phase_db_record=phase_db_record, 
                        flog=flog 
                        )

                    #clean the buffer
                    del serial_buffer[:]
                    p1_port_shared_lib.clear_data_buffer( buffer=base_p1_data )

            else:
               
                if processing_speed['max_processing_speed'] == True:
                    if DUMMY_1SEC_PROCCESSING == True:
                        if stub_serial_buffer != []:
                            # print ( "serial_buffer = " + str(stub_serial_buffer) )
                            serial_buffer = stub_serial_buffer.copy()
                            json_data[apiconst.JSON_API_RM_TMPRTR_IN] ,json_data[apiconst.JSON_API_RM_TMPRTR_OUT] =\
                                 p1_port_shared_lib.current_room_temperature( temperaturedb=temperature_db, flog=flog )
                            json_data[apiconst.JSON_API_WM_CNSMPTN_LTR_M3] =\
                                 p1_port_shared_lib.current_watermeter_count( configdb=config_db, waterdb=watermeter_db, flog=flog)

                            #parseSerBuffer( data_set=base_p1_data, status=p1_status, phase_db_rec=phase_db_record )
                            p1_port_shared_lib.write_p1_telegram_to_ram( buffer=serial_buffer, flog=flog ) 
                            
                            p1_port_shared_lib.parse_serial_buffer( 
                                serialbuffer=serial_buffer, 
                                data_set=base_p1_data, 
                                status=p1_status, 
                                phase_db_rec=phase_db_record, 
                                flog=flog 
                                )
                            update_data_set( 
                                data_set=base_p1_data, 
                                status=p1_status, 
                                phase_db_record=phase_db_record, 
                                flog=flog 
                                )

                time.sleep( 0.1 )
                serCheckCnt = serCheckCnt + 1
                if serCheckCnt > 300: #check updates every 30 seconds.
                    
                    # perodic check and change of fqdn.
                    # set intial FQDN
                    p1_port_shared_lib.fqdn_from_config( verbose=False, configdb=config_db, data_set=json_data, flog=flog )

                    p1_port_shared_lib.backup_data_to_disk_by_timestamp( statusdb=rt_status_db, flog=flog )

                    #print "serial interval check"
                    #############################################################################################
                    # changed in version > 1.3.1 because of the possible high frequency of updates. use less    #
                    # often to remove stress on the database.                                                   #
                    #############################################################################################
                    p1_port_shared_lib.delete_serial_records(   p1_processing=processing_speed, serial_db=e_db_serial, flog=flog )
                    p1_port_shared_lib.delete_phase_record(     p1_processing=processing_speed, phase_db=fase_db,      flog=flog )

                    p1_port_shared_lib.set_p1_processing_speed( p1_processing=processing_speed ,config_db=config_db,flog=flog )

                    check_serial_db_config_settings()

                    p1_port_shared_lib.get_country_day_night_mode( status=p1_status ,configdb=config_db, flog=flog )

                    p1_port_shared_lib.get_gas_telgram_prefix( status=p1_status ,configdb=config_db, flog=flog )
                    #checkCRCsettings()
                    p1_port_shared_lib.get_P1_crc( status=p1_status ,configdb=config_db, flog=flog )
                    serCheckCnt=0

                if abs( p1_status['timestamp_last_insert'] - util.getUtcTime()) > 51:
                    if p1_status['p1_record_is_ok'] == 1:
                        flog.warning(inspect.stack()[0][3]+": geen P1 record te lezen.")
                    p1_status['p1_record_is_ok'] = 0
                    rt_status_db.strset( str( p1_status['p1_record_is_ok'] ), 46, flog ) # P1 data is not ok recieved

                # print abs(last_crc_check_timestamp - getUtcTime()) , " cnt=", crc_error_cnt
                # crc error messages, if any.
                if p1_status['p1_crc_check_is_on'] == True:
                    if abs(p1_status['last_crc_check_timestamp'] - util.getUtcTime()) > 900:  #check every 15 minutes, to limit log entries.
                        p1_status['last_crc_check_timestamp']  = util.getUtcTime()
                        if p1_status['crc_error_cnt'] > 0: 
                            flog.warning("aantal P1 telegram crc fouten gevonden in de afgelopen minuut = " + str( p1_status['crc_error_cnt']) )
                            p1_status['crc_error_cnt'] = 0

        except Exception as e:
            flog.warning( inspect.stack()[0][3] + ": fout bij het wachten op seriele gegevens. Error=" + str( e.args ) )
            check_serial()
            time.sleep( 1 )


def exist_serial_device( tty ):
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

def check_serial():
    global ser1

    for tty in ser_devices_list:

        if exist_serial_device( tty ): # check if device is known to the os.
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

##################################################################
# grouping of functions because it same set of calls is done for #
# debug / testing of functions                                   #
# ################################################################ 
def update_data_set( data_set=None, status=None, phase_db_record=None, flog=None ):

    if p1_port_shared_lib.record_sanity_check( data_set=data_set, status=status, flog=flog ) == True:

        p1_port_shared_lib.insert_db_serial_record( data_set=data_set, status=status, dbstatus=rt_status_db, dbserial=e_db_serial, flog=flog )

        # max waarden kW bijwerken
        #p1_port_shared_lib.max_kW_day_value( dbstatus=rt_status_db, dbserial=e_db_serial, flog=flog )
        day_values.kWupdateStatusDb()

        # dag waarden KWH verbruikt bijwerken
        p1_port_shared_lib.max_kWh_day_value( data_set=data_set, dbstatus=rt_status_db, dbserial=e_db_serial, flog=flog )

        #updateJsonData() 
        p1_port_shared_lib.update_json_data( jsondata=json_data, p1data=data_set )

        p1_port_shared_lib.write_p1_json_to_ram(
            data=json_data,
            flog=flog,
            sysid=system_id
        )

        status['dbx_utc_ok_timestamp'] = p1_port_shared_lib.write_p1_json_dbx_folder( 
            configdb=config_db,
            data=json_data,
            flog=flog,
            sysid=system_id,
            utc_ok_timestamp=status['dbx_utc_ok_timestamp']
        )

        if status['gas_present_in_serial_data'] == True:
            p1_port_shared_lib.instert_db_gas_value( data_set=data_set, status=p1_status, statusdb=rt_status_db, flog=flog )

        p1_port_shared_lib.write_phase_status_to_db( phase_db_rec=phase_db_record, statusdb=rt_status_db, flog=flog )
        p1_port_shared_lib.write_phase_history_values_to_db( phase_db_rec=phase_db_record, configdb=config_db, phasedb=fase_db, flog=flog )
        p1_port_shared_lib.clear_data_buffer( buffer=phase_db_record )

    else:
        flog.error(inspect.stack()[0][3]+": p1 bericht verworpen wegens fout.")
    #flog.setLevel(logging.INFO)

def check_serial_db_config_settings():
    global ser1
    #global day_night_mode 
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

def save_exit(signum, frame):
    #setFileFlags()
    signal.signal(signal.SIGINT, original_sigint)
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    os.umask( 0o002 )
    flog = logger.fileLogger( const.DIR_FILELOG+prgname+".log", prgname )   
    flog.setLevel( logger.logging.INFO )
    flog.consoleOutputOn( True )
    
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal( signal.SIGINT, save_exit )
    main_prod()

