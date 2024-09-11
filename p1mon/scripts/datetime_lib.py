####################################################################
# shared lib for time and data base functions util                 #
# some functions need sudo rights                                  #
####################################################################

import datetime

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