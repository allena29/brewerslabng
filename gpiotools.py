import os
import time
import inspect

import sys

if os.path.exists("simulator"):
	import fakeRPi.GPIO as GPIO
else:
	import RPi.GPIO as GPIO

class gpiotools:


	def __init__(self):
		self.logging=3


		GPIO.setmode(GPIO.BOARD)
		GPIO.setwarnings(False)
	
		if os.path.exists("simulator"):
			self.simulator=True
		else:
			self.simulator=False

		self.PINS={
			'ssrZoneA':
				{'input':False, 'pin':19,
				 'setup':False,'inverse':False,'pup':True},
				# turns on/off power through the SSR
			'ssrZoneB':
				{'input':False, 'pin':23,
				 'setup':False,'inverse':False,'pup':True},
				# turns on/off power through the SSR
			'zoneA':
				{'input':False, 'pin':13,
				 'setup':False,'inverse':True,'pup':True},
				# turns on/off power through the SSR
			'zoneAuse':
				{'input':False, 'pin':10,
				 'setup':False,'inverse':True,'pup':True},
				# NO of the relay for HLT
				# NC of the relay for Boiler
			'extractor':
				{'input':False, 'pin':12,
				 'setup':False,'inverse':True,'pup':True},
			'pump':
				{'input':False, 'pin':16,
				 'setup':False,'inverse':True,'pup':True},
			'zoneB':
				{'input':False, 'pin':26,
				 'setup':False,'inverse':True,'pup':True},	
				# turns on/off power through the SSR
			'zoneBuse':
				{'input':False, 'pin':24,
				 'setup':False,'inverse':True,'pup':True},
				# NO of the relay for HLT
				# NC of the relay for Boiler
			'fermHeat':
				{'input':False, 'pin':22,
				 'setup':False,'inverse':True,'pup':True},
			'fermCool':
				{'input':False, 'pin':18,
				 'setup':False,'inverse':True,'pup':True},




		}


	def _log(self,msg,importance=1):
		if self.logging == 1:
			if importance > 0:
				syslog.syslog(syslog.LOG_DEBUG, msg)
		elif self.logging == 2:
			sys.stderr.write("%s\n" %(msg))
		elif self.logging == 3:
			if importance > 0 or ("%s" %(time.time())).split(".")[0][-3:] == "000":
				syslog.syslog(syslog.LOG_DEBUG, msg)
			sys.stderr.write("%s\n" %(msg))



	def outputHigh(self,pin="<null>"):
		self.output(pin,1)
		if self.simulator:
			o=open("tmpfs/pin%s" %(pin),"w")
			o.close()

	def setLow(self,pin="<null>"):
		self.output(pin,0)
		if self.simulator:
			try:
				os.remove("tmpfs/pin%s" %(pin))
			except:
				pass
	

	def output(self,pin,state=-1):

		if not self.PINS.has_key(pin):
			sys.stderr.write("pin %s does not exist state %s\n" %(pin,state))
		else:
			if not self.PINS[pin]['setup']:
				if self.PINS[pin]['input']:
					sys.stderr.write("pin %s set as an input pin\n" %(pin))
				else:	
					GPIO.setup( self.PINS[pin]['pin'], 0)


			if self.PINS[pin]['inverse']:
				if state == 1:
					state=0
				else:
					state=1
			GPIO.output( self.PINS[pin]['pin'],state)
			self.PINS[pin]['state']=state
			self._log("gpio.output %s %s" %(pin,state))
	
	def input(self,pin):
		if not self.PINS.has_key(pin):
			sys.stderr.write("pin %s does not exist\n" %(pin))
		else:
			if not self.PINS[pin]['setup']:
				if not self.PINS[pin]['input']:
					sys.stderr.write("pin %s set as an output pin\n" %(pin))
				else:	
					if self.PINS[pin]['pup']:
						GPIO.setup( self.PINS[pin]['pin'], 1,pull_up_down=GPIO.PUD_UP)
					else:
						GPIO.setup( self.PINS[pin]['pin'], 1)

			state=GPIO.input( self.PINS[pin]['pin'] )
			if self.PINS[pin]['inverse']:
				if state == True:
					return False
				else:
					return True

			self._log("gpio.input %s %s" %(pin,state))
			return state

	def dump(self):
		for pin in self.PINS:
			if self.PINS[pin]['input']:
				print pin, self.input(pin)
	
	def  waitForChange(self,pin):
		self.input(pin)
		startstate= GPIO.input( self.PINS[pin]['pin'] )
		newstate=startstate
		print "Startt State = ",startstate
		while newstate == startstate:
			newstate=GPIO.input(self.PINS[pin]['pin'])
			print newstate
			time.sleep(.1)
		
		
if __name__ == '__main__':
	gpio=gpiotools()
	o=gpio.output
	i=gpio.input
	for x in gpio.PINS:
		if gpio.PINS[x]['input']:
			print "i('%s',state)" %(x)
		else:
			print "o('%s',state)" %(x)
	
