
import sys
import unittest
from mock import Mock
sys.path.append('../../')
import blng.VoodooX


class TestVoodoo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

    def test_get_root(self):
        session = blng.VoodooX.VoodooX('crux-example.xml')
        session.connect()
        root = session.get_root('voodoox', 'http://brewerslabng.mellon-collie.net/yang/vododoox')

        self.assertEqual(repr(root), 'VoodooXroot{http://brewerslabng.mellon-collie.net/yang/vododoox}')
        expected_result_for_dir = ['bronze', 'container_and_lists', 'default', 'ghost', 'hyphen_leaf', 'lista',
                                   'morecomplex',
                                   'outsidelist', 'patternstr', 'psychedelia', 'quad', 'quarter',
                                   'resolver', 'simplecontainer',
                                   'simpleenum', 'simpleleaf', 'simplelist', 'thing_that_is_leafref',
                                   'thing_that_is_lit_up_for_A',
                                   'thing_that_is_lit_up_for_B', 'thing_that_is_lit_up_for_C',
                                   'thing_that_is_used_for_when', 'thing_to_leafref_against', 'twokeylist',
                                   'whencontainer']
        self.assertEqual(dir(root), expected_result_for_dir)

    def test_get(self):

        session = blng.VoodooX.VoodooX('crux-example.xml')
        session.connect()
        root = session.get_root('voodoox', 'http://brewerslabng.mellon-collie.net/yang/vododoox')

        simpleleaf = root.simpleleaf
        self.assertEqual(simpleleaf, 'CASPER-THE')

        simpleenum = root.simpleenum
        self.assertEqual(simpleenum, None)

        morecomplex = root.morecomplex
        self.assertEqual(dir(morecomplex), ['inner', 'leaf2', 'leaf3', 'leaf4', 'nonconfig'])

        self.assertEqual(morecomplex.leaf2, True)
