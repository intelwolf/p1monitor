####################################################################
# shared lib for time function                                     #
####################################################################
import const
import datetime
import inspect
import time
import json
import urllib.request

#####################################################
# returns the seconds past from the epoc            #
# Thursday 1 January 1970 00:00:00                  #
# integer drops the micro seconds                   #
#####################################################
def utc_time(integer=False):

    dt = datetime.datetime.now(datetime.timezone.utc) 
    utc_epic_seconds_passed = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    if integer == True:
        return int(utc_epic_seconds_passed)
    return utc_epic_seconds_passed


#####################################################
# return the str timestamp and UTC seconds from the #
# OS                                                #
#####################################################
def get_os_timestamp(flog=None):

    try :

        dt = datetime.datetime.now( datetime.timezone.utc )
        utc_time = dt.replace( tzinfo=datetime.timezone.utc )
        datetime_utc = int( utc_time.timestamp() ) 

        t=time.localtime()
        datetime_str = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

    except Exception as e:
        if ( flog != None ):
            flog.error(inspect.stack()[0][3]+": URL error " +str(e) )
        raise Exception("get_os_timestamp() error.") 

    return datetime_str, datetime_utc

#####################################################
# return the str timestamp and UTC seconds from the #
# internet                                          #
#####################################################
def get_inet_timestamp(flog=None):
    try:
        url = const.INTERNET_TIME_URL
        if ( flog != None ):
            flog.debug(inspect.stack()[0][3]+": API URL "+url)
        output = json.loads( urllib.request.urlopen(url).read().decode('utf-8') )

        datetime_str = output['dateTime'][:19].replace("T"," ")

        date_object = datetime.datetime.strptime( datetime_str, "%Y-%m-%d %H:%M:%S" )
        datetime_utc = int(datetime.datetime.timestamp(date_object))

        flog.debug(inspect.stack()[0][3]+": API output "+ str(output))
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": URL error " + str(e) )
        raise Exception("get_inet_timestamp() error.") 
    
    return datetime_str, datetime_utc 