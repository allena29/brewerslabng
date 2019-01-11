
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
        self.maxDiff = 4000
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

    def donttest_simple_types(self):
        """Test very basic primitive types"""
        xmldoc, newxmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_PRIMITIVE))
        received_answer = self.subject.pretty(xmldoc)
        received_answer2 = self.subject.pretty(newxmldoc)

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

        expected_answer2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <simpleleaf>
      <yin-schema path="/simpleleaf">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="simpleleaf">
    <type name="string"/>
  </leaf>
      </yin-schema>
    </simpleleaf>
    <simplecontainer>
      <yin-schema path="/simplecontainer">
        <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="simplecontainer">
    <presence value="true"/>
  </container>
      </yin-schema>
    </simplecontainer>
    <morecomplex>
      <yin-schema path="/morecomplex">
        <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="morecomplex">
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
      </yin-schema>
      <nonconfig>
        <yin-schema path="/morecomplex/nonconfig">
          <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="nonconfig">
      <type name="string"/>
      <config value="false"/>
    </leaf>
        </yin-schema>
      </nonconfig>
      <leaf2>
        <yin-schema path="/morecomplex/leaf2">
          <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf2">
      <type name="boolean"/>
    </leaf>
        </yin-schema>
      </leaf2>
      <inner>
        <yin-schema path="/morecomplex/inner">
          <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="inner">
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
        </yin-schema>
        <leaf5>
          <yin-schema path="/morecomplex/inner/leaf5">
            <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf5">
        <type name="string"/>
        <mandatory value="true"/>
      </leaf>
          </yin-schema>
        </leaf5>
        <leaf6>
          <yin-schema path="/morecomplex/inner/leaf6">
            <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf6">
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
        <mandatory value="false"/>
      </leaf>
          </yin-schema>
        </leaf6>
        <leaf7>
          <yin-schema path="/morecomplex/inner/leaf7">
            <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf7">
        <type name="string"/>
        <default value="this-is-a-default"/>
      </leaf>
          </yin-schema>
        </leaf7>
      </inner>
    </morecomplex>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/simpleleaf</path>
    <path>/simplecontainer</path>
    <path>/morecomplex</path>
    <path>/morecomplex/nonconfig</path>
    <path>/morecomplex/leaf2</path>
    <path>/morecomplex/inner</path>
    <path>/morecomplex/inner/leaf5</path>
    <path>/morecomplex/inner/leaf6</path>
    <path>/morecomplex/inner/leaf7</path>
  </crux-paths>
</crux-schema>
"""

        self.assertEqual(expected_answer, received_answer)
        self.assertEqual(expected_answer2, received_answer2)

    def donttest_grouping(self):
        """Test basic uses from in the same yang module"""
        xmldoc, newxmldoc = self.subject.munge("integrationtest", self._loadXmlDoc(resources.SCHEMA_USES))
        received_answer = self.subject.pretty(xmldoc)
        received_answer2 = self.subject.pretty(newxmldoc)

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

        expected_answer2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <group-a>
      <yin-schema path="/group-a"/>
    </group-a>
    <resolver>
      <yin-schema path="/resolver">
        <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="resolver">
    <leaf name="a">
      <type name="string"/>
    </leaf>
  </container>
      </yin-schema>
      <a>
        <yin-schema>
          <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="a">
      <type name="string"/>
    </leaf>
        </yin-schema>
      </a>
    </resolver>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/group-a</path>
    <path>/resolver</path>
  </crux-paths>
</crux-schema>
"""

        self.assertEqual(expected_answer, received_answer)
        self.assertEqual(expected_answer2, received_answer2)

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

    def donttest_pass1(self):
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

    def donttest_pass2_with_missing_map(self):
        """Test Pass2 with missing types which are not in the map"""
        # Build
        xmldoc = self._loadXmlDoc(resources.SCHEMA_1)

        # Act & Assert
        with self.assertRaises(Error.BlngYangTypeNotSupported) as context:
            self.subject.pass2_stitch_and_recurse(xmldoc)

    def donttest_pass2(self):
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
