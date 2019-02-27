
import os
import sys
import unittest
from mock import Mock
sys.path.append('../../')
import blng.Voodoo


class TestVoodoo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

    def _get_session(self):
        self.subject = blng.Voodoo.DataAccess('crux-example.xml')
        self.root = self.subject.get_root()
        return self.root

    def test_basic_list(self):
        root = self._get_session()

        listelement = root.simplelist.create('Shamanaid')
        self.assertEqual(repr(listelement), 'VoodooListElement: /simplelist')

        expected_hits = ['nonleafkey', 'simplekey']
        self.assertEqual(dir(listelement), expected_hits)

    def test_basic_dir(self):
        root = self._get_session()

        expected_hits = ['inner', 'leaf2', 'leaf3', 'leaf4', 'nonconfig']
        self.assertEqual(dir(root.morecomplex), expected_hits)

    def test_basic_repr(self):
        root = self._get_session()

        node = root.morecomplex
        self.assertEqual(repr(node), "VoodooContainer: /morecomplex")
        self.assertEqual(repr(node.inner), "VoodooContainer: /morecomplex/inner")

        node = root.morecomplex.leaf2
        node = "x123"
        self.assertEqual(repr(node), "'x123'")

    def test_basic_session_leaf(self):
        root = self._get_session()

        value = root.simpleleaf
        self.assertEqual(value, None)

        root.simpleleaf = 'ABC123'
        value = root.simpleleaf
        self.assertEqual(value, 'ABC123')

    def test_basic_session_setup(self):
        self._get_session()

        self.assertEqual(repr(self.root), "VoodooRoot")
