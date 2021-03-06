import os
import subprocess
import shutil
import tempfile
import time
import threading


class thread_thing(threading.Thread):

    def __init__(self, thing):
        threading.Thread.__init__(self)
        self.thing = thing

    def run(self):
        while 1:
            print (thing,time.ctime())
            time.sleep(1)

class thread_rest_server(threading.Thread):


    def __init__(self, datastore, uid, port):
        threading.Thread.__init__(self)
        self.die = False
        self.uid = uid
        self.port = port
        self.datastore = datastore

    def run(self):
        os.system('gunicorn -b 127.0.0.1:%s --reload pyconfhoard.rest.server TESTHARNESS_%s DATASTORE:%s' % (self.port, self.uid, self.datastore))


def before_all(context):
    context.basedir = os.getcwd()
    context.things = {}
    context.cli = None
    context.cli_last_result = []

    if 'PYCONF_PORT' in os.environ:
        context.port = os.environ['PYCONF_PORT']
    else:
        context.port = 8600

    if 'PYCONF_DATASTORE' in os.environ:
        context.datastore_dir = os.environ['PYCONF_DATASTORE']
    else:
        datastore_dir = tempfile.mkdtemp(dir='/tmp')
        context.datastore_dir = datastore_dir
        context.uid = ('%s' % (context)).split(' ')[-1][:-1]

        
        print('Creating datastore in a temporary directory... %s' % (datastore_dir))
        os.mkdir(datastore_dir + '/running')
        os.mkdir(datastore_dir + '/persist')
        os.mkdir(datastore_dir + '/operational')
        os.mkdir(datastore_dir + '/registered')
        print('Launching Rest Server....')
        context.thread_rest_server = thread_rest_server(context.datastore_dir, context.uid, context.port)
        context.thread_rest_server.start()
        time.sleep(5)


def after_all(context):
    for thing in context.things:
        print ('Stopping thing.... %s' % (thing))
        context.things[thing].launch.thing.DIE = True

    if 'PYCONF_DATASTORE' not in os.environ:
        print('Closing Rest Server....')
        process = subprocess.Popen('/bin/bash', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        commands = "ps -ef | grep TESTHARNESS_%s | grep -v grep" % (context.uid) 
        commands = "kill `%s | awk '{print $2}'`" % (commands)
        (out, err) = process.communicate(commands.encode('UTF-8'))

        print('Removing datastore from temporary directory')
        shutil.rmtree(context.datastore_dir)

def after_scenario(context, scenario):
    if context.cli:
        print('Closing CLI Client')
        context.cli.terminate(force=True)
