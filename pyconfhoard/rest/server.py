import falcon
import sys
import os

sys.path.append('pyconfhoard')
sys.path.append('pyconfhoard/rest')

import datastore
import discover
api = application = falcon.API()


datastore_handler = datastore.Resource()
discover_handler = discover.Resource()

api.add_route('/v1/datastore/{datastore}/{path}', datastore_handler)
api.add_route('/v1/discover', discover_handler)
