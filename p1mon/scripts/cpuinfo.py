
import string

#CPU info

def getCpuInfo():
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

        model = list(open('/proc/device-tree/model', 'r'))
        clean_str = "".join(filter( lambda x: x in string.printable, model[0] ))
        result['Pi-model'] = clean_str
       
    
    except Exception as e:
            print ("errror="+str(e))
    return result