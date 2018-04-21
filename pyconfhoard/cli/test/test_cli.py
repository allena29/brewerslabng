import unittest
import os
import json
from mock import Mock
from cli import PyConfHoardCLI

class TestPyConfHoardCLI(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardCLI(no_networking=True)
        self.subject._load_datastores = Mock()
        self.subject.datastore.db = json.loads(open('test/schema.json').read())
        self.object = self.subject.datastore.db
        self.maxDiff = 10000
    def test_show_of_non_existing_path(self):
        try:
            result = self.subject._get_json_cfg_view('show thisdoesnotexist')
            self.fail('Expected to fail because we asked for a non-existing path')
        except ValueError as err:
            self.assertEqual(str(err), 'Path: show thisdoesnotexist does not exist')
            
    def test_show_top_level(self):
        self.subject.datastore.set('simplestleaf', 243)
        result = self.subject._get_json_cfg_view('')
        result = json.loads(result)
        # These asserts access the structures directly - but we should of course
        # always use .get() on the path
        self.assertEqual(result['simplestleaf'], 243)

    def test_show_bottom_leaf(self):
        self.subject._db_oper = self.object
        result = self.subject._get_json_cfg_view('types', filter_blank_values=False)
        result = json.loads(result)

        self.assertEqual(result['number'], None)

    def test_show_mid_container(self):
        self.subject.datastore.set('level1 level2 level3 mixed config', 'this-value-has-been-set')
        self.subject.datastore.set('level1 level2 level3 withcfg config', 'this-value-has-been-set2')
        result = self.subject._get_json_cfg_view('level1 level2 level3')

        expected = """{
    "withcfg": {
        "config": "this-value-has-been-set2"
    },
    "mixed": {
        "config": "this-value-has-been-set"
    }
}"""
        self.assertEqual(result, expected)

    def test_tab_completion_without_leading_text(self):
        line = 'show level1 '
        text = ''
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['level2 '])

    def test_tab_completion_with_leading_text(self):
        line = 'show level1 le'
        text = 'le'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['level2 '])

    def test_tab_completion_top_level_non_unique_input(self):
        line = 'show sim'
        text = 'sim'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['simplecontainer ', 'simplelist ', 'simplestleaf '])

    def test_tab_completion_top_level_unique_input(self):
        line = 'show simpleco'
        text = 'simpleco'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['simplecontainer '])

    def test_tab_completion_mid_level_unique_input_for_something_deep(self):
        line = 'show level1 level2 level3'
        text = ''
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['mixed ', 'withcfg '])

    def test_tab_completion_non_existing_everything(self):
        line = 'show THISDOESNOTEXIST abcdef xyz XXX YYY'
        text = 'YYY'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, [])

    def test_tab_completion_non_existing_except_the_second_thing(self):
        line = 'show THISDOESNOTEXIST level1 abcdef xyz XXX YYY'
        text = ''
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, [])

    def test_tab_completion_create_list(self):
        line = 'create types secondlis'
        text = 'secondlis'
        cmds = self.subject._auto_complete(line, text, cmd='create ')

        self.assertEqual(cmds, ['secondlist '])

    def test_create_list_key(self):
        args = 'create types secondlist KEY'
        self.subject._command_create('types secondlist KEY')

        list_item_key = self.subject.datastore.get('types secondlist KEY item')
        self.assertEqual(list_item_key, 'KEY')

