#!/usr/bin/python

import time
import requests
import blng.Common

"""
This class is intended to take the broadcasted results on the Multicast stream
and publish it into an Influx Database which can then be picked up from an Influx
database.
"""


class PublishGravityToInflux(blng.Common.Common):

    MCAST_PORT = 5092
    LOG_COMPONENT = 'Gravity2Influx'
    # TODO: move the URL for influx db to netconf config store
    INFLUX_URL = 'http://127.0.0.1:8086/write?db=beerstats'

    def init(self):
        self.log.debug('Intialised to publish gravity to %s' % (self.INFLUX_URL))
        self.last_reading = 0

    def _check_message_is_valid(self, cm):
        keys_we_require = ['iSpindelCalculatedGravitySpecific', 'iSpindelTemp']
        for key in keys_we_require:
            if key not in cm:
                self.log.error('%s not available in cm\n%s' % (key, cm))
                return False

        if self._have_we_seen_this_result_before(cm):
            return False
        return True

    def _have_we_seen_this_result_before(self, current_result):
        return current_result['timestamp'] <= self.last_reading

    def persist_data(self, msg_dict):
        timestamp = int(time.time() * 1000000000)
        data_string = "fermgravity,host=%s value=%s %s" % (self.ID, msg_dict['iSpindelCalculatedGravitySpecific'], timestamp)
        r = requests.post(self.INFLUX_URL, data=data_string, timeout=(0.5, 1))
        # r.status_code = 204 NO_CONTNET
        print(r.status_code)

    def multicast_receive_callback(self, cm):
        """
        This method is invoked as a callback from the inherited subscriber class which
        will invoked every time there is 1200 bytes of temperature.
        """
        if self._check_message_is_valid(cm):
            self.last_reading = cm['timestamp']
            try:
                self.persist_data(cm)
                self.log.debug('Persist %s' % (cm))
            except Exception as err:
                self.log.err('Dropping %s' % (cm))
                self.log.err('  %s' % (str(err)))


if __name__ == '__main__':
    publisher = PublishGravityToInflux()
    publisher.subscribe()
