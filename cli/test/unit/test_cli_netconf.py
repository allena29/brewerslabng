import unittest
import sys
sys.path.append('../../')
from mock import patch, Mock, call
from cli import cruxli
from lxml import etree


class TestCruxLI(unittest.TestCase):

    CRUX_CLI_XML = """
<crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux">
  <modules>
          <module>brewerslab</module>
          <namespace>http://brewerslabng.mellon-collie.net/yang/main</namespace>
  </modules>
  <modules>
          <module>integrationtest</module>
          <namespace>http://brewerslabng.mellon-collie.net/yang/integrationtest</namespace>
          <top-level-tags>
                <tag>simpleleaf</tag>
          </top-level-tags>
  </modules>
</crux-cli>
    """

    def setUp(self):
        self.cruxformat = Mock()
        self.netconf = Mock()
        self.subject = cruxli()
        self.subject.attach_formatter(self.cruxformat)
        self.subject._connect_netconf = Mock()

    def test_netconf_negotiation(self):
        """
        This is an example when we have valid data in the crux-cli module
        """
        # Build
        self.subject._process_module = Mock()
        self.subject._process_module.side_effect = [
            ("brewerslab", "http://brewerslabng.mellon-collie.net/yang/main",
             "unspecified", []),
            ("integrationtest",
             "http://brewerslabng.mellon-collie.net/yang/integrationtest",
             "unspecified", ["simpleleaf"])
        ]
        self.subject.netconf_capa['http://brewerslabng.mellon-collie.net/yang/main'] = {}
        self.subject.netconf_capa['http://brewerslabng.mellon-collie.net/yang/integrationtest'] = {}
        crux_modules = etree.fromstring(self.CRUX_CLI_XML)[0]

        # Act
        self.subject._process_modules(self.netconf, crux_modules)

    def test_netconf_negotiation_with_unregistered_netconf_module(self):
        """
        The CRUX CLI metadata can always provide a definition asking for
        support of YANG modules which are not actually on the NETCONF server
        """
        # Build
        self.subject._process_module = Mock()
        self.subject._process_module.side_effect = [
            ('abc', 'http://123', '2018-01-01', ['top-tag1', 'top-tag2'])
        ]
        crux_modules = etree.fromstring(self.CRUX_CLI_XML)[0]

        # Act
        with self.assertRaises(ValueError):
            self.subject._process_modules(self.netconf, crux_modules)

    def test_basic(self):
        pass
