from mock import patch, Mock, call
import unittest
from pitmTemperature import pitmTemperature


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.subject = pitmTemperature()
        self.subject._log = Mock()

    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_first_valid_result(self, mockGetProbes, mockReadExternal, mockTime):

        self.subject._log = Mock()

        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (12.4, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('Accepting result 12.4 lastResult 0 (Adjusted by 0)')

    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_many_values_all_valid(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (12.4, True)

        # Action
        for c in range(10):
            self.subject.getResult()

        # Assert
        self.assertEqual(self.subject._log.call_count, 10)

    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_many_values_with_invalid_values(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (12.4, True)

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
        self.assertEqual(self.subject._log.call_count, 23)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['temperature'], 12.4)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['valid'], True)
        self.assertEqual(self.subject.lastResult['fermentation-probe'], 12.4)

    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_many_values_with_invalid_values_that_stick(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (12.4, True)

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
        self.assertEqual(self.subject._log.call_count, 22)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['temperature'], 12.39)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['valid'], False)
        self.assertEqual(self.subject.lastResult['fermentation-probe'], 16.4)


    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_with_adjustment_made_second_in_list(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (12.4, True)

        self.subject.cfg.probeAdjustments = {
            'fermentation-probe' : [(5, 10, 1.5), (10, 20, 2), (30, 40, 3)]
        }

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('Accepting result 14.4 lastResult 0 (Adjusted by 2)')


    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_with_adjustment_made_first_in_list(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (5.4, True)

        self.subject.cfg.probeAdjustments = {
            'fermentation-probe' : [(5, 10, 1.5), (10, 20, 2)]
        }

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('Accepting result 6.9 lastResult 0 (Adjusted by 1.5)')


    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_with_adjustment_made(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (12.4, True)

        self.subject.cfg.probeAdjustments = {
            'fermentation-probe' : [(5, 10, 1.5), (10, 20, 2)]
        }

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('Accepting result 14.4 lastResult 0 (Adjusted by 2)')



    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_with_adjustments_defined_but_not_in_range(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (52.4, True)

        self.subject.cfg.probeAdjustments = {
            'fermentation-probe' : [(5, 10, 1.5), (10, 20, 2)]
        }

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('Accepting result 52.4 lastResult 0 (Adjusted by 0)')



    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_with_first_reading_at_85(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (85, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('rejecting result fermentation-probe 85 (reason: 85 indicates mis-read)')



    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_with_reading_at_85_previous_valid_reading(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        self.subject.lastResult['fermentation-probe'] = 84.9
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (85, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('Accepting result 85 lastResult 84.9 (Adjusted by 0)')


    @patch('time.sleep')
    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_with_reading_at_85_previous_valid_reading_2(self, mockGetProbes, mockReadExternal, mockTime):
        # Setup
        self.subject.lastResult['fermentation-probe'] = 85.1
        mockGetProbes.return_value = ['fermentation-probe']
        self.subject.probesToMonitor['fermentation-probe'] = True
        mockReadExternal.return_value = (85, True)

        # Action
        self.subject.getResult()

        # Assert
        self.subject._log.assert_called_once_with('Accepting result 85 lastResult 85.1 (Adjusted by 0)')




    @patch('os.path.exists')
    @patch('__builtin__.open')
    def test_submission_with_override_ferm_active(self, mockOpen, mockExists):
        # Build
        self.subject._loop_multicast_socket = False
        self.subject.sock = Mock()
        self.subject.sock.recvfrom.return_value = ' '*1200
        mockExists.side_effect = [ True, False ]
               
        self.subject.submission()


        self.assertEqual(self.subject._targetFerm, (16.7, 17.3, 17.0))

if __name__ == '__main__':
    unittest.main()
