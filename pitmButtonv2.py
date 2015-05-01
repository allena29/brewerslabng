#!/usr/bin/python

# piTempBuzzer
import os
import json
import hashlib
import pickle
import struct
import socket
import syslog
import sys
import threading
import time

from gpiotools2 import gpiotools2
from pitmCfg import pitmCfg





class pitmButton:


	def __init__(self):
		self.logging=2		# 1 = syslog, 2 = stderr
		self.cfg = pitmCfg()
		self.handshake=None
		self.mcastMembership=False
		self.gpio=gpiotools2()

		self.doMonitoring=False
			

			
	def _log(self,msg):
		if self.logging == 1:
			syslog.syslog(syslog.LOG_DEBUG, msg)
		elif self.logging == 2:
			sys.stderr.write("%s\n" %(msg))

			
	def _err(self,msg):
		syslog.syslog(syslog.LOG_ERR, msg)
		sys.stderr.write("%s\n" %(msg))


	def broadcastButtonResult(self):
		print "advertising our Button  capabiltiies"
		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage={}
		controlMessage['_operation'] = 'button'
		controlMessage['_checksum'] ="                                        "


		while 1:

			controlMessage['_button'] = {}
			for button in ['swHlt','swFerm','swSparge','swMash','swBoil','swPump']:
				controlMessage['_button'][ button ] = self.gpio.input( button )
				if controlMessage['_button'][button] and not os.path.exists("simulator"): 
					controlMessage['_button'][ button ] = True
					o=open("ipc/%s" %(button),"w")
					o.close()
				elif os.path.exists("ipc/manualswitch_%s" %(button)):
					controlMessage['_button'][ button ] = True
					o=open("ipc/%s" %(button),"w")
					o.close()
				else:
					controlMessage['_button'][ button ] = False
					try:
						os.remove( "ipc/%s" %(button))
					except:
						pass	

			checksum = "%s%s" %(controlMessage,self.cfg.checksum)
			controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

			msg= json.dumps(controlMessage)
			msg= "%s%s" %(msg," "*(1200-len(msg)))

				 
			sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastButtonPort))
			time.sleep(1)


	"""
		when run locally we will touch files on the file system
		however we will accept events remotely and touch those files so that we can integrate into a simulator
	"""


	def buttonControl(self):

		self._log("Launching Multicast Button Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastButtonPortRX))
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastButtonPortRX))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True



		while True:
			(data, addr) = self.sock.recvfrom(1200)
			self.decodeButtonMessage(data)	
				

	def buttonUncontrol(self):
		if self.mcastMembership:
			self._log("Unregistering Multicast Button Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastButtonPortRX))
			self.sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.cfg.mcastGroup) + socket.inet_aton('0.0.0.0'))
			self.mcastMembership=False

	def decodeButtonMessage(self,data):
		"""
		"""
	
		self._log("in decodeMessage for buttonv2");
		try:
			cm = json.loads( data )
		except:
			self._log("Error unpickling input message\n%s" %(data))
			return

		checksum = cm['_checksum']
		cm['_checksum'] ="                                        "
		ourChecksum = hashlib.sha1("%s%s" %(cm,self.cfg.checksum)).hexdigest()
		self._log("Their checksum %s" %(checksum))
		self._log("Our checksum %s" %(ourChecksum))	
		sys.stderr.write(" %s \n" %(os.getcwd()))
		o=open("ipc/manual_%s" %(cm['button']),"w")
		o.close()


	def sendButtonMessage(self,button,action):
		"""
			button =
			action = press,on,off
		"""
		controlMessage={}

		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage['_operation'] = 'buttonv2'
		controlMessage['_checksum'] ="                                        "
		controlMessage['button']=button
		controlMessage['action']=action
	

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 

		if len(msg) > 1200:
			self._err("Cannot send message - packet too big")

			return
		sys.stderr.write( "%s" %(controlMessage))
		sys.stderr.write("\n")
		sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastButtonPortRX))
		sendSocket.close()




if __name__ == '__main__':
	buttonController = pitmButton()
	x=10000


	# get under the control of the flasher
	broadcastResult = threading.Thread(target=buttonController.broadcastButtonResult)
	broadcastResult.daemon = True
	broadcastResult.start()
	
	try:
		buttonController.buttonControl()
	except KeyboardInterrupt:
		buttonController.buttonUncontrol()
#		while 1:
#			time.sleep(100)




