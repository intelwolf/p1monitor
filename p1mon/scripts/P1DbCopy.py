# run manual with ./P1DbCopy

import argparse
import const
import inspect
import os
import pwd
import sys
import shutil
import logger
import process_lib

prgname = 'P1DbCopy'

filelist = [
    const.FILE_DB_E_FILENAME,
    const.FILE_DB_STATUS,
    const.FILE_DB_CONFIG,
    const.FILE_DB_E_HISTORIE,
    const.FILE_DB_FINANCIEEL,
    const.FILE_DB_WEATHER,
    const.FILE_DB_WEATHER_HISTORIE,
    const.FILE_DB_TEMPERATUUR_FILENAME,
    #const.FILE_DB_WATERMETER,
    const.FILE_DB_PHASEINFORMATION,
    const.FILE_DB_POWERPRODUCTION,
    const.FILE_DB_WATERMETERV2
]

def Main(argv):

    flog.info( "Start van programma " + prgname + "." )
    flog.info(inspect.stack()[0][3]+": wordt uitgevoerd als user -> " + pwd.getpwuid( os.getuid() ).pw_name )

    parser = argparse.ArgumentParser(description='help informatie')
    parser.add_argument( '-sf',      '--sourcefile',           required=False )
    parser.add_argument( '-df',      '--destinationfolder',    required=False )
    parser.add_argument( '-fc',      '--forcecopy',            required=False, action="store_true" ) #copy always even if file exists
    parser.add_argument( '-s2disk',  '--serialcopy2disk',      required=False, action="store_true" )
    parser.add_argument( '-all2ram', '--allcopy2ram',          required=False, action="store_true" )
    parser.add_argument( '-all2disk','--allcopy2disk',         required=False, action="store_true" )
    parser.add_argument( '-t2disk',  '--temperature2disk',     required=False, action="store_true" )
    parser.add_argument( '-w2disk',  '--watermeter2disk',      required=False, action="store_true" )
    parser.add_argument( '-w2ram',   '--watermeter2ram',       required=False, action="store_true" )
    parser.add_argument( '-pp2disk', '--powerproduction2disk', required=False, action="store_true" )
    parser.add_argument( '-pp2ram',  '--powerproduction2ram',  required=False, action="store_true" )

    args = parser.parse_args()

    # print ( args )
    # single file copy 
    if args.sourcefile != None and args.destinationfolder != None:
        flog.info(inspect.stack()[0][3]+": single file copy.")
        copyFile( args.sourcefile, args.destinationfolder , args.forcecopy)
        return

    ####################
    # to disk copy set #
    ####################

    #watermeter ram to disk copy
    if args.watermeter2disk == True:
        flog.info(inspect.stack()[0][3]+": watermeter bestand naar disk.")
        makeBackupFileSet( diskPathByFilename( const.FILE_DB_WATERMETERV2 ) )
        copyFile( const.FILE_DB_WATERMETERV2 , const.DIR_FILEDISK, args.forcecopy )
        return

    #powerproduction to ram to disk copy
    if args.powerproduction2disk == True:
        flog.info(inspect.stack()[0][3]+": kWh eigen levering bestand naar disk.")
        makeBackupFileSet( diskPathByFilename( const.FILE_DB_POWERPRODUCTION) )
        copyFile( const.FILE_DB_POWERPRODUCTION , const.DIR_FILEDISK, args.forcecopy )
        return

    """
    #watermeter to ram to disk copy
    if args.temperature2disk == True:
        flog.debug(inspect.stack()[0][3]+": watermeter bestand maar disk.")
        copyFile( const.FILE_DB_WATERMETER , const.DIR_FILEDISK, args.forcecopy )
        return
    """

    #temperature to ram to disk copy
    if args.temperature2disk == True:
        flog.info(inspect.stack()[0][3]+": temperatuur bestand naar disk.")
        makeBackupFileSet( diskPathByFilename( const.FILE_DB_TEMPERATUUR_FILENAME ) )
        copyFile( const.FILE_DB_TEMPERATUUR_FILENAME , const.DIR_FILEDISK, args.forcecopy)
        return

    #serial to ram to disk copy
    if args.serialcopy2disk == True:
        flog.info(inspect.stack()[0][3]+": serialcopy2disk.")
        #print ( 'serialcopy2disk' )
        #print ( const.FILE_DB_E_FILENAME )
        #print ( const.DIR_FILEDISK )
        makeBackupFileSet( diskPathByFilename( const.FILE_DB_E_FILENAME ) )
        copyFile( const.FILE_DB_E_FILENAME , const.DIR_FILEDISK, args.forcecopy)
        return

    #all to ram to disk copy
    if args.allcopy2ram == True:
        flog.info(inspect.stack()[0][3]+": allcopy2ram")
        listCopy( const.DIR_FILEDISK, const.DIR_RAMDISK, filelist ,args.forcecopy)
        return

    ####################
    # to ram copy set  #
    ####################

    #all to disk to ram copy
    if args.allcopy2disk == True:
        flog.info(inspect.stack()[0][3]+": allcopy2disk")
        listCopy( const.DIR_RAMDISK, const.DIR_FILEDISK, filelist ,args.forcecopy)
        return

    # watermeter disk to ram copy
    if args.watermeter2ram == True:
        flog.info(inspect.stack()[0][3]+": watermeter bestand naar ram.")
        copyFile( diskPathByFilename( const.FILE_DB_WATERMETERV2) , const.DIR_RAMDISK, args.forcecopy )
        return
    
     # watermeter disk to ram copy
    if args.powerproduction2ram == True:
        flog.info(inspect.stack()[0][3]+": kWh eigen levering bestand naar ram.")
        copyFile( diskPathByFilename( const.FILE_DB_POWERPRODUCTION ) , const.DIR_RAMDISK, args.forcecopy )
        return


# functions

##########################################
# make a set if backup files filename.?  #
##########################################
def makeBackupFileSet( filePath ):

    ####################################
    # deactivated in version 1.7.0.    #
    # limited value, mayby used in the #
    # future.                          #
    ####################################

    return


    if ( fileExist( filePath ) == False ):
        #print ( "# 0 geen file = ", filePath )
        return # there is no source file so return.

    # if the first backup does not exits we dont have to shift
    # other files.

    if ( fileExist( filePath + ".1" ) == True ):
        try: # file.1 does exists we have to make room
            #print ( "# 1 rename = ", filePath )
            
            for i in reversed( range( 1, 3) ):
                file_to_rename = filePath + "." + str(i)
                next_file_name = filePath + "." + str(i+1)

                #print ( "# 2 rename = ", file_to_rename, " to ", next_file_name )

                try:
                    if ( fileExist( file_to_rename ) ):
                        os.rename( file_to_rename, next_file_name )
                except Exception as e:
                    print ( "# 3 = ", e )

        except Exception as _e:
            pass
            #print ( "# 4 = ", e )

    try:
        os.rename( filePath, filePath+".1" )
    except Exception as _e:
        pass
        #print ( "# 5 = ", e )


##############################################
# make a complete path to disk from ram path #
##############################################
def diskPathByFilename( filename ):
    _path,tail = os.path.split( filename )
    return const.DIR_FILEDISK + tail

def listCopy( sourcefolder , destinationfolder, filelist, forcecopy ):
    # only make an back=up version of the file when copying to disk
    if destinationfolder == const.DIR_FILEDISK:
         for filename in filelist:
             makeBackupFileSet( diskPathByFilename( filename ) )

    for filename in filelist:
        _path,tail = os.path.split( filename )
        copyFile( sourcefolder+tail, destinationfolder, forcecopy )

def copyFile( sourcefile, destinationfolder, forcecopy ):
    
    _path, file = os.path.split( sourcefile )
    
    """
    print ( "file =",file )
    print ( "_path = ",_path )
    print ( "sourcefile = ",sourcefile )
    print ( "destinationfolder = ", destinationfolder )
    print ( "forcecopy = ", forcecopy )
    print ( "fileExist = ", fileExist(  destinationfolder + file) )
    """

    if forcecopy == False: # only copy when forced
        if fileExist( destinationfolder + file ):
            flog.debug(inspect.stack()[0][3]+": bestand "  + destinationfolder + file + " bestaat en niet gekopierd van " +  sourcefile ) 
            return
    try:
        if fileExist ( destinationfolder + file  ):
            setFile2user( destinationfolder + file )
        shutil.copy2( sourcefile, destinationfolder ) 
        setFile2user( destinationfolder + file )
        flog.debug(inspect.stack()[0][3]+": " + sourcefile + " naar " + destinationfolder + file + " gekopieerd.")
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": kopie " + sourcefile + " naar " + destinationfolder + " fout: " + str(e) )

def setFile2user( filename ):
    try:
        cmd = "sudo /bin/chown -f p1mon:p1mon " + filename
        #if os.system( cmd ) != 0:
        #    raise ValueError('system chown command failed!')
        r = process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog 
        )
        if r[2] > 0:
             raise ValueError('system chown command failed!')

    except Exception as e:
        flog.error(inspect.stack()[0][3]+": setFile2user fout: " + str(e) + "voor file " + filename )
        return False
    return True

def fileExist(filename):
    if os.path.isfile(filename):
        return True
    else:
        return False

#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG+prgname+".log" 
        #setFile2user(logfile,'p1mon')
        flog = logger.fileLogger( logfile, prgname )
        #### aanpassen bij productie
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn(True) 
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit(1)

    Main( sys.argv[1:] )