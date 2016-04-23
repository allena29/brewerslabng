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
	print "<<<<<<<<<<<<<<<<< NOT AUTH >>>>>>>>>>>>>>>>>>>>>>>>>"
	sys.exit(0)

try:
	d=form['date'].value.split(".")
	os.system("""sudo date -s "%s-%s-%s %s:%s" """ %(d[0],d[1],d[2],form['hour'].value,form['minutes'].value))
except:
	print "<<<<<<<<<<<<<<<<< NOT AUTH >>>>>>>>>>>>>>>>>>>>>>>>>"
	sys.exit(0)


print "<xml><status>0</status></xml>"
