
import sys
import unittest
from mock import Mock
sys.path.append('../../')
import blng.VoodooX


class TestVoodoo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

    def test_convert_path_to_xml_filter(self):
        subject = blng.VoodooX.VoodooXInternal()
        subject.namespace = 'http://ns'

        result = subject._convert_path_to_xml_filter('/abc/def/ghi')
        expected_result = """<abc xmlns="http://ns"><def><ghi></ghi></def></abc>"""
        self.assertEqual(result, expected_result)

        result = subject._convert_path_to_xml_filter('/abc')
        expected_result = """<abc xmlns="http://ns"></abc>"""
        self.assertEqual(result, expected_result)

        result = subject._convert_path_to_xml_filter("/abc/def[x='y',a='b',c='d']/fgh")
        expected_result = """<abc xmlns="http://ns"><def><fgh><x>y</x><a>b</a><c>d</c></fgh></def></abc>"""
        self.assertEqual(result, expected_result)
