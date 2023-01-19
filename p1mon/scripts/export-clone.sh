#!/bin/bash
# script om export naar SDHC card naar SDA te maken.
echo "[*] clean van /var/backups/*.gz"
sudo rm -f /var/backups/*.gz
echo "[*] clean van /var/cache/*"
sudo rm -r /var/cache/*
# wissen van cache en dergelijke.
echo "[*] opschonen oude packages"
# clean is beter dan autoclean.
sudo apt-get clean
sudo apt-get autoremove -y
echo "[*] clean pip cache"
sudo pip cache purge 2>/dev/null
echo "[*] file rechten herstellen"
sudo /p1mon/scripts/setok.sh
echo "[*] clone maken naar SDA extern card"
sudo rpi-clone -U -v sda --exclude=/home/p1mon/.cache/* --exclude=/var/hdd.log --exclude=/var/cache/* --exclude=/var/backups/* --exclude=/p1mon/scripts/archief --exclude=/p1mon/www/archief --exclude=/p1mon/www/util/archief --exclude=/p1mon/www/js/archief --exclude=/p1mon/www/css/archief --exclude=/p1mon/data/*.db* --exclude=/p1mon/dev --exclude=/p1mon/scripts/._*  --exclude=/tmp
echo "[*] data en andere gegevens van de SDA card verwijderen"
sudo /p1mon/scripts/clean-clone.sh sda
echo "[*] gereed"
