#!/bin/bash

SOURCEPATH="/p1mon /var/log/"
USAGE="gebruik: $0 <id text>"
FILEPREFIX="full-p1monitor-dump"
TMPPATH="/tmp/"
DOWNLOADPATH="/p1mon/www/download/"

export() {
    #echo $1 # dump id

    FILE=$TMPPATH$FILEPREFIX$1".gz"
    EXCLUDE="$DOWNLOADPATH$FILEPREFIX"

    touch $FILE 
    chmod 660 $FILE
    chown p1mon:p1mon $FILE

    tar  --absolute-names --ignore-failed-read --exclude="*.gz" -zcf $FILE $SOURCEPATH

    # mv to www download folder
    mv $FILE $DOWNLOADPATH

    # export file is done. trigger file
    DONEFILE=$DOWNLOADPATH$FILEPREFIX$1".done"
    touch $DONEFILE
    chmod 660 $DONEFILE
    chown p1mon:p1mon $DONEFILE 
    
    # remove files after a while 
    (sleep 7200;rm $DONEFILE && rm $DOWNLOADPATH$FILEPREFIX$1."gz")&
}


if [ -z "$1" ]
then
    echo "Geen ID opgeven!"
    echo $USAGE
    exit 1
fi
export $1
exit 0




