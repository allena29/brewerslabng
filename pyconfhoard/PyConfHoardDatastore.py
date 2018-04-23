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
        pretty = PyConfHoardFilter()
        raw_object = self.get_raw(path_string)
        filtered = pretty.convert(raw_object, config=config, filter_blank_values=filter_blank_values)
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
        node = self.get_object([], separator=separator)
        dpath.util.merge(node, new_node)

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

        path.append('__value')
        dpath.util.set(self.db, path, set_val)
        node = self._get(path_string, separator=separator)

    def get(self, path_string, separator=' '):
        """
        This method gets a terminating node of the database.

        In future we probably would rather this method intelligently
        return data in the way that get_object/get_listitem would
        """
        return self._get(path_string, separator=separator)

    def get_object(self, path_string, separator=' '):
        """
        This method returns an object of dat
        """
        warnings.warn('get_object will be deprecated - see get_schema/get_raw/get')
        return self._get(path_string, separator=separator)

    def get_schema(self, path_string, separator=' '):
        """
        This method returns both the schema portion of the node in question, this may
        be lacking some of the structure which gives the data it's context to the 
        parent children.
        """
        schema = self._get(path_string, separator=separator, return_schema=True)
        if '__listelement' in schema:
            return schema['__listelement']['__schema']
        else:
            return schema['__schema']

    def get_raw(self, path_string, separator=' '):
        """
        This method returns a raw version of the object with schema and values combined.
        """
        composite = self._get(path_string, separator=separator, return_raw=True)
        return composite

    def _get(self, path_string, separator=' ', obj=None, return_schema=False, return_raw=False):
        """
        This method returns an explicit object from the database.
        The input can be a path_string and will be decoded, if we are passed a list
        we will decode it further.

        By default this operates on the default datastore (self.db) but
        an optional object can be passed in instead.
        """

        if obj is None:
            obj = self.db

        if isinstance(path_string, list):
            path = path_string
        else:
            path = self.decode_path_string(path_string, separator)

        if len(path) == 0:
            return obj

        if not return_schema:
            value, metadata = self._separate_value_from_metadata(dpath.util.get(obj, path))
            return value
        elif not return_raw:
            return dpath.util.get(obj, path)
        else:
            value, metadata = self._separate_value_from_metadata(dpath.util.get(obj, path))
            return metadta

    @staticmethod
    def _separate_value_from_metadata(obj):
        schema = {}
        values = {}
        if '__schema' in obj:
            schema = obj['__schema']

        if '__value' in obj:
            return obj['__value'], schema
        elif '__list' in schema and schema['__list']:
            list = {}
            for key in obj:
                if key is not '__schema':
                    list[key] = obj[key]
            return list, schema
        elif '__container' in schema and schema['__container']:
            container = {}
            for key in obj:
                if key is not '__schema':
                    container[key] = obj[key]
            return (container, schema)
        elif '__listelement' in obj:
            # empty list
            return (obj, schema)

        raise ValueError('Unhandled case in _separate_value_from_metadata %s' % (obj))

    def create(self, path_string, keys, separator=' '):
        """Create a list item
        Note: keys is a space separated list of key values
        """
        # TODO: validation required on set of each of the keys
        path = self.decode_path_string(path_string, separator)

        leaf_metadata = self.get_schema(path_string, separator=separator)
        if not ('__list' in leaf_metadata and leaf_metadata['__list']):
            raise ValueError('Path: %s is not a list - cannot create an item' % (path))
        if not ('__keys') in leaf_metadata:
            raise ValueError('List does not have any keys')

        our_keys = keys.split(' ')
        required_keys = leaf_metadata['__keys'].split(' ')

        if not len(our_keys) == len(required_keys):
            raise ValueError("Path: %s requires the following %s keys %s - %s keys provided" %
                             (self.decode_path_string(path_string), len(required_keys), required_keys, len(our_keys)))

        list = self.get_raw(path)
        # Copy the templated list element
        path.append('__listelement')
        list_element_template = self.get_raw(path)
        if keys in list_element_template:
            raise ValueError("Path: %s key already exists (or key has same name as a yang attribute in this list" % (self.decode_path_string))
        path.pop()

        new_list_element = {}
        for list_item in list_element_template:
            if list_item[0:2] == '__':
                pass
            else:
                new_list_element[list_item] = copy.deepcopy(list_element_template[list_item])
        list[keys] = new_list_element

        for keyidx in range(len(required_keys)):
            this_key_name = required_keys[keyidx]
            # t the key values themselves
            list[keys][this_key_name]['__value'] = our_keys[keyidx]
            list_item_path = list[keys][this_key_name]['__schema']['__path']

            # update the path so it's not /simplelist/item it should be /simplelist/<our keys>/item
            replacement_path_with_our_key = list_item_path[0:list_item_path.rfind(this_key_name)] + keys + '/' + this_key_name
            list[keys][this_key_name]['__schema']['__path'] = replacement_path_with_our_key
        # Would rather not put this here, but it s required by separate_schema_from_values
        list[keys]['__listelement'] = True

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
            return self.db.keys()
        warnings.warn("List needs to send schema into convert - otherwise it cant-filter- some unit tests are passing without this though")
        try:
            obj = self.get_raw(path)
        except KeyError:
            raise ValueError('Path: %s does not exist - cannot build list' %
                             (self.convert_path_to_slash_string(path)))

        filter = PyConfHoardFilter()
        filtered = filter.convert(obj, config=config, filter_blank_values=filter_blank_values)
        return dpath.util.get(filtered, path).keys()

    def _merge_direct_to_root(self, new_node):
        """
        WARNING: this method has no safety checks
        """
        dpath.util.merge(self.db, new_node)
