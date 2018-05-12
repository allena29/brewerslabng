#!/usr/bin/env python3
import copy
import json
import logging
import sys
import json
import os
import dpath.util
import warnings
import PyConfHoardExceptions
from PyConfHoardFilter import PyConfHoardFilter


class PyConfHoardDatastore:

    LOG_LEVEL = 3

    def __init__(self):
        self.db = {}
        self.db_values = {}

        logging.TRACE = 7

        def custom_level_trace(self, message, *args, **kws):
            if self.isEnabledFor(logging.TRACE):
                self._log(logging.TRACE, message, args, **kws)
        logging.Logger.trace = custom_level_trace
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.addLevelName(logging.TRACE, "TRACE")
        logging.basicConfig(level=self.LOG_LEVEL, format=FORMAT)
        self.log = logging.getLogger('DatastoreBackend')
        self.log.debug('Filter Instance Started %s', self)

    def load_blank_schema(self, json_file):
        schema_file = open(json_file)
        self.db = json.loads(schema_file.read())
        schema_file.close()

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
            separated = path.split(separator)
        else:
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

    def view(self, path_string, config, filter_blank_values=True, separator=' '):
        """
        This method provides a human readable rendering of the datastore.
        A new dictionary is returned which removes all the internal metadata

        Schema                                  Filtered
        {'key': {                               {'key': 123}
            '__path': '/key',
            '__value': None,
            '__default': 123
            }
        }

        """
        path = self.decode_path_string(path_string, separator)
        pretty = PyConfHoardFilter(self.db, self.db_values)
        pretty.convert(config=config, filter_blank_values=filter_blank_values)
        filtered = pretty.root
        if len(filtered.keys()) == 0:
            return {'configuration is blank': True}
        elif len(path) == 0:
            return filtered
        else:
            navigated = dpath.util.get(filtered, path_string, separator=separator)
            return navigated

    def _merge_node(self, new_node, separator=' '):
        """
        Applications should use PyConfHoardDataStoreLock.patch instead of this 
        function directly.
        """
        dpath.util.merge(self.db_values, new_node)

    def set(self, path_string, set_val, separator=' '):
        """
        This methods sets a value in the datastore at the pat provided.

        Initial implementation will not allow this to be used for creating
        list items.
        """
        if isinstance(path_string, list):
            path = path_string
        else:
            path = self.decode_path_string(path_string, separator)

        # TODO: validation required on set
        leaf_metadata = self.get_schema(path, separator=separator)
        if not ('__leaf' in leaf_metadata and leaf_metadata['__leaf']):
            raise ValueError('Path: %s is not a leaf - cannot set a value' % (path))
        if '__listkey' in leaf_metadata and leaf_metadata['__listkey']:
            raise ValueError('Path: %s is a list key - cannot set keys' % (path))

        dpath.util.new(self.db_values, path, set_val)

    def get(self, path_string, separator=' '):
        """
        This method gets a terminating node of the database.

        In future we probably would rather this method intelligently
        return data in the way that get_object/get_listitem would
        """
        try:
            return self._get(path_string, separator=separator)
        except KeyError:
            raise ValueError('Path: %s does not exist' % (self.convert_path_to_slash_string(path_string)))

    def get_fragment(self, path_string, separator=' '):
        """
        get_fragment returns a particular fragment of the datastore
        without any other data.

        This means that we different processes can manage different 
        parts of the database.
        """

        path = self.decode_path_string(path_string, separator)
        data = {}

        data_fragment_they_want =  dpath.util.get(self.db_values, path)
        print (data_fragment_they_want)
        dpath.util.new(data, path, data_fragment_they_want)
        print ('here')
        return data

    def get_schema(self, path_string, separator=' '):
        """
        This method returns both the schema portion of the node in question, this may
        be lacking some of the structure which gives the data it's context to the 
        parent children.
        """
        schema = self._get(path_string, separator=separator, return_schema=True)
        if '__listelement' in schema:
            return schema['__listelement']['__schema']
        elif '__schema' in schema:
            return schema['__schema']
        else:
            warnings.warn('Encountered a place where we couldnt return a schema... %s' % (schema.keys()))

    def get_list_element(self, path_string, separator=' '):
        self.log.trace('get_list_element: %s' % (path_string))
        return self._get(path_string, separator=separator)

    def has_list_item(self, path_string, separator=' '):
        """
        This method returns a boolean true/false if the list key is present.
        Note: in practice this method doesn't actually check for a list item it checks
        if the provided path exists.

        TODO: add validation here to trap cases where a deeper path is asked for/non-list item.
        """
        path = self.decode_path_string(path_string, separator)
        self.log.trace('has_list_item: %s' % (self.convert_path_to_slash_string(path)))
        try:
            if self._get(path_string, separator=separator):
                self.log.trace('has_list_item: %s - TRUE' % (path_string))
                return True
            return False
        except KeyError as err:
            self.log.trace('has_list_item: %s - FALSE' % (path_string))
            return False
        


    def _get(self, path_string, separator=' ', obj=(None, None), return_schema=False):
        """
        This method returns an explicit object from the database.
        The input can be a path_string and will be decoded, if we are passed a list
        we will not be decode it further.

        Retreiving the root of the database with the get method is not supported.

        By default this operates on the default datastore (self.db) but
        an optional object can be passed in instead.
        """
        (schema_obj, values_obj) = obj
        if schema_obj is None:
            obj = self.db
        if values_obj is None:
            values_obj = self.db_values

        if isinstance(path_string, list):
            path = path_string
        else:
            path = self.decode_path_string(path_string, separator)

        if return_schema is False:
            try:
                return dpath.util.get(values_obj, path)
            except KeyError:
                return None

        return dpath.util.get(obj, path)

    def create(self, path_string, keys, separator=' '):
        """Create a list item
        Note: keys is a space separated list of key values
        """
        # TODO: validation required on set of each of the keys
        path = self.decode_path_string(path_string, separator)

        leaf_metadata = self.get_schema(path_string, separator=separator)
        self.log.trace('create: %s' % (path_string))

        if not ('__list' in leaf_metadata and leaf_metadata['__list']):
            raise ValueError('Path: %s is not a list - cannot create an item' % (path))
        if not ('__keys') in leaf_metadata:
            raise ValueError('List does not have any keys')

        our_keys = keys.split(' ')
        required_keys = leaf_metadata['__keys'].split(' ')

        if not len(our_keys) == len(required_keys):
            raise ValueError("Path: %s requires the following %s keys %s - %s keys provided" %
                             (self.decode_path_string(path_string), len(required_keys), required_keys, len(our_keys)))

        # TODO::::: we need to validat eif a key already exists

        # Copy the templated list element
        path.append('__listelement')
        list_element_template = dpath.util.get(self.db, path)
        path.pop()

        path.append(keys)


        new_list_element = {}
        for list_item in list_element_template:
            if list_item[0:2] == '__':
                pass
            else:
                new_list_element[list_item] = copy.deepcopy(list_element_template[list_item])
        #list[keys] = new_list_element
        dpath.util.new(self.db, path, list_element_template)
        dpath.util.new(self.db_values, path, {})

        schema = dpath.util.get(self.db, path)
        values = dpath.util.get(self.db_values, path)

        #print('SCHEMA: %s' %(schema))
        #print('VALUES: %s' %(values))
    
        # TODO: this probably needs updating if we have more than a single level
        # of items within our keys... It *MAY* be ok

        for keyidx in range(len(required_keys)):
            this_key_name = required_keys[keyidx]
            # t the key values themselves
            path.append(this_key_name)
            dpath.util.new(self.db_values, path, our_keys[keyidx])
            list_item_path = schema[this_key_name]['__schema']['__path']
            # update the path so it's not /simplelist/item it should be /simplelist/<our keys>/item
            replacement_path_with_our_key = list_item_path[0:list_item_path.rfind(this_key_name)] + keys + '/' + this_key_name
            schema[this_key_name]['__schema']['__path'] = replacement_path_with_our_key



    def convert_path_to_slash_string(self, path):
        if isinstance(path, list):
            path_string = ''
            for x in path:
                path_string = path_string + '/' + x
            return path_string
        else:
            return path_string.replace(' ', '/')

    def list(self, path_string, separator=' ', config=True, filter_blank_values=True):
        """
        This method provides a list of keys within a data object, which can be
        filtered based upon config nodes, or only including nodes where a value
        is set.
        """
        path = self.decode_path_string(path_string, separator=separator)
        if len(path) == 0:
            return sorted(self.db.keys())

        try:
            obj = dpath.util.get(self.db, path)
        except KeyError:
            raise ValueError('Path: %s does not exist - cannot build list' %
                             (self.convert_path_to_slash_string(path)))
        
        try:
            obj_values = dpath.util.get(self.db_values, path)
        except KeyError:
            obj_values = {}

        #filter = PyConfHoardFilter(obj, obj_values)
        filter = PyConfHoardFilter(self.db, self.db_values)
        filter.convert(config=config, filter_blank_values=filter_blank_values)
        filtered = filter.root

        return dpath.util.get(filtered, path).keys()

    def _merge_direct_to_root(self, new_node):
        """
        WARNING: this method has no safety checks
        """
        dpath.util.merge(self.db, new_node)
