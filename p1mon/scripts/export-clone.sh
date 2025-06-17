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
sudo rpi-clone -U -v sda --exclude=/home/p1mon/.cache/*  --exclude=/p1mon/scripts/archief --exclude=/p1mon/www/archief --exclude=/p1mon/www/util/archief --exclude=/p1mon/www/js/archief --exclude=/p1mon/www/css/archief  --exclude=/p1mon/www/font/archief  --exclude=/p1mon/data/*.db* --exclude=/p1mon/dev --exclude=/p1mon/scripts/._*  --exclude=/tmp --exclude=/p1mon/recovery --exclude=/p1mon/var --exclude=/p1mon/dev --exclude=/p1mon/export --exclude=/etc/NetworkManager/system-connections/* --exclude=/etc/resolv.conf --exclude=/etc/letsencrypt/* --exclude=/p1mon/www/json/archief/ --exclude=/p1mon/www/txt/archief/ --exclude=/var/lib/apt/lists/*  --exclude=/var/lib/dpkg/info/* --exclude=/var/cache/apt/*

echo 
if [ $? == 0 ]
then
    echo "[*] data en andere gegevens van de SDA card verwijderen"
    sudo /p1mon/scripts/clean-clone.sh sda
else
    echo "[*] rpi-clone gefaald."
    exit 1
fi

echo "[*] gereed"