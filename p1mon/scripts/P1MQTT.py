# run manual with ./P1MQTT

#import argparse
import apiconst
import base64
import const
import crypto3
import inspect
import json
import logger
import signal
import sys
import sqldb
import time 
import os
import process_lib

import paho.mqtt.client as mqtt
from datetime import datetime

from util import setFile2user, getUtcTime

#const
MQTT_PREFIX         = 'p1monitor'

prgname             = 'P1MQTT'

config_db           = sqldb.configDB()
rt_status_db        = sqldb.rtStatusDb()
e_db_serial         = sqldb.SqlDb1()
watermeter_db       = sqldb.WatermeterDBV2()
weer_db             = sqldb.currentWeatherDB()
temperature_db      = sqldb.temperatureDB()
power_production_db = sqldb.powerProductionDB()
e_db_history_dag    = sqldb.SqlDb4()
e_db_financieel_dag = sqldb.financieelDb()

# Status velden.
# timestamp process gestart                           DB status index =  95
# timestamp laatste MQTT publish bericht verstuurd.   DB status index =  96

mqtt_client                     = None
mqtt_topics_smartmeter          = None
mqtt_topics_watermeter_minute   = None
mqtt_topics_watermeter_day      = None
mqtt_topics_weather             = None
mqtt_topics_indoor_temperature  = None
mqtt_topics_phase               = None
mqtt_topics_powerproduction     = None
mqtt_topics_powergas_day        = None
mqtt_topics_cost_day            = None

mqtt_para = {
    'clientname':'p1monitor',                       # client name DB config index 105
    'topicprefix':'p1montor',                       # Make the topic specific DB config index 106
    'brokeruser': None,                             # broker user name DB config index 107
    'brokerpassword': None,                         # broker password DB config index 108
    'brokerhost': "192.168.2.18",                   # IP or DNS name DB config index 109
    'brokerport': 1883,                             # IP port name DB config index 110
    'brokerkeepalive': 60,                          # TCP/IP session alive in seconds DB config index 111
    'protocol': mqtt.MQTTv311,                      # options available MQTTv31 = 3, MQTTv311 = 4 and MQTTv5 = 5 DB config index 112
    'qosglobal': 0,                                 # options are 0,1,2 QoS (Quality of Service) DB config index 113
    'smartmeterprocessedtimestamp': '',             # timestamp of latest time when the publish was performed.
    'watermeterprocessedtimestamp': '',             # timestamp of latest time when the publish was performed.
    'weatherprocessedtimestamp': '',                # timestamp of latest time when the publish was performed.
    'indoortemperatureprocessedtimestamp': '',      # timestamp of latest time when the publish was performed.
    'phaseprocessedtimestamp': '',                  # timestamp of latest time when the publish was performed.
    'powerproductionprocessedtimestamp': '',        # timestamp of latest time when the publish was performed.
    'powergasdayprocessedtimestamp': '',            # timestamp of latest time when the publish was performed.
    'costdayprocessedtimestamp': '',                # timestamp of latest time when the publish was performed.
    'brokerconnectionstatustext': 'onbekend',       # status of the broker connection, text
    'brokerconnectionisok': False,                  # status of the broker connection, flag
    'reconnecttimeoute': 30,                        # sleeptime before trying a reconnect.
    'smartmeterpublishisactive': False,             # publish on or off DB config index 114
    'watermeterpublishisactive': False,             # publish on or off DB config index 115
    'weatherpublishisactive': False,                # publish on or off DB config index 116
    'indoortemperaturepublishisactive': False,      # publish on or off DB config index 117
    'phasepublishisactive': False,                  # publish on or off DB config index 120
    'powerproductionpublishisactive': False,        # publish on or off DB config index 136
    'powergasdaypublishisactive': False,            # publish on or off DB config index 176
    'costdaypublishisactive': False,                # publish on or off DB config index 177
    'anypublishisactive': False,                    # publish on or off for all publish.
}

mqtt_payload_smartmeter = {
    0:  str( '' ),
    1:  int( 0 ),
    2:  float( 0 ),
    3:  float( 0 ),
    4:  float( 0 ),
    5:  float( 0 ),
    6:  float( 0 ),
    7:  float( 0 ),
    8:  float( 0 ),
    9:  str( '' ),
    10: int( 0 )
}

mqtt_payload_watermeter_minute = {
    0: str( '' ),
    1: int( 0 ),
    2: int( 0 ),
    3: float( 0 ),
    4: float( 0 )
}

mqtt_payload_watermeter_day = {
    0: str( '' ),
    1: int( 0 ),
    2: int( 0 ),
    3: float( 0 ),
    4: float( 0 )
}

mqtt_payload_weather = {
    0:  str( '' ),
    1:  int( 0 ),
    2:  int( 0 ),
    3:  str( '' ),
    4:  str( '' ),
    5:  str( '' ),
    6:  str( '' ),
    7:  int( 0 ),
    8:  int( 0 ),
    9:  float( 0 ),
    10: int( 0 ),
    11: int( 0 ),
    12: int( 0 ),
}

mqtt_payload_indoor_temperature = {
    0:  str( '' ),
    1:  int( 0 ),
    2:  float( 0 ),
    3:  float( 0 ),
    4:  float( 0 ),
    5:  float( 0 ),
    6:  float( 0 ),
    7:  float( 0 ),
}

mqtt_payload_phase = {
    0:  str( '' ),
    1:  int( 0 ),
    2:  float( 0 ),
    3:  float( 0 ),
    4:  float( 0 ),
    5:  float( 0 ),
    6:  float( 0 ),
    7:  float( 0 ),
    8:  float( 0 ),
    9:  float( 0 ),
    10: float( 0 ),
    11: int( 0 ),
    12: int( 0 ),
    13: int( 0 ),
}

mqtt_payload_powerproduction = {
    0: str( '' ),
    1: int( 0 ),
    2: float( 0 ),
    3: float( 0 ),
    4: int( 0 ),
    5: int( 0 ),
    6: float( 0 ),
    7: float( 0 ),
    8: float( 0 ),
    9: float( 0 )
}

mqtt_payload_powergasday = {
    0: str( '' ),
    1: int( 0 ),
    2: float( 0 ),
    3: float( 0 ),
    4: float( 0 ),
    5: float( 0 ),
    6: float( 0 ),
    7: float( 0 ),
    8: float( 0 ),
    9: float( 0 )
}

mqtt_payload_costday = {
    0: str( '' ),
    1: int( 0 ),
    2: float( 0 ),
    3: float( 0 ),
    4: float( 0 ),
    5: float( 0 ),
    6: float( 0 ),
    7: float( 0 )
}


def checkActiveState():
    global mqtt_para

    _id, parameter, _label = config_db.strget( 136, flog )
    if int(parameter) == 1:
        mqtt_para['powerproductionpublishisactive'] = True
    else:
        mqtt_para['powerproductionpublishisactive'] = False

    _id, parameter, _label = config_db.strget( 120, flog )
    if int(parameter) == 1:
        mqtt_para['phasepublishisactive'] = True
    else:
        mqtt_para['phasepublishisactive'] = False

    _id, parameter, _label = config_db.strget( 114, flog )
    if int(parameter) == 1:
        mqtt_para['smartmeterpublishisactive'] = True
    else:
        mqtt_para['smartmeterpublishisactive'] = False

    _id, parameter, _label = config_db.strget( 115, flog )
    if int(parameter) == 1:
        mqtt_para['watermeterpublishisactive'] = True
    else:
        mqtt_para['watermeterpublishisactive'] = False

    _id, parameter, _label = config_db.strget( 116, flog )
    if int(parameter) == 1:
        mqtt_para['weatherpublishisactive'] = True
    else:
        mqtt_para['weatherpublishisactive'] = False
    
    _id, parameter, _label = config_db.strget( 117, flog )
    if int(parameter) == 1:
        mqtt_para['indoortemperaturepublishisactive'] = True
    else:
        mqtt_para['indoortemperaturepublishisactive'] = False

    _id, parameter, _label = config_db.strget( 176, flog )
    if int(parameter) == 1:
        mqtt_para['powergasdaypublishisactive'] = True
    else:
        mqtt_para['powergasdaypublishisactive'] = False

    _id, parameter, _label = config_db.strget( 177, flog )
    if int(parameter) == 1:
        mqtt_para['costdaypublishisactive'] = True
    else:
        mqtt_para['costdaypublishisactive'] = False

    mqtt_para['anypublishisactive'] = (mqtt_para['smartmeterpublishisactive'] or mqtt_para['watermeterpublishisactive'] or \
        mqtt_para['weatherpublishisactive'] or mqtt_para['indoortemperaturepublishisactive'] or mqtt_para['phasepublishisactive'] or mqtt_para['powergasdaypublishisactive'] or mqtt_para['costdaypublishisactive'] )

    #print ( mqtt_para )
    
def setConfigFromDb():
    global mqtt_para, mqtt_topics_smartmeter, mqtt_topics_watermeter_minute, mqtt_topics_watermeter_day, mqtt_topics_weather, mqtt_topics_indoor_temperature, mqtt_topics_phase, mqtt_topics_powerproduction, mqtt_topics_powergas_day, mqtt_topics_cost_day

    try:
        _id, parameter, _label = config_db.strget( 105, flog )
        if parameter == None:
            parameter = ''
        mqtt_para['clientname'] = str(parameter).replace(" ", "")
       
        _id, parameter, _label = config_db.strget( 106, flog )
        if parameter == None:
            parameter = ''

        mqtt_para['topicprefix'] = str(parameter).replace(" ", "") # no whitespace in topic
        if len( mqtt_para['topicprefix'] ) < 1:
            mqtt_para['topicprefix'] = 'p1monitor' # topic may not start with a / this would happen with an empty topicprefix
        
        _id, parameter, _label = config_db.strget( 107, flog )
        mqtt_para['brokeruser'] = str(parameter)

        _id, parameter, _label = config_db.strget( 108, flog )
        if len(parameter) > 0:
            decoded_password = str( base64.standard_b64decode( crypto3.p1Decrypt( parameter, 'mqttclpw') ).decode('utf-8') )
            flog.debug( inspect.stack()[0][3] + " encoded password=" + parameter + " decoded password=" + decoded_password )
            mqtt_para['brokerpassword'] = decoded_password
        else:
             mqtt_para['brokerpassword'] = ''

        _id, parameter, _label = config_db.strget( 109, flog )
        mqtt_para['brokerhost'] = str(parameter).replace(" ", "") # no whitespace in hostname or IP

        _id, parameter, _label = config_db.strget( 110, flog )
        mqtt_para['brokerport'] = int( (parameter).replace(" ", "") ) # no whitespace in port number

        _id, parameter, _label = config_db.strget( 111, flog )
        mqtt_para['brokerkeepalive'] = int( (parameter).replace(" ", "") ) # no whitespace keep alive seconds.

        _id, parameter, _label = config_db.strget( 112, flog )
        mqtt_para['protocol'] = int ( (parameter).replace(" ", "") )# no whitespace number of version 
        mqtt_para['protocol'] = 4
       
        _id, parameter, _label = config_db.strget( 113, flog )
        mqtt_para['qosglobal'] = int( (parameter).replace(" ", "") ) # no whitespace QoS number

        flog.debug( inspect.stack()[0][3] + ": mqtt_para = " + str(mqtt_para) )

    except Exception as e:
        flog.warning( inspect.stack()[0][3]+ ": DB configuratie heeft een probeem -> " + str(e.args[0]) )

    # update the topics
    mqtt_topics_smartmeter = {
        0:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_TS_LCL.lower(),
        1:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_CNSMPTN_GAS_M3.lower(),
        3:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_CNSMPTN_KWH_H.lower(),
        4:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_CNSMPTN_KWH_L.lower(),
        5:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_CNSMPTN_KW.lower(),
        6:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_PRDCTN_KWH_H.lower(),
        7:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_PRDCTN_KWH_L.lower(),
        8:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_PRDCTN_KW.lower(),
        9:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_TRFCD.lower(),
        10: mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_SMARTMETER) + '/' + apiconst.JSON_API_REC_PRCSSD.lower(),
    }   

    mqtt_topics_watermeter_minute = {
        0: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/minute'.lower()  + '/' + apiconst.JSON_TS_LCL.lower(),
        1: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/minute'.lower()  + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/minute'.lower()  + '/' + apiconst.JSON_API_WM_PULS_CNT.lower(),
        3: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/minute'.lower()  + '/' + apiconst.JSON_API_WM_CNSMPTN_LTR.lower(),
        4: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/minute'.lower()  + '/' + apiconst.JSON_API_WM_CNSMPTN_LTR_M3.lower()
    }

    mqtt_topics_watermeter_day = {
        0: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/day'.lower()  + '/' + apiconst.JSON_TS_LCL.lower(),
        1: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/day'.lower()  + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/day'.lower()  + '/' + apiconst.JSON_API_WM_PULS_CNT.lower(),
        3: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/day'.lower()  + '/' + apiconst.JSON_API_WM_CNSMPTN_LTR.lower(),
        4: mqtt_para['topicprefix'] + '/' + apiconst.BASE_WATERMETER + '/day'.lower()  + '/' + apiconst.JSON_API_WM_CNSMPTN_LTR_M3.lower()
    }

    mqtt_topics_weather = {
        0:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_TS_LCL.lower(),
        1:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_CTY_ID.lower(),
        3:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_CTY_NM.lower(),
        4:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_TMPRTR.lower(),
        5:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_DSCRPTN.lower(),
        6:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_ICON.lower(),
        7:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_PRSSR.lower(),
        8:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_HMDTY.lower(),
        9:  mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_WND_SPD.lower(),
        10: mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_WND_DGRS.lower(),
        11: mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_CLDS.lower(),
        12: mqtt_para['topicprefix'] + '/' + os.path.basename(apiconst.ROUTE_WEATHER_CURRENT )  + '/' + apiconst.JSON_API_WTHR_WEATHER_ID.lower(),
    }

    mqtt_topics_indoor_temperature = {
        0:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_TS_LCL.lower(),
        1:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_API_RM_TMPRTR_IN_L.lower(),
        3:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_API_RM_TMPRTR_IN_A.lower(),
        4:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_API_RM_TMPRTR_IN_H.lower(),
        5:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_API_RM_TMPRTR_OUT_L.lower(),
        6:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_API_RM_TMPRTR_OUT_A.lower(),
        7:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_INDOOR + '/' + apiconst.JSON_API_RM_TMPRTR_OUT_H.lower(),
    }

    mqtt_topics_phase = {
        0:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_TS_LCL.lower(),
        1:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_CNSMPTN_L1_W.lower(),
        3:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_CNSMPTN_L2_W.lower(),
        4:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_CNSMPTN_L3_W.lower(),
        5:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_PRDCTN_L1_W.lower(),
        6:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_PRDCTN_L2_W.lower(),
        7:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_PRDCTN_L3_W.lower(),
        8:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_L1_V.lower(),
        9:  mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_L2_V.lower(),
        10: mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_L3_V.lower(),
        11: mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_L1_A.lower(),
        12: mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_L2_A.lower(),
        13: mqtt_para['topicprefix'] + '/' + os.path.basename( apiconst.ROUTE_PHASE )  + '/' + apiconst.JSON_API_PHS_L3_A.lower(),
    }

    mqtt_topics_powerproduction = {
        0:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_TS_LCL.lower(),
        1:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_KWH_H.lower(),
        3:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_KWH_L.lower(),
        4:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_PULS_CNT_H.lower(),
        5:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_PULS_CNT_L.lower(),
        6:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_KWH_TOTAL_H.lower(),
        7:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_KWH_TOTAL_L.lower(),
        8:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_KWH_TOTAL.lower(),
        9:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWERPRODUCTION_S0  + '/minute'.lower()  + '/' + apiconst.JSON_API_PROD_W_PSEUDO.lower(),
    }

    mqtt_topics_powergas_day = {
        0:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_TS_LCL.lower(),
        1:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_CNSMPTN_KWH_L.lower(),
        3:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_CNSMPTN_KWH_H.lower(),
        4:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_PRDCTN_KWH_L.lower(),
        5:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_PRDCTN_KWH_H.lower(),
        6:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_CNSMPTN_DLT_KWH.lower(),
        7:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_PRDCTN_DLT_KWH.lower(),
        8:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_CNSMPTN_GAS_M3.lower(),
        9:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_POWER_GAS + '/day'.lower()  + '/' + apiconst.JSON_API_CNSMPTN_GAS_DLT_M3.lower(),
    }

    mqtt_topics_cost_day = {
        0:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_TS_LCL.lower(),
        1:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_TS_LCL_UTC.lower(),
        2:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_API_FNCL_CNSMPTN_E_H.lower(),
        3:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_API_FNCL_CNSMPTN_E_L.lower(),
        4:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_API_FNCL_PRDCTN_E_H.lower(),
        5:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_API_FNCL_PRDCTN_E_L.lower(),
        6:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_API_FNCL_CNSMPTN_GAS.lower(),
        7:  mqtt_para['topicprefix'] + '/' + apiconst.BASE_FINANCIAL + '/day'.lower()  + '/' + apiconst.JSON_API_FNCL_CNSMPTN_WATER.lower()
    }


    #flog.info (inspect.stack()[0][3]+": MQTT parameters :" + str( mqtt_para ) )

# when the minimal set of broker parameters are set return True or False
def minimalBrokerSettingsAvailable():
    try:   
        if len( mqtt_para['brokerhost']) < 1:
            flog.debug( inspect.stack()[0][3] + ":broker host naam is niet gezet." )
            return False
        if mqtt_para['brokerport']  < 1:
            flog.debug(inspect.stack()[0][3]+":broker host poort is niet gezet.")
            return False
        flog.debug(inspect.stack()[0][3]+":broker host poort en naam zijn gezet.")
        return True
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": Broker parameters niet te lezen! " + +str(e.args[0]))
        return True # don't fail on checks

def Main(argv): 
    flog.info("Start van programma.")
    global mqtt_para, mqtt_client

    # makes link between ramdisk and www/json folder if the link not exits
    # prevents errors in console.log when MQTT is not active.
    make_json_topic_link()

    # open van config database
    try:
        config_db.init(const.FILE_DB_CONFIG,const.DB_CONFIG_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": database niet te openen(1)."+const.FILE_DB_CONFIG+") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_CONFIG_TAB+" succesvol geopend.")
  
    runCheck()

    # open van status database
    try:    
        rt_status_db.init(const.FILE_DB_STATUS,const.DB_STATUS_TAB)
    except Exception as e:
        flog.critical( inspect.stack()[0][3]+": Database niet te openen(2)."+const.FILE_DB_STATUS+") melding:"+str(e.args[0]) )
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_STATUS_TAB+" succesvol geopend.")

    # open van seriele database
    try:
        e_db_serial.init(const.FILE_DB_E_FILENAME ,const.DB_SERIAL_TAB)        
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + " database niet te openen(4)."+const.FILE_DB_E_FILENAME+") melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel "+const.DB_SERIAL_TAB+" succesvol geopend." )

    # open van watermeter database
    try:    
        watermeter_db.init( const.FILE_DB_WATERMETERV2, const.DB_WATERMETERV2_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(5)." + const.FILE_DB_WATERMETERV2 + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_WATERMETERV2_TAB + " succesvol geopend." )

    # open van weer database voor huidige weer
    try:
        weer_db.init(const.FILE_DB_WEATHER ,const.DB_WEATHER_TAB)
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(6)."+const.DB_WEATHER_TAB+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.debug(inspect.stack()[0][3]+": database tabel "+const.DB_WEATHER_TAB+" succesvol geopend.")

    # open van temperatuur database
    try:    
        temperature_db.init(const.FILE_DB_TEMPERATUUR_FILENAME ,const.DB_TEMPERATUUR_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": Database niet te openen(7)."+const.FILE_DB_TEMPERATUUR_FILENAME+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_TEMPERATUUR_TAB +" succesvol geopend.")
    
    # open van power production database
    try:    
        power_production_db.init( const.FILE_DB_POWERPRODUCTION , const.DB_POWERPRODUCTION_TAB, flog )
    except Exception as e:
        flog.critical( inspect.stack()[0][3] + ": Database niet te openen(8)." + const.FILE_DB_POWERPRODUCTION + " melding:" + str(e.args[0]) )
        sys.exit(1)
    flog.info( inspect.stack()[0][3] + ": database tabel " + const.DB_POWERPRODUCTION_TAB + " succesvol geopend." )

    # open van history database (dag interval)
    try:    
        e_db_history_dag.init( const.FILE_DB_E_HISTORIE, const.DB_HISTORIE_DAG_TAB )    
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(9)."+const.FILE_DB_E_HISTORIE+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel "+const.DB_HISTORIE_DAG_TAB+" succesvol geopend.")

    # open van financieel database (dag interval)
    try:
        e_db_financieel_dag.init( const.FILE_DB_FINANCIEEL ,const.DB_FINANCIEEL_DAG_TAB )
    except Exception as e:
        flog.critical(inspect.stack()[0][3]+": database niet te openen(10)."+const.FILE_DB_FINANCIEEL+") melding:"+str(e.args[0]))
        sys.exit(1)
    flog.info(inspect.stack()[0][3]+": database tabel " + const.DB_FINANCIEEL_DAG_TAB + " succesvol geopend." )

    # set proces gestart timestamp
    rt_status_db.timestamp( 95, flog )

    checkActiveState()
    setConfigFromDb()
    makeTopicJsonFile() 
   
    mqtt_para['brokerconnectionstatustext'] = "probeer met de broker een connectie op te bouwen"
    rt_status_db.strset( mqtt_para['brokerconnectionstatustext'], 97, flog )
    
    # INIT connect to the broker
    while True:

        runCheck()

        #flog.setLevel( logging.DEBUG )
        if minimalBrokerSettingsAvailable() == False:
            time.sleep(60) # wait on valid setting, quitely.
            setConfigFromDb()
            continue
        #flog.setLevel( logging.INFO )

        if initMttq() == False:
            flog.info( inspect.stack()[0][3] + ": connectie met broker gefaald, wacht " + \
                str(int(mqtt_para['reconnecttimeoute'])) + " seconden voor een nieuwe poging. " )
            time.sleep( int(mqtt_para['reconnecttimeoute']) )
            setConfigFromDb()
        else:
            flog.info( inspect.stack()[0][3] + ": initiele connectie met broker gereed." )
            break
    
    while True:

        if mqtt_para['brokerconnectionisok'] == False:  # try to reconnect 
            #flog.setLevel( logging.DEBUG )
            if minimalBrokerSettingsAvailable() == False:
                time.sleep(60) # wait on valid setting, quitely.
                setConfigFromDb()
                continue
            #flog.setLevel( logging.INFO )

            if ( getUtcTime()%int( mqtt_para['reconnecttimeoute'] ) ) == 0:
                if mqtt_client != None:
                    try:
                        flog.warning( inspect.stack()[0][3] + ": reconnecting()" )
                        mqtt_client.reconnect()
                    except Exception as e:
                        flog.error( inspect.stack()[0][3] + " reconnectie probleem ->" + str( e ) + " broker host = " + \
                            str(mqtt_para['brokerhost']) + " broker port = " + str(mqtt_para['brokerport']) )

        try:
            _id, parameter, _label = config_db.strget( 118, flog )
            flog.debug( inspect.stack()[0][3]+ ": DB configuratie flag = " + str(parameter) )
            if int(parameter) == 1: # do the changes.
                flog.info( inspect.stack()[0][3]+ ": MQTT configuratie wordt aangepast." )
                setConfigFromDb()
                closeMqtt()
                initMttq()
                checkActiveState() # controleer de DB op welke publish aan of uit staat
                makeTopicJsonFile()
                config_db.strset( '0',118, flog ) # reset config flag.
                flog.info( inspect.stack()[0][3]+ ": MQTT configuratie is aangepast." )
        except Exception as e:
            flog.warning( inspect.stack()[0][3]+ ": DB configuratie flag probleem -> " + str(e.args[0]) )
      
        if mqtt_para['brokerconnectionisok'] == True: 
            
            # smart meter processing
            try:
                #_id, parameter, _label = config_db.strget( 114, flog )
                if mqtt_para['smartmeterpublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 16, flog )
                    if ( mqtt_para['smartmeterprocessedtimestamp'] ) != timestamp:
                        getPayloadFromDB( mqtt_payload_smartmeter, e_db_serial )
                        if len( mqtt_payload_smartmeter[0] ) > 0: # only send when we have data
                            mqttPublish( mqtt_client, mqtt_topics_smartmeter,  mqtt_payload_smartmeter )
                            mqtt_para['smartmeterprocessedtimestamp'] = timestamp
            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij smartmeter publish van melding:"+str(e))


            #######################################################################
            # Important to determine if we have to send data the timestamp when   #
            # data is updated must be set in the status database by the process   #
            # responsible for the processing.                                     #
            # check the index in the lines like this                              #
            # _id, timestamp, _label, _security = rt_status_db.strget( xx, flog ) #
            #######################################################################

            # cost day processing
            try:
                if mqtt_para['costdaypublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 127, flog ) 
                    if ( mqtt_para['costdayprocessedtimestamp'] ) != timestamp:
                        getPayloadFromDB( mqtt_payload_costday, e_db_financieel_dag )
                        if len( mqtt_payload_costday[0] ) > 0: # only send when when we have data
                            mqttPublish( mqtt_client, mqtt_topics_cost_day,  mqtt_payload_costday )
                            mqtt_para['costdayprocessedtimestamp'] = timestamp
            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij financiele gegevens day publish van melding:" + str(e) )


            # powergas day processing
            try:
                if mqtt_para['powergasdaypublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 13, flog ) 
                    if ( mqtt_para['powergasdayprocessedtimestamp'] ) != timestamp:
                        getPayloadFromDB( mqtt_payload_powergasday, e_db_history_dag )
                        if len( mqtt_payload_powergasday[0] ) > 0: # only send when when we have data
                            mqttPublish( mqtt_client, mqtt_topics_powergas_day,  mqtt_payload_powergasday )
                            mqtt_para['powergasdayprocessedtimestamp'] = timestamp
            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij power gas day publish van melding:"+str(e))


            # watermeter processing
            try:
                if mqtt_para['watermeterpublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 90, flog )
                    if ( mqtt_para['watermeterprocessedtimestamp'] ) != timestamp:
                        # minute processing
                        getPayloadFromDB( mqtt_payload_watermeter_minute, watermeter_db , db_index = '11' )
                        if len( mqtt_payload_watermeter_minute[0] ) > 0: # only send when when we have data
                            mqttPublish( mqtt_client, mqtt_topics_watermeter_minute,  mqtt_payload_watermeter_minute )
                            mqtt_para['watermeterprocessedtimestamp'] = timestamp
                        # day processing 
                        getPayloadFromDB( mqtt_payload_watermeter_day, watermeter_db , db_index = '13' )
                        if len( mqtt_payload_watermeter_day[0] ) > 0: # only send when when we have data
                            mqttPublish( mqtt_client, mqtt_topics_watermeter_day,  mqtt_payload_watermeter_day )
                            mqtt_para['watermeterprocessedtimestamp'] = timestamp

            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij watermeter publish van melding:"+str(e))

            # weather processing
            try:
                if mqtt_para['weatherpublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 45, flog )
                    if ( mqtt_para['weatherprocessedtimestamp'] ) != timestamp:
                        getPayloadFromDB( mqtt_payload_weather, weer_db )
                        if len( mqtt_payload_weather[0] ) > 0: # only send when we have data
                            mqttPublish( mqtt_client, mqtt_topics_weather,  mqtt_payload_weather )
                            mqtt_para['weatherprocessedtimestamp'] = timestamp
            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij weer publish van melding:"+str(e))                

            # indoor temperature processing
            try:
                if mqtt_para['indoortemperaturepublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 58, flog )
                    if ( mqtt_para['indoortemperatureprocessedtimestamp'] ) != timestamp:
                        getPayloadFromDB( mqtt_payload_indoor_temperature, temperature_db, db_index = '11' )
                        if len( mqtt_payload_indoor_temperature[0] ) > 0: # only send when we have data
                            mqttPublish( mqtt_client, mqtt_topics_indoor_temperature,  mqtt_payload_indoor_temperature )
                            mqtt_para['indoortemperatureprocessedtimestamp'] = timestamp
            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij binnen temperatuur publish van melding:"+str(e))

            # powerproduction processing
            try:
                if mqtt_para['powerproductionpublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 109, flog )
                    if ( mqtt_para['powerproductionprocessedtimestamp'] ) != timestamp:
                        getPayloadFromDB( mqtt_payload_powerproduction, power_production_db )
                        if len( mqtt_payload_powerproduction[0] ) > 0: # only send when we have data
                            mqttPublish( mqtt_client, mqtt_topics_powerproduction,  mqtt_payload_powerproduction )
                            mqtt_para['powerproductionprocessedtimestamp'] = timestamp
            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij opgewekte energie publish van melding:"+str(e))

            # phase processing
            try:
                #_id, parameter, _label = config_db.strget( 117, flog )
                if mqtt_para['phasepublishisactive'] == True:  #is active
                    _id, timestamp, _label, _security = rt_status_db.strget( 106, flog )
                    if ( mqtt_para['phaseprocessedtimestamp'] ) != timestamp:
                        getPhasePayloadFromDB ( mqtt_payload_phase )
                        if len( mqtt_topics_phase[0] ) > 0: # only send when we have data
                            mqttPublish( mqtt_client, mqtt_topics_phase,  mqtt_payload_phase )
                            mqtt_para['phaseprocessedtimestamp'] = timestamp

            except Exception as e:
                flog.warning(inspect.stack()[0][3]+": onverwachte fout bij binnen fase publish van melding:"+str(e))  

        flog.debug( inspect.stack()[0][3] + ": sleeping... mqtt_para['brokerconnectionisok'] = "  +  str(mqtt_para['brokerconnectionisok']) )

        checkActiveState() # controleer de DB op welke publish aan of uit staat
        if mqtt_para['anypublishisactive'] == False: # ga in langzame modes als alle publish uit staat.
            runCheck()
            time.sleep( 30 ) #slow poll
        else:
            runCheck()
            time.sleep( 2 )


def make_json_topic_link():
    target    = "/p1mon/mnt/ramdisk/mqtt_topics.json"
    link_name = "/p1mon/www/json/mqtt_topics.json"

    if not os.path.isfile( target ):
        #if os.system( "touch " + target ) == 0:
        #    flog.info( inspect.stack()[0][3] + ": leeg " + target + " bestand gemaakt." )
        cmd = "touch " + target
        r = process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog 
        )
        if r[2] == 0:
            flog.info( inspect.stack()[0][3] + ": leeg " + target + " bestand gemaakt." )

    if not os.path.isfile( link_name ):
        #if os.system( "ln -s " + target + " " + link_name ) >0:
        #    flog.error( inspect.stack()[0][3] + ": link maken van " + link_name +  " gefaald" )
        #else: 
        #    flog.info( inspect.stack()[0][3] + ": link maken van " + link_name + " gelukt." )
        cmd = "ln -s " + target + " " + link_name
        r = process_lib.run_process( 
            cms_str = cmd,
            use_shell=True,
            give_return_value=True,
            flog=flog 
        )
        if r[2] > 0:
            flog.error( inspect.stack()[0][3] + ": link maken van " + link_name +  " gefaald" )
        else: 
            flog.info( inspect.stack()[0][3] + ": link maken van " + link_name + " gelukt." )

#####################################################################
# check if the programm is set as active otherwise stop the program #
#####################################################################
def runCheck():
    flog.debug( inspect.stack()[0][3] + ": start van programma run check.")
    #print ( int(time.time())%10 )
    if (int(time.time())%10) > 2:
        #print ("no check")
        return # only do a check every 10 seconds
    #print ("check")    
    _id, run_status, _label = config_db.strget( 135, flog )
    if int( run_status ) == 0: # stop process
        flog.info( inspect.stack()[0][3] + ": programma is niet als actief geconfigureerd, programma wordt gestopt.")
        stop()

def makeTopicJsonFile():
    list_of_topics = []
    if mqtt_para['smartmeterpublishisactive'] == True:
        topicToJson( mqtt_topics_smartmeter, list_of_topics )
    if mqtt_para['watermeterpublishisactive'] == True:
        topicToJson( mqtt_topics_watermeter_minute, list_of_topics )
        topicToJson( mqtt_topics_watermeter_day, list_of_topics )
    if mqtt_para['weatherpublishisactive'] == True:
        topicToJson( mqtt_topics_weather, list_of_topics ) 
    if mqtt_para['indoortemperaturepublishisactive'] == True:
        topicToJson( mqtt_topics_indoor_temperature, list_of_topics ) 
    if mqtt_para['phasepublishisactive'] == True:
        topicToJson( mqtt_topics_phase, list_of_topics )
    if mqtt_para['powerproductionpublishisactive'] == True:
        topicToJson( mqtt_topics_powerproduction, list_of_topics )
    if mqtt_para['powergasdaypublishisactive'] == True:
        topicToJson( mqtt_topics_powergas_day, list_of_topics )
    if mqtt_para['costdaypublishisactive'] == True:
        topicToJson( mqtt_topics_cost_day, list_of_topics )


    try:
        filename = const.FILE_MQTT_TOPICS
        flog.debug( inspect.stack()[0][3] + ": topics json output =" + json.dumps( list_of_topics , sort_keys=True ) + " naar bestand " + filename )
        with open( filename, 'w') as outfile:
            json.dump( sorted(list_of_topics), outfile, sort_keys=True )
        setFile2user( filename,'p1mon' ) # to make sure we can process the file
    except Exception as e:
        flog.error(inspect.stack()[0][3]+": wegschrijven data naar ramdisk is mislukt. melding:"+str(e.args[0]))

def topicToJson(topic, topic_list):
    try:
        for i in range(0 , len(topic) ):
            #flog.debug( inspect.stack()[0][3] + ": topic: " + topic[i] )
            topic_list.append( topic[i] )
    except Exception as e:
        flog.warning( inspect.stack()[0][3] + ": Topic file generatie fout -> " + str(e) )

def closeMqtt():
    global mqtt_client
    flog.debug( inspect.stack()[0][3] + ": start." )
    try:
        mqtt_client.disconnect()
        mqtt_client.loop_stop()
        mqtt_para['brokerconnectionisok'] = False
        mqtt_para['brokerconnectionstatustext'] = "connectie verbroken."
        rt_status_db.strset( mqtt_para['brokerconnectionstatustext'], 97, flog )
        return True
    except Exception as e:
        mqtt_para['brokerconnectionstatustext'] = " MQTT close fout -> " + str( e ) + " broker host = " +\
             str(mqtt_para['brokerhost']) + " broker port = " + str(mqtt_para['brokerport'])
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        rt_status_db.strset( mqtt_para['brokerconnectionstatustext'], 97, flog )
        return False

# the broker will auto reconnect 
def initMttq():
    global mqtt_client
    flog.debug( inspect.stack()[0][3] + ": start." )
    try:

        if mqtt_client != None:
            mqtt_client.disconnect()

        mqtt_client = mqtt.Client( 
            mqtt_para['clientname'] , 
            clean_session=True , 
            protocol = mqtt_para['protocol'] 
        )
        mqtt_client.on_connect    = on_connect
        mqtt_client.on_disconnect = on_disconnect 
        #mqtt_client.on_log        = on_log

        mqtt_client.username_pw_set(
            mqtt_para['brokeruser'], 
            mqtt_para['brokerpassword']
            )

        mqtt_client.connect(
            mqtt_para['brokerhost'], 
            mqtt_para['brokerport'], 
            mqtt_para['brokerkeepalive'], 
        )

        mqtt_client.loop_start()
        time.sleep(5) # make sure we have a connection that works.

        return True
    except Exception as e:
        mqtt_para['brokerconnectionstatustext'] = " MQTT startup fout -> " + str( e ) + " broker host = " +\
             str(mqtt_para['brokerhost']) + " broker port = " + str(mqtt_para['brokerport'])
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        rt_status_db.strset( mqtt_para['brokerconnectionstatustext'], 97, flog )
        mqtt_para['brokerconnectionisok'] = False
        return False

def on_disconnect(client, userdata, rc):
     global mqtt_para
     flog.debug( inspect.stack()[0][3] + ": on_disconnect = " + str(rc) )
     if int(rc) != 0:
        mqtt_para['brokerconnectionisok'] = False
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker onverwacht afgebroken.'
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        rt_status_db.strset( mqtt_para['brokerconnectionstatustext'], 97, flog)

def on_connect(client, userdata, flags, rc):
    flog.debug( inspect.stack()[0][3] + ": on_connect = " + str(rc) )
    checkBrokerConnection( rc )

def checkBrokerConnection( rc ):
    global mqtt_para
    
    flog.debug( inspect.stack()[0][3] + ": return code = " + str(rc) )
   
    if rc == mqtt.CONNACK_ACCEPTED: 
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker succesvol.'
        flog.info( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        mqtt_para['brokerconnectionisok'] = True
    elif rc == mqtt.CONNACK_REFUSED_PROTOCOL_VERSION:
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker gefaald, MQTT protocol wordt niet ondersteunt.'
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        mqtt_para['brokerconnectionisok'] = False
    elif rc == mqtt.CONNACK_REFUSED_IDENTIFIER_REJECTED:
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker gefaald, indentifier geweigerd.'
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        mqtt_para['brokerconnectionisok'] = False
    elif rc == mqtt.CONNACK_REFUSED_SERVER_UNAVAILABLE:
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker gefaald, server niet beschikbaar/bereikbaar.'
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        mqtt_para['brokerconnectionisok'] = False 
    elif rc == mqtt.CONNACK_REFUSED_BAD_USERNAME_PASSWORD:
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker gefaald, naam of wachtwoord niet correct of herkend.'
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        mqtt_para['brokerconnectionisok'] = False 
    elif rc == mqtt.CONNACK_REFUSED_NOT_AUTHORIZED:
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker maken is gefaald door een authenticatie fout, is naam en wachtwoord correct.'
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatustext'] )
        mqtt_para['brokerconnectionisok'] = False 
    else: 
        mqtt_para['brokerconnectionstatustext'] = 'connectie met broker maken is gefaald door een onbekende fout, return code ' + str(rc)
        flog.critical( inspect.stack()[0][3] + ": " + mqtt_para['brokerconnectionstatus'] )
        mqtt_para['brokerconnectionisok'] = False 

    rt_status_db.strset( mqtt_para['brokerconnectionstatustext'], 97, flog)

#def on_log( client, userdata, level, buf ):
#    print("log: ",buf)

# because of the multi records needed from the status DB a specfic function
def getPhasePayloadFromDB( mqtt_payload ):
    _id, mqtt_payload[ 0  ], _label, _security = rt_status_db.strget( 106, flog)
    datetime_object = datetime.strptime( mqtt_payload[ 0  ], '%Y-%m-%d %H:%M:%S' )
    unixtime = int( time.mktime( datetime_object .timetuple() ) )
    mqtt_payload[1] = str( unixtime )
    _id, mqtt_payload[ 2  ], _label, _security = rt_status_db.strget( 74,  flog) #L1 Watt consuption
    _id, mqtt_payload[ 3  ], _label, _security = rt_status_db.strget( 75,  flog) #L1 Watt consuption
    _id, mqtt_payload[ 4  ], _label, _security = rt_status_db.strget( 76,  flog) #L1 Watt consuption
    _id, mqtt_payload[ 5  ], _label, _security = rt_status_db.strget( 77,  flog) #L1 Watt production
    _id, mqtt_payload[ 6  ], _label, _security = rt_status_db.strget( 78,  flog) #L1 Watt production
    _id, mqtt_payload[ 7  ], _label, _security = rt_status_db.strget( 79,  flog) #L1 Watt production
    _id, mqtt_payload[ 8  ], _label, _security = rt_status_db.strget( 103, flog) #L1 Volt
    _id, mqtt_payload[ 9  ], _label, _security = rt_status_db.strget( 104, flog) #L1 Volt
    _id, mqtt_payload[ 10 ], _label, _security = rt_status_db.strget( 105, flog) #L1 Volt
    _id, mqtt_payload[ 11 ], _label, _security = rt_status_db.strget( 100, flog) #L1 Ampere
    _id, mqtt_payload[ 12 ], _label, _security = rt_status_db.strget( 101, flog) #L1 Ampere
    _id, mqtt_payload[ 13 ], _label, _security = rt_status_db.strget( 102, flog) #L1 Ampere
    #print  (mqtt_payload )

def getPayloadFromDB( mqtt_payload, database, db_index=None ):
    try:
        rec = database.select_one_record( db_index = db_index )
        flog.debug( inspect.stack()[0][3] + ": rec= " + str( rec ) )
        if rec != None:
            for i in range(0 , len(rec) ):
                mqtt_payload[i] = rec[i]
    except Exception as e:
        flog.warning( inspect.stack()[0][3]+": probleem met lezen van DB. " + str( e.args[0] ) )

def mqttPublish( client, topics,  payloads ):
    #print ( '#########')
    #print( payloads )
    #print ( '---------')
    #flog.setLevel( logging.DEBUG )
    flog.debug( inspect.stack()[0][3] + ": qos: " + str( mqtt_para['qosglobal']) )
    try:
        for i in range(0 , len(topics) ):
            flog.debug( inspect.stack()[0][3] + ": line: " + str(i) + " topic: " + topics[i] + " payload: " + str( payloads[ i ] ) )
            client.publish( topics[i], payload=payloads[i], qos=mqtt_para['qosglobal'] , retain=False )
        rt_status_db.timestamp( 96,flog ) # update the status db with the latest publish timestamp
    except Exception as e:
        mqtt_para['brokerconnectionstatustext'] = str( e.args[0] )
        flog.warning( inspect.stack()[0][3] + ": MQTT publish onverwachte fout -> " + mqtt_para['brokerconnectionstatustext'] )
        rt_status_db.strset( mqtt_para['brokerconnectionstatustext'], 97, flog)
    #flog.setLevel( logging.INFO )

def saveExit(signum, frame):
    stop()

def stop():
    global mqtt_client
    if mqtt_client != None:
         closeMqtt()
    signal.signal( signal.SIGINT, original_sigint )
    flog.info(inspect.stack()[0][3]+" SIGINT ontvangen, gestopt.")
    sys.exit(0)

#-------------------------------
if __name__ == "__main__":
    try:
        logfile = const.DIR_FILELOG + prgname + ".log" 
        setFile2user( logfile,'p1mon' )
        flog = logger.fileLogger( logfile,prgname )
        flog.setLevel( logger.logging.INFO )
        flog.consoleOutputOn( True )
    except Exception as e:
        print ( "critical geen logging mogelijke, gestopt.:" + str( e.args[0] ) )
        sys.exit(10) #  error: no logging check file rights

    original_sigint = signal.getsignal( signal.SIGINT )
    signal.signal( signal.SIGINT, saveExit )
    Main(sys.argv[1:])