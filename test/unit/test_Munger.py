
import os
import sys
import unittest
from lxml import etree
from mock import Mock
sys.path.append('../../')
from blng import Munger
from blng import Error
from example import resources


class TestCruxMunger(unittest.TestCase):

    def _loadXmlDoc(self, schema_string):
        return etree.fromstring(schema_string.encode('UTF-8'))

    def setUp(self):
        self.maxDiff = 4000
        self.subject = Munger.Munger()
        if not os.path.exists('.cache/crux.yin'):
            yin_file = open(".cache/crux.yin", "w")
            yin_file.write(resources.SCHEMA_CRUX)
            yin_file.close()
        self.subject.typedef_map = {}
        self.subject.replacements = []
        self.subject.grouping_map = {}

    def test_simple_types(self):
        """Test very basic primitive types"""
        xmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_PRIMITIVE))
        received_answer = self.subject.pretty(xmldoc)
        expected_answer = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <leaf name="simpleleaf">
    <type name="string"/>
  </leaf>
  <container name="simplecontainer">
    <presence value="true"/>
  </container>
  <container name="morecomplex">
    <leaf name="nonconfig">
      <type name="string"/>
      <config value="false"/>
    </leaf>
    <leaf name="leaf2">
      <type name="boolean"/>
    </leaf>
    <container name="inner">
      <presence value="true"/>
      <leaf name="leaf5">
        <type name="string"/>
        <mandatory value="true"/>
      </leaf>
      <leaf name="leaf6">
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
        <mandatory value="false"/>
      </leaf>
      <leaf name="leaf7">
        <type name="string"/>
        <default value="this-is-a-default"/>
      </leaf>
    </container>
  </container>
</module>
"""
        self.assertEqual(expected_answer, received_answer)

    def test_grouping(self):
        """Test basic uses from in the same yang module"""
        xmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_USES))
        received_answer = self.subject.pretty(xmldoc)
        expected_answer = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <grouping name="group-a">
    </grouping>
  <container name="resolver">
    <leaf name="a">
      <type name="string"/>
    </leaf>
  </container>
</module>
"""
        self.assertEqual(expected_answer, received_answer)

    def test_munge_union_typedefs(self):
        """Test the basic resolution of typedefs within a union."""
        xmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_UNION))
        received_answer = self.subject.pretty(xmldoc)
        expected_answer = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <typedef name="type2">
    </typedef>
  <typedef name="type3">
    </typedef>
  <leaf name="uuuuuuuu">
    <type name="union">
      <type name="string"/>
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  <type name="uint32"/>
  </type>
  </leaf>
</module>
"""
        self.assertEqual(expected_answer, received_answer)

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
