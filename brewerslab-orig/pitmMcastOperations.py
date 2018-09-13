import socket
import struct
import hashlib
import logging
import syslog
import sys
import json
from pitmCfg import pitmCfg
from pitmLogHandler import pitmLogHandler

"""
This class provides a nice interface to read data from a multicast
socket. The payload is a dictionary in json format padded to exactly
1200 bytes.
"""


class pitmMcast:

    DISABLE_CHECKSUM = True

    def __init__(self):
        self.cfg = pitmCfg()
        self.groot = pitmLogHandler()
        self.sendSocket = None

    def _open_mcast_write_socket(self):
        """
        Open a socket for u to braodcast messges on
        """
        self.sendSocket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sendSocket.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)

    def _verify_checksum(self, controlMessage, port='Unknown'):
        received_checksum = controlMessage['_checksum']
        controlMessage['_checksum'] = "                                        "
        recalculated_checksum = hashlib.sha1(
            "%s%s" % (controlMessage, self.cfg.checksum)).hexdigest()

        if not recalculated_checksum == received_checksum:
            self.groot.err("Checksum mismatch for data on port %s: %s != %s" % (
                port, received_checksum, recalculated_checksum))

        return recalculated_checksum == received_checksum

    def _calculate_and_set_checksum(self, controlMessage):
        # generate the checksum with a bank string first
        controlMessage['_checksum'] = "                                        "
        checksum = "%s%s" % (controlMessage, self.cfg.checksum)
        # then update the message with the actual checksum
        controlMessage['_checksum'] = hashlib.sha1(checksum).hexdigest()

        return controlMessage

    def send_mcast_message(self, msg, port, app='unknown-app'):
        if not self.sendSocket:
            self._open_mcast_write_socket()
        controlMessage = msg
        controlMessage['_operation'] = app

        controlMessage = self._calculate_and_set_checksum(controlMessage)

        msg = json.dumps(controlMessage)
        msg = "%s%s" % (msg, " " * (1200 - len(msg)))
        self.sendSocket.sendto(msg, (self.cfg.mcastGroup, port))

    def open_socket(self, callback, port):
        """
        Open a socket a listen for data in 1200 byte chunks.
        Fire the callback each time
        """
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
        sock.bind(('', port))
        mreq = struct.pack("4sl", socket.inet_aton(
            self.cfg.mcastGroup), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            (data, addr) = sock.recvfrom(1200)
            try:
                cm = json.loads(data)
                checksum = cm['_checksum']
                cm['_checksum'] = "                                        "
                ourChecksum = hashlib.sha1("%s%s" % (cm, checksum)).hexdigest()
                if self.DISABLE_CHECKSUM or self._verify_checksum(cm, port):
                    callback(cm)
            except ImportError:
                self.groot.log("Error decoding input message\n%s" % (data))
                pass
