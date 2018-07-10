import logging
import json
import os
import dpath.util
import requests
import warnings
from requests.auth import HTTPBasicAuth
from PyConfHoardCommon import decode_path_string
from PyConfHoardDatastore import PyConfHoardDatastore, convert_path_to_slash_string
from PyConfHoardError import PyConfHoardPathAlreadyRegistered, PyConfHoardDataPathDoesNotExist, PyConfHoardDataPathNotRegistered


class Data:

    """
    This class provides a single interface to data which can be join many things
    into a consistent view.
    """

    DISCOVER_URL = "/v1/discover"
    DATASTORE_URL = "/v1/datastore"
    LOG_LEVEL = 3

    def __init__(self, config_schema=None, oper_schema=None):
        logging.TRACE = 7

        def custom_level_trace(self, message, *args, **kws):
            if self.isEnabledFor(logging.TRACE):
                self._log(logging.TRACE, message, args, **kws)
        logging.Logger.trace = custom_level_trace
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.addLevelName(logging.TRACE, "TRACE")
        logging.basicConfig(level=self.LOG_LEVEL, format=FORMAT)
        self.log = logging.getLogger('DatastoreFrontend')

        self.config = PyConfHoardDatastore()
        self.oper = PyConfHoardDatastore()
        self.log.debug('Data Frontend Instance %s' % (self))
        self.log.debug('Configuraton Instance created %s' % (self.config))
        self.log.debug('Operational Instance created %s' % (self.oper))
        if config_schema:
            self.log.debug('Loading schema %s for configuration' % (config_schema))
            self.config.load_blank_schema(config_schema)
        if oper_schema:
            self.log.debug('Loading schema %s for operational' % (oper_schema))
            self.oper.load_blank_schema(oper_schema)
        self.config.readonly = True
        self.oper.readonly = True

        self.config_schema = config_schema
        self.oper_schema = oper_schema

        self.map = {}

    def register_from_data(self, config_schema, oper_schema, datastores={}):
        """
        This method can be used in a similair way to register_from_web, however this method
        requires paths to be registered to be placed in datastores which is a list of 
        dictionaries.

        e.g.

        { 'thing1': {'yangpath': '/tupperware'} }
        """
        self.config_schema = config_schema
        self.oper_schema = oper_schema
        
        self.config.schema = config_schema
        self.oper.schema = oper_schema
        for datastore in datastores:
            metadata = datastores[datastore]
            self._register(metadata['yangpath'], metadata['appname'], config_schema, oper_schema)

    def _register(self, path, appname, config_schema, oper_schema):
        (config, oper) = self.register(path, appname, skip_schema_load=True)
        self.log.debug('Configuration Path %s instance as %s' % (path, config))
        self.log.debug('Operational Path %s instance as %s' % (path, oper))
        config.schema = config_schema
        oper.schema = oper_schema

    def register_from_web(self, server, username="no-security", password="has-been-set"):
        """
        This method uses a URL to discover the entire schema of the datastore
        and how it has been subdividied. This will then make the relevant calls
        to populate the database.
        """
        if username == 'no-security':
            warnings.warn('Default username/password has been set for reading data')
        auth = HTTPBasicAuth(username, password)

        response = requests.get(server + self.DISCOVER_URL, auth=auth).text
        discover = json.loads(response)

        self.config_schema = discover['schema-config']
        self.oper_schema = discover['schema-oper']

        self.config.schema = discover['schema-config']
        self.oper.schema = discover['schema-oper']

        datastores = discover['datastores']
        self.log.trace('REGISTER discovered %s' %(datastores.keys()))
        for datastore in discover['datastores']:
            metadata = discover['datastores'][datastore]
            self._register(metadata['yangpath'], metadata['appname'], discover['schema-config'], discover['schema-oper'])
            self.load_from_web(metadata['yangpath'],
                               server + self.DATASTORE_URL + '/running/' + metadata['appname'],
                               server + self.DATASTORE_URL + '/operational/' + metadata['appname'])

    def _lookup_datastore(self, path_string, database='config', separator='/'):
        path = decode_path_string(path_string, separator=separator, return_as_slash=True)
        if path == "/root":
            if database == 'config':
                return self.config
            else:
                return self.oper
        
        if path in self.map:
            return self.map[path][database]
        
        self.log.trace('MAP want %s: have: %s' % (path, self.map))
        for data in self.map:
            path_trimmed = path[0:len(data)]
            if path_trimmed == data:
                return self.map[data][database]

        raise PyConfHoardDataPathNotRegistered(path_string)

    def list(self, path_string, database=None,  separator=' '):
        try:
            data = self._lookup_datastore(path_string, separator=separator)
        except PyConfHoardDataPathNotRegistered as err:
            if database == 'config':
                data = self.config
            else:
                data = self.oper

        self.log.trace('Using instance %s for list operation' % (data))
        if isinstance(path_string, list):
            path = path_string
        else:
            path = decode_path_string(path_string, separator=separator)

        if database is None or database == 'config':
            try:
                return self.config.list(path_string, separator)
            except:
                pass

        if database is None or database == 'oper':
            try:
                return self.oper.list(path_string, separator)
            except:
                pass

        raise PyConfHoardDataPathDoesNotExist(path_string)

    def get(self, path_string, database='config', separator=' '):
        data = self._lookup_datastore(path_string, database)
        return data.get(path_string, separator)

        raise PyConfHoardDataPathDoesNotExist(path_string)

    def set_from_string(self, full_string, database='config', command=''):
        """
        A convenience function to split apart the path, command and value
        and then call the set function.
        """

        value = decode_path_string(full_string[len(command):], get_index=-1)
        path = decode_path_string(full_string[:-len(value)-1])
        self.set(path, value, database, separator=' ')

    def set(self, path_string, set_val, database='config', separator=' '):
        """
        Set a value in the configuration datastore.

        If the database value is set to 'oper' the changes will apply to
        the operational datastore instead.
        """
        data = self._lookup_datastore(path_string, database)
        self.log.trace('SET: %s <= %s' % (path_string, set_val))
        data.set(path_string, set_val, separator)

    def create(self, path_string, list_key, database='config', separator=' '):
        """
        Create a list item
        """
        data = self._lookup_datastore(path_string, database)
        data.create(path_string, list_key, separator)

    def register(self, path_string, appname, readonly=False, skip_schema_load=False):
        """
        This method will registers a configuration/oper datastores at a specifc
        part of the database.
        """
        if str(path_string) in self.map:
            raise PyConfHoardPathAlreadyRegistered(path_string)

        path = decode_path_string(path_string, separator='/')

        thisconfig = PyConfHoardDatastore()
        thisoper = PyConfHoardDatastore()
        thisconfig.id = appname
        thisconfig.config = True
        thisoper.id = appname
        thisoper.config = False

        if not skip_schema_load:
            thisconfig.load_blank_schema(self.config_schema)
            thisoper.load_blank_schema(self.oper_schema)
        dpath.util.new(self.config.db, path, thisconfig)
        dpath.util.new(self.oper.db, path, thisoper)

        self.map[path_string] = {'config': thisconfig,
                                 'oper': thisoper}

        thisconfig.readonly = False
        thisoper.readonly = False

        return (thisconfig, thisoper)

    def persist_to_web(self, server, path_string, username="no-security", password="has-been-set"):
        """
        Persist a particular configuration datastore to a web-server running the pyconfhoard
        REST API.

        At the moment it has been decided to only implement configuration datastores here.
        The idea is that operational data should be handled locally.
        """
        if username == 'no-security':
            warnings.warn('Default username/password has been set for persisting data')

        auth = HTTPBasicAuth(username, password)
        headers = {"Content-Type": "application/json"}

        data = self._lookup_datastore(path_string)
        url = server + self.DATASTORE_URL + '/running/' + data.id
        self.log.info('PERSIST %s (%s keys)' % (url, len(data.keyval)))

        r = requests.patch(url=url, data=json.dumps(data.keyval, indent=4, sort_keys=True),
                           auth=auth, headers=headers)

    def _load(self, path, json_config=None, json_oper=None):
        """
        This internal methods takes a path of the database along with 
        json strings for the configuration and operational data.

        The data here must be keyval pairs
        """
        self.log.trace('_LOAD %s' % (path)) 
        if path not in self.map:
            raise PyConfHoardDataPathNotRegistered(path)

        if json_config:
            config = json.loads(json_config)
            datastore = self._lookup_datastore(path, database='config')
            datastore._merge_keyvals(config)

        if json_oper:
            oper = json.loads(json_oper)
            datastore = self._lookup_datastore(path, database='oper')
            datastore._merge_keyvals(oper)

    def load_from_filesystem(self, path, filepath_config=None, filepath_oper=None):
        """
        Load data from a file system path and merge it into the correct data-store.
        """
        config_incoming = None
        if filepath_config:
            f = open(filepath_config)
            config_incoming = f.read()
            f.close()

        oper_incoming = None
        if filepath_oper:
            f = open(filepath_oper)
            oper_incoming = f.read()
            f.close()

        self._load(path, config_incoming, oper_incoming)

    def load_from_web(self, path, url_config=None, url_oper=None, username='no-security', password='has-been-set'):
        """
        Load data from a web URL and merge it into the correct data-store
        """
        if username == 'no-security':
            warnings.warn('Default username/password has been set for reading data')
        auth = HTTPBasicAuth(username, password)

        oper_incoming = None
        if url_oper:
            oper_incoming = requests.get(url_oper, auth=auth).text
        config_incoming = None
        if url_config:
            config_incoming = requests.get(url_config, auth=auth).text

        self._load(path, config_incoming, oper_incoming)

    def get_database_as_json(self, path_string, database='config', separator='/', pretty=False):
        answer = {'root': {}}
        path = decode_path_string(path_string, separator=separator)

        self.log.trace('GET_CURLY_VIEW %s' % (self.map))
        for data in self.map:
            if database == 'config':
                self.log.trace('GET_CURLY_VIEW_CFG %s' % (data))
                db = self.map[data]['config']
            else:
                self.log.trace('GET_CURLY_VIEW_OPER %s' % (data))
                db = self.map[data]['oper']

            path_to_sub_datastore = decode_path_string(data, separator='/')
            try:
                data_from_sub_datastore = dpath.util.get(db.db, path_to_sub_datastore)
                dpath.util.new(answer, path_to_sub_datastore, data_from_sub_datastore)
            except KeyError:
                pass

            if pretty:
                if len(answer['root']) == 0:
                    return 'Database is blank!'
                return json.dumps(answer['root'], indent=4, sort_keys=True)
            return json.dumps(answer, indent=4, sort_keys=True)


class Thing:

    LOG_LEVEL = 3
    APPNAME = None
    PATHPREFIX = None
    DIE = False
    DATASTORE_BASE = "../../datastore"

    def __init__(self, open_stored_config=True, config_schema="../../yang-schema-config.json",
                 oper_schema="../../yang-schema-oper.json"):
        """This method provides a common approach to build and manage pyangbind based config
        with persistence and very primitive blocking.

        Note: initial design pattern only supports a 1:1 relationship between portion of the yang
        module and owning PyConfHoard service.
        """

        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=self.LOG_LEVEL, format=FORMAT)
        self.log = logging.getLogger(self.APPNAME)
        self.log.info('PyConfHoard Init: %s' % (self))

        self.pyconfhoarddata = Data('../../yang/schema-config.json', '../../yang/schema-oper.json')
        (config, oper) = self.pyconfhoarddata.register(self.PATHPREFIX, self.APPNAME)
        # Load schema file - must have been generate by yin2json
        self.config = config
        self.oper = oper

        self.log.info('PyConfHoard Load Default Schema: OK')

        if 'PYCONF_DATASTORE' in os.environ:
            self.DATASTORE_BASE = os.environ['PYCONF_DATASTORE']

        if open_stored_config:
            self._open_stored_config()

        if hasattr(self, 'setup') and callable(self.setup):
            self.log.info('PyConfHoard Setup %s' % (self))
            self.setup()

        self.log.info('PyConfHoard Started %s' % (self))

    def _open_stored_config(self):
        working_directory = os.getcwd()


        if os.path.exists('%s/persist/%s.pch' % (self.DATASTORE_BASE, self.APPNAME)):
            self.log.info('Loading previous persisted data')

            # Note: we trust when changes are written they are written directly
            # to persist.... so we always just write to running for clients such
            # as the CLI to read frmo
            o = open('%s/persist/%s.pch' % (self.DATASTORE_BASE, self.APPNAME))
            json_str = o.read()
            o.close()

            self.config._merge_direct_to_root(json.loads(json_str))

            o = open('%s/running/%s.pch' % (self.DATASTORE_BASE, self.APPNAME), 'w')
            o.write(self.config.dump())
            o.close()

        elif os.path.exists('%s/startup/%s.pch' % (self.DATASTORE_BASE, self.APPNAME)):
            self.log.info('Loading startup default data')
            o = open('%s/startup/%s.pch' % (self.DATASTORE_BASE, self.APPNAME))
            json_str = o.read()
            o.close()

        if not os.path.exists('%s/operational/%s.pch' % (self.DATASTORE_BASE, self.APPNAME)):
            self.log.info('No existing opdata... providing empty schema')
            opdata = open('%s/operational/%s.pch' % (self.DATASTORE_BASE, self.APPNAME), 'w')
            opdata.write(self.oper.dump())
            opdata.close()

        if not os.path.exists('%s/running/%s.pch' % (self.DATASTORE_BASE, self.APPNAME)):
            self.log.info('No existing running.. providing empty schema')
            cfgdata = open('%s/running/%s.pch' % (self.DATASTORE_BASE, self.APPNAME), 'w')
            cfgdata.write(self.config.dump())
            cfgdata.close()

    def get_config(self, path):
        """
        This method takes in an XPATH(like?) expresion and returns data objects.
        """
        val = self.atastore.get(self.PATHPREFIX + path, separator='/')
        self.log.debug('GET: %s <= %s', path, val)
        return val

    def register(self):
        self.log.info("Registering module %s:%s" % (self.APPNAME, self.PATHPREFIX))
        metadata = {
            'appname': self.APPNAME,
            'yangpath': self.PATHPREFIX,
        }

        o = open('%s/registered/%s.pch' % (self.DATASTORE_BASE, self.APPNAME), 'w')
        o.write(json.dumps(metadata))
        o.close()

    def should_we_sleep(self):
        return not self.DIE

    def __del__(self):
        self.log.info('PyConfHoard Finished: %s' % (self))
