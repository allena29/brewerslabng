import unittest

from blng.Voodoo import DataAccess
from alchemy_cli import alchemy_voodoo_wrapper
import prompt_toolkit.validation


class TestAlchemySimple(unittest.TestCase):

    def setUp(self):
        self.session = DataAccess('crux-example.xml')
        self.root = self.session.get_root()
        self.subject = alchemy_voodoo_wrapper(self.root)

    def test_go_into_conf_mode_and_exit_again(self):

        # Action & Assert
        self.assertEqual(self.subject.mode, 0)
        self.subject.do('configure')
        self.assertEqual(self.subject.mode, 1)
        self.assertEqual(self.subject.OUR_PROMPT, 'brewer@localhost% ')
        self.subject.do('exit')
        self.assertEqual(self.subject.mode, 0)
        self.assertEqual(self.subject.OUR_PROMPT, 'brewer@localhost> ')

    def test_handle_completion_for_command(self):

        results = self.subject._handle_completion_for_command('')
        self.assertGeneratorReturnedEverything(results, ['configure', 'exit'])

        results = self.subject._handle_completion_for_command('c')
        self.assertGeneratorReturnedEverything(results, ['configure'])

        results = self.subject._handle_completion_for_command('z')
        self.assertGeneratorReturnedEverything(results, [])

    def test_handle_completion_for_command_with_path_show_commands(self):
        self.subject._complete_obj = self.root

        results = self.subject._handle_completion_for_command_with_path('show', 'm', 'show m')
        self.assertGeneratorReturnedEverything(results, ['morecomplex'])
        self.assertEqual(self.subject._complete_terminated, -1)

        results = self.subject._handle_completion_for_command_with_path('show', 'morecomplex', 'show morecomplex')
        self.assertGeneratorReturnedEverything(results, ['morecomplex'])

    def test_handle_completion_for_command_with_path_set_commands(self):
        self.subject._complete_obj = self.root

        results = self.subject._handle_completion_for_command_with_path('set', 'm', 'set m')
        self.assertGeneratorReturnedEverything(results, ['morecomplex'])

        results = self.subject._handle_completion_for_command_with_path('set', 'morecomplex', 'set morecomplex')
        self.assertGeneratorReturnedEverything(results, ['morecomplex'])

    def test_handle_completion_for_command_with_path_set_commands_deeper_levels(self):
        """
        Storing lots of start on the object makes unit tests much trickier.
        However, given the auto-complete and validate methods are called many times we need
        somewhere to avoid doing large crunching everytime.
        """

        self.subject._complete_obj = self.root
        results = self.subject._handle_completion_for_command_with_path('show', 'bronze', 'show bronze')
        self.drainGenerator(results)
        self.assertEqual(self.subject._complete_obj._path, '/bronze')
        self.assertGeneratorReturnedEverything(results, [])

        # Note: here the auto completes don't appear until after we type space.
        # This looks most consistent with most auto completes.
        results = self.subject._handle_completion_for_command_with_path('show bronze', '', 'show bronze ')
        self.assertGeneratorReturnedEverything(results, ['silver'])

        results = self.subject._handle_completion_for_command_with_path('show bronze', 'silver', 'show bronze silver')
        self.drainGenerator(results)
        self.assertEqual(self.subject._complete_obj._path, '/bronze/silver')

        results = self.subject._handle_completion_for_command_with_path('show bronze silver', 'g', 'show bronze silver g')
        self.assertGeneratorReturnedEverything(results, ['gold'])

    def test_validate_command(self):

        results = self.subject._handle_completion_for_command_with_path('show', 'simpleleaf', 'show simpleleaf')
        self.assertGeneratorReturnedEverything(results, ['simpleleaf'])
        self.assertEqual(self.subject._complete_terminated, 15)  # this means if the command is <=15 we know backspace was used.
        # otherwise validate will complain.

        with self.assertRaises(prompt_toolkit.validation.ValidationError) as context:
            self.subject.validate(Document('foo this needs to be greater than 15 characters'))
        self.assertEqual(str(context.exception), "Stop typing!")

        self.subject.validate(Document('foo'))
        # Now we have validated a command which is small we should have reset the flag.
        self.assertEqual(self.subject._complete_terminated, -1)

    def assertGeneratorReturnedEverything(self, results, required_results):
        """
        Helper to compare the results of generators.
        """
        not_found_results = list(required_results)
        extra_results = []

        for result in results:

            if result.text not in required_results:
                extra_results.append(result.text)
            for required_result in required_results:
                if result.text == required_result:
                    not_found_results.remove(required_result)
                    break

        if len(not_found_results) and len(extra_results):
            self.fail('Results not found %s\nExtra results found %s' % (str(not_found_results), str(extra_results)))
        if len(not_found_results):
            self.fail('Results not found %s' % (str(not_found_results)))
        if len(extra_results):
            self.fail('Extra results found %s' % (str(extra_results)))

    def drainGenerator(self, gen):
        try:
            while 1:
                next(gen)
        except StopIteration:
            pass


class Document:
    def __init__(self, text):
        self.text = text
