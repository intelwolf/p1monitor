########################################
# sqlite lib for general functions     #
########################################
import sqlite3
import inspect
import filesystem_lib
import time

#import sys

sqlite_table_colum_info = {
    'column_index'              : 0,
    'column_name'               : '',
    'column_type'               : '',
    'not_null'                  : 0,
    'default_value'             : '',
    'part_of_the_primary_key'   : 0
}


####################################################################
# write sql statements to a file als logical backup/export         #
####################################################################
class Sql2File():
    
    ############################################################################
    # db_pathfile file that holds the database                                 #
    # table: table in the datbase                                              #
    # file: the file used to write the sql statments                           #
    # sql_order_index: 0 tot max fields -1 used on the order select statment   #
    # sql_update_mode, sql statment for the insert(0), update(1) or replace(2) #
    # TODO insert and update ** use only lower case sql stamenents             #
    ############################################################################
    def init( self, db_pathfile=None, table=None, filename=None, sql_order_index=0, sql_update_mode=2, flog=None ):
        self.db_pathfile     = db_pathfile
        self.table           = table
        self.flog            = flog
        self.filename        = filename
        self.sql_order_index = sql_order_index
        self.sql_update_mode = sql_update_mode # not used in this version
        self.sql_update_sql  = "replace into" #default
        self.sql_order_field = None

    def execute( self ):

        try:
            # make sql select and update queries
            sql_util = SqliteUtil()
            sql_util.init( db_pathfile=self.db_pathfile, flog=self.flog )
            tab_struct = sql_util.table_structure_info( table=self.table )
            if len(tab_struct) == 0:
                raise Exception( "tabel bestaat niet of is niet te lezen.")

            column_type_list = []
            sql_select_str = "select "
            sql_update_str = str(self.sql_update_sql) + " " + str(self.table) + " ("
            for idx, c in enumerate( tab_struct ):
                if idx == self.sql_order_index:
                    self.sql_order_field = c['column_name']
                sql_select_str += c['column_name'] + ", "
                sql_update_str += c['column_name'] + ", "
                column_type_list.append(c['column_type'])

            sql_select_str = str(sql_select_str[:-2]) # remove last , and space
            sql_select_str += " from " + str(self.table)  + " order by " + str(self.sql_order_field)

            sql_update_str = sql_update_str[:-2] 
            sql_update_str += ") values ("
            #print(  sql_select_str )
            #print(  sql_update_str )
            #print( column_type_list )

            # get the data 
            con = sqlite3.connect( self.db_pathfile )
            cur = con.cursor()
            cur.execute( sql_select_str )
            r=cur.fetchall()
            if con:
                con.close()

            reccount=0
            f = open( self.filename ,"a")
            for i in r:
                line = sql_update_str
            
                sub_sql = ""
                for idx, _f in enumerate( column_type_list ):
                    sub_sql += _format_db_field(idx, column_type_list, i[idx] ) + ", "
        
                sub_sql = sub_sql[:-2] 
                line = line + sub_sql + ");"

                f.write(line+'\n')
                reccount = reccount + 1

            f.close() # close the file
            return reccount
        
        except Exception as e:
            raise Exception( "uitvoering gefaald -> " + str(e) )


#########################################################
# set the correct field format for the sql staments     #
# make sure TEXT has single quotes and the numeric      #
# values do not                                         #
#########################################################
def _format_db_field(field_index, field_type_list, value):
    try:
        if value == None:
            value = 'NULL'
        if field_type_list[field_index] == "TEXT":
            return "'" + str(value) + "'"
        if field_type_list[field_index] == "REAL" or field_type_list[field_index] == "INTEGER" or field_type_list[field_index] == "NUMERIC":
            return str(value)
    except Exception as e:
        raise Exception( "database field types niet te bepalen. probleem -> " + str(e) )

    return ""


 
class SqlSafeOpen():

    ###########################################
    # init the class                          #
    ###########################################
    def open( self, db_class=None, db_pathfile=None, db_table=None, defrag_on=True, flog=None ):
        try:
            db_class.init(db_pathfile , db_table )
            if defrag_on == True:
                db_class.defrag() 
            #return db_class # all is well 
        except Exception as e:
            try:
                flog.warning( __class__.__name__  + " database niet te openen " + str(db_pathfile) + " tabel " + str(db_table) + " melding:" + str(e.args[0]) )
                flog.warning( __class__.__name__  + " database bestand wordt verwijderd, data verlies is waarschijnlijk.")
                filesystem_lib.rm_with_delay( filepath=db_pathfile, timeout=0, flog=flog )
                filesystem_lib.file_system_sync()
                time.sleep( 1 ) # time to remove file and create a new empty database file. 
                db_class.init(db_pathfile , db_table )
            except Exception as e:
                raise Exception("fout" + str(db_pathfile) + " tabel " + str(db_table) + " melding:" + str(e.args[0]) )
            
        #return db_class #all is well, but we lost some records :( 
        


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
    # make a query on the availabel columns   #
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





