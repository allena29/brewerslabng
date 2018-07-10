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
import decimal
from PyConfHoardCommon import decode_path_string, fetch_keys_from_path, convert_path_to_slash_string
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf, PyConfHoardNonConfigList, PyConfHoardNotAList, PyConfHoardWrongKeys, PyConfHoardDataNoLongerRequired, PyConfHoardInvalidUse, PyConfHoardUnhandledUse, PyConfHoardDataPathDoesNotExist, PyConfHoardDataInvalidValueType, PyConfHoardInvalidYangSchema


class PyConfHoardDatastore:

    """
    Ths class is intended to be used internally, see PyConfHoard for the wrapper which should be used
    by consumers of the data.

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
        self.id = ""
        self.config = True
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
        self._merge_keyvals(keyvals)

    def _merge_keyvals(self, keyvals):
        for keyval in keyvals:
            self._merge_keyval(keyval, keyvals[keyval])

    def _merge_keyval(self, key, val):
        self.log.trace('%s <- %s', key, val)

        # Get the schema.
        regex = re.compile("{([A-Za-z0-9]*)}\/?")
        updated_key = regex.sub('/__listelement/', key)
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

        self.validate_against_schema(schema, val, key)

        dpath.util.new(self.db, updated_key, val)
        self.keyval[key] = val

        # TODO: if we pass the schema we have to add into self.db
        # First cover off the simple case without lists, although
        # what we have done so far won't have made it harder.
        index = 0
        if '__listelement' in updated_key:
            keys_in_path = regex.findall(key)
            path_to_work_on = updated_key
            for key_in_path in keys_in_path:
                # strip everything to the right of this key
                found_index = path_to_work_on.find('__listelement')
                left_part_of_key = path_to_work_on[0:found_index]
                right_part_of_key = path_to_work_on[found_index + len('__listelement'):]

                path = decode_path_string(left_part_of_key, separator='/')
                path.append(key_in_path)
                self._create_new_list_element_in_schema(path, key_in_path)

                path_to_work_on = left_part_of_key + key_in_path + '/' + right_part_of_key

    def validate_against_schema(self, schema, val, key=""):
        """
        This method takes in the specific part of the schema as a
        dictionary and a value and will validate and provide the
        value back - which may be converted from a string representation
        to a real representation of the data type.
        """
        if '__schema' not in schema:
            raise PyConfHoardInvalidUse('validate_against_schema not passed a valid schema definition')
        if '__type' not in schema['__schema']:
            raise PyConfHoardInvalidUse('validate_against_schema not passed a valid schema definition')

        invalid = False
        if schema['__schema']['__type'] == 'string':
            return val
        elif schema['__schema']['__type'] == 'decimal64':
            if '__fraction-digits' not in schema['__schema']:
                raise PyConfHoardInvalidYangSchema('Decimal64 must have fraction-digits', key)

            try:
                return decimal.Decimal(val)
            except decimal.InvalidOperation:
                invalid = True

        if invalid:
            raise PyConfHoardDataInvalidValueType(val, schema['__schema']['__type'], key)
        
        raise PyConfHoardUnhandledUse("validate_against_schema - %s not implemented" % (schema['__schema']['__type']))

    def set_from_string(self, full_string, command=''):
        """
        A convenience function to split apart the path, command and value
        and then call the set function.
        """
        value = decode_path_string(full_string[len(command):], get_index=-1)
        path = full_string[:-len(value)-1]
        self.set(path, value)

    def _merge_direct_to_root(self, payload):
        """
        Merge a payload direct to the root of the database.

        I think this will be extended to update the schema to deal with auto-complete
        of list nodes. When the CLI/things merge in existing data they call this method.
        """

        dpath.util.merge(self.db, payload)

    def list(self, path_string, separator=' '):
        """
        Shows structure of the databas
        """
        self.log.trace('%s LIST' % (path_string))
        path = decode_path_string(path_string, separator)
        return fetch_keys_from_path(self.schema, path)

    def get_type(self, path_string, separator=' '):
        """
        Return the type of a particular leaf from the model.
        """
        self.log.trace('%s TYPE', path_string)
        regex = re.compile("{([A-Za-z0-9]*)}\/?")
        path_string = regex.sub('/__listelement/', path_string)
        self.log.trace('%s', path_string)
        path = decode_path_string(path_string, separator)
        schema = dpath.util.get(self.schema, path)

        if '__listelement' in schema:
            return schema['__listelement']['__schema']
        elif '__schema' in schema:
            return schema['__schema']
        else:
            raise PyConfHoardAccessNonLeaf(path)

    def get(self, path_string, separator=' '):
        """
        Get the value of a node from either the datastore, this returns
        whatever object type is requested. For accessing simple data
        get_keypath is quicker..
        """
        node_type = self.get_type(path_string, separator)
        path = decode_path_string(path_string, separator)
        try:
            return dpath.util.get(self.db, path)
        except KeyError:
            pass

        return None

    def get_keypath(self, keypath):
        """
        Get the value of a node from the database
        by providing it's keypath.

        To reference list elements provide the path as 
            /some/path/to/list{key}/leaf
        """
        if keypath not in self.keyval:
            raise PyConfHoardDataPathDoesNotExist(keypath)

        return self.keyval[keypath]

    def set(self, path, set_val, separator=' '):
        """Set the value of a leaf node.
        
        This function requires a decoded path as a string
        e.g. ['root', 'brewhouse', 'temperature', 'mash', 'setpoint'] -> 65
        """
        path_string = convert_path_to_slash_string(path)
        self.log.trace('%s -> %s', path_string, set_val)
        node_type = self.get_type(path_string, '/')
        self.keyval[path_string] = set_val
        regex = re.compile("{([A-Za-z0-9]*)}\/?")
        path_string = regex.sub('/{\g<1>}/', path_string)
        path = decode_path_string(path_string, separator)
        self.log.trace('%s %s' %(path,set_val))
        self.log.trace('%s' %(self.db))
        dpath.util.new(self.db, path_string, set_val, separator='/')
        print(self.db)
        print(self.keyval)

    def create(self, path_string, list_key, separator=' '):
        """
        Create a list-item
        list keys should be a list of separated keys
        """
        node_type = self.get_type(path_string, separator)
        if '__list' not in node_type or node_type['__list'] is False:
            raise PyConfHoardNotAList(path_string)
        self._add_to_list(self.db, node_type, path_string, list_key, separator)

    def _add_to_list(self, db, node_type, path_string, list_keys, separator=' '):
        path = decode_path_string(path_string, separator)
        list_element = dpath.util.get(self.schema, path)
        if not len(list_keys) == len(list_element['__listelement']['__schema']['__keys']):
            raise PyConfHoardWrongKeys(path, list_element['__listelement']['__schema']['__keys'])

        # string_composite_key = '{'
        string_composite_key = ''
        lk = 0
        for list_key in list_element['__listelement']['__schema']['__keys']:
            string_composite_key = string_composite_key + list_keys[lk] + ' '
            lk = lk + 1
        # string_composite_key = string_composite_key[:-1] + '}'
        string_composite_key = string_composite_key[:-1]

        path.append('{' + string_composite_key + '}')
        lk = 0
        for list_key in list_element['__listelement']['__schema']['__keys']:
            path.append(list_key)
            self.keyval[path_string + '{' + list_keys[lk] + '}/' + list_key] = list_keys[lk]
            dpath.util.new(db, path, list_keys[lk])
            path.pop()
            lk = lk + 1

        self._create_new_list_element_in_schema(path, string_composite_key)

    def _create_new_list_element_in_schema(self, path, string_composite_key):
        """
        This method takes in a path and will extend the schema so that the list element
        includes the same schema data.

        e.g. if we have a path /root/simplelist which is a list with a __listelement
        describing it's schema.

        And this is called with a path such as /root/simplelist/glow then we will
        end up with /root/simplelist/glow with a matching schema.
        THe paths on the new listelement will be adjusted with the new keys.
        """
        self.log.trace('%s %s ~extend-schema', convert_path_to_slash_string(path), string_composite_key)
        val = path.pop()
        list_element = dpath.util.get(self.schema, path)
        path.append(val)

        new_list_element = {}
        for list_item in list_element['__listelement']:
            new_list_element[list_item] = copy.deepcopy(list_element['__listelement'][list_item])
            if '__schema' in new_list_element[list_item]:
                new_list_element[list_item]['__schema']['__path'] = new_list_element[list_item]['__schema']['__path'].replace(
                    '/__listelement', '{' + string_composite_key + '}', 1)

        dpath.util.new(self.schema, path, new_list_element)

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
        path = decode_path_string(path_string, separator)
        fragment = dpath.util.get(db, path)
        return json.dumps(fragment, indent=4, sort_keys=True)
