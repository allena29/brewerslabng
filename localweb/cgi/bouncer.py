#!/usr/bin/python

import cgi
form =cgi.FieldStorage()
print "Content-Type:text/html\n\n"
print "Reboot in progress... it may take ~ 10 minutes to reboot and associate against wireless access point <b>"
print form['ssid'].value
print "</b><P>"
print "You may want to adjust your router to ensure we receive a fixed IP address, and to enable remote access allow <b>TCP PORT 54661</b> to be forwarded to <b>"
print form['ip'].value
print "</b><P>"
print "Once rebooted if you are connected to the same wireless access point you can access this page by <a href=http://%s:54661/cgi/index.py>http://%s:54661/cgi/index.py</a>" %(form['ip'].value,form['ip'].value)
print "<P>Note: on each reboot we wait 5 minutes before switching to your preferred wireless access point - beforehand you can connect via the aaaBREWERSLAB local access point <a href=http://172.12.12.122:54661/cgi/index.py>http://172.12.12.122:54661/cgi/index.py</a> "
