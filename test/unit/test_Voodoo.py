
import os
import sys
import unittest
from mock import Mock
sys.path.append('../../')
import blng.Voodoo


class TestVoodoo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

    def _get_session(self):
        self.subject = blng.Voodoo.DataAccess('crux-example.xml')
        self.root = self.subject.get_root()
        return self.root

    def test_deserialise(self):
        serilaised_xml = """<crux-vooodoo>
  <simpleleaf old_value="9998">9999</simpleleaf>
  <morecomplex>
    <leaf2>a</leaf2>
  </morecomplex>
  <simplelist>
    <simplekey listkey="yes">firstkey</simplekey>
  </simplelist>
  <hyphen-leaf>abc123</hyphen-leaf>
  <outsidelist>
    <leafo listkey="yes">a</leafo>
    <insidelist>
      <leafi listkey="yes">A</leafi>
    </insidelist>
  </outsidelist>
  <outsidelist>
    <leafo listkey="yes">b</leafo>
  </outsidelist>
</crux-vooodoo>"""

        root = self._get_session()
        (keystore_cache, schema_cache) = self.subject._cache

        root.simpleleaf = 'value_before_loading_serialised_data'
        self.assertEqual(root.simpleleaf, 'value_before_loading_serialised_data')
        self.assertEqual(list(keystore_cache.items.keys()), ['//simpleleaf'])

        self.subject.loads(serilaised_xml)
        self.assertEqual(list(keystore_cache.items.keys()), [])

        self.assertEqual(root.simpleleaf, '9999')
        self.assertEqual(root.hyphen_leaf, 'abc123')

#        self.assertEqual(list(keystore_cache.items.keys()), ['/simpleleaf', '/hyphen_leaf'])

    def test_advanced_list_with_dump(self):
        # note quite test driven but want to go to bed!

        # list create()
        # list create() without enough keys
        # list create() with too many keys
        # list create() then trying to change the key (not allowed)
        # list Create() and then modifying non keys (allows)
        # creating multiple list entries (different keys) shoudl be allowed
        # actually get lists working
        #
        # session.dumps() after first list item create
        # Out[1]: '<crux-vooodoo>\n  <simpleleaf>Hello World!</simpleleaf>\n  <simplelist>\n    <simplekey>firstkey</simplekey>\n  </simplelist>\n</crux-vooodoo>\n'
        # GOOD
        #
        # session.dumps() after l.create('nextlistelement')
        # Out[5]: '<crux-vooodoo>\n  <simpleleaf>Hello World!</simpleleaf>\n  <simplelist>\n    <simplekey old_value="firstkey">nextlistelement</simplekey>\n  </simplelist>\n</crux-vooodoo>\n'
        # WRONG!!!!
        # But it is nice to see the 'old_value' attribute come in place :-)
        #
        #

        # Act
        root = self._get_session()
        listelement = root.simplelist.create('Shamanaid')
        listelement.nonleafkey = 'sdf'
        # Check the same list element can have the create method called a second name
        listelement = root.simplelist.create('Shamanaid')

        with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
            listelement.simplekey = 'change the value'
        self.assertEqual(str(context.exception), "Changing a list key is not supported. /simplelist[simplekey='Shamanaid']/simplekey")

        received_xml = self.subject.dumps()

        # Assert
        expected_xml = """<crux-vooodoo>
  <simplelist>
    <simplekey listkey="yes">Shamanaid</simplekey>
    <nonleafkey>sdf</nonleafkey>
  </simplelist>
</crux-vooodoo>
"""
        self.assertEqual(expected_xml, received_xml)

        listelement2 = root.simplelist.create('Prophet')
        listelement2.nonleafkey = 'master'
        received_xml = self.subject.dumps()

        # Assert
        expected_xml = """<crux-vooodoo>
  <simplelist>
    <simplekey listkey="yes">Shamanaid</simplekey>
    <nonleafkey>sdf</nonleafkey>
  </simplelist>
  <simplelist>
    <simplekey listkey="yes">Prophet</simplekey>
    <nonleafkey>master</nonleafkey>
  </simplelist>
</crux-vooodoo>
"""
        self.assertEqual(expected_xml, received_xml)

    def test_basic_xmldumps(self):
        root = self._get_session()

        # Act
        root.morecomplex.leaf2 = "sing-and-dance-or-youll"
        leaf2_value = root.morecomplex.leaf2
        root.hyphen_leaf = 'underscore_in_voodoo-should-be-hyphens-in-xmldoc'
        hyphen_leaf_value = root.hyphen_leaf

        received_xml = self.subject.dumps()

        # Assert
        self.assertEqual("sing-and-dance-or-youll", leaf2_value)
        self.assertEqual("underscore_in_voodoo-should-be-hyphens-in-xmldoc", hyphen_leaf_value)
        expected_xml = """<crux-vooodoo>
  <morecomplex>
    <leaf2>sing-and-dance-or-youll</leaf2>
  </morecomplex>
  <hyphen-leaf>underscore_in_voodoo-should-be-hyphens-in-xmldoc</hyphen-leaf>
</crux-vooodoo>
"""
        self.assertEqual(expected_xml, received_xml)

    def test_basic_list(self):
        root = self._get_session()

        listelement = root.simplelist.create('Shamanaid')
        self.assertEqual(repr(listelement), "VoodooListElement: /simplelist[simplekey='Shamanaid']")

        expected_hits = ['nonleafkey', 'simplekey']
        self.assertEqual(dir(listelement), expected_hits)

    def test_basic_dir(self):
        root = self._get_session()

        expected_hits = ['inner', 'leaf2', 'leaf3', 'leaf4', 'nonconfig']
        self.assertEqual(dir(root.morecomplex), expected_hits)

    def test_basic_repr(self):
        root = self._get_session()

        node = root.morecomplex
        self.assertEqual(repr(node), "VoodooContainer: /morecomplex")
        self.assertEqual(repr(node.inner), "VoodooContainer: /morecomplex/inner")

        node = root.morecomplex.leaf2
        node = "x123"
        self.assertEqual(repr(node), "'x123'")

    def test_basic_session_leaf(self):
        root = self._get_session()

        value = root.simpleleaf
        self.assertEqual(value, None)

        root.simpleleaf = 'ABC123'
        value = root.simpleleaf
        self.assertEqual(value, 'ABC123')

    def test_basic_session_setup(self):
        self._get_session()

        self.assertEqual(repr(self.root), "VoodooRoot")
