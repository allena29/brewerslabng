import os
import re
import mysql.connector

# This is intended to tweet recipe based stuff to the twitter account
# as we change modes

twitterApi=None
def doTweet(msg):
	global twitterApi

	if not twitterApi:	
		try:
			import twitter
			from tweetAuth import tweetAuth
			twitterApi = tweetAuth().api	
		except:
			pass
	if twitterApi:
		twitterApi.PostUpdate(msg)
		print msg



brewlog=open("ipc/brewlog-id").read().rstrip()


##
## GRAIN
##

if os.path.exists("ipc/activityDough") and not os.path.exists("ipc/tweet-grainbill"):
	flag=open("ipc/tweet-grainbill","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit  from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='fermentables' and isAdjunct=0" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit)=row
		doTweet("added %s %s of %s #grainbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))


##
## HOPS
##
## FWH
if os.path.exists("ipc/activityHltSparge") and not os.path.exists("ipc/swSparge") and not os.path.exists("ipc/tweet-fwh"):
	flag=open("ipc/tweet-fwh","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >20 AND hopAddAt <21" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s First Wort Hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))



## COPPER 
if os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-copperhop"):
	flag=open("ipc/tweet-copperhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >50" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s Copper Hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))


#
# Flameout
#
if os.path.exists("ipc/activityFlameoutHops") and not os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-flameout"):
	flag=open("ipc/tweet-flameout","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0 AND hopAddAt < 0.002" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s Flameout Hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))



#
# Whirlpool
#
if os.path.exists("ipc/activityWirlpool") and not os.path.exists("ipc/tweet-whirlpoolhop"):
	flag=open("ipc/tweet-whirlpoolhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0.001 AND hopAddAt < 0.003" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s Whirlpool hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))




