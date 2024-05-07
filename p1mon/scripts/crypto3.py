import const
import argparse
import base64
import util 
import string
import sys
import subprocess
import system_info_lib

#from logger        import *
from Crypto.Cipher  import AES
from Crypto.Hash    import SHA256

AES_MODE    = AES.MODE_CBC
MAGIC_SEED  = 'ab64e67aac269d'

# decrypt the base64 string to plaintext string.
# on problem an empty string wil be retured.
# the output is sanitized for printabele charcters, when the string is not printable only
# then there is problem.
def p1Decrypt(cipher_text, seed=MAGIC_SEED):
    try:
      decryption_suite= AES.new(p1CryptoGetKey(), AES_MODE, seedGenerator(seed))
      raw_text       = base64.b64decode(cipher_text)
      str_raw       = decryption_suite.decrypt(raw_text).decode('utf-8')
      idx_right = int(str_raw[-16:])
      str_return = str_raw[:-16].rstrip() # remove space counter
      for _i in range(0, idx_right):
        str_return += ' '
      # make sure we only return printable chars when decription goes south.
      filtered_string = ''.join( filter(lambda x: x in string.printable, str_return) )
      return (filtered_string)
    except Exception as _e:
      #print('error decrypt='+str(e))
      return ''


# encrypt a plaintext string to a base64 string
# on problem an empty string wil be retured.	
def p1Encrypt(plain_text, seed=MAGIC_SEED):
    try:
      encryption_suite = AES.new(p1CryptoGetKey(), AES_MODE, seedGenerator(seed))
      cipher_text 	 = encryption_suite.encrypt( padding16(plain_text) + spaceIndexer(plain_text) )
      return str(base64.b64encode(cipher_text).decode())
    except Exception as _e:
      #print('error encrypt='+str(e))
      return ''

def p1CryptoGetKey(seed=MAGIC_SEED):
    result = system_info_lib.get_cpu_info() # get cpu specific id to generate crypto key
    hash_in = seed
    hash_in = hash_in + result['Serial'] + seed
    hash = SHA256.new(hash_in.encode('utf-8'))
    return( hash.hexdigest().encode()[:32])

def padding16(_in):
    _in     = _in + '                 ' # padding to make multpy of 16
    _out = _in[ :len(_in)-len(_in)%16 ]
    return _out

# return in the format [SSSSS:EEEEE] number of leading and traling spaces in text
def spaceIndexer(_in):
     idx_right = len(_in) - len(_in.rstrip()) # find padding spaces
     return "%16d" % (idx_right)
 
def seedGenerator(_seed):
    hash = SHA256.new()
    hash.update( _seed.encode('utf-8') ) # utf-8 to binary
    return ( hash.hexdigest().encode()[:16]) #str to binary


# test function normaly not used in production.
def testP1CryptoSuite():
    print ("Pyhton 3")

    #print( p1CryptoGetKey('p1monitor') )
    #print( seedGenerator('p1monitor') )
    #return

    words = ['  p1mon   ', '    p1monitor ', '  p1monitor & spaces              ', 'a   ', '    1']
    print("==========================================================")
    print( "Default crypto key '            = '"+str(p1CryptoGetKey()) )
    print( "Seeded (p1monitor) crypto key ' = '"+str(p1CryptoGetKey('p1monitor') ))
    print( "seedGenerator('p1monitor')  '   = '"+str(seedGenerator('p1monitor') ))

    #print( "p1Encrypt('wil') = "+ p1Encrypt('wil') )
    #print("decrypted text wil' = '"+p1Decrypt(p1Encrypt('wil'))+"'")

    #return

    print("----------------------------------------------------------")
    for i in range(len(words)):
        encrypted = p1Encrypt(words[i])
        print("test encrypt van plaintext    '"+words[i]+"' = '"+encrypted)
        print("test decrypt van crypted text '"+words[i]+"' = '"+str(p1Decrypt(encrypted))+"'")
        print("no seed --------------------------------------------------")
    encrypted = p1Encrypt('p1monitor')
    print("test encrypt van plaintext    'p1monitor' = '"+encrypted)
    print("test decrypt van crypted text 'p1monitor' = '"+p1Decrypt(encrypted)+"'")
    print("with seed ----------------------------------------------------")
    encrypted = p1Encrypt('p1monitor','a')
    print("test encrypt van plaintext    'p1monitor' = '"+encrypted)
    print("test decrypt van crypted text 'p1monitor' = '"+p1Decrypt(encrypted,'a')+"'")
    encrypted = p1Encrypt('p1monitor','1234567890123456789123456789')
    print("test encrypt van plaintext    'p1monitor' = '"+encrypted)
    print("test decrypt van crypted text 'p1monitor' = '"+p1Decrypt(encrypted,'1234567890123456789123456789')+"'")
