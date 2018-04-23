import logging
import json
import os
from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardFilter import PyConfHoardFilter


class Thing:

    def __init__(self, appname, yangmodule, yangpath, open_stored_config=True):
        """This method provides a common approach to build and manage pyangbind based config
        with persistence and very primitive blocking.

        The method takes two attributes
        - appname -     an application tag which may in the future be used to provide a
                        namespace. (e.g. TemperatureDS18B20)
        - yangmodule -  name of the yang module as considered to be the top-level in pyangbind
                        auto-generated code. (e.g. brewerslab)
        - yangpath -    An XPATH expression providing a single instance of the data model that this
                        goblin is responsible for. (e.g. /brewhouse/temperature)

        Note: initial design pattern only supports a 1:1 relationship between portion of the yang
        module and owning PyConfHoard service.
        """

        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger(appname)
        self.log.info('PyConfHoard Init: %s' % (self))

        # Load schema file - must have been generate by yin2json
        self._yang_obj = None
        self._appname = appname
        self._ourpath = yangpath
        self._ourmodule = yangmodule

        self.datastore = PyConfHoardDatastore()
        self.datastore.load_blank_schema('../../yang/schema.json')
        self.log.info('PyConfHoard Load Default Schema: OK')
        self.datastore.db = self.datastore.get_object(self._ourpath, separator='/')
        self.log.info('PyConfHoard Filtered Datastore: %s', self._ourpath)

        if open_stored_config:
            working_directory = os.getcwd()
            datastore = '../../datastore'
            if os.path.exists('%s/persist/%s.pch' % (datastore, self._appname)):
                self.log.info('Loading previous persisted data')
                o = open('%s/persist/%s.pch' % (datastore, self._appname))
                json_str = o.read()
                o.close()

                print('TODO merge required here')
                print('After tha we should overwrite running')

            elif os.path.exists('%s/startup/%s.pch' % (datastore, self._appname)):
                self.log.info('Loading startup default data')
                o = open('%s/startup/%s.pch' % (datastore, self._appname))
                json_str = o.read()
                o.close()
                print('TODO merge required here')
                print('After tha we should overwrite running')

            if not os.path.exists('%s/operational/%s.pch' % (datastore, self._appname)):
                self.log.info('No existing opdata... providing empty schema')
                pretty = PyConfHoardFilter()
                filtered = pretty.convert(self.datastore.db, config=False, filter_blank_values=False)

                opdata = open('%s/operational/%s.pch' % (datastore, self._appname), 'w')
                opdata.write(json.dumps(filtered, indent=4))
                opdata.close()

            if not os.path.exists('%s/running/%s.pch' % (datastore, self._appname)):
                self.log.info('No existing running.. providing empty schema')
                pretty = PyConfHoardFilter()
                filtered = pretty.convert(self.datastore.db, config=True, filter_blank_values=False)

                cfgdata = open('%s/running/%s.pch' % (datastore, self._appname), 'w')
                cfgdata.write(json.dumps(filtered, indent=4))
                opdata.close()

        if hasattr(self, 'setup') and callable(self.setup):
            self.log.info('PyConfHoard Setup %s' % (self))
            self.setup()

        self.log.info('PyConfHoard Started %s' % (self))

    def get_config(self, path):
        """
        This method takes in an XPATH(like?) expresion and returns data objects.
        """
        val = self.datastore.get(self._ourpath + path, separator='/')
        self.log.debug('GET: %s <= %s', path, val)
        return val

    def register(self):
        self.log.info("Registering module")
        metadata = {
            'appname': self._appname,
            'yangmodule': self._ourmodule,
            'yangpath': self._ourpath,
        }

        o = open('../../datastore/registered/%s.pch' % (self._appname), 'w')
        o.write(json.dumps(metadata))
        o.close()

    def __del__(self):
        self.log.info('PyConfHoard Finished: %s' % (self))
