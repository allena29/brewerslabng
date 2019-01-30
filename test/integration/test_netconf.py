import unittest
from ncclient import manager
from lxml import etree

""""
from ncclient import manager
from lxml import etree

netconf = manager.connect(host='localhost', port=830,
                          username='netconf', password='netconf',
                          hostkey_verify=False, allow_agent=False,
                          look_for_keys=False,
                          unknown_host_cb=lambda x: True)

path="<integrationtest/>"
response = netconf.get_config(source='running', filter='<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>' % (path))
print(etree.tostring(response.data.getchildren()[0]))
"""


class TestNetconfAssumptions(unittest.TestCase):

    def setUp(self):
        if not hasattr(self, 'netconf'):
            self.netconf = manager.connect(host='localhost', port=830,
                                           username='netconf', password='netconf',
                                           hostkey_verify=False, allow_agent=False,
                                           look_for_keys=False,
                                           unknown_host_cb=lambda x: True)
        self.maxDiff = 400000
        # Replace /integrationtest
        setpath = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" nc:operation="replace">
        <resolver><a>AAA</a></resolver>
        </integrationtest>"""
        self.netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""", target="running")

        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <resolver>
    <a>AAA</a>
  </resolver>
</integrationtest>
"""
        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

    @staticmethod
    def pretty(xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def test_delete_string(self):
        setpath = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" nc:operation="replace">
        <morecomplex><leaf2>true</leaf2><leaf3>234234234</leaf3></morecomplex>
        </integrationtest>"""
        self.netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""", target="running")

        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        #raise ValueError(TestNetconfAssumptions.pretty(response.data.getchildren()[0]))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <morecomplex>
    <leaf2>true</leaf2>
    <leaf3>234234234</leaf3>
  </morecomplex>
</integrationtest>
"""
        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

        setpath = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
        <morecomplex><leaf2>false</leaf2><leaf3 nc:operation="delete"></leaf3></morecomplex>
        </integrationtest>"""

        self.netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""", target="running")

        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        #raise ValueError(TestNetconfAssumptions.pretty(response.data.getchildren()[0]))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <morecomplex>
    <leaf2>false</leaf2>
  </morecomplex>
</integrationtest>
"""
        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

        setpath = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
        <morecomplex nc:operation="delete"/>
        </integrationtest>"""

        self.netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""", target="running")

        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        self.assertEqual([], response.data.getchildren())

    def test_simple_setting(self):
            # Assert
        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <resolver>
    <a>AAA</a>
  </resolver>
</integrationtest>
"""

        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

    def test_setting_list_with_composite_keys(self):
        """
        ncclient.operations.rpc.RPCError: Invalid position of the key "A" in a list "multi-key-list".
        """
        # Set /integrationtest/leaf-a
        setpath = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
           <container-and-lists>
            <multi-key-list><A>AAaa</A><B>bbbbbooo</B></multi-key-list>
           </container-and-lists>
        </integrationtest>"""
        self.netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""", target="running")

        # Assert
        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <resolver>
    <a>AAA</a>
  </resolver>
  <container-and-lists>
    <multi-key-list>
      <A>AAaa</A>
      <B>bbbbbooo</B>
    </multi-key-list>
  </container-and-lists>
</integrationtest>
"""
        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

    def test_setting_and_filtered_gets(self):
        # Set /integrationtest/leaf-a
        setpath = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
           <resolver><leaf-a>234</leaf-a></resolver>
        </integrationtest>"""
        self.netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""", target="running")

        # Assert
        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <resolver>
    <a>AAA</a>
    <leaf-a>234</leaf-a>
  </resolver>
</integrationtest>
"""
        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

        # Add list item
        setpath = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
        <lista>
          <firstkey>ABC</firstkey>
        </lista>
        <simpleenum>A</simpleenum>
        </integrationtest>"""
        self.netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""", target="running")

        # Assert
        path = """<integrationtest/>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <resolver>
    <a>AAA</a>
    <leaf-a>234</leaf-a>
  </resolver>
  <lista>
    <firstkey>ABC</firstkey>
  </lista>
  <simpleenum>A</simpleenum>
</integrationtest>
"""

        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

        # Assert a diverse seleciton of things this should not include lista
        path = """ <integrationtest><resolver/><simpleenum/><integrationtest>"""
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <resolver>
    <a>AAA</a>
    <leaf-a>234</leaf-a>
  </resolver>
  <simpleenum>A</simpleenum>
</integrationtest>
"""

        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

        # We can send the Netconf server all our values (i.e. the previous expected_response
        path = expected_response
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))
        expected_response = """<integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <resolver>
    <a>AAA</a>
    <leaf-a>234</leaf-a>
  </resolver>
  <simpleenum>A</simpleenum>
</integrationtest>
"""

        self.assertEqual(expected_response, TestNetconfAssumptions.pretty(response.data.getchildren()[0]))

        # We can send the Netconf server all our values (i.e. the previous expected_response)
        # And if the value no longer is the same on the NETCONF server we will get no children
        path = expected_response.replace('A', 'B')
        response = self.netconf.get_config(source='running', filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))

        self.assertEqual([], response.data.getchildren())
        #
        #
        # In[74]: setpath = """<resolver xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><a>sad</a><leaf-a>X4</leaf-a></resolv
        #     ...: er>"""
        #
        # In[75]: netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""",
        #                             ...: target="running", error_option="rollback-on-error")
        # ---------------------------------------------------------------------------
