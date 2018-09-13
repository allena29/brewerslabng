import simplejson as json
import falcon
import os
import sys
from PyConfHoardLock import PyConfHoardLock


class Resource(object):

    DATASTORE = "datastore"

    def on_get(self, req, resp, datastore, path):
        req.get_header('TOKEN')

        valid_datastores = ['operational', 'persist', 'running', 'default']
        if datastore not in valid_datastores:
            raise ValueError('Invalid datastore %s: select from %s' % (valid_datastores))

        base = self.DATASTORE + '/' + datastore
        db = base + '/' + path + '.pch'
        if os.path.exists(db):
            o = open(db)
            resp.body = o.read()
            o.close()
        else:
            resp.body = '{}'

        resp.status = falcon.HTTP_200

    def on_patch(self, req, resp, datastore, path):
        if 'application/json' not in req.content_type:
            raise falcon.HTTPUnsupportedMediaType('JSON encoded payload required')

        try:
            body = req.stream.read()
            json_obj = json.loads(body)
        except Exception as err:
            raise ValueError('Unable to decode JSON body %s' % (str(err)))

        with PyConfHoardLock(self.DATASTORE, datastore, path) as lock:
            print('we have a lock...', lock)
            print('we will be patching in this ', json_obj)
            update = lock.patch(json_obj)
            print('response back', update) 
            resp.body = update
