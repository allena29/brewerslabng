#!/usr/bin/python3

from ncclient import manager
import argparse
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
                text = self.session.prompt(self.prompt, bottom_toolbar=cruxformat.bottom_toolbar)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break



class cruxli:


    def __init__(self, host='localhost', port='830', username='netconf', password='netconf'):
        self.netconf = self._connect_netconf(host, port, username, password)
        self.cliformat = cruxformat()
        self.cliformat.welcome()
        

    def __del__(self):
        self._disconnect_netconf()

    def _disconnect_netconf(self):
        pass

    def _connect_netconf(self, host, port, username, password):
        netconf = manager.connect(host=host, port=port, username=username, password=password,
                                  hostkey_verify=False, allow_agent=False, look_for_keys=False,
                                  unknown_host_cb=lambda x:True)

        try:
            schema = netconf.get_schema('crux')
            if not 'namespace "http://brewerslabng.mellon-collie.net/yang/crux";' in schema.data:
                raise ValueError("NETCONF does not support crux protocol")
        except:
            raise ValueError("NETCONF does not support crux protocol")

        return netconf

cli = cruxli()


