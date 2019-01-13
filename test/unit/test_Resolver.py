import unittest
import os
import sys
sys.path.append('../../')
from blng import Resolver
from blng import Error
from example import resources


class TestCruxResolver(unittest.TestCase):

    def setUp(self):

        self.subject = Resolver.Resolver(open("crux-example.xml"))
        """
    TODO:
    SCHEMA_1 = resources.SCHEMA_1
    CRUX_SCHEMA = resources.CRUX_XML

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

        # (cmd, xpath, values) = self.subject.resolve("set morecomplex composite-key-list abc 987")
        # self.assertEqual(cmd, "set")
        # self.assertEqual(xpath, "/morecomplex/composite-key-list")
        # self.assertEqual(values, ["abc", "987"])

    def test_resolving_top_level(self):


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
    """

    def test_find_command(self):
        (command, everythingelse) = self.subject._find_command('set abc')

        self.assertEqual(command, 'set')
        self.assertEqual(everythingelse, 'abc')

    def test_resolve_xpath_simple_path_at_top_level(self):
        (path, pathtype, value) = self.subject._find_xpath('simpleleaf thevalue')

        self.assertEqual(path, '/simpleleaf')
        self.assertEqual(pathtype, 'primitive')
        self.assertEqual(value, 'thevalue')

    def test_resolve_xpath_simple_path_at_top_level_in_a_container(self):
        (path, pathtype, value) = self.subject._find_xpath('resolver leaf-a A')

        self.assertEqual(path, '/resolver/leaf-a')
        self.assertEqual(pathtype, 'primitive')
        self.assertEqual(value, 'A')

    def test_resolve_xpath_simple_list(self):
        (path, pathtype, value) = self.subject._find_xpath('simplelist THEKEY')

        self.assertEqual(path, "/simplelist[simplekey='THEKEY']")
        self.assertEqual(pathtype, 'listelement')
        self.assertEqual(value, [('simplekey', 'THEKEY')])

    def test_resolve_xpath_containers_and_lsits(self):
        (path, pathtype, value) = self.subject._find_xpath('container-and-lists multi-key-list antelope bear')

        self.assertEqual(path, "/container-and-lists/multi-key-list[A='antelope',B='bear']")
        self.assertEqual(pathtype, 'listelement')
        self.assertEqual(value, [('A', 'antelope'), ('B', 'bear')])

        (path, pathtype, value) = self.subject._find_xpath('container-and-lists multi-key-list antelope bear inner C cow')

        self.assertEqual(path, "/container-and-lists/multi-key-list[A='antelope',B='bear']/inner/C")
        self.assertEqual(pathtype, 'primitive')
        self.assertEqual(value, 'cow')

        # try to set a container as if it was a leaf
        with self.assertRaises(Error.BlngUnableToResolveString) as context:
            (path, pathtype, value) = self.subject._find_xpath('container-and-lists multi-key-list antelope bear inner cow')
        self.assertEqual(str(context.exception),
                         """The path ['container-and-lists', 'multi-key-list', 'antelope', 'bear', 'inner', 'cow'] could not be resolved against the current schema.""")

    def test__ensure_remaining_path_is_a_properly_escaped_string_not_properly_quoted(self):
        with self.assertRaises(Error.BlngValueNotEscpaedOrQuoted) as context:
            self.subject._find_a_quoted_escaped_string(['key', '"value', 'thing'], 1)

        self.assertEqual(str(context.exception), """Unquoted or Unescaped characters ['key', '"value', 'thing'] value not properly escaped or quoted""")

    def test__ensure_remaining_path_is_a_properly_escaped_string_not_properly_quoted_too_many_quotes(self):
        with self.assertRaises(Error.BlngValueNotEscpaedOrQuoted) as context:
            self.subject._find_a_quoted_escaped_string(['key', '"value', 'thin"g'], 1)

        self.assertEqual(str(context.exception), """Unquoted or Unescaped characters ['key', '"value', 'thin"g'] value not properly escaped or quoted""")

    def test__find_a_quoted_escaped_string(self):
        value = self.subject._find_a_quoted_escaped_string(['key', 'value'], 1)
        self.assertEqual(value, ('value', 2, 2))

        value = self.subject._find_a_quoted_escaped_string(['key', '"value', 'thing"'], 1)
        self.assertEqual(value, ('value thing', 1, 2))

        value = self.subject._find_a_quoted_escaped_string(['key', '"value', 'extra', 'thing"'], 1)
        self.assertEqual(value, ('value extra thing', 1, 3))

        value = self.subject._find_a_quoted_escaped_string(['key', 'value\\', 'ex"tra\\', 'thing'], 1)
        self.assertEqual(value, ('value ex"tra thing', 1, 3))

    def est__ensure_TODOr(self):
        raise ValueError('think shaed - we need more advanced handling because list keys (and compositse) can be followed by more xpath and schema stuff).')
        raise ValueError('we probably want to convert things into true xpath when we encounter keys')
        raise ValueError('but of course when we do encounter a list we will have yin schema which will tell us exactly how many keys there are so we can')
        raise ValueError('make the lookup somewhat recursive even if the string can be a simpler implementaiton')
        with self.assertRaises(Error.BlngValueNotEscpaedOrQuoted) as context:
            self.subject._ensure_remaining_path_is_a_properly_escaped_string(['key', '"value', 'thin"g'], 1)

        self.assertEqual(str(context.exception), "['key', '\"value', 'thin\"g'] value not properly escaped or quoted")
