#!/usr/bin/python

# piTempTemperature Temperature
import os
import hashlib
import struct
import socket
import syslog
import json
import sys
import threading
import time
import re
from pitmCfg import pitmCfg
from gpiotools import *

if os.path.exists("simulator"):
	import fakeRPi.GPIO as GPIO
else:
	import RPi.GPIO as GPIO





class pitmTemperature:


	def __init__(self):
		self.logging=2		# 1 = syslog, 2 = stderr
		self.cfg = pitmCfg()
		self.gpio = gpiotools()
		self.rxTemp=re.compile("^.*t=(\d+)")

		self.probesToMonitor={}
		self.probesToMonitor[ self.cfg.hltProbe ] = False
		self._targetHlt=(-1,-1,-1)
		self._targetMash=(-1,-1,-1)
		self._targetSparge=(-1,-1,-1)
		self._targetFerm=(-1,-1,-1)
		self._targetBoil=(-1,-1,-1)
		self._mode="unknown-mode"
		self._brewlog="<unknown brewlog.>"
		self._recipe="<unknown recipe>"

		self.mcastMembership=False
		self.currentScenario="unknown"
		self.currentTemperatures={}
		self.currentStatus=0	# 0 = temperatureing
		self.doTemperatureing=False

		# odd readings
		self.odd_readings = {}

		# we need to supress results of 0 and 85 if they are the instant result
		self.lastResult={}

		if os.path.exists("simulator"):
			try:
				os.mkdir("ipc/fake1wire")
			except:
				pass
			self.tempBaseDir="ipc/fake1wire/"
		else:
			self.tempBaseDir="/sys/bus/w1/devices/"

	def uncontrol(self):
		print "closing off relays"
		self.gpio.output("tempProbes",0)

	
	def __del__(self):
		self.uncontrol()

			
	def _log(self,msg):
		if self.logging == 1:
			syslog.syslog(syslog.LOG_DEBUG, msg)
		elif self.logging == 2:
			sys.stderr.write("%s\n" %(msg))

			
	def _err(self,msg):
		syslog.syslog(syslog.LOG_ERR, msg)
		sys.stderr.write("%s\n" %(msg))



	def broadcastResult(self):
		# We should send a broadcast every second whilst we are alive.
		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage={}
		controlMessage['_operation'] = 'temperatureResults1'
		controlMessage['_checksum'] ="                                        "
		controlMessage['currentStatus']=self.currentStatus
		controlMessage['currentResult']=self.currentTemperatures
		
		# we reflect _mode so we don't have to have everything listen to it
		controlMessage['_mode']=self._mode
		# we also refelct the target temperature information which we got from
		# governort
		controlMessage['tempTargetHlt']=self._targetHlt
		controlMessage['tempTargetSparge']=self._targetSparge
		controlMessage['tempTargetMash']=self._targetMash
		controlMessage['tempTargetBoil']=self._targetBoil
		controlMessage['tempTargetFerm']=self._targetFerm
		controlMessage['_brewlog'] = self._brewlog
		controlMessage['_recipe'] = self._recipe
		controlMessage['mashA']= self.cfg.mashAProbe
		controlMessage['mashB']= self.cfg.mashBProbe
		controlMessage['hlt']=self.cfg.hltProbe
		controlMessage['boil']=self.cfg.boilProbe
		controlMessage['ferm']=self.cfg.fermProbe

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 

		if len(msg) > 1200:
			self._err("Cannot send message - packet too big")
			return

		sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastTemperaturePort))
		sendSocket.close()


	def _reject_result(self, probe, temperature, reason="unspecified"):
		self.odd_readings[probe].append(temperature)
		self._log('rejecting result %s %s (reason: %s)' %(probe, temperature, reason))
		self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}				

	def _accept_adjust_and_add_a_reading(self, probe, temperature):
		adjust=0
		if self.cfg.probeAdjustments.has_key(probe):
			for (adjustMin, adjustMax, adjustAmount) in self.cfg.probeAdjustments[ probe ]:
				if temperature >= adjustMin and temperature < adjustMax:
					adjust=adjustAmount
					temperature=temperature+adjust

		self._log("Accepting result %s lastResult %s (Adjusted by %s)" % (temperature, self.lastResult[probe], adjust))
		self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':True}				
		self.lastResult[probe]=temperature
		self.odd_readings[probe] = []

	def getResult(self):
		

		#
		#
		# set temperature probe relays to the correct value
		#
		#
		
		hlt=False
		mash=False
		boil=False
		ferm=False
		if self._mode == "sparge":
			mash=True

		if self._mode.count("delayed_HLT"):
			hlt=True
		if self._mode.count("hlt"):
			hlt=True
		if self._mode.count("mash"):
			mash=True
		if self._mode.count("boil"):
			boil=True
		if self._mode.count("cool"):
			boil=True
			ferm=True
		if self._mode.count("pump"):
			boil=True
			ferm=True
		if self._mode =='ferm-wait':
			ferm=True
		if self._mode =='ferm':
			ferm=True
		# previously we toggled a relay which disconnected
		# the DS18B20 probes, but no longer do this

		for probe in os.listdir( self.tempBaseDir ):
			if probe[0:2] == "28":
				if self.probesToMonitor.has_key( probe):

					# A place to store odd results
					if not self.odd_readings.has_key(probe):
						self.odd_readings[probe] = []

					if self.probesToMonitor[probe]:
						try:
						
							o=open( "%s/%s/w1_slave" %(self.tempBaseDir,probe))
							text=o.readline()
							temp=o.readline()
							o.close()
							openOk=True
						except:
							openOk=False
							print " - oops couldn't open... burrying our head in the sand"
						if openOk:
							if text.count("NO"):
								self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':0,'valid':False}				
								print
							if text.count("YES") and self.rxTemp.match(temp):		# CRC=NO for failed results	
								#rxTemp=re.compile("^.*t=(\d+)")
								
								(temp,)=self.rxTemp.match(temp).groups()
								temperature=float(temp)/1000

								if not self.lastResult.has_key(probe):
									self.lastResult[probe]=0

								if (self.lastResult[probe]) == 0 or len(self.odd_readings[probe]) > 5:
									self._accept_adjust_and_add_a_reading(probe, temperature)
								else:
									if temperature > self.lastResult[probe] * 1.25 or temperature < self.lastResult[probe] * 0.75:
										self._reject_result(probe, temperature, '+/- 25%% swing')
									else:
										self._accept_adjust_and_add_a_reading(probe, temperature)
				

							time.sleep(0.5)		# try a 0.05 delay to avoid false readings



	def submission(self):
		self._log("Submitting to control of Controller")
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True


		if os.path.exists("/tmp/standalone-temp-active"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.tempProbe ] = True
			self._targetFerm=19
		while True:
			(data, addr) = self.sock.recvfrom(1200)
			self.decodeMessage(data)	
				

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
		self._mode=cm['_mode']

		if cm.has_key("_recipe"):
			self._recipe=cm['_recipe']
		if cm.has_key("_brewlog"):
			self._brewlog=cm['_brewlog']

		# looks like we receive targets out of cm['boil'], cm['ferm'], cm['mash'], cm['hlt']	
		# these come from governor via sendOrders()
		# so now we are sending this back on the broadcast of our results, with tempTarget (HLT,Boil, Ferm)
		# and tempTarget2 (Mash)
		self._targetHlt=(-1,-1,-1)
		self._targetMash=(-1,-1,-1)
		self._targetSparge=(-1,-1,-1)
		self._targetFerm=(-1,-1,-1)
		self._targetBoil=(-1,-1,-1)
		if cm['_mode'].count("pump") or cm['_mode'].count("cool"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.fermProbe ] = True
			self.probesToMonitor[ self.cfg.boilProbe ] = True
			self.probesToMonitor[ self.cfg.mashAProbe ] = False
			self.probesToMonitor[ self.cfg.mashBProbe ] = False
			self.probesToMonitor[ self.cfg.hltProbe ] =False
			self._targetFerm=cm['ferm']
			self._targetBoil=cm['boil']
		elif cm['_mode'].count("ferm"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.fermProbe ] = True
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self.probesToMonitor[ self.cfg.mashAProbe ] = False
			self.probesToMonitor[ self.cfg.mashBProbe ] = False
			self.probesToMonitor[ self.cfg.hltProbe ] =False
			self._targetFerm=cm['ferm']
		elif cm['_mode'].count("sparge"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.fermProbe ] = False
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self.probesToMonitor[ self.cfg.mashAProbe ] = True
			self.probesToMonitor[ self.cfg.mashBProbe ] = True
			self._targetMash=cm['mash']
		elif cm['_mode'].count("delayed_HLT"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self.probesToMonitor[ self.cfg.fermProbe ] = True
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self.probesToMonitor[ self.cfg.mashAProbe ] = False
			self.probesToMonitor[ self.cfg.mashBProbe ] = False
			self._targetHlt=cm['hlt']	
		elif cm['_mode'].count("hlt") and cm['_mode'].count("mash"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self.probesToMonitor[ self.cfg.mashAProbe ] = True
			self.probesToMonitor[ self.cfg.mashBProbe ] = True
			self.probesToMonitor[ self.cfg.fermProbe ] = True
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self._targetHlt=cm['hlt']	
			self._targetMash=cm['mash']	
		elif cm['_mode'].count("hlt"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self.probesToMonitor[ self.cfg.mashAProbe ] = False
			self.probesToMonitor[ self.cfg.mashBProbe ] = False
			self.probesToMonitor[ self.cfg.fermProbe ] = False
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self._targetHlt=cm['hlt']
		elif cm['_mode'].count("delayed_HLT"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self.probesToMonitor[ self.cfg.mashAProbe ] = False
			self.probesToMonitor[ self.cfg.mashBProbe ] = False
			self.probesToMonitor[ self.cfg.fermProbe ] = False
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self._targetHlt=cm['hlt']
		elif cm['_mode'].count("boil"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.boilProbe ] = True
			self.probesToMonitor[ self.cfg.hltProbe ] = False
			self.probesToMonitor[ self.cfg.mashAProbe ] = False
			self.probesToMonitor[ self.cfg.mashBProbe ] = False
			self.probesToMonitor[ self.cfg.fermProbe ] = False
			self._targetBoil=cm['boil']
		elif cm['_mode'].count("mash"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.mashAProbe ] = True
			self.probesToMonitor[ self.cfg.mashBProbe ] = True
			self.probesToMonitor[ self.cfg.fermProbe ] = False
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self.probesToMonitor[ self.cfg.hltProbe ] = False
			self._targetMash=cm['mash']
		else:
			self.probesToMonitor[ self.cfg.mashAProbe ] = False
			self.probesToMonitor[ self.cfg.mashBProbe ] = False
			self.probesToMonitor[ self.cfg.fermProbe ] = False
			self.probesToMonitor[ self.cfg.boilProbe ] = False
			self.probesToMonitor[ self.cfg.hltProbe ] = False
			self.doTemperatureing=False


	def start(self):
		self._log("Starting pitmTemperature")



		while True:
			self.getResult()
			self.broadcastResult()
			time.sleep(1)




if __name__ == '__main__':
	try:

		controller = pitmTemperature()


		
		# get under the control of the contoller
		controlThread = threading.Thread(target=controller.submission)
		controlThread.daemon = True
		controlThread.start()
		
		controller.start()


	except KeyboardInterrupt:		

		controller.uncontrol()



