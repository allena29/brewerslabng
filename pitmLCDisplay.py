#!/usr/bin/python

# piTempMonitor LCDisplay


import hashlib
import json
import socket
import struct
import sys
import threading
import syslog
import time
import os

from pitmCfg import pitmCfg
from gpiotools2 import * 

if len(sys.argv) < 2:
	if os.path.exists("simulator"):
		import fakeRPi.GPIO as GPIO
	else:
		try:
			import RPi.GPIO as GPIO
			from raspberrySpyLcd import raspberrySpyLcd
		except ImportError:
			sys.stderr.write("Cannot run raspberry pi without root permissions\n")
			sys.exit(3)



class pitmLCDisplay:


	def __init__(self,rpi=True):
		self.logging=4		# 1 = syslog, 2 = stderr, 3 = supress repeat messages, 4 = every 100 seconds
		self.lastLog=["","","","","","","","","","",""]	
		self.cfg = pitmCfg()
		self.mcastMembership=False
		self._log("pitmLCDispaly")


		self.lastMsgTimestamp=0	
		self.lastLine0=None
		self.lastLine1=None


	def __del__(self):
		if self.mcastMembership:
			self._log("Unregistering Multicast LCD Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastLcdPort))
			self.sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.cfg.mcastGroup) + socket.inet_aton('0.0.0.0'))
			self.mcastMembership=False
			
	def _log(self,msg,importance=10):
		if self.logging == 1:
			if importance > 9:
				syslog.syslog(syslog.LOG_DEBUG, msg)
		elif self.logging == 2:
			sys.stderr.write("%s\n" %(msg))
		elif self.logging == 3:
			if (importance > 9) or  (not self.lastLog[importance] == msg):
				syslog.syslog(syslog.LOG_DEBUG, msg)
			sys.stderr.write("%s\n" %(msg))
		elif self.logging == 4:
			if (importance > 9) or  (("%s" %(time.time())).split(".")[0][-3:] == "000") :
				syslog.syslog(syslog.LOG_DEBUG, msg)
				self.lastLog[importance]=msg
			sys.stderr.write("%s\n" %(msg))


			
	def _err(self,msg):
		syslog.syslog(syslog.LOG_ERR, msg)
		sys.stderr.write("%s\n" %(msg))






	def control(self):
		self._log("Initalising LCD Mcast Listening")
		if not os.path.exists("simulator"):
			self.lcd= raspberrySpyLcd(backlightTimeout=180)
			self.lcd.scrollText("welcome",line=0,alignCenter=1,autoWait=5)
			self.lcd.scrollText(socket.gethostname(),line=1,alignCenter=1,autoWait=5)
			self.lcd.scrollText("",line=2)
			self.lcd.scrollText("",line=3)


		self._log("Launching Multicast LCD Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastLcdPort))
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastLcdPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True

#		gpio2 = gpiotools2()
#		

		while True:
			(data, addr) = self.sock.recvfrom(1200)
			self.decodeMessage(data)	
			time.sleep(0.2)
				
	

	def uncontrol(self):
		if self.mcastMembership:
			self._log("Unregistering Multicast LCD Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastLcdPort))
			self.sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.cfg.mcastGroup) + socket.inet_aton('0.0.0.0'))
			self.mcastMembership=False







	def decodeMessage(self,data):
		"""
		"""
	
		try:
			cm = json.loads( data )
		except:
			self._log("Error unpickling input message\n%s" %(data))
			return

		checksum = cm['_checksum']
		cm['_checksum'] ="                                        "
		ourChecksum = hashlib.sha1("%s%s" %(cm,self.cfg.checksum)).hexdigest()
		if not cm.has_key("selfGenerated"):	cm['selfGenerated'] = False
		if not cm.has_key("autoBlank"):	cm['autoBlank'] = 0
		if not cm.has_key("doNotScrollToStart"):	cm['doNotScrollToStart']=1
		if not cm.has_key("alignCenter"):	cm['alignCenter']=0	
		if not cm.has_key("autoWait"):	cm['autoWait']=0
		if not cm.has_key("cropText"):	cm['cropText']=0
		if not cm.has_key("alert"):	cm['alert']=1
		if not cm.has_key("importance"):	cm['importance']=5
		if cm['line']:
			self.lastLine1 = cm['text']
		else:
			self.lastLine0 = cm['text']

		if cm['selfGenerated']:
			self._log(" Filtering out self generated message")
		else:
			#self._log(" Text: %s\n Line: %s\n autoBlank: %s\n doNotScrollToStart: %s\n alignCenter: %s\n autoWait %s\n cropText %s" %(cm['text'],cm['line'],cm['autoBlank'],cm['doNotScrollToStart'],cm['alignCenter'],cm['autoWait'],cm['cropText']))
			self._log(" Text: %s  Line: %s" %(cm['text'],cm['line']),importance=1)
			




	def sendMessage(self,text="<...>",line=0,cropText=0,selfGenerated=False,alert=1,doNotScrollToStart=0,interruptMessage=None,importance=5):
		"""
		Although send message is in the same class this encodes a message
		and sends it on the multicast socket and is intended to be used by client
		programs.
		
		The options we accept here are a subset of raspberrySpyLcd scrolLText
		The values do align with raspberrySpyLcd

		text 			"string" to print	
		line		 	0,1,2,3
		cropText	 	0,1	(i.e. dont scrol)
		alert			0,1	(ensures backlight is lit for this message)
		doNotScrollToStart	0,1	0 = scroll to start (justify left), 1 = stays at the end of the scroll text (justify right)	
		importance 		0..10	importance - if we set an importance of 10 we will drop a message <=9
							(send the same text and "-importance" to cancel
		"""
		controlMessage={}

		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage['_operation'] = 'lcdDisplay'
		controlMessage['_checksum'] ="                                        "
		if not controlMessage.has_key("interruptMessage"):
			if interruptMessage:
				controlMessage['interruptMessage']=interruptMessage
			else:
				controlMessage['interruptMessage'] = text[0:20]
		if not controlMessage.has_key("selfGenerated"):
			controlMessage['selfGenerated'] = selfGenerated
		if not controlMessage.has_key("text"):
			controlMessage['text'] = text
		if not controlMessage.has_key("line"):
			controlMessage['line'] = line
		if not controlMessage.has_key("alert"):
			controlMessage['alert'] = alert
		if not controlMessage.has_key("importance"):
			controlMessage['importance'] = importance
		if not controlMessage.has_key("doNotScrollToStart"):	
			controlMessage['doNotScrollToStart']=doNotScrollToStart
	

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 

		if len(msg) > 1200:
			self._err("Cannot send message - packet too big")
			return

		sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastLcdPort))
		sendSocket.close()




if __name__ == '__main__':

	if len(sys.argv) < 3:
		# launch daemon
		try:
			lcd = pitmLCDisplay()
			lcd.control()
		except KeyboardInterrupt:
			lcd.uncontrol()

	else:
		print "pitmLCDisplay in client mode"
		lcd=pitmLCDisplay()
		try:
			lcd.sendMessage(sys.argv[1],line=0)
		except:
			pass
		import time
		time.sleep(0.1)	
		try:
			lcd.sendMessage(sys.argv[2],line=1)	
		except ImportError:
			pass


