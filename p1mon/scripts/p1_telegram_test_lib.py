################################################
# set of testing functions for the P1 telegram #
################################################

import const
import inspect
import random
import string
import util


DUMMY_GAS_TIME_ELAPSED = 300 # sec. die verstreken moet zijn voor volgend gas record in dummy mode.

NO_GAS_TEST            = 0
DUMMY_GAS_MODE_2421    = 1
DUMMY_GAS_MODE_2430    = 2
DUMMY_GAS_MODE_2423    = 3

class p1_telegram():

    ############### static class vars ################
    dev_dummy_gas_value         = 0
    timestamp_last_gas_update   = 0

    ###################################################
    # init of the class                               #
    ###################################################
    def init( self, flog, configdb=None ):
        self.flog = flog
        try:
            sqlstr = "select status from " + const.DB_STATUS_TAB + " where id =43"
            gas_dummy_val_rec=configdb.select_rec(sqlstr)
            self.dev_dummy_gas_value=float(gas_dummy_val_rec[0][0])
        except Exception as e:
            flog.warning (inspect.stack()[0][3]+": oude gas waarde was niet te lezen in de configuratie database -> " + str( e.args[0] ) )


    ####################################################
    # return the timout delay for inserting gas values #
    ####################################################
    def gas_interval(self):
        return DUMMY_GAS_TIME_ELAPSED

    ###################################################
    # instert en dummy gas records telegram codes are #
    # configurable                                    #
    ###################################################
    def gas_stub_instert(self, line=None, serialbuffer=None, gasmode=DUMMY_GAS_MODE_2421 ):
        #voeg een dummy gas record in alleen voor ontwikkeling!!!
        try:

            #dev_dummy_gas_value = dev_dummy_gas_value + random.uniform(0, 0.0005) #0.0005
            if util.getUtcTime() - self.timestamp_last_gas_update > DUMMY_GAS_TIME_ELAPSED:
                self.dev_dummy_gas_value = self.dev_dummy_gas_value + random.uniform(0.0, 0.4)  #only update after elapsed time
                self.timestamp_last_gas_update = util.getUtcTime()

            self.flog.debug(inspect.stack()[0][3]+": gas dummy string toevoegen.")
            del serialbuffer[ len(serialbuffer)-1 ]
            
            #if  DUMMY_GAS_MODE_2421 == True:
            if gasmode == DUMMY_GAS_MODE_2421:
                line_1 = ''.join( filter(lambda x: x in string.printable, '0-1:24.2.1(170108160000W)('+'{0:09.3f}'.format(self.dev_dummy_gas_value)+'*m3)\r\n')).rstrip()[0:1024]
                serialbuffer.append( line_1 )
                #serial_buffer.append( '0-1:24.2.1(700101010000W)(00000000)' )
                #flog.debug(inspect.stack()[0][3]+": dummy gas waarde = "+line_1)
                self.flog.warning(inspect.stack()[0][3]+": test gas regel toegevoegd aan telegram: " + line_1 )
            
            #if  DUMMY_GAS_MODE_2423 == True: #(voor Belgie)
            if gasmode == DUMMY_GAS_MODE_2423: #(voor Belgie)
                line_1 = ''.join( filter(lambda x: x in string.printable, '0-1:24.2.3(190830073458S)('+'{0:09.3f}'.format(self.dev_dummy_gas_value)+'*m3)\r\n')).rstrip()[0:1024]
                serialbuffer.append( line_1 )
                #serial_buffer.append( '0-1:24.2.1(700101010000W)(00000000)' )
                #flog.debug(inspect.stack()[0][3]+": dummy gas waarde = "+line_1)
                self.flog.warning(inspect.stack()[0][3]+": test gas regel toegevoegd aan telegram: " + line_1 )

            #if DUMMY_GAS_MODE_2421 == True or DUMMY_GAS_MODE_2423 == True or DUMMY_GAS_MODE_2430 == True:

            #if DUMMY_GAS_MODE_2430 == True:
            if gasmode == DUMMY_GAS_MODE_2430:

                line_1 = ''.join( filter(lambda x: x in string.printable, '0-1:24.3.0(121030140000)(00)(60)(1)(0-1:24.2.1)(m3)\r\n')).rstrip()[0:1024]
                line_2 = ''.join( filter(lambda x: x in string.printable, '('+'{0:09.3f}'.format(self.dev_dummy_gas_value)+')')).rstrip()[0:1024]
                serialbuffer.append( line_1 )
                serialbuffer.append( line_2 )

                self.flog.debug(inspect.stack()[0][3]+": dummy gas waarde = "+line_1)
                self.flog.warning(inspect.stack()[0][3]+": test gas regel 1 toegevoegd aan telegram: " + line_1 )
                self.flog.warning(inspect.stack()[0][3]+": test gas regel 2 toegevoegd aan telegram: " + line_2 )
                self.flog.debug(inspect.stack()[0][3]+": "+line_2)
                
            serialbuffer.append( line )

        except Exception as e:
            self.flog.warning( inspect.stack()[0][3]+": test gas test insert probleem " +  str( e ) )

    ###################################################
    # instert an dummy 3 phase telegram codes         #
    ###################################################
    def phase3_stub_instert ( self, line=None, serialbuffer=None ):
            #voeg een 3 fase regels in, alleen voor ontwikkeling!!!
            try:
                self.flog.debug(inspect.stack()[0][3]+": 3 phase dummy string toevoegen.")

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

                del serialbuffer[ len(serialbuffer)-1 ] # remove last ! line to add records.
                
                # add consumption phase kW
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:21.7.0(' + '{0:06.3f}'.format( act_verbr_kw_l1 )+ '*kW)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:41.7.0(' + '{0:06.3f}'.format( act_verbr_kw_l2 )+ '*kW)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:61.7.0(' + '{0:06.3f}'.format( act_verbr_kw_l3 )+ '*kW)\r\n'))
                serialbuffer.append( line_1 )

                # add production phase kW
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:22.7.0(' + '{0:06.3f}'.format( act_gelvr_kw_l1 )+ '*kW)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:42.7.0(' + '{0:06.3f}'.format( act_gelvr_kw_l2 )+ '*kW)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:62.7.0(' + '{0:06.3f}'.format( act_gelvr_kw_l3 )+ '*kW)\r\n'))
                serialbuffer.append( line_1 )

                #add phase voltage
                l1_v = random.uniform( 225, 235 )
                l2_v = random.uniform( 225, 235 )
                l3_v = random.uniform( 225, 235 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:32.7.0(' + '{0:03.1f}'.format( l1_v )+ '*V)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:52.7.0(' + '{0:03.1f}'.format( l2_v )+ '*V)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:72.7.0(' + '{0:03.1f}'.format( l3_v )+ '*V)\r\n'))
                serialbuffer.append( line_1 )

                # add phase amparage
                l1_a = ((act_verbr_kw_l1 + act_gelvr_kw_l1) * 1000) / l1_v
                l2_a = ((act_verbr_kw_l2 + act_gelvr_kw_l2) * 1000) / l2_v
                l3_a = ((act_verbr_kw_l3 + act_gelvr_kw_l3) * 1000) / l3_v
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:31.7.0(' + '{0:03.0f}'.format( l1_a ) + '*A)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:51.7.0(' + '{0:03.0f}'.format( l2_a ) + '*A)\r\n'))
                serialbuffer.append( line_1 )
                line_1 = ''.join( filter(lambda x: x in string.printable, '1-0:71.7.0(' + '{0:03.0f}'.format( l3_a ) + '*A)\r\n'))
                serialbuffer.append( line_1 )

                serialbuffer.append( line ) # replace last line with ! character 
                #print ( serial_buffer )

                self.flog.warning( inspect.stack()[0][3]+": fase test regel toegevoegd aan telegram: " + \
                " L1: " + '{0:06.3f}'.format( act_verbr_kw_l1 ) + "kW " + '{0:03.1f}'.format( l1_v ) + "V " + '{0:03.0f}'.format( l1_a ) + "A "\
                " L2: " + '{0:06.3f}'.format( act_verbr_kw_l2 ) + "kW " + '{0:03.1f}'.format( l2_v ) + "V " + '{0:03.0f}'.format( l2_a ) + "A "\
                " L3: " + '{0:06.3f}'.format( act_verbr_kw_l3 ) + "kW " + '{0:03.1f}'.format( l3_v ) + "V " + '{0:03.0f}'.format( l3_a ) + "A "
                    )

            except Exception as e:
                self.flog.warning( inspect.stack()[0][3]+": test drie fase test insert probleem " +  str( e ) )
