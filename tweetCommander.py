import os
import re
import sys
import time
import mysql.connector




twitterApi=None
def doTweet(msg,notify=False):
	global twitterApi,tweetProgress,hashtag

	if not twitterApi:	
		try:
			import twitter
			from tweetAuth import tweetAuth
			twitterApi = tweetAuth().api	
		except:
			pass
	if twitterApi:
		if notify:
			twitterApi.PostUpdate("%s %s %s" %(tweetProgress,msg,hashtag))
		else:
			twitterApi.PostUpdate("%s %s" %(msg,hashtag))
		print msg

	else:
		print "Unable to open twitter api"
		sys.exit(2)

# use for main loop
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
# used within the loop
con2=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
# used for updates
conU=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
cursor=con.cursor()
cursor.execute("select gBrewlogs.recipe,gBrewlogs.brewlog,fieldKey,fieldVal from gField,gBrewlogs WHERE gBrewlogs.brewlog = gField.brewlog AND fieldKey LIKE 'tweetEnabled%' and length(fieldVal)>1")
for row in cursor:
	(recipename,brewlog,tweetid,tweettodo)=row
		
	print "Need to tweet for ",recipename,brewlog,tweetid,tweettodo
	brewlog=brewlog
	recipename=recipename
	tweetProgress=""
	hashtag="#brewerslab #%s #b%s" %( re.compile("[^A-Za-z0-9]").sub('',recipename),  re.compile("[^A-Za-z0-9]").sub('',brewlog) )

	print "Twitter Publisher"
	print " hashtag ",hashtag
	print " notification ",tweetProgress


	#
	if tweetid == "tweetEnabled-costvolume" and tweettodo=="yes":
		print "Checking Production Cost"
		cursor2=con2.cursor()
		cursor2.execute("select fieldVal from gField WHERE brewlog ='%s' AND fieldKey = 'litrespackaged' AND length(fieldVal) > 1" %(brewlog))
		for row2 in cursor2:
			(fieldVal,)=row2
			cursor3=con2.cursor()
			cursor3.execute("select entity,cost,litres from gBrewery LIMIT 0,1")
			for row3 in cursor3:
				(entity,cost,litres)=row3
				cursorU=conU.cursor()
				cursorU.execute("UPDATE gBrewery set litres=%s WHERE entity=%s" %(float(litres)+float(fieldVal),entity))
				cursorU=conU.cursor()
				cursorU.execute( "UPDATE gField set fieldVal = 'no'  WHERE brewlog='%s' AND fieldKey='tweetEnabled-costvolume'" %(brewlog))
				doTweet("Packaged %.1f litres of %s (full brewery production cost %.2f GBP/500ml)" %(float(fieldVal), recipename, ((cost/(float(litres)+float(fieldVal))/2  ) )))	

	if tweetid == "tweetEnabled-abv" and tweettodo == "yes":
		print "Checking Final Gravity.....",
		fg=None
		cursor2=con2.cursor()
		cursor2.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='__measuredFg_abv' and length(fieldVal)>1" %(brewlog))
		for row2 in cursor2:
			(recipename,fieldVal)=row2
			fg=fieldVal
		if fg: 
			abv=0
			cursor2=con2.cursor()
			cursor2.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='__abv' and length(fieldVal)>1" %(brewlog))
			for row2 in cursor2:
				(recipename,abv)=row2
			if float(abv) > 0:
				cursorU=conU.cursor()
				cursorU.execute( "UPDATE gField set fieldVal = 'no'  WHERE brewlog='%s' AND fieldKey='tweetEnabled-abv'" %(brewlog))
				doTweet(" .. %s measured FG as %.3f estimated abv %.2f %%" %(recipename,float(fg),abv))
		print ""

