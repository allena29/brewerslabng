import logging
import dpath.util
import json
import PyConfHoardExceptions


class PyConfHoardFilter:
    """
    This class is intended to take a schema based representation of the data
    and instead return the user something that looks more meaningful.

    E.g. our schema looks like this (some of the details has been stripped to 
    aid readability).

    The filter always operates on the root of the database, and takes 
    the schema and values when initialising the filter.

    "simplestleaf": {
        "__config": true,
        "__leaf": true,
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

    def __init__(self, obj, obj_values):
        self.root = {}
        self.root_values = {}
        self.log = logging.getLogger('DatastoreBackend')
        self.log.debug('Filter Instance Started %s', self)
        self.obj = obj
        self.obj_values = obj_values


    def _check_if_suitable_blank_values(self, _obj, _objvalues, _schema, filter_blank_values):
        if filter_blank_values is False:
            return True
        # We get the full path but we might have been called with a deeper 
        # object
        try:
            val =  dpath.util.get(_objvalues, _obj['__schema']['__path'])
            return True
        except KeyError:
            pass

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

    def _check_suitability(self, _obj, _objvalues, _schema, config, filter_blank_values):
        config = self._check_if_suitable_config_non_config(_obj, _schema, config)
        blanks = self._check_if_suitable_blank_values(_obj, _objvalues, _schema, filter_blank_values)
        overall = config and blanks
        self.log.debug('%s %s: config_suitable: %s blank_suitable: %s', _schema['__path'], overall, config, blanks)
        return config and blanks

    def _convert(self, _obj, _objvalues, filter_blank_values=True, config=None):
        """
        """
        for key in _obj:
            if isinstance(_obj[key], dict) and '__schema' in _obj[key] and key is not '__schema':
                _schema = _obj[key]['__schema']
                if '__path' in _schema:
                    val = None

                    suitable = self._check_suitability(_obj[key], _objvalues, _schema, config, filter_blank_values)
                    if suitable:
                        if '__container' in _schema and _schema['__container']:
                            self.log.trace('Creating Tree for %s which is a container', _schema['__path'])
                            dpath.util.new(self.root, _schema['__path'], {})
                        elif '__leaf' in _schema and _schema['__leaf']:
                            self.log.trace('Creating Tree for %s which is a leaf', _schema['__path'])
                            try:
                                val =  dpath.util.get(_objvalues, _schema['__path'])
                            except KeyError:
                                val = None
                            dpath.util.new(self.root, _schema['__path'], val)
                        else:
                            self.log.error('Unable to create tree - %s is unhandled in %s', _obj[key], self._convert)

                    self._convert(_obj[key], _objvalues, filter_blank_values=filter_blank_values, config=config)
            elif isinstance(_obj[key], dict) and '__listelement' in _obj[key] and key is not '__listelement':
                _schema = _obj[key]['__listelement']['__schema']
                if '__path' in _schema:
                    val = None

                    suitable = self._check_suitability(_obj[key], _objvalues, _schema, config, filter_blank_values)
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
                            self._convert(_obj[key][listitem], _objvalues, filter_blank_values=filter_blank_values, config=config)

    def convert(self, config=None, filter_blank_values=True):
        """
        This method provides a tailored version of the schema which can be tailored
        to only include config/non-config values.
        In addition the schema can be supressed if filter_blank_values is set
        """
        _obj = self.obj
        _objvalues = self.obj_values
        self.log.info('Filtering: blank_values %s config: %s len(obj): %s', filter_blank_values, config, len(_obj.keys()))
#        self.log.trace('%s', _obj.keys())
#        self.log.trace('%s', _objvalues.keys())

        self._convert(_obj, _objvalues, config=config, filter_blank_values=filter_blank_values)
        self.log.info('Filtered: len(obj): %s', len(self.root.keys()))
        self.log.info('Filtered: len(obj_values): %s', len(self.root_values.keys()))
