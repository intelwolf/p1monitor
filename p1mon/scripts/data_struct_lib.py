import apiconst
import const

kw_min_max_record = {
    'max_verbr_KW_170' : 0.0,
    'min_verbr_KW_170' : const.NOT_SET,
    'max_gelvr_KW_270' : 0.0,
    'min_gelvr_KW_270' : const.NOT_SET,
    'max_verbr_KW_170_change' : True,
    'min_verbr_KW_170_change' : True,
    'max_gelvr_KW_270_change' : True,
    'min_gelvr_KW_270_change' : True,
    'max_verbr_KW_170_timestamp' : '',
    'min_verbr_KW_170_timestamp' : '',
    'max_gelvr_KW_270_timestamp' : '',
    'min_gelvr_KW_270_timestamp' : ''
}

#############################################
# p1 status record, used for proces status  #
# and such. keeps status                    #
#############################################
p1_status_record = {
    'timestamp_last_insert'     : 0,             # UTC timestamp the last time a record was succesfully inserted into the SQL database.
    'p1_record_is_ok'           : 0,             # 0 last P1 telegram was not ok, 1 is ok.
    'gas_present_in_serial_data': False,         # is gas processing needed/possible.
    'g2h_previous_gas_value'    : const.NOT_SET, # gas
    'g2h_previous_timestamp'    : const.NOT_SET, # gas
    'p1_crc_check_is_on'        : True,          # P1 telegram check if CRC is valid on(True) or of(False)
    'gas_record_prefix_number'  : '1',           # Gas code prefix.
    'day_night_mode'            : 0,             # day/night country flag 0 is NL, 1 is Belgium.
    'last_crc_check_timestamp'  : 0,             # timestamp of last crc check.
    'crc_error_cnt'             : 0,             # number of crc error's until last reset.
    'dbx_utc_ok_timestamp'      : 0              # laatse keer dat een dbx message was send succesfull.
}

##########################################################
# p1_telegram_base_record                                #
#                                                        #
# codering meter standen Nederland.                      #
# 1.8.1 Meterstand dal/nacht voor verbruikte energie     #
# 1.8.2 Meterstand piek/dag voor verbruikte energie      #
# 2.8.1 Meterstand dal/nacht voor teruggeleverde energie #
# 2.8.2 Meterstand piek/dag voor teruggeleverde energie  #
##########################################################
p1_data_base_record = {
    'verbrk_kwh_181'            : const.NOT_SET,
    'verbrk_kwh_182'            : const.NOT_SET,
    'gelvr_kwh_281'             : const.NOT_SET,
    'gelvr_kwh_281'             : const.NOT_SET,
    'act_verbr_kw_170'          : const.NOT_SET,
    'act_gelvr_kw_270'          : const.NOT_SET,
    'gas_verbr_m3_2421'         : const.NOT_SET,
}

#############################################
# solar edge site id dict                   #
#############################################
solaredge_site_config = {
    'ID'          :int(0),  # SITE ID
    'DB_INDEX'    :int(0),  # Site id base number used in the SQL database every site has a base number starting from 20 to 90 supporting 8 sites.
    'DB_DELETE'   :False,   # Flag to remove data from the database (true means purge database)
    'SITE_ACTIVE' :False,   # If the site is active an will be processed into the database
    'START_DATE'  :'',      # The energy production start date of the site.
    'END_DATE'    :'',      # The energy production end date of the site.
}

#############################################
# basic data structure for Dropbox and UDP  #
# broadcast                                 #
#############################################
json_basic  = {
    apiconst.JSON_TS_LCL                : '',               # local time in format yyyy-mm-dd hh:mm:ss mkLocalTimeString()
    apiconst.JSON_TS_LCL_UTC            : '',               # utc timestamp getUtcTime()
    apiconst.JSON_API_API_STTS          : 'production',     # options are production=ok, test, deprecated = will be removed in future version.
    apiconst.JSON_API_VRSN              : const.API_BASIC_VERSION, # id /number will be used in file name.
    apiconst.JSON_API_CNSMPTN_KWH_L     : '',               # consumption of KWH during low (dal) period.
    apiconst.JSON_API_CNSMPTN_KWH_H     : '',               # consumption of KWH during high (piek) period.
    apiconst.JSON_API_PRDCTN_KWH_L      : '',               # production of KWH during low (dal) period.
    apiconst.JSON_API_PRDCTN_KWH_H      : '',               # production of KWH during high (piek) period.
    apiconst.JSON_API_TRFCD             : '',               # peak or low period.
    apiconst.JSON_API_CNSMPTN_KW        : '',               # the consumption in Watt now.
    apiconst.JSON_API_PRDCTN_KW         : '',               # the production in Watt now.
    apiconst.JSON_API_CNSMPTN_GAS_M3    : '',               # consumption of gas in M3.
    apiconst.JSON_API_SFTWR_VRSN        : const.P1_VERSIE,  # software version of P1 software
    apiconst.JSON_API_SYSTM_ID          : const.SYSTEM_ID_DEFAULT,# system ID that is hardware specfic and unique
    apiconst.JSON_API_RM_TMPRTR_IN      : '',               # room temperature input
    apiconst.JSON_API_RM_TMPRTR_OUT     : '',               # room temperature output
    apiconst.JSON_API_WM_CNSMPTN_LTR_M3 : '',               # consumption of water in M3.
    apiconst.JSON_API_VALID_DATA        : 'TRUE',           # used to flag the data good/complete enough to process, also used as a alive beacon and set to FALSE
    apiconst.JSON_API_FQDN              : ''                # Fully Qualified Domain Name for the remote inet access to the API
}

#############################################
# phase data record                         #
#############################################
phase_db_record = {
    'timestamp'          : "",
    'consumption_L1_kW'  : 0, 
    'consumption_L2_kW'  : 0,
    'consumption_L3_kW'  : 0,
    'production_L1_kW'   : 0,
    'production_L2_kW'   : 0,
    'production_L3_kW'   : 0,
    'L1_V'               : 0,
    'L2_V'               : 0,
    'L3_V'               : 0,
    'L1_A'               : 0,
    'L2_A'               : 0,
    'L3_A'               : 0,
}

#############################################
# config record for the speed of processing #
# P1 telegrams                              #
#############################################
p1_processing_speed = {
    'max_processing_speed'       : False,
    'max_days_db_data_retention' : 7
}