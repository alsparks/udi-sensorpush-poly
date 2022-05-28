
import os
import sys
import time
from pysensorpush import PySensorPush

username = 'asparks@doublesparks.net'
password = 'LZokrA9yRKGV'

sp = PySensorPush(username, password)

def makenodes ():
  sensors = sp.sensors()
  for sensorid, values in samples['sensors'].items():
    deviceid = sensorid.split('.')[0]


def poll ():
  samples = sp.samples()
  sensors = sp.sensors
  for sensorid, values in samples['sensors'].items():
    deviceid = sensorid.split('.')[0]
    battery = sensors[sensorid]['battery_voltage']
    name = sensors[sensorid]['name']
    rssi = sensors[sensorid]['rssi']
    type = sensors[sensorid]['type']
    temperature = values[0]['temperature']
    humidity = values[0]['humidity']
    print("   id {}, temp {}, hum {} bat {} rssi {} type {}".format(
      deviceid,temperature,humidity,battery,rssi,type,
    ))


while True:
  print(time.ctime())
  poll()
  print("")
  time.sleep(60)

