#!/usr/bin/env python3
import copy
import json
import logging
import sys
import json
import os
import re
import warnings
import dpath.util
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf, PyConfHoardNonConfigList, PyConfHoardNotAList, PyConfHoardWrongKeys, PyConfHoardDataNoLongerRequired, PyConfHoardInvalidUse, PyConfHoardUnhandledUse
 
class PyConfHoardDatastore:

    """
    The Datastore provides the ability to manipulate data (either config or operational) according to a defined schema.
    
    A template scehma is loaded into the schema however this can be augmented as list items are added.
    When persisting the data we save in a flat keyval store, when we restore data we go through a process of augmenting
    the data.
    When data is shared to consumers who are only interested in a read-only view it may be shared in a json/tree
    based structure.

    - keyval = keyvalue pairs of data which we will persist
    - db     = livedata - needs to be rebuilt everytime a datastore comes to life.
    - schema = the schema - augmented when list elements are created.
    """

    LOG_LEVEL = 3

    def __init__(self):
        self.db = {}
        self.keyval = {}
        self.schema = {}

        self.schema_by_path = {}
        logging.TRACE = 7

        def custom_level_trace(self, message, *args, **kws):
            if self.isEnabledFor(logging.TRACE):
                self._log(logging.TRACE, message, args, **kws)
        logging.Logger.trace = custom_level_trace
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.addLevelName(logging.TRACE, "TRACE")
        logging.basicConfig(level=self.LOG_LEVEL, format=FORMAT)
        self.log = logging.getLogger('DatastoreBackend')
#        self.log.debug('Filter Instance Started %s', self)

    def load_blank_schema(self, json_file):
        schema_file = open(json_file)
        self.schema = json.loads(schema_file.read())
        schema_file.close()

    def load_from_keyvals(self, keyval_file):
        """
        Given a file containing key/value data we will load this in and validate
        it against the schema as we progress through building the db
        """
        keyval_file = open(keyval_file)
        keyvals = json.loads(keyval_file.read())
        keyval_file.close()

        for keyval in keyvals:
            self._merge_keyval(keyval, keyvals[keyval])

    def _merge_keyval(self, key, val):
        self.log.trace('%s <- %s', key, val)
   
        regex = re.compile( "{([A-Za-z0-9]*)}\/?" )
        updated_key = regex.sub('/__listelement', key)
        if not updated_key[0:5] == '/root':
            updated_key = '/root' + updated_key

        if updated_key not in self.schema_by_path:
            try:
                schema = dpath.util.get(self.schema, updated_key)
                self.schema_by_path[updated_key] = self.schema
            except KeyError:
                raise PyConfHoardDataNoLongerRequired(updated_key)
        else:
            schema = self.schema_by_path[updated_key]

        self.validate_against_schema(schema, val)

        ### TODO: if we pass the schema we have to add into self.db
        ### First cover off the simple case without lists, although 
        ### what we have done so far won't have made it harder.
        dpath.util.new(self.db, updated_key, val)
        self.keyval[key] = val

    def validate_against_schema(self, schema, val):
        """
        This method takes in the specific part of the schema as a
        dictionary and a value and will validate and provide a boolean
        response back.
        """
        if '__schema' not in schema:
            raise PyConfHoardInvalidUse('validate_against_schema not passed a valid schema definition')
        if '__type' not in schema['__schema']:
            raise PyConfHoardInvalidUse('validate_against_schema not passed a valid schema definition')
        
        if schema['__schema']['__type'] == 'string':
            return True

        raise PyConfHoardUnhandledUse("validate only implemented for strings")

    def set_from_string(self, full_string, command=''):
        """
        A convenience function to split apart the path, command and value
        and then call the set function.
        """
        # path = self.decode_path_string(full_string[len(command):], ignore_last_n=1)
        value = self.decode_path_string(full_string[len(command):], get_index=-1)
        path = full_string[:-len(value)-1]
        self.set(path, value)

    def _merge_direct_to_root(self, payload):
        """
        Merge a payload direct to the root of the database.

        I think this will be extended to update the schema to deal with auto-complete
        of list nodes. When the CLI/things merge in existing data they call this method.
        """

        dpath.util.merge(self.db, payload)

    def decode_path_string(self, path, separator=' ', ignore_last_n=0, get_index=None):
        """
        This method should always be used to provide safe paths for dpath to work with.
        In particular this will add a fake 'root' element at the begining of the list
        as dpath functions don't like an empty glob.

        TODO: in future we should look to intelligently seprate on spaces
        i.e. level1 level2 level3 cfgonly "this is a value" should result in a path
        path = ['level1', 'level2', 'level3', 'cfgonly']
        value = 'this is a value'
        """
        if not isinstance(path, list):
            if not path[0:5] == separator + 'root':
                path = separator + 'root' + separator + path
            separated = path.split(separator)
        else:
            if not path[0] == 'root':
                path.insert(0, 'root')
            separated = path

        seplen = len(separated)
        # Remove anything which is a null string
        for i in range(seplen):
            if separated[seplen-i-1] == '':
                separated.pop(seplen-i-1)

        for i in range(ignore_last_n):
            try:
                separated.pop()
            except:
                pass

        if isinstance(get_index, int):
            return separated[get_index]

        return separated

    def list(self, path_string, separator=' '):
        """
        Shows structure of the databas
        """
        path = self.decode_path_string(path_string, separator)
        return PyConfHoardDatastore._fetch_keys_from_path(self.schema, path)

    def get_type(self, path_string, separator=' '):
        """
        Return the type of a particular leaf from the model.
        """
        self.log.trace('%s ?type', path_string)
        regex = re.compile( "{([A-Za-z0-9]*)}\/?" )
        print ('>>>>>', path_string)
        path_string = regex.sub('/__listelement/', path_string)
        self.log.trace('%s', path_string)
        path = self.decode_path_string(path_string, separator)
        schema = dpath.util.get(self.schema, path)

        if '__listelement' in schema:
            return schema['__listelement']['__schema']
        elif '__schema' in schema:
            return schema['__schema']
        else:
            raise PyConfHoardAccessNonLeaf(path)

    def get(self, path_string, separator=' '):
        """
        Get the value of a node from either the config or oper 
        datastores.
        """
        node_type = self.get_type(path_string, separator)
        path = self.decode_path_string(path_string, separator)
        try:
            return dpath.util.get(self.db, path)
        except KeyError:
            pass

        return None

    def set(self, path_string, set_val, separator=' '):
        """Set the value of a leaf node"""
        self.log.trace('%s -> %s', path_string, set_val)
        node_type = self.get_type(path_string, separator)
        regex = re.compile( "{([A-Za-z0-9]*)}\/?" )
        path_string = regex.sub('/{\g<1>}/', path_string)
        path = self.decode_path_string(path_string, separator)

        self.keyval[path_string] = set_val
        dpath.util.new(self.db, path, set_val)

    def create(self, path_string, list_key, separator=' '):
        """
        Create a list-item
        list keys should be a list of separated keys
        """
        node_type = self.get_type(path_string, separator)
        if '__list' not in node_type or node_type['__list'] is False:
            raise PyConfHoardNotAList(path)
        self._add_to_list(self.db, node_type, path_string, list_key, separator)

    def _add_to_list(self, db, node_type, path_string, list_keys, separator=' '):
        path = self.decode_path_string(path_string, separator)
        list_element = dpath.util.get(self.schema, path)
        if not len(list_keys) == len(list_element['__listelement']['__schema']['__keys']):
            raise PyConfHoardWrongKeys(path, list_element['__listelement']['__schema']['__keys'])
        
        string_composite_key = '{'
        lk = 0
        for list_key in list_element['__listelement']['__schema']['__keys']:
            string_composite_key = string_composite_key + list_keys[lk] + ' '
            lk = lk + 1
        string_composite_key = string_composite_key[:-1] + '}'

        path.append(string_composite_key)
        lk = 0
        for list_key in list_element['__listelement']['__schema']['__keys']:
            path.append(list_key)
            self.keyval[path_string + '/'+ list_key] = list_keys[lk]
            dpath.util.new(db, path, list_keys[lk])
            path.pop()
            lk = lk + 1

    def dump(self, remove_root=False):
        """
        Dump will take the data from the datastore and provide a json
        representation.

        This will never be re-imported from this format, but instead 
        the key-value data will be used to restructure this.
        """
        if remove_root:
            if 'root' in self.db:
                return json.dumps(self.db['root'], indent=4, sort_keys=True)
            else:
                return '{}'
        return json.dumps(self.db, indent=4, sort_keys=True)

    def persist(self):
        return self.keyval

    def get_fragment(self, path_string, separator=' '):
        db = self.db
        path = self.decode_path_string(path_string, separator)
        fragment = dpath.util.get(db, path)
        return json.dumps(fragment, indent=4, sort_keys=True)

    @staticmethod
    def _fetch_keys_from_path(obj, path):
        result = []
        for key in dpath.util.get(obj, path).keys():
            if key == '__listelement':
                path.append('__listelement')
                return PyConfHoardDatastore._fetch_keys_from_path(obj, path)
            elif key == '__schema':
                pass
            else:
                result.append(key)
        return sorted(result)

    @staticmethod
    def _convert_path_to_slash_string(path):
        if isinstance(path, list):
            path_string = ''
            for x in path:
                path_string = path_string + '/' + x
            return path_string
        return path_string.replace(' ', '/')
