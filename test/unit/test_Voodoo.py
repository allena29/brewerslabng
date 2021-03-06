
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

    def test_list_delete_element(self):
        # BUild
        root = self._get_session()

        one = root.twokeylist.create('a1', 'b1')
        two = root.twokeylist.create('a2', 'b2')
        three = root.twokeylist.create('a3', 'b3')

        self.assertTrue(('a1', 'b1') in root.twokeylist)
        self.assertTrue(('x1', 'b1') not in root.twokeylist)

        ELEPHANT = root.simplelist.create('elephant')
        CAMEL = root.simplelist.create('camel')
        ZOMBIE = root.simplelist.create('zombie')
        GHOUL = root.simplelist.create('ghoul')

        self.assertEqual(len(root.simplelist), 4)
        self.assertTrue('zombie' in root.simplelist)
        self.assertFalse('zombie' not in root.simplelist)
        self.assertEqual(['elephant', 'camel', 'zombie', 'ghoul'], root.simplelist.keys())
        self.assertEqual([['a1', 'b1'], ['a2', 'b2'], ['a3', 'b3']], root.twokeylist.keys())

        for listelement in root.twokeylist:
            listelement.tertiary = listelement.primary + listelement.secondary

        self.assertEqual(root.simplelist['zombie']._path, "/simplelist[simplekey='zombie']")
        self.assertEqual(root.simplelist['ghoul'].simplekey, "ghoul")

        # Action
        del root.simplelist['zombie']

        self.assertTrue('zombie' not in root.simplelist)
        self.assertFalse('elephant' not in root.simplelist)
        self.assertFalse('camel' not in root.simplelist)
        self.assertFalse('ghoul' not in root.simplelist)
        self.assertFalse('zombie' in root.simplelist)
        self.assertTrue('elephant' in root.simplelist)
        self.assertTrue('camel' in root.simplelist)
        self.assertTrue('ghoul' in root.simplelist)

        # Test that this does not actually remove the item from the list
        # it should delete the reference to the list element only
        listelement = root.twokeylist['a2', 'b2']
        del listelement
        self.assertEqual(root.twokeylist['a2', 'b2'].tertiary, 'a2b2')

        del root.twokeylist['a2', 'b2']
        with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
            x = root.twokeylist['a2', 'b2']
        self.assertEqual(str(context.exception), "ListElement does not exist: /twokeylist[primary='a2'][secondary='b2']")

        # Assert
        self.assertEqual(len(root.simplelist), 3)
        self.assertEqual(['elephant', 'camel', 'ghoul'], root.simplelist.keys())
        self.assertEqual([['a1', 'b1'],  ['a3', 'b3']], root.twokeylist.keys())

        expected_xml = """<voodoo>
  <twokeylist>
    <primary listkey="yes">a1</primary>
    <secondary listkey="yes">b1</secondary>
    <tertiary>a1b1</tertiary>
  </twokeylist>
  <twokeylist>
    <primary listkey="yes">a3</primary>
    <secondary listkey="yes">b3</secondary>
    <tertiary>a3b3</tertiary>
  </twokeylist>
  <simplelist>
    <simplekey listkey="yes">elephant</simplekey>
  </simplelist>
  <simplelist>
    <simplekey listkey="yes">camel</simplekey>
  </simplelist>
  <simplelist>
    <simplekey listkey="yes">ghoul</simplekey>
  </simplelist>
</voodoo>
"""

        self.assertEqual(self.subject.dumps(), expected_xml)

    def test_list_iteration(self):
        root = self._get_session()

        one = root.twokeylist.create('a1', 'b1')
        two = root.twokeylist.create('a2', 'b2')

        for listelement in root.twokeylist:
            listelement.tertiary = listelement.primary + listelement.secondary

        for listelement in root.simplelist:
            self.fail('This list was empty so we should not have iterated around it')

        # This has two list elements
        i = 0
        for listelement in root.twokeylist:
            i = i + 1
        self.assertEqual(i, 2)

        one = root.simplelist.create('1111')
        for listelement in root.simplelist:
            listelement.nonleafkey = 'first-set'
            listelement.nonleafkey = listelement.simplekey

        expected_xml = """<voodoo>
  <twokeylist>
    <primary listkey="yes">a1</primary>
    <secondary listkey="yes">b1</secondary>
    <tertiary>a1b1</tertiary>
  </twokeylist>
  <twokeylist>
    <primary listkey="yes">a2</primary>
    <secondary listkey="yes">b2</secondary>
    <tertiary>a2b2</tertiary>
  </twokeylist>
  <simplelist>
    <simplekey listkey="yes">1111</simplekey>
    <nonleafkey old_value="first-set">1111</nonleafkey>
  </simplelist>
</voodoo>
"""

        self.assertEqual(self.subject.dumps(), expected_xml)

    def test_accessing_list_elements(self):
        root = self._get_session()

        x = root.twokeylist.create('a', 'b')
        y = root.twokeylist['a', 'b']
        y.tertiary = '3'
        x = root.twokeylist.create('a', 'b')
        x = root.twokeylist.create('A', 'B')
        root.twokeylist.create('A', 'B').tertiary = 'sdf'

        self.assertEqual(y.tertiary, '3')
        expected_xml = """<voodoo>
  <twokeylist>
    <primary listkey="yes">a</primary>
    <secondary listkey="yes">b</secondary>
    <tertiary>3</tertiary>
  </twokeylist>
  <twokeylist>
    <primary listkey="yes">A</primary>
    <secondary listkey="yes">B</secondary>
    <tertiary>sdf</tertiary>
  </twokeylist>
</voodoo>
"""
        self.assertEqual(self.subject.dumps(), expected_xml)
        self.assertEqual(repr(y), "VoodooListElement: /twokeylist[primary='a'][secondary='b']")

        with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
            a = root.twokeylist['not-existing-key', 'b']
        self.assertEqual(str(context.exception), "ListElement does not exist: /twokeylist[primary='not-existing-key'][secondary='b']")

        with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
            a = root.twokeylist['a', 'non-existing-second-key']
        self.assertEqual(str(context.exception), "ListElement does not exist: /twokeylist[primary='a'][secondary='non-existing-second-key']")

    def test_deserialise_and_serilaise_example_with_cache_checks(self):
        serilaised_xml = """<voodoo>
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
</voodoo>"""

        root = self._get_session()
        (keystore_cache, schema_cache) = self.subject._cache

        root.simpleleaf = 'value_before_loading_serialised_data'
        self.assertEqual(root.simpleleaf, 'value_before_loading_serialised_data')
        self.assertEqual(list(keystore_cache.items.keys()), ['/voodoo/simpleleaf'])

        self.subject.loads(serilaised_xml)
        self.assertEqual(list(keystore_cache.items.keys()), [])
        self.assertEqual(root.morecomplex.leaf2, 'a')

        self.assertEqual(root.simpleleaf, '9999')
        self.assertEqual(root.hyphen_leaf, 'abc123')
        self.assertEqual(list(keystore_cache.items.keys()), ['/voodoo/morecomplex',
                                                             '/voodoo/morecomplex/leaf2', '/voodoo/simpleleaf',  '/voodoo/hyphen_leaf'])

        root.simpleleaf = "value_after_deserialised_and_modified"

        re_serilaised_xml = """<voodoo><simpleleaf old_value="9999">value_after_deserialised_and_modified</simpleleaf>
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
</voodoo>
"""

        self.assertEqual(self.subject.dumps(), re_serilaised_xml)

    def test_deserialise_and_serilaise(self):
        serilaised_xml = """<voodoo>
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
</voodoo>"""

        root = self._get_session()
        self.subject.loads(serilaised_xml)
        root.simpleleaf = "value_after_deserialised_and_modified"
# + is what we have extra in the test
# - is what was recevied extra in the running out
        re_serilaised_xml = """<voodoo><simpleleaf old_value="9999">value_after_deserialised_and_modified</simpleleaf>
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
</voodoo>
"""
        # raise ValueError(self.subject.dumps())
        self.assertEqual(self.subject.dumps(), re_serilaised_xml)

    def test_parents(self):
        root = self._get_session()
        root.psychedelia.psychedelic_rock.noise_pop.shoe_gaze.bands._parent._parent.bands.create('Jesus and the Mary Chain')
        root.psychedelia.psychedelic_rock.noise_pop.dream_pop.bands.create('Night Flowers')
        root.psychedelia.psychedelic_rock.noise_pop.dream_pop.bands.create('Mazzy Star')
        root.psychedelia.psychedelic_rock.noise_pop.dream_pop.bands['Mazzy Star']._parent['Night Flowers'].favourite = 'True'

        expected_xml = """<voodoo>
  <psychedelia>
    <psychedelic_rock>
      <noise_pop>
        <bands>
          <band listkey="yes">Jesus and the Mary Chain</band>
        </bands>
        <dream_pop>
          <bands>
            <band listkey="yes">Night Flowers</band>
            <favourite>True</favourite>
          </bands>
          <bands>
            <band listkey="yes">Mazzy Star</band>
          </bands>
        </dream_pop>
      </noise_pop>
    </psychedelic_rock>
  </psychedelia>
</voodoo>
"""

        self.assertEqual(self.subject.dumps(), expected_xml)
        self.assertEqual(root.psychedelia.psychedelic_rock.noise_pop.shoe_gaze._path, '/psychedelia/psychedelic_rock/noise_pop/shoe_gaze')
        self.assertEqual(root.psychedelia.psychedelic_rock.noise_pop.shoe_gaze._parent._path, '/psychedelia/psychedelic_rock/noise_pop')

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

        expected_xml = """<voodoo>
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
</voodoo>
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
        expected_xml = """<voodoo>
  <simplelist>
    <simplekey listkey="yes">Shamanaid</simplekey>
    <nonleafkey>sdf</nonleafkey>
  </simplelist>
</voodoo>
"""
        self.assertEqual(expected_xml, received_xml)

        listelement2 = root.simplelist.create('Prophet')
        listelement2.nonleafkey = 'master'
        received_xml = self.subject.dumps()

        # Assert
        expected_xml = """<voodoo>
  <simplelist>
    <simplekey listkey="yes">Shamanaid</simplekey>
    <nonleafkey>sdf</nonleafkey>
  </simplelist>
  <simplelist>
    <simplekey listkey="yes">Prophet</simplekey>
    <nonleafkey>master</nonleafkey>
  </simplelist>
</voodoo>
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
        expected_xml = """<voodoo>
  <morecomplex>
    <leaf2>sing-and-dance-or-youll</leaf2>
  </morecomplex>
  <hyphen-leaf>underscore_in_voodoo-should-be-hyphens-in-xmldoc</hyphen-leaf>
</voodoo>
"""
        self.assertEqual(expected_xml, received_xml)

    def test_basic_list(self):
        root = self._get_session()

        listelement = root.simplelist.create('Shamanaid')
        self.assertEqual(repr(listelement), "VoodooListElement: /simplelist[simplekey='Shamanaid']")

        with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
            a = root.simplelist['not-existing-key']
        self.assertEqual(str(context.exception), "ListElement does not exist: /simplelist[simplekey='not-existing-key']")

        expected_hits = ['nonleafkey', 'simplekey']
        self.assertEqual(dir(listelement), expected_hits)
        self.assertEqual(dir(root.simplelist), [])
        self.assertEqual(root.simplelist['Shamanaid'].simplekey, 'Shamanaid')
        self.assertEqual(repr(root.simplelist['Shamanaid']), "VoodooListElement: /simplelist[simplekey='Shamanaid']")

    def test_basic_dir(self):
        root = self._get_session()

        expected_hits = ['inner', 'leaf2', 'leaf3', 'leaf4', 'nonconfig']
        self.assertEqual(dir(root.morecomplex), expected_hits)

    def test_basic_repr(self):
        root = self._get_session()

        node = root.morecomplex
        self.assertEqual(repr(node), "VoodooContainer: /morecomplex")
        self.assertEqual(repr(node.inner), "VoodooPresenceContainer: /morecomplex/inner")

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

    def test_root_only_returns_root(self):
        root = self._get_session()

        with self.assertRaises(blng.Voodoo.BadVoodoo) as context:
            x = root.platinum
        self.assertEqual(str(context.exception), "Unable to find '/platinum' in the schema")
