import unittest
import json
import sys
import dpath.util
sys.path.append('test')
from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf


class TestYang(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardDatastore()
        self.subject_oper = PyConfHoardDatastore()
        self.subject.load_blank_schema('test/schema-config.json')
        self.subject_oper.load_blank_schema('test/schema-oper.json')
        self.maxDiff = 10000

    def test_list_completion(self):
        result = self.subject.list('/', separator='/')
        expected_result = ['simplelist', 'simplestleaf', 'stackedlists', 'tupperware']
        self.assertEqual(result, expected_result)

    def test_list_completion_leaf(self):
        result = self.subject.list('/simplelist', separator='/')
        expected_result = ['id', 'val']
        self.assertEqual(result, expected_result)

    def test_get_type(self):
        result = self.subject.get_type('/simplelist', separator='/')
        self.assertEqual(result['__list'], True)

        try:
            result = self.subject.get_type('/', separator='/')
            self.fail('Accessing / should have thrown AccessNonLeaf exception')
        except PyConfHoardAccessNonLeaf:
            pass

        result = self.subject.get_type('/simplelist{sdfsdfsdf}', separator='/')
        self.assertEqual(result['__path'], '/root/simplelist')

    def test_get_val(self):
        # Retreive a value not yet set should return None
        result = self.subject.get('/simplestleaf', separator='/')
        self.assertEqual(result, None)

    def test_set_val(self):
        set_val = 'sleep'
        self.subject.set('/simplestleaf', set_val, separator='/')
        result = self.subject.get('/simplestleaf', separator='/')
        self.assertEqual(result, set_val)

    def test_set_list_element(self):
        list_key_values = ['glow']
        self.subject.create('/simplelist', list_key_values, separator='/')
        self.subject.set('/simplelist{glow}/val', 'in the dark', separator='/')

    def test_dump(self):
        self.test_set_list_element()
        result = self.subject.dump()
        expected_result = """{
    "root": {
        "simplelist": {
            "{glow}": {
                "id": "glow",
                "val": "in the dark"
            }
        }
    }
}"""

        self.assertEqual(result, expected_result)

    def test_merge_in_keyval(self):
        # Act
        self.subject._merge_keyval('/simplestleaf', 'flowers')

        # Assert
        expected_result = {'root': {'simplestleaf': 'flowers'}}
        self.assertEqual(self.subject.db, expected_result)

    def test_validate_against_schema_string(self):
        # Build
        schema = {'__schema': {
            '__type': 'string'
        }
        }

        # Act
        self.subject.validate_against_schema(schema, "0")

    def test_validate_against_schema_int(self):
        # Build
        schema = {'__schema': {
            '__type': 'integer'
        }
        }

        # Act
        #self.subject.validate_against_schema(schema, "OH")

    def test_persist(self):
        self.test_merge_in_keyval()

        # Act
        result = self.subject.persist()

        # Assert
        expected_result = {'/simplestleaf': 'flowers'}
        self.assertEqual(result, expected_result)

    def test_persist_list(self):

        self.subject.create('simplelist', ['castle'])

        result = self.subject.persist()

        expected_result = {'simplelist{castle}/id': 'castle'}
        self.assertEqual(result, expected_result)

        expected_result = {'root': {'simplelist': {'{castle}': {'id': 'castle'}}}}
        self.assertEqual(self.subject.db, expected_result)

        expected_result = """{
    "__schema": {
        "__decendentconfig": true,
        "__decendentoper": true,
        "__elements": {},
        "__keys": [
            "id"
        ],
        "__list": true,
        "__path": "/root/simplelist",
        "__rootlevel": true
    },
    "id": {
        "__schema": {
            "__config": true,
            "__leaf": true,
            "__listitem": true,
            "__listkey": true,
            "__path": "/root/simplelist{castle}/id",
            "__rootlevel": false,
            "__type": "string",
            "__typedef": false
        }
    },
    "val": {
        "__schema": {
            "__config": true,
            "__leaf": true,
            "__listitem": true,
            "__listkey": false,
            "__path": "/root/simplelist{castle}/val",
            "__rootlevel": false,
            "__type": "string",
            "__typedef": false
        }
    }
}"""
        self.assertEqual(json.dumps(self.subject.schema['root']['simplelist']['{castle}'], indent=4, sort_keys=True), expected_result)

    def test_importing_list_values(self):
        key = '/simplelist{castle}/id'
        val = 'castle'

        # Act
        self.subject._merge_keyval(key, val)

        # Assert
        expected_result = """{
    "__schema": {
        "__decendentconfig": true,
        "__decendentoper": true,
        "__elements": {},
        "__keys": [
            "id"
        ],
        "__list": true,
        "__path": "/root/simplelist",
        "__rootlevel": true
    },
    "id": {
        "__schema": {
            "__config": true,
            "__leaf": true,
            "__listitem": true,
            "__listkey": true,
            "__path": "/root/simplelist{castle}/id",
            "__rootlevel": false,
            "__type": "string",
            "__typedef": false
        }
    },
    "val": {
        "__schema": {
            "__config": true,
            "__leaf": true,
            "__listitem": true,
            "__listkey": false,
            "__path": "/root/simplelist{castle}/val",
            "__rootlevel": false,
            "__type": "string",
            "__typedef": false
        }
    }
}"""
        self.assertEqual(json.dumps(self.subject.schema['root']['simplelist']['castle'], indent=4, sort_keys=True), expected_result)

    def test_stacked_lsits(self):
        key = '/stackedlists/lista{aaaa}/keya'
        val = 'AAA'
        key2 = '/stackedlists/lista{aaaa}/listb{bbbb}/keyb'
        val2 = 'BBB'
        # Act
        self.subject._merge_keyval(key, val)
        self.subject._merge_keyval(key2, val2)

        # Assert
        expected_result = """{
    "__listelement": {
        "__schema": {
            "__decendentconfig": true,
            "__decendentoper": false,
            "__elements": {},
            "__keys": [
                "keyb"
            ],
            "__list": true,
            "__path": "/root/stackedlists/lista/__listelement/listb",
            "__rootlevel": false
        },
        "keyb": {
            "__schema": {
                "__config": true,
                "__leaf": true,
                "__listitem": true,
                "__listkey": true,
                "__path": "/root/stackedlists/lista/__listelement/listb/__listelement/keyb",
                "__rootlevel": false,
                "__type": "string",
                "__typedef": false
            }
        }
    },
    "bbbb": {
        "__schema": {
            "__decendentconfig": true,
            "__decendentoper": false,
            "__elements": {},
            "__keys": [
                "keyb"
            ],
            "__list": true,
            "__path": "/root/stackedlists/lista/__listelement/listb",
            "__rootlevel": false
        },
        "keyb": {
            "__schema": {
                "__config": true,
                "__leaf": true,
                "__listitem": true,
                "__listkey": true,
                "__path": "/root/stackedlists/lista{bbbb}/listb/__listelement/keyb",
                "__rootlevel": false,
                "__type": "string",
                "__typedef": false
            }
        }
    }
}"""
        actual_result = json.dumps(self.subject.schema['root']['stackedlists']['lista']['aaaa']['listb'], indent=4, sort_keys=True)

        # print (actual_result)
        self.assertEqual(actual_result, expected_result)

        expected_result = {'/stackedlists/lista{aaaa}/keya': 'AAA', '/stackedlists/lista{aaaa}/listb{bbbb}/keyb': 'BBB'}
        actual_result = self.subject.keyval

        self.assertEqual(actual_result, expected_result)

    def test_get_keyval(self):
        self.test_set_val()
        self.test_set_list_element()
        self.assertEqual(self.subject.get_keypath('/simplestleaf'), 'sleep')
        print(self.subject.keyval)
        self.assertEqual(self.subject.get_keypath('/simplelist{glow}/val'), 'in the dark')
