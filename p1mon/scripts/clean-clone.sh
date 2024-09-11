#!/bin/bash

PGM=`basename $0`

#RSYNC_OPTIONS="--force -rltWDEgopt"

# List of extra dirs to create under /mnt.
OPTIONAL_MNT_DIRS="clone mnt sda sdb rpi0 rpi1"

# Where to mount the disk filesystems to be rsynced.
CLONE=/mnt/clone
CLONE_LOG=/var/log/$PGM.log
P1MON_SCRIPTS=/p1mon/scripts

HOSTNAME=`hostname`

#SRC_BOOT_PARTITION_TYPE=`parted /dev/mmcblk0 -ms p | grep "^1" | cut -f 5 -d:`
SRC_ROOT_PARTITION_TYPE=`parted /dev/mmcblk0 -ms p | grep "^2" | cut -f 5 -d:`

CUR_DIR=$(pwd)

if [ `id -u` != 0 ]
then
    echo -e "$PGM moet als root draaien :(\n"
    exit 1
fi

usage()
    {
    echo ""
    echo "gebruik: $PGM sdN "
    echo "    Example:  $PGM sda"
    echo ""
    exit 0
    }

VERBOSE=off

while [ "$1" ]
do
    case "$1" in
        -h|--help)
            usage
            ;;
        *)
            if [ "$DST_DISK" != "" ]
            then
                echo "Bad args"
                usage
            fi
            DST_DISK=$1
            ;;
    esac
    shift
done


if [ "$DST_DISK" = "" ]
then
    usage
    exit 0
fi

if ! cat /proc/partitions | grep -q $DST_DISK
then
    echo "Disk '$DST_DISK' bestaat niet."
    echo "Doe de SD card into a USB port."
    echo "Als deze niet verschijnt als '$DST_DISK', doe dan:"
    echo -e "'cat /proc/partitions' om te zien waar de disk is.\n"
    exit 0
fi

unmount_or_abort()
    {
    echo -n "Do you want to unmount $1? (yes/no): "
    read resp
    if [ "$resp" = "y" ] || [ "$resp" = "yes" ]
    then
        if ! umount $1
        then
            echo "Sorry, $PGM could not unmount $1."
            echo -e "Aborting!\n"
            exit 0
        fi
    else
        echo -e "Aborting!\n"
        exit 0
    fi
    }

DST_ROOT_PARTITION=/dev/${DST_DISK}2
DST_BOOT_PARTITION=/dev/${DST_DISK}1

# Check that none of the destination partitions are busy (mounted).
#
DST_ROOT_CURMOUNT=`fgrep "$DST_ROOT_PARTITION " /etc/mtab | cut -f 2 -d ' ' `
DST_BOOT_CURMOUNT=`fgrep "$DST_BOOT_PARTITION " /etc/mtab | cut -f 2 -d ' ' `

if [ "$DST_ROOT_CURMOUNT" != "" ] || [ "$DST_BOOT_CURMOUNT" != "" ]
then
    echo "A destination partition is busy (mounted).  Mount status:"
    echo "    $DST_ROOT_PARTITION:  $DST_ROOT_CURMOUNT"
    echo "    $DST_BOOT_PARTITION:  $DST_BOOT_CURMOUNT"
    if [ "$DST_BOOT_CURMOUNT" != "" ]
    then
        unmount_or_abort $DST_BOOT_CURMOUNT
    fi
    if [ "$DST_ROOT_CURMOUNT" != "" ]
    then
        unmount_or_abort $DST_ROOT_CURMOUNT
    fi
fi


TEST_MOUNTED=`fgrep " $CLONE " /etc/mtab | cut -f 1 -d ' ' `
if [ "$TEST_MOUNTED" != "" ]
then
    echo "This script uses $CLONE for mounting filesystems, but"
    echo "$CLONE is already mounted with $TEST_MOUNTED."
    unmount_or_abort $CLONE 
fi


if [ ! -d $CLONE ]
then
    MNT_MOUNT=`fgrep " /mnt " /etc/mtab | cut -f 1 -d ' ' `
    if [ "$MNT_MOUNT" = "" ]
    then
        mkdir $CLONE
    else
        echo "$MNT_MOUNT is currently mounted on /mnt."
        unmount_or_abort /mnt
        mkdir $CLONE
    fi
fi

echo "=> Mounting $DST_ROOT_PARTITION ($DST_ROOT_VOL_NAME) op $CLONE"
if ! mount $DST_ROOT_PARTITION $CLONE
then
    echo -e "Mount fout van $DST_ROOT_PARTITION, aborting!\n"
    exit 0
fi

if [ ! -d $CLONE/boot ]
then
    mkdir $CLONE/boot
fi

echo "=> Mounting $DST_BOOT_PARTITION op $CLONE/boot"
if ! mount $DST_BOOT_PARTITION $CLONE/boot
then
    umount $CLONE
    echo -e "Mount fout van $DST_BOOT_PARTITION, aborting!\n"
    exit 0
fi

echo "==============================="
# function to process files
delete_from_dir(){
    echo "=> verwerken van $ACTIVE_DIR start."
    cd $ACTIVE_DIR 
    PWD=$(pwd)

    #check if we are in a clone path
    if [[ $ACTIVE_DIR != *"/mnt/clone"* ]]; then
        echo "=> verwerken van $ACTIVE_DIR gestopt, geen clone folder."
        return 1
    fi

    if [ "$ACTIVE_DIR" == "$PWD" ]
        then
            for var in "$@"
            do
                #echo "$var"
                if [ -f "$var" ]; then
                   rm -fvr  "$var"
                   #echo "dummy rm ""$var"
                fi
            done
            echo "=> verwerken van $ACTIVE_DIR succes."
        else 
            echo "=> verwerken van $ACTIVE_DIR gefaald."
    fi
    return 0
}


ACTIVE_DIR=$CLONE/etc/nginx/sites-enabled
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR
    PWD=$(pwd)
    delete_from_dir p1mon_80 p1mon_443
fi

################ Lets Encrypt ##################
echo "=> verwijderden van Lets Encrypt configuratie"
ACTIVE_DIR=$CLONE/etc/letsencrypt/archive
cd $ACTIVE_DIR
echo $(pwd)
rm -rfv ./**
ACTIVE_DIR=$CLONE/etc/letsencrypt/csr
cd $ACTIVE_DIR
echo $(pwd)
rm -rfv ./**
ACTIVE_DIR=$CLONE/etc/letsencrypt/keys
cd $ACTIVE_DIR
echo $(pwd)
rm -rfv ./**
ACTIVE_DIR=$CLONE/etc/letsencrypt/live
cd $ACTIVE_DIR
echo $(pwd)
rm -rfv ./**
ACTIVE_DIR=$CLONE/etc/letsencrypt/renewal
cd $ACTIVE_DIR
echo $(pwd)
rm -rfv ./**
ACTIVE_DIR=$CLONE/etc/letsencrypt/accounts/acme-v02.api.letsencrypt.org/directory
cd $ACTIVE_DIR
echo $(pwd)
rm -rfv ./**


ACTIVE_DIR=$CLONE/etc/nginx/conf.d
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR
    PWD=$(pwd)
    delete_from_dir api-tokens.conf
fi

# make default http config file
echo "=> standaard http configuratie wordt aangemaakt."
ACTIVE_DIR=$CLONE/etc/nginx/sites-enabled
/p1mon/scripts/P1NginxConfig --createhttpconfigfile $ACTIVE_DIR/p1mon_80
echo "=> wacht 10 seconden."
sleep 10

DHCPCDFILE=$CLONE/etc/dhcpcd.conf
echo "=> default dhcpcd config file naar clone schrijven : $DHCPCDFILE"
/p1mon/scripts/P1NetworkConfig --defaultdhcpconfig -fp $DHCPCDFILE
echo "=> wacht 10 seconden."
sleep 10

ACTIVE_DIR=$CLONE/p1mon/data
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir *.db *.txt .*Store ._* *.db.bak
fi

ACTIVE_DIR=$CLONE/p1mon/export
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/recovery
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/mnt/ramdisk
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir *.db *.txt .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/log/p1monitor
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/hdd.log/p1monitor
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/hdd.log
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/var/tmp
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/www/font
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/www/font/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/p1mon/www/txt/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/p1mon/www/download
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/www/js
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/www/json
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir .*Store ._*
fi

ACTIVE_DIR=$CLONE/p1mon/www/json/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    cd $CLONE
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/p1mon/www/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    cd $CLONE
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/p1mon/www/util/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    cd $CLONE
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/p1mon/www/css/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    cd $CLONE
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/p1mon/www/js/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    cd $CLONE
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/p1mon/scripts/archief
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
    cd $CLONE
    rm -rf $ACTIVE_DIR
fi

ACTIVE_DIR=$CLONE/root/.ssh
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/root
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR
    PWD=$(pwd)
    delete_from_dir * .*Store .bash_history ._*
fi

ACTIVE_DIR=$CLONE/home/p1mon
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR
    PWD=$(pwd)
    delete_from_dir .*Store .bash_history ._*
fi

ACTIVE_DIR=$CLONE/home/p1mon/.cache
if  [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR
        PWD=$(pwd)
        delete_from_dir *
fi

ACTIVE_DIR=$CLONE/var/cache/samba
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir *.dat .*Store ._* .ssh .Xauthority
fi

ACTIVE_DIR=$CLONE/var/log
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/log/samba
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/log/ngnix
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/log/wicd
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/lib/php5
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/hhd.log
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/hhd.log/p1monitor
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/hhd.log/samba
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/hhd.log/apt
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

ACTIVE_DIR=$CLONE/var/hhd.log/nginx
if [ -d "$ACTIVE_DIR" ]; then
    cd $ACTIVE_DIR 
    PWD=$(pwd)
    delete_from_dir * .*Store ._*
fi

CLOCK_FILE=$CLONE/etc/fake-hwclock.data
echo "=> verwijderden van realtime klok bestand $CLOCK_FILE"
rm  $CLOCK_FILE

CRONTAB_FILE=$CLONE/var/spool/cron/crontabs/p1mon
echo "=> verwijderden van crontab van p1mon $CRONTAB_FILE"
rm $CRONTAB_FILE

WPA_SUPPLICANT_FILE=$CLONE/etc/wpa_supplicant/wpa_supplicant.conf* 
echo "=> verwijderden van wpa_supplicant bestand $WPA_SUPPLICANT_FILE"
rm $WPA_SUPPLICANT_FILE

API_TOKENS_FILE=$CLONE/etc/nginx/conf.d/api-tokens.conf
echo "=> verwijderden van API tokens bestand $API_TOKENS_FILE"
rm $API_TOKENS_FILE

SOCAT_SERVICE_FILE=$CLONE/etc/systemd/system/socat.service
echo "=> verwijderden van socat service bestand $SOCAT_SERVICE_FILE"
rm $SOCAT_SERVICE_FILE

# deze regel zorgt ervoor dat wpa_supplicant start en een reboot niet nodig is om wifi in stellen.
echo "=> leeg wpa_supplicant bestand wegschrijven "
cp $P1MON_SCRIPTS/wpa_supplicant.conf.empty $CLONE/etc/wpa_supplicant/wpa_supplicant.conf
chmod 660 $CLONE/etc/wpa_supplicant/wpa_supplicant.conf
chown root:p1mon $CLONE/etc/wpa_supplicant/wpa_supplicant.conf

DEV_FOLDER=$CLONE/p1mon/dev
echo "=> verwijderden van dev folder: $DEV_FOLDER"
rm  -r $DEV_FOLDER

EDITOR=$CLONE/p1mon
echo "=> verwijderden van editor cache files: $EDITOR"
find $EDITOR -type f -name "._*" -delete 

VARBACKUP=$CLONE/var/backups/*.gz
echo "=> verwijderden van gzip files : $VARBACKUP"
rm -f $VARBACKUP

cd $CUR_DIR
echo "=> unmounting $CLONE/boot"
umount $CLONE/boot

echo "=> unmounting $CLONE"
umount $CLONE

#echo "=> lege ruimte vullen van /boot met 0 om de SDHC image te verkleinen. dit duurt een paar minuten en de fout No space left on device is ok"
#cat /dev/zero > /boot/zero_file
#rm /boot/zero_file
echo "=> lege ruimte vullen van $DST_ROOT_PARTITION met 0 om de SDHC image te verkleinen."
echo $DST_ROOT_PARTITION
zerofree -v $DST_ROOT_PARTITION

echo "==============================="
exit 0
