#!/usr/bin/python

import time
import os
import RPi.GPIO as GPIO

#PIN 18 is a white led "flash"
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18,0)
GPIO.output(18,1)
os.system(" raspistill -o /currentdata/cam.jpg --timeout 1 --nopreview -w 1024 -h 768 -q 33 -ex sports -hf")
GPIO.output(18,0)



