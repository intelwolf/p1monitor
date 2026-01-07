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
# versie 0.9.13 Aanpassingen voor België gedaan en screensaver.
# versie 201912-0.9.14 watermeter DB toegevoegd
# versie 202002-0.9-15 MQTT
# versie 202004-0.9.16 fase DB en ui toegevoegd.
# versie 202009-0.9.18 aanzienlijke aanpassing aan de API om de IOS app te ondersteunen.
# versie 202012-1.0.0 Versie met support voor S0 puls kWh meting.
# Versie 1.1.0 Watermeter kan nu ook minuut waarden verwerken. 
# Versie 1.2.0 log file viewer toegevoegd.
# Versie 1.3.0 Tweede powerproduction voor solar toegevoegd.
# Versie 1.4.0 Internet API toegevoegd en 1 sec verwerking.
# Versie 1.4.1 DNS en Letsencrypt uitbreidingen. QR code voor API's toegevoegd.
# Versie 1.5.0 P1UpdateAide en Excel export toegevoegd.
# Versie 1.6.0 Bug fixes. patch 1 lost een fout in /etc/dhcpcd.conf
# versie 1.7.0 min max fase info toegevoegd en grootverbruikers meters.
# versie 2.0.0 os upgrade naar Bullseye OS en introductie van Python virtuele omgevingen.
# versie 2.1.0 os upgrade, graaddagen en SOCAT toegevoegd.
# versie 2.2.0 os upgrade, flexibele tarieven en piek waarde toegevoegd.
# versie 2.3.0 P1Upgrade assistent en watermeter conversie verwijderd.
# versie 2.4.0 Veel vertalingen uitgewerkt.
# versie 2.4.1 Vertalingen uitgewerkt aangevuld.
# versie 2.4.2 P1DatabaseOptimizer toegevoegd en fase informatie aan op de main schermen.
# versie 2.4.3 P1SetTime toegevoegd en het instellen van de tijd via het systeem config pagina
# versie 3.0.0 Upgrade naar Raspberry Pi OS Bookworm (Debian 12)
# versie 3.0.1 Nginx opstart probleem /var/lib/nginx/proxy
# versie 3.1.0 added statistic option
# versie 3.2.0 a lot of fixes and MQTT fixes.
# versie 3.3.0 Added Digital watermeter and corresponding changes

###########################################
# onderstaande drie versie constanten bij #
# elke release aanpassen                  #
###########################################
P1_VERSIE                       = "3.3.0"       # semantische versie nummers.
P1_PATCH_LEVEL                  = "3"           # standaard op 0, wordt verhoogd als op een image een patch wordt toegevoegd
P1_SERIAL_VERSION               = "20260107"    # moet altijd gewijzigd worden bij een nieuwe versie

#CRYPTO_SEED                     ="bee31cd96a3ce221"
DEFAULT_EMAIL_NOTIFICATION      = 'P1 monitor notificatie'
# NEW DB FILE NAMES START WITH A NUMBER THAT MUST BE UNIQUE 
# DBX_ = DROPBOX
INTERNET_TIME_URL               ="https://timeapi.io/api/time/current/zone?timeZone=Europe%2FAmsterdam"
ZTATZ_P1_VERSION_URL            ="https://p1-monitor.nl/p1monitor/version.json" # V3.3.0 patch 3
ZTATZ_P1_VERSION_MSG_VERSION    ='MSG_VERSION'
ZTATZ_P1_VERSION_TIMESTAMP      ='TIMESTAMP_LOCAL'
ZTATZ_P1_VERSION                ='P1MON_VERSION'
ZTATZ_P1_VERSION_TEXT           ='VERSION_TEXT'
ZTATZ_P1_VERSION_DOWNLOAD_URL   ='DOWNLOAD_URL'
ZTATZ_P1_SERIAL_VERSION         ='SERIAL_VERSION' 
ZTATZ_P1_VERSION_PATCH_VERSION  ='PATCH_VERSION' # 3.0.0.  Status IDX: 
ZTATZ_P1_VERSION_DOWNLOAD_URL_PATCH ='DOWNLOAD_URL_PATCH' # 3.0.0. Status IDX: 
ZTATZ_P1_VERSION_COMMENT        ='COMMENT' # 3.0.0. Status IDX:
API_BASIC_JSON_PREFIX           ='basic.'
API_BASIC_JSON_SUFFIX           ='.json'
API_BASIC_VERSION               = 7 # updated in version > 1.4.0
UDP_BASIC_API_PORT              = 40721
P1_UPGRADE_ASSIST               ="P1UPGRADEASSIST"
SYSTEM_ID_DEFAULT               ="0000-0000-0000-0000-0000"
DBX_DIR_BACKUP                  ="/backup"
DBX_DIR_DATA                    ="/data"
DBX_REQ_DATA                    ="datarequestsqldb"
DB_SERIAL                       ="e_serial"
DB_E_HISTORIE                   ="e_historie" # added version > 2.4.1
DB_E_HISTORIE_TAIL              ="historie"
DB_CONFIG                       ="configuratie"
DB_CONFIGURATIE                 ="config" # added version > 2.4.1
DB_STATUS                       ="status"
DB_FINANCIEEL                   ="financieel" # aangepast vanaf versie 0.9.19 en hoger was finacieel
DB_WEER                         ="weer"
DB_WEER_HISTORY                 ="01_weer_historie"
DB_TEMPERATURE                  ="02_temperatuur"
DB_WATERMETER                   ="03_watermeter"
DB_PHASEINFORMATION             ="04_faseinformatie"
DB_POWERPRODUCTION              ="05_powerproduction"
DB_WATERMETERV2                 ="06_watermeter"
DB_STATISTICS                   ="07_statistics" # 3.1.0

DB_STATISTICS_TAB               ="statistics" # 3.1.0
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
DB_FASE_MINMAX_DAG_TAB          ="faseminmax_dag"
DB_STATUS_TAB                   ="status"
DB_CONFIG_TAB                   ="config"
DB_FINANCIEEL_DAG_TAB           ="e_financieel_dag"
DB_FINANCIEEL_MAAND_TAB         ="e_financieel_maand"
DB_FINANCIEEL_JAAR_TAB          ="e_financieel_jaar"
#DB_FINANCIEEL_DAG_VOORSPEL_TAB  ="e_financieel_voorspel_dag" remove in version > 2.4.1
DB_ENERGIEPRIJZEN_UUR_TAB       ="energieprijzen_uur"
DB_WEATHER_TAB                  ="weer"
DB_WEATHER_UUR_TAB              ="weer_history_uur"
DB_WEATHER_DAG_TAB              ="weer_history_dag"
DB_WEATHER_MAAND_TAB            ="weer_history_maand"
DB_WEATHER_JAAR_TAB             ="weer_history_jaar"
DB_TEMPERATUUR_TAB              ="temperatuur"
DB_POWERPRODUCTION_TAB          ="powerproduction"
DB_POWERPRODUCTION_SOLAR_TAB    ="powerproduction_solar" # 1.3.0
DIR_EXPORT                      ="/p1mon/export/"
DIR_FILEDISK                    ="/p1mon/data/"
DIR_RECOVERY                    ="/p1mon/recovery/"
FILE_DB_RECOVERY_EXT            =".recovery.db"
#DIR_FILELOG                     ="/p1mon/var/log/"
DIR_FILELOG                     ="/var/log/p1monitor/"
DIR_FILESEMAPHORE               ="/p1mon/mnt/ramdisk/"
DIR_NGINX_BASE                  ="/etc/nginx"
DIR_RAMDISK                     ="/p1mon/mnt/ramdisk/"
DIR_DBX_LOCAL                   ="/p1mon/mnt/ramdisk/dbx" # geen / toevoegen
DIR_VAR                         ="/p1mon/var/"
DIR_SCRIPTS                     ="/p1mon/scripts/"
DIR_UPGRADE_ASSIST              ="/p1monitor"
DIR_UPGRADE_ASSIST_DATA         =DIR_UPGRADE_ASSIST +"/data"
DIR_UPGRADE_ASSIST_WIFI         =DIR_UPGRADE_ASSIST +"/wifi"
DIR_UPGRADE_ASSIST_USB_MOUNT    ='/p1mon/mnt/usb'
DIR_USB_ROOT                    ="/p1monitor"
DIR_UPGRADE_AIDE                ='/aide'
DIR_USB_MOUNT                   ='/p1mon/mnt/usb'
#DIR_TMP                         ="/p1mon/var/tmp/"
DIR_DOWNLOAD                    ="/p1mon/www/download/"
DIR_WWW_CUSTOM                  ="/p1mon/www/custom"
DIR_WWW                         ='/p1mon/www'
EXPORT_PREFIX                   ="p1mon-sql-export"
IMPORT_PREFIX                   ="p1mon-sql-import"
FILE_DBX_AUTH_REDIRECT          ="dbx_auth_redirect.txt"

FILE_DB_STATISTICS              ="/p1mon/mnt/ramdisk/07_statistics.db" # 3.1.0
FILE_DB_POWERPRODUCTION         ="/p1mon/mnt/ramdisk/05_powerproduction.db"
FILE_DB_PHASEINFORMATION        ="/p1mon/mnt/ramdisk/04_faseinformatie.db"
FILE_DB_WATERMETER              ="/p1mon/mnt/ramdisk/03_watermeter.db"
FILE_DB_WATERMETERV2            ="/p1mon/mnt/ramdisk/06_watermeter.db"
FILE_DB_E_FILENAME              ="/p1mon/mnt/ramdisk/e_serial.db"
FILE_DB_E_HISTORIE              ="/p1mon/mnt/ramdisk/e_historie.db"
FILE_DB_CONFIG                  ="/p1mon/mnt/ramdisk/config.db"
FILE_DB_STATUS                  ="/p1mon/mnt/ramdisk/status.db"
FILE_DB_FINANCIEEL              ="/p1mon/mnt/ramdisk/financieel.db"
FILE_DB_WEATHER                 ="/p1mon/mnt/ramdisk/weer.db"
FILE_DB_WEATHER_HISTORIE        ="/p1mon/mnt/ramdisk/01_weer_historie.db"
FILE_P1MSG                      ="/p1mon/mnt/ramdisk/p1msg.txt"
#FILE_WIFISSID                   ="/p1mon/mnt/ramdisk/wifi_essid.txt" # removed 3.0.0
FILE_ETH0MAC                    ="/p1mon/mnt/ramdisk/eth0mac.txt"
FILE_DB_WEER_FILENAME           ="/p1mon/mnt/ramdisk/weer.db"
FILE_MQTT_TOPICS                ="/p1mon/mnt/ramdisk/mqtt_topics.json"
#FILE_DB_WEER_HISTORIE_FILENAME  ="/p1mon/mnt/ramdisk/weer_historie.db"
FILE_DUCKDNS_STATUS             = "/p1mon/mnt/ramdisk/duckdns.status"
FILE_DB_TEMPERATUUR_FILENAME    ="/p1mon/mnt/ramdisk/02_temperatuur.db"
FILE_SESSION                    ="/p1mon/mnt/ramdisk/session.txt"
FILE_PREFIX_CUSTOM_UI           ="/p1mon/var/tmp/custom-www-export-"
FILE_EXPORT_MANIFEST            ="/p1mon/var/tmp/manifest.json"
FILE_UPGRADE_ASSIST_STATUS      ="/p1mon/mnt/ramdisk/upgrade-assist.status"
FILE_UPGRADE_AIDE_STATUS        ="/p1mon/mnt/ramdisk/upgrade-aide.status"
FILE_POWERPRODUCTION_CNT_STATUS ="/p1mon/mnt/ramdisk/powerproduction-counter-reset.status"
FILE_WATERMETER_CNT_STATUS      ="/p1mon/mnt/ramdisk/watermeter-counter-reset.status"
FILE_SQL_IMPORT_STATUS          ="/p1mon/mnt/ramdisk/sqlimport.status"
FILE_PATCH_STATUS               ="/p1mon/mnt/ramdisk/patch.status"
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
P1MSG_BUF_SIZE                  ="120"
NOT_SET                         = 999999999999

######################### NO-IP config #######################
# niet meer in gebruik maar kan in de toekomst weer gebruikt #
# worden.                                                    #
##############################################################
NO_IP_CONFIG_FILE               = '/p1mon/etc/no-ip2.conf'
