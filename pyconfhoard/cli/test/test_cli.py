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

    def test_show_of_non_existing_path(self):
        try:
            result = self.subject._get_json_cfg_view('show thisdoesnotexist')
            self.fail('Expected to fail because we asked for a non-existing path')
        except ValueError as err:
            self.assertEqual(str(err), 'Path: show thisdoesnotexist does not exist')
            
    def test_show_top_level(self):
        result = self.subject._get_json_cfg_view('')
        result = json.loads(result)

        # These asserts access the structures directly - but we should of course
        # always use .get() on the path
        self.assertEqual(result['simplestleaf'],{})
        self.assertEqual(result['types']['number'], {})

    def test_show_bottom_leaf(self):
        self.subject._db_oper = self.object
        result = self.subject._get_json_cfg_view('types')
        result = json.loads(result)

        self.assertEqual(result['number'], {})
        self.assertEqual(result['number'], {})

    def test_show_mid_container(self):
        result = self.subject._get_json_cfg_view('level1 level2 level3')
        result = json.loads(result)

        self.assertEqual(result['mixed'], {'config': {}})
        self.assertEqual(result['withcfg'], {'config': {}})

    def test_tab_completion_without_leading_text(self):
        line = 'show level1 '
        text = ''
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['level2 '])

    def test_tab_completion_with_leading_text(self):
        line = 'show level1 le'
        text = 'le'
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['level2 '])

    def test_tab_completion_top_level_non_unique_input(self):
        line = 'show sim'
        text = 'sim'
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['simplecontainer ', 'simplelist ', 'simplestleaf '])

    def test_tab_completion_top_level_unique_input(self):
        line = 'show simpleco'
        text = 'simpleco'
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['simplecontainer '])

    def test_tab_completion_mid_level_unique_input_for_something_deep(self):
        line = 'show level1 level2 level3'
        text = ''
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['mixed ', 'withcfg '])

    def test_tab_completion_non_existing_everything(self):
        line = 'show THISDOESNOTEXIST abcdef xyz XXX YYY'
        text = 'YYY'
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, [])

    def test_tab_completion_non_existing_except_the_second_thing(self):
        line = 'show THISDOESNOTEXIST level1 abcdef xyz XXX YYY'
        text = ''
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, [])
