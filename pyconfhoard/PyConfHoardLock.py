import json
import dpath.util
import os
import PyConfHoardExceptions


class PyConfHoardLock:

    """
    This class allows us to provide locking of datastores and manage
    giving up the lock if the consumer has a problem.

    This class is largely tested by the REST folder.
    """

    def __init__(self, base, datastore, path):
        self.base = base
        self.datastore = datastore
        self.path = path

    def __enter__(self):
        if os.path.exists('%s/%s/%s.lock' % (self.base, self.datastore, self.path)):
            raise PyConfHoardExceptions.DataStoreLock(message='Failed to obtain lock - datastore %s/%s is already locked' %
                                                      (self.datastore, self.path), errors=None)

        o = open('%s/%s/%s.lock' % (self.base, self.datastore, self.path), 'w')
        o.close()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists('%s/%s/%s.lock' % (self.base, self.datastore, self.path)):

            os.unlink('%s/%s/%s.lock' % (self.base, self.datastore, self.path))

    def patch(self, obj):
        print ('lock.patch.%s/%s/%s' %(self.base, self.datastore, self.path))
        if not os.path.exists('%s/%s/%s.pch' % (self.base, self.datastore, self.path)):
            parent_obj = {}
        else:
            pch = open('%s/%s/%s.pch' % (self.base, self.datastore, self.path))
            parent_obj = json.loads(pch.read())
            pch.close()

        dpath.util.merge(parent_obj, obj)
        print('inside of lock we have parent: %s' % (parent_obj))
        print('inside of lock we have obj: %s' %(obj))
        print('copying to requested datatsore whcih was %s' %(self.datastore))

        new_pch = open('%s/%s/%s.pch' % (self.base, self.datastore, self.path), 'w')
        new_pch.write(json.dumps(parent_obj, indent=4))
        new_pch.close()

        if self.datastore == 'running':
            print('copying over to persit')
            new_pch = open('%s/%s/%s.pch' % (self.base, 'persist', self.path), 'w')
            new_pch.write(json.dumps(parent_obj, indent=4))
            new_pch.close()

        return json.dumps(parent_obj, indent=4, sort_keys=True)
