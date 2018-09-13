#!/usr/bin/python

import time
import os
import RPi.GPIO as GPIO

#PIN 18 is a white led "flash"
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18,0)
GPIO.output(18,1)
os.system("sudo raspistill -o /currentdata/cam.jpg ")
GPIO.output(18,0)



