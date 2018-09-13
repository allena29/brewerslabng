import unittest
import os
import json
from mock import Mock
from cli import PyConfHoardCLI


class TestPyConfHoardCLI(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardCLI(no_networking=True)
        # Manually deal with adding data in without using any files/web
        with open('test/schema-config.json') as c:
            conf_schema = json.loads(c.read())
        with open('test/schema-oper.json') as o:
            oper_schema = json.loads(o.read())
        self.subject.pyconfhoarddata.register_from_data(conf_schema, oper_schema,
                                                        datastores={ 'thing1': {'yangpath': '/root/tupperware', 'appname': 'APPNAME'} })
        self.maxDiff = 10000

    def test_tab_completion_top_level_non_unique_input(self):
        line = 'show tupperware o'
        text = 'o'

        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['outer ', 'outhere '])

    def test_tab_completion_top_level_unique_input(self):
        line = 'show tup'
        text = 'tup'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['tupperware '])

    def test_tab_completion_top_level_wihtout_input(self):
        """ Example:
        2018-06-10 23:42:18,759 - DatastoreFrontend    DEBUG         Data Frontend Instance <PyConfHoard.Data object at 0x104a18fd0>
        2018-06-10 23:42:18,759 - DatastoreFrontend    DEBUG         Configuraton Instance created <PyConfHoardDatastore.PyConfHoardDatastore object at 0x104a274e0>
        2018-06-10 23:42:18,759 - DatastoreFrontend    DEBUG         Operational Instance created <PyConfHoardDatastore.PyConfHoardDatastore object at 0x1056edfd0>
        2018-06-10 23:42:18,760 - DatastoreFrontend    DEBUG         Configuration Path /tupperware instance as <PyConfHoardDatastore.PyConfHoardDatastore object at 0x1056fddd8>
        2018-06-10 23:42:18,760 - DatastoreFrontend    DEBUG         Operational Path /tupperware instance as <PyConfHoardDatastore.PyConfHoardDatastore object at 0x1056fdda0>
        2018-06-10 23:42:18,760 - DatastoreFrontend    TRACE         Using instance <PyConfHoardDatastore.PyConfHoardDatastore object at 0x104a274e0> for list operation
        2018-06-10 23:42:18,760 - DatastoreBackend     TRACE         ['root'] LIST
        """
        line = 'show '
        text = ''
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['complex ', 'simplelist ', 'simplestleaf ', 'stackedlists ', 'tupperware '])

    def test_tab_completion_mid_level_unique_input_for_something_deep(self):
        line = 'show tupperware outer'
        text = ''
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['inner '])

    def test_tab_completion_non_existing_everything(self):
        line = 'show THISDOESNOTEXIST abcdef xyz XXX YYY'
        text = 'YYY'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, [])

    def donttest_tab_completion_create_list(self):
        line = 'create types secondlis'
        text = 'secondlis'
        cmds = self.subject._auto_complete(line, text, cmd='create ')

        self.assertEqual(cmds, ['secondlist '])

    def donttest_create_list_key(self):
        args = 'create types secondlist KEY'
        self.subject._command_create('types secondlist KEY')

        list_item_key = self.subject.datastore.get('types secondlist KEY item')
        self.assertEqual(list_item_key, 'KEY')
