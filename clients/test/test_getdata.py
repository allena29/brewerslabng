import unittest
import os
import datalayer
import subprocess
import sysrepo as sr

print()

process = subprocess.Popen(["bash"],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
(out, err) = process.communicate('sysrepocfg --import=../init-data/integrationtest.xml --format=xml --datastore=running integrationtest'.encode('UTF-8'))
if err:
    raise ValueError('Unable to import data\n%s\n%s' % (our, err))


class test_getdata(unittest.TestCase):

    def setUp(self):
        self.subject = datalayer.DataAccess()
        self.subject.connect()

    def test_get_leaf(self):
        xpath = "/integrationtest:morecomplex/inner/leaf5"
        self.assertEqual(self.subject.get(xpath), 'Inside')

    def test_set_leaves(self):
        """
        This tests setting leaves with and without commits.

        We can see commits don't persist to startup config.
        """
        xpath = "/integrationtest:morecomplex/inner/leaf5"
        value = "Outside"
        self.subject.set(xpath, value)
        self.assertEqual(self.subject.get(xpath), 'Outside')

        self.subject = datalayer.DataAccess()
        self.subject.connect()

        xpath = "/integrationtest:morecomplex/inner/leaf5"
        self.assertNotEqual(self.subject.get(xpath), 'Outside')

        xpath = "/integrationtest:morecomplex/inner/leaf5"
        value = "Outside"
        self.subject.set(xpath, value)
        self.assertEqual(self.subject.get(xpath), 'Outside')
        self.subject.commit()

        self.subject = datalayer.DataAccess()
        self.subject.connect()

        xpath = "/integrationtest:morecomplex/inner/leaf5"
        self.assertEqual(self.subject.get(xpath), 'Outside')

        xpath = "/integrationtest:morecomplex/inner/leaf5"
        value = "Inside"
        self.subject.set(xpath, value)
        self.subject.commit()

    def test_set_leaves_multiple_transactions(self):
        """
        This tests setting values- here we can see sysrepo doesn't block a commit
        when the data changes.

        We can see commits don't persist to startup config.

        Importantly though, we can see that after subject1 has changed the value from
        Inside to Outside subject2 on it's following get picks up the new value
        instead of what it was when it created the value.
        """
        xpath = "/integrationtest:morecomplex/inner/leaf5"
        value = "Outside"

        self.subject1 = datalayer.DataAccess()
        self.subject1.connect('a')
        self.subject2 = datalayer.DataAccess()
        self.subject2.connect('b')

        self.subject1.set(xpath, value)
        self.assertEqual(self.subject1.get(xpath), 'Outside')
        self.subject1.commit()
        self.assertEqual(self.subject2.get(xpath), 'Outside')

        value = 'Middle'
        self.subject2.set(xpath, value)
        self.subject2.commit()
        self.assertEqual(self.subject2.get(xpath), 'Middle')

    def test_leafref(self):
        xpath = "/integrationtest:thing-that-is-leafref"
        valid_value = 'GHI'
        self.subject.set(xpath, valid_value)
        self.subject.commit()

        xpath = "/integrationtest:thing-that-is-leafref"
        invalid_value = 'ZZZ'
        self.subject.set(xpath, invalid_value)

        with self.assertRaises(RuntimeError) as context:
            self.subject.commit()

        self.subject = datalayer.DataAccess()
        self.subject.connect()

        xpath = "/integrationtest:thing-that-is-a-list-based-leafref"
        valid_value = 'I'
        self.subject.set(xpath, valid_value)
        self.subject.commit()

        valid_value = 'W'
        self.subject.set(xpath, valid_value)
        self.subject.commit()
