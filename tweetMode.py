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

if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityDough") and not os.path.exists("ipc/tweet-grainbill"):
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
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityHltSparge") and not os.path.exists("ipc/swSparge") and not os.path.exists("ipc/tweet-fwh"):
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
if not os.path.exists("ipc/swFerm") and os.path.exists("activityReachedBoil") and not os.path.exists("ipc/tweet-copperhop"):
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
# Aroma
#
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityAromaHops") and os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-aroma"):
	flag=open("ipc/tweet-aroma","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >5 AND hopAddAt < 20" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s Aroma Hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))


#
# Aroma
#
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityFinishingHops") and os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-finishhop"):
	flag=open("ipc/tweet-finishhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >3 AND hopAddAt < 10" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s Finishing Hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))


#
# Flameout
#
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityFlameoutHops") and not os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-flameout"):
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
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityWhirlpool") and not os.path.exists("ipc/tweet-whirlpoolhop"):
	flag=open("ipc/tweet-whirlpoolhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	print "select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0.001 AND hopAddAt < 0.003" %(brewlog)
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0.001 AND hopAddAt < 0.003" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s Whirlpool hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))





# Boil Volume
if os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-boilvol"):
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='preBoilVolume' and length(fieldVal)>1" %(brewlog))
	for row in cursor:
		flag=open("ipc/tweet-boilvol","w")
		flag.close()	
		(recipename,fieldVal)=row
		doTweet("currently boiling %sL #brewerslab #%s" %(fieldVal,re.compile("[^A-Za-z0-9]").sub('',recipename)))

# Original Gravity
if os.path.exists("ipc/swFerm") and not os.path.exists("ipc/tweet-og"):
	og=None
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='og' and length(fieldVal)>1" %(brewlog))
	for row in cursor:
		og=fieldVal

	if og:
		con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
		cursor=con.cursor()
		cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='postboilvol' and length(fieldVal)>1" %(brewlog))
		for row in cursor:
			flag=open("ipc/tweet-og","w")
			flag.close()	
			(recipename,fieldVal)=row
			doTweet("%sL of wort in the fermenter - %.4f OG #brewerslab #%s" %(fieldVal,float(og),re.compile("[^A-Za-z0-9]").sub('',recipename)))

