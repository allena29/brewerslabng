#!/usr/bin/python
from gpiotools import gpiotools
print "shutting down relays"
gpio=gpiotools()
gpio.output('fermHeat',0)
gpio.output('fermCool',0)
gpio.output('pump',0)
gpio.output('extractor',0)
gpio.output('ssrZoneA',0)
gpio.output('ssrZoneB',0)
gpio.output('tempProbes',0)
