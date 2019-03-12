
import os
import sys
import unittest
from lxml import etree
from mock import Mock
sys.path.append('../../')
from blng import Munger
from blng import Error
from example import resources
from answers import answers


class TestCruxMunger(unittest.TestCase):

    def _loadXmlDoc(self, schema_string):
        return etree.fromstring(schema_string.encode('UTF-8'))

    def setUp(self):
        self.maxDiff = 400000
        self.subject = Munger.Munger()
        if not os.path.exists('.cache/crux.yin'):
            yin_file = open(".cache/crux.yin", "w")
            yin_file.write(resources.SCHEMA_CRUX)
            yin_file.close()

        if not os.path.exists('.cache/integrationtest.yin'):
            yin_file = open('.cache/integrationtest.yin', 'w')
            yin_file.write(resources.SCHEMA_1)
            yin_file.close()

        self.subject.typedef_map = {}
        self.subject.replacements = []
        self.subject.grouping_map = {}

    def test_crux(self):
        """Test extension's are dropped from the result."""
        xmldoc, newxmldoc = self.subject.munge("crux", self._loadXmlDoc(resources.SCHEMA_CRUX))
        received_answer2 = self.subject.pretty(newxmldoc)
        self.assertEqual(answers.SCHEMA_CRUX_EXPECTED, received_answer2)

    def test_simple_types(self):
        """Test very basic primitive types"""
        xmldoc, newxmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_PRIMITIVE))
        received_answer = self.subject.pretty(xmldoc)
        received_answer2 = self.subject.pretty(newxmldoc)

        self.assertEqual(answers.SCHEMA_TYPES_EXPECTED1, received_answer)
        self.assertEqual(answers.SCHEMA_TYPES_EXPECTED2, received_answer2)

    def test_grouping(self):
        """Test basic uses from in the same yang module"""
        xmldoc, newxmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_USES))
        received_answer = self.subject.pretty(xmldoc)
        received_answer2 = self.subject.pretty(newxmldoc)

        self.assertEqual(answers.SCHEMA_GROUPING_EXPECTED1, received_answer)
        self.assertEqual(answers.SCHEMA_GROUPING_EXPECTED2, received_answer2)

    def test_munge_union_typedefs(self):
        """Test the basic resolution of typedefs within a union."""
        xmldoc, newxmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_UNION))
        received_answer = self.subject.pretty(xmldoc)
        received_answer2 = self.subject.pretty(newxmldoc)

        self.assertEqual(answers.SCHEMA_UNION_EXPECTED1, received_answer)
        self.assertEqual(answers.SCHEMA_UNION_EXPECTED2, received_answer2)

    def test_choice(self):
        """Test the basic munging of a yang choice/case"""
        xmldoc, newxmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_CHOICE))
        received_answer = self.subject.pretty(xmldoc)
        received_answer2 = self.subject.pretty(newxmldoc)
        self.assertEqual(answers.SCHEMA_CHOICE_EXPECTED1, received_answer)
        self.assertEqual(answers.SCHEMA_CHOICE_EXPECTED2, received_answer2)

    def test_when_and_leafref(self):
        """Test inclusion of when conditions"""
        xmldoc, newxmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_WHEN_LEAFREF))
        received_answer2 = self.subject.pretty(newxmldoc)
        self.assertEqual(answers.SCHEMA_CRUX_WHEN_LEAFREF, received_answer2)

    def test_pass1(self):
        # Build
        xmldoc = self._loadXmlDoc(resources.SCHEMA_1)

        # Act
        self.subject.pass1_parse_and_recurse('integrationtest', xmldoc)

        # Assert
        expected_dictkeys_typedef_map = ['integrationtest:type1', 'integrationtest:type2',
                                         'integrationtest:type3', 'integrationtest:type4', 'integrationtest:type-a']
        expected_dictkeys_grouping_map = ['integrationtest:group-a']

        self.assertEqual(expected_dictkeys_typedef_map, list(self.subject.typedef_map.keys()))
        self.assertEqual(expected_dictkeys_grouping_map, list(self.subject.grouping_map.keys()))

    def test_pass2_with_missing_map(self):
        """Test Pass2 with missing types which are not in the map"""
        # Build
        xmldoc = self._loadXmlDoc(resources.SCHEMA_1)

        # Act & Assert
        with self.assertRaises(Error.BlngYangTypeNotSupported) as context:
            self.subject.pass2_stitch_and_recurse(xmldoc)

    def test_pass2(self):
        """Test Pass2 with mis sing types which are not in the map"""
        # Build
        self.subject._lookup_method = Mock()
        xmldoc = self._loadXmlDoc(resources.SCHEMA_1)
        self.subject.pass1_parse_and_recurse('integrationtest', xmldoc)

        # Act
        self.subject.pass2_stitch_and_recurse(xmldoc)

        # Asserts here nee to be sensible based on the thing.i
        expected_replacement_list = []
        self.assertEqual(self.subject._lookup_method.call_count, 14)
