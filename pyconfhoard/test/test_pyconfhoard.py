import unittest
import json
import sys
import dpath.util
sys.path.append('test')
from PyConfHoard import Data, Thing
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf, PyConfHoardDataPathDoesNotExist


class TestYang(unittest.TestCase):
    def setUp(self):
        self.subject = Data('test/schema-config.json', 'test/schema-oper.json')
        self.subject.register('/tupperware')
        self.subject.register('/simplelist')

    def test_create_thing_one(self):

        print('********')
        print(self.subject.config.db, 'root instance')
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
        #iself.subject.register('/tupperware', self.thing1.config, self.thing1.oper)

    def test_list(self):
        self.subject.list('tupperware')
        try:
            self.subject.list('carboard')
            self.fail('PyConfHoardDataPathDoesNotExist should have been thrown because we tried to access a non-existant path')
        except PyConfHoardDataPathDoesNotExist as err:
            pass
