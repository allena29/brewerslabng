#!/usr/bin/python

# piTempMonitor Grapher
import json
import re
import os
import hashlib
import struct
import socket
import syslog
import sys
import threading
import time
import rrdtool

from pitmCfg import pitmCfg





class pitmGrapher:


	def __init__(self):
		self.logging=2		# 1 = syslog, 2 = stderr
		self.cfg = pitmCfg()
#		self.lcdDisplay = pitmLCDisplay()
		(self.tempLow,self.tempHigh,self.tempTarget)=(20,20,20)

		self.mcastMembership=False
		self._brewlog="unknownbrewlog"
		self._recipe="unknownrecipe"
		
		self.initTime=int(time.time()-int(open("/proc/uptime").read().split(".")[0]))

		self.probesToMonitor = { self.cfg.fermProbe : False }
		self.doMonitoring=False
		self.startedMonitoring=False
		self.graphName=None

		self.lastActivity=None
		self.probes={}
		self.rrdData=[]
	
#	def __del__(self):
#		if self.mcastMembership:
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






	def submission(self):
		if not os.path.exists("/tmp/standalone-temp-active"):
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
					

	def broadcastResult(self):

		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage={}
		controlMessage['_operation'] = 'grapher'
		controlMessage['_checksum'] ="                                        "

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 
		while 1:
			sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastGrapherPort))
			time.sleep(1)


	def decodeTempMessage(self,data):
		"""
		"""

		try:
			cm = json.loads( data )
		except:
			self._log("Error unpickling input message\n%s" %(data))
			return

##		print "--- cm START ---"
#		print len(data)
#		print cm
#		print "--- cm END ---"
		checksum = cm['_checksum']
		cm['_checksum'] ="                                        "
		ourChecksum = hashlib.sha1("%s%s" %(cm,self.cfg.checksum)).hexdigest()
		
		if cm.has_key("_recipe"):
			self._recipe=re.compile("[^A-Za-z0-9]").sub('', cm['_recipe'])
		if cm.has_key("_brewlog"):
			self._brewlog=re.compile("[^A-Za-z0-9]").sub('', cm['_brewlog'])

		if cm.has_key("_mode"):
			if os.path.exists("/tmp/standalone-temp-active"):
				self.doMonitoring=True
				self.lastActivity="ferm"
				self.probesToMonitor[ self.cfg.fermProbe]= True 
	
			elif cm['_mode'].count("ferm"):
				self.doMonitoring=True
				self.lastActivity="ferm"
				if cm.has_key("tempTarget"):
					(self.tempLow,self.tempHigh,self.tempTarget)=cm['tempTarget']

				self.probesToMonitor[ self.cfg.fermProbe]= True 
	
			else:
				self.probesToMonitor[ self.cfg.fermProbe ] = False
				(self.tempLow,self.tempHigh,self.tempTarget)=(20,20,20)
				self.lastActivity="no-graph"
				self.doMonitoring=False
		
		if cm.has_key("doMonitoring"):
			self.doMonitoring=cm['doMonitoring']
		if cm.has_key("currentResult"):
			if self.doMonitoring:	self.doGraphData( cm['currentResult'] )
		if cm.has_key("flushResults"):
			self._log("flush results received")
			self.saveGraph()

	def decodeMessage(self,data):
		"""
		"""

		try:
			cm = json.loads( data )
		except:
			self._log("Error unpickling input message\n%s" %(data))
			return

##		print "--- cm START ---"
#		print len(data)
#		print cm
#		print "--- cm END ---"
		checksum = cm['_checksum']
		cm['_checksum'] ="                                        "
		ourChecksum = hashlib.sha1("%s%s" %(cm,self.cfg.checksum)).hexdigest()
		
		if cm.has_key("_recipe"):
			self._recipe=re.compile("[^A-Za-z0-9]").sub('', cm['_recipe'])
		if cm.has_key("_brewlog"):
			self._brewlog=re.compile("[^A-Za-z0-9]").sub('', cm['_brewlog'])

		if cm.has_key("_mode"):
			if cm['_mode'].count("ferm"):
				self.doMonitoring=True
				self.lastActivity="ferm"
				if cm.has_key("tempTarget"):
					(self.tempLow,self.tempHigh,self.tempTarget)=cm['tempTarget']

				self.probesToMonitor[ self.cfg.fermProbe]= True 
	
			else:
				self.probesToMonitor[ self.cfg.fermProbe ] = False
				(self.tempLow,self.tempHigh,self.tempTarget)=(20,20,20)
				self.lastActivity="no-graph"
				self.doMonitoring=False
		
		if cm.has_key("doMonitoring"):
			self.doMonitoring=cm['doMonitoring']
		if cm.has_key("currentResult"):
			if self.doMonitoring:	self.doGraphData( cm['currentResult'] )
		if cm.has_key("flushResults"):
			self._log("flush results received")
			self.saveGraph()

	
	def doGraphData(self,result):
#		print result

		rrdData=""

		stamp=4
		for probe in result:
			if not self.probesToMonitor.has_key(probe):
				print "Probe %s not ok to monitor" %(probe)
			elif self.probesToMonitor[probe]:
				if result[probe]['valid']:
#					if not self.cfg.probes[probe]['activity'] == self.lastActivity:
#						self.probes={}
	#					self.lastActivity= self.cfg.probes[probe]['activity']
					if not self.probes.has_key(probe):
						self.probes[probe]=[]

					self.probes[probe].append( result[probe]['temperature'] )
					rrdData="%s%s:" %(rrdData, result[probe]['temperature'])


	#				print "recorded ",probe,result[probe]['temperature']				

					stamp=result[probe]['timestamp']


		if not stamp == 4:
			for c in range(3-rrdData.count(":")):
				rrdData="%s0:" %(rrdData)
			rrdData="%s:%s%s:%s:%s" %(int(stamp),rrdData, self.tempLow, self.tempHigh, self.tempHigh+10)

			print rrdData
			self.rrdData.append(rrdData)
			
	

	def start(self):
		self._log("Starting pitmGrapher")


		self.keepThreadLaunched=False
		self.recycleThreadLaunched=False

		while True:
			if self.doMonitoring == True and self.startedMonitoring == False and self.lastActivity:
				self.startedMonitoring = True
				print "calling createGraph()"
				self.createGraph()

				if not self.recycleThreadLaunched:
					recycleResult = threading.Thread(target=self.recycleThread)
					recycleResult.daemon = True
					recycleResult.start()
					self.recycleThreadLaunched=True

				self.startMonitoring()

				if not self.keepThreadLaunched:
					keepResult = threading.Thread(target=self.keepThread)
					keepResult.daemon = True
					keepResult.start()
					self.keepThreadLaunched=True

			elif self.doMonitoring == False and self.startedMonitoring == True:
				self.startedMonitoring = False
				self.saveGraph()
				self.keepGraph()
			time.sleep(1)



	def createGraph(self):
#		self.lcdDisplay.sendMessage("Creating Graph",1)
		graphName= '/currentdata/%s_%s_%s_%s.rrd' %(self.lastActivity,self._recipe,self._brewlog,self.initTime)
		graphName  = graphName.decode('utf8').encode('ascii')
		self.graphName=graphName
		if not os.path.exists("/currentdata/%s_%s_%s_%s.rrd" %(self.lastActivity,self._recipe,self._brewlog,self.initTime)):
			print "Creating Graph"
			print "need to create a graph .rrd %s" %(self.lastActivity)

			data_sources=[ 'DS:temp1:GAUGE:60:-10:200', 
					'DS:temp2:GAUGE:60:-10:200',
					'DS:temp3:GAUGE:60:-10:200',
					'DS:temp4:GAUGE:60:-10:200',
					'DS:temp5:GAUGE:60:-10:200',
					'DS:temp6:GAUGE:60:-10:200']
		
			rrdStartTimestamp=int(time.time())	
			print graphName
			rrdtool.create( graphName,'--step','10',
					 '--start', '%s' %( rrdStartTimestamp-2 ),
					 data_sources,
					 'RRA:AVERAGE:0.5:1:129600')

			#129600 = 15 days at 10 seconds intervals (i.e. 86400*15/10)
		else:
			print "/currentdata/%s_%s_%s_%s.rrd" %(self.lastActivity,self._recipe,self._brewlog,self.initTime),
			print  os.path.exists("/currentdata/%s_%s_%s_%s.rrd" %(self.lastActivity,self._recipe,self._brewlog,self.initTime))
			print "Not createing a graph as we already have it"	

		

	def saveGraphThread(self):
		while True:
			if len(self.rrdData):
				print "save graph on thread (every 5 minutes)"
				self.saveGraph()
				
			time.sleep(300)


	def saveGraph(self):
		print "need to save graph %s" %(self.graphName)
		print self.rrdData
		try:
			if not self.graphName:
				print "No graphname oops..."
			else:
				print "Saving graph ",self.graphName
				rrdtool.update( self.graphName,self.rrdData )
		except ImportError:			## error for update frequency
			self._log("could not update data into rrd")
		self.rrdData=[]


	def keepGraph(self,keep=None):
		if not keep:
			keep=self.initTime
		print "need to archive graph so we will take currentdata and save as archivedata"
		O=open("/archivedata/%s_%s_%s_%s.rrd" %(self.lastActivity,self._recipe,self._brewlog,keep),"w")
		o=open("/currentdata/%s_%s_%s_%s.rrd" %(self.lastActivity,self._recipe,self._brewlog,keep))
		O.write(o.read())
		O.close()
		o.close()

	def startMonitoring(self):
		print "start monitoring"
	

	def keepThread(self):
		self._log("Starting Keep Thread")
		while True:
			time.sleep(70)
			self.keepGraph()
				
	def recycleThread(self):
		self._log("Starting Recycle Thread")
		while True:
			keep=self.initTime
	
			for c in range(15):
				for h in range(24):
					self._log("waiting for hour %s  %s of 15 days before recycling" %(h+1,c+1))
					time.sleep(3600)
			self._log("saving  graph before recycle and creating a new graph")
			self.saveGraph()	
			self._log("creating new graph")
			self.createGraph()
			self._log("now %s was %s" %(self.initTime,keep))
			self.keepGraph(keep)
			
	def dataThread(self):
		self._log("Starting Data Capture Thread")
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastTemperaturePort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True

		while True:
			(data, addr) = self.sock.recvfrom(1200)
			self.decodeTempMessage(data)	
			time.sleep(0.1)		

if __name__ == '__main__':

	try:
		controller = pitmGrapher()
#		print os.getcwd()

		# get under the control of the flasher
		broadcastResult = threading.Thread(target=controller.broadcastResult)
		broadcastResult.daemon = True
		broadcastResult.start()

		# do our graphs bits
		controlThread = threading.Thread(target=controller.submission)
		controlThread.daemon = True
		controlThread.start()

		dataThread = threading.Thread(target=controller.dataThread)
		dataThread.daemon = True
		dataThread.start()

		graphThread = threading.Thread(target=controller.saveGraphThread)
		graphThread.daemon = True
		graphThread.start()
		
		controller.start()
	except KeyboardInterrupt:
		controller.uncontrol()



