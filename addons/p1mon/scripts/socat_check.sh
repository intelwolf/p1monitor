#!/bin/bash

service=socat

if (( $(pgrep -x $service | wc -l) == 0 )) 
then
    echo "Service $service stopped"
    #Try to restart the service
    /etc/init.d/$service start
    sleep 1
    #Check if restart was successfully
    if (( $(ps -ef | grep -v grep | grep $service | wc -l) > 0 ))
      then
        echo "Service $service restarted"
      else
        echo "Service $service failed"
      fi
fi
