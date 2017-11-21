from mock import patch, Mock, call
import unittest
import time
from pitmRelay import pitmRelay


class TestPitmRelay(unittest.TestCase):

    def setUp(self):
        self.subject = pitmRelay()
        self.subject.groot.log = Mock()
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
        self.assertEqual(self.subject.groot.log.call_count, 0)


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
        self.assertEqual(self.subject.groot.log.call_count, 1)
        self.subject.groot.log.assert_called_once_with('Temp: 19.0 Target: 20 fridgeHeat: True/True fridgeCool: False/False (delay True) ', importance=0)


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
        self.assertEqual(self.subject.groot.log.call_count, 1)
        self.subject.groot.log.assert_called_once_with('Temp: 19.0 Target: 18 fridgeHeat: False/False fridgeCool: True/True (delay False) ', importance=0)


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
        self.assertEqual(self.subject.groot.log.call_count, 0)
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
        self.assertEqual(self.subject.groot.log.call_count, 0)

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
        self.subject.groot.log.assert_called_once_with('Temp Target is invalid %s,%s,%s' % (cm['tempTargetFerm']), importance=2)

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
        self.subject.groot.log.assert_called_once_with('Temp Target is invalid %s,%s,%s' % (cm['tempTargetFerm']), importance=2)

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
        self.subject.groot.log.assert_called_once_with('Temp Target is invalid %s,%s,%s' % (cm['tempTargetFerm']), importance=2)


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
            call("recircfan", 0),
            call("extractor", 0),
            call("fermHeat", 0)
        ]

        self.subject.gpio.output.assert_has_calls(calls)
        self.assertEqual(self.subject._gpioFermCool, False)
        self.assertEqual(self.subject._gpioFermHeat, False)
        self.assertEqual(self.subject._gpiorecircfan, False)
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
        self.subject.groot.log.assert_called_with("Critical: no valid readings for 100 seconds")
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
        self.subject._safety_check_for_missing_readings = Mock()
        self.subject._lastValidReading['ferm'] = time.time() - 5

        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._safety_check_for_missing_readings.assert_called_once()


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
        # Setup
        self.subject._turn_cooling_off = Mock()
        self.subject._turn_heating_off = Mock()

        # Action
        self.subject._disable_ferm_control()

        # Assert
        self.subject._turn_cooling_off.assert_called_once()
        self.subject._turn_heating_off.assert_called_once()

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

    @patch("os.path.exists")
    def test_is_heating_required_flag_present(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = True

        # Action
        return_value = self.subject._is_heating_required()

        # Assert
        self.assertEqual(return_value, False)

    @patch("os.path.exists")
    def test_is_heating_required_flag_present_temp_high(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = True
        self.subject.zoneTemp = 5
        self.subject.fridgeHeat = False

        # Action
        return_value = self.subject._is_heating_required()

        # Assert
        self.assertEqual(return_value, False)


    @patch("os.path.exists")
    def test_is_heating_required_flag_NOT_present_temp_high(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = False
        self.subject.zoneTemp = 30
        self.subject.zoneUpTarget = 20
        self.subject.fridgeHeat = False

        # Action
        return_value = self.subject._is_heating_required()

        # Assert
        self.assertEqual(return_value, False)

    @patch("os.path.exists")
    def test_is_heating_required_flag_NOT_present_temp_low(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = False
        self.subject.zoneTemp = 5
        self.subject.zoneUpTarget = 20
        self.subject.fridgeHeat = False

        # Action
        return_value = self.subject._is_heating_required()

        # Assert
        self.assertEqual(return_value, True)


    @patch("os.path.exists")
    def test_is_cooling_required_flag_present(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = True

        # Action
        return_value = self.subject._is_cooling_required()

        # Assert
        self.assertEqual(return_value, False)

    @patch("os.path.exists")
    def test_is_cooling_required_flag_present_temp_high(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = True
        self.subject.zoneTemp = 59
        self.subject.zoneDownTarget = 40
        self.subject.fridgeCool = False

        # Action
        return_value = self.subject._is_cooling_required()

        # Assert
        self.assertEqual(return_value, False)

    @patch("os.path.exists")
    def test_is_cooling_required_flag_NOT_present_temp_high(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = False
        self.subject.zoneTemp = 59
        self.subject.zoneDownTarget = 40
        self.subject.fridgeCool = False

        # Action
        return_value = self.subject._is_cooling_required()

        # Assert
        self.assertEqual(return_value, True)


    @patch("os.path.exists")
    def test_is_cooling_required_flag_NOT_present_temp_low(self, pathExistsMock):
        # Setup
        pathExistsMock.return_value = False
        self.subject.zoneTemp = 20
        self.subject.zoneDownTarget = 40
        self.subject.fridgeCool = False

        # Action
        return_value = self.subject._is_cooling_required()

        # Assert
        self.assertEqual(return_value, False)

    def test_turn_heating_on(self):
        # Action
        self.subject._turn_heating_on()

        # Assert
        self.subject.lcdDisplay.sendMessage.assert_called_once_with(" Heating", 2)
        self.subject.gpio.output.assert_called_once_with('fermHeat', 1)
        self.assertEqual(self.subject.fermHeatActiveFor> -1, True)


    def test_turn_cooling_on(self):
        # Action
        self.subject._turn_cooling_on()

        # Assert
        self.subject.lcdDisplay.sendMessage.assert_called_once_with(" Cooling", 2)
        self.subject.gpio.output.assert_called_once_with('fermCool', 1)
        self.assertEqual(self.subject.fermCoolActiveFor> -1, True)


    def test_turn_cooling_off(self):
        # Seup
        self.subject.meterFermC = 10
        self.subject.fermCoolActiveFor = time.time() - 500 

        # Action
        self.subject._turn_cooling_off()

        # Assert
        self.subject.gpio.output.assert_called_once_with('fermCool', 0)
        self.assertEqual(self.subject.fridgeCompressorDelay, 300)
        self.assertEqual(self.subject.meterFermC > 500, True)
        self.subject.groot.log.assert_called_once()
        self.assertEqual(self.subject.fermCoolActiveFor, -1)

    def test_turn_heating_off(self):
        # Seup
        self.subject.meterFermH = 10
        self.subject.fermHeatActiveFor = time.time() - 500 

        # Action
        self.subject._turn_heating_off()

        # Assert
        self.subject.gpio.output.assert_called_once_with('fermHeat', 0)
        self.assertEqual(self.subject.meterFermH > 500, True)
        self.subject.groot.log.assert_called_once()
        self.assertEqual(self.subject.fermHeatActiveFor, -1)


    def test_run_recirc_fan_off(self):
        # Action
        self.subject._turn_recirc_fan_off()

        # Assert
        self.subject.gpio.output.assert_called_once_with('recircfan', 0)

    def test_run_recirc_fan_on(self):
        # Action
        self.subject._turn_recirc_fan_on()

        # Assert
        self.subject.gpio.output.assert_called_once_with('recircfan', 1)

    def test_saftey_check_for_compressor(self):
        # Setup
        self.subject.fridgeCompressorDelay=400
        self.subject._turn_cooling_off = Mock()
        # Action
        return_value = self.subject._safety_check_will_starting_the_fridge_damage_the_compressor()

        # Assert
        self.assertEqual(return_value, True)
        self.subject.lcdDisplay.sendMessage.assert_called_once()
        self.subject._turn_cooling_off.assert_called_once()

    def test_saftey_check_for_compressor_all_ok(self):
        # Setup
        self.subject.fridgeCompressorDelay=0
        
        # Action
        return_value = self.subject._safety_check_will_starting_the_fridge_damage_the_compressor()

        # Assert
        self.assertEqual(return_value, False)
        self.subject.lcdDisplay.sendMessage.assert_not_called()
        self.subject.gpio.output.assert_not_called()

    def test_safety_check_has_frige_been_running_too_long(self):
        # Setup
        self.subject._turn_cooling_off = Mock()
        self.subject.fermCoolActiveFor = time.time() - 2500

        # Action
        return_value = self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off()

        # Assert
        self.assertEqual(return_value, True)
        self.subject._turn_cooling_off.assert_called_once()
        self.assertEqual(self.subject.fridgeCompressorDelay, 601)


    def test_safety_check_has_frige_been_running_too_long_hardly_run_at_all_yet(self):
        # Setup
        self.subject._turn_cooling_off = Mock()
        self.subject.fermCoolActiveFor = time.time() - 2

        # Action
        return_value = self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off()

        # Assert
        self.assertEqual(return_value, False)
        self.subject._turn_cooling_off.assert_not_called()
        self.assertNotEqual(self.subject.fridgeCompressorDelay, 601)

    
    def test_zone_ferm_heating_required(self):
        # Setup
        self.subject.zoneTemp = 19
        self.subject.zoneTarget = 20
        self.subject.zoneUpTarget = 19.5
        self.subject._safety_check_for_missing_readings = Mock()
        self.subject._safety_check_for_unrealistic_readings = Mock()
        self.subject._turn_cooling_off = Mock()
        self.subject._turn_heating_on = Mock()
        self.subject._turn_recirc_fan_on = Mock()

        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._safety_check_for_missing_readings.assert_called_once()
        self.subject._safety_check_for_unrealistic_readings.assert_called_once()
        self.subject._turn_cooling_off.assert_called_once()
        self.subject._turn_heating_on.assert_called_once()
        self.subject._turn_recirc_fan_on.assert_called_once()
    
    def test_zone_ferm_cooling_required(self):
        # Setup
        self.subject.zoneTemp = 21
        self.subject.zoneTarget = 20
        self.subject.zoneDownTarget = 20.5
        self.subject.fermCoolActiveFor = -1
        self.subject._safety_check_for_missing_readings = Mock()
        self.subject._safety_check_for_unrealistic_readings = Mock()
        self.subject._turn_heating_off = Mock()
        self.subject._turn_cooling_on = Mock()
        self.subject._turn_recirc_fan_on = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor.return_value = False
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off = Mock()
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off.return_value = False


        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._safety_check_for_missing_readings.assert_called_once()
        self.subject._safety_check_for_unrealistic_readings.assert_called_once()
        self.subject._turn_cooling_on.assert_called_once()
        self.subject._turn_heating_off.assert_called_once()
        self.subject._turn_recirc_fan_on.assert_called_once()

    
    def test_zone_ferm_cooling_required_compressor_overrun_kics_inn(self):
        # Setup
        self.subject.zoneTemp = 21
        self.subject.zoneTarget = 20
        self.subject.zoneDownTarget = 20.5
        self.subject.fermCoolActiveFor = time.time() - 2000
        self.subject._safety_check_for_missing_readings = Mock()
        self.subject._safety_check_for_unrealistic_readings = Mock()
        self.subject._turn_heating_off = Mock()
        self.subject._turn_cooling_on = Mock()
        self.subject._turn_cooling_off = Mock()
        self.subject._turn_recirc_fan_off = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor.return_value = False
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off = Mock()
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off.return_value = True


        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._safety_check_for_missing_readings.assert_called_once()
        self.subject._safety_check_for_unrealistic_readings.assert_called_once()
        self.subject._turn_heating_off.assert_called_once()
        self.subject._turn_recirc_fan_off.assert_called_once()


    
    def test_zone_ferm_cooling_required_compressor_protection_kicks_in(self):
        # Setup
        self.subject.zoneTemp = 21
        self.subject.zoneTarget = 20
        self.subject.zoneDownTarget = 20.5
        self.subject.fermCoolActiveFor = -1
        self.subject._safety_check_for_missing_readings = Mock()
        self.subject._safety_check_for_unrealistic_readings = Mock()
        self.subject._turn_heating_off = Mock()
        self.subject._turn_cooling_on = Mock()
        self.subject._turn_cooling_off = Mock()
        self.subject._turn_recirc_fan_off = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor.return_value = True
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off = Mock()
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off.return_value = False


        # Action
        self.subject._zone_ferm()

        # Assert
        self.subject._safety_check_for_missing_readings.assert_called_once()
        self.subject._safety_check_for_unrealistic_readings.assert_called_once()
        self.subject._turn_heating_off.assert_called_once()
        self.subject._turn_recirc_fan_off.assert_called_once()


    def test_zone_ferm_target_reached_when_heating(self):
        self.subject.zoneTemp = 20.45210002
        self.subject.fridgeHeat = True
        self.subject.zoneTarget = 20
        self.subject._safety_check_for_missing_readings = Mock()
        self.subject._safety_check_for_unrealistic_readings = Mock()
        self.subject._turn_heating_off = Mock()
        self.subject._turn_cooling_off = Mock()
        self.subject._turn_recirc_fan_off = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor = Mock()
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off = Mock()
        
        # Action
        self.subject._zone_ferm()

        # Assert
        self.assertEqual(self.subject._turn_cooling_off.call_count > 0, True)
        self.assertEqual(self.subject._turn_heating_off.call_count > 0, True)
        self.assertEqual(self.subject._turn_recirc_fan_off.call_count > 0, True)


    def test_zone_ferm_target_reached_when_cooling(self):
        self.subject.zoneTemp = 19.299
        self.subject.fridgeCool = True
        self.subject.zoneTarget = 20
        self.subject._safety_check_for_missing_readings = Mock()
        self.subject._safety_check_for_unrealistic_readings = Mock()
        self.subject._turn_heating_off = Mock()
        self.subject._turn_cooling_off = Mock()
        self.subject._turn_recirc_fan_off = Mock()
        self.subject._safety_check_will_starting_the_fridge_damage_the_compressor = Mock()
        self.subject._safety_check_has_fridge_been_running_too_long_if_so_turn_off = Mock()
        
        # Action
        self.subject._zone_ferm()

        # Assert
        self.assertEqual(self.subject._turn_cooling_off.call_count > 0, True)
        self.assertEqual(self.subject._turn_heating_off.call_count > 0, True)
        self.assertEqual(self.subject._turn_recirc_fan_off.call_count > 0, True)


if __name__ == '__main__':
    unittest.main()
