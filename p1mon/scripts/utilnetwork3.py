
import subprocess

def getNicInfo(nic="eth0"):
    result = {
    "ip4":None, 
    "ip6":None,
    "mac":None,
    "result_ok":True
    }
    cmd_str = "/sbin/ifconfig -a "+nic
    try:
        p = subprocess.Popen(cmd_str,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
        buf = p.stdout.readlines()
        for item in buf: 
            #print ( item )
            value = item.decode('utf-8')
            if value.find('inet ') != -1: # trailing space is important for difference with ip4/ip6
                result['ip4'] = value.split()[1].upper()
            if value.find('inet6') != -1:
                result['ip6'] = item.split()[1].upper().decode('utf-8')
            if value.find('ether') != -1:
                result['mac'] = item.split()[1].upper().decode('utf-8')
    except Exception as _e:
        print ( _e )
        result['result_ok'] = False
    return result