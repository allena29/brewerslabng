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


def send_cli(cli_to_send):
    a=2
#
#
##  GENERIC
#
#


@given("we have started {thing}")
def step_impl(context, thing):
    context.things[thing] = thread_thing(thing)
    context.things[thing].start()
    while context.things[thing].started is False:
        time.sleep(0.5)

@when("we send the following CLI")
def step_impl(context):
    send_cli(context.text)

#
#
##  MASH 
#
#

@given("We set the HLT temperature for the mash to 69.0 degC")
def step_impl(context):
    pass
