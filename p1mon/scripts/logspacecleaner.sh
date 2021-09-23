#!/bin/bash
# script om bestanden te wissen.
LOG_PATH="/var/log"
RM_OLDEST_FILE="sudo find $LOG_PATH -type f -printf '%T+ %p\n' | sort | head -n 5 | cut -d ' ' -f 2 | sudo xargs rm --"
PCT_IN_USE_FOR_FOLDER="$(df -Ph $LOG_PATH | tail -1 | awk '{print $5}\'|cut -d'%' -f1)"
MAX_PCT_IN_USE=80

#echo $RM_OLDEST_FILE
#eval $RM_OLDEST_FILE
#eval $PCT_IN_USE_FOR_FOLDER
#echo $PCT_IN_USE_FOR_FOLDER
echo "[*] controleren of er voldoende ruimte is op $LOG_PATH"

if [ $PCT_IN_USE_FOR_FOLDER -gt $MAX_PCT_IN_USE ]
     then
        echo "[*] Folder $LOG_PATH is te vol, oudste files worden verwijderd." 
        echo "[*] Momenteel is de $LOG_PATH voor $PCT_IN_USE_FOR_FOLDER% vol."
        # force log rotate on nginx. # DOS protection.
        echo "[*] NGINX reload."
        systemctl reload nginx 
        eval $RM_OLDEST_FILE
        echo "[*] Na het wissen is $LOG_PATH voor $PCT_IN_USE_FOR_FOLDER% vol."
     else
        echo "[*] Folder $LOG_PATH heeft voldoende ruimte, momenteel voor $PCT_IN_USE_FOR_FOLDER% vol."
fi
