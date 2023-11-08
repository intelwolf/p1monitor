# run manual with ./P1SmtpCopy

import argparse
import base64
import const
import crypto3
#import email
import inspect
import logger
import makeLocalTimeString
import ssl
import smtplib
import sys
import sqldb
import os
import util
import quote_lib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

prgname      = 'P1SmtpCopy'

config_db    = sqldb.configDB()
rt_status_db = sqldb.rtStatusDb()

# remarks
# Gmail requires that you connect to port 465 if using SMTP_SSL(), and to port 587 when using .starttls()

smtp_para = {
    'mailuser':'',
    'mailuserpassword':'',
    'mailserver':'',                # smtp.gmail.com / mail.ztatz.nl
    'mailserverport_ssl':465,
    'mailserverport_starttls':587,
    'mailserverport_plaintext':25,
    'subject':'',
    'to':[],
    'cc':[],
    'bcc':[],
    'fromalias':'',
    'messagetext':'',
    'messagehtml':'',
    'timeout':60,
    'attachments':[]
}

def Main(argv): 
    flog.info("Start van programma.")
    global smtp_para

    # open van status database
    try:    
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")
  
    # update field from database, the cli switches overwrite the DB values!
   
    _id,smtp_para ['mailuser']                  ,_label = config_db.strget( 63, flog )  
    _id,smtp_para ['mailuserpassword']          ,_label = config_db.strget( 64, flog )
    _id,smtp_para ['mailserver']                ,_label = config_db.strget( 65, flog )
    _id,smtp_para ['mailserverport_ssl']        ,_label = config_db.strget( 66, flog )
    _id,smtp_para ['mailserverport_starttls']   ,_label = config_db.strget( 67, flog )
    _id,smtp_para ['mailserverport_plaintext']  ,_label = config_db.strget( 68, flog )
    _id,smtp_para ['subject']                   ,_label = config_db.strget( 69, flog )
    _id,to                                      ,_label = config_db.strget( 70, flog ) 
    smtp_para['to'] = to.split() 
    _id,cc                                      ,_label = config_db.strget( 74, flog ) 
    smtp_para['cc'] = cc.split()
    _id,bcc                                     ,_label = config_db.strget( 75, flog ) 
    smtp_para['bcc'] = bcc.split()
    _id,smtp_para ['fromalias']                 ,_label = config_db.strget( 71, flog )
    _id,smtp_para ['timeout']                   ,_label = config_db.strget( 72, flog )

    flog.debug( inspect.stack()[0][3] + ": parameters uit de DB:" + str( smtp_para ) )

    parser = argparse.ArgumentParser(description="smtp....")                             # DB ID
    parser.add_argument( '-u'        , '--mailuser',                        required=False ) #63
    parser.add_argument( '-pw'       , '--mailuserpassword',                required=False ) #64
    parser.add_argument( '-srv'      , '--mailserver',                      required=False ) #65
    parser.add_argument( '-pssl'     , '--mailserverport_ssl',              required=False ) #66
    parser.add_argument( '-pstls'    , '--mailserverport_starttls',         required=False ) #67
    parser.add_argument( '-pplain'   , '--mailserverport_plaintext',        required=False ) #68
    parser.add_argument( '-subject'  , '--subject',                         required=False ) #69
    parser.add_argument( '-to'       , '--to', action='append',             required=False ) #70
    parser.add_argument( '-cc'       , '--cc', action='append',             required=False ) #74
    parser.add_argument( '-bcc'      , '--bcc', action='append',            required=False ) #75 
    parser.add_argument( '-from'     , '--fromalias',                       required=False ) #71 
    parser.add_argument( '-msgtext'  , '--messagetext',                     required=False ) #NONE
    parser.add_argument( '-msghtml'  , '--messagehtml',                     required=False ) #NONE
    parser.add_argument( '-time'     , '--timeout',                         required=False ) #72
    parser.add_argument( '-a'        , '--attachment', action='append',     required=False ) #NONE
    parser.add_argument( '-test'     , '--testmail', action='store_true',   required=False ) #NONE

    args = parser.parse_args()

    # send a test mail with default value
    if args.testmail != None:
        smtp_para['messagetext'] = "Dit is een test mail van de P1 monitor en mag genegeert worden. De mail is op " +  makeLocalTimeString.makeLocalTimeString() + " verzonden." + \
        "\n\n" + quote_lib.get_quote() + "\n\nBezoek https://www.ztatz.nl voor meer informatie over de P1 monitor." 
        smtp_para['subject']     = "P1 monitor test email van " + makeLocalTimeString.makeLocalTimeString() + "."

    if args.mailuser != None:
        smtp_para['mailuser'] = args.mailuser
  
    if args.mailuserpassword != None:	
        smtp_para['mailuserpassword'] = args.mailuserpassword 
    else: #decode password
        try:
            smtp_para ['mailuserpassword'] = base64.standard_b64decode(crypto3.p1Decrypt(smtp_para ['mailuserpassword'],'mailpw') ).decode('utf-8')
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": password decodering gefaald. Decoded password=" +\
                smtp_para ['mailuserpassword']+" Gestopt. melding:" + str(e.args[0]) )
            sys.exit(16)
        flog.info("Password decryptie ok.")
        flog.debug( "Decoded password = " + smtp_para [ 'mailuserpassword' ] )
        
    if args.mailserver != None:
        smtp_para['mailserver'] = args.mailserver

    if args.mailserverport_ssl != None:
        smtp_para['mailserverport_ssl'] = int ( args.mailserverport_ssl )

    if args.mailserverport_starttls != None:
        smtp_para['mailserverport_starttls'] = int ( args.mailserverport_starttls )

    if args.mailserverport_plaintext != None:
        smtp_para['mailserverport_plaintext'] = int ( args.mailserverport_plaintext )

    if args.subject != None:
        smtp_para['subject'] = args.subject
    if len( smtp_para['subject'] ) < 1:
        smtp_para['subject'] =  const.DEFAULT_EMAIL_NOTIFICATION
    
    if args.to != None:
        smtp_para['to'].clear()
        for a in  args.to:
            smtp_para['to'].append( a )
    
    if args.cc != None:
        smtp_para['cc'].clear()
        for a in  args.cc:
            smtp_para['cc'].append( a )
    
    if args.bcc != None:
        smtp_para['bcc'].clear()
        for a in  args.bcc:
            smtp_para['bcc'].append( a )
        
    if args.fromalias != None:
            smtp_para['fromalias'] = args.fromalias
    # to get accepted as email the FROM field must contain a string for some email servers Gmail needs it for sure.
    if len( smtp_para['fromalias'] ) < 1:
        smtp_para['fromalias'] = "P1 monitor version " + const.P1_VERSIE 

    if args.messagehtml != None:
            smtp_para['messagehtml'] = args.messagehtml

    if args.messagetext != None:
            smtp_para['messagetext'] = args.messagetext

    if args.timeout != None:
        smtp_para['timeout'] = int( args.timeout )
    
    if args.attachment != None:
        #print ( args.attachment )
        for a in args.attachment:
            smtp_para['attachments'].append( a )

    flog.debug(inspect.stack()[0][3]+": parameters na CLI parsing:" + str( smtp_para ) )
 
    #check if at least one reciever is given.
    cnt_valid_senders = 0
    for x in [ smtp_para['to'], smtp_para['cc'], smtp_para['bcc'] ]:
        if len(x) >0:
            cnt_valid_senders += 1

    if cnt_valid_senders == 0:
        flog.critical (inspect.stack()[0][3] + ": geen TO,CC of BCC ontvangers opgegeven.")
        sys.exit( 1 )

    # 1 Start an SMTP connection that is secured from the beginning using SMTP_SSL().
    # 2 Start an unsecured SMTP connection that can then be encrypted using .starttls()
    # 3 Fallback to unsecure plaintext email.
    
    if sendSmtpMail('ssl') == False:
        flog.info(inspect.stack()[0][3] + ": SSL/TSL verbinding is niet gelukt.")
        if sendSmtpMail('starttls') == False:
            flog.info(inspect.stack()[0][3] + ": STARTTLS verbinding is niet gelukt.")
            if sendSmtpMail('plaintext') == False:
                flog.error("plaintext is mislukt gestopt.")
                sys.exit(1)

    #print ( sendSmtpMail('plaintext') )
    #print ( sendSmtpMail( 'starttls' ) )
    #print (  sendSmtpMail('ssl') )

    flog.info(inspect.stack()[0][3] + ": Programma is succesvol gestopt.")
    rt_status_db.timestamp( 82, flog )
    sys.exit(0) # all is well.


def sendMessage( server ):
    flog.debug(inspect.stack()[0][3]+": sending message to mail user: " + smtp_para['mailuser'] )

    message = MIMEMultipart("alternative")

    message["Subject"]  = smtp_para['subject']
    message["From"]     =  '"' + smtp_para['fromalias']+'"' + ' <' + smtp_para['mailuser'] + '> '
    message["To"]       = ", ".join( smtp_para['to'] )
    message["Cc"]       = ", ".join( smtp_para['cc'] )
    # not add BCC it wil show in the email.

    flog.debug(inspect.stack()[0][3]+": Subject:"   + str( message["Subject"] ) )
    flog.debug(inspect.stack()[0][3]+": From:"      + str( message["From"]    ) )
    flog.debug(inspect.stack()[0][3]+": To:"        + str( message["To"]      ) )
    flog.debug(inspect.stack()[0][3]+": Cc:"        + str( message["Cc"]      ) )
    flog.debug(inspect.stack()[0][3]+": Bcc:"       + str( smtp_para['bcc']   ) )

    part1 = MIMEText( smtp_para['messagetext'],  "plain" )
    part2 = MIMEText( smtp_para['messagehtml'] , "html"  )

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    if len( smtp_para['messagetext'] ) > 0:
       message.attach( part1 )
    if len( smtp_para['messagehtml'] ) > 0:
       message.attach( part2 )

    try:

        # adding attachments when available. 
        for file_and_path in smtp_para['attachments']:
            flog.debug(inspect.stack()[0][3]+": processing attachment:" + str( file_and_path ) )
            _head, filename = os.path.split( file_and_path  ) 

            # Open file in binary mode
            with open( file_and_path , "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64( part )

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition", "attachment; filename=" + filename,
            )

            # Add attachment to message and convert message to string
            message.attach( part )
      

        # go ahead send the thing
        #server.sendmail( smtp_para['mailuser'], smtp_para['mailuser'], message.as_string() )
        server.sendmail( smtp_para['mailuser'], ( smtp_para['to'] + smtp_para['cc'] + smtp_para['bcc'] ) , message.as_string() )

        server.quit()

    except Exception as e:
        flog.error(inspect.stack()[0][3]+": error " + str ( e ) )
        raise Exception('attachments error')

# return True on Succes and False on error.
# modes supported: secure, startls, nonsecure
def sendSmtpMail( mode='ssl' ):
    r = True
    flog.debug(inspect.stack()[0][3]+": gestart., timeout is " + str( smtp_para['timeout'] ) + " seconden." )
    try:

        if mode == 'ssl':
            flog.info(inspect.stack()[0][3]+": email security mode gebruikt is SSL/TLS ") 
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL( smtp_para['mailserver'], int( smtp_para['mailserverport_ssl'] ), context=context , timeout= int( smtp_para['timeout']) ) as server:
                server.login( smtp_para['mailuser'], smtp_para['mailuserpassword'] )
                if flog.getLevel() == logger.logging.DEBUG:
                    server.set_debuglevel(2)
                sendMessage( server )

        elif mode == 'starttls':
            flog.info(inspect.stack()[0][3]+": email security mode gebruikt is STARTTLS") 
            context = ssl.create_default_context()
            server = smtplib.SMTP( smtp_para['mailserver'], int( smtp_para['mailserverport_starttls'] ) , timeout= int( smtp_para['timeout'] ) )
            if flog.getLevel() == logger.logging.DEBUG:
                server.set_debuglevel(2)
            server.starttls( context=context ) # Secure the connection
            server.login( smtp_para['mailuser'], smtp_para['mailuserpassword'] )
            sendMessage( server )

        elif mode == 'plaintext':
            flog.info(inspect.stack()[0][3]+": email security mode gebruikt is PLAINTEXT (onveilig).") 
            server = smtplib.SMTP( smtp_para['mailserver'], int( smtp_para['mailserverport_plaintext']), timeout= int( smtp_para['timeout'] ) )
            if flog.getLevel() == logger.logging.DEBUG:
                server.set_debuglevel(2)
            server.login( smtp_para['mailuser'], smtp_para['mailuserpassword'] )
            sendMessage( server )

    except smtplib.SMTPAuthenticationError as e:
        flog.error( inspect.stack()[0][3]+": naam en/of wachtwoord probleem " + str( e ) )
        r = False
    except smtplib.SMTPSenderRefused as e:
        flog.error( inspect.stack()[0][3]+": email user probleem " + str( e ) )
        r = False
    except smtplib.SMTPConnectError as e:
        flog.error( inspect.stack()[0][3]+": verbinding met server mislukt " + str( e ) )
        r = False   
    except IOError as e:
        if e.errno == 101:
            flog.error(inspect.stack()[0][3]+": Timeout van " + str( smtp_para['timeout'] ) + " seconden." ) 
        r = False  
    except Exception as e:
        flog.error( inspect.stack()[0][3]+":(andere fouten) " + str( e ) )
        r = False

    if r == False:
        flog.error(inspect.stack()[0][3]+": Gestopt. security mode gebruikt is " + str( mode ) ) 

    return r

#-------------------------------
if __name__ == "__main__":
    try:
        logfile = const.DIR_FILELOG + prgname + ".log"
        util.setFile2user( logfile,'p1mon' )
        flog = logger.fileLogger( logfile,prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str( e.args[0] ) )
        sys.exit(10) #  error: no logging check file rights

    Main(sys.argv[1:])
