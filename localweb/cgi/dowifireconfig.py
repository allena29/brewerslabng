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

ip=None
mask=None
gw=None
if form.has_key("ip"):
	ip=form['ip'].value
	if ip == "0.0.0.0":	
		ip=None
	else:
		if not form.has_key("mask") or not form.has_key("gw"):
			print "<xml><status>65</status><msg>missing IP details</msg></xml>"
		else:
			mask=form['mask'].value
			gw=form['gw'].value


if form.has_key("startReconfig"):
	if form['startReconfig'].value =="true":
		restartConfig=True

if len(ssid) < 2 or len(psk) < 2:
	print "<xml><status>67</status><msg>missing details wep or psk not long enough</msg></xml>"

else:
	print "<xml><status>1</status><msg>waiting for wifi to be reconfigured</msg></xml>"
	os.system("sudo echo \"%s\" >/boot/wifissid.txt" %(ssid))
	os.system("sudo echo \"%s\" >/boot/wifipsk.txt" %(psk))
	if ip:
		os.system("sudo echo \"%s\" >/boot/wifiip.txt" %(ip))
		os.system("sudo echo \"%s\" >/boot/wifimask.txt" %(mask))
		os.system("sudo echo \"%s\" >/boot/wifigw.txt" %(gw))

	os.system("sudo sh /home/beer/brewerslab/test-wireless.sh %s %s" %(ssid,psk))

