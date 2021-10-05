import sqlite3 as lite
import inspect
import const
from util import *
from utiltimestamp import utiltimestamp


class configDB():

    def init(self,dbname, table):
        #print "[*DB*] ",dbname, table
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        ID          INTEGER PRIMARY KEY NOT NULL,\
        PARAMETER   TEXT,\
        LABEL       TEXT \
        );")

        # init van tabel. Als de record al bestaat
        # dan wordt er geen record toegevoegd
        # alle records ID moet opvolgende zijn 1,2,3,4,enz....
        self.insert_rec("replace into "+table+\
        " values ('0','"+const.P1_VERSIE+"'                                                    ,'Versie:')") 
        self.insert_rec("insert or ignore into "+table+\
        " values ('1','"+const.TARIEF_VERBR_LAAG+"'                                            ,'Verbruik tarief elektriciteit dal/nacht in euro.')") 
        #self.insert_rec("insert or ignore into "+table+\
        #" values ('1','"+const.TARIEF_VERBR_LAAG+"','Verbruik tarief elektriciteit dal/nacht in euro.')") 
        self.insert_rec("insert or ignore into "+table+\
        " values ('2','"+const.TARIEF_VERBR_HOOG+"'                                            ,'Verbruik tarief elektriciteit piek/dag in euro.')") 
        self.insert_rec("insert or ignore into "+table+\
        " values ('3','"+const.TARIEF_GELVR_LAAG+"'                                            ,'Geleverd tarief elektriciteit dal/nacht in euro.')")  
        self.insert_rec("insert or ignore into "+table+\
        " values ( '4','"+const.TARIEF_GELVR_HOOG+"'                                           ,'Geleverd tarief elektriciteit piek/dag in euro.')")
        self.insert_rec("insert or ignore into "+table+\
        " values ( '5','"+const.TARIEF_VASTRECHT_PER_MAAND+"'                                  ,'Vastrecht tarief elektriciteit per maand in euro.')")
        self.insert_rec("insert or ignore into "+table+\
        " values ( '6','"+const.FILESHARE_MODE_UIT+"'                                          ,'Bestanden delen mode.')")

        # serial data # in version 1.3.0 changed to 115200.
        self.insert_rec("insert or ignore into "+table+" values ( '7' ,'115200'                ,'P1 poort baudrate:')")
        self.insert_rec("insert or ignore into "+table+" values ( '8' ,'8'                     ,'P1 poort bytesize:')") 
        self.insert_rec("insert or ignore into "+table+" values ( '9' ,'N'                     ,'P1 poort pariteit:')")    
        self.insert_rec("insert or ignore into "+table+" values ( '10','1'                     ,'P1 poort stopbits:')") 

        self.insert_rec("insert or ignore into "+table+" values ( '11',''                      ,'Wifi ESSID:')") 
        self.insert_rec("insert or ignore into "+table+" values ( '12',''                      ,'Wifi password (crypto)')") 

        self.insert_rec("insert or ignore into "+table+" values ( '13',''                      ,'Weather API key')")
        self.insert_rec("insert or ignore into "+table+" values ( '14','Amsterdam'             ,'Weather locatie')") 

        self.insert_rec("insert or ignore into "+table+\
        " values ('15','"+const.GAS_TARIEF+"','Verbruik tarief gas in euro.')")
        self.insert_rec("insert or ignore into "+table+\
        " values ( '16','"+const.GAS_VASTRECHT_TARIEF_PER_MAAND+"'                             ,'Vastrecht tarief gas per maand in euro.')")
        # beware default is off.
        self.insert_rec("insert or ignore into "+table+" values ( '17','0'                     ,'basic API aan of uit (1/0)')")
        
        self.insert_rec("insert or ignore into "+table+" values ( '18','1'                     ,'UI actueel levering/verbruik(1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '19','1'                     ,'UI e-historie(1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '20','1'                     ,'UI gas-historie(1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '21','1'                     ,'UI financieel(1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '22','1'                     ,'UI informatie(1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '23','5000'                  ,'UI e-levering maximaal W')")
        self.insert_rec("insert or ignore into "+table+" values ( '24','5000'                  ,'UI e-verbruik maximaal W')")
        # default ID: 6544881	Amsterdam-Zuidoost
        self.insert_rec("insert or ignore into "+table+" values ( '25','6544881'               ,'Weather API ID')")
        self.insert_rec("insert or ignore into "+table+" values ( '26','0'                     ,'weer API aan of uit (1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '27','0'                     ,'historie API aan of uit (1/0)')")
        
        self.insert_rec("insert or ignore into "+table+" values ( '28',''                      ,'FTP user name.')")
        self.insert_rec("insert or ignore into "+table+" values ( '29',''                      ,'FTP wachtwoord.')")
        self.insert_rec("insert or ignore into "+table+" values ( '30',''                      ,'FTP remote directory/folder.')")
        self.insert_rec("insert or ignore into "+table+" values ( '31',''                      ,'FTP server IP/URL')")
        self.insert_rec("insert or ignore into "+table+" values ( '32','21'                    ,'FTP port')")
        self.insert_rec("insert or ignore into "+table+" values ( '33',''                      ,'FTP Filenaam + path om te kopieren')")
        self.insert_rec("insert or ignore into "+table+" values ( '34','10'                    ,'FTP maximaal aantal backup bestanden')")
        self.insert_rec("insert or ignore into "+table+" values ( '35','1'                     ,'FTPS secure connection(1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '36','0'                     ,'FTP back-up aan/uit (1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '37','5:0:*:*:*'             ,'Backup schedule format min:hour:day:month:weekday')")
        self.insert_rec("insert or ignore into "+table+" values ( '38','1'                     ,'gas waarde telegram prefix 1-96.')")
        self.insert_rec("insert or ignore into "+table+" values ( '39','0'                     ,'financiele max. grens waarde')")
        self.insert_rec("insert or ignore into "+table+" values ( '40','0'                     ,'counter value API aan of uit (1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '41','10'                    ,'UI gas-levering maximaal')")
        self.insert_rec("insert or ignore into "+table+" values ( '42','0'                     ,'p1data API aan of uit (1/0)')")
        self.insert_rec("insert or ignore into "+table+" values ( '43','0'                     ,'eigen user interface gebruiken.')") 
        self.insert_rec("insert or ignore into "+table+" values ( '44','0'                     ,'verwarmingstemperatuur gebruiken.')") 
        self.insert_rec("insert or ignore into "+table+" values ( '45','1'                     ,'CRC controle p1 telegram actief.')")
        self.insert_rec("insert or ignore into "+table+" values ( '46','0'                     ,'UI verwarming1/0)')")

        self.insert_rec("insert or ignore into "+table+" values ( '47',''                      ,'Dropbox access token')")
        self.insert_rec("insert or ignore into "+table+" values ( '48','10'                    ,'Dropbox maximaal aantal backup bestanden.')")
        self.insert_rec("insert or ignore into "+table+" values ( '49','0'                     ,'Dropbox back-up aan/uit (1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '50','0'                     ,'Dropbox data delen aan/uit (1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '51','0'                     ,'Controleren op nieuwe p1 monitor versie (1/0).')")

        self.insert_rec("insert or ignore into "+table+" values ( '52','10'                    ,'UI e-verbruik main maximaal')")
        self.insert_rec("insert or ignore into "+table+" values ( '53','5'                     ,'UI e-levering main maximaal')")
        self.insert_rec("insert or ignore into "+table+" values ( '54','1'                     ,'UI gas verbruik main maximaal')")

        self.insert_rec("insert or ignore into "+table+" values ( '55','1'                     ,'UDP broadcast aan/uit (1/0).')")

        self.insert_rec("insert or ignore into "+table+" values ( '56','20'                    ,'UI e-levering maximaal kWh')")
        self.insert_rec("insert or ignore into "+table+" values ( '57','20'                    ,'UI e-verbruik maximaal kWh')")
        
        self.insert_rec("insert or ignore into "+table+" values ( '58',''                      ,'Systeem ID')")
        self.insert_rec("insert or ignore into "+table+" values ( '59','1'                     ,'voorspelling in UI aan (1/0).')")

        # let op deze moet standaard op 1 staan om te voorkomen dat een gebruiker standaard bij gebruik van een inet
        # adres niet bij de config kan komen.
        self.insert_rec("insert or ignore into "+table+" values ( '60','1'                     ,'RFC1918 filtering aan/uit (1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '61','1'                     ,'drie fasen informatie in ui aan/uit (1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '62','1'                     ,'UI meterstanden historie(1/0)')")
        
        # mail notification systeem.
        self.insert_rec("insert or ignore into "+table+" values ( '63', ''                     ,'mail user account') ") 
        self.insert_rec("insert or ignore into "+table+" values ( '64', ''                     ,'mail user wachtwoord(crypto)') ") 
        self.insert_rec("insert or ignore into "+table+" values ( '65', 'niet ingesteld'       ,'mail server hostname') ")
        self.insert_rec("insert or ignore into "+table+" values ( '66', '465'                  ,'mail server SSL/TLS tcp poort') ")
        self.insert_rec("insert or ignore into "+table+" values ( '67', '587'                  ,'mail server STARTTLS tcp poort') ")
        self.insert_rec("insert or ignore into "+table+" values ( '68', '25'                   ,'mail server plaintext tcp poort') ")
        self.insert_rec("insert or ignore into "+table+" values ( '69', 'P1 monitor mailer'    ,'mail onderwerp voor notificaties') ")
        self.insert_rec("insert or ignore into "+table+" values ( '70', ''                     ,'mail TO voor notificaties (list)') ")
        self.insert_rec("insert or ignore into "+table+" values ( '71', ''                     ,'mail FROM alias voor notificaties') ")
        self.insert_rec("insert or ignore into "+table+" values ( '72', '60'                   ,'timeout voor de aflevering van email in seconden.') ")  
        self.insert_rec("insert or ignore into "+table+" values ( '73', '0'                    ,'notificatie alarm als er geen P1 data meer wordt ontvangen(1/0).') ")
        self.insert_rec("insert or ignore into "+table+" values ( '74', ''                     ,'mail CC voor notificaties (list)') ")
        self.insert_rec("insert or ignore into "+table+" values ( '75', ''                     ,'mail BCC voor notificaties (list)') ")
        self.insert_rec("insert or ignore into "+table+" values ( '76','0'                     ,'FTP no secure connection(1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '77','0'                     ,'SFTP secure connection(1/0).')")
        
        # dag nacht mode's
        # NL        = 0
        # Belgie    = 1
        self.insert_rec("insert or ignore into "+table+" values ( '78','0'                     ,'Dag/Nacht mode voor E verwerking.')")
        # screen saver confif
        self.insert_rec("insert or ignore into "+table+" values ( '79','0'                     ,'seconden voordat de screensaver actief wordt. 0 is niet actief.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '80','0'                     ,'seconden nadat de screensaver automatisch uitgeschakeld wordt.')" )
        # powerSwitcher config.
        self.insert_rec("insert or ignore into "+table+" values ( '81','1000'                  ,'gemiddele watt waarde om in te schakelen.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '82','0'                     ,'gemiddele watt waarde om uit te schakelen.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '83','2'                     ,'aantal minuten voor de gemiddele watt waarde voordat wordt ingeschakeld.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '84','2'                     ,'aantal minuten voor de gemiddele watt waarde voordat wordt uitgeschakeld.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '85','27'                    ,'ingestelde GPIO pin, voor schakelen van terug geleverde vermogen.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '86','0'                     ,'vermogen schakelaar aan of uit (0/1).')")
        self.insert_rec("insert or ignore into "+table+" values ( '87','0'                     ,'vermogen schakelaar geforceerd aan of uit (0/1), 0 is automatisch.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '88','0'                     ,'vermogen schakelaar aantal minuten dat aan minimaal actief blijft.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '89','0'                     ,'vermogen schakelaar aantal minuten dat uit minimaal inactief blijft.')" )

        self.insert_rec("insert or ignore into "+table+" values ( '90','0'                     ,'tarief schakelaar aan of uit (0/1).')")
        self.insert_rec("insert or ignore into "+table+" values ( '91','D'                     ,'tarief schakelaar piek of dal tarief (P/D).')")
        self.insert_rec("insert or ignore into "+table+" values ( '92','0'                     ,'tarief schakelaar geforceerd aan of uit (0/1), 0 is automatisch.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '93','0.0.0.0.0.0.0.0.0.0.0' ,'tarief schakelaar timeslot(1) format hh.mm.hh.mm.ma.di.wo.do.vr.za.zo (weekdagen 1 is aan)')" )
        self.insert_rec("insert or ignore into "+table+" values ( '94','0.0.0.0.0.0.0.0.0.0.0' ,'tarief schakelaar timeslot(2) format hh.mm.hh.mm.ma.di.wo.do.vr.za.zo (weekdagen 1 is aan)')" )
        self.insert_rec("insert or ignore into "+table+" values ( '95','22'                    ,'ingestelde GPIO pin, voor schakelen op basis van tarief.')" )

        self.insert_rec("insert or ignore into "+table+" values ( '96','0'                     ,'watermeter meting actief (0/1).')")
        self.insert_rec("insert or ignore into "+table+" values ( '97','17'                    ,'ingestelde GPIO pin, voor het inlezen van watermeter puls.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '98','1.0'                   ,'aantal liter per watermeter puls.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '99','0'                     ,'aantal M3 water op de watermeter')" )
        self.insert_rec("insert or ignore into "+table+" values ( '100',''                     ,'aantal M3 water op de watermeter timestamp.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '101','0'                    ,'reset de watermeter stand,  1 is uitvoeren, 0 is inactief.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '102','0'                    ,'UI watermeter zichtbaar 1/0)')")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '103','" + const.TARIEF_WATER_VASTRECHT_PER_MAAND + "'                      ,'Vastrecht tarief drinkwater per maand in euro.')")
        self.insert_rec("insert or ignore into "+table+\
        " values ( '104','" + const.TARIEF_WATER_TARIEF_PER_M3 + "'                            ,'Tarief drinkwater per m3 in euro.')")

        self.insert_rec("insert or ignore into "+table+" values ( '105','p1monitor'            ,'MQTT client name.')")
        self.insert_rec("insert or ignore into "+table+" values ( '106','p1monitor'            ,'MQTT topic name prefix.')")
        self.insert_rec("insert or ignore into "+table+" values ( '107',''                     ,'MQTT broker user name (account).')")
        self.insert_rec("insert or ignore into "+table+" values ( '108',''                     ,'MQTT broker password.')")
        self.insert_rec("insert or ignore into "+table+" values ( '109',''                     ,'MQTT broker host (IP or dns name).')")
        self.insert_rec("insert or ignore into "+table+" values ( '110','1883'                 ,'MQTT broker host port.')")
        self.insert_rec("insert or ignore into "+table+" values ( '111','60'                   ,'MQTT TCP/IP session alive in seconds.')")
        self.insert_rec("insert or ignore into "+table+" values ( '112','4'                    ,'MQTT protocol version.')")
        self.insert_rec("insert or ignore into "+table+" values ( '113','0'                    ,'MQTT QoS 0,1 of 2')")
        self.insert_rec("insert or ignore into "+table+" values ( '114','0'                    ,'MQTT smartmeter publish aan/uit (1/0).')" )
        self.insert_rec("insert or ignore into "+table+" values ( '115','0'                    ,'MQTT watermeter publish aan/uit (1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '116','0'                    ,'MQTT weer publish aan/uit (1/0).')")
        self.insert_rec("insert or ignore into "+table+" values ( '117','0'                    ,'MQTT kamertemperatuur publish aan/uit (1/0).')")
        # 118 is aanpassen van tcp port, of ander connectie zaken.
        self.insert_rec("insert or ignore into "+table+" values ( '118','1'                    ,'MQTT connectie aanpassen trigger (1 is aanpassen).')")
        self.insert_rec("insert or ignore into "+table+" values ( '119','0'                    ,'Bewaar historische 3 fase informatie in de database (1=ja, 0=nee).')")

        self.insert_rec("insert or ignore into " + table + " values ( '120','0'                ,'MQTT fase publish aan/uit (1/0).')")

        self.insert_rec("insert or ignore into " + table + " values ( '121',''                 ,'verwarming temperatuur in label (leeg wil zeggen dat IN wordt gebruikt).')")
        self.insert_rec("insert or ignore into " + table + " values ( '122',''                 ,'verwarming temperatuur uit label (leeg wil zeggen dat UIT wordt gebruikt).')")
        
        self.insert_rec( "insert or ignore into " + table + " values ( '123','16'              ,'UI Amperage voor drie fase metingen (opties 16, 32 of 64).')")
        self.insert_rec( "insert or ignore into " + table + " values ( '124','4000'            ,'UI Watt voor drie fase metingen (opties 4000, 6000, 8000 of 1000).')" )

        self.insert_rec("insert or ignore into "+table+" values ( '125','0'                    ,'KWh meter productie(S0) meting actief (0/1).')")
        self.insert_rec("insert or ignore into "+table+" values ( '126','26'                   ,'ingestelde GPIO pin, voor het inlezen van KWh meter productie(S0) puls.')" )
        self.insert_rec("insert or ignore into "+table+" values ( '127','0.0005'               ,'aantal kWh per KWh meter productie(S0) puls.')" )

        # opgelet deze regel is bewust een replace geen insert!
        self.insert_rec("replace into "+table+\
            " values ( '128','" + const.P1_PATCH_LEVEL + "'                                     ,'Software patch:')" )

        self.insert_rec("insert or ignore into " + table + " values ( '129','0'                 ,'UI KWh meter productie(S0) zichtbaar 1/0)')")

        self.insert_rec("insert or ignore into " + table + " values ( '130','0'                 ,'aantal kWh op de meter hoog tarief')" )
        self.insert_rec("insert or ignore into " + table + " values ( '131','0'                 ,'aantal kWh op de meter laag tarief')" )
        self.insert_rec("insert or ignore into " + table + " values ( '132',''                  ,'aantal kWh meter timestamp.')" )

        # opgelet deze regel is bewust een replace geen insert!
        self.insert_rec("replace into " + table + " values ('133','" + const.P1_SERIAL_VERSION + "'               ,'Versie nummer:')" ) 

        self.insert_rec("insert or ignore into " + table + " values ( '134','0','Verberg de P1 header in de UI:')")
        self.insert_rec("insert or ignore into " + table + " values ( '135','0'                ,'MQTT programma aan/uit (1/0).')")
        self.insert_rec("insert or ignore into " + table + " values ( '136','0'                ,'MQTT powerproduction publish aan/uit (1/0).')")

        self.insert_rec("insert or ignore into " + table + " values ( '137','0'                ,'P1Sqlimport programma aan/uit (0 is uit >0 is status id en uitvoeren).')")
        self.insert_rec("insert or ignore into " + table + " values ( '138',''                 ,'P1Sqlimport import bestand.')")

        self.insert_rec("insert or ignore into " + table + " values ( '139',''                 ,'SolarEdge API key')")
        self.insert_rec("insert or ignore into " + table + " values ( '140',''                 ,'SolarEdge config json')")
        self.insert_rec("insert or ignore into " + table + " values ( '141','0'                ,'SolarEdge API meting actief (0/1).')")
        self.insert_rec("insert or ignore into " + table + " values ( '142','0'                ,'SolarEdge API alle data herladen actief (0/1).')")
        self.insert_rec("insert or ignore into " + table + " values ( '143','1'                ,'SolarEdge bereken hoog/piek of laag/piek 0 is uit, anders > 0')")
        self.insert_rec("insert or ignore into " + table + " values ( '144','0'                ,'SolarEdge lees alle beschikbare sites van een API key in (1/0).')")
        self.insert_rec("insert or ignore into " + table + " values ( '145','0'                ,'SolarEdge reset de configuratie (1/0).')")
        self.insert_rec("insert or ignore into " + table + " values ( '146','1'                ,'SolarEdge API slimme update frequentie. (1/0)')")
        self.insert_rec("insert or ignore into " + table + " values ( '147','0'                ,'UI Solar Edge kWh productie zichtbaar (1/0)')")

        # Index waarde NL=0, UK=1, FR=2
        self.insert_rec("insert or ignore into " + table + " values ( '148','0'                ,'UI taal selectie 0....n')")

        self.insert_rec("insert or ignore into " + table + " values ( '149','0'                ,'Solar Edge config/DB naar fabrieks instellingen 1/0)')")

        self.insert_rec("insert or ignore into " + table + " values ( '150',''                 ,'Public dynamiche DNS naam.')")

        # DuckDNS
        self.insert_rec("insert or ignore into " + table + " values ( '151',''                 ,'DuckDNS token.')")
        self.insert_rec("insert or ignore into " + table + " values ( '152','1'                ,'DuckDNS is aan(1) of uit(0).')") 
        self.insert_rec("insert or ignore into " + table + " values ( '153','0'                ,'Forceer een DuckDNS update.')") 
        self.insert_rec("insert or ignore into " + table + " values ( '154','0'                ,'P1 data zo snel als mogelijk verwerken(1 max snelheid).')") 

        self.insert_rec("insert or ignore into " + table + " values ( '155','0'                ,'vermogen schakelaar GPIO geinverteerd normaal(0), geinverteerd(1)')")
        self.insert_rec("insert or ignore into " + table + " values ( '156','0'                ,'tarief schakelaar GPIO geinverteerd is normaal(0), geinverteerd(1).')")

        self.insert_rec("insert or ignore into " + table + " values ( '157','0'                ,'UI waterverbruik verbergen (1/0)')")
        self.insert_rec("insert or ignore into " + table + " values ( '158','0'                ,'UI gasverbruik verbergen (1/0)')")

        self.insert_rec("insert or ignore into " + table + " values ( '159',''                 ,'LetsEncrypt email adres')")

        self.insert_rec("insert or ignore into " + table + " values ( '160',''                 ,'P1 API authenticatie tokens.')")
        self.insert_rec("insert or ignore into " + table + " values ( '161','0'                ,'P1 API authenticatie tokens verwerken (1/0).')")

        self.insert_rec("insert or ignore into " + table + " values ( '162','0'                ,'Internet API vlag processing (1/0).')")
        self.insert_rec("insert or ignore into " + table + " values ( '163','0'                ,'Internet API is active(1), niet active(0).')") 

        # static IP addresses 
        self.insert_rec("insert or ignore into " + table + " values ( '164',''                 ,'eth0 static IP adres.')")
        self.insert_rec("insert or ignore into " + table + " values ( '165',''                 ,'wlan0 static IP adres.')")
        self.insert_rec("insert or ignore into " + table + " values ( '166',''                 ,'default gateway static IP adres.')")
        self.insert_rec("insert or ignore into " + table + " values ( '167',''                 ,'domain name server static IP adres.')")

        # values of 168 0=do noting 1=eth0, wlan0=2, default gateway=4, DNS=8
        self.insert_rec("insert or ignore into " + table + " values ( '168','0'                ,'vlag voor static IP adressen, default gateway en DNS.')")
        self.insert_rec("insert or ignore into " + table + " values ( '169','0'                ,'vlag voor het aanvragen van een Dropbox authenticatie token.')")

        self.insert_rec("insert or ignore into " + table + " values ( '170',''                 ,'Dropbox refresh token')")


        #[{"TOKEN": "34FADE76DFEBDDDD", "TIMESTAMP": "2021-06-26 11:12:13"}, {"TOKEN": "FFEE676DESAAAAAF", "TIMESTAMP": "2022-07-30 22:23:59"}]

        # you need an account on www.noip.com before this can be used
        #self.insert_rec("insert or ignore into " + table + " values ( '150',''                 ,'no-ip password')")
        #self.insert_rec("insert or ignore into " + table + " values ( '151',''                 ,'no-ip account name')")
        #self.insert_rec("insert or ignore into " + table + " values ( '152','eth0'             ,'no-ip netwerk device (eth0/wifi).')")
        #self.insert_rec("insert or ignore into " + table + " values ( '153','30'               ,'no-ip update timeout in seconden.')")
        #self.insert_rec("insert or ignore into " + table + " values ( '154','0'                ,'no-ip is aan(1) of uit(0).')")

        self.close_db()

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select ID, PARAMETER, LABEL from '+ self.table +' order by ID')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
        	line = "update " + self.table + " set PARAMETER='"+ str(i[1])+"',LABEL='"+str(i[2])+"' where ID='"+str(i[0])+"';"
        	f.write(line+'\n')
        	reccount=reccount+1
        f.close() #close our file
        return reccount
        
        #setFile2user(filename,'p1mon')  
        #update config set PARAMETER='0.3', LABEL='Versie:' where ID ='1';

    def close_db(self):
        if self.con:
        	self.con.close()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def execute_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()
        
    def strset(self, strtmp, idn, flog):
        sql_update = "update "+self.table+" set PARAMETER='"+str(strtmp)+"' where id="+str(idn)
        #print(sql_update);
        try:
        	self.update_rec(sql_update)
        	#flog.debug(inspect.stack()[1][3]+": config db update: sql="+sql_update)
        except Exception as e:
        	flog.error(inspect.stack()[1][3]+" db config update gefaald voor id="+str(idn)+". Melding="+str(e.args[0]))

    def strget(self, idn, flog):
        sql_select = "select id, parameter, label from "+self.table+" where id="+str(idn)
        try:
        	set = self.select_rec(sql_select)
        	#flog.debug(inspect.stack()[1][3]+": config db select per id: sql="+sql_select)
        	return set[0][0],set[0][1], set[0][2]
        except Exception as e:
        	flog.error(inspect.stack()[1][3]+" db config select gefaald voor id="+str(idn)+". Melding="+str(e.args[0]))

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()


class rtStatusDb():

    def init(self,dbname, table):
        #print dbname, table
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        ID          INTEGER PRIMARY KEY NOT NULL,\
        STATUS      TEXT, \
        LABEL       TEXT, \
        SECURITY    INTEGER  DEFAULT 100\
        );")

        # clean up van het database bestand , file kleiner maken
        #self.con.execute("VACUUM;")
        # init van tabel. Als de record al bestaat
        # dan wordt er geen record toegevoegd     
        self.insert_rec("insert or ignore into "+table+\
        " values ( '1','0','Max dagwaarde Kw verbruik',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '2','"+mkLocalTimeString()+"','Max dagwaarde Kw verbruik (timestamp)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '3','0','Max dagwaarde Kw geleverd',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '4','"+mkLocalTimeString()+"','Max dagwaarde Kw geleverd (timestamp)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '5','onbekend','Tijdstip start van P1 interface(elektrisch):',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '6','onbekend','Tijdstip start database:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '7','onbekend','Tijdstip laatste verwerkt minuten gegevens:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '8','0','Huidige dag KWh verbruik dal/nacht dag (1.8.1)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '9','0','Huidige dag KWh verbruik piek/dag (1.8.2)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '10','0','Huidige dag KWh geleverd dal/nacht dag (2.8.1)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '11','0','Huidige dag KWh geleverd piek/dag (2.8.2)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '12','onbekend','Tijdstip laatste verwerkte uren gegevens:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '13','onbekend','Tijdstip laatste verwerkte dagen gegevens:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '14','onbekend','Tijdstip laatste verwerkte maand gegevens:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '15','onbekend','Tijdstip laatste verwerkte jaar gegevens:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '16','onbekend','Tijdstip laatste verwerkte bericht uit de slimme meter:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '17','onbekend','Tijdstip start watchdog:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '18','0','Processor belasting',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '19','onbekend','Tijd verstreken sinds de laatste herstart:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '20','onbekend','Netwerk LAN IP adres:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '21','0','Ramdisk gebruik.',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '22','0','Besturingssysteem versie:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '23','onbekend','Internet bereikbaar op:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '24','onbekend','Internet bereikbaar:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '25','onbekend','Python versie:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '26','onbekend','Internet IP adres:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '27','onbekend','Internet hostnaam:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '28','onbekend','Netwerk hostnaam:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '29','0','Tijdstip laatste ram naar disk back-up:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '30','0','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '31','0','RAM geheugen belasting:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '32','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '33','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '34','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '35','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '36','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '37','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '38','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '39','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '40','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '41','onbekend','Tijdstip laatste ram naar disk back-up(serial):',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '42','onbekend','Netwerk WifI IP adres:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '43','0','M3 GAS verbruikt:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '44','0','M3 GAS huidige dag verbruikt:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '45','onbekend','Tijdstip laatste verwerkte weer gegevens:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '46','0','P1 data is ok:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '47','onbekend','Tijdstip laatste FTP back-up:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '48','onbekend','FTP back-up start:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '49','onbekend','Tijdstip laatste succesvol FTP back-up:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '50','','Gas verbruik per uur:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '51','onbekend','CPU model:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '52','onbekend','CPU hardware:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '53','onbekend','CPU revision:',0)") 

        self.insert_rec("insert or ignore into "+table+\
        " values ( '54','','',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '55','onbekend','Raspberry Pi model:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '56','onbekend','Tijdstip start UDP daemon:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '57','onbekend','Tijdstip laatste ram naar disk back-up(verwarming):',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '58','onbekend','Tijdstip laatste verwerkte verwarming gegevens:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '59','onbekend','Tijdstip laatste dropbox successvolle authenticatie:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '60','onbekend','Tijdstip laatste Dropbox back-up:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '61','onbekend','Dropbox back-up start:',0)")
        
        self.insert_rec("insert or ignore into "+table+\
        " values ( '62','onbekend','Dropbox backup status:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '63','onbekend','Tijdstip laatste Dropbox data:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '64','','Dropbox data status:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '65','onbekend','Tijdstip start Dropbox daemon:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '66','','Laatste P1 monitor versie:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '67','','Laatste P1 monitor versie datum:',0)") 

        self.insert_rec("insert or ignore into "+table+\
        " values ( '68','','Laatste P1 monitor versie tekst:',0)") 

        self.insert_rec("insert or ignore into "+table+\
        " values ( '69','0','CPU temperatuur:',0)") 

        self.insert_rec("insert or ignore into "+table+\
        " values ( '70','onbekend','Tijdstip start UDP broadcast daemon:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '71','onbekend','Tijdstip laatste UDP broadcast:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '72','onbekend','Netwerk LAN MAC adres:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '73','onbekend','Netwerk Wifi MAC adres:',10)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '74','0','Huidige KW verbruik L1 (21.7.0)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '75','0','Huidige KW verbruik L2 (41.7.0)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '76','0','Huidige KW verbruik L3 (61.7.0)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '77','0','Huidige KW levering L1 (22.7.0)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '78','0','Huidige KW levering L2 (42.7.0)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '79','0','Huidige KW levering L3 (62.7.0)',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '80','onbekend','weer API status',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '81','onbekend','weer API status timestamp',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '82','onbekend','Tijdstip laatste succesvolle email:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '83','0','gemiddele watt waarde voor terug levering schakeling, 0 betekent niet actief.',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '84','onbekend','Tijdstip terug levering, laatste schakeling:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '85','','Dal of Piek tarief:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '86','','Laatste P1 monitor versie URL:',0)") 

        self.insert_rec("insert or ignore into "+table+\
        " values ( '87','onbekend','Tijdstip laatste verwerkte bericht uit de slimme meter (UTC):',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '88','onbekend','Tijdstip tarief schakeling, laatste schakeling:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '89','0','tarief schakeling is actief, 0 betekent niet actief.',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '90','onbekend','Tijdstip laatste verwerkte watermeter puls:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '91','onbekend','Tijdstip laatste verwerkte watermeterstand reset:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '92','onbekend','Serial device dat gebruikt wordt:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '93','onbekend','Status automatische data import:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '94','onbekend','Tijdstip automatische data import:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '95','onbekend','Tijdstip start MQTT client:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '96','onbekend','Tijdstip laatste MQTT client bericht:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '97','onbekend','MQTT client status:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '98','onbekend','Tijdstip start watermeter:',0)")

        self.insert_rec("insert or ignore into "+table+\
        " values ( '99','onbekend','Tijdstip start GPIO daemon:',0)")

        self.insert_rec("insert or ignore into " + table + " values ( '100','0','Huidige Amperage L1 (31.7.0)',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '101','0','Huidige Amperage L2 (51.7.0)',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '102','0','Huidige Amperage L2 (71.7.0)',0)")

        self.insert_rec("insert or ignore into " + table + " values ( '103','0','Huidige Voltage L1 (32.7.0)',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '104','0','Huidige Voltage L2 (52.7.0)',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '105','0','Huidige Voltage L2 (72.7.0)',0)")

        self.insert_rec("insert or ignore into " + table + " values ( '106','onbekend','Tijdstip laatste fase waarde wijziging:',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '107','onbekend','Status van watermeter totaal stand:',0)")

        self.insert_rec("insert or ignore into " + table + " values ( '108','onbekend','Tijdstip start KWh meter productie(S0):',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '109','onbekend','Tijdstip laatste verwerkte KWh meter productie(S0) puls:',0)")
       
        self.insert_rec("insert or ignore into " + table + " values ( '110','','Laatste P1 monitor versie nummer:',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '111','onbekend','Tijdstip laatste verwerkte bericht Solar Edge API:',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '112','onbekend','Tijdstip laatste gefaalde Solar Edge API aanvraag:',0)")

        self.insert_rec("insert or ignore into " + table + " values ( '113','0','Min dagwaarde Kw verbruik',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '114','" + mkLocalTimeString() + "','Min dagwaarde Kw verbruik (timestamp)',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '115','0','Min dagwaarde Kw geleverd',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '116','" + mkLocalTimeString() + "','Min dagwaarde Kw geleverd (timestamp)',0)")

        # Lets Encrypt stuff.
        # status 1=error/not ok, 0=ok/succes, 2=unknow
        self.insert_rec("insert or ignore into " + table + " values ( '117','2','HTTPS certificaat',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '118','2','HTTPS certificaat vernieuwen certificaat',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '119','2','Webserver configuratie',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '120','onbekend','Tijdstip laatste succesvolle certificaat vernieuwing:',0)")
        self.insert_rec("insert or ignore into " + table + " values ( '121','onbekend','Certificaat geldig tot:',0)")

        self.insert_rec("insert or ignore into " + table + " values ( '122','onbekend','Default gateway/router:',0)")

        # fix typo's from version 0.9.15a and up
        sql_update = "update status set label ='Tijdstip laatste verwerkte minuten gegevens:' where id=7"
        self.update_rec(sql_update)
        sql_update = "update status set label ='Tijdstip terug levering, laatste schakeling:' where id=84"
        self.update_rec(sql_update)
        sql_update = "update status set label ='Tijdstip tarief schakeling, laatste schakeling:' where id=88"
        self.update_rec(sql_update)
        sql_update = "update status set label ='Tijdstip laatste verwerkte watermeter puls:' where id=90"
        self.update_rec(sql_update)
        sql_update = "update status set label ='Tijdstip laatste verwerkte watermeterstand reset:' where id=91"
        self.update_rec(sql_update)

        self.close_db()

    def close_db(self):
        if self.con:
        	self.con.close()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def timestamp(self, idn, flog):
        sql_update = "update status set status='"\
        + mkLocalTimeString() + "' where id="+str(idn)
        try:
            self.update_rec(sql_update)
            flog.debug(inspect.stack()[1][3]+": status db update: sql="+sql_update)
        except Exception as e:
            flog.error(inspect.stack()[1][3]+": DB status update gefaald voor id="+str(idn)+". Melding="+str(e.args[0]))

    def strset(self, strtmp, idn, flog):
        sql_update = "update status set status='"+str(strtmp)+"' where id="+str(idn)
        try:
            self.update_rec(sql_update)
            flog.debug(inspect.stack()[1][3]+": status db update: sql="+sql_update)
        except Exception as e:
            flog.error(inspect.stack()[1][3]+" DB status update gefaald voor id="+str(idn)+". Melding="+str(e.args[0]))

    def strget(self, idn, flog):
        sql_select = "select id, status, label, security from "+self.table+" where id="+str(idn)
        try:
            set = self.select_rec(sql_select)
            #flog.debug(inspect.stack()[1][3]+": config db select per id: sql="+sql_select)
            return set[0][0],set[0][1], set[0][2], set[0][3]
        except Exception as e:
            flog.error(inspect.stack()[1][3]+" db status strget gefaald voor id="+str(idn)+". Melding="+str(e.args[0]))	

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

INDEX_SECONDS = 10
INDEX_MINUTE  = 11
INDEX_HOUR    = 12
INDEX_DAY     = 13
INDEX_MONTH   = 14
INDEX_YEAR    = 15

POWER_PRODUCTION_REC = {
    'TIMESTAMP'                 :'', 
    'TIMEPERIOD_ID'             :int(0),
    'POWER_SOURCE_ID'           :int(0),
    'PRODUCTION_KWH_HIGH'       :float(0.0),
    'PRODUCTION_KWH_LOW'        :float(0.0),
    'PULS_PER_TIMEUNIT_HIGH'    :float(0.0),
    'PULS_PER_TIMEUNIT_LOW'     :float(0.0),
    'PRODUCTION_KWH_HIGH_TOTAL' :float(0.0),
    'PRODUCTION_KWH_LOW_TOTAL'  :float(0.0),
    'PRODUCTION_KWH_TOTAL'      :float(0.0),
    'PRODUCTION_PSEUDO_KW'      :float(0.0),
}

class powerProductionDB():
    
    def init( self, dbname, table, flog ):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.flog  = flog
        # table definition
        # TIMESTAMP the timestamp in format yyyy-mm-dd hh:mm:ss 
        # TIMEPERIOD: number that represents the minute:11 hour:12, day,13, month:14, year:15 
        # POWER_SOURCE_ID: a number that indicates the power source 0:not defined, 1:S0 energy kWh S0 power meter
        # PRODUCTION_KWH_HIGH / LOW kWh produced during this time peroid
        # PRODUCTION_KWH_HIGH_TOTAL total kWh produced.
        self.cur.execute( "CREATE TABLE IF NOT EXISTS " + table + "(\
        TIMESTAMP TEXT NOT NULL, \
        TIMEPERIOD_ID             INTEGER NOT NULL DEFAULT 0,\
        POWER_SOURCE_ID           INTEGER NOT NULL DEFAULT 0,\
        PRODUCTION_KWH_HIGH       REAL DEFAULT 0 NOT NULL,\
        PRODUCTION_KWH_LOW        REAL DEFAULT 0 NOT NULL,\
        PULS_PER_TIMEUNIT_HIGH    REAL DEFAULT 0 NOT NULL,\
        PULS_PER_TIMEUNIT_LOW     REAL DEFAULT 0 NOT NULL,\
        PRODUCTION_KWH_HIGH_TOTAL REAL DEFAULT 0 NOT NULL,\
        PRODUCTION_KWH_LOW_TOTAL  REAL DEFAULT 0 NOT NULL, \
        PRODUCTION_KWH_TOTAL      REAL DEFAULT 0 NOT NULL, \
        PRODUCTION_PSEUDO_KW      REAL DEFAULT 0 NOT NULL, \
        PRIMARY KEY( TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID )\
        );")
        self.close_db()

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute( 'select TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH, PRODUCTION_KWH_LOW, PULS_PER_TIMEUNIT_HIGH, PULS_PER_TIMEUNIT_LOW, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL, PRODUCTION_PSEUDO_KW from ' + \
            self.table + ' order by TIMESTAMP' )
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        # print ( r[0] )
        reccount = 0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,TIMEPERIOD_ID,POWER_SOURCE_ID,PRODUCTION_KWH_HIGH,PRODUCTION_KWH_LOW,PULS_PER_TIMEUNIT_HIGH,PULS_PER_TIMEUNIT_LOW,PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL,PRODUCTION_KWH_TOTAL,PRODUCTION_PSEUDO_KW) values ('" + \
            str(i[0]) + "'," +\
            str(i[1]) + "," +\
            str(i[2]) + "," +\
            str(i[3]) + "," +\
            str(i[4]) + "," +\
            str(i[5]) + "," +\
            str(i[6]) + "," +\
            str(i[7]) + "," +\
            str(i[8]) + "," +\
            str(i[9]) + "," +\
            str(i[10]) + \
            ");"
            #print  ( line )
            f.write(line+'\n')
            reccount = reccount + 1
        f.close() #close our file
        return reccount

    def get_timestamp_record( self , timestamp, timeperiod_id, power_source_id ):
        try:
            sqlstr = "select TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH, PRODUCTION_KWH_LOW, PULS_PER_TIMEUNIT_HIGH, PULS_PER_TIMEUNIT_LOW, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL, PRODUCTION_PSEUDO_KW from " + self.table + " where TIMEPERIOD_ID = " + str( timeperiod_id ) + " and POWER_SOURCE_ID = " + str( power_source_id ) + " and " + " timestamp  = '" + timestamp + "'"
            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            set = self.select_rec( sqlstr )
            #self.flog.debug( inspect.stack()[0][3] + ": waarde van bestaande record" + str( set ) )
            if len(set) > 0:
                return set[0][0],set[0][1],set[0][2],set[0][3],set[0][4],set[0][5],set[0][6],set[0][7],set[0][8],set[0][9],set[0][10]
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
            self.close_db()
        return None
    
    def replace_rec_with_values( self, record_values, timeperiod_id, power_source_id ):

        try:
            sqlstr = "replace into " + self.table + " (TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH, PRODUCTION_KWH_LOW, PULS_PER_TIMEUNIT_HIGH, PULS_PER_TIMEUNIT_LOW, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL, PRODUCTION_PSEUDO_KW ) values ('" + \
                     record_values['TIMESTAMP'] + "', " +\
                str( record_values['TIMEPERIOD_ID']   ) + ", " +\
                str( record_values['POWER_SOURCE_ID'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_HIGH'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_LOW'] ) + ", " +\
                str( record_values['PULS_PER_TIMEUNIT_HIGH'] ) + ", " +\
                str( record_values['PULS_PER_TIMEUNIT_LOW'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_HIGH_TOTAL'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_LOW_TOTAL'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_TOTAL'] ) + ", " +\
                str( record_values['PRODUCTION_PSEUDO_KW'] ) + \
                ");" 

            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            self.excute( sqlstr )
            
            return True
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
            self.close_db()
        return False

    # volgorde van tuples mag niet worden gewijzigd, wordt gebruikt in MQTT proces.
    def select_one_record(self , order='desc' ):
        try:
            sqlstr = "select \
                TIMESTAMP, \
                cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
                PRODUCTION_KWH_HIGH,\
                PRODUCTION_KWH_LOW,\
                PULS_PER_TIMEUNIT_HIGH,\
                PULS_PER_TIMEUNIT_LOW,\
                PRODUCTION_KWH_HIGH_TOTAL,\
                PRODUCTION_KWH_LOW_TOTAL, \
                PRODUCTION_KWH_TOTAL, \
                PRODUCTION_PSEUDO_KW \
                from " + self.table + \
                " where TIMEPERIOD_ID = 11 order by timestamp " + str(order) + " limit 1;"
            sqlstr = " ".join( sqlstr.split() )
            set = self.select_rec( sqlstr )
            if len(set) > 0:
                #return  "test", 1, 2, 3, 4, 5, 6, 7, 8, 9
                return set[0][0], set[0][1], set[0][2], set[0][3], set[0][4], set[0][5], set[0][6], set[0][7], set[0][8], set[0][9]

            return None
        except Exception as _e:
            print ( _e )
            return None

    # return number of records in database
    def record_count( self ):
        sql = "select count() from " + self.table
        return int( self.select_rec( sql )[0][0] )

    def select_rec( self, sqlstr ):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def close_db( self ):
        if self.con:
            self.con.close()

    def defrag( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

    def excute(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()


POWER_PRODUCTION_SOLAR_REC = {
    'TIMESTAMP'                 :'', 
    'TIMEPERIOD_ID'             :int(0),
    'POWER_SOURCE_ID'           :int(0),
    'PRODUCTION_KWH_HIGH'       :float(0.0),
    'PRODUCTION_KWH_LOW'        :float(0.0),
    'PRODUCTION_KWH_HIGH_TOTAL' :float(0.0),
    'PRODUCTION_KWH_LOW_TOTAL'  :float(0.0),
    'PRODUCTION_KWH_TOTAL'      :float(0.0),
}

class powerProductionSolarDB():
    
    def init( self, dbname, table, flog ):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.flog  = flog
        # table definition
        # TIMESTAMP the timestamp in format yyyy-mm-dd hh:mm:ss 
        # TIMEPERIOD: number that represents the minute:+1 hour:+2, day,+3, month:+4, year:+5
        # POWER_SOURCE_ID: a number that indicates the power source 0:not defined, 1:Solar Edge energy API
        # PRODUCTION_KWH_HIGH / LOW kWh produced during this time period
        # PRODUCTION_KWH_HIGH_TOTAL total kWh produced.
        self.cur.execute( "CREATE TABLE IF NOT EXISTS " + table + "(\
        TIMESTAMP                 TEXT NOT NULL, \
        TIMEPERIOD_ID             INTEGER NOT NULL DEFAULT 0,\
        POWER_SOURCE_ID           INTEGER NOT NULL DEFAULT 0,\
        PRODUCTION_KWH_HIGH       REAL DEFAULT 0 NOT NULL,\
        PRODUCTION_KWH_LOW        REAL DEFAULT 0 NOT NULL,\
        PRODUCTION_KWH_HIGH_TOTAL REAL DEFAULT 0 NOT NULL,\
        PRODUCTION_KWH_LOW_TOTAL  REAL DEFAULT 0 NOT NULL, \
        PRODUCTION_KWH_TOTAL      REAL DEFAULT 0 NOT NULL, \
        PRIMARY KEY( TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID )\
        );")
        self.close_db()

    def replace_rec_with_values( self, record_values ):

        try:
            sqlstr = "replace into " + self.table + " ( TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH, PRODUCTION_KWH_LOW,PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL ) values ('" + \
                     record_values['TIMESTAMP'] + "', " +\
                str( record_values['TIMEPERIOD_ID']   ) + ", " +\
                str( record_values['POWER_SOURCE_ID'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_HIGH'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_LOW'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_HIGH_TOTAL'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_LOW_TOTAL'] ) + ", " +\
                str( record_values['PRODUCTION_KWH_TOTAL'] ) +\
                ");"

            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            self.excute( sqlstr )
            
            return True
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
            self.close_db()
        return False

    def sql2file( self, filename ):
        #print filename
        self.con = lite.connect( self.dbname )
        self.cur = self.con.cursor()
        self.cur.execute( 'select TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID,PRODUCTION_KWH_HIGH,PRODUCTION_KWH_LOW,PRODUCTION_KWH_HIGH_TOTAL,PRODUCTION_KWH_LOW_TOTAL,PRODUCTION_KWH_TOTAL from ' + \
            self.table + ' order by TIMESTAMP' )
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        # print ( r[0] )
        reccount = 0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,TIMEPERIOD_ID,POWER_SOURCE_ID,PRODUCTION_KWH_HIGH,PRODUCTION_KWH_LOW,PRODUCTION_KWH_HIGH_TOTAL,PRODUCTION_KWH_LOW_TOTAL,PRODUCTION_KWH_TOTAL) values ('" + \
            str(i[0]) + "'," +\
            str(i[1]) + "," +\
            str(i[2]) + "," +\
            str(i[3]) + "," +\
            str(i[4]) + "," +\
            str(i[5]) + "," +\
            str(i[6]) + "," +\
            str(i[7]) + \
            ");"
            #print  ( line )
            f.write(line+'\n')
            reccount = reccount + 1
        f.close() #close our file
        return reccount



    """
    def get_timestamp_record( self , timestamp, timeperiod_id, power_source_id ):
        try:
            sqlstr = "select TIMESTAMP, TIMEPERIOD_ID, POWER_SOURCE_ID, PRODUCTION_KWH_HIGH, PRODUCTION_KWH_LOW, PULS_PER_TIMEUNIT_HIGH, PULS_PER_TIMEUNIT_LOW, PRODUCTION_KWH_HIGH_TOTAL, PRODUCTION_KWH_LOW_TOTAL, PRODUCTION_KWH_TOTAL, PRODUCTION_PSEUDO_KW from " + self.table + " where TIMEPERIOD_ID = " + str( timeperiod_id ) + " and POWER_SOURCE_ID = " + str( power_source_id ) + " and " + " timestamp  = '" + timestamp + "'"
            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            set = self.select_rec( sqlstr )
            #self.flog.debug( inspect.stack()[0][3] + ": waarde van bestaande record" + str( set ) )
            if len(set) > 0:
                return set[0][0],set[0][1],set[0][2],set[0][3],set[0][4],set[0][5],set[0][6],set[0][7],set[0][8],set[0][9],set[0][10]
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
            self.close_db()
        return None
    
    
    # volgorde van tuples mag niet worden gewijzigd, wordt gebruikt in MQTT proces.
    def select_one_record(self , order='desc' ):
        try:
            sqlstr = "select \
                TIMESTAMP, \
                cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
                PRODUCTION_KWH_HIGH,\
                PRODUCTION_KWH_LOW,\
                PULS_PER_TIMEUNIT_HIGH,\
                PULS_PER_TIMEUNIT_LOW,\
                PRODUCTION_KWH_HIGH_TOTAL,\
                PRODUCTION_KWH_LOW_TOTAL, \
                PRODUCTION_KWH_TOTAL, \
                PRODUCTION_PSEUDO_KW \
                from " + self.table + \
                " where TIMEPERIOD_ID = 11 order by timestamp " + str(order) + " limit 1;"
            sqlstr = " ".join( sqlstr.split() )
            set = self.select_rec( sqlstr )
            if len(set) > 0:
                #return  "test", 1, 2, 3, 4, 5, 6, 7, 8, 9
                return set[0][0], set[0][1], set[0][2], set[0][3], set[0][4], set[0][5], set[0][6], set[0][7], set[0][8], set[0][9]

            return None
        except Exception as _e:
            print ( _e )
            return None

    # return number of records in database
    def record_count( self ):
        sql = "select count() from " + self.table
        return int( self.select_rec( sql )[0][0] )

    """

    def select_rec( self, sqlstr ):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def close_db( self ):
        if self.con:
            self.con.close()

    def defrag( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

    def executescript( self,sqlscript ):
        self.con = lite.connect( self.dbname )
        self.cur = self.con.cursor()
        self.cur.executescript( sqlscript )
        self.con.commit()
        self.close_db()

    def excute(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

WATERMETER_REC = {
    'TIMESTAMP'                 :'', 
    'TIMEPERIOD_ID'             :int(0),
    'PULS_PER_TIMEUNIT'         :float(0.0),
    'VERBR_PER_TIMEUNIT'        :float(0.0),
    'VERBR_IN_M3_TOTAAL'        :float(0.0),
}

class WatermeterDBV2(): 

    def init( self, dbname, table, flog ):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.flog  = flog
        # table definition
        # TIMESTAMP the timestamp in format yyyy-mm-dd hh:mm:ss 
        # TIMEPERIOD: number that represents the minute:11 hour:12, day,13, month:14, year:15 
        # PULS_PER_TIMEUNIT number of pulses detected during the period
        # VERBR_PER_TIMEUNIT Liter of water during the period
        # VERBR_IN_M3_TOTAAL Liter of water in M3 during the period
        self.cur.execute(" CREATE TABLE IF NOT EXISTS " +table+"(\
            TIMESTAMP TEXT     TEXT NOT NULL, \
            TIMEPERIOD_ID      INTEGER NOT NULL DEFAULT 0,\
            PULS_PER_TIMEUNIT  REAL DEFAULT 0, \
            VERBR_PER_TIMEUNIT REAL DEFAULT 0, \
            VERBR_IN_M3_TOTAAL REAL DEFAULT 0, \
            PRIMARY KEY( TIMESTAMP, TIMEPERIOD_ID )\
        );")
        self.close_db()

    def get_timestamp_record( self , timestamp, timeperiod_id ):
        try:
            sqlstr = "select TIMESTAMP, TIMEPERIOD_ID, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL from " + self.table + " where TIMEPERIOD_ID = " + str( timeperiod_id ) + " and timestamp  = '" + timestamp + "'"
            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            set = self.select_rec( sqlstr )
            #self.flog.debug( inspect.stack()[0][3] + ": waarde van bestaande record" + str( set ) )
            if len(set) > 0:
                return set[0][0],set[0][1],set[0][2],set[0][3],set[0][4]
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
            self.close_db() 
        return None
 
    def replace_rec_with_values( self, record_values ):
        try:
            sqlstr = "replace into " + self.table + " (TIMESTAMP, TIMEPERIOD_ID, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL  ) values ('" + \
                     record_values['TIMESTAMP'] + "', " +\
                str( record_values['TIMEPERIOD_ID']   ) + ", " +\
                str( record_values['PULS_PER_TIMEUNIT'] ) + ", " +\
                str( record_values['VERBR_PER_TIMEUNIT'] ) + ", " +\
                str( record_values['VERBR_IN_M3_TOTAAL'] ) +\
                ");" 
            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            self.excute( sqlstr )
            return True
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
            self.close_db()
        return False

    def insert_rec_with_values( self, record_values, silent = True ):
        try:
            sqlstr = "insert into " + self.table + " (TIMESTAMP, TIMEPERIOD_ID, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL  ) values ('" + \
                     record_values['TIMESTAMP'] + "', " +\
                str( record_values['TIMEPERIOD_ID']   ) + ", " +\
                str( record_values['PULS_PER_TIMEUNIT'] ) + ", " +\
                str( record_values['VERBR_PER_TIMEUNIT'] ) + ", " +\
                str( record_values['VERBR_IN_M3_TOTAAL'] ) +\
                ");" 
            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            self.excute( sqlstr )
            return True
        except Exception as e:
            if silent == False:
                self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
            self.close_db()
        return False

    # volgorde van tuples mag niet worden gewijzigd, wordt gebruikt in MQTT proces.
    # neemt nu de minuten records in de vorige versie werd uren verstuurd.
    def select_one_record(self , order='desc' ):
        try:
            sqlstr = "select \
                TIMESTAMP, \
                cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
                PULS_PER_TIMEUNIT,  \
                VERBR_PER_TIMEUNIT, \
                VERBR_IN_M3_TOTAAL  \
                from " + self.table + \
                " where TIMEPERIOD_ID = 11 order by timestamp " + str(order) + " limit 1;"
            sqlstr = " ".join( sqlstr.split() )
            set = self.select_rec( sqlstr )
            if len(set) > 0:
                return set[0][0], set[0][1], set[0][2], set[0][3], set[0][4]
            return None
        except Exception as _e:
            print ( _e )
            return None

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute( 'select TIMESTAMP,TIMEPERIOD_ID,PULS_PER_TIMEUNIT,VERBR_PER_TIMEUNIT,VERBR_IN_M3_TOTAAL from ' + \
            self.table + ' order by TIMESTAMP' )
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        # print ( r[0] )
        reccount = 0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,TIMEPERIOD_ID,PULS_PER_TIMEUNIT,VERBR_PER_TIMEUNIT,VERBR_IN_M3_TOTAAL) values ('" + \
            str(i[0]) + "'," +\
            str(i[1]) + "," +\
            str(i[2]) + "," +\
            str(i[3]) + "," +\
            str(i[4]) + \
            ");"
            #print  ( line )
            f.write(line+'\n')
            reccount = reccount + 1
        f.close() #close our file
        return reccount

    # return number of records in database
    def record_count( self ):
        sql = "select count() from " + self.table
        return int( self.select_rec( sql )[0][0] )

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def select_rec( self, sqlstr ):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r

    def close_db( self ):
        if self.con:
            self.con.close()

    def defrag( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

    def excute(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

class PhaseDB():

    def init(self, dbname, table):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        # VEBRK = energie waar je voor betaald aan de leverancier (nuon enz) :(
        # GELVR = energie die je TERUG levert aan de leverancier :)
        # VEBRK KW L1 CODE 21
        # VEBRK KW L2 CODE 41
        # VEBRK KW L3 CODE 61
        # GELVR KW L1 CODE 22
        # GELVR KW L2 CODE 42
        # GELVR Kw L3 CODE 62
        self.cur.execute("CREATE TABLE IF NOT EXISTS " + table + "(\
        TIMESTAMP TEXT PRIMARY KEY NOT NULL, \
        VERBR_L1_KW REAL DEFAULT 0,  \
        VERBR_L2_KW REAL DEFAULT 0,  \
        VERBR_L3_KW REAL DEFAULT 0, \
        GELVR_L1_KW REAL DEFAULT 0, \
        GELVR_L2_KW REAL DEFAULT 0, \
        GELVR_L3_KW REAL DEFAULT 0, \
        L1_V        REAL DEFAULT 0, \
        L2_V        REAL DEFAULT 0, \
        L3_V        REAL DEFAULT 0, \
        L1_A        REAL DEFAULT 0, \
        L2_A        REAL DEFAULT 0, \
        L3_A        REAL DEFAULT 0  \
        );")
        self.close_db()

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute( 'select TIMESTAMP, VERBR_L1_KW, VERBR_L2_KW, VERBR_L3_KW, GELVR_L1_KW, GELVR_L2_KW, GELVR_L3_KW, L1_V, L2_V, L3_V, L1_A, L2_A, L3_A from ' + \
            self.table + ' order by TIMESTAMP' )
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        # print ( r[0] )
        reccount = 0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,VERBR_L1_KW,VERBR_L2_KW,VERBR_L3_KW,GELVR_L1_KW,GELVR_L2_KW,GELVR_L3_KW,L1_V,L2_V,L3_V,L1_A,L2_A,L3_A) values ('" + \
            str(i[0]) + "'," +\
            str(i[1]) + "," +\
            str(i[2]) + "," +\
            str(i[3]) + "," +\
            str(i[4]) + "," +\
            str(i[5]) + "," +\
            str(i[6]) + "," +\
            str(i[7]) + "," +\
            str(i[8]) + "," +\
            str(i[9]) + "," +\
            str(i[10]) + "," +\
            str(i[11]) + "," +\
            str(i[12]) + \
            ");"
            #print  ( line )
            f.write(line+'\n')
            reccount = reccount + 1
        f.close() #close our file
        return reccount

    def close_db(self):
        if self.con:
            self.con.close()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r

class WatermeterDB():
    
    def init( self, dbname, table, flog) :
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.flog  = flog
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
            TIMESTAMP TEXT     PRIMARY KEY NOT NULL, \
            PULS_PER_TIMEUNIT  REAL DEFAULT 0, \
            VERBR_PER_TIMEUNIT REAL DEFAULT 0, \
            VERBR_IN_M3_TOTAAL REAL DEFAULT 0 \
        );")
        # clean up van het database bestand , file kleiner maken
        self.close_db()

    # volgorde van tuples mag niet worden gewijzigd, wordt gebruikt in MQTT proces.
    def select_one_record(self , order='desc' ):
        try:
            sqlstr = "select \
                TIMESTAMP, \
                cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
                PULS_PER_TIMEUNIT,  \
                VERBR_PER_TIMEUNIT, \
                VERBR_IN_M3_TOTAAL  \
                from " + self.table + \
                " order by timestamp " + str(order) + " limit 1;"
            sqlstr = " ".join( sqlstr.split() )
            set = self.select_rec( sqlstr )
            if len(set) > 0:
                return set[0][0], set[0][1], set[0][2], set[0][3], set[0][4]
            return None
        except Exception as _e:
            print ( _e )
            return None

    def update_m3_verbr_phase_1( self, timestamp, m3_resetvalue, mode ):
        
        m3_val = float( m3_resetvalue )

        if mode == 'hour':   
            timestamp = timestamp[0:13]+":00:00"
        """
        if mode == 'day':   
            timestamp = timestamp[0:11]+"00:00:00"
        if mode == 'month':
            timestamp= timestamp[0:7]+"-01 00:00:00"
        if mode == 'year':       
            timestamp = timestamp[0:4]+"-01-01 00:00:00"
        """

        #sanitycheck on timestamp
        if utiltimestamp( timestamp ).santiycheck() == False:
            self.flog.error( inspect.stack()[0][3]+": timestamp_start heeft niet het correcte formaat -> " + str( timestamp ) )
            return False

        try:
            sql_0 = "select min(timestamp) from " + self.table + " where timestamp >= '" + timestamp + "';"
            #find the first record in the table to set timestamp 
            try:
                timestamp_rec = str( self.select_rec( sql_0 )[0][0] )

                if utiltimestamp( timestamp_rec ).santiycheck() == False:
                    self.flog.warning( inspect.stack()[0][3]+": geen valide eerst record gevonden op timestamp = " + \
                        str( timestamp ) + " record lijkt defect of ontbreekt.")
                    return False
                
                if timestamp_rec != timestamp:
                    self.flog.info( inspect.stack()[0][3]+": eerste valide record gevonden op timestamp = " + str( timestamp_rec ) + \
                        " oorspronkelijke timestamp was " + str(timestamp ) )
                    timestamp = timestamp_rec

            except Exception as e:
                self.flog.error( inspect.stack()[0][3]+": geen valide eerst record gevonden op timestamp = " + str( timestamp ) )
                return False

            sql_2 = "update " + self.table + " set VERBR_IN_M3_TOTAAL = " + str( m3_val ) + " where timestamp = '" + timestamp + "';"
            sql_3 = "select max(timestamp) from " + self.table + ";"

            # set the first record with the reset value 
            self.flog.debug( inspect.stack()[0][3] + ": sql_2=" + str( sql_2 ) )
            self.update_rec( sql_2 )

            # walk the rest of the records
            # get the newest record 
            max_timestamp_rec = str(self.select_rec( sql_3 )[0][0])
            self.flog.debug( inspect.stack()[0][3] + ": sql_3=" + str( sql_3 ) )

            # get max failsave count and do some logging
            try:
                sql_1 = "select count() from " + self.table + " where timestamp >= '" + timestamp + "';"
                rec_count = int( self.select_rec( sql_1 )[0][0] )
                self.flog.info ( str( rec_count ) + " records in tabel " + self.table + \
                    " worden verwerkt voor de meterstand aanpassing." )
            except Exception as e:
                self.flog.error( inspect.stack()[0][3]+": aantal records in tabel " + self.table + " is niet te tellen ->" + str(e) )
                return False    

            if rec_count == 1:
                self.flog.debug( inspect.stack()[0][3] + ": maar 1 record te verwerken. ")
                return True

            timestamp_work = timestamp
            failsavecount = rec_count
            while True:
                #print ( "@1 " + timestamp_work + " - " + max_timestamp_rec )
                if mode == 'hour':   
                    timestamp_work = str( datetime.strptime( timestamp_work, "%Y-%m-%d %H:%M:%S") + timedelta( hours=1 ) )  
                """"
                if mode == 'day':   
                    timestamp_work = str( datetime.strptime( timestamp_work, "%Y-%m-%d %H:%M:%S") + timedelta( days=1 ) )                
                if mode == 'month':       
                    timestamp_obj  = utiltimestamp( timestamp_work )
                    timestamp_work = timestamp_obj.monthmodify(1)
                if mode == 'year':       
                    timestamp_work = str(int(timestamp_work[0:4])+1) + timestamp_work[4:]
                """

                try:
                    #print ( "@2 " + timestamp_work + " - " + max_timestamp_rec )

                    # get the Liter used 
                    sql_4 = "select VERBR_PER_TIMEUNIT from " + self.table + " WHERE timestamp = '" + timestamp_work + "';"   
                    #self.flog.debug( inspect.stack()[0][3] + ": sql_4=" + str( sql_4 ) )
                    rec_m3_value = float( self.select_rec( sql_4 )[0][0] )/1000 # conversion from L to m3

                    #if mode == 'hour':
                    m3_val = m3_val + rec_m3_value

                    """
                    if mode == 'day':   
                        sql_6 = "select max(VERBR_PER_TIMEUNIT) from " + self.table + " WHERE timestamp >= '" + \
                        max_timestamp_rec + "';" 
                        m3_value = float( self.select_rec( sql_6 )[0][0] )
                        print ("####=" + m3_value )
                    """

                    #print ( format ( m3_val, '.4f' ) )

                    # do the update
                    sql_5 = "update " + self.table + " SET VERBR_IN_M3_TOTAAL = " + format ( m3_val, '.4f' ) + " WHERE timestamp = '" + timestamp_work + "';" 
                    #self.flog.debug( inspect.stack()[0][3] + ": sql_5=" + str( sql_5 ) )  
                    self.update_rec( sql_5 )
                    
                except Exception as e:
                    self.flog.warning( inspect.stack()[0][3]+": timestamp op tabel = " + self.table + " was niet aan te passen ->" + str(e) )
                    
                #check of the next record exist, otherwise exit the loop.
                if timestamp_work == max_timestamp_rec:
                    break # all records updateed
                
                failsavecount = failsavecount - 1
                #print ( failsavecount )
                if failsavecount < 0:
                    self.flog.warning ( "te veel keren geprobeerd om de meterstanden aan te passen voor tabel " + self.table + " ,geforceerd gestopt.")
                    return False

        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error on sql statement = " + self.table + " ->" + str(e) )
            return False

        return True

    # mode is hour,day,month or year
    # ok is true, not ok is false 
    # TODO sanity check on loop and date, this could kill the database.
    def create_record_set_between_times( self , timestamp_start , timestamp_stop, m3_value, mode ):
        #sanitycheck on timestamp
        if utiltimestamp( timestamp_start ).santiycheck() == False:
            self.flog.error( inspect.stack()[0][3]+": timestamp_start heeft niet het correcte formaat -> " + str( timestamp_start ) )
        if utiltimestamp( timestamp_stop ).santiycheck() == False:
            self.flog.error( inspect.stack()[0][3]+": timestamp_stop heeft niet het correcte formaat -> " + str( timestamp_stop ) )
        if mode == 'hour':
            try:
                rec = self.get_timestamp_record( timestamp_start )
                timestamp_work = rec[0]
                while True:
                    if self.get_timestamp_record(timestamp_work) == None: #limit work and load on database
                        record_values = { "timestamp":timestamp_work, "VERBR_IN_M3_TOTAAL": m3_value }
                        self.replace_rec_with_values( record_values )
                    if timestamp_work == timestamp_stop:
                        return True
                    timestamp_work = str( datetime.strptime(timestamp_work, "%Y-%m-%d %H:%M:%S") + timedelta( hours=1 ) ) 
                    #print (timestamp_work) 
            except Exception as e:
                self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
                return False
        if mode == 'day':
            try:
                rec = self.get_timestamp_record( timestamp_start )
                timestamp_work = rec[0]
                while True:
                    if self.get_timestamp_record(timestamp_work) == None: #limit work and load on database
                        record_values = { "timestamp":timestamp_work, "VERBR_IN_M3_TOTAAL": m3_value }
                        self.replace_rec_with_values( record_values )
                    if timestamp_work == timestamp_stop:
                        return True
                    timestamp_work = str( datetime.strptime(timestamp_work, "%Y-%m-%d %H:%M:%S") + timedelta(days=1 ) ) 
            except Exception as e:
                self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
                return False
        if mode == 'month':
            try:
                rec = self.get_timestamp_record( timestamp_start )
                timestamp_work = rec[0]
                while True:
                    if self.get_timestamp_record(timestamp_work) == None: #limit work and load on database
                        record_values = { "timestamp":timestamp_work, "VERBR_IN_M3_TOTAAL": m3_value }
                        self.replace_rec_with_values( record_values )
                    #print ( timestamp_work )    
                    if timestamp_work == timestamp_stop:
                        return True
                    timestamp_obj  = utiltimestamp( timestamp_work )
                    timestamp_work = timestamp_obj.monthmodify(1)
            except Exception as e:
                self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
                return False

    def get_totals_record(self, timestamp, mode):
        if mode == 'day':
            time_str = timestamp[0:10]
            off_set = 10 
            #print ( "*day = " + time_str )
        if mode == 'month':
            time_str = timestamp[0:7]
            off_set = 7     
            #print ( "*month = " + time_str )
        if mode == 'year':
            time_str = timestamp[0:4]
            off_set = 4     
            #print ( "*year = " + time_str )
        
        try:   
            sql =  "select sum(PULS_PER_TIMEUNIT), sum(VERBR_PER_TIMEUNIT), max(VERBR_IN_M3_TOTAAL) from " + self.table + " where substr(timestamp,1,"\
                + str(off_set) + ") = '" + str(time_str) + "';"
            #print ( sql )
            #self.flog.debug( inspect.stack()[0][3] + ": sql=" + sql )   
            set = self.select_rec( sql )
            #print ("*** " + mode + "**** " +str(set) )
            if len(set) > 0:
                return set[0][0], set[0][1], set[0][2]
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) + " is de mode parameter goed opgegeven?")
            return None    

    def select_previous_rec_with_values(self , timestamp ):
        try:
            #sqlstr = "select TIMESTAMP, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL from " + self.table + \
            #    " where timestamp  < (select max(timestamp) from watermeter_history_uur) order by timestamp desc limit 1;"
            sqlstr = "select TIMESTAMP, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL from " + self.table + \
                " where timestamp  < '" + timestamp + "' order by timestamp desc limit 1"
            sqlstr = " ".join(sqlstr.split())
            self.flog.debug( inspect.stack()[0][3] + ": sql=" + sqlstr )
            set = self.select_rec( sqlstr )
            #self.flog.debug( inspect.stack()[0][3] + ": waarde van bestaande record" + str( set ) )
            if len(set) > 0:
                return set[0][0],set[0][1], set[0][2], set[0][3]
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
        return None

    def replace_rec_with_values(self, record_values ):
        rec = { "TIMESTAMP":'', "PULS_PER_TIMEUNIT":0, "VERBR_PER_TIMEUNIT":0, "VERBR_IN_M3_TOTAAL":0 }
        # clean inputs
        for x in record_values:
            #print ( x.upper() + " " + str(record_values[x]) )
            if x.upper() == 'TIMESTAMP':
                rec['TIMESTAMP'] = record_values[x]
            if x.upper() == 'PULS_PER_TIMEUNIT':
                rec['PULS_PER_TIMEUNIT'] = record_values[x]
            if x.upper()  == 'VERBR_PER_TIMEUNIT':
                rec['VERBR_PER_TIMEUNIT'] = record_values[x]
            if x.upper()  == 'VERBR_IN_M3_TOTAAL':
                    rec['VERBR_IN_M3_TOTAAL'] = record_values[x]
        if rec['TIMESTAMP'] == 0:
            self.flog.error( inspect.stack()[0][3] + ": record ID TIMESTAMP niet gevonden. ") 
            return False
        #print (rec)
        try:
            sqlstr = "replace into " + self.table + " (TIMESTAMP, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL) \
                values ('" + rec['TIMESTAMP'] + "', " + str(rec['PULS_PER_TIMEUNIT']) + ", " +  \
                str(rec['VERBR_PER_TIMEUNIT']) + ", " +  str(rec['VERBR_IN_M3_TOTAAL']) +");" 
            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            self.insert_rec ( sqlstr )
            return True
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
        return False

    def get_timestamp_record(self , timestamp ):
        try:
            sqlstr = "select TIMESTAMP, PULS_PER_TIMEUNIT, VERBR_PER_TIMEUNIT, VERBR_IN_M3_TOTAAL from " + self.table + " where timestamp = '" + timestamp + "'"
            sqlstr = " ".join(sqlstr.split())
            #self.flog.debug( inspect.stack()[0][3] + ": sql(1)=" + sqlstr )
            set = self.select_rec( sqlstr )
            #self.flog.debug( inspect.stack()[0][3] + ": waarde van bestaande record" + str( set ) )
            if len(set) > 0:
                return set[0][0],set[0][1], set[0][2], set[0][3]
        except Exception as e:
            self.flog.error( inspect.stack()[0][3]+": sql error(1) op table " + self.table + " ->" + str(e) )
        return None

    def get_min_max_timestamp( self, timestamp , mode='min'):
        if mode == "max":
            mode = 'max'

        sql_0 = "select " + mode + "(timestamp) from " + self.table + " where timestamp >= '" + timestamp + "';"
        #find the first record in the table to set timestamp 
        try:
            timestamp_rec = str( self.select_rec( sql_0 )[0][0] )

            if utiltimestamp( timestamp_rec ).santiycheck() == False:
                self.flog.warning( inspect.stack()[0][3]+": geen valide eerst record gevonden op timestamp = " + \
                    str( timestamp ) + " record lijkt defect of ontbreekt.")
                return None
                
            return timestamp_rec

        except Exception:
                self.flog.error( inspect.stack()[0][3]+": geen valide eerst record gevonden op timestamp = " + str( timestamp ) )
                return None

    def get_record_count( self, timestamp ):
        sql = "select count() from " + self.table + " where timestamp >= '" + timestamp + "';"     
        try:
            rec_count = int( self.select_rec( sql )[0][0] )
            if rec_count != None:
                return rec_count
        except Exception as e:
                self.flog.error( inspect.stack()[0][3]+": Aantal records in database gaf een fout = " + str( e ) )
                return None
        return None

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP,PULS_PER_TIMEUNIT,VERBR_PER_TIMEUNIT,VERBR_IN_M3_TOTAAL from '+\
        self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,PULS_PER_TIMEUNIT,VERBR_PER_TIMEUNIT,VERBR_IN_M3_TOTAAL) values ('" + \
            str( i[0] ) + "','" +\
            str( i[1] ) + "','" +\
            str( i[2] ) + "','" +\
            str( i[3] ) + "'" +\
            ');'
        #print line 
            f.write(line+'\n')
            reccount=reccount+1
        f.close() #close our file
        return reccount
        #setFile2user(filename,'p1mon')

    def close_db(self):
        if self.con:
            self.con.close()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

class temperatureDB():

    def init(self, dbname, table):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.cur.execute("CREATE TABLE IF NOT EXISTS " + table + "(\
        TIMESTAMP         	TEXT NOT NULL, \
        RECORD_ID        	INTEGER NOT NULL DEFAULT 0,\
        TEMPERATURE_1       REAL DEFAULT 0, \
        TEMPERATURE_1_AVG	REAL DEFAULT 0, \
        TEMPERATURE_1_MIN	REAL DEFAULT 0, \
        TEMPERATURE_1_MAX	REAL DEFAULT 0, \
        TEMPERATURE_2       REAL DEFAULT 0, \
        TEMPERATURE_2_AVG	REAL DEFAULT 0, \
        TEMPERATURE_2_MIN	REAL DEFAULT 0, \
        TEMPERATURE_2_MAX	REAL DEFAULT 0, \
        UNIQUE(TIMESTAMP,RECORD_ID) \
        );")
        self.close_db()
       
        # index does not help in performance
        # self.cur.execute("drop INDEX if exists record_id_timestamp_desc;")
        #self.change_table()
        

    # fix for design error, the timestamp can not by unique because day and month use the same date for the first of the month
    # sqlite does not support the change of a primary key so, we have te recreate the table. :(
    # the UNIQUE clause makes the combination of timestamp and ID equal to a combined primairy key
    def change_table( self, flog ):
        try: 
            flog.info( inspect.stack()[1][3] + " automatische correctie van tabel structuur van tabel " + self.table + " wordt uitgevoerd." )
            self.con = lite.connect( self.dbname )
            self.cur = self.con.cursor()

            # check if the new table has primary key (hack), if this existe we don't have to do the rest.
            sql = "SELECT sql FROM sqlite_master WHERE name = '" + self.table + "';"
            self.cur.execute( sql)
            sql_tab_info = self.cur.fetchall()

        
            if ( sql_tab_info[0][0].find('PRIMARY KEY') != -1): 
                flog.info ( inspect.stack()[1][3] + " Table structuur aangepast.")
            else: 
                return

            tmp_table = self.table + "_tmp"
            
            self.cur.execute( "DROP TABLE IF EXISTS " + tmp_table )
            self.cur.execute("CREATE TABLE " + tmp_table + "(\
            TIMESTAMP         	TEXT NOT NULL, \
            RECORD_ID        	INTEGER NOT NULL DEFAULT 0,\
            TEMPERATURE_1       REAL DEFAULT 0, \
            TEMPERATURE_1_AVG	REAL DEFAULT 0, \
            TEMPERATURE_1_MIN	REAL DEFAULT 0, \
            TEMPERATURE_1_MAX	REAL DEFAULT 0, \
            TEMPERATURE_2       REAL DEFAULT 0, \
            TEMPERATURE_2_AVG	REAL DEFAULT 0, \
            TEMPERATURE_2_MIN	REAL DEFAULT 0, \
            TEMPERATURE_2_MAX	REAL DEFAULT 0,  \
            UNIQUE(TIMESTAMP,RECORD_ID) \
            );")
           
            #self.cur.execute( "CREATE INDEX IF NOT EXISTS idx_timestamp_record_id ON " + tmp_table + " (TIMESTAMP , RECORD_ID);" )
            
            sql = " INSERT INTO " + tmp_table  + " ( TIMESTAMP, RECORD_ID, TEMPERATURE_1, TEMPERATURE_1_AVG, TEMPERATURE_1_MIN, TEMPERATURE_1_MAX, TEMPERATURE_2, TEMPERATURE_2_AVG, TEMPERATURE_2_MIN, TEMPERATURE_2_MAX ) \
            SELECT TIMESTAMP, RECORD_ID, TEMPERATURE_1, TEMPERATURE_1_AVG, TEMPERATURE_1_MIN, TEMPERATURE_1_MAX, TEMPERATURE_2, TEMPERATURE_2_AVG, TEMPERATURE_2_MIN, TEMPERATURE_2_MAX FROM " + self.table + " order by TIMESTAMP;"
            self.cur.execute( sql )
            #print( sql )
            self.con.commit()

            sql = "DROP TABLE IF EXISTS " + self.table 
            self.cur.execute( sql )
            #print ( sql )
            self.con.commit()

            sql = "ALTER TABLE " + tmp_table + " RENAME TO " + self.table
            self.cur.execute( sql )
            #print ( sql )
            self.con.commit()
            
            self.fix_missing_month_day( flog )

            self.close_db() 
          
        except Exception as e:
             flog.error( inspect.stack()[1][3]+" tabel wijzing gefaald." + " Melding=" + str(e.args[0]) )


    def fix_missing_month_day( self, flog ):
        try: 
            self.con = lite.connect( self.dbname )
            self.cur = self.con.cursor()

            flog.info( inspect.stack()[1][3] + " automatische correctie van tabel " + self.table + " wordt uitgevoerd." )
            sql = "select max(timestamp),min(timestamp) from " + self.table + " where RECORD_ID = 12"
            self.cur.execute( sql )
            sql_tab_info = self.cur.fetchall()
            max_date = sql_tab_info[0][0].split('-')
            min_date = sql_tab_info[0][1].split('-')

            end_year    = int(max_date[0])
            end_month   = int(max_date[1])

            start_year  = int(min_date[0])
            start_month = int(min_date[1])
        
            year = start_year
            month = start_month

            while 1:
                date = datetime(year, month, 1, 0, 0, 0)
                timestamp = date.strftime("%Y-%m-%d %H:%M:%S")
                #print( "Date and Time:", timestamp )

                try:
                    # process day values.
                    # returns avg, min, max(in), avg, min, max(out) 
                    temp_list = self.selectAMM( timestamp[:10],12,flog )
                    self.replace(timestamp[:10]+" 00:00:00",\
                        13, \
                        0, \
                        temp_list[0][0],\
                        temp_list[0][1],\
                        temp_list[0][2],\
                        0,\
                        temp_list[0][3],\
                        temp_list[0][4],\
                        temp_list[0][5],\
                        flog )

                    # process month values.
                    # returns avg, min, max(in), avg, min, max(out) 
                    temp_list = self.selectAMM( timestamp[:7],13,flog )
                    self.replace(timestamp[:7]+"-01 00:00:00",\
                        14, \
                        0, \
                        temp_list[0][0],\
                        temp_list[0][1],\
                        temp_list[0][2],\
                        0,\
                        temp_list[0][3],\
                        temp_list[0][4],\
                        temp_list[0][5],\
                        flog )
                    flog.info( inspect.stack()[1][3]+" tabel wijzing (replace) succesvol voor timestamp " + timestamp )

                except Exception as e:
                    flog.warning( inspect.stack()[1][3]+" tabel wijzing (replace) gefaald. voor timestamp " + timestamp + " mislukt. Melding=" + str(e.args[0]))


                #print ( "#", year, month , end_year, end_month) 
                if year == end_year and month >= end_month:
                    break

                if month < 12:
                    month = month + 1
                else:
                    if year < end_year:
                        year = year + 1 
                    month = 1

            self.con.close()

        except Exception as e:
             flog.error( inspect.stack()[1][3]+" tabel wijzing gefaald." + " Melding=" + str(e.args[0]) )

    def execute( self, sqlstr ):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute( sqlstr )
        self.con.commit()
        self.close_db()   
        
    # volgorde van tuples mag niet worden gewijzigd, wordt gebruikt in MQTT proces.
    # subset of database
    def select_one_record(self , order='desc' , record_id=11):
        try:
            # record id = 10 set as last record
            sqlstr = "select \
                TIMESTAMP, \
                cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
                TEMPERATURE_1_MIN, \
                TEMPERATURE_1_AVG, \
                TEMPERATURE_1_MAX, \
                TEMPERATURE_2_MIN, \
                TEMPERATURE_2_AVG, \
                TEMPERATURE_2_MAX  \
                from " + self.table + " where record_id  = " + str( record_id ) + \
                " order by timestamp " + str(order) + " limit 1;"
            sqlstr = " ".join( sqlstr.split() )
            set = self.select_rec( sqlstr )
            if len(set) > 0:
                return set[0][0], set[0][1], set[0][2], set[0][3], set[0][4], set[0][5], \
                    set[0][6], set[0][7]
            return None
        except Exception as _e:
            print ( _e )
            return None

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r

    def sql2file(self, filename):
            #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP, RECORD_ID, TEMPERATURE_1, TEMPERATURE_1_AVG, TEMPERATURE_1_MIN, TEMPERATURE_1_MAX,\
        TEMPERATURE_2, TEMPERATURE_2_AVG, TEMPERATURE_2_MIN, TEMPERATURE_2_MAX from '+\
        self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
        	line = "replace into " + self.table + " (TIMESTAMP,RECORD_ID,TEMPERATURE_1,TEMPERATURE_1_AVG,TEMPERATURE_1_MIN,TEMPERATURE_1_MAX,\
        	TEMPERATURE_2,TEMPERATURE_2_AVG,TEMPERATURE_2_MIN,TEMPERATURE_2_MAX) values ('" + \
        	str(i[0]) + "','" +\
        	str(i[1]) + "','" +\
        	str(i[2]) + "','" +\
        	str(i[3]) + "','" +\
        	str(i[4]) + "','" +\
        	str(i[5]) + "','" +\
        	str(i[6]) + "','" +\
        	str(i[7]) + "','" +\
        	str(i[8]) + "','" +\
        	str(i[9]) + "'" +\
        	');'
        #print line 
        	f.write(line+'\n')
        	reccount=reccount+1
        f.close() #close our file
        return reccount

    def close_db(self):
        if self.con:
        	self.con.close()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

    def replace(self, timestamp,rec_id,t1,t1avg,t1min,t1max,t2,t2avg,t2min,t2max,flog):
        #print ("replace")
        sqlstr = "replace into " + self.table + " (TIMESTAMP, RECORD_ID, TEMPERATURE_1, TEMPERATURE_1_AVG, TEMPERATURE_1_MIN, TEMPERATURE_1_MAX,\
        TEMPERATURE_2, TEMPERATURE_2_AVG, TEMPERATURE_2_MIN, TEMPERATURE_2_MAX) \
        VALUES ('"+\
        str(timestamp) 	+"'," +\
        str(rec_id) 	+","  +\
        str(t1)         + "," +\
        str(t1avg)         + "," +\
        str(t1min)         + "," +\
        str(t1max)         + "," +\
        str(t2)         + "," +\
        str(t2avg)         + "," +\
        str(t2min)         + "," +\
        str(t2max)         + \
        ");"
        
        try:
        	self.con = lite.connect(self.dbname)
        	self.cur = self.con.cursor()
        	self.cur.execute(sqlstr)
        	self.con.commit()
        	self.close_db()
        	flog.debug(inspect.stack()[1][3]+": replace: sql="+sqlstr)
        	#print (sqlstr)
        except Exception as e:
        	flog.warning(inspect.stack()[1][3]+" db replace mislukt."+" Melding="+str(e.args[0]))

    # select average, minimum and maximum
    def selectAMM(self, timestamp, record_id,flog ):

        sqlstr = "select \
        printf(\"%.1f\",avg(temperature_1_avg)), min(temperature_1_min), max(temperature_1_max), \
        printf(\"%.1f\",avg(temperature_2_avg)), min(temperature_2_min), max(temperature_2_max)  \
        from "+self.table+" where record_id = " + \
        str(record_id) + " and substr(timestamp,1," + str(len(timestamp))+") = '"+timestamp+"'"

        flog.debug(inspect.stack()[1][3]+": selectMAN: sql="+sqlstr)

        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r

    def cleanDb(self, flog):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()

        timestr=mkLocalTimeString() 
        # delete seconds values
        sql_del_str = "delete from "+self.table+" where record_id = 10 and timestamp <  '"+\
        str(datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - timedelta(hours=24))+"'"
        self.cur.execute(sql_del_str)
        flog.debug(inspect.stack()[1][3]+": delete day : sql="+sql_del_str)
        
        # delete minute values
        sql_del_str = "delete from "+self.table+" where record_id = 11 and timestamp <  '"+\
        str(datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - timedelta(days=7))+"'"
        self.cur.execute(sql_del_str)
        flog.debug(inspect.stack()[1][3]+": delete day : sql="+sql_del_str)
        
        # delete uren values
        sql_del_str = "delete from "+self.table+" where record_id = 12 and timestamp <  '"+\
        str(datetime.strptime(timestr,"%Y-%m-%d %H:%M:%S") - timedelta(days=366))+"'"
        self.cur.execute(sql_del_str)
        flog.debug(inspect.stack()[1][3]+": delete day : sql="+sql_del_str)
        
        self.con.commit()
        self.close_db()

class historyWeatherDB():

    def init(self,dbname, table):
        #print dbname, table
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        TIMESTAMP         TEXT PRIMARY KEY NOT NULL, \
        CITY_ID         INTEGER NOT NULL,\
        CITY             TEXT, \
        TEMPERATURE_MIN	REAL DEFAULT 0, \
        TEMPERATURE_AVG	REAL DEFAULT 0, \
        TEMPERATURE_MAX	REAL DEFAULT 0, \
        PRESSURE_MIN	INTEGER DEFAULT 0, \
        PRESSURE_AVG	INTEGER DEFAULT 0, \
        PRESSURE_MAX	INTEGER DEFAULT 0, \
        HUMIDITY_MIN	INTEGER DEFAULT 0, \
        HUMIDITY_AVG	INTEGER DEFAULT 0, \
        HUMIDITY_MAX	INTEGER DEFAULT 0, \
        WIND_SPEED_MIN	REAL DEFAULT 0, \
        WIND_SPEED_AVG	REAL DEFAULT 0, \
        WIND_SPEED_MAX	REAL DEFAULT 0, \
        WIND_DEGREE_MIN	REAL DEFAULT 0, \
        WIND_DEGREE_AVG	REAL DEFAULT 0, \
        WIND_DEGREE_MAX	REAL DEFAULT 0 \
        );")
        self.close_db()

    def sql2file(self, filename): 
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP, CITY_ID , CITY,\
        TEMPERATURE_MIN, TEMPERATURE_AVG, TEMPERATURE_MAX,\
        PRESSURE_MIN, PRESSURE_AVG, PRESSURE_MAX,\
        HUMIDITY_MIN, HUMIDITY_AVG, HUMIDITY_MAX,\
        WIND_SPEED_MIN, WIND_SPEED_AVG, WIND_SPEED_MAX,\
        WIND_DEGREE_MIN, WIND_DEGREE_AVG, WIND_DEGREE_MAX\
        from '+\
        self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (\
TIMESTAMP,CITY_ID,CITY,\
TEMPERATURE_MIN,TEMPERATURE_AVG,TEMPERATURE_MAX,\
PRESSURE_MIN,PRESSURE_AVG,PRESSURE_MAX,\
HUMIDITY_MIN,HUMIDITY_AVG,HUMIDITY_MAX,\
WIND_SPEED_MIN,WIND_SPEED_AVG,WIND_SPEED_MAX,\
WIND_DEGREE_MIN,WIND_DEGREE_AVG,WIND_DEGREE_MAX\
) values ('" + \
            str(i[0]) + "'," +\
            str(i[1]) + ",'" +\
            str(i[2]) + "'," +\
            str(i[3]) + "," +\
            str(i[4]) + "," +\
            str(i[5]) + "," +\
            str(i[6]) + "," +\
            str(i[7]) + "," +\
            str(i[8]) + "," +\
            str(i[9]) + "," +\
            str(i[10]) + ","+\
            str(i[11]) + ","+\
            str(i[12]) + ","+\
            str(i[13]) + ","+\
            str(i[14]) + ","+\
            str(i[15]) + ","+\
            str(i[16]) + ","+\
            str(i[17]) +\
            ");"
            #print line 
            f.write(line+'\n')
            reccount=reccount+1
        f.close() #close our file
        return reccount

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r
        
    def close_db(self):
        if self.con:
            self.con.close()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()


class currentWeatherDB():

    def init(self,dbname, table):
        #print dbname, table
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        TIMESTAMP       TEXT PRIMARY KEY NOT NULL, \
        CITY_ID         INTEGER NOT NULL,\
        CITY            TEXT, \
        TEMPERATURE     REAL DEFAULT 0, \
        DESCRIPTION     TEXT, \
        WEATHER_ICON    TEXT, \
        PRESSURE        INTEGER DEFAULT 0, \
        HUMIDITY        INTEGER DEFAULT 0, \
        WIND_SPEED      REAL DEFAULT 0, \
        WIND_DEGREE     REAL DEFAULT 0, \
        CLOUDS          INTEGER DEFAULT 0, \
        WEATHER_ID      INTEGER DEFAULT 0 \
        );")
        self.close_db()

    # volgorde van tuples mag niet worden gewijzigd, wordt gebruikt in MQTT proces.
    def select_one_record(self , order='desc' ):
        try:
            sqlstr = "select \
                datetime( TIMESTAMP, 'unixepoch', 'localtime' ), \
                TIMESTAMP, \
                CITY_ID, \
                CITY, \
                TEMPERATURE, \
                DESCRIPTION, \
                WEATHER_ICON, \
                PRESSURE, \
                HUMIDITY, \
                WIND_SPEED, \
                WIND_DEGREE, \
                CLOUDS, \
                WEATHER_ID \
                from " + self.table + \
                " order by timestamp " + str(order) + " limit 1;"
            sqlstr = " ".join( sqlstr.split() )
            set = self.select_rec( sqlstr )
            if len(set) > 0:
                return set[0][0], set[0][1], set[0][2], set[0][3], set[0][4], \
                       set[0][5], set[0][6], set[0][7], set[0][8], set[0][9], set[0][10], set[0][11], set[0][12] 
            return None
        except Exception as _e:
            print ( _e )
            return None


    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP, CITY_ID , CITY, TEMPERATURE, DESCRIPTION, \
        WEATHER_ICON, PRESSURE, HUMIDITY, WIND_SPEED, WIND_DEGREE, CLOUDS, WEATHER_ID \
        from '+\
        self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,CITY_ID,CITY,TEMPERATURE,DESCRIPTION,\
WEATHER_ICON,PRESSURE,HUMIDITY,WIND_SPEED,WIND_DEGREE,CLOUDS,WEATHER_ID) values ('" + \
            str(i[0]) + "','" +\
            str(i[1]) + "','" +\
            str(i[2]) + "','" +\
            str(i[3]) + "','" +\
            str(i[4]) + "','" +\
            str(i[5]) + "','" +\
            str(i[6]) + "','" +\
            str(i[7]) + "','" +\
            str(i[8]) + "','" +\
            str(i[9]) + "','" +\
            str(i[10]) + "','"+\
            str(i[11]) + "'" +\
            ');'
        #print line 
            f.write(line+'\n')
            reccount=reccount+1
        f.close() #close our file
        return reccount

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r
        
    def close_db(self):
        if self.con:
        	self.con.close()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()
        
    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

class SqlDb1():
    
    def init(self, dbname, table):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        # VEBRK = energie waar je voor betaald aan de leverancier (nuon enz) :(
        # GELVR = energie die je TERUG levert aan de leverancier :)
        # TIMESTAMP_X hele minuut waarde in seconden
        # RECORD_VERWERKT: 0= nog niet verwerk 1, wel verwerkt
        # TARIEFCODE D=DAL, P=PIEK
        # VERBR_GAS
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        TIMESTAMP TEXT PRIMARY KEY NOT NULL, \
        RECORD_VERWERKT INTEGER DEFAULT 0,\
        VERBR_KWH_181 REAL DEFAULT 0, \
        VERBR_KWH_182 REAL DEFAULT 0, \
        GELVR_KWH_281 REAL DEFAULT 0, \
        GELVR_KWH_282 REAL DEFAULT 0, \
        TARIEFCODE TEXT, \
        ACT_VERBR_KW_170 REAL DEFAULT 0, \
        ACT_GELVR_KW_270 REAL DEFAULT 0, \
        VERBR_GAS_2421 REAL DEFAULT 0);")
        # clean up van het database bestand
        self.close_db()

    # volgorde van tuples mag niet worden gewijzigd, wordt gebruikt in MQTT proces.
    def select_one_record(self , order='desc' ):
        try:
            sqlstr = "select \
                TIMESTAMP, \
                cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), \
                VERBR_GAS_2421, \
                VERBR_KWH_182, \
                VERBR_KWH_181, \
                ACT_VERBR_KW_170, \
                GELVR_KWH_282, \
                GELVR_KWH_281, \
                ACT_GELVR_KW_270 ,\
                TARIEFCODE, \
                RECORD_VERWERKT \
                from " + self.table + \
                " order by timestamp " + str(order) + " limit 1;"
            sqlstr = " ".join( sqlstr.split() )
            set = self.select_rec( sqlstr )
            if len(set) > 0:
                return set[0][0], set[0][1], set[0][2], set[0][3], set[0][4], set[0][5], set[0][6], set[0][7], set[0][8], set[0][9], set[0][10]
            return None
        except Exception as _e:
            print ( _e )
            return None


    def close_db(self):
        if self.con:
            self.con.close()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

    def count(self):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select count() from ' + self.table )
        rowcount = self.cur.fetchall()
        self.close_db()
        return int( rowcount[0][0] )

class SqlDb2():
    
    def init(self,dbname, table):
        self.dbname = dbname
        self.con = lite.connect(dbname ) 
        self.cur = self.con.cursor()
        self.table = table
        # VEBRK = energie waar je voor betaald aan de leverancier (nuon enz) :(
        # GELVR = energie die je TERUG leverd aan de leverancier :)
        # TIMESTAMP_X hele minuut waarde in seconden
        # RECORD_VERWERKT: 0= nog niet verwerk 1, wel verwerkt
        # TARIEFCODE D=DAL=001, P=PIEK=002
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
            TIMESTAMP TEXT PRIMARY KEY NOT NULL, \
            VERBR_KWH_181 REAL DEFAULT 0, \
            VERBR_KWH_182 REAL DEFAULT 0, \
            GELVR_KWH_281 REAL DEFAULT 0, \
            GELVR_KWH_282 REAL DEFAULT 0, \
            VERBR_KWH_X REAL DEFAULT 0,\
            GELVR_KWH_X REAL DEFAULT 0,\
            TARIEFCODE TEXT, \
            ACT_VERBR_KW_170 REAL DEFAULT 0, \
            ACT_GELVR_KW_270 REAL DEFAULT 0, \
            VERBR_GAS_2421 REAL DEFAULT 0\
        );")
        # clean up van het database bestand , file kleiner maken
        self.close_db()


    def executscript( self, script ): #TODO verder uitzoeken/testen.
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.executescript( script )
        self.close_db()

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, \
        GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X,TARIEFCODE,ACT_VERBR_KW_170, ACT_GELVR_KW_270 ,VERBR_GAS_2421 from '+\
        self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,VERBR_KWH_181,VERBR_KWH_182,\
GELVR_KWH_281,GELVR_KWH_282,VERBR_KWH_X,GELVR_KWH_X,TARIEFCODE,ACT_VERBR_KW_170,\
ACT_GELVR_KW_270,VERBR_GAS_2421) values ('" + \
            str(i[0]) + "','" +\
            str(i[1]) + "','" +\
            str(i[2]) + "','" +\
            str(i[3]) + "','" +\
            str(i[4]) + "','" +\
            str(i[5]) + "','" +\
            str(i[6]) + "','" +\
            str(i[7]) + "','" +\
            str(i[8]) + "','" +\
            str(i[9]) + "','" +\
            str(i[10]) + "'" +\
            ');'
        #print line 
            f.write(line+'\n')
            reccount=reccount+1
        f.close() #close our file
        return reccount
        #setFile2user(filename,'p1mon')

    def close_db(self):
        if self.con:
            self.con.close()

    def insert_rec( self,sqlstr ):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute( sqlstr )
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()


class SqlDb3():

    def init(self,dbname, table):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        # VEBRK = energie waar je voor betaald aan de leverancier (nuon enz) :(
        # GELVR = energie die je TERUG leverd aan de leverancier :)
        # TIMESTAMP_X hele minuut waarde in seconden
        # RECORD_VERWERKT: 0= nog niet verwerk 1, wel verwerkt
        # TARIEFCODE D=DAL=001, P=PIEK=002
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        TIMESTAMP TEXT PRIMARY KEY NOT NULL, \
        VERBR_KWH_181 REAL DEFAULT 0, \
        VERBR_KWH_182 REAL DEFAULT 0, \
        GELVR_KWH_281 REAL DEFAULT 0, \
        GELVR_KWH_282 REAL DEFAULT 0, \
        VERBR_KWH_X REAL DEFAULT 0,\
        GELVR_KWH_X REAL DEFAULT 0,\
        TARIEFCODE TEXT, \
        VERBR_GAS_2421 REAL DEFAULT 0,\
        VERBR_GAS_X REAL DEFAULT 0\
        );")
        self.close_db()

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281,\
        GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X,TARIEFCODE, VERBR_GAS_2421, VERBR_GAS_X from '+\
        self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,VERBR_KWH_181,VERBR_KWH_182,\
GELVR_KWH_281,GELVR_KWH_282,VERBR_KWH_X,GELVR_KWH_X,TARIEFCODE,VERBR_GAS_2421,VERBR_GAS_X) values ('" + \
            str(i[0]) + "','" +\
            str(i[1]) + "','" +\
            str(i[2]) + "','" +\
            str(i[3]) + "','" +\
            str(i[4]) + "','" +\
            str(i[5]) + "','" +\
            str(i[6]) + "','" +\
            str(i[7]) + "','" +\
            str(i[8]) + "','" +\
            str(i[9]) + "'" +\
            ');'
            #print line 
            f.write(line+'\n')
            reccount=reccount+1
        f.close() #close our file
        return reccount

    def close_db(self):
        if self.con:
            self.con.close()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

class SqlDb4():

    def init(self,dbname, table):
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        # VEBRK = energie waar je voor betaald aan de leverancier (nuon enz) :(
        # GELVR = energie die je TERUG leverd aan de leverancier :)
        # TIMESTAMP_X hele minuut waarde in seconden
        # RECORD_VERWERKT: 0= nog niet verwerk 1, wel verwerkt
        # TARIEFCODE D=DAL=001, P=PIEK=002
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        TIMESTAMP TEXT PRIMARY KEY NOT NULL, \
        VERBR_KWH_181 REAL DEFAULT 0, \
        VERBR_KWH_182 REAL DEFAULT 0, \
        GELVR_KWH_281 REAL DEFAULT 0, \
        GELVR_KWH_282 REAL DEFAULT 0, \
        VERBR_KWH_X REAL DEFAULT 0,\
        GELVR_KWH_X REAL DEFAULT 0, \
        VERBR_GAS_2421 REAL DEFAULT 0,\
        VERBR_GAS_X REAL DEFAULT 0\
        );")
        # clean up van het database bestand , file kleiner maken
        self.close_db()

    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281,\
        GELVR_KWH_282, VERBR_KWH_X, GELVR_KWH_X, VERBR_GAS_2421, VERBR_GAS_X from '+\
        self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,VERBR_KWH_181,VERBR_KWH_182,\
GELVR_KWH_281,GELVR_KWH_282,VERBR_KWH_X,GELVR_KWH_X,VERBR_GAS_2421,VERBR_GAS_X) values ('" + \
            str(i[0]) + "','" +\
            str(i[1]) + "','" +\
            str(i[2]) + "','" +\
            str(i[3]) + "','" +\
            str(i[4]) + "','" +\
            str(i[5]) + "','" +\
            str(i[6]) + "','" +\
            str(i[7]) + "','" +\
            str(i[8]) + "'" +\
            ');'
    #print line 
            f.write(line+'\n')
            reccount=reccount+1
        f.close() #close our file
        return reccount

    def close_db(self):
        if self.con:
            self.con.close()

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()

class financieelDb():
    def init(self, dbname, table):
        #print dbname
        #print "[*]",table
        self.dbname = dbname
        self.con = lite.connect(dbname)
        self.cur = self.con.cursor()
        self.table = table
        # VEBRK = energie waar je voor betaald aan de leverancier (nuon enz) :(
        # GELVR = energie die je TERUG levert aan de leverancier :)
        self.cur.execute("CREATE TABLE IF NOT EXISTS "+table+"(\
        TIMESTAMP TEXT PRIMARY KEY NOT NULL, \
        VERBR_P REAL DEFAULT 0,\
        VERBR_D REAL DEFAULT 0,\
        GELVR_P REAL DEFAULT 0,\
        GELVR_D REAL DEFAULT 0,\
        GELVR_GAS REAL DEFAULT 0,\
        VERBR_WATER REAL DEFAULT 0\
        );")
        self.close_db()
        # add column, extentions
        try: 
            sql = "ALTER TABLE " + self.table + " ADD COLUMN VERBR_WATER REAL DEFAULT 0;"
            #print (sql)
            self.execute( sql )
        except:
            pass # don't fail if column allready exits


    def sql2file(self, filename):
        #print filename
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute('select TIMESTAMP, VERBR_P, VERBR_D, GELVR_P, GELVR_D, GELVR_GAS, VERBR_WATER from '+ self.table +' order by TIMESTAMP')
        r=self.cur.fetchall()
        self.close_db() 
        # put the stuff into a file
        #print r
        reccount=0
        f = open(filename,"a")
        for i in r:
            line = "replace into " + self.table + " (TIMESTAMP,VERBR_P,VERBR_D,GELVR_P,GELVR_D,GELVR_GAS,VERBR_WATER) values ('" + \
            str(i[0]) + "','" +\
            str(i[1]) + "','" +\
            str(i[2]) + "','" +\
            str(i[3]) + "','" +\
            str(i[4]) + "','" +\
            str(i[5]) + "','" +\
            str(i[6]) + "'" +\
            ');'
            #print line 
            f.write(line+'\n')
            reccount=reccount+1
        f.close() #close our file
        return reccount
        #setFile2user(filename,'p1mon')         

    def close_db(self):
        if self.con:
            self.con.close()

    def execute( self, sqlstr ):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute( sqlstr )
        self.con.commit()
        self.close_db()

    def select_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        r=self.cur.fetchall()
        self.close_db()
        return r 

    def insert_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def update_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def del_rec(self,sqlstr):
        self.con = lite.connect(self.dbname)
        self.cur = self.con.cursor()
        self.cur.execute(sqlstr)
        self.con.commit()
        self.close_db()

    def defrag(self):
        self.con = lite.connect(self.dbname)
        self.con.execute("VACUUM;")
        self.close_db()

    def integrity_check( self ):
        self.con = lite.connect(self.dbname)
        self.con.execute("PRAGMA quick_check;")
        self.close_db()


