####################################################################
# shared lib for system/os functions                               #
####################################################################
import subprocess

####################################################################
# return the amoutn of ram is in use in pct                        #
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

