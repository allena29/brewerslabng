import unittest
import json

from PyConfHoardDatastore import PyConfHoardDatastore


class TestYang(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema.json')
        self.maxDiff=4888

    def test_decode_path_string(self):
        result = self.subject.decode_path_string('////abc/1234///ef', separator='/')
        self.assertEqual(result, ['abc', '1234', 'ef'])

    def test_list_config_nodes_from_root(self):
        result = self.subject.list('')
        self.assertEqual(result, ['simplestleaf', 'simplecontainer', 'level1', 'simplelist', 'types'])


    def test_list_config_nodes_from_child(self):
        result = self.subject.list('simplecontainer')
        self.assertEqual(result, ['leafstring'])

    def test_get_config_nodes_from_root(self):
        result = self.subject.get('')
        self.assertTrue('simplecontainer' in result)
        self.assertTrue('level1' in result)


    def test_get_depper_from_root(self):
        result = self.subject.get_object('level1 level2')
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
    "simplestleaf": {},
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
        # print (json.dumps(result, indent=4))
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
                                            
    def test_set_simple_leaf(self):
        before_update = self.subject.get('/simplestleaf', separator='/')
        self.assertEqual(before_update, None)

        self.subject.set('/simplestleaf', 'this can be any string', separator='/')

        after_update = self.subject.get('/simplestleaf', separator='/')
        self.assertEqual(after_update, 'this can be any string')

    def test_set_simple_deep_leaf(self):
        val = """This a multiline\nstring"""
        self.subject.set('/level1/level2/level3/mixed/config', val, separator='/')

        after_update = self.subject.get('/level1/level2/level3/mixed/config', separator='/')
        self.assertEqual(after_update, val)

    def test_attempt_to_set_a_non_leaf(self):
        try:
            self.subject.set('level1 level2 level3', 'val')
            self.fail('Set on a non-leaf must fail')
        except ValueError as err:
            self.assertEqual(str(err), "Path: ['level1', 'level2', 'level3'] is not a leaf - cannot set a value")

    def test_create_list_item(self):
        listval = self.subject.get_object('simplelist')
        self.subject.create('simplelist', 'valueForFirstKey')
        listval = self.subject.get_object('simplelist')

        self.subject.set('simplelist valueForFirstKey subitem', 'abc')

        self.assertEqual(self.subject.get('/simplelist/valueForFirstKey/subitem', separator='/'), 'abc')


    def test_changing_a_list_key(self):
        listval = self.subject.get_object('simplelist')
        self.subject.create('simplelist', 'valueForFirstKey')

        try:
            self.subject.set('simplelist valueForFirstKey item', 'abc')
        except ValueError as err:
            self.assertEqual(str(err), "Path: ['simplelist', 'valueForFirstKey', 'item'] is a list key - cannot set keys")

        listelement = self.subject.get_object('simplelist valueForFirstKey')

    def test_create_list_item_with_wrong_number_of_keys(self):
        try:
            self.subject.create('simplelist', 'firstkeyVal secondkeyVal')
            self.fail('Set on a list with the wrong number of keys must fail')
        except ValueError as err:
            self.assertEqual(str(err), "Path: ['simplelist'] requires the following 1 keys ['item'] - 2 keys provided")


    def test_create_list_item_on_a_non_list(self):
        try:
            self.subject.create('level1 level2 level3', 'val')
            self.fail('Set on a non-leaf must fail')
        except ValueError as err:
            self.assertEqual(str(err), "Path: ['level1', 'level2', 'level3'] is not a list - cannot create an item")


