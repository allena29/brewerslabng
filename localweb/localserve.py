#!/usr/bin/python

import sys
import os
import time
from threading import Thread
import BaseHTTPServer
import CGIHTTPServer
import SocketServer
import BaseHTTPServer
import SimpleHTTPServer

class ThreadingSimpleServer(SocketServer.ThreadingMixIn,
		   BaseHTTPServer.HTTPServer):
    pass

import sys


os.chdir("localweb")
handler = CGIHTTPServer.CGIHTTPRequestHandler
server = ThreadingSimpleServer(('', 54661), handler)

# on win32 we are testing just against the directory  for if allowed or not
# on python 2.6 (linux) we seemed to be testing the whole path
# CGIHTTPServerAAA is an adapation which works for win32.
handler.cgi_directories = ["/cgi"]
#
#/vsdwba/ofp/prod/merged"]
#handler.cgi_directories = ["/vsdwba/"]
#ofp/prod/merged/","/vsdwba/prod/merged/"]

try:
    while 1:
	sys.stdout.flush()
	server.handle_request()
except KeyboardInterrupt:
    print "Finished"
