import unittest
import json
from mock import Mock
from cli import PyConfHoardCLI
from cli import PyConfHoardCommon

class TestPyConfHoardCLI(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardCLI()
        self.subject._load_datastores = Mock()

        self.object = {
            "abc123": {
                "def": "456"
            },
            "abcdef": {
                "xyz": {
                    "XXX": {
                        "YYY": {
                            "ZZZ": 'end'
                        }
                    }
                }
            }
        }

        self.schema = {
            'abc123': {
                'def': {
                    'type': 'string',
                    'config': True
                }
            },
            'abcdef': {
                'xyz': {
                    'XXX': {
                        'YYY': {
                            'ZZZ': {
                                'type': 'enumeration',
                                'enum_values': [
                                    'end',
                                    'start',
                                ]
                            }
                        }
                    }
                }
            }
        }
    def test_show_of_non_existing_path(self):
        
        try:
            result = self.subject._get_json_cfg_view(self.object, 'show thisdoesnotexist')
            self.fail('Expected to fail because we asked for a non-existing path')
        except Exception as err:
            self.assertEqual(str(err), 'Path: show thisdoesnotexist does not exist')


    def test_show_top_level(self):
        result = self.subject._get_json_cfg_view(self.object, '')
        result = json.loads(result)

        self.assertEqual(result['abc123']['def'], "456")
        self.assertEqual(result['abcdef']['xyz']['XXX']['YYY']['ZZZ'], "end")

    def test_show_bottom_leaf(self):
        self.subject._db_oper = self.object
        result = self.subject._get_json_cfg_view(self.object, 'abcdef xyz XXX YYY ZZZ')
        result = json.loads(result)

        self.assertEqual(result, "end")

    def test_show_mid_container(self):
        result = self.subject._get_json_cfg_view(self.object, 'abcdef xyz XXX YYY')
        result = json.loads(result)

        self.assertEqual(result['ZZZ'], "end")

    def test_tab_completion_top_level_non_unique_input(self):
        line = 'show ab'
        text = 'ab'
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['abc123 ', 'abcdef '])

    def test_tab_completion_top_level_unique_input(self):
        line = 'show abc12'
        text = 'abc12'
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['abc123 '])

    def test_tab_completion_top_level_unique_input_for_something_deep(self):
        line = 'show abcdef xyz XXX YYY'
        text = ''
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, ['ZZZ '])

    def test_tab_completion_non_existing_top_level_input(self):
        line = 'show THISDOESNOTEXIST abcdef xyz XXX YYY'
        text = ''
        cmds = self.subject._auto_complete(self.object, line, text)

        self.assertEqual(cmds, [])

    def test_get_node_finding_top_level_node_matches(self):
        path = 'abc123'

        result = PyConfHoardCommon._get_node(self.object, path)

        self.assertEqual(list(result.keys()), ['def'])

    def test_get_node_finding_top_level_node_does_not_match(self):
        path = 'abc12'

        result = PyConfHoardCommon._get_node(self.object, path)

        self.assertEqual(list(result.keys()), ['abc123', 'abcdef'])

    def test_get_node_finding_top_level_node_does_not_match_but_we_match_something_deeper(self):
        path = 'abc12'

        result = PyConfHoardCommon._get_node(self.object, path)

        self.assertEqual(list(result.keys()), ['abc123', 'abcdef'])

    def test_validate_enumeration_invalid_value(self):
        path = 'abcdef xyz XXX YYY ZZZ middle'
        try:
            result = PyConfHoardCommon._validate_node(self.object, path, self.schema)
            self.fail('ValueError should have been raised because we did not set a known enumeration')
        except ValueError as err:
            self.assertEqual(str(err), "Invalid Value: key ZZZ value  middle != ['end', 'start']")
    
    def test_validate_and_set_enumeration_valid_value(self):
        path = 'abcdef xyz XXX YYY ZZZ start'
        result = PyConfHoardCommon._validate_node(self.object, path, self.schema)
        PyConfHoardCommon._set_node(self.object, path)
        updated = PyConfHoardCommon._get_node(self.object, 'abcdef xyz XXX YYY')
        self.assertEqual(updated['ZZZ'], 'start')

