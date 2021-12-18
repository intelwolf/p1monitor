########################################
# sqlite lib for general functions     #
########################################
import sqlite3
import inspect
import sys


sqlite_table_colum_info = {
    'column_index'              : 0,
    'column_name'               : '',
    'column_type'               : '',
    'not_null'                  : 0,
    'default_value'             : '',
    'part_of_the_primary_key'   : 0
}


class SqliteUtil():

    ###########################################
    # init the class                          #
    ###########################################
    def init( self, db_pathfile=None, flog=None ):
        self.db_pathfile = db_pathfile
        self.con  = sqlite3.connect( self.db_pathfile )
        self.flog = flog
        self.flog.debug( inspect.stack()[0][3] + ": open van database  = " + str( db_pathfile ) )
        self.cursor = self.con.cursor()
        self.close()


    ###########################################
    # make a query on the avaliabel columns   #
    ###########################################
    def query_str(self, table=None, flog=None, sortindex=None ):
        list_of_columns = self.table_structure_info( table=table )

        sort_column_str = None # used to set the colum for sorting, if any
        sql_str = 'select '
        for idx, c in enumerate( list_of_columns ):
            sql_str = sql_str + c['column_name'] + ', '
            #print( idx )
            if sortindex != None:
                if idx == int(sortindex):
                    sort_column_str = c['column_name']

        sql_str = sql_str[:-2] # remove last , and space
        sql_str= sql_str + " from " + table

        if sort_column_str != None:
            sql_str = sql_str + " order by " + sort_column_str
        return sql_str


    ###########################################
    # table info                              #
    ###########################################
    def table_structure_info( self, table=None ):
        list_of_columns = []
        columns = self.select_rec( "PRAGMA table_info("+ table + ")" ) 
        for c in columns:
            column_info = sqlite_table_colum_info.copy()
            column_info['column_index']             = c[0]
            column_info['column_name']              = c[1]
            column_info['column_type']              = c[2]
            column_info['not_null']                 = c[3]
            column_info['default_value']            = c[4]
            column_info['part_of_the_primary_key']  = c[5]
            list_of_columns.append( column_info )
        return list_of_columns

    #####################################################
    # check database file integrity                     #
    #####################################################
    def integrity_check( self ):
        try:
            self.con = sqlite3.connect( self.db_pathfile )
            self.con.cursor().execute( "PRAGMA integrity_check;" )
            self.con.cursor().execute( "PRAGMA foreign_key_check;")
            self.close()
        except Exception as e:
            raise Exception( "database bestand " + self.db_pathfile + " probleem -> " + str(e) )
   
    #####################################################
    # list all tables in a database                     #
    #####################################################
    def list_tables_in_database( self ):
        table_list = []
        sql_list_tables = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        tables = self.select_rec( sql_list_tables )
        if len( tables ) > 0:
            for table in tables:
                table_list.append( str(table[0]))
        return table_list

    #####################################################
    # count records in the database                     #
    #####################################################
    def count_records(self, table=None ):
        #print ( "table[0]=",table[0] )
        sql_count = "SELECT count(*) FROM " + str(table) + ";"
        count_value = self.select_rec( sql_count )
        #print ( str(count_value[0][0]) )
        return str( count_value[0][0] )

    ###########################################
    # select records from the datbase         #
    ###########################################
    def select_rec( self, sqlstr ):
        self.con    = sqlite3.connect( self.db_pathfile )
        self.cursor = self.con.cursor()
        self.cursor.execute( sqlstr )
        r = self.cursor.fetchall()
        self.close()
        return r

    ###########################################
    # close the database                      #
    ###########################################
    def close( self ):
        if self.con:
            self.con.close()

   

