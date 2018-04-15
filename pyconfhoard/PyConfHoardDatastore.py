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
        separated = path.split(separator)
        seplen = len(separated)
        for i in range(seplen):
            if separated[seplen-i-1] == '':
                separated.pop(seplen-i-1)

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
        path.append('__value')
        dpath.util.set(self.db, path, set_val)
        node = self.get(path_string, get_value=False, separator=separator)

    def get(self, path_string, get_value=True, separator=' '):
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
            return self._get_value(dpath.util.get(self.db, path))
        else:
            return dpath.util.get(self.db, path)

    def _get_value(self, obj):
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
            return obj

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
