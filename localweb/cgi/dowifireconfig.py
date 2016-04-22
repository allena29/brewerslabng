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

ssid=""
psk=""
restartConfig=False
if not auth:
	print "<xml><status>66</status><msg>wrong admin password</msg></xml>"
	sys.exit(0)
elif not form.has_key("ssid") or not form.has_key("wep"):
	print "<xml><status>65</status><msg>missing details</msg></xml>"
	sys.exit(0)
else:
	ssid=form['ssid'].value
	psk=form['wep'].value

if form.has_key("keepDetails"):
	o=open("wifistate/.__GLOBAL__","w")
	o.write("%s:%s:"% (ssid,psk))
	o.close()
	print "<xml><status>0</status></xml>"
	os.system("sudo sh /home/beer/brewerslab/rebootIn15.sh &")
	sys.exit(0)


if form.has_key("startReconfig"):
	if form['startReconfig'].value =="true":
		restartConfig=True

if len(ssid) < 2 or len(psk) < 2:
	print "<xml><status>67</status><msg>missing details wep or psk not long enough</msg></xml>"

elif not os.path.exists("wifistate/%s" %(ssid)) or restartConfig:
	print "<xml><status>1</status><msg>waiting for wifi to be reconfigured</msg></xml>"
#	sys.stderr.write("sudo sh /home/beer/brewerslab/test-wireless.sh %s %s" %(ssid,psk))
	os.system("sudo sh /home/beer/brewerslab/test-wireless.sh %s %s" %(ssid,psk))
else:
	status=open("wifistate/%s" %(ssid)).read().rstrip()
	if status == "TRYING":
		print "<xml><status>2</status><msg>WIFI Reconfigured - Trying to obtain ip address</msg></xml>"
	elif status == "SUCCESS":
		print "<xml><status>0</status><msg>WIFI OK</msg><ip>%s</ip></xml>" %(open("wifistate/%s.ip" %(ssid)).read().rstrip() ) 
	else:
		print "<xml><status>69</status><msg>UNKNOWN STATE: %s</msg></xml>" %(status)

