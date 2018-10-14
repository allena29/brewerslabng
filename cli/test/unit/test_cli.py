import sys
sys.path.append('../../')
from mock import patch, Mock, call
import unittest
from cli import cruxli


class TestCruxLI(unittest.TestCase):

    def setUp(self):
        self.cruxformat = Mock()
        self.netconf = Mock()
        self.subject = cruxli()
        self.subject.attach_formatter(self.cruxformat)
        self.subject._connect_netconf = Mock()

    def test_basic(self):
        pass
