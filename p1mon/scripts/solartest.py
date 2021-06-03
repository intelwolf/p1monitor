#!/usr/bin/python3

##########################
# solar edge test script #
##########################


############# TODO #############


import solaredge_lib as se

#solar = se.Solaredge("GYEU7C6QZ5D41OVSGWCR5IAY1YUK9XKD") #Timothy de Keulenaer 

solar = se.Solaredge("NKMF3HUPL2VIYKUSUUGKNDY20SXTH8T5", debug=True) #GWS65
site_id = 571918 #GWS65

#print( solar.get_site_list() )
""" output
[*] DEBUG :  https://monitoringapi.solaredge.com/sites/list {'api_key': 'NKMF3HUPL2VIYKUSUUGKNDY20SXTH8T5', 'size': 100, 'startIndex': 0, 'sortOrder': 'ASC', 'status': 'Active,Pending'}
{'sites': {'count': 1, 'site': [{'id': 571918, 'name': 'Scheppink - 11685', 'accountId': 31263, 'status': 'Active', 'peakPower': 3.6, 'lastUpdateTime': '2021-03-19', 'currency': 'EUR', 'installationDate': '2017-10-24', 'ptoDate': None, 'notes': '', 'type': 'Optimizers & Inverters', 'location': {'country': 'Netherlands', 'city': 'Zwolle', 'address': 'Veronicaweg 19', 'address2': '', 'zip': '8042 CD', 'timeZone': 'Europe/Amsterdam', 'countryCode': 'NL'}, 'primaryModule': {'manufacturerName': 'S-Energy', 'modelName': '300 mono percium', 'maximumPower': 300.0}, 'uris': {'DETAILS': '/site/571918/details', 'DATA_PERIOD': '/site/571918/dataPeriod', 'OVERVIEW': '/site/571918/overview'}, 'publicSettings': {'isPublic': False}}]}}
"""

#site_id_list = [ site_id , site_id ] #double of same id to test the data
#print( solar.get_data_periods( site_id_list) )
""" 
{'datePeriodList': {'count': 2, 'siteEnergyList': [{'siteId': 571918, 'dataPeriod': {'startDate': '2017-10-25', 'endDate': '2021-03-19'}}, {'siteId': 571918, 'dataPeriod': {'startDate': '2017-10-25', 'endDate': '2021-03-19'}}]}}
"""

#site_id_list = [ site_id , site_id ] #double of same id to test the data
#start_date = '2021-03-01' # encoding van het tijd helpt niet
#end_date   = '2021-03-19'
#print( solar.get_energy( site_id_list, start_date, end_date ) ) # default is day (max 1 year).
"""
{'sitesEnergy': {'timeUnit': 'DAY', 'unit': 'Wh', 'count': 2, 'siteEnergyList': [{'siteId': 571918, 'energyValues': {'measuredBy': 'INVERTER', 'values': [{'date': '2021-03-01 00:00:00', 'value': 6731.0}, {'date': '2021-03-02 00:00:00', 'value': 6956.0}, {'date': '2021-03-03 00:00:00', 'value': 3765.0}, {'date': '2021-03-04 00:00:00', 'value': 1301.0}, {'date': '2021-03-05 00:00:00', 'value': 6510.0}, {'date': '2021-03-06 00:00:00', 'value': 4734.0}, {'date': '2021-03-07 00:00:00', 'value': 2464.0}, {'date': '2021-03-08 00:00:00', 'value': 3092.0}, {'date': '2021-03-09 00:00:00', 'value': 1764.0}, {'date': '2021-03-10 00:00:00', 'value': 2163.0}, {'date': '2021-03-11 00:00:00', 'value': 3000.0}, {'date': '2021-03-12 00:00:00', 'value': 3747.0}, {'date': '2021-03-13 00:00:00', 'value': 4782.0}, {'date': '2021-03-14 00:00:00', 'value': 5182.0}, {'date': '2021-03-15 00:00:00', 'value': 4972.0}, {'date': '2021-03-16 00:00:00', 'value': 4577.0}, {'date': '2021-03-17 00:00:00', 'value': 4841.0}, {'date': '2021-03-18 00:00:00', 'value': 4513.0}, {'date': '2021-03-19 00:00:00', 'value': 1911.0}]}}, {'siteId': 571918, 'energyValues': {'measuredBy': 'INVERTER', 'values': [{'date': '2021-03-01 00:00:00', 'value': 6731.0}, {'date': '2021-03-02 00:00:00', 'value': 6956.0}, {'date': '2021-03-03 00:00:00', 'value': 3765.0}, {'date': '2021-03-04 00:00:00', 'value': 1301.0}, {'date': '2021-03-05 00:00:00', 'value': 6510.0}, {'date': '2021-03-06 00:00:00', 'value': 4734.0}, {'date': '2021-03-07 00:00:00', 'value': 2464.0}, {'date': '2021-03-08 00:00:00', 'value': 3092.0}, {'date': '2021-03-09 00:00:00', 'value': 1764.0}, {'date': '2021-03-10 00:00:00', 'value': 2163.0}, {'date': '2021-03-11 00:00:00', 'value': 3000.0}, {'date': '2021-03-12 00:00:00', 'value': 3747.0}, {'date': '2021-03-13 00:00:00', 'value': 4782.0}, {'date': '2021-03-14 00:00:00', 'value': 5182.0}, {'date': '2021-03-15 00:00:00', 'value': 4972.0}, {'date': '2021-03-16 00:00:00', 'value': 4577.0}, {'date': '2021-03-17 00:00:00', 'value': 4841.0}, {'date': '2021-03-18 00:00:00', 'value': 4513.0}, {'date': '2021-03-19 00:00:00', 'value': 1911.0}]}}]}}

### TWEEDE KEER de data wordt aangevuld voor het huidige uur
[*] DEBUG :  https://monitoringapi.solaredge.com/sites/571918,571918/energy {'api_key': 'NKMF3HUPL2VIYKUSUUGKNDY20SXTH8T5', 'startDate': '2021-03-01', 'endDate': '2021-03-19', 'timeUnit': 'DAY'}
{'sitesEnergy': {'timeUnit': 'DAY', 'unit': 'Wh', 'count': 2, 'siteEnergyList': [{'siteId': 571918, 'energyValues': {'measuredBy': 'INVERTER', 'values': [{'date': '2021-03-01 00:00:00', 'value': 6731.0}, {'date': '2021-03-02 00:00:00', 'value': 6956.0}, {'date': '2021-03-03 00:00:00', 'value': 3765.0}, {'date': '2021-03-04 00:00:00', 'value': 1301.0}, {'date': '2021-03-05 00:00:00', 'value': 6510.0}, {'date': '2021-03-06 00:00:00', 'value': 4734.0}, {'date': '2021-03-07 00:00:00', 'value': 2464.0}, {'date': '2021-03-08 00:00:00', 'value': 3092.0}, {'date': '2021-03-09 00:00:00', 'value': 1764.0}, {'date': '2021-03-10 00:00:00', 'value': 2163.0}, {'date': '2021-03-11 00:00:00', 'value': 3000.0}, {'date': '2021-03-12 00:00:00', 'value': 3747.0}, {'date': '2021-03-13 00:00:00', 'value': 4782.0}, {'date': '2021-03-14 00:00:00', 'value': 5182.0}, {'date': '2021-03-15 00:00:00', 'value': 4972.0}, {'date': '2021-03-16 00:00:00', 'value': 4577.0}, {'date': '2021-03-17 00:00:00', 'value': 4841.0}, {'date': '2021-03-18 00:00:00', 'value': 4513.0}, {'date': '2021-03-19 00:00:00', 'value': 2026.0}]}}, {'siteId': 571918, 'energyValues': {'measuredBy': 'INVERTER', 'values': [{'date': '2021-03-01 00:00:00', 'value': 6731.0}, {'date': '2021-03-02 00:00:00', 'value': 6956.0}, {'date': '2021-03-03 00:00:00', 'value': 3765.0}, {'date': '2021-03-04 00:00:00', 'value': 1301.0}, {'date': '2021-03-05 00:00:00', 'value': 6510.0}, {'date': '2021-03-06 00:00:00', 'value': 4734.0}, {'date': '2021-03-07 00:00:00', 'value': 2464.0}, {'date': '2021-03-08 00:00:00', 'value': 3092.0}, {'date': '2021-03-09 00:00:00', 'value': 1764.0}, {'date': '2021-03-10 00:00:00', 'value': 2163.0}, {'date': '2021-03-11 00:00:00', 'value': 3000.0}, {'date': '2021-03-12 00:00:00', 'value': 3747.0}, {'date': '2021-03-13 00:00:00', 'value': 4782.0}, {'date': '2021-03-14 00:00:00', 'value': 5182.0}, {'date': '2021-03-15 00:00:00', 'value': 4972.0}, {'date': '2021-03-16 00:00:00', 'value': 4577.0}, {'date': '2021-03-17 00:00:00', 'value': 4841.0}, {'date': '2021-03-18 00:00:00', 'value': 4513.0}, {'date': '2021-03-19 00:00:00', 'value': 2026.0}]}}]}}
"""

site_id_list = [ site_id , site_id ] #double of same id to test the data
start_date = "2021-03-18"
end_date   = "2021-03-19"
print( solar.get_energy( site_id_list, start_date, end_date , "QUARTER_OF_AN_HOUR" ) ) # default is day (max 1 year).
#print( solar.get_energy( site_id_list, start_date, end_date , "HOUR" ) )
#print( solar.get_energy( site_id_list, start_date, end_date , "DAY" ) )
#print( solar.get_energy( site_id_list, start_date, end_date , "MONTH" ) )
#print( solar.get_energy( site_id_list, start_date, end_date , "YEAR" ) )

"""
https://monitoringapi.solaredge.com/sites/571918,571918/energy?api_key=NKMF3HUPL2VIYKUSUUGKNDY20SXTH8T5&startDate=2021-03-18&endDate=2021-03-19&timeUnit=YEAR
{'sitesEnergy': {'timeUnit': 'YEAR', 'unit': 'Wh', 'count': 2, 'siteEnergyList': [{'siteId': 571918, 'energyValues': {'measuredBy': 'INVERTER', 'values': [{'date': '2021-01-01 00:00:00', 'value': 180399.0}]}}, {'siteId': 571918, 'energyValues': {'measuredBy': 'INVERTER', 'values': [{'date': '2021-01-01 00:00:00', 'value': 180399.0}]}}]}}
"""

#werkt
#https://monitoringapi.solaredge.com/sites/571918,571918/power?startTime=2019-03-19%2011:00:00&endTime=2019-03-19%2013:00:00&api_key=NKMF3HUPL2VIYKUSUUGKNDY20SXTH8T5