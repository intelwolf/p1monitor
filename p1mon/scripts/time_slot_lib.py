
from datetime import datetime
from inspect import stack

class time_slot_selector:

    #######################################################
    # class init function                                 #
    #######################################################
    def __init__(self, flog=None, time_slots_list=None, init_minute=-1 ):
        self.last_time_processed_minute = init_minute # init value, so the first call will always return true.
        self.flog = flog 
        self.time_slots_list = time_slots_list

    #######################################################
    # get a true value when the minute in the slot is not #
    # processed.                                          #
    #######################################################
    def timeslot( self ):
        now = datetime.now()
        
        if self.time_slots_list == None:
            list_of_time_slots = [[0,15],[16,30],[31,45],[46,59]]
        else:
            list_of_time_slots = self.time_slots_list

        for slots in list_of_time_slots:
            if now.minute >= slots[0] and now.minute <= slots[1]:
                #print ( slots[0], slots[1] )
                if self.last_time_processed_minute >= slots[0] and self.last_time_processed_minute <= slots[1]:
                    self.flog.debug( stack()[0][3] + " GEEN "+ str(slots[0]) + "-"+ str(slots[1]) +\
                         " minuten bereik verwerking. Laatste verwerkings minuut " +\
                              str( self.last_time_processed_minute) )
                    return False
                else:
                    self.flog.debug( stack()[0][3] + " WEL "+ str(slots[0]) + "-"+ str(slots[1]) +\
                         " minuten bereik verwerking. Laatste verwerkings minuut " +\
                              str( self.last_time_processed_minute) )
                    self.last_time_processed_minute = now.minute
                    return True