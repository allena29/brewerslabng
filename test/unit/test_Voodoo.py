
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

    def test_deserialise_and_serilaise_example_with_cache_checks(self):
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
        self.assertEqual(root.morecomplex.leaf2, 'a')

        self.assertEqual(root.simpleleaf, '9999')
        self.assertEqual(root.hyphen_leaf, 'abc123')
        self.assertEqual(list(keystore_cache.items.keys()), ['//morecomplex', '//morecomplex/leaf2', '//simpleleaf',  '//hyphen_leaf'])

        root.simpleleaf = "value_after_deserialised_and_modified"

        re_serilaised_xml = """<crux-vooodoo><simpleleaf old_value="9999">value_after_deserialised_and_modified</simpleleaf>
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
</crux-vooodoo>
"""

        self.assertEqual(self.subject.dumps(), re_serilaised_xml)

    def test_deserialise_and_serilaise(self):
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
        self.subject.loads(serilaised_xml)
        root.simpleleaf = "value_after_deserialised_and_modified"

        re_serilaised_xml = """<crux-vooodoo><simpleleaf old_value="9999">value_after_deserialised_and_modified</simpleleaf>
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
</crux-vooodoo>
"""
        # raise ValueError(self.subject.dumps())
        self.assertEqual(self.subject.dumps(), re_serilaised_xml)

    def test_list_within_list(self):
        root = self._get_session()
        a = root.simplelist.create('a')

        for c in range(2):
            root = self._get_session()

            a = root.simplelist.create('a')
            a.nonleafkey = 'b'
            b = root.simplelist.create('b')
            b.nonleafkey = 'bb'
            A = root.outsidelist.create('AA')
            B = root.outsidelist.create('BB')
            B = root.outsidelist.create('BB')
            B = root.outsidelist.create('BB')
            B.insidelist.create('bbbbbb')
            A = root.outsidelist.create('AA')
            a = A.insidelist.create('aaaaa')
            english = A.otherinsidelist.create('one', 'two', 'three')
            english.otherlist4 = 'four'
            french = A.otherinsidelist.create('un', 'deux', 'trois')
            french.otherlist4 = 'quatre'
            french.language = 'french'
            italian = B.otherinsidelist.create('uno', 'due', 'tres')
            italian.otherlist4 = 'quattro'
            italian.language = 'italian'
            spanish = B.otherinsidelist.create('uno', 'dos', 'tres')
            spanish.otherlist4 = 'cuatro'
            spanish.language = 'spanish'
            spanish = A.otherinsidelist.create('uno', 'dos', 'tres')
            spanish.otherlist4 = 'cuatro'
            spanish.language = 'spanish'
            german = B.otherinsidelist.create('eins', 'zwei', 'drei')
            with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
                swedish = B.otherinsidelist.create('et', 'två', 'tre', 'fyra')
            self.assertEqual(str(context.exception), "Wrong Number of keys require 3 got 4. keys defined: ['otherlist1', 'otherlist2', 'otherlist3']")

            with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
                danish = A.otherinsidelist.create('et', 'to')
                danish.language = 'danish'
            self.assertEqual(str(context.exception), "Wrong Number of keys require 3 got 2. keys defined: ['otherlist1', 'otherlist2', 'otherlist3']")

            dutch_part1 = A.otherinsidelist.create('een', 'twee', 'drie')
            dutch_part1.otherlist4 = 'vier'
            dutch_part1.language = 'dutch'
            dutch_part2 = B.otherinsidelist.create('een', 'twee', 'drie')
            dutch_part2.otherlist5 = 'vijf'
            dutch_part2.language = 'dutch'

        expected_xml = """<crux-vooodoo>
  <simplelist>
    <simplekey listkey="yes">a</simplekey>
    <nonleafkey>b</nonleafkey>
  </simplelist>
  <simplelist>
    <simplekey listkey="yes">b</simplekey>
    <nonleafkey>bb</nonleafkey>
  </simplelist>
  <outsidelist>
    <leafo listkey="yes">AA</leafo>
    <insidelist>
      <leafi listkey="yes">aaaaa</leafi>
    </insidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">one</otherlist1>
      <otherlist2 listkey="yes">two</otherlist2>
      <otherlist3 listkey="yes">three</otherlist3>
      <otherlist4>four</otherlist4>
    </otherinsidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">un</otherlist1>
      <otherlist2 listkey="yes">deux</otherlist2>
      <otherlist3 listkey="yes">trois</otherlist3>
      <otherlist4>quatre</otherlist4>
      <language>french</language>
    </otherinsidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">uno</otherlist1>
      <otherlist2 listkey="yes">dos</otherlist2>
      <otherlist3 listkey="yes">tres</otherlist3>
      <otherlist4>cuatro</otherlist4>
      <language>spanish</language>
    </otherinsidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">een</otherlist1>
      <otherlist2 listkey="yes">twee</otherlist2>
      <otherlist3 listkey="yes">drie</otherlist3>
      <otherlist4>vier</otherlist4>
      <language>dutch</language>
    </otherinsidelist>
  </outsidelist>
  <outsidelist>
    <leafo listkey="yes">BB</leafo>
    <insidelist>
      <leafi listkey="yes">bbbbbb</leafi>
    </insidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">uno</otherlist1>
      <otherlist2 listkey="yes">due</otherlist2>
      <otherlist3 listkey="yes">tres</otherlist3>
      <otherlist4>quattro</otherlist4>
      <language>italian</language>
    </otherinsidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">uno</otherlist1>
      <otherlist2 listkey="yes">dos</otherlist2>
      <otherlist3 listkey="yes">tres</otherlist3>
      <otherlist4>cuatro</otherlist4>
      <language>spanish</language>
    </otherinsidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">eins</otherlist1>
      <otherlist2 listkey="yes">zwei</otherlist2>
      <otherlist3 listkey="yes">drei</otherlist3>
    </otherinsidelist>
    <otherinsidelist>
      <otherlist1 listkey="yes">een</otherlist1>
      <otherlist2 listkey="yes">twee</otherlist2>
      <otherlist3 listkey="yes">drie</otherlist3>
      <otherlist5>vijf</otherlist5>
      <language>dutch</language>
    </otherinsidelist>
  </outsidelist>
</crux-vooodoo>
"""
        self.assertEqual(self.subject.dumps(), expected_xml)

    def test_list_with_dump(self):
        # note quite test driven but want to go to bed!

        # list create()
        # list create() without enough keys
        # list create() with too many keys
        # list create() then trying to change the key (not allowed)
        # list Create() and then modifying non keys (allows)
        # creating multiple list entries (different keys) shoudl be allowed
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
