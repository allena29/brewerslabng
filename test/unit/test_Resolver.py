import unittest
import sys
sys.path.append('../../')
from blng import Resolver
from example import resources


class TestCruxResolver(unittest.TestCase):

    SCHEMA_1 = resources.SCHEMA_1

    def setUp(self):

        self.subject = Resolver.Resolver()
        self.subject.register_top_tag("simpleleaf", "http://brewerslabng.mellon-collie.net/yang/integrationtest")

        yin_file = open(".cache/integrationtest.yin", "w")
        yin_file.write(self.SCHEMA_1)
        yin_file.close()

    # def test_basic_lookup_of_a_top_level(self):
    #    self.subject.show('')

    def test_load_simple_schema(self):
        """Basic test of loeading a schema"""
        # Act
        self.subject.load_schema_to_memory('simpleleaf', 'integrationtest')

        # Assert
        self.assertEqual(list(self.subject.in_memory.keys()), ['integrationtest'])

    def test_resolving_inner(self):
        (cmd, xpath, value) = self.subject.resolve("show morecomplex leaf2")
        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/morecomplex/leaf2")
        self.assertEqual(value, None)

    def test_resolving_top_level(self):
        """
        Basic test of resolving things at the top level, we should always be given back
        a command, xpath and value
        """

        (cmd, xpath, value) = self.subject.resolve("show")
        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/")
        self.assertEqual(value, None)
        (cmd, xpath, value) = self.subject.resolve("show simpleleaf")

        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(value, None)

        (cmd, xpath, value) = self.subject.resolve("set simpleleaf \"abc 1234\"")
        self.assertEqual(cmd, "set")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(value, "abc 1234")

        (cmd, xpath, value) = self.subject.resolve("set simpleleaf \"abc 1234\"")
        self.assertEqual(cmd, "set")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(value, "abc 1234")

        (cmd, xpath, value) = self.subject.resolve("show simplecontainer")
        self.assertEqual(cmd, 'show')
        self.assertEqual(xpath, "/simplecontainer")
        self.assertEqual(value, None)
