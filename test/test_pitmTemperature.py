from mock import patch, Mock
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


if __name__ == '__main__':
    unittest.main()
