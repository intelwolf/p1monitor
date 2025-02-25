####################################################################
# shared lib for processing the power related data                 #
####################################################################

from ast import Raise
from urllib.parse import parse_qsl
import const
import datetime
import inspect
import time
import process_lib

#############################################################
# class to send email of the high or low watt treshold      #
# reached.                                                  #
#############################################################
class WattTresholdNotification():

    def __init__( self, configdb=None, serialdb=None, flog=None ):
        self.configdb           = configdb
        self.serialdb           = serialdb
        self.flog               = flog
        self.watt_production    = 0
        self.watt_consumption   = 0

        self.did_send_consumption_overshoot_message     = False
        self.did_send_consumption_undershoot_message    = False
        self.did_send_production_overshoot_message      = False
        self.did_send_production_undershoot_message     = False

        self.consumption_overshoot_threshold  = 0
        self.consumption_undershoot_threshold = 0
        self.production_overshoot_threshold   = 0
        self.production_undershoot_threshold  = 0

        self.consumption_overshoot_on   = 0
        self.consumption_undershoot_on  = 0
        self.production_overshoot_on    = 0
        self.production_undershoot_on   = 0

        self.consumption_overshoot_timeout   = 0
        self.consumption_undershoot_timeout  = 0
        self.production_overshoot_timeout    = 0
        self.production_undershoot_timeout   = 0

        self.email_timeout_user_setting      = 30

        # the time to wait before sending an new threshold change
        # in seconds
        self.EMAIL_SEND_WAIT_TIME = 60


    ###########################################
    # one to excute them all                  #
    ###########################################
    def run( self ): 
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        ############ RUN criteria #############
        # 1: is check activated (no return)
        # 2: is the use time valid, time and days (no return)
        # 3: is the threshold reached  (no return)
        # 4: is the threshold changed with the last value. 
        # 5: is above or below message all ready send do nothing, is the threshold below the setting send counter message. 
        # 6: only send message after the Hysteresis time has passed (EMAIL_SEND_WAIT_TIME).

        # read all of the 4 possible notifications, only continue when one is active
        self._notification_active()
        if self.consumption_overshoot_on == 0 and self.consumption_undershoot_on == 0 and self.production_overshoot_on == 0 and self.production_undershoot_on == 0:
            self.flog.debug( FUNCTION_TAG + ": geen van de notificaties staat aan, gestopt." )
            return 

        if self._power_values() == False:
            #self.flog.warning( FUNCTION_TAG + ": verbruik en geleverde Watt waarden zijn niet te lezen, gestopt.") 
            return

        self._consumption_overshoot()
        self._consumption_undershoot()
        self._production_overshoot()
        self._production_undershoot()


    ##################################################
    # production undershoot                           #
    ##################################################
    def _production_undershoot( self ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "." + inspect.currentframe().f_code.co_name

        if self.production_undershoot_on == 0:
            self.flog.debug( FUNCTION_TAG + ": notificatie staat uit, gestopt." )
            return

        self.flog.debug( FUNCTION_TAG + ": gestart.")

        watt_trigger = self._run_check(
            timewindow_db_index=210,
            threshold_watt_index=218,
            overshoot=False,
            watt_measurement=self.watt_production
            )

        subject_text = "Ondergrenswaarde van geleverd vermogen."

        if watt_trigger == True and self.did_send_production_undershoot_message == False:
        
            if self.production_undershoot_timeout > self._getUtcTime():
                self.flog.debug( FUNCTION_TAG + ": timeout is nog van toepassing.")
                return

            message_text = "Ondergrenswaarde van " + str(self.production_undershoot_threshold) + " W is overschreden. De gemeten waarde is " + str(self.watt_production) + " W."
            message_html = "<p>Ondergrenswaarde van <span class='color-blue'>" + str(self.production_undershoot_threshold) + " W</span> is overschreden. De gemeten waarde is <span class='color-red'>" + str(self.watt_production) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                self.did_send_production_undershoot_message = True
                self._message_to_log(sender="Geleverd vermogen", msg=message_text)


        if watt_trigger == False and self.did_send_production_undershoot_message == True:

            message_text = "Ondergrenswaarde van " + str(self.production_undershoot_threshold) + " W is niet langer overschreden. De gemeten waarde is " + str(self.watt_production) + " W."
            message_html = "<p>Ondergrenswaarde van <span class='color-blue'>" + str(self.production_undershoot_threshold) + " W</span> is niet langer overschreden. De gemeten waarde is <span class='color-green'>" + str(self.watt_production) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                self.did_send_production_undershoot_message = False
                self._message_to_log(sender="Geleverd vermogen", msg=message_text)

            self.production_undershoot_timeout = self._getUtcTime() + self.EMAIL_SEND_WAIT_TIME


    ##################################################
    # production overshoot                           #
    ##################################################
    def _production_overshoot( self ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        if self.production_overshoot_on == 0:
            self.flog.debug( FUNCTION_TAG + ": notificatie staat uit, gestopt." )
            return

        self.flog.debug( FUNCTION_TAG + ": gestart.")

        watt_trigger = self._run_check(
            timewindow_db_index=209,
            threshold_watt_index=217,
            overshoot=True,
            watt_measurement=self.watt_production
            )

        subject_text = "Bovengrenswaarde van geleverd vermogen."

        if watt_trigger == True and self.did_send_production_overshoot_message == False:
        
            if self.production_overshoot_timeout > self._getUtcTime():
                self.flog.debug( FUNCTION_TAG + ": timeout is nog van toepassing.")
                return

            message_text = "Bovengrenswaarde van " + str(self.production_overshoot_threshold) + " W is overschreden. De gemeten waarde is " + str(self.watt_production) + " W."
            message_html = "<p>Bovengrenswaarde van <span class='color-blue'>" + str(self.production_overshoot_threshold) + " W</span> is overschreden. De gemeten waarde is <span class='color-red'>" + str(self.watt_production) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                self.did_send_production_overshoot_message = True
                self._message_to_log(sender="Geleverd vermogen", msg=message_text)


        if watt_trigger == False and  self.did_send_production_overshoot_message == True:

            # Bovengrenswaarde van 100W is niet langer overschreden.  De gemeten waarde is xxx W
            message_text = "Bovengrenswaarde van " + str(self.production_overshoot_threshold) + " W is niet langer overschreden. De gemeten waarde is " + str(self.watt_production) + " W."
            message_html = "<p>Bovengrenswaarde van <span class='color-blue'>" + str(self.production_overshoot_threshold) + " W</span> is niet langer overschreden. De gemeten waarde is <span class='color-green'>" + str(self.watt_production) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                 self.did_send_production_overshoot_message = False
                 self._message_to_log(sender="Geleverd vermogen", msg=message_text)

            self.production_overshoot_timeout = self._getUtcTime() + self.EMAIL_SEND_WAIT_TIME


    ##################################################
    # consumption undershoot                         #
    ##################################################
    def _consumption_undershoot( self ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        #print("##",self.production_overshoot_threshold )
        
        if self.consumption_undershoot_on == 0:
            self.flog.debug( FUNCTION_TAG + ": notificatie staat uit, gestopt." )
            return

        self.flog.debug( FUNCTION_TAG + ": gestart.")

        watt_trigger = self._run_check(
            timewindow_db_index=212,
            threshold_watt_index=220,
            overshoot=False,
            watt_measurement=self.watt_consumption
            )


        subject_text = "Ondergrenswaarde van verbruikt vermogen."

        if watt_trigger == True and self.did_send_consumption_undershoot_message == False:
        
            if self.consumption_undershoot_timeout > self._getUtcTime():
                self.flog.debug( FUNCTION_TAG + ": timeout is nog van toepassing.")
                return

            message_text = "Ondergrenswaarde van " + str(self.consumption_undershoot_threshold) + " W is overschreden. De gemeten waarde is " + str(self.watt_consumption) + " W."
            message_html = "<p>Ondergrenswaarde van <span class='color-blue'>" + str(self.consumption_undershoot_threshold) + " W</span> is overschreden. De gemeten waarde is <span class='color-red'>" + str(self.watt_consumption) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                self.did_send_consumption_undershoot_message = True
                self._message_to_log(sender="Verbruikt vermogen", msg=message_text)

        if watt_trigger == False and self.did_send_consumption_undershoot_message == True:

            message_text = "Ondergrenswaarde van " + str(self.consumption_undershoot_threshold) + " W is niet langer overschreden. De gemeten waarde is " + str(self.watt_consumption) + " W."
            message_html = "<p>Ondergrenswaarde van <span class='color-blue'>" + str(self.consumption_undershoot_threshold) + " W</span> is niet langer overschreden. De gemeten waarde is <span class='color-green'>" + str(self.watt_consumption) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                self.did_send_consumption_undershoot_message = False
                self._message_to_log(sender="Verbruikt vermogen", msg=message_text)

            self.consumption_undershoot_timeout = self._getUtcTime() + self.EMAIL_SEND_WAIT_TIME


    ##################################################
    # consumption overshoot                          #
    ##################################################
    def _consumption_overshoot( self ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        #print("##",self.production_overshoot_threshold )
        
        if self.consumption_overshoot_on == 0:
            self.flog.debug( FUNCTION_TAG + ": notificatie staat uit, gestopt." )
            return

        self.flog.debug( FUNCTION_TAG + ": gestart.")

        watt_trigger = self._run_check(
            timewindow_db_index=211,
            threshold_watt_index=219,
            overshoot=True,
            watt_measurement=self.watt_consumption 
            )

        subject_text = "Bovengrenswaarde van verbruikt vermogen."

        if watt_trigger == True and self.did_send_consumption_overshoot_message == False:
        
            if self.consumption_overshoot_timeout > self._getUtcTime():
                self.flog.debug( FUNCTION_TAG + ": timeout is nog van toepassing.")
                return

            message_text = "Bovengrenswaarde van " + str(self.consumption_overshoot_threshold) + " W is overschreden. De gemeten waarde is " + str(self.watt_consumption) + " W."
            message_html = "<p>Bovengrenswaarde van <span class='color-blue'>" + str(self.consumption_overshoot_threshold) + " W</span> is overschreden. De gemeten waarde is <span class='color-red'>" + str(self.watt_consumption) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                self.did_send_consumption_overshoot_message = True
                self._message_to_log(sender="Verbruikt vermogen", msg=message_text)

        if watt_trigger == False and self.did_send_consumption_overshoot_message == True:


            message_text = "Bovengrenswaarde van " + str(self.consumption_overshoot_threshold) + " W is niet langer overschreden. De gemeten waarde is " + str(self.watt_consumption) + " W."
            message_html = "<p>Bovengrenswaarde van <span class='color-blue'>" + str(self.consumption_overshoot_threshold) + " W</span> is niet langer overschreden. De gemeten waarde is <span class='color-green'>" + str(self.watt_consumption) + " W.</span></p>"

            if self._send_mail( subject_text=subject_text, message_text=message_text, message_html=message_html ) == True:
                self.did_send_consumption_overshoot_message = False
                self._message_to_log(sender="Verbruikt vermogen", msg=message_text)

            self.consumption_overshoot_timeout = self._getUtcTime() + self.EMAIL_SEND_WAIT_TIME


    ##################################################
    # log function                                   #
    ##################################################
    def _message_to_log(self, sender="not set", msg="none"):
         self.flog.info( sender + ": " + msg)


    ##################################################
    # current UTC time in seconds                    #
    ##################################################
    def _getUtcTime( self ):
        now = datetime.datetime.utcnow()
        return int((now - datetime.datetime(1970, 1, 1)).total_seconds())

    ####################################################
    # send an email                                    #
    # return true, send went well, false a problem     #
    ####################################################
    def _send_mail( self, subject_text="subject_text", message_text="message", message_html="<H1>message</H1>" ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        CSS_EMAIL_STYLE =\
        """
        <style>
            .color-red  {color: red;}
            .color-blue {color: blue;}
            .color-green {color: green;}
        </style>
        """

        try:
            # construct subject.
            _id, subject, _label = self.configdb.strget( 69, self.flog )
            if len( subject) < 1:
                subject = const.DEFAULT_EMAIL_NOTIFICATION

            subject_str  = ' -subject "' + subject + " " + subject_text + '"'
            message_text = ' -msgtext "' + message_text + '"'
            message_html = ' -msghtml "' + CSS_EMAIL_STYLE + message_html + '"'
            timeout      = ' -time "'    + str( self.email_timeout_user_setting ) + '"'
            cmd = "/p1mon/scripts/P1SmtpCopy '" + timeout + subject_str + message_text + message_html + "' >/dev/null 2>&1"
            
            self.flog.debug( FUNCTION_TAG + ": cmd  = " + str( cmd ) )

            r = process_lib.run_process( 
                cms_str = cmd,
                use_shell=True,
                give_return_value=True,
                flog=self.flog,
                timeout=self.email_timeout_user_setting
                )
            if ( r[2] ) > 0:
                    self.flog.error( FUNCTION_TAG+ " email notificatie is gefaald." )
                    return False

        except Exception as e:
            self.flog.error( FUNCTION_TAG + ": onverwachte fout " + str(e) )
            return False

        return True


    ####################################################
    # run check                                        #
    # checks if the notification is active, if the     #
    # time/days are set, watt threshold, if the        #
    # watt check should be over (>) or undersshoot(<)  #
    # return False on error or does not fulfill        #
    # the checks. True means all values do fulfill     #
    ####################################################
    def _run_check( self, timewindow_db_index=0, threshold_watt_index=0, overshoot=True, watt_measurement=0 ):
        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        # check if day and time windows is active 
        if self._check_timewindow( timewindow_db_index ) == False:
            self.flog.debug( FUNCTION_TAG + ": tijdstip of dag niet ingesteld.")
            return False

        # read global email timeout
        try:
            # read treshold value 
            _id, timeout_str, _label = self.configdb.strget( 72, self.flog )
            timeout= int( timeout_str )
            self.email_timeout_user_setting = timeout
            self.flog.debug( FUNCTION_TAG + ": email time out is gezet op " + str( self.email_timeout_user_setting ) )
        except:
            self.flog.warning( FUNCTION_TAG + ": onverwachte fout " + str(e) )

        # check power treshold
        try:
            # read treshold value 
            _id, watt, _label = self.configdb.strget( threshold_watt_index, self.flog )
            watt_setting = int(watt)
            self.flog.debug( FUNCTION_TAG + ": watt grenswaarde is " + str(watt_setting) )
        except:
            self.flog.error( FUNCTION_TAG + ": onverwachte fout " + str(e) )
            return False

        if threshold_watt_index == 217:
            #print(" 217" )
            self.production_overshoot_threshold  = watt_setting
        elif threshold_watt_index == 218:
            #print(" 218" )
            self.production_undershoot_threshold = watt_setting
        elif threshold_watt_index == 219:
            #print(" 219" )
            self.consumption_overshoot_threshold = watt_setting
        elif threshold_watt_index == 220:
            #print(" 220" )
            self.consumption_undershoot_threshold = watt_setting

        #print("# check")
        try:
            # check if the watt threshold os reached.
            if ( overshoot == True ):
                if ( watt_measurement >= watt_setting ):
                    self.flog.debug( FUNCTION_TAG + ": watt waarde hoger dan ingesteld " + str(watt_setting) )
                    #print("# check 2")
                    return True
                else:
                    return False
                
            if ( overshoot == False ):
                if ( watt_measurement <= watt_setting ):
                    self.flog.debug( FUNCTION_TAG + ": watt waarde lager dan ingesteld " + str(watt_setting) )
                    #print("# check 3")
                    return True
                else:
                    return False

            #print("# check 4")

        except Exception as e:
            self.flog.error( FUNCTION_TAG + ": onverwachte fout " + str(e) )
            return False
        
        #print("# check 5")


    ##################################################
    # read from DB if any of the notifications is    #
    # active, is set the class variables             #
    ##################################################
    def _notification_active( self ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            sqlstr = "select PARAMETER from " + const.DB_CONFIG_TAB + " where ID >=213 and ID <=216 order by ID;"
            self.flog.debug( FUNCTION_TAG + ": sql query = "+ str(sqlstr) )
            record = self.configdb.select_rec(sqlstr)
            self.flog.debug( FUNCTION_TAG + ": sql record = " +  str(record) )

            if record[0][0] != None:
                self.production_overshoot_on    = int(record[0][0])
            if record[1][0] != None:
                 self.production_undershoot_on  = int(record[1][0])
            if record[2][0] != None:
                self.consumption_overshoot_on   = int(record[2][0])
            if record[3][0] != None:
                self.consumption_undershoot_on  = int(record[3][0])

            self.flog.debug( FUNCTION_TAG + ": production_overshoot_on="  + str(self.production_overshoot_on) +\
                " production_undershoot_on=" + str(self.production_undershoot_on)+\
                " consumption_overshoot_on=" + str(self.consumption_overshoot_on)+\
                " consumption_undershoot_on=" + str(self.consumption_undershoot_on) )

        except Exception as e:
            self.flog.error( FUNCTION_TAG +": fout bij het lezen van aan/uit status." + str(e) )
            return False


    ##################################################
    # read consumption and production values from DB #
    # true when all is well                          #
    ##################################################
    def _power_values( self ):

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # multply by 1000 to get Watt from Kw and cast as integer.
            sqlstr = "select CAST(avg(act_verbr_kw_170)*1000 as INT) ,CAST(avg(act_gelvr_kw_270)*1000 as INT) from " + const.DB_SERIAL_TAB + " where substr(timestamp,1,16) = '" + timestamp +"'"
            
            self.flog.debug( FUNCTION_TAG + ": sql query = "+ str(sqlstr) )
            record = self.serialdb.select_rec(sqlstr)
            self.flog.debug( FUNCTION_TAG + ": sql record = " +  str(record) )

            if( record[0][0] == None or record[0][1] == None ):
                #msg = "Watt waarde zijn niet te lezen."
                #self.flog.warning( FUNCTION_TAG + ": " + msg)
                return False

            self.watt_consumption = record[0][0]
            self.watt_production  = record[0][1]

            self.flog.debug( FUNCTION_TAG + ": consumption = " +  str(self.watt_consumption) + " W, production = " + str(self.watt_production) + " W.")
            return True

        except Exception as e:
            self.flog.error( FUNCTION_TAG +": onverwachte fout -> " + str(e) )
            return False


    #####################################
    # false on error or when not active #
    # true when all is well             #
    #####################################
    def _check_timewindow ( self, db_config_id ) -> bool:

        FUNCTION_TAG = __class__.__name__ + "." + __name__ + "."+ inspect.currentframe().f_code.co_name

        try:
            # check if the timeslot can be read and parsed 
            _id, raw_timestring, _label = self.configdb.strget( db_config_id, self.flog )
            self.flog.debug( FUNCTION_TAG + ": timeslot " + raw_timestring )

            # parse timedata
            p = raw_timestring.split( '.' )

            #  weekday() returns an integer with a value from 0 to 6, 0 is monday.
            day_idx_current = datetime.date.today().weekday()
            if int(p[day_idx_current+4]) != 1:
                self.flog.debug( FUNCTION_TAG + ": dag is niet geactiveerd, dag index is " +  str(day_idx_current) )
                return False
            self.flog.debug( FUNCTION_TAG + ": vandaag is geactiveerd, dag index is " +  str(day_idx_current) )

            # time conversion
            hh1 = int(p[0])
            mm1 = int(p[1])
            hh2 = int(p[2])
            mm2 = int(p[3])

            # convert the hours+min to minutes in the day as set
            tstart = ( int(p[0])*60 ) + int(p[1])
            tstop  = ( int(p[2])*60 ) + int(p[3])
            self.flog.debug( FUNCTION_TAG + ": start tijd" + f" {hh1 :02d}:{mm1 :02d}(" + str(tstart) + " minuten)," + " eindtijd" + f" {hh2 :02d}:{mm2 :02d}(" + str(tstop) + " minuten)." )

            # convert the hours+min to minutes in current time
            current_time = time.localtime()
            check_time = current_time.tm_hour*60 + current_time.tm_min 
            self.flog.debug( FUNCTION_TAG + ": controle tijdstip"+  f" {current_time.tm_hour:02d}:{current_time.tm_min :02d}(" + str(check_time) + " minuten)" )

            if check_time <= tstop and check_time >= tstart:
                 self.flog.debug( FUNCTION_TAG + ": " +  "huidige tijdstip valt in de ingestelde periode.")
                 return True
            else:
                self.flog.debug( FUNCTION_TAG + ": " +  "huidige tijdstip valt niet in de ingestelde periode.")
                return False

        except Exception as e:
            self.flog.error( FUNCTION_TAG + ": onverwachte fout " + str(e) )
            return False
