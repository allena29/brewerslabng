#!/usr/bin/python

import os
import sys
import threading
import time

from pitmMcastOperations import pitmMcast
from pitmLogHandler import pitmLogHandler
from gpiotools2 import gpiotools2
from pitmCfg import pitmCfg


class pitmButton:

    """
    pitmButton manages the toggling of mode switches.

    These switches may be
     - Physcial, which are read from GPIO
     - or fake buttons (ipc/manualswitch_<NAME>

    In both cases if a physical button is on or the fakebutton is set
    the status is written to an ipc/<NAME> file and broadcast via multicast
    """

    def __init__(self, rpi=True):
        self.cfg = pitmCfg()
        self.groot = pitmLogHandler()

        if rpi:
            self.gpio = gpiotools2()
            self.doMonitoring = False


    def _check_a_single_button(self, button):
        if os.path.exists('ipc/manualswitch_%s' % (button)):
            return True
        return self.gpio.input(button)

    def _set_ipc_flag(self, button):
        o = open("ipc/%s" % (button), "w")
        o.close()

    def _remove_ipc_flag(self, button):
        try:
            os.remove("ipc/%s" % (button))
        except:
            pass

    def _build_button_control_message(self):
        controlMessage = {}
        controlMessage['_operation'] = 'button'
        controlMessage['_checksum'] = "                                        "
        controlMessage['_button'] = {}
        for button in ['swHlt', 'swFerm', 'swSparge', 'swMash', 'swBoil', 'swPump']:
            button_state = self._check_a_single_button(button)

            if button_state:
                self._set_ipc_flag(button)
            else:
                self._remove_ipc_flag(button)
            controlMessage['_button'][button] = button_state
             
        return controlMessage


    def broadcastButtonResult(self):
        print "advertising our Button  capabiltiies"
        mcastHandler = pitmMcast()

        while 1:
            controlMessage = self._build_button_control_message()
            mcastHandler.send_mcast_message(controlMessage, self.cfg.mcastButtonPort, 'button')
            time.sleep(1)


if __name__ == '__main__':
    buttonController = pitmButton()
    broadcastResult = threading.Thread(target=buttonController.broadcastButtonResult)
    broadcastResult.daemon = True
    broadcastResult.start()

    while 1:
        time.sleep(5)
