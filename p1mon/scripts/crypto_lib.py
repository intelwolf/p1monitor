####################################################################
# shared lib for crypto functions                                  #
# todo replaces crypto3.py in the future                           #
####################################################################

#from cryptography.fernet import Fernet
import base64
import cryptography
import cpuinfo
import hashlib
import inspect
import secrets

#from cryptography.fernet import Fernet
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

MAGIC_SEED = 'ab64e67aac269d'

class P1monCrypto():

    ###########################################
    # init the class                          #
    ###########################################
    def init( self, flog=None ):
        self.symmetric_key=None
        self.flog = flog

    ###################################################
    # make an symmetric key for decoding and decoding #
    ###################################################
    def set_symmetric_key( self, seed=MAGIC_SEED ):

        result = cpuinfo.get_cpu_info() # get cpu specific id to generate crypto key
        hash_in = str( seed ) + str(result['Serial']) + str( seed )

        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=seed.encode(),
            iterations=100000,
            backend=backend
        )
        self.symmetric_key = base64.urlsafe_b64encode( kdf.derive( hash_in.encode()) )
        self.flog.debug( inspect.stack()[0][3] + ": symmetric key = " + str( self.symmetric_key )  )


    #########################################
    # encrypt binary file                   #
    #########################################
    def encrypt_file( self, source_pathfile=None, destination_pathfile=None ):
        try:

            fernet = Fernet( self.symmetric_key )

            with open( source_pathfile, 'rb') as file:
                original = file.read()

            encrypted = fernet.encrypt( original ) 

            with open( destination_pathfile, 'wb') as encrypted_file:
                encrypted_file.write( encrypted )

        except Exception as e:
            self.flog.error( inspect.stack()[0][3] + ": symmetric key = " + str( e ) )
            raise Exception( "encryptie van bestand " + source_pathfile  + " gefaald " )

    #########################################
    # encrypt binary file                   #
    #########################################
    def decrypt_file( self, source_pathfile=None, destination_pathfile=None ):
        try:

            fernet = Fernet( self.symmetric_key )

            with open( source_pathfile, 'rb') as enc_file:
                encrypted = enc_file.read()
  
            # decrypting the file
            decrypted = fernet.decrypt(encrypted)
  
            # opening the file in write mode and
            # writing the decrypted data
            with open( destination_pathfile,'wb') as dec_file:
                dec_file.write(decrypted)

        except Exception as e:
            self.flog.error( inspect.stack()[0][3] + ": symmetric key = " + str( e ) )
            raise Exception( "decryptie van bestand " + source_pathfile  + " gefaald " )

          