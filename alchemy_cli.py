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
        (0, 'exit'),
        (1, '')  # let the user press enter
    ]

    CONF_ALLOWED_COMMANDS = [
        (0, 'exit'),
        (2, 'set '),
        (3, 'show '),
        (3, 'delete '),
        (1, '')  # let the user press enter
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
        self._complete_terminated = -1
        self.root = init_voodoo_object

    def _get_bottom_bar(self):
        return HTML(self.CURRENT_CONTEXT._path)

    def get_completions(self, document, complete_event):
        """
        Note: we always must yield
        #Completion(), index#
        #
        # So far start_position is 0 (non-negative allows us to delete stuff)
        """

        command = document.text
        if ' ' in command:
            last_complete_command = command[:command.rfind(' ')]
            last_portion = command[command.rfind(' ')+1:]
            return self._handle_completion_for_command_with_path(last_complete_command, last_portion, command)
        else:
            return self._handle_completion_for_command(command)

    def _handle_completion_for_command_with_path(self, last_complete_command, last_portion, command):
        if self._complete_terminated >= len(command):
            self.log.debug('we have used backspace... cleaning up flag termianted flag ')
            return
        else:
            self._complete_terminated = -1

        if self.cache.is_path_cached(last_complete_command):
            for valid_command in self.cache.get_item_from_cache(last_complete_command):
                yield Completion(valid_command, -len(command))
        else:
            # TODO: cache needs to come here.
            self.log.debug('_handle_completion_with_path: %s ... %s', last_complete_command, last_portion)
            # self.log.debug('Length of command %s = %s', len(command), command)
            # self.log.debug('Length of last_complete_command %s = %s', len(last_complete_command), last_complete_command)
            #   yield Completion(' TODO: get children', -(len(command)-len(last_complete_command)))
            children = self._complete_obj.__dir__()
            for child in children:
                if child[:len(last_portion)] == last_portion:
                    if last_complete_command[:3] == 'set':
                        self._complete_terminated = -1

                        yield Completion(str(child + ' '), -(len(command)-len(last_complete_command))+1)
                    else:
                        if str(child) == last_portion:
                            child_obj = getattr(self._complete_obj, child)
                            if not hasattr(child_obj, '_path'):
                                self._complete_terminated = len(command)
                                self.log.debug('SET TERMINATED FLAG to length %s', len(command))
                        else:
                            self._complete_terminated = False
                        yield Completion(str(child), -(len(command)-len(last_complete_command))+1)

    def _handle_completion_for_command(self, command):
        self.log.debug('_handle_completion_for_command ... %s', command)
        self.log.debug('RESETTING FLAGS FOR AUTOCOMPLETE')
        self._complete_terminated = -1
        self._complete_obj = self.effective_root_obj
        for valid_command in [v for hide, v in self.allowed_commands if hide != 1]:
            command_split = command.split(' ')
            command_length = len(valid_command)-1
            our_first_portion = command_split[0]
            if our_first_portion == valid_command[:len(our_first_portion)]:
                yield Completion(valid_command, -len(command)-1)

    def validate(self, document):
        command = document.text
        if self._complete_terminated > 0:
            raise ValidationError(message='Stop typing!', cursor_position=len(command)-1)

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
            text = prompt(alchemy.OUR_PROMPT, bottom_toolbar=alchemy._get_bottom_bar(), completer=alchemy,
                          validator=alchemy, style=alchemy.STYLE, rprompt=alchemy._get_right_prompt(),
                          validate_while_typing=True)

            alchemy.do(text)
            alchemy.log.debug('We Got: %s', text)
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
