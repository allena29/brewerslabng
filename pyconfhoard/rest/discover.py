import json
import falcon
import os

class Resource(object):

    def on_get(self, req, resp):
        req.get_header('TOKEN')

        datastores ={}
        base = 'datastore/registered'
        for item in os.listdir(base):
            if item[-4:] == '.pch':
                o = open('datastore/registered/%s' % (item))
                metadata = json.loads(o.read())
                o.close()
                datastores[item[:-4]] = metadata

        yin = open('yang/schema.json')    
        schema = json.loads(yin.read())
        yin.close()
        resp.body = json.dumps({'datastores': datastores, 'schema': schema})
        resp.status = falcon.HTTP_200

