#!/bin/bash
#/home/p1mon/.local/bin/gunicorn -b localhost:10721 --workers 4 P1Api:app --reload
# uitzoeken flags gunicorn
#-D, --daemon
# False
# Daemonize the Gunicorn process.
# restart van service als deze ge-killed wordt.
#
echo "------------------------------"
echo "| Alleen voor ontwikkelwerk! |"
echo "------------------------------"
/home/p1mon/.local/bin/gunicorn --timeout 900 --bind localhost:10721 --worker-tmp-dir /p1mon/mnt/ramdisk --workers 1 P1Api:app --reload 
#/home/p1mon/.local/bin/gunicorn --timeout 900 --bind 0.0.0.0:10721 --worker-tmp-dir /p1mon/mnt/ramdisk --workers 1 P1Api:app --reload 
