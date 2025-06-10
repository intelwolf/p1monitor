#!/usr/bin/python3
import const
import sys
import inspect
import os
import pwd

from sqldb import *
from logger import *
from util import *
from crontab import CronTab

prgname 				= 'P1Scheduler'
ftp_backup_cronlabel	= 'FTPbackup'
config_db				= configDB()
rt_status_db			= rtStatusDb()

def Main(argv): 
	flog.info("Start van programma.")
	flog.info(inspect.stack()[0][3]+": wordt uitgevoerd als user -> "+pwd.getpwuid( os.getuid() ).pw_name)

	# open van status database      
	try:    
		rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
	except Exception as e:
		flog.critical(inspect.stack()[0][3]+": Database niet te openen(1)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]))
		sys.exit(1)
	flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van config database      
	try:
		config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
	except Exception as e:
		flog.critical(inspect.stack()[0][3]+": database niet te openen(2)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]))
		sys.exit(2)
	flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")
	
	try:
		my_cron = CronTab(user='p1mon')
	except Exception as e:
		flog.error(inspect.stack()[0][3]+": crontab kon niet worden gestart, gestopt. Fout="+str(e.args[0]))	
		sys.exit(3)	
	
	#check add or to remove
	_id,do_ftp_backup ,_label = config_db.strget(36,flog)
	_id, do_dbx_backup ,_label = config_db.strget(49,flog)
	
	# do some casting....comparing strings is a pain
	do_ftp_backup = int(do_ftp_backup)
	do_dbx_backup = int(do_dbx_backup)
	if do_ftp_backup == 1 or do_dbx_backup == 1:
		parameter = 1
	else:
		parameter = 0

	if int(parameter) == 0:
		flog.info(inspect.stack()[0][3]+": FTP backup staat uit, crontab wordt gewist")
		deleteJob(my_cron,ftp_backup_cronlabel)
	else:
		_id,parameter,_label = config_db.strget(37,flog)
		flog.info(inspect.stack()[0][3]+": cron parameters uit config database="+parameter)
		parts = parameter.split(':')
		if len(parts) != 5:
			flog.info(inspect.stack()[0][3]+": tijd velden niet correct, gestopt")
			sys.exit(4)
			
		deleteJob(my_cron,ftp_backup_cronlabel)
		try:
			job = my_cron.new(command='/p1mon/scripts/pythonlaunch.sh P1Backup.py >/dev/null 2>&1', comment=ftp_backup_cronlabel)
			#job = my_cron.new(command='/p1mon/scripts/P1Backup.py', comment=ftp_backup_cronlabel)
			job.setall(str(parts[0]), str(parts[1]), str(parts[2]), str(parts[3]), str(parts[4]))
			my_cron.write()
		except Exception as e:
			flog.error(inspect.stack()[0][3]+": FTP crontab kon niet worden ingesteld, gestopt! Fout="+str(e.args[0]) )	
			sys.exit(5)

	flog.info("Programma is succesvol gestopt.")
	sys.exit(0) # all is well.

def deleteJob(cron,job_id):
	try:
		cron.remove_all(comment=ftp_backup_cronlabel)
		cron.write()
	except Exception as _e:
		flog.debug(inspect.stack()[0][3]+": crontab bevat geen commando met het label "+\
		ftp_backup_cronlabel+" geen fout.")	
	
	
#-------------------------------
if __name__ == "__main__":
	try:
		os.umask( 0o002 )
		logfile = const.DIR_FILELOG+prgname+".log" 
		setFile2user(logfile,'p1mon')
		flog = fileLogger(logfile,prgname)    
		#### aanpassen bij productie
		flog.setLevel(logging.INFO)
		flog.consoleOutputOn(True)
	except Exception as e:
		print ( "critical geen logging mogelijke, gestopt.:"+str(e.args[0]) )
		sys.exit(10) #  error: no logging check file rights

	Main(sys.argv[1:])       
