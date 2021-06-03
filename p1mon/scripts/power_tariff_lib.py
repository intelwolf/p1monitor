####################################################################
# power tariff calculator, tries to determine the power tariff for #
# hour and timestamps. For months and year a percentage of high    #
# and low tariff will be returned.                                 #
# accuracy will differ and holidays are not taken into account.    #
# usage utiltimestamp.get_year_precentages( "2021-04-06 00:00:00") #
####################################################################

import calendar
from  utiltimestamp import  utiltimestamp

days_per_month_list       = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
days_per_month_leap_list  = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
months_per_year_list      = [ 1, 2, 3, 4, 5, 6, 7, 8, 9 ,10, 11, 12 ]
high_tariff_hours_set_1   = [ 7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22 ] # other provinces that Limburg and Brabant.
high_tariff_hours_set_2   = [ 7,8,9,10,11,12,13,14,15,16,17,18,19,20 ]       # provinces Limburg and Brabant.

####################################################################
# get the percentage of high tariff and low tariff for the given   #
# day, month, year and hour. The other days will be set to high    #
# tariff it is improbable that during the low tariff period during #
# the day that power will be generated due to the lack of sunshine #
# during the night. :)                                             #
####################################################################
def get_hour_percentages( timestring , tariff_set=1 ):
    #high_tariff_pct = 1
    try:

        #high_tariff_pct = 0

        ut = utiltimestamp( timestring )

        year =  int(ut.getparts()[0] )
        month = int(ut.getparts()[1] )
        day =   int(ut.getparts()[2] )
        hour =  int(ut.getparts()[3] )
        
        # set the time frame for low tarif
        high_tariff_hours = high_tariff_hours_set_1
        if tariff_set == 2:
            high_tariff_hours = high_tariff_hours_set_2 
        
        if calendar.weekday( year, month, day ) > 4: # weekday are 0 - 4, 5 and 6 are the weekend days Sat,Sun.
            #print("weekend")
            return 0, 1

        #print( "hour processing=", hour )
        for h in high_tariff_hours:
            if int(h) == int(hour):
                #print ( h )
                return 1, 0
        
        return 0, 1

    except Exception as e:
        print( str(e.args[0]) )

    # default is high tariff
    return 1,0
    

####################################################################
# get the percentage of high tariff and low tariff for the given   #
# day, month and year. The other days will be set to high tariff   #
# it is improbable that during the low tariff period during the    #
# day that power will be generated due to the lack of sunshine     #
# during the night. :)                                             #
####################################################################
def get_day_percentages( timestring ):
    high_tariff_pct = 0
    try:
        ut = utiltimestamp( timestring )

        year =  int(ut.getparts()[0] )
        month = int(ut.getparts()[1] )
        day =   int(ut.getparts()[2] )
        high_tariff_pct = 0
        if calendar.weekday( year, month, day ) < 5: # weekday are 0 - 4, 5 and 6 are the weekend days Sat,Sun.
            high_tariff_pct = 1

    except Exception as e:
        print( str(e.args[0]) )

    return high_tariff_pct, round( 1-high_tariff_pct, 4 )  # high_tariff and low tariff 


####################################################################
# get the percentage of high tariff and low tariff for the given   #
# month and year. returns to floats 1 - 0.nnnn                     # 
####################################################################
def get_month_percentages( timestring ):
    high_tariff_pct = 0
    try:
        ut = utiltimestamp( timestring )
    
        year =  int(ut.getparts()[0] )
        month = int(ut.getparts()[1] )

        days_month_list = days_per_month_list
        if calendar.isleap( year ) == True:
            days_month_list = days_per_month_leap_list # set for leap year.

        non_weekend_days = get_non_weekend_days_month( year, month )
        high_tariff_pct = round( non_weekend_days/ days_month_list[month-1], 4 )

    except Exception as e:
        print( str(e.args[0]) )

    return high_tariff_pct, round( 1-high_tariff_pct, 4 )  # high_tariff and low tariff 


####################################################################
# get the percentage of high tariff and low tariff for the given   #
# year. returns to floats 1 - 0.nnnn                               # 
####################################################################
def get_year_percentages( timestring ):
    high_tariff_pct = 0
    try:
        ut = utiltimestamp( timestring )
        year = int(ut.getparts()[0] )
        #year = 2021 #debug
        total_days = 365
        if calendar.isleap( year ) == True:
            total_days = 366
        # get the number of weekend day  
        non_weekend_days = get_non_weekend_days_year( year )
        high_tariff_pct = round( non_weekend_days/total_days, 4 )
    except Exception as e:
        print( str(e.args[0]) )
    #print ( total_days )
    return high_tariff_pct, round( 1-high_tariff_pct, 4 )  # high_tariff and low tariff 


####################################################################
# get the total number of working days Monday to Friday for the    #
# given month.                                                     # 
####################################################################
def get_non_weekend_days_month( year, month ):
    week_days = 0 
    try:

        days_month_list = days_per_month_list
        if calendar.isleap( year ) == True:
            days_month_list = days_per_month_leap_list # set for leap year.

        for d in range( 1, days_month_list[month-1]+1 ):
            #print( d, month, year )
            if calendar.weekday( year, month, d ) < 5: # weekday are 0 - 4, 5 and 6 are the weekend days Sat,Sun.
                week_days += 1
        
    except Exception as e:
        print( str(e.args[0]) )

    return week_days


####################################################################
# get the total number of working days Monday to Friday for the    #
# given year.                                                      # 
####################################################################
def get_non_weekend_days_year( year ):
    week_days = 0 
    try:
        day_list_index = 0
        days_month_list = days_per_month_list
        if calendar.isleap( year ) == True:
            days_month_list = days_per_month_leap_list # set for leap year.
        for m in months_per_year_list:
            for d in range( 1, days_month_list[day_list_index]+1 ):
                #print( d, m, year )
                if calendar.weekday( year, m, d ) < 5: # weekday are 0 - 4, 5 and 6 are the weekend days Sat,Sun.
                    week_days += 1
            day_list_index += 1
    except Exception as e:
        print( str(e.args[0]) )

    return week_days