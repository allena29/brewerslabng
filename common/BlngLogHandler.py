#!/usr/bin/python
import syslog
import sys
import time


class BlngLogHandler:

    """
    This allow us to send logs to syslog and stdout
    """
    
    def __init__(self):
        self.logging =3
        self.lastLog = ["", "", "", "", "", "", "", "", "", "", ""]    

    def log(self, msg, importance=10):
        if self.logging == 1:
            if importance > 9:
                syslog.syslog(syslog.LOG_DEBUG, msg)
        elif self.logging == 2:
            sys.stderr.write("%s\n" % (msg))
        elif self.logging == 3:
            if (importance > 9) or ((("%s" % (time.time())).split(".")[0][-3:] == "000") or (not self.lastLog[importance] == msg)):
                syslog.syslog(syslog.LOG_DEBUG, msg)
                self.lastLog[importance] = msg
            sys.stderr.write("%s\n" % (msg))

    def err(self, msg):
        syslog.syslog(syslog.LOG_ERR, msg)
        sys.stderr.write("%s\n" % (msg))

