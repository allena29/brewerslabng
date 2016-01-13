import os
import re
import sys
import time
from pitmCfg import pitmCfg
import mysql.connector

os.chdir("/home/beer/brewerslab/master/")
# This is intended to tweet recipe based stuff to the twitter account
# as we change modes

if not os.path.exists("ipc/brewlog-id") or not os.path.exists("ipc/recipe-name"):
	print "No brewlog or recipe-name"
	sys.exit(3)

cfg=pitmCfg()
brewlog=open("ipc/brewlog-id").read().rstrip()
recipename=open("ipc/recipe-name").read().rstrip()
tweetProgress=cfg.tweetProgress
hashtag="#brewerslab #%s #b%s" %( re.compile("[^A-Za-z0-9]").sub('',recipename),  re.compile("[^A-Za-z0-9]").sub('',brewlog) )

print "Twitter Publisher"
print " hashtag ",hashtag
print " notification ",tweetProgress




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



#
#
# brew start
print "Activity Started....",
if not os.path.exists("ipc/tweeted-brewstart") and os.path.exists("activityStarted"):
	flag=open("ipc/tweeted-brewstart","w")
	flag.close()
	doTweet('Started a brewday %s' %(recipename))
	print "DONE",
print ""

# mash out and sparge
print "Activities....",
if not os.path.exists("ipc/tweeted-mash-nearly-finished") and os.path.exists("activityMashout"):
	flag=open("ipc/tweeted-mash-nearly-finished","w")
	flag.close()
	doTweet('mash out and sparge',notify=True)
	print " MASH OUT",
if not os.path.exists("ipc/tweeted-boil-nearly-finished") and os.path.exists("ipc/activityBoilNearlyFinished"):
	flag=open("ipc/tweeted-boil-nearly-finished","w")
	flag.close()
	doTweet('boil finished',notify=True)
	print " BOIL NEARLY FINISHED",


print ""



##
## GRAIN
##

if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityDough") and not os.path.exists("ipc/tweet-grainbill"):
	print "Checking Grain Bill....",
	flag=open("ipc/tweet-grainbill","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit  from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='fermentables' and isAdjunct=0" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit)=row
		doTweet("added %s %s of %s #grainbill" %(qty,unit,ingredient))
		print "DONE",
	print ""

##
## HOPS
##
## FWH
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityHltSparge") and not os.path.exists("ipc/swSparge") and not os.path.exists("ipc/tweet-fwh"):
	print "Checking FWH Hops....",
	flag=open("ipc/tweet-fwh","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >20 AND hopAddAt <21" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		doTweet("added %s %s of %s First Wort Hops #hopbill" %(qty,unit,ingredient))
		print "DONE",
	print ""


## COPPER 
if not os.path.exists("ipc/swFerm") and os.path.exists("activityReachedBoil") and not os.path.exists("ipc/tweet-copperhop"):
	print "Checking Copper Hops....",
	flag=open("ipc/tweet-copperhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >50" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		doTweet("added %s %s of %s Copper Hops #hopbill" %(qty,unit,ingredient))
		print "DONE",
	print ""

#
# Aroma
#
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityAromaHops") and os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-aroma"):
	print "Checking Aroma Hops....",
	flag=open("ipc/tweet-aroma","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >5 AND hopAddAt < 20" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		time.sleep(99)
		doTweet("added %s %s of %s Aroma Hops #hopbill" %(qty,unit,ingredient))
		print "DONE",
	print ""


print "Temperature related tweets....",
if not os.path.exists("ipc/tweeted-whirlpool") and os.path.exists("ipc/activityWhirlpool"):
	flag=open("ipc/tweeted-whirlpool","w")
	flag.close()
	doTweet('time to whirlpool hops',notify=True)
	print " WHIRLPOOL",
if not os.path.exists("ipc/tweeted-cool") and os.path.exists("ipc/activityCool30"):
	flag=open("ipc/tweeted-cool","w")
	flag.close()
	doTweet('wort cool',notify=True)
	print " COOLED",
if not os.path.exists("ipc/tweeted-mash-tun-pre") and os.path.exists("ipc/activityMashTunPre"):
	flag=open("ipc/tweeted-mash-tun-pre","w")
	flag.close()
	doTweet('time to pre-heat mashtun',notify=True)
	print " MASH TUN PRE",
if not os.path.exists("ipc/tweeted-hlt-temp") and os.path.exists("ipc/activityHltTemp"):
	flag=open("ipc/tweeted-hlt-temp","w")
	flag.close()
	doTweet('mash liquor ready',notify=True)
	print " MASH LIQUOR READY",
if not os.path.exists("ipc/tweeted-sparge-temp") and os.path.exists("ipc/activitySpargeTemp"):
	flag=open("ipc/tweeted-sparge-temp","w")
	flag.close()
	doTweet('sparge liquor ready',notify=True)
	print " SPARGE LIQUOR READY",
if not os.path.exists("ipc/tweeted-boil-temp") and os.path.exists("ipc/activityReachedBoil"):
	flag=open("ipc/tweeted-boil-temp","w")
	flag.close()
	doTweet('kettle nearly at a boil',notify=True)
	print " KETTLE READY",
if not os.path.exists("ipc/tweet-ferm-pitching-temp") and os.path.exsits("ipc/ferm-pitching-temp"):
	flag=open("ipc/tweet-ferm-pitching-temp","w")
	flag.close()
	doTweet('FV at pitching temp',notify=True)
	print " FV PITCHING TEMP",
print

#
# Finishing Hops
#
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityFinishingHops") and os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-finishhop"):
	print "Checking Finishing Hops....",
	flag=open("ipc/tweet-finishhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >3 AND hopAddAt < 10" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row	
		doTweet("added %s %s of %s Finishing Hops #hopbill" %(qty,unit,ingredient))
		print "DONE",
	print ""

#
# Flameout
#
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityFlameoutHops") and not os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-flameout"):
	print "Checking Flameout Hops....",
	flag=open("ipc/tweet-flameout","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0 AND hopAddAt < 0.002" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		doTweet("added %s %s of %s Flameout Hops #hopbill" %(qty,unit,ingredient))
		print "DONE"
	print ""

#
# Whirlpool
#
if not os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityWhirlpool") and not os.path.exists("ipc/tweet-whirlpoolhop"):
	print "Checking Whirlpool hops....",
	flag=open("ipc/tweet-whirlpoolhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0.001 AND hopAddAt < 0.003" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		doTweet("added %s %s of %s Whirlpool hops #hopbill" %(qty,unit,ingredient))
		print "DONE",
	print ""
#
# Dry Hop
#
if os.path.exists("ipc/swFerm") and os.path.exists("ipc/activityDryhop") and not os.path.exists("ipc/tweet-dryhop"):
	print "Checking Dry-hop {button press}....",
	flag=open("ipc/tweet-dryhop","w")
	flag.close()	
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	print "select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt  < 0.004" %(brewlog)
	cursor.execute("select recipe,ingredient,qty,unit,hopAddAt from gIngredients,gBrewlogs where gBrewlogs.recipe=gIngredients.recipename and brewlog='%s' and ingredientType='hops' AND hopAddAt >0.001 AND hopAddAt < 0.003" %(brewlog))
	for row in cursor:
		(recipename,ingredient,qty,unit,hopAddAt)=row
		doTweet("added %s %s of %s dry hops #hopbill" %(qty,unit,ingredient))
		print "DONE",
	print ""




#
# Other Stats
#
# Boil Volume
if os.path.exists("ipc/swBoil") and not os.path.exists("ipc/tweet-boilvol"):
	print "Checking Boil Volume....."
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='preBoilVolume' and length(fieldVal)>1" %(brewlog))
	for row in cursor:
		flag=open("ipc/tweet-boilvol","w")
		flag.close()	
		(recipename,fieldVal)=row
		doTweet("currently boiling %sL of wort" %(fieldVal))

# SG 1..5
for s in range(5):
	sg=s+1
	if os.path.exists("ipc/swFerm") and not os.path.exists("ipc/tweet-sg%s" %(sg)):
		print "Checking Gravity Sample %s....." %(sg),
		con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
		cursor=con.cursor()
		cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='sg%s' and length(fieldVal)>1" %(brewlog,sg))
		for row in cursor:
			flag=open("ipc/tweet-sg%s" %(sg),"w")
			flag.close()	
			(recipename,fieldVal)=row
			doTweet(".. measured gravity at %.3f" %(float(fieldVal)))
		print ""

# Original Gravity
if not os.path.exists("ipc/swPump") and  os.path.exists("ipc/swFerm") and not os.path.exists("ipc/tweet-og"):
	print "Checking Original Gravity....."
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
			doTweet("%sL of wort in the fermenter - %.3f OG" %(fieldVal,float(og)))



# Final Gravity
if os.path.exists("ipc/post-ferm")  and not os.path.exists("ipc/tweet-abv"):
	print "Checking Final Gravity.....",
	fg=None
	con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
	cursor=con.cursor()
	cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='__measuredFg_abv' and length(fieldVal)>1" %(brewlog))
	for row in cursor:
		(recipename,fieldVal)=row
		fg=fieldVal
	if fg: 
		abv=0
		con=mysql.connector.connect(host="192.168.1.13",user='brewerslab',password='beer',database="brewerslab")
		cursor=con.cursor()
		cursor.execute("select gBrewlogs.recipe,fieldVal from gField,gBrewlogs WHERE gField.brewlog='%s' AND gBrewlogs.brewlog = gField.brewlog AND fieldKey='__abv' and length(fieldVal)>1" %(brewlog))
		for row in cursor:
			(recipename,fieldVal)=row
			flag=open("ipc/tweet-abv","w")
			flag.close()	
			(recipename,fieldVal)=row
			doTweet("Measured FG as %.3f estimated abv %.2f %%" %(float(fg),abv))
	print ""




# Fermentation Over (reads in post-ferm flag)
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

	print "Checking ferm status (Algoirthim 1)....",
	if averageCoolEvents == 0:
		preFerm=True
		for b in range(len(buckets)-2):		# start considering 3rd buckets onwards
			if buckets[b+2][2] > 0 and buckets[b+2][3] > 0:	# only consider buckets with valid timestamps
#				print "Checking bucket ",b+2,time.ctime(float(buckets[b+2][2])),time.ctime(float(buckets[b+2][3]))
#				print "\t",buckets[b+2][1],averageHeatEvents*.33
				if buckets[b+2][1] < averageHeatEvents*0.33 and preFerm:
#					print "\tNow think we are in active fermentation %s vs %s" %(buckets[b+2][1],averageHeatEvents)
					preFerm=False
				elif not preFerm and buckets[b+2][1] > averageHeatEvents*.33:
#					print "\tNow think we are out of active fermentation"
#					print "\tBut we will put on a 24 hour delay"
					if not os.path.exists("ipc/post-ferm"):
						flag=open("ipc/post-ferm","w")
						flag.close()
	print

	if os.path.exists("ipc/post-ferm"):
		print "Checking post ferm....",
		if time.time() > os.stat("ipc/post-ferm").st_mtime + (1.5*86400):
			doTweet("%s fermentation nearing an end" %(tweetProgress))
			o=open("ipc/adjustFermTarget","w")
			o.write("21")
			o.close()
			print "YES"
		else:
			print "NO"	



