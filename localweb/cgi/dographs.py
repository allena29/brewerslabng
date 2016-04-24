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
	if form.has_key("baseTime"):
		baseTime=form['baseTime'].value
		sys.stderr.write("basetime%s" %(baseTime))
		for x in os.listdir("archivedata"):
			if x.count(baseTime):
				try:
					os.remove("archivedata/%s" %(x))
				except:	
					pass
except:
	print "<<<<<<<<<<<<<<<<< ERROR >>>>>>>>>>>>>>>>>>>>>>>>>"
	sys.exit(0)


print "<xml><status>0</status></xml>"
