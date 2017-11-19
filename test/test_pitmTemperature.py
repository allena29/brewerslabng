from mock import patch, Mock, call
import unittest
from pitmTemperature import pitmTemperature

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.subject = pitmTemperature()
        print 'setup fired'

    @patch('pitmTemperature.pitmTemperature._read_temperature_from_external_probe')
    @patch('pitmTemperature.pitmTemperature._get_probes_to_monitor')
    def test_getResult_first_valid_result(self, mockGetProbes, mockReadExternal):
       
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
       
        self.subject._log = Mock()

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
       
        self.subject._log = Mock()

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
       
        self.subject._log = Mock()

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
    
        # This result should be supressed
        mockReadExternal.return_value = (8.4, True)
        for c in range(2):
            self.subject.getResult()

        # Assert
        self.assertEqual(self.subject._log.call_count, 22)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['temperature'], 8.4)
        self.assertEqual(self.subject.currentTemperatures['fermentation-probe']['valid'], False)
        self.assertEqual(self.subject.lastResult['fermentation-probe'], 16.4)



if __name__ == '__main__':
    unittest.main()
