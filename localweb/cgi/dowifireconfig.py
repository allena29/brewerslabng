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
		if not form.has_key("cidr") or not form.has_key("gw"):
			print "<xml><status>65</status><msg>missing IP details</msg></xml>"
		else:
			cidr=form['cidr'].value
			gw=form['gw'].value


if len(ssid) < 2 or len(psk) < 2:
	print "<xml><status>67</status><msg>missing details wep or psk not long enough</msg></xml>"

else:
	print "<xml><status>1</status><msg>waiting for wifi to be reconfigured</msg></xml>"
	os.system("sudo python /home/beer/brewerslab/bootcfg.py ssid \"%s\"" %(ssid))
	os.system("sudo python /home/beer/brewerslab/bootcfg.py psk \"%s\"" %(psk))
	if ip:
		os.system("sudo python /home/beer/brewerslab/bootcfg.py ip \"%s\"" %(ip))
		os.system("sudo python /home/beer/brewerslab/bootcfg.py cidr \"%s\"" %(cidr))
		os.system("sudo python /home/beer/brewerslab/bootcfg.py gw \"%s\"" %(gw))

	os.system("sudo sh /home/beer/brewerslab/rebootIn15.sh reboot")

