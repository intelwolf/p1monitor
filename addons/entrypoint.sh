#!/bin/bash

if [ ! -f /var/tmp/.firstrun ]; then 
	echo Modifying scripts..
	# sudo sed -i "s/^ *network_lib.regenerate/#&/" /p1mon/scripts/P1NetworkConfig.py
	# Remove logspacecleaner
	sed -i "s/sudo \$PRG_PATH\$PRG11/#&/" /p1mon/scripts/p1mon.sh
	sed -i "s/crontab_lib.set_crontab_logcleaner/pass #&/" /p1mon/scripts/P1Watchdog.py
	# remove activate script
	sed -i "s/source bin/#&/" /p1mon/scripts/p1mon.sh
	# remove renice option
	sed -i "s/sudo renice/#&/" /p1mon/scripts/p1mon.sh
	# Modify error output GPIO
	sed -i 's/PRG14 2>\&1 /PRG14 \&/' /p1mon/scripts/p1mon.sh
	# mimic local gunicorn
	mkdir -p /p1mon/p1monenv/bin && touch /p1mon/p1monenv/bin/activate && ln -s /usr/local/bin/gunicorn /p1mon/p1monenv/bin/gunicorn
	if [[ ! -f /sys/class/thermal/thermal_zone0/temp ]]; then 
		echo "Disable CPU temperature check"
	       	sudo sed -i "s/^ *get_cpu_temperature/#&/" /p1mon/scripts/P1Watchdog.py 
	fi
	if [[ ! -z $TZ ]]; then
		sudo ln -fs /usr/share/zoneinfo/$TZ /etc/localtime
		sudo dpkg-reconfigure -f noninteractive tzdata
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
		echo "Setting socat option file"
		echo "OPTIONS=$SOCAT_CONF" | sudo tee /etc/default/socat
		echo '* * * * * /p1mon/scripts/socat_check.sh >> /var/log/socat.log' | sudo crontab - 
	fi
	if [[ ! -z $LOGROTATE ]]; then
		sudo sed -i "s/daily/${LOGROTATE}/" /etc/p1monitor
		sudo mv /etc/p1monitor /etc/logrotate.d
	fi
	if [[ ! -z $CRONTAB ]]; then
		crontab -l | { cat; cat ${CRONTAB}; } |crontab -
	fi
        sudo chown -R p1mon:p1mon /p1mon/mnt /p1mon/data
	touch /var/tmp/.firstrun
fi

echo "Restore file privileges"
sudo chmod g+w /p1mon/mnt/ramdisk /p1mon/data

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
sudo --preserve-env /p1mon/scripts/p1mon.sh start

echo "Setting ramdisk rights"
sudo chown p1mon:p1mon /p1mon/mnt/ramdisk/*db

echo "Writing cron"
/p1mon/scripts/P1Scheduler.py 

# On SIGTERM stop services 
trap "echo SIGTERM received; /p1mon/scripts/p1mon.sh stop && exit 0" SIGTERM

while true; do sleep 1 ; done

exit 0
