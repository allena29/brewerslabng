#!/usr/bin/python

# piTempLedFlasher
import os
import hashlib
import json
import struct
import socket
import syslog
import sys
import threading
import time

from pitmCfg import pitmCfg

from i2ctools21 import *


class pitmLedFlasher:

    def uncontrol(self):
        if self.daemon:
            self.i2c.output('lFermBlue', 0)
            self.i2c.output('lFermGreen', 0)
            self.i2c.output('lBoilBlue', 0)
            self.i2c.output('lBoilGreen', 0)
            self.i2c.output('lMashBlue', 0)
            self.i2c.output('lMashGreen', 0)
            self.i2c.output('lSpargeBlue', 0)
            self.i2c.output('lSpargeGreen', 0)
            self.i2c.output('lHltBlue', 0)
            self.i2c.output('lHltGreen', 0)
            self.i2c.output('lSys', 0)

    def __init__(self, daemon=False):
        self.logging = 2		# 1 = syslog, 2 = stderr
        self.cfg = pitmCfg()
        self.daemon = daemon
        self.mcastMembership = False

        self.simulator = False
        if os.path.exists("simulator"):
            self.simulator = True
            print "Simulator Mode for LED"

        if daemon:
            self.i2c = i2ctools21(address=0x21)
            self.i2c.output('lMashRed', 0)
            self.i2c.output('lBoilRed', 0)
            self.i2c.output('lHltRed', 0)
            self.i2c.output('lFermRed', 0)
            self.i2c.output('lSpargeRed', 0)
            self.i2c.output('lSys', 0)
            self.i2c.output('lHltBlue', 0)
            self.i2c.output('lHltGreen', 0)
            self.i2c.output('lSpargeBlue', 0)
            self.i2c.output('lSpargeGreen', 0)
            self.i2c.output('lMashBlue', 0)
            self.i2c.output('lMashGreen', 0)
            self.i2c.output('lBoilBlue', 0)
            self.i2c.output('lBoilGreen', 0)
            self.i2c.output('lFermBlue', 0)
            self.i2c.output('lFermGreen', 0)

            if os.path.exists("simulator"):
                for x in ['lMashRed', 'lMashGreen', 'lMashBlue', 'lBoilRed', 'lBoilBlue', 'lBoilGreen', 'lHltRed', 'lHltGreen', 'lHltBlue', 'lFermRed', 'lFermGreen', 'lFermBlue', 'lSpargeRed', 'lSpargeGreen', 'lSpargeBlue', 'lSys', 'lMashPurple', 'lMashYellow', 'lMashWhite', 'lBoilPurple', 'lBoilYellow', 'lBoilWHite', 'lHltYellow', 'lHltPurple', 'lHltWhite', 'lFermWhite', 'lFermPurple', 'lFermYellow', 'lSpargeYellow', 'lSpargeWhite', 'lSpargePurple', 'lMashCyan', 'lBoilCyan', 'lHltCyan', 'lFermCyan', 'lSpargeCyan']:
                    try:
                        os.remove("ipc/fakeled_%s" % (x))
                    except:
                        pass

        self.flashThread = {'lMash': None, 'lFerm': None, 'lBoil': None, 'lSparge': None, 'lHlt': None, 'lSys': None}
        self.flashStatus = {'lMash': ("noflash", 0), 'lFerm': ("noflash", 0), 'lBoil': ("noflash", 0),
                            'lSparge': ("noflash", 0), 'lHlt': ("noflash", 0), 'lSys': ("noflash", 0)}

        self.ledBuzy = {
            'tBuzzer': False,
            'lSparge': False,
            'lMash': False,
            'lHlt': False,
            'lBoil': False,
            'lFerm': False,
            'lSys': False,
        }

    def _log(self, msg):
        if self.logging == 1:
            syslog.syslog(syslog.LOG_DEBUG, msg)
        elif self.logging == 2:
            #sys.stderr.write("%s\n" %(msg))
            sys.stderr.write("%s,%s,flasher,%s\n" % (time.ctime(), time.time(), msg))

    def _err(self, msg):
        syslog.syslog(syslog.LOG_ERR, msg)
        sys.stderr.write("%s\n" % (msg))

    def ledSubmission(self):
        self._log("Submitting to control of Controller")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
        self.sock.bind(('', self.cfg.mcastPort))
        mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.mcastMembership = True

        while True:
            (data, addr) = self.sock.recvfrom(1200)
            self.decodeLedMessage(data)
            time.sleep(2)

    def decodeLedMessage(self, data):
        """
        """

        try:
            cm = json.loads(data)
        except:
            self._log("Error unpickling input message\n%s" % (data))
            return

        if cm.has_key("lBuzzer"):
            self.doLed('tBuzzer', cm)
        if cm.has_key("lHlt"):
            self.doLed('lHlt', cm)
        if cm.has_key("lBoil"):
            self.doLed('lBoil', cm)
        if cm.has_key("lSparge"):
            self.doLed('lSparge', cm)
        if cm.has_key("lMash"):
            self.doLed('lMash', cm)
        if cm.has_key("lFerm"):
            self.doLed('lFerm', cm)
        if cm.has_key("lSys"):
            self.doLed('lSys', cm)

        checksum = cm['_checksum']
        cm['_checksum'] = "                                        "
        ourChecksum = hashlib.sha1("%s%s" % (cm, self.cfg.checksum)).hexdigest()

    def doLed(self, led, msg):
        self._log(" Message: %s : %s\n" % (msg, led))

        i2c = self.i2c
        if led == "lSys" and msg[led]['colour'] == "off":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output("lSys", 0)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sBlue" % (led))
                except:
                    pass
                try:
                    os.remove("ipc/fakeled_%sGreen" % (led))
                except:
                    pass
                try:
                    os.remove("ipc/fakeled_%sRed" % (led))
                except:
                    pass
        elif msg[led]['colour'] == "flash" and led == "lSys":
            self.flashStatus[led] = ("", time.time())
            self.flashThread[led] = threading.Thread(target=self.ledFlashing, args=(led,))
            self.flashThread[led].daemon = True
            self.flashThread[led].start()
        elif led == "lSys":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output("lSys", 1)
            if os.path.exists("simulator"):
                o = open("ipc/fakeled_%sRed" % (led), "w")
                o.close()
                o = open("ipc/fakeled_%sBlue" % (led), "w")
                o.close()
                o = open("ipc/fakeled_%sGreen" % (led), "w")
                o.close()
        if msg[led]['colour'] == "white":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 1)
            i2c.output('%sGreen' % (led), 1)
            i2c.output('%sRed' % (led), 1)
            if os.path.exists("simulator"):
                o = open("ipc/fakeled_%sRed" % (led), "w")
                o.close()
                o = open("ipc/fakeled_%sBlue" % (led), "w")
                o.close()
                o = open("ipc/fakeled_%sGreen" % (led), "w")
                o.close()
        elif msg[led]['colour'] == "purple":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 1)
            i2c.output('%sGreen' % (led), 0)
            i2c.output('%sRed' % (led), 1)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sGreen" % (led))
                except:
                    pass
                o = open("ipc/fakeled_%sBlue" % (led), "w")
                o.close()
                o = open("ipc/fakeled_%sRed" % (led), "w")
                o.close()
        elif msg[led]['colour'] == "yellow":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 0)
            i2c.output('%sGreen' % (led), 1)
            i2c.output('%sRed' % (led), 1)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sBlue" % (led))
                except:
                    pass
                o = open("ipc/fakeled_%sRed" % (led), "w")
                o.close()
                o = open("ipc/fakeled_%sGreen" % (led), "w")
                o.close()
        elif msg[led]['colour'] == "cyan":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 1)
            i2c.output('%sGreen' % (led), 1)
            i2c.output('%sRed' % (led), 0)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sRed" % (led))
                except:
                    pass
                o = open("ipc/fakeled_%sBlue" % (led), "w")
                o.close()
                o = open("ipc/fakeled_%sGreen" % (led), "w")
                o.close()
        elif msg[led]['colour'] == "red":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 0)
            i2c.output('%sGreen' % (led), 0)
            i2c.output('%sRed' % (led), 1)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sBlue" % (led))
                except:
                    pass
                try:
                    os.remove("ipc/fakeled_%sGreen" % (led))
                except:
                    pass
                o = open("ipc/fakeled_%sRed" % (led), "w")
                o.close()
        elif msg[led]['colour'] == "blue":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 1)
            i2c.output('%sGreen' % (led), 0)
            i2c.output('%sRed' % (led), 0)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sGreen" % (led))
                except:
                    pass
                try:
                    os.remove("ipc/fakeled_%sRed" % (led))
                except:
                    pass
                o = open("ipc/fakeled_%sBlue" % (led), "w")
                o.close()
        elif msg[led]['colour'] == "green":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 0)
            i2c.output('%sGreen' % (led), 1)
            i2c.output('%sRed' % (led), 0)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sBlue" % (led))
                except:
                    pass
                try:
                    os.remove("ipc/fakeled_%sRed" % (led))
                except:
                    pass
                o = open("ipc/fakeled_%sGreen" % (led), "w")
                o.close()
        elif msg[led]['colour'] == "flashred":
            self.flashStatus[led] = ("Red", time.time())
            self.flashThread[led] = threading.Thread(target=self.ledFlashing, args=(led,))
            self.flashThread[led].daemon = True
            self.flashThread[led].start()
        elif msg[led]['colour'] == "flashgreen":
            self.flashStatus[led] = ("Green", time.time())
            self.flashThread[led] = threading.Thread(target=self.ledFlashing, args=(led,))
            self.flashThread[led].daemon = True
            self.flashThread[led].start()
        elif msg[led]['colour'] == "flashblue":
            self.flashStatus[led] = ("Blue", time.time())
            self.flashThread[led] = threading.Thread(target=self.ledFlashing, args=(led,))
            self.flashThread[led].daemon = True
            self.flashThread[led].start()
        elif msg[led]['colour'] == "off":
            self.flashStatus[led] = ("noflash", time.time())
            i2c.output('%sBlue' % (led), 0)
            i2c.output('%sGreen' % (led), 0)
            i2c.output('%sRed' % (led), 0)
            if os.path.exists("simulator"):
                try:
                    os.remove("ipc/fakeled_%sBlue" % (led))
                except:
                    pass
                try:
                    os.remove("ipc/fakeled_%sGreen" % (led))
                except:
                    pass
                try:
                    os.remove("ipc/fakeled_%sRed" % (led))
                except:
                    pass

    def ledFlashing(self, led):
        doFlash = True
        (colour, uniqueId) = self.flashStatus[led]
        self._log("Flashing Led required %s : uniqueId=%s" % (led, uniqueId))
        if os.path.exists("simulator"):
            try:
                os.remove("ipc/fakeled_%sBlue" % (led))
            except:
                pass
            try:
                os.remove("ipc/fakeled_%sGreen" % (led))
            except:
                pass
            try:
                os.remove("ipc/fakeled_%sRed" % (led))
            except:
                pass

        while doFlash:
            (x, newUniqueId) = self.flashStatus[led]
            if uniqueId == newUniqueId:
                self.i2c.output("%s%s" % (led, colour), 1)
                if os.path.exists("simulator"):
                    o = open("ipc/fakeled_%s%s" % (led, colour), "w")
                    o.close()
                    time.sleep(0.4)
            if uniqueId == newUniqueId:
                self.i2c.output("%s%s" % (led, colour), 0)
                if os.path.exists("simulator"):
                    try:
                        os.remove("ipc/fakeled_%s%s" % (led, colour))
                    except:
                        pass
                time.sleep(0.4)
            if not uniqueId == newUniqueId:
                doFlash = False

    def listenLedThread(self):
        self._log("Starting Led Flasher Listening Thread")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
        self.sock.bind(('', self.cfg.mcastFlasherInPort))
        mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.mcastMembership = True

        while True:
            (data, addr) = self.sock.recvfrom(1200)
            self.decodeLedMessage(data)
            time.sleep(0.1)

    def broadcastLedResult(self):

        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
        controlMessage = {}
        controlMessage['_operation'] = 'flasher'
        controlMessage['_checksum'] = "                                        "

        checksum = "%s%s" % (controlMessage, self.cfg.checksum)
        controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

        msg = json.dumps(controlMessage)
        msg = "%s%s" % (msg, " " * (1200 - len(msg)))
        while 1:
            sendSocket.sendto(msg, (self.cfg.mcastGroup, self.cfg.mcastFlasherPort))
            time.sleep(0.5)

    def sendMessage(self, led, colour):
        """
        This function is used by client programs to send us a multicast message
                led = [lHlt,lMash,lSparge,lBoil,lFerm]
                colour = white, purple, yellow,blue,green, red, off
        """

        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
        controlMessage = {}
        controlMessage['_operation'] = 'flasher'
        controlMessage['_checksum'] = "                                        "
        controlMessage[led] = {'colour': colour}

        checksum = "%s%s" % (controlMessage, self.cfg.checksum)
        controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

        msg = json.dumps(controlMessage)
        msg = "%s%s" % (msg, " " * (1200 - len(msg)))
        sendSocket.sendto(msg, (self.cfg.mcastGroup, self.cfg.mcastFlasherInPort))


if __name__ == '__main__':
    try:
        controller = pitmLedFlasher(daemon=True)
        broadcastLedResult = threading.Thread(target=controller.broadcastLedResult)
        broadcastLedResult.daemon = True
        broadcastLedResult.start()

        listenLedThread = threading.Thread(target=controller.listenLedThread)
        listenLedThread.daemon = True
        listenLedThread.start()
#
        while 1:
            time.sleep(1)

    except KeyboardInterrupt:
        #		pass
        controller.uncontrol()
