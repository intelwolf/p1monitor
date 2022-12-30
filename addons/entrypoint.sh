#!/bin/bash

if [ ! -f /var/tmp/.firstrun ]; then 
	echo Modifying scripts..
	sudo sed -i "s/^ *network_lib.regenerate/#&/" /p1mon/scripts/P1NetworkConfig.py
#	sudo sed -i "s/    DiskRestore()/&\n    setFileFlags()/" /p1mon/scripts/P1Db.py
#	sed -i "s/nice --adjustment=-15 sudo -i -u p1mon //" /p1mon/scripts/p1mon.sh
	# mimic local gunicorn
	mkdir -p /home/p1mon/.local/bin && ln -s /usr/local/bin/gunicorn /home/p1mon/.local/bin/gunicorn
	if [[ ! -f /sys/class/thermal/thermal_zone0/temp ]]; then 
		echo "Disable CPU temperature check"
	       	sudo sed -i "s/^ *getCpuTemp/#&/" /p1mon/scripts/P1Watchdog.py 
	fi
	if [[ ! -z $PROXYPATH ]]; then
		echo "Setting reverse proxy configurations"
		sudo sed -i 's/PHP_SELF//' /p1mon/www/login.php
		sudo sed -i "s|\$_SERVER\['PH|'/${PROXYPATH}' . &|" /p1mon/www/util/p1mon-password.php
		sudo sed -i 's/"\/api/".\/api/ ; s/"\/fine/".\/fine/ ; s/"\/txt/".\/txt/ ; s/\/main-1/.\/main-1/' /p1mon/www/*.php
		sudo sed -i 's/"\/api/".\/api/' /p1mon/www/util/*.php
		sudo sed -i "s|PROXY_PATH_REPLACE|${PROXYPATH}|" /etc/nginx/sites-enabled/default
	fi
	if [[ ! -z $SOCAT_CONF ]]; then
		sudo echo "OPTIONS=$SOCAT_CONF" > /etc/default/socat
		echo '* * * * * /p1mon/scripts/socat_check.sh >> /var/log/socat.log' | sudo crontab - 
	fi
        sudo chown -R p1mon:p1mon /p1mon/mnt /p1mon/data
        sudo chmod g+w /p1mon/mnt/ramdisk /p1mon/data
	touch /var/tmp/.firstrun
fi

echo "Starting cron"
sudo service cron start

echo "Starting nginx"
sudo service nginx start

echo "Starting php-fpm"
sudo mkdir /run/php
sudo /usr/sbin/php-fpm7.4 --fpm-config /etc/php/7.4/fpm/php-fpm.conf

if [[ ! -z $SOCAT_CONF ]]; then
	sudo service socat start
fi

echo "Starting p1mon"
sudo --preserve-env=GPIOZERO_PIN_FACTORY,PIGPIO_ADDR /p1mon/scripts/p1mon.sh start

echo "Setting ramdisk rights"
sudo chown p1mon:p1mon /p1mon/mnt/ramdisk/*db

echo "Writing cron"
/p1mon/scripts/P1Scheduler.py 

# On SIGTERM stop services 
trap "echo SIGTERM received; /p1mon/scripts/p1mon.sh stop && exit 0" SIGTERM

while true; do sleep 1 ; done

exit 0
