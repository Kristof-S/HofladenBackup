from influxdb import InfluxDBClient
import urllib
import time
import datetime


#Temperature setting
targetTempLager = 4.0
targetTempHofladen = 3.3

# Humidity settings
humidityLow = 85.0
humidityHigh = 94.0

# disable some parts of the logic
doHumidifier = True 

# some definitions
turnHeatingON = "http://192.168.0.38/House/SetAction.php?ToggleActuator=1&State=ON"
turnHeatingOFF = "http://192.168.0.38/House/SetAction.php?ToggleActuator=1&State=OFF"

turnHeatingLagerON = "http://192.168.0.38/House/SetAction.php?ToggleActuator=2&State=ON"
turnHeatingLagerOFF = "http://192.168.0.38/House/SetAction.php?ToggleActuator=2&State=OFF"

turnHumidifierLagerON = "http://192.168.0.38/House/SetAction.php?ToggleActuator=4&State=ON"
turnHumidifierLagerOFF = "http://192.168.0.38/House/SetAction.php?ToggleActuator=4&State=OFF"

turnVentLagerON = "http://192.168.0.38/House/SetAction.php?ToggleActuator=3&State=ON"
turnVentLagerOFF = "http://192.168.0.38/House/SetAction.php?ToggleActuator=3&State=OFF"

client = InfluxDBClient(host='localhost', port=8086)

SensorHofladen = "0x28ffd37d94164fc"
SensorDraussen = "0x28fff1e6c01758d"

def DEBUG(message):
    # return
    print(message)

def GetTemp(sensor):
    result = client.query("SELECT value FROM Temperatures.autogen.temperature WHERE Sensor = '{}' ORDER BY time DESC LIMIT 1".format(sensor))
    values = result.get_points()
    temp = 0
    t = datetime.datetime.now()
    for item in values:
        temp = item["value"]
        t = datetime.datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%SZ") 
    return {"time" : t, "Temp" : temp}
    
def checkTempLager():
    result = client.query("SELECT * FROM Temperatures.autogen.BME280 WHERE ID = 1 ORDER BY time DESC LIMIT 1")
    values = result.get_points()

    data = next(values)
    print (data)

    timeDiff = datetime.datetime.utcnow() - datetime.datetime.strptime(data["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
    if timeDiff.total_seconds() > 15*60:
        print ("WARNING: latest measurement is more than 15 min old! Ignoring and turning all OFF")
        urllib.request.urlopen(turnHeatingLagerOFF)
        urllib.request.urlopen(turnVentLagerOFF)
        urllib.request.urlopen(turnHumidifierLagerOFF)
        return

    if data["Temp"] < targetTempLager - 0.5:
        print ("INFO: Temp Low -> Heating ON")
        urllib.request.urlopen(turnHeatingLagerON)
    elif data["Temp"] > targetTempLager + 0.2:
        print ("INFO: Temp OK -> Heating OFF")
        urllib.request.urlopen(turnHeatingLagerOFF)

    # Humidity
    isOnHumidifier = False
    if doHumidifier:
        isOnHumidifier = True
        if data["RH"] < humidityLow:
            print ("INFO: Humidity Low: {:.1f} -> Humidifier ON".format(data["RH"]))
            urllib.request.urlopen(turnHumidifierLagerON)
            isOnHumidifier = True
        if data["RH"] > humidityHigh:
            print ("INFO: Humidity OK: {:.1f} -> Humidifier OFF".format(data["RH"]))
            urllib.request.urlopen(turnHumidifierLagerOFF)
            isOnHumidifier = False

    # Ventillation: turn on if colder outside by at least 2C. Hysteresis for turning OFF: 1C
    # TODO: add time constraints 
    outsideTemp = GetTemp(SensorDraussen)
    if data["Temp"] > outsideTemp["Temp"]+2.0 and data["Temp"] > 7.0: # and isOnHumidifier == False:
        print("INFO: Truning Ventillation ON")
        urllib.request.urlopen(turnVentLagerON)
    elif data["Temp"] < outsideTemp["Temp"] + 1.0: # or isOnHumidifier == True:
        print("INFO: Truning Ventillation OFF")
        urllib.request.urlopen(turnVentLagerOFF)

    

def checkTempHofladen():
    result = client.query("SELECT value FROM Temperatures.autogen.temperature WHERE Sensor = '{}' ORDER BY time DESC LIMIT 1".format(SensorHofladen))
    values = result.get_points()
    temp = 0
    for item in values:
        temp = item["value"]

    print(temp)

    if temp > targetTempHofladen + 0.3:
        print("Turning heating OFF")
        urllib.request.urlopen(turnHeatingOFF)  
    elif temp < targetTempHofladen - 0.3:
        print("turning heating ON")
        urllib.request.urlopen(turnHeatingON)

while True:
    DEBUG("check temp in Lager")
    checkTempLager()
    DEBUG("check temp in Hofladen")
    checkTempHofladen()
    DEBUG("Sleeping ...")
    time.sleep(60)
