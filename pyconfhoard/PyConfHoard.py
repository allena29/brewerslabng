import inspect
import logging
import json
import os
from pydoc import locate

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
        self.__path_helper = YANGPathHelper()

        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger(appname)
        self.log.info('PyConfHoard Init: %s' % (self))

        # Load schema file - must have been generate by yin2json
        self._yang_obj = None
        for (name, obj) in inspect.getmembers(binding):
            if name == yangmodule:
                self._yang_obj = obj(path_helper=self.__path_helper)

        if not self._yang_obj:
            raise RuntimeError('Unable to find class %s in pyangbinding' % (yangmodule))
        self.log.debug('Found top-level yang module object %s' % (repr(self._yang_obj)))

        self._ourmodule = yangmodule
        # Navigate down
        self._ourpath = yangpath    
        try:
            self._yang = self.__path_helper.get(yangpath)[0]
        except:
            raise RuntimeError('Unable to navigate to %s' % (yangpath))

        self._appname = appname

        if open_stored_config:
            working_directory = os.getcwd()
            datastore = '../../datastore'
            if os.path.exists('%s/persist/%s.pch' % (datastore, self._appname)):
                self.log.info('Loading previous persisted data')
                o = open('%s/persist/%s.pch' % (datastore, self._appname))
                json_str = o.read()
                o.close()
                self._yang = self.loader(self._yang, json_str)
            elif os.path.exists('%s/startup/%s.pch' % (datastore, self._appname)):
                self.log.info('Loading startup default data')
                o = open('%s/startup/%s.pch' % (datastore, self._appname))
                json_str = o.read()
                o.close()
                self._yang = self.loader(self._yang, json_str)

            if not os.path.exists('%s/operational/%s.pch' % (datastore, self._appname)):
                self.log.info('No existing opdata... providing empty schema')
                opdata = open('%s/operational/%s.pch' % (datastore, self._appname), 'w')
                opdata.write(self.dumper(self._yang, opdata=True))
                opdata.close()
            if not os.path.exists('%s/persist/%s.pch' % (datastore, self._appname)):
                self.log.info('No existing persist.. providing empty schema')
                opdata = open('%s/persist/%s.pch' % (datastore, self._appname), 'w')
                opdata.write(self.dumper(self._yang, opdata=False))
                opdata.close()


        if hasattr(self, 'setup') and callable(self.setup):
            self.log.info('PyConfHoard Setup %s' % (self))
            self.setup()

        self.log.info('PyConfHoard Started %s' % (self))

    @staticmethod
    def dumper(yang, opdata=False, pretty=False):
        """        
        This method stores the in-memory object structure as an IETF JSON object.
        All config based nodes are dumped, but op-data is not.

        The yang object must be provided to this method.

        This makes use of a customised version of pyangbind distributed as part
        of this repository.
        """

        if opdata:
            ignore_opdata = False
            ignore_conf_leaves = True
        else:
            ignore_opdata = True
            ignore_conf_leaves = False

        obj = json.loads(pybindJSON.dumps(yang, filter=False, ignore_opdata=ignore_opdata,
                                                  ignore_conf_leaves=ignore_conf_leaves, mode='ietf'))
        if pretty:
            return json.dumps(obj, indent=4, sort_keys=True)
        else:
            return json.dumps(obj)


    @staticmethod
    def loader(yang, json_str):
        """
        This method loads a IETF Json string representing the in-memory object structure
        and replaces the in-memory data.
        """

        try:
            json_obj = json.loads(json_str)
        except ValueError as err:
            raise ValueError('Invalid JSON payload provided\n' + err.message)
        return pybindJSONDecoder.load_ietf_json(json_obj, None, None, yang)

    def get_config(self, path):
        """
        This method takes in an XPATH(like?) expresion and returns data objects.
        """
        self.log.debug('GET: %s => %s' % (path, self.__path_helper.get('%s%s' % (self._ourpath, path))))
        return self.__path_helper.get('%s%s' % (self._ourpath, path))

    def register(self):
        self.log.info("Registering module")
        metadata = {
            'appname': self._appname,
            'yangmodule': self._ourmodule,
            'yangpath': self._ourpath,
        }

        o = open ('../../datastore/registered/%s.pch' % (self._appname), 'w')
        o.write(json.dumps(metadata))
        o.close()

    def __del__(self):
        self.log.info('PyConfHoard Finished: %s' % (self))
