import unittest
import sys
sys.path.append('../../')
from blng import Resolver


class TestCruxResolver(unittest.TestCase):

    SCHEMA_1 = """<?xml version="1.0" encoding="UTF-8"?>
<module name="integrationtest"
        xmlns="urn:ietf:params:xml:ns:yang:yin:1"
        xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest"
        xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <import module="crux">
    <prefix value="crux"/>
  </import>
  <typedef name="type1">
    <type name="string">
      <pattern value="brew[a-z]*">
        <error-message>
          <value>String must start with brew</value>
        </error-message>
      </pattern>
    </type>
  </typedef>
  <typedef name="type2">
    <type name="uint32"/>
  </typedef>
  <typedef name="type3">
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  </typedef>
  <typedef name="type4">
    <type name="union">
      <type name="type3"/>
      <type name="type2"/>
    </type>
  </typedef>
  <leaf name="simpleleaf">
    <type name="string"/>
  </leaf>
  <container name="simplecontainer">
    <presence value="true"/>
  </container>
  <list name="simplelist">
    <key value="simplekey"/>
    <leaf name="simplekey">
      <type name="string"/>
    </leaf>
    <leaf name="nonleafkey">
      <crux:info>
        <crux:text>A non-leaf key</crux:text>
      </crux:info>
      <type name="uint32"/>
      <description>
        <text>ABC</text>
      </description>
    </leaf>
  </list>
  <container name="morecomplex">
    <leaf name="nonconfig">
      <crux:info>
        <crux:text>A non-configuration node</crux:text>
      </crux:info>
      <type name="string"/>
      <config value="false"/>
    </leaf>
    <leaf name="leaf2">
      <crux:info>
        <crux:text>must be 1 or 0 dont sit on the fence</crux:text>
      </crux:info>
      <type name="boolean"/>
    </leaf>
    <leaf name="leaf3">
      <crux:info>
        <crux:text>Should allow a string starting with brew - but no spaces</crux:text>
      </crux:info>
      <type name="type2"/>
    </leaf>
    <leaf name="leaf4">
      <crux:info>
        <crux:text>Should allow A, B, C or a uint32</crux:text>
      </crux:info>
      <type name="type4"/>
    </leaf>
    <container name="inner">
      <presence value="true"/>
      <leaf name="leaf5">
        <type name="string"/>
        <mandatory value="true"/>
      </leaf>
      <leaf name="leaf6">
        <type name="string"/>
        <mandatory value="false"/>
      </leaf>
      <leaf name="leaf7">
        <type name="string"/>
        <default value="this-is-a-default"/>
      </leaf>
    </container>
  </container>
</module>"""

    def setUp(self):
        self.subject = Resolver.Resolver()
        self.subject.register_top_tag("simpleleaf", "http://brewerslabng.mellon-collie.net/yang/integrationtest")

        yin_file = open(".cache/integrationtest.yin", "w")
        yin_file.write(self.SCHEMA_1)
        yin_file.close()

    # def test_basic_lookup_of_a_top_level(self):
    #    self.subject.show('')

    def test_load_simple_schema(self):
        """Basic test of loeading a schema"""
        # Act
        self.subject.load_schema_to_memory('simpleleaf', 'integrationtest')

        # Assert
        self.assertEqual(list(self.subject.in_memory.keys()), ['integrationtest'])

    def test_show(self):
        """
        Basic test of showing everything from the top level
        """

        (cmd, xpath, value) = self.subject.resolve("show")
        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/")
        self.assertEqual(value, None)
        (cmd, xpath, value) = self.subject.resolve("show simpleleaf")

        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(value, None)

        (cmd, xpath, value) = self.subject.resolve("set simpleleaf \"abc 1234\"")
        self.assertEqual(cmd, "set")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(value, "abc 1234")
