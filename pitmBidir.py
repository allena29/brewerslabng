#!/usr/bin/python

# piTempBuzzer
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





class pitmNFS:


	def __init__(self):
		self.logging=2		# 1 = syslog, 2 = stderr
		self.cfg = pitmCfg()
		self.handshake=None
		self.mcastMembership=False


		self.doMonitoring=False
			

			
	def _log(self,msg):
		if self.logging == 1:
			syslog.syslog(syslog.LOG_DEBUG, msg)
		elif self.logging == 2:
			sys.stderr.write("%s\n" %(msg))

			
	def _err(self,msg):
		syslog.syslog(syslog.LOG_ERR, msg)
		sys.stderr.write("%s\n" %(msg))


	def broadcastNFSResult(self):
		print "advertising our NFS  capabiltiies"
		sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
		controlMessage={}
		controlMessage['_operation'] = 'nfs'
		controlMessage['_handshake']=self.handshake
		controlMessage['_checksum'] ="                                        "

		checksum = "%s%s" %(controlMessage,self.cfg.checksum)
		controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

		msg= json.dumps(controlMessage)
		msg= "%s%s" %(msg," "*(1200-len(msg))) 
		while 1:
			sendSocket.sendto( msg ,(self.cfg.mcastGroup,self.cfg.mcastBidirPort))
			time.sleep(1)

if __name__ == '__main__':
	try:
		controller = pitmNFS()
		x=10000

		if not os.path.exists("simulator"):
			while int(x) > 0 and not  int(x) == 32 and not int(x) == 8192:
				controller._log("attempting mount")
				x=os.system("sudo mount 192.168.1.14:/home/allena29/piTempMonitor/master/ipc /home/allena29/piTempMonitor/slave/ipc")
				time.sleep(2)

		while not controller.handshake:
			if os.path.exists("ipc/handshake"):
				o=open("ipc/handshake")
				controller.handshake = o.read()
				o.close()
			time.sleep(1)

		# get under the control of the flasher
		broadcastNFSResult = threading.Thread(target=controller.broadcastNFSResult)
		broadcastNFSResult.daemon = True
		broadcastNFSResult.start()
		
		while 1:
			time.sleep(100)

	except KeyboardInterrupt:
		controller.uncontrol()



