import unittest
import os
import json
from mock import Mock
from cli import PyConfHoardCLI


class TestPyConfHoardCLI(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardCLI(no_networking=True)
        self.subject.config._load_datastores = Mock()
        self.subject.oper._load_datastores = Mock()
        self.subject.config.schema = json.loads(open('test/schema-config.json').read())
        self.subject.oper.schema = json.loads(open('test/schema-oper.json').read())
        self.maxDiff = 10000

    def test_show_of_non_existing_path(self):
        result = self.subject._get_json_cfg_view('show thisdoesnotexist')
        expected_result = """Database is blank"""
        self.assertEqual(result, expected_result)

    def test_show_top_level(self):
        self.subject.config.set('simplestleaf', 243)
        result = self.subject._get_json_cfg_view('')
        result = json.loads(result)
        self.assertEqual(result['simplestleaf'], 243)

    def test_tab_completion_top_level_non_unique_input(self):
        line = 'show tupperware o'
        text = 'o'

        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['outer ', 'outhere '])

    def test_tab_completion_top_level_unique_input(self):
        line = 'show tup'
        text = 'tup'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['tupperware '])

    def test_tab_completion_mid_level_unique_input_for_something_deep(self):
        line = 'show tupperware outer'
        text = ''
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, ['inner '])

    def test_tab_completion_non_existing_everything(self):
        line = 'show THISDOESNOTEXIST abcdef xyz XXX YYY'
        text = 'YYY'
        cmds = self.subject._auto_complete(line, text)

        self.assertEqual(cmds, [])

    def donttest_tab_completion_create_list(self):
        line = 'create types secondlis'
        text = 'secondlis'
        cmds = self.subject._auto_complete(line, text, cmd='create ')

        self.assertEqual(cmds, ['secondlist '])

    def donttest_create_list_key(self):
        args = 'create types secondlist KEY'
        self.subject._command_create('types secondlist KEY')

        list_item_key = self.subject.datastore.get('types secondlist KEY item')
        self.assertEqual(list_item_key, 'KEY')
