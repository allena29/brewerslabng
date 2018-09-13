#!/usr/bin/python

print "Content-Type:text/xml\n"
import sys
import os
import cgi

form=cgi.FieldStorage()

auth=False
if form.has_key("adminpass"):
	if form['adminpass'].value  == "brewerslabaaa123":
		auth=True

if not auth:
	print "<xml><status>66</status><msg>wrong admin password</msg></xml>"
	sys.exit(0)

if form.has_key("reboot"):
	print "<xml><status>0</status></xml>"
	os.system("sudo sh /home/beer/brewerslab/rebootIn15.sh &")
	sys.exit(0)

if form.has_key("poweroff"):
	print "<xml><status>0</status></xml>"
	os.system("sudo sh /home/beer/brewerslab/rebootIn15.sh poweroff &")
	sys.exit(0)
