from __future__ import division


"""


This code has been through a number of iterations.

First as a PyGTK+ application, which used object representation of data
principly documented in brewerslabData.py

This started to transition to a GoogleAppEngine application, however this
became a difficult converstion.

Somewhere along the way an android app was created.

ngData.py was introduced via to bridge the google app engine calls via a 
mysql backend. The frontend then started to move into it's current 
web based form in the metroui directory.


The metroui doesn't support creating processes, these are best done via
testRecipe.py which generated the mysql statements.




"""

public =1 


################################################################################################################################################
from brewerslabEngine import *
from brewerslabData import *
import time


#
#
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
#
#
#	Stores
#
#
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
#
#


userid="testuser"




presets=brwlabPresetData( userid )

if os.path.exists("store/%s/store" %(userid)):
	stores = pickle.loads( open("store/%s/store" %(userid)).read() )
else:
	stores=brwlabInventory()

# Update everything should be created via the Data objects and not
# directly. presets.getMisc, presets.getConsumable will return
# a preset or create a new object.
# The pre-existing flag will be set if it was already in the database
# although this doesn't necessairly mean it wasn't created by us
# previously.

tesco = presets.getSupplier("Tesco")

water = presets.getMisc("Bottled Water (2L)")
water.category="Water"
water.subcategory="Bottled Water"
water.supplier=tesco
water.qty_multiple = 2

for wate in range(38):
	purchase=brwlabPurchase(water)
	purchase.qty=2
	purchase.price=0.085
	stores.addPurchase( purchase )

############################################################


slurry = presets.getYeast("Yeast Slurry")
slurry.atten=73
slurry.category="Yeast"
slurry.subcategory="Ale"

purchase=brwlabPurchase( slurry )
purchase.qty=1
purchase.price=0.00
purchase.purchaseDate("2010-10-18")
purchase.bestBeforeDate("2013-12-1")
stores.addPurchase( purchase )



safale04 = presets.getYeast("Safale S04")
safale04.atten=73
safale04.category="Yeast"
safale04.subcategory="Ale"

hcg = presets.getSupplier("Homebrew Centre Grimsby")

purchase=brwlabPurchase(safale04)
purchase.qty=1
purchase.price=1.99
stores.addPurchase( purchase )

for c in range(3):
	purchase=brwlabPurchase( safale04 )
	purchase.qty=1
	purchase.price=1.99
	purchase.supplier=hcg
	purchase.purchaseDate("2010-12-24")
	purchase.bestBeforeDate("2011-12-24")
	stores.addPurchase( purchase )

############################################################

marisOtter = presets.getFermentable("Maris Otter")

for maris in range(6):

	purchase=brwlabPurchase( marisOtter )
	purchase.qty=1000
	purchase.price=0.00148
	purchase.supplier=hcg
	purchase.purchaseDate("2010-10-16")
	purchase.bestBeforeDate("2011-10-16")
	stores.addPurchase( purchase )


brewuk=presets.getSupplier("BrewUK")

biscuit = presets.getFermentable("Biscuit")

purchase=brwlabPurchase( biscuit )
purchase.qty=500
purchase.price=0.0044
purchase.supplier=brewuk
purchase.purchaseDate("2010-10-18")
purchase.bestBeforeDate("2011-12-1")
stores.addPurchase( purchase )


sugar = presets.getConsumable("priming sugar")
sugar.category="primingsugar"

purchase=brwlabPurchase( sugar )
purchase.qty=400
purchase.price=.001
purchase.suppler=tesco
stores.addPurchase(purchase)


crystal = presets.getFermentable("Crystal 150")

purchase=brwlabPurchase( crystal )
purchase.qty=750
purchase.price=0.00159
purchase.supplier=hcg
purchase.purchaseDate("2010-10-16")
purchase.bestBeforeDate("2011-10-16")
stores.addPurchase( purchase )

goldensyrup = presets.getFermentable("Golden Syrup")
goldensyrup.calculateFromYield(100)
goldensyrup.color=0
goldensyrup.isAdjunct=1
goldensyrup.addBoil=1
goldensyrup.category="Adjunct"

purchase=brwlabPurchase( goldensyrup )
purchase.qty=200
purchase.price=0.0189
purchase.supplier=tesco
stores.addPurchase( purchase )



honey = presets.getFermentable("Honey")
honey.calculateFromYield(76)
honey.color=0
honey.isAdjunct=1
honey.addBoil=1
honey.category="Adjunct"

purchase=brwlabPurchase( honey )
purchase.qty=3040
purchase.price=0.00197058
purchase.supplier=tesco
purchase.purchaseDate("2010-12-20")
purchase.bestBeforeDate("2012-06-30")
stores.addPurchase( purchase )


purchase=brwlabPurchase( marisOtter )
purchase.qty=3000
purchase.price=0.0014666667
purchase.supplier=hcg
purchase.purchaseDate("2010-12-24")
purchase.bestBeforeDate("2011-12-24")
stores.addPurchase( purchase )



torrifiedwheat = presets.getFermentable("Torrified Wheat",78)
torrifiedwheat.calculateFromYield(78)
torrifiedwheat.colour=2
torrifiedwheat.isGrain=1
torrifiedwheat.mustMash=1
torrifiedwheat.category="Grain"
torrifiedwheat.subcategory="Head Retention"

purchase=brwlabPurchase( torrifiedwheat )
purchase.qty=500
purchase.price=0.0015
purchase.supplier=hcg
purchase.purchaseDate("2010-12-24")
purchase.bestBeforeDate("2011-12-24")
stores.addPurchase( purchase )


caramalt = presets.getFermentable("Caramalt")
caramalt.calculateFromYield(75)
caramalt.colour=14
caramalt.isGrain=1
caramalt.mustMash=0
caramalt.category="Grain"
caramalt.subcategory="Speciality"


caragold = presets.getFermentable("CaraGold")
caragold.calculateFromYield(74)
caragold.colour=9
caragold.isGrain=1
caragold.mustMash=0
caragold.category="Grain"
caragold.subcategory="Speciality"
thermometer=presets.getEquipment("Digital Thermometer")
thermometer.mustSterilise=1
jug=presets.getEquipment("Jug (1.5L)")
jug.mustSterilise=1
saucepan=presets.getEquipment("Saucepan")
bottler=presets.getEquipment("Little Bottler")
funnel=presets.getEquipment("Funnel")
syringe=presets.getEquipment("2.5ml Syringe")
filteringFunnel=presets.getEquipment("Filtering Funnel")
filteringFunnel.mustSterilise=1
smalljug=presets.getEquipment("Small Jug")
smalljug.mustSterilise=1
plastictapfilter=presets.getEquipment("Plastic Tap Filter")
plastictapfilter.mustSterilise=1
fermentationbin6gal=presets.getEquipment("Fermentation Bin (6 Gal)")
fermentationbin6gal.mustSterilise=1
fermentationbin6gal.subEquipment.append( plastictapfilter )
fermentationbin6gal.weight=1125	# weight in grames wihtout lid, but with taps etc
fermentationbin6gal.weightlids=1131 # weight in grames with lid
fermentationbin6gal.dead_space=1.5	# litres		measured		
fermentationbin=presets.getEquipment("Fermentation Bin")
fermentationbin.mustSterilise=1
fermentationbin.subEquipment.append( plastictapfilter )
fermentationbin.weight=873	# weight in grames
fermentationbin.deadspace=3.34	# litres		measured 30thJan2010
fermentationbin.dead_space=2	
sparge_arm=presets.getEquipment("Sparge Arm")
sparge_arm.mustSterilise=1
sterilisingPowder = presets.getConsumable("Sterilising Powder")
sterilisingPowder.dosage=4.5
sterilisingPowder.unit="tsp"
timer =presets.getEquipment("Timer")

jerry10l =presets.getEquipment("10l Kettle")
jerry10l.volume=10
jerry10l.mustSterilise=0
jerry10l.dead_space=0


copperkettle=presets.getSupplier("Copper Kettle Homebrewing")
mash_tun_tap=presets.getEquipment("Mash Tun Tap")
mash_tun_tap.mustSterilise=1

saucepan=presets.getEquipment("Saucepan")
saucepan.mustSterilise=1
mashpaddle=presets.getEquipment("Mash Paddle")
mashpaddle.mustSterilise=1

hydrometer=presets.getEquipment("Hydrometer")
hydrometer.mustSterilise=1
trialjar=presets.getEquipment("Trial Jar")
trialjar.mustSterilise=1
slottedspoon=presets.getEquipment("Slotted Spoon")
slottedspoon.mustSterilise=1
thermometer3=presets.getEquipment("Thermometer")
thermometer3.mustSterilise=1
thermometer2=presets.getEquipment("Thermometer")
thermometer2.mustSterilise=1
immersionchiller=presets.getEquipment("Immersion Chiller")
immersionchiller.mustSterilise=1
immersionheater=presets.getEquipment("Immersion Heater")
immersionheater.mustSterilise=1
largepaddle=presets.getEquipment("Large Paddle")
largepaddle.mustSterilise=1
mash_tun=presets.getEquipment("Mash Tun")
mash_tun.mustSterilise=1
mash_tun.dead_space=2.25
mash_tun.subEquipment.append( mash_tun_tap )
hlt=presets.getEquipment("Hot Liquor Tank")
hlt.image="images/hlt.png"
hlt.mustSterilise=1
hlt.heatPower=1.6
hlt.description="A Hot Liquor Tank is used to heat water."
hlt.instructions="A Hot Liquor Tank can be made from a fermentation bin with electric kettles installed."
hlt.dead_space=3.5
kettle70l =presets.getEquipment("70l Kettle")
kettle70l.volume=70
kettle70l.mustSterilise=1
kettle70l.dead_space=2		# estimate 30/1/2010
kettle70l.boilVolume=60

purchase=brwlabPurchase( caragold )
purchase.qty=1000
purchase.price=0.00245
purchase.supplier= copperkettle
purchase.purchaseDate("2010-12-24")
purchase.bestBeforeDate("2011-12-24")
stores.addPurchase( purchase )



############################################################


hallertauhersbrucker=presets.getHop("Hallertau Hersbrucker",2.4)

purchase=brwlabPurchase( hallertauhersbrucker )
purchase.qty=100
purchase.hop_actual_alpha = 2.4
purchase.price=0.00199
purchase.supplier=copperkettle
purchase.purchaseDate("2010-10-14")
purchase.bestBeforeDate("2014-10-14")
stores.addPurchase( purchase )


willamette=presets.getHop("Willamette",4.8)

purchase=brwlabPurchase( willamette )
purchase.hop_actual_alpha=4.8
purchase.hop_aged_alpha = 3.77
purchase.hop_actual_alpha = 3.77
purchase.qty=100
purchase.price=0.0199
purchase.supplier=copperkettle
purchase.purchaseDate("2010-10-14")
stores.addPurchase( purchase )


worcester=presets.getSupplier("Worcester Hop Shop")

northdown = presets.getHop("Northdown",7.5)

purchase=brwlabPurchase( northdown )
purchase.qty=75
purchase.price=0.0199
purchase.supplier=worcester
purchase.purchaseDate("2010-10-14")
stores.addPurchase( purchase )


brewmart = presets.getSupplier("Sheffield Brewmart")

#hallertauhersbrucker22 = presets.getHop("Hallertau Hersbrucker",2.2)
#purchase=brwlabPurchase( hallertauhersbrucker22 )
purchase=brwlabPurchase( hallertauhersbrucker )
purchase.hop_actual_alpha = 2.2
purchase.hop_aged_alpha = 1.92
purchase.hop_actual_alpha = 2.2
purchase.qty=70
purchase.price=0.044419
purchase.supplier=brewmart
purchase.purchaseDate("2010-4-2")
purchase.bestBeforeDate("2014-4-2")
stores.addPurchase( purchase )


saaz= presets.getHop("SaaZ",3.5)

purchase=brwlabPurchase( saaz )
purchase.qty=100
purchase.price=0.0199
purchase.supplier=copperkettle
purchase.purchaseDate("2010-10-14")
stores.addPurchase( purchase )


glacier= presets.getHop("Glacier",5.6)

purchase=brwlabPurchase( glacier )
purchase.qty=303333
purchase.price=0.01023
purchase.supplier=hcg
purchase.purchaseDate("2010-4-10")
purchase.bestBeforeDate("2012-2-2")
stores.addPurchase( purchase )


cascade= presets.getHop("Cascade",5.8)
cascade.addAt=60			## Is this still needed?

purchase=brwlabPurchase( cascade )
purchase.qty=100
purchase.price=0.0199
purchase.supplier=worcester
purchase.hop_actual_alpha=5.8
purchase.hop_aged_alpha = 5.2		# todo automatically calculate this one day
purchase.hop_actual_alpha=5.2
purchase.purchaseDate("2010-10-14")
stores.addPurchase( purchase )



challenger= presets.getHop("challenger",7.6)


purchase=brwlabPurchase( challenger )
purchase.qty=75
purchase.price=0.0199
purchase.supplier=worcester
purchase.purchaseDate("2010-10-14")
stores.addPurchase( purchase )


centennial= presets.getHop("Centennial",11.7)



for wate in range(4):
	purchase=brwlabPurchase(water)
	purchase.qty=2
	purchase.price=0.085
	purchase.purchaseDate("2011-1-12")
	stores.addPurchase( purchase )

for wate in range(0):
	purchase=brwlabPurchase(water)
	purchase.qty=2
	purchase.price=0.085
	purchase.purchaseDate("2011-1-18")
	stores.addPurchase( purchase )

for wate in range(0):
	purchase=brwlabPurchase(water)
	purchase.qty=2
	purchase.price=0.085
	purchase.purchaseDate("2011-1-20")
	stores.addPurchase( purchase )


citric = presets.getConsumable("Citric Acid")
citric.unit="tsp"

protofloc = presets.getConsumable("Protofloc")
protofloc.copper_fining=1
protofloc.copper_fining=0.25
protofloc.unit="tablet" 

campdenTablet= presets.getConsumable("Campden Tablets")
campdenTablet.unit="tablet"
crs= presets.getConsumable("AMS (CRS)")
crs.unit="ml"
salifert= presets.getConsumable("Salifert Alkaline Test")
salifert.unit="tests"
burton = presets.getConsumable("Burton Water Salts")
burton.unit="tsp"


yeastvit = presets.getConsumable("Yeast Vit")
yeastvit.yeast_nutrient=2.5
yeastvit.unit="gm"


copperkettle=presets.getSupplier("Copper Kettle Homebrewing")
purchase=brwlabPurchase( protofloc )
purchase.qty=10
purchase.qty_multiple=1
purchase.price=0.125
purchase.supplier= copperkettle
purchase.purchaseDate("2010-12-24")
purchase.bestBeforeDate("2011-12-24")
stores.addPurchase( purchase )



maltmiller=presets.getSupplier("The Malt Miller")
northernbrewer= presets.getHop("Northern Brewer",6.1)

purchase=brwlabPurchase( northernbrewer )
purchase.qty=1004
purchase.price=0.0255
purchase.supplier=maltmiller
purchase.purchaseDate("2011-1-24")
purchase.bestBeforeDate("2012-1-24")
#stores.addPurchase( purchase )


purchase=brwlabPurchase( centennial )
purchase.qty=100
purchase.price=0.0255
purchase.supplier=maltmiller
purchase.purchaseDate("2011-1-24")
purchase.bestBeforeDate("2012-1-24")
#stores.addPurchase( purchase )

saflager=presets.getYeast("Saflager W-34/70")
saflager.atten=73
saflager.category="Yeast"
saflager.subcategory="Lager"

purchase=brwlabPurchase( saflager )
purchase.qty=1
purchase.price=1.50
purchase.supplier=maltmiller
purchase.purchaseDate("2011-1-24")
purchase.bestBeforeDate("2011-2-24")
#stores.addPurchase( purchase )







#
#
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
#
#
#	Process
#
#
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
#
#



myprocessK=brwlabProcess()
myprocessK.credit="Adam Allen"
myprocessK.name="40AG"


myprocessK.description="Worsdell Brewing - An updated process for use in the entirely within the garage, with the introduction of basic water treatment"

myprocessK.boilers = [kettle70l]
myprocessK.hlt = hlt
myprocessK.mash_tun = mash_tun




# Preparation
step = myprocessK.brewday.newstep("Preparation")
#step.newSubStep( ("If using a fermentation-fridge move it into position, it is necessary to wait >12 hours after moving the fridge before using.",{'complete':1}) )
step.newSubStep( ("Add ice-boxes to the freezer, these will be used to cool the immersion chiller water",{'complete':1}) )
#step.newSubStep( ("Ensure batteries for thermometers are available",{'complete':1}))
#step.newSubStep( ("Ensure clean towells are available as well as clean dry cloths for the floor",{'complete':1}))
step.text="The day before brew day the preparation above should be carried out, as well as checking stock/ingredients are available"



# Gather things
step = myprocessK.brewday.newstep("Assemble Mash/Lauter Tun")
step.text="Assemble the bucket in bucket mash tun, complete with scavenger tube. Gather Sparge Arm, Vorlauf Funnel Paddle and digital thermometer."
step.img=['assemblemashtun.png']

# Gather things
step = myprocessK.brewday.newstep("Assemble Hot Liquor Tank")
step.text="Assemble the hot liquor tank, complete with latstock and thermometer probe"
step.img=['assemblehlt.png']

# Gather things
#step = myprocessK.brewday.newstep("Assemble Kettle")
#step.text="Assemble the kettles with ball-valve tap. Use a stainless steel washer on the inside and pfte tape around thread. "
#step.img=['assemblekettle.png']

# Gather things
step = myprocessK.brewday.newstep("Assmeble Fermentation Bin")
step.text="Assemble the fermentation bin, complete with back filter"
step.img=['assemblefv.png']


# Gather things
#step = myprocessK.brewday.newstep("Gather small stockpots")
#step.text="Gather small stockpots and measuring spoons, these will be used to contain the grain"



## Gather things
#step = myprocessK.brewday.GatherThings()
#step.text="The grain can be measured later"

# Clean Equipment
step = myprocessK.brewday.newstep("Clean Equipment")
step.text="Clean equipment with a mild detergent. It is important to clean equipment before use, any equipment used before the boil only needs to be cleaned as the wort will be sterilised during the boil. Equipment used after the boil must either be sterilised with sterilising solution, or limited equipment may be sterilised in the boiler. Note: don't use 2 real taps for the HLT, use one dummy tap. The equipment to clean is: hlt, sparge arm, mash tun, jug, large paddle, thermometer, stoarge box, kettles and jerry can. "
step.addEquipment( mashpaddle )
step.addEquipment( hlt )
step.addEquipment( sparge_arm )
step.addEquipment( mash_tun )
step.addEquipment( jug ) # try do without a jug
step.addEquipment( smalljug )
step.addEquipment( largepaddle )
step.addEquipment( thermometer )
#step.addEquipment( storagebox )
#step.addEquipment( filteringFunnel )
jar2l=presets.getConsumable("2l Jar")
jar2l.muststerilise=1
jar400ml=presets.getConsumable("400ml Jar")
jar400ml.muststerilise=1
pfte=presets.getConsumable("PFTE Tape")
pfte.unit="m"
measuringspoon=presets.getEquipment("Measuring Spoon")
crowncaps=presets.getConsumable("Crown Caps")
crowncaps.category="bottlecaps"
bottles=presets.getConsumable("500ml glass bottle")
bottles.volume=474
bottles.fullvolume=500
bottles.caprequired=1
bottles.category="bottle"
muslinbag=presets.getConsumable("Muslin Bag")
measuringspoon=presets.getEquipment("Measuring Spoon")
crowncaps=presets.getConsumable("Crown Caps")
crowncaps.category="bottlecaps"
bottles=presets.getConsumable("500ml glass bottle")
bottles.volume=474
bottles.fullvolume=500
bottles.caprequired=1
bottles.category="bottle"
muslinbag=presets.getConsumable("Muslin Bag")
bottlebrush=presets.getEquipment("Bottle Brush")
step.addEquipment( jerry10l )
step.newSubStep( ("Clean HLT",{'complete':1}) )
step.newSubStep( ("Clean FV",{'complete':1}) )
step.newSubStep( ("Clean Kettle",{'complete':1}) )
step.newSubStep( ("Clean Mashtun",{'complete':1}) )

# Clean work area
step = myprocessK.brewday.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before commencing the brew day"



step.img=["sterilise_setup1.png"]



### modified for a more logical break in the proceedings.



# Fill the HLT
step = myprocessK.brewday.newstep("Fill HLT (for Mash Liquor)")
step.text="Fill the HLT with ...mash_liquid_6...L of water for the mash and add a campden tablet to remove chlorine, stir and leave for 5 minutes"
step.addConsumable( campdenTablet, 1)
# Fill the HLT
step = myprocessK.brewday.newstep("Treat Mash Liquor")
step.text="Treat the mash water to remove alkalinity, this should be done 5 minutes after adding the campden tablet. The low-resolution method for alkalinity test is used as the alkalinity is very hard. Once the salifert solution is orange/pink  "
step.addConsumable( salifert , 1)
step.newSubStep( ("Add 2ml of water into the test vial for the Salifert Alkalinity Test.",{'complete':1}))
step.newSubStep( ("Add 2 drops of KH-Indicator to the test vial.",{'complete':1}))
step.newSubStep( ("Add 1ml of reagent to the fine granularity syringe.",{'complete':1}))
step.newSubStep( ("Add drop by drop to the, mixing the solution each time, the colour needs to change from blue/green to orange/pink, turn the syringe upside down and use the reading at the upper part of the black piston",{'complete':1}))
step.attention="Note: only add 75%% of the CRS adjustment during this step - the calculations in this step only calculate 75%%"
step.newSubStep( ("Add CRS based upon the calculations below to the mash liquid and stir. (75%% calcualted in this step)",{'complete':1}))
step.fields.append( ('Mashwater PH','mashWaterPH','') )
step.fields.append( ('Mash Salifert Reagent Remaining','__mashSalifertReagent','0.10'))
step.widgets['mashAlkalinity'] = ('salifertAlkalinity',['__mashSalifertReagent'])
step.fields.append( ('Mash Alkalinity','mashAlkalinity',''))
step.widgets['mashCrsAdjustment'] = ('mashCrsAdjustment',['__mashSalifertReagent'])
step.fields.append( ('Mash CRS Adjustment','mashCrsAdjustment',''))
step.img=['treatwater.png']


step = myprocessK.brewday.newstep("Measure Treated Mash Liquor")
step.text="In the previous step we added 75%% of the CRS adjustment we should remeasure the treated mash liquor (high resolution test) and decide if to add more adjustment"
step.addConsumable( salifert , 2)
step.newSubStep( ("Add 4ml of water into the test vial for the Salifert Alkalinity Test.",{'complete':1}))
step.newSubStep( ("Add 4 drops of KH-Indicator to the test vial.",{'complete':1}))
step.newSubStep( ("Add 1ml of reagent to the fine granularity syringe.",{'complete':1}))
step.newSubStep( ("Add drop by drop to the, mixing the solution each time, the colour needs to change from blue/green to orange/pink, turn the syringe upside down and use the reading at the upper part of the black piston",{'complete':1}))
step.newSubStep( ("Add CRS based upon the calculations below to the mash liquid and stir.",{'complete':1}))
step.fields.append( ('Mash Retest Salifert Reagent Remaining','__mashSalifertReagentRetest','0.10'))
step.widgets['mashAlkalinityRetest'] = ('salifertAlkalinityHighRes',['__mashSalifertReagentRetest'])
step.fields.append( ('Mash Alkalinity','mashAlkalinityRetest',''))
step.widgets['mashCrsAdjustmentRetest'] = ('mashCrsAdjustmentRetest',['__mashSalifertReagentRetest'])
step.fields.append( ('Mash CRS Adjustment','mashCrsAdjustmentRetest',''))




# Fill the HLT
step = myprocessK.brewday.newstep("Begin heating mash water")
step.text="(HLT) Heat the mash water to strike temperature + 5 degC (...strike_temp_5... degC)"
step.attention="Do not turn on the temperature controller until the elements in the kettle are covered with water."
step.img=['treatwater.png']


# Gather grain
step = myprocessK.brewday.newstep("Gather Grain")
step.text="Gather the and measure the grain required for the brewday"
step.auto="gatherthegrain"
step.addConsumable(burton,2)
# Note: there is a hardcoded assumption in cloudNG.py:compile() which assumes we have exactly 1 substep
step.newSubStep( ("Add 1 teaspoon of gypsum -OR- 2 teaspoons of burton water salts to the grain.",{'complete':1}))		
			# this is dosage of gypsum correct, thought it might have been too much



# Mash
step = myprocessK.brewday.newstep("Get Ready to Mash")
step.text="Once the Mash Water has been heated to 65C then pre-heat the mash tun."
step.newSubStep( ("Boil 1.5L of tap water and add to the mash tun, add the lid to the mash tun",{'complete':1}))
#step.auto="grainqty"
step.img = ['mash.png']


# Fill the Mash Tun
step = myprocessK.brewday.newstep("Fill the mash tun with mash liquid")# and set aside the grain. During this step the mash tun should be well insulated to maintain a stable temperature")
step.text="Fill the mashtun with the mash liquor in order the water is to ...strike_temp_5...C (Strike Temp ...strike_temp...C). The water in the HLT should be heated to 5degC higher than strke temp to account for some losses while transferring the liquid, however the temperature should be monitored. Note: if more water is used in the mash tun the strike temperature should be lower, if less water is used then the strike temperature should be higer."
step.prereq="Mash Water is at ...strike_temp_5...C"
step.newSubStep( ("Discard the water used for preheating the mash tun",{'complete':1}))
step.newSubStep( ("Fill the mash tun with  ...mash_liquid...L of water heated to ...strike_temp_5...C.", {'complete':1}) )
step.newSubStep( ("Set aside 1.7L of boiling water and 1.7L of cold water which may optionally may be used for adjustment of temperature/consistency", {'complete':1}))
step.attention="If the grain temperature is not between 15-20 degC then the calculations should be re-run to provide a hotter/colder strike temp."


#
#
#
myprocessK.recipeUpgrades['grainthicknessMustBeGreaterThan'] = 1.35


# Dough in the grain 
step = myprocessK.brewday.newstep("Dough in the grain")
step.text="(MASH) The temperature for mashing is important high temperatures will lead to extraction of tannins, low temperatures will not provide efficient conversion. Lower temperature conversion - around 64-66.6C  will take longer but will produce a more complete conversion of complex starches to sugars resulting in more fermentation and a clean, lighter tasting beer. A high temperature conversion of 68.5-70 C will result in less starch conversion leaving a beer with more unfermentable dextrines. This will create a beer with a full body and flavor. Middle mash temperatures  67.69 C will result in medium bodied beers.  The consistency of the mixture should be resemble porridge. (Note: this is still subject to refining in the past this was calculated with a ratio of 1.25 but recipes will be at least 1.35 with this process."

step.newSubStep( ("With the temperature of the mash liquid at ...strike_temp...C stir in the grain.", {'complete':1}))
step.newSubStep( ("The aim is to mash at a temperature of ...target_mash_temp...C", {'complete':1}))
step.newSubStep( ("Cover and set aside for 60 minutes.",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("Take out the mash paddle",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("If after a few minutes the temperature difference is +/- 3degC of the ...target_mash_temp...C target then a temperature adjustment may be carried out with care.", {'complete':1}))
step.newSubStep( ("Press the button on the controller to start the mash timer.", {'complete':1}))
step.newSubStep( ("Take a sample of the mash to measure the PH",{'complete':1}))

step.addEquipment( timer )
step.fields.append(('Ambinet Temp(C)','mash_ambient_temp',''))
step.fields.append(('Adjustment Needed','mash_adjusment_needed',''))
step.fields.append(('(Start) Mash Temp Acheived','mash_start_temp',''))
step.attention="The Temperature of the Grain Bed should remain below 75degC throughout."
step.img=["dough.png"]








# Fill the HLT
step = myprocessK.brewday.newstep("Fill HLT (for Sparge Liquor)")
step.text="Fill the HLT so that it contains ...sparge_water...L of water for the sparge and add a campden tablet to remove chlorine and a level teaspoon of citric acid, stir and leave for 5 minutes"
step.addConsumable( campdenTablet, 1)
step.fields.append(('(MID1) Mash Temp Acheived','mash_mid1_temp',''))

# Fill the HLT
step = myprocessK.brewday.newstep("Treat Sparge Liquor")
step.text="Treat the mash water to remove alkalinity, this should be done 5 minutes after adding the campden tablet. The high-resolution method for alkalinity test is used as the water will have some mash liuor left. Once the salifert solution is orange/pink  "
step.addConsumable( salifert , 1)
step.newSubStep( ("Add 4ml of water into the test vial for the Salifert Alkalinity Test.",{'complete':1}))
step.newSubStep( ("Add 4 drops of KH-Indicator to the test vial.",{'complete':1}))
step.newSubStep( ("Add 1ml of reagent to the fine granularity syringe.",{'complete':1}))
step.newSubStep( ("Add drop by drop to the, mixing the solution each time, the colour needs to change from blue/green to orange/pink, turn the syringe upside down and use the reading at the upper part of the black piston",{'complete':1}))
step.newSubStep( ("Add the CRS based upon the calculations below to the sparge liquid and stir.",{'complete':1}))
step.fields.append( ('Sparge Water PH','spargehWaterPH','') )
step.fields.append( ('Mash Salifert Reagent Remaining','__spargeSalifertReagent','0.10'))
step.widgets['spargeAlkalinity'] = ('salifertAlkalinityHignRes',['__spargeSalifertReagent'])
step.fields.append( ('Sparge Alkalinity','spargeAlkalinity',''))
step.widgets['spargeCrsAdjustment'] = ('spargeCrsAdjustment',['__spargeSalifertReagent'])
step.fields.append( ('Sparge CRS Adjustment','spargeCrsAdjustment',''))
step.img=['treatwater.png']


# Fill the HLT 
step = myprocessK.brewday.newstep("Heat Sparge Liquor")
step.text="(MASH + SPARGE) The sparge water is expected to take around ...sparge_heating_time... minutes to heat."
step.newSubStep(("Begin heating the sparge water to ...sparge_temp...C",{'complete':1}))
step.attention="The HLT is constructed with standard kettle elements, therefore it is advisable to alternate between the elements 3 or 4 times during the heating. The temperature controller should only power one kettle element at any time."


# Bring the wort to the boil
## if we are doing First Wort Hops then we need this here;
step = myprocessK.brewday.newstep("Measure Hops")
step.text="Measure the hops for addition to the kettle."
step.auto="hopmeasure_v3"
step.img=["boil.png"]


# Monitor Mash Equipment
step = myprocessK.brewday.newstep("Monitor the Mash")
step.text="Monitor the temperature of the mash."
step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."

step.fields.append(('(MID15) Mash Temp Acheived','mash_mid15_temp',''))
step.fields.append(('(MID16) Mash Temp Acheived','mash_mid16_temp',''))
step.fields.append(('(MID17) Mash Temp Acheived','mash_mid17_temp',''))
step.fields.append(('(MID18) Mash Temp Acheived','mash_mid18_temp',''))
step.fields.append(('(MID19) Mash Temp Acheived','mash_mid19_temp',''))
step.fields.append(('(MID20) Mash Temp Acheived','mash_mid20_temp',''))
step.fields.append(('(MID21) Mash Temp Acheived','mash_mid21_temp',''))
step.fields.append(('(MID22) Mash Temp Acheived','mash_mid22_temp',''))
step.fields.append(('(MID23) Mash Temp Acheived','mash_mid23_temp',''))
step.fields.append(('(MID24) Mash Temp Acheived','mash_mid24_temp',''))
step.fields.append(('(MID25) Mash Temp Acheived','mash_mid25_temp',''))


# Ensure Sparge Water is at the correct temperature
step = myprocessK.brewday.newstep("Assemble Sparge Setup and begin Recirculation")
#step.addConsumable(muslinbag,1)
step.addEquipment(funnel)


step.text="Once the sparge water is at the correct temperature ...sparge_temp...C AND the mash duration has completedthe sparge setup can be setup. During this step the cloudy wort with bits of grain will drained leading to a natural grain filter forming."
step.newSubStep( ("Take off the lid from the mash tun and assemble the sparge arm",{}))
step.newSubStep( ("Allow up to 6 litres of wort to drain from the mash tun into the kettle, the wort should be carefully added back to the top of the lauter tun trying to ensure minimal disturbance.",{'complete':1}))
step.fields.append(('(End) Mash Temp Acheived','mash_end_temp',''))
step.newSubStep( ("Collect sample of mash to measure PH",{'complete':1}))
step.attention="Set the thermometer to alarm if the temperature is higher than 71deg. If it is then lid should be lifted to reduce the heat."
step.img=["spargesetup.png"]



step = myprocessK.brewday.newstep("First Wort Hopping")
step.condition=[]
step.condition.append( ['first_wort_hop_qty','>',0] )
step.text="Add the first wort hops to the boiler before starting to sparge"
step.auto="hopaddFirstWort_v3"



# Start Sparge
step = myprocessK.brewday.newstep("Start Fly Sparging")
step.text="(SPARGE) Sparging will drain the sugar from the grain providing us with wort. The process of sparging should be carried out slowly. The temperature of the gain bed will be raised during this proess (note there is no instant change of temperature). The grain bed should stay below 76 deg C. We need to aim for a boil volume of ...boil_vol...L. General wisdom is to keep 1 inch of water above the grain bed- however there is a trade off (the more water above the grain bed the smaller/slower temperature rise of the grain bed, the less water above the grain bed the bigger/quicker temperature rise of the grain bed."
#Throughout the process monitor flow of liquid into and out of the mash tun to try maintain an equilibrium"
step.newSubStep( ("Collect sample of sparge water to measure PH",{'complete':1}))
step.img=["dosparge.png"]







step = myprocessK.brewday.newstep("Start Boiling the Wort")
step.text="(BOIL) Boiling the wort drives off unwanted volatile components, coagulates proteins,  and sanitising the wort for fermentation. The first boil should be ...kettle1volume...L of wort. We are aiming for a gravity of ...kettle1preboilgravity... It is expected the kettle will loose ...kettle1evaporation...L due to evaporation """
step.newSubStep( ("Start boiling the wort.",{}))
step.attention="Use thermometer alarm to determine when the wort has reached a boil."
step.img=["boil.png"]

step.fields.append( ('Temp (C)','__kettle1_temp1','60') )
step.fields.append( ('Gravity (1.xxx)','__kettle1_grav1','1.007') )
step.widgets['__kettle1_adjusted1'] = ('gravityTempAdjustment',['__kettle1_temp1','__kettle1_grav1'])
step.fields.append( ('Adjusted Gravity','__kettle1_adjusted1','') )
step.fields.append( ('Pre Boil Gravity','preboilgravity',''))
step.fields.append( ('Pre Boil Volume','preboilvolume',''))




# Dynamic Recipe Adjustment.
step = myprocessK.brewday.newstep("Dynamic Recipe Adjustment")
step.text="If the mash was particularly efficent/inefficient it may be desirarble to top up fermentables, dilute wort, increase/decrease hop quantities. The target pre-boil gravity is ...preboil_gravity... (total post-boil gravity ...estimated_og...). The target wort volume required is ...boil_vol...L. The gravity quotes here takes account of later topup of ...topupvol...L. Estimated gravity post boil pre cooling is ...postboilprecoolgravity..."
step.attention="Be careful with topup at this stage, the dilution of cooling/evaporation will concentrate the wort further. If the wort is too concentrated at this stage delay dilution until the cooling stage. Making readings of volume/gravities is the most important thing at this stage."



step.fields.append( ('Topup Gravity','__topupgravity','1.000') )
step.fields.append( ('Topup Gravity Temp','__topupgravitytemp','20') )
step.widgets['__topupgravityadjusted'] = (' gravityTempAdjustment',['__topupgravity','__topupgravitytemp'])
step.fields.append( ('Topup Gravity Adjusted','__topupgravityadjusted','1.000') )
step.fields.append( ('Final Gravity Required','__topupgravityrequired','') )



# Begin sterilising remaining equipment
step = myprocessK.brewday.newstep("Sterilise Equipment")
step.text="It is important throughout the brew day to keep any equipment which will come into contact with the wort post-boil sterilised. Equipment used before the boil does not need to be sterilised but does need to be clean. Note: the silicone tube used for transferring wort from the boiler into the fermentation bin will be sanitised in a later step."
step.newSubStep( ("Fill the fermentation bin with 10 litres of warm water and 2 tsp of sterilising powder.",{'complete':1}))
step.newSubStep( ("Ensure fermentation bin is fully sterilised with equipment.",{'complete':1}))
step.newSubStep( ("Ensure a 'filter' is added to the back of the fermentation bin tap",{'complete':1}))
step.img=['sterilise1step.png']



step.addEquipment( fermentationbin6gal )

# Rinse Equipment
step = myprocessK.brewday.newstep("Rinse Equipment")
step.text="Rinse Equipment in the same way as sterilising, equipment should be rinsed with 25 litres of cold water."


step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."

step.fields.append(('(MID8) Mash Temp Acheived','mash_mid8_temp',''))
step.fields.append(('(MID9) Mash Temp Acheived','mash_mid9_temp',''))
step.fields.append(('(MID10) Mash Temp Acheived','mash_mid10_temp',''))
step.fields.append(('(MID11) Mash Temp Acheived','mash_mid11_temp',''))
step.fields.append(('(MID12) Mash Temp Acheived','mash_mid12_temp',''))
step.fields.append(('(MID13) Mash Temp Acheived','mash_mid13_temp',''))
step.fields.append(('(MID14) Mash Temp Acheived','mash_mid14_temp',''))


step.img=["sighttube.png"]


# Bring the wort to the boil
step = myprocessK.brewday.newstep("Bittering Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Once the wort is at a rolling boil the hops can be added and the lid should be left half covered."
step.img=["boil.png"]
step.newSubStep(("Start timer for 45 minutes after which the protofloc copper finings will be added",{'complete':1,'kitchentimer' : ('b',3600) }))
step.auto="hopaddBittering_v3_withadjuncts"


# Bring the wort to the boil
step = myprocessK.brewday.newstep("Pump Wort")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="(BOIL + PUMP) With the wort at a boil recirculate with the pump to ensure that the pump and tubing is sterilised. Pump for 5 minutes"



# Bring the wort to the boil
step = myprocessK.brewday.newstep("Aroma Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the aroma hops to the kettle with 15 minutes remaining. The immersion chiller will need to be sterilised during this period and irishmoss/protofloc added to help coagulate proteins in the wort. For small boils it may be necessary to tie the immersion chiller with cable ties."
step.newSubStep(("Start timer for 15 minutes .",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the irishmoss/protofloc and continue boiling for 15 minutes.",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the immersion chiller",{'complete':1,'kitchentimer' : ('a',900) }))
step.auto="hopaddAroma_v3"
step.img=["boil.png"]


## Sanitise
#step = myprocessK.brewday.newstep("Sanitise the boiler tube")
#step.text="Put the transfer tube in the kettle, open the tap of the kettle and start the pump to recirculate the boiling wort in order to sanitise the transfer tube."


# Bring the wort to the boil
step = myprocessK.brewday.newstep("Finishing Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the finishing hops to the kettle and stop the heat."
step.auto="hopaddFinishing_v3"
step.img=["boil.png"]


# Yeast Rehydration
#step = myprocessK.brewday.newstep("Boil Yeast Rehydration Water")
#step.text="Rehydration yeast provides a gentle start for the yeast and helps fermentation start quickly. If using yeast slurry instead then this step will still be carried out to sterilise the jug in order to measure the yeast slurry."
#step.newSubStep(("Boil 500ml of water and set aside in a pyrex jug",{'complete':1}))
#step.newSubStep(("After 10 minutes put the hug in a water bath to cool the water to 25 degC",{'complete':1}))
#step.attention="Yeast should nto be added to the rehydration water unless is is <25 degC"




# Cool Wort
step = myprocessK.brewday.newstep("Cool wort")
step.text="(PUMP) It is important to cool the wort quickly, ice water can help to cooling water towards the end of cooling. The estimated gravity required is ...estimated_og... Do not aerate the wort while, however the pump can be used to recirculate the wort through the already sanitised transfer tube."
step.newSubStep(("Setup the immersion chiller and and start pushing cold water through to cool the wort to 20 degC",{'complete':1}))
step.img=["drain3.png"]
step.newSubStep(("With the temperature of the wort at 35degC start using ice to cool the temperature of the cooling water.",{'complete':1}))
step.newSubStep(("Add half of the yeast contents to the rehydration water, for Safale S04 the temperature of the yeast rehydration water should be 27degC +/- 3degC",{'complete':1}))
step.condition=[]
step.fields.append( ('Post Boil Volume (Pre Cool)','postboilvolumebeforecool','') )



# Drain Wort
step = myprocessK.brewday.newstep("Pump wort into fermentation bin")
step.condition=[]
step.text="(PUMP + FERM) With the wort cooled to 20degC, then record the volume of the wort in the boiler, before draining the wort from the fermentation bin."
step.attention="Once started draining avoid turning off the tap as this can stop the syphon effect. To maximise the wort from the boiler it should be titled with a wooden board underneath and then disturbance should be minimised in order to make best use of hop bed to filter out hot break material."
step.img=["drain1.png"]



step.fields.append( ('Drain Temp)','tempdraintemp','') )
step.fields.append( ('Drain Gravity','tempdraingravity','') )
step.widgets['tempdrainedgravity'] = ('gravityTempAdjustment',['tempdraintemp','tempdraingravity'])
step.fields.append( ('Drain Adjusted Gravity','tempdrainedgravity',''))

step.fields.append( ('Tmp Addition Temp (C)','__2additiontemp','') )
step.fields.append( ('Tmp Addition Gravity (1.xxx)','__2additiongravity','') )
step.widgets['__2additionadjustedgravity'] = ('gravityTempAdjustment',['__2additiontemp','__2additiongravity'])
step.fields.append( ('Tmp Addition Adjusted Gravity','__2additionadjustedgravity','') )

step.fields.append( ('Tmp Gathered Wort Volume','__2gatheredvol','') )
step.fields.append( ('Tmp Addition Volume','__2additionvol','') )
step.widgets['2precoolgravity'] = ('combineMultipleGravity',['__2gatheredadjustedgravity','__2additionadjustedgravity','__2gatheredvol','__2additionvol'])
step.fields.append( ('Tmp Pre Cool Gravity','2precoolgravity','') )



# Cool Wort
step = myprocessK.brewday.newstep("Topup")
step.text="As the wort is cooled a decision should be made on the gravity of the resulting wort. It is hard to increase the gravity (as the high gravity wort is already used) but easy to reduce the gravity (as diluted wort/sterilised water will be easily available). It is best to make the decision when the wort is as cool as possible to reduce the effect of the hydrometer adjustments. If there was a high mash temperature factor in high final gravity when trying to calculate alcohol. Too severe a dilution will reduce the bittering/hop aroma. Planned volume in the fermenter (pretopup)....precoolfvvolume... with a later topup of ...topupvol...L, planed original gravity ...postboil_precool_og.../...estimated_og... (precool/cool)  planned final gravity ...estimated_fg... planned abv ....estimated_abv..."
step.fields.append( ('Fermentation Bin Pre Topup Temp)','fvpretopuptemp','') )
step.fields.append( ('Fermentation Bin Pre Topup Gravity','fvpretopupgrav','') )
step.widgets['fvpretopupadjusted'] = ('gravityTempAdjustment',['fvpretopuptemp','fvpretopupgrav'])
step.fields.append( ('Fermentation Bin Pre Topup Adjusted Gravity','fvpretopupadjusted',''))
step.fields.append( ('Fermentation Bin Volume','fvpretopupvolume','') )

step.fields.append( ('Tmp Original Gravity','__prerinseOg_abv',''))
step.fields.append( ('Tmp Final Gravity','__prerinseFg_abv',''))
step.widgets['__preRinseAbv'] = ('abvCalculation',['__prerinseOg_abv','__prerinseFg_abv'])
step.fields.append( ('Temp ABV','__preRinseAbv',''))


step.fields.append( ('Tmp Addition Temp (C)','__2additiontemp','') )
step.fields.append( ('Tmp Addition Gravity (1.xxx)','__2additiongravity','') )
step.widgets['__2additionadjustedgravity'] = ('gravityTempAdjustment',['__2additiontemp','__2additiongravity'])
step.fields.append( ('Tmp Addition Adjusted Gravity','__2additionadjustedgravity','') )
step.fields.append( ('Tmp Addition Volume','__2additionvol','') )
step.widgets['2precoolgravity'] = ('combineMultipleGravity',['fvpretopupadjusted','__2additionadjustedgravity','fvpretopupvolume','__2additionvol'])
step.fields.append( ('Post Topup Gravity','fvposttopupgravity','') )
step.fields.append( ('Post Topup Volume','fvposttopupvolume','') )
step.fields.append( ('Post Topup Post Cool Gravity','fvpostuppostcoolgravity','') )




# Measure
step = myprocessK.brewday.newstep("Clean")
step.text="Throughout the brewday it is a good idea to have been cleaning equipment, it's only at this stage that it is practical to clean the pump by cycling boiling water through it."


# Measure
step = myprocessK.brewday.newstep("Measure")
step.text="(FERM) Recording results is important to track the quality of the brew. The expected original gravity is ...estimated_og..., final gravity estimate is ...estimated_fg..., estimated abv ...estimated_abv..."
step.newSubStep(("Aerate the wort for 5 minutes",{'complete':1}))
step.newSubStep(("After aerating the wort measure take a sample to measure the original gravity.",{'complete':1}))
step.fields.append( ('Original Gravity','og','') )
step.fields.append( ('Fermentation bin Weight','postboilweight','') )
step.fields.append( ('Fermentation bin vol (after cooling)','postboilvol','') )
step.fields.append( ('Wort left in boiler vol','leftovervol','') )



step = myprocessK.brewday.newstep("Measure PH from brewday")
step.text="Various samples should have been taken start of mash, end of mash and sparge water to determine the PH throughout the process. The PH meter will need to be calibrated with a solution of a known PH at a set temperature. 4.00 @ 5-25, 4.01 @ 30, 4.02 @ 35, 4.03 @ 40, 4.04 @ 45, 4.06 @ 50, 4.07 @ 55, 4.09 @ 60, 4.12 @ 70, 4.16 @ 80, 4.20 @ 90, 4.22 @ 95. 6.95 @ 5, 6.92 @ 10, 6.90 @ 15, 6.88 @ 20, 6.86 @ 25, 6.85 @ 30, 6.84 @ 35-40, 6.83 @ 45-55, 6.84 @ 60, 6.85 @ 70, 6.86 @ 80, 6.88 @ 90"
step.attention="PH meter is calibrated for 25degC."
step.fields.append( ('Mash PH','mashPH','') )
step.fields.append( ('Post Mash PH','postMashWaterPH','') )
step.fields.append( ('Spargewater PH','spargeWaterPH','') )
step.fields.append( ('Finished Wort PH','wortPH','') )



# Pitch
step = myprocessK.brewday.newstep("Pitch Yeast")
step.text="If using yeast slurry then measure 400ml of slurry assuming the batch size is <6 gallon and the yeast slurry must be less than 14 days old. Before using yeast slurry a check on the progress of ferementation from the previous batch is required."
step.newSubStep(("Once the wort is at pitching temperature (20degC)",{'complete':1}))
#oistep.newSubStep(("Optionally add an immersion heater set for 18degC",{'complete':1}))
step.addConsumable(yeastvit,0.5)
step.newSubStep(("Pitch the yeast",{'complete':1}))
step.newSubStep(("Add half a teaspoon of yeastvit",{'complete':1}))

step = myprocessK.brewday.newstep("Relax!")
step.text="Finished the brewday"

###########################
#Post Brew Day


step = myprocessK.postbrewday.newstep("Kraussen")
step.text="Checking for signs of fermentation begining such as a temperature rise (temp controller in a brew fridge will mask this), or the kraussen (yeast crust forming on top of the wort). "
step.newSubStep(("Kraussen Observed.",{'complete':1}))
step.attention="Once activity of fermentation has been confirmed do not open the feremntation bin"
step.fields.append(('Time first fridge trigger','fridgetriggerdelay',''))
step.fields.append(('Temp after 12 hours','fermtemp12',''))
step.fields.append(('Temp after 1 day','fermtemp24',''))
step.fields.append(('Temp after 2 days','fermtemp48',''))
step.fields.append(('Temp after 3 days','fermtemp72',''))
step.fields.append(('Temp after 4 days','fermtemp96',''))
step.fields.append(('Temp after 5 days','fermtemp120',''))


step = myprocessK.postbrewday.newstep("Dryhop")
step.text ="After 3 days add the dry hops. There is differing opinion about adding hops, too early and the aroma is driven off by the CO2 produced in fermentation, too late and there *may* be a *potential* oxidation risk. The alcohol should protect anynasty organisms in the hops from taking hold. However the hop tea-balls can still be santiised in boiling water."
step.auto="dryhop"
step.condition=[]

step = myprocessK.postbrewday.newstep("Measure specific gravity (1st)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 1 (1.xxx)','sg1',''))


step = myprocessK.postbrewday.newstep("Measure specific gravity (2nd)")
step.text ="After 7 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 2 (1.xxx)','sg2',''))


step = myprocessK.postbrewday.newstep("Measure specific gravity (3rd)")
step.text ="After 8 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 3 (1.xxx)','sg3',''))


step = myprocessK.postbrewday.newstep("Measure specific gravity (4th)")
step.text ="After 9 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 4 (1.xxx)','sg4',''))

step = myprocessK.postbrewday.newstep("Measure specific gravity (5th)")
step.text ="After 10 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 5 (1.xxx)','sg5',''))




step = myprocessK.postbrewday.newstep("Calculate Alcohol")
step.text="The alcohol can be calculated from the original gravity and the stable final gravity readings."
step.fields.append( ('Measured Final Gravity','__measuredFg_abv',''))
step.widgets['__abv'] = ('abvCalculation',['og','__measuredFg_abv'])
step.fields.append( ('ABV','__abv','') )


step = myprocessK.bottlingAndKegging.GatherThings()


step = myprocessK.bottlingAndKegging.newstep("Gather Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gatherthepolypins"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Polypins\n"
step.newSubStep(("Gather ...polypinqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

step = myprocessK.bottlingAndKegging.newstep("Gather Mini Kegs")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gathertheminikegs"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Minikegs with bungs/safety vent bungs\n"
step.newSubStep(("Gather ...minikegqty... minikegs",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available


step = myprocessK.bottlingAndKegging.newstep("Gather Bottles")
step.condition=[]
step.condition.append(['bottleqty','>',0])
step.auto="gatherthebottles"
step.stockDependency=["bottle"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Bottles\n"
step.newSubStep(("Gather ...bottleqty... bottles",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

#step = myprocessK.bottlingAndKegging.newstep("Move fermentation bin")
#step.text="If needed move the fermentation bin to a height suitable for bottling from. This should be carried out early to allow any disturbance to settle"


step = myprocessK.bottlingAndKegging.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before starting with bottling."
step.addEquipment(bottlebrush)
step.addEquipment(hydrometer)
step.addEquipment(trialjar)
step.addEquipment(slottedspoon)
step.addEquipment(thermometer2)
step.addEquipment(smalljug)
step.addEquipment(jug)
step.addEquipment(bottler)
step.addEquipment(measuringspoon)

step.addEquipment(jar2l)
step.addEquipment(jar400ml)

#step = myprocessK.bottlingAndKegging.newstep("Setup Work Area")
#step.text="Setup the work area as shown in the image, cleaning the bottles may be carried out the previous evening to save time."
#step.img=["bottlingsetup.png"]


step = myprocessK.bottlingAndKegging.newstep("Clean Bottles")
step.text="Cleaning the bottles using hot water and detergent."
step.newSubStep(("Clean the bottles using a bottle brush to ensure no deposits are left in the bottle. Drain solution out of the bottles.",{'complete':1}))
step.newSubStep(("Rinse the bottles with a small amount of water.",{'complete':1}))
step.img=['bottleclean.png']

step = myprocessK.bottlingAndKegging.primingSolution()
step.text="Priming solution provides more fermentables for the yeast to convert into further alcohol and natural carbonation"
step.newSubStep(("Measure ...primingsugartotal... (...primingsugarqty... per bottle) priming sugar and set aside.",{'complete':1}))
step.newSubStep(("Add ...primingwater... ml of water to the saucepan and heat to 90degC, once at 90degC stir in the sugar",{'complete':1}))
step.newSubStep(("Maintain the temperature at 85degC for 5 minutes and then cool in a water bath to less that 30 degC.",{'complete':1}))
step.img=['primingsolution.png']
step.attention="Be careful with the volume of sugar in each bottle as introducing too many fermentables can lead to exploding bottles"


#step = myprocessK.bottlingAndKegging.newstep("Setup Work Area 2")
#step.text="Setup the work area as show in the image, during the bottling stage all equipment will be required."
#step.img=["bottlingsetup2.png"]


step = myprocessK.bottlingAndKegging.newstep("Sterilise Crown Caps")
step.text="Crown caps needs to be sterilised before use."
step.newSubStep(("Boil 500ml of water and add to a clean pyrex jug",{'complete':1}))
step.newSubStep(("Add ...num_crown_caps... crown caps/plastic caps to the jug and set aside.",{'complete':1}))


step = myprocessK.bottlingAndKegging.newstep("Prepare Jars for Yeast Harvesting")
step.text="Yeast harvesting may be carried out if fresh yeast was used for a brew with an original gravity < 1.060 and the next brew is due to be carried out in less than 14 days"
step.newSubStep(("Fill the 2L Jar with boiling water, add the lid securely and set aside",{'complete':1}))
step.newSubStep(("Fill each of the 400ml jars with boiling water add the lid a set aside.",{'complete':1}))
step.newSubStep(("After 10 minutes add the 400ml jars into a cold water bath to cool the water",{'complete':1}))

#step = myprocessK.bottlingAndKegging.newstep("Sterilise Saucepan")
#step.text="Sterilise the saucepan, thermometer and slotted spoon, and measuring spoon by adding the equipment to the saucepan and filling with boiling water. Set aside for at least 15 minutes"



step = myprocessK.bottlingAndKegging.newstep("Fill bottles with sterilising solution")
step.text="Use 3/4 of a level teaspoon of sterilising solution in a full jug of warm water. (which equates to 1 level teaspoon per 3L)"
step.newSubStep(("Arrange bottles in a crate ready to sterilise",{'complete':1}))
step.addConsumable( sterilisingPowder,4)
step.addEquipment( saucepan )
step.addEquipment( funnel )
step.img=['bottlingseq.png']
step.text="The sterilising of bottles is carried out by filling each bottle full with a sterilising solution. The funnel will be sterilsing as the bottles are filled. "
step.auto="sterilisebottles"
step.newSubStep(("Immerse the little bottler in a bottle of sterilising solution rotate to ensure both ends are covered inside and out.",{'complete':1}))


step = myprocessK.bottlingAndKegging.newstep("Empty bottles")
step.img=['bottlingempty.png']
step.text="After 5 minutes begin to partially empty sterilising solution from the bottles filling any of the mini kegs, each mini keg.It is important to the make sure the top of the bottle is sterilised. Bottles should be half emptied, and then given a good shake before finishing emptying the bottle."
step.attention="If using mini kegs or polypins the sterilising solution should be reused for the mini kegs/polypins"
step.newSubStep(("The first two bottles should be emptitied into the large jug, this gives an opportunity to serilise the top of the bottle",{'complete':1}))
#step.newSubStep(("If using mini kegs empty the remaining bottles into the mini kegs. Each mini keg should be fully filled with sterilising solution. If there is not enough sterilising solution in the bottles additional solution needs to be made.",{'complete':1}))


step = myprocessK.bottlingAndKegging.newstep("Fill polypins with sterilising solution")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gather4"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"

step = myprocessK.bottlingAndKegging.newstep("Fill mini kegs with sterilising solution")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gather3"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"


step = myprocessK.bottlingAndKegging.newstep("Empty Polypins")
step.img=['bottlingempty.png']
step.condition=[]
step.auto="empty_polypin"
step.condition.append(['polypinqty','>',0])
step.text="Empty the sterilising solution from the polypins, using the taps"

step = myprocessK.bottlingAndKegging.newstep("Empty Minikegs")
step.img=['bottlingempty.png']
step.auto="empty_minikeg"
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Empty the sterilising solution from the minikegs, using the taps"


step = myprocessK.bottlingAndKegging.newstep("Rinse Bottles")
#step.img['bottlingrinse.png']
step.text="Bottles need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.attention="If using mini kegs/polypins the water should be empties into the minikegs/polypins"
step.newSubStep(("Fill each bottle with a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each bottle and empty the water.",{'complete':1}))


step = myprocessK.bottlingAndKegging.newstep("Rinse Polypins")
#step.img['bottlingrinse.png']
step.condition=[]
step.auto="rinse_polypin"
step.condition.append(['polypinqty','>',0])
step.text="Polypins need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  polypin a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each polypin and empty via the tap.",{'complete':1}))


step = myprocessK.bottlingAndKegging.newstep("Rinse Minikegs")
#step.img['bottlingrinse.png']
step.condition=[]
step.auto="rinse_minikeg"
step.condition.append(['minikegqty','>',0])
step.text="Minikegs need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  minikeg a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each minikeg and empty via the tap.",{'complete':1}))





	# need to think about removing this step if no stock of mini kegs available

step = myprocessK.bottlingAndKegging.newstep("Add priming solution to each bottle")
step.text="Stir the priming and then add 15ml of priming solution to each bottle"


step = myprocessK.bottlingAndKegging.newstep("Add priming solution to each polypin")
step.text="Stir the priming and then add 45ml of priming solution to each polypin"
step.auto="prime_polypin"
step.condition=[]
step.condition.append(['polypinqty','>',0])

step = myprocessK.bottlingAndKegging.newstep("Add priming solution to each minikeg")
step.auto="prime_minikeg"
step.text="Stir the priming and then add 120ml of priming solution to each minikeg"
step.condition=[]
step.condition.append(['minikegqty','>',0])


# Fill polypins kegs first
step = myprocessK.bottlingAndKegging.newstep("Fill Polypins")
step.condition=[]
step.auto="fill_polypin"
step.condition.append(['polypinqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The polypins should be filled with a little bottler, leaving half an inch of headspace."
step.newSubStep(("Fill each of the polypins. Add the tap and purge the remaining air ",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessK.bottlingAndKegging.newstep("Fill Mini Kegs")
step.condition=[]
step.auto="fill_minikeg"
step.condition.append(['miniqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The minikegs should be filled with a little bottler, leaving an inch of headspace."
step.newSubStep(("Fill each of the mini kegs",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessK.bottlingAndKegging.newstep("Fill bottles")
step.text="While filling it is useful to group the bottles by type to ensure even filling."
step.newSubStep(("Begin filling each bottle leaving an inch of space at the neck empty.",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"


step = myprocessK.bottlingAndKegging.newstep("Yeast Harvest Part 1")
step.text="To harvest the yeast the yeast cake is topped up with clean pre-boiled/sterilised water which will separate the yeast from the trub."
step.newSubStep(("Ensure any remaining beer not bottled is emptied carefully out of the fermentation bin, there should be very little (less than 200ml) beer remaining",{'complete':1}))
step.newSubStep(("Add 400ml of water to the yeast cake and stir gently",{'complete':1}))
step.newSubStep(("Remove the large spoon and let the fermentation bin settle for 1 hour",{'complete':1}))
step.img=["yeastcake1.png"]
step.attention="Sanitisation is very important while harvesting the yeast"


step = myprocessK.bottlingAndKegging.newstep("Attach Caps")
step.text="Once bottling has finished it is time to attach the caps."


step = myprocessK.bottlingAndKegging.newstep("Yeast Harvest Part 2")
step.text="The yeast from the fermentation bin will then be stored in the sterilised airtight container and set aside in the fridge"
step.newSubStep(("Fill the 2L jar with the solution from the fermentation bin, and then store in the fridge",{'complete':1}))
step.img=["yeastcake2.png"]
step.attention="Sanitisation is very important while harvesting the yeast. A label should be added to the jar to ensure the yeast is not used after 14 days,"

#ensure beer is removed without sucking up the yeast, 200ml beer on top is ok
#add 1L of water into bottom of fermentation bin.... swirl to ensure yeast is loose (or stir if we have the spoon in the bucket still).
#empty into 2L container.  straisfy
#

 # donosbourner.

step = myprocessK.bottlingAndKegging.newstep("Optional Secondary Conditioning")
step.text="If the ambient temperature is less than 18 degC it is a good idea to put the bottles into a water bath which can be heated to 20 degC. This ensures that the yeast has ideal conditions for working through the new fermenetables in the priming sugar"
step.attention="If using an aquarium heater in the water bath - it must always remain submerged. Ensure the water is at the correct temperature before adding bottles"
step.img=['secondarycondition.png']

step = myprocessK.bottlingAndKegging.newstep("Code bottles")
step.text="Ensure that the bottles can be identified, either via crown caps, labels etc. Once the beer is in condition full size labels may be added."
step.fields.append( ('Number of Bottles','numbottles','') )
step.fields.append( ('Number of Bottles (bad fills)','numbottlesbadfills','') )
step.fields.append( ('Number of MiniKegs','minikegs','') )
step.fields.append( ('Wastage in fermentation bin','fvpostbottlewastage','') )

step = myprocessK.bottlingAndKegging.newstep("Cleanup")
step.text="All equipment should be cleaned and left to dry before packing away for the next brewday"
step.attention="Ensure all equipment is completely dry before packing away."

step = myprocessK.bottlingAndKegging.newstep("Monitor Conditoning")
step.text="In the first si weeks it is necessary to check the progress of conditoning."
step.newSubStep(("After 1 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 2 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 3 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 4 sample beer 1, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 5 sample beer 2, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 6 sample beer 3, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))




myprocessK.save("process/allena29/40AG")
myprocessK.generateMySql()





#print "!!! SQL CODE TO INSERT NEW ITEM INTO gItems"
#print "i n s  e r t into gItems values(null,'test@example.com','consumable','','watertreatment','Salifert Alkaline Test','salifertalkalinetest''1','test',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,'','',0,0,0,0,'','',1,"",0,0,0,0)"



