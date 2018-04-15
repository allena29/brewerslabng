#!/usr/bin/env python2.7

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

    def decode_path_string(self, path, separator=' '):
        """
        TODO: in future we should look to intelligently seprate on spaces
        i.e. level1 level2 level3 cfgonly "this is a value" should result in a path
        path = ['level1', 'level2', 'level3', 'cfgonly']
        value = 'this is a value'
        """
        return path.split(separator)


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
 #                           print ('creating key on new_idct', key, obj[key])
                            new_dict[key] = {}
                            xx = filter_node(obj[key], new_dict[key], config)
                else:
                    if key == '__value' and obj[key]:
                        new_dict[key] = obj[key]

            return new_dict

        original_obj = self.get(path_string)
        new_dict = {}
        new_dict = filter_node(original_obj, new_dict, config)
        return new_dict

    def get(self, path_string, separator=' '):
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

        if path[0] == '':
            return self.db
        return dpath.util.get(self.db, path)

    def list_lazy(self, path_string, config=True):
        path = self.decode_path_string(path_string)
        while len(path):
            try:
                obj = self.get(path)
                return self._build_list(obj, config)
            except:
                x = path.pop()

    def list(self, path_string, config=True):
        obj = self.get(path_string)
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
            if isinstance(obj[key], dict):
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


    @staticmethod
    def _get_node(our_node, path,
                  fail_if_no_match=False,
                  lazy_fail=False,
                  create_if_no_match=None):
        """
        Attempt to filter down an object by it's keys

        our_node - an object
        path     - a space separate path of keys
                   Note: keys cannot contain spaces
        """
        if isinstance(path, list):
            keys_to_navigate = path
        else:
            keys_to_navigate = path.split(' ')

        i = 0 
        for key in keys_to_navigate:
            if len(key):
                if key in our_node:
                    our_node = our_node[key]
                elif lazy_fail and i < len(keys_to_navigate)-1:
                    raise ValueError('%s %s %s %s %s' % (our_node,path, i, len(keys_to_navigate), keys_to_navigate))
                elif fail_if_no_match:
                    raise ValueError('Path: %s does not exist' % (path))
                elif create_if_no_match and i == len(keys_to_navigate) - 2:
                    our_node[key] = create_if_no_match
            i = i + 1     
    
        return our_node

    @staticmethod
    def _set_node(obj, text):
        """
        This method takes in a string (space separated)
            like brewehouse power mode val

        We then take the last two elements as the key value and key element
        """

        set_string = text.split(' ')
        if len(set_string) < 3:
            raise ValueError("Invalid command - set some thing value")
        set_value = set_string.pop()
        set_key = set_string.pop()
        node = PyConfHoardDatastore._get_node(obj, set_string)
        node[set_key] = set_value
       
    @staticmethod
    def _validate_node(obj, text, schema):
        set_string = text.split(' ')
        if len(set_string) < 3:
            raise ValueError("Invalid command - set some thing value")
        set_value = set_string.pop()
        yang_meta = PyConfHoardDatastore._get_node(schema, set_string)

        set_key = set_string.pop()
        node = PyConfHoardDatastore._get_node(obj, set_string)
 
        if yang_meta['type'] == 'enumeration':
            if set_value not in yang_meta['enum_values']:
                raise ValueError('Invalid Value: key %s value  %s != %s' % (set_key, set_value, yang_meta['enum_values']))

        return set_value

