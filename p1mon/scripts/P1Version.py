# run manual with ./P1Version

import const
import sys
import argparse
import calendar
import json
import time

OUTPUT_FILE = '/p1mon/var/version.json'


"""
    {
    "MSG_VERSION": 1,
    "TIMESTAMP_LOCAL": "2024-12-28 12:43:55",
    "P1MON_VERSION":   "2.4.3",
    "SERIAL_VERSION":  20241228,
    "VERSION_TEXT":    "December 2024",
    "DOWNLOAD_URL":    "https://www.ztatz.nl/p1-monitor-download-202412-v2-4-3/"
    }
"""


# DATA set
version_dict = {
    "MSG_VERSION":          2,
    "TIMESTAMP_LOCAL":      "YYYY-MM-DD HH:MM:SS",
    "P1MON_VERSION":        const.P1_VERSIE,
    "SERIAL_VERSION":       const.P1_SERIAL_VERSION,
    "VERSION_TEXT":         "",
    "DOWNLOAD_URL":         "",
    "PATCH_VERSION":        const.P1_PATCH_LEVEL,
    "DOWNLOAD_URL_PATCH":   "",
    "COMMENT":              ""
}

def Main(argv): 

    print("Start van programma.")

    parser = argparse.ArgumentParser(description="Create JSON version info.")

    parser.add_argument(
        '-u', '--url', 
        required=False,
        help="url of the main/base image."
        )
    parser.add_argument(
        '-up', '--urlpatch', 
        required=False,
        help="url of the patch."
        )
    parser.add_argument(
        '-c', '--comment', 
        required=False,
        help="url of the patch.",
        nargs='+'
        )   

    args = parser.parse_args()
   
    if args.url == None:
        print("stopped, no download URL given :( ")
        sys.exit(1)
    else:
       version_dict["DOWNLOAD_URL"] = str(args.url)

    if args.urlpatch != None:
       version_dict["DOWNLOAD_URL_PATCH"] = str(args.url)

    if args.comment != None:
         version_dict["COMMENT"] = ' '.join(args.comment)
    
    # general stuff
    t=time.localtime()
    version_dict["TIMESTAMP_LOCAL"] = "%04d-%02d-%02d %02d:%02d:%02d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    version_dict["VERSION_TEXT"] = calendar.month_name[t.tm_mon] + " " + "%04d" %(t.tm_year)

    if int( version_dict["PATCH_VERSION"] ) > 0 and  len(version_dict["DOWNLOAD_URL_PATCH"]) < 4 :
         print ( "warning, the patch level is larger then 0. are you missing the patch url (-up)? " )

    # Serializing json
    json_object = json.dumps(version_dict, indent=4)
 
    # Writing to sample.json
    with open( OUTPUT_FILE, "w" ) as outfile:
        outfile.write( json_object )

    print ("json file " + str( OUTPUT_FILE ) + " is written.")
    print ( json_object )
    print ("done")

#-------------------------------
if __name__ == "__main__":
    Main(sys.argv[1:])        



