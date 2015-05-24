#!/usr/bin/python
import socket
import json
import struct
import signal
import sys
import time
import threading
from SimpleWebSocketServer import *
from pitmCfg import *

cfg=pitmCfg()
clients = []
globalData={'_lastUpdate':0,'lcd':{}}


def lcdMcast():
	global globalData
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastLcdPort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True:
		(data, addr) = sock.recvfrom(1200)
		print data
		globalData['lcd'] = data
		globalData['_lastUpdate']=time.time()
		time.sleep(0.5)		


sys.stderr.write("Joining Multicast LCD\n")
lcdThread = threading.Thread(target=lcdMcast)
lcdThread.daemon = True
lcdThread.start()


def publishWs():
	global globalData,clients
	while 1:
		for client in list(clients):
			print client.address, "send Data",globalData
			client.sendTextMessage( json.dumps( globalData ))

		time.sleep(1)
publishThread = threading.Thread(target=publishWs)
publishThread.daemon = True
publishThread.start()


class McastWebService(WebSocket):
	global clientLastUpdate

	def handleMessage(self):
		for client in list(clients):
			if client != self:
				client.sendMessage(self.address[0] + ' - ' + self.data)

	def handleConnected(self):
		print self.address, 'connected'
		clients.append(self)

	def handleClose(self):
		clients.remove(self)
		print self.address, 'closed'


sys.stderr.write("Starting WebSocket Server\n")
server = SimpleWebSocketServer('',54662, McastWebService)
server.serveforever()
