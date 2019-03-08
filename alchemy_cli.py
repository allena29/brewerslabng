from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import time
import os
import sys
import logging


import blng.Voodoo
# pr.disable()
# pr.print_stats()


class LogWrap():

    ENABLED = True
    ENABLED_INFO = True
    ENABLED_DEBUG = True

    def __init__(self):
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('alchemy')

    def info(self, *args):
        if self.ENABLED and self.ENABLED_INFO:
            self.log.info(args)

    def error(self, *args):
        if self.ENABLED:
            self.log.error(args)

    def debug(self, *args):
        if self.ENABLED and self.ENABLED_DEBUG:
            self.log.debug(args)


# pr = cProfile.Profile()
# pr.enable()
session = blng.Voodoo.DataAccess('crux-example.xml')
vcache = session._keystorecache

root = session.get_root()


class alchemy_voodoo_wrapper(Validator, Completer):

    """
    This class is responsible for wrapping a voodo data object into something that can behave
    a bit like a feature rich CLI.

    The intent is to keep 'alchmey' contained to just providing presetnation/adaptation.
    Any kind of DIFF/Serilaisation requirements must be implemented on Voodoo.

    We are aiming to provide a Juniper stlye of CLI.
    """
    OPER_OUR_PROMPT = 'brewer@localhost> '
    CONF_OUR_PROMPT = 'brewer@localhost% '

    STYLE = Style.from_dict({
        'rprompt': 'bg:#ff0066 #ffffff'
    })

    OPER_ALLOWED_COMMANDS = [
        (0, 'configure'),  # This is a terminating command
        (1, 'conf'),  # This is a terminating command too - but it's an alise we don't want to show in auto-complete
        (1, 'conf t'),  # likewise
        (0, 'exit')
    ]

    CONF_ALLOWED_COMMANDS = [
        (0, 'exit')
        # would expect set etc here to be more dynamically added in becuase what we last did and where
        # the user thinks they are in the navigation is important here.
    ]

    def __init__(self, init_voodoo_object):
        self.log = blng.Voodoo.LogWrap()
        self.CURRENT_CONTEXT = init_voodoo_object
        self.allowed_commands = self.OPER_ALLOWED_COMMANDS
        self.mode = 0
        self.cache = blng.Voodoo.CruxVoodooCache(self.log)
        self.path_we_are_working_on = []
        self._last_command_failure = None
        self.log = LogWrap()
        self.OUR_PROMPT = self.OPER_OUR_PROMPT

    def bottom_toolbar(self):
        return HTML(self.CURRENT_CONTEXT._path)

    def get_completions(self, document, complete_event):
        """
        Note: we always must yield
        #Completion(), index#
        #
        #So far start_position is 0 (non-negative allows us to delete stuff)
        """

        if self.cache.is_path_cached(document.text):
            a = 5/0

        if len(self.path_we_are_working_on) == 0:
            for (hide, valid_command) in self.allowed_commands:
                #print('__VALID__', valid_command, '__DOCTEXT__',document.text)#
                if not hide and document.text == valid_command[:len(document.text)]:
                    yield Completion(valid_command, -len(document.text))
                    # Note: this method is part of a generator class, which means we can
                    # yield as many times as we like but the execution takes a break until
                    # the caller invokes next()
                    # yield Completion('abxxxx', 0)
                    # for c in range(12):
                    #    yield Completion('result'+str(c), 0)
#
        #    print()

    def validate(self, document):
        if self.mode == 0 and self.path_we_are_working_on == 0:
            pass
        pass

    def get_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def _get_right_prompt(self):
        if self._last_command_failure:
            return self._last_command_failure

    def _validated_oper_command(self, command):
        if (1, command) in self.OPER_ALLOWED_COMMANDS or (0, command) in self.OPER_ALLOWED_COMMANDS:
            self.log.debug('_validated_oper_command TRUE: %s', command)
            self._last_comamnd = command
            self._last_command_mode = 0
            self._last_command_failure = None
            return True
        self._last_command_failure = 'Unrecognised Command'
        self.log.debug('_validated_oper_command FALSE: %s', command)

    def _validated_conf_command(self, command):
        if (1, command) in self.CONF_ALLOWED_COMMANDS or (0, command) in self.CONF_ALLOWED_COMMANDS:
            self._last_command = command
            self._last_command_mode = 1
            self._last_command_failure = None
            return True

        self._last_command_failure = 'Unrecognised Command'

    def _do_oper_command(self, command):
        self.log.debug('_do_oper_command: %s', command)
        if command == 'configure' or command == 'conf' or command == 'conf t':
            self.log.debug('We have gone into conf mode')
            self.mode = 1
            self.OUR_PROMPT = self.CONF_OUR_PROMPT
        elif command == 'exit':
            self.log.debug('Exit frmo Oper Mode is the same as just saying exit everything')
            sys.exit(0)

    def _do_conf_command(self, command):
        self.log.debug('_do_conf_command: %s', command)
        if command == 'exit':
            self.log.debug('We have gone out of conf mode: # TODO: what about hanging changes in the transaction - this needs a confirm')
            self.mode = 0
            self.OUR_PROMPT = self.OPER_OUR_PROMPT

    def do(self, command):
        if self.mode == 0:
            if self._validated_oper_command(command):
                self._do_oper_command(command)
        else:
            if self._validated_conf_command(command):
                self._do_conf_command(command)


if __name__ == '__main__':

    alchemy = alchemy_voodoo_wrapper(root)

    try:
        #  bottom_toolbar=alchemy.bottom_toolbar
        # get rid of bottom for now,

        if os.path.exists('cli.startup') and len(sys.argv) == 1:
            with open('cli.startup') as file_handle:

                line = file_handle.readline()
                while line != "":
                    alchemy.log.debug('Using cli startup to do %s', (line[:-1]))

                    print(line[0], line[2:-1])
                    if line[0] == 'O':
                        alchemy.mode = 0
                        alchemy.do(line[2:-1])
                    elif line[0] == 'C':
                        alchemy.mode = 1
                        alchemy.do(line[2:-1])
                    line = file_handle.readline()
        while 1:
            text = prompt(alchemy.OUR_PROMPT, completer=alchemy, validator=alchemy, style=alchemy.STYLE, rprompt=alchemy._get_right_prompt())
            alchemy.do(text)
            print('we got:', text)
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
