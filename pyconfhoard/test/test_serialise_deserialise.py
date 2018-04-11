import unittest

from binding import tester
from Villain import Goblin


class TestYang(unittest.TestCase):

    def setUp(self):
        self.subject = Goblin('testAppName', 'tester', '', False)

    def test_build_yang_simple_list(self):
       # Build
        yang = self.subject._yang_obj
        """
        module: tester
          +--rw list1* [key1]
             +--rw key1      string
             +--rw nonkey?   string
         """

        item1 = yang.list1.add('abc123')
        item2 = yang.list1.add('xyz987')
        item3 = yang.list1.add('ooo000')

        # Assert
        self.assertEqual(len(self.subject.get_config("/list1")), 3)

        fetched_item1 = self.subject.get_config("/list1[key1='xyz987']")[0]
        self.assertEqual(fetched_item1.key1, "xyz987")
        self.assertEqual(fetched_item1.nonkey, "")
        item2.nonkey = 'now_this_value_has_been_set'
        self.assertEqual(fetched_item1.nonkey, item2.nonkey)

        # Fetching a non-existing key has to return an error
        try:
            fetched_item1 = self.subject.get_config("/list1[key1='non-existant-key']")[0]
            self.fail('fetching key should give index error')
        except IndexError:
            pass

        # Even if the key name looks similair to something we already have
        try:
            fetched_item1 = self.subject.get_config("/list1[key1='abc12']")[0]
            self.fail('fetching key should give index error')
        except IndexError:
            pass

        # Adding a duplicate list entry should give a key error
        try:
            yang.list1.add('abc123')
            self.fail('adding duplicate should give a key error')
        except KeyError:
            pass

        # Basic check on the serialisation
        serialised = self.subject.dumper(yang)
        expected_serialised = """{"__namespace": "tester", "list1": [{"nonkey": "", "key1": "abc123"}, {"nonkey": "now_this_value_has_been_set", "key1": "xyz987"}, {"nonkey": "", "key1": "ooo000"}]}"""
        self.assertEqual(serialised, expected_serialised)

        # After deleting an entry the serialised answer must differ
        yang.list1.delete('xyz987')
        self.assertNotEqual(self.subject.dumper(yang), expected_serialised)

        # We should be able to load the json payload back in (with a little adjustment
        # to give a key 'from-load'
        self.subject.loader(yang, expected_serialised.replace('ooo000', 'from-load'))
        fetched_item1 = self.subject.get_config("/list1[key1='from-load']")[0]

        # Dump only opdata
        serialised = self.subject.dumper(yang, opdata=True)
        expected_serialised = """{"__namespace": "tester", "list1": [{"key1": "abc123", "stats": {"heartrate": 0}}, {"key1": "ooo000", "stats": {"heartrate": 0}}, {"key1": "xyz987", "stats": {"heartrate": 0}}, {"key1": "from-load", "stats": {"heartrate": 0}}]}"""
        self.assertEqual(serialised, expected_serialised)
