# run manual with ./P1CryptoV2

import sys
import argparse
import const
import inspect
#import imp
import logger
import util
import crypto3

#from Crypto.Cipher import AES

prgname = 'P1CryptoV2'

def Main(argv): 
    parser = argparse.ArgumentParser(description="encrypte of decrypte input string")
    parser.add_argument('-e', '--enc',    required=False)
    parser.add_argument('-d', '--dec',    required=False)
    parser.add_argument('-s', '--seed',    required=False)
    parser.add_argument('-t', '--test', required=False, action="store_true")    # flag only
    args = parser.parse_args()
    enc         = args.enc   # encode the input string
    dec         = args.dec   # decode the base64 input to a string
    seed        = args.seed  # seed the internal key with a identifier to prevent plaintext attack.

    if args.test == True:
        crypto3.testP1CryptoSuite()
        sys.exit(0)

    try:
        if enc != None:
            if seed != None:
                result = crypto3.p1Encrypt( enc, seed )
            else:
                result = crypto3.p1Encrypt( enc )
            print ( result )
            flog.debug(inspect.stack()[0][3]+": encoding result: "+str(result))
    
        if dec != None:
            if seed != None:
                result = crypto3.p1Decrypt(dec, seed)
            else:
                result = crypto3.p1Decrypt(dec)
            print ( result )
            flog.debug(inspect.stack()[0][3]+": encoding result: "+str(result))
    except Exception as e:    
        flog.error(inspect.stack()[0][3]+": gestopt."+str(e))
    
#-------------------------------
if __name__ == "__main__":
    try:
        logfile = const.DIR_FILELOG+prgname+".log" 
        util.setFile2user( logfile, 'p1mon ')
        flog = logger.fileLogger( logfile, prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn(False)
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
        sys.exit(10) #  error: no logging check file rights

    Main(sys.argv[1:])
