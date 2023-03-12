import smbus2
from influxdb import InfluxDBClient
import time


def run_sync_readData():
  dbClient = InfluxDBClient(host='localhost', port=8086)

  port = 1
  address = 0x44
  bus = smbus2.SMBus(port)

  # setup device and read values
  bus.write_i2c_block_data(address, 0x2C, [0x06])
  time.sleep(0.5)
  data = bus.read_i2c_block_data(0x44, 0x00, 6)
 
  # Convert the data
  temp = data[0] * 256 + data[1]
  cTemp = -45 + (175 * temp / 65535.0)
  humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
 
  # Output data to screen
  #print "Temperature in Celsius is : %.2f C" %cTemp
  #print "Relative Humidity is : %.2f %%RH" %humidity
  

  # the sample method will take a single reading and return a
  # compensated_reading object

  dataINFLUX=[] # this is an array of measurements to store in INFLUX
  dataINFLUX.append("{measurement} ID={sensorID},Temp={sensorTemp},RH={sensorRH},Pressure={sensorP}"
     .format(measurement="BME280", 
             sensorID=1, sensorTemp=cTemp, sensorRH=humidity, sensorP=0)) 
  if dbClient.write_points(dataINFLUX, database='Temperatures', time_precision='ms', batch_size=10000, protocol='line') != True:
    print("Error: Could not write to influxDB")
  # the compensated_reading class has the following attributes

if __name__ == "__main__":
  while(1):  
    run_sync_readData()
    time.sleep(10) 

