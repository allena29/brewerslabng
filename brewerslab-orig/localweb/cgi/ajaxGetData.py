#!/usr/bin/python

import os
import time

print "Content-Type: text/xml\n"

o=open("../ipc/fermTarget")
fermTarget=o.read().rstrip()
o.close()

if os.path.exists("../ipc/disable-fermcool"):
	fermCoolDisabled=1
else:
	fermCoolDisabled=0

if os.path.exists("../ipc/disable-ferm-heat"):
	fermHeatDisabled=1
else:
	fermHeatDisabled=0


if os.path.exists("../ipc/hlt-delay-until"):
	o=open("../ipc/hlt-delay-until")
	hltdelay=o.read().rstrip()
	o.close()
	(hltDelayY,hltDelayM,hltDelayD,hltDelayh,hltDelaym,hltDelays,a,b,c)=time.localtime( float(hltdelay) )
	hltDelayy=1
else:
	hltDelayY=2016
	hltDelayM=11
	hltDelayD=18
	hltDelayh=21
	hltDelaym=13
	hltDelayy=0 
print "<xml>"
print "<fermTarget>%s</fermTarget>" %(fermTarget)
print "<fermCoolDisabled>%s</fermCoolDisabled>" %(fermCoolDisabled)
print "<fermHeatDisabled>%s</fermHeatDisabled>" %(fermHeatDisabled)
print "<hltdelayY>%s</hltdelayY>" %(hltDelayY)
print "<hltdelayM>%s</hltdelayM>" %(hltDelayM)
print "<hltdelayD>%s</hltdelayD>" %(hltDelayD)
print "<hltdelaym>%s</hltdelaym>" %(hltDelaym)
print "<hltdelayh>%s</hltdelayh>" %(hltDelayh)
print "<hltdelayy>%s</hltdelayy>" %(hltDelayy)
print "</xml>"

