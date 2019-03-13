from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

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

        self.effective_root = ''        # lost track of this think it is now effectively _complete_obj
        self.effective_root_obj = init_voodoo_object
        self._complete_terminated = -1
        self._complete_obj = self.effective_root_obj
        self._complete_command = ""
        self.root = init_voodoo_object

        self.OPER_SESSION = PromptSession()
        self.CONF_SESSION = PromptSession()
        self.OUR_SESSION = self.OPER_SESSION

        self.current = []
        self.current_completion_cmdstring = []
        self.current_completion_obj = [None, self.effective_root_obj]

    def _get_bottom_bar(self):
        return HTML(self.CURRENT_CONTEXT._path)

    def get_completions(self, document, complete_event):
        """
        either YeildCompletion(text, characters to delete)
        or raise StopITeration
        """
        if not self.valid:
            raise StopIteration

        if self.valid:
            for option in self.current_completion_cmdstring[len(self.current)-1]:
                if option[:len(self.current_portion)] == self.current_portion:
                    yield Completion(option, -len(self.current_portion))
                #    self.log.debug('completion called %s (%s)', document.text, self.current_portion)

        raise StopIteration

    def validate(self, document):
        """
        validation gets called first and blocks before get_completions() is run.

        current         - stores a space separated string for the current command getting validated.
        self.current    - stores the last successfully validated command.

        """
        current = self._split_with_quoted_escaped_strings(document.text)

        if len(current) < len(self.current):
            self.log.debug('We have used the backspace to remove an element')

        if not self._build_completion_objects(current):
            # this will trigger on space after tab completion
            raise ValidationError(message="Invalid node")

        last_portion = current[-1]
        ok = False
        for option in self.current_completion_cmdstring[-1]:
            if option[:len(last_portion)] == last_portion:
                ok = True

        if not ok:
            raise ValidationError(message='This is garbage')
#        self.log.debug('we are sorting out element %s', current[-1])
        self.valid = False

        self.log.debug('validation called - %s', str(current))
        self.log.debug('previous validation called - %s', str(current))

        self.current_portion = current[-1]
        self.current = current
        self.valid = True

    def _build_completion_objects(self, current, purge=False):
        """
        The aim of this method is to porvide two lists
            self.current_completion_cmdstring = []
            self.current_completion_obj = []

        The cmdstring is a quick an easy thing to iterate around of validations.
        We provide the next element we expect to be required.
        The cmdstring object should be a CruxNode.

        An example of current_completion_cmdstring :
            b"INFO: 1552513330.792348 DEBUG BCS  ['delete ', 'exit', 'set ', 'show ']
            b"INFO: 1552513330.792407 DEBUG BCS  ['TODO_stores', 'bronze', 'container_and_lists', ...]
            b"INFO: 1552513330.7924302 DEBUG BCS  ['silver']
            b"INFO: 1552513330.792449 DEBUG BCS  ['gold']
            b"INFO: 1552513330.792466 DEBUG BCS  ['platinum']
        An example of current_completion_obj after typing brewer@localhost% show bronze silver gold platinum d:
            b'INFO: 1552513421.53766 DEBUG BCO  None
            b'INFO: 1552513421.5376809 DEBUG BCO  VoodooRoot
            b'INFO: 1552513421.537706 DEBUG BCO  VoodooContainer: /bronze
            b'INFO: 1552513421.5377321 DEBUG BCO  VoodooContainer: /bronze/silver
            b'INFO: 1552513421.537754 DEBUG BCO  VoodooContainer: /bronze/silver/gold
            b'INFO: 1552513421.5377762 DEBUG BCO  VoodooContainer: /bronze/silver/gold/platinum

        There is a tiny amount of caching involved - if we consider a path
            show bronze silver gold platinum
        We we only call __dir__() on the crux node and build the list once.

        TODO: on backspace something needs to claer the last entry.
        """

        if purge:
            self.current_completion_cmdstring = []
            self.current_completion_obj = []

        new_completions = []

        # for x in self.current_completion_cmdstring:
        #    self.log.debug('BCS  %s', str(x))
        # for x in self.current_completion_obj:
        #    self.log.debug('BCO  %s', str(repr(x)))

        for index in range(len(current)):
            if len(self.current_completion_cmdstring) > index:
                self.log.debug('we already have index %s', index)
            else:
                # We don't have what we need to determine completions
                if index == 0:
                    """
                    After this stage we should

                    self.current_completion_obj and self.current_completion_cmdstring lists for
                    the first index (the command) and the second index the thing that comes next.
                    """
                    for valid_command in [v for hide, v in self.allowed_commands if hide != 1]:
                        new_completions.append(valid_command)
                    new_completions.sort()

                    self.current_completion_cmdstring.append(new_completions)
                    self.current_completion_obj = [None, self.effective_root_obj]

                    new_completions = self._get_completions_from_object(self.current_completion_obj[index+1])
                    self.current_completion_cmdstring.append(new_completions)

                if index > 0:
                    if current[-1] == '':
                        previous_text = current[-2]

                        try:
                            next_obj = getattr(self.current_completion_obj[-1], previous_text)
                        except Exception as err:
                            return False
                        self.current_completion_obj.append(next_obj)

                        new_completions = self._get_completions_from_object(next_obj)
                        self.current_completion_cmdstring.append(new_completions)

        return True

    def _get_completions_from_object(self, obj):
        new_completions = []
        for command in obj.__dir__():
            new_completions.append(command)
        new_completions.sort()
        return new_completions

    def _split_with_quoted_escaped_strings(self, text):
        """TODO: this isn't actually implemented!"""
        return text.split(' ')

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
            self.OUR_SESSION = self.OPER_SESSION
            self._build_completion_objects('', purge=True)

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
        self.OUR_SESSION = self.CONF_SESSION
        self._build_completion_objects('', purge=True)


if __name__ == '__main__':

    ctrl_c_count = 0
    try:
        #  bottom_toolbar=alchemy.bottom_toolbar
        # get rid of bottom for now,
        alchemy = alchemy_voodoo_wrapper(root)

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
            try:
                text = alchemy.OUR_SESSION.prompt(alchemy.OUR_PROMPT, bottom_toolbar=alchemy._get_bottom_bar(), completer=alchemy,
                                                  validator=alchemy, style=alchemy.STYLE, rprompt=alchemy._get_right_prompt(),
                                                  validate_while_typing=True, complete_while_typing=True,
                                                  auto_suggest=AutoSuggestFromHistory())

                alchemy.do(text)
                alchemy.log.debug('We Got: %s', text)

                ctrl_c_count = 0
            except KeyboardInterrupt:
                ctrl_c_count = ctrl_c_count + 1
                if ctrl_c_count == 2:
                    sys.exit(0)
    except EOFError:
        pass
