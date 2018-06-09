import unittest
import json
import sys
import dpath.util
sys.path.append('test')
from PyConfHoard import Data, Thing
from PyConfHoardCommon import decode_path_string
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf, PyConfHoardDataPathDoesNotExist, PyConfHoardDataPathNotRegistered


class TestYang(unittest.TestCase):
    def setUp(self):
        self.subject = Data('test/schema-config.json', 'test/schema-oper.json')
        self.subject.register('/tupperware')
        self.subject.register('/simplelist')

    def test_create_thing_one(self):

        print('********')
        print(self.subject.config.db, 'root instance')
        print(self.subject.config.db['root'])
        print(self.subject.config.db['root']['tupperware'], 'tupperware')
        print(self.subject.config.db['root']['simplelist'], 'simplelist')
        print(self.subject.config.db)
        # So far we should be able to merge things like this
        # to have one view over lots of pyconfhoard datastore instances

        x=self.subject.config.db['root']['tupperware']
        x.set('/root/tupperware/config', 'plastic', separator='/')
        print(x)
        print(x.keyval)
        print('********')
        self.assertFalse(self.subject.config.db is self.subject.config.db['root']['tupperware'])
        #iself.subject.register('/tupperware', self.thing1.config, self.thing1.oper)

    def test_list(self):
        self.subject.list('tupperware')
        try:
            self.subject.list('carboard')
            self.fail('PyConfHoardDataPathDoesNotExist should have been thrown because we tried to access a non-existant path')
        except PyConfHoardDataPathDoesNotExist as err:
            pass

    def test_get_and_set(self):
        try:
            self.subject.set('/x123123123', 'this')
            self.fail('We should have had an exception for accessing a non-registered path')
        except PyConfHoardDataPathNotRegistered as err:
            pass

        self.subject.set('/tupperware/config', 'this-value', separator='/')
        result = self.subject.get('/tupperware/config', separator='/')
        self.assertEqual('this-value', result)

    def test_decode_path_string(self):
        result = decode_path_string('/x/1/2/3{abc}', separator='/')
        self.assertEqual(['root', 'x', '1', '2', '3', '{abc}'], result)

        result = decode_path_string('/x/1/2/3{abc}/x{def}', separator='/')
        self.assertEqual(['root', 'x', '1', '2', '3', '{abc}', 'x', '{def}'], result)

    def test_list_create(self):
        self.subject.create('/simplelist', ['crystal'], separator='/')
        self.subject.set('/simplelist{crystal}/val', 'maze', separator='/')
        result = self.subject.get('/simplelist{crystal}/id', separator='/')
        self.assertEqual(result, 'crystal')
        result = self.subject.get('/simplelist{crystal}/val', separator='/')
        self.assertEqual(result, 'maze')
