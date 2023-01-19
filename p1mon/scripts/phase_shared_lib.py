####################################################################
# shared lib for processing the phase related data                 #
####################################################################

from asyncio.log import logger
import const
import datetime
import logger
import inspect
import time
import util
import os
import process_lib

#############################################################
# class to send email of the high or low voltage treshold   #
# reached.                                                  #
#############################################################
class VoltageMinMaxNotification():

    def __init__( self, configdb=None, phasedb=None, flog=None ):
        self.configdb = configdb
        self.phasedb  = phasedb
        self.flog     = flog
        self.did_send_high_message = False
        self.did_send_low_message  = False
        
        
    def run( self ):

        try:
            _id, on, _label = self.configdb.strget( 175, self.flog )
            if int(on) != 1:
                self.flog.debug( __class__.__name__ + ": email voor controle min en max spanning staat uit, geen actie.")  
                return 
        except:
            return

        try:

            # construct subject.
            _id, subject, _label = self.configdb.strget( 69, self.flog )
            if len( subject ) < 1:
                subject =  const.DEFAULT_EMAIL_NOTIFICATION

            _id, v_max, _label = self.configdb.strget( 173, self.flog )
            _id, v_min, _label = self.configdb.strget( 174, self.flog )
            v_max = float( v_max )
            v_min = float( v_min )

            t = time.localtime()
            timestring = "%04d-%02d-%02d %02d:%02d:%02d"% ( t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec )
    
            sql = "select max(L1_V),max(L2_V),max(L3_V),min(L1_V),min(L2_V),min(L3_V) from " + const.DB_FASE_REALTIME_TAB + " where substr(timestamp,1,16) = '" + timestring[0:16] + "';"
            #self.flog.debug( __class__.__name__ + ": max-min sql = "  + str(sql) )
          
            rec = self.phasedb.select_rec( sql )
            #self.flog.debug( __class__.__name__ + ": sql select rec ="  + str(rec) )

            # check ik the record has valid (not None) data.
            for i in range( len(rec[0]) ):
                if rec[0][i] == None:
                    self.flog.debug( __class__.__name__ + ": SQL select bevat geen valide data, er wordt niets gedaan." )
                    return

            max_L1 = float(rec[0][0])
            max_L2 = float(rec[0][1])
            max_L3 = float(rec[0][2])
            min_L1 = float(rec[0][3])
            min_L2 = float(rec[0][4])
            min_L3 = float(rec[0][5]) 

            # for the min values we filter the 0 values because they are a default value
            # else the minus value will always be zero (0)
            min_list = list()
            if ( min_L1 != 0 ):
                min_list.append( min_L1 )
            if ( min_L2 != 0 ):
                min_list.append( min_L2 )
            if ( min_L3 != 0 ):
                min_list.append( min_L3 )

            # get the max of min values over three phases.
            max_total = max( max_L1, max_L2, max_L3 )
            min_total = min( min_list )

            #print ( max_total, min_total, v_max, v_min )

            # high threshold check 
            if max_total >= v_max and self.did_send_high_message == False:
                self.flog.debug( inspect.stack()[0][3] + ": SEND(1) max Lx waarden " + str( max_total) + " zijn groter dan de hoog grenswaarde van " + str(v_max) )
                l1_text = 'L1: ' + str(max_L1) + 'V'
                l2_text = 'L2: ' + str(max_L2) + 'V'
                l3_text = 'L3: ' + str(max_L3) + 'V'
                upper_text = 'Ingestelde bovengrenswaarde: ' + str(v_max) + ' V'
                subject_str = ' -subject "' + subject + ' (bovengrens fase spanning bereikt)."'
                messagetext = ' -msgtext "' + timestring + ': bovengrens van de spanning van een van de drie fasen bereikt.\n' + l1_text  + '\n' + l2_text + '\n' +  l3_text + '\n' + upper_text + '\n"'
                messagehtml = ' -msghtml "<p>' + timestring + ': bovengrens van de spanning van een van de drie fasen bereikt.</p><p>' + l1_text  + '<br>' + l2_text + '<br>' +  l3_text + '<br>' + upper_text + '</p>"'
                #if os.system( '/p1mon/scripts/P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' ) > 0:
                #    self.flog.error( inspect.stack()[0][3]+" email notificatie bovengrenswaarde gefaald(1)." )
                #else:
                #    self.did_send_high_message = True
                #    self.flog.info( inspect.stack()[0][3] + ": bovengrens fase spanning bereikt (" + str( max_total ) + ") is groter dan de hoogste grenswaarde van " + str(v_max) )
            
                #./pythonlaunch.sh P1SmtpCopy.py '-subject "test2 wil" -msgtext "a b c"'

                #cmd = '/p1mon/scripts/pythonlaunch.sh P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' # 2.0.0 upgrade
                cmd = "/p1mon/scripts/pythonlaunch.sh P1SmtpCopy.py '" + subject_str + messagetext + messagehtml + "' >/dev/null 2>&1"

                self.flog.debug( __class__.__name__ + ": mail = " + cmd )
                r = process_lib.run_process( 
                    cms_str = cmd,
                    use_shell=True,
                    give_return_value=True,
                    flog=self.flog 
                )
                if r[2] > 0:
                     self.flog.error( __class__.__name__ + " email notificatie bovengrenswaarde gefaald(1)." )
                else:
                    self.did_send_high_message = True
                    self.flog.info( __class__.__name__ + ": bovengrens fase spanning bereikt (" + str( max_total ) + ") is groter dan de hoogste grenswaarde van " + str(v_max) )

            # high treshold reset check.
            if max_total < v_max and self.did_send_high_message == True:
                self.flog.debug( inspect.stack()[0][3] + ": SEND(2) max Lx waarden " + str( max_total) + " is kleiner dan de hoog grenswaarde van " + str(v_max) )
                self.did_send_high_message = False
                l1_text = 'L1: ' + str(max_L1) + 'V'
                l2_text = 'L2: ' + str(max_L2) + 'V'
                l3_text = 'L3: ' + str(max_L3) + 'V'
                upper_text = 'Ingestelde bovengrenswaarde: ' + str(v_max) + ' V'
                subject_str = ' -subject "' + subject + ' (bovengrens fase spanning opgeheven)."'
                messagetext = ' -msgtext "' + timestring + ': bovengrens van de spanning van een van de drie fasen niet langer van toepassing.\n' + l1_text  + '\n' + l2_text + '\n' +  l3_text + '\n' + upper_text + '\n"'
                messagehtml = ' -msghtml "<p>' + timestring + ': bovengrens van de spanning van een van de drie fasen niet langer van toepassing.</p><p>' + l1_text  + '<br>' + l2_text + '<br>' +  l3_text + '<br>' + upper_text + '</p>"'
                #if os.system( '/p1mon/scripts/P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' ) > 0:
                #    self.flog.error( inspect.stack()[0][3]+" email notificatie bovengrenswaarde gefaald(2)." )
                #else:
                #    self.did_send_high_message = False
                #    self.flog.info( inspect.stack()[0][3] + ": bovengrens fase spanning niet langer van toepassing (" + str( max_total ) + ") is kleiner dan de hoogste grenswaarde van " + str(v_max) )

                cmd = '/p1mon/scripts/pythonlaunch.sh P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' # 2.0.0 upgrade
                self.flog.debug( inspect.stack()[0][3] + ": mail = " + cmd )
                r = process_lib.run_process( 
                    cms_str = cmd,
                    use_shell=True,
                    give_return_value=True,
                    flog=self.flog 
                )
                if r[2] > 0:
                    self.flog.error( inspect.stack()[0][3]+" email notificatie bovengrenswaarde gefaald(2)." )
                else:
                    self.did_send_high_message = False
                    self.flog.info( inspect.stack()[0][3] + ": bovengrens fase spanning niet langer van toepassing (" + str( max_total ) + ") is kleiner dan de hoogste grenswaarde van " + str(v_max) )

            # low threshold check 
            if min_total <= v_min and self.did_send_low_message == False:
                self.flog.debug( inspect.stack()[0][3] + ": SEND(3) min Lx waarden " + str( max_total) + " is kleiner dan de laag grenswaarde van " + str(v_min) )
                l1_text = 'L1: ' + str(min_L1) + 'V'
                l2_text = 'L2: ' + str(min_L2) + 'V'
                l3_text = 'L3: ' + str(min_L3) + 'V'
                lower_text = 'Ingestelde ondergrenswaarde: ' + str(v_min) + ' V'
                subject_str = ' -subject "' + subject + ' (ondergrens fase spanning bereikt)."'
                messagetext = ' -msgtext "' + timestring + ': ondergrens van de spanning van een van de drie fasen bereikt.\n' + l1_text  + '\n' + l2_text + '\n' +  l3_text + '\n' + lower_text + '\n"'
                messagehtml = ' -msghtml "<p>' + timestring + ': ondergrens van de spanning van een van de drie fasen bereikt.</p><p>' + l1_text  + '<br>' + l2_text + '<br>' +  l3_text + '<br>' + lower_text + '</p>"'
                #if os.system( '/p1mon/scripts/P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' ) > 0:
                #    self.flog.error( inspect.stack()[0][3]+" email notificatie ondergrenswaarde gefaald(1)." )
                #else:
                #    self.did_send_low_message = True
                #    self.flog.info( inspect.stack()[0][3] + ": ondergrens fase spanning bereikt (" + str( min_total ) + ") is kleiner dan de lage grenswaarde " + str(v_min) )

                #cmd = '/p1mon/scripts/pythonlaunch.sh P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' # 2.0.0 upgrade
                cmd = "/p1mon/scripts/pythonlaunch.sh P1SmtpCopy.py '" + subject_str + messagetext + messagehtml + "' >/dev/null 2>&1"
                self.flog.debug( __class__.__name__ + ": mail = " + cmd )
                r = process_lib.run_process( 
                    cms_str = cmd,
                    use_shell=True,
                    give_return_value=True,
                    flog=self.flog 
                )
                if r[2] > 0:
                     self.flog.error( __class__.__name__ + " email notificatie ondergrenswaarde gefaald(1)." )
                else:
                    self.did_send_low_message = True
                    self.flog.info( __class__.__name__ + ": ondergrens fase spanning bereikt (" + str( min_total ) + ") is kleiner dan de lage grenswaarde " + str(v_min) )

             # low threshold reset check 
            if min_total > v_min and self.did_send_low_message == True:
                self.flog.debug( __class__.__name__ + ": SEND(4) min Lx waarden " + str( max_total ) + " zijn groter dan de laag grenswaarde van " + str(v_min) )
                l1_text = 'L1: ' + str(min_L1) + 'V'
                l2_text = 'L2: ' + str(min_L2) + 'V'
                l3_text = 'L3: ' + str(min_L3) + 'V'
                lower_text = 'Ingestelde ondergrenswaarde: ' + str(v_min) + ' V'
                subject_str = ' -subject "' + subject + ' (ondergrens fase spanning opgeheven)."'
                messagetext = ' -msgtext "' + timestring + ': ondergrens van de spanning van een van de drie fasen niet langer van toepassing.\n' + l1_text  + '\n' + l2_text + '\n' +  l3_text + '\n' + lower_text + '\n"'
                messagehtml = ' -msghtml "<p>' + timestring + ': ondergrens van de spanning van een van de drie fasen fasen niet langer van toepassing.</p><p>' + l1_text  + '<br>' + l2_text + '<br>' +  l3_text + '<br>' + lower_text + '</p>"'
                #if os.system( '/p1mon/scripts/P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' ) > 0:
                #    self.flog.error( inspect.stack()[0][3]+" email notificatie ondergrenswaarde gefaald(1)." )
                #else:
                #    self.did_send_low_message = False
                #    self.flog.info( inspect.stack()[0][3] + ": ondergrens van de spanning van een van de drie fasen fasen niet langer van toepassing (" + str( min_total ) + ") is groter dan de lage grenswaarde " + str(v_min) )

                #cmd = '/p1mon/scripts/pythonlaunch.sh P1SmtpCopy.py ' + subject_str + messagetext + messagehtml + ' >/dev/null 2>&1' # 2.0.0 upgrade
                cmd = "/p1mon/scripts/pythonlaunch.sh P1SmtpCopy.py '" + subject_str + messagetext + messagehtml + "' >/dev/null 2>&1"
                self.flog.debug( __class__.__name__ + ": mail = " + cmd )
                r = process_lib.run_process( 
                    cms_str = cmd,
                    use_shell=True,
                    give_return_value=True,
                    flog=self.flog 
                )
                if r[2] > 0:
                     self.flog.error( __class__.__name__ + " email notificatie ondergrenswaarde gefaald(1)." )
                else:
                    self.did_send_low_message = False
                    self.flog.info( __class__.__name__ + ": ondergrens van de spanning van een van de drie fasen fasen niet langer van toepassing (" + str( min_total ) + ") is groter dan de lage grenswaarde " + str(v_min) )

        except Exception as e:
            self.flog.error( __class__.__name__ + ": error " + str(e) )



#############################################################
# reset the data structure so every day start with zero or  #
# max values                                                #
#############################################################
def _init_min_max_record( minmaxrec=None, flog=None , timestamp=None): 
    flog.debug( inspect.stack()[0][3] + ": reset data structure phase_db_min_max_record." )
    minmaxrec['timestamp'] = timestamp;
    minmaxrec['max_consumption_L1_kW'] = 0 
    minmaxrec['max_consumption_L2_kW'] = 0
    minmaxrec['max_consumption_L3_kW'] = 0
    minmaxrec['max_production_L1_kW'] = 0
    minmaxrec['max_production_L2_kW'] = 0 
    minmaxrec['max_production_L3_kW'] = 0
    minmaxrec['max_L1_V'] = 0
    minmaxrec['max_L2_V'] = 0
    minmaxrec['max_L3_V'] = 0
    minmaxrec['max_L1_A'] = 0
    minmaxrec['max_L2_A'] = 0
    minmaxrec['max_L3_A'] = 0

    minmaxrec['min_consumption_L1_kW'] = const.NOT_SET
    minmaxrec['min_consumption_L2_kW'] = const.NOT_SET
    minmaxrec['min_consumption_L3_kW'] = const.NOT_SET
    minmaxrec['min_production_L1_kW']  = const.NOT_SET
    minmaxrec['min_production_L2_kW']  = const.NOT_SET
    minmaxrec['min_production_L3_kW']  = const.NOT_SET
    minmaxrec['min_L1_V']              = const.NOT_SET
    minmaxrec['min_L2_V']              = const.NOT_SET
    minmaxrec['min_L3_V']              = const.NOT_SET
    minmaxrec['min_L1_A']              = const.NOT_SET
    minmaxrec['min_L2_A']              = const.NOT_SET
    minmaxrec['min_L3_A']              = const.NOT_SET

#############################################################
# return True if one of the DB record field is > or <       #
#############################################################
def _check_db_for_update( rec=None, minmaxrec=None ):

    if   float(rec[0][0]) > minmaxrec['max_consumption_L1_kW']: 
        return True
    elif float(rec[0][1]) > minmaxrec['max_consumption_L2_kW']: 
        return True
    elif float(rec[0][2]) > minmaxrec['max_consumption_L3_kW']: 
        return True 
    elif float(rec[0][3]) > minmaxrec['max_production_L1_kW']: 
        return True
    elif float(rec[0][4]) > minmaxrec['max_production_L2_kW']: 
        return True 
    elif float(rec[0][5]) > minmaxrec['max_production_L3_kW']: 
        return True 
    elif float(rec[0][6]) > minmaxrec['max_L1_V']: 
        return True
    elif float(rec[0][7]) > minmaxrec['max_L2_V']: 
        return True
    elif float(rec[0][8]) > minmaxrec['max_L3_V']: 
        return True
    elif float(rec[0][9]) > minmaxrec['max_L1_A']: 
        return True
    elif float(rec[0][10]) > minmaxrec['max_L2_A']: 
        return True
    elif float(rec[0][11]) > minmaxrec['max_L3_A']: 
        return True
    elif float(rec[0][12]) < minmaxrec['min_consumption_L1_kW']: 
        return True
    elif float(rec[0][13]) < minmaxrec['min_consumption_L2_kW']: 
        return True
    elif float(rec[0][14]) < minmaxrec['min_consumption_L3_kW']: 
        return True
    elif float(rec[0][15]) < minmaxrec['min_production_L1_kW']: 
        return True
    elif float(rec[0][16]) < minmaxrec['min_production_L2_kW']: 
        return True
    elif float(rec[0][17]) < minmaxrec['min_production_L3_kW']: 
        return True
    elif float(rec[0][18]) < minmaxrec['min_L1_V']: 
        return True
    elif float(rec[0][19]) < minmaxrec['min_L2_V']: 
        return True
    elif float(rec[0][20]) < minmaxrec['min_L3_V']: 
        return True
    elif float(rec[0][21]) < minmaxrec['min_L1_A']:
        return True
    elif float(rec[0][22]) < minmaxrec['min_L2_A']:
        return True
    elif float(rec[0][23]) < minmaxrec['min_L3_A']:
        return True

    return False


def delete_min_max_records( phasedb=None, flog=None , retentiondays=1096, timestamp=None):

    try:
        # dagen records verwijderen
        sql_del_str = "delete from " + const.DB_FASE_MINMAX_DAG_TAB + " where timestamp <  '"+\
        str(datetime.datetime.strptime(timestamp,"%Y-%m-%d") - datetime.timedelta(days=retentiondays))+"'"
    
        flog.debug(inspect.stack()[0][3]+": sql="+sql_del_str)
        phasedb.excute( sql_del_str )
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": verwijderen dag records die ouder zijn dan " + str(retentiondays) + " dagen, delete gefaald. Melding="+str(e.args[0]) )


#############################################################
# update the V,I and W phase minimal and maximal day values #
# in the database and                                       #
#############################################################
def write_phase_min_max_day_values_to_db( minmaxrec=None, configdb=None, phasedb=None, flog=None, timestamp=None):

    # only add data when fase info is set to on.
    if configdb.strget( 119 ,flog )[1] == "1":
        try:

            # check if the min-max-rec is set or of the day has changed.

            if minmaxrec['timestamp'] != timestamp[0:10]:
                _init_min_max_record( minmaxrec=minmaxrec, flog=flog ,timestamp=timestamp[0:10] )

            flog.debug( inspect.stack()[0][3] + ": fase informatie verwerken voor timestamp " + str(timestamp) )
            sql = "select max(VERBR_L1_KW),max(VERBR_L2_KW),max(VERBR_L3_KW),max(GELVR_L1_KW),max(GELVR_L2_KW),max(GELVR_L3_KW),max(L1_V),max(L2_V),max(L3_V),max(L1_A), max(L2_A),max(L3_A),min(VERBR_L1_KW),min(VERBR_L2_KW), min(VERBR_L3_KW),min(GELVR_L1_KW),min(GELVR_L2_KW),min(GELVR_L3_KW),min(L1_V),min(L2_V),min(L3_V),min(L1_A),min(L2_A), min(L3_A) from " + const.DB_FASE_REALTIME_TAB + " where substr(timestamp,1,10) = '" + timestamp[0:10] + "';"
            flog.debug( inspect.stack()[0][3] + ": max-min sql = "  + str(sql) )

            rec=phasedb.select_rec( sql )
            flog.debug( inspect.stack()[0][3] + ": sql select rec ="  + str(rec) )

            # check if any of the values are changed, if so do an DB update
            # else don't te limit load on the database
            doupdate = _check_db_for_update( rec=rec, minmaxrec=minmaxrec )

            flog.debug( inspect.stack()[0][3] + ": do update = "  + str(doupdate) )

            if ( doupdate == True ):

                minmaxrec['max_consumption_L1_kW'] = float(rec[0][0])
                minmaxrec['max_consumption_L2_kW'] = float(rec[0][1])
                minmaxrec['max_consumption_L3_kW'] = float(rec[0][2])

                minmaxrec['max_production_L1_kW'] = float(rec[0][3])
                minmaxrec['max_production_L2_kW'] = float(rec[0][4])
                minmaxrec['max_production_L3_kW'] = float(rec[0][5])

                minmaxrec['max_L1_V'] = float(rec[0][6])
                minmaxrec['max_L2_V'] = float(rec[0][7])
                minmaxrec['max_L3_V'] = float(rec[0][8])

                minmaxrec['max_L1_A'] = float(rec[0][9])
                minmaxrec['max_L2_A'] = float(rec[0][10])
                minmaxrec['max_L3_A'] = float(rec[0][11])

                minmaxrec['min_consumption_L1_kW'] = float(rec[0][12])
                minmaxrec['min_consumption_L2_kW'] = float(rec[0][13])
                minmaxrec['min_consumption_L3_kW'] = float(rec[0][14])

                minmaxrec['min_production_L1_kW'] = float(rec[0][15])
                minmaxrec['min_production_L2_kW'] = float(rec[0][16])
                minmaxrec['min_production_L3_kW'] = float(rec[0][17])

                minmaxrec['min_L1_V'] = float(rec[0][18])
                minmaxrec['min_L2_V'] = float(rec[0][19])
                minmaxrec['min_L3_V'] = float(rec[0][20])

                minmaxrec['min_L1_A'] =  float(rec[0][21])
                minmaxrec['min_L2_A'] =  float(rec[0][22])
                minmaxrec['min_L3_A'] =  float(rec[0][23])

                # create update / insert sql
                sqlupdate = "replace into " + const.DB_FASE_MINMAX_DAG_TAB + \
                " (TIMESTAMP,\
                MAX_VERBR_L1_KW, MAX_VERBR_L2_KW, MAX_VERBR_L3_KW, \
                MAX_GELVR_L1_KW, MAX_GELVR_L2_KW, MAX_GELVR_L3_KW,\
                MAX_L1_V, MAX_L2_V, MAX_L3_V, \
                MAX_L1_A, MAX_L2_A, MAX_L3_A, \
                MIN_VERBR_L1_KW, MIN_VERBR_L2_KW, MIN_VERBR_L3_KW, \
                MIN_GELVR_L1_KW, MIN_GELVR_L2_KW, MIN_GELVR_L3_KW, \
                MIN_L1_V, MIN_L2_V, MIN_L3_V, \
                MIN_L1_A, MIN_L2_A, MIN_L3_A \
                ) values ('" + \
                str( timestamp[0:10] ) + " 00:00:00'," + \
                str(minmaxrec['max_consumption_L1_kW']) + "," + \
                str(minmaxrec['max_consumption_L2_kW']) + "," + \
                str(minmaxrec['max_consumption_L3_kW']) + "," + \
                str(minmaxrec['max_production_L1_kW']) + "," + \
                str(minmaxrec['max_production_L2_kW']) + "," + \
                str(minmaxrec['max_production_L3_kW']) + "," + \
                str(minmaxrec['max_L1_V']) + "," + \
                str(minmaxrec['max_L2_V']) + "," + \
                str(minmaxrec['max_L3_V']) + "," + \
                str(minmaxrec['max_L1_A']) + "," + \
                str(minmaxrec['max_L2_A']) + "," + \
                str(minmaxrec['max_L3_A']) + "," + \
                str(minmaxrec['min_consumption_L1_kW']) + "," + \
                str(minmaxrec['min_consumption_L2_kW']) + "," + \
                str(minmaxrec['min_consumption_L3_kW']) + "," + \
                str(minmaxrec['min_production_L1_kW']) + "," + \
                str(minmaxrec['min_production_L2_kW']) + "," + \
                str(minmaxrec['min_production_L3_kW']) + "," + \
                str(minmaxrec['min_L1_V']) + "," + \
                str(minmaxrec['min_L2_V']) + "," + \
                str(minmaxrec['min_L3_V']) + "," + \
                str(minmaxrec['min_L1_A']) + "," + \
                str(minmaxrec['min_L2_A']) + "," + \
                str(minmaxrec['min_L3_A']) + \
                ");"

                #flog.setLevel( logger.logging.DEBUG )
                sqlupdate = " ".join(sqlupdate.split())
                flog.debug( inspect.stack()[0][3] + ": update sql  = "  + str(sqlupdate) )
                phasedb.excute( sqlupdate )
                #flog.setLevel( logger.logging.INFO )

                delete_min_max_records( phasedb=phasedb, flog=flog , retentiondays=1096, timestamp=timestamp[0:10])

        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": update/insert gefaald. Melding=" + str(e.args[0]) )
    else:
         flog.debug( inspect.stack()[0][3] + ": fase informatie verwerken staat uit." )


#############################################################
# write a record to the phase datebase en deletes old       #
# records that are passed the rentention time               #
#############################################################
def write_phase_history_values_to_db( phase_db_rec=None, configdb=None, phasedb=None, flog=None ):

    phase_db_rec['timestamp'] = util.mkLocalTimeString()

    # only add data when fase info is set to on.
    if configdb.strget( 119 ,flog )[1] == "1": 
        try:

            sqlstr = "insert or replace into " + const.DB_FASE_REALTIME_TAB + " (TIMESTAMP, VERBR_L1_KW,VERBR_L2_KW,VERBR_L3_KW,GELVR_L1_KW,GELVR_L2_KW,GELVR_L3_KW,L1_V,L2_V,L3_V,L1_A,L2_A,L3_A) VALUES ('" + \
                str( phase_db_rec['timestamp'] )         + "'," + \
                str( phase_db_rec['consumption_L1_kW'] ) + "," + \
                str( phase_db_rec['consumption_L2_kW'] ) + "," + \
                str( phase_db_rec['consumption_L3_kW'] ) + "," + \
                str( phase_db_rec['production_L1_kW'] )  + "," + \
                str( phase_db_rec['production_L2_kW'] )  + "," + \
                str( phase_db_rec['production_L3_kW'] )  + "," + \
                str( phase_db_rec['L1_V'] )              + ", " + \
                str( phase_db_rec['L2_V'] )              + ", " + \
                str( phase_db_rec['L3_V'] )              + ", " + \
                str( phase_db_rec['L1_A'] )              + ", " + \
                str( phase_db_rec['L2_A'] )              + ", " + \
                str( phase_db_rec['L3_A'] )              + ")"

            sqlstr = " ".join( sqlstr.split() )
            flog.debug( inspect.stack()[0][3] + ": SQL =" + str(sqlstr) )
            phasedb.insert_rec(sqlstr)

        except Exception as e:
            flog.error( inspect.stack()[0][3] + ": Insert gefaald. Melding=" + str(e.args[0]) )

#############################################################
# update the status database of the current phase data      #
#############################################################
def write_phase_status_to_db( phase_db_rec=None, statusdb=None, flog=None):

    try:
        
        if float( phase_db_rec['consumption_L1_kW'] ) != const.NOT_SET:
            statusdb.strset( float( phase_db_rec['consumption_L1_kW'] ) ,74, flog )
        else:
            statusdb.strset( '0.0' ,74, flog )
            phase_db_rec['consumption_L1_kW'] = 0

        if float( phase_db_rec['consumption_L2_kW'] ) !=  const.NOT_SET:
            statusdb.strset( float( phase_db_rec['consumption_L2_kW'] ) ,75, flog )

        else:
            statusdb.strset( '0.0' ,75, flog )
            phase_db_rec['consumption_L2_kW'] = 0

        if float( phase_db_rec['consumption_L3_kW'] ) !=  const.NOT_SET:
            statusdb.strset( float( phase_db_rec['consumption_L3_kW'] ) ,76, flog )
        else:
            statusdb.strset( '0.0' ,76, flog )
            phase_db_rec['consumption_L3_kW'] = 0

        if float( phase_db_rec['production_L1_kW'] ) !=  const.NOT_SET:
            statusdb.strset( float( phase_db_rec['production_L1_kW'] ) ,77, flog )
        else:
            statusdb.strset( '0.0' ,77, flog )
            phase_db_rec['production_L1_kW'] = 0

        if float( phase_db_rec['production_L2_kW'] ) !=  const.NOT_SET:
            statusdb.strset( float( phase_db_rec['production_L2_kW'] ) ,78, flog )
        else:
            statusdb.strset( '0.0' ,78, flog )
            phase_db_rec['production_L2_kW'] = 0

        if float( phase_db_rec['production_L3_kW'] ) !=  const.NOT_SET:
            statusdb.strset( float( phase_db_rec['production_L3_kW'] ) ,79, flog )
        else:
            statusdb.strset( '0.0' ,79, flog )
            phase_db_rec['production_L3_kW'] = 0

        if float( phase_db_rec['L1_V'] ) != const.NOT_SET:
            statusdb.strset( float( phase_db_rec['L1_V'] ) ,103, flog )
        else:
            statusdb.strset( '0.0' ,103, flog )
            phase_db_rec['L1_V'] = 0

        if float( phase_db_rec['L2_V'] ) != const.NOT_SET:
            statusdb.strset( float( phase_db_rec['L2_V'] ) ,104, flog )
        else:
            statusdb.strset( '0.0' ,104, flog )
            phase_db_rec['L2_V'] = 0

        if float( phase_db_rec['L3_V'] ) != const.NOT_SET:
            statusdb.strset( float( phase_db_rec['L3_V'] ) ,105, flog )
        else:
            statusdb.strset( '0.0' ,105, flog )
            phase_db_rec['L3_V'] = 0

        if float( phase_db_rec['L1_A'] ) != const.NOT_SET:
            statusdb.strset( float( phase_db_rec['L1_A'] ) ,100, flog )
        else:
            statusdb.strset( '0.0' ,100, flog )
            phase_db_rec['L1_A'] = 0

        if float( phase_db_rec['L2_A'] ) != const.NOT_SET:
            statusdb.strset( float( phase_db_rec['L2_A'] ) ,101, flog )
        else:
            statusdb.strset( '0.0' ,101, flog )
            phase_db_rec['L2_A'] = 0

        if float( phase_db_rec['L3_A'] ) != const.NOT_SET:
            statusdb.strset( float( phase_db_rec['L3_A'] ) ,102, flog )
        else:
            statusdb.strset( '0.0' ,102, flog )
            phase_db_rec['L3_A'] = 0

        statusdb.timestamp( 106, flog ) # update timestamp of phase values in status database.

    except Exception as e:
            flog.error( inspect.stack()[0][3] + ": probleem met update van fase data naar status database =" + str(e.args[0]) )

#############################################################
# deletes the records in the phase data base based on the   #
# number of retention day's. currently 7 days for 10 sec    #
# processing and 1 day for 1 second processing              #
#############################################################
def delete_phase_record( p1_processing=None, phase_db=None, flog=None ):

    try:

        timestampstr = util.mkLocalTimeString()

        #if ( int( phase_db_rec['timestamp'][14:16] )%5 ) == 0: # delete every 5 minutes and not every record to limit DB load and fragmentaion.
        
        sql_del_str = "delete from " + const.DB_FASE_REALTIME_TAB + " where timestamp <  '"+\
                str( datetime.datetime.strptime( \
                timestampstr, "%Y-%m-%d %H:%M:%S") -\
                datetime.timedelta( days=p1_processing['max_days_db_data_retention'] )) + "'"

        flog.debug( inspect.stack()[0][3] + ": sql=" + sql_del_str )

        phase_db.del_rec(sql_del_str)

    except Exception as e:
        flog.error( inspect.stack()[0][3] + ": verwijderen fase records ,delete gefaald. Melding=" + str(e.args[0]) )
