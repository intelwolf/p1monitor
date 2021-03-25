
import calendar
import datetime

from datetime import datetime

class utiltimestamp():

    def __init__( self, timestring ):
        self.timestring = timestring
        self.year    = 0
        self.month   = 1
        self.day     = 1
        self.hour    = 0
        self.minute  = 0
        self.seconds = 0   
        self.__splittimestring()

    # check if the timestring is a valid format
    def santiycheck(self):
        try:
            datetime.strptime( self.timestring, "%Y-%m-%d %H:%M:%S" )
            return True
        except ValueError:
            return False

    # add or subtract nummer of months
    def monthmodify( self, months ):
        return self.__monthdelta( datetime.strptime( self.timestring, "%Y-%m-%d %H:%M:%S"), months )
       
    def getparts( self ):
        return  "{:02d}".format( self.year ),\
                "{:02d}".format( self.month ), \
                "{:02d}".format( self.day ), \
                "{:02d}".format( self.hour ), \
                "{:02d}".format( self.minute ), \
                "{:02d}".format( self.seconds )
      
    def __splittimestring( self):
        self.year    = int( self.timestring[0:4] )
        self.month   = int( self.timestring[5:7] )
        self.day     = int( self.timestring[8:10] )
        self.hour    = int( self.timestring[11:13] )
        self.minute  = int( self.timestring[14:16] )
        self.seconds = int( self.timestring[17:19] )
    
    def __monthdelta(self, date, delta):
        m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
        if not m: m = 12
        d = min(date.day, calendar.monthrange(y, m)[1])
        return str(date.replace(day=d,month=m, year=y))