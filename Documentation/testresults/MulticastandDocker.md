# NOte we either get everything off the wire or we lose it with this code


### client


```python
import struct
import socket
import time

buttonSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
buttonSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
buttonSock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
buttonSock.bind(('', 50000))
mreq = struct.pack("4sl", socket.inet_aton('239.232.168.250'), socket.INADDR_ANY)
buttonSock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
while 1:
    (data, addr) = buttonSock.recvfrom(8)
    print data,addr,'...'
    time.sleep(0.01)
```


### server

```python
root@7ca208fe8639:/opt/dev# more test.py
import struct
import time

import socket

sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
while 1:
    msg='isdjfiosdhfiowhfio2rh2934hr29fwhf92hf982ehf2'
    sendSocket.sendto( msg ,('239.232.168.250',50000))
    print 'sent msg', msg
    time.sleep(1)
```


# iperf

This was confirmed with tcpdump - no special things.

### server

```
root@aa113cf86a53:/opt/dev# iperf -s -u -B 224.0.55.55 -i 1
------------------------------------------------------------
Server listening on UDP port 5001
Binding to local address 224.0.55.55
Joining multicast group  224.0.55.55
Receiving 1470 byte datagrams
UDP buffer size:  208 KByte (default)
------------------------------------------------------------
[  4] local 224.0.55.55 port 5001 connected with 172.17.0.2 port 54526
[  4]  0.0- 1.0 sec   129 KBytes  1.06 Mbits/sec   0.111 ms    0/   90 (0%)
[  4]  1.0- 2.0 sec   128 KBytes  1.05 Mbits/sec   0.077 ms    0/   89 (0%)
[  4]  2.0- 3.0 sec   128 KBytes  1.05 Mbits/sec   0.077 ms    0/   89 (0%)
[  4]  0.0- 3.0 sec   386 KBytes  1.05 Mbits/sec   0.076 ms    0/  269 (0%)
```

### client

```
root@7ca208fe8639:/opt/dev# iperf -c 224.0.55.55 -u -T 32 -t 3 -i 1
------------------------------------------------------------
Client connecting to 224.0.55.55, UDP port 5001
Sending 1470 byte datagrams, IPG target: 11215.21 us (kalman adjust)
Setting multicast TTL to 32
UDP buffer size:  208 KByte (default)
------------------------------------------------------------
[  3] local 172.17.0.2 port 54526 connected with 224.0.55.55 port 5001
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec   131 KBytes  1.07 Mbits/sec
[  3]  1.0- 2.0 sec   128 KBytes  1.05 Mbits/sec
[  3]  2.0- 3.0 sec   128 KBytes  1.05 Mbits/sec
[  3]  0.0- 3.0 sec   386 KBytes  1.05 Mbits/sec
[  3] Sent 269 datagrams
root@7ca208fe8639:/opt/
```

