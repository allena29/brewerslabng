import json


class testresource:

    @staticmethod
    def new_node_object():
        return json.loads("""{
    "simplestleaf": {
        "__value": null,
        "__schema": {
            "__config": true,
            "__leaf": true,
            "__path": "/simplestleaf",
            "__listkey": false,
            "__listitem": true,
            "__type": "string",
            "__rootlevel": true
        }
    },
    "simplecontainer": {
        "__schema": {
            "__path": "/simplecontainer",
            "__container": true,
            "__decendentconfig": true,
            "__decendentoper": true,
            "__rootlevel": true
        },
        "leafstring": {
            "__value": null,
            "__schema": {
                "__config": true,
                "__leaf": true,
                "__path": "/simplecontainer/leafstring",
                "__listkey": false,
                "__listitem": true,
                "__type": "string",
                "__rootlevel": false
            }
        },
        "leafnonconfig": {
            "__value": null,
            "__schema": {
                "__config": false,
                "__leaf": true,
                "__path": "/simplecontainer/leafnonconfig",
                "__listkey": false,
                "__listitem": true,
                "__type": "string",
                "__rootlevel": false
            }
        }
    },
    "level1": {
        "__schema": {
            "__path": "/level1",
            "__container": true,
            "__decendentconfig": true,
            "__decendentoper": true,
            "__rootlevel": true
        },
        "level2": {
            "__schema": {
                "__path": "/level1/level2",
                "__container": true,
                "__decendentconfig": true,
                "__decendentoper": true,
                "__rootlevel": false
            },
            "level3": {
                "__schema": {
                    "__path": "/level1/level2/level3",
                    "__container": true,
                    "__decendentconfig": true,
                    "__decendentoper": true,
                    "__rootlevel": false
                },
                "withcfg": {
                    "__schema": {
                        "__path": "/level1/level2/level3/withcfg",
                        "__container": true,
                        "__decendentconfig": true,
                        "__decendentoper": false,
                        "__rootlevel": false
                    },
                    "config": {
                        "__value": null,
                        "__schema": {
                            "__config": true,
                            "__leaf": true,
                            "__path": "/level1/level2/level3/withcfg/config",
                            "__listkey": false,
                            "__listitem": true,
                            "__type": "string",
                            "__rootlevel": false
                        }
                    }
                },
                "withoutcfg": {
                    "__schema": {
                        "__path": "/level1/level2/level3/withoutcfg",
                        "__container": true,
                        "__decendentconfig": false,
                        "__decendentoper": true,
                        "__rootlevel": false
                    },
                    "nonconfig": {
                        "__value": null,
                        "__schema": {
                            "__config": false,
                            "__leaf": true,
                            "__path": "/level1/level2/level3/withoutcfg/nonconfig",
                            "__listkey": false,
                            "__listitem": true,
                            "__type": "string",
                            "__rootlevel": false
                        }
                    }
                },
                "mixed": {
                    "__schema": {
                        "__path": "/level1/level2/level3/mixed",
                        "__container": true,
                        "__decendentconfig": true,
                        "__decendentoper": true,
                        "__rootlevel": false
                    },
                    "config": {
                        "__value": null,
                        "__schema": {
                            "__config": true,
                            "__leaf": true,
                            "__path": "/level1/level2/level3/mixed/config",
                            "__listkey": false,
                            "__listitem": true,
                            "__type": "string",
                            "__rootlevel": false
                        }
                    },
                    "nonconfig": {
                        "__value": null,
                        "__schema": {
                            "__config": false,
                            "__leaf": true,
                            "__path": "/level1/level2/level3/mixed/nonconfig",
                            "__listkey": false,
                            "__listitem": true,
                            "__type": "string",
                            "__rootlevel": false
                        }
                    }
                }
            }
        }
    },
    "simplelist": {
        "__listelement": {
            "__schema": {
                "__list": true,
                "__elements": {},
                "__path": "/simplelist",
                "__keys": "item",
                "__decendentconfig": true,
                "__decendentoper": true,
                "__rootlevel": true
            },
            "item": {
                "__value": null,
                "__schema": {
                    "__config": true,
                    "__leaf": true,
                    "__path": "/simplelist/item",
                    "__listitem": true,
                    "__listkey": true,
                    "__type": "string",
                    "__rootlevel": false
                }
            },
            "subitem": {
                "__value": null,
                "__schema": {
                    "__config": false,
                    "__leaf": true,
                    "__path": "/simplelist/subitem",
                    "__listkey": false,
                    "__listitem": true,
                    "__type": "string",
                    "__rootlevel": false
                }
            }
        }
    },
    "types": {
        "__schema": {
            "__path": "/types",
            "__container": true,
            "__decendentconfig": true,
            "__decendentoper": false,
            "__rootlevel": true
        },
        "number": {
            "__value": null,
            "__schema": {
                "__config": true,
                "__leaf": true,
                "__path": "/types/number",
                "__listkey": false,
                "__listitem": true,
                "__type": "uint8",
                "__rootlevel": false
            }
        },
        "biggernumber": {
            "__value": null,
            "__schema": {
                "__config": true,
                "__leaf": true,
                "__path": "/types/biggernumber",
                "__listkey": false,
                "__listitem": true,
                "__type": "uint16",
                "__rootlevel": false
            }
        },
        "bignumber": {
            "__value": null,
            "__schema": {
                "__config": true,
                "__leaf": true,
                "__path": "/types/bignumber",
                "__listkey": false,
                "__listitem": true,
                "__type": "uint32",
                "__rootlevel": false
            }
        },
        "hugenumber": {
            "__value": null,
            "__schema": {
                "__config": true,
                "__leaf": true,
                "__path": "/types/hugenumber",
                "__listkey": false,
                "__listitem": true,
                "__type": "uint64",
                "__rootlevel": false
            }
        },
        "secondlist": {
            "__listelement": {
                "__schema": {
                    "__list": true,
                    "__elements": {},
                    "__path": "/types/secondlist",
                    "__keys": "item",
                    "__decendentconfig": true,
                    "__decendentoper": false,
                    "__rootlevel": false
                },
                "item": {
                    "__value": null,
                    "__schema": {
                        "__config": true,
                        "__leaf": true,
                        "__path": "/types/secondlist/item",
                        "__listitem": true,
                        "__listkey": true,
                        "__type": "enumeration",
                        "__enum_values": [
                            "A",
                            "B"
                        ],
                        "__rootlevel": false
                    }
                },
                "thingwithdefault": {
                    "__value": null,
                    "__schema": {
                        "__config": true,
                        "__leaf": true,
                        "__path": "/types/secondlist/thingwithdefault",
                        "__listkey": false,
                        "__listitem": true,
                        "__type": "string",
                        "__default": "HELLO",
                        "__rootlevel": false
                    }
                },
                "innerlist": {
                    "__listelement": {
                        "__schema": {
                            "__list": true,
                            "__elements": {},
                            "__path": "/types/secondlist/innerlist",
                            "__keys": "item",
                            "__decendentconfig": true,
                            "__decendentoper": false,
                            "__rootlevel": false
                        },
                        "item": {
                            "__value": null,
                            "__schema": {
                                "__config": true,
                                "__leaf": true,
                                "__path": "/types/secondlist/innerlist/item",
                                "__listitem": true,
                                "__listkey": true,
                                "__type": "string",
                                "__rootlevel": false
                            }
                        }
                    }
                }
            }
        },
        "compositekeylist": {
            "__listelement": {
                "__schema": {
                    "__list": true,
                    "__elements": {},
                    "__path": "/types/compositekeylist",
                    "__keys": "keyA keyB",
                    "__decendentconfig": true,
                    "__decendentoper": false,
                    "__rootlevel": false
                },
                "keyA": {
                    "__value": null,
                    "__schema": {
                        "__config": true,
                        "__leaf": true,
                        "__path": "/types/compositekeylist/keyA",
                        "__listitem": true,
                        "__listkey": true,
                        "__type": "string",
                        "__rootlevel": false
                    }
                },
                "keyB": {
                    "__value": null,
                    "__schema": {
                        "__config": true,
                        "__leaf": true,
                        "__path": "/types/compositekeylist/keyB",
                        "__listitem": true,
                        "__listkey": true,
                        "__type": "string",
                        "__rootlevel": false
                    }
                }
            }
        }
    }
}""")
