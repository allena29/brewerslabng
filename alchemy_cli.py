from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
import time
import os
import socket

import sys
import logging


import blng.Voodoo
# pr.disable()
# pr.print_stats()


class LogWrap():

    ENABLED = False
    ENABLED_INFO = True
    ENABLED_DEBUG = True

    ENABLED_REMOTE = True
    REMOTE_LOG_IP = "127.0.0.1"
    REMOTE_LOG_PORT = 6666

    def __init__(self):
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('alchemy')

        if self.ENABLED_REMOTE:
            self.log_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self._pad_truncate_to_size("STARTED ("+str(time.time())+"):")
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    @staticmethod
    def _args_wildcard_to_printf(*args):
        if isinstance(args, tuple):
            # (('Using cli startup to do %s', 'O:configure'),)
            args = list(args[0])
            if len(args) == 0:
                return ''
            message = args.pop(0)
            if len(args) == 0:
                pass
            if len(args) == 1:
                message = message % (args[0])
            else:
                message = message % tuple(args)
        else:
            message = args
        return (message)

    def _pad_truncate_to_size(self, message, size=1024):
        if len(message) < size:
            message = message + ' '*(1024-len(message))
        elif len(message) > 1024:
            message = message[:1024]
        return message.encode()

    def info(self, *args):
        if self.ENABLED and self.ENABLED_INFO:
            self.log.info(args)
        if self.ENABLED_REMOTE and self.ENABLED_INFO:
            print('a')
            message = 'INFO ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    def error(self, *args):
        if self.ENABLED:
            self.log.error(args)
        if self.ENABLED_REMOTE:
            message = 'INFO ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    def debug(self, *args):
        if self.ENABLED and self.ENABLED_DEBUG:
            self.log.debug(args)

        if self.ENABLED_REMOTE and self.ENABLED_DEBUG:
            message = 'DEBUG ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))


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
        (0, 'exit'),
        (2, 'set '),
        (2, 'show ')
        # would expect set etc here to be more dynamically added in becuase what we last did and where
        # the user thinks they are in the navigation is important here.
    ]

    def __init__(self, init_voodoo_object):
        self.log = LogWrap()
        self.CURRENT_CONTEXT = init_voodoo_object
        self.allowed_commands = self.OPER_ALLOWED_COMMANDS
        self.mode = 0
        self.cache = blng.Voodoo.CruxVoodooCache(self.log)
        self._last_command_failure = None
        self.OUR_PROMPT = self.OPER_OUR_PROMPT

        self.effective_root = ''
        self.effective_root_obj = init_voodoo_object
        self.root = init_voodoo_object

    def bottom_toolbar(self):
        return HTML(self.CURRENT_CONTEXT._path)

    def get_completions(self, document, complete_event):
        """
        Note: we always must yield
        #Completion(), index#
        #
        # So far start_position is 0 (non-negative allows us to delete stuff)
        """

        command = document.text
        self.log.debug('command.text in auto complete %s', command)
        for (hide, valid_command) in self.allowed_commands:
            #print('__VALID__', valid_command, '__DOCTEXT__',document.text)#
            if hide == 0 and document.text == valid_command[:len(document.text)]:
                yield Completion(valid_command, -len(document.text))
                # Note: this method is part of a generator class, which means we can
                # yield as many times as we like but the execution takes a break until
                # the caller invokes next()
                # yield Completion('abxxxx', 0)
                # for c in range(12):
                #    yield Completion('result'+str(c), 0)

            # Really needd to work out what the best thing to do is here.
            # hide == 2 is a special case of auto complete
            # based on effective_root_obj

            if hide == 2 or hide == 3:  # and document.text == valid_command[:len(document.text)]:
                # pretty sure voodo needs some kind of path based lookup to get access
                # to data.
                if command.count(' ') == 0:

                    command_split = command.split(' ')
                    command_length = len(valid_command)-1
                    our_first_portion = command_split[0]
                    self.log.debug('debug auto complete type 2 no spaces %s = %s', our_first_portion, valid_command[:len(our_first_portion)])

                    if our_first_portion == valid_command[:len(our_first_portion)]:
                        yield Completion(valid_command, -len(document.text))
                if not self.cache.is_path_cached(command):
                    self.log.debug('CACHE-MISS: %s', command)
                    self.cache.add_entry(command, [])

                for completion in self.cache.get_item_from_cache(command):
                    yield Completion(compleition, -len(document.text))

                """
                Old way of doing things before docks thoughts.
                Don't like this approach because it implies we have show XXXX for everything.
                i.e. typing sh<TAB> completes to show simpleleaf which might not be what we wnat.

                command_split = command.split(' ')
                command_length = len(valid_command)-1
                our_first_portion = command_split[0]

                # Need a way of debugging completer without using the terminal...
                if our_first_portion == valid_command[:len(our_first_portion)]:
                    self.log.debug('True: %s == %s', our_first_portion, valid_command[:len(our_first_portion)])
                    children = self.effective_root_obj.__dir__()
                    for child in children:
                        # self.log.debug('Adding auto complete (type2) %s%s', valid_command, str(child))
                        yield Completion(valid_command + str(child), -len(document.text))
                else:
                    self.log.debug('False: %s == %s', our_first_portion, valid_command[:len(our_first_portion)])
                """

    def validate(self, document):
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
        """
        Assumption is that any command ending in a space needs additional handling to ensure
        it matches the root object.
        Any command not ending in a space is a 'command' command and can be processed as is
        without futher input.

        a 'command command' is exit which is listed as 'exit' in the CONF_ALLOWED_COMMANDS dict
        not 'command command' is 'set ' which needs more stuff.

        There will be hybrids (e.g. show)
        show can be either show\n or show thing\n or show thing more precise\n

        TODO:
        need a good think about 'set'
        do we render the children of set when we move into conf mode????

        keep in mind that one day we will have 'edit path' which will change where we consider root
        to be.
        """

        if (1, command) in self.CONF_ALLOWED_COMMANDS or (0, command) in self.CONF_ALLOWED_COMMANDS:
            self._last_command = command
            self._last_command_mode = 1
            self._last_command_failure = None
            return True

        self._last_command_failure = 'Unrecognised Command'

    def _do_oper_command(self, command):
        self.log.debug('_do_oper_command: %s', command)
        if command == 'configure' or command == 'conf' or command == 'conf t':
            self._switch_to_conf_mode()
        elif command == 'exit':
            self.log.debug('Exit frmo Oper Mode is the same as just saying exit everything')
            sys.exit(0)

    def _do_conf_command(self, command):
        self.log.debug('_do_conf_command: %s', command)
        if command == 'exit':
            self.log.debug('We have gone out of conf mode: # TODO: what about hanging changes in the transaction - this needs a confirm')
            self.mode = 0
            self.OUR_PROMPT = self.OPER_OUR_PROMPT
            self.allowed_commands = self.OPER_ALLOWED_COMMANDS

    def do(self, command):
        if self.mode == 0:
            if self._validated_oper_command(command):
                self._do_oper_command(command)
        else:
            if self._validated_conf_command(command):
                self._do_conf_command(command)

    def _switch_to_conf_mode(self):
        self.log.debug('We have gone into conf mode with effective_root: %s', self.effective_root)
        self.mode = 1
        self.OUR_PROMPT = self.CONF_OUR_PROMPT
        self.allowed_commands = self.CONF_ALLOWED_COMMANDS


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
