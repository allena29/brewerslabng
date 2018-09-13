#!/usr/bin/python
#
# HD44780 LCD Test Script for
# Raspberry Pi
#
# Author : Matt Hawkins, refactored into class with scrolling support
# Site   : http://www.raspberrypi-spy.co.uk
# 
# Date   : 26/07/2012
# - updated for 4x20 originally did 2x16

import os
import sys
import syslog
import threading
import RPi.GPIO as GPIO
import time

class raspberrySpyLcd:


	def __init__(self,backlightTimeout=5):
				
		# The wiring for the LCD is as follows:
		# 1 : GND
		# 2 : 5V
		# 3 : Contrast (0-5V)*
		# 4 : RS (Register Select)
		# 5 : R/W (Read Write)       - GROUND THIS PIN
		# 6 : Enable or Strobe
		# 7 : Data Bit 0             - NOT USED
		# 8 : Data Bit 1             - NOT USED
		# 9 : Data Bit 2             - NOT USED
		# 10: Data Bit 3             - NOT USED
		# 11: Data Bit 4
		# 12: Data Bit 5
		# 13: Data Bit 6
		# 14: Data Bit 7
		# 15: LCD Backlight +5V**
		# 16: LCD Backlight GND

		GPIO.setwarnings(False)
		self.dbg=1
		# Define GPIO to LCD mapping
		self.LCD_RS = 7 # 26 #7
		self.LCD_E  = 8 #24 #8
		self.LCD_D4 = 25 # 22 #25
		self.LCD_D5 = 24 # 18 #24
		self.LCD_D6 = 23 # 16 #23
		self.LCD_D7 = 18 # 12 #18

		# Define some device constants
		self.LCD_WIDTH = 20    # Maximum characters per line
		self.LCD_CHR = True
		self.LCD_CMD = False

		self.LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
		self.LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line 
		self.LCD_LINE_3 = 0x94
		self.LCD_LINE_4 = 0xD4

		self.lines=[self.LCD_LINE_1,self.LCD_LINE_2,self.LCD_LINE_3,self.LCD_LINE_4]

		# Timing constants
		self.E_PULSE = 0.00005	# was 15 now 29
		self.E_DELAY = 0.00005	# was 15 now 2	9



		# Backlight PI
		self.LCD_BACKLIGHT= 11	#transistor
		self.LCD_BACKLIGHT_TRIGGER_1 = 9
		self.LCD_BACKLIGHT_TRIGGER_2 = 10
		self.LCD_BACKLIGHT_TRIGGER_3 = 22#17
		self.LCD_BACKLIGHT_TRIGGER_4 = 27#17
		self.LCD_BACKLIGHT_TRIGGER_5 = 17#17

		self.backlightTimeout=backlightTimeout
		self.backlightTimer=self.backlightTimeout+time.time()
		self.backlight=False

		GPIO.setmode(GPIO.BCM) # Use BOARD GPIO numbers rather GPIO numbers
		GPIO.setup(self.LCD_E, GPIO.OUT)  # E
		GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
		GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
		GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
		GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
		GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7


		if self.LCD_BACKLIGHT:
			GPIO.setup(self.LCD_BACKLIGHT, GPIO.OUT)	# backlight transistor pin
			GPIO.setup(self.LCD_BACKLIGHT_TRIGGER_1, GPIO.IN,pull_up_down=GPIO.PUD_UP)	# backlight trigger pin
			GPIO.setup(self.LCD_BACKLIGHT_TRIGGER_2, GPIO.IN,pull_up_down=GPIO.PUD_UP)	# backlight trigger pin
			GPIO.setup(self.LCD_BACKLIGHT_TRIGGER_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# backlight trigger pin
			GPIO.setup(self.LCD_BACKLIGHT_TRIGGER_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)	# backlight trigger pin
			GPIO.setup(self.LCD_BACKLIGHT_TRIGGER_5, GPIO.IN,pull_up_down=GPIO.PUD_UP)	# backlight trigger pin

		self.reinitDisplay()
		self.busy=[False,False,False,False]
		self.shutdown=False
		self.interruptMessage=["","","",""]
		self.importance=[-1,-1,-1,-1]
		self.useSyslog=False
		self._log("raspberrySpyLcd Started")

		if self.LCD_BACKLIGHT:
			self.backlightThread = threading.Thread(target=self._backlightTimer)
			self.backlightThread.daemon = True
			self.backlightThread.start()
			self.backlightTriggerThread = threading.Thread(target=self._backlightTrigger)
			self.backlightTriggerThread.daemon = True
			self.backlightTriggerThread.start()

	def __del__(self):
		self.shutdown=True
		self._lcdByte(self.lines[0], self.LCD_CMD)
		self._lcdString( "-"*self.LCD_WIDTH )
		self._lcdByte(self.lines[1], self.LCD_CMD)
		self._lcdString( "-"*self.LCD_WIDTH )


	def _log(self,msg):
		if self.useSyslog:
			syslog.syslog(syslog.LOG_DEBUG, "(raspberrySpyLcd) %s" %(msg))
		else:
			sys.stderr.write("%s\n" %(msg))


	def _backlightTrigger(self):
		while True:
			if os.path.exists("ipc/manual_backlight"):
				self._log("Backlight Manual Trigger on IPC")
				os.unlink("ipc/manual_backlight")
				self.enableBacklight()
				self.backlightTimer=time.time()
				time.sleep(10)
			if GPIO.input(self.LCD_BACKLIGHT_TRIGGER_1) == True:
				self._log("Backlight Manual Trigger on Pin 1")
				self.enableBacklight()
				self.backlightTimer=time.time()
				time.sleep(10)
			elif GPIO.input(self.LCD_BACKLIGHT_TRIGGER_2) == True:
				self._log("Backlight Manual Trigger on Pin 2")
				self.enableBacklight()
				self.backlightTimer=time.time()
				time.sleep(10)
			elif GPIO.input(self.LCD_BACKLIGHT_TRIGGER_3) == True:
				self._log("Backlight Manual Trigger on Pin 3")
				self.enableBacklight()
				self.backlightTimer=time.time()
				time.sleep(10)
			elif GPIO.input(self.LCD_BACKLIGHT_TRIGGER_4) == True:
				self._log("Backlight Manual Trigger on Pin 4")
				self.enableBacklight()
				self.backlightTimer=time.time()
				time.sleep(10)
			elif GPIO.input(self.LCD_BACKLIGHT_TRIGGER_5) == True:
				self._log("Backlight Manual Trigger on Pin 5")
				self.enableBacklight()
				self.backlightTimer=time.time()
				time.sleep(10)
			time.sleep(0.2)



	def _backlightTimer(self):
		while True:
			if self.backlight:
				if self.backlightTimer + self.backlightTimeout < time.time():
					self._log("Backlight turning off after %s seconds" %(time.time()-(self.backlightTimer)))
					GPIO.output(self.LCD_BACKLIGHT,0)
					self.backlight=False
			time.sleep(1)


	def _doScrollText(self,text,line,autoBlank,doNotScrollToStart,alignCenter,autoWait,cropText,alert,importance):
		if len(text) > self.LCD_WIDTH and cropText:
			text=text[0:self.LCD_WDITH]
			if alignCenter:
				if self.dbg:	self._log("Showing cropped message %s (center align)" %(text))
				self._lcdByte(self.lines[line], self.LCD_CMD)
				
				l=int((self.LCD_WIDTH-len(text))/2)
				self._lcdString("%s%s" %(" "*l,text))
			else:
				if self.dbg:	self._log("Showing cropped message %s" %(text))
				self._lcdByte(self.lines[line], self.LCD_CMD)
				self._lcdString(text)
		elif len(text) < self.LCD_WIDTH:

			if alignCenter:
				if self.dbg:	self._log("Showing full message %s (center align)" %(text))
				self._lcdByte(self.lines[line], self.LCD_CMD)
				
				l=int((self.LCD_WIDTH-len(text))/2)
				self._lcdString("%s%s" %(" "*l,text))
			else:
				if self.dbg:	self._log("Showing full message %s" %(text))
				self._lcdByte(self.lines[line], self.LCD_CMD)
				self._lcdString(text)
		else:	
			if self.dbg:	self._log("...started thread for scroll message %s" %(text))
			for c in range((len(text)-self.LCD_WIDTH)+1):

				
				if os.path.exists("ipc/manual_backlight") or GPIO.input(self.LCD_BACKLIGHT_TRIGGER_1) == False or GPIO.input(self.LCD_BACKLIGHT_TRIGGER_2) == False:# or	GPIO.input(self.LCD_BACKLIGHT_TRIGGER_3) == False:
					if os.path.exists("ipc/manual_backlight"):
						os.unlink("ipc/manual_backlight")
					print "Triggering interrupt message code here"
					self._lcdByte(self.lines[line], self.LCD_CMD)
					self._lcdString( self.interruptMessage[line] )
					self.busy[line]=False
					return

				if not self.shutdown:
					
					if alert:	self.backlightTimer=time.time()
					self._lcdByte(self.lines[line], self.LCD_CMD)
					self._lcdString( text[c:] )

					for tx in range(4):
						if os.path.exists("ipc/manual_backlight") or GPIO.input(self.LCD_BACKLIGHT_TRIGGER_1) == False or GPIO.input(self.LCD_BACKLIGHT_TRIGGER_2) == False or	GPIO.input(self.LCD_BACKLIGHT_TRIGGER_3) == False or GPIO.input(self.LCD_BACKLIGHT_TRIGGER_4) or GPIO.input(self.LCD_BACKLIGHT_TRIGGER_5):
							if os.path.exists("ipc/manual_backlight"):
								os.unlink("ipc/manual_backlight")
							print "Triggering interrupt message code here"
							self._lcdByte(self.lines[line], self.LCD_CMD)
							self._lcdString( self.interruptMessage[line] )
							self.busy[line]=False
							return
						time.sleep(0.1)	

			if not doNotScrollToStart:
				time.sleep(3)

				if self.dbg:	self._log("...resetting long line to begining" )
				if alert:	self.backlightTimer=time.time()+autoWait
				self._lcdByte(self.lines[line], self.LCD_CMD)
				self._lcdString(text)
			
		if autoBlank:
			if self.dbg:	self._log("...waiting %s seconds for autoblank" %(autoBlank))
			if alert:	self.backlightTimer=time.time()+autoBlank
			time.sleep(autoBlank)
			self._lcdByte(self.lines[line], self.LCD_CMD)
			self._lcdString(" "*self.LCD_WIDTH)
		
		if autoWait:
			if self.dbg:	self._log("...waiting %s seconds for autowait" %(autoWait))
			if alert:	self.backlightTimer=time.time()+autoWait
			time.sleep(autoWait)
			self._lcdByte(self.lines[line], self.LCD_CMD)
			self._lcdString(" "*self.LCD_WIDTH)
	

		if not autoWait and not autoBlank:
			time.sleep(0.135)		# must wait a small amount of time

	
		self.busy[line]=False

	def reinitDisplay(self):
		# Initialise display
		self._lcdByte(0x33,self.LCD_CMD)
		self._lcdByte(0x32,self.LCD_CMD)
		self._lcdByte(0x28,self.LCD_CMD)
		self._lcdByte(0x0C,self.LCD_CMD)  
		self._lcdByte(0x06,self.LCD_CMD)
		self._lcdByte(0x01,self.LCD_CMD)  



	def enableBacklight(self):
		self._log("Enabling Backlight")
		GPIO.output(self.LCD_BACKLIGHT,1)
		self.backlightTimer = time.time()
		self.backlight=True

	def scrollText(self,text,line=0,autoBlank=0,doNotScrollToStart=1,alignCenter=0,autoWait=0,cropText=0,alert=1,importance=1,onInterruptMessage=""):
		"""
			text [mandatory]
			line [optional, 0 : 1] 		defaults to first line (0)
			autoBlank	[optional n] 	wait 'n' seconds before blanking
			doNotScrollToStart [option 0,1]	after scrolling a message jump back to the start
			alignCenter [optional 0,1]	if message fits in the display width align to center
			autoWait [optional n]		wait at least 'n' seconds before the next message - don't blank afterwards
			cropText [optional 0,1]		cropText (don't scroll)
			alert [optional 0,1]		should the backlight timer be reset and the backligh enbaled
			importance 			not implemented
			onInterruptMessage		what we should display if a scroll is completed
		"""
		if self.dbg:	self._log("Text To Display on Line %s: %s\n" %(line,text))
		if line == 0:
			self.reinitDisplay()


		if importance < 0:
			print "Checking if we can cancel the importance flag for line ",line
			if -importance == self.importance[line]:
				print "yes we cane"
				self.importance[line]=-99
			print -importance,self.importance[line]
		if self.importance[line] > importance:
			print "our importance is less than current importance.",importance,self.importance[line],text
			return

		while self.busy[line]:
			if self.dbg:	self._log("...Line %s busy\n" %(line))
			time.sleep(0.1)
		
	
	
		self.busy[line]=True
		self.importance[line]= importance	
		if self.LCD_BACKLIGHT and alert:
			self.enableBacklight()
						
		self.interruptMessage[line] = onInterruptMessage
		print "if we are interrupted we are going to show",onInterruptMessage," <<<",line

		self.scrollerThread = threading.Thread(target=self._doScrollText,args=(text,line,autoBlank,doNotScrollToStart,alignCenter,autoWait,cropText,alert,importance))
		self.scrollerThread.daemon=True
		self.scrollerThread.start()

		
		time.sleep(0.10)


	def _lcdString(self,message):
		message = message.ljust(self.LCD_WIDTH," ")  
		for i in range(self.LCD_WIDTH):
			self._lcdByte(ord(message[i]),self.LCD_CHR)

	def _lcdByte(self,bits, mode):
		# Send byte to data pins
		# bits = data
		# mode = True  for character
		#        False for command

		GPIO.output(self.LCD_RS, mode) # RS

		# High bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x10==0x10:
			GPIO.output(self.LCD_D4, True)
		if bits&0x20==0x20:
			GPIO.output(self.LCD_D5, True)
		if bits&0x40==0x40:
			GPIO.output(self.LCD_D6, True)
		if bits&0x80==0x80:
			GPIO.output(self.LCD_D7, True)

		# Toggle 'Enable' pin
		time.sleep(self.E_DELAY)    
		GPIO.output(self.LCD_E, True)  
		time.sleep(self.E_PULSE)
		GPIO.output(self.LCD_E, False)  
		time.sleep(self.E_DELAY)      

		# Low bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x01==0x01:
			GPIO.output(self.LCD_D4, True)
		if bits&0x02==0x02:
			GPIO.output(self.LCD_D5, True)
		if bits&0x04==0x04:
			GPIO.output(self.LCD_D6, True)
		if bits&0x08==0x08:
			GPIO.output(self.LCD_D7, True)

		# Toggle 'Enable' pin
		time.sleep(self.E_DELAY)    
		GPIO.output(self.LCD_E, True)  
		time.sleep(self.E_PULSE)
		GPIO.output(self.LCD_E, False)  
		time.sleep(self.E_DELAY)   



if __name__ == '__main__':
	testHarness=True
	lcd = raspberrySpyLcd()
	try:
		lcd.scrollText(sys.argv[1],0)
		testHarness=False
	except:
		pass
	try:
		lcd.scrollText(sys.argv[2],1)
		testHarness=False
	except:
		pass
	try:
		time.sleep(int(sys.argv[3]))
	except IndexError:
		pass
	except KeyboardInterrupt:
		pass


	if not testHarness:
		sys.exit(0)


	if testHarness:
		sys.stderr.write("Test Harness, simple test\n")
		lcd.scrollText("Testing, Testing, 1,2,1,2 HD44780",0)
		lcd.scrollText("Test script for modified raspberrypi-spy.co.uk script",1)
	time.sleep(30)
	sys.stderr.write("Test Harness, not backlightt\n")
	lcd.scrollText("do not enable",0,alert=0)
	lcd.scrollText("backlight",1,alert=0)
	time.sleep(15)
	sys.stderr.write("Test Harness, with backlight and center line 0\n")
	lcd.scrollText("with",0,alert=1,alignCenter=1)
	lcd.scrollText("backlight",1,alert=0)
	time.sleep(5)
	lcd.scrollText("no",0,alert=0,alignCenter=1,autoBlank=3)
	lcd.scrollText("backlight",1,alert=0)
	time.sleep(50)



	time.sleep(5000)
	lcd=None
