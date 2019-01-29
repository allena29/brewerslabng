#!/usr/bin/python3

# import argparse
import logging
import sys
import time
from lxml import etree

from format import cruxformat
sys.path.append("../")
from blng import Yang
from blng import ChangeSet
from ncclient import manager
# from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
# from prompt_toolkit.validation import Validator, ValidationError
# from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


class cruxli:

    def __init__(self, host='localhost', port='830',
                 username='netconf', password='netconf'):

        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger('cli')
        self.changeset = None

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.cliformat = None
        self.yang_manager = Yang.Yang()

    def reset_cli(self):
        self.mode = 0
        self.exit = False

    def start_cli_session(self):
        self.reset_cli()
        self.netconf = self._connect_netconf(self.host, self.port, self.username, self.password)
        self.yang_manager.negotiate_netconf_capabilities(self.netconf)
        self.schema = etree.parse('.cache/__crux-schema.xml')

    def __del__(self):
        self._disconnect_netconf()

    def _disconnect_netconf(self):
        pass

    def attach_formatter(self, formatter):
        self.cliformat = formatter

    def _connect_netconf(self, host, port, username, password):
        """
        Connect to a given NETCONF host and verify that it has the CRUX
        YANG module installed.

        If a NETCONF server does indeed have the correct module installed
        it shuld provide a list of YANG Modules which are to be used with
        this CLI engine.

        <?xml version="1.0" encoding="UTF-8"?>
         <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
               xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
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

        netconf = manager.connect(host=host, port=port,
                                  username=username, password=password,
                                  hostkey_verify=False, allow_agent=False,
                                  look_for_keys=False,
                                  unknown_host_cb=lambda x: True)

        return netconf

    def _process_module(self, cm):
        module = None
        namespace = None
        revision = 'unspecified'
        tops = []
        for x in cm.getchildren():
            if x.tag == self.CRUX_NS + "module":
                module = x.text
            if x.tag == self.CRUX_NS + "namespace":
                namespace = x.text
            if x.tag == self.CRUX_NS + "revision":
                revision = x.text
            if x.tag == self.CRUX_NS + "top-level-tags":
                for t in x.getchildren():
                    if t.tag == self.CRUX_NS + "tag":
                        tops.append(t.text)

        if module and namespace:
            if namespace not in self.netconf_capa:
                raise ValueError('NETCONF server does expose %s %s' % (module,
                                                                       namespace))

        self.cli_modules[module] = namespace

        return (module, namespace, revision, tops)

    def _process_modules(self, netconf, crux_modules):
        """
        Process the list of modules given an XML structure representing the
        configuration of /crux-cli
        """
        for cm in crux_modules.getchildren():
            (module, namespace, revision, tops) = self._process_module(cm)

            for t in tops:
                if t in self.yang_manager.top_levels:
                    raise ValueError("Top-level tag %s is already registered to another namespace")
                self.log.debug("Registered new top-level tag %s to %s" % (t, namespace))
                self.yang_manager.top_levels[t] = namespace

            self.yang_manager.cache_schema(netconf, module, namespace, revision)

        for ym in self.yang_manager.netconf_capa:
            print("We need schema for %s" % (ym))

    def process_cli_line(self, line):
        """
        Called each time we process an operational line of CLI.
        """
        self.log.debug('Oper line into us: %s' % (line))
        if line[0:4] == "conf":
            self.log.debug("Switching into configuration mode")
            self.mode = 1
            self.changeset = ChangeSet.ChangeSet()

        elif line[0:4] == "show":
            self.log.debug("Show operation state")
        elif line[0:4] == "exit":
            self.log.debug("Exit required")
            self.exit = True
        elif line == "":
            pass
        else:
            self.cliformat.opermode_error(line)

    def process_config_cli_line(self, line):
        self.log.debug("Config line to use: %s" % (line))
        if line[0:4] == "exit":
            self.log.debug("Switching into operational mode")
            self.mode = 0

    def get_and_process_next_command(self):
        if self.mode:
            self.process_config_cli_line(self.cliformat.configmode_prompt())
        else:
            self.process_cli_line(self.cliformat.opermode_prompt())

    def loop(self):
        try:
            self.process_cli_line(self.cliformat.welcome())
            while not self.exit:
                try:
                    self.get_and_process_next_command()
                except KeyboardInterrupt:
                    pass
                except EOFError:
                    break
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass


if __name__ == '__main__':
    cli = cruxli()
    cli.attach_formatter(cruxformat())
    cli.start_cli_session()
    cli.loop()
