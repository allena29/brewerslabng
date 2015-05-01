#!/usr/bin/python
import pickle
import cgi
import time
import os
import sys
import json
import re
#import mysql.connector
#from cloudNG import *

probeLabel="Probe"
probeMin=0
probeMax=1000
activities = {
	'Mash' : {'min':65,'max':69,'lowalarm':True,'highalarm':True,'sleep':False},
	'Fermentation':{'min':18,'max':21,'lowalarm':False,'highalarm':False,'sleep':True},
	'HLT' : {'min' : 80, 'max':87,'lowalarm':False,'highalarm':True,'sleep':False},
	'Boiler' : {'min' : 99,'max':101,'lowalarm':False,'highalarm':True,'sleep':False},
	}

probesx = {
	# TODO: remove the min/max/alarm from the probes
	'28-000004722947' : {'shortlabel':'A','label' : 'ProbeA', 'activity' : 'Mash'}, 
	'28-000004714ca7' : {'shortlabel':'B','label' : 'ProbeB','activity' : 'Mash'},
	'28-0000045007de' : {'shortlabel':'A','label' : 'ProbeA','activity' :'Fermentation'},
	'28-0000044fb99d' : {'shortlabel':'A','label' : 'ProbeA','activity' : 'Boiler'},
	'28-0000044dcda4' : {'shortlabel':'A','label' : 'ProbeA','activity' :'HLT'},
	}


#y=sys.stdin.readline().split(",")
#x = #sys.stdin.read()
#con=mysql.connector.connect(user='root',database="brewerslab")
#sys.stdout.write("Content-Type:text/plain\n\n")
sys.stdout.write("Content-Type:text/xml\n\n")
form=cgi.FieldStorage()

def xmlsafe(text):
	text=re.compile("[\n\r]").sub("</br>",text)
	safe=re.compile("<").sub("{:leftbracket:}",  re.compile(">").sub("{:rightbracket:}",  re.compile("&").sub("{:ampersand:}", re.compile("/").sub("{:forwardslash:}", text ) )  ) )
	return text

if form.has_key("tempMonitor"):
	if form['tempMonitor'].value == "shutdown":
		sys.stderr.write("Halting temperature monitoring... or attempting to anyway")
		os.system("ssh -lallena29 192.168.1.14 \"touch /tmp/dbg_button3\" >/dev/null 2>/dev/null")


		try:
			os.unlink("/tmp/tempactive")
		except:
			pass
		try:
			os.unlink("/tmp/tempresult")
		except:
			pass

tempOnline=False
x=os.system("ping -w 1 -c 1 192.168.1.14 2>/dev/null >/dev/null")
if x == 0:
	tempOnline=True
	if form.has_key("tempMonitor"):
		if form['tempMonitor'].value == "start":
			sys.stderr.write("Starting temperature monitoring... or attempting to anyway")
			o=open("/tmp/tempactive","w")
			o.close()
			
			os.system("ssh -lallena29 192.168.1.14 \"touch /tmp/dbg_button\" >/dev/null 2>/dev/null")

if x > 0:	
	try:
		os.unlink("/tmp/tempactive")
	except:
		pass


	try:
		os.unlink("/tmp/tempresult")
	except:
		pass

tempActive=False
if os.path.exists("/tmp/tempactive"):	tempActive=True


if not os.path.exists("/tmp/tempresult") and os.path.exists("/tmp/tempactive"):
	a=	os.stat("/tmp/tempactive").st_mtime
	sys.stderr.write("tempactive was set at %s/%s\n" %(time.ctime(a),a))
	if (time.time() - a) > 10:
		try:
			os.unlink("/tmp/tempactive")
		except:
			pass
		tempActive=False

sys.stdout.write("<xml>\n")
sys.stdout.write("<tempActive>%s</tempActive>\n" %(tempActive))
sys.stdout.write("<tempOnline>%s</tempOnline>\n" %(tempOnline))

probes=0
if tempActive:
	o=open("/tmp/tempresult")
	d=pickle.loads(o.read())
	o.close()
	i=0
	for x in d['currentResult']:
		if not d['currentResult'][x]['valid']:
			sys.stdout.write("<probe%s>%s</probe%s>\n" %(i, "-",i))
		else:
			sys.stdout.write("<probe%s>%s</probe%s>\n" %(i, d['currentResult'][x]['temperature'],i))
		i=i+1

		if probesx.has_key(x):
			probeLabel=probesx[x]['activity']
		if activities.has_key( probeLabel ):
			probeMin=activities[ probeLabel ]['min']
			probeMax=activities[ probeLabel ]['max']

	probes=len(d['currentResult'])
	
	sys.stdout.write("<probeTimestamp>%s</probeTimestamp>\n" %( time.ctime( os.stat("/tmp/tempresult").st_mtime)))

sys.stdout.write("<probeLabel>%s</probeLabel>\n" %(probeLabel))
sys.stdout.write("<probeMin>%s</probeMin>\n" %(probeMin))
sys.stdout.write("<probeMax>%s</probeMax>\n" %(probeMax))
sys.stdout.write("<probes>%s</probes>\n" %(probes))
if os.path.exists("timer-expire"):
	sys.stdout.write("<timerActive>True</timerActive>\n")
	sys.stdout.write("<serverTime>%.0f</serverTime>\n" %(time.time()))
	sys.stdout.write("<startTime>%.0f</startTime>\n" %( os.stat("timer-expire").st_ctime ))
	sys.stdout.write("<startStamp>%s</startStamp>\n" %( time.ctime(os.stat("timer-expire").st_ctime )))
	expire= open("timer-expire").read() 
	sys.stdout.write("<expireTime>%s</expireTime>\n" %(  expire.split(".")[0] ))
	sys.stdout.write("<expireStamp>%s</expireStamp>\n" %(  time.ctime(float(expire))))
else:
	sys.stdout.write("<timerActive>False</timerActive>\n")
sys.stdout.write("</xml>\n")

