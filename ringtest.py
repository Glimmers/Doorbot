#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

outpin = 35

GPIO.setmode(GPIO.BOARD)
GPIO.setup(outpin, GPIO.OUT)

print("Bringing pin high")
GPIO.output(outpin, GPIO.HIGH)

time.sleep(.5)

print("Bringing pin low")
GPIO.output(outpin, GPIO.LOW)

GPIO.cleanup(outpin)

