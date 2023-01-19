#!/bin/bash
###################################################################
# Erease the oldest files from LOG_PATH until percent used drops  #
# below the MAX_PCT_IN_USE. Files will be ereased in sets         #
# of FILES_ERASE_COUNT with a maximun of LOOP_COUNT rounds        #
# max files ereased on a run is FILES_ERASE_COUNT * LOOP_COUNT    #
###################################################################
LOG_PATH="/var/log"
LOOP_COUNT=10
MAX_PCT_IN_USE=70
FILES_ERASE_COUNT=3

# functions
pct_in_use() {
    local r=$(df -Ph $LOG_PATH | tail -1 | awk '{print $5}\'|cut -d'%' -f1)
    echo "$r"
}

# number of files
get_list_of_oldest_files() { 
    local r=$(sudo find $LOG_PATH -type f -printf '%T+ %p\n' | sort | head -n $FILES_ERASE_COUNT | cut -d ' ' -f 2 )
    echo "$r"
}

echo "[*] controleren of er voldoende ruimte is op $LOG_PATH"

for (( j=0; j<$LOOP_COUNT; j++ ));
    do
        result=$(pct_in_use)
        if [ $result -gt $MAX_PCT_IN_USE ]
        then
            echo "[*] Folder $LOG_PATH heeft onvoldoende ruimte, momenteel voor $result% vol."
            echo "[*] NGINX reload."
            sudo systemctl reload nginx
            file_list=$(get_list_of_oldest_files)
            echo "[*] files worden gewist "$file_list
            sudo rm $file_list
            
        else
            echo "[*] Folder $LOG_PATH heeft voldoende ruimte, momenteel voor $result% vol."
            break # leave the loop when percentage dropsm below MAX_PCT_IN_USE
        fi
    done

echo "[*] gereed."

exit 0
