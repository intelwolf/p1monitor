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
PRG19="P1UpgradeAide.py"
PRG20="P1Notifier.py"
P1FILE="p1msg.txt"

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
            sleep 1
            echo "timeout is 1 seconden."
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
            echo "sudo killall "$1" wordt uitgevoerd."
            sudo killall $1
        fi
    fi
}

stop() {

    echo "Processen worden gestopt, even geduld aub."

    # Notifier stop
    process_kill $PRG20 2

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
    process_kill $PRG15 1

    # P1WatermeterV2
    process_kill $PRG16 1

    # P1SolarEdge 
    process_kill $PRG17 1

    # MQTT stop
    process_kill $PRG13 1

    

}

stop
