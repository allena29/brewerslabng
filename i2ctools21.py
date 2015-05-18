import os
import time
if not os.path.exists("simulator"):
	import smbus
import sys

class i2ctools21:

	"""
The pattern we were following from:
 - https://github.com/nathanchantrell/Python-MCP230XX/blob/master/mcp23017.py
 doesn't uite work when resetting pin 0
	"""

	def __init__(self,address=0x21):

		self.simulator=False
		if os.path.exists("simulator"):
			
			self.simulator=True


		self.binaryMask=[1,2,4,8,16,32,64,128,256]		

		if address == 0x21:
			self.BANKA=[0,0,0,0,0,0,0,0]
			self.BANKB=[0,0,0,0,0,0,0,0]
			
			self.PINS={
				'lSpargeRed' : {'input':False,'bank':"B",'pin':0,'setup':False,'inverse':False},
				'lSpargeGreen' : {'input':False,'bank':"B",'pin':1,'setup':False,'inverse':False},
				'lSpargeBlue' : {'input':False,'bank':"B",'pin':2,'setup':False,'inverse':False},
				'lHltBlue' : {'input':False,'bank':"B",'pin':3,'setup':False,'inverse':False},
				'lHltRed' : {'input':False,'bank':"B",'pin':4,'setup':False,'inverse':False},
				'lHltGreen' : {'input':False,'bank':'B','pin':5,'setup':False,'inverse':False},	
				'lMashGreen' : {'input':False,'bank':'B','pin':6,'setup':False,'inverse':False},	
				'lSys' : {'input':False,'bank':'B','pin':7,'setup':False,'inverse':False},	

			
				'lMashBlue' : {'input':False,'bank':'A','pin':1,'setup':False,'inverse':False},	
				'lBoilGreen' : {'input':False,'bank':'A','pin':2,'setup':False,'inverse':False},	
				'lFermGreen' : {'input':False,'bank':'A','pin':3,'setup':False,'inverse':False},
				'lFermBlue' : {'input':False,'bank':'A','pin':4,'setup':False,'inverse':False},	
				'lFermRed' : {'input':False,'bank':'A','pin':5,'setup':False,'inverse':False},	
				'lBoilRed' : {'input':False,'bank':'A','pin':6,'setup':False,'inverse':False},
				'lMashRed' : {'input':False,'bank':"A",'pin':7,'setup':False,'inverse':False},
				'lBoilBlue' : {'input':False,'bank':'A','pin':0,'setup':False,'inverse':False},
			}

		else:
			print "Unknown MCP23017"
		
		self.address = address # I2C address of MCP23017, based upon the tying of A0,A1,A3 adress pins to ground


		#
		# set some default values
		#
		if self.address==0x21:
			self.bankaVal=0x00
			self.bankbVal=0x00

		if os.path.exists("simulator"):
			o=open("ipc/fakei2c_%s" %(self.address),"w")
			o.write("%s;%s;" %(self.bankaVal,self.bankbVal))
			o.close()
			return
	
		# in this initial cut we only support output pins
		if not self.simulator:
			self.bus = smbus.SMBus(1)
		
		success=False
		while not success:
			try:
				if not self.simulator:
					self.bus.write_byte_data(self.address,0x00,0x00) # Set all of bank A to outputs 
				success=True
			except:
				sys.stderr.write("error setting bank a to output\n")
			time.sleep(0.02)
		success=False
		while not success:
			try:
				if not self.simulator:
					self.bus.write_byte_data(self.address,0x01,0x00) # Set all of bank B to outputs
				success=True
			except:
				sys.stderr.write("erorr setting bank b to output\n")
			time.sleep(0.02)
		success=False
		while not success:
			try:
				if not self.simulator:
					self.bus.write_byte_data(self.address,0x12,self.bankaVal) # Set all of bank A to low
				success=True
			except:
				sys.stderr.write("error setting bank a default value\n")		
			time.sleep(0.02)
		success=False
		while not success:
			try:
				if not self.simulator:
					self.bus.write_byte_data(self.address,0x13,self.bankbVal) # Set all of bank B to low
				success=True
			except:
				sys.stderr.write("error setting bank b default value\n")
			time.sleep(0.02)
	

	def __del__(self):

		if self.address==0x21:
			banka=0x00
			bankb=0x00

		if os.path.exists("simulator"):
			o=open("ipc/fakei2c_%s" %(self.address),"w")
			o.write("%s;%s;" %(banka,bankb))
			o.close()
			return

		if not self.simulator:
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
					if not self.simulator:
						self.bus.write_byte_data(self.address,0x00,0x00) # Set all of bank A to outputs 
				except:
					sys.stderr.write("error setting up bank A\n")
				bank=self.BANKA
				bankAddress=0x12
			else:
				try:
					if not self.simulator:
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
				if not self.simulator:
					self.bus.write_byte_data(self.address,bankAddress,value)
			except:
				#self.lcdDisplay.sendMessage("Error output to",0,importance=9)
				#self.lcdDisplay.sendMessage("i2c bus",importance=9)
				#self.lcdDisplay.sendMessage(" %s" %(self.address) ,importance=9)
				#self.lcdDisplay.sendMessage(" ",importance=9)
				print "i2c bus error",
				try:
					if not self.simulator:
						self.bus.write_byte_data(self.address,bankAddress,value)
					print "recovered"	
				except:
					print "unable to recover"
				#self.lcdDisplay.sendMessage("Error output to",0,importance=-9)
				#self.lcdDisplay.sendMessage("i2c bus",importance=-9)
				#self.lcdDisplay.sendMessage(" %s" %(self.address) ,importance=-9)
				#self.lcdDisplay.sendMessage(" ",importance=-9)
			
					
			time.sleep(0.02)


	
	
if __name__ == '__main__':
	if not len(sys.argv) == 2:
		address=0x21
	else:
		address=0x21
	i2c=i2ctools21(address=address)
	o=i2c.output
#	i=i2c.input
	for x in i2c.PINS:
		if i2c.PINS[x]['input']:
			print "input pins not supported"
			#print "i('%s',state)" %(x)
		else:
			print "o('%s',state)" %(x)
	
