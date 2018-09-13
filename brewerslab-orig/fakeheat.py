#!/usr/bin/python
import os
import sys
import time

print "starting fake heater"

tempc={'hltSetTemp': False,'mashSetTemp':False,'boilSetTemp':False,'fermSetTemp':False}
tempx={'hltSetTemp': 0,'mashSetTemp':0,'boilSetTemp':0,'fermSetTemp':19.2}

def handleTemp(probeId):
	global tempx
	if os.path.exists("ipc/fakeelement_%s" %(probeId)):
		o=open("ipc/fakeelement_%s" %(probeId))
		settemp=float(o.read())
		o.close()
		if not tempx[ probeId ] == settemp:
			tempc[probeId]=True
			tempx[probeId]=settemp
		try:
			a=1
			os.unlink("ipc/fakeelement_%s" %(probeId))
		except:
			pass	
		
		print "setting %s to %s " %(probeId,settemp)


def convertTemp(probe,probeid,settemp):
	global tempc
	settemp="%s" %(settemp)
	tmp="%s" %( settemp )
	print probeid,tmp
	if tmp.count(".") < 1:
		tmp2 = "000"
	else:
		tmp2 = "%s0000 " %(tmp.split(".")[1])
	tmp="000%s" %( settemp.split(".")[0])

	if settemp < 100:
		temp="%s%s" %(tmp[-1:],tmp2[0:3])
	else:
		temp="%s%s" %(tmp[-2:],tmp2[0:3])

	print tempc[probe]
	if tempc[probe]:
		try:
			os.mkdir("ipc/fake1wire/%s/" %(probeid))
		except:
			pass
		o=open("ipc/fake1wire/%s/w1_slave" %(probeid),"w")
		o.write("ff ff ff ff ff ff ff ff ff : crc=25 YES\n")
		print " writing probe id %s --> %s\n" %(probeid,temp)
		o.write("ff ff ff ff ff ff ff ff ff t=%s\n" %(temp))
		o.close()
	return temp

while 1:

	# handle temp reads in ipc files to see if we have been given an override from the gui
	handleTemp("hltSetTemp")
	handleTemp("hltSetTemp")
	handleTemp("mashSetTemp")
	handleTemp("fermSetTemp")
	handleTemp("boilSetTemp")

	
	# if our elements are on then we increase temps
	if not os.path.exists("ipc/relayZoneUseA") and os.path.exists("ipc/relayZoneA") and os.path.exists("ipc/gpioSsrA"):
		if tempx['hltSetTemp'] < 95:
			if tempx['hltSetTemp'] > 80:
				tempx['hltSetTemp']=tempx['hltSetTemp']+0.381
			else:
				tempx['hltSetTemp']=tempx['hltSetTemp']+3.81
			tempc['hltSetTemp']=True
	elif not os.path.exists("ipc/relayZoneUseA") and os.path.exists("ipc/relayZoneA") and not os.path.exists("ipc/gpioSsrA"):
		if tempx['hltSetTemp'] > 10:
			tempx['hltSetTemp']=tempx['hltSetTemp']- 0.2
			tempc['hltSetTemp']=True

	if not os.path.exists("ipc/relayZoneUseB") and os.path.exists("ipc/relayZoneB") and os.path.exists("ipc/gpioSsrB"):
		if tempx['hltSetTemp'] < 95:
			if tempx['hltSetTemp'] > 80:
				tempx['hltSetTemp']=tempx['hltSetTemp']+0.381
			else:
				tempx['hltSetTemp']=tempx['hltSetTemp']+3.81
			tempc['hltSetTemp']=True
	elif not os.path.exists("ipc/relayZoneUseB") and os.path.exists("ipc/relayZoneB") and not os.path.exists("ipc/gpioSsrB"):
		if tempx['hltSetTemp'] > 10:
			tempx['hltSetTemp']=tempx['hltSetTemp']- 0.2
			tempc['hltSetTemp']=True


	# Boil Element A on
	if os.path.exists("ipc/relayZoneUseA") and os.path.exists("ipc/relayZoneA") and os.path.exists("ipc/gpioSsrA"):
		if tempx['boilSetTemp'] < 97:
			if tempx['boilSetTemp'] > 80:
				tempx['boilSetTemp']=tempx['boilSetTemp']+0.181	
			else:
				tempx['boilSetTemp']=tempx['boilSetTemp']+1.91
			tempc['boilSetTemp']=True
	if os.path.exists("ipc/relayZoneUseA") and os.path.exists("ipc/relayZoneA") and not os.path.exists("ipc/gpioSsrA"):
		if tempx['boilSetTemp'] > 10:
			tempx['boilSetTemp']=tempx['boilSetTemp']-0.2
			tempc['boilSetTemp']=True
	if os.path.exists("ipc/relayZoneUseB") and os.path.exists("ipc/relayZoneB") and os.path.exists("ipc/gpioSsrB"):
		if tempx['boilSetTemp'] < 97:
			if tempx['boilSetTemp'] > 80:
				tempx['boilSetTemp']=tempx['boilSetTemp']+0.181	
			else:
				tempx['boilSetTemp']=tempx['boilSetTemp']+1.91
			tempc['boilSetTemp']=True
	if os.path.exists("ipc/relayZoneUseB") and os.path.exists("ipc/relayZoneB") and not os.path.exists("ipc/gpioSsrB"):
		if tempx['boilSetTemp'] > 10:
			tempx['boilSetTemp']=tempx['boilSetTemp']-0.2
			tempc['boilSetTemp']=True
	

	if os.path.exists("ipc/swFerm"):
		if os.path.exists('ipc/pinfermCool'):
			tempx['fermSetTemp']=tempx['fermSetTemp']-0.1
			tempc['fermSetTemp']=True
		elif os.path.exists('ipc/pinfermHeat'):
			tempx['fermSetTemp']=tempx['fermSetTemp']+0.3
			tempc['fermSetTemp']=True
		elif os.path.exists("ipc/fermdone"):
			tempx['fermSetTemp']=tempx['fermSetTemp']-0.02
			tempc['fermSetTemp']=True
		else:
			tempx['fermSetTemp']=tempx['fermSetTemp']+0.02
			tempc['fermSetTemp']=True

	# now writes out the files
	from pitmCfg import *
	cfg=pitmCfg()

	probeid=cfg.hltProbe
	temp=convertTemp( 'hltSetTemp',probeid,tempx['hltSetTemp'] ) 

	probeid=cfg.mashAProbe
	temp=convertTemp( 'mashSetTemp',probeid,tempx['mashSetTemp'] ) 

	probeid=cfg.mashBProbe
	temp=convertTemp( 'mashSetTemp',probeid, tempx['mashSetTemp'] ) 
	
	probeid=cfg.boilProbe
	temp=convertTemp( 'boilSetTemp',probeid, tempx['boilSetTemp'] ) 
	
	probeid=cfg.fermProbe
	temp=convertTemp( 'fermSetTemp',probeid, tempx['fermSetTemp'] ) 
	

	time.sleep(2)


