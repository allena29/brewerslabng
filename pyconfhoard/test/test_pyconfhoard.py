import unittest
import json
import sys
import dpath.util
sys.path.append('test')
from PyConfHoard import Data, Thing
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf


class TestYang(unittest.TestCase):
    def setUp(self):
        self.subject = Data('test/schema-config.json', 'test/schema-oper.json')

    def test_create_thing_one(self):
        self.subject.register('/tupperware')

        print('********')
        print(self.subject.config.db)
        print(self.subject.config)
        print(self.subject.config.db['root']['tupperware'])
        print(dpath.util.get(self.subject.config.db, '/root/tupperware'))
        print(self.subject.config.db)
        # So far we should be able to merge things like this
        # to have one view over lots of pyconfhoard datastore instances

        x=self.subject.config.db['root']['tupperware']
        x.set('/root/tupperware/config', 'plastic', separator='/')
        print(x)
        print(x.keyval)
        print('********')

        #iself.subject.register('/tupperware', self.thing1.config, self.thing1.oper)

