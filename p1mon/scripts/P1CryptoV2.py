# run manual with ./P1CryptoV2

import sys
import argparse
import const
import inspect
import logger
import util
import filesystem_lib
#import crypto3
import crypto_lib

prgname = 'P1CryptoV2'

def Main(argv): 
    parser = argparse.ArgumentParser(description="encrypt of decrypt input string")
    parser.add_argument('-e', '--enc',      required=False)
    parser.add_argument('-d', '--dec',      required=False)
    parser.add_argument('-s', '--seed',     required=False)
    parser.add_argument('-t', '--test',     required=False, action="store_true")    # flag only
    args = parser.parse_args()
    enc         = args.enc   # encode the input string
    dec         = args.dec   # decode the base64 input to a string
    seed        = args.seed  # seed the internal key with a identifier to prevent plaintext attack.

    if args.test == True:
        crypto_lib.CryptoBase64().testP1CryptoSuite()
        sys.exit(0)

    try:
        if enc != None:
            cb = crypto_lib.CryptoBase64()
            if seed != None:
                result = cb.p1Encrypt( plain_text=enc, seed=seed )
            else:
                result = cb.p1Encrypt( plain_text=enc )
            print( result )
            flog.debug(inspect.stack()[0][3]+": encoding result: "+str(result))
    
        if dec != None:
            cb = crypto_lib.CryptoBase64()
            if seed != None:  
                result = cb.p1Decrypt( cipher_text=dec, seed=seed )
            else:
                result = cb.p1Decrypt( cipher_text=dec )
            print ( result )
            flog.debug(inspect.stack()[0][3]+": encoding result: "+str(result))
    except Exception as e:    
        flog.error(inspect.stack()[0][3]+": gestopt."+str(e))
    
#-------------------------------
if __name__ == "__main__":
    try:
        filepath = const.DIR_FILELOG + prgname + ".log" 
        try:
            filesystem_lib.set_file_permissions( filepath=filepath, permissions='664' )
            filesystem_lib.set_file_owners( filepath=filepath, owner_group='p1mon:p1mon' )
        except Exception as e:
            pass 
           
        flog = logger.fileLogger( filepath, prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn(False)
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(10) #  error: no logging check file rights

    Main(sys.argv[1:])
