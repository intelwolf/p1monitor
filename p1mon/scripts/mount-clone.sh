#!/bin/bash

PGM=`basename $0`

RSYNC_OPTIONS="--force -rltWDEgopt"

# List of extra dirs to create under /mnt.
OPTIONAL_MNT_DIRS="clone mnt sda sdb rpi0 rpi1"

# Where to mount the disk filesystems to be rsynced.
CLONE=/mnt/clone

CLONE_LOG=/var/log/$PGM.log

HOSTNAME=`hostname`

SRC_BOOT_PARTITION_TYPE=`parted /dev/mmcblk0 -ms p | grep "^1" | cut -f 5 -d:`
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
exit 0

