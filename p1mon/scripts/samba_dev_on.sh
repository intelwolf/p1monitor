#!/bin/bash
/bin/rm /etc/samba/smb.conf;/bin/ln /etc/samba/smb.conf.dev /etc/samba/smb.conf;/usr/sbin/service smbd restart
