import paho.mqtt.client as mqtt
import json
import re
import socket
import subprocess
import time

import sys
import logging
logging.basicConfig(filename="temper2_impl.log", level=logging.INFO, filemode="w", format="%(asctime)s|%(process)d|%(levelname)s|%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logging.info("started")
log = logging.getLogger("temper2")

MAX_TEMP = 90.0

def read_config():
    with open("config.json") as config_file:
        data = json.load(config_file)
    return data

config = read_config()

log.setLevel(config["logLevel"])

client = mqtt.Client(config["mqtt"]["client"])
client.username_pw_set(username=config["mqtt"]["user"], password=config["mqtt"]["password"])
client.connect(config["mqtt"]["host"], config["mqtt"]["port"], keepalive=120)    

def init():
    log.debug("In beginConn") 
    #Need to get the device id of the Temper2 device: 0001:0004:01
    result = subprocess.run([config["hidQueryPath"],"-e"], stdout=subprocess.PIPE )

    deviceId = ""
    deviceIds = re.search(r"(.*?1) : 413d:2107.*", result.stdout.decode('utf-8'), re.M|re.I)
    if deviceIds:
        deviceId = deviceIds.group(1)
        log.warning("Temper2 - Found DeviceId {}".format(deviceId))
    else:
        log.warning("NO MATCH")
        raise Exception("No 413d:2107 device found.")

    return deviceId

def get_Temper2Reading(device_id):
    result = subprocess.run([config["hidQueryPath"], device_id,'0x01','0x80','0x33','0x01','0x00','0x00','0x00','0x00'], stdout=subprocess.PIPE)
    log.debug("Server Rack Temperature Script result is {}".format(result))  #'0001:0004:01'
    parts = result.stdout.decode('utf-8').split('\n')
    while '' in parts:
        parts.remove('')
    return parts

def calc_Temperature(parts):
    temperature_line = parts[len(parts) - 1].split(' ')
    # list looks like ['\t', '80', '01', '0a', '73', '', '', '4e', '20', '00', '00']
    # we want item 3 & 4 ('0a', '73')

    temp = ((int(temperature_line[3], 16) << 8 ) + int(temperature_line[4], 16)) / 100
    return temp 

def get_system_temperature():
    result = subprocess.run([config["systemTemperatureScript"]], stdout=subprocess.PIPE)
    log.debug("System Temperature Script result is {}".format(result))  # result is x86_pkg_temp  45.0\n, so need to grab the number only
    return convert_system_temperature_result(result.stdout.decode('utf-8'))

def convert_system_temperature_result(result):
    temp_string = result.split("  ") # 2 spaces
    return temp_string[1].split("\n")[0]

#Connect to USB
device_id = init()

client.loop_start()
while True:
    temp_parts = get_Temper2Reading(device_id)
    current_temperature = calc_Temperature(temp_parts)
    if current_temperature < MAX_TEMP:
        msg = '{{"temperature":{}}}'.format(current_temperature)
        client.publish(config["publishServerRackTemperatureTopic"], msg)
        log.debug("Published Server Rack Temperature {}".format(msg))
    else:
        # Sometimes the unit returns crazy values 328 deg celcius, for now we just log
        log.warning("Wrong Temperature reading [{}]".format(current_temperature))

    msg = '{{"temperature":{}}}'.format(get_system_temperature())
    client.publish(config["publishSystemTemperatureTopic"], msg)
    log.debug("Published System Temperature {}".format(msg))


    time.sleep(config["scanInterval"]) #In Seconds
