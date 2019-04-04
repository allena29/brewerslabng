from ncclient import manager
from ncclient.xml_ import *
import logging
import sys
import warnings
import re
warnings.simplefilter("ignore", DeprecationWarning)

logger = logging.getLogger('ncclient')
logger.setLevel('WARNING')

with manager.connect(host='localhost', port=830, username='netconf', password='netconf',
                     hostkey_verify=False, allow_agent=False, unknown_host_cb=lambda x: True,
                     look_for_keys=False) as m:

    print('Capabilities')
    for c in m.server_capabilities:
        print(c)
    print('')

    print('Schema')
    print(m.get_schema('integrationtest'))

    print('Running configuration')
    url = "http://brewerslabng.mellon-collie.net/yang/integrationtest"
    xpath = "/x:simpleleaf"
    filter = """<nc:filter type="xpath" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" """
    filter = filter + """ xmlns:x="%s" select="%s" />""" % (url, xpath)
    print(m.get_config(source='running', filter=filter))

    print('Edit configuration')
    xml = """
    <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <simpleleaf xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">ABC987</simpleleaf>
    </nc:config>
    """
    print(m.edit_config(xml, target='running'))

    print('Running configuration again')
    filter = """<simpleleaf xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>"""
    filter_xml = """<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (filter)
    print(m.get_config(source='running', filter=filter_xml))
