#!/usr/bin/python
import syslog
import sys
import time
import logging


class LogHandler:

    """
    This allow us to send logs to syslog and stderr via logger
    """

    def __init__(self, component):
        self.logging = 3
        self.lastLog = ["", "", "", "", "", "", "", "", "", "", ""]
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.__logger = logging.getLogger(component)

    def debug(self, msg, importance=10):
        self.log(msg, importance)

    def log(self, msg, importance=10):
        if self.logging == 1:
            if importance > 9:
                syslog.syslog(syslog.LOG_DEBUG, msg)
                self.__logger.debug(msg)
        elif self.logging == 2:
            sys.stderr.write("%s\n" % (msg))
        elif self.logging == 3:
            if (importance > 9) or ((("%s" % (time.time())).split(".")[0][-3:] == "000") or (not self.lastLog[importance] == msg)):
                syslog.syslog(syslog.LOG_DEBUG, msg)
                self.lastLog[importance] = msg
            self.__logger.debug(msg)

    def err(self, msg):
        syslog.syslog(syslog.LOG_ERR, msg)
        self.__logger.error(msg)
