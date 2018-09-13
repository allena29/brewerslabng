import json
import time
import pickle
import sys
import socket
import struct

class test:

	def __init__(self):
		try:
			o=open("/currentdata/temp-mcast-rx-on","w")
			o.close()
		except:
			pass
	def __del__(self):
		try:
			os.unlink("/currentdata/temp-mcast-rx-on")
		except:
			pass

t=test()

MCAST_GRP = '239.232.168.250'
MCAST_PORT = 5087

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
                #d=pickle.loads(data)
                d=json.loads(data)
#{'_operation': 'temperatureResults', 'currentStatus': 0, '_checksum': '81bed18605115fd99c84bd694cf7773fc85fea34', 'currentResult': {'28-000003ebc866': {'ti
#mestamp': 1386191015.916445, 'valid': True, 'temperature': 14.812}, '28-000004714ca7': {'timestamp': 1386191017.70598, 'valid': True, 'temperature': 15.125}}
#}
		o=open("/currentdata/temps/currentResult","w")
		o.write( pickle.dumps(d))
		o.close()
		for x in d['currentResult']:
                        sys.stdout.write("%s %s %.4f\t" %(x,d['currentResult'][x]['valid'],d['currentResult'][x]['temperature']))
				
                for c in range(3-len(d['currentResult'])):
                        sys.stdout.write("--------------- ----- -----\t")

                sys.stdout.write("\n")
                sys.stdout.flush()
        except ImportError:
                a=False
                sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP, socket.inet_aton(MCAST_GRP) + socket.inet_aton('0.0.0.0'))

	time.sleep(1)

del t

