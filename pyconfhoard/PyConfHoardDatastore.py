#!/usr/bin/env python3
import copy
import json
import sys
import json
import os
import dpath.util
import PyConfHoardExceptions


class PyConfHoardDataFilter:

    def __init__(self):
        self.root = {}

    def _check_if_suitable_blank_values(self, _obj, filter_blank_values):
        if '__value' in _obj and _obj['__value']:
            return True
        elif filter_blank_values is False:
            return True
        return False

    def _check_if_suitable_config_non_config(self, _obj, config):
        if '__leaf' in _obj and _obj['__leaf'] is True:
            if config == _obj['__config']:
                return True
        else:
            if config is True and '__decendentconfig' in _obj and _obj['__decendentconfig']:
                return True
            elif config is False and '__decendentoper' in _obj and _obj['__decendentoper']:
                return True
        return False

    def _check_suitability(self, _obj, config, filter_blank_values):
        config = self._check_if_suitable_config_non_config(_obj, config)
        blanks = self._check_if_suitable_blank_values(_obj, filter_blank_values)
        overall = config and blanks
        return config and blanks

    def _convert(self, _obj, filter_blank_values=True, config=None, collapse__value=True):

        for key in _obj:
            if isinstance(_obj[key], dict):
                if '__path' in _obj[key]:
                    val = None
                    suitable = self._check_suitability(_obj[key], config, filter_blank_values)
                    if suitable:
                        if '__container' in _obj[key] and _obj[key]['__container']:
                            dpath.util.new(self.root, _obj[key]['__path'], {})
                        elif '__list' in _obj[key] and _obj[key]['__list']:
                            dpath.util.new(self.root, _obj[key]['__path'], {})
                        elif collapse__value is False:
                            dpath.util.new(self.root, _obj[key]['__path'], {'__value': _obj[key]['__value']})
                        else:
                            dpath.util.new(self.root, _obj[key]['__path'], _obj[key]['__value'])

                    self._convert(_obj[key], filter_blank_values=filter_blank_values, config=config, collapse__value=collapse__value)

    def convert(self, _obj, config=None, filter_blank_values=True, collapse__value=True):
        self._convert(_obj, config=config, filter_blank_values=filter_blank_values, collapse__value=collapse__value)
        return self.root


class PyConfHoardDatastore:

    def __init__(self):
        self.db = {}

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

    def view(self, path_string, config, filter_blank_values=True):
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

        pretty = PyConfHoardDataFilter()
        raw_object = self.get_object(path_string)
        filtered = pretty.convert(raw_object, config=config, filter_blank_values=filter_blank_values)
        navigated = self._get(path_string, obj=filtered, get_value=False)
        return navigated

    def merge_node(self, new_node, separator=' '):
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
        leaf_metadata = self._get(path, get_value=False, separator=separator)
        if not ('__leaf' in leaf_metadata and leaf_metadata['__leaf']):
            raise ValueError('Path: %s is not a leaf - cannot set a value' % (path))
        if '__listkey' in leaf_metadata and leaf_metadata['__listkey']:
            raise ValueError('Path: %s is a list key - cannot set keys' % (path))

        path.append('__value')
        dpath.util.set(self.db, path, set_val)
        node = self._get(path_string, get_value=False, separator=separator)

    def get(self, path_string, separator=' '):
        return self._get(path_string, get_value=True, separator=separator)

    def get_object(self, path_string, separator=' '):
        return self._get(path_string, get_value=False, separator=separator)

    def _get(self, path_string, get_value=True, separator=' ', obj=None):
        """
        This method returns an explicit object from the database.
        The input can be a path_string and will be decoded, if we are passed a list
        we will decode it further.

        By default this operates on the default datastore (self.db) but
        an optional object can be passed in instead.

        TODO: in future we should intelligently derrive if get_value is required
        or get is rquried.
        """

        if obj is None:
            obj = self.db

        if isinstance(path_string, list):
            path = path_string
        else:
            path = self.decode_path_string(path_string, separator)

        if len(path) == 0:
            return obj

        if get_value:
            return self._get_value(path, dpath.util.get(obj, path))
        else:
            return dpath.util.get(obj, path)

    def create(self, path_string, keys, separator=' '):
        """Create a list item
        Note: keys is a space separated list of key values
        """
        # TODO: validation required on set of each of the keys
        leaf_metadata = self._get(path_string, get_value=False, separator=separator)
        if not ('__list' in leaf_metadata and leaf_metadata['__list']):
            raise ValueError('Path: %s is not a list - cannot create an item' % (self.decode_path_string(path_string)))
        if not ('__keys') in leaf_metadata:
            raise ValueError('List does not have any keys')

        our_keys = keys.split(' ')
        required_keys = leaf_metadata['__keys'].split(' ')

        if not len(our_keys) == len(required_keys):
            raise ValueError("Path: %s requires the following %s keys %s - %s keys provided" %
                             (self.decode_path_string(path_string), len(required_keys), required_keys, len(our_keys)))

        list_element = self.get_object(path_string)
        if keys in list_element:
            raise ValueError("Path: %s key already exists (or key has same name as a yang attribute in this list" % (self.decode_path_string))

        new_list_element = {}
        for list_item in list_element:
            if list_item[0:2] == '__':
                pass
            else:
                new_list_element[list_item] = copy.deepcopy(list_element[list_item])

        list_element[keys] = new_list_element
        for keyidx in range(len(required_keys)):
            this_key_name = required_keys[keyidx]
            list_element[keys][this_key_name]['__value'] = our_keys[keyidx]

    def _get_value(self, path, obj):
        """
        This method takes an object and return the value or None.
        If a default is set and there is not __value we will return
        __default instead.
        """
        if '__leaf' in obj and obj['__leaf'] == True:
            if '__value' in obj and obj['__value']:
                return obj['__value']
            elif '__default' in obj:
                return obj['__default']
            else:
                return None

        else:
            raise ValueError('Path: %s is not a leaf - cannot get a value' % (path))

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

        try:
            obj = self.get_object(path)
        except KeyError:
            raise ValueError('Path: %s does not exist - cannot build list' %
                             (self.convert_path_to_slash_string(path)))

        filter = PyConfHoardDataFilter()
        filtered = filter.convert(obj, config=config, filter_blank_values=filter_blank_values)
        return dpath.util.get(filtered, path).keys()


class PyConfHoardDataStoreLock:

    """
    This class allows us to provide locking of datastores and manage
    giving up the lock if the consumer has a problem.

    This class is largely tested by the REST folder.
    """

    def __init__(self, base, datastore, path):
        self.base = base
        self.datastore = datastore
        self.path = path

    def __enter__(self):
        if os.path.exists('%s/%s/%s.lock' % (self.base, self.datastore, self.path)):
            raise PyConfHoardExceptions.DataStoreLock(message='Failed to obtain lock - datastore %s/%s is already locked' %
                                                      (self.datastore, self.path), errors=None)

        o = open('%s/%s/%s.lock' % (self.base, self.datastore, self.path), 'w')
        o.close()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists('%s/%s/%s.lock' % (self.base, self.datastore, self.path)):

            os.unlink('%s/%s/%s.lock' % (self.base, self.datastore, self.path))
        print('exit')

    def patch(self, obj):
        if not os.path.exists('%s/%s/%s.pch' % (self.base, self.datastore, self.path)):
            parent_obj = {}
        else:
            pch = open('%s/%s/%s.pch' % (self.base, self.datastore, self.path))
            parent_obj = json.loads(pch.read())
            pch.close()

        dpath.util.merge(parent_obj, obj)

        new_pch = open('%s/%s/%s.pch' % (self.base, self.datastore, self.path), 'w')
        new_pch.write(json.dumps(parent_obj, indent=4))
        new_pch.close()

        if self.datastore is 'running':
            new_pch = open('%s/%s/%s.pch' % (self.base, 'persist', self.path), 'w')
            new_pch.write(json.dumps(parent_obj, indent=4))
            new_pch.close()

        return json.dumps(parent_obj, indent=4)
