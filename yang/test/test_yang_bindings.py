import unittest
import sys
sys.path.append('../../confvillain')

from binding import brewerslab


class TestYang(unittest.TestCase):

    def test_fermentation(self):
        yang = brewerslab()
        self.subject = yang.brewhouse.temperature

        self.assertEqual(self.subject.fermentation.results.latest, 0.0)
        self.assertEqual(self.subject.fermentation.results.average.minute, 0.0)
        self.assertEqual(self.subject.fermentation.results.average.hourly, 0.0)
        self.assertEqual(self.subject.fermentation.results.average.daily, 0.0)
        self.assertEqual(self.subject.fermentation.monitor, 0.0)
        # Note: pyangbind doesn't create objects with default value
        # although there are methods to test/retreive default
        self.assertEqual(self.subject.fermentation.setpoint, 0.0)
        self.assertEqual(self.subject.fermentation.highpoint, 0.0)
        self.assertEqual(self.subject.fermentation.lowpoint, 0.0)
        probe1 = self.subject.hardware.probe.add('123-456')

        offset1 = probe1.offsets.add('0 99')
        offset1.offset = 0.05
        offset2 = probe1.offsets.add('100 99999')
        offset2.offset = 0.1
