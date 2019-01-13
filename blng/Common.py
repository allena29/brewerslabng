#!/usr/bin/python

import time
import blng.LogHandler as LogHandler
import blng.Multicast as Multicast
import blng.Http as Http
import blng.Tcp as Tcp
import subprocess


def shell_command(command):
    process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    (output, error) = process.communicate(command.encode('utf-8'))
    return (output, error)


class Common:

    MCAST_PORT = 4999
    HTTP_PORT = 4998
    HTTP_LISTEN_PORT = 4997
    TCP_PORT = 4996
    LOG_COMPONENT = 'DummyComponent'

    def __init__(self):
        self.__mcastreceiver = None
        self.__mcastsender = None
        self.__httpreceiver = None
        self.__tcpreceeiver = None

        if not hasattr(self, 'ID'):
            # TODO: pick up ID from os.environ
            self.ID = "shjips"

        if hasattr(self, 'LOG_COMPONENT'):
            self.log = LogHandler.LogHandler(self.LOG_COMPONENT)

        if hasattr(self, 'init') and callable(getattr(self, 'init')):
            sub_init = getattr(self, 'init')
            sub_init()

    def broadcast(self, msg):
        """
        Boaddcast multicast data
        """
        if not self.__mcastsender:
            self.__mcastsender = Multicast.Multicast(self.MCAST_PORT, self.LOG_COMPONENT)
        self.__mcastsender.send_mcast_message(msg, self.MCAST_PORT, self.LOG_COMPONENT)

    def subscribe(self):
        """
        Subscribe to receive data, each time a valid 1200byte payload is received we will
        invoke the callback passing in a JSON decoded object.
        """
        if hasattr(self, '__mcastsocket'):
            # TODO: do something to unsubscribe irst
            pass

        self.__mcastreceiver = Multicast.Multicast(self.LOG_COMPONENT)
        try:
            self.__mcastsocket = self.__mcastreceiver.open_socket(self.multicast_receive_callback, self.MCAST_PORT)
        except KeyboardInterrupt:
            pass

    def multicast_receive_callback(self, xxx):
        print('override multicast_receive_callback - not re-implemented in child class')

    def http_callback_post(self, path, post):
        print('http_callback_post not defined in child class')

    def http_callback_get(self, path):
        print('http_callback_get not defined in child class')

    def tcp_callback(self):
        print('tcp_callback not defined in child class')

    def tcp_listen(self):
        self.__tcpreceiver = Tcp.Tcp(self.TCP_PORT, self.LOG_COMPONENT)
        try:
            self.__tcpreceiver.tcp_callback = self.tcp_callback
            self.__tcpreceiver.serve()
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def http_listen(self):
        self.__httpreceiver = Http.Http(self.HTTP_PORT, self.LOG_COMPONENT)
        try:
            self.__httpreceiver.serve()
            self.__httpreceiver.http_callback_post = self.http_callback_post
            self.__httpreceiver.http_callback_get = self.http_callback_get
            while 1:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        self.__httpreceiver.end_serve()
