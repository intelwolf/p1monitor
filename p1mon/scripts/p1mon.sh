#!/bin/bash
PROG="p1mon"
PHP_SESSIONS="/run/php/sessions"
PYTHONENV="/p1mon/p1monenv"
MY_PYTHON="python3"
PRG_PATH="/p1mon/scripts/"
PID_PATH="/p1mon/mnt/ramdisk/"
DB_PATH="/p1mon/mnt/ramdisk/"
LOG_PATH="/var/log/p1monitor/"
LOCK_PATH="/var/lock/"
WWW_DOWLOAD_PATH="/p1mon/www/download"
EXPORT_PATH="/p1mon/export/"
RAMDISK="/p1mon/mnt/ramdisk/"
DATADISK="/p1mon/data/"
DBX_ROOT="/p1mon/mnt/ramdisk/dbx/"
DBX_DATA="/data" 
DBX_BACKUP="/backup"
STATUS_FILE="p1mon*status"
PRG1="P1SerReader"
PRG2="P1Db"
PRG3="P1Watchdog"
PRG4="*.log*"
PRG5="P1Weather"
PRG6="P1UdpDaemon"
PRG7="P1DropBoxDeamon"
PRG8="P1UdpBroadcaster"
PRG9="gunicorn"
PRG9_PATH="/p1mon/p1monenv/bin/"
PRG9_ALIAS="P1Api.py"
PRG9_PARAMETERS="--timeout 900 --bind localhost:10721 --worker-tmp-dir /p1mon/mnt/ramdisk --workers 3 P1Api:app --log-level warning"
PRG10="niet meer in gebruik"
PRG11="logspacecleaner.sh"
PRG12="niet meer in gebruik"
PRG13="P1MQTT"
PRG14="P1GPIO"
PRG15="P1PowerProductionS0"
PRG16="P1WatermeterV2"
PRG17="P1SolarEdgeReader"
PRG18="niet meer in gebruik"
PRG19="P1UpgradeAide"
PRG20="P1Notifier"
PRG21="P1DbCopy"
PRG22="P1DatabaseOptimizer"
P1FILE="p1msg.txt"

# make a symbolic link for old /etc/nginx/sites-enabled/p1mon_80 config files added in version 2.0.0
sudo ln -s /run/php/php-fpm.sock /run/php/php7.3-fpm.sock  2>/dev/null # /dev/null to be silent when link allready exits.

## reset rechten wegens dev werk en kopie acties.
sudo /bin/chmod 775  $PRG_PATH$PRG8 $PRG_PATH$PRG1 $PRG_PATH$PRG2 $PRG_PATH$PRG3 $PRG_PATH$PRG5 $PRG_PATH$PRG6 $LOG_PATH$PRG4 $PID_PATH$P1FILE  &>/dev/null
sudo /bin/chown p1mon:p1mon $PRG_PATH$PRG8 $PRG_PATH$PRG1 $PRG_PATH$PRG2 $PRG_PATH$PRG3 $PRG_PATH$PRG5 $PRG_PATH$PRG6 $LOG_PATH$PRG4 $PID_PATH$P1FILE &>/dev/null

cd $PRG_PATH
sudo chmod 754 P1*.py*;sudo chown p1mon:p1mon P1*.py
sudo chmod 754 *.sh;sudo chown p1mon:p1mon *.sh 
sudo chmod 660 *_lib.py
## set de bash stub scripts
sudo ls P1*|grep -v py|xargs -n 1 chmod 750

# make p1monitor log folder (new from june 2019)
sudo mkdir -p p1monitor $LOG_PATH
sudo /bin/chown p1mon:p1mon $LOG_PATH $WWW_DOWLOAD_PATH $EXPORT_PATH $RAMDISK
sudo /bin/chmod 775 $LOG_PATH 
sudo /bin/chmod 770 $WWW_DOWLOAD_PATH $EXPORT_PATH

#PHP sessions path, PHP will not create this directory structure automatically
echo "[*] PHP folder $PHP_SESSIONS wordt aangemaakt."
sudo /usr/bin/mkdir -p $PHP_SESSIONS
sudo /usr/bin/chmod 733 $PHP_SESSIONS
sudo /usr/bin/chmod +t $PHP_SESSIONS

cd $LOG_PATH
sudo /bin/chown p1mon:p1mon *.log
sudo /bin/chmod 664 *.log

# clean log files on any action, also done by the watchdog
# script clean when gets full. Should never happen ;)
sudo $PRG_PATH$PRG11

# setup the python enviroment
cd $PYTHONENV
source bin/activate
cd $PRG_PATH

start() {

    # Upgrade Aide check if there is data on an USB drive
    # restore and enlarge the SDHC when there is data on
    # the drive.
    $PRG_PATH$PRG19 --restore --reboot
    #eval "$MY_PYTHON $PRG19 --restore --reboot"
    echo "[*] $PRG19 gestart."

    # disable power save van de wifi.
    echo "[*] Wifi power save wordt uitgezet."
    sudo /sbin/iw dev wlan0 set power_save off
    /sbin/iw wlan0 get power_save
    echo "[*] Wifi power save is uitgezet."

    #upgrade assist start (vervallen vanaf versie 2.3.0)
    #echo "Upgrade assist wordt gestart."
    #eval "$MY_PYTHON $PRG10 --restore"
    #echo "[*] $PRG10 gestart."
    #$PRG_PATH$PRG10

    # note the watchdog does the import from /p1mon/data 
    # failsave stop of processed that may stil be running
    echo "[*] failsave stop voor dat de processen weer worden gestart."
    stop
    echo "[*] 2 seconden wachttijd"
    sleep 2

    # set sticky bit for C program to run als p1mon 
    # sudo /bin/chmod +s /p1mon/scripts/p1monExec # verwijderd in versie 2.0.0
    # remove status file(s) if they exists.
    sudo /bin/rm $RAMDISK$STATUS_FILE &>/dev/null

    # Database fix
    # do flash disk, before the copy to ram.
    echo "[*] $PRG22 gestart. watermeter fix."
    $PRG_PATH$PRG22 -ws -d 2>&1 >/dev/null

    # Start P1 port reader.
    $PRG_PATH$PRG1 2>&1 >/dev/null &
    #eval "$MY_PYTHON $PRG1 2>&1 >/dev/null &"
    pid=$! # last command pid
    #echo "running "$pid
    sleep 5 # give some time to start the process
    #sudo renice -n -15 -p $pid >/dev/null 
    sudo renice -n -15 $(pgrep -P $pid) >/dev/null # make sure the serial processing has an higer priorty
    echo "[*] $PRG1 process prioriteit verhoogd."
    #echo "running "$pid
    echo "[*] $PRG1 gestart."
    # tijd zodat de serial db bij het starten gedefragmenteerd kan worden
    echo "[*] 3 seconden wachttijd"
    sleep 3

    # start the database process
    $PRG_PATH$PRG2 2>&1 >/dev/null &
    #eval "$MY_PYTHON $PRG2 2>&1 >/dev/null &"
    echo "[*] $PRG2 gestart."
    echo "[*] 3 seconden wachttijd"
    sleep 3

    # DropBoxDaemon start
    # make folders if not available (thank you -p switch)
    # folder are also made by program.
    sudo /bin/mkdir -p $DBX_ROOT $DBX_ROOT$DBX_DATA $DBX_ROOT$DBX_BACKUP
    sudo find  $DBX_ROOT -type d -exec chmod 774 {} +
    sudo /bin/chmod 774 $DBX_ROOT
    sudo /bin/chown p1mon:p1mon $DBX_ROOT $DBX_ROOT$DBX_DATA $DBX_ROOT$DBX_BACKUP
    #eval "$MY_PYTHON $PRG7 2>&1 >/dev/null &"
    $PRG_PATH$PRG7 2>&1 >/dev/null &
    echo "[*] $PRG7 gestart."

    # Watchdog start
    $PRG_PATH$PRG3 2>&1 >/dev/null &
    #eval "$MY_PYTHON $PRG3 2>&1 >/dev/null &"
    echo "[*] $PRG3 gestart."

    # run weather once to make sure we have the weather database, fixes import issues.
    #eval "$MY_PYTHON $PRG5 --getweather 2>&1 >/dev/null &"
    $PRG_PATH$PRG5 --getweather 2>&1 >/dev/null &
    echo "[*] $PRG5 -getweather gestart."
    echo "[*] 2 seconden wachttijd"
    sleep 2

    # run weather once to recover graaddagen when not set
    # when set do nothing. use UI to force the recalculating
    # eval "$MY_PYTHON $PRG5 --recover 2>&1 >/dev/null &"
    $PRG_PATH$PRG5 --recover 2>&1 >/dev/null &
    echo "[*] $PRG5 --recover gestart."

    # UDP deamon start
    $PRG_PATH$PRG6 2>&1 >/dev/null &
    #eval "$MY_PYTHON $PRG6 2>&1 >/dev/null &"
    echo "[*] $PRG6 gestart."

    # UDP broadcast start
    $PRG_PATH$PRG8 &>/dev/null &
    #eval "$MY_PYTHON $PRG8 2>&1 >/dev/null &"
    $PRG_PATH$PRG8 2>&1 >/dev/null &
    echo "[*] $PRG8 gestart."

    # API start
    cd $PRG_PATH
    # $PRG9_PATH$PRG9$PRG9_PARAMETERS 2>&1 >/dev/null &
    eval "$PRG9_PATH$PRG9 $PRG9_PARAMETERS 2>&1 >/dev/null &"
    echo "[*] $PRG9_ALIAS gestart."

    # GPIO start
    #$PRG_PATH$PRG14 &>/dev/null &
    #eval "$MY_PYTHON $PRG14 2>&1 >/dev/null &"
    $PRG_PATH$PRG14 2>&1 >/dev/null &
    echo "[*] $PRG14 gestart."
 
    # Notifier start
    #$PRG_PATH$PRG20 2>&1 >/dev/null &
    #eval "$MY_PYTHON $PRG20 2>&1 >/dev/null &"
    $PRG_PATH$PRG20 2>&1 >/dev/null &
    echo "[*] $PRG20 gestart."

    # set database rechten
    echo "[*] file rechten database bestanden aanpassen."
    sleep 3
    sudo  /bin/chmod 664 $DB_PATH*.db
    echo "[*] file rechten database bestanden correct gezet."
    echo "[*] start gereed."

}


function process_kill() {
    pids=$( ps -ef | grep $1 | grep -v grep | awk '{ print $2 }' )
    pidslist=$( ps -ef | grep $1 |grep -v grep | awk '{ printf("%d ",$2) }')

    # do a normal kill
    if [ -z "${pids}" ]
    then
        echo "[*] Geen pid gevonden voor proces $1, proces is niet actief."
        return
    else
        echo "[*] Killing pid(s) "$pidslist" proces naam is "$1
        ps -ef | grep $1 | grep -v grep | awk '{ print $2 }' | xargs sudo kill -s SIGINT
    fi

    if [ ! -z "$2" ]
    then
        echo "[*] Wacht "$2" seconden tot "$1" met pid(s) $pidslist gestopt is."
        sleep $2 #wait $2 sec for next test
    fi

    #pids=$( ps -ef | grep $1 | grep -v grep | awk '{ print $2 }' )
    pids=$( ps -ef | grep $1 |grep -v grep | awk '{ printf("%d ",$2) }' )
    if [ -z "${pids}" ]
    then
       return
     else
        # failsave kill
        pids=$( ps -ef | grep $1 | grep -v grep | awk '{ print $2 }' )
        if [ -z "${pids}" ]
        then
            echo "[*] Er lopen geen processen meer met de naam "$1
            echo "[*] --------------------------------------------"
        else
            echo "[*] Failsave kill gestart, dit is niet normaal voor proces "$1
            echo "[*] ------------------------------------------------------------"
            ps -ef | grep $1 | grep -v grep | awk '{ print $2 }' | xargs sudo kill -s SIGKILL
        fi
    fi
}

stop() {

    echo "[*] Processen worden gestopt, even geduld aub."

    # Notifier stop
    process_kill $PRG20 3

    # Serial interface stop
    process_kill $PRG1 3

    # GPIO stop
    process_kill $PRG14 3

    # UDP broadcast stop
    process_kill $PRG8 3

    # Dropbox stop
    process_kill $PRG7 3

    # Udp Sender stop
    process_kill $PRG6 4

    # DB stop
    process_kill $PRG2 12 

    # Watchdog stop
    process_kill $PRG3 2

    # Powerproduction stop
    process_kill $PRG15 4

    # P1WatermeterV2
    process_kill $PRG16 4

    # P1SolarEdge 
    process_kill $PRG17 3

    # MQTT stop
    process_kill $PRG13 3

    # API stop
    process_kill $PRG9_PATH$PRG9 3

    # copy ram to disk
    copytodisk

}

cleardb() {
  echo "[*] wissen van database gestart."
  # database files worden hernoemd en niet gewist als noodmaatregel.
  # in ram zullen ze verdwijnen op disk blijven ze bestaan.
  echo "[*] database files worden hernoemd met .bak extentie"
  # geef de bestaande db bestanden een bak extentie.
  echo "[*] Backup maken van data folder "${DATADISK}
  cd $DATADISK &>/dev/null
  /usr/bin/rename --verbose --force "s/db$/db.bak/g" *
  echo "[*] verwijderen van de ramdisk folder "${RAMDISK} 
  cd $RAMDISK &>/dev/null
  rm --force --verbose *.db
  cd $PRG_PATH &>/dev/null
}

copytodisk(){
     # force all the ram DB to disk
    echo "[*] Ram naar disk copy starten."
    $PRG_PATH$PRG21 --allcopy2disk --forcecopy 2>&1 >/dev/null 
    echo "[*] $PRG21 Ram naar disk copy gereed."

    # schrijf cache naar disk/flash
    sync
    echo "[*] 10 seconden wachttijd, zodat data veilig naar disk wordt gekopierd."
    sleep 10
    echo "[*] stop gereed."
}

case "$1" in
    start)
        start
        exit 0
    ;;
    stop)
        stop
        exit 0
    ;;
    reload|restart|force-reload)
        stop
        sleep 1
        start
        exit 0
    ;;
    cleardatabase)
        stop
        cleardb
        start
        exit 0
    ;;
    **)
        echo "[*] Usage: $0 {start|stop|restart|cleardatabase}" 
        exit 1
    ;;
esac
