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

##
##		if self.mcastMembership:
#			self._log("Unregistering Multicast Control Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastPort))
#			self.sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.cfg.MCAST_GRP) + socket.inet_aton('0.0.0.0'))
#			self.mcastMembership=False
			
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
		#print controlMessage
		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 

		if len(msg) > 1200:
			self._err("Cannot send message - packet too big")
			return

		sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastTemperaturePort))
		sendSocket.close()
#		print "sending ",controlMessage



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
		if self._mode.count("hlt"):
			hlt=True
		if self._mode.count("mash"):
			mash=True
		if self._mode.count("boil"):
			boil=True
		if self._mode.count("cool"):
			boil=True

		if self._mode =='ferm':
			ferm=True

		if ferm or hlt or mash or boil:
			self.gpio.output("tempProbes",True)
		else:	
			self.gpio.output("tempProbes",False)


		for probe in os.listdir( self.tempBaseDir ):
			if probe[0:2] == "28":
				if self.probesToMonitor.has_key( probe):
					if self.probesToMonitor[probe]:
						print "Permitted to monitor ",probe,
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
							if text.count("YES"):		# CRC=NO for failed results	
								print temp
								#temperature = float(temp.split(" ")[9][2:])/1000
								temperature = float(temp.split("=")[1][0:3])/10


								if not self.lastResult.has_key(probe):
									self.lastResult[probe]=0

								# fudge factor for 0 / 85 results when not connected	
								if temperature == 0 and self.lastResult[probe] == 85:
									self._log("Ignoring result - cannot swing from 0 to 85")
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}					
								elif temperature == 85 and self.lastResult[probe] < 84:
									self._log("Ignoring result - don't believe we went from <84 to 85 in one reading")
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}				
								elif temperature == 85 and self.lastResult[probe] < 86:
									self._log("Ignoring result - don't believe we went from >85 to 85 in one reading")
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}				
								elif temperature == 85 and self.lastResult[probe] == 0:
									self._log("Ignoring result - cannot swing from 85 to 0")
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}				
								elif temperature < 0:
									self._log("Ignoring Temperature, <0")
									
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}				
								elif temperature == 0 and ( (self.lastResult[probe] >0 and self.lastResult[probe] <0)):
									self._log("Accepting result %s lastResult %s" %(temperature,self.lastResult[probe]))
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':True}				
								elif temperature == 85 and ( (self.lastResult[probe] > 85 and self.lastResult[probe] <85)):
									self._log("Accepting result %s lastResult %s" %(temperature,self.lastResult[probe]))
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':True}				
								elif temperature == 0 and self.lastResult[probe] == 0:
									self._log("Cannot have 0 in concurrent readings")
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}				
								elif temperature == 85 and self.lastResult[probe] == 85:
									self._log("Cannot have 85 in concurrent readings")
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':False}								
								else:	
									self._log("Probe: %s Temperature: %s" %(probe,temperature))
									self.currentTemperatures[ probe ] = {'timestamp':time.time(),'temperature':temperature,'valid':True}				
					
								self.lastResult[probe]=temperature

							time.sleep(1)		# try a 0.05 delay to avoid false readings



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
#		print "Mode:", cm['_mode']
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
		if cm['_mode'].count("ferm"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.fermProbe ] = True
			self._targetFerm=cm['ferm']
		elif cm['_mode'].count("sparge") and cm['_mode'].count("mash"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self.probesToMonitor[ self.cfg.mashAProbe ] = True
			self.probesToMonitor[ self.cfg.mashBProbe ] = True
			self._targetSparge=cm['sparge']		
			self._targetMash=cm['mash']
		elif cm['_mode'].count("sparge"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self._targetSparge=cm['sparge']		
		elif cm['_mode'].count("hlt") and cm['_mode'].count("mash"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self.probesToMonitor[ self.cfg.mashAProbe ] = True
			self.probesToMonitor[ self.cfg.mashBProbe ] = True
			self._targetHlt=cm['hlt']	
			self._targetMash=cm['mash']	
		elif cm['_mode'].count("hlt"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.hltProbe ] = True
			self._targetHlt=cm['hlt']
		elif cm['_mode'].count("cool"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.boilProbe ] = True
			self._targetFerm=cm['ferm']
		elif cm['_mode'].count("boil"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.boilProbe ] = True
			self._targetBoil=cm['boil']
		elif cm['_mode'].count("mash"):
			self.doTemperatureing=True
			self.probesToMonitor[ self.cfg.mashAProbe ] = True
			self.probesToMonitor[ self.cfg.mashBProbe ] = True
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



