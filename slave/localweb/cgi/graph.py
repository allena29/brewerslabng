#!/usr/bin/python

import sys
import os

graphPngs=[]
for x in os.listdir("currentdata"):
	if x.count("ferm") and x.count(".png"):
		graphPngs.append(x)

sys.stdout.write( "Content-Type: image/png\n\n")
if len(x) == 0:
	o=open("nograph.png")
else:
	o=open("currentdata/%s" %(graphPngs[-1]))
sys.stdout.write(o.read())
o.close()
