import time

def makeLocalTimeString ( mode='long' ): 
    t = time.localtime()
    if mode == 'long':
        return "%04d-%02d-%02d %02d:%02d:%02d"% ( t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec )
    if mode == 'short':
        return "%04d-%02d-%02d"% (t.tm_year, t.tm_mon, t.tm_mday)
        