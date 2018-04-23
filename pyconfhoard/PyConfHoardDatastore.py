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


class PyConfHoardDataFilter:

    """
    This class is intended to take a schema based representation of the data
    and instead return the user something that looks more meaningful.

    E.g. our schema looks like this (some of the details has been stripped to 
    aid readability).

    "simplestleaf": {
        "__config": true,
        "__leaf": true,
        "__value": null,
        "__path": "/simplestleaf",
        "__listkey": false,
        "__type": "string",
        "__rootlevel": true
    },
    "simplecontainer": {
        "__path": "/simplecontainer",
        "__container": true,
        "__decendentconfig": true,
        "__decendentoper": true,
        "__rootlevel": true,
        "leafstring": {
                ..
        },
        "leafnonconfig": {
                ..
        }
    },
    "simplelist": {
        "__list": true,
        "__elements": {},
        "__path": "/simplelist",
        "__keys": "item",
        "__decendentconfig": true,
        "__decendentoper": true,
        "__rootlevel": true,
        "item": {
            "__config": true,
            "__leaf": true,
            "__value": null,
            "__path": "/simplelist/item",
            "__listkey": true,
            "__type": "string",
            "__rootlevel": false
        },
        "subitem": {
                ..
        }
    }

    We would like to translate to
    {
        "simplestleaf": <value>,
        "simplecontainer" {
            "leafstring": <value>,
            "leafnoncofnig: <value>,
        "simplelist": {
            <listkey>: {
                "item": <listkey>,
                "subitem": <value>
            }
        }
    }

    If there are no listitems then simplelist shoudl jsut be {}
    """

    def __init__(self):
        self.root = {}
        self.log = logging.getLogger('DatastoreBackend')
        self.log.debug('Filter Instance Started %s', self)

    def _check_if_suitable_blank_values(self, _obj, _schema, filter_blank_values):
        if '__value' in _obj and _obj['__value']:
            return True
        elif filter_blank_values is False:
            return True
        return False

    def _check_if_suitable_config_non_config(self, _obj, _schema, config):
        if '__leaf' in _schema and _schema['__leaf'] is True:
            if config == _schema['__config']:
                return True
        else:
            if config is True and '__decendentconfig' in _schema and _schema['__decendentconfig']:
                return True
            elif config is False and '__decendentoper' in _schema and _schema['__decendentoper']:
                return True
        return False

    def _check_suitability(self, _obj, _schema, config, filter_blank_values):
        config = self._check_if_suitable_config_non_config(_obj, _schema, config)
        blanks = self._check_if_suitable_blank_values(_obj, _schema, filter_blank_values)
        overall = config and blanks
        self.log.debug('%s %s: config_suitable: %s blank_suitable: %s', _schema['__path'], overall, config, blanks)
        return config and blanks

    def _convert(self, _obj, filter_blank_values=True, config=None):
        """
        """
        for key in _obj:
            if isinstance(_obj[key], dict) and '__schema' in _obj[key] and key is not '__schema':
                _schema = _obj[key]['__schema']
                if '__path' in _schema:
                    val = None

                    suitable = self._check_suitability(_obj[key], _schema, config, filter_blank_values)
                    if suitable:
                        if '__container' in _schema and _schema['__container']:
                            self.log.trace('Creating Tree for %s which is a container', _schema['__path'])
                            dpath.util.new(self.root, _schema['__path'], {})
                        elif '__leaf' in _schema and _schema['__leaf']:
                            self.log.trace('Creating Tree for %s which is a leaf', _schema['__path'])
                            dpath.util.new(self.root, _schema['__path'], _obj[key]['__value'])
                        else:
                            self.log.error('Unable to create tree - %s is unhandled in %s', _obj[key], self._convert)

                    self._convert(_obj[key], filter_blank_values=filter_blank_values, config=config)
            elif isinstance(_obj[key], dict) and '__listelement' in _obj[key] and key is not '__listelement':
                _schema = _obj[key]['__listelement']['__schema']
                if '__path' in _schema:
                    val = None

                    suitable = self._check_suitability(_obj[key], _schema, config, filter_blank_values)
                    if suitable:
                        if '__list' in _schema and _schema['__list']:
                            self.log.trace('%s is a list', _schema['__path'])
                            dpath.util.new(self.root, _schema['__path'], {})
                        else:
                            a = 5/0
                            self.log.error('%s is unhandled in %s', _obj[key], self._convert)

                    for listitem in _obj[key]:
                        if not listitem == '__listelement':
                            self.log.trace('Creating Tree for %s which is a list element', _obj[key]['__listelement']['__schema']['__path'])
                            dpath.util.new(self.root, _obj[key]['__listelement']['__schema']['__path'], {})
                            self._convert(_obj[key][listitem], filter_blank_values=filter_blank_values, config=config)

    def convert(self, _obj, config=None, filter_blank_values=True):
        if '__schema' in _obj:
            self.log.error('Object: Not valid')
            self.log.trace('%s', _obj)

        self.log.info('Filtering: blank_values %s config: %s len(obj): %s', filter_blank_values, config, len(_obj.keys()))
        self.log.trace('%s', _obj.keys())
        self._convert(_obj, config=config, filter_blank_values=filter_blank_values)
        self.log.info('Filtered: len(obj): %s', len(self.root.keys()))
        return self.root


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
        pretty = PyConfHoardDataFilter()
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
        node = self._get(path_string, get_value=False, separator=separator)

    def get(self, path_string, separator=' '):
        """
        This method gets a terminating node of the database.

        In future we probably would rather this method intelligently
        return data in the way that get_object/get_listitem would
        """
        return self._get(path_string, get_value=True, separator=separator)

    def get_object(self, path_string, separator=' '):
        """
        This method returns an object of dat
        """
        warnings.warn('get_object will be deprecated - see get_schema/get_raw/get')
        return self._get(path_string, get_value=False, separator=separator)

    def get_schema(self, path_string, separator=' '):
        """
        This method returns both the schema portion of the node in question, this may
        be lacking some of the structure which gives the data it's context to the 
        parent children.
        """
        schema = self._get(path_string, get_value=True, separator=separator, return_schema=True)
        if '__listelement' in schema:
            return schema['__listelement']['__schema']
        else:
            return schema['__schema']

    def get_raw(self, path_string, separator=' '):
        """
        This method returns a raw version of the object with schema and values combined.
        """
        composite = self._get(path_string, get_value=True, separator=separator, return_raw=True)
        return composite

    def _get(self, path_string, get_value=True, separator=' ', obj=None, return_schema=False, return_raw=False):
        """
        This method returns an explicit object from the database.
        The input can be a path_string and will be decoded, if we are passed a list
        we will decode it further.

        By default this operates on the default datastore (self.db) but
        an optional object can be passed in instead.

        TODO: in future we should intelligently derrive if get_value is required
        or get is rquried.

        Returns:
            value by default
            tuple of (value, metadata) if return_schema is set
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

        filter = PyConfHoardDataFilter()
        filtered = filter.convert(obj, config=config, filter_blank_values=filter_blank_values)
        return dpath.util.get(filtered, path).keys()

    def _merge_direct_to_root(self, new_node):
        """
        WARNING: this method has no safety checks
        """
        dpath.util.merge(self.db, new_node)


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
