#!/usr/bin/env python2.7

import sys
import json


class PyConfHoardCommon:

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
        node = PyConfHoardCommon._get_node(obj, set_string)
        node[set_key] = set_value
       
    @staticmethod
    def _validate_node(obj, text, schema):
        set_string = text.split(' ')
        if len(set_string) < 3:
            raise ValueError("Invalid command - set some thing value")
        set_value = set_string.pop()
        yang_meta = PyConfHoardCommon._get_node(schema, set_string)

        set_key = set_string.pop()
        node = PyConfHoardCommon._get_node(obj, set_string)
 
        if yang_meta['type'] == 'enumeration':
            if set_value not in yang_meta['enum_values']:
                raise ValueError('Invalid Value: key %s value  %s != %s' % (set_key, set_value, yang_meta['enum_values']))

        return set_value

