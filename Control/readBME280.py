import smbus2
import bme280
from influxdb import InfluxDBClient
import time


def run_sync_readData():
  dbClient = InfluxDBClient(host='localhost', port=8086)

  port = 1
  address = 0x76
  bus = smbus2.SMBus(port)

  calibration_params = bme280.load_calibration_params(bus, address)

  # the sample method will take a single reading and return a
  # compensated_reading object
  data = bme280.sample(bus, address, calibration_params)

  dataINFLUX=[] # this is an array of measurements to store in INFLUX
  dataINFLUX.append("{measurement} ID={sensorID},Temp={sensorTemp},RH={sensorRH},Pressure={sensorP}"
     .format(measurement="BME280", 
             sensorID=1, sensorTemp=data.temperature, sensorRH=data.humidity, sensorP=data.pressure)) 
  if dbClient.write_points(dataINFLUX, database='Temperatures', time_precision='ms', batch_size=10000, protocol='line') != True:
    print("Error: Could not write to influxDB")
  # the compensated_reading class has the following attributes
  print(data.id)
  print(data.timestamp)
  print(data.temperature)
  print(data.pressure)
  print(data.humidity)

  # there is a handy string representation too
  print(data)

if __name__ == "__main__":
  while(1):  
    run_sync_readData()
    time.sleep(10) 

