import os
import re
import time
from pitmCfg import pitmCfg
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
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0.001 AND hopAddAt < 0.003" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s Whirlpool hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))


#
# Dry Hop
#
if os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityDryhop") and not os.path.exists("ipc/tweet-dryhop"):
	flag=open("ipc/tweet-dryhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	print "select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt  < 0.004" %(brewlog)
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0.001 AND hopAddAt < 0.003" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		print row
		doTweet("added %s %s of %s dry hops #hopbill #brewerslab #%s" %(qty,unit,ingredient,re.compile("[^A-Za-z0-9]").sub('',recipename)))





#
# Other Stats
#
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
if not os.path.exists("ipc/swPump") and  os.path.exists("ipc/swFerm") and not os.path.exists("ipc/tweet-og"):
	og=None
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='og' and length(fieldVal)>1" %(brewlog))
	for row in cursor:
		(recipename,fieldVal)=row
		og=fieldVal

	if og:
		con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
		cursor=con.cursor()
		cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='postboilvol' and length(fieldVal)>1" %(brewlog))
		for row in cursor:
			(recipename,fieldVal)=row
			flag=open("ipc/tweet-og","w")
			flag.close()	
			(recipename,fieldVal)=row
			doTweet("%sL of wort in the fermenter - %.4f OG #brewerslab #%s" %(fieldVal,float(og),re.compile("[^A-Za-z0-9]").sub('',recipename)))


# Fermentation Over (reads in post-ferm flag)
cfg=pitmCfg()
if os.path.exists("ipc/swFerm") and not os.path.exists("ipc/tweet-fermover"):



	flags=os.listdir("ipc/fermprogress")
	flags.sort()

	bucketsize=3600*4
	bucketstart=os.stat("ipc/ferm-pitching-temp").st_mtime
	bucketend=bucketstart+bucketsize
	buckets=[ [ 0,0,0,0] ]



	heatEvents=0
	coolEvents=0
	for flag in flags:
		(utc,event)=flag.split("-")
		if float(utc) > bucketend:
			buckets[-1][0]= coolEvents
			buckets[-1][1]= heatEvents
			buckets[-1][2] = bucketstart
			buckets[-1][3] = bucketend
			bucketstart=bucketend
			bucketend=bucketstart+bucketsize

			heatEvents=0
			coolEvents=0

			buckets.append( [0,0,0,0] )
		if float(utc) < bucketend:
			if event == "low":
				heatEvents=heatEvents+1
	#			print "HEAT EVENT",time.ctime(float(utc))
			if event == "high":	
				coolEvents=coolEvents+1
	#			print "COOL EVENT",time.ctime(float(utc))
			buckets[-1].append( (utc,event) )
		
	averageHeatEvents=buckets[0][1]
	averageHeatEvents=averageHeatEvents+buckets[1][1]
	averageCoolEvents=buckets[0][0]
	averageCoolEvents=averageCoolEvents+buckets[1][0]



	# Above we have create a number of buckets which gives a list for each bucket
	# 0 = coolevents (the number of times the fridge kicked in)
	# 1 = heatevents (the number of times the heater kicked in)
	# 2 = start epoch of bucket
	# 3 = end epoch of bucket
	# 4 + 2 item tuple for each event (low,epoch)  (normal,epoch)  (high,epoch)

	# Algorithim 1: 
	# cool weather where the fridge doesn't kick in 
	# (note: fridge can be used to bring down to pitching temp)
	# if we haave 33% of heat events we call it pre-fermentation

	if averageCoolEvents == 0:
		preFerm=True
		for b in range(len(buckets)-2):		# start considering 3rd buckets onwards
			if buckets[b+2][2] > 0 and buckets[b+2][3] > 0:	# only consider buckets with valid timestamps
#				print "Checking bucket ",b+2,time.ctime(float(buckets[b+2][2])),time.ctime(float(buckets[b+2][3]))
#				print "\t",buckets[b+2][1],averageHeatEvents*.33
				if buckets[b+2][1] < averageHeatEvents*0.33:
#					print "\tNow think we are in active fermentation %s vs %s" %(buckets[b+2][1],averageHeatEvents)
					preFerm=False
				elif not preFerm and buckets[b+2][1] > averageHeatEvents*.33:
#					print "\tNow think we are out of active fermentation"
#					print "\tBut we will put on a 24 hour delay"
					if not os.path.exists("ipc/post-ferm"):
						flag=open("ipc/post-ferm","w")
						flag.close()
					

	if os.path.exists("ipc/post-ferm"):
		if time.time() > os.stat("ipc/post-ferm").st_mtime + 86400:
			doTweet("%s fermentation nearing an end #brewerslab #%s" %(cfg.tweetProgress,re.compile("[^A-Za-z0-9]").sub('',open("ipc/recipe-name").read())) )
	
