#!/usr/bin/python
import os

print "Refresh: 120; log.py"
print "Content-Type: text/html"
print ""
print "<tt><div id='log' style='height: 800px; overflow-y:scroll; overflow-x: hidden;'>"
print "<font size=2>"
o=open("/var/log/beer/pitm.py").read().split("\n")

x=len(o)
x=x-150
if x < 0:	x=0

for i in range(150):
	msg=o[i+x].split(".py:")
	if len(msg) == 2:
		print "<b>%s</b><br>&nbsp;&nbsp;&nbsp;%s<BR>" %(msg[0],msg[1])

print "</div>"
print "<script language=Javascript>"
print """obj=document.getElementById("log");"""
print """obj.scrollTop=obj.scrollHeight;"""
print "</script>"

