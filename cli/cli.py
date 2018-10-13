#!/usr/bin/python3

import argparse
import hashlib
import logging
import os
import time
from ncclient import manager
from lxml import etree
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


class cruxformat:

    """
    This class is responsible for providing the cosmetic appearance of the command line interface, the behaviour itself is defined
    in cruxli. Much of the presentation options here are goverend by prompt_toolkit

    The command line interface has two basic modes, operational and configuration mode.
    """

    DEFAULT_OPER_COMMANDS = {
        'configure': 'enter configuration mode',
        'exit':      'exit from the CLI interface',
        'show':      'operational status'
    }

    def __init__(self):
        self.session = PromptSession()
        self.config_mode = False
        self.prompt = 'brewer@localhost> '

    @staticmethod
    def bottom_toolbar():
        return HTML('Connected')

    def welcome(self):
        print('Welcome to BREWERS COMMAND LINE INTERFACE')
        return self.opermode_prompt()

    def opermode_prompt(self):
        return self.session.prompt(self.prompt, bottom_toolbar=cruxformat.bottom_toolbar, completer=self.get_oper_mode_command_list(), complete_while_typing=True, validate_while_typing=True, auto_suggest=AutoSuggestFromHistory())

    def get_oper_mode_command_list(self):
        return WordCompleter(self.DEFAULT_OPER_COMMANDS.keys())

    def opermode_error(self, line):
        """
        When a user makes a mistake within operational mode provide some guidance to the user including a
        list of commands that are valid
        """
        print('%s\nError: expecting...\n' % (line))
        for command in self.DEFAULT_OPER_COMMANDS:
            print('%s%s - %s' % (command, ' '*(10-len(command)), self.DEFAULT_OPER_COMMANDS[command]))
        print("[error][%s]" % (self.get_time()))

    def get_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

class cruxli:

    def __init__(self, host='localhost', port='830', username='netconf', password='netconf'):

        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger('cli')
        transport_log = logging.getLogger('ncclient.transport.ssh')
        transport_log.level = logging.ERROR
        rpc_log = logging.getLogger('cclient.operations.rpc')
        rpc_log.level = logging.ERROR
        session_log = logging.getLogger('ncclient.transport.session')
        session_log.level = logging.ERROR

        self.netconf_capa = {}

        self.netconf = self._connect_netconf(host, port, username, password)
        self.cliformat = cruxformat()

        self.mode = 0
        self.exit = False

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
            self.netconf_capa[c[0]] = {'module': c[1]}

        if not 'http://brewerslabng.mellon-collie.net/yang/crux' in self.netconf_capa:
            raise ValueError("NETCONF does not support crux protocol")

        filter = """<crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux"><modules></crux-cli>"""
        crux_modules = self._netconf_get_xml(netconf, filter)[0]
        for cm in crux_modules.getchildren():
            module = None
            namespace = None
            revision = 'unspecified'
            for x in cm.getchildren():
                if x.tag == '{http://brewerslabng.mellon-collie.net/yang/crux}module':
                    module = x.text
                if x.tag == '{http://brewerslabng.mellon-collie.net/yang/crux}namespace':
                    namespace = x.text
                if x.tag == '{http://brewerslabng.mellon-collie.net/yang/crux}revision':
                    revision = x.text

            if module and namespace:
                if namespace not in self.netconf_capa:
                    raise ValueError('NETCONF server does expose %s %s' % (module, namespace))

            id = "%s-%s-%s" % (module, namespace, revision)
            hash = hashlib.sha1(id.encode('UTF-8')).hexdigest()
            self.netconf_capa[namespace]['id'] = hash
            if os.path.exists('.cache/%s.schema' % (hash)):
                self.log.debug('We have a cached version of the schema %s/%s' % (id, hash))
                print('already have %s' % (hash))
            else:
                self.log.debug('We do not have a version of the schema for %s' % (id))
                with open('.cache/%s.schema' % (hash), 'w') as file:
                    file.write(str(netconf.get_schema(module)))

        return netconf

    def _netconf_get_xml(self, netconf, filter, config=True, source='running'):
        filter_xml = """<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (filter)
        data_str = str(netconf.get_config(source=source, filter=filter_xml))
        return etree.fromstring(data_str.encode('UTF-8')).getchildren()[0]

    def process_cli_line(self, line):
        self.log.debug('Oper line into us: %s' % (line))
        if line[0:4] == 'conf':
            self.log.debug('Switching into configuration mode')
            self.mode = 1
        elif line[0:4] == 'show':
            self.log.debug('Show operation state')
        elif line[0:4] == 'exit':
            self.log.debug('Exit required')
            self.exit = True
        elif line == "":
            pass
        else:
            self.cliformat.opermode_error(line)

    def process_config_cli_line(self, line):
        self.log.debug('Config line to use: %s' % (line))

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

cli = cruxli()
cli.loop()
