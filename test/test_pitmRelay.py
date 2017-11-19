from mock import patch, Mock, call
import unittest
import time
from pitmRelay import pitmRelay


class TestPitmRelay(unittest.TestCase):

    def setUp(self):
        self.subject = pitmRelay()
        self.subject._log = Mock()
        self.subject.lcdDisplay = Mock()
        self.subject.gpio = Mock()
        self.subject.zoneTemp = 20

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


    def test_callback_zome_temp_thread_when_ferm_valid_result_COOLING(self):
        # Setup
        self.subject._mode = 'ferm'
        self.subject.cfg.fermProbe = 'ferm-probe'
        self.subject.fridgeCompressorDelay = 0
        self.subject.zoneTarget = 18
        self.subject.fridgeHeat = False
        self.subject._gpioFermHeat = False
        self.subject.fridgeCool = True
        self.subject._gpioFermCool = True
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
        self.subject._log.assert_called_once_with('Temp: 19.0 Target: 18 fridgeHeat: False/False fridgeCool: True/True (delay False) ', importance=0)


    def test_callback_zome_temp_thread_when_ferm_valid_result_TEMP_ERROR(self):
        # Setup
        self.subject._mode = 'ferm'
        self.subject.cfg.fermProbe = 'ferm-probe'
        self.subject.fridgeCompressorDelay = 0
        self.subject.zoneTarget = 18
        self.subject.fridgeHeat = False
        self.subject._gpioFermHeat = False
        self.subject.fridgeCool = True
        self.subject._gpioFermCool = True
        cm = {
            'currentResult' : {
                self.subject.cfg.fermProbe : {
                    'valid' : False,
                }
            }
        }

        # Action
        self.subject.callback_zone_temp_thread(cm)

        # Assert
        self.assertEqual(self.subject._log.call_count, 0)
        self.subject.lcdDisplay.sendMessage.assert_called_once_with('Temp Result Error', 2)


    def test_callback_zome_temp_thread_when_ferm_update_targets(self):

        HEAT_AT_TEMP = 10.1
        COOL_AT_TEMP = 29.9
        TARGET_TEMP = 20.0

        # Setup
        self.subject._mode = 'idle'
        cm = {
            'tempTargetFerm' : (HEAT_AT_TEMP, COOL_AT_TEMP, TARGET_TEMP)
        }

        # Action
        self.subject.callback_zone_temp_thread(cm)

        # Assert
        self.assertEqual(self.subject.zoneUpTarget, HEAT_AT_TEMP)
        self.assertEqual(self.subject.zoneDownTarget, COOL_AT_TEMP)
        self.assertEqual(self.subject.zoneTarget, TARGET_TEMP)
        self.assertEqual(self.subject._log.call_count, 0)

    def test_callback_zome_temp_thread_when_ferm_update_targets_INVALID(self):
        HEAT_AT_TEMP = 4.5
        COOL_AT_TEMP = 29.9
        TARGET_TEMP = 20.0

        # Setup
        self.subject._mode = 'idle'
        cm = {
            'tempTargetFerm' : (HEAT_AT_TEMP, COOL_AT_TEMP, TARGET_TEMP)
        }

        # Action
        self.subject.callback_zone_temp_thread(cm)

        # Assert
        self.subject._log.assert_called_once_with('Temp Target is invalid %s,%s,%s' % (cm['tempTargetFerm']), importance=2)

    def test_callback_zome_temp_thread_when_ferm_update_targets_INVALID_2(self):
        HEAT_AT_TEMP = 10.4
        COOL_AT_TEMP = 4.4
        TARGET_TEMP = 20.0

        # Setup
        self.subject._mode = 'idle'
        cm = {
            'tempTargetFerm' : (HEAT_AT_TEMP, COOL_AT_TEMP, TARGET_TEMP)
        }

        # Action
        self.subject.callback_zone_temp_thread(cm)

        # Assert
        self.subject._log.assert_called_once_with('Temp Target is invalid %s,%s,%s' % (cm['tempTargetFerm']), importance=2)

    def test_callback_zome_temp_thread_when_ferm_update_targets_INVALID_3(self):
        HEAT_AT_TEMP = 10.4
        COOL_AT_TEMP = 24.4
        TARGET_TEMP = 4

        # Setup
        self.subject._mode = 'idle'
        cm = {
            'tempTargetFerm' : (HEAT_AT_TEMP, COOL_AT_TEMP, TARGET_TEMP)
        }

        # Action
        self.subject.callback_zone_temp_thread(cm)

        # Assert
        self.subject._log.assert_called_once_with('Temp Target is invalid %s,%s,%s' % (cm['tempTargetFerm']), importance=2)


    def test_zoneThread_mode_idle(self):
        # Setup
        self.subject._mode = 'idle'
        self.subject._zone_idle_shutdown = Mock()

        # Action
        self.subject._do_zone_thread()

        # Assert
        self.subject._zone_idle_shutdown.assert_called_once()

    def test_zoneThread_mode_shutdown(self):
        # Setup
        self.subject._mode = 'idle'
        self.subject._zone_idle_shutdown = Mock()

        # Action
        self.subject._do_zone_thread()

        # Assert
        self.subject._zone_idle_shutdown.assert_called_once()

    def test_zone_idle_shutdown(self):
        # Action
        self.subject._zone_idle_shutdown()

        # Assert
        calls = [
            call("fermCool", 0),
            call("reircfan", 0),
            call("extractor", 0),
            call("fermHeat", 0)
        ]

        self.subject.gpio.output.assert_has_calls(calls)
        self.assertEqual(self.subject._gpioFermCool, False)
        self.assertEqual(self.subject._gpioFermHeat, False)
        self.assertEqual(self.subject._gpioreircfan, False)
        self.assertEqual(self.subject._gpioExtractor, False)
        self.assertEqual(self.subject.fridgeHeat, False)
        self.assertEqual(self.subject.fridgeCool, False)


    def test_zoneThread_mode_boil(self):
        # Setup
        self.subject._mode = 'boil'
        self.subject._zone_boil = Mock()

        # Action
        self.subject._do_zone_thread()

        # Assert
        self.subject._zone_boil.assert_called_once()

    def test_zone_boil(self):
        # Action
        self.subject._zone_boil()

        # Assert
        calls = [
            call("fermHeat", 0),
            call("fermCool", 0),
            call("extractor", 1)
        ]

        self.subject.gpio.output.assert_has_calls(calls)
        self.assertEqual(self.subject._gpioFermCool, False)
        self.assertEqual(self.subject._gpioFermHeat, False)
        self.assertEqual(self.subject._gpioExtractor, True)
        self.assertEqual(self.subject.fridgeHeat, False)
        self.assertEqual(self.subject.fridgeCool, False)


    def test_zoneThread_mode_ferm_first_time_around(self):
        # Setup
        self.subject._mode = 'ferm'
        self.subject._zone_ferm = Mock()

        # Action
        self.subject._do_zone_thread()

        # Assert
        self.subject._zone_ferm.assert_called_once()

        self.assertEqual(self.subject._lastValidReading['ferm'] > -1, True)

    def test_ferm_safetycheck_for_missing_readings(self):
        # Setup
        self.subject._lastValidReading['ferm'] = time.time() - 500

        # Action
        return_value = self.subject._safety_check_for_missing_readings()

        # Assert
        self.subject._log.assert_called_with("Critical: no valid readings for 100 seconds")
        self.subject.gpio.output.assert_has_calls([
            call('fermHeat', 0),
            call('fermCool', 0),
            call('recircfan', 0)
        ])
        self.assertEqual(self.subject._gpioFermCool, False)
        self.assertEqual(self.subject._gpioFermHeat, False)
        self.assertEqual(self.subject.fridgeCompressorDelay, 300)

        self.subject.lcdDisplay.sendMessage.assert_called_once_with('CRITICAL Temp Result Error', 2)

        self.assertEqual(return_value, False)


    def test_ferm_safetycheck_for_missing_readings_when_everything_is_awesome(self):
        # Setup
        self.subject._lastValidReading['ferm'] = time.time() - 5

        # Action
        return_value = self.subject._safety_check_for_missing_readings()

        # Assert
        self.assertEqual( self.subject.gpio.output.call_count, 0)
        self.assertEqual(return_value, True)
    


    def test_zone_ferm(self):
        # Setup
        self.subject._lastValidReading['ferm'] = time.time() - 5

        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._safety_check_for_missing_readings()


    def test_zone_ferm_with_missing_readings(self):
        # Setup
        self.subject._lastValidReading['ferm'] = time.time() - 500
        # Action

        self.subject._zone_ferm()

        # Assert
        self.subject._safety_check_for_missing_readings()
        #TODO:


    @patch("os.path.exists")
    def test_zone_ferm_no_ferm_control_flag_present(self, pathexistsMock):
        # Setup
        pathexistsMock.return_value = True
        self.subject._disable_ferm_control = Mock()
        self.subject._safety_check_for_missing_readings = Mock()

        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._disable_ferm_control.assert_called_once()


    @patch("os.path.exists")
    def test_zone_ferm_no_ferm_control_flag_NOT_present(self, pathexistsMock):
        # Setup
        pathexistsMock.return_value = False
        self.subject._disable_ferm_control = Mock()
        self.subject._safety_check_for_missing_readings = Mock()

        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._disable_ferm_control.assert_not_called()

    def test_zone_ferm_dsiable_ferm_control(self):
        # Action
        self.subject._disable_ferm_control()

        # Assert
        self.subject.gpio.output.assert_has_calls([
            call('fermHeat', 0),
            call('recircfan', 0),
            call('fermCool', 0)
        ])
        self.assertEqual(self.subject._gpioFermCool, False)
        self.assertEqual(self.subject._gpioFermHeat, False)
        self.assertEqual(self.subject.fridgeCompressorDelay, 300)

    def test_safety_check_for_unrealistic_readings_79(self):
        # Setup
        self.subject.zoneTemp = 79

        # Action
        return_value = self.subject._safety_check_for_unrealistic_readings()

        # Assert
        self.assertEqual(return_value, False)

    def test_safety_check_for_unrealistic_readings_2(self):
        # Setup
        self.subject.zoneTemp = 2

        # Action
        return_value = self.subject._safety_check_for_unrealistic_readings()

        # Assert
        self.assertEqual(return_value, False)

    def test_safety_check_for_unrealistic_readings_20(self):
        # Action
        return_value = self.subject._safety_check_for_unrealistic_readings()

        # Assert
        self.assertEqual(return_value, True)

    def test_zone_ferm_with_unrealistic_values_79(self):
        # Setup
        self.subject.zoneTemp = 79
        self.subject._lastValidReading['ferm'] = time.time() - 50

        # Action
        return_value = self.subject._zone_ferm()

        # Assert
        # TODO

    def test_zone_ferm_with_unrealistic_values_3(self):
        # Setup
        self.subject.zoneTemp = 3
        self.subject._lastValidReading['ferm'] = time.time() - 50

        # Action
        return_value = self.subject._zone_ferm()

        # Assert
        # TODO

if __name__ == '__main__':
    unittest.main()
