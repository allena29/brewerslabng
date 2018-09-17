#!/usr/bin/python

import blng.Multicast as Multicast
import blng.LogHandler as LogHandler


class Common:

    def __init__(self):
        if not hasattr(self, 'ID'):
            # TODO: pick up ID from os.environ
            self.ID = "shjips"

        if hasattr(self, 'LOG_COMPONENT'):
            self.log = LogHandler.LogHandler(self.LOG_COMPONENT)

        if hasattr(self, 'init') and callable(getattr(self, 'init')):
            sub_init = getattr(self, 'init')
            sub_init()
