#!/bin/bash
sudo /bin/rm /etc/samba/smb.conf;sudo /bin/ln /etc/samba/smb.conf.dev /etc/samba/smb.conf;sudo /usr/sbin/service smbd restart
