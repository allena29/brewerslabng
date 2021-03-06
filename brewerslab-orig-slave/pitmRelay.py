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
from pitmLogHandler import pitmLogHandler
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
        Enable power to Zone A (pitmSsrRelay)
        Enable power to Zone B (pitmSsrRelay)
        Toggle Zone A use  ** ONE OF THESE RELAYS IS BROKEN **
        Toggle Zone B use

    """

    def __init__(self, rpi=True):
        self.cfg = pitmCfg()
        self.groot = pitmLogHandler()

        self.fermCoolActiveFor = -1
        self.fermHeatActiveFor = -1

        self.fridgeCompressorDelay = 120
        self.fridgeCool = False
        self.fridgeHeat = False

        # Count how long we have been active for
        self.meterFermH = 0
        self.meterFermC = 0

        self._lastValidReading = {'ferm': -1}

        self.mcastMembership = False

        self.zoneTemp = -1
        self.zoneTarget = -1
        self.zoneTempTimestamp = -1
        self.zoneUpTarget = -1
        self.zoneDownTarget = -1

        self._mode = "UNKNOWN"
        self.cycle = 4

        self.recircfanCount = 0

        self._gpioFermCool = None
        self._gpioFermHeat = None
        self._gpiorecircfan = None
        self._gpioExtractor = None

        if rpi:
            self.gpio = gpiotools()
            self.lcdDisplay = pitmLCDisplay()
            self.gpio.output("fermCool", 0)
            self.gpio.output('recircfan', 0)
            self.gpio.output('extractor', 0)
            self.gpio.output("fermHeat", 0)

    def __del__(self):
        self._mode = "shutdown"
        self.gpio.output('fermHeat', 0)
        self.gpio.output('fermCool', 0)
        self.gpio.output('recircfan', 0)
        self.gpio.output('extractor', 0)

    def uncontrol(self):
        self.groot.log("Uncontrol Called")
        self._mode = "shutdown"
        self.gpio.output('fermHeat', 0)
        self.gpio.output('fermCool', 0)
        self.gpio.output('recircfan', 0)
        self.gpio.output('extractor', 0)

    def submission(self):
        self.groot.log("Submitting to control of Controller")
        if os.path.exists('ipc/overrideModeFerm'):
            self._mode = 'ferm'
            return

        mcast_handler = pitmMcast()
        mcast_handler.open_socket(self.callback_set_mode, self.cfg.mcastPort)

    def callback_set_mode(self, cm):
        if cm.has_key('_mode'):
            self._mode = cm['_mode']

    def zoneTempThread(self):
        self.groot.log("Listening for temperature'")
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
                    self.groot.log("Temp: %s Target: %s(>%s <%s) fridgeHeat: %s/%s fridgeCool: %s/%s (delay %s) " % (self.zoneTemp, self.zoneTarget, self.zoneUpTarget, self.zoneDownTarget,
                                                                                                            self.fridgeHeat, self._gpioFermHeat, self.fridgeCool, self._gpioFermCool, delay), importance=0)
                else:
                    self.lcdDisplay.sendMessage("Temp Result Error", 2)

        if cm.has_key("tempTargetFerm"):
            # zoneDownTarget when we need to start cooling
            # zoneUpTarget when we need to start heating
            # zoneTarget when we need to stop cooling/heating
            (self_zoneUpTarget, self_zoneDownTarget, self_zoneTarget) = cm['tempTargetFerm']
            if self_zoneUpTarget < 5 or self_zoneDownTarget < 5 or self_zoneTarget < 5:
                self.groot.log("Temp Target is invalid %s,%s,%s" % (cm['tempTargetFerm'][0], cm['tempTargetFerm'][1], cm['tempTargetFerm'][2]), importance=2)
            else:
                (self.zoneUpTarget, self.zoneDownTarget, self.zoneTarget) = cm['tempTargetFerm']

    def _zone_idle_shutdown(self):
        self.fridgeCompressorDelay = 301
        self.gpio.output("fermCool", 0)
        self.gpio.output('recircfan', 0)
        self.gpio.output('extractor', 0)
        self.gpio.output("fermHeat", 0)
        self._gpioFermCool = False
        self._gpioFermHeat = False
        self._gpiorecircfan = False
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
            self.groot.log("Critical: no valid readings for 100 seconds")
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
            self.groot.log("Unrealistic Temperature Value %s:%s %s\n" % (self.zoneTemp, self.zoneTempTimestamp, self._mode))
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
            self.groot.log("Cooling has been active for %s - resting fridge" % (time.time() - self.fermCoolActiveFor))
            self._turn_cooling_off()
            # we have a longer sleep if getting turn off because of long running
            self.fridgeCompressorDelay = 601 
            return True

        return False

    def _is_heating_required(self):
        if os.path.exists("ipc/disable-ferm-heat"):
            return False
        if self.zoneTemp < self.zoneUpTarget and not self.fridgeHeat:
            self.groot.log("Heating Requied %s < %s" % (self.zoneTemp, self.zoneUpTarget))
            return True

        return False

    def _turn_cooling_off(self):
        self.gpio.output('fermCool', 0)
        self._gpioFermCool = False
        self.fridgeCool = False
        if self.fridgeCompressorDelay < 1:
            self.fridgeCompressorDelay = 300
        if self.fermCoolActiveFor > 0:
            self.meterFermC = self.meterFermC + (time.time() - self.fermCoolActiveFor)
            self.groot.log("Cooling total active time %s" % (self.meterFermC))
            self.fermCoolActiveFor = -1

    def _turn_cooling_on(self):
        """
        Important safety checks for compressor must be called before this
        """
        self.lcdDisplay.sendMessage(" Cooling", 2)
        self._gpioFermCool = True
        self.gpio.output('fermCool', 1)
	self.fridgeCool = True
        if self.fermCoolActiveFor == -1:
            self.fermCoolActiveFor = time.time()

    def _turn_heating_on(self):
        self.fridgeHeat = True
	self._gpioFermHeat = True
        self.gpio.output('fermHeat', 1)

        self.lcdDisplay.sendMessage(" Heating", 2)
        if self.fermHeatActiveFor == -1:
            self.fermHeatActiveFor = time.time()

    def _turn_heating_off(self):
        self.fridgeHeat = False
        self.gpio.output('fermHeat', 0)
        self._gpioFermHeat = False
        if self.fermHeatActiveFor > 0:
            self.meterFermH = self.meterFermH + (time.time() - self.fermHeatActiveFor)
            if self.fermHeatActiveFor > 0:
                self.groot.log("Heating total active time %s" % (self.meterFermH))
            self.fermHeatActiveFor = -1

    def _turn_recirc_fan_on(self):
        self.gpio.output('recircfan', 1)

    def _turn_recirc_fan_off(self):
        self.gpio.output('recircfan', 0)

    def _is_cooling_required(self):
        if os.path.exists("ipc/disable-fermcool"):
            return False

        if self.zoneTemp > self.zoneDownTarget:
            self.groot.log("Cooling Required %s > %s" % (self.zoneTemp, self.zoneDownTarget))
            return True

        return False

    def _zone_ferm(self):
        self.fridgeCompressorDelay = self.fridgeCompressorDelay - 1
        safety_check_ok = self._safety_check_for_missing_readings()
        if not safety_check_ok:
            self.groot.log("Unrealistic readings!")
            # Cannot continue because we have no valid reading
            return

        unrealistic_values_check_ok = self._safety_check_for_unrealistic_readings()
        if not unrealistic_values_check_ok:
            return

        if not self.fridgeHeat and not self.fridgeCool:
            self.lcdDisplay.sendMessage("", 2)

        if os.path.exists("ipc/no-ferm-control"):
            self._disable_ferm_control()

        if self._gpiorecircfan == None:
            self.gpio.output('recircfan', 0)
            self._gpiorecircfan = False
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


        if self.fridgeHeat and self.zoneTemp > self.zoneTarget - 0.15:
            self.groot.log("Target Reached stopping heat active for %s" % (time.time() - self.fermHeatActiveFor))
            self._turn_cooling_off()
            self._turn_heating_off()
            self._turn_recirc_fan_off()

        if self.fridgeCool and self.zoneTemp < self.zoneTarget + 0.15:
            self.groot.log("Target Reached stopping cooling active for %s" % (time.time() - self.fermCoolActiveFor))
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
        mcast_handler = pitmMcast()

        while 1:
            controlMessage = {}
            controlMessage['gpiorecircfan'] = self._gpiorecircfan
            controlMessage['gpioExtractor'] = self._gpioExtractor
            controlMessage['gpioFermCool'] = self._gpioFermCool
            controlMessage['gpioFermHeat'] = self._gpioFermHeat

            mcast_handler.send_mcast_message(controlMessage, self.cfg.mcastRelayPort, 'relay')

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
