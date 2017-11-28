from mock import patch, Mock, call
import unittest
import time
from pitmButtonv2 import pitmButton


class TestPitmRelay(unittest.TestCase):

    def setUp(self):
        self.subject = pitmButton()
        self.subject.groot.log = Mock()
        self.subject.gpio = Mock()

    @patch("os.path.exists")
    def test_check_a_single_button_with_fakebutton_flag(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = True
        self.subject._set_ipc_flag = Mock()
        self.subject._remove_ipc_flag = Mock()

        # Action
        return_value = self.subject._check_a_single_button('myButton')

        # Assert
        self.assertEqual(return_value, True)


    @patch("os.path.exists")
    def test_check_a_single_button_without_fakebutton_flag_and_realbutton_not_pressed(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = False
        self.subject.gpio.input.return_value = False
        self.subject._set_ipc_flag = Mock()
        self.subject._remove_ipc_flag = Mock()

        # Action
        return_value = self.subject._check_a_single_button('myButton')

        # Assert
        self.assertEqual(return_value, False)


    @patch("os.path.exists")
    def test_check_a_single_button_without_fakebutton_flag_but_realbutton_pressed(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = False
        self.subject.gpio.input.return_value = True
        self.subject._set_ipc_flag = Mock()
        self.subject._remove_ipc_flag = Mock()

        # Action
        return_value = self.subject._check_a_single_button('myButton')

        # Assert
        self.assertEqual(return_value, True)


    def test_build_button_control_message(self):
        # Setup
        self.subject._check_a_single_button = Mock()
        self.subject._check_a_single_button.side_effect = [True, False, True, True, False, True]
        self.subject._set_ipc_flag = Mock()
        self.subject._remove_ipc_flag = Mock()

        # Action
        return_value = self.subject._build_button_control_message()

        # Assert
        self.assertEqual(return_value['_button']['swHlt'], True)
        self.assertEqual(return_value['_button']['swFerm'], False)
        self.assertEqual(return_value['_button']['swSparge'], True)
        self.assertEqual(return_value['_button']['swMash'], True)
        self.assertEqual(return_value['_button']['swBoil'], False)
        self.assertEqual(return_value['_button']['swPump'], True)


    @patch("__builtin__.open")
    def test_set_ipc_flag(self, openMock):
        # Action
        self.subject._set_ipc_flag('mybutton')

        # Assert
        openMock.assert_called_once_with('ipc/mybutton', 'w')


    @patch("os.remove")
    def test_remove_ipc_flag(self, removeMock):
        # Action
        self.subject._remove_ipc_flag('mybutton')

        # Assert
        removeMock.assert_called_once_with('ipc/mybutton')
