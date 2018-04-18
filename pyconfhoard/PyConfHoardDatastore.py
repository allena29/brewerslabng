#!/usr/bin/env python3

import copy
import json
import sys
import json
import dpath.util


class PyConfHoardDataFilter:


    def __init__(self):
        self.root = {}
        
    def _convert(self, _obj, filter_blank_values=True):

        for key in _obj:
            if isinstance(_obj[key], dict):
                if '__path' in _obj[key]:
                    # print (_obj[key]['__path'], key, _obj[key])
                    if '__container' in _obj[key] and _obj[key]['__container']:
                        dpath.util.new(self.root, _obj[key]['__path'], {})
                    if '__list' in _obj[key] and _obj[key]['__list']:
                        dpath.util.new(self.root, _obj[key]['__path'], {})

                    if '__value' in _obj[key] and _obj[key]['__value'] and filter_blank_values:
                        dpath.util.new(self.root, _obj[key]['__path'], _obj[key]['__value'])
                    elif filter_blank_values == False:
                        dpath.util.new(self.root, _obj[key]['__path'], {})
                    self._convert(_obj[key], filter_blank_values=filter_blank_values)
#            else:
#                print (_obj.keys())
                
    def convert(self, _obj):
        self._convert(_obj)
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

    def view(self, path_string, config):
        """
        TBD
        """
        print  ('config option not yet supported here')
        pretty = PyConfHoardDataFilter()
        pretty.convert(self.get_object(path_string))

        return pretty.root

    def merge_node(self, new_node, separator=' '):
        node = self.get_object([], separator=separator)
        # print ('trying to merge into ... ', node)
        # print ('want to merge in.... ', new_node)
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

    def list(self, path, config=True, filter_blank_values=True):
        print ('list..',path)
        try:
            obj = self.get_object(path)
        except KeyError:
            print ('raise vale')
            raise ValueError('Path: %s does not exist - cannot build list' % (path.replace(' ','/')))
        filter = PyConfHoardDataFilter()
        filtered = filter.convert(obj)
        # If we filtered the object get the last key we filtered on
        if len(path) > 0:
            # print ('return here because %s has more than 0 elements' %(path))
            # print ('b>', dpath.util.get(filtered, path).keys())
            return dpath.util.get(filtered, path).keys()
        else:
            # print ('a>', dpath.util.get(filtered, path).keys())
            return dpath.util.get(filtered, path).keys()

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
