#!/usr/bin/python3
# from 01-08-2018 all new development will be done with Pyhton 3.x
import argparse
import const
import dropbox
import inspect
import sys

from dropbox import DropboxOAuth2FlowNoRedirect
from logger import logging,fileLogger
from util import setFile2user

# Get these from the developer dropbox site.
APP_KEY      ='sefdetwey2877wd'
APP_SECRET   ='vd2blgf607pdx3x'

prgname = 'P1DropBoxAuth'

# generates an url (-u) to get auth token or give a acces token -(t) based on an authorisation token from the dropbox website.
# beware the url generated auth token can only be used ONCE to generate a access token!
# "ERROR" when bad things happen, inspect logfile.

def Main(argv): 
    flog.info("Start van programma.")
    
    parser = argparse.ArgumentParser(description="-t <token> of -u (geef authenticatie url)")
    #parser.add_argument('-t','--token' )
    parser.add_argument('-t','--token', action='append', nargs=argparse.REMAINDER )
    parser.add_argument('-u','--url', action='store_true' )
    
    args = parser.parse_args()
  
    if args.url == False and args.token == None:
           print('Fout geen parameters opgegeven, cpu cycles verspild :)')
           return

    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

    if args.url == True:
        try:
            print ( auth_flow.start() )
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": url generatie gefaald melding:"+str(e.args[0]))
            print ('ERROR')    
        return
    
    if args.token != None:
        try:
            oauth_result = auth_flow.finish( args.token )
            print( oauth_result.access_token )
        except Exception as e:
            flog.critical(inspect.stack()[0][3]+": authenticatie gefaald melding:"+str(e.args[0])+ ". Is het authenticatie token al niet een keer gebruikt?")
            print ('ERROR')
        return

#-------------------------------
if __name__ == "__main__":
	try:
		logfile = const.DIR_FILELOG+prgname+".log" 
		setFile2user(logfile,'p1mon')
		flog = fileLogger(logfile,prgname)    
		#### aanpassen bij productie
		flog.setLevel(logging.INFO)
		flog.consoleOutputOn(False)
	except Exception as e:
		print ("critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
		sys.exit(10) #  error: no logging check file rights

	Main(sys.argv[1:])     