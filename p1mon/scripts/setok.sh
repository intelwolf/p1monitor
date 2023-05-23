#!/bin/bash
# script om bestanden de juiste rechten te geven
echo "[*] Scripts folder aanpassen"
cd /p1mon/scripts 
chmod 754 *.py*;chown p1mon:p1mon *.py*;ls -l *.py*
#chmod 774 p1mon;chown p1mon:p1mon *
chmod 754 *.sh
echo "[*] Bash python start scripts aanpassen"
ls P1*|grep -v py
ls P1*|grep -v py|xargs -n 1 chmod 750
echo "[*] www folders aanpassen."
find /p1mon/www -type d -exec chmod 775 {} +
echo  "[*] www bestanden aanpassen"
find /p1mon/www -type f -exec chmod 664 {} +
find /p1mon/www -type f -exec chown p1mon:p1mon {} +
# dev folder aanpassen
echo  "[*] dev bestanden aanpassen"
find /p1mon/dev -type f -exec chmod 774 {} +
find /p1mon/dev -type d -exec chmod 775 {} +
find /p1mon/dev -type f -exec chown p1mon:p1mon {} +
# databestanden aanpassen
echo  "[*] database bestanden aanpassen"
cd /p1mon/mnt/ramdisk
chmod 664 *.db; chown p1mon:p1mon *.db; ls -l *.db
cd /p1mon/data
chmod 664 *.db; chown p1mon:p1mon *.db; ls -l *.db
echo "[*] dropbox cache aanpassen"
chmod 774 /p1mon/mnt/ramdisk/dbx /p1mon/mnt/ramdisk/dbx/data /p1mon/mnt/ramdisk/dbx/backup
chown p1mon:p1mon /p1mon/mnt/ramdisk/dbx /p1mon/mnt/ramdisk/dbx/data /p1mon/mnt/ramdisk/dbx/backup
#  log aanpassen
echo "[*] export folder aanpassen"
cd /p1mon/export
chmod 770 .;chown p1mon:p1mon .
echo "[*] /var/tmp aanpassen."
chmod 770 /p1mon/var/tmp; chown p1mon:p1mon /p1mon/var/tmp   
# wissen van cache en dergelijke.
echo "[*] opschonen oude packages"
# clean is beter dan autoclean.
apt-get clean 
apt-get autoremove -y
echo "[*] clean van /var/backups/*.gz"
rm -f /var/backups/*.gz
echo "[*] gereed"