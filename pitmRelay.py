#!/usr/bin/python
# piTempBuzzer
import os
import hashlib
import struct
import socket
import syslog
import sys
import threading
import time

from pitmCfg import pitmCfg
from pitmLCDisplay import *
from pitmMcastOperations import pitmMcast
from gpiotools import gpiotools



class pitmRelay:

    """
    This calls deals with the logic for turning relay's on and off.

    An eight-relay board is connected to a Raspberry PI for the following functions
        1) Fridge Heater
        2) Fridge
        3) Fridge Reciculating Fan
        4) Extract Fan (for boil-time)

    The other pins relays are used for 
        Enable power to Zone A
        Enable power to Zone B
        Toggle Zone A use  ** ONE OF THESE RELAYS IS BROKEN **
        Toggle Zone B use

    """
    
    def __init__(self):
        self.logging = 3		# 1 = syslog, 2 = stderr
        self.lastLog = ["", "", "", "", "", "", "", "", "", "", ""]
        self.cfg = pitmCfg()
        self.gpio = gpiotools()
        self.lcdDisplay = pitmLCDisplay()

        self.fermCoolActiveFor = -1
        self.fermHeatActiveFor = -1

        self.fridgeCompressorDelay = 300
        self.fridgeCool = False
        self.fridgeHeat = False

        # Count how long we have been active for
        self.meterFermH = 0
        self.meterFermC = 0

        self.gpio.output('fermHeat', 0)
        self.gpio.output('fermCool', 0)
        self._lastValidReading = {'ferm': -1}

        self.mcastMembership = False

        self.zoneTemp = -1
        self.zoneTarget = -1
        self.zoneTempTimestamp = -1
        self.zoneUpTarget = -1
        self.zoneDownTarget = -1

        self.ssrZoneA = False
        self.ssrZoneB = False

        self.ssrPinA = False
        self.ssrPinB = False

        self._mode = "UNKNOWN"

        self._gpioFermCool = None
        self._gpioFermHeat = None
        self._gpioreircfan = None
        self._gpioExtractor = None
        self.gpio.output("fermCool", 0)
        self.gpio.output('reircfan', 0)
        self.gpio.output('extractor', 0)
        self.gpio.output("fermHeat", 0)
        self.cycle = 4
        self.zoneAduty = 0
        self.zoneBduty = 0
        self.zoneAmeter = 0
        self.zoneBmeter = 0

        # used for zone toggling
        self.useZoneA = True
        self.zoneToggleCount = 0
        self.singleZone = True

        self.reircfanCount = 0

        self.ssrFanRequiredUntil = -1

    def __del__(self):
        self._mode = "shutdown"
        self.gpio.output('fermHeat', 0)
        self.gpio.output('fermCool', 0)
        self.gpio.output('reircfan', 0)
        self.gpio.output('extractor', 0)
        self.gpio.output('zoneA', 0)
        self.gpio.output('zoneB', 0)
        self.gpio.output('tSsrFan', 0)

    def uncontrol(self):
        self._log("Uncontrol Called")
        self._mode = "shutdown"
        self.gpio.output('fermHeat', 0)
        self.gpio.output('fermCool', 0)
        self.gpio.output('reircfan', 0)
        self.gpio.output('extractor', 0)
        self.gpio.output('zoneA', 0)
        self.gpio.output('zoneB', 0)
        self.gpio.output('tSsrFan', 0)

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

    def _err(self, msg):
        syslog.syslog(syslog.LOG_ERR, msg)
        sys.stderr.write("%s\n" % (msg))

    def submission(self):
        self._log("Submitting to control of Controller")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 4)
        self.sock.bind(('', self.cfg.mcastPort))
        mreq = struct.pack("4sl", socket.inet_aton(self.cfg.mcastGroup), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            (data, addr) = self.sock.recvfrom(1200)
            try:
                cm = json.loads(data)
            except:
                self._log("Error decoding input message\n%s" % (data))
                return

            checksum = cm['_checksum']
            cm['_checksum'] = "                                        "
            ourChecksum = hashlib.sha1("%s%s" % (cm, self.cfg.checksum)).hexdigest()

            self._mode = cm['_mode']

            time.sleep(1)

    def zoneTempThread(self):
        self._log("Listening for temperature'")
        mcast_handler = pitmMcast()
        mcast_handler.open_socket(self.callback_zone_temp_thread, self.cfg.mcastTemperaturePort)

    def callback_zone_temp_thread(self, cm):
        """
        This call back decodes the temperature and sets it on ourself.
        It also logs
        """
        if not self._mode == "idle":
            if cm['currentResult'].has_key(self.cfg.fermProbe):
                if cm['currentResult'][self.cfg.fermProbe]['valid']:
                    self.zoneTemp = float(cm['currentResult'][self.cfg.fermProbe]['temperature'])
                    self.zoneTempTimestamp = time.time()
                    if self.fridgeCompressorDelay > 0:
                        delay = True
                    else:
                        delay = False
                    self._log("Temp: %s Target: %s fridgeHeat: %s/%s fridgeCool: %s/%s (delay %s) " % (self.zoneTemp, self.zoneTarget,
                                                                                                       self.fridgeHeat, self._gpioFermHeat, self.fridgeCool, self._gpioFermCool, delay), importance=0)
                else:
                    self.lcdDisplay.sendMessage("Temp Result Error", 2)

        if cm.has_key("tempTargetFerm"):
            # zoneDownTarget when we need to start cooling
            # zoneUpTarget when we need to start heating
            # zoneTarget when we need to stop cooling/heating
            (self_zoneUpTarget, self_zoneDownTarget, self_zoneTarget) = cm['tempTargetFerm']
            if self_zoneUpTarget < 5 or self_zoneDownTarget < 5 or self_zoneTarget < 5:
                self._log("Temp Target is invalid %s,%s,%s" % (cm['tempTargetFerm']), importance=2)
            else:
                (self.zoneUpTarget, self.zoneDownTarget, self.zoneTarget) = cm['tempTargetFerm']


    def _zone_idle_shutdown(self):
            self.fridgeCompressorDelay = 301
            self.gpio.output("fermCool", 0)
            self.gpio.output('reircfan', 0)
            self.gpio.output('extractor', 0)
            self.gpio.output("fermHeat", 0)
            self._gpioFermCool = False
            self._gpioFermHeat = False
            self._gpioreircfan = False
            self._gpioExtractor = False
            self.fridgeHeat = False
            self.fridgeCool = False

    def _zone_boil(self):
            self.gpio.output('fermHeat', 0)
            self.gpio.output('fermCool', 0)
            self.gpio.output('extractor', 1)
            self._gpioFermCool = False
            self._gpioFermHeat = False
            self._gpioExtractor = True
    
    def zoneThread(self):
        """
        The main action loop that deals with switching relays
        """
        while True:
            self._do_zone_thread()
            time.sleep(1)

    def _do_zone_thread(self):
        if self._mode == "idle" or self._mode == "shutdown":
            self._zone_idle_shutdown()
        elif self._mode.count("boil"):
            self._zone_boil()
        elif self._mode == "ferm":

            if not self.fridgeHeat and not self.fridgeCool:
                self.lcdDisplay.sendMessage("", 2)

            if self._lastValidReading['ferm'] == -1:
                self._lastValidReading['ferm'] = time.time()
            print self._lastValidReading['ferm'] + 10, time.time(), self._lastValidReading['ferm'] + 10 < time.time()
            if self._lastValidReading['ferm'] + 100 < time.time():
                self._log("Critical: no valid readings for 100 seconds")
                self.gpio.output('fermHeat', 0)
                self._gpioFermCool = False
                self._gpioFermHeat = False
                self.lcdDisplay.sendMessage("CRITICAL Temp Result Error", 2)
                self.gpio.output('fermCool', 0)
                self.fridgeCompressorDelay = 300

            elif self._lastValidReading['ferm'] + 5 < time.time():
                self._log("Warning no valid readings for 5 seconds")
            elif os.path.exists("no-ferm-control"):
                self.gpio.output('fermHeat', 0)
                self._gpioFermCool = False
                self._gpioFermHeat = False
                self.gpio.output('fermCoolt', 0)
                self.fridgeCompressorDelay = 300
                print "Not using fermentation control"

            if self._gpioreircfan == None:
                self.gpio.output('reircfan', 0)
                self._gpioreircfan = False
            if self._gpioExtractor == None:
                self.gpio.output('extractor', 0)
                self._gpioExtractor = False
            if self.zoneTemp > 75 or self.zoneTemp < 4:
                self._log("Unrealistic Temperature Value %s:%s %s\n" % (self.zoneTemp, self.zoneTempTimestamp, self._mode))
            else:
                self._lastValidReading['ferm'] = time.time()
#					self.lcdDisplay.sendMessage(" - Target %sC" %(self.zoneTarget),1)
                if self.zoneTemp < self.zoneUpTarget and not self.fridgeHeat:
                    if self.zoneTemp < 3:
                        self._log("not setting heat required as we have a very low temp")
                    elif os.path.exists("ipc/disable-ferm-heat"):
                        pass
                    else:
                        self._log("Heating Requied %s < %s" % (self.zoneTemp, self.zoneUpTarget))
                        self.gpio.output('fermCool', 0)
                        self._gpioFermCool = False
                        self.fridgeCompressorDelay = 300
                        self.fridgeHeat = True

                if self.fridgeHeat:
                    sys.stderr.write("ferm heat turned on\n")
                    self.gpio.output('fermHeat', 1)

                    self._gpioFermHeat = True
                    self.lcdDisplay.sendMessage(" Heating", 2)
                    if self.fermHeatActiveFor == -1:
                        self.fermHeatActiveFor = time.time()


#					print self.zoneTemp,self.zoneDownTarget,self.zoneUpTarget,self.fridgeCool,self.fridgeHeat
                if self.zoneTemp > self.zoneDownTarget and not self.fridgeCool:
                    if os.path.exists("ipc/disable-fermcool"):
                        pass
                    else:
                        self._log("Cooling Required %s > %s" % (self.zoneTemp, self.zoneDownTarget))
                        self.gpio.output('fermHeat', 0)
                        self._gpioFermHeat = False
                        self.fridgeCool = True

                if self.fridgeCool:
                    if self.fridgeCompressorDelay > 0:
                        self.lcdDisplay.sendMessage(" %s - Fridge Delay" % (self.fridgeCompressorDelay), 2)
                        sys.stderr.write("Fridge Compressor Delay\n")
#							self._log("Compressor Delay %s\n" %(self.fridgeCompressorDelay))
                        self.gpio.output('fermCool', 0)
                        self._gpioFermCool = False
                    else:
                        if (time.time() - self.fermCoolActiveFor > 1800) and self.fermCoolActiveFor > 0:
                            self.fridgeCompressorDelay = 601
                            self._log("Cooling has been active for %s - resting fridge" % (time.time() - self.fermCoolActiveFor))
                            if self.fermCoolActiveFor > 0:
                                self.meterFermC = self.meterFermC + (time.time() - self.fermCoolActiveFor)
                            self._log("Cooling total active time %s" % (self.meterFermC))
                            self.fermCoolActiveFor = -1
                            self._gpioFermCool = False
                            sys.stderr.write("Fridge turned off\n")
                            self.gpio.output('fermCool', 0)
                        else:
                            self.lcdDisplay.sendMessage(" Cooling", 2)
                            self._gpioFermCool = True
                            sys.stderr.write("Fridge turned on\n")
                            self.gpio.output('fermCool', 1)
                            if self.fermCoolActiveFor == -1:
                                self.fermCoolActiveFor = time.time()

                if self.fridgeHeat and self.zoneTemp > self.zoneTarget - 0.05:
                    self._log("Target Reached stopping heat active for %s" % (time.time() - self.fermHeatActiveFor))
                    self.fridgeHeat = False

                    self.gpio.output('fermHeat', 0)
                    self.gpio.output('fermCool', 0)
                    self._gpioFermHeat = False
                    self.fridgeCompressorDelay = 301
                    if self.fermCoolActiveFor > 0:
                        self.meterFermC = self.meterFermC + (time.time() - self.fermCoolActiveFor)
                    self._log("Cooling total active time %s" % (self.meterFermC))
                    self.fermCoolActiveFor = -1
                    self.meterFermH = self.meterFermH + (time.time() - self.fermHeatActiveFor)
                    if self.fermHeatActiveFor > 0:
                        self._log("Heating total active time %s" % (self.meterFermH))
                    self.fermHeatActiveFor = -1

                if self.fridgeCool and self.zoneTemp < self.zoneTarget + 0.05:
                    self._log("Target Reached stopping cooling active for %s" % (time.time() - self.fermCoolActiveFor))
                    self.fridgeCool = False
                    self.gpio.output("fermCool", 0)
                    self.gpio.output("fermHeat", 0)
                    self.fridgeCompressorDelay = 301
                    self._gpioFermCool = False
                    if self.fermCoolActiveFor > 0:
                        self.meterFermC = self.meterFermC + (time.time() - self.fermCoolActiveFor)
                    self._log("Cooling total active time %s" % (self.meterFermC))
                    self.fermCoolActiveFor = -1
                    if self.fermHeatActiveFor > 0:
                        self.meterFermH = self.meterFermH + (time.time() - self.fermHeatActiveFor)
                    self._log("Heating total active time %s" % (self.meterFermH))
                    self.fermHeatActiveFor = -1

                self.fridgeCompressorDelay = self.fridgeCompressorDelay - 1

            # if we are heating or cooling turn on the reircfan
            # this means we can switch the reircfan for a fan
            if self.fridgeCool and self.fridgeCompressorDelay < 1:
                self.gpio.output('reircfan', 1)
                self._gpioreircfan = True
            elif self.fridgeHeat:
                print "reircfan SHOULD BE ON"
                self.gpio.output('reircfan', 1)
                self._gpioreircfan = True
            elif not self.fridgeCool and not self.fridgeHeat:
                self.gpio.output('reircfan', 0)
                self._gpioreircfan = False

        elif self._mode.count("reircfan"):
            self.gpio.output('reircfan', 1)
            self._gpioreircfan = True


    def broadcastResult(self):
        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
        controlMessage = {}
        controlMessage['_operation'] = 'relay'
        controlMessage['_checksum'] = "                                        "

        checksum = "%s%s" % (controlMessage, self.cfg.checksum)
        controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

        while 1:
            controlMessage['gpioreircfan'] = self._gpioreircfan
            controlMessage['gpioExtractor'] = self._gpioExtractor
            controlMessage['gpioFermCool'] = self._gpioFermCool
            controlMessage['gpioFermHeat'] = self._gpioFermHeat
            msg = json.dumps(controlMessage)
            msg = "%s%s" % (msg, " " * (1200 - len(msg)))
            sendSocket.sendto(msg, (self.cfg.mcastGroup, self.cfg.mcastRelayPort))
            time.sleep(1)


if __name__ == '__main__':
    try:
        controller = pitmRelay()

        #
        broadcastResult = threading.Thread(target=controller.broadcastResult)
        broadcastResult.daemon = True
        broadcastResult.start()

        # get under the control of the contoller
        controlThread = threading.Thread(target=controller.submission)
        controlThread.daemon = True
        controlThread.start()

        # get temperature status from zone a
        zoneTempThread = threading.Thread(target=controller.zoneTempThread)
        zoneTempThread.daemon = True
        zoneTempThread.start()

#		# start a relay thread
        zoneRelayThread = threading.Thread(target=controller.zoneThread)
        zoneRelayThread.daemon = True
        zoneRelayThread.start()

        while 1:
            time.sleep(1)

    except KeyboardInterrupt:
        controller.uncontrol()
        pass
