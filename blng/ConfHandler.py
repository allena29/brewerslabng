import json
import os
import shutil
import time
import pyangbinding
import pyangbind.lib.pybindJSON as pb_json
# TODO: ideally this isn't hardcoded
from pyangbinding import brewerslab


class ConfigHandlerError(Exception):

    def __init__(self, message):
        super().__init__(message)


class ConfigHandler:

    YANG_MODULE = "brewerslab"
    LOCK_WAIT_TIME = 0.0251
    LOCK_WAIT = 10
    LOCK_WRITE_WAIT = 50

    """
    This class handles reading/writing configuration into python representations, using
    pyangbind - a very basic locking mechanism is provided to manage reading/writing.

    This explicitly hardcodes the pyangbindings dues to the import and the YANG_MODULE,
    however it should be possible to dynamically import things.

    """

    def __init__(self, sub_module):
        """
        Create a new sub-datatsore which can be access via python.

        E.g.

        conf_subdatastore = ConfHandler('sub-part-of-yang-module')
        cfg = conf_datatsore.new()
        cfg = conf_subdatastore.load()
        cfg.yang_leaf = "ABC"
        conf_subdatastore.write()

        with conf_datatstore as cfg:
            # Now we have a lock on the sub-datiastore
            # IMPORTANT: whenever we use the 'with conf_subdatastore' we will either be given
            # a new object if nothing is saved on disk, or the latest version from the disk.
            cfg.just_a_test = 'abc'
            time.sleep(50)
        # Now we don't have a lock on the sub-datastore
        """

        self.sub_module = sub_module
        self.last_modified = -1
        self.have_lock = False
        self.cfg = None

    def __enter__(self):
        for c in range(self.LOCK_WRITE_WAIT):
            if os.path.exists("cfg/%s.locked" % (self.sub_module)):
                time.sleep(self.LOCK_WAIT_TIME)
                continue
            else:
                with open("cfg/%s.locked" % (self.sub_module), "w") as lock_file:
                    lock_file.flush()

                self.have_lock = True
                if not self.cfg and not os.path.exists("cfg/%s.json" % (self.sub_module)):
                    self.cfg = self.new()
                else:
                    self.cfg = pb_json.load("cfg/%s.json" % (self.sub_module), pyangbinding, self.YANG_MODULE)
                    stat = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime
                    self.last_modified = stat

                return self.cfg
        raise ConfigHandlerError("%s is locked" % (self.sub_module))

    def __exit__(self, a, b, c):
        if os.path.exists("cfg/%s.locked" % (self.sub_module)):
            self.have_lock = False
            os.unlink("cfg/%s.locked" % (self.sub_module))

    def new(self):
        """
        Create a new sub-datastore - but do not persist it to disk.
        """
        self.cfg = brewerslab()

        return self.cfg

    def open(self):
        """
        Open a sub-datastore, unless it's locked and then wait a reasonable time returning
        a pyangbind representation of the datastore.

        Once the configuration has been loaded the lock is removed.
        """
        stat = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime
        if self.last_modified > -1 and self.last_modified == stat:
            return self.cfg

        for c in range(self.LOCK_WAIT):
            if os.path.exists("cfg/%s.locked" % (self.sub_module)):
                time.sleep(self.LOCK_WAIT_TIME)
                continue
            else:
                if not os.path.exists("cfg/%s.json" % (self.sub_module)):
                    raise ConfigHandlerError("%s does not exist" % (self.sub_module))

                stat = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime
                self.cfg = pb_json.load("cfg/%s.json" % (self.sub_module), pyangbinding, self.YANG_MODULE)
                stat2 = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime

                if not stat == stat2:
                    raise ConfigHandlerError("%s changed whilst we were reading it" % (self.sub_module))

                self.last_modified = stat
                return self.cfg

        raise ConfigHandlerError("%s is locked" % (self.sub_module))

    def write(self, block_write_if_changed=True):
        """
        Write configuration to the sub-datastore, unless it's locked and then wait to try hard to
        write the data we have.
        """

        for c in range(self.LOCK_WAIT):
            if not self.have_lock and os.path.exists("cfg/%s.locked" % (self.sub_module)):
                time.sleep(self.LOCK_WAIT_TIME)
                continue
            else:
                if (block_write_if_changed and os.path.exists("cfg/%s.json" % (self.sub_module)) and
                        not os.stat("cfg/%s.json" % (self.sub_module)).st_mtime == self.last_modified):
                    raise ConfigHandlerError("%s changed before we wrote our data" % (self.sub_module))
                with open("cfg/%s.locked" % (self.sub_module), "w") as lock_file:
                    lock_file.flush()

                    with open("cfg/%s.tmp" % (self.sub_module), "w") as temp_file:
                        temp_file.write(pb_json.dumps(self.cfg))

                    if os.path.exists("cfg/%s.old" % (self.sub_module)):
                        os.unlink("cfg/%s.old" % (self.sub_module))

                    if os.path.exists("cfg/%s.json" % (self.sub_module)):
                        shutil.move("cfg/%s.json" % (self.sub_module), "cfg/%s.old" % (self.sub_module))
                    shutil.move("cfg/%s.tmp" % (self.sub_module), "cfg/%s.json" % (self.sub_module))

                stat = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime
                self.last_modified = stat

                if os.path.exists('cfg/%s.locked' % (self.sub_module)):
                    os.unlink("cfg/%s.locked" % (self.sub_module))

                return self.cfg

        raise ConfigHandlerError("%s is locked" % (self.sub_module))

    @staticmethod
    def to_json(cfg_object):
        return json.loads(pb_json.dumps(cfg_object))
