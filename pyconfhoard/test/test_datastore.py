import unittest
import json
import sys
sys.path.append('test')
from stub import testresource
from PyConfHoardDatastore import PyConfHoardDatastore


class TestYang(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema.json')
        self.maxDiff = 10000

    def test_decode_path_string(self):
        result = self.subject.decode_path_string('////abc/1234///ef/g', separator='/')
        self.assertEqual(result, ['abc', '1234', 'ef', 'g'])

    def test_decode_path_string_remove_n_2(self):
        result = self.subject.decode_path_string('////abc/1234///ef/g', separator='/', ignore_last_n=2)
        self.assertEqual(result, ['abc', '1234'])

    def test_decode_path_string_get_index(self):
        result = self.subject.decode_path_string('////abc/1234///ef/g', separator='/', get_index=-1)
        self.assertEqual(result, 'g')

    def test_list_config_nodes_from_root(self):
        result = self.subject.list('')
        self.assertEqual(list(result), ['simplestleaf', 'simplecontainer', 'level1', 'simplelist', 'types'])

    def test_list_config_nodes_from_child(self):
        result = self.subject.list('simplecontainer', filter_blank_values=False)
        self.assertEqual(list(result), ['leafstring'])

    def test_get_config_nodes_from_root(self):
        result = self.subject.get('')
        self.assertTrue('simplecontainer' in result)
        self.assertTrue('level1' in result)

    def test_get_depper_from_root(self):
        result = self.subject.get('level1 level2')
        self.assertTrue('level3' in result)
        self.assertTrue('mixed' in result['level3'])

    def test_listing_non_existant_path(self):
        try:
            self.subject.list('simplecontainer nonexist')
            self.fail('Listing a non existant node should throw an exception')
        except Exception as err:
            self.assertEqual(str(err), "Path: /simplecontainer/nonexist does not exist - cannot build list")

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
        listval = self.subject.get_raw('simplelist')
        self.subject.create('simplelist', 'valueForFirstKey')
        listval = self.subject.get_raw('simplelist')
        self.subject.set('simplelist valueForFirstKey subitem', 'abc')

        self.assertEqual(self.subject.get('/simplelist/valueForFirstKey/subitem', separator='/'), 'abc')

    def test_has_list_item(self):
        listval = self.subject.get_raw('simplelist')
        self.subject.create('simplelist', 'valueForFirstKey')
        listval = self.subject.get_raw('simplelist')
        self.subject.set('simplelist valueForFirstKey subitem', 'abc')

        self.assertEqual(self.subject.has_list_item('/simplelist/valueForFirstKey', separator='/'), True)
        self.assertEqual(self.subject.has_list_item('/simplelist/valueForFirstKe', separator='/'), False)

    def test_changing_a_list_key(self):
        listval = self.subject.get_object('simplelist')
        self.subject.create('simplelist', 'valueForFirstKey')

        try:
            self.subject.set('simplelist valueForFirstKey item', 'abc')
        except ValueError as err:
            self.assertEqual(str(err), "Path: ['simplelist', 'valueForFirstKey', 'item'] is a list key - cannot set keys")

        listelement = self.subject.get('simplelist valueForFirstKey')

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

    def test_merge_new_conf_data_into_existing_schema(self):
        before_merge = json.dumps(self.subject.get_object(''), indent=4)
        new_node = testresource.new_node_object()
        new_node['level1']['level2']['level3']['withcfg']['config']['__value'] = 'this-has-been-set-in-merge!'

        self.subject._merge_node(new_node)

        after_merge = json.dumps(self.subject.get_object(''), indent=4)

        updated_node_val = self.subject.get('/level1/level2/level3/withcfg/config', separator='/')
        self.assertEqual(updated_node_val, 'this-has-been-set-in-merge!')
