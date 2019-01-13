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
        (path, pathtype, value) = self.subject._find_xpath('resolver leaf-a 242')

        self.assertEqual(path, '/resolver/leaf-a')
        self.assertEqual(pathtype, 'primitive')
        self.assertEqual(value, '242')

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

    def test_find_types_allowed(self):
        types = self.subject._find_types_allowed('/simpleleaf')
        self.assertEqual([('type', 'string', None)], types)

        types = self.subject._find_types_allowed('/morecomplex/leaf4')
        self.assertEqual([('literal', 'A', None),
                          ('literal', 'B', None),
                          ('literal', 'C', None),
                          ('type', 'uint32', None)
                          ], types)

        types = self.subject._find_types_allowed('/simpleenum')
        self.assertEqual([('literal', 'A', None)], types)

        types = self.subject._find_types_allowed('/simplelist')
        self.assertEqual([('list', ['simplekey'], None)], types)
