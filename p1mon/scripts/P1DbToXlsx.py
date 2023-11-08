# run manual with ./P1DbToXlsx

import argparse
import const
import datetime
import filesystem_lib
import inspect
import logger
import os
import pathlib
#import pwd
#import pytz
import random
import string
import sqlite_lib
import sys
#import subprocess
import time
import util
import xlsxwriter

prgname = 'P1DbToXlsx'

XLSX_SUFFIX = '.xlsx'

def Main( argv ):
    my_pid = os.getpid()

    parser = argparse.ArgumentParser(description="converteren van een sqlite database naar een excel xlsx bestand.",)
    parser.add_argument('-db', '--datebase',
        required=False,
        help="de naam/locatie van het sqlite database bestand dat moet worden omgezet"
        )
    parser.add_argument('-o', '--output',
        required=False,
        help="de naam/locatie van het xlsx bestand, als er geen naam opgeven wordt dan wordt de naam van het database bestand gebruikt met de .xlsx extentie."
        )


    args = parser.parse_args()
    flog.debug( inspect.stack()[0][3] + ": " + str( args ) )

    if args.datebase != None:

        try:

            if not os.path.exists( args.datebase ):
                flog.error(inspect.stack()[0][3] + ": database bestand " + str(args.datebase)  + " niet gevonden, gestopt!")
                sys.exit( 1 )

            # check if output file is set or make the output file name.
            if args.output == None:
                xlxs_filepath = args.datebase + XLSX_SUFFIX
                flog.warning(inspect.stack()[0][3] + ": Excel output bestand niet opgeven. Excel bestand "  + str(xlxs_filepath) + " wordt gebruikt")
            else:
                xlxs_filepath = args.output
                if pathlib.PurePath( xlxs_filepath ).suffix.lower() != XLSX_SUFFIX:
                    xlxs_filepath = xlxs_filepath + XLSX_SUFFIX
                flog.info(inspect.stack()[0][3] + ": Excel output bestand " + str(xlxs_filepath) + " wordt gebruikt")

            if os.path.exists( xlxs_filepath ):
                filesystem_lib.rm_with_delay( filepath=None, timeout=0 )

            # start the conversion
            database_conversion( db_filepath=args.datebase, xlsx_filepath=xlxs_filepath, flog=flog )

            flog.info(inspect.stack()[0][3] + ": Conversie gereed.")
            sys.exit(0)

        except Exception as e:
            flog.error(inspect.stack()[0][3] + ": onverwachte fout -> " + str(e) )
            sys.exit( 1 )
   
    flog.error(inspect.stack()[0][3] + ": Gestopt omdat er geen valide parameters zijn opgegeven." )
    sys.exit( 1 )


######################
##### functions ######
######################

def database_conversion( db_filepath=None, xlsx_filepath=None, flog=None ):

    # use a tempory name to ensure that the download only happens after complition of the file

    random_string = random_string = ''.join( random.choices(string.ascii_uppercase + string.digits, k=24))

    #workbook = xlsxwriter.Workbook( xlsx_filepath )
    # close the workbook to force a write to the file location
    # if this fails we don't have or can procede. 
    #workbook.close()

    tmp_workbook_filename = str( pathlib.PurePath( xlsx_filepath ).parent ) + '/'  + random_string + '.tmp'
    flog.debug( inspect.stack()[0][3] + ": tmp filename " + str( tmp_workbook_filename ) )

    # open again to work with the workbook.
    workbook = xlsxwriter.Workbook( tmp_workbook_filename, {
        'constant_memory': False,  # true saves memory during conversion.
        'tmpdir': '/var/log/p1monitor' # does, not do a lot but is saves in writes to the SDHC card.
        } )

    t=time.localtime()

    # workbook properties
    workbook.set_properties(
        {
        'title'     : str( pathlib.PurePath( xlsx_filepath ).name ),
        'author'    : 'P1-monitor version ' + const.P1_VERSIE + " " + const.P1_SERIAL_VERSION,
        'created'   : datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, hour=t.tm_hour, minute=t.tm_min, second=t.tm_sec),
        'comments'  : 'Created with ' + prgname 
        })

    #workbook.set_custom_property('Source',  str( pathlib.PurePath( db_filepath ).name ) )
    workbook.set_custom_property('Source',  'xxxx') 
    workbook.set_custom_property('Checked by',       'Eve')

    #workbook formating etc.
    xlsx_bold = workbook.add_format({'bold': True})

    sql_util = sqlite_lib.SqliteUtil()
    sql_util.init( db_pathfile=db_filepath, flog=flog )
    db_tables_list = sql_util.list_tables_in_database()

    # do a sort so the excel sheet will allways have the same sequence of tabs.
    db_tables_list.sort()
    flog.debug( inspect.stack()[0][3] + ": " + str( db_tables_list ) )

    # walk every table in the datbase and add every tabel to a new tab in the Excel workbook
    for tab in db_tables_list:
        flog.debug( inspect.stack()[0][3] + ": tabel " + str( tab ) + " van database " + str( db_filepath )  + " wordt verwerkt" )
        tab_record_count = sql_util.count_records( table=tab )
        flog.info( inspect.stack()[0][3] + ": tabel " + str(tab) + " bevat " + str( tab_record_count ) + " records." )

        try:
            # add the TAB
            worksheet = workbook.add_worksheet( str( tab ) )

            # get the table structure and set the heading in the excel tab 
            tab_struct = sql_util.table_structure_info( table=tab )
            
            col_width_list = []

            # write the column names
            for idx, c in enumerate( tab_struct ):
                #print ( c['column_name'] , idx )
                worksheet.write( 0 ,idx, c['column_name'], xlsx_bold )
                # set the inital width, do 1.25 to for the bold header font.
                col_width_list.append( len(c['column_name']) * 1.25 )

            worksheet.set_column(0, len(tab_struct)-1, 20)

            # make query to get the content 
            sql_query = sql_util.query_str( table=tab, flog=flog, sortindex=0 )
            records = sql_util.select_rec( sql_query )

            for row, record in enumerate( records ):
                #print ( row, record )
                for col, value in enumerate( record ):
                    #print ( row, col,  value )
                    worksheet.write( row+1 ,col, value )

                    if len(str(value)) > col_width_list[col]:
                        col_width_list[col] = len( str(value) )

            for col, value in enumerate( col_width_list  ):
                # add 2 to width because of bold headers
                worksheet.set_column( col, col, value )

        except Exception as e:
            flog.error(inspect.stack()[0][3] + ": onverwachte fout in database " + str( db_filepath ) + " en tabel " + str( tab ) + " -> " + str(e) )

    # write to file
    workbook.close()

    # rename tmp file to xlsx file
    os.rename( tmp_workbook_filename , xlsx_filepath )


#-------------------------------
if __name__ == "__main__":
    try:
        os.umask( 0o002 )
        logfile = const.DIR_FILELOG + prgname + ".log"
        util.setFile2user( logfile, 'p1mon' )
        flog = logger.fileLogger( logfile, prgname )
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )

    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str(e.args[0]) )
        sys.exit( 1 ) #  error: no logging check file rights

    Main( sys.argv[1:] )

