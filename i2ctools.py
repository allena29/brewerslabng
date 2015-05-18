import os
import time
if not os.path.exists("simulator"):
	import smbus
import sys

class i2ctools:

	"""
The pattern we were following from:
 - https://github.com/nathanchantrell/Python-MCP230XX/blob/master/mcp23017.py
 doesn't uite work when resetting pin 0
	"""

	def __init__(self,address=0x25):




		self.binaryMask=[1,2,4,8,16,32,64,128,256]		

		if address == 0x25:
			self.BANKA=[1,1,1,1,1,1,1,1]
			self.BANKB=[0,0,0,0,0,0,0,0]
			
			self.PINS={
				'b0' : {'input':False,'bank':"B",'pin':0,'setup':False,'inverse':False},
				'b1' : {'input':False,'bank':"B",'pin':1,'setup':False,'inverse':False},
				'b2' : {'input':False,'bank':"B",'pin':2,'setup':False,'inverse':False},
				'b3' : {'input':False,'bank':"B",'pin':3,'setup':False,'inverse':False},
				'b4' : {'input':False,'bank':"B",'pin':4,'setup':False,'inverse':False},
				'b5' : {'input':False,'bank':'B','pin':5,'setup':False,'inverse':False},	
				'b6' : {'input':False,'bank':'B','pin':6,'setup':False,'inverse':False},	
				'b7' : {'input':False,'bank':'B','pin':7,'setup':False,'inverse':False},	

			
				'hltProbePower' : {'input':False,'bank':'A','pin':1,'setup':False,'inverse':True},	
				'mashProbeData' : {'input':False,'bank':'A','pin':2,'setup':False,'inverse':True},	
				'mashProbePower' : {'input':False,'bank':'A','pin':3,'setup':False,'inverse':True},
				'boilProbeData' : {'input':False,'bank':'A','pin':4,'setup':False,'inverse':True},	
				'boilProbePower' : {'input':False,'bank':'A','pin':5,'setup':False,'inverse':True},	
				'fermProbeData' : {'input':False,'bank':'A','pin':6,'setup':False,'inverse':True},
				'fermProbePower' : {'input':False,'bank':"A",'pin':7,'setup':False,'inverse':True},
				'hltProbeData' : {'input':False,'bank':'A','pin':0,'setup':False,'inverse':True},
			}

		else:
			print "Unknown MCP23017"
		
		self.address = address # I2C address of MCP23017, based upon the tying of A0,A1,A3 adress pins to ground


		#
		# set some default values
		#
		if self.address==0x25:
			self.bankaVal=0xff
			self.bankbVal=0x00

		if os.path.exists("simulator"):
			o=open("ipc/fakei2c_%s" %(self.address),"w")
			o.write("%s;%s;" %(self.bankaVal,self.bankbVal))
			o.close()
			return
	
		# in this initial cut we only support output pins
		self.bus = smbus.SMBus(1)
		success=False
		while not success:
			try:
				self.bus.write_byte_data(self.address,0x00,0x00) # Set all of bank A to outputs 
				success=True
			except:
				sys.stderr.write("error setting bank a to output\n")
			time.sleep(0.02)
		success=False
		while not success:
			try:
				self.bus.write_byte_data(self.address,0x01,0x00) # Set all of bank B to outputs
				success=True
			except:
				sys.stderr.write("erorr setting bank b to output\n")
			time.sleep(0.02)
		success=False
		while not success:
			try:
				self.bus.write_byte_data(self.address,0x12,self.bankaVal) # Set all of bank A to low
				success=True
			except:
				sys.stderr.write("error setting bank a default value\n")		
			time.sleep(0.02)
		success=False
		while not success:
			try:
				self.bus.write_byte_data(self.address,0x13,self.bankbVal) # Set all of bank B to low
				success=True
			except:
				sys.stderr.write("error setting bank b default value\n")
			time.sleep(0.02)
	
#		# was looking to refactor  so we couuld hav rExtractor() and rPump()
#		# as convenience functions
#		for pin in self.PINS:
#			if not self.PINS[pin]['input']:
#				self.__dict__[pin]=self.output	
#

	def __del__(self):

		if self.address==0x25:
			banka=0xff
			bankb=0x00

		if os.path.exists("simulator"):
			o=open("ipc/fakei2c_%s" %(self.address),"w")
			o.write("%s;%s;" %(banka,bankb))
			o.close()
			return

		self.bus.write_byte_data(self.address,0x12,banka)
		self.bus.write_byte_data(self.address,0x13,bankb)

		self.bus.write_byte_data(self.address,0x12,banka)
		self.bus.write_byte_data(self.address,0x13,bankb)

	# in 
	def outputHigh(self,pin="<null>"):
		self.output(pin,1)

	def setLow(self,pin="<null>"):
		self.output(pin,0)

	

	def output(self,pin,state=-1):
		
		if not self.PINS.has_key(pin):
			sys.stderr.write("pin %s does not exist\n" %(pin))
		else:

			pinNum=self.PINS[pin]['pin']
			if self.PINS[pin]['bank'] == "A":				
				try:
					self.bus.write_byte_data(self.address,0x00,0x00) # Set all of bank A to outputs 
				except:
					sys.stderr.write("error setting up bank A\n")
				bank=self.BANKA
				bankAddress=0x12
			else:
				try:
					self.bus.write_byte_data(self.address,0x01,0x00) # Set all of bank A to outputs 
				except:
					sys.stderr.write("error setting up bank B\n")
				bank=self.BANKB
				bankAddress=0x13
		

		
			if self.PINS[pin]['inverse']:
				if state == 1:
					state=0
				else:
					state=1

			bank[pinNum] = state
			#print bank
			value=0
			for i in range(8):
				if bank[i] == 1:
					value=value+self.binaryMask[i]			
#				else:
#					print i," no additional"
#			print "value computed as",value

			self.PINS[pin]['state']=state


			if self.PINS[pin]['bank'] == "A":
				self.bankaVal=value
			else:
				self.bankbVal=value

			if os.path.exists("simulator"):
				o=open("ipc/fakei2c_%s" %(self.address),"w")
				o.write("%s;%s;" %(self.bankaVal,self.bankbVal))
				o.close()
				return
			try:

#				print "I2C: ",value
				self.bus.write_byte_data(self.address,bankAddress,value)
			except:
				#self.lcdDisplay.sendMessage("Error output to",0,importance=9)
				#self.lcdDisplay.sendMessage("i2c bus",importance=9)
				#self.lcdDisplay.sendMessage(" %s" %(self.address) ,importance=9)
				#self.lcdDisplay.sendMessage(" ",importance=9)
				print "i2c bus error",
				try:
					self.bus.write_byte_data(self.address,bankAddress,value)
					print "recovered"	
				except:
					print "unable to recover"
				#self.lcdDisplay.sendMessage("Error output to",0,importance=-9)
				#self.lcdDisplay.sendMessage("i2c bus",importance=-9)
				#self.lcdDisplay.sendMessage(" %s" %(self.address) ,importance=-9)
				#self.lcdDisplay.sendMessage(" ",importance=-9)
			
					
			time.sleep(0.02)


	
	"""
	def input(self,pin):
		if not self.PINS.has_key(pin):
			sys.stderr.write("pin %s does not exist\n" %(pin))
		else:
			if not self.PINS[pin]['setup']:
				if not self.PINS[pin]['input']:
					sys.stderr.write("pin %s set as an output pin\n" %(pin))
				else:	
					GPIO.setup( self.PINS[pin]['pin'], 1)

			state=GPIO.input( self.PINS[pin]['pin'] )
			print "RAW STATE",state	
			if self.PINS[pin]['inverse']:
				if state == True:
					return False
				else:
					return True
			return state
	
	def  waitForChange(self,pin):
		self.input(pin)
		startstate= GPIO.input( self.PINS[pin]['pin'] )
		newstate=startstate
		print "Startt State = ",startstate
		while newstate == startstate:
			newstate=GPIO.input(self.PINS[pin]['pin'])
			print newstate
			time.sleep(.1)
		
	"""

	
if __name__ == '__main__':
	if not len(sys.argv) == 2:
		address=0x25
	else:
		address=0x25
	i2c=i2ctools(address=address)
	o=i2c.output
#	i=i2c.input
	for x in i2c.PINS:
		if i2c.PINS[x]['input']:
			print "input pins not supported"
			#print "i('%s',state)" %(x)
		else:
			print "o('%s',state)" %(x)
	
