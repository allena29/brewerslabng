import unittest
import sys
sys.path.append('../../')
from blng import Munger
from example import resources


class TestCruxMunger(unittest.TestCase):

    SCHEMA_1 = resources.SCHEMA_1
    SCHEMA_2 = resources.SCHEMA_2

    def setUp(self):
        self.subject = Munger.Munger()

        yin_file = open(".cache/integrationtest.yin", "w")
        yin_file.write(self.SCHEMA_1)
        yin_file.close()

        yin_file = open(".cache/crux.yin", "w")
        yin_file.write(self.SCHEMA_2)
        yin_file.close()

    def test_munge_simplecase(self):
        self.subject.munge("integrationtest")
