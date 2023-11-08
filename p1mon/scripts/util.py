# util/diverse functions
# pytz is een externe lib!
import time
import const
import pytz
import math
import calendar
import os
import grp
import stat
#import commands
import re
import sys
import string
import psutil
import logging
import subprocess
from datetime import datetime, timedelta
from pwd import getpwnam


# the number of seconds from 1970-01-01
def getUtcTime():
    now = datetime.utcnow()
    return int((now - datetime(1970, 1, 1)).total_seconds())

def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

def cleanDigitStr(str_in):
    str_out = re.sub(r'[^-.0-9]', '', str_in)
    #print ('cleanDigitStr = ' + str_out + " str in = " + str_in + " len(str_out)=" + str( len(str_out) ) )
    if len(str_out) == 0:
        return const.NOT_SET
    else:
        #print ('cleanDigitStr(return) = ' + str_out)
        return str_out

def daysPerMonth(date):
    return calendar.monthrange( int(date[0:4]), int(date[5:7]) )[1]

def name2uid(name):
    return getpwnam(name).pw_uid
    
def name2gid(group):
    return grp.getgrnam(group).gr_gid

def setFile2user( filename, username):
    try :
        os.chmod(filename, stat.S_IREAD|stat.S_IWRITE|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH)
        fd = os.open(filename, os.O_RDONLY)
        os.fchown(fd, name2uid(username), name2gid(username))
        os.close(fd)   
    except Exception as _e:
        return False
    return True
        
def fileExist(filename):
    if os.path.isfile(filename):
        return True
    else:
        return False

def file_delta_timestamp( src_file, dst_dir ):
    # geef secs verschil terug van bestanden
    try :
        statinfo_src = os.stat(src_file)
        _head,tail = os.path.split(src_file)
        statinfo_dst = os.stat(dst_dir+"/"+tail)
        return int(abs(statinfo_src.st_mtime - statinfo_dst.st_mtime))   
    except Exception as _e:
        return int(-1)


# haal een maand van de timestring af en geef het
# jaar en maand terug.
def prevYearMonth(timestr):
    month = int(timestr[5:7])
    year = int(timestr[0:4])       
    if month >1:
        month = month-1
    else:
        month = 12
        year = year -1   
    return "%04d-%02d"%(year, month)  

# geeft True terug als in de timestr yyyy-mm-hh dd:mm:ss
# mm = 0,5,15,2 enz = true
def isMod(timestr, mod=5):
    if int(timestr[14:16])%mod == 0:
        return True
    return False

#als een waarde kleiner dan 0 is dan wordt eens string van 0
#terug gegeven
def alwaysPlus(val):
    if val < 0:
        return str('0')
    else:
        return str(val)

#afronden tot drie cijfers achter de comma
def floatX3(f):
    return math.ceil(float(f)*1000)/1000

#is het zomertijd? True = ja False = nee
def is_dst():
    zonename='Europe/Amsterdam'
    tz = pytz.timezone(zonename)
    now = pytz.utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)

# timestring daycheck
# format yyyy-mm-dd hh:mm:ss
# check op[ gebruik doen
def IsNewDay(t1,t2):
    t1 = int(str(t1)[8:10])
    t2 = int(str(t2)[8:10])  
    return abs(t2-t1)

# sec_offset is het aantal seconden extra of minder van UTC/GMT
# NL wintertijd = 3600 zomertijd =7200
def mkLocalTimeString(): 
    t=time.localtime()
    return "%04d-%02d-%02d %02d:%02d:%02d"\
    % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    
def mkLocalTimestamp(): 
    t=time.localtime()
    return "%04d%02d%02d%02d%02d%02d"\
    % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)    
