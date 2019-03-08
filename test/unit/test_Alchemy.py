import unittest

from blng.Voodoo import DataAccess
from alchemy_cli import alchemy_voodoo_wrapper


class TestAlchemySimple(unittest.TestCase):

    def test_go_into_conf_mode_and_exit_again(self):
        # Build
        session = DataAccess('crux-example.xml')
        root = session.get_root()
        self.subject = alchemy_voodoo_wrapper(root)

        # Action & Assert
        self.assertEqual(self.subject.mode, 0)
        self.subject.do('configure')
        self.assertEqual(self.subject.mode, 1)
        self.assertEqual(self.subject.OUR_PROMPT, 'brewer@localhost% ')
        self.subject.do('exit')
        self.assertEqual(self.subject.mode, 0)
        self.assertEqual(self.subject.OUR_PROMPT, 'brewer@localhost> ')
