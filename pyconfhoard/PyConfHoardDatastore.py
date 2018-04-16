#!/usr/bin/env python3

import copy
import sys
import json
import dpath.util

class PyConfHoardDatastore:
    
    def __init__(self):
        self.db = {}

    def load_blank_schema(self, json_file):
        schema_file = open(json_file)
        self.db = json.loads(schema_file.read())
        schema_file.close()

    def decode_path_string(self, path, separator=' ', ignore_last_n=0):
        """
        TODO: in future we should look to intelligently seprate on spaces
        i.e. level1 level2 level3 cfgonly "this is a value" should result in a path
        path = ['level1', 'level2', 'level3', 'cfgonly']
        value = 'this is a value'
        """
        if not isinstance(path, list):
            separated = path.split(separator)
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

        return separated


    def get_filtered(self, path_string, config):
        """
        Get a filtered view of configuration from the database.
        If we request not to see config=True or config=False these nodes will be
        removed.
        """
        def filter_node(obj, new_dict, config):
            # print ('filter_node: %s' %(obj))
            for key in obj:
                if isinstance(obj[key], dict):
                    config_test = PyConfHoardDatastore._check_for_config_or_not_config(obj[key], config)
            #        print ('configtest...', config_test)
                    if config_test:
                        if not key[0:2] == '__':
                            new_dict[key] = {}
                            xx = filter_node(obj[key], new_dict[key], config)
                else:
                    if key == '__value' and obj[key]:
                        new_dict[key] = obj[key]

            return new_dict

        original_obj = self.get_object(path_string)
        new_dict = {}
        new_dict = filter_node(original_obj, new_dict, config)
        return new_dict

    def merge_node(self, new_node, separator=' '):
        node = self.get_object('', separator=separator)
#        print ('trying to merge into ... ', node)
#        print ('want to merge in.... ', new_node)
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
            raise ValueError('Path: %s is a list key - cannot set keys' %(path))

        path.append('__value')
        dpath.util.set(self.db, path, set_val)
        node = self._get(path_string, get_value=False, separator=separator)

    def get(self, path_string, separator=' '):
        return self._get(path_string, get_value=True, separator=separator)

    def get_object(self, path_string, separator=' '):
        return self._get(path_string, get_value=False, separator=separator)

    def _get(self, path_string, get_value=True, separator=' '):
        """
        This method returns an explicit object from the database.
        The input can be a path_string and will be decoded, if we are passed a list
        we will decode it further.

        See also get_filtered
        """
        if isinstance(path_string, list):
            path = path_string
        else:
            path = self.decode_path_string(path_string, separator)

        if len(path) == 0:
            return self.db

        if get_value:
            return self._get_value(path, dpath.util.get(self.db, path))
        else:
            return dpath.util.get(self.db, path)

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
                                 

        #print ('xxxxsetting', path_string + separator + key)
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
        # print (json.dumps(list_element, indent=4)) 


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
            raise ValueError('Path: %s is not a leaf - cannot get a value')

    def list(self, path_string, config=True):
        try:
            obj = self.get_object(path_string)
        except KeyError:
            raise ValueError('Path: %s does not exist - cannot build list' % (path_string.replace(' ','/')))
        return self._build_list(obj, config)

    def list_root(self, config=True):
        obj = self.db
        return self._build_list(obj, config)

    def _build_list(self, obj, config):
        keys = []
        for key in obj:
            if self._filter(obj[key], config):
                keys.append(key)

        return keys

    @staticmethod
    def _check_for_config_or_not_config(obj, config, result=False):
        if result:
            return True
        for key in obj:
            if not isinstance(obj, dict):
                pass
            elif isinstance(obj[key], dict) :
                if '__config' in obj[key] and obj[key]['__config'] == config:
                    return True
                result = PyConfHoardDatastore._check_for_config_or_not_config(obj[key], config, result)
            else:
                if key == '__config' and obj[key] == config:
                    return True
        return result

    def _filter(self, obj, config):
        """
        Filter to make sure one or more of our decendants match the type
        """
        result = PyConfHoardDatastore._check_for_config_or_not_config(obj, config)
    #        print ('final answer... for obj',result)
        return result
