from datetime import datetime
from dateutil.relativedelta import relativedelta

###################################################################
# get a list of date yyyy-mm-dd when the start en end             #
# date range is longer then the range value                       #
# start_date: yyyy-mm-dd                                          #
# end_date: yyyy-mm-dd                                            #
# period, years(y), month(m), days(d)                             #
# repeatdate: True means next date set starts with the end date   #
# of the previous  data set                                       #
# returns list of list with start en end dates                    #
# throws exception ValueError                                     #
# usage:                                                          #
# create_date_list( start_date, end_date, period = 'm', range=n ) #
###################################################################
def create_date_list( start_date, end_date, period = 'm', range=300, repeatdate=False ):

    try:
        
        if start_date > end_date:
            tmp = end_date
            end_date = start_date
            start_date = tmp

        mount_count = diff_months( start_date + " 00:00:00", end_date + " 00:00:00" ) 
        

        # default is months(m)
        range_delta = relativedelta( months = range )
        range_increment = relativedelta( months = 1 )

        if period == 'd':
            range_delta = relativedelta( days = range )
            range_increment = relativedelta( days = 1 )
        if period == 'y':
            range_delta = relativedelta( years = range )
            range_increment = relativedelta( years = 1 )

        date_list = []
        if mount_count > range: 
            dloop_start = datetime.strptime( start_date, '%Y-%m-%d' )
            while True:
                dates_item    = [ dloop_start.strftime('%Y-%m-%d'), '' ]
                dloop_start   = dloop_start + range_delta
                dates_item[1] = dloop_start.strftime('%Y-%m-%d')
                if repeatdate == False:
                    dloop_start   = dloop_start + range_increment # add for the next round

                date_list.append( dates_item )

                if dates_item[1] >= end_date:
                    dates_item[1] = end_date
                    break
                #print ( date_list )
        else: 
            dates_item = [start_date, end_date ]
            date_list.append( dates_item )

        # fix possible order problem for last entry
        #print (  len(date_list)-1 )
        #print( "#", date_list[ len(date_list)-1 ][0] )
        #print( "#", date_list[ len(date_list)-1 ][1] )
        if date_list[ len(date_list)-1 ][0] > date_list[ len(date_list)-1 ][1]:
            d1 = datetime.strptime( date_list[ len(date_list)-1 ][0], '%Y-%m-%d' )
            d1 = d1 - range_increment
            #print ( d1 )
            date_list[ len(date_list)-1 ][0] = d1.strftime('%Y-%m-%d')
        
        return date_list

    except ValueError:
        raise ValueError("Are the timestamps the right format? ")

###########################################################
# get the nummer of years between two timestamps          #
# strings in the format yyyy-mm-dd hh:mm:ss.              #
# returns an int with the nummer of complete years        #
# throws exception ValueError                             #
# usage:                                                  #
# diff_year("2017-01-01 00:00:00","2017-01-01 00:00:00")  #
###########################################################
def diff_years( timestamp_start, timestamp_end ):
    try:

        d1 = datetime.strptime( timestamp_start, '%Y-%m-%d %H:%M:%S' )
        d2 = datetime.strptime( timestamp_end,   '%Y-%m-%d %H:%M:%S' )
        
        months = abs( (d1.year - d2.year) * 12 + d1.month - d2.month )
        if months < 13:
            return 0 # < then 1 year
        month_years = months - (months % 12) # get the years in months
        return abs(int(month_years / 12) )   # return the complete set of years minus the rest months

    except ValueError:
        raise ValueError("Are the timestamps the right format? ")


###########################################################
# get the nummer of months between two timestamps         #
# strings in the format yyyy-mm-dd hh:mm:ss.              #
# returns an int with the nummer of months                #
# throws exception ValueError                             #
# usage:                                                  #
# diff_month("2017-01-01 00:00:00","2017-01-01 00:00:00") #
###########################################################
def diff_months( timestamp_start, timestamp_end ):
    try:

        d1 = datetime.strptime( timestamp_start, '%Y-%m-%d %H:%M:%S' )
        d2 = datetime.strptime( timestamp_end,   '%Y-%m-%d %H:%M:%S' )
        return abs( int( (d1.year - d2.year) * 12 + d1.month - d2.month ) )
    except ValueError:
        raise ValueError("Are the timestamps the right format?")

###########################################################
# get the nummer of days between two timestamps           #
# strings in the format yyyy-mm-dd hh:mm:ss.              #
# returns an int with the nummer of days                  #
# throws exception ValueError                             #
# usage:                                                  #
# diff_days("2017-01-01 00:00:00","2017-01-01 00:00:00")  #
###########################################################
def diff_days( timestamp_start, timestamp_end ):
    try:
        d1 = datetime.strptime( timestamp_start, '%Y-%m-%d %H:%M:%S' )
        d2 = datetime.strptime( timestamp_end,   '%Y-%m-%d %H:%M:%S' )
        delta = d1 - d2 
        return abs( int(delta.days) )
    except ValueError:
        raise ValueError("Are the timestamps the right format? ")


###########################################################
# get the nummer of hours between two timestamps          #
# strings in the format yyyy-mm-dd hh:mm:ss.              #
# returns an int with the nummer of hours                 #
# throws exception ValueError                             #
# usage:                                                  #
# diff_hours("2017-01-01 00:00:00","2017-01-01 00:00:00") #
###########################################################
def diff_hours( timestamp_start, timestamp_end ):
    try:
        # get the days to convert to hours
        d1 = datetime.strptime( timestamp_start[0:10], '%Y-%m-%d' )
        d2 = datetime.strptime( timestamp_end[0:10],   '%Y-%m-%d' )
        delta = d1 - d2 
        delta_hours_by_days = abs( delta.days * 24)
       
        # get the remaining time to convert the seconds to hours
        d1 = datetime.strptime( timestamp_start[11:19], '%H:%M:%S' )
        d2 = datetime.strptime( timestamp_end[11:19],   '%H:%M:%S' )
        if d1 < d2:
            delta_days = d2 - d1 
        else:
            delta_days = d1 - d2 
        delta_hours_by_remaining_seconds = abs( int( delta_days.seconds/3600) )
       
        # sum the parts 
        total_hours = delta_hours_by_days + delta_hours_by_remaining_seconds
        return total_hours

    except ValueError:
        raise ValueError("Are the timestamps the right format? ")