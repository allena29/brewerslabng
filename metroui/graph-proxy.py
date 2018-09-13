#!/usr/bin/python
import time
import sys
import urllib
import os

if os.path.exists("../websocket/mode"):
	mode=open("../websocket/mode").read()
	if mode.count("ferm"):
		sys.stdout.write("Refresh: 660;url=graph-proxy.py?%s\n" %(time.time()))
sys.stdout.write("Content-Type: image/png\n\n")

f=urllib.urlopen("http://192.168.1.15:54661/cgi/graph.py")
sys.stdout.write(f.read())
