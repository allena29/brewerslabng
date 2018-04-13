#!/usr/bin/env python2.7

import time
import sys
import json
import requests
from cmd2 import Cmd


class PyConfHoardCLI(Cmd):

    prompt = 'wild@localhost> '
    SERVER = 'http://127.0.0.1:8000'

    def __init__(self):
        Cmd.__init__(self)

        self.allow_redirection = False
        self.debug = False

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

        self._db_conf = {}
        self._db_oper = {}

        # need some kind of refresh mechanism for opdata/config
        self._load_datastores()

    def _load_datastores(self):
        discover = None
        try:
            response = requests.get('%s/v1/discover' % (self.SERVER)).text
            discover = json.loads(response)
        except Exception as err:
            raise RuntimeError('Unable to connect to %s' % (self.SERVER))

        for datastore in discover['datastores']:
            metadata = discover['datastores'][datastore]
            space_sep_path = metadata['yangpath'][1:].replace('/', ' ')

            response = requests.get('%s/v1/datastore/operational/%s' % (self.SERVER,
                                                                        metadata['appname'])).text
            oper = json.loads(response)
            self._get_node(self._db_oper, space_sep_path, create_if_no_match=oper)

            response = requests.get('%s/v1/datastore/persist/%s' % (self.SERVER,
                                                                    metadata['appname'])).text
            conf = json.loads(response)
            self._get_node(self._db_conf, space_sep_path, create_if_no_match=conf)

    def _exit_conf_mode(self):
        self._in_conf_mode = False
        print('')
        self.prompt = 'robber@localhost> '

        del self.do_set
        del self.do_delete
        self.do_show = self._command_oper_show
        self.complete_show = self._autocomplete_oper_show

    def _enter_conf_mode(self):
        self._in_conf_mode = True
        self.prompt = 'robber@localhost% '
        print('Entering configuration mode private')
        self._conf_header()
        # TODO in later version refresh these commands on tab complete.
        # TODO: make tab completion show a better column based presentation.
        self.do_set = self._command_set
        self.do_delete = self._command_delete
        self.do_show = self._command_conf_show
        self.complete_show = self._autocomplete_conf_show

    def _ok(self):
        print('')
        print('[ok][%s]' % (time.ctime()))

    def _error(self, err=None):
        if err:
            print(err.message)
        print('')
        print('[error][%s]' % (time.ctime()))

    def _conf_header(self):
        self._ok()
        print('[edit]')

    # We use _command_xxxx prefix to show commands which will be dynamically removed
    # or added based on mode.

    def _get_node(self, our_node, path, fail_if_no_match=False, create_if_no_match=None):
        """
        Attempt to filter down an object by it's keys

        our_node - an object
        path     - a space separate path of keys
                   Note: keys cannot contain spaces
        """
        keys_to_navigate = path.split(' ')
        i = 0 
        for key in keys_to_navigate:
            if len(key):
                if our_node.has_key(key):
                    our_node = our_node[key]
                elif fail_if_no_match:
                    raise ValueError('Path: %s does not exist' % (path))
                elif create_if_no_match and i == len(keys_to_navigate) - 2:
                    our_node[key] = create_if_no_match
            i = i + 1     

        return our_node

    def _auto_complete(self, our_node, line, text, cmd='show '):
        """
        our_node - an object
        line     - the full line of text (e.g. show fermentation
        text     - the text fragment autom completing (e.g. fermentation)
        """
        path_to_find = line[len(cmd):]
        our_node = self._get_node(our_node, path_to_find)
        cmds = []
        for key in our_node:
            if key[0:len(text)] == text:
                cmds.append(key+ ' ')

        cmds.sort()
        return cmds

    def _get_json_cfg_view(self, our_node, path):
        our_node = self._get_node(our_node, path, fail_if_no_match=True)
        return json.dumps(our_node, sort_keys=True, indent=4, separators=(',', ': '))

    # Show Command
    def _command_oper_show(self, args):
        'Show node in the operational database'
        try:
            print(self._get_json_cfg_view(self._db_oper, args))
            self._ok()
        except Exception as err:
            self._error(err)

    def _command_conf_show(self, args):
        try:
            print(self._get_json_cfg_view(self._db_conf, args))
            self._ok()
        except Exception as err:
            self._error(err)

    def _autocomplete_oper_show(self, text, line, begidx, endidx):
        return self._auto_complete(self._db_oper, line, text)

    def _autocomplete_conf_show(self, text, line, begidx, endidx):
        return self._auto_complete(self._db_conf, line, text)


    def _command_delete(self, args):
        print('command elete called', args)

    def _command_set(self, args):
        'Set node in the configurationl database'
        if len(args) < 1:
            raise ValueError('Incomplete command: set %s' % (args))
        print('command setw called', args)




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


if __name__ == '__main__':
    cli = PyConfHoardCLI()
    cli.cmdloop()
