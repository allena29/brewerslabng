#!/usr/bin/python
import os
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
		'/simulator-ssr':{},
		'/simulator-relay':{},
		'/simulator-gov':{},
		'/simulator-temp':{},
		'/simulator-button':{}  }
dataLastUpdate={'/simulator-lcd':0,
		'/simulator-led':0,
		'/simulator-ssr':0,
		'/simulator-relay':0,
		'/simulator-gov':0,
		'/simulator-temp':0,
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
			#dataLastUpdate['/simulator-led']=time.time()
			dataLastUpdate['/simulator-lcd']=time.time()
		except:
			pass
		time.sleep(0.2)		


sys.stderr.write("Joining Multicast LED\n")
ledThread = threading.Thread(target=ledMcast)
ledThread.daemon = True
ledThread.start()


def relayMcast():
	global globalData,dataLastUpdate
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastRelayPort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True:
		(data, addr) = sock.recvfrom(1200)
		j=json.loads(data)
		try:
			globalData['/simulator-relay'] = j
			#dataLastUpdate['/simulator-relay']=time.time()
			dataLastUpdate['/simulator-ssr']=time.time()
		except:
			pass
		time.sleep(0.8)		


sys.stderr.write("Joining Multicast Relay\n")
relayThread = threading.Thread(target=relayMcast)
relayThread.daemon = True
relayThread.start()


def ssrrelayMcast():
	global globalData,dataLastUpdate
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastSsrRelayPort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True:
		(data, addr) = sock.recvfrom(1200)
		j=json.loads(data)
		try:
			globalData['/simulator-ssr'] = j
			dataLastUpdate['/simulator-ssr']=time.time()
		except:
			pass
		time.sleep(0.2)		


sys.stderr.write("Joining Multicast SSR Relay\n")
ssrrelayThread = threading.Thread(target=ssrrelayMcast)
ssrrelayThread.daemon = True
ssrrelayThread.start()



def govMcast():
	global globalData,dataLastUpdate
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastPort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	lastMode="__"
	while True:
		(data, addr) = sock.recvfrom(1200)
		j=json.loads(data)
		try:
			globalData['/simulator-gov'] = j
			dataLastUpdate['/simulator-gov']=time.time()
			if j.has_key("_mode"):
				if not j['_mode'] == lastMode:	
					try:
						o=open("mode","w")
						o.write( j['_mode'])
						o.close()
						lastMode = j['_mode']
						print "set mode to",lastMode
					except:
						pass
		except:
			pass
		time.sleep(0.9)		


sys.stderr.write("Joining Multicast Gov\n")
govThread = threading.Thread(target=govMcast)
govThread.daemon = True
govThread.start()




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
			#dataLastUpdate['/simulator-button']=time.time()
			dataLastUpdate['/simulator-gov']=time.time()
		except:
			pass
		time.sleep(1)		


sys.stderr.write("Joining Multicast Button\n")
buttonThread = threading.Thread(target=buttonMcast)
buttonThread.daemon = True
buttonThread.start()



def tempMcast():
	global globalData,dataLastUpdate
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
	sock.bind(('', cfg.mcastTemperaturePort))
	mreq = struct.pack("4sl", socket.inet_aton(cfg.mcastGroup), socket.INADDR_ANY)
	sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	while True:
		(data, addr) = sock.recvfrom(1200)
		j=json.loads(data)
		try:
			globalData['/simulator-temp'] = j
			#dataLastUpdate['/simulator-temp']=time.time()
			dataLastUpdate['/simulator-gov']=time.time()
		except:
			pass
		time.sleep(1)		


sys.stderr.write("Joining Multicast Temperature\n")
tempThread = threading.Thread(target=tempMcast)
tempThread.daemon = True
tempThread.start()


def publishWs():
	global globalData,clients,dataLastUpdate,clientLastUpdate
	while 1:
		for client in list(clients):
			if client.request.path == "/simulator-lcd":
				if dataLastUpdate[ client.request.path ] > clientLastUpdate[ "%s%s" %(client.address) ]:
					clientLastUpdate[ "%s%s" %(client.address) ] = dataLastUpdate[ client.request.path ]
					client.sendMessage( u"%s" %( json.dumps( {
						'lcd0': globalData[ "/simulator-lcd"][0],
						'lcd1': globalData[ "/simulator-lcd"][1],
						'lcd2': globalData[ "/simulator-lcd"][2],
						'lcd3': globalData[ "/simulator-lcd"][3],
						'led': globalData["/simulator-led"],	
						})  ))

				if (time.time() - dataLastUpdate[ client.request.path ] ) > 600:
					globalData['/simulator-lcd'][0]={'importance':0,'text':' - no active lcd'}
					globalData['/simulator-lcd'][1]={'importance':0,'text':'   messages'}
					globalData['/simulator-lcd'][2]={'importance':0,'text':''}
					globalData['/simulator-lcd'][3]={'importance':0,'text':''}
					globalData['/simulator-led']={'lSys':{'colour':'red'},
								      'lHlt':{'colour':'red'},
								      'lSparge':{'colour':'red'},
								      'lFerm':{'colour':'red'},
								      'lBoil':{'colour':'red'},
								      'lMash':{'colour':'red'} }
					client.sendMessage( u"%s" %( json.dumps( {
						'lcd0': globalData[ "/simulator-lcd"][0],
						'lcd1': globalData[ "/simulator-lcd"][1],
						'lcd2': globalData[ "/simulator-lcd"][2],
						'lcd3': globalData[ "/simulator-lcd"][3],
						'led': globalData["/simulator-led"],	
						})  ))

			if client.request.path == "/simulator-ssr":
				if dataLastUpdate[ client.request.path ] > clientLastUpdate[ "%s%s" %(client.address) ]:
					clientLastUpdate[ "%s%s" %(client.address) ] = dataLastUpdate[ client.request.path ]
					if globalData[ client.request.path ].has_key("_operation"):
						client.sendMessage( u"%s" %( json.dumps( {'ssr':globalData['/simulator-ssr'], 'relay': globalData['/simulator-relay'] } )  ))


			if client.request.path == "/simulator-gov":
				if dataLastUpdate[ client.request.path ] > clientLastUpdate[ "%s%s" %(client.address) ]:
					clientLastUpdate[ "%s%s" %(client.address) ] = dataLastUpdate[ client.request.path ]
					if globalData[ client.request.path ].has_key("_operation"):
						laststep=""
						if globalData['/simulator-gov'].has_key("_brewlog"):
							brewlog=globalData['/simulator-gov']['_brewlog']
							if os.path.exists("../metroui/progress/%s/last-step-complete" %(brewlog)):
								laststep=open("../metroui/progress/%s/last-step-complete" %(brewlog)).read()
					
						client.sendMessage( u"%s" %( json.dumps(
							{  'gov':globalData['/simulator-gov'],
							   'button':globalData['/simulator-button'],
							   'laststep':laststep,
							   'temp':globalData['/simulator-temp']
							}  )))

				if (time.time() - dataLastUpdate[ client.request.path ] ) > 600:
					globalData[ '/simulator-gov' ] =  {'_mode':'Lost Contact with Governer'} 
					globalData[ '/simulator-temp' ] = {}
					laststep="Unkown"
					globalData['/simulator-button'] = {}

					client.sendMessage( u"%s" %( json.dumps(
						{  'gov':globalData['/simulator-gov'],
						   'button':globalData['/simulator-button'],
						   'laststep':laststep,
						   'temp':globalData['/simulator-temp']
						}  )))

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
