import logging
import json
import os
import dpath.util
import requests
from PyConfHoardCommon import decode_path_string
from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardError import PyConfHoardPathAlreadyRegistered,PyConfHoardDataPathDoesNotExist,PyConfHoardDataPathNotRegistered

class Data:


    """
    This class provides a single interface to data which can be join many things
    into a consistent view.
    """

    DISCOVER_URL = "/v1/discover"
    DATASTORE_URL = "/v1/datastore"

    def __init__(self, config_schema=None, oper_schema=None):
        self.config = PyConfHoardDatastore()
        self.oper = PyConfHoardDatastore()
        if config_schema:
            self.config.load_blank_schema(config_schema)
        if oper_schema:
            self.oper.load_blank_schema(oper_schema)
        self.config.readonly = True
        self.oper.readonly = True

        self.config_schema = config_schema
        self.oper_schema = oper_schema

        self.map = {}

    def register_from_web(self, server):
        """
        This method uses a URL to discover the entire schema of the datastore
        and how it has been subdividied. This will then make the relevant calls
        to populate the database.

        There is no similair register_from_file
        """
        response = requests.get(server + self.DISCOVER_URL).text
        discover = json.loads(response)

        self.config_schema = discover['schema-config']
        self.oper_schema = discover['schema-oper']
        datastores = discover['datastores']
        for datastore in discover['datastores']:
            metadata = discover['datastores'][datastore]
            self.register(metadata['yangpath'], skip_schema_load=True)
            self.load_from_web(metadata['yangpath'],
                                server + self.DATASTORE_URL + '/running/' + metadata['appname'],
                                server + self.DATASTORE_URL + '/operational/' + metadata['appname'])



    def _lookup_datastore(self, path_string, database='config'):
        path = str(decode_path_string(path_string))
        if path_string in self.map:
            return self.map[path_string][database]

        for data in self.map:
            if path_string[0:len(data)] == data:
                print('about to use %s for %s' %(data,path_string))
                return self.map[data][database]
        raise PyConfHoardDataPathNotRegistered(path_string)

    def list(self, path_string, separator=' '):
        self._lookup_datastore(path_string)

        try:
            return self.config.list(path_string, separator)
        except:
            pass
        try:
            return self.oper.list(path_string, separator)
        except:
            pass
        
        raise PyConfHoardDataPathDoesNotExist(path_string) 

    def list(self, path_string, separator=' '):
        try:
            return self.config.list(path_string, separator)
        except:
            pass
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
        path = full_string[:-len(value)-1]
        self.set(path, value, database, separator=' ')

    def set(self, path_string, set_val, database='config', separator=' '):
        """
        Set a value in the configuration datastore.

        If the database value is set to 'oper' the changes will apply to
        the operational datastore instead.
        """
        data = self._lookup_datastore(path_string, database)
        print('using instnace %s for setting data' % (data))
        data.set(path_string, set_val, separator)

    def create(self, path_string, list_key, database='config', separator=' '):
        """
        Create a list item
        """
        data = self._lookup_datastore(path_string, database)
        data.create(path_string, list_key, separator)

    def register(self, path_string, readonly=False, skip_schema_load=False):
        """
        This method will registers a configuration/oper datastores at a specifc
        part of the database.
        """
        if str(path_string) in self.map:
            raise PyConfHoardPathAlreadyRegistered(path_string)

        path = decode_path_string(path_string, separator='/')

        thisconfig = PyConfHoardDatastore()
        thisoper = PyConfHoardDatastore()
        if not skip_schema_load:
            thisconfig.load_blank_schema(self.config_schema)
            thisoper.load_blank_schema(self.oper_schema)
        dpath.util.new(self.config.db, path, thisconfig)
        dpath.util.new(self.oper.db, path, thisoper)

        self.map[path_string] = {'config': thisconfig,
                                 'oper': thisoper}

        thisconfig.readonly = False
        thisoper.readonly = False

    def _load(self, path, json_config=None, json_oper=None):
        """
        This internal methods takes a path of the database along with 
        json strings for the configuration and operational data.

        The data here must be keyval pairs
        """
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

    def load_from_web(self, path, url_config=None, url_oper=None):
        """
        Load data from a web URL and merge it into the correct data-store
        """
        oper_incoming = None
        if url_oper:
            oper_incoming = requests.get(url_oper).text
        config_incoming = None
        if url_config:
            config_incoming = requests.get(url_config).text

        self._load(path, config_incoming, oper_incoming)


class Thing:

    LOG_LEVEL = 3
    APPNAME = None
    PATHPREFIX = None

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

        # Load schema file - must have been generate by yin2json
        self.config = PyConfHoardDatastore()
        self.config.load_blank_schema(config_schema)
        self.oper = PyConfHoardDatastore()
        self.oper.load_blank_schema(oper_schema)

        self.log.info('PyConfHoard Load Default Schema: OK')

        if open_stored_config:
            self._open_stored_config()

    def _open_stored_config(self):
        if open_stored_config:
            working_directory = os.getcwd()
            datastore = '../../datastore'
            if os.path.exists('%s/persist/%s.pch' % (datastore, self.APPNAME)):
                self.log.info('Loading previous persisted data')

                # Note: we trust when changes are written they are written directly
                # to persist.... so we always just write to running for clients such
                # as the CLI to read frmo
                o = open('%s/persist/%s.pch' % (datastore, self.APPNAME))
                json_str = o.read()
                o.close()

                self.config._merge_direct_to_root(json.loads(json_str))

                o = open('%s/running/%s.pch' % (datastore, self.APPNAME), 'w')
                o.write(self.config.dump())
                o.close()

            elif os.path.exists('%s/startup/%s.pch' % (datastore, self.APPNAME)):
                self.log.info('Loading startup default data')
                o = open('%s/startup/%s.pch' % (datastore, self.APPNAME))
                json_str = o.read()
                o.close()
                print('TODO merge required here')
                print('After tha we should overwrite running')

            if not os.path.exists('%s/operational/%s.pch' % (datastore, self.APPNAME)):
                self.log.info('No existing opdata... providing empty schema')
                opdata = open('%s/operational/%s.pch' % (datastore, self.APPNAME), 'w')
                opdata.write(self.oper.dump())
                opdata.close()

            if not os.path.exists('%s/running/%s.pch' % (datastore, self.APPNAME)):
                self.log.info('No existing running.. providing empty schema')
                cfgdata = open('%s/running/%s.pch' % (datastore, self.APPNAME), 'w')
                cfgdata.write(self.config.dump())
                cfgdata.close()

        if hasattr(self, 'setup') and callable(self.setup):
            self.log.info('PyConfHoard Setup %s' % (self))
            self.setup()

        self.log.info('PyConfHoard Started %s' % (self))

    def get_config(self, path):
        """
        This method takes in an XPATH(like?) expresion and returns data objects.
        """
        val = self.datastore.get(self.PATHPREFIX + path, separator='/')
        self.log.debug('GET: %s <= %s', path, val)
        return val

    def register(self):
        self.log.info("Registering module")
        metadata = {
            'appname': self.APPNAME,
            'yangpath': self.PATHPREFIX,
        }

        o = open('../../datastore/registered/%s.pch' % (self.APPNAME), 'w')
        o.write(json.dumps(metadata))
        o.close()

    def __del__(self):
        self.log.info('PyConfHoard Finished: %s' % (self))
