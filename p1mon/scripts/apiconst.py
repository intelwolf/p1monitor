#constants 
# Versie 0.1 27-12-2018 eerste versie
# versie 1.0 30-11-2019 watermeter toegevoegd
# versie 1.1 13-01-2021 powerproduction aanpassingen en watermeter API aanpassingen.

# routing
ROUTE_CATALOG         = '/api/v1/catalog'
ROUTE_CATALOG_HELP    = ROUTE_CATALOG + '/help'

ROUTE_SMARTMETER      = '/api/v1/smartmeter'
ROUTE_SMARTMETER_HELP = ROUTE_SMARTMETER + '/help'

ROUTE_PHASE          = '/api/v1/phase'
ROUTE_PHASE_HELP     = ROUTE_PHASE + '/help'

ROUTE_PHASE_MINMAX_DAY      = '/api/v1/phaseminmax/day'
ROUTE_PHASE_MINMAX_DAY_HELP = ROUTE_PHASE_MINMAX_DAY  + '/help'

ROUTE_P1_PORT_TELEGRAM      = '/api/v1/p1port/telegram'
ROUTE_P1_PORT_TELEGRAM_HELP = ROUTE_P1_PORT_TELEGRAM  + '/help'

ROUTE_STATUS         = '/api/v1/status'
ROUTE_STATUS_HELP    = ROUTE_STATUS    + '/help'
ROUTE_STATUS_ID      = ROUTE_STATUS    + '/{id}'
ROUTE_STATUS_ID_HELP = ROUTE_STATUS_ID + '/help'

ROUTE_CONFIG         = '/api/v1/configuration'
ROUTE_CONFIG_HELP    = ROUTE_CONFIG    + '/help'
ROUTE_CONFIG_ID      = ROUTE_CONFIG    + '/{id}'
ROUTE_CONFIG_ID_HELP = ROUTE_CONFIG_ID + '/help'

BASE_FINANCIAL            = 'financial' # don't use in path in the code
ROUTE_FINANCIAL_DAY       = '/api/v1/financial/day'
ROUTE_FINANCIAL_DAY_HELP  = ROUTE_FINANCIAL_DAY + '/help'

ROUTE_FINANCIAL_MONTH      = '/api/v1/financial/month'
ROUTE_FINANCIAL_MONTH_HELP = ROUTE_FINANCIAL_MONTH + '/help'

ROUTE_FINANCIAL_YEAR      = '/api/v1/financial/year'
ROUTE_FINANCIAL_YEAR_HELP = ROUTE_FINANCIAL_YEAR + '/help'

ROUTE_FINANCIAL_DYNAMIC_TARIFF      = '/api/v1/financial/dynamic_tariff'
ROUTE_FINANCIAL_DYNAMIC_TARIFF_HELP = ROUTE_FINANCIAL_DYNAMIC_TARIFF + '/help'

BASE_POWER_GAS           = 'powergas' # don't use in path in the code
ROUTE_POWER_GAS_MIN      = '/api/v1/powergas/minute'
ROUTE_POWER_GAS_MIN_HELP = ROUTE_POWER_GAS_MIN + '/help'

ROUTE_POWER_GAS_HOUR      = '/api/v1/powergas/hour'
ROUTE_POWER_GAS_HOUR_HELP = ROUTE_POWER_GAS_HOUR + '/help'

ROUTE_POWER_GAS_DAY      = '/api/v1/powergas/day'
ROUTE_POWER_GAS_DAY_HELP = ROUTE_POWER_GAS_DAY + '/help'

ROUTE_POWER_GAS_MONTH      = '/api/v1/powergas/month'
ROUTE_POWER_GAS_MONTH_HELP = ROUTE_POWER_GAS_MONTH + '/help'

ROUTE_POWER_GAS_YEAR       = '/api/v1/powergas/year'
ROUTE_POWER_GAS_YEAR_HELP  = ROUTE_POWER_GAS_YEAR + '/help'

ROUTE_WEATHER_HOUR          = '/api/v1/weather/hour'
ROUTE_WEATHER_HOUR_HELP     = ROUTE_WEATHER_HOUR + '/help'

ROUTE_WEATHER_DAY           = '/api/v1/weather/day'
ROUTE_WEATHER_DAY_HELP      = ROUTE_WEATHER_DAY + '/help'

ROUTE_WEATHER_MONTH         = '/api/v1/weather/month'
ROUTE_WEATHER_MONTH_HELP    = ROUTE_WEATHER_MONTH + '/help'

ROUTE_WEATHER_YEAR          = '/api/v1/weather/year'
ROUTE_WEATHER_YEAR_HELP     = ROUTE_WEATHER_YEAR + '/help'

ROUTE_WEATHER_CURRENT       = '/api/v1/weather'
ROUTE_WEATHER_CURRENT_HELP  = ROUTE_WEATHER_CURRENT + '/help'

BASE_INDOOR                         = 'indoor/temperature' # don't use in path in the code
ROUTE_INDOOR_TEMPERATURE            = '/api/v1/indoor/temperature'
ROUTE_INDOOR_TEMPERATURE_HELP       = ROUTE_INDOOR_TEMPERATURE + '/help'

ROUTE_INDOOR_TEMPERATURE_MIN        = '/api/v1/indoor/temperature/minute'
ROUTE_INDOOR_TEMPERATURE_MIN_HELP   = ROUTE_INDOOR_TEMPERATURE_MIN + '/help'

ROUTE_INDOOR_TEMPERATURE_HOUR       = '/api/v1/indoor/temperature/hour'
ROUTE_INDOOR_TEMPERATURE_HOUR_HELP  = ROUTE_INDOOR_TEMPERATURE_HOUR + '/help'

ROUTE_INDOOR_TEMPERATURE_DAY        = '/api/v1/indoor/temperature/day'
ROUTE_INDOOR_TEMPERATURE_DAY_HELP   = ROUTE_INDOOR_TEMPERATURE_DAY + '/help'

ROUTE_INDOOR_TEMPERATURE_MONTH      = '/api/v1/indoor/temperature/month'
ROUTE_INDOOR_TEMPERATURE_MONTH_HELP = ROUTE_INDOOR_TEMPERATURE_MONTH + '/help'

ROUTE_INDOOR_TEMPERATURE_YEAR       = '/api/v1/indoor/temperature/year'
ROUTE_INDOOR_TEMPERATURE_YEAR_HELP  = ROUTE_INDOOR_TEMPERATURE_YEAR + '/help'

"""
#BASE_WATERMETER                     = 'watermeter' # don't use in path in the code
#ROUTE_WATERMETER_MIN                = '/api/v1/watermeter/min'
#ROUTE_WATERMETER_MIN_HELP           = ROUTE_WATERMETER_MIN + '/help'

#ROUTE_WATERMETER_HOUR               = '/api/v1/watermeter/hour'
#ROUTE_WATERMETER_HOUR_HELP          = ROUTE_WATERMETER_HOUR + '/help'

#ROUTE_WATERMETER_DAY                 = '/api/v1/watermeter/day'
#ROUTE_WATERMETER_DAY_HELP           = ROUTE_WATERMETER_DAY + '/help'

#ROUTE_WATERMETER_MONTH              = '/api/v1/watermeter/month'
#ROUTE_WATERMETER_MONTH_HELP         = ROUTE_WATERMETER_MONTH + '/help'

#ROUTE_WATERMETER_YEAR               = '/api/v1/watermeter/year'
#ROUTE_WATERMETER_YEAR_HELP          = ROUTE_WATERMETER_YEAR + '/help'
"""

BASE_WATERMETER                     = 'watermeter' # don't use in path in the code
ROUTE_WATERMETER_MIN_V2             = '/api/v2/watermeter/minute'
ROUTE_WATERMETER_MIN_HELP_V2        = ROUTE_WATERMETER_MIN_V2 + '/help'

ROUTE_WATERMETER_HOUR_V2            = '/api/v2/watermeter/hour'
ROUTE_WATERMETER_HOUR_HELP_V2       = ROUTE_WATERMETER_HOUR_V2 + '/help'

ROUTE_WATERMETER_DAY_V2             = '/api/v2/watermeter/day'
ROUTE_WATERMETER_DAY_HELP_V2        = ROUTE_WATERMETER_DAY_V2 + '/help'

ROUTE_WATERMETER_MONTH_V2           = '/api/v2/watermeter/month'
ROUTE_WATERMETER_MONTH_HELP_V2      = ROUTE_WATERMETER_MONTH_V2 + '/help'

ROUTE_WATERMETER_YEAR_V2            = '/api/v2/watermeter/year'
ROUTE_WATERMETER_YEAR_HELP_V2       = ROUTE_WATERMETER_YEAR_V2 + '/help'

BASE_POWERPRODUCTION_S0             = 'powerproduction' # don't use in path in the code
ROUTE_POWERPRODUCTION_S0_MIN        = '/api/v1/powerproduction/minute'
ROUTE_POWERPRODUCTION_S0_MIN_HELP   = ROUTE_POWERPRODUCTION_S0_MIN + '/help'

ROUTE_POWERPRODUCTION_S0_HOUR       = '/api/v1/powerproduction/hour'
ROUTE_POWERPRODUCTION_S0_HOUR_HELP       = ROUTE_POWERPRODUCTION_S0_HOUR + '/help'

ROUTE_POWERPRODUCTION_S0_DAY        = '/api/v1/powerproduction/day'
ROUTE_POWERPRODUCTION_S0_DAY_HELP   = ROUTE_POWERPRODUCTION_S0_DAY + '/help'

ROUTE_POWERPRODUCTION_S0_MONTH      = '/api/v1/powerproduction/month'
ROUTE_POWERPRODUCTION_S0_MONTH_HELP = ROUTE_POWERPRODUCTION_S0_MONTH + '/help'

ROUTE_POWERPRODUCTION_S0_YEAR       = '/api/v1/powerproduction/year'
ROUTE_POWERPRODUCTION_S0_YEAR_HELP  = ROUTE_POWERPRODUCTION_S0_YEAR + '/help'

BASE_POWERPRODUCTION_SOLAR          = 'powerproductionsolar' # don't use in path in the code
ROUTE_POWERPRODUCTION_SOLAR_MIN      = '/api/v1/powerproductionsolar/minute/{power_source_id}/{db_index}'
ROUTE_POWERPRODUCTION_SOLAR_MIN_HELP = '/api/v1/powerproductionsolar/minute/help'

ROUTE_POWERPRODUCTION_SOLAR_HOUR     = '/api/v1/powerproductionsolar/hour/{power_source_id}/{db_index}'
ROUTE_POWERPRODUCTION_SOLAR_HOUR_HELP = '/api/v1/powerproductionsolar/hour/help'

ROUTE_POWERPRODUCTION_SOLAR_DAY      = '/api/v1/powerproductionsolar/day/{power_source_id}/{db_index}'
ROUTE_POWERPRODUCTION_SOLAR_DAY_HELP = '/api/v1/powerproductionsolar/day/help'

ROUTE_POWERPRODUCTION_SOLAR_MONTH    = '/api/v1/powerproductionsolar/month/{power_source_id}/{db_index}'
ROUTE_POWERPRODUCTION_SOLAR_MONTH_HELP = '/api/v1/powerproductionsolar/month/help'

ROUTE_POWERPRODUCTION_SOLAR_YEAR     = '/api/v1/powerproductionsolar/year/{power_source_id}/{db_index}'
ROUTE_POWERPRODUCTION_SOLAR_YEAR_HELP = '/api/v1/powerproductionsolar/year/help'

#JSON fields MATCH JSON_xx and EXPL_xxx
JSON_TS_LCL                 = 'TIMESTAMP_lOCAL'                      # local time in format yyyy-mm-dd hh:mm:ss mkLocalTimeString()
JSON_TS_LCL_UTC             = 'TIMESTAMP_UTC'                        # utc timestamp getUtcTime()
JSON_API_API_STTS           = 'API_STATUS'                           # options are production=ok, test, deprecated = will be removed in future version.
JSON_API_VRSN               = 'API_VERSION'                          # id / number will be used in file name.
JSON_API_CNSMPTN_KWH_L      = 'CONSUMPTION_KWH_LOW'                  # consumption of KWH during low (dal) period. (181)
JSON_API_CNSMPTN_KWH_H      = 'CONSUMPTION_KWH_HIGH'                 # consumption of KWH during high (piek) period. (182)
JSON_API_PRDCTN_KWH_L       = 'PRODUCTION_KWH_LOW'                   # production of KWH during low (dal) period. (281)
JSON_API_PRDCTN_KWH_H       = 'PRODUCTION_KWH_HIGH'                  # production of KWH during high (piek) period. (282)
JSON_API_TRFCD              = 'TARIFCODE'                            # peak or low period.
JSON_API_CNSMPTN_KW         = 'CONSUMPTION_KW'                       # the consumption in kilo Watt at this moment.
JSON_API_PRDCTN_KW          = 'PRODUCTION_KW'                        # the production in kilo Watt at this moment.
JSON_API_VALID_DATA         = 'VALID_DATA'                           # used to flag the data good/complete enough to process.
JSON_API_FQDN               = 'API_FQDN'                             # Fully Qualified Domain Name for the remote inet access to the API
JSON_API_P1_TELEGRAM        = 'P1_TELEGRAM'                          # ASCII string P1 telegram.

JSON_API_CNSMPTN_DLT_KWH    = 'CONSUMPTION_DELTA_KWH'                # the consumption in kilo Watt hour during this period
JSON_API_PRDCTN_DLT_KWH     = 'PRODUCTION_DELTA_KWH'                 # the production in kilo Watt hour during this period.

JSON_API_CNSMPTN_W          = 'CONSUMPTION_W'                        # the consumption in Watt at this moment.
JSON_API_PRDCTN_W           = 'PRODUCTION_W'                         # the production in Watt at this moment.
JSON_API_CNSMPTN_GAS_M3     = 'CONSUMPTION_GAS_M3'                   # consumption of gas in M3.
JSON_API_CNSMPTN_GAS_DLT_M3 = 'CONSUMPTION_GAS_DELTA_M3'             # consumption of gas in M3 during the period.
JSON_API_SFTWR_VRSN         = 'P1_SOFTWARE_VERSION'                  # software version of P1 software
JSON_API_SYSTM_ID           = 'P1_SYSTEM_ID'                         # system ID that is hardware specific and unique
JSON_API_RM_TMPRTR_IN       = 'ROOM_TEMPERATURE_IN'                  # room temperature input,raw data not processed
JSON_API_RM_TMPRTR_OUT      = 'ROOM_TEMPERATURE_OUT'                 # room temperature output,raw data not processed
JSON_API_REC_PRCSSD         = 'RECORD_IS_PROCESSED'                  # record is processed into the database
JSON_API_STTS_ID            = 'STATUS_ID'                            # unique record ID
JSON_API_STTS               = 'STATUS'                               # the status of the ID/label.
JSON_API_STTS_LBL           = 'LABEL'                                # description of the status.
JSON_API_SCRTY              = 'SECURITY'                             # security id
JSON_API_FNCL_CNSMPTN_E_L   = 'CONSUMPTION_COST_ELECTRICITY_LOW'     # Consumption costs electricity low tariff
JSON_API_FNCL_CNSMPTN_E_H   = 'CONSUMPTION_COST_ELECTRICITY_HIGH'    # Consumption costs electricity high tariff
JSON_API_FNCL_PRDCTN_E_L    = 'PRODUCTION_REVENUES_ELECTRICITY_LOW'  # production revenues electricity low tariff
JSON_API_FNCL_PRDCTN_E_H    = 'PRODUCTION_REVENUES_ELECTRICITY_HIGH' # production revenues electricity high tariff
JSON_API_FNCL_CNSMPTN_GAS   = 'CONSUMPTION_COST_GAS'                 # Consumption costs gas
JSON_API_FNCL_CNSMPTN_WATER = 'CONSUMPTION_COST_WATER'               # Consumption costs water
JSON_API_CTY_ID             = 'CITY_ID'                              # Weather provider id for location of weather data.
JSON_API_CTY_NM             = 'CITY_NAME'                            # Weather provider name for location of weather data.
JSON_API_TMPRTR_L           = 'TEMPERATURE_LOW'                      # Weather temperature lowest temperature 
JSON_API_TMPRTR_A           = 'TEMPERATURE_AVERAGE'                  # Weather temperature average temperature
JSON_API_TMPRTR_H           = 'TEMPERATURE_HIGH'                     # Weather temperature highest temperature
JSON_API_PRSSR_L            = 'PRESSURE_LOW'                         # Weather lowest atmospheric or air pressure  
JSON_API_PRSSR_A            = 'PRESSURE_AVERAGE'                     # Weather average atmospheric or air pressure 
JSON_API_PRSSR_H            = 'PRESSURE_HIGH'                        # Weather highest atmospheric or air pressure 
JSON_API_HUMIDITY_L         = 'HUMIDITY_LOW'                         # Weather lowest relative humidity
JSON_API_HUMIDITY_A         = 'HUMIDITY_AVERAGE'                     # Weather average relative humidity
JSON_API_HUMIDITY_H         = 'HUMIDITY_HIGH'                        # Weather highest relative humidity
JSON_API_WND_SPD_L          = 'WIND_SPEED_LOW'                       # Weather lowest wind speed in meter/sec
JSON_API_WND_SPD_A          = 'WIND_SPEED_AVERAGE'                   # Weather average wind speed in meter/sec
JSON_API_WND_SPD_H          = 'WIND_SPEED_HIGH'                      # Weather highest wind speed in meter/sec
JSON_API_WND_DGRS_L         = 'WIND_DEGREES_LOW'                     # Weather lowest wind degrees (meteorological)
JSON_API_WND_DGRS_A         = 'WIND_DEGREES_HUMIDITY_AVERAGE'        # Weather lowest wind degrees (meteorological)
JSON_API_WND_DGRS_H         = 'WIND_DEGREES_HIGH'                    # Weather lowest wind degrees (meteorological)
JSON_DGR_DYS                = 'DEGREE_DAYS'                          # A degree day is a unit of account for the simple inclusion of (varying) temperature in calculations of energy consumption.
JSON_API_CNFG_ID            = 'CONFIGURATION_ID'                     # unique record ID for config.
JSON_API_CNFG_PRMTR         = 'PARAMETER'                            # configuration value.
JSON_API_CNFG_LABEL         = 'LABEL'                                # label (name) of the configuration item.
JSON_API_WTHR_TMPRTR        = 'TEMPERATURE'                          # Weather temperature.
JSON_API_WTHR_DSCRPTN       = 'WEATHER_DESCRIPTION'                  # Weather description from the weather provider, like sun, mist, etc.
JSON_API_WTHR_ICON          = 'WEATHER_ICON'                         # Weather icon code, weather provider specific.
JSON_API_WTHR_PRSSR         = 'PRESSURE'                             # Weather atmospheric or air pressure.
JSON_API_WTHR_HMDTY         = 'HUMIDITY'                             # Weather relative humidity percentage (0-100).
JSON_API_WTHR_WND_SPD       = 'WIND_SPEED'                           # Weather wind speed in meter/sec.
JSON_API_WTHR_WND_DGRS      = 'WIND_DEGREES'                         # Weather wind degrees (meteorological).
JSON_API_WTHR_CLDS          = 'CLOUDS'                               # Weather cloudiness percentage (0-100).
JSON_API_WTHR_WEATHER_ID    = 'WEATHER_ID'                           # Weather condition id, weather provider specfic.
JSON_API_RM_TMPRTR_RCRD_ID  = 'ROOM_TEMPERATURE_RECORD_TYPE_ID'      # type of record id, 10-15 (current,minute,day,hour,month,year).
JSON_API_RM_TMPRTR_IN_L     = 'ROOM_TEMPERATURE_IN_LOW'              # room temperature input, low value in degrees Celsius.
JSON_API_RM_TMPRTR_IN_A     = 'ROOM_TEMPERATURE_IN_AVERAGE'          # room temperature input, average value degrees Celsius.
JSON_API_RM_TMPRTR_IN_H     = 'ROOM_TEMPERATURE_IN_HIGH'             # room temperature input, high value in degrees Celsius.
JSON_API_RM_TMPRTR_OUT_L    = 'ROOM_TEMPERATURE_OUT_LOW'             # room temperature output, low value in degrees Celsius.
JSON_API_RM_TMPRTR_OUT_A    = 'ROOM_TEMPERATURE_OUT_AVERAGE'         # room temperature output, average value degrees Celsius.
JSON_API_RM_TMPRTR_OUT_H    = 'ROOM_TEMPERATURE_OUT_HIGH'            # room temperature output, high value in degrees Celsius.

JSON_API_WM_PULS_CNT        = 'WATERMETER_PULS_COUNT'                # Nummer of detected pulses per timeunit (min, hour, day, month, year).
JSON_API_WM_CNSMPTN_LTR     = 'WATERMETER_CONSUMPTION_LITER'         # Liter of waterused per timeunit (min, hour, day, month, year).
JSON_API_WM_CNSMPTN_LTR_M3  = 'WATERMETER_CONSUMPTION_TOTAL_M3'      # consumption of water in M3 during the period.

JSON_API_PHS_CNSMPTN_L1_W   = 'CONSUMPTION_L1_W'                     # Consumption of W for phase L1
JSON_API_PHS_CNSMPTN_L2_W   = 'CONSUMPTION_L2_W'                     # Consumption of W for phase L2
JSON_API_PHS_CNSMPTN_L3_W   = 'CONSUMPTION_L3_W'                     # Consumption of W for phase L3
JSON_API_PHS_PRDCTN_L1_W    = 'PRODUCTION_L1_W'                      # Production of W for phase L1
JSON_API_PHS_PRDCTN_L2_W    = 'PRODUCTION_L2_W'                      # Production of W for phase L2
JSON_API_PHS_PRDCTN_L3_W    = 'PRODUCTION_L3_W'                      # Production of W for phase L3
JSON_API_PHS_L1_V           = 'L1_V'                                 # Voltage phase L1
JSON_API_PHS_L2_V           = 'L2_V'                                 # Voltage phase L2
JSON_API_PHS_L3_V           = 'L3_V'                                 # Voltage phase L3
JSON_API_PHS_L1_A           = 'L1_A'                                 # Amperage phase L1
JSON_API_PHS_L2_A           = 'L2_A'                                 # Amperage phase L2
JSON_API_PHS_L3_A           = 'L3_A'                                 # Amperage phase L3

JSON_API_PHS_CNSMPTN_L1_W_MAX  = 'CONSUMPTION_L1_W_MAX'              # Consumption of W for phase L1 maximum
JSON_API_PHS_CNSMPTN_L2_W_MAX  = 'CONSUMPTION_L2_W_MAX'              # Consumption of W for phase L2 maximum
JSON_API_PHS_CNSMPTN_L3_W_MAX  = 'CONSUMPTION_L3_W_MAX'              # Consumption of W for phase L3 maximum
JSON_API_PHS_PRDCTN_L1_W_MAX   = 'PRODUCTION_L1_W_MAX'               # Production of W for phase L1 maximum
JSON_API_PHS_PRDCTN_L2_W_MAX   = 'PRODUCTION_L2_W_MAX'               # Production of W for phase L2 maximum
JSON_API_PHS_PRDCTN_L3_W_MAX   = 'PRODUCTION_L3_W_MAX'               # Production of W for phase L3 maximum
JSON_API_PHS_L1_V_MAX          = 'L1_V_MAX'                          # Voltage phase L1 maximum
JSON_API_PHS_L2_V_MAX          = 'L2_V_MAX'                          # Voltage phase L2 maximum
JSON_API_PHS_L3_V_MAX          = 'L3_V_MAX'                          # Voltage phase L3 maximum
JSON_API_PHS_L1_A_MAX          = 'L1_A_MAX'                          # Amperage phase L1 maximum
JSON_API_PHS_L2_A_MAX          = 'L2_A_MAX'                          # Amperage phase L2 maximum
JSON_API_PHS_L3_A_MAX          = 'L3_A_MAX'                          # Amperage phase L3 maximum

JSON_API_PHS_CNSMPTN_L1_W_MIN  = 'CONSUMPTION_L1_W_MIN'              # Consumption of W for phase L1 minimum
JSON_API_PHS_CNSMPTN_L2_W_MIN  = 'CONSUMPTION_L2_W_MIN'              # Consumption of W for phase L2 minimum
JSON_API_PHS_CNSMPTN_L3_W_MIN  = 'CONSUMPTION_L3_W_MIN'              # Consumption of W for phase L3 minimum
JSON_API_PHS_PRDCTN_L1_W_MIN   = 'PRODUCTION_L1_W_MIN'               # Production of W for phase L1 minimum
JSON_API_PHS_PRDCTN_L2_W_MIN   = 'PRODUCTION_L2_W_MIN'               # Production of W for phase L2 minimum
JSON_API_PHS_PRDCTN_L3_W_MIN   = 'PRODUCTION_L3_W_MIN'               # Production of W for phase L3 minimum
JSON_API_PHS_L1_V_MIN          = 'L1_V_MIN'                          # Voltage phase L1 minimum
JSON_API_PHS_L2_V_MIN          = 'L2_V_MIN'                          # Voltage phase L2 minimum
JSON_API_PHS_L3_V_MIN          = 'L3_V_MIN'                          # Voltage phase L3 minimum
JSON_API_PHS_L1_A_MIN          = 'L1_A_MIN'                          # Amperage phase L1 minimum
JSON_API_PHS_L2_A_MIN          = 'L2_A_MIN'                          # Amperage phase L2 minimum
JSON_API_PHS_L3_A_MIN          = 'L3_A_MIN'                          # Amperage phase L3 minimum

JSON_API_PROD_PERIOD_ID     = 'TIMEPERIOD_ID'                        # Number  / index of time period.
JSON_API_PROD_PWR_SRC_ID    = 'POWER_SOURCE_ID'                      # Number / index of the power source, 0 is not defined, 1 is S0 kWh puls.
JSON_API_PROD_KWH_H         = 'PRODUCTION_KWH_HIGH'                  # kWh during the period for the high tariff.
JSON_API_PROD_KWH_L         = 'PRODUCTION_KWH_LOW'                   # kWh during the period for the low tariff.
JSON_API_PROD_PULS_CNT_H    = 'PULS_PER_TIMEUNIT_HIGH'               # Number of detected pulses per timeunit (min, hour, day, month, year) for the high tariff.
JSON_API_PROD_PULS_CNT_L    = 'PULS_PER_TIMEUNIT_LOW'                # Number of detected pulses per timeunit (min, hour, day, month, year) for the low tariff.
JSON_API_PROD_KWH_TOTAL_H   = 'PRODUCTION_KWH_HIGH_TOTAL'            # total kWh during the period for the high tariff.
JSON_API_PROD_KWH_TOTAL_L   = 'PRODUCTION_KWH_LOW_TOTAL'             # total kWh during the period for the low tariff.
JSON_API_PROD_KWH_TOTAL     = 'PRODUCTION_KWH_TOTAL'                 # total kWh during the period for the low and high tariff.
JSON_API_PROD_W_PSEUDO      = 'PRODUCTION_PSEUDO_W'                  # total Watt calculated during the period, this is an simulated/approximated value.

JSON_API_FNCL_DYN_TRFF_KWH  = 'DYNAMIC_TARIFF_KWH'                   # dynamic tariff kwh.
JSON_API_FNCL_DYN_TRFF_GAS  = 'DYNAMIC_TARIFF_GAS'                   # dynamic tariff gas.


#JSON field explained.
EXPL_TS_LCL                 = 'Time in format yyyy-mm-dd hh:mm:ss'
EXPL_TS_LCL_UTC             = 'UTC timestamp'
EXPL_API_STTS               = 'Options are production=ok, test, deprecated = will be removed in future version.'
EXPL_API_VRSN               = 'ID / number will be used in file name.'
EXPL_API_CNSMPTN_KWH_L      = 'Consumption of KWH during low (dal) period. Meter code 181.'
EXPL_API_CNSMPTN_KWH_H      = 'Consumption of KWH during high (piek) period. Meter code 182.'
EXPL_API_PRDCTN_KWH_L       = 'Production of KWH during low (dal) period. Meter code 281.'
EXPL_API_PRDCTN_KWH_H       = 'Production of KWH during high (piek) period. Meter code 282.'
EXPL_API_TRFCD              = 'High or low period for production of consumption of kWh. Low = D, High = P'
EXPL_API_CNSMPTN_KW         = 'The consumption in kilo Watt at this moment.'
EXPL_API_PRDCTN_KW          = 'The production in kilo Watt at this moment.'

EXPL_API_CNSMPTN_DLT_KWH    = 'The consumption in kilo Watt hour (kWh) during this period.'
EXPL_API_PRDCTN_DLT_KWH     = 'The production in kilo Watt hour (kWh) during this period.'

EXPL_API_CNSMPTN_W          = 'The consumption in Watt at this moment.'
EXPL_API_PRDCTN_W           = 'The production in Watt at this moment.'
EXPL_API_CNSMPTN_GAS_M3     = 'Consumption of gas in M3.'
EXPL_API_CNSMPTN_GAS_DLT_M3 = 'Consumption of gas in M3 during the period.'
EXPL_API_SFTWR_VRSN         = 'Software version of P1 software'
EXPL_API_SYSTM_ID           = 'System ID that is hardware specific and unique'
EXPL_API_RM_TMPRTR_IN       = 'Room temperature input,raw data not processed in degrees Celsius.'
EXPL_API_RM_TMPRTR_OUT      = 'Room temperature output,raw data not processed in degrees Celsius.'
EXPL_API_REC_PRCSSD         = 'Record is processed into the database. 1 is done, 0 is to do.'
EXPL_API_STTS_ID            = 'Unique record ID'
EXPL_API_STTS               = 'The status of the ID/label.'
EXPL_API_STTS_LBL           = 'Description of the status.'
EXPL_API_SCRTY              = 'Security id.'
EXPL_API_FNCL_CNSMPTN_E_L   = 'Consumption costs electricity low tariff.'
EXPL_API_FNCL_CNSMPTN_E_H   = 'Consumption costs electricity high tariff.'
EXPL_API_FNCL_PRDCTN_E_L    = 'Production revenues electricity low tariff.'
EXPL_API_FNCL_PRDCTN_E_H    = 'Production revenues electricity high tariff.'
EXPL_API_FNCL_CNSMPTN_GAS   = 'Consumption costs gas.'
EXPL_API_FNCL_CNSMPTN_WATER = 'Consumption costs water.'
EXPL_API_CTY_ID             = 'Weather provider id for location of weather data.'
EXPL_API_CTY_NM             = 'Weather provider name for location of weather data.'
EXPL_API_TMPRTR_L           = 'Weather temperature lowest temperature.' 
EXPL_API_TMPRTR_A           = 'Weather temperature average temperature.'
EXPL_API_TMPRTR_H           = 'Weather temperature highest temperature.'
EXPL_API_PRSSR_L            = 'Weather lowest atmospheric or air pressure.'  
EXPL_API_PRSSR_A            = 'Weather average atmospheric air pressure.' 
EXPL_API_PRSSR_H            = 'Weather highest atmospheric air pressure.'
EXPL_API_HUMIDITY_L         = 'Weather lowest relative humidity.'
EXPL_API_HUMIDITY_A         = 'Weather average relative humidity.'
EXPL_API_HUMIDITY_H         = 'Weather highest relative humidity.'
EXPL_API_WND_SPD_L          = 'Weather lowest wind speed in meter/sec.'
EXPL_API_WND_SPD_A          = 'Weather average wind speed in meter/sec.'
EXPL_API_WND_SPD_H          = 'Weather highest wind speed in meter/sec.'
EXPL_API_WND_DGRS_L         = 'Weather smallest number of wind degrees (meteorological).'
EXPL_API_WND_DGRS_A         = 'Weather average number of wind degrees (meteorological).'
EXPL_API_WND_DGRS_H         = 'Weather highest number of wind degrees (meteorological).'
EXPL_API_DGR_DYS            = 'A degree day is a unit of account for the simple inclusion of (varying) temperature in calculations of energy consumption.'
EXPL_API_CNFG_ID            = 'Unique record ID for config.'
EXPL_API_CNFG_PRMTR         = 'Configuration value.'
EXPL_API_CNFG_LABEL         = 'Label (name) of the configuration item.'
EXPL_API_WTHR_TMPRTR        = 'Weather temperature.'
EXPL_API_WTHR_DSCRPTN       = 'Weather description from the weather provider, like sun, mist, etc.'
EXPL_API_WTHR_ICON          = 'Weather icon code, weather provider specific.'
EXPL_API_WTHR_PRSSR         = 'Weather atmospheric or air pressure.'
EXPL_API_WTHR_HMDTY         = 'Weather relative humidity percentage (0-100).'
EXPL_API_WTHR_WND_SPD       = 'Weather wind speed in meter/sec.'
EXPL_API_WTHR_WND_DGRS      = 'Weather wind degrees (meteorological).'
EXPL_API_WTHR_CLDS          = 'Weather cloudiness percentage (0-100).'
EXPL_API_WTHR_WEATHER_ID    = 'Weather condition id, weather provider specific.'
EXPL_API_RM_TMPRTR_RCRD_ID  = 'Type of record id, 10-15 (current,minute,day,hour,month,year).'
EXPL_API_RM_TMPRTR_IN_L     = 'Room temperature input, low value in degrees Celsius.'
EXPL_API_RM_TMPRTR_IN_A     = 'Room temperature input, average value degrees Celsius.'
EXPL_API_RM_TMPRTR_IN_H     = 'Room temperature input, high value in degrees Celsius.'
EXPL_API_RM_TMPRTR_OUT_L    = 'Room temperature output, low value in degrees Celsius.'
EXPL_API_RM_TMPRTR_OUT_A    = 'Room temperature output, average value degrees Celsius.'
EXPL_API_RM_TMPRTR_OUT_H    = 'Room temperature output, high value in degrees Celsius.'

EXPL_API_P1_TELEGRAM        = 'ASCII string P1 telegram.'
EXPL_API_VALID_DATA         = 'used to flag the data good/complete enough to process. options valid or invalid'

EXPL_API_WM_PULS_CNT        = 'Nummer of detected pulses per timeunit (minute,hour, day, month, year).'
EXPL_API_WM_CNSMPTN_LTR     = 'Liter of waterused per timeunit (minute,hour, day, month, year).'
EXPL_API_WM_CNSMPTN_LTR_M3  = 'Consumption of water in M3 during the period.'

EXPL_API_PHS_CNSMPTN_L1_W   = 'Consumption of Watt for phase L1'
EXPL_API_PHS_CNSMPTN_L2_W   = 'Consumption of Watt for phase L2'
EXPL_API_PHS_CNSMPTN_L3_W   = 'Consumption of Watt for phase L3'
EXPL_API_PHS_PRDCTN_L1_W    = 'Production of Watt for phase L1'
EXPL_API_PHS_PRDCTN_L2_W    = 'Production of Watt for phase L2'
EXPL_API_PHS_PRDCTN_L3_W    = 'Production of Watt for phase L3'
EXPL_API_PHS_L1_V           = 'Voltage phase L1'
EXPL_API_PHS_L2_V           = 'Voltage phase L2'
EXPL_API_PHS_L3_V           = 'Voltage phase L3'
EXPL_API_PHS_L1_A           = 'Amperage phase L1'
EXPL_API_PHS_L2_A           = 'Amperage phase L2'
EXPL_API_PHS_L3_A           = 'Amperage phase L3'


EXPL_API_PHS_CNSMPTN_L1_W_MAX = 'Consumption of W for phase L1 maximum'
EXPL_API_PHS_CNSMPTN_L2_W_MAX = 'Consumption of W for phase L2 maximum'
EXPL_API_PHS_CNSMPTN_L3_W_MAX = 'Consumption of W for phase L3 maximum'
EXPL_API_PHS_PRDCTN_L1_W_MAX  = 'Production of W for phase L1 maximum'
EXPL_API_PHS_PRDCTN_L2_W_MAX  = 'Production of W for phase L2 maximum'
EXPL_API_PHS_PRDCTN_L3_W_MAX  = 'Production of W for phase L3 maximum'
EXPL_API_PHS_L1_V_MAX         = 'Voltage phase L1 maximum'
EXPL_API_PHS_L2_V_MAX         = 'Voltage phase L2 maximum'
EXPL_API_PHS_L3_V_MAX         = 'Voltage phase L3 maximum'
EXPL_API_PHS_L1_A_MAX         = 'Amperage phase L1 maximum'
EXPL_API_PHS_L2_A_MAX         = 'Amperage phase L2 maximum'
EXPL_API_PHS_L3_A_MAX         = 'Amperage phase L3 maximum'

EXPL_API_PHS_CNSMPTN_L1_W_MIN = 'Consumption of W for phase L1 minimum'
EXPL_API_PHS_CNSMPTN_L2_W_MIN = 'Consumption of W for phase L2 minimum'
EXPL_API_PHS_CNSMPTN_L3_W_MIN = 'Consumption of W for phase L3 minimum'
EXPL_API_PHS_PRDCTN_L1_W_MIN  = 'Production of W for phase L1 minimum'
EXPL_API_PHS_PRDCTN_L2_W_MIN  = 'Production of W for phase L2 minimum'
EXPL_API_PHS_PRDCTN_L3_W_MIN  = 'Production of W for phase L3 minimum'
EXPL_API_PHS_L1_V_MIN         = 'Voltage phase L1 minimum'
EXPL_API_PHS_L2_V_MIN         = 'Voltage phase L2 minimum'
EXPL_API_PHS_L3_V_MIN         = 'Voltage phase L3 minimum'
EXPL_API_PHS_L1_A_MIN         = 'Amperage phase L1 minimum'
EXPL_API_PHS_L2_A_MIN         = 'Amperage phase L2 minimum'
EXPL_API_PHS_L3_A_MIN         = 'Amperage phase L3 minimum'

EXPL_API_PROD_PERIOD_ID     = 'Number/index of time period 11-15 (minute,day,hour,month,year).'
EXPL_API_PROD_PERIOD_ID_SOLAR = 'Number/index of time period (minute,day,hour,month,year).'
EXPL_API_PROD_PWR_SRC_ID    = 'Number/index of the power source, 0 is not defined, 1 is S0 kWh puls.'
EXPL_API_PROD_PWR_SRC_ID_SOLAR = 'Number/index of the power source, 0 is not defined, 1 is Solar Edge.'
EXPL_API_PROD_KWH_H         = 'kWh during the period for the high tariff.'
EXPL_API_PROD_KWH_L         = 'kWh during the period for the low tariff.'
EXPL_API_PROD_PULS_CNT_H    = 'Number of detected pulses per timeunit (min, hour, day, month, year) for the high tariff.'
EXPL_API_PROD_PULS_CNT_L    = 'Number of detected pulses per timeunit (min, hour, day, month, year) for the low tariff.'
EXPL_API_PROD_KWH_TOTAL_H   = 'Total kWh during the period for the high tariff.'
EXPL_API_PROD_KWH_TOTAL_L   = 'Total kWh during the period for the low tariff.'
EXPL_API_PROD_KWH_TOTAL     = 'Total kWh during the period for the low and high tariff.'
EXPL_API_PROD_W_PSEUDO      = 'Total Watt calculated during the period, this is an simulated/approximated value.'

EXPL_API_FNCL_DYN_TRFF_KWH  = 'Dynamic tariff kwh.'
EXPL_API_FNCL_DYN_TRFF_GAS  = 'Dynamic tariff gas.'

#json types
TYPE_JSON_STRING         = 'string'
TYPE_JSON_INTEGER        = 'integer'
TYPE_JSON_NUMBER         = 'number'  # int or floating point.
TYPE_JSON_NUMBER_INTEGER =  TYPE_JSON_NUMBER + ' or ' + TYPE_JSON_INTEGER + ' depending on the format specifier used.'

#api parameter key words
API_PARAMETER_LIMIT          = 'limit'
API_PARAMETER_SORT           = 'sort'
API_PARAMETER_JSON_TYPE      = 'json'
API_PARAMETER_ROUND          = 'round'
API_PARAMETER_STARTTIMESTAMP = 'starttime'
API_PARAMETER_ID             = 'id'
API_PARAMETER_NONE           = 'none'
API_PARAMETER_RANGETIMESTAMP = 'range'

API_STATUS_TEST              = 'test'
API_STATUS_PRODUCTION        = 'production'
API_STATUS_DEPRECATED        = 'deprecated'
API_STATUS_VALID             = 'valid'
API_STATUS_INVALID           = 'invalid'

#api options 
API_OPTION_LIMIT          =  API_PARAMETER_LIMIT          + ' {default all, >0 } number of entries returned'
API_OPTION_SORT_TIMESTAMP =  API_PARAMETER_SORT           + ' (on timestamp) {default desc, asc} sort on timestamp'
API_OPTION_JSON           =  API_PARAMETER_JSON_TYPE      + ' {default array, object} json output options see https://www.json.org/'
API_OPTION_ROUND          =  API_PARAMETER_ROUND          + ' {default off, on} round to the nearest integer, no fractions in the output'
API_OPTION_STARTTIMESTAMP =  API_PARAMETER_STARTTIMESTAMP + ' {default now, YYYY-MM-DD HH:MM:SS} from which moment in time data should retrieved'
API_OPTION_RANGE          =  API_PARAMETER_RANGETIMESTAMP + ' {YYYY-MM-DD HH:MM:SS} all records that fit the timestamp string will be retrieved'
API_OPTION_ID             =  API_PARAMETER_ID             + ' {default all, id, help}'


# api catalog overview
HELP_ROUTE_CATALOG_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_PARAMETER_NONE,
    "api_description"   : "List of available API Uniform Resource Identifiers (URI).",
    "api_usage"         : "<ip>" + ROUTE_CATALOG + ',<ip>' + ROUTE_CATALOG_HELP,
    "fields"            : API_PARAMETER_NONE
}


# help data
# SQL AS Reference
# sqlstr = select TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), PRICE_KWH REAL PRICE_GAS 
#
HELP_ROUTE_FINANCIAL_DYNAMIC_TARIFF_JSON = { 
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP,
    "api_description"   : "The dynamic tariff values per hour. Data is added when available from the tariff supplier. Data is ordered on timestamp.",
    "api_usage"         : "<ip>" + ROUTE_FINANCIAL_DYNAMIC_TARIFF+ '?'+ API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2023-04-02 10:50:55 or ' + API_PARAMETER_RANGETIMESTAMP + '=2023-04-02, <ip>' + ROUTE_FINANCIAL_DYNAMIC_TARIFF_HELP,
    "fields": [
        {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
        },
        { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_FNCL_DYN_TRFF_KWH,
           "description" : EXPL_API_FNCL_DYN_TRFF_KWH,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_FNCL_DYN_TRFF_GAS,
           "description" : EXPL_API_FNCL_DYN_TRFF_GAS,
           "type": TYPE_JSON_NUMBER_INTEGER
        }
    ]
}



# help data
# SQL AS Reference
#sqlstr = "select TIMESTAMP, cast(strftime('%s',TIMESTAMP) as Integer), RECORD_VERWERKT, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, \
#            GELVR_KWH_282, TARIEFCODE, ACT_VERBR_KW_170, ACT_GELVR_KW_270, VERBR_GAS_2421
HELP_ROUTE_SMARTMETER_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP,
    "api_description"   : "The standardised and verified data that the smart meter can deliver. The number of entries returned is optional. The data is added with a frequency of 10 seconds. Data is ordered on timestamp.",
    "api_usage"         : "<ip>" + ROUTE_SMARTMETER + '?'+ API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2018-01-03 12:03:55, <ip>' + ROUTE_SMARTMETER + ", <ip>" + ROUTE_SMARTMETER_HELP,
    "fields": [
        {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
        },
        { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_REC_PRCSSD,
           "description" : EXPL_API_REC_PRCSSD,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_CNSMPTN_KWH_L,
           "description" : EXPL_API_CNSMPTN_KWH_L,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_CNSMPTN_KWH_H,
           "description" : EXPL_API_CNSMPTN_KWH_H,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_PRDCTN_KWH_L,
           "description" : EXPL_API_PRDCTN_KWH_L,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_PRDCTN_KWH_H,
           "description" : EXPL_API_PRDCTN_KWH_H,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_TRFCD ,
           "description" : EXPL_API_TRFCD,
           "type": TYPE_JSON_STRING
        }
        ,
        { 
           "name" : JSON_API_CNSMPTN_W,
           "description" : EXPL_API_CNSMPTN_W,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_PRDCTN_W,
           "description" : EXPL_API_PRDCTN_W,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_CNSMPTN_GAS_M3,
           "description" : EXPL_API_CNSMPTN_GAS_M3,
           "type": TYPE_JSON_NUMBER_INTEGER
        }
    ]
}


# config data
# SQL AS Reference
# 'select ID,PARAMETER,LABEL from config order by id'
HELP_ROUTE_P1_PORT_TELEGRAM = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_JSON,
    "api_description"   : "The P1 telegram as received from the smart meter. It is the last telegram that is successfully received in the form of a JSON array.",
    "api_usage"         : "<ip>" + ROUTE_P1_PORT_TELEGRAM + "?" + API_PARAMETER_JSON_TYPE + "=object",
    "fields": [
        {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_VALID_DATA ,
           "description" : EXPL_API_VALID_DATA ,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_API_P1_TELEGRAM,
           "description" : EXPL_API_P1_TELEGRAM,
           "type": TYPE_JSON_STRING
         },

    ]
}


# config data
# SQL AS Reference
# 'select ID,PARAMETER,LABEL from config order by id'
HELP_ROUTE_CONFIG_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       :  API_OPTION_ID + ', ' + API_OPTION_JSON,
    "api_description"   : "configuration information of various parts of the P1 monitor. It is a list of records displayed as JSON array. The records are sorted in ascending order by " + JSON_API_CNFG_ID,
    "api_usage"         : "<ip>" + ROUTE_CONFIG + "?" + API_PARAMETER_JSON_TYPE + "=object",
    "fields": [
        {
           "name" : JSON_API_CNFG_ID,
           "description" : EXPL_API_CNFG_ID,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_CNFG_PRMTR,
           "description" : EXPL_API_CNFG_PRMTR,
           "type": TYPE_JSON_STRING
        },
        { 
           "name" : JSON_API_CNFG_LABEL,
           "description" : EXPL_API_CNFG_LABEL,
           "type": TYPE_JSON_STRING
        }
    ]
}

# status data
# SQL AS Reference
# 'select ID, STATUS,LABEL,SECURITY from status order by id'
HELP_ROUTE_STATUS_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_ID + ', ' + API_OPTION_JSON,
    "api_description"   : "status information of various parts of the P1 monitor. It is a list of records displayed as JSON array. The records are sorted in ascending order by " + JSON_API_STTS_ID,
    "api_usage"         : "<ip>" + ROUTE_STATUS + '?' + API_PARAMETER_JSON_TYPE +  "=object",
    "fields": [
        {
           "name" : JSON_API_STTS_ID,
           "description" : EXPL_API_STTS_ID,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_STTS,
           "description" : EXPL_API_STTS,
           "type": TYPE_JSON_STRING
        },
        { 
           "name" : JSON_API_STTS_LBL,
           "description" : EXPL_API_STTS_LBL,
           "type": TYPE_JSON_STRING
        },
        { 
           "name" : JSON_API_SCRTY,
           "description" : EXPL_API_SCRTY,
           "type": TYPE_JSON_INTEGER
        }
    ]
}

# status data
# SQL AS Reference
# select TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), VERBR_P, VERBR_D, GELVR_P,GELVR_D, GELVR_GAS from xxx order by timestamp
HELP_ROUTE_FINANCIAL_DAY_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       :  API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Financial data that is ordered on timestamp",
    "api_usage"         : "<ip>{" + ROUTE_FINANCIAL_DAY + ', ' + ROUTE_FINANCIAL_MONTH + ', ' + ROUTE_FINANCIAL_YEAR + '}?' + API_PARAMETER_JSON_TYPE + '=object, <ip>{' + ROUTE_FINANCIAL_DAY_HELP + ', ' + ROUTE_FINANCIAL_MONTH_HELP + ',' + ROUTE_FINANCIAL_YEAR_HELP + '}' ,
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_FNCL_CNSMPTN_E_H,
           "description" : EXPL_API_FNCL_CNSMPTN_E_H,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_FNCL_CNSMPTN_E_L,
           "description" : EXPL_API_FNCL_CNSMPTN_E_L,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_FNCL_PRDCTN_E_H,
           "description" : EXPL_API_FNCL_PRDCTN_E_H,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_FNCL_PRDCTN_E_L,
           "description" : EXPL_API_FNCL_PRDCTN_E_L,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_FNCL_CNSMPTN_GAS,
           "description" : EXPL_API_FNCL_CNSMPTN_GAS,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_FNCL_CNSMPTN_WATER,
           "description" : EXPL_API_FNCL_CNSMPTN_WATER,
           "type": TYPE_JSON_NUMBER
         }
    ]
}

# status data
# SQL AS Reference
# select TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, GELVR_KWH_282, VERBR_KWH_X, 
# GELVR_KWH_X TARIEFCODE ACT_VERBR_KW_170, ACT_GELVR_KW_270, VERBR_GAS_2421 from ....
HELP_ROUTE_POWER_GAS_MIN_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Power and gas data with a minute interval that is ordered on timestamp",
    "api_usage"         : "<ip>" + ROUTE_POWER_GAS_MIN + '?'+ API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2018-01-03 12:03:55 or ' + API_PARAMETER_RANGETIMESTAMP + '=2020-01-03, <ip>' + ROUTE_POWER_GAS_MIN + ', <ip>' + ROUTE_POWER_GAS_MIN_HELP,
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_CNSMPTN_KWH_L,
           "description" : EXPL_API_CNSMPTN_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_CNSMPTN_KWH_H,
           "description" : EXPL_API_CNSMPTN_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_KWH_L,
           "description" : EXPL_API_PRDCTN_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_KWH_H,
           "description" : EXPL_API_PRDCTN_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_CNSMPTN_DLT_KWH,
           "description" : EXPL_API_CNSMPTN_DLT_KWH,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_DLT_KWH,
           "description" : EXPL_API_PRDCTN_DLT_KWH,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_TRFCD,
           "description" : EXPL_API_TRFCD,
           "type": TYPE_JSON_STRING
         },
         {  
           "name" : JSON_API_CNSMPTN_KW,
           "description" : EXPL_API_CNSMPTN_KW,
           "type": TYPE_JSON_NUMBER
         },
         {  
           "name" : JSON_API_PRDCTN_KW,
           "description" : EXPL_API_PRDCTN_KW,
           "type": TYPE_JSON_NUMBER
         },
         {  
           "name" : JSON_API_CNSMPTN_GAS_M3,
           "description" : EXPL_API_CNSMPTN_GAS_M3,
           "type": TYPE_JSON_NUMBER
         }
    ]
}

# status data
# SQL AS Reference
# TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281 GELVR_KWH_282, 
# VERBR_KWH_X, GELVR_KWH_X, TARIEFCODE , VERBR_GAS_2421, VERBR_GAS_X 
HELP_ROUTE_POWER_GAS_HOUR_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Power and gas data with an hour interval that is ordered on timestamp",
    "api_usage"         : "<ip>" + ROUTE_POWER_GAS_MIN + '?'+ API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2018-01-03 12:03:55 or ' + API_PARAMETER_RANGETIMESTAMP + '=2020-01-03, <ip>' + ROUTE_POWER_GAS_MIN + ', <ip>' + ROUTE_POWER_GAS_MIN_HELP,
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_CNSMPTN_KWH_L,
           "description" : EXPL_API_CNSMPTN_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_CNSMPTN_KWH_H,
           "description" : EXPL_API_CNSMPTN_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_KWH_L,
           "description" : EXPL_API_PRDCTN_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_KWH_H,
           "description" : EXPL_API_PRDCTN_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_CNSMPTN_DLT_KWH,
           "description" : EXPL_API_CNSMPTN_DLT_KWH,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_DLT_KWH,
           "description" : EXPL_API_PRDCTN_DLT_KWH,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_TRFCD,
           "description" : EXPL_API_TRFCD,
           "type": TYPE_JSON_STRING
         },
         {  
           "name" : JSON_API_CNSMPTN_GAS_M3,
           "description" : EXPL_API_CNSMPTN_GAS_M3,
           "type": TYPE_JSON_NUMBER
         },
         {  
           "name" : JSON_API_CNSMPTN_GAS_DLT_M3,
           "description" : EXPL_API_CNSMPTN_GAS_DLT_M3,
           "type": TYPE_JSON_NUMBER
         }
    ]
}

# SQL AS Reference
# TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281 GELVR_KWH_282, 
# VERBR_KWH_X, GELVR_KWH_X , VERBR_GAS_2421, VERBR_GAS_X 
HELP_ROUTE_POWER_GAS_DAY_MONTH_YEAR_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Power and gas data with an day, month or year interval that is ordered on timestamp",
    "api_usage"         : "<ip>" + ROUTE_POWER_GAS_MIN + '?'+ API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2018-01-03 12:03:55 or ' + API_PARAMETER_RANGETIMESTAMP + '=2020-01-03, <ip>' + ROUTE_POWER_GAS_MIN + ', <ip>' + ROUTE_POWER_GAS_MIN_HELP,
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_CNSMPTN_KWH_L,
           "description" : EXPL_API_CNSMPTN_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_CNSMPTN_KWH_H,
           "description" : EXPL_API_CNSMPTN_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_KWH_L,
           "description" : EXPL_API_PRDCTN_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_KWH_H,
           "description" : EXPL_API_PRDCTN_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_CNSMPTN_DLT_KWH,
           "description" : EXPL_API_CNSMPTN_DLT_KWH,
           "type": TYPE_JSON_NUMBER
         },
         { 
           "name" : JSON_API_PRDCTN_DLT_KWH,
           "description" : EXPL_API_PRDCTN_DLT_KWH,
           "type": TYPE_JSON_NUMBER
         },
         {  
           "name" : JSON_API_CNSMPTN_GAS_M3,
           "description" : EXPL_API_CNSMPTN_GAS_M3,
           "type": TYPE_JSON_NUMBER
         },
         {  
           "name" : JSON_API_CNSMPTN_GAS_DLT_M3,
           "description" : EXPL_API_CNSMPTN_GAS_DLT_M3,
           "type": TYPE_JSON_NUMBER
         }
    ]
}

# status data
# SQL AS Reference
# select TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), CITY_ID, CITY, TEMPERATURE_MIN, TEMPERATURE_AVG, TEMPERATURE_MAX, 
# PRESSURE_MIN, PRESSURE_AVG, PRESSURE_MAX, HUMIDITY_MIN, HUMIDITY_AVG, HUMIDITY_MAX, WIND_SPEED_MIN, WIND_SPEED_AVG, WIND_SPEED_MAX, 
# WIND_DEGREE_MIN, WIND_DEGREE_AVG, WIND_DEGREE_MAX, DEGREE_DAYS from
HELP_ROUTE_WEATHER_DAY_MONTH_YEAR_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       :  API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP,
    "api_description"   : "Historical weather data with an hour, day, month or year interval that is ordered on timestamp.",
    "api_usage"         : "<ip>{" + ROUTE_WEATHER_HOUR + ', ' + ROUTE_WEATHER_DAY + ', ' + ROUTE_WEATHER_MONTH + ', ' + ROUTE_WEATHER_YEAR + '}?' + API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2018-01-03 12:03:55, <ip>{' + ROUTE_WEATHER_HOUR + ', ' + ROUTE_WEATHER_DAY + ', ' + ROUTE_WEATHER_MONTH + ', ' + ROUTE_WEATHER_YEAR + '},<ip>{' + ROUTE_WEATHER_HOUR_HELP + ', ' + ROUTE_WEATHER_DAY_HELP + ', ' + ROUTE_WEATHER_MONTH_HELP + ', ' +ROUTE_WEATHER_MONTH_HELP + '}',
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_CTY_ID,
           "description" : EXPL_API_CTY_ID,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_CTY_NM,
           "description" : EXPL_API_CTY_NM,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_API_TMPRTR_L,
           "description" : EXPL_API_TMPRTR_L,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_TMPRTR_A,
           "description" : EXPL_API_TMPRTR_A,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_TMPRTR_H,
           "description" : EXPL_API_TMPRTR_H,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_PRSSR_L,
           "description" : EXPL_API_PRSSR_L,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PRSSR_A,
           "description" : EXPL_API_PRSSR_A,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PRSSR_H,
           "description" : EXPL_API_PRSSR_H,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_HUMIDITY_L,
           "description" : EXPL_API_HUMIDITY_L,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_HUMIDITY_A,
           "description" : EXPL_API_HUMIDITY_A,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_HUMIDITY_H,
           "description" : EXPL_API_HUMIDITY_H,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_WND_SPD_L,
           "description" : EXPL_API_WND_SPD_L,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WND_SPD_A,
           "description" : EXPL_API_WND_SPD_A,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WND_SPD_H,
           "description" : EXPL_API_WND_SPD_H,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WND_DGRS_L,
           "description" : EXPL_API_WND_DGRS_L,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WND_DGRS_A,
           "description" : EXPL_API_WND_DGRS_A,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WND_DGRS_H,
           "description" : EXPL_API_WND_DGRS_H,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_DGR_DYS,
           "description" : EXPL_API_DGR_DYS,
           "type": TYPE_JSON_NUMBER_INTEGER
         }
    ]
}

# status data
# SQL AS Reference
# sqlstr_base_regular =  "select datetime( TIMESTAMP, 'unixepoch', 'localtime' ), TIMESTAMP, CITY_ID, CITY, TEMPERATURE, DESCRIPTION, 
# WEATHER_ICON, PRESSURE, HUMIDITY, WIND_SPEED, WIND_DEGREE, CLOUDS, WEATHER_ID from "
HELP_ROUTE_WEATHER_CURRENT_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP,
    "api_description"   : "Current weather data.",
    "api_usage"         : "<ip>" + ROUTE_WEATHER_CURRENT + ",<ip>" + ROUTE_WEATHER_CURRENT + '?' + API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2018-01-03 12:03:55, <ip>' + ROUTE_WEATHER_CURRENT_HELP + '}',
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_CTY_ID,
           "description" : EXPL_API_CTY_ID,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_CTY_NM,
           "description" : EXPL_API_CTY_NM,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_API_WTHR_TMPRTR,
           "description" : EXPL_API_WTHR_TMPRTR,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WTHR_DSCRPTN,
           "description" : EXPL_API_WTHR_DSCRPTN,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_API_WTHR_ICON,
           "description" : EXPL_API_WTHR_ICON,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_API_WTHR_PRSSR,
           "description" : EXPL_API_WTHR_PRSSR,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_API_WTHR_HMDTY,
           "description" : EXPL_API_WTHR_HMDTY,
           "type": TYPE_JSON_INTEGER 
         },
         { 
           "name" : JSON_API_WTHR_WND_SPD,
           "description" : EXPL_API_WTHR_WND_SPD,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WTHR_WND_DGRS,
           "description" : EXPL_API_WTHR_WND_DGRS,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WTHR_CLDS,
           "description" : EXPL_API_WTHR_CLDS,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_WTHR_WEATHER_ID,
           "description" : EXPL_API_WTHR_WEATHER_ID,
           "type": TYPE_JSON_NUMBER_INTEGER
         }
    ]
}

# status data
# SQL AS Reference
# select TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), CITY_ID, CITY, TEMPERATURE_MIN, TEMPERATURE_AVG, TEMPERATURE_MAX, 
# PRESSURE_MIN, PRESSURE_AVG, PRESSURE_MAX, HUMIDITY_MIN, HUMIDITY_AVG, HUMIDITY_MAX, WIND_SPEED_MIN, WIND_SPEED_AVG, WIND_SPEED_MAX, 
# WIND_DEGREE_MIN, WIND_DEGREE_AVG, WIND_DEGREE_MAX from
HELP_ROUTE_INDOOR_TEMPERATURE_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Indoor temperature data with a current(10sec), minute, hour, day, month or year interval that is ordered on timestamp.",
    "api_usage"         : "<ip>{" + ROUTE_INDOOR_TEMPERATURE + ', ' + ROUTE_INDOOR_TEMPERATURE_MIN + ', ' + ROUTE_INDOOR_TEMPERATURE_HOUR + ', ' + ROUTE_INDOOR_TEMPERATURE_DAY + ', ' + ROUTE_INDOOR_TEMPERATURE_MONTH + ', ' + ROUTE_INDOOR_TEMPERATURE_YEAR + '}?' + API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2018-01-03 12:03:55 or ' + API_PARAMETER_RANGETIMESTAMP + '=2020-01-03, <ip>{' + ROUTE_INDOOR_TEMPERATURE + ', ' + ROUTE_INDOOR_TEMPERATURE_MIN + ', ' + ROUTE_INDOOR_TEMPERATURE_HOUR + ', ' + ROUTE_INDOOR_TEMPERATURE_DAY + ', ' + ROUTE_INDOOR_TEMPERATURE_MONTH + ', ' + ROUTE_INDOOR_TEMPERATURE_YEAR + '},<ip>{' + ROUTE_INDOOR_TEMPERATURE_HELP + ', ' + ROUTE_INDOOR_TEMPERATURE_MIN_HELP + ', ' + ROUTE_INDOOR_TEMPERATURE_HOUR_HELP + ', ' + ROUTE_INDOOR_TEMPERATURE_DAY_HELP + ', ' + ROUTE_INDOOR_TEMPERATURE_MONTH_HELP + ', ' + ROUTE_INDOOR_TEMPERATURE_YEAR_HELP + '}',
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_RCRD_ID,
           "description" : EXPL_API_RM_TMPRTR_RCRD_ID,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_IN,
           "description" : EXPL_API_RM_TMPRTR_IN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_IN_L,
           "description" : EXPL_API_RM_TMPRTR_IN_L,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_IN_A,
           "description" : EXPL_API_RM_TMPRTR_IN_A,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_IN_H,
           "description" : EXPL_API_RM_TMPRTR_IN_H,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_OUT,
           "description" : EXPL_API_RM_TMPRTR_OUT,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_OUT_L,
           "description" : EXPL_API_RM_TMPRTR_OUT_L,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_OUT_A,
           "description" : EXPL_API_RM_TMPRTR_OUT_A,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_RM_TMPRTR_OUT_H,
           "description" : EXPL_API_RM_TMPRTR_OUT_H,
           "type": TYPE_JSON_NUMBER_INTEGER
         }
    ]
}

# status data
# SQL AS Reference
# select TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), CITY_ID, CITY, TEMPERATURE_MIN, TEMPERATURE_AVG, TEMPERATURE_MAX, 
# PRESSURE_MIN, PRESSURE_AVG, PRESSURE_MAX, HUMIDITY_MIN, HUMIDITY_AVG, HUMIDITY_MAX, WIND_SPEED_MIN, WIND_SPEED_AVG, WIND_SPEED_MAX, 
# WIND_DEGREE_MIN, WIND_DEGREE_AVG, WIND_DEGREE_MAX from
HELP_ROUTE_WATERMETER_MIN_HOUR_DAY_MONTH_YEAR_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_TEST,
    "api_options"       :  API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Historical watermeter data.",
    "api_usage"         : "<ip>{" + ROUTE_WATERMETER_MIN_V2 + ', ' + ROUTE_WATERMETER_HOUR_V2 + ', ' + ROUTE_WATERMETER_DAY_V2 + ', ' + ROUTE_WATERMETER_MONTH_V2 + ', ' + ROUTE_WATERMETER_YEAR_V2 + '}?' + API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2019-11-30 12:03:55, or ' + API_PARAMETER_RANGETIMESTAMP + '=2020-01-03, <ip>{' + ROUTE_WATERMETER_HOUR_V2 + ', ' + ROUTE_WATERMETER_DAY_V2 + ', ' + ROUTE_WATERMETER_MONTH_V2 + ', ' + ROUTE_WATERMETER_YEAR_V2 + '},<ip>{' + ROUTE_WATERMETER_HOUR_HELP_V2 + ', ' + ROUTE_WATERMETER_DAY_HELP_V2 + ', ' + ROUTE_WATERMETER_MONTH_HELP_V2 + ', ' +ROUTE_WATERMETER_MONTH_HELP_V2 + '}',
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PROD_PERIOD_ID,
           "description" : EXPL_API_PROD_PERIOD_ID,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_WM_PULS_CNT,
           "description" : EXPL_API_WM_PULS_CNT,
           "type": TYPE_JSON_INTEGER
         },
        { 
           "name" : JSON_API_WM_CNSMPTN_LTR ,
           "description" : EXPL_API_WM_CNSMPTN_LTR,
           "type": TYPE_JSON_NUMBER 
         },
         { 
           "name" : JSON_API_WM_CNSMPTN_LTR_M3,
           "description" : EXPL_API_WM_CNSMPTN_LTR_M3,
           "type": TYPE_JSON_NUMBER 
         }
         
    ]
}

#help data 
# SQL AS Reference
#sqlstr = "select TIMESTAMP, cast(strftime('%s',TIMESTAMP) as Integer), RECORD_VERWERKT, VERBR_KWH_181, VERBR_KWH_182, GELVR_KWH_281, \
#            GELVR_KWH_282, TARIEFCODE, ACT_VERBR_KW_170, ACT_GELVR_KW_270, VERBR_GAS_2421
HELP_ROUTE_PHASE_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP,
    "api_description"   : "The standardised and verified electric phase data that the smart meter can deliver. The content and Watt, Voltage and Amperage can differ depending on the type of smart meter. The number of entries returned is optional. Data is ordered on timestamp.",
    "api_usage"         : "<ip>" + ROUTE_PHASE + '?'+ API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2020-02-28 12:03:55, <ip>' + ROUTE_PHASE + ", <ip>" + ROUTE_PHASE_HELP,
    "fields": [
        {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
        },
        { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_CNSMPTN_L1_W,
           "description" : EXPL_API_PHS_CNSMPTN_L1_W,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_CNSMPTN_L2_W,
           "description" : EXPL_API_PHS_CNSMPTN_L2_W,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_CNSMPTN_L3_W,
           "description" : EXPL_API_PHS_CNSMPTN_L3_W,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_PRDCTN_L1_W,
           "description" : EXPL_API_PHS_PRDCTN_L1_W,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_PRDCTN_L2_W,
           "description" : EXPL_API_PHS_PRDCTN_L2_W,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_PRDCTN_L3_W,
           "description" : EXPL_API_PHS_PRDCTN_L3_W,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_L1_V ,
           "description" : EXPL_API_PHS_L1_V,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_PHS_L2_V ,
           "description" : EXPL_API_PHS_L2_V,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_PHS_L3_V ,
           "description" : EXPL_API_PHS_L3_V,
           "type": TYPE_JSON_NUMBER_INTEGER
        },
        { 
           "name" : JSON_API_PHS_L1_A,
           "description" : EXPL_API_PHS_L1_A,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_L2_A,
           "description" : EXPL_API_PHS_L2_A,
           "type": TYPE_JSON_INTEGER
        },
        { 
           "name" : JSON_API_PHS_L3_A,
           "description" : EXPL_API_PHS_L3_A,
           "type": TYPE_JSON_INTEGER
        }
    ]
}


HELP_ROUTE_POWER_PRODUCTION_MIN_DAY_MONTH_YEAR_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Power production data with an minute, day, month or year interval that is ordered on timestamp",
    "api_usage"         : "<ip>{"+ ROUTE_POWERPRODUCTION_S0_MIN + ', ' +  ROUTE_POWERPRODUCTION_S0_HOUR + ', ' + ROUTE_POWERPRODUCTION_S0_DAY + ', ' + ROUTE_POWERPRODUCTION_S0_MONTH + ', ' + ROUTE_POWERPRODUCTION_S0_YEAR + '}?' +\
                                  API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2020-25-10 10:21:55, or ' +\
                                  API_PARAMETER_RANGETIMESTAMP + '=2020-25-10, <ip>{'+ ROUTE_POWERPRODUCTION_S0_MIN + ROUTE_POWERPRODUCTION_S0_HOUR + ', ' + ROUTE_POWERPRODUCTION_S0_DAY + ', ' + ROUTE_POWERPRODUCTION_S0_MONTH + ', ' + ROUTE_POWERPRODUCTION_S0_YEAR  + '},<ip>{' + ROUTE_POWERPRODUCTION_S0_MIN_HELP + ', ' + ROUTE_POWERPRODUCTION_S0_HOUR_HELP + ', ' + ROUTE_POWERPRODUCTION_S0_DAY_HELP + ', ' + ROUTE_POWERPRODUCTION_S0_MONTH_HELP + ', ' + ROUTE_POWERPRODUCTION_S0_YEAR_HELP + '}',
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PROD_PERIOD_ID ,
           "description" : EXPL_API_PROD_PERIOD_ID ,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PROD_PWR_SRC_ID,
           "description" : EXPL_API_PROD_PWR_SRC_ID,
           "type": TYPE_JSON_INTEGER
         },
         {
           "name" : JSON_API_PROD_KWH_H,
           "description" : EXPL_API_PROD_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_KWH_L,
           "description" : EXPL_API_PROD_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_PULS_CNT_H,
           "description" : EXPL_API_PROD_PULS_CNT_H,
           "type": TYPE_JSON_INTEGER
        },
        {
           "name" : JSON_API_PROD_PULS_CNT_L,
           "description" : EXPL_API_PROD_PULS_CNT_L,
           "type": TYPE_JSON_INTEGER
         },
         {
           "name" : JSON_API_PROD_KWH_TOTAL_H,
           "description" : EXPL_API_PROD_KWH_TOTAL_H,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_KWH_TOTAL_L,
           "description" : EXPL_API_PROD_KWH_TOTAL_L,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_KWH_TOTAL,
           "description" : EXPL_API_PROD_KWH_TOTAL,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_W_PSEUDO,
           "description" : EXPL_API_PROD_W_PSEUDO,
           "type": TYPE_JSON_NUMBER
         }
    ]
}


HELP_ROUTE_POWER_PRODUCTION_SOLAR_MIN_DAY_MONTH_YEAR_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "Solar power production data with an minute, day, month or year interval that is ordered on timestamp. Data is built in to support multiple site id’s.  Each dataset starts with a number in de range 20 – 90 (the database ID),  see the configuration page. The tens represent the specific site and the units respectively minutes (1), hours (2), days (3), months (4) and years (5). Examples: site 1 minute value is 21, site 1 hour value is 22, site 2 minute value is 31, site 2 hour value is 32 etc.  The {power_source_id} is a number,  for example for Solar Edge this is 1",
    "api_usage"         : "<ip>{"+ ROUTE_POWERPRODUCTION_SOLAR_MIN + ', ' +  ROUTE_POWERPRODUCTION_SOLAR_HOUR + ', ' + ROUTE_POWERPRODUCTION_SOLAR_DAY + ', ' + ROUTE_POWERPRODUCTION_SOLAR_MONTH + ', ' + ROUTE_POWERPRODUCTION_SOLAR_YEAR + '}?' +\
                                  API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2020-25-10 10:21:55, or ' +\
                                  API_PARAMETER_RANGETIMESTAMP + '=2020-25-10, <ip>{'+ ROUTE_POWERPRODUCTION_SOLAR_MIN + ROUTE_POWERPRODUCTION_SOLAR_HOUR + ', ' + ROUTE_POWERPRODUCTION_SOLAR_DAY + ', ' + ROUTE_POWERPRODUCTION_SOLAR_MONTH + ', ' + ROUTE_POWERPRODUCTION_SOLAR_YEAR  + '},<ip>{' + ROUTE_POWERPRODUCTION_SOLAR_MIN_HELP + ', ' + ROUTE_POWERPRODUCTION_SOLAR_HOUR_HELP + ', ' + ROUTE_POWERPRODUCTION_SOLAR_DAY_HELP + ', ' + ROUTE_POWERPRODUCTION_SOLAR_MONTH_HELP + ', ' + ROUTE_POWERPRODUCTION_SOLAR_YEAR_HELP + '}',
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PROD_PERIOD_ID ,
           "description" : EXPL_API_PROD_PERIOD_ID_SOLAR ,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PROD_PWR_SRC_ID,
           "description" : EXPL_API_PROD_PWR_SRC_ID_SOLAR,
           "type": TYPE_JSON_INTEGER
         },
         {
           "name" : JSON_API_PROD_KWH_H,
           "description" : EXPL_API_PROD_KWH_H,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_KWH_L,
           "description" : EXPL_API_PROD_KWH_L,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_KWH_TOTAL_H,
           "description" : EXPL_API_PROD_KWH_TOTAL_H,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_KWH_TOTAL_L,
           "description" : EXPL_API_PROD_KWH_TOTAL_L,
           "type": TYPE_JSON_NUMBER
         },
         {
           "name" : JSON_API_PROD_KWH_TOTAL,
           "description" : EXPL_API_PROD_KWH_TOTAL,
           "type": TYPE_JSON_NUMBER
         }
    ]
}




#help data 
# SQL AS Reference
# select TIMESTAMP, cast(strftime('%s', TIMESTAMP, 'utc' ) AS Integer), MAX_VERBR_L1_KW * 1000,MAX_VERBR_L2_KW * 1000,MAX_VERBR_L3_KW * 1000,MAX_GELVR_L1_KW * 1000, MAX_GELVR_L2_KW * 1000,MAX_GELVR_L3_KW * 1000,MAX_L1_V,MAX_L2_V,MAX_L3_V,MAX_L1_A,MAX_L2_A,MAX_L3_A,MIN_VERBR_L1_KW * 1000,MIN_VERBR_L2_KW * 1000,MIN_VERBR_L3_KW * 1000, MIN_GELVR_L1_KW * 1000, MIN_GELVR_L2_KW * 1000, MIN_GELVR_L3_KW * 1000, MIN_L1_V,MIN_L2_V,MIN_L3_V,MIN_L1_A,MIN_L2_A,MIN_L3_A 
HELP_ROUTE_POWER_PHASE_MINMAX_DAY_JSON = {
    "api_version"       : 1,
    "api_status"        : API_STATUS_PRODUCTION,
    "api_options"       : API_OPTION_LIMIT + ', ' + API_OPTION_SORT_TIMESTAMP + ', ' + API_OPTION_JSON  + ', ' + API_OPTION_ROUND + ", " + API_OPTION_STARTTIMESTAMP + ", " + API_OPTION_RANGE,
    "api_description"   : "The maximum and minimum  values of the three phases (L1,L2,L3). ",
    "api_usage"         : "<ip>{"+ ROUTE_PHASE_MINMAX_DAY + '}?' +\
                                  API_PARAMETER_LIMIT +'=10&' + API_PARAMETER_SORT + '=asc&' + API_PARAMETER_JSON_TYPE + '=object&' + API_PARAMETER_ROUND + '=on&' + API_PARAMETER_STARTTIMESTAMP + '=2022-04-24 10:21:55, or ' +\
                                  API_PARAMETER_RANGETIMESTAMP + '=2020-04-24, <ip>{'+ ROUTE_PHASE_MINMAX_DAY + '},<ip>{' + ROUTE_PHASE_MINMAX_DAY_HELP + '}',
    "fields": [
         {
           "name" : JSON_TS_LCL,
           "description" : EXPL_TS_LCL,
           "type": TYPE_JSON_STRING
         },
         { 
           "name" : JSON_TS_LCL_UTC,
           "description" : EXPL_TS_LCL_UTC,
           "type": TYPE_JSON_INTEGER
         },
         { 
           "name" : JSON_API_PHS_CNSMPTN_L1_W_MAX ,
           "description" : EXPL_API_PHS_CNSMPTN_L1_W_MAX ,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         { 
           "name" : JSON_API_PHS_CNSMPTN_L2_W_MAX,
           "description" : EXPL_API_PHS_CNSMPTN_L2_W_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_CNSMPTN_L3_W_MAX,
           "description" : EXPL_API_PHS_CNSMPTN_L3_W_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_PRDCTN_L1_W_MAX,
           "description" : EXPL_API_PHS_PRDCTN_L1_W_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_PRDCTN_L2_W_MAX,
           "description" : EXPL_API_PHS_PRDCTN_L2_W_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_PRDCTN_L3_W_MAX,
           "description" : EXPL_API_PHS_PRDCTN_L3_W_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L1_V_MAX,
           "description" : EXPL_API_PHS_L1_V_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L2_V_MAX,
           "description" : EXPL_API_PHS_L2_V_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L3_V_MAX,
           "description" : EXPL_API_PHS_L3_V_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L1_A_MAX,
           "description" : EXPL_API_PHS_L1_A_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L2_A_MAX,
           "description" : EXPL_API_PHS_L2_A_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L3_A_MAX,
           "description" : EXPL_API_PHS_L3_A_MAX,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_CNSMPTN_L1_W_MIN,
           "description" : EXPL_API_PHS_CNSMPTN_L1_W_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_CNSMPTN_L2_W_MIN,
           "description" : EXPL_API_PHS_CNSMPTN_L2_W_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_CNSMPTN_L3_W_MIN,
           "description" : EXPL_API_PHS_CNSMPTN_L3_W_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_PRDCTN_L1_W_MIN,
           "description" : EXPL_API_PHS_PRDCTN_L1_W_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_PRDCTN_L2_W_MIN,
           "description" : EXPL_API_PHS_PRDCTN_L2_W_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_PRDCTN_L3_W_MIN,
           "description" : EXPL_API_PHS_PRDCTN_L3_W_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L1_V_MIN,
           "description" : EXPL_API_PHS_L1_V_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L2_V_MIN,
           "description" : EXPL_API_PHS_L2_V_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L3_V_MIN,
           "description" : EXPL_API_PHS_L3_V_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L1_A_MIN,
           "description" : EXPL_API_PHS_L1_A_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L2_A_MIN,
           "description" : EXPL_API_PHS_L2_A_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
         {
           "name" : JSON_API_PHS_L3_A_MIN,
           "description" : EXPL_API_PHS_L3_A_MIN,
           "type": TYPE_JSON_NUMBER_INTEGER
         },
    ]
}



