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
        self._gpiorecricfan = None
        self._gpioExtractor = None
        self.gpio.output("fermCool", 0)
        self.gpio.output('recricfan', 0)
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

        self.recricfanCount = 0

        self.ssrFanRequiredUntil = -1

    def __del__(self):
        self._mode = "shutdown"
        self.gpio.output('fermHeat', 0)
        self.gpio.output('fermCool', 0)
        self.gpio.output('recricfan', 0)
        self.gpio.output('extractor', 0)
        self.gpio.output('zoneA', 0)
        self.gpio.output('zoneB', 0)
        self.gpio.output('tSsrFan', 0)

    def uncontrol(self):
        self._log("Uncontrol Called")
        self._mode = "shutdown"
        self.gpio.output('fermHeat', 0)
        self.gpio.output('fermCool', 0)
        self.gpio.output('recricfan', 0)
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
            self.gpio.output('recricfan', 0)
            self.gpio.output('extractor', 0)
            self.gpio.output("fermHeat", 0)
            self._gpioFermCool = False
            self._gpioFermHeat = False
            self._gpiorecricfan = False
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

    def _disable_ferm_control(self):
        self._turn_cooling_off()
        self._turn_heating_off()


    def _safety_check_for_missing_readings(self):
        if self._lastValidReading['ferm'] + 100 < time.time():
            self._log("Critical: no valid readings for 100 seconds")
            self.gpio.output('fermHeat', 0)
            self._gpioFermCool = False
            self._gpioFermHeat = False
            self.lcdDisplay.sendMessage("CRITICAL Temp Result Error", 2)
            self.gpio.output('fermCool', 0)
            self.gpio.output('recircfan', 0)
            self.fridgeCompressorDelay = 300
            return False

        return True

    def _safety_check_for_unrealistic_readings(self):
        if self.zoneTemp > 75 or self.zoneTemp < 4:
            self._log("Unrealistic Temperature Value %s:%s %s\n" % (self.zoneTemp, self.zoneTempTimestamp, self._mode))
            return False
        return True

    def _safety_check_will_starting_the_fridge_damage_the_compressor(self):
        if self.fridgeCompressorDelay > 0:
            self.lcdDisplay.sendMessage(" %s - Fridge Delay" % (self.fridgeCompressorDelay), 2)
            self._turn_cooling_off()
            return True

        return False

    def _safety_check_has_fridge_been_running_too_long_if_so_turn_off(self):
        if (time.time() - self.fermCoolActiveFor > 1800) and self.fermCoolActiveFor > 0:
            self._log("Cooling has been active for %s - resting fridge" % (time.time() - self.fermCoolActiveFor))
            self._turn_cooling_off()
            # we have a longer sleep if getting turn off because of long running
            self.fridgeCompressorDelay = 601
            return True

        return False

    def _is_heating_required(self):
        if os.path.exists("ipc/disable-ferm-heat"):
            return False

        if self.zoneTemp < self.zoneUpTarget and not self.fridgeHeat:
            self._log("Heating Requied %s < %s" % (self.zoneTemp, self.zoneUpTarget))
            return True

        return False

    def _turn_cooling_off(self):
        self.gpio.output('fermCool', 0)
        self._gpioFermCool = False
        if self.fridgeCompressorDelay < 1:
		self.fridgeCompressorDelay = 300
        if self.fermCoolActiveFor > 0:
            self.meterFermC = self.meterFermC + (time.time() - self.fermCoolActiveFor)
            self._log("Cooling total active time %s" % (self.meterFermC))
            self.fermCoolActiveFor = -1

    def _turn_cooling_on(self):
        """
        Important safety checks for compressor must be called before this
        """

        self.lcdDisplay.sendMessage(" Cooling", 2)
        self._gpioFermCool = True
        self.gpio.output('fermCool', 1)
        if self.fermCoolActiveFor == -1:
            self.fermCoolActiveFor = time.time()


    def _turn_heating_on(self):
        self.fridgeHeat = True
        self.gpio.output('fermHeat', 1)

        self.lcdDisplay.sendMessage(" Heating", 2)
        if self.fermHeatActiveFor == -1:
            self.fermHeatActiveFor = time.time()


    def _turn_heating_off(self):
        self.fridgeHeat = False
        self.gpio.output('fermHeat', 0)
        if self.fermHeatActiveFor > 0:
            self.meterFermH = self.meterFermH + (time.time() - self.fermHeatActiveFor)
            if self.fermHeatActiveFor > 0:
                self._log("Heating total active time %s" % (self.meterFermH))
            self.fermHeatActiveFor = -1

    def _turn_recirc_fan_on(self):
        self.gpio.output('recircfan', 1)

    def _turn_recirc_fan_off(self):
        self.gpio.output('recircfan', 0)

    def _is_cooling_required(self):
        if os.path.exists("ipc/disable-fermcool"):
            return False

        if self.zoneTemp > self.zoneDownTarget and not self.fridgeCool:
            self._log("Cooling Required %s > %s" % (self.zoneTemp, self.zoneDownTarget))
            return True

        return False

    def _zone_ferm(self):
        self.fridgeCompressorDelay = self.fridgeCompressorDelay - 1

	print self.fridgeCompressorDelay

        safety_check_ok = self._safety_check_for_missing_readings()
        if not safety_check_ok:
            # Cannot continue because we have no valid reading
            return

        unrealistic_values_check_ok = self._safety_check_for_unrealistic_readings()
        if not unrealistic_values_check_ok:
            return

        if not self.fridgeHeat and not self.fridgeCool:
            self.lcdDisplay.sendMessage("", 2)

        if os.path.exists("ipc/no-ferm-control"):
            self._disable_ferm_control()


        if self._gpiorecricfan == None:
            self.gpio.output('recricfan', 0)
            self._gpiorecricfan = False
        if self._gpioExtractor == None:
            self.gpio.output('extractor', 0)
            self._gpioExtractor = False


        self._lastValidReading['ferm'] = time.time()
#					self.lcdDisplay.sendMessage(" - Target %sC" %(self.zoneTarget),1)

        heating_required = self._is_heating_required()
        cooling_required = self._is_cooling_required()
    
        if heating_required:
            self._turn_cooling_off()
            self._turn_heating_on()
            self._turn_recirc_fan_on()


        elif cooling_required:
            self._turn_heating_off()
            if self._safety_check_will_starting_the_fridge_damage_the_compressor():
                self._turn_recirc_fan_off()
            elif self._safety_check_has_fridge_been_running_too_long_if_so_turn_off():
                self._turn_recirc_fan_off()
            else:
                self._turn_recirc_fan_on()
                self._turn_cooling_on()


        if self.fridgeHeat and self.zoneTemp > self.zoneTarget:
            self._log("Target Reached stopping heat active for %s" % (time.time() - self.fermHeatActiveFor))
            self._turn_cooling_off()
            self._turn_heating_off()
            self._turn_recirc_fan_off()

        if self.fridgeCool and self.zoneTemp < self.zoneTarget:
            self._log("Target Reached stopping cooling active for %s" % (time.time() - self.fermCoolActiveFor))
            self._turn_cooling_off()
            self._turn_heating_off()
            self._turn_recirc_fan_off()



    def _do_zone_thread(self):
        if self._mode == "idle" or self._mode == "shutdown":
            self._zone_idle_shutdown()
        elif self._mode.count("boil"):
            self._zone_boil()
        elif self._mode == "ferm":
            if self._lastValidReading['ferm'] == -1:
               self._lastValidReading['ferm'] = time.time()
            self._zone_ferm()


    def broadcastResult(self):
        sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sendSocket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
        controlMessage = {}
        controlMessage['_operation'] = 'relay'
        controlMessage['_checksum'] = "                                        "

        checksum = "%s%s" % (controlMessage, self.cfg.checksum)
        controlMessage['_checksum'] = hashlib.sha1(self.cfg.checksum).hexdigest()

        while 1:
            controlMessage['gpiorecricfan'] = self._gpiorecricfan
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
