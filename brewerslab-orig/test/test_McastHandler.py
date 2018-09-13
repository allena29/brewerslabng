from mock import patch, Mock, call
import unittest
import time

from pitmMcastOperations import pitmMcast


class TestMcastOperations(unittest.TestCase):

    def setUp(self):
        self.subject = pitmMcast()
        self.subject.groot.log = Mock()


    def test_calculate_and_set_checksum(self):
        # Setup
        message = { 'hello' : 'world!' }

        # Action
        updated_message = self.subject._calculate_and_set_checksum(message)

        # Assert
        self.assertEqual(updated_message['_checksum'], '54440d7f0fc99b44e0cc6e0e0f4ef5abee11ad43')


    def test_checksum_with_a_tampered_message(self):
        # Setup
        message = { 'hello' : 'world!' }

        # Action
        updated_message = self.subject._calculate_and_set_checksum(message)
        updated_message['hello'] = 'tampered'

        result = self.subject._verify_checksum(updated_message)

        # Assert
        self.assertEqual(result, False)
        
    def test_checksum_with_a_message_which_has_not_been_messed_with(self):
        # Setup
        message = { 'hello' : 'world!' }

        # Action
        updated_message = self.subject._calculate_and_set_checksum(message)

        result = self.subject._verify_checksum(updated_message)

        # Assert
        self.assertEqual(result, True)
        

    def test_send_mcast_message(self):
        # Setup
        self.subject.sendSocket = Mock()
        
        message = { 'hello' : 'world!' }
        port = 1234
        app = 'unittest-app'

        # Action

        self.subject.send_mcast_message(message, port, app)

        # Assert
        json_decoded =self
