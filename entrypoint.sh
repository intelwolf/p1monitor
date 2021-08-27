#!/bin/bash

if [ $DISABLECPUTEMP = true ]; then
   echo "Disable CPU temperature check"
   sed -i "s/^ *getCpuTemp/#&/" /p1mon/scripts/P1Watchdog.py
fi

echo "Starting cron"
service cron start

echo "Starting nginx"
service nginx start
#/usr/sbin/nginx &

echo "Starting php-fpm"
mkdir /run/php
/usr/sbin/php-fpm7.3 --fpm-config /etc/php/7.3/fpm/php-fpm.conf

echo "Starting p1mon"
cd /p1mon/scripts
./p1mon.sh start
chmod 777 /p1mon/mnt/ramdisk
chmod 666 /p1mon/mnt/ramdisk/*
chown -R p1mon:p1mon /p1mon/export /p1mon/var

# On SIGTERM stop services 
trap 'echo "SIGTERM";touch /var/log/p1monitor/shutdown' SIGTERM

# Waiting until p1mon shutdown is requested
while [ ! -e /var/log/p1monitor/shutdown ]
do
   sleep 5
done

echo "Stopping p1mon"
/p1mon/scripts/p1mon.sh stop

exit 0
