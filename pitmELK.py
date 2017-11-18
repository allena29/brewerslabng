from __future__ import division
#!/usr/bin/python

# piTempLedFlasher
import socket
import json
import os
import hashlib
import struct
import socket
import syslog
import sys
import threading
import time


"""
With a simple ELK stack running we can use Kibana to draw basic graphs
The RRD tool graphs have a tenedency to fail to generate - and are not
pretty by today standard.

Getting ELK running on Raspberry Pi isn't so trivial because of CPU 
architecture, so this instead sends the results to logstash running on
another machine.

The logstash conf is very trivial.

input{
  tcp {
      port => 5959
          codec => json
      }
}




output {
  stdout {
    codec => rubydebug
  }
  elasticsearch {
  }
}
"""

from pitmCfg import pitmCfg

class pitmELKMonitor:


	SERVER_ADDRESS = ('192.168.3.1', 5959)

	def __init__(self):
		self.logging=2		# 1 = syslog, 2 = stderr
		self.cfg = pitmCfg()

		self.tcpsock = None
		
		self.msg_dict = {
			'@metadata' : {
				'beat' : 'pitm-elk-monitor',
				'type' : 'python'
			}
		}

	
	def __del__(self):
		if self.tcpsock:
			self.tcpsock.close()



	def _open_socket_if_it_is_closed(self):
		if self.tcpsock:
			return True

		try:

			self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.tcpsock.connect(self.SERVER_ADDRESS)
			print 'socket opened to ', self.SERVER_ADDRESS

		except:
			self.tcpsock = None
		
		return self.tcpsock


	def decodeTempMessage(self,data,zone="Unknown"):
		"""
		"""

		try:
			cm = json.loads( data )
		except:
			return

		checksum = cm['_checksum']
		cm['_checksum'] ="                                        "
		ourChecksum = hashlib.sha1("%s%s" %(cm,self.cfg.checksum)).hexdigest()
		self.doMonitoring = False
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

		if self.doMonitoring:
			for probe in cm['currentResult']:
				if cm['currentResult'][probe]['valid']:
					print probe,cm['currentResult'][probe]['temperature']
					now = time.localtime()

					probeId = self.cfg.probeId[probe]

					self.msg_dict[probeId] = float(cm['currentResult'][probe]['temperature'])
					self.msg_dict["@timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S", now)				

					self._open_socket_if_it_is_closed()


					try:
						msg = json.dumps(self.msg_dict) + '\n'
						self.tcpsock.sendall(msg)
						print "sent"+ msg
					except:
						print "Unable to send on socket"
						self.tcpsock = None
	
	def updateStatsZoneA(self):
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
			time.sleep(2)		


if __name__ == '__main__':
	try:
		controller = pitmELKMonitor()

		updateStatsThread = threading.Thread(target=controller.updateStatsZoneA)
		updateStatsThread.daemon = True
		updateStatsThread.start()
	
		while 1:
			time.sleep(1)	

	except KeyboardInterrupt:
		controller.uncontrol()



