import unittest
import os
from mock import Mock
import sys
from lxml import etree
sys.path.append('../../')
from blng import ChangeSet
from blng import Error
from example import resources


class TestChangeSet(unittest.TestCase):

    DEFAULT_XMLDOC = """<?xml version="1.0" encoding="UTF-8"?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><simpleleaf>HELLO THERE!!!!</simpleleaf></integrationtest></data>"""

    @staticmethod
    def pretty(xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def setUp(self):
        self.schema = open('.cache/__crux-schema.xml').read()
        self.subject = ChangeSet.ChangeSet(self.schema)
        self.xmldoc = self.subject._get_xmldoc_without_xmlns(self.DEFAULT_XMLDOC)

    def test_opening_transactions(self):
        self.subject.begin_transaction(self.DEFAULT_XMLDOC)
        self.subject.begin_transaction(self.DEFAULT_XMLDOC)

        self.assertNotEqual(self.subject.transaction['xmldoc'], None)
        self.assertNotEqual(self.subject.transaction['originalxmldoc'], None)
        self.assertEqual(self.subject.transaction['keypaths'], {})

    def test_create_xml_nodes_based_on_path_simple_string(self):
        self.subject._create_elements('/data/integrationtest/resolver/leaf-a', self.xmldoc)

        expected_answer = """<data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <integrationtest>
    <simpleleaf>HELLO THERE!!!!</simpleleaf>
    <resolver>
      <leaf-a/>
    </resolver>
  </integrationtest>
</data>
"""

    def test_create_xml_nodes_based_on_path_simple_list(self):
        self.subject._create_elements("/data/integrationtest/simplelist[simplekey='ABC123']", self.xmldoc)

        expected_answer = """<data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <integrationtest>
    <simpleleaf>HELLO THERE!!!!</simpleleaf>
    <simplelist>
      <simplekey>ABC123</simplekey>
    </simplelist>
  </integrationtest>
</data>
"""
        self.assertEqual(expected_answer, TestChangeSet.pretty(self.xmldoc))

    def test_create_xml_nodes_based_on_path_composite_key_list(self):
        """
        This is a more complex case of creating a list item where the list has slightly different
        list entries already existing - however they doin't entirely match the keys so in the
        final XML DOC we should have a 4th entrie of [A='aaaa',B='bbbb'] with the inner container.
        """
        xmlstr = """<?xml version="1.0" encoding="UTF-8"?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
        <container-and-lists>
            <multi-key-list><A>aaaa</A><B>but-no-matching-b</B></multi-key-list>
            <multi-key-list><A>not-matching-a</A><B>not-matching-b</B></multi-key-list>
            <multi-key-list><A>not-matching-a</A><B>bbbb</B></multi-key-list>
        </container-and-lists>
        </integrationtest></data>"""
        xmldoc = self.subject._get_xmldoc_without_xmlns(xmlstr)

        self.subject._create_elements("/data/integrationtest/container-and-lists/multi-key-list[A='aaaa',B='bbbb']/inner/C", xmldoc)

        expected_answer = """<data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <integrationtest>
        <container-and-lists>
            <multi-key-list><A>aaaa</A><B>but-no-matching-b</B></multi-key-list>
            <multi-key-list><A>not-matching-a</A><B>not-matching-b</B></multi-key-list>
            <multi-key-list><A>not-matching-a</A><B>bbbb</B></multi-key-list>
        <multi-key-list><A>aaaa</A><B>bbbb</B><inner><C/></inner></multi-key-list></container-and-lists>
        </integrationtest>
</data>
"""
        self.assertEqual(expected_answer, TestChangeSet.pretty(xmldoc))

    def test_create_xml_based_on_nested_lists(self):
        self.subject._create_elements("/data/integrationtest/list-a[firstkey='primary']/listb[secondkey='secondary',thirdkey='tertiary']/nonkey", self.xmldoc)

        expected_answer = """<data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <integrationtest>
    <simpleleaf>HELLO THERE!!!!</simpleleaf>
    <list-a>
      <firstkey>primary</firstkey>
      <listb>
        <secondkey>secondary</secondkey>
        <thirdkey>tertiary</thirdkey>
        <nonkey/>
      </listb>
    </list-a>
  </integrationtest>
</data>
"""
        self.assertEqual(expected_answer, TestChangeSet.pretty(self.xmldoc))

    # def test_extracting_xpath_key_values(self):
    #     self.subject = ChangeSet.ChangeSet(None)
    #
    #     xmldoc = self.subject._get_xmldoc_without_xmlns(self.DEFAULT_XMLDOC)
    #
    #     #self.subject._extract_xpath_keys_and_create_in_xmldoc("/sdf/sdf/sdfsdf[asdfsdf='sdfsdf',asdasd='sdfsdf2sdf']/dsfsdf/dsfsdf/[dsf='sdf']/sdf", xmldoc)
    #     self.subject._extract_xpath_keys_and_create_in_xmldoc("/integrationtest/simplelist[simplekey='dsfsdf']", xmldoc)

    def test_setting_value_list(self):
        self.subject = ChangeSet.ChangeSet(self.schema)
        trans_id = self.subject.begin_transaction(
            """<?xml version="1.0" encoding="UTF-8"?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><simpleleaf>HELLO THERE!!!!</simpleleaf></integrationtest></data>"""
        )

        self.subject.modify("/integrationtest/simpleleaf", "bac")
        self.subject.modify("/integrationtest/simplelist[simplekey='sdf']/nonleafkey", "bac")
        print(self.subject.frame_netconf_xml())
        # '/data/'+'/integrationtest/simpleleaf', 'bac')

    def test_setting_value_simple_leaf(self):
        self.subject = ChangeSet.ChangeSet(self.schema)
        trans_id = self.subject.begin_transaction(
            """<?xml version="1.0" encoding="UTF-8"?><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"><integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><simpleleaf>HELLO THERE!!!!</simpleleaf></integrationtest></data>"""
        )

        self.subject.modify("/integrationtest/simpleleaf", "bac")

        framed_xml = self.subject.frame_netconf_xml()

        expected_framed_xml = """<data xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <integrationtest>
    <simpleleaf>bac</simpleleaf>
  </integrationtest>
</data>
"""

        self.assertEqual(expected_framed_xml, framed_xml)
