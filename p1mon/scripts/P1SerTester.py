# run manual with P1SerTester
import sys
import argparse
import time
import serial
import signal
import time

prgname = 'P1SerTester 5.0 (Python 3 version)'

def saveExit(signum, frame):
    global ser1
    ser1.close()   
    signal.signal(signal.SIGINT, original_sigint)
    print("SIGINT ontvangen, gestopt.")
    sys.exit(0)

def Main(argv):
    global ser1
    filename = "/var/log/p1monitor/sertest-" + mkLocalTimeString() + ".txt"
  
    parser = argparse.ArgumentParser(description=" Voorbeeld: P1SerTester.py -br 9600 -bs 7 -p E -s 1 (standaard parameters).") 
    parser.add_argument('-br',      '--baudrate',        required=False, default=9600,    type=int )
    parser.add_argument('-bs',      '--bytesize',        required=False, default=7,       type=int )
    parser.add_argument('-p',       '--parity',          required=False, default="E",              )
    parser.add_argument('-s',       '--stopbits',        required=False, default=1,       type=int )
    parser.add_argument('-d',       '--serialdevice',    required=False, default="/dev/ttyUSB0"    )
    parser.add_argument('-mode1',   '--mode1152008N1',   required=False, action="store_true", help="veel gebruikte P1 poort instelling 115200 8 N 1" )
    parser.add_argument('-mode2',   '--mode11152007E1',  required=False, action="store_true", help="veel gebruikte P1 poort instelling 115200 7 E 1" )

    args = parser.parse_args()

    #Set COM port config
    ser1 = serial.Serial()
    ser1.baudrate   = args.baudrate
    ser1.bytesize   = args.bytesize
    ser1.parity     = args.parity
    ser1.stopbits   = args.stopbits

    if args.mode1152008N1 == True:
        ser1.baudrate    = 115200
        ser1.bytesize    = 8 
        ser1.parity      = "N"
        ser1.stopbits    = 1
    
    if args.mode11152007E1 == True:
        ser1.baudrate    = 115200
        ser1.bytesize    = 7 
        ser1.parity      = "E"
        ser1.stopbits    = 1

    ser1.xonxoff    = 0
    ser1.rtscts     = 0 
    ser1.timeout    = 1
    ser1.port       = args.serialdevice
    
    print( "Waarschuwing, gebruik dit programma niet tegelijk met P1SerReader.py" )
    print( "serial device: "    + str( ser1.port ) )
    print( "baudrate : "        + str( ser1.baudrate ) )
    print( "bytesize : "        + str( ser1.bytesize ) )
    print( "parity : "          + str( ser1.parity ) )
    print( "stopbits : "        + str( ser1.stopbits )  )
    print( "output wordt naar het bestand " + filename + " geschreven.")

    ser1.open()

    fp = open(filename,'w')

    while True:
        
        if ser1.in_waiting > 1:

            try:
                x = mkLocalTimeString() + ": " + ser1.readline().decode('utf-8')
                print ( x )
                fp.write(x)
                fp.flush()
            except Exception as e:
                err = mkLocalTimeString() + ": " + "fout -> " + str(e.args[0])
                print ( err )
                fp.write( err )
                fp.flush()
                time.sleep(1)
        else:
            time.sleep(0.5)
            
    fp.close() 

# sec_offset is het aantal seconden extra of minder van UTC/GMT
# NL wintertijd = 3600 zomertijd =7200
def mkLocalTimeString(): 
    t=time.localtime()
    p1 = "%04d%02d%02d" % (t.tm_year, t.tm_mon, t.tm_mday )
    p2 = "%02d%02d%02d" % (t.tm_hour, t.tm_min, t.tm_sec  )
    return  p1 + p2

#-------------------------------
if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, saveExit)
    Main(sys.argv[1:])