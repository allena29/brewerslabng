
import sys
import unittest
from mock import Mock
sys.path.append('../../')
import blng.VoodooX


class TestVoodoo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

    def _get_internal(self):
        internal = blng.VoodooX.VoodooXInternal('crux-example.xml')
        internal.namespace = 'http://ns'
        internal.parentnode = 'voodoox'
        internal.data = Mock()
        return internal

    def _fake_element(self, tag, attrib=None, text=None):
        element = Mock()
        element.tag = tag
        element.attrib = attrib
        element.text = text
        return element

    def test_root(self):
        internal = self._get_internal()

        root = blng.VoodooX.VoodooXroot(internal, '/', '/')
        root._getschema = Mock()
        root._getchildren = Mock(return_value=[self._fake_element('b'), self._fake_element('c')])

        self.assertEqual(repr(root), 'VoodooXroot{http://ns}')

        internal.data.getchildren.return_value = [self._fake_element('{http://ns}b'),
                                                  self._fake_element('{http://ns}c')]
        self.assertEqual(dir(root), ['b', 'c'])

    def test_convert_path_to_xml_filter(self):
        subject = self._get_internal()

        result = subject._convert_path_to_xml_filter('/abc/def/ghi')
        expected_result = """<abc xmlns="http://ns"><def><ghi></ghi></def></abc>"""
        self.assertEqual(result, expected_result)

        result = subject._convert_path_to_xml_filter('/abc')
        expected_result = """<abc xmlns="http://ns"></abc>"""
        self.assertEqual(result, expected_result)

        result = subject._convert_path_to_xml_filter("/abc/def[x='y',a='b',c='d']/fgh")
        expected_result = """<abc xmlns="http://ns"><def><fgh><x>y</x><a>b</a><c>d</c></fgh></def></abc>"""
        self.assertEqual(result, expected_result)
