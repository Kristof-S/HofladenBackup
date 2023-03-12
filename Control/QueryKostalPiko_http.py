import requests
import json
from influxdb import InfluxDBClient
import time

IPWR = '192.168.2.2'; # IP der Photovoltaik-Anlage eintragen
URL = 'http://' + IPWR + '/api/dxs.json';

QCodes_DC = {
  33556736:'DCP',         # in W
  33555202:'DC1U',             # in V
  33555201:'DC1I',             # in A
  33555203:'DC1P',             # in W
  33555458:'DC2U',             # in V
  33555457:'DC2I',                # in A
  33555459:'DC2P',             # in W
  33555714:'DC3U',             # in V
  33555713:'DC3I',                # in A
  33555715:'DC3P',             # in W
}

QCodes_all = {
  # DC parameters
  33556736:'DCP',         # in W
  33555202:'DC1U',             # in V
  33555201:'DC1I',             # in A
  33555203:'DC1P',             # in W
  33555458:'DC2U',             # in V
  33555457:'DC2I',                # in A
  33555459:'DC2P',             # in W
  33555714:'DC3U',             # in V
  33555713:'DC3I',                # in A
  33555715:'DC3P',             # in W
  #Netz Netzparameter
  67109120:'ACP',     # in W
  67110400:'ACF',            # in Hz
  67110656:'ACcosPhi',
  #Netz Phase 1
  67109378:'AC1U',              # in V
  67109377:'AC1I',                 # in A
  67109379:'AC1P',              # in W
  #Netz Phase 2
  67109634:'AC2U',              # in V
  67109633:'AC2I',                 # in A
  67109635:'AC2P',              # in W
  #Netz Phase 3
  67109890:'AC3U',              # in V
  67109889:'AC3I',                 # in A
  67109891:'AC3P',               # in W
  #16780032:'Status',                  # 0:Off
  251658754:'Energy_d',               # in Wh
  #Statistik - Gesamt
  251658753:'Energy_tot',               # in kWh
  #'ID_Hausverbrauch_G':251659009:,        # in kWh
  #'ID_Eigenverbrauch_G':251659265,       # in kWh
  #'ID_Eigenverbrauchsquote_G':251659280, # in %
  #'ID_Autarkiegrad_G':251659281,         # in %
  #251658496:'OnTime',           # in h
}

QCodes_Integrated = {
  #16780032:'Status',                  # 0:Off
  251658754:'Energy_d',               # in Wh
  #Statistik - Gesamt
  251658753:'Energy_tot',               # in kWh
  #'ID_Hausverbrauch_G':251659009:,        # in kWh
  #'ID_Eigenverbrauch_G':251659265,       # in kWh
  #'ID_Eigenverbrauchsquote_G':251659280, # in %
  #'ID_Autarkiegrad_G':251659281,         # in %
  #251658496:'OnTime',           # in h
}

QCodes = {
  'ID_DCEingangGesamt':33556736,	 # in W
  'ID_Ausgangsleistung':67109120,        # in W
  'ID_Eigenverbrauch':83888128,          # in W
  'ID_Status':16780032,                  # 0:Off
  'ID_Ertrag_d':251658754,               # in Wh
  'ID_Hausverbrauch_d':251659010,        # in Wh
  'ID_Eigenverbrauch_d':251659266,       # in Wh
  'ID_Eigenverbrauchsquote_d':251659278, # in %
  'ID_Autarkiegrad_d':251659279,         # in %
  #Statistik - Gesamt
  'ID_Ertrag_G':251658753,               # in kWh
  'ID_Hausverbrauch_G':251659009,        # in kWh
  'ID_Eigenverbrauch_G':251659265,       # in kWh
  'ID_Eigenverbrauchsquote_G':251659280, # in %
  'ID_Autarkiegrad_G':251659281,         # in %
  'ID_Betriebszeit':251658496,           # in h
  #Momentanwerte - PV Generator
  'ID_DC1Spannung':33555202,             # in V
  'ID_DC1Strom':33555201,                # in A
  'ID_DC1Leistung':33555203,             # in W
  'ID_DC2Spannung':33555458,             # in V
  'ID_DC2Strom':33555457,                # in A
  'ID_DC2Leistung':33555459,             # in W
  'ID_DC3Spannung':33555714,             # in V
  'ID_DC3Strom':33555713,                # in A
  'ID_DC3Leistung':33555715,             # in W
  #Momentanwerte Haus
  'ID_HausverbrauchSolar':83886336,      # in W
  'ID_HausverbrauchBatterie':83886592,   # in W
  'ID_HausverbrauchNetz':83886848,       # in W
  'ID_HausverbrauchPhase1':83887106,     # in W
  'ID_HausverbrauchPhase2':83887362,     # in W
  'ID_HausverbrauchPhase3':83887618,     # in W
  #Netz Netzparameter
  'ID_NetzAusgangLeistung':67109120,     # in W
  'ID_NetzFrequenz':67110400,            # in Hz
  'ID_NetzCosPhi':67110656,
  #Netz Phase 1
  'ID_P1Spannung':67109378,              # in V
  'ID_P1Strom':67109377,                 # in A
  'ID_P1Leistung':67109379,              # in W
  #Netz Phase 2
  'ID_P2Spannung':67109634,              # in V
  'ID_P2Strom':67109633,                 # in A
  'ID_P2Leistung':67109635,              # in W
  #Netz Phase 3
  'ID_P3Spannung':67109890,              # in V
  'ID_P3Strom':67109889,                 # in A
  'ID_P3Leistung':67109891               # in W
}

def MakeRequestString(QCodes):
    requestString = URL
    first = True;
    for ID,Names in QCodes.items():
        if first:
            requestString += '?dxsEntries={}'.format(ID)
            first = False
        else:
            requestString += '&dxsEntries={}'.format(ID)
    return(requestString)

def GetValuesFromInverter(QCodes):
  ret = requests.get(MakeRequestString(QCodes))
  j = json.loads(ret.text)
  valueDict = {}
  for i in j["dxsEntries"]:
    valueDict[QCodes[i['dxsId']]] = i['value']
  return valueDict


###
# Retrieve values and uplaod to INFLIX
###
def ReadAndStoreValues():
    dbClient = InfluxDBClient(host='192.168.0.38', port=8086)
    print("Retrieving: values")
    valueDict = GetValuesFromInverter(QCodes_all)

    print("Influx upload: DC values")
    # Make Influx query
    dataINFLUX=[]
    dataINFLUX.append(
      "{measurement} DC_P={DCP},DC1_U={DCU1},DC1_I={DCI1},DC1_P={DC1P},DC2_U={DCU2},DC2_I={DCI2},DC2_P={DC2P},DC3_U={DCU3},DC3_I={DCI3},DC3_P={DC3P}"
      .format(measurement="WR_1",
              DCP=valueDict['DCP'],
              DCU1=valueDict['DC1U'], DCI1=valueDict['DC1I'], DC1P=valueDict['DC1P'],
              DCU2=valueDict['DC2U'], DCI2=valueDict['DC2I'], DC2P=valueDict['DC2P'],
              DCU3=valueDict['DC3U'], DCI3=valueDict['DC3I'], DC3P=valueDict['DC3P']
              ))

    if dbClient.write_points(dataINFLUX, database='PV', time_precision='s', batch_size=10001, protocol='line') != True:
        print("Error: Could not write to influxDB")


    #print("Retrieving: AC values")
    #valueDict = GetValuesFromInverter(QCodes_AC)
    # Make Influx query
    print("Influx upload: AC values")
    dataINFLUX=[]
    dataINFLUX.append(
      "{measurement} Energy_d={Energy_d},Energy_tot={Energy_tot},AC_P={ACP},AC_F={ACF},AC_cosPhi={ACcosPhi},AC1_U={ACU1},AC1_I={ACI1},AC1_P={AC1P},AC2_U={ACU2},AC2_I={ACI2},AC2_P={AC2P},AC3_U={ACU3},AC3_I={ACI3},AC3_P={AC3P}"
      .format(measurement="WR_1",
              Energy_d=valueDict['Energy_d'],Energy_tot=valueDict['Energy_tot'],
              ACP=valueDict['ACP'],ACF=valueDict['ACF'],ACcosPhi=valueDict['ACcosPhi'],
              ACU1=valueDict['AC1U'], ACI1=valueDict['AC1I'], AC1P=valueDict['AC1P'],
              ACU2=valueDict['AC2U'], ACI2=valueDict['AC2I'], AC2P=valueDict['AC2P'],
              ACU3=valueDict['AC3U'], ACI3=valueDict['AC3I'], AC3P=valueDict['AC3P']
              ))
    if dbClient.write_points(dataINFLUX, database='PV', time_precision='s', batch_size=10001, protocol='line') != True:
        print("Error: Could not write to influxDB")

    print("done")
if __name__ == "__main__":
  while(1):
    #try:
    ReadAndStoreValues()
    #except:
    #  print("Could not get Values")
    #  time.sleep(60)
    time.sleep(60)
