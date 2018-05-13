import logging
import json
import os
from PyConfHoardDatastore import PyConfHoardDatastore
from PyConfHoardFilter import PyConfHoardFilter


class Thing:

    LOG_LEVEL = 3
    APPNAME = None
    PATHPREFIX = None

    def __init__(self, open_stored_config=True):
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
        self.datastore = PyConfHoardDatastore()
        self.datastore.load_blank_schema('../../yang/schema.json')

        self.log.info('PyConfHoard Load Default Schema: OK')
        self.log.info('PyConfHoard Filtered Datastore: %s', self.PATHPREFIX)

        if open_stored_config:
            print (
                   "Overwrite")
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
                self.datastore._merge_direct_to_root(json.loads(json_str))
                o = open('%s/running/%s.pch' % (datastore, self.APPNAME), 'w')
                o.write(json.dumps(self.datastore.db_values, indent=4))
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
                pretty = PyConfHoardFilter(self.datastore.db, self.datastore.db_values)
                pretty.convert(config=False, filter_blank_values=False)
                filtered = pretty.root

                opdata = open('%s/operational/%s.pch' % (datastore, self.APPNAME), 'w')
                opdata.write(json.dumps(filtered, indent=4))
                opdata.close()

            if not os.path.exists('%s/running/%s.pch' % (datastore, self.APPNAME)):
                self.log.info('No existing running.. providing empty schema')
                pretty = PyConfHoardFilter(self.datastore.db, self.datastore.db_values)
                pretty.convert(config=True, filter_blank_values=False)
                filtered = pretty.root

                cfgdata = open('%s/running/%s.pch' % (datastore, self.APPNAME), 'w')
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
