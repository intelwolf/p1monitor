#!/bin/bash

SOURCEPATH="/p1mon /var/log/"
USAGE="gebruik: $0 <id text>"
FILEPREFIX="full-p1monitor-dump"
TMPPATH="/p1mon/var/tmp/"
DOWNLOADPATH="/p1mon/www/download/"

export() {
    #echo $1 # dump id

    FILE=$TMPPATH$FILEPREFIX$1".gz"
    EXCLUDE1="*.gz"
    EXCLUDE2="/p1mon/mnt/ramdisk/*"

    sudo touch $FILE 
    sudo chmod 660 $FILE
    sudo chown p1mon:p1mon $FILE

    CMD="sudo tar --absolute-names --ignore-failed-read --exclude=$EXCLUDE1 --exclude=$EXCLUDE2 -zcf $FILE $SOURCEPATH"
    #echo $CMD
    eval $CMD

    # mv to www download folder
    mv $FILE $DOWNLOADPATH

    # export file is done. trigger file
    DONEFILE=$DOWNLOADPATH$FILEPREFIX$1".done"
    touch $DONEFILE
    sudo chmod 660 $DONEFILE
    sudo chown p1mon:p1mon $DONEFILE 
    
    # remove files after a while 
    CMD="(sleep 7200;rm $DONEFILE;rm $DOWNLOADPATH$FILEPREFIX$1.gz)"
    #echo "$CMD &"
    eval "$CMD &"
}


if [ -z "$1" ]
then
    echo "Geen ID opgeven!"
    echo $USAGE
    exit 1
fi
export $1
exit 0




