#!/usr/bin/python
import syslog
import sys
import time
import logging


class LogHandler:

    """
    This allow us to send logs to syslog and stderr via logger, this carries over
    from the raspberry pi LCD screen logging code - in which case sending messages
    too frequently would overwhelm the I2C bus. Importance was used to drop trivial
    messages if previous messages hadn't finished playing out.

    """

    def __init__(self, component):
        """
        Logging 
            1 = always log to syslog and local logger
            2 = logger only
            3 = auto-reduce logging to syslog but always log to local logger
        """
        self.logging = 3
        self.lastLog = ["", "", "", "", "", "", "", "", "", "", ""]
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.__logger = logging.getLogger(component)

    def info(self, msg, importance=10):
        self.log(msg, importance, syslog_level=syslog.LOG_INFO, logger='info')

    def debug(self, msg, importance=10):
        self.log(msg, importance)

    def log(self, msg, importance=10, syslog_level=syslog.LOG_DEBUG, logger='debug'):
        logger_method = getattr(self.__logger, logger)
        if self.logging == 1:
            if importance > 9:
                syslog.syslog(syslog_level, msg)
                logger_method(msg)
        elif self.logging == 2:
            logger_method(msg)
        elif self.logging == 3:
            if (importance > 9) or ((("%s" % (time.time())).split(".")[0][-3:] == "000") or (not self.lastLog[importance] == msg)):
                syslog.syslog(syslog_level, msg)
                self.lastLog[importance] = msg
            logger_method(msg)

    def error(self, msg):
        self.log(msg, importance=20, syslog_level=syslog.LOG_ERR, logger='error')

    def err(self, msg):
        self.log(msg, importance=20, syslog_level=syslog.LOG_ERR, logger='error')
