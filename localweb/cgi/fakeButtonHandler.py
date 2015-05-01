#!/usr/bin/python
import os
import cgi
import sys
form=cgi.FieldStorage()

print "Content-Type: text/html\n\n"
print 
print form["button"].value

x=form['button'].value



# Volume
allowed={'mashFillVol':True,'boilFillVol':True,'fermFillVol':True,'hltFillVol':True,'spargeFillVol':True,'spargeEmptyVol':True,
	'mashEmptyVol':True,'boilEmptyVol':True,'fermEmptyVol':True,'hltEmptyVol':True,}

if allowed.has_key(x):
	o=open("../ipc/%s" %(x),"w")
	o.close()


# Temperature
#r91 01 4b 46 7f ff 0f 10 25 : crc=25 YES
#91 01 4b 46 7f ff 0f 10 25 t=25062
#SetTemp
allowed={'mashSetTemp' : True,'boilSetTemp':True,'fermSetTemp':True,'hltSetTemp':True}
if allowed.has_key(x):
	o=open("../ipc/fakeelement_%s" %(x),"w")
	o.write( form['onoff'].value )
	o.close()

	sys.exit(0)
	tmp="%s" %(form['onoff'].value)
	if tmp.count(".") < 1:
		tmp2 = "000"
	else:
		tmp2 = "%s0000 " %(tmp.split(".")[1])
	tmp="000%s" %(form['onoff'].value.split(".")[0])
	
	temp="%s%s" %(tmp[-3:],tmp2[0:3])
	from pitmCfg import *
	cfg=pitmCfg()

	probeid=None
	if x == "hltSetTemp":
		probeid=cfg.hltProbe
	if x == "mashSetTemp":
		probeid=cfg.mashAProbe
	if x == "boilSetTemp":
		probeid=cfg.boilProbe
	if x == "fermSetTemp":
		probeid=cfg.fermProbe

	if probeid:
		sys.stderr.write("%s\n" %(cfg))
		try:
			os.mkdir("../ipc/fake1wire/%s/" %(probeid))
		except:
			pass
		o=open("../ipc/fake1wire/%s/w1_slave" %(probeid),"w")
		o.write("ff ff ff ff ff ff ff ff ff : crc=25 YES\n")
		o.write("ff ff ff ff ff ff ff ff ff t=%s\n" %(temp))
		o.close()

	if x == "mashSetTemp":
		probeid=cfg.mashBProbe
		sys.stderr.write("%s\n" %(cfg))
		try:
			os.mkdir("../ipc/fake1wire/%s/" %(probeid))
		except:
			pass
		o=open("../ipc/fake1wire/%s/w1_slave" %(probeid),"w")
		o.write("ff ff ff ff ff ff ff ff ff : crc=25 YES\n")
		o.write("ff ff ff ff ff ff ff ff ff t=%s\n" %(temp))
		o.close()


# Switches
allowed={'swHlt':True,'swMash':True,'swSparge':True,'swBoil':True,'swFerm':True,'swPump':True}
sys.stderr.write("switches %s\n" %(x))
if allowed.has_key(x):
	if form['onoff'].value == "on":
		sys.stderr.write("adding %s  ../ipc/manualswitch_%s\n" %(os.getcwd(),x))
		o=open("../ipc/manualswitch_%s" %(x),"w")
		o.close()
	else:
		try:
			sys.stderr.write("removing ipc/manualswitch_%s\n" %(x))
			os.remove("../ipc/manualswitch_%s" %(x))
		except:
			pass

# Push Buttons
allowed={'pRotaryA':True,'pRotaryB':True,'pOk':True,'pLeft':True,'pDown':True,'pRight':True}
if allowed.has_key(x):
	for y in allowed:
		try:
			os.remove("../ipc/manual_%s" %(y))
		except:
			pass
	o=open("../ipc/manual_%s" %(form['button'].value),"w")
	o.close()
