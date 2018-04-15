import unittest

from PyConfHoardCommon import PyConfHoardCommon


class TestYang(unittest.TestCase):

    def setUp(self):
        self.subject = PyConfHoardCommon()
        self.subject.load_blank_schema('test/schema.json')

    def test_list_config_nodes_from_root(self):
        result = self.subject.list('')
        self.assertEqual(result, ['simplecontainer', 'level1'])

    def test_get_config_nodes_from_root(self):
        result = self.subject.get('')
        self.assertTrue('simplecontainer' in result)
        self.assertTrue('level1' in result)


    def test_get_depper_from_root(self):
        result = self.subject.get('level1 level2')
        self.assertTrue('level3' in result)
        self.assertTrue('mixed' in result['level3'])

    def test_filtering_of_config_nodes_in_a_list(self):
        result = self.subject.list('level1 level2 level3')
        self.assertEqual(result, ['withcfg', 'mixed'])

    def test_filtering_of_non_config_nodes_in_a_list(self):
        result = self.subject.list('level1 level2 level3', config=False)
        self.assertEqual(result, ['withoutcfg', 'mixed'])

    
