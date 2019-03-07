from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
import time

import blng.Voodoo
# pr.disable()
# pr.print_stats()


# pr = cProfile.Profile()
# pr.enable()
session = blng.Voodoo.DataAccess('crux-example.xml')
vcache = session._keystorecache

root = session.get_root()


class alchemy_voodoo_wrapper(Completer, Validator):

    """
    This class is responsible for wrapping a voodo data object into something that can behave
    a bit like a feature rich CLI.

    The intent is to keep 'alchmey' contained to just providing presetnation/adaptation.
    Any kind of DIFF/Serilaisation requirements must be implemented on Voodoo.

    We are aiming to provide a Juniper stlye of CLI.
    """

    OPER_ALLOWED_COMMANDS = [
        'configure terminal',
        'exit'
    ]

    CONF_ALLOWED_COMMANDS = [
        'delete ',
        'edit ',
        'exit ',
        'set '
    ]

    def __init__(self, init_voodoo_object):
        self.log = blng.Voodoo.LogWrap()
        self.CURRENT_CONTEXT = init_voodoo_object
        self.allowed_commands = self.OPER_ALLOWED_COMMANDS
        self.mode = 0
        self.cache = blng.Voodoo.CruxVoodooCache(self.log)
        self.path_we_are_working_on = []

    def bottom_toolbar(self):
        return HTML(self.CURRENT_CONTEXT._path)

    def completer(self):
        return WordCompleter['sdf']

    def get_completions(self, document, complete_event):
        """
        Note: we always must yield
        Completion(), index

        So far index has been 0
        """

        if self.cache.is_path_cached(document.text):
            a = 5/0

        if len(self.path_we_are_working_on) == 0:
            for valid_command in self.allowed_commands:
                print('__VALID__', valid_command, '__DOCTEXT__', document.text)
            print()

        yield Completion('', start_position=0)

    def validate(self, document):
        #raise ValidationError(message='boo')
        pass


alchemy = alchemy_voodoo_wrapper(root)

try:
    #  bottom_toolbar=alchemy.bottom_toolbar
    # get rid of bottom for now,
    text = prompt('> ', completer=alchemy, validator=alchemy)
    iprint('we got', text)
except KeyboardInterrupt:
    pass
except EOFError:
    pass
