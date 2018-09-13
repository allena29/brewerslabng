import unittest
import os
import json
from mock import Mock, patch, ANY
import PyConfHoardExceptions
import builtins

import datastore


class TestPyConfHoardCLI(unittest.TestCase):

    def setUp(self):
        self.subject = datastore.Resource()

    @patch('os.path.exists')
    def test_rest_patch_method_if_we_cannot_get_a_lock(self, osPathExistMock):

        osPathExistMock.side_effect = [True]
        req = Mock()
        resp = Mock()
        datastore = 'running'
        path = 'NameOfThing'

        req.content_type = 'application/json'
        req.stream.read.side_effect = [
            """{}"""
        ]

        try:
            self.subject.on_patch(req, resp, datastore, path)
        except PyConfHoardExceptions.DataStoreLock as err:
            self.assertEqual('Failed to obtain lock - datastore running/NameOfThing is already locked', str(err))

    @patch('os.unlink')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_rest_patch_method_if_we_can_get_a_lock(self, osPathExistMock, openMock, osRemoveMock):
        osRemoveMock.return_value = Mock()
        openMock.return_value = dummyopen()
        osPathExistMock.side_effect = [
            False,  # lock exists on enter
            False,  # Existing data is present
            True,  # lock exists on exit
        ]
        req = Mock()
        resp = Mock()
        datastore = 'running'
        path = 'NameOfThing'

        request_json_body = """{
    "brewhouse": {
        "temperature": {
            "fermentation": {
                "setpoint": {
                    "__value": 17.0
                },
                "probe": {
                    "id": {
                        "__value": "28-0000"
                    }
                }
            }
        }
    }
}"""

        req.content_type = 'application/json'
        req.stream.read.side_effect = [
            request_json_body
        ]

        try:
            self.subject.on_patch(req, resp, datastore, path)
        except PyConfHoardExceptions.DataStoreLock as err:
            self.assertEqual('Failed to obtain lock - datastore running/NameOfThing is already locked', str(err))

        osRemoveMock.assert_called_once_with('datastore/running/NameOfThing.lock')
        self.assertEqual(resp.body, request_json_body)

    @patch('os.unlink')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_rest_patch_method_if_we_can_get_a_lock_and_the_data_already_existed(self, osPathExistMock, openMock, osRemoveMock):

        existingdata = Mock()
        existingdata.read.return_value = """{
    "brewhouse": {
        "temperature": {
            "fermentation": {
                "setpoint": {
                    "__value": null,
                    "__default": 17.0
                }
            }
        }
    }
}"""

        osRemoveMock.return_value = Mock()
        openMock.side_effect = [
            dummyopen(),  # creating the lock
            existingdata,
            dummyopen(),  # writing data after patch
        ]
        osPathExistMock.side_effect = [
            False,  # lock exists on enter
            True,  # Existing data is present
            True,  # lock exists on exit
        ]
        req = Mock()
        resp = Mock()
        datastore = 'running'
        path = 'NameOfThing'

        request_json_body = """{
    "brewhouse": {
        "temperature": {
            "fermentation": {
                "setpoint": {
                    "__value": 17.0
                },
                "probe": {
                    "id": {
                        "__value": "28-0000"
                    }
                }
            }
        }
    }
}"""

        req.content_type = 'application/json'
        req.stream.read.side_effect = [
            request_json_body
        ]

        try:
            self.subject.on_patch(req, resp, datastore, path)
        except PyConfHoardExceptions.DataStoreLock as err:
            self.assertEqual('Failed to obtain lock - datastore running/NameOfThing is already locked', str(err))

        osRemoveMock.assert_called_once_with('datastore/running/NameOfThing.lock')

        combined_body = """{
    "brewhouse": {
        "temperature": {
            "fermentation": {
                "setpoint": {
                    "__default": 17.0,
                    "__value": 17.0
                },
                "probe": {
                    "id": {
                        "__value": "28-0000"
                    }
                }
            }
        }
    }
}"""

        self.assertEqual(resp.body, combined_body)

    @patch('os.unlink')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_rest_patch_method_if_we_can_get_a_lock_and_the_data_already_existed(self, osPathExistMock, openMock, osRemoveMock):

        existingdata = Mock()
        existingdata.read.return_value = """{
    "brewhouse": {
        "temperature": {
            "fermentation": {
                "setpoint": {
                    "__value": null,
                    "__default": 17.0
                }
            },
            "othernode": {
                "__value": "abc123"
            }
        }
    }
}"""
        runningafter = dummyopen()
        persistafter = dummyopen()

        osRemoveMock.return_value = Mock()
        openMock.side_effect = [
            dummyopen(),  # creating the lock
            existingdata,
            runningafter,
            persistafter,
        ]
        osPathExistMock.side_effect = [
            False,  # lock exists on enter
            True,  # Existing data is present
            True,  # lock exists on exit
        ]
        req = Mock()
        resp = Mock()
        datastore = 'running'
        path = 'NameOfThing'

        request_json_body = """{
    "brewhouse": {
        "temperature": {
            "fermentation": {
                "setpoint": {
                    "__value": 17.0
                },
                "probe": {
                    "id": {
                        "__value": "28-0000"
                    }
                }
            }
        }
    }
}"""

        req.content_type = 'application/json'
        req.stream.read.side_effect = [
            request_json_body
        ]

        try:
            self.subject.on_patch(req, resp, datastore, path)
        except PyConfHoardExceptions.DataStoreLock as err:
            self.assertEqual('Failed to obtain lock - datastore running/NameOfThing is already locked', str(err))

        osRemoveMock.assert_called_once_with('datastore/running/NameOfThing.lock')

        combined_body = """{
    "brewhouse": {
        "temperature": {
            "fermentation": {
                "setpoint": {
                    "__default": 17.0,
                    "__value": 17.0
                },
                "probe": {
                    "id": {
                        "__value": "28-0000"
                    }
                }
            },
            "othernode": {
                "__value": "abc123"
            }
        }
    }
}"""

        # Check the updated payload is sent back to the client
        self.assertEqual(resp.body, combined_body)
        # Check the updated payload is written to the
        runningafter.write.assert_called_once_with(combined_body)
        # Check the updated payload is written to persist
        persistafter.write.assert_called_once_with(combined_body)

    @patch('os.unlink')
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_rest_patch_method_if_we_can_get_a_lock_and_the_operdata_already_existed(self, osPathExistMock, openMock, osRemoveMock):

        existingdata = Mock()
        existingdata.read.return_value = """{
 }"""
        operafter = dummyopen()

        osRemoveMock.return_value = Mock()
        openMock.side_effect = [
            dummyopen(),  # creating the lock
            existingdata,
            operafter,
        ]
        osPathExistMock.side_effect = [
            False,  # lock exists on enter
            True,  # Existing data is present
            True,  # lock exists on exit
        ]
        req = Mock()
        resp = Mock()
        datastore = 'operational'
        path = 'NameOfThing'

        request_json_body = """{
    "operational": 1
}"""

        req.content_type = 'application/json'
        req.stream.read.side_effect = [
            request_json_body
        ]

        try:
            self.subject.on_patch(req, resp, datastore, path)
        except PyConfHoardExceptions.DataStoreLock as err:
            self.assertEqual('Failed to obtain lock - datastore running/NameOfThing is already locked', str(err))

        osRemoveMock.assert_called_once_with('datastore/operational/NameOfThing.lock')

        # Check the updated payload is sent back to the client
        self.assertEqual(resp.body, request_json_body)
        # Check the updated payload is written to the
        operafter.write.assert_called_once_with(request_json_body)


class dummyopen:

    def __init__(self):
        self.write = Mock()
        self.read = Mock()
        self.close = Mock()
