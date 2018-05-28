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
        self.subject_oper = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema-config.json')
        self.subject_oper.load_blank_schema('test/schema-oper.json')
        self.maxDiff = 10000

    def test_list_completion(self):
        result = self.subject.list('/', separator='/')
        expected_result = ['simplelist', 'simplestleaf', 'tupperware']
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


    def test_set_list_element(self):
        list_key_values = ['glow']
        self.subject.create('/simplelist', list_key_values, separator='/')
        self.subject.set('/simplelist{glow}/val', 'in the dark', separator='/')

    
    def test_dump(self):
        self.test_set_list_element()
        result = self.subject.dump()
        expected_result = """{
    "root": {
        "simplelist": {
            "{glow}": {
                "id": "glow",
                "val": "in the dark"
            }
        }
    }
}"""

        self.assertEqual(result, expected_result)
