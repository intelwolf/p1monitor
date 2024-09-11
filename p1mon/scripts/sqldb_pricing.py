import sqlite3

class PricingDb():

    def init( self, dbname, table,flog=None):
        self.flog = flog
        #print dbname, table
        self.dbname = dbname
        self.con = sqlite3.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.cur.execute( "CREATE TABLE IF NOT EXISTS " + table + "(\
        TIMESTAMP TEXT PRIMARY KEY NOT NULL, \
        PRICE_KWH REAL DEFAULT NULL,\
        PRICE_GAS REAL DEFAULT NULL\
        );")
        self.close_db()

    def execute( self, sqlstr ):
        self.con = sqlite3.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute( sqlstr )
        self.con.commit()
        self.close_db()

    def select_rec( self, sqlstr ):
        self.con = sqlite3.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def close_db(self):
        if self.con:
            self.con.close()