import unittest
import os
import sys
sys.path.append('../../')
from blng import Resolver
from blng import Error
from example import resources


class TestCruxResolver(unittest.TestCase):

    SCHEMA_1 = resources.SCHEMA_1
    CRUX_SCHEMA = resources.CRUX_XML

    def setUp(self):

        self.subject = Resolver.Resolver()
        self.subject.register_top_tag("/simpleleaf", "http://brewerslabng.mellon-collie.net/yang/integrationtest", "integrationtest")
        self.subject.register_top_tag("/morecomplex", "http://brewerslabng.mellon-collie.net/yang/integrationtest", "integrationtest")

        yin_file = open(".cache/integrationtest.yin", "w")
        yin_file.write(self.SCHEMA_1)
        yin_file.close()

        if not os.path.exists(".cache/__crux-schema.xml"):
            crux_schema_file = open(".cache/__crux-schema.xml", "w")
            crux_schema_file.write(self.CRUX_XML)
            crux_schema_file.close()
    # def test_basic_lookup_of_a_top_level(self):
    #    self.subject.show('')

    def test_find_schema_definition_for_path_not_registered(self):

        # Act
        with self.assertRaises(Error.BlngPathNotValid) as context:
            self.subject._find_schema_definition_for_path('/ficticiuosus/sdff/sdfsdf')
        self.assertEqual(str(context.exception), "/ficticiuosus/sdff/sdfsdf is not valid.")

    def test_find_schema_definition_for_path_registered_simple_path(self):
        # Act
        self.subject._find_schema_definition_for_path('/morecomplex/leaf2')
        self.assertTrue(str(["morecomplex", "leaf2"]) in self.subject.path_lookup_cache)

    def test_find_schema_definition_for_path_registered_composite_list_case(self):
        # Act
        todo = ""
        self.subject._find_schema_definition_for_path('/morecomplex/composite-key-list/keyone/keytwo')
        self.assertEqual(todo, "this should be the schema for /morecomplex/composite-key-list")
        self.assertTrue(str(["morecomplex", "composite-key-list", "keyone", "keytwo"]) in self.subject.path_lookup_cache)

    def test_load_simple_schema(self):
        """Basic test of loeading a schema"""
        # Act
        (result_module_name, result_module) = self.subject._load_schema_to_memory('integrationtest')

        # Assert
        self.assertEqual(list(self.subject.module_cache.keys()), ['integrationtest'])
        self.assertEqual(self.subject.path_lookup_cache[str(["simpleleaf"])], result_module)
        self.assertEqual(result_module_name, "integrationtest")
        self.assertEqual(result_module, self.subject.module_cache["integrationtest"])

        # Act
        (result_module_name, result_module2) = self.subject._load_schema_to_memory('integrationtest')

        # Assert
        self.assertEqual(list(self.subject.module_cache.keys()), ['integrationtest'])
        self.assertEqual(self.subject.path_lookup_cache[str(["simpleleaf"])], result_module)
        self.assertEqual(result_module_name, "integrationtest")
        self.assertEqual(result_module, self.subject.module_cache["integrationtest"])
        self.assertEqual(result_module, result_module2)

    def test_some_bad_cases(self):
        (cmd, xpath, values) = self.subject.resolve("set morecomplex composite-key-list abc ABC\" \"987 654\"")
        self.assertEqual(cmd, "set")
        self.assertEqual(xpath, "/morecomplex/composite-key-list")
        self.assertEqual(values, ["abc ABC", "987 654"])

    def test_resolving_inner(self):
        (cmd, xpath, values) = self.subject.resolve("show morecomplex leaf2")
        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/morecomplex/leaf2")
        self.assertEqual(values, [])

        (cmd, xpath, values) = self.subject.resolve("set morecomplex composite-key-list \"abc ABC\" \"987 654\"")
        self.assertEqual(cmd, "set")
        self.assertEqual(xpath, "/morecomplex/composite-key-list")
        self.assertEqual(values, ["abc ABC", "987 654"])

        #(cmd, xpath, values) = self.subject.resolve("set morecomplex composite-key-list abc 987")
        #self.assertEqual(cmd, "set")
        #self.assertEqual(xpath, "/morecomplex/composite-key-list")
        #self.assertEqual(values, ["abc", "987"])

    def test_resolving_top_level(self):
        """
        Basic test of resolving things at the top level, we should always be given back
        a command, xpath and values
        """

        (cmd, xpath, values) = self.subject.resolve("show")
        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/")
        self.assertEqual(values, [])
        (cmd, xpath, values) = self.subject.resolve("show simpleleaf")

        self.assertEqual(cmd, "show")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(values, [])

        (cmd, xpath, values) = self.subject.resolve("set simpleleaf \"abc 1234\"")
        self.assertEqual(cmd, "set")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(values, ["abc 1234"])

        (cmd, xpath, values) = self.subject.resolve("set simpleleaf abc1234")
        self.assertEqual(cmd, "set")
        self.assertEqual(xpath, "/simpleleaf")
        self.assertEqual(values, ["abc1234"])

        (cmd, xpath, values) = self.subject.resolve("show simplecontainer")
        self.assertEqual(cmd, 'show')
        self.assertEqual(xpath, "/simplecontainer")
        self.assertEqual(values, [])
