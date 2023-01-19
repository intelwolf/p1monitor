####################################################################
# shared lib for system/os functions                               #
####################################################################
import inspect
import subprocess
import time
import psutil
import platform
import string

####################################################################
# get Rpi CPU information                                          #
####################################################################
def get_cpu_info():
    result = {
    "CPU-cores":'', 
    "CPU-model":'', 
    "CPU-features":'',
    "CPU-implementer":'',
    "CPU-architecture":'',
    "CPU-variant":'',
    "CPU-part":'',
    "CPU-revision":'',
    "Hardware":'',
    "Revision":'',
    "Serial":'',
    "Pi-model":'',
    "Error":''
    }    
    try:
        # get pi type
        core_cnt = 0
        lines = tuple(open('/proc/cpuinfo', 'r'))
        for line in lines:
            #print (line)
            if 'model name' in line:
                result['CPU-model'] = line.split(':')[1].strip() 
            if 'Features' in line:
                result['CPU-features'] = line.split(':')[1].strip()
            if 'CPU implementer' in line:
                result['CPU-implementer'] = line.split(':')[1].strip()
            if 'CPU architecture' in line:
                result['CPU-architecture'] = line.split(':')[1].strip()
            if 'processor' in line:
                core_cnt += 1
                result['CPU-cores'] = str(core_cnt)
            if 'CPU variant' in line:
                result['CPU-variant'] = line.split(':')[1].strip()
            if 'CPU part' in line:
                result['CPU-part'] = line.split(':')[1].strip()
            if 'CPU-revision' in line:
                    result['CPU-revision'] = line.split(':')[1].strip()
            if 'Hardware' in line:
                    result['Hardware'] = line.split(':')[1].strip()
            if 'Revision' in line:
                    result['Revision'] = line.split(':')[1].strip()
            if 'Serial' in line:
                    result['Serial'] = line.split(':')[1].strip()

        #model = list(open('/proc/device-tree/model', 'r'))
        model = {0:'Docker'}
        result['Hardware'] = 'Docker Container'
        result['Revision'] = 'Docker'
        result['Serial'] = '-'
        clean_str = "".join(filter( lambda x: x in string.printable, model[0] ))
        result['Pi-model'] = clean_str

    except Exception as e:
            print ("errror="+str(e))
    return result

####################################################################
# get the python version number like 3.9.2                         #
####################################################################
def get_python_version(): 
    try :
        #print ( platform.python_version() )
        return platform.python_version()
    except Exception:
        return "onbekend"

####################################################################
# get name of the os like Linux-5.15.32-v7l..................      #
####################################################################
def get_os_version():
    try :
        return platform.platform(aliased=0, terse=0)
    except Exception as _e:
        return "onbekend"


####################################################################
# get percentange of ths sdhc card used                            #
####################################################################
def get_disk_pct_used( path ): #180ok
    try:
        r = float(str.replace( str( psutil.disk_usage( path )).split()[3].split('=')[1],')','') ) 
        return str(r)
    except Exception as _e:
        #print ( str(e) )
        return "onbekend."


####################################################################
# get the time passsed since last reboot                           #
####################################################################
def get_system_uptime( flog=None ): #180ok
    #flog.setLevel(logging.DEBUG)
    try:
        proc = subprocess.Popen(['/bin/cat','/proc/uptime'], stdout=subprocess.PIPE)
        tmp = proc.stdout.read().decode('utf-8')
        #secpassed = long(tmp.split()[0].split('.',1)[0])
        secpassed = int(tmp.split()[0].split('.',1)[0])
        #secpassed = secpassed + 180000
        days = int(secpassed/86400)
        flog.debug(inspect.stack()[0][3]+" raw secs ="+str(tmp)+" secs. cleaned="+str(secpassed)+" dagen verstreken="+str(days) )
        timestr = ''
        if days > 1:
            timestr =  str(days)+  " dagen "
        if days == 1:
            timestr =  str(days)+  " dag " 
        timestr = timestr+time.strftime("%H:%M:%S", time.gmtime(secpassed) )
        flog.debug( inspect.stack()[0][3]+" uptime is: "+timestr )
        return timestr
    except Exception as e:
        flog.error(inspect.stack()[0][3]+" geen uptime gevonden? error="+str(e))
        return "onbekend."

####################################################################
# return the cpu temperatrure in centigrade                        #
####################################################################
def get_cpu_temperature( return_as_str=True ):
    tfile = open('/sys/class/thermal/thermal_zone0/temp','r')
    temp = float(tfile.read())
    tfile.close()
    tempC = temp/1000
   # print( tempC )
    if return_as_str:
        return str( tempC )
    else:
        return tempC

####################################################################
# return the amount of ram is in use in pct                        #
####################################################################
def get_ram_used_pct():
    try:
        proc = subprocess.Popen(['/usr/bin/free','-k'], stdout=subprocess.PIPE)
        stdout, stderr  = proc.communicate()
        exit_code = int( proc.wait( timeout=10 ) )
        #print ( stdout )
        if exit_code == 0:
            tmp = stdout.decode('utf-8')
            mem_total  = int( tmp.split('\n')[1].split()[1] )
            mem_used   = int( tmp.split('\n')[1].split()[2] )
            #men_free   = int( tmp.split('\n')[1].split()[3] )
            mem_shared = int( tmp.split('\n')[1].split()[4] )
            #mem_cached = int( tmp.split('\n')[1].split()[5] )
            #print ( "mem_total=",mem_total )
            #print ( "mem_used=",mem_used  )
            #print ( "mem_shared=",mem_shared  )
            r = "{:10.1f}".format( (( mem_used +  mem_shared ) / mem_total ) * 100 ).strip()
            #print ( r )
            return r
        raise ValueError("RAM uitlezen duurde te lang")
    except Exception as e:
        #print( str(e) )
        raise ValueError("RAM info was niet te lezen ->" + str(e) )
