#!/usr/bin/python

import os
import sys
import time

print "Content-Type: text/xml\n"

if not os.path.exists("/tmp/standalone-temp-active"):
	print "<xml><msg>Monitoring not started</msg><status>1</status></xml>"
	
elif len(os.listdir("/currentdata/lastreading")) == 0:
	print "<xml><msg>No readings gathered</msg><status>1</status></xml>"

else:
	sys.stdout.write("<xml>\n")
	from pitmCfg import *
	cfg=pitmCfg()
	readings=0
	for probe in os.listdir("/currentdata/lastreading"):
		o=open("/currentdata/lastreading/%s" %(probe))
		timeread=os.stat("/currentdata/lastreading/%s" %(probe)).st_mtime
		temp=o.read().rstrip()
		o.close()
		sys.stdout.write(" <reading%s>%s %.3f at %s</reading%s>\n" %(readings,cfg.probeId[ probe ], float(temp), time.ctime( timeread ), readings))
		readings=readings+1
	sys.stdout.write(" <readings>%s</readings>\n" %(readings))
	sys.stdout.write(" <status>0</status>\n")
	sys.stdout.write("</xml>")
