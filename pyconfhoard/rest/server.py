import falcon
import sys
import os

sys.path.append('pyconfhoard')
sys.path.append('pyconfhoard/rest')

import datastore
import discover
api = application = falcon.API()

datastore_file_path = 'datastore'
if 'DATASTORE:' in sys.argv[-1]:
    datastore_file_path = sys.argv[-1].split(':')[1]

datastore_handler = datastore.Resource()
datastore_handler.DATASTORE = datastore_file_path
discover_handler = discover.Resource()
discover_handler.DATASTORE = datastore_file_path

api.add_route('/v1/datastore/{datastore}/{path}', datastore_handler)
api.add_route('/v1/discover', discover_handler)
