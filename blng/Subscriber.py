#!/usr/bin/python

import blng.Common as Common
import blng.Multicast as Multicast


class Subscriber(Common.Common):

    def subscribe(self, mcastPort):
        if hasattr(self, '__mcastsocket'):
            # TODO: do something to unsubscribe irst
            pass

        self.__mcasthandler = Multicast.Multicast()
        try:
            self.__mcastsocket = self.__mcasthandler.open_socket(self.multicast_receive_callback, mcastPort)
        except KeyboardInterrupt:
            pass

        print('subscribe')

    def multicast_receive_callback(self, xxx):
        print('override multicast_receive_bacllback')
