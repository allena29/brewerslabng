#!/usr/bin/env python
import json
import traceback
import hashlib
import importlib
import unittest
import time
import os
import re
import sys
import behave
from behave.__main__ import run_behave
from coverage import Coverage
from colorama import Fore
from colorama import Style
from cmd2 import Cmd


class resultswallower(unittest.TextTestResult):

    separator1 = ''
    separator2 = ''

    def printErrors(self):
        pass

    def printErrorList(self, a, b):
        pass

    def startTest(self, test):
        sys.stdout.write(Style.NORMAL)
        sys.stdout.write(str(test))
        sys.stdout.flush()

    def addSuccess(self, test):
        sys.stdout.write('\033[%sD' % (len(str(test))))
        sys.stdout.write(Style.NORMAL)
        sys.stdout.write(Fore.GREEN)
        sys.stdout.write(str(test))
        sys.stdout.write(Style.RESET_ALL)
        sys.stdout.write('\n')

    def addError(self, test, err):
        sys.stdout.write('\033[%sD' % (len(str(test))))
        sys.stdout.write(Style.NORMAL)
        sys.stdout.write(Fore.RED)
        sys.stdout.write(str(test))
        sys.stdout.write(Style.DIM)
        sys.stdout.write(str(err))
        sys.stdout.write(Style.RESET_ALL)
        sys.stdout.write('\n')


class testnavigator(Cmd):

    DEFAULT_PROMPT = 'testnavigator>'
    prompt = DEFAULT_PROMPT

    def __init__(self, testDirectory=None, testtest=None, testCase=None):
        Cmd.__init__(self)

        self.allow_redirection = False
        self.debug = True

        self.testcae = None
        self.testcases = []
        self.tests = {}
        self.workingdir = None
        self.testdir = None
        self.failures = []

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
#        if hasattr(Cmd, 'do_eof'):
#            del Cmd.do_eof
#        if hasattr(Cmd, 'do_eos'):
#            del Cmd.do_eos
        if hasattr(Cmd, 'do_unalias'):
            del Cmd.do_unalias

    def _ok(self):
        print('')
        print('[ok][%s]' % (time.ctime()))

    def _error(self, err=None):
        if err:
            print(str(err))
        print('')
        print('[error][%s]' % (time.ctime()))

    @staticmethod
    def truncate_prompt(prompt):
        return '/'.join(prompt.split('/')[-3:])

    @staticmethod
    def xterm_message(msg, colour=None, oldmsg="", newline=False, style=Style.NORMAL):
        if len(oldmsg):
            sys.stdout.write('\033[%sD' % (len(oldmsg)))
        sys.stdout.write(style)
        if colour:
            sys.stdout.write(colour)
        sys.stdout.write(msg)
        sys.stdout.write(Style.RESET_ALL)
        if len(msg) < len(oldmsg):
            sys.stdout.write(' ' * (len(oldmsg) - len(msg)))

        if newline:
            sys.stdout.write('\n')
        sys.stdout.flush()

    def do_exit(self, args):
        'Exit the navigator - or move up a level of the context'
        return True

    def complete_run(self, text, line, begidx, endidx):
        if not self.testcase:
            return []

        if len(text.split()) == 0:
            return self.tests[self.testcase]['tests']

        result = []
        for item in self.tests[self.testcase]['tests']:
            if item[0:len(text)] == text:
                result.append(item)
        result.sort()
        return result

    def do_workingdir(self, args):
        'Set the working directory when running a test'
        if os.path.exists(args):
            self.workingdir = args
        else:
            raise RuntimeError('Unable to change to working directory')

    def complete_select(self, text, line, begidx, endidx):
        """
        This method runs when the CLI wants to tab-complete a 'select' command.

        We will receive text (which could be blank) or contain a substring
        and line which will include the full line including the command itself.
        """
        if len(text.split()) == 0:
            return self.testcases_filesys

        result = []
        for item in self.testcases_filesys:
            if item[0:len(text)] == text:
                result.append(item)
        result.sort()
        return result

    def do_select(self, args):
        'Select a File containing python unittests'
        self.tests = {}

        if self.python_unittest:
            if not os.path.exists('test_%s.py' % (args)):
                self.xterm_message('Unable to open test case %s from %s' %
                                   (args, os.getcwd()), Fore.RED, newline=True)
                return False

            self.xterm_message('Loading file....', Fore.YELLOW)
            self._select_test_cases_from_directory(args)

        if self.python_behave:
            if not os.path.exists('%s.feature' % (args)):
                self.xterm_message('Unable to open feature %s from %s' %
                                   (args, os.getcwd()), Fore.RED, newline=True)
                return False

            self.xterm_message('Loading file....', Fore.YELLOW)
            self._select_feature_from_directory(args)

    def _select_feature_from_directory(self, args):
        self.testcase = args
        # in the case of a scenario a test is a scenario
        self.tests[args] = {'class': None, 'feature': None, 'tests': [], 'tags': {}}

        feature = None
        lasttag = None
        regex_feature = re.compile('^Feature: (.*)')
        regex_scenario = re.compile('^\s*Scenario: (.*)')
        regex_tag = re.compile('^\s*@(\S+)\s*$')

        with open('%s.feature' % (args)) as file:
            line = file.readline()
            while line != "":
                if regex_feature.match(line):
                    feature = regex_feature.sub('\g<1>', line).rstrip()
                    self.tests[self.testcase]['feature'] = feature
                if regex_scenario.match(line):
                    scenario = regex_scenario.sub('\g<1>', line).rstrip()
                    self.tests[self.testcase]['tests'].append(scenario)
                    if lasttag:
                        self.tests[self.testcase]['tags'][scenario] = lasttag
                lasttag = None
                if regex_tag.match(line):
                    lasttag = regex_tag.sub('\g<1>', line).rstrip()
                line = file.readline()

        self.prompt = 'tester(%s.%s.%s)%% ' % (self.truncate_prompt(self.testdir), args, feature)
        self.xterm_message('Loaded %s scenario(s) from %s' % (len(self.tests[args]['tests']), args),
                           Fore.GREEN, oldmsg='Loading file....', newline=True)

    def _select_test_cases_from_directory(self, args):
        #        self.xterm_message('Running from %s' % (os.getcwd()), Fore.CYAN, newline=True, style=Style.DIM)
        self.testcase = args
        self.tests[args] = {'class': None, 'feature': None, 'tests': [], 'tags': {}}
        regex_import = re.compile('^import unittest\s*$')
        regex_class = re.compile('^class (\S+)\(.*[tT]est.*\):\s*$')
        regex_test = re.compile('^ {4}def test_([^\(]+)\(.*:\s*$')
        found_import = False
        found_class = None

        with open('test_%s.py' % (args)) as file:
            line = file.readline()
            while line != "":
                if regex_import.match(line):
                    found_import = True
                if regex_class.match(line) and found_class is None:
                    found_class = regex_class.sub('\g<1>', line)
                elif regex_class.match(line) and found_class is not None:
                    self.xterm_message('Constraint: only one unittest class supported.',
                                       Fore.RED, oldmsg='Loading file....', newline=True)
                    return False
                if regex_test.match(line):
                    self.tests[self.testcase]['tests'].append(regex_test.sub('\g<1>', line))
                line = file.readline()

        if found_class is None:
            self.xterm_message('Unable to find class from the testcase file %s' % (file),
                               Fore.RED, oldmsg='Loading file....', newline=True)
            return False

        self.prompt = 'tester(%s.%s.%s)%% ' % (self.truncate_prompt(self.testdir), args, found_class)
        self.tests[args]['class'] = found_class
        self.xterm_message('Loaded %s test(s) from %s' % (len(self.tests[args]['tests']), args),
                           Fore.GREEN, oldmsg='Loading file....', newline=True)

    def do_run(self, args):
        'Run a test (or set of tests)'
        if self.workingdir:
            os.chdir(self.workingdir)
            sys.path.insert(0, self.workingdir)
        self.xterm_message('Running from %s' % (os.getcwd()), Fore.CYAN, newline=True, style=Style.DIM)
        try:
            if self.python_unittest:
                self._execute_unit_tests(args)
            elif self.python_behave:
                self._execute_feature_files(args)
        except Exception as err:
            self.xterm_message(traceback.format_exc(), Fore.RED, newline=True, style=Style.DIM)
            self._error()
        if self.workingdir:
            os.chdir(self.testdir)
        self._ok()

    def _execute_feature_files(self, args):
        for test in self.tests:
            self.xterm_message('%s' % (test))
            config = behave.configuration.Configuration(["-f", "null", "--no-summary",
                                                         "%s.feature" % (test)])
            runner = behave.runner.Runner
            result = run_behave(config, runner)

            self.xterm_message('%s' % (test), Fore.GREEN, style=Style.NORMAL, oldmsg='%s' % (test))
            print('')

    def _execute_unit_tests(self, args):
        """
        Execute python unit test and save a basic summary into the following place.
        $HOME/.pyunittest/hash

        The test cases are executed wtih coverage enabled.
        """
        self.failures = {}
        if hasattr(Cmd, 'do_rerun'):
            del Cmd.do_rerun

        if len(self.tests) == 0:
            for test in os.listdir('./'):
                if test[0:5] == 'test_' and test[-3:] == '.py':
                    self.testcase = test[5:-3]
                    self._select_test_cases_from_directory(self.testcase)

        count = 0
        suite = unittest.TestSuite()
        for testcase in self.tests:
            msg = 'Testcase %s ' % (testcase)
            if self.tests[testcase]['class']:
                self.xterm_message(msg, Fore.MAGENTA, oldmsg=msg)
                tests_to_run = []
                for item in self.tests[testcase]['tests']:
                    if item[0:len(args)] == args:
                        tests_to_run.append(item)
                        count = count + 1
                msg = 'Running %s tests(s)...      ' % (len(tests_to_run))
                module = None
                self.xterm_message(msg, Fore.MAGENTA, newline=True)
                try:
                    module = importlib.import_module('test_%s' % (testcase))
                except ImportError as err:
                    self.xterm_message('Unable to import testcase file - perhaps python is battered and bruised :-(\n%s' %
                                       (str(err)), Fore.RED, newline=True)
                    self.xterm_message(traceback.format_exc(), Fore.RED, newline=True, style=Style.DIM)

                if module:
                    try:
                        class__ = '%s' % (self.tests[testcase]['class'])
                        class_ = getattr(module, class__)
                        for item in tests_to_run:
                            suite.addTest(class_('test_%s' % (item)))
                    except AttributeError as err:
                        self.xterm_message('Unable to instantiate class - perhaps there is no valid test case defined in this file :-(\n%s' %
                                           (str(err)), Fore.RED, newline=True)

        cov = Coverage()
        cov.start()
        results = unittest.TextTestRunner(verbosity=9).run(suite)
        cov.stop()
        cov.html_report(directory='covhtml')

        # Remove modules
        module_to_remove = []
        for c in range(50):
            try:
                for mod in sys.modules:
                    if hasattr(sys.modules[mod], '__file__') and sys.modules[mod].__file__[0:len(self.workingdir)] == self.workingdir:
                        module_to_remove.append(mod)
                    elif mod[0:5] == "test_":
                        module_to_remove.append(mod)
            except Exception as err:
                pass
                # We may get a RuntimeError that the dict sys.modules change size during iteration

        for mod in module_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]

        for (testcase, string) in results.failures:
            raise ValueError('we dont handle failures')

        error_count = 0
        unique_failures = {}
        for (testcase, string) in results.errors:
            if string not in unique_failures:
                unique_failures[string] = []
            unique_failures[string].append(testcase)
            error_count = error_count + 1

        if error_count == 0:
            self.xterm_message("\n\nRun %s tests with 0 errors" % (count), Fore.GREEN, newline=True, style=Style.NORMAL)
            return False

        self.xterm_message("\n\nRun %s tests with %s errors" % (count, error_count), Fore.RED, newline=True, style=Style.NORMAL)

        erridx = 0
        for error in unique_failures:
            erridx = erridx + 1
            print("     %s   %s cases of the following error" % (erridx, len(unique_failures[error])))
            for line in error.split('\n'):
                print("          %s" % (line))
            for test in unique_failures[error]:
                print("            %s" % (test))
                cosmetic_name = str(test).split(' ')[0][5:]
                self.failures[cosmetic_name] = str(test)
        self.xterm_message("Run %s tests with %s errors" % (count, error_count), Fore.RED, newline=True, style=Style.NORMAL)

        Cmd.do_rerun = self._do_rerun
        Cmd.complete_rerun = self._complete_rerun

    def _do_rerun(self, args):
        """re-run test cases which have recently failed."""
        print("Not implemented - want to rerun args: ", args, "This may not be a valid test")

    def _complete_rerun(self, text, line, begidx, endidx):
        failures = []
        if line == 'rerun ':
            for failure in self.failures:
                failures.append(failure)
        else:
            for failure in self.failures:
                if failure[0:len(text)] == text:
                    failures.append(failure)
        failures.sort()
        return failures


if __name__ == '__main__':
    cli = testnavigator()
    if len(sys.argv) < 2:
        testnavigator.xterm_message("""Usage: %s <directory>""" % (sys.argv[0]), Fore.RED, newline=True)
        sys.exit(1)
    if not os.path.exists(sys.argv[1]):
        testnavigator.xterm_message("""Usage: %s <directory>\n\n%s does not exist""" %
                                    (sys.argv[0], sys.argv[1]), Fore.RED, newline=True)
        sys.exit(1)
    testdir = sys.argv[1]
    cli.workingdir = str(os.getcwd())
    cli.homedir = os.environ['HOME']
    cli.full_workingdir = os.path.abspath(cli.workingdir)
    # This should be an option.
    # recursively loop arounf each sub directory adding it to the path

    def add_to_sys_path(pwd):
        have_py = False
        for filething in os.listdir(pwd):
            if os.path.isdir(pwd + '/' + filething) and not filething[0] == '.':
                add_to_sys_path(pwd + '/' + filething)
            elif filething[-3:] == '.py':
                have_py = True
        if have_py:
            sys.path.append(pwd)
    add_to_sys_path(os.getcwd())

    os.chdir(testdir)
    tmp_test_dir = testdir.encode('UTF-8')
    cli.test_hash = hashlib.sha1(tmp_test_dir).hexdigest()

    if not os.path.exists(cli.homedir + '/.pyunittestcli'):
        os.mkdir(cli.homedir + '/.pyunittestcli')
    if not os.path.exists(cli.homedir + '/.pyunittestcli/%s' % (cli.test_hash)):
        os.mkdir(cli.homedir + '/.pyunittestcli/%s' % (cli.test_hash))

    if os.path.exists(cli.homedir + '/.pyunittestcli/python_path.json'):
        o = open(cli.homedir + '/.pyunittestcli/python_path.json')
        j = json.loads(o.read())
        o.close()
        if cli.full_workingdir in j:
            paths = j[cli.full_workingdir]
            for path in paths:
                sys.path.insert(0, path)

    cli.base_dir = os.getcwd()
    sys.argv.pop(1)
    sys.path.insert(0, cli.base_dir)
    cli.testdir = testdir
    cli.testcases_filesys = []
    cli.python_unittest = False
    cli.python_behave = False

    def add_to_test_path(cli, pwd, recurse=True):
        """
        Recurse around the directory adding tests to be executed.

        Each file containing tests will be added to the dictionaries so
        that we can run all test cases immediately.

        """
        for test in os.listdir(pwd):
            if test == '__pycache__':
                pass
            elif os.path.isdir(pwd + test) and not test[0] == '.':
                add_to_test_path(cli, pwd + '/' + test)
            elif test[0:5] == 'test_' and test[-3:] == '.py':
                test_name = pwd + '/' + test[5:-3]
                cli.testcases_filesys.append(test_name.replace('./', '').split('/')[-1])
                cli.python_unittest = True
                if recurse:
                    cli._select_test_cases_from_directory(test[5:-3])
            elif test[-8:] == '.feature':
                feature_name = pwd + '/' + test[:-8]
                cli.testcases_filesys.append(feature_name.replace('./', '').split('/')[-1])
                if recurse:
                    cli._select_feature_from_directory(feature_name.replace('./', '').replace('//', '/'))
                cli.python_behave = True

    recurse = False
    if len(sys.argv) == 1:
        recurse = True
    elif len(sys.argv) == 2 and sys.argv[-1] == 'run':
        recurse = True
    elif len(sys.argv) == 3 and sys.argv[-2] == 'run' and sys.argv[-1] == 'exit':
        recurse = True
    add_to_test_path(cli, cli.testdir, recurse=recurse)

    if cli.python_behave and cli.python_unittest:
        testnavigator.xterm_message("""Directory can only contain unittest's or feature files""", Fore.RED, newline=True)
        sys.exit(1)
    if not cli.python_behave and not cli.python_unittest:
        testnavigator.xterm_message("""Directory contains no unittest's or feature files""", Fore.RED, newline=True)
        sys.exit(1)

    cli.prompt = 'tester(' + cli.truncate_prompt(testdir) + ')% '
    cli.cmdloop(intro='Python Unittest Navigator')
