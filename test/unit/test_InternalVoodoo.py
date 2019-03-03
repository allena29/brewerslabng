
import os
import sys
import unittest
from mock import Mock, call
sys.path.append('../../')
import os
import blng.Voodoo
from lxml import etree


class CruxVoodooRootExtended(blng.Voodoo.CruxVoodooRoot):

    def _populate_children(self):
        pass


class TestVoodooInternals(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

        self.log = Mock()

        # for child in etree.parse("crux-example.xml").getroot().getchildren():
        #    if child.tag == 'inverted-schema':
        #        self._schema = child

        self.keystore_cache = Mock()  # blng.Voodoo.CruxVoodooCache(self.log, 'keystore')
        self.schema_cache = Mock()  # blng.Voodoo.CruxVoodooCache(self.log, 'schema')
        self._cache = (self.keystore_cache, self.schema_cache)
        self._xmldoc = Mock()  # CruxVoodoBackendWrapper()
        self._schema = Mock()

    def test_get_schema_from_root_node_path_does_not_exist(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//morecomplex'

        self.schema_cache.is_path_cached.side_effect = [False]
        self._schema.xpath.side_effect = [[]]

        # Act
        with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
            root._getschema(path)

        # Assert
        self.schema_cache.is_path_cached.assert_called_once_with(path)
        self.schema_cache.add_entry.assert_not_called()
        self._schema.xpath.assert_called_once_with(path)
        self.assertEqual(str(context.exception), "Unable to find '/morecomplex' in the schema")

    def test_get_schema_from_root_node_path_does_exist_cache_miss(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//morecomplex'

        self.schema_cache.is_path_cached.side_effect = [False]
        schema_element = Mock()
        self._schema.xpath.side_effect = [[schema_element]]

        # Act
        answer = root._getschema(path)

        # Assert
        self.schema_cache.is_path_cached.assert_called_once_with(path)
        self.schema_cache.add_entry.assert_called_once_with(path, schema_element)
        self._schema.xpath.assert_called_once_with(path)
        self.assertEqual(answer, schema_element)

    def test_get_schema_from_root_node_path_does_exist_cache_hit(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//morecomplex'

        self.schema_cache.is_path_cached.side_effect = [True]
        schema_element = Mock()
        self.schema_cache.get_item_from_cache.side_effect = [schema_element]

        # Act
        answer = root._getschema(path)

        # Assert
        self.schema_cache.is_path_cached.assert_called_once_with(path)
        self.schema_cache.add_entry.assert_not_called()
        self._schema.xpath.assert_not_called()

        self.assertEqual(answer, schema_element)

    def test_get_schema_from_root_node_path_does_exist_cache_miss_hyphen_case(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//container_and_lists'
        path_adjusted = '//container-and-lists'

        self.schema_cache.is_path_cached.side_effect = [False]
        schema_element = Mock()
        self._schema.xpath.side_effect = [[], [schema_element]]

        # Act
        answer = root._getschema(path)

        # Assert
        self.schema_cache.is_path_cached.assert_called_once_with(path)
        self.schema_cache.add_entry.assert_called_once_with(path, schema_element)
        self._schema.xpath.assert_has_calls([call(path), call(path_adjusted)])

        self.assertEqual(answer, schema_element)

    def test_get_xmlnode_from_root_cache_miss(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//morecomplex'

        self.keystore_cache.is_path_cached.side_effect = [False]
        schema_element = Mock()
        self._xmldoc.xpath.side_effect = [[schema_element]]

        # Act
        answer = root._getxmlnode(path)

        # Assert
        self.keystore_cache.is_path_cached.assert_called_once_with(path)
        self.keystore_cache.add_entry.assert_called_once_with(path, schema_element)
        self._xmldoc.xpath.assert_called_once_with(path)
        self.assertEqual(answer, [schema_element])

    def test_get_xmlnode_from_root_cache_miss_with_hyphens(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//more_complex'
        path_adjusted = '//more-complex'

        self.keystore_cache.is_path_cached.side_effect = [False]
        schema_element = Mock()
        self._xmldoc.xpath.side_effect = [[], [schema_element]]

        # Act
        answer = root._getxmlnode(path)

        # Assert
        self.keystore_cache.is_path_cached.assert_called_once_with(path)
        self.keystore_cache.add_entry.assert_called_once_with(path, schema_element)
        self._xmldoc.xpath.assert_has_calls([call(path), call(path_adjusted)])
        self.assertEqual(answer, [schema_element])

    def test_get_xmlnode_from_root_cache_hit(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//morecomplex'

        self.keystore_cache.is_path_cached.side_effect = [True]
        schema_element = Mock()
        self.keystore_cache.get_item_from_cache.side_effect = [schema_element]

        # Act
        answer = root._getxmlnode(path)

        # Assert
        self.keystore_cache.is_path_cached.assert_called_once_with(path)
        self.keystore_cache.add_entry.assert_not_called()
        self._xmldoc.xpath.assert_not_called()
        self.assertEqual(answer, [schema_element])

    def test_get_xmlnode_item_does_not_exist(self):
        # Build
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)

        path = '//notexisting'

        self.keystore_cache.is_path_cached.side_effect = [False]
        self._xmldoc.xpath.side_effect = [[], []]

        # Act
        answer = root._getxmlnode(path)

        # Assert
        self.keystore_cache.is_path_cached.assert_called_once_with(path)
        self.keystore_cache.add_entry.assert_not_called()
        self._xmldoc.xpath.assert_has_calls([call(path), call(path)])
