#!/bin/bash

service=socat

if (( $(pgrep -x $service | wc -l) == 0 )) 
then
    echo "Service $service stopped"
    #Try to restart the service
    echo "Stop SerReader.."
    pkill -f -e P1SerReader.py
    sleep 1
    echo "Stort $service.."
    /etc/init.d/$service start
    sleep 1
    echo "Start SerReader.."
    /p1mon/scripts/P1SerReader &
    sleep 1
    #Check if restart was successfully
    if (( $(ps -ef | grep -v grep | grep $service | wc -l) > 0 ))
      then
        echo "Service $service restarted"
      else
        echo "Service $service failed"
      fi
fi
