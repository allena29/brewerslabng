#!/usr/bin/python3

import argparse
from ncclient import manager
from lxml import etree
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


class cruxformat:

    def __init__(self):
        self.session = PromptSession()

        self.config_mode = False
        self.prompt = '> '

    @staticmethod
    def bottom_toolbar():
        return HTML('Connected')

    def welcome(self):
        while 1:
            try:
                #text = self.session.prompt(self.prompt, bottom_toolbar=cruxformat.bottom_toolbar)
                break
            except KeyboardInterrupt:
                continue
            except EOFError:
                break


class cruxli:

    def __init__(self, host='localhost', port='830', username='netconf', password='netconf'):
        self.netconf_capa = {}
        self.netconf = self._connect_netconf(host, port, username, password)

        self.cliformat = cruxformat()
        self.cliformat.welcome()

    def __del__(self):
        self._disconnect_netconf()

    def _disconnect_netconf(self):
        pass

    def _connect_netconf(self, host, port, username, password):
        """
        Connect to a given NETCONF host and verify that it has the CRUX YANG module installed.

        If a NETCONF server does indeed have the correct module installed it shuld provide a
        list of YANG Modules which are to be used with this CLI engine.

        <?xml version="1.0" encoding="UTF-8"?>
         <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
          <crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux">
           <modules>
            <module>brewerslab</module>
           </modules>
           <modules>
            <module>integrationtest</module>
           </modules>
          </crux-cli>
         </data>
        """

        netconf = manager.connect(host=host, port=port, username=username, password=password,
                                  hostkey_verify=False, allow_agent=False, look_for_keys=False,
                                  unknown_host_cb=lambda x: True)


        for capa in netconf.server_capabilities:
            c = capa.split('?')
            c.append('')
            self.netconf_capa[c[0]] = c[1]

        if not 'http://brewerslabng.mellon-collie.net/yang/crux' in self.netconf_capa:
            raise ValueError("NETCONF does not support crux protocol")

        filter = """<crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux"><modules></crux-cli>"""
        crux_modules = self._netconf_get_xml(netconf, filter)[0]
        for cm in crux_modules.getchildren():            
            module = None
            namespace = None
            for x in cm.getchildren():
                if x.tag == '{http://brewerslabng.mellon-collie.net/yang/crux}module':
                    module = x.text
                if x.tag == '{http://brewerslabng.mellon-collie.net/yang/crux}namespace':
                    namespace = x.text

            if module and namespace:
                if namespace not in self.netconf_capa:
                    raise ValueError('NETCONF server does expose %s %s' % (module, namespace))

        return netconf

    def _netconf_get_xml(self, netconf, filter, config=True, source='running'):
        filter_xml = """<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (filter)
        data_str = str(netconf.get_config(source=source, filter=filter_xml))
        return etree.fromstring(data_str.encode('UTF-8')).getchildren()[0]



cli = cruxli()
