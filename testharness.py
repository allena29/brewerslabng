from pitmLedFlasher import *
from pitmLCDisplay import *
import sys
from gpiotools import *
from gpiotools2 import *
import time

testtype="all"
if len(sys.argv) > 1:
	testtype=sys.argv[1]

#i2c=i2ctools(address=0x21)
#go=gpiotools()
#:wqgo2=gpiotools2()

selfledFlasher=pitmLedFlasher()
lcd=pitmLCDisplay()

if testtype == "all" or testtype == "lcd":
	print "Testing LCD"
	lcd.sendMessage('Testing',0)
	lcd.sendMessage(' Lcd Display',1)
	lcd.sendMessage('Hello World !!!!!!!!!',2)
	lcd.sendMessage('',3)
	time.sleep(2)

if testtype == "all" or testtype == "ledflash":
	lcd.sendMessage('Testing',0)
	lcd.sendMessage(' Led Flasher',1)
	lcd.sendMessage("",2)
	lcd.sendMessage("",3)


	for x in range(1):
		pin="Sys"
		color=""
		selfledFlasher.sendMessage('l%s' %(pin),"flash%s" %(color))
		time.sleep(5)
		colors=['red','blue','green']
		for pin in ['Hlt','Sparge','Boil','Mash','Ferm']:
			for color in colors:
				print pin,"flash",color
				lcd.sendMessage("Pin=%s" %(pin),2)
				lcd.sendMessage("Colour=Flash%s" %(color),3)
				selfledFlasher.sendMessage('l%s' %(pin),"flash%s" %(color))
				time.sleep(5)
			selfledFlasher.sendMessage('l%s' %(pin),"off")
if testtype == "all" or testtype == "led":
	lcd.sendMessage('Testing',0)
	lcd.sendMessage(' Led Flasher',1)
	lcd.sendMessage("",2)
	lcd.sendMessage("",3)
	colors=['red','green','blue','yellow','purple','cyan','white','off']
	for pin in ['Sys','Hlt','Sparge','Boil','Mash','Ferm']:
		for color in colors:
			print pin,color
			lcd.sendMessage("Pin=%s" %(pin),2)
			lcd.sendMessage("Colour=%s" %(color),3)
			selfledFlasher.sendMessage('l%s' %(pin),color)
			time.sleep(0.8)
		time.sleep(0.3)

lcd.sendMessage("",0)
lcd.sendMessage("",1)
lcd.sendMessage("",2)
lcd.sendMessage("",3)


lcd.sendMessage("",0)
lcd.sendMessage("",1)
lcd.sendMessage("",2)
lcd.sendMessage("",3)


if testtype == "all" or testtype == "input":
	lcd.sendMessage("Testing",0)
	lcd.sendMessage(" inputs",1)
	lcd.sendMessage("",2)
	lcd.sendMessage("",3)

#31 = HLT
#35 = Sparge
#36 = boil
#32=Mash
##29  = ferm
#22 Pump
	for ii in ['swHlt','swSparge','swBoil','swMash','swFerm','swPump']:
		
		lcd.sendMessage(ii,2)
		print "looking for ii",ii
		x=0
		y=1
		while y:
		
			if go2.input( ii ):
				x=x+1	
				print "True"
			if x > 10:
				y=0
				lcd.sendMessage("Found as %s" %(go2.PINS[ii]['pin']),2)
				print "Found as %s" %(go2.PINS[ii]['pin'])
			time.sleep(0)
			
	for ii in ['pLeft','pRight','pOk']:
		
		lcd.sendMessage(ii,2)
		print "Looking for ",ii
		x=0
		y=1
		while y:
		
			if go.input( ii ):
				x=x+1	
				print "True"
			if x > 10:
				y=0
				lcd.sendMessage("Found as %s" %(go.PINS[ii]['pin']),2)
				print "Found as %s" %(go.PINS[ii]['pin'])
			time.sleep(0)

	lcd.sendMessage("Rotary Encoder",2)
	r=gpioRotary()
			
lcd.sendMessage("",0)
lcd.sendMessage("",1)
lcd.sendMessage("",2)
lcd.sendMessage("",3)

