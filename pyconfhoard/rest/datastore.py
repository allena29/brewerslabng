import json
import falcon
import os

class Resource(object):

    def on_get(self, req, resp, datastore, path):
        req.get_header('TOKEN')


        valid_datastores = ['operational', 'persist', 'running', 'default']
        if datastore not in valid_datastores:
            raise ValueError('Invalid datastore %s: select from %s' % (valid_datastores))

        base = 'datastore/' + datastore 
        db = base + '/' + path + '.pch'
        if os.path.exists(db):
            object = {'xxx'}
            o = open(db)
            resp.body = o.read()
            o.close()
        else:
            resp.body = '{}'

        resp.status = falcon.HTTP_200

