
import system_info_lib
from Crypto.Hash import SHA256

MAGIC_SEED_ID = 'd6353e4bf18dac180c7c54088f78704c0ecd3a9'

def getSystemId():
    r = MAGIC_SEED_ID + MAGIC_SEED_ID
    try:
        cpu_info = system_info_lib.get_cpu_info()
        r = SHA256.new( cpu_info['Serial'].encode('utf-8') ).hexdigest() + MAGIC_SEED_ID
    except Exception as _e:
        print ( str(_e) )
        pass
    r = ( SHA256.new(r.encode('utf-8')).hexdigest().upper() )
    return '-'.join((r[:4],r[4:8],r[8:12],r[12:16],r[16:20]))


