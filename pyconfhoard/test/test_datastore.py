import unittest
import json
import sys
import dpath.util
sys.path.append('test')
from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf


class TestYang(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema.json')
        self.maxDiff = 10000

    def test_list_completion(self):
        result = self.subject.list('/', separator='/')
        expected_result = ['simplelist', 'simplestleaf']
        self.assertEqual(result, expected_result)

    def test_list_completion_leaf(self):
        result = self.subject.list('/simplelist', separator='/')
        expected_result = ['id', 'val']
        self.assertEqual(result, expected_result)

    def test_get_type(self):
        result = self.subject.get_type('/simplelist', separator='/')
        self.assertEqual(result['__list'], True)

        try:
            result = self.subject.get_type('/', separator='/')
            self.fail('Accessing / should have thrown AccessNonLeaf exception')
        except PyConfHoardAccessNonLeaf:
            pass
        
        
        result = self.subject.get_type('/simplelist{sdfsdfsdf}', separator='/')
        self.assertEqual(result['__path'], '/root/simplelist')

    def test_get_val(self):
        # Retreive a value not yet set should return None
        result = self.subject.get('/simplestleaf', separator='/')
        self.assertEqual(result, None)

    def test_set_val(self):
        set_val = 'sleep'
        self.subject.set('/simplestleaf', set_val, separator='/')
        result = self.subject.get('/simplestleaf', separator='/')
        self.assertEqual(result, set_val)

        try:
            self.subject.set('/simplelist', set_val, separator='/')
            self.fail('Settings /simplelist as a non-config node should throw PyConfHoardNonConfigLeaf exception')
        except PyConfHoardNonConfigLeaf:
            pass

    def test_set_list_element(self):
        list_key_values = ['glow']
        self.subject.create('/simplelist', list_key_values, separator='/')

        print(json.dumps(self.subject.schema, indent=4))
        print(json.dumps(self.subject.db_config, indent=4))
        self.subject.set('/simplelist{glow}/val', 'in the dark', separator='/')

        print(json.dumps(self.subject.db_config, indent=4))
         
