#!/usr/bin/python
# piTempBuzzer
import os
import json
import hashlib
import json
import struct
import socket
import syslog
import sys
import threading
import time

from pitmCfg import pitmCfg
from pitmLCDisplay import *

from gpiotools import gpiotools





class pitmSsrRelay:


	def __init__(self):
		self.logging=3		# 1 = syslog, 2 = stderr
		self.lastLog=["","","","","","","","","","",""]	
		if not os.path.exists("simulator"):
			self.logging=3
			syslog.openlog( facility=syslog.LOG_LOCAL7)
		self.cfg = pitmCfg()
		self.gpio = gpiotools()
		self.lcdDisplay=pitmLCDisplay()
		
		
		# our first job is to make sure all the relays are set to 1
		# so that they stay N/O
		# we do this in co-opreation with the master
		# controlling a transistor to ensure the relay	
		# opto isolator's don't have power until
		# after we have done this
		self.gpio.output('ssrZoneA',0)
		self.gpio.output('ssrZoneB',0)
#		self.gpio.output('tSsrFan',0)	
	
		self.mcastMembership=False

		self.zoneTemp=-1
		self.zoneTarget=-1
		self.zoneTempTimestamp=-1

		self.ssrZoneA=False
		self.ssrZoneB=False
		self.ssrPinA=False
		self.ssrPinB=False
		
		# Used to broadcast the gpio status
		self._relayZoneA=False
		self._relayZoneB=False
		self._relayZoneUseA=False
		self._relayZoneUseB=False
		self._gpiossrA=False
		self._gpiossrB=False

		self.hltActive=False
		self.boilActive=False


		self.cycle=4
		self.zoneAduty=0
		self.zoneBduty=0
		self.zoneAmeter=0
		self.zoneBmeter=0

		# used for zone toggling
		self.useZoneA=True
		self.zoneToggleCount=0
		self.singleZone=True


		self.ssrFanRequiredUntil=-1


	def __del__(self):

		self.gpio.output('ssrZoneA',0)
		self.gpio.output('ssrZoneB',0)
	#	self.gpio.output('tSsrFan',0)	
		
	def uncontrol(self):
		self._log("Uncontrol Called")

		self.gpio.output('ssrZoneA',0)
		self.gpio.output('ssrZoneB',0)
	#	self.gpio.output('tSsrFan',0)	

	
	def _log(self,msg,importance=10):
		if self.logging == 1:
			if importance > 9:
				syslog.syslog(syslog.LOG_DEBUG, msg)
		elif self.logging == 2:
			sys.stderr.write("%s\n" %(msg))
		elif self.logging == 3:
			if (importance > 9) or (  (("%s" %(time.time())).split(".")[0][-3:] == "000") or (not self.lastLog[importance] == msg)):
				syslog.syslog(syslog.LOG_DEBUG, msg)
				self.lastLog[importance]=msg
			sys.stderr.write("%s\n" %(msg))


			
	def _err(self,msg):
		syslog.syslog(syslog.LOG_ERR, msg)
		sys.stderr.write("%s\n" %(msg))



	def submission(self):
		self._log("Submitting to control of Controller")
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		
		while True:
			(data, addr) = self.sock.recvfrom(1200)		
			try:
				cm = json.loads( data )
			except:
				self._log("Error unpickling input message\n%s" %(data))
				return

			checksum = cm['_checksum']
			cm['_checksum'] ="                                        "
			ourChecksum = hashlib.sha1("%s%s" %(cm,self.cfg.checksum)).hexdigest()


#			if time.time() > self.ssrFanRequiredUntil:
#				self.gpio.output('tSsrFan',0)	
				


			if not cm['_mode'].count("hlt") and not cm['_mode'].count("boil"):
				print "not hlt not boil zoneA = 0"
				self.gpio.output('zoneA',0)
				self.gpio.output('zoneB',0)
				self.gpio.output('ssrZoneA',0)
				self.gpio.output('ssrZoneB',0)
				self.gpio.output('zoneAuse',0)
				self.gpio.output('zoneBuse',0)
				self._relayZoneA=False
				self._relayZoneB=False
				self._relayZoneUseA=False
				self._relayZoneUseB=False
				self._gpiossrA=False
				self._gpiossrB=False

			#
			# HLT (mash water) heating processing
			#
			if self.hltActive and not cm['_mode'].count("hlt"):
				self._log("HLT Reset")
				if not os.path.exists("simulator"):
					self.lcdDisplay.sendMessage("No target/zone temp A",3,importance=-8)		# this resets the message
				self.hltActive=False
#				self.gpio.output('zoneA',0)
#				self.gpio.output('zoneB',0)
#				self.gpio.output('zoneAuse',0)
#				self.gpio.output('zoneBuse',0)

			if cm['_mode'].count("hlt") and not self.hltActive and not cm['_mode'] == "idle":
				self._log("HLT Init")
				self._log(" - setting zoneA power on to HLT mode")
				self._log(" - setting zoneB power on to HLT mode")
				self.gpio.output('zoneA',1)
				self.gpio.output('zoneB',1)
				self.gpio.output('zoneAuse',0)
				self.gpio.output('zoneBuse',0)
				self._relayZoneA=True
				self._relayZoneB=True
				self._relayZoneUseA=False
				self._relayZoneUseB=False


				self.htlActive=True
				self.zoneAduty=1
				self.zoneBduty=0
				self.useZoneA=True

			spargeOrHlt=False
			if cm['_mode'].count("sparge") and not cm['_mode'] == "idle":
				self.hltActive=True			
				(tMin,tMax,tTarget)=cm['sparge']
				self.zoneTarget=tTarget
#				print "Using Sparge Target",tTarget
				spargeOrHlt=True
			elif cm['_mode'].count("hlt") and not cm['_mode'] == "idle":
				self.hltActive=True			
				(tMin,tMax,tTarget)=cm['hlt']
				self.zoneTarget=tTarget
#				print "Using HLT Target",tTarget
				spargeOrHlt=True
			

			if spargeOrHlt:
				if self.zoneTemp == -1 or self.zoneTarget == -1:
					self._log("no target temp - sparge/hlt")
					if not os.path.exists("simulator"):
						self.lcdDisplay.sendMessage("No target/zone temp A",3,importance=8)
					time.sleep(3)
				else:
					if not os.path.exists("simulator"):
						self.lcdDisplay.sendMessage("No target/zone temp A",3,importance=-8)

					# if we are 95% of the temperature target then we will set this to 1
					if self.zoneTemp <  (self.zoneTarget *  0.95):
						loadRequired=self.cycle
					elif self.zoneTemp > self.zoneTarget:
						loadRequired=0
					else:
						loadRequired=0.85
					
					
					# load requiired
					self._log("HLT: load required %s %.1f %.1f " %(loadRequired,self.zoneTemp,self.zoneTarget))
#					print "Load Required ",loadRequired,self.zoneTemp,self.zoneTarget,self.zoneToggleCount
#					print " ZONE A",self.useZoneA,self.zoneAduty,self.ssrZoneA,self.zoneAmeter
#					print " ZONE B", "-----",self.zoneBduty,self.ssrZoneB,self.zoneBmeter

					if self.zoneToggleCount > 33:
						self.zoneToggleCount=0
						if self.useZoneA:
							self._log("HLT: switching from A to B")
							self.useZoneA=False
							self.zoneAduty=0
							self.zoneBduty=loadRequired
						else:
							self._log("HLT: switching from B to A")
							self.useZoneA=True
							self.zoneBduty=0
							self.zoneAduty=loadRequired



					if self.zoneTemp < self.zoneTarget:
						if self.useZoneA:
							self.ssrZoneA=True
							self.zoneAduty=loadRequired
							self.zoneBduty=0
#							print "Line 221: ssrZoneA=True"
						else:
							self.ssrZoneB=True
							self.zoneAduty=0
							self.zoneBduty=loadRequired
#							print "Line 224: ssrZoneB=True"
					else:
						self.ssrZoneA=False
						self.ssrZoneB=False
#						print "Line 227: ssrZoneA=False"
#						print "Line 228: ssrZoneB=False"
			
			#
			# BOIL heating processing
			#
			if self.boilActive and not cm['_mode'].count("boil"):
				self._log("BOIL Reset")
				if not os.path.exists("simulator"):
					self.lcdDisplay.sendMessage("No target/zone temp A",3,importance=-8)		# this resets the message
				self.boilActive=False

			if cm['_mode'].count("boil") and not self.boilActive and not cm['_mode'] == "idle":
				self._log("BOIL Init")
				self._log(" - setting zoneA power on to BOIL mode")
				self._log(" - setting zoneB power on to BOIL mode")

				self.gpio.output('zoneA',1)
				self.gpio.output('zoneB',1)
				self.gpio.output('zoneAuse',1)
				self.gpio.output('zoneBuse',1)
				self._relayZoneA=True
				self._relayZoneB=True
				self._relayZoneUseA=True
				self._relayZoneUseB=True



				self.boilActive=True
				self.zoneAduty=1
				self.zoneBduty=0
				self.useZoneA=True
				self.useZoneB=True
			if cm['_mode'].count("boil") and not cm['_mode'] == "idle":
				self.boilActive=True			
				(tMin,tMax,tTarget)=cm['boil']
				self.zoneTarget=tTarget
			


				if self.zoneTemp == -1 or self.zoneTarget == -1:
					self._log("boil: no target/temp")
					if not os.path.exists("simulator"):
						self.lcdDisplay.sendMessage("No target/zone temp A",3,importance=8)
					time.sleep(3)
				else:
					if not os.path.exists("simulator"):
						self.lcdDisplay.sendMessage("No target/zone temp A",3,importance=-8)


					# if we are 95% of the temperature target then we will set this to 1
					if self.zoneTemp <  (self.zoneTarget -  0.47):
						loadRequired=self.cycle
					elif self.zoneTemp > self.zoneTarget:
						loadRequired=0
					else:
						loadRequired=0.85
					
					# load required
					self._log("BOIL: load required %s %.1f %.1f " %(loadRequired,self.zoneTemp,self.zoneTarget))
#					print "BOIL:Load Required ",loadRequired,self.zoneTemp,self.zoneTarget,self.zoneToggleCount
#					print "BOIL: ZONE A",self.useZoneA,self.zoneAduty,self.ssrZoneA,self.zoneAmeter
#					print "BOIL: ZONE B",self.zoneBduty,self.ssrZoneB,self.zoneBmeter

					if self.zoneTemp < self.zoneTarget * 0.90:
						# if we are less than 90% of the target then use both elements
						self.useZoneA=True
						self.useZoneB=True
						self.singleZone=False
						self.zoneAduty=loadRequired
						self.zoneBduty=loadRequired
					else:
						self.singleZone=True
					
					if self.singleZone:	
						if self.zoneToggleCount > 33:
							if self.useZoneA:
								self._log("BOIL: switching from A to B")
								self.useZoneA=False
								self.useZoneB=True
								self.zoneAduty=0
								self.zoneBduty=loadRequired
								self.ssrA=False
							else:
								self._log("BOIL: switching from B to A")
								self.useZoneB=False
								self.useZoneA=True
								self.zoneBduty=0
								self.zoneAduty=loadRequired
								self.ssrB=False

						else:
							if self.useZoneA:
								self.zoneAduty=loadRequired
								self.zoneBduty=0
							else:
								self.zoneAduty=0
								self.zoneBduty=loadRequired	

					if self.zoneTemp < self.zoneTarget:
						if self.useZoneA and self.useZoneB:
							self.ssrZoneA=True
							self.ssrZoneB=True
						elif self.useZoneA:
							self.ssrZoneA=True
							self.ssrZoneB=False
						else:
							self.ssrZoneB=True
							self.ssrZoneA=False
					else:
						self.ssrZoneA=False
						self.ssrZoneB=False
	

	def zoneTempThread(self):
		self._log("Listening for temeprature from Zone A")
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		sock.bind(('', self.cfg.mcastTemperaturePort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		
		while True:
			(data, addr) = sock.recvfrom(1200)		
			try:
				cm = json.loads( data )
			except:
				self._log("Error unickling input message\n%s" %(data))
				return

			checksum = cm['_checksum']
			cm['_checksum'] ="                                        "
			ourChecksum = hashlib.sha1("%s%s" %(cm,self.cfg.checksum)).hexdigest()
			if cm['currentResult'].has_key( self.cfg.hltProbe ) and self.hltActive:
				if cm['currentResult'][self.cfg.hltProbe]['valid']:
					self.zoneTemp = float( cm['currentResult'][self.cfg.hltProbe]['temperature'])
					self.zoneTempTimestamp=time.time()
				else:
					self.lcdDisplay.sendMessage("Temp Result Error",2)

			if cm['currentResult'].has_key( self.cfg.boilProbe ) and self.boilActive:
				if cm['currentResult'][self.cfg.boilProbe]['valid']:
					self.zoneTemp = float( cm['currentResult'][self.cfg.boilProbe]['temperature'])
					self.zoneTempTimestamp=time.time()
				else:
					self.lcdDisplay.sendMessage("Temp Result Error",2)

			
			

	
	def zoneBssrThread(self):
		self._log("Zone B SSR Thread active")
		while True:
			if not self.hltActive and not self.boilActive:
				self.gpio.output('ssrZoneB',0)
				self._gpiossrB=False
				self.ssrPinB=False
				time.sleep(1)
			if self.hltActive or self.boilActive:
					
				if self.ssrZoneB:
					if self.zoneBduty == 0:
						print "\tB. DUTY = 0 (temp %.2f target %.2f)" %(self.zoneTemp,self.zoneTarget)
						time.sleep(1)
					else:
						while self.singleZone and self.ssrPinA:
							print "t\t... waiting for SSR A to stop firing"
							time.sleep(0.2)
						print "\tB. ON : ",time.time()," for ", self.zoneBduty*self.cycle," has been active for", self.zoneBmeter,"(",self.zoneToggleCount,")",self.zoneTarget,self.zoneTemp
						self.gpio.output('ssrZoneB',1)
						self._gpiossrB=True
						self.ssrPinB=True
						time.sleep(self.zoneBduty*self.cycle)
#						self.ssrFanRequiredUntil=time.time()+30
#						self.gpio.output('tSsrFan',1)
						self.ssrZoneB=True
						if  self.zoneBduty == self.cycle:
							print "\tB. duty time is set to 100pcnt"
						else:
							print "\tB. OFF: ",time.time()," for ", (self.cycle-(self.zoneBduty*self.cycle))
							self.gpio.output('ssrZoneB',0)
							self._gpiossrB=False
							self.ssrPinB=False
						if self.zoneBduty == self.cycle:	
							time.sleep(0)
						else:
							print "zone B duty/cycle ",self.zoneBduty,self.cycle
							(self.cycle-(self.zoneBduty*self.cycle))
							time.sleep(self.cycle-(self.zoneBduty*self.cycle))

						self.zoneBmeter=self.zoneBmeter + (self.zoneBduty*self.cycle)
						self.zoneToggleCount=self.zoneToggleCount+ (self.zoneBduty*self.cycle)

				else:
					print "\tB. SSR MASTER FLAG OFF (temp %.2f target %.2f)" %(self.zoneTemp,self.zoneTarget)
					self.ssrPinB=False
					self.gpio.output('ssrZoneB',0)
					self._gpiossrB=False
					time.sleep(1)


	
	def zoneAssrThread(self):
		self._log("Zone A SSR Thread active")
		while True:
			if not self.hltActive and not self.boilActive:
				self.gpio.output('ssrZoneA',0)
				self._gpiossrA=False
				self.ssrPinA=False
				time.sleep(1)
			if self.hltActive or self.boilActive:	
				if self.ssrZoneA:
					if self.zoneAduty == 0:
						print "\tA. DUTY = 0 (temp %.2f target %.2f)" %(self.zoneTemp,self.zoneTarget)
						time.sleep(1)
					else:
						while self.singleZone and self.ssrPinB:
							print "t\t... waiting for SSR B to stop firing"
							time.sleep(0.2)
						print "\tA. ON : ",time.time()," for ", self.zoneAduty*self.cycle," has been active for", self.zoneAmeter,"(",self.zoneToggleCount,")",self.zoneTarget,self.zoneTemp
#						self.ssrFanRequiredUntil=time.time()+30
#						self.gpio.output('tSsrFan',1)
						self.gpio.output('ssrZoneA',1)
						self._gpiossrA=True
						self.ssrPinA=True
						if self.zoneAduty == self.cycle:	
							time.sleep(self.cycle)
						else:
							time.sleep(self.zoneAduty*self.cycle)
						if  self.zoneAduty ==  self.cycle:
							print "\tA. duty time is set to 1"
						else:
							print "\tA. OFF: ",time.time()," for ", (self.cycle-(self.zoneAduty*self.cycle))
							self.gpio.output('ssrZoneA',0)
							self._gpiossrA=False
							self.ssrPinA=False
						if self.zoneAduty == self.cycle:
							time.sleep(0)
						else:
							time.sleep(self.cycle-(self.zoneAduty*self.cycle))
							print "zone A duty/cycle ",self.zoneAduty,self.cycle,(self.cycle-(self.zoneAduty*self.cycle))

						self.zoneAmeter=self.zoneAmeter + (self.zoneAduty * self.cycle)
						self.zoneToggleCount=self.zoneToggleCount+ (self.zoneAduty*self.cycle)

				else:
					print "\tA. SSR MASTER FLAG OFF (temp %.2f target %.2f)" %(self.zoneTemp,self.zoneTarget)
					self.gpio.output('ssrZoneA',0)
					self._gpiossrA=False
					self._relayZoneUseA=False
					self.ssrPinA=False
					time.sleep(1)




	def broadcastResult(self):
		print "advertising our SSR capabiltiies"
		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage={}
		controlMessage['_operation'] = 'ssrrelay'
		controlMessage['_checksum'] ="                                        "

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		while 1:
			controlMessage['relayZoneA'] = self._relayZoneA
			controlMessage['relayZoneB'] = self._relayZoneB
			controlMessage['relayZoneUseA'] = self._relayZoneUseA
			controlMessage['relayZoneUseB'] = self._relayZoneUseB
			controlMessage['gpioSsrA'] = self._gpiossrA	
			controlMessage['gpioSsrB'] = self._gpiossrB

			if self._relayZoneA:
				o=open("ipc/relayZoneA","w")
				o.close()
			else:
				try:
					os.unlink("ipc/relayZoneA")
				except:
					pass
			if self._relayZoneB:
				o=open("ipc/relayZoneB","w")
				o.close()
			else:
				try:
					os.unlink("ipc/relayZoneB")
				except:
					pass

			if self._relayZoneUseA:
				o=open("ipc/relayZoneUseA","w")
				o.close()
			else:
				try:
					os.unlink("ipc/relayZoneUseA")
				except:
					pass

			if self._relayZoneUseB:
				o=open("ipc/relayZoneUseB","w")
				o.close()
			else:
				try:
					os.unlink("ipc/relayZoneUseB")
				except:
					pass

#			print "broadcastResult,",self._gpiossrA,self._gpiossrB
			if self._gpiossrA:
				o=open("ipc/gpioSsrA","w")
				o.close()
			else:
#				print "trying to remove gpioSsrA file"
				try:
					os.unlink("ipc/gpioSsrA")
#					print "scucess"
				except:
					pass
			if self._gpiossrB:
				o=open("ipc/gpioSsrB","w")
				o.close()
			else:
				try:
					os.unlink("ipc/gpioSsrB")
				except:
					pass


			msg= json.dumps(controlMessage)
			msg= "%s%s" %(msg," "*(1200-len(msg))) 
			sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastSsrRelayPort))
			time.sleep(1)


if __name__ == '__main__':
	try:
		controller = pitmSsrRelay()
		
		# get under the control of the flasher
		broadcastResult = threading.Thread(target=controller.broadcastResult)
		broadcastResult.daemon = True
		broadcastResult.start()

		# get under the control of the contoller
		controlThread = threading.Thread(target=controller.submission)
		controlThread.daemon = True
		controlThread.start()
		
		# get temperature status from zone a
		zoneTempThread = threading.Thread(target=controller.zoneTempThread)
		zoneTempThread.daemon = True
		zoneTempThread.start()
		
#		# start a SSR thread
		zoneAssrThread = threading.Thread(target=controller.zoneAssrThread)
		zoneAssrThread.daemon = True
		zoneAssrThread.start()
#		
#		# start a SSR thread
		zoneBssrThread = threading.Thread(target=controller.zoneBssrThread)
		zoneBssrThread.daemon = True
		zoneBssrThread.start()

		
		while 1:
			time.sleep(1)

	except KeyboardInterrupt:
		controller.uncontrol()
		pass


