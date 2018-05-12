import unittest
import json

from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardFilter import PyConfHoardFilter


class TestFilter(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema.json')
        self.maxDiff = 10000

    def donttest_convert_to_pretty_config_data_without_filter(self):
        self.subject.set('simplestleaf', 'abc123')
        self.subject.set('simplecontainer leafstring', 'foobar')

        pretty = PyConfHoardFilter(self.subject.db, self.subject.db_values)
        pretty.convert(config=True, filter_blank_values=False)

        print (json.dumps(pretty.root, indent=4))

        expected_answer = """{
    "simplelist": {}, 
    "level1": {
        "level2": {
            "level3": {
                "mixed": {
                    "config": null
                }, 
                "withcfg": {
                    "config": null
                }
            }
        }
    }, 
    "simplestleaf": "abc123", 
    "simplecontainer": {
        "leafstring": "foobar"
    }, 
    "types": {
        "bignumber": null, 
        "hugenumber": null, 
        "compositekeylist": {}, 
        "number": null, 
        "biggernumber": null, 
        "secondlist": {}
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def test_convert_to_pretty_config_data_without_filter_simple_list(self):
        self.subject.set('simplestleaf', 'abc123')
        self.subject.set('simplecontainer leafstring', 'foobar')
        self.subject.create('simplelist', 'valueForFirstKey')
        self.subject.set('simplelist valueForFirstKey subitem', 'abc')

#        print (json.dumps(self.subject.db, indent=4))
        pretty = PyConfHoardFilter(self.subject.db, self.subject.db_values)
        pretty.convert(config=True, filter_blank_values=False)

        expected_answer = """{
    "level1": {
        "level2": {
            "level3": {
                "mixed": {
                    "config": null
                },
                "withcfg": {
                    "config": null
                }
            }
        }
    },
    "simplecontainer": {
        "leafstring": "foobar"
    },
    "simplelist": {
        "valueForFirstKey": {
            "item": "valueForFirstKey"
        }
    },
    "simplestleaf": "abc123",
    "types": {
        "biggernumber": null,
        "bignumber": null,
        "compositekeylist": {},
        "hugenumber": null,
        "number": null,
        "secondlist": {}
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4, sort_keys=True), expected_answer)

    def donttest_convert_to_config_filter_blanks_enabled(self):
        self.subject.set('simplestleaf', 'abc123')
        self.subject.set('simplecontainer leafstring', 'foobar')

        pretty = PyConfHoardFilter(self.subject.db, self.subject.db_values)
        pretty.convert(config=True, filter_blank_values=True)

        expected_answer = """{
    "simplestleaf": "abc123", 
    "simplecontainer": {
        "leafstring": "foobar"
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def donttest_convert_to_operdata_filter_blanks_enabled(self):
        self.subject.set('simplecontainer leafnonconfig', 'foobar1')

        pretty = PyConfHoardFilter(self.subject.db, self.subject.db_values)
        pretty.convert(config=False, filter_blank_values=True)

        expected_answer = """{
    "simplecontainer": {
        "leafnonconfig": "foobar1"
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def donttest_convert_to_operdata_filter_blanks_disabled(self):
        self.subject.set('simplecontainer leafnonconfig', 'foobar1')

        pretty = PyConfHoardFilter(self.subject.db, self.subject.db_values)
        pretty.convert(config=False, filter_blank_values=False)

        # Note: after each , there is a space
        expected_answer = """{
    "simplelist": {}, 
    "level1": {
        "level2": {
            "level3": {
                "mixed": {
                    "nonconfig": null
                }, 
                "withoutcfg": {
                    "nonconfig": null
                }
            }
        }
    }, 
    "simplecontainer": {
        "leafnonconfig": "foobar1"
    }
}"""

        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)

    def alreadytest_convert_to_operdata_without_collapsing_value(self):
        self.subject.set('simplecontainer leafnonconfig', 'foobar1')
        pretty = PyConfHoardFilter()
        pretty.convert(self.subject.db, config=False, filter_blank_values=True)

        expected_answer = """{
    "simplecontainer": {
        "leafnonconfig": "foobar1"
    }
}"""
        self.assertEqual(json.dumps(pretty.root, indent=4), expected_answer)
