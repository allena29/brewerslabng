#!rusr/bin/python

# piTempMonitor Controller
import urllib2
import re
import json
import hashlib
import os
import struct
import socket
import syslog
import sys
import threading
import time
import twitter
from tweetAuth import tweetAuth
from pitmCfg import pitmCfg
from pitmLCDisplay import pitmLCDisplay
from pitmLedFlasher import *
from gpiotools2 import *


class pitmController:


	def __init__(self):
		self.logging=3		# 1 = syslog, 2 = stderr
		self.lastLog=["","","","","","","","","","",""]	
		self.cfg = pitmCfg()
		self.lcdDisplay = pitmLCDisplay()
		self.ledFlasher = pitmLedFlasher()
		self.gpio=gpiotools2()
		
		self.mcastMembership=False
		self.mode="idle"
		self.loopDelay=0.125
		self.pLeft=0
		self.pRight=0
		self.okCount=0
		self._recipe="unknown-recipe"
		self._brewlog="unknown-brewlog"

		# Targets
		self.fermLow =-1
		self.fermHigh=-1
		self.fermTarget=-1
		# Targets for 
		self.hltLow=-1
		self.hltHigh=-1
		self.hltTarget=-1
		# Targets for
		self.mashLow=-1
		self.mashHigh=-1
		self.mashTarget=-1

		self.mashDuration=3600
		self.boilDuration=3600
		self.fermentationDuration=604800
		self.mashStart=0
		self.boilStart=0
		self.fermentationStart=0

		self.hltVol=0
		self.mashVol=0
		self.boilVol=0
		self.fermVol=0
		self.hltTargetVol=0
		self.mashTargetVol=0
		self.boilTargetVol=0
		self.fermTargetVol=0


		self.twitterApi=None
		try:
			import twitter
			from tweetAuth import tweetAuth
			self.twitterApi = tweetAuth().api	
		except:
			pass
		print "Have a twitter api of",self.twitterApi

		# Remove temporary flags
		for x in ['doshutdown','buttonhlt','buttonmash','buttonboil','buttonferm','buttonpump','manbuttonhlt','manbuttonmash','manbuttonboil','manbuttonferm','manbuttonpump']:
			try:
				os.unlink("ipc/%s" %(x))
			except:
				pass
	
		
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




	def sendOrders(self):
		controlMessage={}
		while 1:
			sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
			sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
			controlMessage['_operation'] = 'controller'
			controlMessage['_mode']=self.mode
			controlMessage['_checksum'] ="                                        "
			checksum = "%s%s" %(controlMessage,self.cfg.checksum)
			controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

			# hlt
			if self.mode.count('hlt'):
				controlMessage['hlt'] = (self.hltLow,self.hltHigh,self.hltTarget)
			# sparge
			if self.mode.count('sparge'):
				controlMessage['sparge']=(self.spargeLow,self.spargeHigh,self.spargeTarget)

			# mash or dought
			if self.mode.count('dough'):
				controlMessage['mash']=(self.strikeLow,self.strikeHigh,self.strikeTarget)
			elif self.mode.count('mash'):
				controlMessage['mash']=(self.mashLow,self.mashHigh,self.mashTarget)

			# fermentation
			if self.mode.count('ferm'):
				controlMessage['ferm']=(self.fermLow,self.fermHigh,self.fermTarget)
			if self.mode.count('cool'):
				controlMessage['ferm']=(self.fermLow,self.fermHigh,self.fermTarget)
				controlMessage['cool']=(self.fermLow,self.boilHigh,self.fermTarget)
			if self.mode.count('boil'):		
				controlMessage['boil']=(self.boilLow,self.boilHigh, self.boilTarget)
#			controlMessage['durations']=(self.mashDuration,self.mashStart,self.boilDuration,self.boilStart,self.fementationDuration,self.fermentationStart)


			controlMessage['_recipe']=self._recipe
			controlMessage['_brewlog']=self._brewlog	
			msg= json.dumps(controlMessage)
			msg= "%s%s" %(msg," "*(1200-len(msg))) 
			
			sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastPort))

			time.sleep(0.2)


			#
			# extended stats
			#
			controlMessage['volumes']={}
			controlMessage['volumes']['hlt']=[ self.hltVol,self.hltTargetVol]
			controlMessage['volumes']['mash']=[ self.mashVol,self.mashTargetVol]
			controlMessage['volumes']['ferm']=[ self.fermVol,self.fermTargetVol]
			controlMessage['volumes']['boil']=[ self.boilVol,self.boilTargetVol]
			msg= json.dumps(controlMessage)
			msg= "%s%s" %(msg," "*(1200-len(msg))) 
			
			sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastStatsPort))


			time.sleep(0.8)
	
		sendSocket.close()




	def error(self,msg1,msg2,msg3,msg4):
		self.lcdDisplay.sendMessage("%s%s" %(msg1," "*(20-len(msg1))),0)
		self.lcdDisplay.sendMessage("%s%s" %(msg2," "*(20-len(msg2))),1)
		self.lcdDisplay.sendMessage("%s%s" %(msg3," "*(20-len(msg3))),2)
		self.lcdDisplay.sendMessage("%s%s" %(msg4," "*(20-len(msg4))),3)
		self.ledFlasher.sendMessage('lSys','red')
		self.ledFlasher.sendMessage('lHlt','red')
		self.ledFlasher.sendMessage('lSparge','red')
		self.ledFlasher.sendMessage('lMash','red')
		self.ledFlasher.sendMessage('lBoil','red')
		self.ledFlasher.sendMessage('lFerm','red')

		while 1:
			self.checkShutdownRebootButtons()
			time.sleep(1)

	def rotaryUp(self):
		self.pLeft=self.pLeft+1
		time.sleep(0.05)
	def rotaryDown(self):
		self.pRight=self.pRight+1
		time.sleep(0.05)


	def startOrders(self):
		# set controller underway
		controlThread = threading.Thread(target=self.sendOrders)
		controlThread.daemon = True
		controlThread.start()
	

		

	def start(self):
		self.startedMonitoring=False
	
		# monitor the button
		lastButtonState=0
		self.busy=False

	
		self.lcdDisplay.sendMessage("     Please Wait   ",0)
		self.lcdDisplay.sendMessage("          0%       ",1)
		self.lcdDisplay.sendMessage("                   ",2)
		self.lcdDisplay.sendMessage("    Getting Ready  ",3)

		self.ledFlasher.sendMessage('lSys','flash')


		# functions we require to be active:
 		#  - monitor (i.e. the stats on the display)
		#  - temp probe A
		#  - temp probe B
		#  - grapher A
		#  - grapher B
		#  - SSR
		#  - buzzer 
		#  - led flasher 
		self._log(" waiting for monitor")
		# Listen for Monitor
		self.monitorSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.monitorSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.monitorSock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.monitorSock.bind(('', self.cfg.mcastMonitorPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.monitorSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		(data, addr) = self.monitorSock.recvfrom(1200)
		self.lcdDisplay.sendMessage("         12%       ",1)

		
		# Listen for Temperature Probe A
		self._log(" waiting for temperature - primary")
		self.probeaSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.probeaSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.probeaSock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.probeaSock.bind(('', self.cfg.mcastTemperaturePort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.probeaSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		(data, addr) = self.probeaSock.recvfrom(1200)
		self.lcdDisplay.sendMessage("         24%       ",1)

		
		time.sleep(1)
		self.lcdDisplay.sendMessage("         36%       ",1)


		self._log(" waiting for grapher")
		# Listen for Grapher
		self.graphSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.graphSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.graphSock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.graphSock.bind(('', self.cfg.mcastGrapherPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.graphSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		

		(data, addr) = self.graphSock.recvfrom(1200)
		self.lcdDisplay.sendMessage("         48%       ",1)




		self._log(" waiting for ssr relay controller")
		# Listen for Grapher
		self.ssrRelaySock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.ssrRelaySock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.ssrRelaySock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.ssrRelaySock.bind(('', self.cfg.mcastSsrRelayPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.ssrRelaySock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		

		(data, addr) = self.ssrRelaySock.recvfrom(1200)
		self.lcdDisplay.sendMessage("         60%       ",1)



		self._log(" waiting for relay controller")
		# Listen for Grapher
		self.relaySock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.relaySock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.relaySock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.relaySock.bind(('', self.cfg.mcastRelayPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.relaySock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		

		(data, addr) = self.relaySock.recvfrom(1200)


		self.lcdDisplay.sendMessage("         80%       ",1)



		self._log(" waiting for flasher")
		# Listen for Grapher
		self.flasherSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.flasherSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.flasherSock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.flasherSock.bind(('', self.cfg.mcastFlasherPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.flasherSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		

		(data, addr) = self.flasherSock.recvfrom(1200)
		self.lcdDisplay.sendMessage("         90%       ",1)


		self._log(" waiting for button")
		# Listen for Grapher
		self.buttonSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.buttonSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.buttonSock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.buttonSock.bind(('', self.cfg.mcastButtonPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.buttonSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		

		(data, addr) = self.buttonSock.recvfrom(1200)
		self.lcdDisplay.sendMessage("         95%       ",1)
		self.lcdDisplay.sendMessage("    Nearly There   ",3)



		self._log(" waiting for bidir")
		# Listen for Grapher
		self.bidirSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.bidirSock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.bidirSock.bind(('', self.cfg.mcastBidirPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.bidirSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

		

		(data, addr) = self.bidirSock.recvfrom(1200)

		# check that the slave is mounted to us
		o=open("ipc/handshake")
		handshake=o.readline()
		o.close()
		

		try:
			cm=json.loads(data)
			if not cm.has_key("_handshake"):
				cm['_handshake']="MISSING"
		except:
			cm['_handshake']="ERROR"

		
		if not handshake == cm['_handshake'] and not os.path.exists("simulator"):
			self._log("Handshake mismatch %s vs expected %s" %(cm['_handshake'],handshake))
			self.error('Error Loading',' master/slave',' not in sync','')
	

		# if any of the buttons are showing then we should tell the user to de-select activities first	
		activityStillActive=True
		msgShown=False
		while activityStillActive:
			activityStillActive=False
			self.ledFlasher.sendMessage('lSys','off')
			if os.path.exists("ipc/swHlt"):	
				activityStillActive=True
				self.ledFlasher.sendMessage('lHlt','red')
			else:
				self.ledFlasher.sendMessage('lHlt','off')

			if os.path.exists("ipc/swMash"):	
				activityStillActive=True
				self.ledFlasher.sendMessage('lMash','red')
			else:
				self.ledFlasher.sendMessage('lMash','off')
			if os.path.exists("ipc/swSparge"):	
				activityStillActive=True
				self.ledFlasher.sendMessage('lSparge','red')
			else:
				self.ledFlasher.sendMessage('lSparge','off')
	
			if os.path.exists("ipc/swBoil"):	
				activityStillActive=True
				self.ledFlasher.sendMessage('lBoil','red')
			else:
				self.ledFlasher.sendMessage('lBoil','off')

			if os.path.exists("ipc/swPump"):	
				activityStillActive=True
				self.ledFlasher.sendMessage('lPump','red')
			else:
				self.ledFlasher.sendMessage('lPump','off')
			if os.path.exists("ipc/swFerm"):	
				activityStillActive=True
				self.ledFlasher.sendMessage('lFerm','red')
			else:
				self.ledFlasher.sendMessage('lFerm','off')

			
			if activityStillActive and not msgShown:
				msgShown=True
				self.lcdDisplay.sendMessage("Error:             ",0)
				self.lcdDisplay.sendMessage("  De-select        ",1)
				self.lcdDisplay.sendMessage("  activities       ",2)
				self.lcdDisplay.sendMessage("  first            ",3)
				self.ledFlasher.sendMessage('lSys','red')

		self._log("Worsdell Brewing")


		self.lcdDisplay.sendMessage("                   ",0)
		self.lcdDisplay.sendMessage("      Worsdell     ",2)
		self.lcdDisplay.sendMessage("       Brewing     ",3)
		self.lcdDisplay.sendMessage("                   ",1)

		self.ledFlasher.sendMessage('lSys','off')
		self.ledFlasher.sendMessage('lHlt','off')
		self.ledFlasher.sendMessage('lSparge','off')
		self.ledFlasher.sendMessage('lBoil','off')
		self.ledFlasher.sendMessage('lMash','off')
		self.ledFlasher.sendMessage('lPump','off')
		self.ledFlasher.sendMessage('lFerm','off')

		
		self.startOrders()

		
		buttonState=False	
		while buttonState == False:
			if self.gpio.input('pOk'):	buttonState=True
			self.checkShutdownRebootButtons()
			time.sleep(0.3)

		self._log(" - ready for brewing")

		# Activate Rotary Encoder
		self.rotary = gpioRotary()
		self.rotary.clockwise = self.rotaryUp
		self.rotary.counterclockwise = self.rotaryDown
		brewlog=self.selectBrewlog()


		self.mainButtonLoop()




	def selectBrewlog(self,hash=None):

		if os.path.exists("ipc/manualbrewhash"):
			return open("ipc/manualbrewhash").read()[:-1]


		self.lcdDisplay.sendMessage("..............     ",0)
		self.lcdDisplay.sendMessage("                   ",1)
		self.lcdDisplay.sendMessage("                   ",2)
		self.lcdDisplay.sendMessage("                   ",3)


		# 
		# fetch data from brewerlsab database 
		#
		self._log(" - select brewlog fetching stats")
		try:
			recipes=json.loads(urllib2.urlopen("http://192.168.1.13:54660/metroui/pitmBrewloglist.py").read())
		except:
			self.error('Error:',' unable to fetch',' recipe stats','')


		self._log("Asking for which brewlog")
		self.lcdDisplay.sendMessage("Select Brew...     ",0)

		star=0
		indx=0
		brewSelected=None

		for r in recipes:
			if r['hash'] == hash:
				brewSelected=r
	
		while not brewSelected:
			if len(recipes) > indx:
				if star == 0:
					self.lcdDisplay.sendMessage("> %s %s" %(recipes[indx]['recipe'],recipes[indx]['brewlog']),1,interruptMessage="  %s" %(recipes[indx]['recipe']) )
				else:
					self.lcdDisplay.sendMessage("  %s" %(recipes[indx]['recipe']),1)
			else:
				self.lcdDisplay.sendMessage("                   ",1)

			if len(recipes) > indx+1:
				if star == 1:
					self.lcdDisplay.sendMessage("> %s %s" %(recipes[indx+1]['recipe'],recipes[indx+1]['brewlog']),2)
				else:
					self.lcdDisplay.sendMessage("  %s" %(recipes[indx+1]['recipe']),2)
			else:
				self.lcdDisplay.sendMessage("                   ",2)

			if len(recipes) > indx+2:
				if star == 2:
					self.lcdDisplay.sendMessage("> %s %s" %(recipes[indx+2]['recipe'],recipes[indx+2]['brewlog']),3)
				else:
					self.lcdDisplay.sendMessage("  %s" %(recipes[indx+2]['recipe']),3)
			else:
				self.lcdDisplay.sendMessage("                   ",3)


			changeBrewScreen=False
			lastButton=None
			while not changeBrewScreen:


				# with real raspberry pi we were changing on release of pOk
				# however that is harder to emulte in the simulator, so now we just go with pOk
				#if not self.gpio.input('pOk') and lastButton == 'pOk') (:
				if self.gpio.input('pOk'):
					if indx+star < len(recipes):
						changeBrewScreen=True
						brewSelected=recipes[indx+star]
#				if self.gpio.input('pOk'):
#					lastButton="pOk"
#				elif not os.path.exists("simulator"):
#					lastButton=None	


				if self.pLeft > 0:
					self.pLeft=0
					if star > 0:
						star=star-1
					elif star == 0 and indx > 0:
						indx=indx-1
					changeBrewScreen=True
				if self.pRight > 0:
					self.pRight=0
					if star < 2:
						star=star+2
					elif star == 2 and indx < len(recipes)-3:
						indx=indx+1

					changeBrewScreen=True

				self.checkShutdownRebootButtons()

				time.sleep(0.0025)



		if brewSelected:
			self.fermLow=brewSelected['fermLow']
			self.fermHigh=brewSelected['fermHigh']
			self.fermTarget=brewSelected['fermTarget']
			self.hltLow=brewSelected['hltLow']
			self.hltHigh=brewSelected['hltHigh']
			self.hltTarget=brewSelected['hltTarget']
			self.mashLow=brewSelected['mashLow']
			self.mashHigh=brewSelected['mashHigh']
			self.mashTarget=brewSelected['mashTarget']
			self.spargeLow=brewSelected['spargeLow']			
			self.spargeHigh=brewSelected['spargeHigh']
			self.spargeTarget=brewSelected['spargeTarget']
			self.strikeLow=brewSelected['strikeLow']
			self.strikeHigh=brewSelected['strikeHigh']
			self.strikeTarget=brewSelected['strikeTarget']

			self.hltTargetVol=float(brewSelected['mash_water'])+6
			self.spargeTargetVol=float(brewSelected['sparge_water'])+6
			self.mashTargetVol=float(brewSelected['mash_water'])
			self.boilTargetVol=float(brewSelected['boil_vol'])
			self.fermTargetVol=float(brewSelected['precoolfvvolume'])

			self.boilLow=85
			self.boilHigh=87
			self.boilTarget=95
			self._recipe=brewSelected['recipe']
			self._brewlog=brewSelected['brewlog']
			self._log(" Recipe: %s Brewlog: %s" %(self._recipe,self._brewlog))
			self.lcdDisplay.sendMessage( self._recipe , 0)
			self.lcdDisplay.sendMessage(" %s" %( self._brewlog),1)
			self.lcdDisplay.sendMessage("        ----",2)
			if not os.path.exists("ipc/tweeted-brewstart"):
				flag=open("ipc/tweeted-brewstart","w")
				flag.close()
				try:
					self.twitterApi.PostUpdate('Started a brewday %s #brewerslab #%s' %(self._recipe,re.compile("[^A-Za-z0-9]").sub('',self._recipe) ))
				except:
					pass	
		else:	
			self._log("Inconsistent state - we don't have brew details")



	def updateResults(self,result,zone="A"):
		# NOt sure this is really used anywhere
		for probe in result:
			if zone == "A":
				if result[probe]['valid'] :
					if  not result[probe]['timestamp'] <= self.zoneAtempTimestamp:
					#	self._log("probe,%s,temp%s,,using temperature result - %s seconds old" %(probe,result[probe]['temperature'], time.time()-result[probe]['timestamp']))
						self.zoneAtempTimestamp = result[probe]['timestamp']
						self.zoneAtemp = result[probe]['temperature'] 
#				else:
#					self._log("probe,%s,temp,N/A,invalid result,%s" %(probe,result[probe]['temperature']))
				self.zoneAprobe=probe
			if zone == "B":
				if result[probe]['valid'] :
					if not result[probe]['timestamp'] <= self.zoneBtempTimestamp:
						#self._log("probe,%s,temp%s,,using temperature result - %s seconds old" %(probe,result[probe]['temperature'], time.time()-result[probe]['timestamp']))
						self.zoneBtempTimestamp = result[probe]['timestamp']
						self.zoneBtemp= result[probe]['temperature'] 
#				else:
#					self._log("probe,%s,temp,N/A,invalid result,%s" %(probe,result[probe]['temperature']))
				self.zoneBprobe=probe






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
			if cm['_mode'].count( "hlt"):
				self.doMonitoring=True

			if cm['_mode'].count("mash"):
				self.doMonitoring=True

			if cm['_mode'].count("boil"):
				self.doMonitoring=True
			
			if cm['_mode'].count("ferm"):
				self.doMonitoring=True


		if cm.has_key("currentResult"):
			if self.doMonitoring:
				self.updateResults( cm['currentResult'] ,zone)

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
			self.decodeMessage(data,zone="A")	
			time.sleep(0.5)		

			

	def mainButtonLoop(self):	

		self._log("In main button loop")

		# Set initial flags
		self.pump=False
		self.extractor=False
		self.hltpower=False
		self.boilpower=False
		self.fermheat=False
		self.fermfridge=False
		self.turnOffExtractorAfter=0	

		self.zoneAtempTimestamp=0
		self.zoneBtempTimestamp=0
		self.zoneAtemp=0
		self.zoneBtemp=0
		self.zoneAprobe=""
		self.zoneBprobe=""

		self.fermTimeUnder=0
		self.fermHeatActive=0
		self.fermCoolActive=0
		self.fermTimeOver=0

		# Set  Temperature Thread
		updateStatsThread = threading.Thread(target=self.updateStatsZoneA)
		updateStatsThread.daemon = True
		updateStatsThread.start()

		self.lastMode=""	

		self.showActivityOrTime=0

		# main button loop
		self.lcdDisplay.sendMessage("  Select Activity",3)


		self.pLeft=False
		self.pRight=False
		#  - buttons active lo
		while True:

			self.adjustVolumes()

			for dummy  in range(10):
				self.adjustTargets()
				time.sleep(0.2)

			if self.extractor:
				extractor=self.extractor
			elif self.turnOffExtractorAfter > 0:
				extractor=self.turnOffExtractorAfter
			else:
				extractor=False
			self._log("mode, %s pwrhlt, %s pwrboil, %s, extractor, %s, pump, %s, fermheat, %s, fermfridge, %s " %(self.mode, self.hltpower, self.boilpower, extractor, self.pump,self.fermheat,self.fermfridge),importance=8)


			#
			# Toggling the modes
			if os.path.exists("ipc/swHlt") or os.path.exists("ipc/manual_swHlt"):
				self.boilpower=False
				self.pump=False
				self.extractor=False
				# we are heating the HLT, this will be for mash water

				hltDelay=True
				if os.path.exists("ipc/hlt-delay-until"):
					hltDelayTime=int(open("ipc/hlt-delay-until").read())
					
					self._log("HLT Delayed until %s" %(time.ctime(hltDelayTime)))
					if time.time() > hltDelayTime:
						self._log("HLT Delayed has cleared")
						try:
							os.unlink("ipc/hlt-delay-until")	
						except:
							pass
				else:
					hltDelay=False

				if hltDelay:
					self.lcdDisplay.sendMessage(" HLT Delay ",3)
	
				if not hltDelay:
					self.htlpower=True
					self.mode="hlt"	

					self.lcdDisplay.sendMessage(" Heat Mash Water",3)


				time.sleep(1)

			
			elif (os.path.exists("ipc/swMash") or os.path.exists("ipc/manual_swMash")) and  os.path.exists("ipc/mash_toggle_type-dough"):
				self.pump=False
				self.extractor=False
				self.hltpower=False
				self.boilpower=False
				self.mode="mash/dough"
				self.lcdDisplay.sendMessage(" Mash / Dough In Grain",3)	
	
			elif (os.path.exists("ipc/swMash") or os.path.exists("ipc/manual_swFerm")) and not os.path.exists("ipc/mash_toggle_type-dough"):
				#we could just be doing a mash
				# but not doughing in the grain
				self.pump=False
				self.extractor=False
				self.hltpower=False
				self.boilpower=False
				self.mode="mash"
			
				if self.mashStart == 0:
					self.mashStart=time.time()	

				# or we could also be heating the sparge water
				if os.path.exists("ipc/swSparge"):
					self.mode="hlt/sparge/mash"
					self.hltpower=True				
					if self.showActivityOrTime > 3:
						MINUTES="%02d" %( self.mashDuration  /60)
						SECONDS="%02d" %( self.mashDuration -(int(MINUTES)*60))
						duration="%sm%ss" %(MINUTES,SECONDS)
						MINUTES="%02d" %( (time.time()-self.mashStart  )/60)
						SECONDS="%02d" %( (time.time()-self.mashStart ) -(int(MINUTES)*60))
						elapsed="%sm%ss" %(MINUTES,SECONDS)
					
						self.lcdDisplay.sendMessage(" Mash %s/%s" %(elapsed,duration),3)
					else:
						self.lcdDisplay.sendMessage(" Mash / Heat Sparge",3)
				else:
	
					self.mode="mash"	
					if self.showActivityOrTime > 3:
						print "tweet bot",self._mode
						if (self.time()-self.mashStart) > self.mashDuration - 300 and not os.path.exists("ipc/tweeted-mash-nearly-finished"):
							
							flag=open("ipc/tweeted-mash-nearly-finished","w")
							flag.close()
							try:
								self.twitterApi.PostUpdate('%s mash out and sparge #brewerslab' %(self.cfg.tweetProgress))
							except:
								pass	
						MINUTES="%02d" %( self.mashDuration  /60)
						SECONDS="%02d" %( self.mashDuration -(int(MINUTES)*60))
						duration="%sm%ss" %(MINUTES,SECONDS)
						MINUTES="%02d" %( (time.time()-self.mashStart  )/60)
						SECONDS="%02d" %( (time.time()-self.mashStart ) -(int(MINUTES)*60))
						elapsed="%sm%ss" %(MINUTES,SECONDS)
					
						self.lcdDisplay.sendMessage(" Mash %s/%s" %(elapsed,duration),3)
					else:
						self.lcdDisplay.sendMessage(" Mash The Grain",3)

				time.sleep(1)


			# or we could also be heating the sparge wate onlyr
			elif os.path.exists("ipc/swSparge"):
				self.mode="hlt/sparge"

				self.hltpower=True				
				self.lcdDisplay.sendMessage(" Heat Sparge Water",3)

				time.sleep(1)


			elif os.path.exists("ipc/swBoil"):			

				if self.boilStart == 0 and not os.path.exists("ipc/boil_getting-ready"):
					self.boilStart=time.time()

				# we then move onto boil only
				self.hltpower=False
				self.boilpower=True
				self.mode="boil"


				if os.path.exists("ipc/swPump"): 
					self.mode="boil/pump" 
					self.lcdDisplay.sendMessage(" Boil/Pump Wort",3)
				else:
					if os.path.exists("ipc/boil_getting-ready"):
						self.lcdDisplay.sendMessage(" Bringing to Boil",3)
					else:
						if self.showActivityOrTime > 3:


							print "tweet bot",self._mode
							if (self.time()-self.boilStart) > self.boilDuration - 300 and not os.path.exists("ipc/tweeted-boil-nearly-finished"):

								flag=open("ipc/tweeted-boil-nearly-finished","w")
								flag.close()
								try:
									self.twitterApi.PostUpdate('%s boil finished #brewerslab' %(self.cfg.tweetProgress))
								except:
									pass	

							MINUTES="%02d" %( self.boilDuration  /60)
							SECONDS="%02d" %( self.boilDuration -(int(MINUTES)*60))
							duration="%sm%ss" %(MINUTES,SECONDS)
							MINUTES="%02d" %( (time.time()-self.boilStart  )/60)
							SECONDS="%02d" %( (time.time()-self.boilStart ) -(int(MINUTES)*60))
							elapsed="%sm%ss" %(MINUTES,SECONDS)
						
							self.lcdDisplay.sendMessage(" Boil %s/%s" %(elapsed,duration),3)
						else:
							self.lcdDisplay.sendMessage(" Boiling The Wort",3)
				self.extractor=True
				
				if os.path.exists("ipc/buttonpump"):
					self.pump=True
				else:
					self.pump=False
					self.turnOffExtractorAfter = time.time() + 18


				time.sleep(1)
		
			elif os.path.exists("ipc/swPump") and os.path.exists("ipc/swFerm"):  
				self.mode="pump" 
				self.lcdDisplay.sendMessage(" Transfer the wort",3)

			elif os.path.exists("ipc/swPump"): 
				self.mode="pump/cool" 
				self.lcdDisplay.sendMessage(" Cool The Wort",3)


			elif os.path.exists("ipc/swFerm") and os.path.exists("ipc/ferm-notstarted"):
				self.mode="ferm-wait"
				self.lcdDisplay.sendMessage(" Pitch the Yeast",3)

			elif os.path.exists("ipc/swFerm"):
				self.mode="ferm"
				if self.showActivityOrTime > 3:

					DAYS=int("%01d" %( (time.time()-self.fermentationStart  )/60/60/24))
					x=time.time()-self.fermentationStart-(DAYS*60*60*24)
					HOURS="%02d" %( x /60/60)
					x=x-(int(HOURS)*60*60)
					MINUTES="%02d" %( x/60)
				
					self.lcdDisplay.sendMessage(" Ferment %sd%sh%s," %(DAYS,HOURS,MINUTES),3)
				else:
					self.lcdDisplay.sendMessage(" Fermentation",3)
	
				if self.fermentationStart == 0:
					self.fermentationStart = time.time()

				

			else:


				if self._mode == "idle":
					self.lcdDisplay.sendMessage( self._recipe , 0)
					self.lcdDisplay.sendMessage(" %s" %( self._brewlog),1)
					self.lcdDisplay.sendMessage("        ----",2)
					self.lcdDisplay.sendMessage("  Select Activity",3)


				self.mode="idle"
				self.hltpower=False
				self.boilpower=False
				self.pump=False
		
			self.lastMode=self.mode

			self.checkShutdownRebootButtons()

			self.showActivityOrTime=self.showActivityOrTime + 1
			if self.showActivityOrTime > 8:
				self.showActivityOrTime=0
#			time.sleep(0.5)



	def checkShutdownRebootButtons(self):
			# Shutdown required
			if os.path.exists("ipc/doshutdown") or ( self.pLeft > 15 and self.okCount >15):
				self.doShutdown()
			# Reboot  required
			if os.path.exists("ipc/doreboot") or ( self.okCount > 15 and self.pRight > 15):
				self.doShutdown(reboot=True)
			
			pOk=self.gpio.input('pOk')
			pLeft=self.gpio.input('pLeft')
			pRight=self.gpio.input('pRight')	

			if pOk and pLeft:
				self.pLeft=self.pLeft+1
				self.okCount=self.okCount+1
				print "OK",self.pRight,"UP",self.pLeft
			elif pOk and pRight:
				self.okCount=self.okCount+1
				self.pRight=self.pRight+1
				print "OK",self.pRight,"UP",self.pLeft
			elif pRight:
				self.pRight=self.pRight+1
				print "DOWN",self.pRight,"up",self.pLeft
			elif pLeft:
				self.pLeft=self.pLeft+1
				print "down",self.pRight,"UP",self.pLeft
			elif pOk:
				self.okCount=self.okCount+1
				print "OK",self.okCount


			if not pRight:
				self.pRight=0
			if not pLeft:
				self.pLeft=0
			if not pOk:
				self.okCount=0
			if pOk:
				return True	


	def doShutdown(self,reboot=False):

		for ipcFlag in os.listdir("ipc"):
			try:
				os.unlink("ipc/%s" %(ipcFlag))
			except:
				pass



		if reboot:
			self._log("Reboot Required")
			self.lcdDisplay.sendMessage("Rebooting          ",0,importance=9)
		else:
			self._log("Shutdown Required")
			self.lcdDisplay.sendMessage("Shutting Down      ",0,importance=9)
		self.lcdDisplay.sendMessage("                   ",2,importance=9)
		self.lcdDisplay.sendMessage("                   ",3,importance=9)


		# now start to shutdown the slave
		self.lcdDisplay.sendMessage("       80%         ",1,importance=9)
		if reboot:
			os.system("ssh 192.168.1.15 sh /home/beer/brewerslab/slave/stop.sh reboot")
		else:
			os.system("ssh 192.168.1.15 sh /home/beer/brewerslab/slave/stop.sh poweroff")
	
		# now wait for pings to finish
		self.lcdDisplay.sendMessage("       85%         ",1,importance=9)
		x=0
		while int(x) < 1:
			x=os.system("ping 192.168.1.15 -w 3 -c 1")

		# now wait for 15 seconds 
		self.lcdDisplay.sendMessage("       90%         ",1,importance=9)
		time.sleep(15)
		os.system("sync")


		# now shutdwon ourself
		self.lcdDisplay.sendMessage("       98%         ",1,importance=9)
		if reboot:
			os.system("sh /home/pi/brewerslab/master/stop.sh reboot")
		else:
			os.system("sh /home/pi/brewerslab/master/stop.sh poweroff")
		time.sleep(2)
		self.lcdDisplay.sendMessage("       99%         ",1,importance=9)



	def adjustVolumes(self):
		"""
		This is currently a placeholder for the simulator, but in the future perhap flow meters could
		get us somewhere close
		"""

		if os.path.exists("ipc/fermFillVol"):
			self.fermVol = self.fermTargetVol
			try:
				os.unlink("ipc/fermFillVol")
			except:
				pass
		if os.path.exists("ipc/fermEmptyVol"):
			self.fermVol = 0
			try:
				os.unlink("ipc/fermEmptyVol")
			except:
				pass
		if os.path.exists("ipc/mashFillVol"):
			self.mashVol = self.mashTargetVol
			try:
				os.unlink("ipc/mashFillVol")
			except:
				pass
		if os.path.exists("ipc/mashEmptyVol"):
			self.mashVol = 0
			try:
				os.unlink("ipc/mashEmptyVol")
			except:
				pass
		if os.path.exists("ipc/boilFillVol"):
			self.boilVol = self.boilTargetVol
			try:
				os.unlink("ipc/boilFillVol")
			except:
				pass
		if os.path.exists("ipc/boilEmptyVol"):
			self.boilVol = 0
			try:
				os.unlink("ipc/boilEmptyVol")
			except:
				pass
		if os.path.exists("ipc/hltFillVol") and os.path.exists("ipc/mash_toggle_type-dough"):
			self.hltVol = self.hltTargetVol
			try:
				os.unlink("ipc/hltFillVol")
			except:
				pass
		if os.path.exists("ipc/hltEmptyVol") and os.path.exists("ipc/mash_toggle_type-dough"):
			self.hltVol = 0
			try:
				os.unlink("ipc/hltEmptyVol")
			except:
				pass
		if os.path.exists("ipc/hltFillVol") and not os.path.exists("ipc/mash_toggle_type-dough"):
			self.hltVol = self.spargeTargetVol
			try:
				os.unlink("ipc/hltFillVol")
			except:
				pass
		if os.path.exists("ipc/hltEmptyVol") and not os.path.exists("ipc/mash_toggle_type-dough"):
			self.hltVol = 0
			try:
				os.unlink("ipc/hltEmptyVol")
			except:
				pass



	def adjustTargets(self):
		if os.path.exists("ipc/adjustFermTarget"):
			newTarget="?"
			try:
				newTarget=float(re.compile("^\s*([0-9\.]*)\s*$").sub('\g<1>',open("ipc/adjustFermTarget").read()))
				self.fermLow = newTarget - 0.3
				self.fermHigh = newTarget + 0.3
				self.fermTarget=newTarget
				self._log("Adjusting Fermentation Target to %s" %(newTarget))
				os.unlink("ipc/adjustFermTarget")
				self.lcdDisplay.sendMessage(" Target = %s" %(self.fermTarget),2)
			except:
				self._log("Adjust Target invalid %s - ignoring" %(newTarget))
				try:
					os.unlink("ipc/adjustFermTarget")
				except:
					pass

		if os.path.exists("ipc/adjustSpargeTarget"):
			newTarget="?"
			try:
				newTarget=float(re.compile("^\s*([0-9\.]*)\s*$").sub('\g<1>',open("ipc/adjustSpargeTarget").read()))
				self.spargeLow = newTarget - 0.3
				self.spargeHigh = newTarget + 0.3
				self.spargeTarget=newTarget
				self._log("Adjusting Sparge Target to %s" %(newTarget))
				os.unlink("ipc/adjustSpargeTarget")
				self.lcdDisplay.sendMessage(" Target = %s" %(self.spargeTarget),2)
			except:
				self._log("Adjust Target invalid %s - ignoring" %(newTarget))
				try:
					os.unlink("ipc/adjustSpargeTarget")
				except:
					pass

		if os.path.exists("ipc/adjustHltTarget"):
			newTarget="?"
			try:
				newTarget=float(re.compile("^\s*([0-9\.]*)\s*$").sub('\g<1>',open("ipc/adjustHltTarget").read()))
				self.hltLow = newTarget - 0.3
				self.hltHigh = newTarget + 0.3
				self.hltTarget=newTarget
				self._log("Adjusting HLT Target to %s" %(newTarget))
				os.unlink("ipc/adjustHltTarget")
				self.lcdDisplay.sendMessage(" Target = %s" %(self.hltTarget),2)
			except:
				self._log("Adjust Target invalid %s - ignoring" %(newTarget))
				try:
					os.unlink("ipc/adjustHltTarget")
				except:
					pass

		if os.path.exists("ipc/adjustBoilTarget"):
			newTarget="?"
			try:
				newTarget=float(re.compile("^\s*([0-9\.]*)\s*$").sub('\g<1>',open("ipc/adjustBoilTarget").read()))
				self.boilLow = newTarget - 0.3
				self.boilHigh = newTarget + 0.3
				self.boilTarget=newTarget
				self._log("Adjusting Boil Target to %s" %(newTarget))
				os.unlink("ipc/adjustBoilTarget")
				self.lcdDisplay.sendMessage(" Target = %s" %(self.boilTarget),2)
			except:
				self._log("Adjust Target invalid %s - ignoring" %(newTarget))
				try:
					os.unlink("ipc/adjustBoilTarget")
				except:
					pass

		if not self.gpio.input('pLeft') and self.pLeft:
			self.pLeft=False			
			if self.mode.count("ferm"):
				self.fermLow=self.fermLow -0.2
				self.fermHigh=self.fermHigh-0.2
				self.fermTarget=self.fermTarget-0.2
				self.lcdDisplay.sendMessage(" Target = %s" %(self.fermTarget),2)
				self._log("Reduced Ferm Temperature Aim by 0.2 %s" %(self.fermTarget))
			elif self.mode.count("sparge"):
				self.spargeLow=self.spargeLow -0.2
				self.spargeHigh=self.spargeHigh-0.2
				self.spargeTarget=self.spargeTarget-0.2
				self.lcdDisplay.sendMessage(" Target = %s" %(self.spargeTarget),2)
				self._log("Reduced Sparge Temperature Aim by 0.2 %s" %(self.spargeTarget))
			elif self.mode.count("hlt"):
				self.hltLow=self.hltLow -0.2
				self.hltHigh=self.hltHigh-0.2
				self.hltTarget=self.hltTarget-0.2
				self.lcdDisplay.sendMessage(" Target = %s" %(self.hltTarget),2)
				self._log("Reduced HLT Temperature Aim by 0.2 %s" %(self.fermTarget))
			elif self.mode.count("boil"):
				self.boilLow=self.boilLow -0.2
				self.boilHigh=self.boilHigh-0.2
				self.boilTarget=self.boilTarget-0.2
				self.lcdDisplay.sendMessage(" Target = %s" %(self.boilTarget),2)
				self._log("Reduced Boil Temperature Aim by 0.2 %s" %(self.boilTarget))

			if self.mode.count("ferm-wait"):
				try:
					os.remove("ipc/ferm-notstarted")
					self._log("Removed Ferm Not Started Flag")
				except:
					pass

			if self.mode.count("dough"):
				try:
					os.remove("ipc/mash_toggle_type-dough")
					self._log("Removed Mash/Dough Toggle")
				except:
					pass
					
			if self.mode.count("boil"):
				try:
					os.remove("ipc/boil_getting-ready")
					self._log("Removed Boil Getting Ready Flag")
				except:
					pass

		if not self.gpio.input('pRight') and self.pRight:
			self.pRight=False
			if self.mode.count("ferm"):
				self.fermLow=self.fermLow +0.2
				self.fermHigh=self.fermHigh+0.2
				self.fermTarget=self.fermTarget+0.2
				self._log("Increased Boil Temperature Aim by 0.2 %s" %(self.fermTarget))
				self.lcdDisplay.sendMessage(" Target = %s" %(self.fermTarget),2)
			elif self.mode.count("sparge"):
				self.spargeLow=self.spargeLow +0.2
				self.spargeHigh=self.spargeHigh+0.2
				self.spargeTarget=self.spargeTarget+0.2
				self._log("Increased Sparge Temperature Aim by 0.2 %s" %(self.spargeTarget))
			elif self.mode.count("hlt"):
				self.hltLow=self.hltLow +0.2
				self.hltHigh=self.hltHigh+0.2
				self.hltTarget=self.hltTarget+0.2
				self.lcdDisplay.sendMessage(" Target = %s" %(self.hltTarget),2)
				self._log("Increased HLT Temperature Aim by 0.2 %s" %(self.hltTarget))
			elif self.mode.count("boil"):
				self.boilLow=self.boilLow +0.2
				self.boilHigh=self.boilHigh+0.2
				self.boilTarget=self.boilTarget+0.2
				self.lcdDisplay.sendMessage(" Target = %s" %(self.boilTarget),2)
				self._log("Increased Boil Temperature Aim by 0.2 %s" %(self.boilTarget))


			if self.mode.count("ferm-wait"):
				try:
					os.remove("ipc/ferm-notstarted")
					self._log("Removed Ferm Not Started Flag")
				except:
					pass


			if self.mode.count("boil"):
				try:
					os.remove("ipc/boil_getting-ready")
					self._log("Removed Boil Getting Ready Flag")
				except:
					pass
			if self.mode.count("dough"):
				try:
					os.remove("ipc/mash_toggle_type-dough")
					self._log("Removed Mash/Dough Toggle")
				except:
					pass

		if self.gpio.input('pLeft') and not self.pLeft:
			self.pLeft=True
		if self.gpio.input('pRight') and not self.pRight:
			self.pRight=True


if __name__ == '__main__':

	try:
		controller = pitmController()
		controller.start()
	except KeyboardInterrupt:
		controller.uncontrol()



