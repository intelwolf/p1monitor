#!/bin/bash
# script om export naar SDHC card naar SDA te maken.
echo "[*] clean van /var/backups/*.gz"
rm -f /var/backups/*.gz
# wissen van cache en dergelijke.
echo "[*] opschonen oude packages"
# clean is beter dan autoclean.
apt-get clean
apt-get autoremove -y
echo "[*] clean pip cache"
pip cache purge 2>/dev/null
echo "[*] file rechten herstellen"
/p1mon/scripts/setok.sh
echo "[*] clone maken naar SDA extern card"
rpi-clone -v sda
echo "[*] data en andere gegevens van de SDA card verwijderen"
/p1mon/scripts/clean-clone.sh sda
echo "[*] gereed"