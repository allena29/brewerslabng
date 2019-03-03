import os
import json
from flask_restplus import Namespace, Resource, fields, reqparse

api = Namespace('temperatures', description='Hot and Cold Temperature Sutff')


@api.route('/')
class Temps(Resource):
    @api.doc('dig_temperatures')
    def get(self):
        '''List of probes that monitor temperature'''
        return {}


@api.route('/withid/<id>')
class Temps(Resource):
    @api.doc('dig_temperatures')
    def get(self, id):
        '''List of probes that monitor temperature'''
        return {'this_is_the_id': id}


example3_parser = reqparse.RequestParser()
example3_parser.add_argument('q', choices=('one', 'two'), location='path')


@api.route('/with-query-string')
class Temps(Resource):
    @api.expect(example3_parser)
    def get(self):
        """List images"""
        example3_parser = reqparse.RequestParser()
        example3_parser.add_argument('q')
        args = example3_parser.parse_args()
        query_string_value = args.get('q')
        return {'query_string_value': city_value}


example4_fields = api.model('MyModel', {
    'name': fields.String,
    'age': fields.Integer(min=0)
})

# GET does not support fields.


@api.route('/with-fields')
class Temps(Resource):
    @api.expect(example4_fields)
    def post(self):
        """
        Documentation for the method
        goes here
        """
        payload = api.payload
        return {'name': payload['name'], 'age': str(payload['age'])}
