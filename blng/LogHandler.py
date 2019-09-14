#!/usr/bin/python
import syslog
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
        self.lastLog = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=99, format=FORMAT)
        self.__logger = logging.getLogger(component)
        self.__logger.setLevel(logging.DEBUG)

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
        self.log(msg, importance=11, syslog_level=syslog.LOG_ERR, logger='error')

    def err(self, msg):
        self.log(msg, importance=11, syslog_level=syslog.LOG_ERR, logger='error')


class LogWrap():

    ENABLED = False
    ENABLED_INFO = True
    ENABLED_DEBUG = True

    ENABLED_REMOTE = False
    REMOTE_LOG_IP = "127.0.0.1"
    REMOTE_LOG_PORT = 6666

    def __init__(self, component, enable_terminal=False, enable_remote=False):
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger(component)
        self.ENABLED = enable_terminal
        self.ENABLED_REMOTE = enable_remote

        if self.ENABLED_REMOTE:
            self.log_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = self._pad_truncate_to_size("STARTED ("+str(time.time())+"):")
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    @staticmethod
    def _args_wildcard_to_printf(*args):
        if isinstance(args, tuple):
            # (('Using cli startup to do %s', 'O:configure'),)
            args = list(args[0])
            if len(args) == 0:
                return ''
            message = args.pop(0)
            if len(args) == 0:
                pass
            if len(args) == 1:
                message = message % (args[0])
            else:
                message = message % tuple(args)
        else:
            message = args
        return (message)

    def _pad_truncate_to_size(self, message, size=1024):
        if len(message) < size:
            message = message + ' '*(1024-len(message))
        elif len(message) > 1024:
            message = message[:1024]
        return message.encode()

    def info(self, *args):
        if self.ENABLED and self.ENABLED_INFO:
            self.log.info(args)
        if self.ENABLED_REMOTE and self.ENABLED_INFO:
            print('a')
            message = 'INFO ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    def error(self, *args):
        if self.ENABLED:
            self.log.error(args)
        if self.ENABLED_REMOTE:
            message = 'INFO ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))

    def debug(self, *args):
        if self.ENABLED and self.ENABLED_DEBUG:
            self.log.debug(args)

        if self.ENABLED_REMOTE and self.ENABLED_DEBUG:
            message = 'DEBUG ' + LogWrap._args_wildcard_to_printf(args)
            message = self._pad_truncate_to_size('INFO: %s %s' % (str(time.time()), message))
            self.log_socket.sendto(message, (self.REMOTE_LOG_IP, self.REMOTE_LOG_PORT))
