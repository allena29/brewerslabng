#!/usr/bin/python3

import libsysrepoPython3 as sr
import sys

class DataProvider:

    def __init__(self, module_name):
        self.module_name = module_name
        self.connect()

    def connect(self):
        self.conn = sr.Connection("provider_%s" %(self.module_name))
        self.session = sr.Session(self.conn)
        self.subscribe = sr.Subscribe(self.session)

        self.subscribe.module_change_subscribe(self.module_name, self.callback)

        sr.global_loop()

    def callback(self):
        sys.stderr.write('Callback has not been over-ridden\n')


