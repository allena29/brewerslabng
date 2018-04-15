import unittest
import json

from PyConfHoardDatastore import PyConfHoardDatastore


class TestYang(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema.json')
        self.maxDiff=4888
    def test_list_config_nodes_from_root(self):
        result = self.subject.list('')
        self.assertEqual(result, ['simplecontainer', 'level1', 'simplelist', 'types'])


    def test_list_config_nodes_from_child(self):
        result = self.subject.list('simplecontainer')
        self.assertEqual(result, ['leafstring'])

    def test_get_config_nodes_from_root(self):
        result = self.subject.get('')
        self.assertTrue('simplecontainer' in result)
        self.assertTrue('level1' in result)


    def test_get_depper_from_root(self):
        result = self.subject.get('level1 level2')
        self.assertTrue('level3' in result)
        self.assertTrue('mixed' in result['level3'])

    def test_filtering_of_config_nodes_in_a_list(self):
        result = self.subject.list('level1 level2 level3')
        self.assertEqual(result, ['withcfg', 'mixed'])

    def test_filtering_of_non_config_nodes_in_a_list(self):
        result = self.subject.list('level1 level2 level3', config=False)
        self.assertEqual(result, ['withoutcfg', 'mixed'])

    def test_listing_non_existant_path(self):
        try:
            self.subject.list('simplecontainer nonexist')
            self.fail('Listing a non existant node should throw an exception')
        except Exception as err:
            self.assertEqual(str(err), "['simplecontainer', 'nonexist']")
    
    def test_listing_non_existant_path_lower_down_lazy_list(self):
        result = self.subject.list_lazy('simplecontainer nonexist')
        self.assertEqual(result, ['leafstring'])

    def test_listing_non_existant_path_at_root_lazy_list(self):
        result = self.subject.list_lazy('nonexist')
        self.assertEqual(result, None)

    def test_get_filtered_configuration_view(self):
        result = self.subject.get_filtered('', config=True)

        expected_result = """{
    "simplecontainer": {
        "leafstring": {}
    },
    "level1": {
        "level2": {
            "level3": {
                "withcfg": {
                    "config": {}
                },
                "mixed": {
                    "config": {}
                }
            }
        }
    },
    "simplelist": {
        "item": {}
    },
    "types": {
        "number": {},
        "biggernumber": {},
        "bignumber": {},
        "hugenumber": {},
        "secondlist": {
            "item": {},
            "thingwithdefault": {},
            "innerlist": {
                "item": {}
            }
        },
        "compositekeylist": {
            "keyA": {},
            "keyB": {}
        }
    }
}"""
        print (json.dumps(result, indent=4))
        self.assertMultiLineEqual(json.dumps(result, indent=4), expected_result)
                                            
    
    def test_get_filtered_operational_view(self):
        result = self.subject.get_filtered('', config=False)

        expected_result = """{
    "simplecontainer": {
        "leafnonconfig": {}
    },
    "level1": {
        "level2": {
            "level3": {
                "withoutcfg": {
                    "nonconfig": {}
                },
                "mixed": {
                    "nonconfig": {}
                }
            }
        }
    },
    "simplelist": {
        "subitem": {}
    }
}"""
        self.assertMultiLineEqual(json.dumps(result, indent=4), expected_result)
                                            
 
