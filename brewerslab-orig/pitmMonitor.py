from __future__ import division
#!/usr/bin/python

# piTempLedFlasher
import json
import os
import hashlib
import struct
import socket
import syslog
import sys
import threading
import time



from pitmCfg import pitmCfg


if os.path.exists("simulator"):
	import fakeRPi.GPIO as GPIO
else:
	import RPi.GPIO as GPIO


from pitmCfg import pitmCfg
from pitmLCDisplay import pitmLCDisplay
from pitmLedFlasher import pitmLedFlasher

class pitmMonitor:


	def __init__(self):
		self.logging=2		# 1 = syslog, 2 = stderr
		self.cfg = pitmCfg()

		self._mode="Unknown"
		self.mcastMembership=False
		self.doMonitoring=False
		self.lcdDisplay = pitmLCDisplay()
		self.ledFlasher = pitmLedFlasher()
		self.probes={}
		self.lastTempReading={}
		self.tempTargetHlt=(-1,-1,-1)	#
		self.tempTargetSparge=(-1,-1,-1)	# 
		self.tempTargetMash=(-1,-1,-1)	# 
		self.tempTargetBoil=(-1,-1,-1)	#
		self.tempTargetFerm=(-1,-1,-1)	#

		# fuzzy logic to track when fermentation is complete
		self.fermStarted=0	
		self.lastalarm=""
	
	def _log(self,msg):
		if self.logging == 1:
			syslog.syslog(syslog.LOG_DEBUG, msg)
		elif self.logging == 2:
			sys.stderr.write("%s,%s,monitor,%s\n" %(time.ctime(),time.time(),msg))

			
	def _err(self,msg):
		syslog.syslog(syslog.LOG_ERR, msg)
		sys.stderr.write("%s\n" %(msg))


	def broadcastResult(self):
		# We should send a broadcast every second whilst we are alive.
		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage={}
		controlMessage['_operation'] = 'monitorResults'
		controlMessage['_checksum'] ="                                        "

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 

		if len(msg) > 1200:
			self._err("Cannot send message - packet too big")
			return

		sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastMonitorPort))
		sendSocket.close()


	def submission(self):
		self._log("Submitting to control of Controller")
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True

		while True:
			(data, addr) = self.sock.recvfrom(1200)
			time.sleep(0.5)
#			self.decodeMessage(data)	
				

	def decodeTempMessage(self,data,zone="Unknown"):
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
		self.doMonitoring=False
		if cm.has_key("_mode"):
			self._mode=cm['_mode']
			if cm['_mode'].count( "delayed_HLT"):
				self.doMonitoring=True
			if cm['_mode'].count( "hlt"):
				self.doMonitoring=True
			if cm['_mode'] == "sparge":
				self.doMonitoring=True

			if cm['_mode'].count("mash"):
				self.doMonitoring=True

			if cm['_mode'].count("boil"):
				self.doMonitoring=True
			
			if cm['_mode'].count("pump"):
				self.doMonitoring=True

			if cm['_mode'].count("cool"):
				self.doMonitoring=True
			
			if cm['_mode'].count("ferm"):
				self.doMonitoring=True

		print "Mode:",cm['_mode'],zone,self.doMonitoring
		print cm

		if cm.has_key("tempTargetHlt"):
			self.tempTargetHlt=cm['tempTargetHlt']
		if cm.has_key("tempTargetSparge"):
			self.tempTargetSparge=cm['tempTargetSparge']
		if cm.has_key("tempTargetMash"):
			self.tempTargetMash=cm['tempTargetMash']
		if cm.has_key("tempTargetFerm"):
			self.tempTargetFerm=cm['tempTargetFerm']
		if cm.has_key("tempTargetBoil"):
			self.tempTargetBoil=cm['tempTargetBoil']

		if cm.has_key("currentResult"):
			if self.doMonitoring:
#				if zone == "A":
#					print cm
				self.updateResults( cm['currentResult'] )
#				print "updateReuslts called"


	def decodeMessage(self,data,zone="Unknown"):
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
		self.doMonitoring=False
		if cm.has_key("_mode"):
			self._mode=cm['_mode']
			if cm['_mode'].count( "delayed_HLT"):
				self.doMonitoring=True

			if cm['_mode'].count( "hlt"):
				self.doMonitoring=True

			if cm['_mode'].count("mash"):
				self.doMonitoring=True

			if cm['_mode'].count("boil"):
				self.doMonitoring=True
			
			if cm['_mode'].count("ferm"):
				self.doMonitoring=True

#		print "Mode:",cm['_mode'],zone,self.doMonitoring
		print cm

		if cm.has_key("tempTargetHlt"):
			self.tempTargetHlt=cm['tempTargetHlt']
		if cm.has_key("tempTargetSparge"):
			self.tempTargetSparge=cm['tempTargetSparge']
		if cm.has_key("tempTargetMash"):
			self.tempTargetMash=cm['tempTargetMash']
		if cm.has_key("tempTargetFerm"):
			self.tempTargetFerm=cm['tempTargetFerm']
		if cm.has_key("tempTargetBoil"):
			self.tempTargetBoil=cm['tempTargetBoil']

		if cm.has_key("currentResult"):
			if self.doMonitoring:
#				if zone == "A":
#					print cm
				self.updateResults( cm['currentResult'] )
#				print "updateReuslts called"

	def updateResults(self,result):
		for probe in result:
#			print probe,result[probe]['valid']
			if result[probe]['valid']:
				if not self.probes.has_key( probe ):
					self.probes[probe]=[]
					self.lastTempReading[probe]=-1
				
		
				if  result[probe]['timestamp'] <= self.lastTempReading[probe]:
					self._log("probe,%s,temp,N/A,status,not using temp result as it has been used before" %(probe))
				else:
					self._log("probe,%s,temp%s,,using temperature result - %s seconds old" %(probe,result[probe]['temperature'], time.time()-result[probe]['timestamp']))
					self.lastTempReading[probe]= result[probe]['timestamp']
					self.probes[probe].append( result[probe]['temperature'] )
					if len(self.probes[probe]) > 86400:
						self.probes[probe].pop(0)
			else:
				self._log("probe,%s,temp,N/A,invalid result,%s" %(probe,result[probe]['temperature']))
	#	print self.probes



	def updateStatsZoneA(self):
		self._log("Starting pitmMonitor Stats Collection for Zone A")
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastTemperaturePort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True

		while True:
			(data, addr) = self.sock.recvfrom(1200)
			self.decodeTempMessage(data,zone="A")	
			time.sleep(0.5)		

			

	def updateStats2(self):
		self._log("Starting pitmMonitor Stats Collection for Zone B")
		self.sockb = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sockb.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sockb.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sockb.bind(('', self.cfg.mcastTemperatureSecondPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sockb.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True
#
		while True:
			(data, addr) = self.sockb.recvfrom(1200)
			self.decodeMessage(data,zone="B")	
			time.sleep(0.5)		

			
	def getProbeDetail(self,probe):
		probeOk=False
		probeid=""
		led=""
		targetMin=-2
		targetMax=-2
		target=-2
		if self._mode.count( "cool") and probe == self.cfg.boilProbe:
			probeOk=True
			probeid="cool :"
			led="lBoil"
			(targetMin,targetMax,target)=self.tempTargetFerm
		if self._mode.count( "boil") and probe == self.cfg.boilProbe:
			probeOk=True
			probeid="boil :"
			led="lBoil"
			(targetMin,targetMax,target)=self.tempTargetBoil
		if (self._mode.count("delayed_HLT") or self._mode.count( "hlt")) and probe == self.cfg.hltProbe:
			probeOk=True
			if self._mode.count("sparge"):
				led="lSparge"
				probeid="sparg:"
				(targetMin,targetMax,target)=self.tempTargetSparge
			else:
				led="lHlt"
				probeid="hlt  :"
				(targetMin,targetMax,target)=self.tempTargetHlt
		if self._mode== "sparge" and probe == self.cfg.mashAProbe:
			probeOk=True
			probeid="mashA:"
			led="lMash"
			(targetMin,targetMax,target)=self.tempTargetMash
		if self._mode.count( "mash") and probe == self.cfg.mashAProbe:
			probeOk=True
			probeid="mashA:"
			led="lMash"
			(targetMin,targetMax,target)=self.tempTargetMash
		if self._mode=="sparge" and probe == self.cfg.mashBProbe:
			probeOk=True
			probeid="mashB:"	
			led="lMash"
			(targetMin,targetMax,target)=self.tempTargetMash

		if self._mode.count( "mash") and probe == self.cfg.mashBProbe:
			probeOk=True
			probeid="mashB:"	
			led="lMash"
			(targetMin,targetMax,target)=self.tempTargetMash

		if self._mode.count("ferm") and probe == self.cfg.fermProbe:
			probeOk=True
			probeid="ferm :"
			led="lFerm"
			(targetMin,targetMax,target)=self.tempTargetFerm

		return (probeOk,probeid, targetMin,targetMax, target,led)

	def updateDisplay(self):
		self._log("Starting pitmMonitor display for line 0 ")
		while True:
			if not self.doMonitoring:
				self.ledFlasher.sendMessage( 'lHlt','off')
				self.ledFlasher.sendMessage( 'lSparge','off')
				self.ledFlasher.sendMessage( 'lBoil','off')
				self.ledFlasher.sendMessage( 'lMash','off')
				self.ledFlasher.sendMessage( 'lFerm','off')
				if not self._mode == "Unknown" and not self._mode == "idle":	
					self.lcdDisplay.sendMessage("",0,importance=0)
					self.lcdDisplay.sendMessage(" - no temp results -",1,importance=0)
					self.lcdDisplay.sendMessage("",2,importance=0)

			if self.doMonitoring:
				try:

					self.ledFlasher.sendMessage( 'lHlt','off')
					self.ledFlasher.sendMessage( 'lSparge','off')
					self.ledFlasher.sendMessage( 'lBoil','off')
					self.ledFlasher.sendMessage( 'lMash','off')
					self.ledFlasher.sendMessage( 'lFerm','off')
					time.sleep(0.3)
					line=0


					if not self._mode == "idle":
						for probe in self.probes:

							activity=""
							alert=False
							(probeOk,probeid,targetMin,targetMax,target,led) = self.getProbeDetail(probe)

							if probeOk:
								self._log("display,%s,current,%s,target,%s" %(probeid,self.probes[probe][-1], target))
								if self.lastTempReading[probe] + 30  < time.time():
									self.lcdDisplay.sendMessage("%s%sXX.X Aim:%.1f" %( probeid,alarm, target ), line,alert=alert)
									self.ledFlasher.sendMessage(led,'purple')
								else:
									if self._mode.count( "cool") or self._mode == "boil/pump":
										if self.probes[probe][-1] < 67 and not os.path.exists("ipc/activityWhirlpool"):
											flag=open("ipc/activityWhirlpool","w")
											flag.close()
										if self.probes[probe][-1] < 30 and not os.path.exists("ipc/activityCool30"):
											flag=open("ipc/activityCool30","w")
											flag.close()
									if self._mode == "hlt":
										if self.probes[probe][-1] > 60 and not os.path.exists("ipc/activityMashTunPre"):
											flag=open("ipc/activityMashTunPre","w")
											flag.close()
										if self.probes[probe][-1] > target-2 and not os.path.exists("ipc/activityHltTemp"):
											flag=open("ipc/activityHltTemp","w")
											flag.close()
									if self._mode.count("sparge"):
										if self.probes[probe][-1] > target-2 and not os.path.exists("ipc/activitySpargeTemp"):
											flag=open("ipc/activitySpargeTemp","w")
											flag.close()
									if self._mode == "boil":
										if self.probes[probe][-1] > target-2 and not os.path.exists("ipc/activityReachedBoil"):
											flag=open("ipc/activityReachedBoil","w")
											flag.close()
						
	
							#
									alarm=""
									if self.probes[probe][-1] > targetMax:
										alarm=">"
										self.ledFlasher.sendMessage(led,'red')
									elif self.probes[probe][-1] < targetMin:
										self.ledFlasher.sendMessage(led,'blue')
										alarm="<"
									else:
										alarm=""
										self.ledFlasher.sendMessage(led,'green')
									self.lcdDisplay.sendMessage("%s%s%.1f Aim:%.1f" %( probeid,alarm,self.probes[probe][-1], target ), line,alert=alert)


									if self._mode == "ferm":
										if not alarm == self.lastalarm:
											self.lastalarm=alarm
											print "ALARM FLAG SET",alarm
											if alarm == "":
												flag=open("ipc/fermprogress/%s-normal" %(time.time()),"w")
												flag.close()
											elif alarm == "<":
												flag=open("ipc/fermprogress/%s-low" %(time.time()),"w")
												flag.close()
											elif alarm == ">":
												flag=open("ipc/fermprogress/%s-high" %(time.time()),"w")
												flag.close()
													
										if alarm == "" and not os.path.exists("ipc/ferm-pitching-temp"):
											flag=open("ipc/ferm-pitching-temp","w")
											flag.close()
											self.fermStarted=time.time()



								line=line+1
						time.sleep(3)

						if line == 1:
							self.lcdDisplay.sendMessage("",1,importance=0)
						if line == 1 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)
						if line == 2 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)
						line=0
						for probe in self.probes:
							activity=""
							alert=False
							(probeOk,probeid,targetMin,targetMax,target,led) = self.getProbeDetail(probe)

							if probeOk:
								self._log("display,%s,current,%s,maximum,%s" %(probeid,self.probes[probe][-1], max(self.probes[probe])))
								if self.lastTempReading[probe] + 30 < time.time():
									self.ledFlasher.sendMessage(led,'purple')
									self.lcdDisplay.sendMessage("%s%sXX.X Max:%.1f" %( probeid,alarm, max(self.probes[probe])), line,alert=alert)
								else:
									alarm=""
									if self.probes[probe][-1] > targetMax:
										alarm=">"
										self.ledFlasher.sendMessage(led,'red')
									elif self.probes[probe][-1] < targetMin:
										alarm="<"
										self.ledFlasher.sendMessage(led,'blue')
									else:
										self.ledFlasher.sendMessage(led,'green')
									self.lcdDisplay.sendMessage("%s%s%.1f Max:%.1f" %( probeid,alarm,self.probes[probe][-1], max(self.probes[probe])), line,alert=alert)
								line=line+1
						time.sleep(3)
						if line == 1:
							self.lcdDisplay.sendMessage("",1,importance=0)
						if line == 1 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)
						if line == 2 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)


						line=0
						for probe in self.probes:
							activity=""
							alert=False
							(probeOk,probeid,targetMin,targetMax,target,led) = self.getProbeDetail(probe)

							if probeOk:
								self._log("display,%s,current,%s,minimum,%s" %(probeid,self.probes[probe][-1], min(self.probes[probe])))
								if self.lastTempReading[probe] + 30  < time.time():
									self.ledFlasher.sendMessage(led,'purple')
									self.lcdDisplay.sendMessage("%s%sXX.X Min:%.1f" %(probeid,alarm, min(self.probes[probe])),line,alert=alert)
								else:
									alarm=""

									if self.probes[probe][-1] > targetMax:
										alarm=">"
										self.ledFlasher.sendMessage(led,'red')
									elif self.probes[probe][-1] < targetMin:
										alarm="<"
										self.ledFlasher.sendMessage(led,'blue')
									else:
										alarm=" "
										self.ledFlasher.sendMessage(led,'green')
									self.lcdDisplay.sendMessage("%s%s%.1f Min:%.1f" %(probeid,alarm, self.probes[probe][-1], min(self.probes[probe])),line,alert=alert)
								line=line+1
						time.sleep(3)

						if line == 1:
							self.lcdDisplay.sendMessage("",1,importance=0)
						if line == 1 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)
						if line == 2 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)

						line=0
						for probe in self.probes:
							activity=""
							alert=False
							(probeOk,probeid,targetMin,targetMax,target,led) = self.getProbeDetail(probe)

							if probeOk:
								self._log("display,%s,current,%s,average,%s" %(probeid,self.probes[probe][-1], sum(self.probes[probe])/len(self.probes[probe])))
								if self.lastTempReading[probe] + 30  < time.time() :
									self.ledFlasher.sendMessage(led,'purple')

									self.lcdDisplay.sendMessage("%s%sXX.X Avg:%.1f" %(probeid,alarm, sum(self.probes[probe])/len(self.probes[probe])),line,alert=alert)
								else:
									if self.probes[probe][-1] > targetMax:
										alarm=">"
										self.ledFlasher.sendMessage(led,'red')
									elif self.probes[probe][-1] < targetMin:
										alarm="<"
										self.ledFlasher.sendMessage(led,'blue')
									else:
										alarm=" "
										self.ledFlasher.sendMessage(led,'green')
									self.lcdDisplay.sendMessage("%s%s%.1f Avg:%.1f" %(probeid,alarm, self.probes[probe][-1],sum(self.probes[probe])/len(self.probes[probe])),line,alert=alert)

								line=line+1
						if line == 1:
							self.lcdDisplay.sendMessage("",1,importance=0)
						if line == 1 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)
						if line == 2 and not self._mode == "ferm":
							self.lcdDisplay.sendMessage("",2,importance=0)
				except ImportError:
					print "Dictionary might have changed sized .. passing"	
			time.sleep(3)




if __name__ == '__main__':
	try:
		controller = pitmMonitor()

		# get under the control of the contoller
		controlThread = threading.Thread(target=controller.submission)
		controlThread.daemon = True
		controlThread.start()
		

		updateStatsThread = threading.Thread(target=controller.updateStatsZoneA)
		updateStatsThread.daemon = True
		updateStatsThread.start()
	
		updateStats2Thread = threading.Thread(target=controller.updateStats2)
		updateStats2Thread.daemon = True
		updateStats2Thread.start()
		

		updateDisplayThread = threading.Thread(target=controller.updateDisplay)
		updateDisplayThread.daemon = True
		updateDisplayThread.start()

		
		while 1:
			controller.broadcastResult()
			time.sleep(1)

	except KeyboardInterrupt:
		controller.uncontrol()



