
import sys
import unittest
from mock import Mock
sys.path.append('../../')
import blng.VoodooX


class TestVoodoo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

    def test_get_root(self):
        session = blng.VoodooX.VoodooX()
        session.connect()
        root = session.get_root('voodoox', 'http://brewerslabng.mellon-collie.net/yang/vododoox')

        self.assertEqual(repr(root), 'VoodooXroot{http://brewerslabng.mellon-collie.net/yang/vododoox}/')

    def test_dir_of_node(self):
        session = blng.VoodooX.VoodooX()
        session.connect()
        root = session.get_root('voodoox', 'http://brewerslabng.mellon-collie.net/yang/vododoox')

        self.assertEqual(dir(root), ['bronze', 'morecomplex'])
