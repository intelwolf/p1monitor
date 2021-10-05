#!/bin/bash

## Fill in name of program here.
PROG="p1mon"
PRG_PATH="/p1mon/scripts/"
PID_PATH="/p1mon/mnt/ramdisk/"
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
USB_LOCK="LCK*ttyUSB0"
PRG1="P1SerReader.py"
PRG2="P1Db.py"
PRG3="P1Watchdog.py"
PRG4="*.log*"
PRG5="P1Weather.py"
PRG6="P1UdpDaemon.py"
PRG7="P1DropBoxDeamon.py"
PRG8="P1UdpBroadcaster.py"
PRG9="gunicorn"
PRG9_PATH="/home/p1mon/.local/bin/"
PRG9_ALIAS="P1Api"
PRG9_PARAMETERS=" --timeout 900 --bind localhost:10721 --worker-tmp-dir /p1mon/mnt/ramdisk --workers 2 P1Api:app --log-level warning"
PRG10="P1UpgradeAssist.py --restore"
PRG11="logspacecleaner.sh"
PRG12="P1Watermeter.py" #//TODO aanpassen
PRG13="P1MQTT.py"
PRG14="P1GPIO.py"
PRG15="P1PowerProductionS0.py"
PRG16="P1WatermeterV2.py"
PRG17="P1SolarEdgeReader.py"
PRG18="P1NetworkConfig.py"
P1FILE="p1msg.txt"


## reset rechten wegens dev werk en kopie acties.
#sudo /bin/chmod 775  $PRG_PATH$PRG8 $PRG_PATH$PRG1 $PRG_PATH$PRG2 $PRG_PATH$PRG3 $PRG_PATH$PRG5 $PRG_PATH$PRG6 $LOG_PATH$PRG4 $PID_PATH$P1FILE  &>/dev/null
#sudo /bin/chown p1mon:p1mon $PRG_PATH$PRG8 $PRG_PATH$PRG1 $PRG_PATH$PRG2 $PRG_PATH$PRG3 $PRG_PATH$PRG5 $PRG_PATH$PRG6 $LOG_PATH$PRG4 $PID_PATH$P1FILE &>/dev/null
cd /p1mon/scripts
sudo chmod 754 P1*.py*;sudo chown p1mon:p1mon P1*.py
sudo chmod 754 *.sh;sudo chown p1mon:p1mon *.sh 
sudo chmod 660 *_lib.py

 # make p1monitor log folder (new from june 2019)
sudo mkdir -p p1monitor $LOG_PATH
sudo /bin/chown p1mon:p1mon $LOG_PATH $WWW_DOWLOAD_PATH $EXPORT_PATH $RAMDISK
sudo /bin/chmod 775 $LOG_PATH 
sudo /bin/chmod 770 $WWW_DOWLOAD_PATH $EXPORT_PATH


# clean log files on any action, also done by the watchdog
# script clean when gets full. Should never happen ;)
sudo $PRG_PATH$PRG11

start() {

    # make sure we have an valid /etc/dhcpcd.conf file
    $PRG_PATH$PRG18 --defaultdhcpconfig
    echo "2 seconden wachttijd"
    sleep 2

    # disable power save van de wifi.
    echo "Wifi power save wordt uitgezet."
    sudo /sbin/iw dev wlan0 set power_save off
    /sbin/iw wlan0 get power_save
    echo "Wifi power save is uitgezet."

    #upgrade assist start
    echo "Upgrade assist wordt gestart."
    $PRG_PATH$PRG10
    # note the watchdog does the import from /p1mon/data 

    # failsave stop of processed that may stil be running
    echo "failsave stop voor dat de processen weer worden gestart."
    stop
    echo "2 seconden wachttijd"
    sleep 2

    # set sticky bit for C program to run als p1mon 
    sudo /bin/chmod +s /p1mon/scripts/p1monExec
    # remove status file als dat bestaat
    sudo /bin/rm $RAMDISK$STATUS_FILE &>/dev/null 
    #sudo nice --adjustment=-15 su -c p1mon $PRG_PATH$PRG1 &>/dev/null &
    sudo nice --adjustment=-15 sudo -i -u p1mon $PRG_PATH$PRG1 &>/dev/null &
    echo "$PRG1 gestart."
    echo "5 seconden wachttijd"
    # tijd zodat de serial db bij het starten gedefragmenteerd kan worden
    sleep 5

    # DB start
    $PRG_PATH$PRG2 &>/dev/null &
    echo "$PRG2 gestart."
    echo "5 seconden wachttijd"
    sleep 5

    # DropBoxDaemon start
    # make folders if not available (thank you -p switch)
    # folder are also made by program.
    sudo /bin/mkdir -p $DBX_ROOT $DBX_ROOT$DBX_DATA $DBX_ROOT$DBX_BACKUP
    sudo find  $DBX_ROOT -type d -exec chmod 774 {} +
    sudo /bin/chmod 774 $DBX_ROOT
    sudo /bin/chown p1mon:p1mon $DBX_ROOT $DBX_ROOT$DBX_DATA $DBX_ROOT$DBX_BACKUP
    $PRG_PATH$PRG7 &>/dev/null &
    echo "$PRG7 gestart."

    # Watchdog start
    $PRG_PATH$PRG3 2>&1 >/dev/null &
    echo "$PRG3 gestart."

    # run weather once to make sure we have the weather database, fixes import issues.
    $PRG_PATH$PRG5 2>&1 >/dev/null & 

    # UDP deamon start
    $PRG_PATH$PRG6 &>/dev/null &
    echo "$PRG6 gestart."

    # UDP broadcast start
    $PRG_PATH$PRG8 &>/dev/null &
    echo "$PRG8 gestart."

    # API start
    $PRG9_PATH$PRG9$PRG9_PARAMETERS 2>&1 >/dev/null &
    echo "$PRG9_ALIAS gestart."

    # MQTT start (done by wachtdog process )
    #$PRG_PATH$PRG13 &>/dev/null &
    #echo "$PRG13 gestart."

    # GPIO start
    $PRG_PATH$PRG14 &>/dev/null &
    echo "$PRG14 gestart."

}

#function is_script_running() {
#    if [ $( ps -ef| grep $1 | grep -v grep | wc -l ) -gt 0 ]
#    then
#      echo " $1 already running"
#      echo "1"
#    else
#      echo " $1 is not running"
#      echo "0"
#    fi
#}

function process_kill() {
    PID=$( pidof -x $1 )
    if [ -z "$PID" ]
    then
        echo "Geen pid gevonden voor proces $1, proces is niet actief."
    else
        echo "Killing pid(s) "$PID" proces naam is "$1
        sudo kill -s SIGINT $PID 1>&2 >/dev/null
        if [ "$2" ]; then
            echo "timeout is "$2" seconden."
            sleep $2
        else
            sleep 3
            echo "timeout is 3 seconden."
        fi

        PID=$( pidof -x $1 )
        if [ -z "$PID" ]
        then
            echo "Er lopen geen processen meer met de naam "$1
            echo "--------------------------------------------"
        else 
            echo "Failsave kill gestart, dit is niet normaal voor proces "$1
            echo "------------------------------------------------------------"
            # reread processes, to make sure we have the right one
            PID=$( pidof -x $1 )
            sudo kill -s SIGINT $PID 1>&2 >/dev/null
            echo "timeout is $2 seconden"
            sleep 1
            if [ -z "$PID" ]; then
                echo "forceer het stoppen van proces "$1
                sudo kill -s SIGTERM $PID 1>&2 >/dev/null
                sleep 1
                sudo killall $1
            fi
        fi
    fi
}

stop() {

    echo "Processen worden gestopt, even geduld aub."

    # Serial interface stop
    process_kill $PRG1

    # GPIO stop
    process_kill $PRG14

    # API stop
    process_kill $PRG9

    # UDP broadcast stop
    process_kill $PRG8

    # Dropbox stop
    process_kill $PRG7

    # Udp Sender stop
    process_kill $PRG6

     # DB stop
    process_kill $PRG2

    # Watchdog stop
    process_kill $PRG3
    
    #######################################################
    # door de watchdog gestarte processen stoppen na het  #
    # stoppen van de watchdog                             #
    #######################################################

    # Powerproduction stop
    process_kill $PRG15 5

    # P1WatermeterV2
    process_kill $PRG16 5

    # P1SolarEdge 
    process_kill $PRG17 5

    # MQTT stop
    process_kill $PRG13 5

}

cleardb() {
  # database files worden hernoemd en niet gewist als noodmaatregel.
  # in ram zullen ze verdwijnen op disk blijven ze bestaan.
  echo  "database files worden hernoemd met .bak extentie"
  # geef de bestaande db bestanden een bak extentie.
  echo "Backup maken van data folder "${DATADISK}
  cd $DATADISK &>/dev/null
  /usr/bin/rename --verbose --force "s/db$/db.bak/g" *
  echo "verwijderen van de ramdisk folder "${RAMDISK} 
  cd $RAMDISK &>/dev/null
  rm --force --verbose *.db
  cd $PRG_PATH &>/dev/null
}

case "$1" in
    start)
		#initScripts # no longer needed
        start
        exit 0
    ;;
    stop)
        stop
        exit 0
    ;;
    reload|restart|force-reload)
        stop
        sleep 5
        start
        exit 0
    ;;
    cleardatabase)
        stop
        echo "wissen van database gestart."
        cleardb
        start
        exit 0
    ;;
    **)
        echo "Usage: $0 {start|stop|restart|cleardatabase}" 
        exit 1
    ;;
esac
