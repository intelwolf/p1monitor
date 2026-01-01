########################################
# lib for financial functions          #
########################################
import const
import inspect
import sys
import util
import logging

####################################################################
# calculate financial cost for kwh, gas, water                     #
# the hour values are used, maken sure the source tables kwh,gas,  #
# water are updated.                                               #
####################################################################
class Cost2Database():

    kw_price_per_hour = {
        'kwh_high_tariff_consumption'   : 0.0,
        'kwh_low_tariff_consumption'    : 0.0,
        'kwh_high_tariff_production'    : 0.0,
        'kwh_low_tariff_production'     : 0.0,
        'gas_consumption'               : 0.0,
        'water_consumption'             : 0.0,
    }

    day_cost = {
        'verbr_p'     : 0.0,
        'verbr_d'     : 0.0,
        'gelvr_p'     : 0.0,
        'gelvr_d'     : 0.0,
        'verbr_gas'   : 0.0,
        'verbr_water' : 0.0,
    }

    #rt_status_db.timestamp( 127,flog ) # set timestamp of cost processed day

    def init( self, financial_db=None, kwh_gas_db=None, watermeter_db=None, config_db=None, status_db=None, flog=None ):
        self.flog                   = flog
        self.config_db              = config_db
        self.status_db              = status_db
        self.financial_db           = financial_db
        self.kwh_gas_db             = kwh_gas_db
        self.watermeter_db          = watermeter_db
        self.cost_mode              = 0 #0 static prices, >1 dynamic prices
        self.prices_dict            = {}
        self.fixed_fee_kwh_day      = 0.0
        self.fixed_fee_gas_day      = 0.0
        self.fixed_fee_water_day    = 0.0
        self.dynamic_fee_kwh        = 0.0
        self.dynamic_fee_gas        = 0.0

        self.flog.debug( __class__.__name__ + ": init succesvol " )

    ##############################################################
    # timestamp of the day to use standard format                #
    ##############################################################
    def execute( self, timestamp=None ):

        self.flog.debug( __class__.__name__ + ": execute gestart succesvol met timestamp " + str(timestamp) )
        day_cost = self.day_cost.copy()

        self._get_price_mode()
        self._set_hour_prices( timestamp=timestamp )
        self._calculate_kwh_gas_prices( timestamp=timestamp, data=day_cost )
        self._calculate_water_prices(   timestamp=timestamp, data=day_cost )

        """
        print("\n---------------------------\n")
        print(  self.prices_dict )
        print("\n###########################\n")
        """
     
        self._update_financial_db_day( timestamp=timestamp, data=day_cost )
        self._update_financial_db( timestamp=timestamp, period='month' ) 
        self._update_financial_db( timestamp=timestamp, period='year' )

        # clean up, for the next run.
        day_cost.clear()
        self.prices_dict.clear()

        self.status_db.timestamp( 127,self.flog ) # set timestamp of cost processed day

        #sys.exit()
 
    ##############################################################
    # update the cost database for day prices                    #
    ##############################################################
    def _update_financial_db_day(self, timestamp=None, data=None ):

        #update record
        try:
            sqlstr = "insert or replace into "+\
            const.DB_FINANCIEEL_DAG_TAB + " values ('"\
            +timestamp[0:10]+" 00:00:00',"\
            +str(data['verbr_p'])+","\
            +str(data['verbr_d'])+","\
            +str(data['gelvr_p'])+","\
            +str(data['gelvr_d'])+","\
            +str(data['verbr_gas'])+","\
            +str(data['verbr_water'])+")"
            sqlstr=" ".join(sqlstr.split())
            self.flog.debug(__class__.__name__ + ": sql(update update kosten dag )=" + sqlstr )
            self.financial_db.insert_rec(sqlstr)

        except Exception as e:
            self.flog.error( __class__.__name__ + ": sql error update kosten dag)" + str(e) )

    ##############################################################
    # update the cost database for month or year prices          #
    ##############################################################
    def _update_financial_db(self, timestamp=None, period='month'):

        if period == 'month':
            substr_len=7
            tmp_timestamp = timestamp[0:substr_len]
            text_period = 'maand'
            select_table = const.DB_FINANCIEEL_DAG_TAB
            update_table = const.DB_FINANCIEEL_MAAND_TAB
            timestamp_str = "-01 00:00:00"

        if period == 'year':
            substr_len=4
            tmp_timestamp = timestamp[0:substr_len]
            text_period = 'jaar'
            select_table = const.DB_FINANCIEEL_MAAND_TAB
            update_table = const.DB_FINANCIEEL_JAAR_TAB
            timestamp_str = "-01-01 00:00:00"

        try:
            sqlstr = "select sum(verbr_p), sum(verbr_d), sum(gelvr_p), sum(gelvr_d) ,sum(gelvr_gas), sum(verbr_water) from "+\
            select_table + " where substr(timestamp,1," + str(substr_len) + ") = '" + tmp_timestamp + "'"
            sqlstr=" ".join(sqlstr.split())
            self.flog.debug( __class__.__name__ + ": sql(select kosten " + str(text_period) + ") = " + sqlstr)
            rec=self.financial_db.select_rec(sqlstr)
        except Exception as e:
            self.flog.error( __class__.__name__ + ": sql error(select kosten " + str(text_period) + ") " + str(e) )

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

        self.flog.debug(__class__.__name__ + ": " + str(text_period) + " kosten verbruik piek zijn " + str(verbr_p) )
        self.flog.debug(__class__.__name__ + ": " + str(text_period) + " kosten verbruik dal zijn "  + str(verbr_d) )
        self.flog.debug(__class__.__name__ + ": " + str(text_period) + " opbrengsten piek zijn "     + str(gelvr_p) )
        self.flog.debug(__class__.__name__ + ": " + str(text_period) + " opbrengsten dal zijn "      + str(gelvr_d) )
        self.flog.debug(__class__.__name__ + ": " + str(text_period) + " kosten gas zijn "           + str(verbr_gas) )
        self.flog.debug(__class__.__name__ + ": " + str(text_period) + " kosten water zijn "         + str(verbr_water) )
        
        #update record
        try:
            sqlstr = "insert or replace into "+ update_table + " values ('"\
            + timestamp[0:substr_len] + str(timestamp_str) + "',"\
            +str(verbr_p)+","\
            +str(verbr_d)+","\
            +str(gelvr_p)+","\
            +str(gelvr_d)+","\
            +str(verbr_gas)+","\
            +str(verbr_water)+")"
            sqlstr=" ".join(sqlstr.split())
            self.flog.debug( __class__.__name__ + ": sql( update kosten " + str(text_period) + ") = " + sqlstr )
            self.financial_db.insert_rec(sqlstr)
        except Exception as e:
            self.flog.error(inspect.stack()[0][3]+": sql( update kosten " + str(text_period) + ") =)" +str(e) )


    ##############################################################
    # convert water consumption to actual costs                  #
    ##############################################################
    def _calculate_water_prices( self, timestamp=None, data=None ):
        self.flog.debug( __class__.__name__ + ": water berekening gestart. " )
        timestamp_dag = timestamp[0:10]

        # read te hour records for the day in the timestamp.
        try:
            sqlstr = "select SUM(VERBR_PER_TIMEUNIT) from " + const.DB_WATERMETERV2_TAB + " where (TIMEPERIOD_ID=12 or TIMEPERIOD_ID=22) and substr(timestamp,1,10) = '" + timestamp_dag + "'"

            #sqlstr = "select TIMESTAMP, VERBR_PER_TIMEUNIT from " + const.DB_WATERMETERV2_TAB + " where TIMEPERIOD_ID=12 and substr(timestamp,1,10) = '" + timestamp_dag + "'"

            sqlstr =" ".join(sqlstr.split())
            self.flog.debug( __class__.__name__ + ": sql(water)=" + sqlstr )

            records = self.watermeter_db.select_rec( sqlstr )

            self.flog.debug(__class__.__name__ + ": waarde van water record" + str(records))
            self.flog.debug(__class__.__name__ +  ": timestamp = " + str(timestamp_dag) + " liters vandaag is " + str(records[0][0]))
        except Exception as e:
            self.flog.error( __class__.__name__ + ": sql error(water)" +str(e) )

        if records[0][0] != None: # Only calculate when there is a water value.
            try:
                data['verbr_water'] = self.prices_dict[0]['water_consumption'] * float(records[0][0])
                self.flog.debug(__class__.__name__ +  ": water kosten zonder vastrecht " + str(data['verbr_water']))
                data['verbr_water'] += self.fixed_fee_water_day
                self.flog.debug(__class__.__name__ +  ": water kosten inclusief vastrecht " + str(data['verbr_water']))
            except Exception as e:
                self.flog.warning( __class__.__name__ + ": fout bij het bereken van de dag kosten water " + str(e) )
           

    ##############################################################
    # convert kwh and gas consumption/production to actual costs #
    ##############################################################
    def _calculate_kwh_gas_prices( self, timestamp=None, data=None ):

        #self.flog.setLevel( logging.DEBUG )

        self.flog.debug( __class__.__name__ + ": kwh en gas berekening gestart. " )

        timestamp_dag = timestamp[0:10]

        # read te day records for the day in the timestamp.
        try:
            sqlstr = "select CAST( substr(timestamp,12,2) as INT), TARIEFCODE, VERBR_KWH_X, GELVR_KWH_X, VERBR_GAS_X from " +\
            const.DB_HISTORIE_UUR_TAB + " where substr(timestamp,1,10) = '" + timestamp_dag + "'"
            sqlstr=" ".join(sqlstr.split())
            self.flog.debug( inspect.stack()[0][3]+": sql(kwh-gas)=" + sqlstr )
            records = self.kwh_gas_db.select_rec(sqlstr)
            self.flog.debug(inspect.stack()[0][3]+": waarde van kwh-gas record" + str(records))
        except Exception as e:
            self.flog.error(inspect.stack()[0][3]+": sql error(kwh, gas)"+str(e))

        for rec in records:

            #print( self.prices_dict[rec[0]]['kwh_high_tariff_consumption'] )
            try:
                if rec[1] == "P":
                    data['verbr_p'] += ( self.prices_dict[rec[0]]['kwh_high_tariff_consumption'] * rec[2])
                else:
                    data['verbr_d'] += ( self.prices_dict[rec[0]]['kwh_low_tariff_consumption']  * rec[2])

                if rec[1] == "P":
                    data['gelvr_p'] += ( self.prices_dict[rec[0]]['kwh_high_tariff_production'] * rec[3])
                else:
                    data['gelvr_d'] += ( self.prices_dict[rec[0]]['kwh_low_tariff_production']  * rec[3])

                data['verbr_gas']   += ( self.prices_dict[rec[0]]['gas_consumption']            * rec[4])
            except Exception as e:
                self.flog.warning( __class__.__name__ + ": fout bij het aanpassen gas en kwh gebruik voor uur " + str(e) )

        try:
            data['verbr_d'] += self.fixed_fee_kwh_day
            data['verbr_gas'] += self.fixed_fee_gas_day
        except Exception as e:
              self.flog.error( __class__.__name__ + ": fout bij het aanpassen gas en kwh vastrecht." + str(e) )
        

        #self.flog.setLevel( logging.INFO )

    ##############################################################
    # fill the dictionary with prices for every day              #
    # sets static or dynamic prices                              #
    ##############################################################
    def _set_hour_prices( self, timestamp=None ):
      
        try:
            sqlstr = "select id, parameter from " + const.DB_CONFIG_TAB +\
            " where id <=5 or id=15 or id=16 or id=103 or id=104 or id=205 or id=208 order by id asc"
            sqlstr=" ".join( sqlstr.split() )
            self.flog.debug( __class__.__name__ + ": sql(kosten static)=" + sqlstr )
            rec_config=self.config_db.select_rec(sqlstr)
            self.flog.debug( __class__.__name__ + ": waarde van tarieven record" + str(rec_config) )
        except Exception as e:
            self.flog.error( __class__.__name__ + ": sql error(vaste kosten)" +str(e) )

        try:
            # fixed_fee(vastrecht)day 
            timestamp_dag = timestamp[0:10]
            self.fixed_fee_kwh_day = float(rec_config[5][1]) / util.daysPerMonth( timestamp_dag )
            self.flog.debug( __class__.__name__ +": Elektriciteit vastrecht per dag is " + str(self.fixed_fee_kwh_day) + " per maand is " + rec_config[5][1] )

            self.fixed_fee_gas_day = float(rec_config[7][1])/ util.daysPerMonth( timestamp_dag ) 
            self.flog.debug( __class__.__name__ +": Gas vastrecht per dag is " + str(self.fixed_fee_gas_day) + " per maand is " + rec_config[7][1] )

            self.fixed_fee_water_day = float(rec_config[8][1])/ util.daysPerMonth( timestamp_dag )
            self.flog.debug( __class__.__name__ +": Water vastrecht per dag is " + str(self.fixed_fee_water_day)+" per maand is " + rec_config[8][1] )

            self.dynamic_fee_kwh = float(rec_config[10][1]) 
            self.flog.debug( __class__.__name__ +": inkoop bedrag per kWh (vast bedrag) € " + str(self.dynamic_fee_kwh) )
            
            self.dynamic_fee_gas = float(rec_config[11][1]) 
            self.flog.debug( __class__.__name__ +": inkoop bedrag per kuub gas (vast bedrag) € " + str(self.dynamic_fee_gas) )

        except Exception as e:
            self.flog.error( __class__.__name__ + ": vastrecht prijzen -> " + str(e))

        tmp_dict = self.kw_price_per_hour.copy()

        #water usage cost are the same for dynamic or static costs. 
        try:
            tmp_dict['water_consumption'] = float(rec_config[9][1])/1000
        except Exception as e:
            self.flog.error( __class__.__name__ + ": probleem met de water prijs -> " + str(e))

        #################### STATIC COSTS ###################
        if self.cost_mode == 0: # static costs

            try:
                tmp_dict['kwh_high_tariff_consumption'] = float(rec_config[2][1])
                tmp_dict['kwh_low_tariff_consumption']  = float(rec_config[1][1])
                tmp_dict['kwh_high_tariff_production']  = float(rec_config[4][1])
                tmp_dict['kwh_low_tariff_production']   = float(rec_config[3][1])
                tmp_dict['gas_consumption']             = float(rec_config[6][1])
            except Exception as e:
                self.flog.error( __class__.__name__ + ": probleem met de prijzen -> " + str(e))

            self.flog.debug( __class__.__name__ +": statische tarieven  -> " + str(tmp_dict) )

            # maken the prices for every hour, for static they are the same.
            # done so calculations are always the same. 
            for hour in range(24):
                new_dict = tmp_dict.copy()
                self.prices_dict[hour] = new_dict

        #################### DYNAMIC COSTS ###################
        else: # dynamic costs

            #self.flog.setLevel( logging.DEBUG )

            try:
                sqlstr = "select CAST( substr(timestamp,12,2) as INT),PRICE_KWH, PRICE_GAS from " + const.DB_ENERGIEPRIJZEN_UUR_TAB +\
                "  where substr(timestamp,1,10) = '" + timestamp[0:10] + "'"
                sqlstr = " ".join( sqlstr.split() )
                self.flog.debug( __class__.__name__ + ": sql(kosten dynamic)=" + sqlstr )
                records = self.financial_db.select_rec(sqlstr)
                self.flog.debug( __class__.__name__ + ": waarde van tarieven record" + str(records) )
            except Exception as e:
                self.flog.error( __class__.__name__ + ": sql error( dynamische kosten )"+str(e))

            for rec in records:
                try:
                    if rec[1] != None:
                        tmp_dict['kwh_high_tariff_consumption'] = float(rec[1])
                        tmp_dict['kwh_low_tariff_consumption']  = float(rec[1])
                        tmp_dict['kwh_high_tariff_production']  = float(rec[1])
                        tmp_dict['kwh_low_tariff_production']   = float(rec[1])

                    if rec[2] != None:
                        tmp_dict['gas_consumption']             = float(rec[2]) + self.dynamic_fee_gas

                    if tmp_dict['kwh_high_tariff_consumption'] >=0:
                        tmp_dict['kwh_high_tariff_consumption'] += self.dynamic_fee_kwh
                    else: 
                        tmp_dict['kwh_high_tariff_consumption'] -= self.dynamic_fee_kwh

                    if tmp_dict['kwh_low_tariff_consumption'] >=0:
                        tmp_dict['kwh_low_tariff_consumption'] += self.dynamic_fee_kwh
                    else: 
                        tmp_dict['kwh_low_tariff_consumption'] -= self.dynamic_fee_kwh

                    if tmp_dict['kwh_high_tariff_production'] >=0:
                        tmp_dict['kwh_high_tariff_production'] += self.dynamic_fee_kwh
                    else: 
                        tmp_dict['kwh_high_tariff_production'] -= self.dynamic_fee_kwh

                    if tmp_dict['kwh_low_tariff_production'] >=0:
                        tmp_dict['kwh_low_tariff_production'] += self.dynamic_fee_kwh
                    else: 
                        tmp_dict['kwh_low_tariff_production'] -= self.dynamic_fee_kwh
                    
                    new_dict = tmp_dict.copy()
                    self.prices_dict[rec[0]] = new_dict

                except Exception as e:
                   self.flog.warning( __class__.__name__ + ": probleem met de prijzen (dynamische) -> " + str(e))

            #self.flog.debug( __class__.__name__ + ": self.prices_dict =" + str(self.prices_dict) )
            #self.flog.setLevel( logging.INFO )

    ##############################################################
    # set the mode for using prices                              #
    ##############################################################
    def _get_price_mode( self ):
        try:
            _id, cost_mode, _label = self.config_db.strget( 204, self.flog )
            self.cost_mode = int(cost_mode)
            if self.cost_mode > 0 :
                self.flog.debug( __class__.__name__ + ": dynamische kosten actief." )
            else:
                self.flog.debug( __class__.__name__ + ": vaste kosten actief." )
        except Exception as e:
             self.flog.error( __class__.__name__ + ": prijzen mode (dynamische of vaste kosten niet te lezen) " + str(e.args) )
    
    

