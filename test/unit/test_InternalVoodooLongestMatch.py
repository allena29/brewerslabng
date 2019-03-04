
import os
import sys
import unittest
from mock import Mock, call, ANY, patch
sys.path.append('../../')
import os
import blng.Voodoo
from lxml import etree


class CruxVoodooRootExtended(blng.Voodoo.CruxVoodooRoot):

    def _getxmlnode(self, path):
        """
        This is a workaround using side_effects from Mock is triggering __getattr__
        and __setattr__ from the VoodooNode.
        """
        print('_getxmlnode of ', self, 'called for path', path)
        self.__dict__['_getxmlnode_side_effects_index'] = self.__dict__['_getxmlnode_side_effects_index'] + 1
        return self.__dict__['_getxmlnode_side_effects'][self.__dict__['_getxmlnode_side_effects_index'] - 1]

        return []

    def _populate_children(self):
        pass


class TestLog:

    def debug(self, *args, **kwargs):
        print('DEBUG', args, kwargs)

    def info(self, *args, **kwargs):
        print('INFO', args, kwargs)


class TestVoodooInternals(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

        self.log = Mock()
        self.log = TestLog()
        # for child in etree.parse("crux-example.xml").getroot().getchildren():
        #    if child.tag == 'inverted-schema':
        #        self._schema = child

        self.keystore_cache = Mock()  # blng.Voodoo.CruxVoodooCache(self.log, 'keystore')
        self.schema_cache = Mock()  # blng.Voodoo.CruxVoodooCache(self.log, 'schema')
        self._cache = (self.keystore_cache, self.schema_cache)
        self._xmldoc = Mock()  # CruxVoodoBackendWrapper()
        self._schema = Mock()

    def test_find_longest_match_on_toplevel_node(self):
        """
        TODO:

        This method is making a very
        big assumption at this stage that it will not be called if the path does in fact exist.
        """
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)
        root.__dict__['_getxmlnode_side_effects'] = []
        root.__dict__['_getxmlnode_side_effects_index'] = 0

        path = '/voodoo/some'

        result = root._find_longest_match_path(self._xmldoc, path)

        self.assertNotEqual(self._xmldoc, result)
        self.assertNotEqual(None, result)
        self._xmldoc.append.assert_has_calls([call(ANY)])

    @patch("lxml.etree.Element")
    def test_find_longest_match(self, mockElement):
        """
        This test is an empty root so we have to go all the way back to the start
        """
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)
        root.__dict__['_getxmlnode_side_effects'] = [[], [], [], []]
        root.__dict__['_getxmlnode_side_effects_index'] = 0

        path = '/voodoo/some/path/to/find/deep'

        """
        We expect the longest match will look for
         /some/path/to/find
         /some/path/to
         /some/path/
         /some

        Since every call to getxmlnode returned nothing we ended up at the start.
        """
        result = root._find_longest_match_path(self._xmldoc, path)

        mockElement.assert_has_calls([
            call('some'),
            call('path'),
            call().append(ANY),
            call('to'),
            call().append(ANY),
            call('find'),
            call().append(ANY),
            call('deep'),
            call().append(ANY)
        ])

        self.assertNotEqual(self._xmldoc, result)
        self.assertNotEqual(None, result)

    @patch("lxml.etree.Element")
    def test_find_longest_match_matching_halfway(self, mockElement):
        """
        This test is an empty root so we have to go all the way back to the start
        """
        some_path_element_halfway = Mock()
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)
        root.__dict__['_getxmlnode_side_effects'] = [[], [], [some_path_element_halfway]]

        root.__dict__['_getxmlnode_side_effects_index'] = 0

        path = '/voodoo/some/path/to/find/deep'

        """
        We expect the longest match will look for
         /some/path/to/find
         /some/path/to
         /some/path/        <-- this is our mock


        Since every call to getxmlnode returned nothing we ended up at the start.
        """
        result = root._find_longest_match_path(self._xmldoc, path)

        mockElement.assert_has_calls([
            call('find'),
            call().append(ANY),
            call('deep'),
            call().append(ANY),
        ])

        self.assertNotEqual(self._xmldoc, result)
        self.assertNotEqual(None, result)

    @patch("lxml.etree.Element")
    def test_find_longest_match_matching_halfway_list_keys(self, mockElement):
        """
        This test is an empty root so we have to go all the way back to the start
        """
        some_path_element_halfway = Mock()
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)
        root.__dict__['_getxmlnode_side_effects'] = [[], [], [some_path_element_halfway]]

        root.__dict__['_getxmlnode_side_effects_index'] = 0

        path = "/voodoo/some/path/to/find/deep[key='sdf']"

        """
        We expect the longest match will look for
         /some/path/to/find
         /some/path/to
         /some/path/        <-- this is our mock


        Since every call to getxmlnode returned nothing we ended up at the start.
        """
        result = root._find_longest_match_path(self._xmldoc, path)

        mockElement.assert_has_calls([
            call('to'),
            call('find'),
            call().append(ANY),
            call('deep'),
            call().append(ANY),
            call('key'),
            call().attrib.__setitem__('listkey', 'yes'),
            call().append(ANY)
        ])

        self.assertNotEqual(self._xmldoc, result)
        self.assertNotEqual(None, result)

    @patch("lxml.etree.Element")
    def test_find_longest_match_matching_halfway_composite_list_keys(self, mockElement):
        """
        This test is an empty root so we have to go all the way back to the start
        """
        some_path_element_halfway = Mock()
        root = CruxVoodooRootExtended(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)
        root.__dict__['_getxmlnode_side_effects'] = [[], [], [some_path_element_halfway]]

        root.__dict__['_getxmlnode_side_effects_index'] = 0

        path = "/voodoo/some/path/to/find/deep[key='sdf'][key2='abc']"

        """
        We expect the longest match will look for
         /some/path/to/find
         /some/path/to
         /some/path/        <-- this is our mock


        Since every call to getxmlnode returned nothing we ended up at the start.
        """
        result = root._find_longest_match_path(self._xmldoc, path)

        mockElement.assert_has_calls([
            call('to'),
            call('find'),
            call().append(ANY),
            call('deep'),
            call().append(ANY),
            call('key'),
            call().attrib.__setitem__('listkey', 'yes'),
            call().append(ANY),
            call('key2'),
            call().attrib.__setitem__('listkey', 'yes'),
            call().append(ANY),
        ])

        self.assertNotEqual(self._xmldoc, result)
        self.assertNotEqual(None, result)
