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
globalData={'/simulator-lcd':[{},{},{},{} ],
		'/simulator-led':{},
		'/simulator-button':{}  }
dataLastUpdate={'/simulator-lcd':0,
		'/simulator-led':0,
		'/simulator-button':0}
clientLastUpdate={}

def lcdMcast():
	global globalData,dataLastUpdate
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastLcdPort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True:
		(data, addr) = sock.recvfrom(1200)
		j=json.loads(data)
		try:
			globalData['/simulator-lcd'][ j['line'] ]  = j
			dataLastUpdate['/simulator-lcd']=time.time()
		except:
			pass
		time.sleep(0.2)		


sys.stderr.write("Joining Multicast LCD\n")
lcdThread = threading.Thread(target=lcdMcast)
lcdThread.daemon = True
lcdThread.start()

def ledMcast():
	global globalData,dataLastUpdate
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastFlasherInPort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True:
		(data, addr) = sock.recvfrom(1200)
		j=json.loads(data)
		if not j.has_key("lSys"):	j['ledSys']={'colour':'off'}
		if not j.has_key("lHlt"):	j['ledHt']={'colour':'off'}
		if not j.has_key("lSparge"):	j['ledSparge']={'colour':'off'}
		if not j.has_key("lMash"):	j['ledMash']={'colour':'off'}
		if not j.has_key("lBoil"):	j['ledBoil']={'colour':'off'}
		if not j.has_key("lFerm"):	j['ledFerm']={'colour':'off'}
		try:
			globalData['/simulator-led'] = j
			dataLastUpdate['/simulator-led']=time.time()
		except:
			pass
		time.sleep(0.2)		


sys.stderr.write("Joining Multicast LED\n")
ledThread = threading.Thread(target=ledMcast)
ledThread.daemon = True
ledThread.start()

def buttonMcast():
	global globalData,dataLastUpdate
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastButtonPort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True:
		(data, addr) = sock.recvfrom(1200)
		j=json.loads(data)
		try:
			globalData['/simulator-button'] = j
			dataLastUpdate['/simulator-button']=time.time()
		except:
			pass
		time.sleep(1)		


sys.stderr.write("Joining Multicast Button\n")
buttonThread = threading.Thread(target=buttonMcast)
buttonThread.daemon = True
buttonThread.start()


def publishWs():
	global globalData,clients,dataLastUpdate,clientLastUpdate
	while 1:
		for client in list(clients):
			if client.request.path == "/simulator-lcd":
				if dataLastUpdate[ client.request.path ] > clientLastUpdate[ "%s%s" %(client.address) ]:
					clientLastUpdate[ "%s%s" %(client.address) ] = dataLastUpdate[ client.request.path ]
					for lcdLine in globalData[ client.request.path ]:
						if lcdLine.has_key("line"):
							client.sendMessage( u"%s" %( json.dumps(lcdLine)  ))

			if client.request.path == "/simulator-led":
				if dataLastUpdate[ client.request.path ] > clientLastUpdate[ "%s%s" %(client.address) ]:
					clientLastUpdate[ "%s%s" %(client.address) ] = dataLastUpdate[ client.request.path ]
					if globalData[ client.request.path ].has_key("_operation"):
						client.sendMessage( u"%s" %( json.dumps(globalData['/simulator-led']  )))

			if client.request.path == "/simulator-button":
				if dataLastUpdate[ client.request.path ] > clientLastUpdate[ "%s%s" %(client.address) ]:
					clientLastUpdate[ "%s%s" %(client.address) ] = dataLastUpdate[ client.request.path ]
					if globalData[ client.request.path ].has_key("_operation"):
						client.sendMessage( u"%s" %( json.dumps(globalData['/simulator-button']['_button']  )))

		time.sleep(0.3)




publishThread = threading.Thread(target=publishWs)
publishThread.daemon = True
publishThread.start()


class McastWebService(WebSocket):

	def handleConnected(self):
		global clientLastUpdate
		print self.address, 'connected'
		clientLastUpdate[ "%s%s" %(self.address) ] = 0
		clients.append(self)

	def handleClose(self):
		global clientLastUdate
		clients.remove(self)
		del clientLastUpdate[ "%s%s" %(self.address) ]
		print self.address, 'closed'


sys.stderr.write("Starting WebSocket Server\n")
server = SimpleWebSocketServer('',54662, McastWebService)
server.serveforever()
