import time
import inspect
import os
import sys

if os.path.exists("simulator"):
	import fakeRPi.GPIO as GPIO
else:
	import RPi.GPIO as GPIO

class gpiotools:


	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		print GPIO.RPI_REVISION
		print GPIO.VERSION

		self.PINS={
			'tBacklight' : {'input':False,'pin':11,'setup':False,'inverse':False,'pup':False},
			'pLeft' : {'input':True,'pin':10,'setup':False,'inverse':True,'pup':True},
			'pRight' : {'input':True,'pin':9,'setup':False,'inverse':True,'pup':True}, 
			'pOk' : {'input':True,'pin':27,'setup':False,'inverse':True,'pup':True}, 		
			'pRotaryB' : {'input':True,'pin':22,'setup':False,'inverse':True,'pup':True}, 
			'pRotaryA' : {'input':True,'pin':17,'setup':False,'inverse':True,'pup':True}, 		

		}


	def outputHigh(self,pin="<null>"):
		self.output(pin,1)

	def setLow(self,pin="<null>"):
		self.output(pin,0)

	

	def output(self,pin,state=-1):

		if not self.PINS.has_key(pin):
			sys.stderr.write("pin %s does not exist\n" %(pin))
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

			if os.path.exists("ipc/manual_%s" %(pin)):
				os.unlink("ipc/manual_%s" %(pin))
				print "file existed returning True"
				return True
			state=GPIO.input( self.PINS[pin]['pin'] )
#			print "RAW STATE",self.PINS[pin]['pin'],state	
			if self.PINS[pin]['inverse']:
				if state == True:
					return False
				else:
					return True
			return state
	
	def  waitForState(self,pin,stateRequired=False):
		while True:
			if self.input(pin) == stateRequired:
				return
			time.sleep(0.1)
		
	
	def  waitForChange(self,pin):
		self.input(pin)
		startstate= GPIO.input( self.PINS[pin]['pin'] )
		newstate=startstate
		print "Startt State = ",startstate
		while newstate == startstate:
			newstate=GPIO.input(self.PINS[pin]['pin'])
			print newstate
			time.sleep(.1)
		



 
class RotaryEncoder: 

# adapted from http://www.bobrathbone.com/raspberrypi/Raspberry%20Rotary%20Encoders.pdf
#	(
# Author : Bob Rathbone 
# Site : http://www.bobrathbone.com
 
	CLOCKWISE=1 
	ANTICLOCKWISE=2 
	BUTTONDOWN=3 
	BUTTONUP=4 

	rotary_a = 0 
	rotary_b = 0 
	rotary_c = 0 
	last_state = 0 
	direction = 0 

	# Initialise rotary encoder object 
	def __init__(self,callback): 
		self.pinA = 13 
		self.pinB =11
#		self.button=15
		self.callback = callback 
		GPIO.setmode(GPIO.BOARD) 

		self.left=0
		self.right=0
		# The following lines enable the internal pull-up resistors 
		# on version 2 (latest) boards 
		GPIO.setwarnings(False) 
		GPIO.setup(self.pinA, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
		GPIO.setup(self.pinB, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
		#GPIO.setup(self.button, GPIO.IN, pull_up_down=GPIO.PUD_UP
		
		 # Add event detection to the GPIO inputs 
		GPIO.add_event_detect(self.pinA, GPIO.FALLING, callback=self.switch_event) 
		GPIO.add_event_detect(self.pinB, GPIO.FALLING, callback=self.switch_event) 
		return 

	# Call back routine called by switch events 
	def switch_event(self,switch): 
		if GPIO.input(self.pinA):
			self.rotary_a = 1 
		else: 
			self.rotary_a = 0 

		if GPIO.input(self.pinB): 
			self.rotary_b = 1 
		else: 
			self.rotary_b = 0 

		self.rotary_c = self.rotary_a ^ self.rotary_b 
		new_state = self.rotary_a * 4 + self.rotary_b * 2 + self.rotary_c * 1 
		delta = (new_state - self.last_state) % 4 
		self.last_state = new_state 
		event = 0 

		if delta == 1: 
			if self.direction == self.CLOCKWISE: 
				print "Clockwise" 
				event = self.direction 
			else: 
				self.right=self.right+1
				self.left=0
				self.direction = self.CLOCKWISE 
		elif delta == 3: 
			if self.direction == self.ANTICLOCKWISE: 
				print "Anticlockwise" 
				event = self.direction 
			else: 
				self.left=self.left+1
				self.right=0
				self.direction = self.ANTICLOCKWISE 

		if delta > 0:
			if not self.callback:
				print "callback",self.direction,self.left,self.right
				if self.left > 0:
					print "LEFT"
					self.left=0
				if self.right > 0:
					print "RIGHT"
					self.right=0


class gpioRotary:
	
	def __init__(self):
		self.pinB = 11 
		self.pinA =13

		GPIO.setmode(GPIO.BOARD) 
		# The following lines enable the internal pull-up resistors 
		# on version 2 (latest) boards 
		GPIO.setwarnings(False) 
		GPIO.setup(self.pinA, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
		GPIO.setup(self.pinB, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
		#GPIO.setup(self.button, GPIO.IN, pull_up_down=GPIO.PUD_UP
	
		self.encoder0Pos=0

		self.busy=False		
		self.clockwise=None
		self.counterclockwise=None

		 # Add event detection to the GPIO inputs 
		GPIO.add_event_detect(self.pinA, GPIO.FALLING, callback=self.switch_eventA) 
#		GPIO.add_event_detect(self.pinB, GPIO.FALLING, callback=self.switch_eventB) 

	def switch_eventA(self,switch):
		# look r a low-to-high on channel A
		if GPIO.input(self.pinA):
			# check pin B to see which was we are turning
			if not GPIO.input( self.pinB):
				self.encoder0Pos=self.encoder0Pos+1	#cw
				direction="cw"
			else:
				self.encoder0Pos=self.encoder0Pos-1	#ccw
				direction="ccw"
  		else:
			#   // must be a high-to-low edge on channel A                                       
			if GPIO.input(self.pinB):
				self.encoder0Pos=self.encoder0Pos+1	#cw
				direction="cw"
			else:
				self.encoder0Pos=self.encoder0Pos-1	#ccw
				direction="ccw"
		print "A",self.encoder0Pos,direction

		if not self.busy:
			self.busy=True
			if self.encoder0Pos < -1:
				print "Trigger Counter Clockwise",self.clockwise

				if self.clockwise:	self.clockwise()
				self.encoder0Pos=0
			if self.encoder0Pos > 1:
				print "Trigger CLockwise",self.counterclockwise
				if self.counterclockwise:	self.counterclockwise()
				self.encoder0Pos=0
			self.busy=False
		else:
			print "- skiping roatry event"
	def switch_eventB(self,switch):
		# look r a low-to-high on channel A
		if GPIO.input(self.pinB):
			# check pin B to see which was we are turning
			if GPIO.input( self.pinA ):
				self.encoder0Pos=self.encoder0Pos+1	#cw
				direction="cw"
			else:
				self.encoder0Pos=self.encoder0Pos-1	#ccw
				direction="ccw"
  		else:
			#   // must be a high-to-l2ow edge on channel A                                       
			if not GPIO.input(self.pinA):
				self.encoder0Pos=self.encoder0Pos+1	#cw
				direction="cw"
			else:
				self.encoder0Pos=self.encoder0Pos-1	#ccw
				direction="ccw"
		print "B",self.encoder0Pos,direction





if __name__ == '__main__':
	gpio=gpiotools()
	o=gpio.output
	i=gpio.input
	for x in gpio.PINS:
		if gpio.PINS[x]['input']:
			print "i('%s')" %(x)
		else:
			print "o('%s',state)" %(x)
#	r=RotaryEncoder(None)	
	r=gpioRotary()
