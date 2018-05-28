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
import PyConfHoardExceptions
# from PyConfHoardFilter import PyConfHoardFilter
from PyConfHoardError import PyConfHoardAccessNonLeaf, PyConfHoardNonConfigLeaf, PyConfHoardNonConfigList, PyConfHoardNotAList, PyConfHoardWrongKeys


class PyConfHoardDatastore:


    LOG_LEVEL = 3

    def __init__(self):
        self.db = {}
        self.schema = {}

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

    def set_from_string(self, full_string, command=''):
        """
        A convenience function to split apart the path, command and value
        and then call the set function.
        """
        path = self.decode_path_string(full_string[len(command):], ignore_last_n=1)
        value = self.decode_path_string(full_string[len(command):], get_index=-1)
        self.set(path, value)

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

        print('>>>>>%s<<<<' %(path_string))
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

        dpath.util.new(self.db, path, set_val)

    def create(self, path_string, list_key, separator=' '):
        """
        Create a list-item
        list keys should be a list of separated keys
        """
        node_type = self.get_type(path_string, separator)
        path = self.decode_path_string(path_string, separator)

        if '__list' not in node_type or node_type['__list'] is False:
            raise PyConfHoardNotAList(path)
        self._add_to_list(self.db, node_type, path, list_key)

    def _add_to_list(self, db, node_type, path, list_keys):
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
            dpath.util.new(db, path, list_keys[lk])
            path.pop()
            lk = lk + 1
        print (list_element)

    def dump(self):
        return json.dumps(self.db, indent=4, sort_keys=True)

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
