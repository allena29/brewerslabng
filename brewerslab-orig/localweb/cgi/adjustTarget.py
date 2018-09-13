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


if form.has_key("disableCooling"):
	o=open("../ipc/disable-fermcool","w")
	o.close()
	result['cooling']="disabled"
else:
	try:
		os.unlink("../ipc/disable-fermcool")
	except:
		pass
	result['cooling']="enabled"


if form.has_key("disableHeting"):
	o=open("../ipc/disable-ferm-heat","w")
	o.close()
	result['heating']="disabled"
else:
	try:	
		os.unlink("../ipc/disable-ferm-heat")
	except:
		pass
	result['heating']="enabled"

print json.dumps(result)
