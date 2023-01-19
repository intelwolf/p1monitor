
import inspect

from gpiozero   import LED, Button
from sqldb      import  rtStatusDb,configDB
#from logger     import fileLogger,logging


class gpioDigtalInput():
       
    def init( self, db_config_id , config_db , flog ):
        self.db_config_id           = db_config_id 
        self.config_db              = config_db
        self.flog                   = flog
        self.gpio_pin               = None

        # reading from database the pin number
        _id, gpio_pin_value , _label = self.config_db.strget( self.db_config_id , self.flog )
        flog.info( inspect.stack()[0][3] + ": gpioDigtalInput gelezen uit database, pin nummer is " + str( gpio_pin_value ) )
        # init the gpio pin 
        if self.no_duplicate_use_of_pins_used_as_input() == True:
            self.gpio_pin = Button ( int(gpio_pin_value) , pull_up=True, hold_repeat=False  )
        else:
            flog.info( inspect.stack()[0][3] + ": gpioDigtalInput niet gezet wegens dubbel gebruik van pin's " + str( gpio_pin_value ) )
            self.gpio_pin = None

    # True is an pulse, False not
    def gpioWaitRead( self ):
        if self.gpio_pin.wait_for_press( timeout=10 ) == False:
            return False
        self.gpio_pin.wait_for_press()
        self.flog.debug( inspect.stack()[0][3] + ": press detected."  )
        self.gpio_pin.wait_for_release()
        self.flog.debug( inspect.stack()[0][3] + ": press released."  )
        return True

    def close(self):
        self.gpio_pin.close()

    def check_pin_from_db( self ):
        #self.flog.info( inspect.stack()[0][3]+ ": entry." )
        # reading from database the pin number
        _id, gpio_pin_value , _label = self.config_db.strget( self.db_config_id , self.flog )
        if self.gpio_pin.pin.number != int( gpio_pin_value ): #check if pin is changed, in config
            #self.flog.info( inspect.stack()[0][3]+ ": entry 2." )
            self.gpio_pin.close()
            self.gpio_pin = Button ( int(gpio_pin_value) , pull_up=True, hold_repeat=False  )
            self.flog.info( inspect.stack()[0][3]+ ": GPIO pin aangepast naar pin " + str( gpio_pin_value) )
            #self.flog.info( inspect.stack()[0][3]+ ": entry 3." )
        #self.flog.info( inspect.stack()[0][3]+ ": exit 4." )

    def no_duplicate_use_of_pins_used_as_input( self ):
        # update this as the config.db is changed
        # curent config index's used
        # 85, 95 , 97  126 is input

        check_set = set()
        # we use a set because a set won't except double values, so when an pin is already used the
        # number of enteries wil be less then 4

        try:
            _id, gpio_pin_value_85, _label  = self.config_db.strget(   85 , self.flog )  # GPIO 27 Default pin
            check_set.add( gpio_pin_value_85 ) 
            _id, gpio_pin_value_95, _label  = self.config_db.strget(   95 , self.flog ) # GPIO 22 Default pin
            check_set.add( gpio_pin_value_95 ) 
            _id, gpio_pin_value_97, _label  = self.config_db.strget(   97 , self.flog ) # GPIO 17 Default pin
            check_set.add( gpio_pin_value_97 ) 
            _id, gpio_pin_value_126, _label = self.config_db.strget( 126 , self.flog )  # GPIO 26 Default pin
            check_set.add( gpio_pin_value_126 ) 

            self.flog.debug( inspect.stack()[0][3] + ": gpio_pin_value_85=" + gpio_pin_value_85 + " gpio_pin_value_95="\
                 + gpio_pin_value_95 + " pio_pin_value_97=" + gpio_pin_value_97 + " gpio_pin_value_126=" + gpio_pin_value_126 )
            
            # none of the pins may be equal
            # we use a set because a set won't except double values, so when an pin is already used the
            # number of enteries wil be less then 4
            if len( check_set ) != 4:
                return False
            return True
        except:
            return False



class gpioDigtalOutput():
   
    ##################################################################
    # invertio used to invert the io of the GPIO when set to true    #
    # the on will be off and visa versa.                             #
    ##################################################################
    def init( self, db_config_id , config_db , flog , invert_io=False ):
        self.db_config_id           = db_config_id 
        self.config_db              = config_db
        self.flog                   = flog
        self.invert_io              = invert_io
        
        # reading from database the pin number
        _id, gpio_pin_value , _label = self.config_db.strget( self.db_config_id , self.flog )
        flog.debug( inspect.stack()[0][3] + ": gpioDigtalOutput() gelezen uit database, pin nummer is " + str( gpio_pin_value ) )
        # init the gpio pin 
        self.gpio_pin = LED( int(gpio_pin_value)  )

    def gpioOn( self,  on ):
        self.check_pin_from_db()
        
        if self.invert_io == True:
            on = not on

        if on == True:
            if self.gpio_pin.value == 0:
                self.gpio_pin.on()
                if self.invert_io == False:
                    self.flog.info( inspect.stack()[0][3] + ": gpioDigtalOutput() pin " + str( self.gpio_pin.pin.number ) + " ingeschakeld.")
                else:
                    self.flog.info( inspect.stack()[0][3] + ": gpioDigtalOutput() pin " + str( self.gpio_pin.pin.number ) + " uitgeschakeld.")
        else:
            if self.gpio_pin.value == 1:
                self.gpio_pin.off()
                if self.invert_io == False:
                    self.flog.info( inspect.stack()[0][3] + ": gpioDigtalOutput() pin " + str( self.gpio_pin.pin.number ) + " uitgeschakeld.")
                else:
                    self.flog.info( inspect.stack()[0][3] + ": gpioDigtalOutput() pin " + str( self.gpio_pin.pin.number ) + " ingeschakeld.") 

    def set_invert_io( self, on=False ):
            self.invert_io = on

    def close(self):
        self.gpio_pin.close()


    def check_pin_from_db( self ):
         # reading from database the pin number
        _id, gpio_pin_value , _label = self.config_db.strget( self.db_config_id , self.flog )
        if self.gpio_pin.pin.number != int( gpio_pin_value ): #check if pin is changed, in config
            self.gpio_pin.close()
            self.gpio_pin = LED( int(gpio_pin_value) )
            self.flog.info( inspect.stack()[0][3]+ ": GPIO pin aangepast op pin " + str( gpio_pin_value) )

