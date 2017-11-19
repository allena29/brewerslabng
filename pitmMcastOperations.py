import socket
import struct
import hashlib
import logging
import syslog
import sys
import json
from pitmCfg import pitmCfg

"""
This class provides a nice interface to read data from a multicast
socket. The payload is a dictionary in json format padded to exactly
1200 bytes.
"""

class pitmMcast:

    DISABLE_CHECKSUM = True

    def __init__(self):
        # TODO: cleanup logging to use something more standard
        self.logging = 3
        self.lastLog = ["", "", "", "", "", "", "", "", "", "", ""]
        self.cfg = pitmCfg()

    def open_socket(self, callback, port):
        """
        Open a socket a listen for data in 1200 byte chunks.
        Fire the callback each time
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
        sock.bind(('', port))
        mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            (data, addr) = sock.recvfrom(1200)
            try:
                cm = json.loads(data)
                checksum = cm['_checksum']
                cm['_checksum'] = "                                        "
                ourChecksum = hashlib.sha1("%s%s" % (cm, checksum)).hexdigest()
                if self.DISABLE_CHECKSUM or checksum == ourChecksum:
                    callback(cm)
                else:
                    self._log("Checksum mismatch for data on port %s: %s != %s" %(port, checksum, ourChecksum))
            except ImportError:
                self._log("Error decoding input message\n%s" % (data))
                pass


    def _log(self, msg, importance=10):
        if self.logging == 1:
            if importance > 9:
                syslog.syslog(syslog.LOG_DEBUG, msg)
        elif self.logging == 2:
            sys.stderr.write("%s\n" % (msg))
        elif self.logging == 3:
            if (importance > 9) or ((("%s" % (time.time())).split(".")[0][-3:] == "000") or (not self.lastLog[importance] == msg)):
                syslog.syslog(syslog.LOG_DEBUG, msg)
                self.lastLog[importance] = msg
            sys.stderr.write("%s\n" % (msg))

