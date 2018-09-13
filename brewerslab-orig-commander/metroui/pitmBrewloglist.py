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
	print comma,
	(brewlog,recipe,brewhash)=row
	if brewlog:
		con2=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
		cursor2=con2.cursor()
		cursor2.execute("select target_mash_temp,boil_vol,mash_liquid,sparge_water,precoolfvvolume,strike_temp from gRecipeStats WHERE recipe='%s' AND brewlog='%s' ORDER BY entity DESC LIMIT 0,1" %(recipe,brewlog))

		
		detail= {'brewlog':brewlog,'recipe':recipe,'hash':brewhash, 'fermLow':18.7,'fermHigh':19.3,'fermTarget':19, 'hltLow':87.5,'hltHigh':88.5,'hltTarget':88, 'spargeLow':81.5,'spargeHigh':82.5,'spargeTarget':82 ,'mashLow':66,'mashHigh':68,'mashTarget':67, 'strikeLow':81.999,'strikeTarget':82,'strikeHigh':82.1  } 

		# Get the hop schedules
		# dryhop, whirlpool, flameout, finishing, aroma, fwh, copper
		hops=[False,False,False,False,False,False,False]
		con3=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
		cursor3=con3.cursor()
		cursor3.execute("select distinct(hopAddAt) from gIngredients where recipeName ='%s' AND hopAddAt >0" %(recipe))
		for row3 in cursor3:
			(hopAddAt,)=row3
			if hopAddAt > 30:	hops[6]=True
			if hopAddAt > 20 and hopAddAt < 21:	hops[5]=True
			if hopAddAt > 10 and hopAddAt < 20:	hops[4]=True
			if hopAddAt > 3 and hopAddAt <10:	hops[3]=True
			if hopAddAt > 0 and hopAddAt < 0.002:	hops[2]=True
			if hopAddAt > 0.001 and hopAddAt < 0.002:	hops[1]=True
			if hopAddAt < 0.003:	hops[0]=True
				
		detail['hops']=hops	

		for row2 in cursor2:
			(target_mash_temp,boil_vol,mash_water,sparge_water,precoolfvvolume,strike_temp) = row2
			detail['hltLow']=float(strike_temp)+3
			detail['hltHigh']=float(strike_temp)+4
			detail['hltTarget']=float(strike_temp)+3.5
			detail['hltLow']=float(strike_temp)+3
			detail['boil_vol']=boil_vol
			detail['mash_water']=mash_water
			detail['sparge_water']=sparge_water
			detail['precoolfvvolume']=precoolfvvolume
			detail['mashTarget'] = target_mash_temp
			detail['mashHigh'] = target_mash_temp + 0.75
			detail['mashLow'] = target_mash_temp - 0.75


		con4=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
		cursor4=con4.cursor()
		cursor4.execute("select fermTemp,fermLowTemp,fermHighTemp from gRecipes WHERE recipename='%s' ORDER BY entity DESC LIMIT 0,1" %(recipe))
		for row4 in cursor4:
			(fermTemp,fermLowTemp,fermHighTemp)=row4
			detail['fermTarget'] = float(fermTemp)
			detail['fermLow'] = float(fermLowTemp)
			detail['fermHigh'] = float(fermHighTemp)
		

		print json.dumps(detail),
		comma="\n,"
		print ""

print "]"
