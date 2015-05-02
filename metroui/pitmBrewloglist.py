#!/usr/bin/python
import re
import json
import sys
import time
import cgi
import mysql.connector
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")

print "Content-Type: text/plain\n\n"
cursor=con.cursor()
cursor.execute("select brewlog,recipe,brewhash FROM gBrewlogs ORDER BY entity DESC")

print "["
comma=" "
for row in cursor:
	(brewlog,recipe,brewhash)=row
	con2=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
	cursor2=con2.cursor()
	cursor2.execute("select target_mash_temp,boil_vol,mash_liquid,sparge_water,precoolfvvolume from gRecipeStats WHERE recipe='%s' AND brewlog='%s' ORDER BY entity DESC LIMIT 0,1" %(recipe,brewlog))
	
	sys.stdout.write("%s " %(comma))
	detail={}
	detail['boil_vol']=100
	detail['sparge_water']=100
	detail['precoolfvvolume']=100
	detail['mash_water']=100
	
	detail= {'brewlog':brewlog,'recipe':recipe,'hash':brewhash, 'fermLow':18.7,'fermHigh':19.3,'fermTarget':19, 'hltLow':87.5,'hltHigh':88.5,'hltTarget':88, 'spargeLow':81.5,'spargeHigh':82.5,'spargeTarget':82 ,'mashLow':66,'mashHigh':68,'mashTarget':67, 'strikeLow':81.999,'strikeTarget':82,'strikeHigh':82.1  } 
#print json.dumps(detail)
	for row2 in cursor2:
		(target_mash_temp,boil_vol,mash_water,sparge_water,precoolfvvolume) = row2
		detail['boil_vol']=boil_vol
		detail['mash_water']=mash_water
		detail['sparge_water']=sparge_water
		detail['precoolfvvolume']=precoolfvvolume
		detail['mashTarget'] = target_mash_temp
		detail['mashHigh'] = target_mash_temp + 0.75
		detail['mashLow'] = target_mash_temp - 0.75
	print json.dumps(detail),

	comma="\n,"
print "]"
