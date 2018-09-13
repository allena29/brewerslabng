#!/usr/bin/python



import hashlib
import json
import socket
import struct
import sys
import threading
import syslog
import time
import os
import max7219.led as led


from pitmCfg import pitmCfg


class pitmLEDmatrix:


	def __init__(self,rpi=True):
		self.logging=4		# 1 = syslog, 2 = stderr, 3 = supress repeat messages, 4 = every 100 seconds
		self.lastLog=["","","","","","","","","","",""]	
		self.cfg = pitmCfg()
		self.mcastMembership=False
		self._log("pitmLEDmatrix")


		self.lastMsgTimestamp=0	
		self.lastLine0=None
		self.lastLine1=None
		if len(sys.argv) < 2:
			self.device = led.matrix(cascaded=8,vertical=True)
			self.device.brightness(0)

	def __del__(self):
		if self.mcastMembership:
			self._log("Unregistering Multicast LCD Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastMatrixPort))
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
		self._log("Launching Multicast LED Matrix Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastMatrixPort))
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
		self.sock.bind(('', self.cfg.mcastMatrixPort))
		mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		self.mcastMembership=True


		while True:
			(data, addr) = self.sock.recvfrom(1200)
			self.decodeMessage(data)	
			time.sleep(0.2)
				
	

	def uncontrol(self):
		if self.mcastMembership:
			self._log("Unregistering Multicast LED Matrix Socket %s:%s" %(self.cfg.mcastGroup,self.cfg.mcastMatrixPort))
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
		self._log(" Text: %s " %(cm['text']) )
		self.device.show_message( cm['text'] )



		




	def sendMessage(self,text="<......>"):
		"""
		Although send message is in the same class this encodes a message
		and sends it on the multicast socket and is intended to be used by client
		programs.
		
		The options we accept here are a subset of raspberrySpyLcd scrolLText
		The values do align with raspberrySpyLcd

		text 			"string" to print	
		"""
		controlMessage={}

		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage['_operation'] = 'ledMatrix'
		controlMessage['_checksum'] ="                                        "
		controlMessage['text'] = text

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 

		if len(msg) > 1200:
			self._err("Cannot send message - packet too big")
			return

		sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastMatrixPort))
		sendSocket.close()




if __name__ == '__main__':

	if len(sys.argv) < 2:
		# launch daemon
		try:
			ledm = pitmLEDmatrix()
			ledm.control()
		except KeyboardInterrupt:
			ledm.uncontrol()

	else:
		print "pitmLEDmatrix in client mode"
		ledm=pitmLEDmatrix()
		try:
			ledm.sendMessage(sys.argv[1])
		except:
			pass
		import time


