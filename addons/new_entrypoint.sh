#!/bin/bash

# Exit on error for better debugging
set -e

if [ ! -f /var/tmp/.firstrun ]; then
    echo "Modifying scripts.."
    
    # Combine multiple sed operations on same file
    sed -i \
        -e "s/\$PRG_PATH\$PRG18/#&/" \
        -e "s/sudo \$PRG_PATH\$PRG11/#&/" \
        -e "s/source bin/#&/" \
        -e "s/sudo renice/#&/" \
        -e 's/PRG14 2>\&1 /PRG14 \&/' \
        /p1mon/scripts/p1mon.sh
    
    # Single sed for P1Watchdog.py
    sed -i "s/crontab_lib.set_crontab_logcleaner/pass #&/" /p1mon/scripts/P1Watchdog.py
    
    # Check thermal zone
    if [ ! -f /sys/class/thermal/thermal_zone0/temp ]; then
        echo "Disable CPU temperature check"
        sudo sed -i "s/^ *get_cpu_temperature/#&/" /p1mon/scripts/P1Watchdog.py
    fi
    
    # Mimic local gunicorn
    mkdir -p /p1mon/p1monenv/bin
    touch /p1mon/p1monenv/bin/activate
    ln -sf /usr/local/bin/gunicorn /p1mon/p1monenv/bin/gunicorn
    
    # Timezone configuration
    if [ -n "$TZ" ]; then
        sudo ln -sf /usr/share/zoneinfo/$TZ /etc/localtime
        sudo dpkg-reconfigure -f noninteractive tzdata
    fi
    
    # Proxy path configuration
    if [ -n "$PROXYPATH" ]; then
        echo "Setting reverse proxy configurations"
        sudo sed -i 's/PHP_SELF//' /p1mon/www/login.php
        sudo sed -i "s|\$_SERVER\['PH|'/${PROXYPATH}' . &|" /p1mon/www/util/p1mon-password.php
        sudo sed -i 's/"\/api/".\/api/g ; s/"\/fine/".\/fine/g ; s/"\/txt/".\/txt/g ; s/\/main-1/.\/main-1/g' /p1mon/www/*.php
        sudo sed -i 's/"\/api/".\/api/' /p1mon/www/util/*.php
        sudo sed -i "s|PROXY_PATH_REPLACE|${PROXYPATH}|" /etc/nginx/sites-enabled/default
    fi
    
    # Socat configuration
    if [ -n "$SOCAT_CONF" ]; then
        echo "Setting socat option file"
        echo "OPTIONS=$SOCAT_CONF" | sudo tee /etc/default/socat > /dev/null
        echo '* * * * * /p1mon/scripts/socat_check.sh >> /var/log/socat.log' | sudo crontab -
    fi
    
    # Logrotate configuration
    if [ -n "$LOGROTATE" ]; then
        sudo sed -i "s/daily/${LOGROTATE}/" /etc/p1monitor
        sudo mv /etc/p1monitor /etc/logrotate.d/
    fi
    
    # Crontab addition
    if [ -n "$CRONTAB" ]; then
        { crontab -l 2>/dev/null || true; cat "$CRONTAB"; } | crontab -
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
sudo mkdir -p /run/php
sudo /usr/sbin/php-fpm8.2 --fpm-config /etc/php/8.2/fpm/php-fpm.conf

[ -n "$SOCAT_CONF" ] && sudo service socat start

echo "Starting p1mon"
sudo --preserve-env /p1mon/scripts/p1mon.sh start

echo "Setting ramdisk rights"
sudo chown p1mon:p1mon /p1mon/mnt/ramdisk/*db

echo "Writing cron"
/p1mon/scripts/P1Scheduler.py

# On SIGTERM stop services
trap "/p1mon/scripts/p1mon.sh stop; exit 0" SIGTERM

# Keep container running
exec tail -f /dev/null
