import logging
import logging.handlers
import time
import os

def mkLocalTimeString(): 
    t=time.localtime()
    return "%04d-%02d-%02d %02d:%02d:%02d"\
    % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

class fileLogger():

    def __init__(self, logfile, prgname):
        #oldmask = os.umask()
        #os.umask( 0o002 )
        self.loglevel=logging.DEBUG
        self.consoleoutput = False
        self.lgr = logging.getLogger(prgname)
        self.lgr.setLevel(self.loglevel)     
        self.fh = logging.handlers.RotatingFileHandler(logfile, maxBytes=1024000, backupCount=3 )
        self.fh.setLevel(self.loglevel)
        self.frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh.setFormatter(self.frmt)
        self.lgr.addHandler(self.fh)
        #os.umask( oldmask ) 

    # primair voor debug werkzaamheden
    # staat default uit
    def consoleOutputOn(self,on):
        self.consoleoutput = on
    
    def setLevel(self,level):
        self.loglevel=level
        self.lgr.setLevel(self.loglevel)
        self.fh.setLevel(self.loglevel)
    
    def getLevel(self ):
        return self.loglevel
       
    def debug(self,msg_in):
        self.lgr.debug(msg_in)
        if self.consoleoutput and self.loglevel<=logging.DEBUG:
            print (mkLocalTimeString()+" Debug: "+msg_in)
            
    def info(self,msg_in):
        self.lgr.info(msg_in)
        if self.consoleoutput and self.loglevel<=logging.INFO:
            print (mkLocalTimeString()+" Info: "+msg_in)
            
    def warning(self,msg_in):
        self.lgr.warn(msg_in)
        if self.consoleoutput and self.loglevel<=logging.WARNING:
            print (mkLocalTimeString()+" Warning: "+msg_in)
        
    def error(self,msg_in):
        self.lgr.error(msg_in)
        if self.consoleoutput and self.loglevel<=logging.ERROR:
            print (mkLocalTimeString()+" Error: "+msg_in)
        
    def critical(self,msg_in):
        self.lgr.critical(msg_in)
        if self.consoleoutput and self.loglevel<=logging.CRITICAL:
            print (mkLocalTimeString()+" Critical: "+msg_in)
         
    def all_level_test(self):
        self.debug("Logger debug test.")
        self.info("Logger info test.")
        self.warning("Logger warning test.")
        self.error("Logger error test.")
        self.critical("Logger critical test.")
