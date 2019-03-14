
import os
import sys
import unittest
from mock import Mock
sys.path.append('../../')
from blng.Witch import Witch
from blng.Voodoo import DataAccess


class TestVoodoo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 400000

    def test_simple_comparsion_wihtout_lists(self):
        old_session = DataAccess('crux-example.xml')
        session = DataAccess('crux-example.xml')

        old_root = old_session.get_root()
        old_root.morecomplex.leaf3 = 'sfd'
        old_root.simpleenum = '235'
        root = session.get_root()
        root.simpleleaf = 'abc'
        root.bronze.silver
        root.bronze.silver.gold.platinum.deep = 'down'
        root.simpleenum = '234'
        root.bronze.silver.gold
        root.simpleenum = '234'
        root.simpleenum = '234'

        w = Witch(root, old_root)

        result = ''
        for line in w.show():
            result = result + line + '\n'

        expected_result = """--- CONFIGURATION START ---
+ simpleleaf abc;
+ bronze:
+   silver:
+     gold:
+       platinum:
+         deep down;
- simpleenum 235;
+ simpleenum 234;
- morecomplex:
-   leaf3 sfd:
--- CONFIGURATION END ---
"""
        self.assertEqual(result, expected_result)
