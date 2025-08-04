import sqlite3

#################################################################
# structure information 
#@ ID a unique id multiple records are used                                         
#@ DATA_ID, used to select type of data and period 
## kWh 
# 1: kWh min consumption
# 2: kWh hour consumption
# 3: kWh day consumption
# 4: kWh month consumption
# 5: kWh year consumption
# 6: kWh min production
# 7: kWh hour production
# 8: kWh day production
# 9: kWh month production
# 10: kWh year production
## Gas
# 11: gas hour
# 12: gas day
# 13: gas month
# 14: gas year
## Water 
# 15: water min
# 16: water hour
# 17: water day
# 18: water month
# 19: water year
#@ ACTIVE, use the record for updates and display. 0=False.
## periods when selected. 
#@ TIMESTAMP_START
#@ TIMESTAMP_STOP 
#@ MODE
## type of statistic
# 0: not defined
# 1: Average 
# 2: Maximum
# 3: Minimum
# 4: Sum
## result of the statics calculation
#@ VALUE
#@ UPDATED: timestamp of last update or null when never.

class StatisticDb():

    def init( self, dbname, table, flog=None):
        self.flog = flog
        #print( dbname, table )
        self.dbname = dbname
        self.con = sqlite3.connect( dbname )
        self.cur = self.con.cursor()
        self.table = table
        sql = "CREATE TABLE IF NOT EXISTS " + table + "(\
        ID INTEGER PRIMARY KEY NOT NULL, \
        DATA_ID INTEGER DEFAULT 0, \
        ACTIVE INTEGER  DEFAULT 0, \
        TIMESTAMP_START TEXT DEFAULT '', \
        TIMESTAMP_STOP TEXT DEFAULT '', \
        MODE INTEGER DEFAULT 0, \
        VALUE REAL DEFAULT 0, \
        UPDATED TEXT DEFAULT '' \
        );"
       
        self.cur.execute( sql ) 
        self.close_db()
        #self.set_all_default_records()

    """
    def set_all_default_records( self ):
        r = range(1, 20) # index + 1, due to 
        for n in r:
            self.insert_when_exists_not(n)
    """
    
    # maybe for the future.
    """ 
    def insert_when_exists_not( self, data_id=0 ):
        rec = self.select_rec("SELECT count(DATA_ID) FROM statistics WHERE DATA_ID == " + str(data_id)  + " and MODE == 1" )
        #print ( "SELECT count(DATA_ID) FROM statistics WHERE DATA_ID == " + str(data_id)  + " and MODE == 1" ) 
        #print ( rec[0][0] )
        if ( rec != None ):
            if( rec[0][0] == 0 ):
                #print ( "insert")
                sql_str = "insert or ignore into " + self.table + "( DATA_ID, MODE, SYSTEM_DEFAULT ) values (" + str(data_id) + ", 1, 1);" 
                #print ( sql_str )
                self.execute( sql_str )
    """

    def execute( self, sqlstr ):
        self.con = sqlite3.connect( self.dbname )
        self.cur = self.con.cursor()
        self.cur.execute( sqlstr )
        self.con.commit()
        self.close_db()

    def select_rec( self, sqlstr ):
        self.con = sqlite3.connect( self.dbname )
        self.cur = self.con.cursor()
        self.cur.execute( sqlstr )
        r=self.cur.fetchall()
        self.close_db()
        return r 
    
    def insert_rec( self,sqlstr ):
        self.con = sqlite3.connect( self.dbname )
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag( self ):
        self.con = sqlite3.connect( self.dbname )
        self.con.execute("VACUUM;")
        self.close_db()
    
    def integrity_check( self ):
        self.con = sqlite3.connect( self.dbname )
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

    def close_db(self):
        if self.con:
            self.con.close()
