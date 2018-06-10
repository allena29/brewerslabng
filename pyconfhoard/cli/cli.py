#!/usr/bin/env python2.7
import traceback
import time
import logging
import sys
import json
import requests
from colorama import Fore
from colorama import Style
from PyConfHoard import Data
from PyConfHoardCommon import decode_path_string
from cmd2 import Cmd



class PyConfHoardCLI(Cmd):

    prompt = 'wild@localhost> '
    SERVER = 'http://127.0.0.1:8000'
    LOG_LEVEL = logging.CRITICAL

    def __init__(self, no_networking=False):
        Cmd.__init__(self)

        self.allow_redirection = False
        self.debug = True

        logging.TRACE = 7

        def custom_level_trace(self, message, *args, **kws):
            if self.isEnabledFor(logging.TRACE):
                self._log(logging.TRACE, message, args, **kws)
        logging.Logger.trace = custom_level_trace
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.addLevelName(logging.TRACE, "TRACE")
        logging.basicConfig(level=self.LOG_LEVEL, format=FORMAT)
        self.log = logging.getLogger('CLI')

        # To remove built-in commands entirely, delete their "do_*" function from the
        # cmd2.Cmd class
        if hasattr(Cmd, 'do_load'):
            del Cmd.do_load
        if hasattr(Cmd, 'do_py'):
            del Cmd.do_py
        if hasattr(Cmd, 'do_pyscript'):
            del Cmd.do_pyscript
        if hasattr(Cmd, 'do_shell'):
            del Cmd.do_shell
        if hasattr(Cmd, 'do_alias'):
            del Cmd.do_alias
        if hasattr(Cmd, 'do_shortcuts'):
            del Cmd.do_shortcuts
        if hasattr(Cmd, 'do_edit'):
            del Cmd.do_edit
        if hasattr(Cmd, 'do_set'):
            del Cmd.do_set
        if hasattr(Cmd, 'do_quit'):
            del Cmd.do_quit
        if hasattr(Cmd, 'do__relative_load'):
            del Cmd.do__relative_load
        if hasattr(Cmd, 'do_eof'):
            del Cmd.do_eof
        if hasattr(Cmd, 'do_eos'):
            del Cmd.do_eos

        self.exclude_from_help.append('do_eof')
        self.exclude_from_help.append('do_conf')

        # this comes in 0.8 and will hide eof from tab completion :-)
        self.do_show = self._command_oper_show
        self.complete_show = self._autocomplete_oper_show

        self._in_conf_mode = False

        self.pyconfhoarddata = Data()
        self.oper = self.pyconfhoarddata.oper
        self.config = self.pyconfhoarddata.config

        self.dirty_flags = {}
        self.dirty_flag = False

        # need some kind of refresh mechanism for opdata/config
        if not no_networking:
            self._load_datastores()


    def _load_datastores(self):
        """
        This internal method loads the basic schema and then will merge in the datastores
        of each thing that we have.
        """

        discover = None
        msg = 'Connecting...'
        PyConfHoardCLI.xterm_message(msg, Fore.YELLOW)
        try:
            self.pyconfhoarddata.register_from_web(self.SERVER)
            PyConfHoardCLI.xterm_message(msg.replace(msg, 'Comand Line READY'), Fore.GREEN, msg, newline=True)
        except Exception as err:
            PyConfHoardCLI.xterm_message(msg.replace(msg, 'Unable to connect to command-line %s' % (self.SERVER)), Fore.RED, msg, newline=True)
            sys.exit(0)

    def _exit_conf_mode(self):
        self._in_conf_mode = False
        print('')
        self.prompt = 'robber@localhost> '

        del self.do_set
        del self.do_delete
        self.do_show = self._command_oper_show
        self.complete_show = self._autocomplete_oper_show
        del self.complete_set
        del self.do_create
        del self.complete_create
        del self.do_commit

    def _enter_conf_mode(self):
        self._in_conf_mode = True
        self.prompt = 'robber@localhost% '
        print('Entering configuration mode private')
        self._conf_header()
        self.do_set = self._command_set
        self.complete_set = self._autocomplete_conf_set

        self.do_delete = self._command_delete
        self.do_show = self._command_conf_show
        self.complete_show = self._autocomplete_conf_show
        self.complete_create = self._autocomplete_conf_create
        self.do_create = self._command_create
        self.do_commit = self._command_commit

    def _ok(self):
        print('')
        print('[ok][%s]' % (time.ctime()))

    def _error(self, err=None):
        if err:
            print(str(err))
        print('')
        print('[error][%s]' % (time.ctime()))

    def _conf_header(self):
        self._ok()
        print('[edit]')

    # We use _command_xxxx prefix to show commands which will be dynamically removed
    # or added based on mode.

    def _auto_complete(self, line, text, cmd='show ', config=True, filter_blank_values=False):
        """
        line     - the full line of text (e.g. show fermentation
        text     - the text fragment autom completing (e.g. fermentation)

        Note: cmd2 will swallow any exceptions and the command-line-completion
        won't behave as we expect.

        Examples:

            line            text        result
            'show '         ''          ['brewhouse ' ', 'ingredients ', 'recipes ']
            'show br'       'br'        ['brewhouse ']

            if text = '' then we search datastore for the full pth
            if text != '' then we have to search the datastore for everything except the prtial element.


        """

        if config is True:
            db = self.config
        else:
            db = self.oper

        try:
            strip_partial_elements = 0
            # Attempt to get the path which might not exist
            cmds = []
            try:
                if not text == '':
                    strip_partial_elements = 1
                path_to_find = db.decode_path_string(line[len(cmd):], ignore_last_n=strip_partial_elements)
                xcmds = db.list(path_to_find)
                cmds = []
                for key in xcmds:
                    if key[0:len(text)] == text:
                        cmds.append(key + ' ')
            except ImportError as err:
                pass
            cmds.sort()
        except Exception as err:
            #print (str(err))
            pass
        return cmds

    # Show Command
    def _command_oper_show(self, args):
        'Show node in the operational database'
        print (args,'<oper')
        path = decode_path_string(args)
        try:
            print(self.pyconfhoarddata.get_database_as_json(path, database='config', pretty=True))
            self._ok()
        except Exception as err:
            self._error(err)

    def _command_conf_show(self, args):
        'Show node in the configuration database'
        print (args,'<show')
        path = decode_path_string(args)
        try:
            print(self.pyconfhoarddata.get_database_as_json(path, database='oper', pretty=True))
            self._ok()
        except Exception as err:
            self._error(err)

    def _autocomplete_oper_show(self, text, line, begidx, endidx):
        if text == '':
            text = line.split(' ')[-1]
        return self._auto_complete(line, text, config=False)

    def _autocomplete_conf_show(self, text, line, begidx, endidx):
        return self._auto_complete(line, text, config=True)

    def _autocomplete_conf_create(self, text, line, begidx, endidx):
        # TODO: in future we shouldn't auto complete things that don't have a list as a decednant
        return self._auto_complete(line, text, 'create ', config=True, filter_blank_values=False)

    def _command_create(self, args):
        path_to_list = self.config.decode_path_string(args, ignore_last_n=1)
        key = self.config.decode_path_string(args, get_index=-1)
        self.config.create(path_to_list, key)

    def _command_delete(self, args):
        print('command elete called', args)

    def _command_set(self, args):
        'Set node in the configurationl database'
        if len(args) < 1:
            raise ValueError('Incomplete command: set %s' % (args))
        self.config.set_from_string(args)

    def _autocomplete_conf_set(self, text, line, begidx, endidx):
        if self._in_conf_mode:
            return self._auto_complete(line, text, 'set ', config=True, filter_blank_values=False)


    def _command_commit(self, args):
        'Save configuration to the database'
        for this_datastore in self.datastores:
            self.pyconfhoarddata.persist(self.SERVER, self.datastores[this_datastore]['yangpath'])

    def do_eof(self, args):
        # Implements CTRL+D
        if self._in_conf_mode:
            self._exit_conf_mode()
        else:
            print('')
            return self._STOP_AND_EXIT
        sys.exit(0)

    def do_exit(self, args):
        return self.do_eof(args)

    def do_configure(self, args):
        if self._in_conf_mode:
            raise ValueError('Already in configure mode')
        self._enter_conf_mode()

    # Ideally we would be able to tab complet confi... config... configure...
    def do_conf(self, args):
        self.do_configure(args)

    @staticmethod
    def xterm_message(msg, colour, oldmsg="", newline=False):
        if len(oldmsg):
            sys.stdout.write('\033[%sD' % (len(oldmsg)))
        sys.stdout.write(colour)
        sys.stdout.write(msg)
        sys.stdout.write(Style.RESET_ALL)
        if len(msg) < len(oldmsg):
            sys.stdout.write(' ' * (len(oldmsg) - len(msg)))

        if newline:
            sys.stdout.write('\n')
        sys.stdout.flush()


if __name__ == '__main__':
    cli = PyConfHoardCLI()
    cli.cmdloop()
