from mock import patch, Mock, call
import unittest
from TemperatureProviderDs18B20 import TemperatureProviderDs18B20


class TestTempProviderDs18B20(unittest.TestCase):

    def setUp(self):
        self.subject = TemperatureProviderDs18B20('TemperatureDs18B20', 'brewerslab', '/brewhouse/temperature',
                                                  open_stored_config=False)
        self.subject.log = Mock()

        # Add some default data to /brewhouse/temperature/hardware/probes
        hardware = self.subject.get_config('/hardware')[0]
        self.probe_ferm = hardware.probe.add('fermentation-probe')
        probe_other = hardware.probe.add('other-probe')

        offset1 = self.probe_ferm.offsets.add('5 10')
        offset1.offset = 1.5
        offset2 = self.probe_ferm.offsets.add('10 20')
        offset2.offset = 2
        offset_for_wrong_probe = probe_other.offsets.add('50 70')
        offset_for_wrong_probe.offset = 59

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_first_valid_result(self, mockGetProbes, mockReadExternal, mockTime):

        self.subject._log = Mock()

        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (12.4, True)
        # For this test we do not want any offset
        self.probe_ferm.offsets.delete('5 10')
        self.probe_ferm.offsets.delete('10 20')

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('Accepting result 12.4 lastResult 0 (Adjusted by 0)')

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_many_values_all_valid(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (12.4, True)

        # Action
        for c in range(10):
            self.subject.getResult()

        # Assert
        self.assertEqual(self.subject.log.info.call_count, 10)

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_many_values_with_invalid_values(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (12.4, True)

        self.probe_ferm.offsets.delete('5 10')
        self.probe_ferm.offsets.delete('10 20')

        # Action
        for c in range(10):
            self.subject.getResult()

        # These temperatures should be ignored because there were not enough of them
        # to believe the external probe.
        mockReadExternal.return_value = (16.4, True)
        for c in range(3):
            self.subject.getResult()

        mockReadExternal.return_value = (12.4, True)
        for c in range(10):
            self.subject.getResult()

        # Assert
        self.assertEqual(self.subject.log.info.call_count, 23)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['temperature'], 12.4)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['valid'], True)
        self.assertEqual(self.subject.lastResult['fermentation-probe'], 12.4)

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_many_values_with_invalid_values_that_stick(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (12.4, True)

        self.probe_ferm.offsets.delete('5 10')
        self.probe_ferm.offsets.delete('10 20')

        # Action
        for c in range(10):
            self.subject.getResult()

        # This result should be believed after we have more than some bad result
        mockReadExternal.return_value = (16.4, True)
        for c in range(10):
            self.subject.getResult()

        # This result should be supressed because it deviates too much
        mockReadExternal.return_value = (12.39, True)
        for c in range(2):
            self.subject.getResult()

        # Assert
        self.assertEqual(self.subject.log.info.call_count, 22)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['temperature'], 12.39)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['valid'], False)
        self.assertEqual(self.subject.lastResult['fermentation-probe'], 16.4)

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_with_adjustment_made_second_in_list(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (12.4, True)

        offset3 = self.probe_ferm.offsets.add('30 40')
        offset3.offset = 3

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('Accepting result 14.4 lastResult 0 (Adjusted by 2.0)')

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_with_adjustment_made_first_in_list(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (5.4, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('Accepting result 6.9 lastResult 0 (Adjusted by 1.5)')

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_with_adjustment_made(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (12.4, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('Accepting result 14.4 lastResult 0 (Adjusted by 2.0)')

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_with_adjustments_defined_but_not_in_range(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (52.4, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('Accepting result 52.4 lastResult 0 (Adjusted by 0)')

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_with_first_reading_at_85(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (85, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('rejecting result fermentation-probe 85 (reason: 85 indicates mis-read)')

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_with_reading_at_85_previous_valid_reading(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        self.subject.lastResult['fermentation-probe'] = 84.9
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (85, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('Accepting result 85 lastResult 84.9 (Adjusted by 0)')

    @patch('time.sleep')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._read_temperature_from_external_probe')
    @patch('TemperatureProviderDs18B20.TemperatureProviderDs18B20._get_probes_to_monitor')
    def test_getResult_with_reading_at_85_previous_valid_reading_2(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        self.subject.lastResult['fermentation-probe'] = 85.1
        mockGetProbes.return_value = ['fermentation-probe']
        mockReadExternal.return_value = (85, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject.log.info.assert_called_once_with('Accepting result 85 lastResult 85.1 (Adjusted by 0)')
