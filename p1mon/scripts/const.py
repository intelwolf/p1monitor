# constanten gebruikt bij meerdere scripts
# versie 0.3.1 export & bug fixes.
# versie 0.3.2 bug dat serial pariteit niet goed werkt.
# versie 0.5 API toegevoegd.
# versie 0.6 GAS meting toegevoegd
# versie 0.7 Weer informatie toegevoegd
# versie 0.7.2 API's toegevoegd.
# Versie 0.8 FTP back-up en Wifi bugs gefixed
# Versie 0.8.1 weer historie
# versie 0.9.3 Dropbox 
# versie 0.9.3.1 fix for wifi import issue.
# versie 0.9.4 Eerste versie met IOS app support.
# versie 0.9.6 API versie update.
# versie 0.9.7 API rewrite naar Falcon/Gunicorn.
# versie 0.9.10 meterstanden overzicht toegevoegd.
# versie 0.9.11 upgrade naar Raspbian Buster email notificatie. Pi4 geschikt.
# versie 0.9.13 Aanpassingen voor Belgie gedaan en screensaver.
# versie 201912-0.9.14 watermeter DB toegevoegd
# versie 202002-0.9-15 MQTT
# versie 202004-0.9.16 fase DB en ui toegevoegd.
# versie 202009-0.9.18 aanzienlijke aanpassing aan de API om de IOS app te ondersteunen.
# versie 202012-1.0.0 Versie met support voor S0 puls kWh meting.
# Versie 1.1.0 Watermeter kan nu ook minuut waarden verwerken. 
# Versie 1.2.0 log file viewer toegevoegd.

###########################################
# onderstaande drie versie constanten bij #
# elke release aanpassen                  #
###########################################
P1_VERSIE                       = "1.2.0"       # semantische versie nummers.
P1_PATCH_LEVEL                  = "0"           # standaard op 0, wordt verhoogd als op een image een patch wordt uigevoerd.
P1_SERIAL_VERSION               = "20210303"    # moet altijd gewijzigd worden bij een nieuwe versie


#CRYPTO_SEED                     ="bee31cd96a3ce221"
DEFAULT_EMAIL_NOTIFICATION      = 'P1 monitor notificatie'
# NEW DB FILE NAMES START WITH A NUMBER THAT MUST BE UNIQUE 
# DBX_ = DROPBOX
ZTATZ_P1_VERSION_URL            ="https://www.ztatz.nl/p1monitor/version.json"
ZTATZ_P1_VERSION_MSG_VERSION    ='MSG_VERSION'
ZTATZ_P1_VERSION_TIMESTAMP      ='TIMESTAMP_LOCAL'
ZTATZ_P1_VERSION                ='P1MON_VERSION'
ZTATZ_P1_VERSION_TEXT           ='VERSION_TEXT'
ZTATZ_P1_VERSION_DOWNLOAD_URL   ='DOWNLOAD_URL'
ZTATZ_P1_SERIAL_VERSION         ='SERIAL_VERSION'
API_BASIC_JSON_PREFIX           ='basic.'
API_BASIC_JSON_SUFFIX           ='.json'
API_BASIC_VERSION               =6
UDP_BASIC_API_PORT              =40721
P1_UPGRADE_ASSIST               ="P1UPGRADEASSIST"
SYSTEM_ID_DEFAULT               ="0000-0000-0000-0000-0000"
DBX_DIR_BACKUP                  ="/backup"
DBX_DIR_DATA                    ="/data"
DBX_REQ_DATA                    ="datarequestsqldb"
DB_SERIAL                       ="e_serial"
DB_E_HISTORIE                   ="historie"
DB_CONFIG                       ="configuratie"
DB_STATUS                       ="status"
DB_FINANCIEEL                   ="financieel" # aangepast vanaf versie 0.9.19 en hoger was finacieel
DB_WEER                         ="weer"
DB_WEER_HISTORY                 ="01_weer_historie"
DB_TEMPERATURE                  ="02_temperatuur"
DB_WATERMETER                   ="03_watermeter"
DB_PHASEINFORMATION             ="04_faseinformatie"
DB_POWERPRODUCTION              ="05_powerproduction"
DB_WATERMETERV2                 ="06_watermeter"
DB_SERIAL_TAB                   ="e_serial"
DB_HISTORIE_MIN_TAB             ="e_history_min"
DB_HISTORIE_UUR_TAB             ="e_history_uur"
DB_HISTORIE_DAG_TAB             ="e_history_dag"
DB_HISTORIE_MAAND_TAB           ="e_history_maand"
DB_HISTORIE_JAAR_TAB            ="e_history_jaar"
DB_WATERMETER_UUR_TAB           ="watermeter_history_uur"
DB_WATERMETER_DAG_TAB           ="watermeter_history_dag"
DB_WATERMETER_MAAND_TAB         ="watermeter_history_maand"
DB_WATERMETER_JAAR_TAB          ="watermeter_history_jaar"
DB_WATERMETERV2_TAB             ="watermeter"
DB_FASE_REALTIME_TAB            ="faseinformatie"
DB_STATUS_TAB                   ="status"    
DB_CONFIG_TAB                   ="config"     
DB_FINANCIEEL_DAG_TAB           ="e_financieel_dag"
DB_FINANCIEEL_MAAND_TAB         ="e_financieel_maand"
DB_FINANCIEEL_JAAR_TAB          ="e_financieel_jaar"
DB_FINANCIEEL_DAG_VOORSPEL_TAB  ="e_financieel_voorspel_dag"
DB_WEATHER_TAB                  ="weer"
DB_WEATHER_UUR_TAB              ="weer_history_uur"
DB_WEATHER_DAG_TAB              ="weer_history_dag"
DB_WEATHER_MAAND_TAB            ="weer_history_maand"
DB_WEATHER_JAAR_TAB             ="weer_history_jaar"
DB_TEMPERATUUR_TAB              ="temperatuur"
DB_POWERPRODUCTION_TAB          ="powerproduction"
DIR_EXPORT                      ="/p1mon/export/"
DIR_FILEDISK                    ="/p1mon/data/"
#DIR_FILELOG                     ="/p1mon/var/log/"
DIR_FILELOG                     ="/var/log/p1monitor/"
DIR_FILESEMAPHORE               ="/p1mon/mnt/ramdisk/"
DIR_RAMDISK                     ="/p1mon/mnt/ramdisk/"
DIR_DBX_LOCAL                   ="/p1mon/mnt/ramdisk/dbx" # geen / toevoegen
DIR_VAR                         ="/p1mon/var/"
DIR_SCRIPTS                     ="/p1mon/scripts/"
DIR_UPGRADE_ASSIST              ="/p1monitor"
DIR_UPGRADE_ASSIST_DATA         =DIR_UPGRADE_ASSIST +"/data"
DIR_UPGRADE_ASSIST_WIFI         =DIR_UPGRADE_ASSIST +"/wifi"
DIR_UPGRADE_ASSIST_USB_MOUNT    ='/p1mon/mnt/usb'
#DIR_TMP                         ="/p1mon/var/tmp/"
DIR_DOWNLOAD                    ="/p1mon/www/download/"
DIR_WWW_CUSTOM                  ="/p1mon/www/custom"
EXPORT_PREFIX                   ="p1mon-sql-export"
IMPORT_PREFIX                   ="p1mon-sql-import"

FILE_DB_POWERPRODUCTION         ="/p1mon/mnt/ramdisk/05_powerproduction.db"
#FILE_DB_POWERPRODUCTION_TMP     ="/p1mon/mnt/ramdisk/06_powerproduction_tmp.db"

FILE_DB_PHASEINFORMATION        ="/p1mon/mnt/ramdisk/04_faseinformatie.db"
FILE_DB_WATERMETER              ="/p1mon/mnt/ramdisk/03_watermeter.db"
FILE_DB_WATERMETERV2            ="/p1mon/mnt/ramdisk/06_watermeter.db"
FILE_DB_E_FILENAME              ="/p1mon/mnt/ramdisk/e_serial.db"
FILE_DB_E_FILENAME              ="/p1mon/mnt/ramdisk/e_serial.db"
FILE_DB_E_HISTORIE              ="/p1mon/mnt/ramdisk/e_historie.db"
FILE_DB_CONFIG                  ="/p1mon/mnt/ramdisk/config.db"
FILE_DB_STATUS                  ="/p1mon/mnt/ramdisk/status.db"
FILE_DB_FINANCIEEL              ="/p1mon/mnt/ramdisk/financieel.db"
FILE_DB_WEATHER                 ="/p1mon/mnt/ramdisk/weer.db"
FILE_DB_WEATHER_HISTORIE        ="/p1mon/mnt/ramdisk/01_weer_historie.db"
FILE_P1MSG                      ="/p1mon/mnt/ramdisk/p1msg.txt"
FILE_WIFISSID                   ="/p1mon/mnt/ramdisk/wifi_essid.txt"
FILE_ETH0MAC                    ="/p1mon/mnt/ramdisk/eth0mac.txt"
FILE_DB_WEER_FILENAME           ="/p1mon/mnt/ramdisk/weer.db"
FILE_MQTT_TOPICS                ="/p1mon/mnt/ramdisk/mqtt_topics.json"
#FILE_DB_WEER_HISTORIE_FILENAME  ="/p1mon/mnt/ramdisk/weer_historie.db"
FILE_DB_TEMPERATUUR_FILENAME    ="/p1mon/mnt/ramdisk/02_temperatuur.db"
FILE_SESSION                    ="/p1mon/mnt/ramdisk/session.txt"
FILE_PREFIX_CUSTOM_UI           ="/p1mon/var/tmp/custom-www-export-"
FILE_EXPORT_MANIFEST            ="/p1mon/var/tmp/manifest.json"
FILE_UPGRADE_ASSIST_STATUS      ="/p1mon/mnt/ramdisk/upgrade-assist.status"
FILE_POWERPRODUCTION_CNT_STATUS ="/p1mon/mnt/ramdisk/powerproduction-counter-reset.status"
FILE_WATERMETER_CNT_STATUS      ="/p1mon/mnt/ramdisk/watermeter-counter-reset.status"
FILE_SQL_IMPORT_STATUS          ="/p1mon/mnt/ramdisk/sqlimport.status"
TARIEF_VERBR_LAAG               ="0.20522"
TARIEF_VERBR_HOOG               ="0.20522"
TARIEF_GELVR_LAAG               ="0.20522"
TARIEF_GELVR_HOOG               ="0.20522"
TARIEF_VASTRECHT_PER_MAAND      ="6.10"
GAS_TARIEF                      ="0.64"
GAS_VASTRECHT_TARIEF_PER_MAAND  ="0"
TARIEF_WATER_VASTRECHT_PER_MAAND="0"
TARIEF_WATER_TARIEF_PER_M3      ="0"
FINANCIEEL_GRENS_MAX            ="0"
FILESHARE_MODE_UIT              ="uit"
FILESHARE_MODE_DATA             ="data"
FILESHARE_MODE_DEV              ="dev"
P1MSG_BUF_SIZE                  ="120"
NOT_SET                         =999999999999

