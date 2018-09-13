import time
import json
import sys
import socket
import struct

class test:

	def __init__(self):
		try:
			o=open("/currentdata/gov-mcast-rx-on","w")
			o.close()
		except:
			pass
	def __del__(self):
		try:
			os.unlink("/currentdata/gov-mcast-rx-on")
		except:
			pass

t=test()

MCAST_GRP = '239.232.168.250'
MCAST_PORT = 5085

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.bind(('', MCAST_PORT))
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print MCAST_GRP,MCAST_PORT


a=True
I=500
while a:
#        if I == 0:
 #               a=False
  #      I=I-1
        try:
                data, addr = sock.recvfrom(1059)
#               sys.stdout.write(".")
#               sys.stdout.write(data)
                d=json.loads(data)
		sys.stdout.write("%s: " %(time.ctime()))
		sys.stdout.write( d['_mode'] )
		try:
			o=open("/currentdata/mode", "w")
			o.write( d['_mode'])
			o.close()
		except:
			pass
		sys.stdout.write("\n")
                sys.stdout.flush()
        except ImportError:
                a=False
                sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(MCAST_GRP) + socket.inet_aton('0.0.0.0'))

	time.sleep(1)

del t

