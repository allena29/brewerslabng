#!/usr/bin/python

import json
import time
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
    TCP_PORT = 9501
    LOG_COMPONENT = 'BroadcastISpindel'

    FORMULA_1 = 0.008626076
    FORMULA_2 = 0.439419453
    FORMULA_3 = 4.677151587

    def init(self):
        self.log.debug('Intialised to broadcast iSpindel Stats')

    def convertAngle(self, angle):
        """ Return the angle converted into Plato"""
        return self.FORMULA_1 * angle **2 - self.FORMULA_2 * angle + self.FORMULA_3

    def convertPlatoToSG(self, plato):
        """ Return specific gravity (i.e. 1.xxxx)"""
        return 1 + (plato / (258.6 - ( (plato/258.2) *227.1) ) )

    def tcp_callback(self, data):
        """
        This method is invoked as a callback from the inherited subscriber class which
        will be invoked everytime something connects to send data on the TCP_PORT
        will invoked every time there is 1200 bytes of temperature.

        The data we receive will is JSON-ish 
        {'b'"name":"iSpindel000","ID":14039613,"token":"xxx","angle":42.89461,
         "temperature":16.75,"battery":4.176225,"gravity":3.501669,"interval":600}
        """
        try:
            clean_data = str(data).replace("'b'\"", "\"")[2:-5]
            json_data = json.loads(clean_data)
            msg_dict = {}
            msg_dict['iSpindelTemp'] = float(json_data['temperature'])
            msg_dict['iSpindelTilt'] = float(json_data['angle'])
            msg_dict['iSpindelBattery'] = float(json_data['battery'])
            msg_dict['iSpindelReportedGravityPlato'] = float(json_data['gravity'])
            msg_dict['iSpindelCalculatedGravityPlato'] = self.convertAngle(float(json_data['angle']))
            msg_dict['iSpindelCalculatedGravitySpecific'] = self.convertPlatoToSG(self.convertAngle(float(json_data['angle'])))
            msg_dict['timestamp'] = time.time()

            self.broadcast(msg_dict)
            self.log.info('Gravity %s' % (msg_dict['iSpindelCalculatedGravitySpecific']))
        except Exception as e:
            self.log.error('Unable to decode and broadcast data: %s\n %s' % (str(data), str(e)))


if __name__ == '__main__':
    broadcast = BroadcastISpindelGravity()
    broadcast.tcp_listen()

