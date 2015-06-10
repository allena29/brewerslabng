#!/usr/bin/python
import json
import os
import time
import cgi

print "Content-Type: text/plain\n"


form=cgi.FieldStorage()

result={}


if form.has_key("adjustFermTarget"):
	o=open("../ipc/adjustFermTarget","w")
	o.write("%s" %(float(form['adjustFermTarget'].value)))
	o.close()

	result['adjustFermTarget']=form['adjustFermTarget'].value


print json.dumps(result)
