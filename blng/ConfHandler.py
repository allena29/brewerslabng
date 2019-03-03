import json
import os
import shutil
import time
import pyangbinding
import pyangbind.lib.pybindJSON as pb_json
# TODO: make this less hadcoded
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

        conf_datastore = ConfHandler('sub-part-of-yang-module')
        cfg = conf_datatsore.new()
        cfg = conf_datastore.load()
        cfg.yang_leaf = "ABC"
        conf_datastore.write()

        with conf_datatstore as cfg:
            # Now we have a lock on the sub-datiastore
            # IMPORTANT: whenever we use the 'with conf_datastore' we will either be given
            # a new object if nothing is saved on disk, or the latest version from the disk.
            cfg.just_a_test = 'abc'
            time.sleep(50)
        # Now we don't have a lock on the sub-datastore
        """

        self.sub_module = sub_module
        self.last_modified = -1
        self.have_lock = False
        self.cfg = None

    def exists(self):
        if os.path.exists('cfg/%s.json' % (self.sub_module)):
            return True
        return False

    def status(self):
        if self._is_locked():
            with open("cfg/%s.locked" % (self.sub_module)) as lock:
                lock_info = lock.read()
            print("Datastore locked: %s" % (lock_info))
        else:
            print("Datstore unlocked")

        if self.exists():
            status = os.stat("cfg/%s.json" % (self.sub_module))
            print("Datstore size: %s modified: %s" % (status.st_size, time.ctime(status.st_mtime)))
        else:
            print("Datastore does not exist")

    def _is_locked(self, wait_time=0, wait=1, throw_exception=False):
        for c in range(wait):
            if os.path.exists("cfg/%s.locked" % (self.sub_module)):
                time.sleep(wait_time)
                continue
            else:
                return False

        if throw_exception:
            raise ConfigHandlerError("%s is locked" % (self.sub_module))

        return True

    def get_lock(self, wait_time=0.0025, wait=5):
        self._is_locked(wait_time, wait, True)

        with open("cfg/%s.locked" % (self.sub_module), "w") as lock_file:
            lock_file.write("Locked by %s at %s" % (str(self), time.ctime()))
            lock_file.flush()
        self.have_lock = True
        return True

    def discard_lock(self):
        if self._is_locked():
            os.unlink("cfg/%s.locked" % (self.sub_module))
        self.have_lock = False

    def __enter__(self):
        self.get_lock(self.LOCK_WAIT_TIME, self.LOCK_WRITE_WAIT)

        if not self.cfg and not os.path.exists("cfg/%s.json" % (self.sub_module)):
            self.cfg = self.new()
        else:
            self.cfg = pb_json.load("cfg/%s.json" % (self.sub_module), pyangbinding, self.YANG_MODULE)
            stat = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime
            self.last_modified = stat

        return self

    def __exit__(self, a, b, c):
        self.discard_lock()

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

        self._is_locked(wait_time=self.LOCK_WAIT_TIME, wait=self.LOCK_WAIT, throw_exception=True)

        if not self.exists():
            raise ConfigHandlerError("%s does not exist" % (self.sub_module))

        stat = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime
        self.cfg = pb_json.load("cfg/%s.json" % (self.sub_module), pyangbinding, self.YANG_MODULE)
        stat2 = os.stat("cfg/%s.json" % (self.sub_module)).st_mtime

        if not stat == stat2:
            raise ConfigHandlerError("%s changed whilst we were reading it" % (self.sub_module))

        self.last_modified = stat
        return self.cfg

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

    @staticmethod
    def print(cfg_object):
        print(json.dumps(json.loads(pb_json.dumps(cfg_object)), indent=4))
