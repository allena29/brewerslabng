#!/usr/bin/python

import time
import requests
import blng.Subscriber as Subscriber

"""
This class is intended to take the broadcasted results on the Multicast stream
and publish it into an Influx Database which can then be picked up from an Influx
database.
"""


class PublishFermChamberToInflux(Subscriber.Subscriber):

    MCAST_PORT = 5082
    LOG_COMPONENT = 'FermChamber2Influx'
    # TODO: move the URL for influx db to netconf config store
    INFLUX_URL = 'http://127.0.0.1:8086/write?db=beerstats'

    def init(self):
        self.log.debug('Intialised to publish ferm chamber status to %s' % (self.INFLUX_URL))

    def persist_data(self, msg_dict):
        timestamp = int(time.time() * 1000000000)
        data_string = "fermchamber,host=%s value=%s %s" % (self.ID, msg_dict['value'], timestamp)
        r = requests.post(self.INFLUX_URL, data=data_string, timeout=(0.5, 1))
#        r.status_code = 204 NO_CONTNET
  #      print(r.status_code)

    def multicast_receive_callback(self, cm):
        value = 0
        if cm['gpioFermHeat']:
            value = 1
        if cm['gpioFermCool']:
            value = -1

        msg_dict = {}
        msg_dict['value'] = value
        try:
            self.persist_data(msg_dict)
            self.log.debug('Persist %s' % (msg_dict))
        except Exception as err:
            self.log.err('Dropping %s' % (msg_dict))
            self.log.err('  %s' % (str(err)))


if __name__ == '__main__':
    publisher = PublishFermChamberToInflux()
    publisher.subscribe()
