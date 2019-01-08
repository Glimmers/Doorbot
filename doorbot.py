#!/usr/bin/python3 -u

import RPi.GPIO as GPIO
import os
import fcntl
import time
import syslog
import atexit
import requests
import configparser
from datetime import datetime

noalertfile = '/home/doorbot/noalert'
pidfile = '/home/doorbot/doorbot.pid'

# Use pi pin numbers
GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor_pin, GPIO.IN)

# Pull and parse config file
config = configparser.ConfigParser()
config.read('doorbot.ini')

# Missing main section, bail
if 'Doorbot' not in config:
  raise Exception('Missing "Doorbot" section in doorbot.ini')

main_config = config['Doorbot']
use_camera = main_config.getboolean('UseCamera', False)

# We need to know what pin we're listening on
if 'sensorpin' not in main_config:
  raise Exception('Missing SensorPin definition in Doorbot section of doorbot.ini')

sensor_pin = main_config.getint('sensorpin')

if 'discordwebhook' not in main_config:
  raise Exception('Missing "DiscordWebhook" definition in Doorbot section of doorbot.ini')

discord_webhook = main_config.get('discordwebhook')
discord_uri = "https://discordapp.com/api/webhooks/" + discord_webhook

# Message to display when the bell is rung. If one's not provided, we give a generic
message = main_config.get('message', '@here Ding Dong')

# Build camera image path if we're set to use a camera
camera_image_uri=''

if use_camera:
  camera_config = config['Camera']

  # We need at least a host and a path for the camera, everything else can be either implied or skipped
  if 'host' not in camera_config:
    raise Exception('Missing "Host" definition in [Camera] section of doorbot.ini')

  if 'path' not in camera_config:
    raise Exception('Missing "Path" definition in [Camera] section of doorbot.ini')

  camera_protocol = camera_config.get('protocol', 'http')
  camera_host = camera_config.get('host')
  camera_path = camera_config.get('path')
  camera_user = camera_config.get('user', '')
  camera_pass = camera_config.get('pass', '')
  camera_hostpath = camera_host + camera_path
  camera_prot = camera_protocol + '://'

  if (camera_protocol != 'http' and camera_protocol != 'https'):
    raise Exception('Unable to handle Protocol ' + camera_protocol + ' . Valid protocols are http or https')

  # Assemble full uri based on provided info
  if (camera_user == ''):
    camera_image_uri = camera_prot + camera_hostpath
  elif (camera_pass == ''):
    camera_image_uri = camera_prot + camera_user + '@' + camera_hostpath
  else:
    camera_image_uri = camera_prot + camera_user + ':' + camera_pass + '@' + camera_hostpath

discord_json = """
{
    "content": "Camera view:",
    "embed": {
       "url": "attachment://doorbot.jpg"
    }
}
"""

camera_form = {
    'content':'Camera view:',
    'payload_json':discord_json
}

# Function for clearing the PID file on completion

def closePid(pidHandle):
    pidHandle.seek(0)
    pidHandle.truncate()
    fcntl.flock(pidHandle, fcntl.LOCK_UN)
    pidHandle.close()

# Lock the PID file to prevent multiple bot instances from running simultaneously
pid = str(os.getpid())
pidLock = open(pidfile, 'w') 
fcntl.flock(pidLock, fcntl.LOCK_EX | fcntl.LOCK_NB)
pidLock.write(pid)
pidLock.flush()
os.fsync(pidLock)

atexit.register(closePid, pidLock)

print("Now Waiting")

while (True):
  status = GPIO.wait_for_edge(sensor_pin, GPIO.RISING, timeout=1000)
  
  if status == sensor_pin:
    time.sleep(10.0/1000)
  
    # Debounce/deglitch filter to strip out false positives 
    if GPIO.input(sensor_pin) == False :
      time.sleep(10.0/1000)
      if GPIO.input(sensor_pin) == False :
        print(str(datetime.now()) + " -- " + "Glitch. Disregarding")
        continue

    # If we're not set to alert, don't send web alert, don't get camera image 
    if os.path.isfile(noalertfile) :
      print(str(datetime.now()) + " -- " + "Bell rang, alerts disabled")
      continue

    # Send doorbell alert
    doorbell_message = { 'content':message }
    response = requests.post(discord_uri, data = doorbell_message) 

    status = response.status_code
    msg = response.text

    print(str(datetime.now()) + " -- " + str(status) + ": " + msg)

    # If we're not using the camera, go back to waiting here
    if (use_camera == False):
      time.sleep(5)
      continue

    # Get jpeg from camera
    camera_response = requests.get(camera_image_uri)
    camera_image = camera_response.content

    # Assemble camera post
    camera_message = { 'content':'Camera view:' }
    camera_files = {'file':('doorbot.jpg', camera_image, 'image/jpeg', {'Expires': '0'})}

    response = requests.post(discord_uri, data = camera_message, files = camera_files) 
    status = response.status_code
    msg = response.text

    print(str(datetime.now()) + " -- " + str(status) + ": " + msg)
    time.sleep(5)

