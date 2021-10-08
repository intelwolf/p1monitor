##########################################
# dropbox support libs and constants     #
##########################################
# config db indexes                      #
# access_token   = 47                    #
# refresh token  = 170                   #
# refresh_token_expiration_timeout = 171 #
##########################################
import const
import crypto3
import dropbox
import inspect

# Get these from the developer dropbox site.
APP_KEY           = 'sefdetwey2877wd'
APP_SECRET        = 'vd2blgf607pdx3x'
CRYPT_KEY_ACCESS  = 'YxRv7LOMT0KiZC9FMz1mc0tY00q'
CRYPT_KEY_REFRESH = 'PqUuChmKCFu2hQx6eUe5X45vcDD'
#DROPBOX_REDIRECT_URL_FILE = const.DIR_RAMDISK + const.FILE_DBX_AUTH_REDIRECT 

AUTHFLOW = dropbox.DropboxOAuth2FlowNoRedirect(
        APP_KEY,
        consumer_secret=APP_SECRET,
        token_access_type='offline',
        scope=[
            'account_info.read',
            'files.metadata.write',
            'files.metadata.read',
            'files.content.write',
            'files.content.read',
            'file_requests.write',
            'file_requests.read'
            ]
        )

#####################################################
# check to see if the dbx acces token is stil valid #
# false the connection is not ok, reauthenticate    #
# true, all is well                                 #
#####################################################
def connection_is_valid( dbx=None, flog=None ):
    try:
        _user_info = dbx.users_get_current_account()
        flog.debug(inspect.stack()[0][3] + ": authenticatie met dropbox succesvol." )
        return True
    except Exception as e: 
        flog.warning (inspect.stack()[0][3] + ": authenticatie gefaald melding:" +str(e.args[0]) )
    return False


def authenticate_dbx(flog=None, config_db=None, rt_status_db=None ):
    
    flog.debug(inspect.stack()[0][3]+": authenticatie met dropbox start.")

    _id,access_token_crypted ,_label = config_db.strget( 47, flog )
    flog.debug(inspect.stack()[0][3]+": access_token(encrypted) = " + access_token_crypted )
    access_token = crypto3.p1Decrypt( access_token_crypted, CRYPT_KEY_ACCESS )
    flog.debug(inspect.stack()[0][3]+": decrypted key = " + str(access_token)) 

    _id, refresh_token_crypted  ,_label = config_db.strget( 170, flog )
    flog.debug(inspect.stack()[0][3]+": refresh_token(encrypted) = " + refresh_token_crypted )
    refresh_token = crypto3.p1Decrypt( refresh_token_crypted, CRYPT_KEY_REFRESH )
    flog.debug(inspect.stack()[0][3]+": decrypted refresh_token = " + str(refresh_token )) 

    try:

        dbx = dropbox.Dropbox(
            oauth2_access_token  = access_token,
            oauth2_refresh_token = refresh_token,
            app_key              = APP_KEY,
            app_secret           = APP_SECRET
        )

        dbx.users_get_current_account()
        rt_status_db.timestamp( 59,flog ) # dropbox succes timestamp
        flog.debug(inspect.stack()[0][3]+": authenticatie met dropbox succesvol.")
    except Exception as e:
        rt_status_db.strset('authenticatie gefaald',62,flog)
        flog.critical(inspect.stack()[0][3]+": authenticatie gefaald melding:" + str(e.args[0]) )
        dbx = None
    return dbx
