#!/usr/bin/python
import json
import os
import time
import cgi

print "Content-Type: text/plain\n"

updated=False
hltMode=False
if os.path.exists("../ipc/swHlt") or os.path.exists("../ipc/manualswitch_swHlt"):
	hltMode=True

delayUntil=0
if os.path.exists("../ipc/hlt-delay-until"):
	try:
		delayUntil=int(open("../ipc/hlt-delay-until").read())
	except:
		pass
form=cgi.FieldStorage()
if form.has_key("delay"):
	updated=True
	try:
		delayUntil=int(form['delay'].value)
		o=open("../ipc/hlt-delay-until","w")
		o.write("%s" %(int(delayUntil)))
		o.close()
	except:
		updated=False
result={'hlt':hltMode,'delayUntil':[delayUntil,time.ctime(delayUntil)] ,'updateValid':updated}

print json.dumps(result)
