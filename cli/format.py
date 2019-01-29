#!/usr/bin/python3

import sys
import time
# from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
# from prompt_toolkit.validation import Validator, ValidationError
# from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


class cruxformat:

    """
    This class is responsible for providing the cosmetic appearance of
    the command line interface, the behaviour itself is defined in cruxli.
    Much of the presentation options here are goverend by prompt_toolkit

    The command line interface has two basic modes, operational and
    configuration modes.
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
        self.config_prompt = 'brewer@localhost# '

    @staticmethod
    def bottom_toolbar():
        return HTML('Connected')

    def welcome(self):
        print('Welcome to BREWERS COMMAND LINE INTERFACE')
        return self.opermode_prompt()

    def configmode_prompt(self):
        print("")
        print("[edit] ")
        return self.session.prompt(self.config_prompt,
                                   bottom_toolbar=cruxformat.bottom_toolbar,
                                   completer=self.get_oper_mode_command_list(),
                                   complete_while_typing=True,
                                   validate_while_typing=True,
                                   auto_suggest=AutoSuggestFromHistory())

    def opermode_prompt(self):
        return self.session.prompt(self.prompt,
                                   bottom_toolbar=cruxformat.bottom_toolbar,
                                   completer=self.get_oper_mode_command_list(),
                                   complete_while_typing=True,
                                   validate_while_typing=True,
                                   auto_suggest=AutoSuggestFromHistory())

    def get_oper_mode_command_list(self):
        return WordCompleter(self.DEFAULT_OPER_COMMANDS.keys())

    def opermode_error(self, line):
        """
        When a user makes a mistake within operational mode provide some
        guidance to the user including a list of commands that are valid
        """
        print('%s\nError: expecting...\n' % (line))
        for command in self.DEFAULT_OPER_COMMANDS:
            print('%s%s - %s' % (command, ' '*(10-len(command)),
                                 self.DEFAULT_OPER_COMMANDS[command]))
        print("[error][%s]" % (self.get_time()))

    def get_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
