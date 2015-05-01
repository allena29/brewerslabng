#!/usr/bin/python
import pickle
import cgi
import time
import os
import sys
import json
import re
from pitmCfg import *
cfg=pitmCfg()

#import mysql.connector
#from cloudNG import *
#print "Content-Type: text/plain\n\n"
"""
{'_operation': 'temperatureResults1', 'currentResult': {'28-000003eba86a': {'timestamp': 1415460685.074648, 'valid': True, 'temperature': 68.2}, '28-000003ebc866': {'timestamp': 1415460686.911647, 'valid': True, 'temperature': 78.4}, '28-000003ebccea': {'timestamp': 1415460688.744619, 'valid': True, 'temperature': 68.1}}, '_mode': 'hlt/sparge/mash', '_checksum': '81bed18605115fd99c84bd694cf7773fc85fea34', 'tempTargetBoil': (-1, -1, -1), 'tempTargetHlt': (-1, -1, -1), '_brewlog': u'08.11.2014', 'tempTargetFerm': (-1, -1, -1), 'tempTargetSparge': (81.5, 82.5, 82), 'currentStatus': 0, 'tempTargetMash': (66, 68, 67), '_recipe': u'Mosaic'}
"""

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



sys.stdout.write("<xml>\n")

if not os.path.exists("/currentdata/temp-mcast-rx-on") or not os.path.exists("/currentdata/temps/currentResult"):
	print "<tempActive>false</tempActive>"
else:
	print "<tempActive>true</tempActive>"

o=open("/currentdata/temps/currentResult")
d=pickle.loads( o.read()) 
o.close()

probeA=False
probeB=False
probeC=False
			
			

if d['_mode'].count("ferm"):
	probeId=cfg.fermProbe
	(low,high,target) = d['tempTargetFerm']
	if d['currentResult'].has_key( probeId):
		if d['currentResult'][ probeId ]['valid']:
			temp=d['currentResult'][probeId]['temperature']

			if temp > target:
				colour="red"
			elif temp < target:
				colour="blue"
			else:
				colour="green"
			
			print "<probeAcolour>%s</probeAcolour>" %(colour)
			print "<probeAtemp>%s</probeAtemp>" %(temp)
			print "<probeAlabel>Fermentation</probeAlabel>"
			print "<probeAtarget>%s</probeAtarget>" %(target)
	probeA=True



elif d['_mode'].count("hlt"):
	probeId=cfg.hltProbe
	if d['_mode'].count("sparge"):
		print "<probeAlabel>Sparge</probeAlabel>"
		(low,high,target) = d['tempTargetSparge']
	else:
		print "<probeAlabel>HLT</probeAlabel>"
		(low,high,target) = d['tempTargetHlt']
	if d['currentResult'].has_key( probeId):
		if d['currentResult'][ probeId ]['valid']:
			temp=d['currentResult'][probeId]['temperature']

			if temp > target:
				colour="red"
			elif temp < target:
				colour="blue"
			else:
				colour="green"
			
			print "<probeAcolour>%s</probeAcolour>" %(colour)
			print "<probeAtemp>%s</probeAtemp>" %(temp)
			print "<probeAtarget>%s</probeAtarget>" %(target)


			
	probeA=True
			

elif d['_mode'].count("cool"):
	probeId=cfg.boilProbe
	(low,high,target) = d['tempTargetFerm']
	if d['currentResult'].has_key( probeId):
		if d['currentResult'][ probeId ]['valid']:
			temp=d['currentResult'][probeId]['temperature']

			if temp > target:
				colour="red"
			elif temp < target:
				colour="blue"
			else:
				colour="green"
			
			print "<probeAcolour>%s</probeAcolour>" %(colour)
			print "<probeAtemp>%s</probeAtemp>" %(temp)
			print "<probeAtarget>%s</probeAtarget>" %(target)
			print "<probeAlabel>Cool</probeAlabel>"

	probeA=True
			
elif d['_mode'].count("boil"):
	probeId=cfg.boilProbe
	(low,high,target) = d['tempTargetBoil']
	if d['currentResult'].has_key( probeId):
		if d['currentResult'][ probeId ]['valid']:
			temp=d['currentResult'][probeId]['temperature']

			if temp > target:
				colour="red"
			elif temp < target:
				colour="blue"
			else:
				colour="green"
			
			print "<probeAcolour>%s</probeAcolour>" %(colour)
			print "<probeAtemp>%s</probeAtemp>" %(temp)
			print "<probeAtarget>%s</probeAtarget>" %(target)
			print "<probeAlabel>Boil</probeAlabel>"

	probeA=True
			


if d['_mode'].count("mash"):

	if probeA:
		B="B"
		C="C"
		probeB=True
		probeC=True
	else:
		B="A"
		C="B"
		probeA=True
		probeB=True
	probeId=cfg.mashAProbe
	(low,high,target) = d['tempTargetMash']
	if d['currentResult'].has_key( probeId):
		if d['currentResult'][ probeId ]['valid']:
			temp=d['currentResult'][probeId]['temperature']

			if temp > target:
				colour="red"
			elif temp < target:
				colour="blue"
			else:
				colour="green"
			
			print "<probe%scolour>%s</probe%scolour>" %(B,colour,B)
			print "<probe%stemp>%s</probe%stemp>" %(B,temp,B)
			print "<probe%starget>%s</probe%starget>" %(B,target,B)
			print "<probe%slabel>Mash</probe%slabel>" %(B,B)





	probeId=cfg.mashBProbe
	(low,high,target) = d['tempTargetMash']
	if d['currentResult'].has_key( probeId):
		if d['currentResult'][ probeId ]['valid']:
			temp=d['currentResult'][probeId]['temperature']

			if temp > target:
				colour="red"
			elif temp < target:
				colour="blue"
			else:
				colour="green"
			
			print "<probe%scolour>%s</probe%scolour>" %(C,colour,C)
			print "<probe%stemp>%s</probe%stemp>" %(C,temp,C)
			print "<probe%starget>%s</probe%starget>" %(C,target,C)
			print "<probe%slabel>Mash</probe%slabel>" %(C,C)


if not probeA:
	print "<probeAcolour>disabled</probeAcolour>"

if not probeB:
	print "<probeBcolour>disabled</probeBcolour>"

if not probeC:
	print "<probeCcolour>disabled</probeCcolour>"

print "</xml>"
