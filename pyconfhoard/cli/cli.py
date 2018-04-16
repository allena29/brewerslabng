#!/usr/bin/env python2.7

import time
import sys
import json
import requests
from colorama import Fore
from colorama import Style
from PyConfHoardDatastore import PyConfHoardDatastore
from cmd2 import Cmd




class PyConfHoardCLI(Cmd):

    prompt = 'wild@localhost> '
    SERVER = 'http://127.0.0.1:8000'

    def __init__(self, no_networking=False):
        Cmd.__init__(self)

        self.allow_redirection = False
        self.debug = True

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

        self.datastore = PyConfHoardDatastore()

        # need some kind of refresh mechanism for opdata/config
        if not no_networking:
            self._load_datastores()

    def _load_datastores(self):

        discover = None
        try:
            response = requests.get('%s/v1/discover' % (self.SERVER)).text
            discover = json.loads(response)
        except Exception as err:
            raise RuntimeError('Unable to connect to %s' % (self.SERVER))

        self.datastore.db = discover['schema']

        for datastore in discover['datastores']:
            metadata = discover['datastores'][datastore]

            msg = 'Loading..<OPER:%s>' % (metadata['appname'])
            PyConfHoardCLI.xterm_message(msg, Fore.YELLOW)
            try:
                response = requests.get('%s/v1/datastore/operational/%s' % (self.SERVER, metadata['appname'])).text
                if len(response):
                    operdata = json.loads(response)
                PyConfHoardCLI.xterm_message(msg.replace('Loading..', ''), Fore.GREEN, msg, newline=True)
                self.datastore.merge_node(operdata)
            except Exception as err:
                PyConfHoardCLI.xterm_message(msg.replace('Loading..', 'ERROR! '), Fore.RED, msg, newline=True)
                raise err

            msg = 'Loading..<CFG:%s>' % (metadata['appname'])
            PyConfHoardCLI.xterm_message(msg,Fore.YELLOW)
            try:
                response = requests.get('%s/v1/datastore/running/%s' % (self.SERVER, metadata['appname'])).text
                if len(response):
                    config = json.loads(response)
                self.datastore.merge_node(config)
                PyConfHoardCLI.xterm_message(msg.replace('Loading..', ''), Fore.GREEN, msg, newline=True)
            except Exception as err:
                PyConfHoardCLI.xterm_message(msg.replace('Loading..', 'ERROR! '), Fore.RED, msg, newline=True)

            if config == {}:
                msg = 'Loading..<INIT:%s>' % (metadata['appname'])
                PyConfHoardCLI.xterm_message(msg,Fore.YELLOW)
                try:
                    response = requests.get('%s/v1/datastore/default/%s' % (self.SERVER, metadata['appname'])).text
                    if len(response):
                        config = json.loads(response)
                    self.datastore.merge_node(config)
                    PyConfHoardCLI.xterm_message(msg.replace('Loading..', ''), Fore.GREEN, msg, newline=True)
                except Exception as err:
                    PyConfHoardCLI.xterm_message(msg.replace('Loading..', 'ERROR! '), Fore.RED, msg, newline=True)


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

    def _ok(self):
        print('')
        print('[ok][%s]' % (time.ctime()))

    def _error(self, err=None):
        if err:
            print (str(err))
        print ('')
        print ('[error][%s]' % (time.ctime()))

    def _conf_header(self):
        self._ok()
        print('[edit]')

    # We use _command_xxxx prefix to show commands which will be dynamically removed
    # or added based on mode.


    def _auto_complete(self, our_node, line, text, cmd='show ', config=True):
        """
        our_node - an object
        line     - the full line of text (e.g. show fermentation
        text     - the text fragment autom completing (e.g. fermentation)

        Note: cmd2 will swallow any exceptions and the command-line-completion
        won't behave as we expect.
        """
        try:
            path_to_find = line[len(cmd):]
            # Attempt to get the path which might not exist
            cmds = []
            try:
                # TODO: although we pass in config ti's not taking effect
                if path_to_find.count(' ') < 1:
                    # print ('case1',path_to_find)
                    xcmds = self.datastore.list_root(config=config)
                else:
                    # print ('case2',path_to_find)
                    if text == '':
                        path_to_find = self.datastore.decode_path_string(path_to_find, ignore_last_n=0)
                    else:
                        path_to_find = self.datastore.decode_path_string(path_to_find, ignore_last_n=1)
                    xcmds = self.datastore.list(path_to_find, config=config)
                cmds = []
                for key in xcmds:
                    if key[0:len(text)] == text:
                        cmds.append(key + ' ')
            except:
                pass
            cmds.sort()
        except Exception as err:
            print('!!!!! exception in autocomplete %s' % (str(err)))

        return cmds


    def _get_json_cfg_view(self, path, config=True):
        try:
            our_node = self.datastore.get_filtered(path, config)
        except KeyError as err:
            raise ValueError('Path: %s does not exist' % (path))

        return json.dumps(our_node, sort_keys=True, indent=4, separators=(',', ': '))

    # Show Command
    def _command_oper_show(self, args):
        'Show node in the operational database'
        try:
            print(self._get_json_cfg_view(args, config=False))
            self._ok()
        except Exception as err:
            self._error(err)

    def _command_conf_show(self, args):
        try:
            print(self._get_json_cfg_view(args, config=True))
            self._ok()
        except Exception as err:
            self._error(err)

    def _autocomplete_oper_show(self, text, line, begidx, endidx):
        if text == '':
            text=line.split(' ')[-1]
#        print ('...text/line  %s/%s' %(text,line))
        return self._auto_complete(False, line, text)

    def _autocomplete_conf_show(self, text, line, begidx, endidx):
        return self._auto_complete(True, line, text)

    def _autocomplete_conf_create(self, text, line, begidx, endidx):
        # TODO: in future we shouldn't auto complete things that don't have a list as a decednant
        return self._auto_complete(True, line, text, 'create ')

    def _command_create(self, args):

        path_to_list = self.datastore.decode_path_string(args, ignore_last_n=1)
        key = self.datastore.decode_path_string(args, get_index=-1)
        self.datastore.create(path_to_list, key)


    def _command_delete(self, args):
        print('command elete called', args)

    def _command_set(self, args):
        'Set node in the configurationl database'
        if len(args) < 1:
            raise ValueError('Incomplete command: set %s' % (args))
        print ('set command not implement')
#        PyConfHoardDatastore._set_node(self._db_conf, args)

    def _autocomplete_conf_set(self, text, line, begidx, endidx):
        if self._in_conf_mode: 
            return self._auto_complete(self._db_conf, line, text, cmd='set ')

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
            sys.stdout.write(' ' *(len(oldmsg) - len(msg)))

        if newline:
            sys.stdout.write('\n')
        sys.stdout.flush()


if __name__ == '__main__':
    cli = PyConfHoardCLI()
    cli.cmdloop()
