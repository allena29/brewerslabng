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
