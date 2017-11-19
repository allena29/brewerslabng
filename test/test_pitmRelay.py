from mock import patch, Mock, call
import unittest
from pitmRelay import pitmRelay


class TestPitmRelay(unittest.TestCase):

    def setUp(self):
        self.subject = pitmRelay()
        self.subject._log = Mock()
        self.subject.lcdDisplay = Mock()
        self.subject.gpio = Mock()

    def test_callback_zome_temp_thread_when_idle(self):
        # Setup
        self.subject._mode = 'idle'
        cm = {
        }

        # Action
        self.subject.callback_zone_temp_thread(cm)

        # Assert
        self.assertEqual(self.subject._log.call_count, 0)


    def test_callback_zome_temp_thread_when_ferm_valid_result_HEATING(self):
        # Setup
        self.subject._mode = 'ferm'
        self.subject.cfg.fermProbe = 'ferm-probe'
        self.fridgeCompressDelay = 30
        self.subject.zoneTarget = 20
        self.subject.fridgeHeat = True
        self.subject._gpioFermHeat = True
        self.subject.fridgeCool = False
        self.subject._gpioFermCool = False
        cm = {
            'currentResult' : {
                self.subject.cfg.fermProbe : {
                    'valid' : True,
                    'temperature' : 19.0
                }
            }
        }

        # Action
        self.subject.callback_zone_temp_thread(cm)

        # Assert
        self.assertEqual(self.subject._log.call_count, 1)
        self.subject._log.assert_called_once_with('Temp: 19.0 Target: 20 fridgeHeat: True/True fridgeCool: False/False (delay True) ', importance=0)


if __name__ == '__main__':
    unittest.main()
