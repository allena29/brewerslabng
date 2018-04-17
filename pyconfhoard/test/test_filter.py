import unittest
import json

from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardDatastore import PyConfHoardDataFilter

class TestFilter(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema.json')
        self.maxDiff=10000

    def test_convert_to_pretty(self):
        self.subject.set('simplestleaf', 'abc123')
        self.subject.set('simplecontainer leafstring', 'foobar')

        pretty = PyConfHoardDataFilter()
        pretty.convert(self.subject.db)

        # print (json.dumps(pretty.root, indent=4))

        expected_answer = """{
    "simplestleaf": "abc123",
    "simplecontainer": {
        "leafstring": "foobar"
    },
    "level1": {
        "level2": {
            "level3": {
                "withcfg": {},
                "withoutcfg": {},
                "mixed": {}
            }
        }
    },
    "simplelist": {},
    "types": {
        "secondlist": {
            "innerlist": {}
        },
        "compositekeylist": {}
    }
}"""
    
        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)
