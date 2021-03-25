#!/bin/bash
FILE=$(date "+%Y%m%d%H%M%S.02_temperatuur.db")
#echo $FILE
/bin/cp /p1mon/data/02_temperatuur.db /p1mon/mnt/ramdisk/dbx/backup/$FILE
