#!/bin/bash

USAGE="gebruik: $0 export <id text> | import <bestand>"
WWW_PATH="/p1mon/www/custom"
BACKUP_FILE="/p1mon/var/tmp/custom-www-export-"

export() {
    #echo $1 # export id
    cd $WWW_PATH
    FILE=$BACKUP_FILE$1".gz"
    tar -zcf $FILE .
    if [ $? -ne 0 ]; then
        echo "tar backup is gefaald!"
        exit 1
    fi
    chmod 660 $FILE
    chown p1mon:p1mon $FILE
    # export file is done.
    touch $BACKUP_FILE$1".done"
    chmod 660 $BACKUP_FILE$1".done"
    chown p1mon:p1mon $BACKUP_FILE$1".done"  
}

import() {
    #echo $1 # import filename
    cd $WWW_PATH
    tar -zxf $1 -C $WWW_PATH
    if [ $? -ne 0 ]; then
        echo "tar restore is gefaald!"
        exit 1
    fi
    rm $1
}

case "$1" in
    export)
        if [ -z "$2" ]
        then
            echo "Geen ID opgeven!"
            echo $USAGE
            exit 1
        fi
        export $2
        exit 0
    ;;
    import)
        if [ -z "$2" ]
        then
            echo "Geen import file opgegeven."
            echo $USAGE
            exit 1
        fi
        if [ ! -f "$2" ]; then
            echo "Import file ($2) bestaat niet!"
            exit 1
        fi
        import $2
        exit 0
    ;;
    **)
        echo $USAGE
        exit 1
    ;;
esac


