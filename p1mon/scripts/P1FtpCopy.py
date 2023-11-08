# run manual with ./P1FtpCopy

import argparse
import base64
import const
import crypto3
import ftplib
import inspect
import logger
import os.path
import sys
import shutil
import subprocess
import sqldb
import re

from ftplib import FTP_TLS
#from sqldb import configDB,rtStatusDb
#from logger import *
from util import setFile2user,getUtcTime
from subprocess import check_output

prgname         = 'P1FtpCopy'
fileprefix      = 'P1BU-'
config_db       = sqldb.configDB()
rt_status_db    = sqldb.rtStatusDb()

# because of ea bug in sftlib we are now using shell comands to connect with FTSP (curl) 
# this problem occured during the upgrade to buster and python 3.7 

ftp_para = {
    'user':'', 
    'password':'',
    'directory':'',
    'server':'',
    'port':21,
    'filename':'',
    'maxfilecount':0,
    'ftps':0 ,
    'sftp':0 ,
    'ftp':0
}

def Main(argv): 
    flog.info("Start van programma.")
    global ftp_para 

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

    rt_status_db.timestamp(47,flog)

# update field from database, the cli switches overwrite the DB values!
    _id,ftp_para['user']         ,_label = config_db.strget(28,flog)
    _id,ftp_para['password']     ,_label = config_db.strget(29,flog)
    _id,ftp_para['directory']    ,_label = config_db.strget(30,flog)
    _id,ftp_para['server']       ,_label = config_db.strget(31,flog)
    _id,ftp_para['port']         ,_label = config_db.strget(32,flog)
    _id,ftp_para['filename']     ,_label = config_db.strget(33,flog)
    _id,ftp_para['maxfilecount'] ,_label = config_db.strget(34,flog)
    _id,ftp_para['ftps']         ,_label = config_db.strget(35,flog) # was secure
    _id,ftp_para['ftp']          ,_label = config_db.strget(76,flog)
    _id,ftp_para['sftp']         ,_label = config_db.strget(77,flog)
    # sftp toevoegen. ftp toevoegen

    flog.debug(inspect.stack()[0][3]+": parameters uit de DB:"+str(ftp_para))

    parser = argparse.ArgumentParser(description="ftp....")
    parser.add_argument('-u'    , '--user',         required=False)
    parser.add_argument('-pw'    , '--password',     required=False)
    parser.add_argument('-dir'    , '--directory',    required=False)
    parser.add_argument('-srv'    , '--server',       required=False)
    parser.add_argument('-fname', '--filename',     required=False)    
    parser.add_argument('-mfcnt', '--maxfilecount', required=False)
    parser.add_argument('-pt'    , '--port',         required=False)
    parser.add_argument('-ftps'    , '--ftps',         required=False, action="store_true") # flag only
    parser.add_argument('-sftp'    , '--sftp',         required=False, action="store_true") # flag only
    parser.add_argument('-ftp'  , '--ftp',          required=False, action="store_true") # flag only

    args = parser.parse_args()
    if args.user != None:
        ftp_para['user'] = args.user

    if args.password != None:
        ftp_para['password'] = args.password
        flog.debug( "password van commandline ontvangen -> " + ftp_para['password'] )
    else: #decode password from database
        try:
            ftp_para['password'] = base64.standard_b64decode(crypto3.p1Decrypt(ftp_para['password'],'ftppw') ).decode('utf-8')
            #  added by Aad
            if ftp_para['password'] == '':
                ftp_para['password'] = "''"
                raise Exception(" wachtwoord is niet ingesteld.")
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": password decodering gefaald. Decoded password=" +\
                ftp_para['password']+" Gestopt. melding:" + str(e.args[0]) )
            sys.exit(16)
        flog.info("Password decryptie ok.")
        flog.debug("Decoded password = " + ftp_para['password'])


    if args.directory != None:
        ftp_para['directory'] = args.directory

    if args.server != None:
        ftp_para['server'] = args.server
    else:
        try:
            if ftp_para['server'] == '':
                ftp_para['server'] = "''"
                raise Exception("server adres (IP adres of url) is niet ingesteld.")
        except Exception as e:
            flog.error(inspect.stack()[0][3]+": Gestopt, melding: " + str(e.args[0]) )
            sys.exit(17)

    if args.filename != None:
        ftp_para['filename'] = args.filename

    if args.maxfilecount != None:
        ftp_para['maxfilecount'] = int(args.maxfilecount)

    if args.port != None:
        ftp_para['port'] = int(args.port)

    if args.ftp == True:
        ftp_para['ftp']         = 1
        ftp_para['ftps']        = 0 
        ftp_para['sftp']        = 0

    if args.ftps == True:
        ftp_para['ftp']         = 0
        ftp_para['ftps']        = 1 
        ftp_para['sftp']        = 0

    if args.sftp == True:
        ftp_para['ftp']         = 0
        ftp_para['ftps']        = 0 
        ftp_para['sftp']        = 1

    flog.debug(inspect.stack()[0][3]+": parameters na CLI parsing:"+str(ftp_para))

    if int(ftp_para['ftp'])==0 and int(ftp_para['ftps'])==0 and int(ftp_para['sftp'])==0:
         flog.warning( inspect.stack()[0][3]+": geen ftp, ftps of sftp opties geslecteerd!" )

    if os.path.isfile(ftp_para['filename']) == False:
        rt_status_db.strset('fout: te kopieren bestand niet gevonden. Gestopt.',48,flog)
        flog.error(inspect.stack()[0][3]+": te kopieren bestand niet gevonden. Gestopt.")
        sys.exit(17)    

    # do normal plain text FTP
    if int(ftp_para['ftp']) == 1:
        flog.info(inspect.stack()[0][3]+": probeer bestand  " + ftp_para['filename'] + " te kopieren via ftp.")
        try:
            ftpConnection = ftpConnect()
            if len(ftp_para['directory']) > 0:
                ftpChangeDirectory(ftpConnection, ftp_para['directory'])
            ftpCopy(ftpConnection, ftp_para['filename'])
            flog.info(inspect.stack()[0][3]+": bestand  " + ftp_para['filename'] + " succesvol gekopierd via ftp.")
            ftpConnection.quit() # be polite to ftp servers
        except Exception as e:
            rt_status_db.strset('fout: server antwoord: '+str(e.args[0])+' Gestopt.',48,flog)
            flog.error(inspect.stack()[0][3]+": FTP server antwoord: "+str(e.args[0])+" Gestopt.")
            sys.exit(11)    

        rt_status_db.strset( "FTP transfer is succesvol gestopt.", 48, flog )
        rt_status_db.timestamp( 49,flog )
        flog.info( "FTP transfer is succesvol gestopt." )
        sys.exit(0) # all is well.

    # TODO ftps en sftp aanpassen zodat ze poort meenemen.
    # do ftps FTP with SSL
    if int(ftp_para['ftps']) == 1:
        
        #################################################################
        # STEP 1 copy the file                                          #
        #################################################################
        try: # copying file

            #flog.setLevel( logging.DEBUG )

            _head,tail = os.path.split( ftp_para['filename'] ) 
            changed_filename    = '//p1mon/mnt/ramdisk/' + fileprefix + str(getUtcTime()) + '-' + tail
            #server              = "ftps://"+ftp_para['server']
            server              = "ftp://"+ftp_para['server'] #+ ":990"
            if len(ftp_para['directory']) > 0:
                server  = server + "/" + ftp_para['directory'] + "/" # checked can handle // and / in path.
            
            flog.debug( inspect.stack()[0][3]+": server path is=" + str(server ) )
            shutil.copy( ftp_para['filename'], changed_filename )


            flog.info(inspect.stack()[0][3]+": probeer bestand  " + ftp_para['filename'] + " te kopieren via ftps.")
            
            """
            cp = subprocess.run([ "curl",  "--ssl-reqd", "--ftp-ssl-control", "-ssl", "--globoff", "--insecure", "-sSv", server, "--user", ftp_para['user']+":"+ftp_para['password'], "-T", changed_filename  ], \
                universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60 )
            """
            
            cp = subprocess.run([ "curl", "--ftp-ssl-control", "--ftp-ssl" ,"--globoff", "--insecure", "-sSv", server, "--user", ftp_para['user']+":"+ftp_para['password'], "-T", changed_filename  ], \
                universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60 )

            flog.debug( inspect.stack()[0][3]+": cp.stdout="        + str(cp.stdout) )
            flog.debug( inspect.stack()[0][3]+": cp.stderr="        + str(cp.stderr) )
            flog.debug( inspect.stack()[0][3]+": cp.returncode="    + str(cp.returncode ) )

            # Added by Aad.
            saveDelete( changed_filename ) # remove tmp copy of file.

            if cp.returncode == 0:
                flog.info(inspect.stack()[0][3]+": bestand  " + ftp_para['filename'] + " succesvol gekopierd via ftps als " + changed_filename )
            else:
                raise Exception( cp.stderr.replace("\n","") )

        except Exception as e:
            rt_status_db.strset('fout: server antwoord: '+str( e.args[0 ])+' Gestopt.',48,flog)
            flog.error(inspect.stack()[0][3]+": SFTP server antwoord: "+str(e.args[0])+" Gestopt.")
            sys.exit(11)
        
        #################################################################
        # STEP 2 checking if we have reached the maxium number of files #
        #################################################################
        try: # checkin if max files are reached
            _head,tail = os.path.split( ftp_para['filename'] ) 
            changed_filename    = '//p1mon/mnt/ramdisk/' + fileprefix + str(getUtcTime()) + tail
            server              = "ftp://"+ftp_para['server']
            if len(ftp_para['directory']) > 0:
                server  = server + "/" + ftp_para['directory'] + "/" # checked can handle // and / in path.
            
            flog.debug( inspect.stack()[0][3]+": server path is=" + str(server ) )

            cp = subprocess.run([ "curl", "--ftp-ssl-control", "--ftp-ssl", "--globoff", "--insecure", "-sS", server, "--user", ftp_para['user']+":"+ftp_para['password'], "--list-only" ], \
                 universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60 )
            
            #flog.debug( inspect.stack()[0][3]+": cp.stdout="        + str(cp.stdout) )
            #flog.debug( inspect.stack()[0][3]+": cp.stderr="        + str(cp.stderr) )
            #flog.debug( inspect.stack()[0][3]+": cp.returncode="    + str(cp.returncode ) )

            if cp.returncode == 0: # process output, proces files based on epoch value in filename
                filtered_file_list = grep("\AP1BU-\d+", cp.stdout.split('\n') )
                if len(filtered_file_list) < int(ftp_para['maxfilecount'])-1: 
                    flog.info(inspect.stack()[0][3]+": maximale aantal van files "+str(ftp_para['maxfilecount'])+" niet gehaald ("+str(len(filtered_file_list))+")")
                else:
                    flog.info(inspect.stack()[0][3]+": maximale aantal van files overschreden "+str(ftp_para['maxfilecount']))
                    ftpsRemoveOldFiles( filtered_file_list )
            else:
                raise Exception( cp.stderr.replace("\n","") )
        except Exception as e:
            rt_status_db.strset( 'fout: directory list server : ' + str(e.args[0]) + ' Gestopt.', 48, flog )
            flog.error( inspect.stack()[0][3]+": SFTP directory list server fout: " + str(e.args[0]) + " Gestopt." )
            sys.exit(13)

        rt_status_db.strset( "FTPS transfer is succesvol gestopt.", 48, flog )
        rt_status_db.timestamp( 49,flog )
        flog.info( "FTPS transfer is succesvol gestopt." )
        sys.exit(0) # all is well.

    # do sftp FTP with SSH
    if int(ftp_para['sftp']) == 1:
        
        #################################################################
        # STEP 1 copy the file                                          #
        #################################################################
        try: # copying file
            _head,tail = os.path.split( ftp_para['filename'] ) 
            tmp_path = '/var/log/p1monitor/'
            changed_filename    = tmp_path + fileprefix + str(getUtcTime()) + '-' + tail
            server              = "sftp://"+ftp_para['server'] + "/"
            if len(ftp_para['directory']) > 0:
                server  = server + ftp_para['directory'] + "/" # checked can handle // and / in path.
            else:
                server  = server + "home/"

            flog.debug( inspect.stack()[0][3]+": server path is=" + str(server ) )

            #print ( "changed_filename " + changed_filename + " filename " + ftp_para['filename'] ) 

            shutil.copy( ftp_para['filename'], changed_filename )
            flog.info(inspect.stack()[0][3]+": probeer bestand " + ftp_para['filename'] + " te kopieren via sftp.")
            
            # parameters curl
            # -s Silent or quiet mode. Do not show progress meter or error messages
            # -S When used with -s, --silent, it makes curl show an error message if it fails.
            # -v Makes curl verbose during the operation.
            # --user Specify the user name and password to use for server authentication.
            # -T --upload-file <file> Transfer local FILE to destination
            # --globoff This option switches off the "URL globbing parser"specify URLs that contain the letters {}[]
            # --insecure For SFTP and SCP, this option makes curl skip the known_hosts verification

            cp = subprocess.run([ "curl","--globoff", "--insecure", "-sSv", server, "--user", ftp_para['user']+":"+ftp_para['password'], "-T", changed_filename ], \
                universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60 )

            flog.debug( inspect.stack()[0][3]+": cp.stdout="        + str(cp.stdout) )
            flog.debug( inspect.stack()[0][3]+": cp.stderr="        + str(cp.stderr) )
            flog.debug( inspect.stack()[0][3]+": cp.returncode="    + str(cp.returncode ) )

            #Added by Aad.
            saveDelete( changed_filename ) # remove tmp copy of file.

            if cp.returncode == 0:
                flog.info(inspect.stack()[0][3]+": bestand  " + ftp_para['filename'] + " succesvol gekopierd via ftps als " + changed_filename )
            else:
                raise Exception( cp.stderr.replace("\n","") )

        except Exception as e:
            rt_status_db.strset('fout: server antwoord: '+str( e.args[0 ])+' Gestopt.',48,flog)
            flog.error(inspect.stack()[0][3]+": SFTP server antwoord: "+str(e.args[0])+" Gestopt.")
            sys.exit(11)

        #################################################################
        # STEP 2 checking if we have reached the maxium number of files #
        #################################################################
        try: # checkin if max files are reached

            #_head,tail = os.path.split( ftp_para['filename'] ) 
            #changed_filename    = '//p1mon/mnt/ramdisk/' + fileprefix + str(getUtcTime()) + '-' + tail

            server = "sftp://"+ftp_para['server'] + "/"
            if len(ftp_para['directory']) > 0:
                server  = server + ftp_para['directory'] + "/" # checked can handle // and / in path.
            else:
                server  = server + "home/"

            flog.debug( inspect.stack()[0][3]+": server path is=" + str(server ) )

            # Modified by Aad: for clarity, conform curl params: --list-only parameter added.
            cp = subprocess.run([ "curl", "--globoff", "--insecure", "-sSv", server, "--user", ftp_para['user']+":"+ftp_para['password'], "--list-only" ], \
                 universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60 )
            
            flog.debug( inspect.stack()[0][3]+": cp.stdout="        + str(cp.stdout) )
            flog.debug( inspect.stack()[0][3]+": cp.stderr="        + str(cp.stderr) )
            flog.debug( inspect.stack()[0][3]+": cp.returncode="    + str(cp.returncode ) )

            # pre-process output that could have a unspecified layout.
            filtered_file_list=[]
            matched_lines = [line for line in cp.stdout.split('\n') if fileprefix in line]
            for line in matched_lines:
                #filtered_file_list.append ( line[ line.find('P1BU-'): ] )
                #modified by Aad: absolute find filter replaced by variable.
                filtered_file_list.append ( line[ line.find(fileprefix): ] )

            if cp.returncode == 0: # process output, proces files based on epoch value in filename
                if len( filtered_file_list ) < int(ftp_para['maxfilecount'])-1: 
                    flog.info(inspect.stack()[0][3]+": maximale aantal van files "+str(ftp_para['maxfilecount'])+" niet gehaald ("+str(len(filtered_file_list))+")")
                else:
                    flog.info(inspect.stack()[0][3]+": maximale aantal van files overschreden "+str(ftp_para['maxfilecount']))
                    # sftpRemoveOldFiles( filtered_file_list ) # orignal
                    if sftpRemoveOldFiles( filtered_file_list ) == False:
                        flog.info( inspect.stack()[0][3] + " Een of meerdere bestanden >" + str(ftp_para['maxfilecount']) + " zijn niet gewist.")

            else:
                raise Exception( cp.stderr.replace("\n","") )
        except Exception as e:
            rt_status_db.strset( 'fout: directory list server : ' + str(e.args[0]) + ' Gestopt.', 48, flog )
            flog.error( inspect.stack()[0][3]+": SFTP directory list server fout: " + str(e.args[0]) + " Gestopt." )
            sys.exit(13)

        rt_status_db.strset( "SFTP transfer is succesvol gestopt.", 48, flog )
        rt_status_db.timestamp( 49,flog )
        flog.info( "SFTP transfer is succesvol gestopt." )
        sys.exit(0) # all is well.

################################
# delete file, bug fail silent #
################################
def saveDelete( filename ):
    try:
        os.remove( filename )
        flog.debug( inspect.stack()[0][3]+": bestand " + str(filename) + " verwijderd." )
    except Exception:
        pass

def sftpRemoveOldFiles( filtered_file_list ):     
    filtered_file_list.sort(reverse=True)
    server = "sftp://"+ftp_para['server'] + "/"
   
    if len(ftp_para['directory']) > 0:
        path = ftp_para['directory'] + "/" # checked can handle // and / in path.
    else:
        path = "/home/"

    flog.debug( inspect.stack()[0][3]+": server path is=" + str(server ) )
   
    #print ( filtered_file_list )
    try:
        # added by Aad for returning function result.
        RM_error = False
        for item in filtered_file_list[ int(ftp_para['maxfilecount']):]:
            file_and_path = path + item
            flog.debug( inspect.stack()[0][3]+": file and path is=" + str( file_and_path ) )
            
            #added by by Aad: -Q command quote aangepast
            cp = subprocess.run([ "curl", "--globoff", "--insecure", "-sSv", server, "--user", ftp_para['user']+":"+ftp_para['password'], "-Q", '-rm \"/' + file_and_path + '\""' ] , \
                universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60 )
            
            #flog.debug( inspect.stack()[0][3]+": cp.stdout="        + '\r\n' + str(cp.stdout) )
            #flog.debug( inspect.stack()[0][3]+": cp.stderr="        + '\r\n' + str(cp.stderr) )
            #flog.debug( inspect.stack()[0][3]+": cp.returncode="    + str( cp.returncode ) )

            if cp.returncode == 0: # process output, proces files based on epoch value in filename
                flog.info( inspect.stack()[0][3] + ": file " + file_and_path + " gewist.")
            else: 
                flog.info( inspect.stack()[0][3] + ": file " + file_and_path + " niet gewist. cp.returncode = " + str(cp.returncode))
                RM_error = True
        # added by Aad: return false when one or more files > maxfilecount not deleted by -Q quote
        if RM_error == True:
            return False
    except Exception as e:
            #Modified by Aad: better errortext (copy paste failure ?)
            rt_status_db.strset( ' fout: wissen server files > maxfilescount : ' + str(e.args[0]) + ' gestopt.', 48, flog )
            flog.warning( inspect.stack()[0][3]+": waarschuwing probleem met het wissen van bestanden." )
            #added by Aad: exit when system subproces failed
            sys.exit(13)
    # added by Aad: return true when all files > maxfilecount are deleted
    return True


def ftpsRemoveOldFiles( filtered_file_list ):     
    filtered_file_list.sort(reverse=True)
    server = "ftp://"+ftp_para['server']

    #print ( filtered_file_list )
    try:
        for item in filtered_file_list[ int(ftp_para['maxfilecount']):]:
            if len(ftp_para['directory']) > 0:
                file_and_path  = "/" + ftp_para['directory'] + "/" + item # checked can handle // and / in path.
            else:
                file_and_path = item
            #print (file_and_path )
            cp = subprocess.run([ "curl", "--ftp-ssl-control", "--ftp-ssl", "--globoff", "--insecure", "-sS", server, "--user", ftp_para['user']+":"+ftp_para['password'], "-Q", "-DELE "+file_and_path ], \
                 universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60 )
            
            #flog.debug( inspect.stack()[0][3]+": cp.stdout="        + '\r\n' + str(cp.stdout) )
            #flog.debug( inspect.stack()[0][3]+": cp.stderr="        + '\r\n' + str(cp.stderr) )
            #flog.debug( inspect.stack()[0][3]+": cp.returncode="    + str( cp.returncode ) )

            if cp.returncode == 0: # process output, proces files based on epoch value in filename
                 flog.info( inspect.stack()[0][3] + ": file " + file_and_path + " gewist.")
            else: 
                raise Exception( cp.stderr.replace("\n","") )
    except Exception as e:
            rt_status_db.strset( 'fout: directory list server : ' + str(e.args[0]) + ' Gestopt.', 48, flog )
            flog.warning( inspect.stack()[0][3]+": bestand  " + file_and_path + " is niet verwijderd." )
            
def ftpCopy(ftpConnection, filename):
    _head,tail = os.path.split(filename) 
    try:
        ftpConnection.storbinary('STOR '+tail, open(filename, 'rb'), blocksize=128)
    except Exception as e:
        rt_status_db.strset('fout: copy file naar server: '+str(e.args[0])+' Gestopt.',48,flog)
        flog.error(inspect.stack()[0][3]+": copy file naar server: "+str(e.args[0])+" Gestopt.")
        sys.exit(12)
    
    try:
        file_list=ftpConnection.nlst()
    except Exception as e:
        rt_status_db.strset('fout: directory list server : '+str(e.args[0])+' Gestopt.',48,flog)
        flog.error(inspect.stack()[0][3]+": directory list server fout: "+str(e.args[0])+" Gestopt.")
        sys.exit(13)
    
    
    flog.debug(inspect.stack()[0][3]+": file list van FTP server: "+str(file_list))
    try:
        ftpConnection.rename(tail, fileprefix + str(getUtcTime()) + '-' + tail )
    except Exception as e:
        rt_status_db.strset('fout: hernoemen van file ('+tail+') mislukt: '+str(e.args[0])+' Gestopt.',48,flog)
        flog.error(inspect.stack()[0][3]+": hernoemen van file ("+tail+") mislukt: "+str(e.args[0])+" Gestopt.")
        sys.exit(14)
        
    if int(ftp_para['maxfilecount']) > -1:
        flog.debug(inspect.stack()[0][3]+": wissen van oude files staat aan. maximaal aantal files is "+str(ftp_para['maxfilecount']))
        ftpRemoveOldFiles(ftpConnection, file_list)


def ftpRemoveFile(ftpConnection, filename):
    #print("#"+filename)
    try:
        ftpConnection.delete(filename)
        flog.info( inspect.stack()[0][3] + ": file " + filename+ " gewist.")
    except Exception as e:
        rt_status_db.strset('fout: wissen van file ('+ filename +') mislukt: '+str(e.args[0])+' Gestopt.',48,flog)
        flog.error(inspect.stack()[0][3]+": wissen van file "+filename+" mislukt "+str(e.args[0])+" Gestopt.")
        sys.exit(15)

def ftpRemoveOldFiles(ftpConnection, filelist):
    global ftp_para 
    filtered_file_list = grep("\AP1BU-\d+",filelist)
    #print ( filtered_file_list )
    if len(filtered_file_list) < int(ftp_para['maxfilecount'])-1: 
        flog.info(inspect.stack()[0][3]+": maximale aantal van files "+str(ftp_para['maxfilecount'])+" niet gehaald ("+str(len(filtered_file_list))+")")
        return
    else:
        flog.info(inspect.stack()[0][3]+": maximale aantal van files overschreden "+str(ftp_para['maxfilecount']))

    filtered_file_list.sort(reverse=True)
    flog.debug(inspect.stack()[0][3]+": *filtered file list: "+str(filtered_file_list))

    # clean files that beyond the max file count
    for item in filtered_file_list[ int(ftp_para['maxfilecount']):]:
        ftpRemoveFile(ftpConnection,item)

def    ftpChangeDirectory(ftpConnection, directory):
    try:
        ftpConnection.cwd(directory)
    except Exception as e:
        rt_status_db.strset("fout: wijzigen van folder "+directory+" mislukt "+str(e.args[0])+" Gestopt.",48,flog)
        flog.error(inspect.stack()[0][3]+": wijzigen van folder "+directory+" mislukt "+str(e.args[0])+" Gestopt.")
        sys.exit(16)

def ftpConnect():
    global ftp_para
    flog.warning("Er wordt geen beveiligde verbinding gebruikt.")
    ftpConnection = ftplib.FTP()
    ftpConnection.connect( ftp_para['server'], int(ftp_para['port']))
    ftpConnection.login(ftp_para['user'],ftp_para['password'])
    flog.info(inspect.stack()[0][3]+": server: "+ftpConnection.getwelcome())
    return ftpConnection        


def grep(pattern,word_list):
    expr = re.compile(pattern)
    return [elem for elem in word_list if expr.match(elem)]        
     
#-------------------------------
if __name__ == "__main__":
    try:
        logfile = const.DIR_FILELOG+prgname+".log"
        setFile2user(logfile,'p1mon')
        flog = logger.fileLogger( logfile,prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
        sys.exit(10) #  error: no logging check file rights

    Main(sys.argv[1:])
