#!/bin/bash
PYTHONENV="/p1mon/p1monenv"
LOGFILE="/var/log/p1monitor/pythonlaunch.log"


function info_logger()
{
    #echo "$( date "+%Y-%m-%d %H:%M:%S,00" ) $@" >> $LOGFILE
    echo "$( date "+%Y-%m-%d %H:%M:%S,000 - pythonlaunch - INFO -" ) $@" >> $LOGFILE
}

function error_logger()
{
    #echo "$( date "+%Y-%m-%d %H:%M:%S,00" ) $@" >> $LOGFILE
    echo "$( date "+%Y-%m-%d %H:%M:%S,000 - pythonlaunch - ERROR -" ) $@" >> $LOGFILE
}


if [ -z "$1" ]
  then
    text="Geen programma naam opgegeven: gebruik <programma naam in de folder /p1mon/scripts >"
    echo $text
    error_logger $text
    exit 1
fi

cd /p1mon/scripts

if [ ! -f "$1" ]; then
    text="$1 niet gevonden."
    echo $text
    error_logger $text
    exit 1
fi

cd $PYTHONENV
source bin/activate

cd /p1mon/scripts

#echo "parmeters = "$@
eval "python3 $@ &" # @ is all the parameters we got on the command line
#echo pid=$!

#sleep 1
runpid=$( ps -eo pid | grep $! )
#echo $runpid

PRG_LOWER=$( echo "$1" | tr '[:upper:]' '[:lower:]' ) # lower case the prg name zo Crypto and crypto works.

# before production change $@ for $1
if [ -z "$runpid" ]
then
    text="$@ uitvoeren is gefaald."
    if [[ $PRG_LOWER == *"crypto"* ]]; then # don't log crypto stuff crypto stuff details
         text="$1 uitvoeren is gefaald."
    else 
         text="$@ uitvoeren is gefaald."
    fi
    error_logger $text
    exit 1
else
    if [[ $PRG_LOWER == *"crypto"* ]]; then # don't log crypto stuff details
        text="$1 uitvoeren is succesvol."
    else 
         text="$@ uitvoeren is succesvol."
    fi
    info_logger $text
    exit 0
fi
