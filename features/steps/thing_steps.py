from behave import given, when, then, step
import imp
import sys
import pexpect
import threading
import time
import os


class thread_thing(threading.Thread):

    def __init__(self, thing):
        threading.Thread.__init__(self)
        self.thing = thing
        self.started = False
        os.environ['FAKE_DS18B20_RESULT_DIR'] = "/tmp/1wire"
        if not os.path.exists('/tmp/1wire'):
            os.mkdir('/tmp/1wire')

    def run(self):
        sys.path.insert(0, os.getcwd() + '/pyconfhoard')
        os.chdir('things')
        if not os.path.exists(self.thing + '.py'):
            assert False, 'Thing %s does not exist' % (self.thing)
        os.chdir(self.thing.split('/')[0])
        py_mod = imp.load_source(self.thing.split('/')[1], self.thing.split('/')[1] +'.py')
        launcher = getattr(py_mod, 'Launch')
        self.launch = launcher()
        self.started = True
        self.launch.thing.register()
        self.launch.thing.start()
