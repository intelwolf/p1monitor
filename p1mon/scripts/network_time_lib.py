####################################################################
# shared lib for processing ntp / network time functions           #
####################################################################
import json
import subprocess
import time

SUBPROCESS_TIMEOUT = 5

#############################################
# p1 network time status record             #
#############################################
time_record = {
    'timezone'            : "",    # time zone like Europe/Amsterdam (CET, +0100)
    'ntp_synchronized'    : False, # the ntp time is synced to the system time
    'ntp'                 : False, # is NTP active
    "ntp_server_name"     : "",    # the dns name of the last NTP server used
    "ntp_server_ip"       : "",    # the ip adres of the last NTP server used
    "ntp_last_timestamp"  : "",    # the last succesvol ntp message timestamp
}

class NetworkTimeStatus():

    tr = time_record

    ###########################################
    # return the update time status data      #
    ###########################################
    def status( self ) -> time_record: 
        self.timedatectl_show()
        self.timedatectl_show_timesync()
        return self.tr

    ####################################################
    # returns the json represtation of the status      #
    ####################################################
    def json( self ) :
        return json.dumps( self.tr ) 

    #####################################################
    # run the system command timedatectl show-timesync  #
    # to fetch some of the data                         #
    #####################################################
    def timedatectl_show_timesync( self):

        try :

            cmd_str = "timedatectl show-timesync"
            p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True )
            _stdout=subprocess.PIPE
            (output, _err) = p.communicate()
            _p_status = p.wait( timeout=SUBPROCESS_TIMEOUT )
            #print ( output.decode('utf-8'), _err )
            for item in str(output.decode('utf-8')).split("\n"):

                if item.startswith("ServerName"):
                    sub_item = item.split("=")
                    self.tr['ntp_server_name'] = sub_item[1]
                
                if item.startswith("ServerAddress"):
                    sub_item = item.split("=")
                    self.tr['ntp_server_ip'] = sub_item[1]

                # tricky because of nested message with = in the text
                if item.startswith("NTPMessage"):
                    for sub_item in item.split(","):
                        sub_sub_item = sub_item.split("=")
                        #print ( sub_sub_item )
                        if sub_sub_item[0].strip() == "ReceiveTimestamp":
                            #print ( "ReceiveTimestamp=", sub_sub_item[1] )
                            timestamp = sub_sub_item[1].split(" ")
                            self.tr['ntp_last_timestamp'] = timestamp[1] + " " + timestamp[2] # get onnly date and time

        except Exception as e:
            raise Exception('timedatectl show-timesync error')

    #####################################################
    # run the system command timedatectl show           #
    # to fetch some of the data                         #
    #####################################################
    def timedatectl_show( self):

        try :

            cmd_str = "timedatectl show "
            p = subprocess.Popen( cmd_str, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True )
            _stdout=subprocess.PIPE
            (output, _err) = p.communicate()
            _p_status = p.wait( timeout=SUBPROCESS_TIMEOUT )
            #print ( output.decode('utf-8'), _err )
            for item in str(output.decode('utf-8')).split("\n"):
                sub_item = item.split("=")
                #print ( sub_item )
                if sub_item[0] == "Timezone":
                    self.tr['timezone'] = sub_item[1]
                if sub_item[0] == "NTPSynchronized":
                    if sub_item[1] == "yes":
                        self.tr['ntp_synchronized'] = True
                    else:
                        self.tr['ntp_synchronized'] = False
                if sub_item[0] == "NTP":
                    if sub_item[1] == "yes":
                        self.tr['ntp'] = True
                    else:
                        self.tr['ntp'] = False

        except Exception as e:
            raise Exception('timedatectl show error')






