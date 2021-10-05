#!/bin/bash

if [ ! -f /var/tmp/.firstrun ]; then 
	echo Modifying scripts..
	sed -i "s/^ *network_lib.regenerate/#&/" /p1mon/scripts/P1NetworkConfig.py
	sed -i "s/sudo nice --adjustment=-15 sudo -i -u p1mon //" /p1mon/scripts/p1mon.sh
	# mimic local gunicorn
	mkdir -p /home/p1mon/.local/bin && ln -s /usr/local/bin/gunicorn /home/p1mon/.local/bin/gunicorn
	if [[ $DISABLECPUTEMP = true ]]; then 
		echo "Disable CPU temperature check"
	       	sed -i "s/^ *getCpuTemp/#&/" /p1mon/scripts/P1Watchdog.py 
	fi
	if [[ ! -z $PROXYPATH ]]; then
		echo "Setting reverse proxy configurations"
		sed -i 's/PHP_SELF//' /p1mon/www/login.php
		sed -i "s|\$_SERVER\['PH|'/${PROXYPATH}' . &|" /p1mon/www/util/p1mon-password.php
		sed -i 's/"\/api/".\/api/ ; s/"\/fine/".\/fine/ ; s/"\/txt/".\/txt/ ; s/\/main-1/.\/main-1/' /p1mon/www/*.php
		sed -i 's/"\/api/".\/api/' /p1mon/www/util/*.php
		sed -i "s|PROXY_PATH_REPLACE|${PROXYPATH}|" /etc/nginx/sites-enabled/default
	fi
	touch /var/tmp/.firstrun
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

# dropbox auth
chmod +r /p1mon/scripts/dropbox_lib.py

chmod 777 /p1mon/mnt/ramdisk
chmod 666 /p1mon/mnt/ramdisk/*
chown -R p1mon:p1mon /p1mon/export /p1mon/var 

echo "Writing cron"
/p1mon/scripts/P1Scheduler.py 

# On SIGTERM stop services 
trap 'echo "SIGTERM";touch /var/log/p1monitor/shutdown' SIGTERM

# Waiting until p1mon shutdown is requested
while [[ ! -e /var/log/p1monitor/shutdown ]]
do
   sleep 5
done

echo "Stopping p1mon"
/p1mon/scripts/p1mon.sh stop

exit 0
