from flask_restplus import Api

from .temperatures import api as ns_temperatures

api = Api(
    title='Brewerslab stuff via Rest API',
    version='0.0.0.0.0',
    description='A very quick and dirty experiment'
    # All API metadatas
)

api.add_namespace(ns_temperatures, path='/brewerslabng/v1')
