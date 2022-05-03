'''
Weather-logging MicroPython script for Raspberry Pico and BME280 sensor

Logs timestamped readings of temperature in celsius, humidity percentage,
and air pressure in hPa to a CSV file

Use config.json to change filename, log frequency and hardware settings

Note that because the Pico does not have a real-time clock, UTC timestamp
always starts at 1609459201 on battery power
'''

import bme280
import json
import machine
import os
import time

config = json.load(open('config.json'))
filename = config['filename'] + '.csv'

# Set up hardware config and create sensor reader
i2c = machine.I2C(id=config['i2c_bus_id'],
                  scl=machine.Pin(config['scl_pin']),
                  sda=machine.Pin(config['sda_pin']))
bme = bme280.BME280(i2c=i2c)
led = machine.Pin(25, machine.Pin.OUT)

# Discard erroneous initial reading
bme.read_compensated_data()

# Sleep for a millisecond to prevent further bad readings
time.sleep(.01)

# Create file and write headers if file doesn't already exist
if filename not in os.listdir():
    with open(filename, 'w') as file:
        file.write('Timestamp, Temperature, Pressure, Humidity\n')

while True:
    # If current second is zero
    if time.localtime()[5] == 0:
        timestamp = time.time()
        
        # Take reading and apply conversions
        t, p, h = bme.read_compensated_data()
        temperature = t / 100
        pressure = p // 256 / 100
        humidity = round(h / 1024, 2)
        
        
        # Append row to CSV file
        with open(filename, 'a') as file:
            file.write('{}, {}, {}, {}\n'.format(timestamp, temperature,
                                                 pressure, humidity))
            
        # Blink LED after log
        led.value(1)
        time.sleep(.25)
        led.value(0)
    
        time.sleep(config['minutes_between_logs'] * 60 - 1)