####################################################################
# shared lib for crypto functions                                  #
# todo replaces crypto3.py in the future                           #
####################################################################

import base64
#import cryptography
import inspect
import system_info_lib
#import os

from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

MAGIC_SEED = 'ab64e67aac269d'

digital_signing_verify_keys_b64 = {
    '1' : 'fDJE5j7z+yaCsnLuNLWj0uZLt7drR00z/rl0flNLzSo=',
    '2' : 'ng9OlUvD+4bz1Moy7mr/9xXTiJOZ1jnwsQgkLf2Jy6o=',
    '3' : '24Ma5jJBxVoDDpFzq5apWFqOKzDTUz5cZCrvsjDRA4U=',
    '4' : 'qU4QgfHP7BQBpyWnxAbrhxS1PtuJjVYewpUdiwWjwAA='
}

class DigitalSignature():

    #######################################################
    # class init function                                 #
    #######################################################
    def __init__(self, flog=None, debug=False):
        self.flog = flog
        self.signing_key = None # private key
        self.verify_key  = None  # public key
        self.debug = debug

    #######################################################
    # used outside the class for export and such          #
    # returns siging and verify key.                      #
    #######################################################
    def create_key_pairs( self ):
        self.__create_key_pairs()

        str_signing_key_b64 = self.signing_key.encode(encoder=Base64Encoder).decode("utf-8")
        str_verify_key_b64  = self.verify_key.encode(encoder=Base64Encoder).decode("utf-8")

        if self.debug:
            print( "DEBUG print_key_pairs signing_key_b64:" + str_signing_key_b64 )
            print( "DEBUG print_key_pairs verify_key_b64:"  + str_verify_key_b64 )

        return str_signing_key_b64 , str_verify_key_b64

    #######################################################
    # verify the file with a verify key and write a file  #
    # without the digital signature source_filepath,      #
    # destination_filepath, verify_key_b64 are mandatory  #
    #######################################################
    def verify_write_file( self, source_filepath=None, destination_filepath=None, verify_key_b64=None ):
        if source_filepath == None:
            raise Exception( "source_filepath niet opgeven " )

        if destination_filepath == None:
            raise Exception( "destination_filepath niet opgeven " )

        if verify_key_b64 == None:
            raise Exception( "verify_key_b64 key niet opgeven " )

        if self.debug:
            print ( "DEBUG verify_write_file: filepath = " + source_filepath )
        try:
            f = open( source_filepath, 'rb')
            signed = f.read()
            f.close()
        except Exception as e:
            raise Exception( "lezen van bestand " + source_filepath  + " gefaald" )

        try:
            self.verify_key = VerifyKey( verify_key_b64, encoder=Base64Encoder)
            verified_data = self.verify_key.verify( signed )
            
            if self.debug:
                print ("DEBUG verify_write_file: -----------------")
                print ("DEBUG verify_write_file: [*] data signed.")
                print ( signed )
                print ("DEBUG verify_write_file:[*] data verified.")
                print ( verified_data )
                print ("DEBUG verify_write_file: -----------------")

        except Exception as e:
            raise Exception( "verifying gefaald " + str(e))

        try:
            f = open( destination_filepath, 'wb')
            f.write( verified_data )
            f.close()
        except Exception as e:
            raise Exception( "schrijven van bestand " + destination_filepath  + " gefaald." )

        if self.debug:
            print ("DEBUG verify_write_file: "+ destination_filepath + " succesvol weggeschreven.")


    #######################################################
    # sign a file source_filepath, destination_filepath   #
    # signing_key_b64 is mandatory                        #
    #######################################################
    def sign_write_file( self, source_filepath=None, destination_filepath=None , signing_key_b64=None , verify_key_b64=None ):

        if source_filepath == None:
            raise Exception( "source_filepath niet opgeven " )

        if destination_filepath == None:
            raise Exception( "destination_filepath niet opgeven " )

        if signing_key_b64 == None:
            raise Exception( "signing_key_64 key niet opgeven " )
        else: 
            self.signing_key = SigningKey(signing_key_b64, encoder=Base64Encoder)

        if self.debug:
            print ( "DEBUG sign_write_file: filepath = " + source_filepath )
        try:
            f = open( source_filepath, 'rb')
            data = f.read()
            f.close()
        except Exception as e:
            raise Exception( "lezen van bestand " + source_filepath  + " gefaald" )

        #print ( b"data=" + data )
        try:
            signed = self.signing_key.sign( data )
        except Exception as e:
            raise Exception( "singing van " + source_filepath  + " gefaald" )

        # verify the sigend data with given verify key or with the 
        # generated verify key from the signed key.
        # the verify key can ben made from the signed key but 
        # the signed key cannot made from the verify key.
        # so the singed is the private key and the verifiy key is
        # the public key.
        try:
            if verify_key_b64 != None:
                self.verify_key = VerifyKey( verify_key_b64, encoder=Base64Encoder)
            else:
                self.verify_key = self.signing_key.verify_key
            verified_data = self.verify_key.verify( signed )
            if self.debug:
                print ("DEBUG sign_write_file: -----------------")
                print ("DEBUG sign_write_file: [*] data signed.")
                print ( signed )
                print ("DEBUG sign_write_file:[*] data verified.")
                print ( verified_data )
                print ("DEBUG sign_write_file: -----------------")

        except Exception as e:
            raise Exception( "verifying gefaald " + str(e))

        try:
            f = open( destination_filepath, 'wb')
            f.write( signed )
            f.close()
        except Exception as e:
            raise Exception( "schrijven van bestand " + destination_filepath  + " gefaald." )

    def __create_key_pairs( self ):
        self.signing_key = SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        if self.debug:
            print ( "DEBUG: signing_key = " + str( self.signing_key )  + "\nDEBUG: verify_key = " + str( self.verify_key ) + "\n" )




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

        result = system_info_lib.get_cpu_info() # get cpu specific id to generate crypto key
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

          