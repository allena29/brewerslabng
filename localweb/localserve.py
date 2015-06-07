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

handler.cgi_directories = ["/cgi"]

try:
    while 1:
	sys.stdout.flush()
	server.handle_request()
except KeyboardInterrupt:
    print "Finished"
