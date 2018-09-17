from __future__ import division
#!/usr/bin/python

# piTempLedFlasher
import socket
import json
import os
import hashlib
import requests
import struct
import socket
import syslog
import sys
import threading
import time
import blng.Subscriber as Subscriber

"""
This class is intended to take the broadcasted results on the Multicast stream
and publish it into an Influx Database which can then be picked up from an Influx
database.
"""


class PublishTemperatureToInflux(Subscriber.Subscriber):

    LOG_COMPONENT = 'Temperature2Influx'
    # TODO: move the URL for influx db to netconf config store
    INFLUX_URL = 'http://192.168.3.6:8086/write?db=temperatures'

    def init(self):
        self.log.debug('Intialised to publish temperature to %s' % (self.INFLUX_URL))
        self.lastmode = ""
        self.last_reading = {}

    def _check_message_is_valid(self, probe, cm):
        keys_we_require = ['currentResult']
        for key in keys_we_require:
            if key not in cm:
                print('%s not available in cm\n%s' % (key, cm))
                return False

        keys_we_require = ['timestamp', 'valid', 'temperature']
        for key in keys_we_require:
            if key not in cm['currentResult'][probe]:
                print('%s not available in currentResult\n%s' % (key, cm['currentResult']))
                return False

        keys_we_require = ['tempTargetMash', 'tempTargetHlt', 'tempTargetBoil', 'tempTargetFerm']
        for key in keys_we_require:
            if key not in cm:
                print('%s not available in currentResult[probe]\n%s' % (key, cm['currentResult'][probe]))
                return False

        if self._have_we_seen_this_result_before(probe, cm['currentResult'][probe]):
            return False

        return 'valid' in cm['currentResult'][probe]

    def _have_we_seen_this_result_before(self, probe, current_result):
        if probe not in self.last_reading:
            self.last_reading[probe] = 0
        return current_result['timestamp'] <= self.last_reading[probe]

    def persist_data(self, msg_dict):
        """"
+  65         TODO: we need to convert probeId mappings into Netconf datastore - not read from config file.
+  66         TODO: we need to move target temperatures into Netconf datastore - not broadcast from governor
i
0
down vote
import requests

url_string = 'http://localhost:8086/write?db=mydb'
data_string = 'cpu_load_short,host=server01,region=us-west value=0.64 1434055562000000000'

r = requests.post(url_string, data=data_string)
        """
        timestamp = int(time.time() * 1000000000)
        data_string = "ferm,host=%s value=%s %s" % (self.ID, msg_dict['ferm'], timestamp)
        r = requests.post(self.INFLUX_URL, data=data_string, timeout=(0.5, 1))
        # r.status_code = 204 NO_CONTNET
        print(r.status_code)

    def multicast_receive_callback(self, cm):
        """
        This method is invoked as a callback from the inherited subscriber class which
        will invoked every time there is 1200 bytes of temperature.

        TODO: we need to convert probeId mappings into Netconf datastore - not read from config file.
        TODO: we need to move target temperatures into Netconf datastore - not broadcast from governor
        """
        doMonitoring = False
        if '_mode' in cm:
            if cm['_mode'].count("delayed_HLT"):
                doMonitoring = True
            if cm['_mode'].count("hlt"):
                doMonitoring = True
            if cm['_mode'] == "sparge":
                doMonitoring = True
            if cm['_mode'].count("mash"):
                doMonitoring = True
            if cm['_mode'].count("boil"):
                doMonitoring = True
            if cm['_mode'].count("pump"):
                doMonitoring = True
            if cm['_mode'].count("cool"):
                doMonitoring = True
            if cm['_mode'].count("ferm"):
                doMonitoring = True
            if not cm['_mode'] == self.lastmode:
                self.lastmode = cm['_mode']

        if doMonitoring:
            for probe in cm['currentResult']:
                if self._check_message_is_valid(probe, cm):
                    self.last_reading[probe] = cm['currentResult'][probe]['timestamp']

                    now = time.localtime()
                    #probeId = self.cfg.probeId[probe]
                    # TODO: add configuration hooks to map configuration - for now hardcoded
                    probeId = 'ferm'
                    print(cm['currentResult'][probe]['temperature'], probeId)

                    if probeId in ['tunA', 'tunB']:
                        target = cm['tempTargetMash']
                    elif probeId == 'hlt':
                        target = cm['tempTargetHlt']
                    else:
                        target = cm['tempTarget%s%s' % (probeId[0].upper(), probeId.replace(' ', '')[1:])]

                    msg_dict = {}
                    msg_dict[probeId] = float(cm['currentResult'][probe]['temperature'])

                    msg_dict['%s_low' % (probeId)] = float(target[0])
                    msg_dict['%s_high' % (probeId)] = float(target[1])
                    msg_dict['%s_target' % (probeId)] = float(target[2])
                    msg_dict["recipe"] = cm['_recipe']

                    try:
                        self.persist_data(msg_dict)
                        self.log.debug('Persist %s' % (msg_dict))
                    except Exception as err:
                        self.log.err('Dropping %s' % (msg_dict))
                        self.log.err('  %s' % (str(err)))


if __name__ == '__main__':
    publisher = PublishTemperatureToInflux()
    publisher.subscribe(5087)
