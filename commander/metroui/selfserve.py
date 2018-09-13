#!/usr/bin/python

# Self Server
import sys
import time
import os
import pickle
import BaseHTTPServer
import CGIHTTPServer
import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import socket
import struct
import threading

class mcastThread:

	def __del__(self):
		try:
	        	self.sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(self.MCAST_GRP) + socket.inet_aton('0.0.0.0'))
		except:
			pass

	def __init__(self):
		self.MCAST_GRP = '239.232.168.250'
		self.MCAST_PORT = 5087
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
		self.sock.bind(('', self.MCAST_PORT))
		mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
		self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


	def monitorTemp(self):
		while 1:
			try:
				data, addr = self.sock.recvfrom(1059)
				d=pickle.loads(data)

				o=open("/tmp/tempresult","w")
				o.write(data)
				o.close()
				for x in d['currentResult']:
					sys.stdout.write("%s %s %.4f\t" %(x,d['currentResult'][x]['valid'],d['currentResult'][x]['temperature']))
				for c in range(3-len(d['currentResult'])):
					sys.stdout.write("--------------- ----- -----\t")

				sys.stdout.write("\n")
				sys.stdout.flush()

			except:
				pass
			time.sleep(0.75)



print """
=========================================================


Launching Local Server:
	To access use: http://localhost:54661/



=========================================================
 

"""



if not os.path.exists("index.html"):
	o=open("index.html","w")
	o.write("""
	<Script Langauge="Javascript">
	window.location.replace("metroui/index.py");
	</script>
	""")
	o.close()




class ThreadingSimpleServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass



if __name__ == '__main__':
	mcastThread=mcastThread()
	mcastTempMonitorThread = threading.Thread(target=mcastThread.monitorTemp)
	mcastTempMonitorThread.daemon=True
	mcastTempMonitorThread.start()

handler = CGIHTTPServer.CGIHTTPRequestHandler
server = ThreadingSimpleServer(('', 54661), handler)
handler.cgi_directories = ["/metroui"]
try:
	while 1:
        	sys.stdout.flush()
        	server.handle_request()
except KeyboardInterrupt:
	print "Finished"




