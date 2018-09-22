import socket
import struct
import hashlib
import logging
import syslog
import sys
import json

import blng.LogHandler as LogHandler

"""
This class provides a nice interface to read data from a multicast
socket. The payload is a dictionary in json format padded to exactly
1200 bytes.
"""


class Multicast:

    DISABLE_CHECKSUM = True
    CHECKSUM = "ABFJDSGF"
    MCAST_GROUP = "239.232.168.250"
    MCAST_PORT = 5000

    def __init__(self, mcast_port=0, log_component=''):
        self.log = LogHandler.LogHandler(log_component + 'Multicast')
        self.sendSocket = None
        if mcast_port:
            self.MCAST_PORT = mcast_port

    def _open_mcast_write_socket(self):
        """
        Open a socket for u to braodcast messges on
        """
        self.log.info('Opening multicast send socket')
        self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)

    def _verify_checksum(self, controlMessage, port='Unknown'):
        received_checksum = controlMessage['_checksum']
        controlMessage['_checksum'] = "                                        "
        pre_verify = "%s%s" % (controlMessage, self.CHECKSUM)
        recalculated_checksum = hashlib.sha1(pre_verify.encode('utf-8')).hexdigest()

        if not recalculated_checksum == received_checksum:
            self.log.err("Checksum mismatch for data on port %s: %s != %s" % (
                port, received_checksum, recalculated_checksum))

        return recalculated_checksum == received_checksum

    def _calculate_and_set_checksum(self, controlMessage):
        # generate the checksum with a bank string first
        controlMessage['_checksum'] = "                                        "
        checksum = "%s%s" % (controlMessage, self.CHECKSUM)
        # then update the message with the actual checksum
        controlMessage['_checksum'] = hashlib.sha1(checksum.encode('utf-8')).hexdigest()

        return controlMessage

    def send_mcast_message(self, msg, port, app='unknown-app'):
        if not self.sendSocket:
            self._open_mcast_write_socket()
        controlMessage = msg
        controlMessage['_operation'] = app

        controlMessage = self._calculate_and_set_checksum(controlMessage)

        msg = json.dumps(controlMessage)
        msg = "%s%s" % (msg, " " * (1200 - len(msg)))
        self.sendSocket.sendto(msg.encode('UTF-8'), (self.MCAST_GROUP, self.MCAST_PORT))

    def open_socket(self, callback, port):
        """
        Open a socket a listen for data in 1200 byte chunks.
        Fire the callback each time
        """
        self.log.info('Opening Multicast Receive Socket %s' % (port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
        sock.bind(('', port))
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GROUP), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            (data, addr) = sock.recvfrom(1200)
            try:
                cm = json.loads(data)
                checksum = cm['_checksum']
                cm['_checksum'] = "                                        "
                received_checksum = "%s%s" % (cm, checksum)
                ourChecksum = hashlib.sha1(received_checksum.encode('utf-8')).hexdigest()
                if self.DISABLE_CHECKSUM or self._verify_checksum(cm, port):
                    callback(cm)
            except ImportError:
                self.log.debug("Error decoding input message\n%s" % (data))
                pass
