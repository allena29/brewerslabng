#!/usr/bin/python

import blng.Common


class BroadcastISpindelGravity(blng.Common.Common):

    """
    This class will run an lightweight web-server to allow the iSpindel to connect
    via it's Generic HTTP method. The iSpindel must be configured with the IP
    address and HTTP_PORT of this server.

    Each time a result is received it will be processed and broadcast via a 1200
    byte JSON string on Multicast group, by default  232.239.168.250 port 5092
    """


    MCAST_PORT = 5092
    HTTP_PORT = 9501
    LOG_COMPONENT = 'BroadcastISpindel'

    def init(self):
        self.log.debug('Intialised to broadcast iSpindel Stats')


    def http_callback_post(self, path, json):
        """
        This method is invoked as a callback from the inherited subscriber class which
        will invoked every time there is 1200 bytes of temperature.

        TODO: we need to convert probeId mappings into Netconf datastore - not read from config file.
        TODO: we need to move target temperatures into Netconf datastore - not broadcast from governor
        """
        print ('child do post %s' % (json))


if __name__ == '__main__':
    broadcast = BroadcastISpindelGravity()
    broadcast.http_listen()

