import unittest
import os
import datalayer
import subprocess
import sysrepo as sr


process = subprocess.Popen(["bash"],
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
(out, err) = process.communicate('sysrepocfg --import=../init-data/integrationtest.xml --format=xml --datastore=running integrationtest'.encode('UTF-8'))
if err:
    raise ValueError('Unable to import data\n%s\n%s' % (our, err))


class test_node_based_access(unittest.TestCase):

    def setUp(self):
        self.subject = datalayer.DataAccess()
        self.subject.connect()
        self.root = self.subject.get_root('integrationtest')

    def test_root(self):
        self.assertEqual(repr(self.root), 'BlackArtRoot{}')

        expected_children = ['bronze', 'container-and-lists', 'default', 'dirty-secret', 'empty', 'hyphen-leaf', 'imports-in-here', 'list-to-leafref-against', 'lista', 'morecomplex', 'outsidelist', 'patternstr', 'psychedelia', 'quad', 'quarter', 'resolver', 'simplecontainer', 'simpleenum',
                             'simpleleaf', 'simplelist', 'thing-that-is-a-list-based-leafref', 'thing-that-is-leafref', 'thing-that-is-lit-up-for-A', 'thing-that-is-lit-up-for-B', 'thing-that-is-lit-up-for-C', 'thing-that-is-used-for-when', 'thing-to-leafref-against', 'twokeylist', 'whencontainer']
        self.assertEqual(dir(self.root), expected_children)

    def test_simplest_leaf(self):
        self.assertEqual(self.root.simpleleaf, 'duke')

        self.root.simpleleaf = 'spirit'
        self.assertEqual(self.root.simpleleaf, 'spirit')

        self.root.simpleleaf = None
        # TODO: assert here that the leaf is not persisted in the sysrepo data.
        # (The data access here will give us None if something doesn't exist, but
        # it would also give us None if we have no lookup stuff)
        # Ideally we would have the data access into sysrepo completely mocked.
        self.assertEqual(self.root.simpleleaf, None)

        self.subject.commit()

    def test_containers(self):
        morecomplex = self.root.morecomplex
        self.assertEqual(repr(morecomplex), "BlackArtContainer{/integrationtest:morecomplex}")

        expected_children = ['extraboolean', 'extraboolean2', 'extraboolean3', 'inner', 'leaf2', 'leaf3', 'leaf4', 'nonconfig']
        self.assertEqual(dir(morecomplex), expected_children)

        self.assertEqual(morecomplex.leaf3, 12345)
        self.assertEqual(morecomplex.inner.leaf7, 'this-is-a-default')

        inner = morecomplex.inner
        self.assertEqual(repr(inner), 'BlackArtPresenceContainer{/integrationtest:morecomplex/integrationtest:inner} Exists')
        inner.leaf7 = 'this-is-not-a-default-now'
        self.assertEqual(morecomplex.inner.leaf7, 'this-is-not-a-default-now')
        self.assertTrue(morecomplex.inner.exists())

        simplecontainer = self.root.simplecontainer
        self.assertEqual(repr(simplecontainer), "BlackArtPresenceContainer{/integrationtest:simplecontainer} Does Not Exist")
        self.assertFalse(simplecontainer.exists())

        simplecontainer.create()
        self.assertTrue(simplecontainer.exists())
