import unittest
import json

from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardDatastore import PyConfHoardDataFilter


class TestFilter(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema.json')
        self.maxDiff = 10000

    def test_convert_to_pretty_config_data_without_filter(self):
        self.subject.set('simplestleaf', 'abc123')
        self.subject.set('simplecontainer leafstring', 'foobar')

        pretty = PyConfHoardDataFilter()
        pretty.convert(self.subject.db, config=True, filter_blank_values=False)

        # print (json.dumps(pretty.root, indent=4))

        expected_answer = """{
    "simplestleaf": "abc123",
    "simplecontainer": {
        "leafstring": "foobar"
    },
    "level1": {
        "level2": {
            "level3": {
                "withcfg": {
                    "config": null
                },
                "mixed": {
                    "config": null
                }
            }
        }
    },
    "simplelist": {},
    "types": {
        "number": null,
        "biggernumber": null,
        "bignumber": null,
        "hugenumber": null,
        "secondlist": {},
        "compositekeylist": {}
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def donttest_convert_to_config_filter_blanks_enabled(self):
        self.subject.set('simplestleaf', 'abc123')
        self.subject.set('simplecontainer leafstring', 'foobar')

        pretty = PyConfHoardDataFilter()
        pretty.convert(self.subject.db, config=True, filter_blank_values=True)

        expected_answer = """{
    "simplestleaf": "abc123",
    "simplecontainer": {
        "leafstring": "foobar"
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def donttest_convert_to_operdata_filter_blanks_enabled(self):
        self.subject.set('simplecontainer leafnonconfig', 'foobar1')

        pretty = PyConfHoardDataFilter()
        pretty.convert(self.subject.db, config=False, filter_blank_values=True)

        expected_answer = """{
    "simplecontainer": {
        "leafnonconfig": "foobar1"
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def donttest_convert_to_operdata_filter_blanks_disabled(self):
        self.subject.set('simplecontainer leafnonconfig', 'foobar1')

        pretty = PyConfHoardDataFilter()
        pretty.convert(self.subject.db, config=False, filter_blank_values=False)

        expected_answer = """{
    "simplecontainer": {
        "leafnonconfig": "foobar1"
    },
    "level1": {
        "level2": {
            "level3": {
                "withoutcfg": {
                    "nonconfig": null
                },
                "mixed": {
                    "nonconfig": null
                }
            }
        }
    },
    "simplelist": {}
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def alreadytest_convert_to_operdata_without_collapsing_value(self):
        self.subject.set('simplecontainer leafnonconfig', 'foobar1')
        print (self.subject.db['simplecontainer'])
        pretty = PyConfHoardDataFilter()
        pretty.convert(self.subject.db, config=False, filter_blank_values=True)

        expected_answer = """{
    "simplecontainer": {
        "leafnonconfig": "foobar1"
    }
}"""
        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)
