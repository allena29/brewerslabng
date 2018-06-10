import unittest
import json
import sys
import dpath.util
from mock import patch, ANY
sys.path.append('test')
from PyConfHoard import Data, Thing
from PyConfHoardCommon import decode_path_string
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf, PyConfHoardDataPathDoesNotExist, PyConfHoardDataPathNotRegistered


class TestWrapperForData(unittest.TestCase):
    def setUp(self):
        self.subject = Data('test/schema-config.json', 'test/schema-oper.json')
        self.subject.register('/tupperware')
        self.subject.register('/simplelist')

    def test_create_thing_one(self):

        print('********')
        print(self.subject.config.db, 'root instance')
        print(self.subject.config.db['root'])
        print(self.subject.config.db['root']['tupperware'], 'tupperware')
        print(self.subject.config.db['root']['simplelist'], 'simplelist')
        print(self.subject.config.db)

        x=self.subject.config.db['root']['tupperware']
        x.set('/root/tupperware/config', 'plastic', separator='/')
        print(x)
        print(x.keyval)
        print('********')
        self.assertFalse(self.subject.config.db is self.subject.config.db['root']['tupperware'])

    def test_list(self):
        # List is used for auto-complete on things like th ecommand line
        result = self.subject.list('tupperware')
        self.assertEqual(result, ['config', 'outer', 'outhere'])

        result = self.subject.list('/tupperware/outer', separator='/')
        self.assertEqual(result, ['inner'])

        result = self.subject.list('/', separator='/')
        self.assertEqual(result, ['simplelist', 'simplestleaf', 'stackedlists', 'tupperware'])

        try:
            self.subject.list('carboard')
            self.fail('PyConfHoardDataPathDoesNotExist should have been thrown because we tried to access a non-existant path')
        except PyConfHoardDataPathDoesNotExist as err:
            pass

    def test_get_and_set(self):
        try:
            self.subject.set('/x123123123', 'this')
            self.fail('We should have had an exception for accessing a non-registered path')
        except PyConfHoardDataPathNotRegistered as err:
            pass

        self.subject.set('/tupperware/config', 'this-value', separator='/')
        result = self.subject.get('/tupperware/config', separator='/')
        self.assertEqual('this-value', result)

    def test_decode_path_string(self):
        result = decode_path_string('/x/1/2/3{abc}', separator='/')
        self.assertEqual(['root', 'x', '1', '2', '3', '{abc}'], result)

        result = decode_path_string('/x/1/2/3{abc}/x{def}', separator='/')
        self.assertEqual(['root', 'x', '1', '2', '3', '{abc}', 'x', '{def}'], result)

    def test_list_create(self):
        self.subject.create('/simplelist', ['crystal'], separator='/')
        self.subject.set('/simplelist{crystal}/val', 'maze', separator='/')
        result = self.subject.get('/simplelist{crystal}/id', separator='/')
        self.assertEqual(result, 'crystal')
        result = self.subject.get('/simplelist{crystal}/val', separator='/')
        self.assertEqual(result, 'maze')

    def test_load(self):
        config = """
        {"/root/tupperware/config": "abc123"}
        """
        self.subject._load('/tupperware', config)
        self.assertEqual(self.subject.get('/tupperware/config', separator='/'), 'abc123')

    @patch("requests.patch")
    @patch("requests.get")
    def test_load_metadata_from_web(self, requests_get_mock, requests_patch_mock):
        discover_response = DummyResponse("""{
    "datastores": {
        "Thing1": {
            "appname": "The plastic container",
            "yangpath": "/tupperware"
        },
        "Thing2": {
            "appname": "The thins wil multiple things",
            "yangpath": "/simplelist"
        }
    },
    "schema-config": {
        "root": {
            "simplelist": {
                "__listelement": {
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
                            "__path": "/root/simplelist/__listelement/id",
                            "__rootlevel": false,
                            "__type": "string"
                        }
                    },
                    "val": {
                        "__schema": {
                            "__config": true,
                            "__leaf": true,
                            "__listitem": true,
                            "__listkey": false,
                            "__path": "/root/simplelist/__listelement/val",
                            "__rootlevel": false,
                            "__type": "string"
                        }
                    }
                }
            },
            "simplestleaf": {
                "__schema": {
                    "__config": true,
                    "__leaf": true,
                    "__listitem": true,
                    "__listkey": false,
                    "__path": "/root/simplestleaf",
                    "__rootlevel": true,
                    "__type": "string"
                }
            },
            "stackedlists": {
                "__schema": {
                    "__container": true,
                    "__decendentconfig": true,
                    "__decendentoper": false,
                    "__path": "/root/stackedlists",
                    "__rootlevel": true
                },
                "lista": {
                    "__listelement": {
                        "__schema": {
                            "__decendentconfig": true,
                            "__decendentoper": false,
                            "__elements": {},
                            "__keys": [
                                "keya"
                            ],
                            "__list": true,
                            "__path": "/root/stackedlists/lista",
                            "__rootlevel": false
                        },
                        "keya": {
                            "__schema": {
                                "__config": true,
                                "__leaf": true,
                                "__listitem": true,
                                "__listkey": true,
                                "__path": "/root/stackedlists/lista/__listelement/keya",
                                "__rootlevel": false,
                                "__type": "string"
                            }
                        },
                        "listb": {
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
                                        "__type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "tupperware": {
                "__schema": {
                    "__container": true,
                    "__decendentconfig": true,
                    "__decendentoper": true,
                    "__path": "/root/tupperware",
                    "__rootlevel": true
                },
                "config": {
                    "__schema": {
                        "__config": true,
                        "__leaf": true,
                        "__listitem": true,
                        "__listkey": false,
                        "__path": "/root/tupperware/config",
                        "__rootlevel": false,
                        "__type": "string"
                    }
                },
                "outer": {
                    "__schema": {
                        "__container": true,
                        "__decendentconfig": true,
                        "__decendentoper": false,
                        "__path": "/root/tupperware/outer",
                        "__rootlevel": false
                    },
                    "inner": {
                        "__schema": {
                            "__container": true,
                            "__decendentconfig": true,
                            "__decendentoper": false,
                            "__path": "/root/tupperware/outer/inner",
                            "__rootlevel": false
                        },
                        "number": {
                            "__schema": {
                                "__config": true,
                                "__leaf": true,
                                "__listitem": true,
                                "__listkey": false,
                                "__path": "/root/tupperware/outer/inner/number",
                                "__rootlevel": false,
                                "__type": "uint32"
                            }
                        }
                    }
                },
                "outhere": {
                    "__schema": {
                        "__container": true,
                        "__decendentconfig": false,
                        "__decendentoper": false,
                        "__path": "/root/tupperware/outhere",
                        "__rootlevel": false
                    }
                }
            }
        }
    },
    "schema-oper": {
        "root": {
            "simplelist": {
                "__listelement": {
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
                            "__path": "/root/simplelist/__listelement/id",
                            "__rootlevel": false,
                            "__type": "string"
                        }
                    },
                    "operval": {
                        "__schema": {
                            "__config": false,
                            "__leaf": true,
                            "__listitem": true,
                            "__listkey": false,
                            "__path": "/root/simplelist/__listelement/operval",
                            "__rootlevel": false,
                            "__type": "string"
                        }
                    }
                }
            },
            "simpleoper": {
                "__schema": {
                    "__config": false,
                    "__leaf": true,
                    "__listitem": true,
                    "__listkey": false,
                    "__path": "/root/simpleoper",
                    "__rootlevel": true,
                    "__type": "string"
                }
            },
            "stackedlists": {
                "__schema": {
                    "__container": true,
                    "__decendentconfig": true,
                    "__decendentoper": false,
                    "__path": "/root/stackedlists",
                    "__rootlevel": true
                },
                "lista": {
                    "__listelement": {
                        "__schema": {
                            "__decendentconfig": true,
                            "__decendentoper": false,
                            "__elements": {},
                            "__keys": [
                                "keya"
                            ],
                            "__list": true,
                            "__path": "/root/stackedlists/lista",
                            "__rootlevel": false
                        },
                        "keya": {
                            "__schema": {
                                "__config": true,
                                "__leaf": true,
                                "__listitem": true,
                                "__listkey": true,
                                "__path": "/root/stackedlists/lista/__listelement/keya",
                                "__rootlevel": false,
                                "__type": "string"
                            }
                        },
                        "listb": {
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
                                        "__type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "tupperware": {
                "__schema": {
                    "__container": true,
                    "__decendentconfig": true,
                    "__decendentoper": true,
                    "__path": "/root/tupperware",
                    "__rootlevel": true
                },
                "oper": {
                    "__schema": {
                        "__config": false,
                        "__leaf": true,
                        "__listitem": true,
                        "__listkey": false,
                        "__path": "/root/tupperware/oper",
                        "__rootlevel": false,
                        "__type": "string"
                    }
                },
                "outer": {
                    "__schema": {
                        "__container": true,
                        "__decendentconfig": true,
                        "__decendentoper": false,
                        "__path": "/root/tupperware/outer",
                        "__rootlevel": false
                    },
                    "inner": {
                        "__schema": {
                            "__container": true,
                            "__decendentconfig": true,
                            "__decendentoper": false,
                            "__path": "/root/tupperware/outer/inner",
                            "__rootlevel": false
                        }
                    }
                },
                "outhere": {
                    "__schema": {
                        "__container": true,
                        "__decendentconfig": false,
                        "__decendentoper": false,
                        "__path": "/root/tupperware/outhere",
                        "__rootlevel": false
                    }
                }
            }
        }
    }
}""")
        config_response = DummyResponse('')
        oper_response = DummyResponse('')
            
        requests_get_mock.side_effect = [
            discover_response,
            config_response,
            oper_response,
            config_response,
            oper_response
        ]
        self.subject.map = {}
        
        # Act
        self.subject.register_from_web('http://localhost:8000')
        self.subject.set('/tupperware/config', 'bang-bang-your-dead', separator='/')
        self.subject.persist_to_web('http://localhost:8000', '/tupperware')
        
        # Assert
        expected_patch = """{\n    "/tupperware/config": "bang-bang-your-dead"\n}"""
        self.assertEqual(list(self.subject.map.keys()), ['/tupperware', '/simplelist'] )
        requests_patch_mock.assert_called_once_with(auth=ANY, data=expected_patch, headers={'Content-Type': 'application/json'}, url="http://localhost:8000/v1/datastore/running//tupperware")


    def test_get_json_struct(self):
        # Build
        self.test_get_and_set()
        
        # Act
        answer = self.subject.get_database_as_json('/', database='config', separator='/')
        
        # Assert
        expected_answer = """{
    "root": {
        "tupperware": {
            "config": "this-value"
        }
    }
}"""
        self.assertEqual(expected_answer, answer)

    def test_get_json_struct2(self):
        # Act
        answer = self.subject.get_database_as_json('/', database='config', separator='/', pretty=True)
        
        # Assert
        expected_answer = """Database is blank!"""
        self.assertEqual(expected_answer, answer)


class DummyResponse:
    def __init__(self, text):
        self.text=text

