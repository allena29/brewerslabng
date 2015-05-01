from __future__ import division


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

copperkettle=presets.getSupplier("Copper Kettle Homebrewing")

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


myprocess=brwlabProcess()
myprocess.credit="Adam Allen"

myprocess.name="9AG3i4"
myprocess.description="A process designed for small batches in a domestic environment with 2 stove top 'copper' boilers"

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

plasticbottles=presets.getConsumable("500ml plastic bottle")
plasticbottles.volume=475
plasticbottles.caprequired=0
plasticbottles.category="bottle"
plasticbottles.fullvolume=500
bottlebrush=presets.getEquipment("Bottle Brush")

purchase=brwlabPurchase(pfte)
purchase.qty=24
purchase.price=0.085
stores.addPurchase( purchase )


latstockfloat=presets.getEquipment("Latstock Float")
latstockfloat.mustSterilise=1
latstockfloat2=presets.getEquipment("Latstock Float")
latstockfloat2.mustSterilise=1
tap_with_tubing=presets.getEquipment("Tap with syphon tube")
tap_with_tubing.mustSterilise=1
tap_with_tubing2=presets.getEquipment("Tap with syphon tube")
tap_with_tubing2.mustSterilise=1
hlt=presets.getEquipment("Hot Liquor Tank")
hlt.image="images/hlt.png"
hlt.mustSterilise=1
hlt.heatPower=1.6
hlt.description="A Hot Liquor Tank is used to heat water."
hlt.instructions="A Hot Liquor Tank can be made from a fermentation bin with electric kettles installed."
hlt.dead_space=3.5
hlt.subEquipment.append( tap_with_tubing )
hlt.subEquipment.append( tap_with_tubing2 ) 
hlt.subEquipment.append( latstockfloat )
hlt.subEquipment.append( latstockfloat2 )

jug=presets.getEquipment("Jug (1.5L)")
jug.mustSterilise=1
saucepan=presets.getEquipment("Saucepan")
bottler=presets.getEquipment("Little Bottler")
funnel=presets.getEquipment("Funnel")
syringe=presets.getEquipment("2.5ml Syringe")


scavengertube=presets.getEquipment("Scavenger Tube")
scavengertube.mustSterilise=1
mash_tun_tap=presets.getEquipment("Mash Tun Tap")
mash_tun_tap.mustSterilise=1

mash_tun=presets.getEquipment("Mash Tun")
mash_tun.mustSterilise=1
mash_tun.dead_space=2.25
mash_tun.subEquipment.append( mash_tun_tap )
mash_tun.subEquipment.append( scavengertube )

largepaddle=presets.getEquipment("Large Paddle")
largepaddle.mustSterilise=1
storagebox=presets.getEquipment("Storage Box")
storagebox.mustSterilise=1
thermometer=presets.getEquipment("Digital Thermometer")
thermometer.mustSterilise=1
atc800=presets.getEquipment("ATC800+ Temperature Controller")
atc800.mustSterilise=1
wastebox=brwlabEquipment("Waste Container")
wastebox.text ="The waste box is used for collecting sterilising solution/rinse water. After sterilising the mash equipment it can be considered sterile."

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

kettle70l =presets.getEquipment("70l Kettle")
kettle70l.volume=70
kettle70l.mustSterilise=1
kettle70l.dead_space=2		# estimate 30/1/2010
kettle70l.boilVolume=60
kettle20l =presets.getEquipment("20l Kettle")
kettle20l.volume=20
kettle20l.mustSterilise=1
kettle20l.dead_space=1.25		# estimate 30/1/2010
kettle20l.boilVolume=14
kettle15l =presets.getEquipment("15l Kettle")
kettle15l.volume=15
kettle15l.mustSterilise=1
kettle15l.dead_space=1.25	# estimate 30/1/2010.
kettle15l.boilVolume=12
myprocess.boilers = [kettle20l,kettle15l,kettle70l]

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
		# some of the need to tip the feremntation might be due to using the WRONG attribute name here
		# it shoul dead_space not deadspace.
		# The default used from brewerslab calculte was 2 litres so we will use that even though it 	
		# should hvae been 3.34. There is a new fermentation bin in town now so it doesn't make a huge difference
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
stores.addPurchase( brwlabPurchase(sterilisingPowder, 50, 0.0595) )

stores.addPurchase( brwlabPurchase(plasticbottles,40,0.06))		# making bottle cost 0.06 to cover wastage
stores.addPurchase( brwlabPurchase(bottles,85,0.06))		# making bottle cost 0.06 to cover wastage

stores.addPurchase( brwlabPurchase(crowncaps,80,0.019))
stores.addPurchase( brwlabPurchase(crowncaps,100,0.019))








##################################################################################################################################################### Brew Day

# Equipment / Process Binding
myprocess.hlt = hlt
myprocess.mash_tun = mash_tun


# Clean work area
step = myprocess.brewday.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before commencing the brew day"


# Gather things
step = myprocess.brewday.GatherThings()


# Clean Equipment
step = myprocess.brewday.newstep("Clean Equipment")
step.text="Clean equipment with a mild detergent. It is important to clean equipment to ensure any dirt is removed before sterilisation."
step.addEquipment( hlt )
step.addEquipment( atc800) 
step.addEquipment( sparge_arm )
step.addEquipment( mash_tun )
step.addEquipment( jug ) # try do without a jug
step.addEquipment( largepaddle )
step.addEquipment( thermometer )
#step.addEquipment( kettle20l )
#step.addEquipment( kettle15l )



# Setup Equipment
step = myprocess.brewday.newstep("Setup Equipment")
step.text="The hot liquor tank must be positioned higher than the mash tun with the sparge arm assembled. The brewing kettle is positoned the lowest."
step.newSubStep( ("Setup the equipment as pictured",{'complete':1}) )
step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to 82degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))
step.img=["sterilise_setup1.png"]

# Sterilise Equipment
step = myprocess.brewday.newstep("Sterilise Equipment - Part 1")
step.text="It is important throughout the brew day to ensure that equipment which comes into contact with the wort is sterilised. This step focuses on the equipment to get the mashing underway."
step.newSubStep( ("Add the jug, large paddle and digital thermometer probe to the hlt and ensure it is sterilised",{'complete':1}))
step.newSubStep( ("Attach two taps to the hlt, and add the latstocks floats to the inside taps. Attach the temperature probe to one of the floats. Attach the syphon tubes with taps to the outside of the hlt taps.",{'complete':1}) )
step.newSubStep( ("Add 10 litres of warm water and 2 tsp of sterilising powder to the hot liquor tank. Ensure all surfaces of the hot liquor tank are soaked in sterilising solution.", {'complete':1}))
step.newSubStep( ("Drain sterilsing solution from the hot liquor tank into the mash tun via the sparge arm. (Note: internal latstock floats and two external syphon tubes should also be used).", {'complete':1}) )
step.newSubStep( ("Ensure all surfaces of the mash tun and inner lauter-tun are washed well with sterilising solution.", {'complete':1}) )
step.newSubStep( ("Drain sterilising solution from the mash tun and discard", {'complete':1}) )
#step.auto="sterilise"	# this sterilises everything
step.addConsumable( sterilisingPowder, 2)


# Rinse equipment
step = myprocess.brewday.newstep("Rinse Equipment")
step.text="Rinse Equipment in the same way as sterilsing, equipment should be rinsed with 25 litres of cold water."


# Mash
step = myprocess.brewday.newstep("Get Ready to Mash")
step.text="During the mash the complex starches into simple sugars suitable for fermentation. During mashing temperature control is important but an insulated mash tun will not change significantly over an hour."
step.newSubStep( ("Fill the hot liquor tank with ...sparge_water...L of water for the sparging", {'complete':1}))
step.attention="Do not turn on the temperature controller until the elements in the kettle are covered with water."


# Fill the Mash Tun
step = myprocess.brewday.newstep("Fill the mash tun with mash liquid. During this step the mash tun should be well insulated.")
step.newSubStep( ("Fill the mash tun with  ...mash_liquid...L of water heated to ...strike_temp_5...C. The water will take approximately ...sparge_heating_time... minutes to heat", {'complete':1}) )
step.newSubStep( ("Set aside the grain ready to stir into the mash tun when the temperature reduces to ...strike_temp...", {'complete':1}) )
step.newSubStep( ("Set aside 1.7L of boiling water and 1.7L of cold water which may optionally may be used for adjustment of temperature.", {'complete':1}))
step.attention="If the grain temperature is not within 15-20 degC then the calculations should be re-run to provide a hotter/colder strike temp."
step.img=["mash_setup.png"]


# Dough in the grain 
step = myprocess.brewday.newstep("Dough in the grain")
step.text="The temperature for mashing is important high temperatures will lead to extraction of tannins, low temperatures will not provide efficient conversion. Try: An optional sterilised spoon tied to a mixer with plastic ties may be used to save mixing"
step.newSubStep( ("With the temperature of the mash liquid at ...strike_temp...C stir in the grain.", {'complete':1}))
step.newSubStep( ("The aim is to mash at a temperature of ...target_mash_temp...C. If the temperature difference is +/- 3degC then an adjustment may be carried out.\n", {'complete':1}))
step.newSubStep( ("If satisifed with the temperature then cover and set aside for 60 minutes.",{'complete':1,'timer':3600}))
step.addEquipment( timer )
step.attention="The Temperature of the Grain Bed should remain below 75degC throughout"


# Fill the HLT 
step = myprocess.brewday.newstep("Fill the HLT and begin heating")
step.text="Fill the HLT with ...sparge_water... L of sparge water. The sparge water is expected to take around ...sparge_heating_time... minutes to heat."
step.attention="The HLT is constructed with standard kettle elements, therefore it is advisable to alternate between the elements 3 or 4 times during the heating. The temperature controller should only power one kettle element at any time."


# Begin sterilising remaining equipment
step = myprocess.brewday.newstep("Sterilise Part 2")
step.text="It is important throughout the brew day to ensure that equipment which comes into contact with the wort is sterilised. This step focuses on the equipment needed after the mashing."
step.newSubStep( ("Fill the large kettle with 15 litres of warm water and 3 tsp of sterilising powder.",{'complete':1}))
step.newSubStep( ("Add the thermometers, hydrometer and trial jar, slotted spoon, optional immersion heater, and small jug to the kettle. Ensure that all sides of the large kettle are rinsed",{'complete':1}))
step.newSubStep( ("Ensure all surfaces and equipment are well covered with sterilising solution (including lids). Then drain the solution from the 20l kettle into the 15l kettle",{'complete':1}))
step.newSubStep( ("Leave the sterilisng solution for a few minutes in the 15l kettle, then ensure all surfaces are covered before draining into the fermentation bin",{'complete':1}))
step.newSubStep( ("Leave the sterilisng solution for a few minutes in the fermentation bin, then ensure all surfaces are covered before discarding",{'complete':1}))
step.addEquipment( kettle15l )
step.addEquipment( kettle20l )
step.addEquipment( smalljug )
step.addEquipment( fermentationbin )
step.addEquipment( hydrometer )
step.addEquipment( slottedspoon )
step.addEquipment( thermometer3 )
step.addEquipment( thermometer2 )
step.addEquipment( immersionheater )

# Rinse Equipment
step = myprocess.brewday.newstep("Rinse Equipment")
step.text="Rinse Equipment in the same way as sterilising, equipment should be rinsed wiht 25 litres of cold water."


# Ensure Sparge Water is at the correct temperature
step = myprocess.brewday.newstep("Assemble Sparge Setup and begin Recirculation")
step.text="Once the sparge water is at the correct temperature ...sparge_temp...C the sparge setup can be setup. During this step the cloudy wort with bits of grain will drained leading to a natural grain filter forming."
step.newSubStep( ("Take off the lid from the mash tun and assemble the sparge arm",{}))
step.newSubStep( ("Allow up to 6 litres of wort to drain from the mash tun into the kettle, the wort should be carefully added back to the top of the lauter tun trying to ensure minimal disturbance.",{'complete':1}))


# Start Sparge
step = myprocess.brewday.newstep("Start Fly Sparging")
step.text="Sparging will drain the sugar from the grain providing us with wort. The process of sparging should be carried out slowly. The aim is to keep an inch of water above the top of the grain bed throughout the process."
step.newSubStep( ("Begin draining the wort from the mash tun, once there is 1 inch of water above the top of the grain bed start allowing water from the hot liquor tun (HLT) slowly",{'complete':1}))
step.newSubStep( ("After the sparge volume is reached or the gravity of the runoff is below 1.006 then stop sparging. Transfer some of the early runoff's from the 20l kettle into the 15l kettle so that the volumes are roughly equal",{'complete':1}))
step.attention="It is important the wort is not retained once it drops below 1.006. As the wort will be higher than 20degC during the sparging this gives some safey margin (between 30-40 deg the reading will be 3-7 points lower than the hydrometer)"
#Throughout the process monitor flow of liquid into and out of the mash tun to try maintain an equilibrium"


# Dynamic Recipe Adjustment.
step = myprocess.brewday.newstep("Dynamic Recipe Adjustment")
step.text="If the mash was particularly efficent/inefficient it may be desirarble to top up fermentables, dilute wort, increase/decrease hop quantities."
step.auto="dynamicrecipeadjustment"


# Bring the wort to the boil
step = myprocess.brewday.newstep("Bring the Wort to the boil")
step.text="Boiling the wort extracts bitterness and aroma from the hops, driving off unwanted volatile components, coagulates proteins,  and sanitising the wort for fermentation"


# Measure Hops
step = myprocess.brewday.newstep("Measure Hops")
step.text="Measure the hops and place aside ready to add during the boil."
step.auto="hopmeasure"


# Bring the wort to the boil
step = myprocess.brewday.newstep("Hop Additions")
step.text="Boiling the wort extracts bitterness and aroma from the hops"
step.newSubStep(("Once the wort has reached a good rolling boil leave the lids half covering the stock pot.",{'complete':1}))
step.addConsumable(protofloc,1)

step.auto="hopaddition" # implicit fining's and immersion chiller


# Yeast Rehydration
step = myprocess.brewday.newstep("Boil Yeast Rehydration Water")
step.text="Rehydration yeast prvoides a gentle start for the yeast and helps fermentation start quickly."
step.newSubStep(("Boil 500ml of water and set aside in a pyrex jug",{'complete':1}))
step.newSubStep(("After 10 minutes put the hug in a water bath to cool the water to 25 degC",{'complete':1}))
step.attention="Yeast should nto be added to the rehydration water unless is is <25 degC"


# Drain Wort
step = myprocess.brewday.newstep("Drain wort into the fermentation bin")
step.text="Transfer wort into the fermentation bin"
step.newSubStep(("Begin transfering the wort into the fermentation bin trying to minimise aeration.",{'complete':1}))
step.newSubStep(("Setup the immersion chiller and and start pushing cold water through to cool the wort to 20 degC",{'complete':1}))
step.newSubStep(("Add half of the yeast contents to the rehydration water",{'complete':1}))
step.attention="While draining the wort into the fermentation bin do not aerate the wort while it is hot. Aeration should happen once the wort is at pitching template"



# Measure
step = myprocess.brewday.newstep("Measure")
step.text="Recording results is important to track the quality of the brew. The expected original gravity is ...estimated_og... "
step.newSubStep(("Aerate the wort for 5 minutes",{'complete':1}))
step.newSubStep(("After aerating the wort measure take a sample to measure the original gravity.",{'complete':1}))
step.fields.append( ('Original Gravity','og','') )
step.fields.append( ('Fermentation bin Weight','postboilweight','') )


# Pitch
step = myprocess.brewday.newstep("Pitch Yeast")
step.newSubStep(("Once the wort is at pitching temperature (20degC) measure the original gravity with a hydrometer and record. If using yeast slurry then measure 400ml of slurry assuming batch size is 6days old. Before using yeast slurry a check on the progress/health of fermentation from the previous batch is required. If using yeast slurry see http://mrmalty.com/calc/calc.html",{'complete':1}))
step.attention="The temperature must be stable at pitching temperature (i.e. 20deg). Once the yeast is pitched oxygen must not be introduced into the beer - nor any unsterilised equipment"
step.newSubStep(("Add 1/2 teaspoon of yeast vit",{'complete':1}))
step.newSubStep(("Optionally add an immersion heater set for 18degC",{'complete':1}))
step.newSubStep(("Pitch the yeast",{'complete':1}))




###########################
#Post Brew Day


step = myprocess.postbrewday.newstep("Kraussen")
step.text="Checking for signs of fermentation begining such ass a temperature rise, or the kraussen (yeast crust forming on top of the wort). "


step = myprocess.postbrewday.newstep("Measure specific gravity (1st)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 1 (1.xxx)','sg1',''))


step = myprocess.postbrewday.newstep("Measure specific gravity (2nd)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 2 (1.xxx)','sg2',''))


step = myprocess.postbrewday.newstep("Measure specific gravity (3rd)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 3 (1.xxx)','sg3',''))


step = myprocess.postbrewday.newstep("Measure specific gravity (4th)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 4 (1.xxx)','sg4',''))




#########################
# Bottling Day

# Empty the wort into the fermentation bin:sp
# 
# Empty Wort into the brewing 

#step.attention="temperature may need to be raised >82degC depending on the loss so that the grain bed is 73 degC. The water in the ATC800 is set to 82... initial plan was 77degC. JBK thread recommends 85degC plus monitoring. will go for 82 for now"

#Continuous Sparging usually results in better extractions. The wort is re-circulated and drained until about an inch of wort remains above the grain bed. The sparge water is gently added, as necessary, to keep the fluid at least at that level. The goal is to gradually replace the wort with the water, stopping the sparge when the gravity is 1.008 or when enough wort has been collected, whichever comes first. This method demands more attention by the brewer, but can produce a higher yield.

#http://www.jimsbeerkit.co.uk/forum/viewtopic.php?f=2&t=16963&start=0&st=0&sk=t&sd=a
#75 deg C


######################################### Bottling / Kegging Day


step = myprocess.bottlingAndKegging.GatherThings()


step = myprocess.bottlingAndKegging.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before starting with bottling."
step.addEquipment(bottlebrush)
step.addEquipment(hydrometer)
step.addEquipment(trialjar)
step.addEquipment(slottedspoon)
step.addEquipment(saucepan)
step.addEquipment(thermometer2)
step.addEquipment(smalljug)
step.addEquipment(jug)
step.addEquipment(bottler)
step.addEquipment(measuringspoon)


step = myprocess.bottlingAndKegging.newstep("Setup Work Area")
step.text="Setup the work area as shown in the image, cleaning the bottles may be carried out the previous evening to save time."
step.img=["bottlingsetup.png"]


step = myprocess.bottlingAndKegging.newstep("Clean Bottles")
step.text="Cleaning the bottles using hot water and detergent."
step.newSubStep(("Clean the bottles using a bottle brush to ensure no deposits are left in the bottle. Drain solution out of the bottles.",{'complete':1}))
step.newSubStep(("Rinse the bottles with a small amount of water.",{'complete':1}))


step = myprocess.bottlingAndKegging.newstep("Setup Work Area 2")
step.text="Setup the work area as show in the image, during the bottling stage all equipment will be required."
step.img=["bottlingsetup2.png"]


step = myprocess.bottlingAndKegging.newstep("Sterilise Crown Caps")
step.text="Crown caps needs to be sterilised before use."
step.newSubStep(("Boil 500ml of water and add to a clean pyrex jug",{'complete':1}))
step.newSubStep(("Add ...num.crown.caps... to the jug and set aside.",{'complete':1}))


step = myprocess.bottlingAndKegging.newstep("Prepare Sterilising Solution")
step.text="Prepare sterilisng solution and arrange bottles in rows of 7 bottles"
step.newSubStep(("Arrange bottles in rows of 7.",{'complete':1}))
step.newSubStep(("Prepare sterilising solution by mixing 2 tsp in 2 litres of warm water",{'complete':1}))
step.newSubStep(("Immerse the little bottler in the jug of sterilising solution, ensure the sterilising solution reach all parts of the little bottler.",{'complete':1}))
step.addConsumable( sterilisingPowder,4)
step.addEquipment( saucepan )
step.addEquipment( funnel )


step = myprocess.bottlingAndKegging.newstep("Fill bottles (Cycle 1)")
step.img=['bottlingseq.png']
step.text="The sterilising of bottles is carried out by filling the bottles in sequence."
step.newSubStep(("Fill the first row of bottles with sterilising solution from the first jug",{'complete':1}))
step.newSubStep(("Prepare sterilising solution by mixing 2 tsp in 2 litres of warm water",{'complete':1}))
step.newSubStep(("Fill the second row of bottles with sterilising solution from the second jug",{'complete':1}))
step.newSubStep(("Empty the sterilising solution from the first row of bottles into the 3rd row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Empty the sterilising solution from the second row of bottles into the 4th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Empty the sterilising solution from the third row of bottles into the 5th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Optional: Empty the sterilising solution from the fourth row of bottles into the 6th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Empty sterilising solution from all bottles into the saucepan (with the thermometer, meuasing and slotted spoon)",{'complete':1}))


step = myprocess.bottlingAndKegging.newstep("Fill bottles (Cycle 2)")
step.text="This time the sequence of bottles is revesed so that the first row is the only 5th/6th row."
step.newSubStep(("Fill the first row of bottles with sterilising solution from the first jug",{'complete':1}))
step.newSubStep(("Prepare sterilising solution by mixing 2 tsp in 2 litres of warm water",{'complete':1}))
step.newSubStep(("Fill the second row of bottles with sterilising solution from the second jug",{'complete':1}))
step.newSubStep(("Empty the sterilising solution from the first row of bottles into the 3rd row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Empty the sterilising solution from the second row of bottles into the 4th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Empty the sterilising solution from the third row of bottles into the 5th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Optional: Empty the sterilising solution from the fourth row of bottles into the 6th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in sterilising solution.",{'complete':1}))
step.newSubStep(("Empty sterilising solution from all bottles into the saucepan (with the thermometer and saucepan)",{'complete':1}))


step = myprocess.bottlingAndKegging.newstep("Rinse bottles (Cycle 1)")
step.text="The rinsing of bottles is carried out in the same way as the sterilising"
step.newSubStep(("Fill the first row of bottles with clean water from the first jug",{'complete':1}))
step.newSubStep(("Fill the second row of bottles with clean water from the second jug",{'complete':1}))
step.newSubStep(("Empty the water from the first row of bottles into the 3rd row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water solution.",{'complete':1}))
step.newSubStep(("Empty the water from the second row of bottles into the 4th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water solution.",{'complete':1}))
step.newSubStep(("Empty the water from the third row of bottles into the 5th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water.",{'complete':1}))
step.newSubStep(("Optional: Empty the water from the fourth row of bottles into the 6th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water.",{'complete':1}))
step.newSubStep(("Empty water from all bottles into the saucepan (with the thermometer and saucepan)",{'complete':1}))


step = myprocess.bottlingAndKegging.newstep("Rinse bottles (Cycle 2")
step.text="This time the seequence of bottles is revrsed so the first row is now the 5th/6th row from the previous step"
step.newSubStep(("Fill the first row of bottles with clean water from the first jug",{'complete':1}))
step.newSubStep(("Fill the second row of bottles with clean water from the second jug",{'complete':1}))
step.newSubStep(("Empty the water from the first row of bottles into the 3rd row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water solution.",{'complete':1}))
step.newSubStep(("Empty the water from the second row of bottles into the 4th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water solution.",{'complete':1}))
step.newSubStep(("Empty the water from the third row of bottles into the 5th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water.",{'complete':1}))
step.newSubStep(("Optional: Empty the water from the fourth row of bottles into the 6th row of bottles, shake each bottle before emptying, and make sure the neck of the upturned bottle is covered in water.",{'complete':1}))
step.newSubStep(("Empty water from all bottles into the saucepan (with the thermometer and saucepan)",{'complete':1}))


step = myprocess.bottlingAndKegging.primingSolution()
step.text="Priming solution provides more fermentables for the yeast to convert into further alcohol and natural carbonation"
step.newSubStep(("Measure ...primingsugartotal... (...primingsugarqty... per bottle) priming sugar and set aside.",{'complete':1}))
step.newSubStep(("Add ...primingwater... ml of water to the saucepan and heat to 90degC",{'complete':1}))
step.newSubStep(("Maintain the temperature at 85degC for 5 minutes and then cool in a water bath to less that 30 degC.",{'complete':1}))
step.attention="Be careful with the volume of sugar in each bottle as introducing too many fermentables can lead to exploding bottles"


step = myprocess.bottlingAndKegging.newstep("Add priming solution to each bottle")
step.text="Stir the priming and then add 15ml of priming solution to each bottle"


step = myprocess.bottlingAndKegging.newstep("Fill bottles")
step.text="While filling it is useful to group the bottles by type to ensure even filling"
step.newSubStep(("Begin filling each bottle leaving an inch of space at the neck empty. Rest a crown cap on the bottle as soon as it is full and set aside ",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"


step = myprocess.bottlingAndKegging.newstep("Attach Caps")
step.text="Once bottling has finished it is time to attach the caps."


step = myprocess.bottlingAndKegging.newstep("Optional Secondary Conditioning")
step.text="If the ambient temperature is less than 18 degC it is a good idea to put the bottles into a water bath which can be heated to 20 degC. This ensures that the yeast has ideal conditions for working through the new fermenetables in the priming sugar"


step = myprocess.bottlingAndKegging.newstep("Labels bottles")
step.text="Ensure that the bottles can be identified, either via crown caps, labels etc. Once the beer is in condition it full size labels may be added"


step = myprocess.bottlingAndKegging.newstep("Cleanup")
step.text="All equipment should be cleaned and left to dry before packing away for the next brewday"





#
#
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
#
#
#	Recipe
#
#
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
#
#
suffolkredblonde = brwlabRecipe()

suffolkredblonde.process = myprocess

suffolkredblonde.batch_size_required=15
suffolkredblonde.boil_time=60

# Note: at this stage could use percentages instead of actual weights.
# if using percentages make sure scaleAlcohol() is called before calculate()
# and before checkStockAndPrice()

suffolkredblonde.addFermentable(marisOtter,3000)
suffolkredblonde.addFermentable(biscuit,250)
suffolkredblonde.addFermentable(goldensyrup,100)

# Note: at this stage could use percentages instead of actual weights.
# if using percentages make sure scaleHops() is called before calculate()
# and before checkStockAndPrice()

suffolkredblonde.addHop(cascade,20, hopAddition=60)
suffolkredblonde.addHop(saaz,15, hopAddition=15)
suffolkredblonde.addHop(saaz,5, hopAddition=5)


# Not quite decided if to move everything into the process!
# or maybe implement a method that allows for items to be taken from the process
suffolkredblonde.addYeast(safale04,1)





if suffolkredblonde.attachProcess( myprocess ) < 1:
	print "Process cannot be used"

# Scale Hops should have a process bound
# Hops are based on the final volume so shouldn't need to recalculate 
#suffolkredblonde.scaleHops( 25 )

# Scale ABV should have a process bound
# Scales Alcohol By Volume
#suffolkredblonde.scaleAlcohol( 4 )

#suffolkredblonde.addIngredient(water, suffolkredblonde.waterRequirement() )
		#addIngredient alias for everything





#
# Calculate the Recipe
# Outputs lot's of information to stderr
#
#

#suffolkredblonde.calculate()

# Scale Alcohol 




(cost,stock) = stores.checkStockAndPrice( suffolkredblonde)

#if len(stock['__out_of_stock__']) == 0:
#	sys.stderr.write("Enough stock for recipe\n")
##else:
##	sys.stderr.write("Not enough stock for recipe\n")
#	for x in stock['__out_of_stock__']:
#		print x,stock['__qty_available__'][x],stock['__qty_required__'][x]
#
#print "Cost of recipe %.2f\n" %(cost['__total__'])



#styleAdvice = suffolkredblonde.findStyle()
#print styleAdvice['styles'][0]['stylename']
	

#mash=brwlabMash()
#print mash.getStrikeTemperature()


suffolkredblonde.attachProcess( myprocess ) 
#	print "Process cannot be used"


#suffolkredblonde.calculate()

our_stock=stores.takeStock(suffolkredblonde)
#(cost,stock) = stores.checkStockAndPrice( suffolkredblonde)





thegoosegrain = brwlabRecipe()
thegoosegrain.credit="Adam Allen"
thegoosegrain.name="The Gold Goose"
thegoosegrain.description=""
thegoosegrain.description="A copy of 'White River Goose' but using Cascade in place of Centennial and Caragold instead of a Caramalt. The golden syrrup is replaced by a bigger malt content"
thegoosegrain.process = myprocess

thegoosegrain.batch_size_required=17
#thegoosegrain.batch_size_required_plus_wastage=20
thegoosegrain.boil_time=60

# Note: at this stage could use percentages instead of actual weights.
# if using percentages make sure scaleAlcohol() is called before calculate()
# and before checkStockAndPrice()

thegoosegrain.addFermentable(marisOtter,2950)
thegoosegrain.addFermentable(caragold,500)
thegoosegrain.addFermentable(torrifiedwheat,250)
#thegoosegrain.addFermentable(goldensyrup,100)
thegoosegrain.addFermentable(honey,200)

# Note: at this stage could use percentage WEIGHTS instead of actual weights.
# if using percentages make sure scaleHops() is called before calculate()
# and before checkStockAndPrice()
# or we could set the weight to 0 and instead send hopIBU and leave
# calculate to translate it into a weight

thegoosegrain.addHop(cascade, 0, hopAddition=60,hopIBU=17)		# substitute for centennial

thegoosegrain.addHop(cascade,0, hopAddition=15,hopIBU=9.7)		# substitute for centennial
thegoosegrain.addHop(glacier,0, hopAddition=15,hopIBU=7.7)	
thegoosegrain.addHop(hallertauhersbrucker,0, hopAddition=15,hopIBU=2.7)	

thegoosegrain.addHop(cascade,0, hopAddition=5,hopIBU=2.3)		# substitute for centennial
thegoosegrain.addHop(glacier,0, hopAddition=5,hopIBU=1.1)	
thegoosegrain.addHop(hallertauhersbrucker,0, hopAddition=5,hopIBU=0.8)	


thegoosegrain.addHop(hallertauhersbrucker,10, hopAddition=0.001)	

# Not quite decided if to move everything into the process!
# or maybe implement a method that allows for items to be taken from the process
thegoosegrain.addYeast(safale04,1)



# Adjustment for efficiency should be carried out after adding the grain
# and before any other adjustment methods are called
thegoosegrain.adjustMashEfficiency(67, [marisOtter,caragold])
 



if thegoosegrain.attachProcess( myprocess ) < 1:
	print "Process cannot be used"

thegoosegrain.calculate()
# Scale Hops should have a process bound
# Hops are based on the final volume so shouldn't need to recalculate 
thegoosegrain.scaleHops( 40.0 )

thegoosegrain.calculate()


# Scale ABV should have a process bound
# Scales Alcohol By Volume
#thegoosegrain.scaleAlcohol( 4 )

thegoosegrain.addIngredient(water, thegoosegrain.waterRequirement() )





#
# Calculate the Recipe
# Outputs lot's of information to stderr
#
#

thegoosegrain.calculate()

# Scale Alcohol 



# this could be extended in the future to deal with the age of hops 
thegoosegrain.adjustHopAlphaQty(stores)



# this isn't ideal but allows us to tweaks the hops used.
# turns out we did have 80g of cascade after all
#for x in thegoosegrain.hops_by_addition[ 60 ]:	
#	thegoosegrain.hops_by_addition[60][x] = thegoosegrain.hops_by_addition[60][x]-0.8
#(h,q) = thegoosegrain.hops[0]
#thegoosegrain.hops.remove( (h,q) )
#thegoosegrain.hops.append( (h,q-0.8) )


#sys.exit(0)


thegoosegrain.calculate()



(cost,stock) = stores.checkStockAndPrice( thegoosegrain)







if len(stock['__out_of_stock__']) == 0:
	print "Enough stock for recipe\n" 
else:
	print "Not enough stock for recipe\n"
	for x in stock['__out_of_stock__']:
		print x,stock['__qty_available__'][x],stock['__qty_required__'][x]

#print "Cost of recipe %.2f\n" %(cost['__total__'])



styleAdvice = thegoosegrain.findStyle()
if len(styleAdvice):	
	if len(styleAdvice['styles']):	print styleAdvice['styles'][0]['stylename']
#if len(styleAdvice):	if len(styleAdvice['styles']):	if styleAdvice['styles'][0].has_key("styleName"):	print styleAdvice['styles'][0]['stylename']
	


if thegoosegrain.attachProcess( myprocess ) < 1:
	print "Process cannot be used"

#print stores.dumpStore()

if not os.path.exists("store/%s" %(userid)):	os.mkdir("store/%s" %(userid))
if not os.path.exists("presets/%s" %(userid)):	os.mkdir("presets/%s" %(userid))
if not os.path.exists("recipes/%s" %(userid)):	os.mkdir("recipes/%s" %(userid))
if not os.path.exists("process/%s" %(userid)):	os.mkdir("process/%s" %(userid))
#presets.save()


#print stock['__qty_available__']
#sys.exit(0)

myprocess.priming_sugar = sugar

our_stock = stores.takeStock(thegoosegrain)
#print "our_stock"
#for z in our_stock['consumables']:
#	print z,"\n\t",our_stock['consumables'][z]
#sys.exit(0)

(cost,stock) = stores.checkStockAndPrice( thegoosegrain )
#print "___"
#for x in our_stock['consumables']:
#	print x
#a=5/0


#myprocess.compile( suffolkredblonde )
#myprocess.compile( thegoosegrain , stores )

thegoosegrain.save("recipes/%s/testRecipe_the_gold_goose" %(userid))

#suffolkredblonde.save("recipes/allena29/a_pair_of_pairs")


suffolkredblonde.attachProcess( myprocess )



#myprocess.save("process/%s/%s" %(userid,myprocess.name))


# Brewlog is a place where we can gather things together
brewlog = brwlabBrewlog(myprocess,thegoosegrain)
brewlog.name="Gold Goose AG Attempt 2"
brewlog.stock = our_stock

#myprocess.compile( suffolkredblonde )
#myprocess.compile( thegoosegrain, brewlog)

#print myprocess.dump()
#myprocess.save("process/%s/%s" %(userid,myprocess.name))
#thegoosegrain.save("recipes/allena29/the_gold_goose")


#suffolkredblonde.calculate()
#suffolkredblonde.save("recipes/allena29/a_pair_of_pairs")


"""
for stocktype in ['fermentables','hops','yeast','misc','consumables','ingredients']:
	print stocktype
	for uid in stock[stocktype]:	
		if uid != "__total__":
			(ingtype,ingname) = uid
			
			print " %.2f %% (%.1f) %s "  %( ((stock[ stocktype ][ uid ] / stock[ stocktype ]['__total__']) * 100 ), stock[ stocktype ][uid], ingname  )
"""
myprocess.compile( thegoosegrain, brewlog)


#print thegoosegrain.calclog

#print myprocess.dump()
#print thegoosegrain.dump()


haveStock="Stock Missing %s" %(stock['__out_of_stock__'])
if not len(stock['__out_of_stock__']):	haveStock="Stock Available"
#print " ABV %.2f OG %.4f FG %.4f EBC %d IBU %.2f Water %.1f (Sparge %.1f/Mash %.1f) Cost %.2f %s" %(thegoosegrain.estimated_abv, thegoosegrain.estimated_og, thegoosegrain.estimated_fg, thegoosegrain.estimated_ebc, thegoosegrain.estimated_ibu,thegoosegrain.water_required,thegoosegrain.sparge_water,thegoosegrain.mash_liquid,00,haveStock)
















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




myprocessF=brwlabProcess()
myprocessF.credit="Adam Allen"
myprocessF.name="24AG22i23"


myprocessF.description="A new process with a 70l boiler"

myprocessF.boilers = [kettle70l]
myprocessF.hlt = hlt
myprocessF.mash_tun = mash_tun




# Preparation
step = myprocessF.brewday.newstep("Preparation")
step.newSubStep( ("If using a fermentation-fridge move it into position, it is necessary to wait >12 hours after moving the fridge before using.",{'complete':1}) )
step.newSubStep( ("Add ice-boxes to the freezer, these will be used to cool the immersion chiller water",{'complete':1}) )
step.newSubStep( ("Ensure batteries for thermometers are available",{'complete':1}))
step.newSubStep( ("Ensure clean towells are available as well as clean dry cloths for the floor",{'complete':1}))
step.text="The day before brew day the preparation above should be carried out, as well as checking stock/ingredients are available"



# Gather things
step = myprocessF.brewday.newstep("Assemble Mash/Lauter Tun")
step.text="Assemble the bucket in bucket mash tun, complete with scavenger tube. Gather Sparge Arm, Vorlauf Funnel Paddle and digital thermometer."
step.img=['assemblemashtun.png']

# Gather things
step = myprocessF.brewday.newstep("Assemble Hot Liquor Tank")
step.text="Assemble the hot liquor tank, complete with latstock and ATC800+ thermometer probe"
step.img=['assemblehlt.png']

# Gather things
#step = myprocessF.brewday.newstep("Assemble Kettle")
#step.text="Assemble the kettles with ball-valve tap. Use a stainless steel washer on the inside and pfte tape around thread. "
#step.img=['assemblekettle.png']

# Gather things
step = myprocessF.brewday.newstep("Assmeble Fermentation Bin")
step.text="Assemble the fermentation bin, complete with back filter"
step.img=['assemblefv.png']


# Gather things
step = myprocessF.brewday.newstep("Gather small stockpots")
step.text="Gather small stockpots and measuring spoons, these will be used to contain the grain"



## Gather things
#step = myprocessF.brewday.GatherThings()
#step.text="The grain can be measured later"

# Clean Equipment
step = myprocessF.brewday.newstep("Clean Equipment")
step.text="Clean equipment with a mild detergent. It is important to clean equipment before use, any equipment used before the boil only needs to be cleaned as the wort will be sterilised during the boil. Equipment used after the boil must either be sterilised with sterilising solution, or limited equipment may be sterilised in the boiler. Note: don't use 2 real taps for the HLT, use one dummy tap. The equipment to clean is: hlt, sparge arm, mash tun, jug, large paddle, thermometer, stoarge box, kettles and jerry can. "
step.addEquipment( mashpaddle )
step.addEquipment( hlt )
step.addEquipment( atc800) 
step.addEquipment( sparge_arm )
step.addEquipment( mash_tun )
step.addEquipment( jug ) # try do without a jug
step.addEquipment( smalljug )
step.addEquipment( largepaddle )
step.addEquipment( thermometer )
#step.addEquipment( storagebox )
#step.addEquipment( filteringFunnel )
step.addEquipment( kettle20l )
step.addEquipment( kettle15l )
step.addEquipment( jerry10l )
step.newSubStep( ("Clean HLT",{'complete':1}) )
step.newSubStep( ("Clean FV",{'complete':1}) )
step.newSubStep( ("Clean Kettle",{'complete':1}) )
step.newSubStep( ("Clean Mashtun",{'complete':1}) )

# Clean work area
step = myprocessF.brewday.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before commencing the brew day"


# Setup Equipment
step = myprocessF.brewday.newstep("Setup Equipment")
step.text="The hot liquor tank must be positioned higher than the mash tun with the sparge arm assembled. The brewing kettle is positoned the lowest."
#step.newSubStep( ("Setup the equipment as pictured",{'complete':1}) )
#step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to ...strike_temp_5...degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))

step.img=["sterilise_setup1.png"]



### modified for a more logical break in the proceedings.



# Fill the HLT
step = myprocessF.brewday.newstep("Treat Mash Water / Begin heating mash water")
step.text="Fill the HLT with ...mash_liquid_6...L of water for the mash and heat to strike temp + 5 deg. The strike temperature takes account of the cold grain absorbing heat."
step.addConsumable( campdenTablet, 1)
step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to ...strike_temp_5...degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))
step.newSubStep( ("Fill the hot liquor tank with ...mash_liquid_6...L of water for the mash",{'complete':1}))
step.newSubStep( ("If not using bottled water for the Mash Liquid crush half a Campden tablet into the water and leave for 5 minutes. Leave a further 5 minutes and there stir well.",{'complete':1}))
step.newSubStep( ("Begin heating the mash liquid to ...strike_temp_5...C, continue with other steps in the background.", {'complete':1}))
step.newSubStep( ("Take a sample of mash water at 25degC and record the PH",{'complete':1}))
step.attention="Do not turn on the temperature controller until the elements in the kettle are covered with water."
step.fields.append( ('Mashwater PH','mashWaterPH','') )
step.img=['treatwater.png']


# Gather grain
step = myprocessF.brewday.newstep("Gather Grain")
step.text="Gather the and measure the grain required for the brewday"
step.auto="gatherthegrain"
step.addConsumable(burton,2)
step.newSubStep( ("Add 1 teaspoon of gypsum -OR- 2 teaspoons of burton water salts to the grain.",{'complete':1}))		# this is correct, thought it might have been too much


# Mash
step = myprocessF.brewday.newstep("Get Ready to Mash")
step.text="Once the Mash Water has been heated to 65C then pre-heat the mash tun."
step.newSubStep( ("Boil 1.5L of tap water and add to the mash tun, add the lid to the mash tun",{'complete':1}))
#step.auto="grainqty"
step.img = ['mash.png']


# Fill the Mash Tun
step = myprocessF.brewday.newstep("Fill the mash tun with mash liquid")# and set aside the grain. During this step the mash tun should be well insulated to maintain a stable temperature")
step.text="Fill the mashtun with the mash liquor in order the water is to ...strike_temp_5...C (Strike Temp ...strike_temp...C). The water in the HLT should be heated to 5degC higher than strke temp to account for some losses while transferring the liquid, however the temperature should be monitored. Note: if more water is used in the mash tun the strike temperature should be lower, if less water is used then the strike temperature should be higer."
step.prereq="Mash Water is at ...strike_temp_5...C"
step.newSubStep( ("Discard the water used for preheating the mash tun into the 20l kettle",{'complete':1}))
step.newSubStep( ("Fill the mash tun with  ...mash_liquid...L of water heated to ...strike_temp_5...C.", {'complete':1}) )
step.newSubStep( ("Set aside 1.7L of boiling water and 1.7L of cold water which may optionally may be used for adjustment of temperature/consistency", {'complete':1}))
step.attention="If the grain temperature is not between 15-20 degC then the calculations should be re-run to provide a hotter/colder strike temp."


#
#
#
myprocessF.recipeUpgrades['grainthicknessMustBeGreaterThan'] = 1.35


# Dough in the grain 
step = myprocessF.brewday.newstep("Dough in the grain")
step.text="The temperature for mashing is important high temperatures will lead to extraction of tannins, low temperatures will not provide efficient conversion. Lower temperature conversion - around 64-66.6C  will take longer but will produce a more complete conversion of complex starches to sugars resulting in more fermentation and a clean, lighter tasting beer. A high temperature conversion of 68.5-70 C will result in less starch conversion leaving a beer with more unfermentable dextrines. This will create a beer with a full body and flavor. Middle mash temperatures  67.69 C will result in medium bodied beers.  The consistency of the mixture should be resemble porridge. (Note: this is still subject to refining in the past this was calculated with a ratio of 1.25 but recipes will be at least 1.35 with this process."

step.newSubStep( ("With the temperature of the mash liquid at ...strike_temp...C stir in the grain.", {'complete':1}))
step.newSubStep( ("The aim is to mash at a temperature of ...target_mash_temp...C", {'complete':1}))
step.newSubStep( ("Cover and set aside for 60 minutes.",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("Take out the mash paddle",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("If after a few minutes the temperature difference is +/- 3degC of the ...target_mash_temp...C target then a temperature adjustment may be carried out with care.", {'complete':1}))
step.newSubStep( ("Take a sample of the mash to measure the PH",{'complete':1}))

step.addEquipment( timer )
step.fields.append(('Ambinet Temp(C)','mash_ambient_temp',''))
step.fields.append(('Adjustment Needed','mash_adjusment_needed',''))
step.fields.append(('(Start) Mash Temp Acheived','mash_start_temp',''))
step.attention="The Temperature of the Grain Bed should remain below 75degC throughout."
step.img=["dough.png"]







# Fill the HLT 
step = myprocessF.brewday.newstep("Fill the HLT and begin heating")
step.text="Fill the HLT with sparge water, there will be some water left in the HLT after taking out the mash water. The sparge water is expected to take around ...sparge_heating_time... minutes to heat. Note: this process assumes bottled/britta filtered water will be used for this step."
step.newSubStep(("Fill the HLT so that it contains ...sparge_water... L",{'complete':1}))
step.addConsumable( citric,0.5)
step.newSubStep(("Add citric acid (half a teaspoon) to the sparge water and stir.",{'complete':1}))
step.newSubStep(("Begin heating the sparge water to ...sparge_temp...C",{'complete':1}))
step.attention="The HLT is constructed with standard kettle elements, therefore it is advisable to alternate between the elements 3 or 4 times during the heating. The temperature controller should only power one kettle element at any time."
step.fields.append(('(MID1) Mash Temp Acheived','mash_mid1_temp',''))



# Begin sterilising remaining equipment
step = myprocessF.brewday.newstep("Sterilise Equipment")
step.text="It is important throughout the brew day to keep any equipment which will come into contact with the wort post-boil sterilised. Equipment used before the boil does not need to be sterilised but does need to be clean. Note: the silicone tube used for transferring wort from the boiler into the fermentation bin will be sanitised in a later step. If there is no tap on the bottom of the fermentation bin a large pipette (turkey baster) should be sterilised to take gravity samples later in the process."
step.newSubStep( ("Fill the fermentation bin with 10 litres of warm water and 2 tsp of sterilising powder.",{'complete':1}))

# track somehow if the fermentation bin has a tap on the bottom

#step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer probe, and a glass jug into the fermentation bin.",{'complete':1}))
step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer and a glass jug into the fermentation bin.",{'complete':1}))
#step.newSubStep( ("Add equipment that will be used post boil. Small Jug, Hydrometer, Trial Jar, Thermometer",{'complete':1}))
step.newSubStep( ("Ensure fermentation bin is fully sterilised with equipment, after 10 minutes of sterilising equipment place equipment in the small storage stockport.",{'complete':1}))
step.newSubStep( ("Ensure a 'filter' is added to the back of the fermentation bin tap",{'complete':1}))
step.newSubStep( ("Ensure all the feremntation bin has been sterilised and empty solution into the small stock pot.",{'complete':1}))
step.img=['sterilise1step.png']
step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."



step.addEquipment( smalljug )
step.addEquipment( fermentationbin6gal )
step.addEquipment( hydrometer )
step.addEquipment( trialjar )
#step.addEquipment( thermometer3 )
step.addEquipment( thermometer2 )
#step.addEquipment( immersionchiller )
myprocessF.immersionchiller = immersionchiller
step.addConsumable( pfte, 0.5 )
step.fields.append(('(MID2) Mash Temp Acheived','mash_mid2_temp',''))
step.fields.append(('(MID3) Mash Temp Acheived','mash_mid3_temp',''))
step.fields.append(('(MID4) Mash Temp Acheived','mash_mid4_temp',''))
step.fields.append(('(MID5) Mash Temp Acheived','mash_mid5_temp',''))
step.fields.append(('(MID6) Mash Temp Acheived','mash_mid6_temp',''))
step.fields.append(('(MID7) Mash Temp Acheived','mash_mid7_temp',''))



# Rinse Equipment
step = myprocessF.brewday.newstep("Rinse Equipment")
step.text="Rinse Equipment in the same way as sterilising, equipment should be rinsed with 25 litres of cold water. The equipment which has been sterilised should be set aside for later use."


step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."

step.fields.append(('(MID8) Mash Temp Acheived','mash_mid8_temp',''))
step.fields.append(('(MID9) Mash Temp Acheived','mash_mid9_temp',''))
step.fields.append(('(MID10) Mash Temp Acheived','mash_mid10_temp',''))
step.fields.append(('(MID11) Mash Temp Acheived','mash_mid11_temp',''))
step.fields.append(('(MID12) Mash Temp Acheived','mash_mid12_temp',''))
step.fields.append(('(MID13) Mash Temp Acheived','mash_mid13_temp',''))
step.fields.append(('(MID14) Mash Temp Acheived','mash_mid14_temp',''))


# Sanitise
step = myprocessF.brewday.newstep("Sanitise the boiler tube")
step.text="Boil a kettle of water and add to the an empty small stock pot, curl up the silicon tube which will be used for transferring wort into the fermentation bin later. pour in the kettle of water - including inside the tube."

# Monitor Mash Equipment
step = myprocessF.brewday.newstep("Monitor the Mash")
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
step = myprocessF.brewday.newstep("Assemble Sparge Setup and begin Recirculation")
#step.addConsumable(muslinbag,1)
step.addEquipment(funnel)


step.text="Once the sparge water is at the correct temperature ...sparge_temp...C AND the mash duration has completedthe sparge setup can be setup. During this step the cloudy wort with bits of grain will drained leading to a natural grain filter forming."
step.newSubStep( ("Take off the lid from the mash tun and assemble the sparge arm",{}))
step.newSubStep( ("Allow up to 6 litres of wort to drain from the mash tun into the kettle, the wort should be carefully added back to the top of the lauter tun trying to ensure minimal disturbance.",{'complete':1}))
step.fields.append(('(End) Mash Temp Acheived','mash_end_temp',''))
step.newSubStep( ("Collect sample of mash to measure PH",{'complete':1}))
step.attention="Set the thermometer to alarm if the temperature is higher than 71deg. If it is then lid should be lifted to reduce the heat."
step.img=["spargesetup.png"]


# Start Sparge
step = myprocessF.brewday.newstep("Start Fly Sparging")
step.text="Sparging will drain the sugar from the grain providing us with wort. The process of sparging should be carried out slowly. The temperature of the gain bed will be raised during this proess (note there is no instant change of temperature). The grain bed should stay below 76 deg C. We need to aim for a boil volume of ...boil_vol...L. General wisdom is to keep 1 inch of water above the grain bed- however there is a trade off (the more water above the grain bed the smaller/slower temperature rise of the grain bed, the less water above the grain bed the bigger/quicker temperature rise of the grain bed."
#Throughout the process monitor flow of liquid into and out of the mash tun to try maintain an equilibrium"
step.newSubStep( ("Collect sample of sparge water to measure PH",{'complete':1}))

step.img=["dosparge.png"]







step = myprocessF.brewday.newstep("Start Boiling the Wort")
step.text="Boiling the wort drives off unwanted volatile components, coagulates proteins,  and sanitising the wort for fermentation. The first boil should be ...kettle1volume...L of wort. We are aiming for a gravity of ...kettle1preboilgravity... It is expected the kettle will loose ...kettle1evaporation...L due to evaporation """
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
step = myprocessF.brewday.newstep("Dynamic Recipe Adjustment")
step.text="If the mash was particularly efficent/inefficient it may be desirarble to top up fermentables, dilute wort, increase/decrease hop quantities. The target pre-boil gravity is ...preboil_gravity... (total post-boil gravity ...estimated_og...). The target wort volume required is ...boil_vol...L. The gravity quotes here takes account of later topup of ...topupvol...L. Estimated gravity post boil pre cooling is ...postboilprecoolgravity..."
step.attention="Be careful with topup at this stage, the dilution of cooling/evaporation will concentrate the wort further. If the wort is too concentrated at this stage delay dilution until the cooling stage. Making readings of volume/gravities is the most important thing at this stage."



step.fields.append( ('Topup Gravity','__topupgravity','1.000') )
step.fields.append( ('Topup Gravity Temp','__topupgravitytemp','20') )
step.widgets['__topupgravityadjusted'] = (' gravityTempAdjustment',['__topupgravity','__topupgravitytemp'])
step.fields.append( ('Topup Gravity Adjusted','__topupgravityadjusted','1.000') )
step.fields.append( ('Final Gravity Required','__topupgravityrequired','') )



step.img=["sighttube.png"]

# Bring the wort to the boil
step = myprocessF.brewday.newstep("Measure Hops")
step.text="Measure the hops for addition to the kettle."
step.auto="hopmeasure_v3"
step.img=["boil.png"]


# Bring the wort to the boil
step = myprocessF.brewday.newstep("Bittering Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Once the wort is at a rolling boil the hops can be added and the lid should be left half covered."
step.img=["boil.png"]
step.newSubStep(("Start timer for 45 minutes after which the protofloc copper finings will be added",{'complete':1,'kitchentimer' : ('b',3600) }))
step.newSubStep(("Turn on the fridge with ATC Control to 20 degC",{'complete':1}))
step.auto="hopaddBittering_v3_withadjuncts"



# Bring the wort to the boil
step = myprocessF.brewday.newstep("Aroma Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the aroma hops to the kettle with 15 minutes remaining. The immersion chiller will need to be sterilised during this period and irishmoss/protofloc added to help coagulate proteins in the wort. For small boils it may be necessary to tie the immersion chiller with cable ties."
step.newSubStep(("Start timer for 15 minutes .",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the irishmoss/protofloc and continue boiling for 15 minutes.",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the immersion chiller",{'complete':1,'kitchentimer' : ('a',900) }))
step.auto="hopaddAroma_v3"
step.img=["boil.png"]

# Bring the wort to the boil
step = myprocessF.brewday.newstep("Finishing Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the finishing hops to the kettle and stop the heat."
step.auto="hopaddFinishing_v3"
step.img=["boil.png"]


# Yeast Rehydration
step = myprocessF.brewday.newstep("Boil Yeast Rehydration Water")
step.text="Rehydration yeast provides a gentle start for the yeast and helps fermentation start quickly. If using yeast slurry instead then this step will still be carried out to sterilise the jug in order to measure the yeast slurry."
step.newSubStep(("Boil 500ml of water and set aside in a pyrex jug",{'complete':1}))
step.newSubStep(("After 10 minutes put the hug in a water bath to cool the water to 25 degC",{'complete':1}))
step.attention="Yeast should nto be added to the rehydration water unless is is <25 degC"




# Cool Wort
step = myprocessF.brewday.newstep("Cool wort")
step.text="It is important to cool the wort quickly, ice water can help to cooling water towards the end of cooling. The estimated gravity required is ...estimated_og... Do not aerate the wort while- however gentle circulation can help to avoid hot/cool spots during the cooling process"
step.newSubStep(("Setup the immersion chiller and and start pushing cold water through to cool the wort to 20 degC",{'complete':1}))
step.img=["drain3.png"]
step.newSubStep(("With the temperature of the wort at 35degC start using ice to cool the temperature of the cooling water.",{'complete':1}))
step.newSubStep(("Add half of the yeast contents to the rehydration water, for Safale S04 the temperature of the yeast rehydration water should be 27degC +/- 3degC",{'complete':1}))
step.condition=[]
step.fields.append( ('Post Boil Volume (Pre Cool)','postboilvolumebeforecool','') )



# Drain Wort
step = myprocessF.brewday.newstep("Drain wortinto fermentation bin")
step.condition=[]
step.text="With the wort cooled to 20degC, then record the volume of the wort in the boiler, before draining the wort from the fermentation bin."
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
step = myprocessF.brewday.newstep("Topup")
step.text="As the wort is cooling a decision should be made on the gravity of the resulting wort. It is hard to increase the gravity (as the high gravity wort is already used) but easy to reduce the gravity (as diluted wort/sterilised water will be easily available). It is best to make the decision when the wort is as cool as possible to reduce the effect of the hydrometer adjustments. If there was a high mash temperature factor in high final gravity when trying to calculate alcohol. Too severe a dilution will reduce the bittering/hop aroma. Planned volume in the fermenter (pretopup)....precoolfvvolume... with a later topup of ...topupvol...L, planed original gravity ...postboil_precool_og.../...estimated_og... (precool/cool)  planned final gravity ...estimated_fg... planned abv ....estimated_abv..."
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
step = myprocessF.brewday.newstep("Measure")
step.text="Recording results is important to track the quality of the brew. The expected original gravity is ...estimated_og..., final gravity estimate is ...estimated_fg..., estimated abv ...estimated_abv..."
step.newSubStep(("Aerate the wort for 5 minutes",{'complete':1}))
step.newSubStep(("After aerating the wort measure take a sample to measure the original gravity.",{'complete':1}))
step.fields.append( ('Original Gravity','og','') )
step.fields.append( ('Fermentation bin Weight','postboilweight','') )
step.fields.append( ('Fermentation bin vol (after cooling)','postboilvol','') )
step.fields.append( ('Wort left in boiler vol','leftovervol','') )



step = myprocessF.brewday.newstep("Measure PH from brewday")
step.text="Various samples should have been taken start of mash, end of mash and sparge water to determine the PH throughout the process. The PH meter will need to be calibrated with a solution of a known PH at a set temperature. 4.00 @ 5-25, 4.01 @ 30, 4.02 @ 35, 4.03 @ 40, 4.04 @ 45, 4.06 @ 50, 4.07 @ 55, 4.09 @ 60, 4.12 @ 70, 4.16 @ 80, 4.20 @ 90, 4.22 @ 95. 6.95 @ 5, 6.92 @ 10, 6.90 @ 15, 6.88 @ 20, 6.86 @ 25, 6.85 @ 30, 6.84 @ 35-40, 6.83 @ 45-55, 6.84 @ 60, 6.85 @ 70, 6.86 @ 80, 6.88 @ 90"
step.attention="PH meter is calibrated for 25degC."
step.fields.append( ('Mash PH','mashPH','') )
step.fields.append( ('Post Mash PH','postMashWaterPH','') )
step.fields.append( ('Spargewater PH','spargeWaterPH','') )
step.fields.append( ('Finished Wort PH','wortPH','') )


# Move Fermentation Bin
step = myprocessF.brewday.newstep("Move Fermentation Bin")
step.newSubStep(("Setup temperature controller for the fermentation fridge and set the temperature to 20degC. The temperature probe must be insulated against the side of the fermentation bin in order to measure the wort temperature as accurately as possible",{'complete':1})) 
step.text="Move the fermentation bin to a suitable location for the duration of fermentation (ideally a stable temperature). It may help to tranfer some of the COOLED wort into the 15L kettle before moving, and then recombining into the fermentation bin. At this stage of the process aeration is ok."
step.attention="The 15L kettle must remain sterile and should be emptitied of all hot-break/hops before using it"
step.img=['tempcontrol.png']



# Pitch
step = myprocessF.brewday.newstep("Pitch Yeast")
step.text="If using yeast slurry then measure 400ml of slurry assuming the batch size is <6 gallon and the yeast slurry must be less than 14 days old. Before using yeast slurry a check on the progress of ferementation from the previous batch is required."
step.newSubStep(("Once the wort is at pitching temperature (20degC)",{'complete':1}))
#oistep.newSubStep(("Optionally add an immersion heater set for 18degC",{'complete':1}))
step.addConsumable(yeastvit,0.5)
step.newSubStep(("Pitch the yeast",{'complete':1}))
step.newSubStep(("Add half a teaspoon of yeastvit",{'complete':1}))



###########################
#Post Brew Day


step = myprocessF.postbrewday.newstep("Kraussen")
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


step = myprocessF.postbrewday.newstep("Dryhop")
step.text ="After 3 days add the dry hops. There is differing opinion about adding hops, too early and the aroma is driven off by the CO2 produced in fermentation, too late and there *may* be a *potential* oxidation risk. The alcohol should protect anynasty organisms in the hops from taking hold."
step.auto="dryhop"
step.condition=[]
step.condition.append( ['dryhop','>',1] )
step.newSubStep(("Kraussen Observed.",{'complete':1}))

step = myprocessF.postbrewday.newstep("Measure specific gravity (1st)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 1 (1.xxx)','sg1',''))


step = myprocessF.postbrewday.newstep("Measure specific gravity (2nd)")
step.text ="After 7 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 2 (1.xxx)','sg2',''))


step = myprocessF.postbrewday.newstep("Measure specific gravity (3rd)")
step.text ="After 8 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 3 (1.xxx)','sg3',''))


step = myprocessF.postbrewday.newstep("Measure specific gravity (4th)")
step.text ="After 9 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 4 (1.xxx)','sg4',''))

step = myprocessF.postbrewday.newstep("Measure specific gravity (5th)")
step.text ="After 10 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 5 (1.xxx)','sg5',''))




step = myprocessF.postbrewday.newstep("Calculate Alcohol")
step.text="The alcohol can be calculated from the original gravity and the stable final gravity readings."
step.fields.append( ('Measured Final Gravity','__measuredFg_abv',''))
step.widgets['__abv'] = ('abvCalculation',['og','__measuredFg_abv'])
step.fields.append( ('ABV','__abv','') )


step = myprocessF.bottlingAndKegging.GatherThings()


step = myprocessF.bottlingAndKegging.newstep("Gather Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gatherthepolypins"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Polypins\n"
step.newSubStep(("Gather ...polypinqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

step = myprocessF.bottlingAndKegging.newstep("Gather Mini Kegs")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gathertheminikegs"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Minikegs with bungs/safety vent bungs\n"
step.newSubStep(("Gather ...minikegqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available


step = myprocessF.bottlingAndKegging.newstep("Gather Bottles")
step.condition=[]
step.condition.append(['bottleqty','>',0])
step.auto="gatherthebottles"
step.stockDependency=["bottle"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Bottles\n"
step.newSubStep(("Gather ...bottleqty... bottles",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

step = myprocessF.bottlingAndKegging.newstep("Move fermentation bin")
step.text="If needed move the fermentation bin to a height suitable for bottling from. This should be carried out early to allow any disturbance to settle"


step = myprocessF.bottlingAndKegging.newstep("Clean Work Area")
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

step = myprocessF.bottlingAndKegging.newstep("Setup Work Area")
step.text="Setup the work area as shown in the image, cleaning the bottles may be carried out the previous evening to save time."
step.img=["bottlingsetup.png"]


step = myprocessF.bottlingAndKegging.newstep("Clean Bottles")
step.text="Cleaning the bottles using hot water and detergent."
step.newSubStep(("Clean the bottles using a bottle brush to ensure no deposits are left in the bottle. Drain solution out of the bottles.",{'complete':1}))
step.newSubStep(("Rinse the bottles with a small amount of water.",{'complete':1}))
step.img=['bottleclean.png']


step = myprocessF.bottlingAndKegging.newstep("Setup Work Area 2")
step.text="Setup the work area as show in the image, during the bottling stage all equipment will be required."
step.img=["bottlingsetup2.png"]


step = myprocessF.bottlingAndKegging.newstep("Sterilise Crown Caps")
step.text="Crown caps needs to be sterilised before use."
step.newSubStep(("Boil 500ml of water and add to a clean pyrex jug",{'complete':1}))
step.newSubStep(("Add ...num_crown_caps... crown caps/plastic caps to the jug and set aside.",{'complete':1}))


step = myprocessF.bottlingAndKegging.newstep("Prepare Jars for Yeast Harvesting")
step.text="Yeast harvesting may be carried out if fresh yeast was used for a brew with an original gravity < 1.060 and the next brew is due to be carried out in less than 14 days"
step.newSubStep(("Fill the 2L Jar with boiling water, add the lid securely and set aside",{'complete':1}))
step.newSubStep(("Fill each of the 400ml jars with boiling water add the lid a set aside.",{'complete':1}))
step.newSubStep(("After 10 minutes add the 400ml jars into a cold water bath to cool the water",{'complete':1}))

#step = myprocessF.bottlingAndKegging.newstep("Sterilise Saucepan")
#step.text="Sterilise the saucepan, thermometer and slotted spoon, and measuring spoon by adding the equipment to the saucepan and filling with boiling water. Set aside for at least 15 minutes"

step = myprocessF.bottlingAndKegging.primingSolution()
step.text="Priming solution provides more fermentables for the yeast to convert into further alcohol and natural carbonation"
step.newSubStep(("Measure ...primingsugartotal... (...primingsugarqty... per bottle) priming sugar and set aside.",{'complete':1}))
step.newSubStep(("Add ...primingwater... ml of water to the saucepan and heat to 90degC, once at 90degC stir in the sugar",{'complete':1}))
step.newSubStep(("Maintain the temperature at 85degC for 5 minutes and then cool in a water bath to less that 30 degC.",{'complete':1}))
step.img=['primingsolution.png']
step.attention="Be careful with the volume of sugar in each bottle as introducing too many fermentables can lead to exploding bottles"



step = myprocessF.bottlingAndKegging.newstep("Fill bottles with sterilising solution")
step.text="Use 3/4 of a level teaspoon of sterilising solution in a full jug of warm water. (which equates to 1 level teaspoon per 3L)"
step.newSubStep(("Arrange bottles in a crate ready to sterilise",{'complete':1}))
step.addConsumable( sterilisingPowder,4)
step.addEquipment( saucepan )
step.addEquipment( funnel )
step.img=['bottlingseq.png']
step.text="The sterilising of bottles is carried out by filling each bottle full with a sterilising solution. The funnel will be sterilsing as the bottles are filled. "
step.auto="sterilisebottles"
step.newSubStep(("Immerse the little bottler in a bottle of sterilising solution rotate to ensure both ends are covered inside and out.",{'complete':1}))


step = myprocessF.bottlingAndKegging.newstep("Empty bottles")
step.img=['bottlingempty.png']
step.text="After 5 minutes begin to partially empty sterilising solution from the bottles filling any of the mini kegs, each mini keg.It is important to the make sure the top of the bottle is sterilised. Bottles should be half emptied, and then given a good shake before finishing emptying the bottle."
step.attention="If using mini kegs or polypins the sterilising solution should be reused for the mini kegs/polypins"
step.newSubStep(("The first two bottles should be emptitied into the large jug, this gives an opportunity to serilise the top of the bottle",{'complete':1}))
#step.newSubStep(("If using mini kegs empty the remaining bottles into the mini kegs. Each mini keg should be fully filled with sterilising solution. If there is not enough sterilising solution in the bottles additional solution needs to be made.",{'complete':1}))


step = myprocessF.bottlingAndKegging.newstep("Fill polypins with sterilising solution")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gather4"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"

step = myprocessF.bottlingAndKegging.newstep("Fill mini kegs with sterilising solution")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gather3"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"


step = myprocessF.bottlingAndKegging.newstep("Empty Polypins")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Empty the sterilising solution from the polypins, using the taps"

step = myprocessF.bottlingAndKegging.newstep("Empty Minikegs")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Empty the sterilising solution from the minikegs, using the taps"


step = myprocessF.bottlingAndKegging.newstep("Rinse Bottles")
#step.img['bottlingrinse.png']
step.text="Bottles need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.attention="If using mini kegs/polypins the water should be empties into the minikegs/polypins"
step.newSubStep(("Fill each bottle with a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each bottle and empty the water.",{'complete':1}))


step = myprocessF.bottlingAndKegging.newstep("Rinse Polypins")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Polypins need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  polypin a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each polypin and empty via the tap.",{'complete':1}))


step = myprocessF.bottlingAndKegging.newstep("Rinse Minikegs")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Minikegs need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  minikeg a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each minikeg and empty via the tap.",{'complete':1}))





	# need to think about removing this step if no stock of mini kegs available

step = myprocessF.bottlingAndKegging.newstep("Add priming solution to each bottle")
step.text="Stir the priming and then add 15ml of priming solution to each bottle"


step = myprocessF.bottlingAndKegging.newstep("Add priming solution to each polypin")
step.text="Stir the priming and then add 45ml of priming solution to each polypin"
step.condition=[]
step.condition.append(['polypinqty','>',0])

step = myprocessF.bottlingAndKegging.newstep("Add priming solution to each minikeg")
step.text="Stir the priming and then add 120ml of priming solution to each minikeg"
step.condition=[]
step.condition.append(['minikegqty','>',0])


# Fill polypins kegs first
step = myprocessF.bottlingAndKegging.newstep("Fill Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The polypins should be filled with a little bottler, leaving half an inch of headspace."
step.newSubStep(("Fill each of the polypins. Add the tap and purge the remaining air ",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessF.bottlingAndKegging.newstep("Fill Mini Kegs")
step.condition=[]
step.condition.append(['miniqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The minikegs should be filled with a little bottler, leaving an inch of headspace."
step.newSubStep(("Fill each of the mini kegs",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessF.bottlingAndKegging.newstep("Fill bottles")
step.text="While filling it is useful to group the bottles by type to ensure even filling."
step.newSubStep(("Begin filling each bottle leaving an inch of space at the neck empty.",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"


step = myprocessF.bottlingAndKegging.newstep("Yeast Harvest Part 1")
step.text="To harvest the yeast the yeast cake is topped up with clean pre-boiled/sterilised water which will separate the yeast from the trub."
step.newSubStep(("Ensure any remaining beer not bottled is emptied carefully out of the fermentation bin, there should be very little (less than 200ml) beer remaining",{'complete':1}))
step.newSubStep(("Add 400ml of water to the yeast cake and stir gently",{'complete':1}))
step.newSubStep(("Remove the large spoon and let the fermentation bin settle for 1 hour",{'complete':1}))
step.img=["yeastcake1.png"]
step.attention="Sanitisation is very important while harvesting the yeast"


step = myprocessF.bottlingAndKegging.newstep("Attach Caps")
step.text="Once bottling has finished it is time to attach the caps."


step = myprocessF.bottlingAndKegging.newstep("Yeast Harvest Part 2")
step.text="The yeast from the fermentation bin will then be stored in the sterilised airtight container and set aside in the fridge"
step.newSubStep(("Fill the 2L jar with the solution from the fermentation bin, and then store in the fridge",{'complete':1}))
step.img=["yeastcake2.png"]
step.attention="Sanitisation is very important while harvesting the yeast. A label should be added to the jar to ensure the yeast is not used after 14 days,"

#ensure beer is removed without sucking up the yeast, 200ml beer on top is ok
#add 1L of water into bottom of fermentation bin.... swirl to ensure yeast is loose (or stir if we have the spoon in the bucket still).
#empty into 2L container.  straisfy
#

 # donosbourner.

step = myprocessF.bottlingAndKegging.newstep("Optional Secondary Conditioning")
step.text="If the ambient temperature is less than 18 degC it is a good idea to put the bottles into a water bath which can be heated to 20 degC. This ensures that the yeast has ideal conditions for working through the new fermenetables in the priming sugar"
step.attention="If using an aquarium heater in the water bath - it must always remain submerged. Ensure the water is at the correct temperature before adding bottles"
step.img=['secondarycondition.png']

step = myprocessF.bottlingAndKegging.newstep("Code bottles")
step.text="Ensure that the bottles can be identified, either via crown caps, labels etc. Once the beer is in condition full size labels may be added."
step.fields.append( ('Number of Bottles','numbottles','') )
step.fields.append( ('Number of Bottles (bad fills)','numbottlesbadfills','') )
step.fields.append( ('Number of MiniKegs','minikegs','') )
step.fields.append( ('Wastage in fermentation bin','fvpostbottlewastage','') )

step = myprocessF.bottlingAndKegging.newstep("Cleanup")
step.text="All equipment should be cleaned and left to dry before packing away for the next brewday"
step.attention="Ensure all equipment is completely dry before packing away."

step = myprocessF.bottlingAndKegging.newstep("Monitor Conditoning")
step.text="In the first si weeks it is necessary to check the progress of conditoning."
step.newSubStep(("After 1 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 2 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 3 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 4 sample beer 1, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 5 sample beer 2, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 6 sample beer 3, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))




myprocessF.save("process/allena29/24AG21i23")
#myprocessF.generateMySql()


myprocessG=brwlabProcess()
myprocessG.credit="Adam Allen"
myprocessG.name="25AG26i27"


myprocessG.description="An updated process for use in the entirely within the garage."

myprocessG.boilers = [kettle70l]
myprocessG.hlt = hlt
myprocessG.mash_tun = mash_tun




# Preparation
step = myprocessG.brewday.newstep("Preparation")
#step.newSubStep( ("If using a fermentation-fridge move it into position, it is necessary to wait >12 hours after moving the fridge before using.",{'complete':1}) )
step.newSubStep( ("Add ice-boxes to the freezer, these will be used to cool the immersion chiller water",{'complete':1}) )
#step.newSubStep( ("Ensure batteries for thermometers are available",{'complete':1}))
#step.newSubStep( ("Ensure clean towells are available as well as clean dry cloths for the floor",{'complete':1}))
step.text="The day before brew day the preparation above should be carried out, as well as checking stock/ingredients are available"



# Gather things
step = myprocessG.brewday.newstep("Assemble Mash/Lauter Tun")
step.text="Assemble the bucket in bucket mash tun, complete with scavenger tube. Gather Sparge Arm, Vorlauf Funnel Paddle and digital thermometer."
step.img=['assemblemashtun.png']

# Gather things
step = myprocessG.brewday.newstep("Assemble Hot Liquor Tank")
step.text="Assemble the hot liquor tank, complete with latstock and ATC800+ thermometer probe"
step.img=['assemblehlt.png']

# Gather things
#step = myprocessG.brewday.newstep("Assemble Kettle")
#step.text="Assemble the kettles with ball-valve tap. Use a stainless steel washer on the inside and pfte tape around thread. "
#step.img=['assemblekettle.png']

# Gather things
step = myprocessG.brewday.newstep("Assmeble Fermentation Bin")
step.text="Assemble the fermentation bin, complete with back filter"
step.img=['assemblefv.png']


# Gather things
step = myprocessG.brewday.newstep("Gather small stockpots")
step.text="Gather small stockpots and measuring spoons, these will be used to contain the grain"



## Gather things
#step = myprocessG.brewday.GatherThings()
#step.text="The grain can be measured later"

# Clean Equipment
step = myprocessG.brewday.newstep("Clean Equipment")
step.text="Clean equipment with a mild detergent. It is important to clean equipment before use, any equipment used before the boil only needs to be cleaned as the wort will be sterilised during the boil. Equipment used after the boil must either be sterilised with sterilising solution, or limited equipment may be sterilised in the boiler. Note: don't use 2 real taps for the HLT, use one dummy tap. The equipment to clean is: hlt, sparge arm, mash tun, jug, large paddle, thermometer, stoarge box, kettles and jerry can. "
step.addEquipment( mashpaddle )
step.addEquipment( hlt )
step.addEquipment( atc800) 
step.addEquipment( sparge_arm )
step.addEquipment( mash_tun )
step.addEquipment( jug ) # try do without a jug
step.addEquipment( smalljug )
step.addEquipment( largepaddle )
step.addEquipment( thermometer )
#step.addEquipment( storagebox )
#step.addEquipment( filteringFunnel )
step.addEquipment( kettle20l )
step.addEquipment( kettle15l )
step.addEquipment( jerry10l )
step.newSubStep( ("Clean HLT",{'complete':1}) )
step.newSubStep( ("Clean FV",{'complete':1}) )
step.newSubStep( ("Clean Kettle",{'complete':1}) )
step.newSubStep( ("Clean Mashtun",{'complete':1}) )

# Clean work area
step = myprocessG.brewday.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before commencing the brew day"


# Setup Equipment
step = myprocessG.brewday.newstep("Setup Equipment")
step.text="The hot liquor tank must be positioned higher than the mash tun with the sparge arm assembled. The brewing kettle is positoned the lowest."
#step.newSubStep( ("Setup the equipment as pictured",{'complete':1}) )
#step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to ...strike_temp_5...degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))

step.img=["sterilise_setup1.png"]



### modified for a more logical break in the proceedings.



# Fill the HLT
step = myprocessG.brewday.newstep("Treat Mash Water / Begin heating mash water")
step.text="Fill the HLT with ...mash_liquid_6...L of water for the mash and heat to strike temp + 5 deg. The strike temperature takes account of the cold grain absorbing heat."
step.addConsumable( campdenTablet, 1)
step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to ...strike_temp_5...degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))
step.newSubStep( ("Fill the hot liquor tank with ...mash_liquid_6...L of water for the mash",{'complete':1}))
step.newSubStep( ("If not using bottled water for the Mash Liquid crush half a Campden tablet into the water and leave for 5 minutes. Leave a further 5 minutes and there stir well.",{'complete':1}))
step.newSubStep( ("Begin heating the mash liquid to ...strike_temp_5...C, continue with other steps in the background.", {'complete':1}))
step.newSubStep( ("Take a sample of mash water at 25degC and record the PH",{'complete':1}))
step.attention="Do not turn on the temperature controller until the elements in the kettle are covered with water."
step.fields.append( ('Mashwater PH','mashWaterPH','') )
step.img=['treatwater.png']


# Gather grain
step = myprocessG.brewday.newstep("Gather Grain")
step.text="Gather the and measure the grain required for the brewday"
step.auto="gatherthegrain"
step.addConsumable(burton,2)
step.newSubStep( ("Add 1 teaspoon of gypsum -OR- 2 teaspoons of burton water salts to the grain.",{'complete':1}))		# this is correct, thought it might have been too much


# Mash
step = myprocessG.brewday.newstep("Get Ready to Mash")
step.text="Once the Mash Water has been heated to 65C then pre-heat the mash tun."
step.newSubStep( ("Boil 1.5L of tap water and add to the mash tun, add the lid to the mash tun",{'complete':1}))
#step.auto="grainqty"
step.img = ['mash.png']


# Fill the Mash Tun
step = myprocessG.brewday.newstep("Fill the mash tun with mash liquid")# and set aside the grain. During this step the mash tun should be well insulated to maintain a stable temperature")
step.text="Fill the mashtun with the mash liquor in order the water is to ...strike_temp_5...C (Strike Temp ...strike_temp...C). The water in the HLT should be heated to 5degC higher than strke temp to account for some losses while transferring the liquid, however the temperature should be monitored. Note: if more water is used in the mash tun the strike temperature should be lower, if less water is used then the strike temperature should be higer."
step.prereq="Mash Water is at ...strike_temp_5...C"
step.newSubStep( ("Discard the water used for preheating the mash tun into the 20l kettle",{'complete':1}))
step.newSubStep( ("Fill the mash tun with  ...mash_liquid...L of water heated to ...strike_temp_5...C.", {'complete':1}) )
step.newSubStep( ("Set aside 1.7L of boiling water and 1.7L of cold water which may optionally may be used for adjustment of temperature/consistency", {'complete':1}))
step.attention="If the grain temperature is not between 15-20 degC then the calculations should be re-run to provide a hotter/colder strike temp."


#
#
#
myprocessG.recipeUpgrades['grainthicknessMustBeGreaterThan'] = 1.35


# Dough in the grain 
step = myprocessG.brewday.newstep("Dough in the grain")
step.text="The temperature for mashing is important high temperatures will lead to extraction of tannins, low temperatures will not provide efficient conversion. Lower temperature conversion - around 64-66.6C  will take longer but will produce a more complete conversion of complex starches to sugars resulting in more fermentation and a clean, lighter tasting beer. A high temperature conversion of 68.5-70 C will result in less starch conversion leaving a beer with more unfermentable dextrines. This will create a beer with a full body and flavor. Middle mash temperatures  67.69 C will result in medium bodied beers.  The consistency of the mixture should be resemble porridge. (Note: this is still subject to refining in the past this was calculated with a ratio of 1.25 but recipes will be at least 1.35 with this process."

step.newSubStep( ("With the temperature of the mash liquid at ...strike_temp...C stir in the grain.", {'complete':1}))
step.newSubStep( ("The aim is to mash at a temperature of ...target_mash_temp...C", {'complete':1}))
step.newSubStep( ("Cover and set aside for 60 minutes.",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("Take out the mash paddle",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("If after a few minutes the temperature difference is +/- 3degC of the ...target_mash_temp...C target then a temperature adjustment may be carried out with care.", {'complete':1}))
step.newSubStep( ("Take a sample of the mash to measure the PH",{'complete':1}))

step.addEquipment( timer )
step.fields.append(('Ambinet Temp(C)','mash_ambient_temp',''))
step.fields.append(('Adjustment Needed','mash_adjusment_needed',''))
step.fields.append(('(Start) Mash Temp Acheived','mash_start_temp',''))
step.attention="The Temperature of the Grain Bed should remain below 75degC throughout."
step.img=["dough.png"]







# Fill the HLT 
step = myprocessG.brewday.newstep("Fill the HLT and begin heating")
step.text="Fill the HLT with sparge water, there will be some water left in the HLT after taking out the mash water. The sparge water is expected to take around ...sparge_heating_time... minutes to heat. Note: this process assumes bottled/britta filtered water will be used for this step."
step.newSubStep(("Fill the HLT so that it contains ...sparge_water... L",{'complete':1}))
step.addConsumable( citric,0.5)
step.newSubStep(("Add citric acid (half a teaspoon) to the sparge water and stir.",{'complete':1}))
step.newSubStep(("Begin heating the sparge water to ...sparge_temp...C",{'complete':1}))
step.attention="The HLT is constructed with standard kettle elements, therefore it is advisable to alternate between the elements 3 or 4 times during the heating. The temperature controller should only power one kettle element at any time."
step.fields.append(('(MID1) Mash Temp Acheived','mash_mid1_temp',''))



# Bring the wort to the boil
## if we are doing First Wort Hops then we need this here;
step = myprocessG.brewday.newstep("Measure Hops")
step.text="Measure the hops for addition to the kettle."
step.auto="hopmeasure_v3"
step.img=["boil.png"]


# Begin sterilising remaining equipment
step = myprocessG.brewday.newstep("Sterilise Equipment")
step.text="It is important throughout the brew day to keep any equipment which will come into contact with the wort post-boil sterilised. Equipment used before the boil does not need to be sterilised but does need to be clean. Note: the silicone tube used for transferring wort from the boiler into the fermentation bin will be sanitised in a later step. If there is no tap on the bottom of the fermentation bin a large pipette (turkey baster) should be sterilised to take gravity samples later in the process."
step.newSubStep( ("Fill the fermentation bin with 10 litres of warm water and 2 tsp of sterilising powder.",{'complete':1}))

# track somehow if the fermentation bin has a tap on the bottom

#step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer probe, and a glass jug into the fermentation bin.",{'complete':1}))
step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer and a glass jug into the fermentation bin.",{'complete':1}))
#step.newSubStep( ("Add equipment that will be used post boil. Small Jug, Hydrometer, Trial Jar, Thermometer",{'complete':1}))
step.newSubStep( ("Ensure fermentation bin is fully sterilised with equipment, after 10 minutes of sterilising equipment place equipment in the small storage stockport.",{'complete':1}))
step.newSubStep( ("Ensure a 'filter' is added to the back of the fermentation bin tap",{'complete':1}))
step.newSubStep( ("Ensure all the feremntation bin has been sterilised and empty solution into the small stock pot.",{'complete':1}))
step.img=['sterilise1step.png']
step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."



step.addEquipment( smalljug )
step.addEquipment( fermentationbin6gal )
step.addEquipment( hydrometer )
step.addEquipment( trialjar )
#step.addEquipment( thermometer3 )
step.addEquipment( thermometer2 )
#step.addEquipment( immersionchiller )
myprocessG.immersionchiller = immersionchiller
#step.addConsumable( pfte, 0.5 )
step.fields.append(('(MID2) Mash Temp Acheived','mash_mid2_temp',''))
step.fields.append(('(MID3) Mash Temp Acheived','mash_mid3_temp',''))
step.fields.append(('(MID4) Mash Temp Acheived','mash_mid4_temp',''))
step.fields.append(('(MID5) Mash Temp Acheived','mash_mid5_temp',''))
step.fields.append(('(MID6) Mash Temp Acheived','mash_mid6_temp',''))
step.fields.append(('(MID7) Mash Temp Acheived','mash_mid7_temp',''))



# Rinse Equipment
step = myprocessG.brewday.newstep("Rinse Equipment")
step.text="Rinse Equipment in the same way as sterilising, equipment should be rinsed with 25 litres of cold water. The equipment which has been sterilised should be set aside for later use."


step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."

step.fields.append(('(MID8) Mash Temp Acheived','mash_mid8_temp',''))
step.fields.append(('(MID9) Mash Temp Acheived','mash_mid9_temp',''))
step.fields.append(('(MID10) Mash Temp Acheived','mash_mid10_temp',''))
step.fields.append(('(MID11) Mash Temp Acheived','mash_mid11_temp',''))
step.fields.append(('(MID12) Mash Temp Acheived','mash_mid12_temp',''))
step.fields.append(('(MID13) Mash Temp Acheived','mash_mid13_temp',''))
step.fields.append(('(MID14) Mash Temp Acheived','mash_mid14_temp',''))


# Sanitise
step = myprocessG.brewday.newstep("Sanitise the boiler tube")
step.text="Boil a kettle of water and add to the an empty small stock pot, curl up the silicon tube which will be used for transferring wort into the fermentation bin later. pour in the kettle of water - including inside the tube."

# Monitor Mash Equipment
step = myprocessG.brewday.newstep("Monitor the Mash")
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
step = myprocessG.brewday.newstep("Assemble Sparge Setup and begin Recirculation")
#step.addConsumable(muslinbag,1)
step.addEquipment(funnel)


step.text="Once the sparge water is at the correct temperature ...sparge_temp...C AND the mash duration has completedthe sparge setup can be setup. During this step the cloudy wort with bits of grain will drained leading to a natural grain filter forming."
step.newSubStep( ("Take off the lid from the mash tun and assemble the sparge arm",{}))
step.newSubStep( ("Allow up to 6 litres of wort to drain from the mash tun into the kettle, the wort should be carefully added back to the top of the lauter tun trying to ensure minimal disturbance.",{'complete':1}))
step.fields.append(('(End) Mash Temp Acheived','mash_end_temp',''))
step.newSubStep( ("Collect sample of mash to measure PH",{'complete':1}))
step.attention="Set the thermometer to alarm if the temperature is higher than 71deg. If it is then lid should be lifted to reduce the heat."
step.img=["spargesetup.png"]



step = myprocessG.brewday.newstep("First Wort Hopping")
step.condition=[]
step.condition.append( ['first_wort_hop_qty','>',0] )
step.text="Add the first wort hops to the boiler before starting to sparge"
step.auto="hopaddFirstWort_v3"



# Start Sparge
step = myprocessG.brewday.newstep("Start Fly Sparging")
step.text="Sparging will drain the sugar from the grain providing us with wort. The process of sparging should be carried out slowly. The temperature of the gain bed will be raised during this proess (note there is no instant change of temperature). The grain bed should stay below 76 deg C. We need to aim for a boil volume of ...boil_vol...L. General wisdom is to keep 1 inch of water above the grain bed- however there is a trade off (the more water above the grain bed the smaller/slower temperature rise of the grain bed, the less water above the grain bed the bigger/quicker temperature rise of the grain bed."
#Throughout the process monitor flow of liquid into and out of the mash tun to try maintain an equilibrium"
step.newSubStep( ("Collect sample of sparge water to measure PH",{'complete':1}))

step.img=["dosparge.png"]







step = myprocessG.brewday.newstep("Start Boiling the Wort")
step.text="Boiling the wort drives off unwanted volatile components, coagulates proteins,  and sanitising the wort for fermentation. The first boil should be ...kettle1volume...L of wort. We are aiming for a gravity of ...kettle1preboilgravity... It is expected the kettle will loose ...kettle1evaporation...L due to evaporation """
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
step = myprocessG.brewday.newstep("Dynamic Recipe Adjustment")
step.text="If the mash was particularly efficent/inefficient it may be desirarble to top up fermentables, dilute wort, increase/decrease hop quantities. The target pre-boil gravity is ...preboil_gravity... (total post-boil gravity ...estimated_og...). The target wort volume required is ...boil_vol...L. The gravity quotes here takes account of later topup of ...topupvol...L. Estimated gravity post boil pre cooling is ...postboilprecoolgravity..."
step.attention="Be careful with topup at this stage, the dilution of cooling/evaporation will concentrate the wort further. If the wort is too concentrated at this stage delay dilution until the cooling stage. Making readings of volume/gravities is the most important thing at this stage."



step.fields.append( ('Topup Gravity','__topupgravity','1.000') )
step.fields.append( ('Topup Gravity Temp','__topupgravitytemp','20') )
step.widgets['__topupgravityadjusted'] = (' gravityTempAdjustment',['__topupgravity','__topupgravitytemp'])
step.fields.append( ('Topup Gravity Adjusted','__topupgravityadjusted','1.000') )
step.fields.append( ('Final Gravity Required','__topupgravityrequired','') )



step.img=["sighttube.png"]


# Bring the wort to the boil
step = myprocessG.brewday.newstep("Bittering Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Once the wort is at a rolling boil the hops can be added and the lid should be left half covered."
step.img=["boil.png"]
step.newSubStep(("Start timer for 45 minutes after which the protofloc copper finings will be added",{'complete':1,'kitchentimer' : ('b',3600) }))
step.newSubStep(("Turn on the fridge with ATC Control to 20 degC",{'complete':1}))
step.auto="hopaddBittering_v3_withadjuncts"


# Bring the wort to the boil
step = myprocessG.brewday.newstep("Pump Wort")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="With the wort at a boil recirculate with the pump to ensure that the pump and tubing is sterilised. Pump for 5 minutes"



# Bring the wort to the boil
step = myprocessG.brewday.newstep("Aroma Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the aroma hops to the kettle with 15 minutes remaining. The immersion chiller will need to be sterilised during this period and irishmoss/protofloc added to help coagulate proteins in the wort. For small boils it may be necessary to tie the immersion chiller with cable ties."
step.newSubStep(("Start timer for 15 minutes .",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the irishmoss/protofloc and continue boiling for 15 minutes.",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the immersion chiller",{'complete':1,'kitchentimer' : ('a',900) }))
step.auto="hopaddAroma_v3"
step.img=["boil.png"]

# Bring the wort to the boil
step = myprocessG.brewday.newstep("Finishing Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the finishing hops to the kettle and stop the heat."
step.auto="hopaddFinishing_v3"
step.img=["boil.png"]


# Yeast Rehydration
#step = myprocessG.brewday.newstep("Boil Yeast Rehydration Water")
#step.text="Rehydration yeast provides a gentle start for the yeast and helps fermentation start quickly. If using yeast slurry instead then this step will still be carried out to sterilise the jug in order to measure the yeast slurry."
#step.newSubStep(("Boil 500ml of water and set aside in a pyrex jug",{'complete':1}))
#step.newSubStep(("After 10 minutes put the hug in a water bath to cool the water to 25 degC",{'complete':1}))
#step.attention="Yeast should nto be added to the rehydration water unless is is <25 degC"




# Cool Wort
step = myprocessG.brewday.newstep("Cool wort")
step.text="It is important to cool the wort quickly, ice water can help to cooling water towards the end of cooling. The estimated gravity required is ...estimated_og... Do not aerate the wort while- however gentle circulation can help to avoid hot/cool spots during the cooling process"
step.newSubStep(("Setup the immersion chiller and and start pushing cold water through to cool the wort to 20 degC",{'complete':1}))
step.img=["drain3.png"]
step.newSubStep(("With the temperature of the wort at 35degC start using ice to cool the temperature of the cooling water.",{'complete':1}))
step.newSubStep(("Add half of the yeast contents to the rehydration water, for Safale S04 the temperature of the yeast rehydration water should be 27degC +/- 3degC",{'complete':1}))
step.condition=[]
step.fields.append( ('Post Boil Volume (Pre Cool)','postboilvolumebeforecool','') )



# Drain Wort
step = myprocessG.brewday.newstep("Pump wort into fermentation bin")
step.condition=[]
step.text="With the wort cooled to 20degC, then record the volume of the wort in the boiler, before draining the wort from the fermentation bin."
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
step = myprocessG.brewday.newstep("Topup")
step.text="As the wort is cooling a decision should be made on the gravity of the resulting wort. It is hard to increase the gravity (as the high gravity wort is already used) but easy to reduce the gravity (as diluted wort/sterilised water will be easily available). It is best to make the decision when the wort is as cool as possible to reduce the effect of the hydrometer adjustments. If there was a high mash temperature factor in high final gravity when trying to calculate alcohol. Too severe a dilution will reduce the bittering/hop aroma. Planned volume in the fermenter (pretopup)....precoolfvvolume... with a later topup of ...topupvol...L, planed original gravity ...postboil_precool_og.../...estimated_og... (precool/cool)  planned final gravity ...estimated_fg... planned abv ....estimated_abv..."
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
step = myprocessG.brewday.newstep("Measure")
step.text="Recording results is important to track the quality of the brew. The expected original gravity is ...estimated_og..., final gravity estimate is ...estimated_fg..., estimated abv ...estimated_abv..."
step.newSubStep(("Aerate the wort for 5 minutes",{'complete':1}))
step.newSubStep(("After aerating the wort measure take a sample to measure the original gravity.",{'complete':1}))
step.fields.append( ('Original Gravity','og','') )
step.fields.append( ('Fermentation bin Weight','postboilweight','') )
step.fields.append( ('Fermentation bin vol (after cooling)','postboilvol','') )
step.fields.append( ('Wort left in boiler vol','leftovervol','') )



step = myprocessG.brewday.newstep("Measure PH from brewday")
step.text="Various samples should have been taken start of mash, end of mash and sparge water to determine the PH throughout the process. The PH meter will need to be calibrated with a solution of a known PH at a set temperature. 4.00 @ 5-25, 4.01 @ 30, 4.02 @ 35, 4.03 @ 40, 4.04 @ 45, 4.06 @ 50, 4.07 @ 55, 4.09 @ 60, 4.12 @ 70, 4.16 @ 80, 4.20 @ 90, 4.22 @ 95. 6.95 @ 5, 6.92 @ 10, 6.90 @ 15, 6.88 @ 20, 6.86 @ 25, 6.85 @ 30, 6.84 @ 35-40, 6.83 @ 45-55, 6.84 @ 60, 6.85 @ 70, 6.86 @ 80, 6.88 @ 90"
step.attention="PH meter is calibrated for 25degC."
step.fields.append( ('Mash PH','mashPH','') )
step.fields.append( ('Post Mash PH','postMashWaterPH','') )
step.fields.append( ('Spargewater PH','spargeWaterPH','') )
step.fields.append( ('Finished Wort PH','wortPH','') )


## Move Fermentation Bin
#step = myprocessG.brewday.newstep("Move Fermentation Bin")
#step.newSubStep(("Setup temperature controller for the fermentation fridge and set the temperature to 20degC. The temperature probe must be insulated against the side of the fermentation bin in order to measure the wort temperature as accurately as possible",{'complete':1})) 
#step.text="Move the fermentation bin to a suitable location for the duration of fermentation (ideally a stable temperature). It may help to tranfer some of the COOLED wort into the 15L kettle before moving, and then recombining into the fermentation bin. At this stage of the process aeration is ok."
#step.attention="The 15L kettle must remain sterile and should be emptitied of all hot-break/hops before using it"
#step.img=['tempcontrol.png']
#


# Pitch
step = myprocessG.brewday.newstep("Pitch Yeast")
step.text="If using yeast slurry then measure 400ml of slurry assuming the batch size is <6 gallon and the yeast slurry must be less than 14 days old. Before using yeast slurry a check on the progress of ferementation from the previous batch is required."
step.newSubStep(("Once the wort is at pitching temperature (20degC)",{'complete':1}))
#oistep.newSubStep(("Optionally add an immersion heater set for 18degC",{'complete':1}))
step.addConsumable(yeastvit,0.5)
step.newSubStep(("Pitch the yeast",{'complete':1}))
step.newSubStep(("Add half a teaspoon of yeastvit",{'complete':1}))



###########################
#Post Brew Day


step = myprocessG.postbrewday.newstep("Kraussen")
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


step = myprocessG.postbrewday.newstep("Dryhop")
step.text ="After 3 days add the dry hops. There is differing opinion about adding hops, too early and the aroma is driven off by the CO2 produced in fermentation, too late and there *may* be a *potential* oxidation risk. The alcohol should protect anynasty organisms in the hops from taking hold."
step.auto="dryhop"
step.condition=[]
step.condition.append( ['dryhop','>',1] )
step.newSubStep(("Kraussen Observed.",{'complete':1}))

step = myprocessG.postbrewday.newstep("Measure specific gravity (1st)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 1 (1.xxx)','sg1',''))


step = myprocessG.postbrewday.newstep("Measure specific gravity (2nd)")
step.text ="After 7 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 2 (1.xxx)','sg2',''))


step = myprocessG.postbrewday.newstep("Measure specific gravity (3rd)")
step.text ="After 8 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 3 (1.xxx)','sg3',''))


step = myprocessG.postbrewday.newstep("Measure specific gravity (4th)")
step.text ="After 9 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 4 (1.xxx)','sg4',''))

step = myprocessG.postbrewday.newstep("Measure specific gravity (5th)")
step.text ="After 10 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 5 (1.xxx)','sg5',''))




step = myprocessG.postbrewday.newstep("Calculate Alcohol")
step.text="The alcohol can be calculated from the original gravity and the stable final gravity readings."
step.fields.append( ('Measured Final Gravity','__measuredFg_abv',''))
step.widgets['__abv'] = ('abvCalculation',['og','__measuredFg_abv'])
step.fields.append( ('ABV','__abv','') )


step = myprocessG.bottlingAndKegging.GatherThings()


step = myprocessG.bottlingAndKegging.newstep("Gather Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gatherthepolypins"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Polypins\n"
step.newSubStep(("Gather ...polypinqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

step = myprocessG.bottlingAndKegging.newstep("Gather Mini Kegs")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gathertheminikegs"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Minikegs with bungs/safety vent bungs\n"
step.newSubStep(("Gather ...minikegqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available


step = myprocessG.bottlingAndKegging.newstep("Gather Bottles")
step.condition=[]
step.condition.append(['bottleqty','>',0])
step.auto="gatherthebottles"
step.stockDependency=["bottle"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Bottles\n"
step.newSubStep(("Gather ...bottleqty... bottles",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

step = myprocessG.bottlingAndKegging.newstep("Move fermentation bin")
step.text="If needed move the fermentation bin to a height suitable for bottling from. This should be carried out early to allow any disturbance to settle"


step = myprocessG.bottlingAndKegging.newstep("Clean Work Area")
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

step = myprocessG.bottlingAndKegging.newstep("Setup Work Area")
step.text="Setup the work area as shown in the image, cleaning the bottles may be carried out the previous evening to save time."
step.img=["bottlingsetup.png"]


step = myprocessG.bottlingAndKegging.newstep("Clean Bottles")
step.text="Cleaning the bottles using hot water and detergent."
step.newSubStep(("Clean the bottles using a bottle brush to ensure no deposits are left in the bottle. Drain solution out of the bottles.",{'complete':1}))
step.newSubStep(("Rinse the bottles with a small amount of water.",{'complete':1}))
step.img=['bottleclean.png']


step = myprocessG.bottlingAndKegging.newstep("Setup Work Area 2")
step.text="Setup the work area as show in the image, during the bottling stage all equipment will be required."
step.img=["bottlingsetup2.png"]


step = myprocessG.bottlingAndKegging.newstep("Sterilise Crown Caps")
step.text="Crown caps needs to be sterilised before use."
step.newSubStep(("Boil 500ml of water and add to a clean pyrex jug",{'complete':1}))
step.newSubStep(("Add ...num_crown_caps... crown caps/plastic caps to the jug and set aside.",{'complete':1}))


step = myprocessG.bottlingAndKegging.newstep("Prepare Jars for Yeast Harvesting")
step.text="Yeast harvesting may be carried out if fresh yeast was used for a brew with an original gravity < 1.060 and the next brew is due to be carried out in less than 14 days"
step.newSubStep(("Fill the 2L Jar with boiling water, add the lid securely and set aside",{'complete':1}))
step.newSubStep(("Fill each of the 400ml jars with boiling water add the lid a set aside.",{'complete':1}))
step.newSubStep(("After 10 minutes add the 400ml jars into a cold water bath to cool the water",{'complete':1}))

#step = myprocessG.bottlingAndKegging.newstep("Sterilise Saucepan")
#step.text="Sterilise the saucepan, thermometer and slotted spoon, and measuring spoon by adding the equipment to the saucepan and filling with boiling water. Set aside for at least 15 minutes"

step = myprocessG.bottlingAndKegging.primingSolution()
step.text="Priming solution provides more fermentables for the yeast to convert into further alcohol and natural carbonation"
step.newSubStep(("Measure ...primingsugartotal... (...primingsugarqty... per bottle) priming sugar and set aside.",{'complete':1}))
step.newSubStep(("Add ...primingwater... ml of water to the saucepan and heat to 90degC, once at 90degC stir in the sugar",{'complete':1}))
step.newSubStep(("Maintain the temperature at 85degC for 5 minutes and then cool in a water bath to less that 30 degC.",{'complete':1}))
step.img=['primingsolution.png']
step.attention="Be careful with the volume of sugar in each bottle as introducing too many fermentables can lead to exploding bottles"



step = myprocessG.bottlingAndKegging.newstep("Fill bottles with sterilising solution")
step.text="Use 3/4 of a level teaspoon of sterilising solution in a full jug of warm water. (which equates to 1 level teaspoon per 3L)"
step.newSubStep(("Arrange bottles in a crate ready to sterilise",{'complete':1}))
step.addConsumable( sterilisingPowder,4)
step.addEquipment( saucepan )
step.addEquipment( funnel )
step.img=['bottlingseq.png']
step.text="The sterilising of bottles is carried out by filling each bottle full with a sterilising solution. The funnel will be sterilsing as the bottles are filled. "
step.auto="sterilisebottles"
step.newSubStep(("Immerse the little bottler in a bottle of sterilising solution rotate to ensure both ends are covered inside and out.",{'complete':1}))


step = myprocessG.bottlingAndKegging.newstep("Empty bottles")
step.img=['bottlingempty.png']
step.text="After 5 minutes begin to partially empty sterilising solution from the bottles filling any of the mini kegs, each mini keg.It is important to the make sure the top of the bottle is sterilised. Bottles should be half emptied, and then given a good shake before finishing emptying the bottle."
step.attention="If using mini kegs or polypins the sterilising solution should be reused for the mini kegs/polypins"
step.newSubStep(("The first two bottles should be emptitied into the large jug, this gives an opportunity to serilise the top of the bottle",{'complete':1}))
#step.newSubStep(("If using mini kegs empty the remaining bottles into the mini kegs. Each mini keg should be fully filled with sterilising solution. If there is not enough sterilising solution in the bottles additional solution needs to be made.",{'complete':1}))


step = myprocessG.bottlingAndKegging.newstep("Fill polypins with sterilising solution")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gather4"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"

step = myprocessG.bottlingAndKegging.newstep("Fill mini kegs with sterilising solution")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gather3"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"


step = myprocessG.bottlingAndKegging.newstep("Empty Polypins")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Empty the sterilising solution from the polypins, using the taps"

step = myprocessG.bottlingAndKegging.newstep("Empty Minikegs")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Empty the sterilising solution from the minikegs, using the taps"


step = myprocessG.bottlingAndKegging.newstep("Rinse Bottles")
#step.img['bottlingrinse.png']
step.text="Bottles need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.attention="If using mini kegs/polypins the water should be empties into the minikegs/polypins"
step.newSubStep(("Fill each bottle with a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each bottle and empty the water.",{'complete':1}))


step = myprocessG.bottlingAndKegging.newstep("Rinse Polypins")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Polypins need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  polypin a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each polypin and empty via the tap.",{'complete':1}))


step = myprocessG.bottlingAndKegging.newstep("Rinse Minikegs")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Minikegs need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  minikeg a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each minikeg and empty via the tap.",{'complete':1}))





	# need to think about removing this step if no stock of mini kegs available

step = myprocessG.bottlingAndKegging.newstep("Add priming solution to each bottle")
step.text="Stir the priming and then add 15ml of priming solution to each bottle"


step = myprocessG.bottlingAndKegging.newstep("Add priming solution to each polypin")
step.text="Stir the priming and then add 45ml of priming solution to each polypin"
step.condition=[]
step.condition.append(['polypinqty','>',0])

step = myprocessG.bottlingAndKegging.newstep("Add priming solution to each minikeg")
step.text="Stir the priming and then add 120ml of priming solution to each minikeg"
step.condition=[]
step.condition.append(['minikegqty','>',0])


# Fill polypins kegs first
step = myprocessG.bottlingAndKegging.newstep("Fill Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The polypins should be filled with a little bottler, leaving half an inch of headspace."
step.newSubStep(("Fill each of the polypins. Add the tap and purge the remaining air ",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessG.bottlingAndKegging.newstep("Fill Mini Kegs")
step.condition=[]
step.condition.append(['miniqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The minikegs should be filled with a little bottler, leaving an inch of headspace."
step.newSubStep(("Fill each of the mini kegs",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessG.bottlingAndKegging.newstep("Fill bottles")
step.text="While filling it is useful to group the bottles by type to ensure even filling."
step.newSubStep(("Begin filling each bottle leaving an inch of space at the neck empty.",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"


step = myprocessG.bottlingAndKegging.newstep("Yeast Harvest Part 1")
step.text="To harvest the yeast the yeast cake is topped up with clean pre-boiled/sterilised water which will separate the yeast from the trub."
step.newSubStep(("Ensure any remaining beer not bottled is emptied carefully out of the fermentation bin, there should be very little (less than 200ml) beer remaining",{'complete':1}))
step.newSubStep(("Add 400ml of water to the yeast cake and stir gently",{'complete':1}))
step.newSubStep(("Remove the large spoon and let the fermentation bin settle for 1 hour",{'complete':1}))
step.img=["yeastcake1.png"]
step.attention="Sanitisation is very important while harvesting the yeast"


step = myprocessG.bottlingAndKegging.newstep("Attach Caps")
step.text="Once bottling has finished it is time to attach the caps."


step = myprocessG.bottlingAndKegging.newstep("Yeast Harvest Part 2")
step.text="The yeast from the fermentation bin will then be stored in the sterilised airtight container and set aside in the fridge"
step.newSubStep(("Fill the 2L jar with the solution from the fermentation bin, and then store in the fridge",{'complete':1}))
step.img=["yeastcake2.png"]
step.attention="Sanitisation is very important while harvesting the yeast. A label should be added to the jar to ensure the yeast is not used after 14 days,"

#ensure beer is removed without sucking up the yeast, 200ml beer on top is ok
#add 1L of water into bottom of fermentation bin.... swirl to ensure yeast is loose (or stir if we have the spoon in the bucket still).
#empty into 2L container.  straisfy
#

 # donosbourner.

step = myprocessG.bottlingAndKegging.newstep("Optional Secondary Conditioning")
step.text="If the ambient temperature is less than 18 degC it is a good idea to put the bottles into a water bath which can be heated to 20 degC. This ensures that the yeast has ideal conditions for working through the new fermenetables in the priming sugar"
step.attention="If using an aquarium heater in the water bath - it must always remain submerged. Ensure the water is at the correct temperature before adding bottles"
step.img=['secondarycondition.png']

step = myprocessG.bottlingAndKegging.newstep("Code bottles")
step.text="Ensure that the bottles can be identified, either via crown caps, labels etc. Once the beer is in condition full size labels may be added."
step.fields.append( ('Number of Bottles','numbottles','') )
step.fields.append( ('Number of Bottles (bad fills)','numbottlesbadfills','') )
step.fields.append( ('Number of MiniKegs','minikegs','') )
step.fields.append( ('Wastage in fermentation bin','fvpostbottlewastage','') )

step = myprocessG.bottlingAndKegging.newstep("Cleanup")
step.text="All equipment should be cleaned and left to dry before packing away for the next brewday"
step.attention="Ensure all equipment is completely dry before packing away."

step = myprocessG.bottlingAndKegging.newstep("Monitor Conditoning")
step.text="In the first si weeks it is necessary to check the progress of conditoning."
step.newSubStep(("After 1 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 2 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 3 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 4 sample beer 1, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 5 sample beer 2, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 6 sample beer 3, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))




myprocessG.save("process/allena29/25AG26i27")
#myprocessG.generateMySql()








myprocessH=brwlabProcess()
myprocessH.credit="Adam Allen"
myprocessH.name="26AG27i28"


myprocessH.description="Worsdell Brewing - An updated process for use in the entirely within the garage, with a small number of tweaks."

myprocessH.boilers = [kettle70l]
myprocessH.hlt = hlt
myprocessH.mash_tun = mash_tun




# Preparation
step = myprocessH.brewday.newstep("Preparation")
#step.newSubStep( ("If using a fermentation-fridge move it into position, it is necessary to wait >12 hours after moving the fridge before using.",{'complete':1}) )
step.newSubStep( ("Add ice-boxes to the freezer, these will be used to cool the immersion chiller water",{'complete':1}) )
#step.newSubStep( ("Ensure batteries for thermometers are available",{'complete':1}))
#step.newSubStep( ("Ensure clean towells are available as well as clean dry cloths for the floor",{'complete':1}))
step.text="The day before brew day the preparation above should be carried out, as well as checking stock/ingredients are available"



# Gather things
step = myprocessH.brewday.newstep("Assemble Mash/Lauter Tun")
step.text="Assemble the bucket in bucket mash tun, complete with scavenger tube. Gather Sparge Arm, Vorlauf Funnel Paddle and digital thermometer."
step.img=['assemblemashtun.png']

# Gather things
step = myprocessH.brewday.newstep("Assemble Hot Liquor Tank")
step.text="Assemble the hot liquor tank, complete with latstock and thermometer probe"
step.img=['assemblehlt.png']

# Gather things
#step = myprocessH.brewday.newstep("Assemble Kettle")
#step.text="Assemble the kettles with ball-valve tap. Use a stainless steel washer on the inside and pfte tape around thread. "
#step.img=['assemblekettle.png']

# Gather things
step = myprocessH.brewday.newstep("Assmeble Fermentation Bin")
step.text="Assemble the fermentation bin, complete with back filter"
step.img=['assemblefv.png']


# Gather things
#step = myprocessH.brewday.newstep("Gather small stockpots")
#step.text="Gather small stockpots and measuring spoons, these will be used to contain the grain"



## Gather things
#step = myprocessH.brewday.GatherThings()
#step.text="The grain can be measured later"

# Clean Equipment
step = myprocessH.brewday.newstep("Clean Equipment")
step.text="Clean equipment with a mild detergent. It is important to clean equipment before use, any equipment used before the boil only needs to be cleaned as the wort will be sterilised during the boil. Equipment used after the boil must either be sterilised with sterilising solution, or limited equipment may be sterilised in the boiler. Note: don't use 2 real taps for the HLT, use one dummy tap. The equipment to clean is: hlt, sparge arm, mash tun, jug, large paddle, thermometer, stoarge box, kettles and jerry can. "
step.addEquipment( mashpaddle )
step.addEquipment( hlt )
step.addEquipment( atc800) 
step.addEquipment( sparge_arm )
step.addEquipment( mash_tun )
step.addEquipment( jug ) # try do without a jug
step.addEquipment( smalljug )
step.addEquipment( largepaddle )
step.addEquipment( thermometer )
#step.addEquipment( storagebox )
#step.addEquipment( filteringFunnel )
step.addEquipment( kettle20l )
step.addEquipment( kettle15l )
step.addEquipment( jerry10l )
step.newSubStep( ("Clean HLT",{'complete':1}) )
step.newSubStep( ("Clean FV",{'complete':1}) )
step.newSubStep( ("Clean Kettle",{'complete':1}) )
step.newSubStep( ("Clean Mashtun",{'complete':1}) )

# Clean work area
step = myprocessH.brewday.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before commencing the brew day"


# Setup Equipment
#step = myprocessH.brewday.newstep("Setup Equipment")
#step.text="The hot liquor tank must be positioned higher than the mash tun with the sparge arm assembled. The brewing kettle is positoned the lowest."
#step.newSubStep( ("Setup the equipment as pictured",{'complete':1}) )
#step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to ...strike_temp_5...degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))

step.img=["sterilise_setup1.png"]



### modified for a more logical break in the proceedings.



# Fill the HLT
step = myprocessH.brewday.newstep("Treat Mash Water / Begin heating mash water")
step.text="Fill the HLT with ...mash_liquid_6...L of water for the mash and heat to strike temp + 5 deg. The strike temperature takes account of the cold grain absorbing heat."
step.addConsumable( campdenTablet, 1)
step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to ...strike_temp_5...degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))
step.newSubStep( ("Fill the hot liquor tank with ...mash_liquid_6...L of water for the mash",{'complete':1}))
step.newSubStep( ("If not using bottled water for the Mash Liquid crush half a Campden tablet into the water and leave for 5 minutes. Leave a further 5 minutes and there stir well.",{'complete':1}))
step.newSubStep( ("Begin heating the mash liquid to ...strike_temp_5...C, continue with other steps in the background.", {'complete':1}))
step.newSubStep( ("Take a sample of mash water at 25degC and record the PH",{'complete':1}))
step.attention="Do not turn on the temperature controller until the elements in the kettle are covered with water."
step.fields.append( ('Mashwater PH','mashWaterPH','') )
step.img=['treatwater.png']


# Gather grain
step = myprocessH.brewday.newstep("Gather Grain")
step.text="Gather the and measure the grain required for the brewday"
step.auto="gatherthegrain"
step.addConsumable(burton,2)
step.newSubStep( ("Add 1 teaspoon of gypsum -OR- 2 teaspoons of burton water salts to the grain.",{'complete':1}))		# this is correct, thought it might have been too much


# Mash
step = myprocessH.brewday.newstep("Get Ready to Mash")
step.text="Once the Mash Water has been heated to 65C then pre-heat the mash tun."
step.newSubStep( ("Boil 1.5L of tap water and add to the mash tun, add the lid to the mash tun",{'complete':1}))
#step.auto="grainqty"
step.img = ['mash.png']


# Fill the Mash Tun
step = myprocessH.brewday.newstep("Fill the mash tun with mash liquid")# and set aside the grain. During this step the mash tun should be well insulated to maintain a stable temperature")
step.text="Fill the mashtun with the mash liquor in order the water is to ...strike_temp_5...C (Strike Temp ...strike_temp...C). The water in the HLT should be heated to 5degC higher than strke temp to account for some losses while transferring the liquid, however the temperature should be monitored. Note: if more water is used in the mash tun the strike temperature should be lower, if less water is used then the strike temperature should be higer."
step.prereq="Mash Water is at ...strike_temp_5...C"
step.newSubStep( ("Discard the water used for preheating the mash tun into the 20l kettle",{'complete':1}))
step.newSubStep( ("Fill the mash tun with  ...mash_liquid...L of water heated to ...strike_temp_5...C.", {'complete':1}) )
step.newSubStep( ("Set aside 1.7L of boiling water and 1.7L of cold water which may optionally may be used for adjustment of temperature/consistency", {'complete':1}))
step.attention="If the grain temperature is not between 15-20 degC then the calculations should be re-run to provide a hotter/colder strike temp."


#
#
#
myprocessH.recipeUpgrades['grainthicknessMustBeGreaterThan'] = 1.35


# Dough in the grain 
step = myprocessH.brewday.newstep("Dough in the grain")
step.text="The temperature for mashing is important high temperatures will lead to extraction of tannins, low temperatures will not provide efficient conversion. Lower temperature conversion - around 64-66.6C  will take longer but will produce a more complete conversion of complex starches to sugars resulting in more fermentation and a clean, lighter tasting beer. A high temperature conversion of 68.5-70 C will result in less starch conversion leaving a beer with more unfermentable dextrines. This will create a beer with a full body and flavor. Middle mash temperatures  67.69 C will result in medium bodied beers.  The consistency of the mixture should be resemble porridge. (Note: this is still subject to refining in the past this was calculated with a ratio of 1.25 but recipes will be at least 1.35 with this process."

step.newSubStep( ("With the temperature of the mash liquid at ...strike_temp...C stir in the grain.", {'complete':1}))
step.newSubStep( ("The aim is to mash at a temperature of ...target_mash_temp...C", {'complete':1}))
step.newSubStep( ("Cover and set aside for 60 minutes.",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("Take out the mash paddle",{'complete':1,'kitchentimer':('a',3600) }))
step.newSubStep( ("If after a few minutes the temperature difference is +/- 3degC of the ...target_mash_temp...C target then a temperature adjustment may be carried out with care.", {'complete':1}))
step.newSubStep( ("Take a sample of the mash to measure the PH",{'complete':1}))

step.addEquipment( timer )
step.fields.append(('Ambinet Temp(C)','mash_ambient_temp',''))
step.fields.append(('Adjustment Needed','mash_adjusment_needed',''))
step.fields.append(('(Start) Mash Temp Acheived','mash_start_temp',''))
step.attention="The Temperature of the Grain Bed should remain below 75degC throughout."
step.img=["dough.png"]







# Fill the HLT 
step = myprocessH.brewday.newstep("Fill the HLT and begin heating")
step.text="Fill the HLT with sparge water, there will be some water left in the HLT after taking out the mash water. The sparge water is expected to take around ...sparge_heating_time... minutes to heat. Note: this process assumes bottled/britta filtered water will be used for this step."
step.newSubStep(("Fill the HLT so that it contains ...sparge_water... L",{'complete':1}))
step.addConsumable( citric,0.5)
step.newSubStep(("Add citric acid (half a teaspoon) to the sparge water and stir.",{'complete':1}))
step.newSubStep(("Begin heating the sparge water to ...sparge_temp...C",{'complete':1}))
step.attention="The HLT is constructed with standard kettle elements, therefore it is advisable to alternate between the elements 3 or 4 times during the heating. The temperature controller should only power one kettle element at any time."
step.fields.append(('(MID1) Mash Temp Acheived','mash_mid1_temp',''))



# Bring the wort to the boil
## if we are doing First Wort Hops then we need this here;
step = myprocessH.brewday.newstep("Measure Hops")
step.text="Measure the hops for addition to the kettle."
step.auto="hopmeasure_v3"
step.img=["boil.png"]


# Begin sterilising remaining equipment
step = myprocessH.brewday.newstep("Sterilise Equipment")
step.text="It is important throughout the brew day to keep any equipment which will come into contact with the wort post-boil sterilised. Equipment used before the boil does not need to be sterilised but does need to be clean. Note: the silicone tube used for transferring wort from the boiler into the fermentation bin will be sanitised in a later step. If there is no tap on the bottom of the fermentation bin a large pipette (turkey baster) should be sterilised to take gravity samples later in the process."
step.newSubStep( ("Fill the fermentation bin with 10 litres of warm water and 2 tsp of sterilising powder.",{'complete':1}))

# track somehow if the fermentation bin has a tap on the bottom

#step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer probe, and a glass jug into the fermentation bin.",{'complete':1}))
step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer and a glass jug into the fermentation bin.",{'complete':1}))
#step.newSubStep( ("Add equipment that will be used post boil. Small Jug, Hydrometer, Trial Jar, Thermometer",{'complete':1}))
step.newSubStep( ("Ensure fermentation bin is fully sterilised with equipment, after 10 minutes of sterilising equipment place equipment in the small storage stockport.",{'complete':1}))
step.newSubStep( ("Ensure a 'filter' is added to the back of the fermentation bin tap",{'complete':1}))
step.newSubStep( ("Ensure all the feremntation bin has been sterilised and empty solution into the small stock pot.",{'complete':1}))
step.img=['sterilise1step.png']
step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."



step.addEquipment( smalljug )
step.addEquipment( fermentationbin6gal )
step.addEquipment( hydrometer )
step.addEquipment( trialjar )
#step.addEquipment( thermometer3 )
step.addEquipment( thermometer2 )
#step.addEquipment( immersionchiller )
myprocessH.immersionchiller = immersionchiller
#step.addConsumable( pfte, 0.5 )
step.fields.append(('(MID2) Mash Temp Acheived','mash_mid2_temp',''))
step.fields.append(('(MID3) Mash Temp Acheived','mash_mid3_temp',''))
step.fields.append(('(MID4) Mash Temp Acheived','mash_mid4_temp',''))
step.fields.append(('(MID5) Mash Temp Acheived','mash_mid5_temp',''))
step.fields.append(('(MID6) Mash Temp Acheived','mash_mid6_temp',''))
step.fields.append(('(MID7) Mash Temp Acheived','mash_mid7_temp',''))



# Rinse Equipment
step = myprocessH.brewday.newstep("Rinse Equipment")
step.text="Rinse Equipment in the same way as sterilising, equipment should be rinsed with 25 litres of cold water. The equipment which has been sterilised should be set aside for later use."


step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."

step.fields.append(('(MID8) Mash Temp Acheived','mash_mid8_temp',''))
step.fields.append(('(MID9) Mash Temp Acheived','mash_mid9_temp',''))
step.fields.append(('(MID10) Mash Temp Acheived','mash_mid10_temp',''))
step.fields.append(('(MID11) Mash Temp Acheived','mash_mid11_temp',''))
step.fields.append(('(MID12) Mash Temp Acheived','mash_mid12_temp',''))
step.fields.append(('(MID13) Mash Temp Acheived','mash_mid13_temp',''))
step.fields.append(('(MID14) Mash Temp Acheived','mash_mid14_temp',''))


# Monitor Mash Equipment
step = myprocessH.brewday.newstep("Monitor the Mash")
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
step = myprocessH.brewday.newstep("Assemble Sparge Setup and begin Recirculation")
#step.addConsumable(muslinbag,1)
step.addEquipment(funnel)


step.text="Once the sparge water is at the correct temperature ...sparge_temp...C AND the mash duration has completedthe sparge setup can be setup. During this step the cloudy wort with bits of grain will drained leading to a natural grain filter forming."
step.newSubStep( ("Take off the lid from the mash tun and assemble the sparge arm",{}))
step.newSubStep( ("Allow up to 6 litres of wort to drain from the mash tun into the kettle, the wort should be carefully added back to the top of the lauter tun trying to ensure minimal disturbance.",{'complete':1}))
step.fields.append(('(End) Mash Temp Acheived','mash_end_temp',''))
step.newSubStep( ("Collect sample of mash to measure PH",{'complete':1}))
step.attention="Set the thermometer to alarm if the temperature is higher than 71deg. If it is then lid should be lifted to reduce the heat."
step.img=["spargesetup.png"]



step = myprocessH.brewday.newstep("First Wort Hopping")
step.condition=[]
step.condition.append( ['first_wort_hop_qty','>',0] )
step.text="Add the first wort hops to the boiler before starting to sparge"
step.auto="hopaddFirstWort_v3"



# Start Sparge
step = myprocessH.brewday.newstep("Start Fly Sparging")
step.text="Sparging will drain the sugar from the grain providing us with wort. The process of sparging should be carried out slowly. The temperature of the gain bed will be raised during this proess (note there is no instant change of temperature). The grain bed should stay below 76 deg C. We need to aim for a boil volume of ...boil_vol...L. General wisdom is to keep 1 inch of water above the grain bed- however there is a trade off (the more water above the grain bed the smaller/slower temperature rise of the grain bed, the less water above the grain bed the bigger/quicker temperature rise of the grain bed."
#Throughout the process monitor flow of liquid into and out of the mash tun to try maintain an equilibrium"
step.newSubStep( ("Collect sample of sparge water to measure PH",{'complete':1}))

step.img=["dosparge.png"]







step = myprocessH.brewday.newstep("Start Boiling the Wort")
step.text="Boiling the wort drives off unwanted volatile components, coagulates proteins,  and sanitising the wort for fermentation. The first boil should be ...kettle1volume...L of wort. We are aiming for a gravity of ...kettle1preboilgravity... It is expected the kettle will loose ...kettle1evaporation...L due to evaporation """
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
step = myprocessH.brewday.newstep("Dynamic Recipe Adjustment")
step.text="If the mash was particularly efficent/inefficient it may be desirarble to top up fermentables, dilute wort, increase/decrease hop quantities. The target pre-boil gravity is ...preboil_gravity... (total post-boil gravity ...estimated_og...). The target wort volume required is ...boil_vol...L. The gravity quotes here takes account of later topup of ...topupvol...L. Estimated gravity post boil pre cooling is ...postboilprecoolgravity..."
step.attention="Be careful with topup at this stage, the dilution of cooling/evaporation will concentrate the wort further. If the wort is too concentrated at this stage delay dilution until the cooling stage. Making readings of volume/gravities is the most important thing at this stage."



step.fields.append( ('Topup Gravity','__topupgravity','1.000') )
step.fields.append( ('Topup Gravity Temp','__topupgravitytemp','20') )
step.widgets['__topupgravityadjusted'] = (' gravityTempAdjustment',['__topupgravity','__topupgravitytemp'])
step.fields.append( ('Topup Gravity Adjusted','__topupgravityadjusted','1.000') )
step.fields.append( ('Final Gravity Required','__topupgravityrequired','') )



step.img=["sighttube.png"]


# Bring the wort to the boil
step = myprocessH.brewday.newstep("Bittering Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Once the wort is at a rolling boil the hops can be added and the lid should be left half covered."
step.img=["boil.png"]
step.newSubStep(("Start timer for 45 minutes after which the protofloc copper finings will be added",{'complete':1,'kitchentimer' : ('b',3600) }))
step.newSubStep(("Turn on the fridge with ATC Control to 20 degC",{'complete':1}))
step.auto="hopaddBittering_v3_withadjuncts"


# Bring the wort to the boil
step = myprocessH.brewday.newstep("Pump Wort")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="With the wort at a boil recirculate with the pump to ensure that the pump and tubing is sterilised. Pump for 5 minutes"



# Bring the wort to the boil
step = myprocessH.brewday.newstep("Aroma Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the aroma hops to the kettle with 15 minutes remaining. The immersion chiller will need to be sterilised during this period and irishmoss/protofloc added to help coagulate proteins in the wort. For small boils it may be necessary to tie the immersion chiller with cable ties."
step.newSubStep(("Start timer for 15 minutes .",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the irishmoss/protofloc and continue boiling for 15 minutes.",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the immersion chiller",{'complete':1,'kitchentimer' : ('a',900) }))
step.auto="hopaddAroma_v3"
step.img=["boil.png"]


# Sanitise
step = myprocessH.brewday.newstep("Sanitise the boiler tube")
step.text="Boil a kettle of water and add to the an empty small stock pot, curl up the silicon tube which will be used for transferring wort into the fermentation bin later. pour in the kettle of water - including inside the tube."


# Bring the wort to the boil
step = myprocessH.brewday.newstep("Finishing Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the finishing hops to the kettle and stop the heat."
step.auto="hopaddFinishing_v3"
step.img=["boil.png"]


# Yeast Rehydration
#step = myprocessH.brewday.newstep("Boil Yeast Rehydration Water")
#step.text="Rehydration yeast provides a gentle start for the yeast and helps fermentation start quickly. If using yeast slurry instead then this step will still be carried out to sterilise the jug in order to measure the yeast slurry."
#step.newSubStep(("Boil 500ml of water and set aside in a pyrex jug",{'complete':1}))
#step.newSubStep(("After 10 minutes put the hug in a water bath to cool the water to 25 degC",{'complete':1}))
#step.attention="Yeast should nto be added to the rehydration water unless is is <25 degC"




# Cool Wort
step = myprocessH.brewday.newstep("Cool wort")
step.text="It is important to cool the wort quickly, ice water can help to cooling water towards the end of cooling. The estimated gravity required is ...estimated_og... Do not aerate the wort while- however gentle circulation can help to avoid hot/cool spots during the cooling process"
step.newSubStep(("Setup the immersion chiller and and start pushing cold water through to cool the wort to 20 degC",{'complete':1}))
step.img=["drain3.png"]
step.newSubStep(("With the temperature of the wort at 35degC start using ice to cool the temperature of the cooling water.",{'complete':1}))
step.newSubStep(("Add half of the yeast contents to the rehydration water, for Safale S04 the temperature of the yeast rehydration water should be 27degC +/- 3degC",{'complete':1}))
step.condition=[]
step.fields.append( ('Post Boil Volume (Pre Cool)','postboilvolumebeforecool','') )



# Drain Wort
step = myprocessH.brewday.newstep("Pump wort into fermentation bin")
step.condition=[]
step.text="With the wort cooled to 20degC, then record the volume of the wort in the boiler, before draining the wort from the fermentation bin."
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
step = myprocessH.brewday.newstep("Topup")
step.text="As the wort is cooling a decision should be made on the gravity of the resulting wort. It is hard to increase the gravity (as the high gravity wort is already used) but easy to reduce the gravity (as diluted wort/sterilised water will be easily available). It is best to make the decision when the wort is as cool as possible to reduce the effect of the hydrometer adjustments. If there was a high mash temperature factor in high final gravity when trying to calculate alcohol. Too severe a dilution will reduce the bittering/hop aroma. Planned volume in the fermenter (pretopup)....precoolfvvolume... with a later topup of ...topupvol...L, planed original gravity ...postboil_precool_og.../...estimated_og... (precool/cool)  planned final gravity ...estimated_fg... planned abv ....estimated_abv..."
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
step = myprocessH.brewday.newstep("Measure")
step.text="Recording results is important to track the quality of the brew. The expected original gravity is ...estimated_og..., final gravity estimate is ...estimated_fg..., estimated abv ...estimated_abv..."
step.newSubStep(("Aerate the wort for 5 minutes",{'complete':1}))
step.newSubStep(("After aerating the wort measure take a sample to measure the original gravity.",{'complete':1}))
step.fields.append( ('Original Gravity','og','') )
step.fields.append( ('Fermentation bin Weight','postboilweight','') )
step.fields.append( ('Fermentation bin vol (after cooling)','postboilvol','') )
step.fields.append( ('Wort left in boiler vol','leftovervol','') )



step = myprocessH.brewday.newstep("Measure PH from brewday")
step.text="Various samples should have been taken start of mash, end of mash and sparge water to determine the PH throughout the process. The PH meter will need to be calibrated with a solution of a known PH at a set temperature. 4.00 @ 5-25, 4.01 @ 30, 4.02 @ 35, 4.03 @ 40, 4.04 @ 45, 4.06 @ 50, 4.07 @ 55, 4.09 @ 60, 4.12 @ 70, 4.16 @ 80, 4.20 @ 90, 4.22 @ 95. 6.95 @ 5, 6.92 @ 10, 6.90 @ 15, 6.88 @ 20, 6.86 @ 25, 6.85 @ 30, 6.84 @ 35-40, 6.83 @ 45-55, 6.84 @ 60, 6.85 @ 70, 6.86 @ 80, 6.88 @ 90"
step.attention="PH meter is calibrated for 25degC."
step.fields.append( ('Mash PH','mashPH','') )
step.fields.append( ('Post Mash PH','postMashWaterPH','') )
step.fields.append( ('Spargewater PH','spargeWaterPH','') )
step.fields.append( ('Finished Wort PH','wortPH','') )


## Move Fermentation Bin
#step = myprocessH.brewday.newstep("Move Fermentation Bin")
#step.newSubStep(("Setup temperature controller for the fermentation fridge and set the temperature to 20degC. The temperature probe must be insulated against the side of the fermentation bin in order to measure the wort temperature as accurately as possible",{'complete':1})) 
#step.text="Move the fermentation bin to a suitable location for the duration of fermentation (ideally a stable temperature). It may help to tranfer some of the COOLED wort into the 15L kettle before moving, and then recombining into the fermentation bin. At this stage of the process aeration is ok."
#step.attention="The 15L kettle must remain sterile and should be emptitied of all hot-break/hops before using it"
#step.img=['tempcontrol.png']
#


# Pitch
step = myprocessH.brewday.newstep("Pitch Yeast")
step.text="If using yeast slurry then measure 400ml of slurry assuming the batch size is <6 gallon and the yeast slurry must be less than 14 days old. Before using yeast slurry a check on the progress of ferementation from the previous batch is required."
step.newSubStep(("Once the wort is at pitching temperature (20degC)",{'complete':1}))
#oistep.newSubStep(("Optionally add an immersion heater set for 18degC",{'complete':1}))
step.addConsumable(yeastvit,0.5)
step.newSubStep(("Pitch the yeast",{'complete':1}))
step.newSubStep(("Add half a teaspoon of yeastvit",{'complete':1}))



###########################
#Post Brew Day


step = myprocessH.postbrewday.newstep("Kraussen")
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


step = myprocessH.postbrewday.newstep("Dryhop")
step.text ="After 3 days add the dry hops. There is differing opinion about adding hops, too early and the aroma is driven off by the CO2 produced in fermentation, too late and there *may* be a *potential* oxidation risk. The alcohol should protect anynasty organisms in the hops from taking hold."
step.auto="dryhop"
step.condition=[]
step.condition.append( ['dryhop','>',1] )
step.newSubStep(("Kraussen Observed.",{'complete':1}))

step = myprocessH.postbrewday.newstep("Measure specific gravity (1st)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 1 (1.xxx)','sg1',''))


step = myprocessH.postbrewday.newstep("Measure specific gravity (2nd)")
step.text ="After 7 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 2 (1.xxx)','sg2',''))


step = myprocessH.postbrewday.newstep("Measure specific gravity (3rd)")
step.text ="After 8 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 3 (1.xxx)','sg3',''))


step = myprocessH.postbrewday.newstep("Measure specific gravity (4th)")
step.text ="After 9 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 4 (1.xxx)','sg4',''))

step = myprocessH.postbrewday.newstep("Measure specific gravity (5th)")
step.text ="After 10 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 5 (1.xxx)','sg5',''))




step = myprocessH.postbrewday.newstep("Calculate Alcohol")
step.text="The alcohol can be calculated from the original gravity and the stable final gravity readings."
step.fields.append( ('Measured Final Gravity','__measuredFg_abv',''))
step.widgets['__abv'] = ('abvCalculation',['og','__measuredFg_abv'])
step.fields.append( ('ABV','__abv','') )


step = myprocessH.bottlingAndKegging.GatherThings()


step = myprocessH.bottlingAndKegging.newstep("Gather Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gatherthepolypins"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Polypins\n"
step.newSubStep(("Gather ...polypinqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

step = myprocessH.bottlingAndKegging.newstep("Gather Mini Kegs")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gathertheminikegs"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Minikegs with bungs/safety vent bungs\n"
step.newSubStep(("Gather ...minikegqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available


step = myprocessH.bottlingAndKegging.newstep("Gather Bottles")
step.condition=[]
step.condition.append(['bottleqty','>',0])
step.auto="gatherthebottles"
step.stockDependency=["bottle"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Bottles\n"
step.newSubStep(("Gather ...bottleqty... bottles",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

#step = myprocessH.bottlingAndKegging.newstep("Move fermentation bin")
#step.text="If needed move the fermentation bin to a height suitable for bottling from. This should be carried out early to allow any disturbance to settle"


step = myprocessH.bottlingAndKegging.newstep("Clean Work Area")
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

#step = myprocessH.bottlingAndKegging.newstep("Setup Work Area")
#step.text="Setup the work area as shown in the image, cleaning the bottles may be carried out the previous evening to save time."
#step.img=["bottlingsetup.png"]


step = myprocessH.bottlingAndKegging.newstep("Clean Bottles")
step.text="Cleaning the bottles using hot water and detergent."
step.newSubStep(("Clean the bottles using a bottle brush to ensure no deposits are left in the bottle. Drain solution out of the bottles.",{'complete':1}))
step.newSubStep(("Rinse the bottles with a small amount of water.",{'complete':1}))
step.img=['bottleclean.png']

step = myprocessH.bottlingAndKegging.primingSolution()
step.text="Priming solution provides more fermentables for the yeast to convert into further alcohol and natural carbonation"
step.newSubStep(("Measure ...primingsugartotal... (...primingsugarqty... per bottle) priming sugar and set aside.",{'complete':1}))
step.newSubStep(("Add ...primingwater... ml of water to the saucepan and heat to 90degC, once at 90degC stir in the sugar",{'complete':1}))
step.newSubStep(("Maintain the temperature at 85degC for 5 minutes and then cool in a water bath to less that 30 degC.",{'complete':1}))
step.img=['primingsolution.png']
step.attention="Be careful with the volume of sugar in each bottle as introducing too many fermentables can lead to exploding bottles"


#step = myprocessH.bottlingAndKegging.newstep("Setup Work Area 2")
#step.text="Setup the work area as show in the image, during the bottling stage all equipment will be required."
#step.img=["bottlingsetup2.png"]


step = myprocessH.bottlingAndKegging.newstep("Sterilise Crown Caps")
step.text="Crown caps needs to be sterilised before use."
step.newSubStep(("Boil 500ml of water and add to a clean pyrex jug",{'complete':1}))
step.newSubStep(("Add ...num_crown_caps... crown caps/plastic caps to the jug and set aside.",{'complete':1}))


step = myprocessH.bottlingAndKegging.newstep("Prepare Jars for Yeast Harvesting")
step.text="Yeast harvesting may be carried out if fresh yeast was used for a brew with an original gravity < 1.060 and the next brew is due to be carried out in less than 14 days"
step.newSubStep(("Fill the 2L Jar with boiling water, add the lid securely and set aside",{'complete':1}))
step.newSubStep(("Fill each of the 400ml jars with boiling water add the lid a set aside.",{'complete':1}))
step.newSubStep(("After 10 minutes add the 400ml jars into a cold water bath to cool the water",{'complete':1}))

#step = myprocessH.bottlingAndKegging.newstep("Sterilise Saucepan")
#step.text="Sterilise the saucepan, thermometer and slotted spoon, and measuring spoon by adding the equipment to the saucepan and filling with boiling water. Set aside for at least 15 minutes"



step = myprocessH.bottlingAndKegging.newstep("Fill bottles with sterilising solution")
step.text="Use 3/4 of a level teaspoon of sterilising solution in a full jug of warm water. (which equates to 1 level teaspoon per 3L)"
step.newSubStep(("Arrange bottles in a crate ready to sterilise",{'complete':1}))
step.addConsumable( sterilisingPowder,4)
step.addEquipment( saucepan )
step.addEquipment( funnel )
step.img=['bottlingseq.png']
step.text="The sterilising of bottles is carried out by filling each bottle full with a sterilising solution. The funnel will be sterilsing as the bottles are filled. "
step.auto="sterilisebottles"
step.newSubStep(("Immerse the little bottler in a bottle of sterilising solution rotate to ensure both ends are covered inside and out.",{'complete':1}))


step = myprocessH.bottlingAndKegging.newstep("Empty bottles")
step.img=['bottlingempty.png']
step.text="After 5 minutes begin to partially empty sterilising solution from the bottles filling any of the mini kegs, each mini keg.It is important to the make sure the top of the bottle is sterilised. Bottles should be half emptied, and then given a good shake before finishing emptying the bottle."
step.attention="If using mini kegs or polypins the sterilising solution should be reused for the mini kegs/polypins"
step.newSubStep(("The first two bottles should be emptitied into the large jug, this gives an opportunity to serilise the top of the bottle",{'complete':1}))
#step.newSubStep(("If using mini kegs empty the remaining bottles into the mini kegs. Each mini keg should be fully filled with sterilising solution. If there is not enough sterilising solution in the bottles additional solution needs to be made.",{'complete':1}))


step = myprocessH.bottlingAndKegging.newstep("Fill polypins with sterilising solution")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gather4"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"

step = myprocessH.bottlingAndKegging.newstep("Fill mini kegs with sterilising solution")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gather3"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"


step = myprocessH.bottlingAndKegging.newstep("Empty Polypins")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Empty the sterilising solution from the polypins, using the taps"

step = myprocessH.bottlingAndKegging.newstep("Empty Minikegs")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Empty the sterilising solution from the minikegs, using the taps"


step = myprocessH.bottlingAndKegging.newstep("Rinse Bottles")
#step.img['bottlingrinse.png']
step.text="Bottles need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.attention="If using mini kegs/polypins the water should be empties into the minikegs/polypins"
step.newSubStep(("Fill each bottle with a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each bottle and empty the water.",{'complete':1}))


step = myprocessH.bottlingAndKegging.newstep("Rinse Polypins")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Polypins need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  polypin a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each polypin and empty via the tap.",{'complete':1}))


step = myprocessH.bottlingAndKegging.newstep("Rinse Minikegs")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Minikegs need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  minikeg a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each minikeg and empty via the tap.",{'complete':1}))





	# need to think about removing this step if no stock of mini kegs available

step = myprocessH.bottlingAndKegging.newstep("Add priming solution to each bottle")
step.text="Stir the priming and then add 15ml of priming solution to each bottle"


step = myprocessH.bottlingAndKegging.newstep("Add priming solution to each polypin")
step.text="Stir the priming and then add 45ml of priming solution to each polypin"
step.condition=[]
step.condition.append(['polypinqty','>',0])

step = myprocessH.bottlingAndKegging.newstep("Add priming solution to each minikeg")
step.text="Stir the priming and then add 120ml of priming solution to each minikeg"
step.condition=[]
step.condition.append(['minikegqty','>',0])


# Fill polypins kegs first
step = myprocessH.bottlingAndKegging.newstep("Fill Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The polypins should be filled with a little bottler, leaving half an inch of headspace."
step.newSubStep(("Fill each of the polypins. Add the tap and purge the remaining air ",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessH.bottlingAndKegging.newstep("Fill Mini Kegs")
step.condition=[]
step.condition.append(['miniqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The minikegs should be filled with a little bottler, leaving an inch of headspace."
step.newSubStep(("Fill each of the mini kegs",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessH.bottlingAndKegging.newstep("Fill bottles")
step.text="While filling it is useful to group the bottles by type to ensure even filling."
step.newSubStep(("Begin filling each bottle leaving an inch of space at the neck empty.",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"


step = myprocessH.bottlingAndKegging.newstep("Yeast Harvest Part 1")
step.text="To harvest the yeast the yeast cake is topped up with clean pre-boiled/sterilised water which will separate the yeast from the trub."
step.newSubStep(("Ensure any remaining beer not bottled is emptied carefully out of the fermentation bin, there should be very little (less than 200ml) beer remaining",{'complete':1}))
step.newSubStep(("Add 400ml of water to the yeast cake and stir gently",{'complete':1}))
step.newSubStep(("Remove the large spoon and let the fermentation bin settle for 1 hour",{'complete':1}))
step.img=["yeastcake1.png"]
step.attention="Sanitisation is very important while harvesting the yeast"


step = myprocessH.bottlingAndKegging.newstep("Attach Caps")
step.text="Once bottling has finished it is time to attach the caps."


step = myprocessH.bottlingAndKegging.newstep("Yeast Harvest Part 2")
step.text="The yeast from the fermentation bin will then be stored in the sterilised airtight container and set aside in the fridge"
step.newSubStep(("Fill the 2L jar with the solution from the fermentation bin, and then store in the fridge",{'complete':1}))
step.img=["yeastcake2.png"]
step.attention="Sanitisation is very important while harvesting the yeast. A label should be added to the jar to ensure the yeast is not used after 14 days,"

#ensure beer is removed without sucking up the yeast, 200ml beer on top is ok
#add 1L of water into bottom of fermentation bin.... swirl to ensure yeast is loose (or stir if we have the spoon in the bucket still).
#empty into 2L container.  straisfy
#

 # donosbourner.

step = myprocessH.bottlingAndKegging.newstep("Optional Secondary Conditioning")
step.text="If the ambient temperature is less than 18 degC it is a good idea to put the bottles into a water bath which can be heated to 20 degC. This ensures that the yeast has ideal conditions for working through the new fermenetables in the priming sugar"
step.attention="If using an aquarium heater in the water bath - it must always remain submerged. Ensure the water is at the correct temperature before adding bottles"
step.img=['secondarycondition.png']

step = myprocessH.bottlingAndKegging.newstep("Code bottles")
step.text="Ensure that the bottles can be identified, either via crown caps, labels etc. Once the beer is in condition full size labels may be added."
step.fields.append( ('Number of Bottles','numbottles','') )
step.fields.append( ('Number of Bottles (bad fills)','numbottlesbadfills','') )
step.fields.append( ('Number of MiniKegs','minikegs','') )
step.fields.append( ('Wastage in fermentation bin','fvpostbottlewastage','') )

step = myprocessH.bottlingAndKegging.newstep("Cleanup")
step.text="All equipment should be cleaned and left to dry before packing away for the next brewday"
step.attention="Ensure all equipment is completely dry before packing away."

step = myprocessH.bottlingAndKegging.newstep("Monitor Conditoning")
step.text="In the first si weeks it is necessary to check the progress of conditoning."
step.newSubStep(("After 1 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 2 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 3 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 4 sample beer 1, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 5 sample beer 2, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 6 sample beer 3, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))




myprocessH.save("process/allena29/26AG27i28")
myprocessH.generateMySql()









myprocessI=brwlabProcess()
myprocessI.credit="Adam Allen"
myprocessI.name="27AG28i29"


myprocessI.description="Worsdell Brewing - An updated process for use in the entirely within the garage, with the introduction of basic water treatment"

myprocessI.boilers = [kettle70l]
myprocessI.hlt = hlt
myprocessI.mash_tun = mash_tun




# Preparation
step = myprocessI.brewday.newstep("Preparation")
#step.newSubStep( ("If using a fermentation-fridge move it into position, it is necessary to wait >12 hours after moving the fridge before using.",{'complete':1}) )
step.newSubStep( ("Add ice-boxes to the freezer, these will be used to cool the immersion chiller water",{'complete':1}) )
#step.newSubStep( ("Ensure batteries for thermometers are available",{'complete':1}))
#step.newSubStep( ("Ensure clean towells are available as well as clean dry cloths for the floor",{'complete':1}))
step.text="The day before brew day the preparation above should be carried out, as well as checking stock/ingredients are available"



# Gather things
step = myprocessI.brewday.newstep("Assemble Mash/Lauter Tun")
step.text="Assemble the bucket in bucket mash tun, complete with scavenger tube. Gather Sparge Arm, Vorlauf Funnel Paddle and digital thermometer."
step.img=['assemblemashtun.png']

# Gather things
step = myprocessI.brewday.newstep("Assemble Hot Liquor Tank")
step.text="Assemble the hot liquor tank, complete with latstock and thermometer probe"
step.img=['assemblehlt.png']

# Gather things
#step = myprocessI.brewday.newstep("Assemble Kettle")
#step.text="Assemble the kettles with ball-valve tap. Use a stainless steel washer on the inside and pfte tape around thread. "
#step.img=['assemblekettle.png']

# Gather things
step = myprocessI.brewday.newstep("Assmeble Fermentation Bin")
step.text="Assemble the fermentation bin, complete with back filter"
step.img=['assemblefv.png']


# Gather things
#step = myprocessI.brewday.newstep("Gather small stockpots")
#step.text="Gather small stockpots and measuring spoons, these will be used to contain the grain"



## Gather things
#step = myprocessI.brewday.GatherThings()
#step.text="The grain can be measured later"

# Clean Equipment
step = myprocessI.brewday.newstep("Clean Equipment")
step.text="Clean equipment with a mild detergent. It is important to clean equipment before use, any equipment used before the boil only needs to be cleaned as the wort will be sterilised during the boil. Equipment used after the boil must either be sterilised with sterilising solution, or limited equipment may be sterilised in the boiler. Note: don't use 2 real taps for the HLT, use one dummy tap. The equipment to clean is: hlt, sparge arm, mash tun, jug, large paddle, thermometer, stoarge box, kettles and jerry can. "
step.addEquipment( mashpaddle )
step.addEquipment( hlt )
step.addEquipment( atc800) 
step.addEquipment( sparge_arm )
step.addEquipment( mash_tun )
step.addEquipment( jug ) # try do without a jug
step.addEquipment( smalljug )
step.addEquipment( largepaddle )
step.addEquipment( thermometer )
#step.addEquipment( storagebox )
#step.addEquipment( filteringFunnel )
step.addEquipment( kettle20l )
step.addEquipment( kettle15l )
step.addEquipment( jerry10l )
step.newSubStep( ("Clean HLT",{'complete':1}) )
step.newSubStep( ("Clean FV",{'complete':1}) )
step.newSubStep( ("Clean Kettle",{'complete':1}) )
step.newSubStep( ("Clean Mashtun",{'complete':1}) )

# Clean work area
step = myprocessI.brewday.newstep("Clean Work Area")
step.text="Clean the entire work area with mild detergent. It is important to ensure the entire work area is clean before commencing the brew day"


# Setup Equipment
#step = myprocessI.brewday.newstep("Setup Equipment")
#step.text="The hot liquor tank must be positioned higher than the mash tun with the sparge arm assembled. The brewing kettle is positoned the lowest."
#step.newSubStep( ("Setup the equipment as pictured",{'complete':1}) )
#step.newSubStep( ("Plug in the ATC-800+ temperature controller and set to ...strike_temp_5...degC. Ensure the supply is off and then connect the power leads from the controller to the elements on the HLT.",{'complete':1}))

step.img=["sterilise_setup1.png"]



### modified for a more logical break in the proceedings.



# Fill the HLT
step = myprocessI.brewday.newstep("Fill HLT (for Mash Liquor)")
step.text="Fill the HLT with ...mash_liquid_6...L of water for the mash and add a campden tablet to remove chlorine, stir and leave for 5 minutes"
step.addConsumable( campdenTablet, 1)
# Fill the HLT
step = myprocessI.brewday.newstep("Treat Mash Liquor")
step.text="Treat the mash water to remove alkalinity, this should be done 5 minutes after adding the campden tablet. The low-resolution method for alkalinity test is used as the alkalinity is very hard. Once the salifert solution is orange/pink  "
step.addConsumable( salifert , 1)
step.newSubStep( ("Add 2ml of water into the test vial for the Salifert Alkalinity Test.",{'complete':1}))
step.newSubStep( ("Add 2 drops of KH-Indicator to the test vial.",{'complete':1}))
step.newSubStep( ("Add 1m of reagent to the fine granularity syringe.",{'complete':1}))
step.newSubStep( ("Add drop by drop to the, mixing the solution each time, the colour needs to change from blue/green to orange/pink, turn the syringe upside down and use the reading at the upper part of the black piston",{'complete':1}))
step.newSubStep( ("Add CRS based upon the calculations below to the mash liquid and stir.",{'complete':1}))
step.fields.append( ('Mashwater PH','mashWaterPH','') )
step.fields.append( ('Mash Salifert Reagent Remaining','__mashSalifertReagent','0.10'))
step.widgets['mashAlkalinity'] = ('salifertAlkalinity',['__mashSalifertReagent'])
step.fields.append( ('Mash Alkalinity','mashAlkalinity',''))
step.widgets['mashCrsAdjustment'] = ('mashCrsAdjustment',['__mashSalifertReagent'])
step.fields.append( ('Mash CRS Adjustment','mashCrsAdjustment',''))
step.img=['treatwater.png']

# Fill the HLT
step = myprocessI.brewday.newstep("Begin heating mash water")
step.text="(HLT) Heat the mash water to strike temperature + 5 degC (...strike_temp_5... degC)"
step.attention="Do not turn on the temperature controller until the elements in the kettle are covered with water."
step.img=['treatwater.png']


# Gather grain
step = myprocessI.brewday.newstep("Gather Grain")
step.text="Gather the and measure the grain required for the brewday"
step.auto="gatherthegrain"
step.addConsumable(burton,2)
step.newSubStep( ("Add 1 teaspoon of gypsum -OR- 2 teaspoons of burton water salts to the grain.",{'complete':1}))		# this is correct, thought it might have been too much


# Mash
step = myprocessI.brewday.newstep("Get Ready to Mash")
step.text="Once the Mash Water has been heated to 65C then pre-heat the mash tun."
step.newSubStep( ("Boil 1.5L of tap water and add to the mash tun, add the lid to the mash tun",{'complete':1}))
#step.auto="grainqty"
step.img = ['mash.png']


# Fill the Mash Tun
step = myprocessI.brewday.newstep("Fill the mash tun with mash liquid")# and set aside the grain. During this step the mash tun should be well insulated to maintain a stable temperature")
step.text="Fill the mashtun with the mash liquor in order the water is to ...strike_temp_5...C (Strike Temp ...strike_temp...C). The water in the HLT should be heated to 5degC higher than strke temp to account for some losses while transferring the liquid, however the temperature should be monitored. Note: if more water is used in the mash tun the strike temperature should be lower, if less water is used then the strike temperature should be higer."
step.prereq="Mash Water is at ...strike_temp_5...C"
step.newSubStep( ("Discard the water used for preheating the mash tun into the 20l kettle",{'complete':1}))
step.newSubStep( ("Fill the mash tun with  ...mash_liquid...L of water heated to ...strike_temp_5...C.", {'complete':1}) )
step.newSubStep( ("Set aside 1.7L of boiling water and 1.7L of cold water which may optionally may be used for adjustment of temperature/consistency", {'complete':1}))
step.attention="If the grain temperature is not between 15-20 degC then the calculations should be re-run to provide a hotter/colder strike temp."


#
#
#
myprocessI.recipeUpgrades['grainthicknessMustBeGreaterThan'] = 1.35


# Dough in the grain 
step = myprocessI.brewday.newstep("Dough in the grain")
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
step = myprocessI.brewday.newstep("Fill HLT (for Sparge Liquor)")
step.text="Fill the HLT so that it contains ...sparge_water...L of water for the sparge and add a campden tablet to remove chlorine and a level teaspoon of citric acid, stir and leave for 5 minutes"
step.addConsumable( campdenTablet, 1)
step.fields.append(('(MID1) Mash Temp Acheived','mash_mid1_temp',''))

# Fill the HLT
step = myprocessI.brewday.newstep("Treat Sparge Liquor")
step.text="Treat the mash water to remove alkalinity, this should be done 5 minutes after adding the campden tablet. The low-resolution method for alkalinity test is used as the alkalinity is very hard. Once the salifert solution is orange/pink  "
step.addConsumable( salifert , 1)
step.newSubStep( ("Add 2ml of water into the test vial for the Salifert Alkalinity Test.",{'complete':1}))
step.newSubStep( ("Add 2 drops of KH-Indicator to the test vial.",{'complete':1}))
step.newSubStep( ("Add 1m of reagent to the fine granularity syringe.",{'complete':1}))
step.newSubStep( ("Add drop by drop to the, mixing the solution each time, the colour needs to change from blue/green to orange/pink, turn the syringe upside down and use the reading at the upper part of the black piston",{'complete':1}))
step.newSubStep( ("Add CRS based upon the calculations below to the sparge liquid and stir.",{'complete':1}))
step.fields.append( ('Sparge Water PH','spargehWaterPH','') )
step.fields.append( ('Mash Salifert Reagent Remaining','__spargeSalifertReagent','0.10'))
step.widgets['spargeAlkalinity'] = ('salifertAlkalinity',['__spargeSalifertReagent'])
step.fields.append( ('Sparge Alkalinity','spargeAlkalinity',''))
step.widgets['spargeCrsAdjustment'] = ('spargeCrsAdjustment',['__spargeSalifertReagent'])
step.fields.append( ('Sparge CRS Adjustment','spargeCrsAdjustment',''))
step.img=['treatwater.png']


# Fill the HLT 
step = myprocessI.brewday.newstep("Heat Sparge Liquor")
step.text="(MASH + SPARGE) The sparge water is expected to take around ...sparge_heating_time... minutes to heat."
step.newSubStep(("Begin heating the sparge water to ...sparge_temp...C",{'complete':1}))
step.attention="The HLT is constructed with standard kettle elements, therefore it is advisable to alternate between the elements 3 or 4 times during the heating. The temperature controller should only power one kettle element at any time."


# Bring the wort to the boil
## if we are doing First Wort Hops then we need this here;
step = myprocessI.brewday.newstep("Measure Hops")
step.text="Measure the hops for addition to the kettle."
step.auto="hopmeasure_v3"
step.img=["boil.png"]


# Begin sterilising remaining equipment
step = myprocessI.brewday.newstep("Sterilise Equipment")
step.text="It is important throughout the brew day to keep any equipment which will come into contact with the wort post-boil sterilised. Equipment used before the boil does not need to be sterilised but does need to be clean. Note: the silicone tube used for transferring wort from the boiler into the fermentation bin will be sanitised in a later step."
step.newSubStep( ("Fill the fermentation bin with 10 litres of warm water and 2 tsp of sterilising powder.",{'complete':1}))

# track somehow if the fermentation bin has a tap on the bottom

#step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer probe, and a glass jug into the fermentation bin.",{'complete':1}))
#step.newSubStep( ("Add hydrometer,large spoon,trial jar, thermometer and a glass jug into the fermentation bin.",{'complete':1}))
#step.newSubStep( ("Add equipment that will be used post boil. Small Jug, Hydrometer, Trial Jar, Thermometer",{'complete':1}))
#step.newSubStep( ("Ensure fermentation bin is fully sterilised with equipment, after 10 minutes of sterilising equipment place equipment in the small storage stockport.",{'complete':1}))
step.newSubStep( ("Ensure fermentation bin is fully sterilised with equipment.",{'complete':1}))
step.newSubStep( ("Ensure a 'filter' is added to the back of the fermentation bin tap",{'complete':1}))
step.newSubStep( ("Ensure all the feremntation bin has been sterilised and empty solution into the small stock pot.",{'complete':1}))
step.img=['sterilise1step.png']
step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."



step.addEquipment( smalljug )
step.addEquipment( fermentationbin6gal )
step.addEquipment( hydrometer )
step.addEquipment( trialjar )
#step.addEquipment( thermometer3 )
step.addEquipment( thermometer2 )
#step.addEquipment( immersionchiller )
myprocessI.immersionchiller = immersionchiller
#step.addConsumable( pfte, 0.5 )
step.fields.append(('(MID2) Mash Temp Acheived','mash_mid2_temp',''))
step.fields.append(('(MID3) Mash Temp Acheived','mash_mid3_temp',''))
step.fields.append(('(MID4) Mash Temp Acheived','mash_mid4_temp',''))
step.fields.append(('(MID5) Mash Temp Acheived','mash_mid5_temp',''))
step.fields.append(('(MID6) Mash Temp Acheived','mash_mid6_temp',''))
step.fields.append(('(MID7) Mash Temp Acheived','mash_mid7_temp',''))



# Rinse Equipment
step = myprocessI.brewday.newstep("Rinse Equipment")
step.text="Rinse Equipment in the same way as sterilising, equipment should be rinsed with 25 litres of cold water."


step.attention="Be careful to monitor the temperature during the mash, if the mash tun is well insulated it may be that the temperature rises not falls. Temperature must not rise above 70C. High temperautere 68.5-70C results in more unfermentables, 67-68.5 will result in medium body beers."

step.fields.append(('(MID8) Mash Temp Acheived','mash_mid8_temp',''))
step.fields.append(('(MID9) Mash Temp Acheived','mash_mid9_temp',''))
step.fields.append(('(MID10) Mash Temp Acheived','mash_mid10_temp',''))
step.fields.append(('(MID11) Mash Temp Acheived','mash_mid11_temp',''))
step.fields.append(('(MID12) Mash Temp Acheived','mash_mid12_temp',''))
step.fields.append(('(MID13) Mash Temp Acheived','mash_mid13_temp',''))
step.fields.append(('(MID14) Mash Temp Acheived','mash_mid14_temp',''))


# Monitor Mash Equipment
step = myprocessI.brewday.newstep("Monitor the Mash")
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
step = myprocessI.brewday.newstep("Assemble Sparge Setup and begin Recirculation")
#step.addConsumable(muslinbag,1)
step.addEquipment(funnel)


step.text="Once the sparge water is at the correct temperature ...sparge_temp...C AND the mash duration has completedthe sparge setup can be setup. During this step the cloudy wort with bits of grain will drained leading to a natural grain filter forming."
step.newSubStep( ("Take off the lid from the mash tun and assemble the sparge arm",{}))
step.newSubStep( ("Allow up to 6 litres of wort to drain from the mash tun into the kettle, the wort should be carefully added back to the top of the lauter tun trying to ensure minimal disturbance.",{'complete':1}))
step.fields.append(('(End) Mash Temp Acheived','mash_end_temp',''))
step.newSubStep( ("Collect sample of mash to measure PH",{'complete':1}))
step.attention="Set the thermometer to alarm if the temperature is higher than 71deg. If it is then lid should be lifted to reduce the heat."
step.img=["spargesetup.png"]



step = myprocessI.brewday.newstep("First Wort Hopping")
step.condition=[]
step.condition.append( ['first_wort_hop_qty','>',0] )
step.text="Add the first wort hops to the boiler before starting to sparge"
step.auto="hopaddFirstWort_v3"



# Start Sparge
step = myprocessI.brewday.newstep("Start Fly Sparging")
step.text="(SPARGE) Sparging will drain the sugar from the grain providing us with wort. The process of sparging should be carried out slowly. The temperature of the gain bed will be raised during this proess (note there is no instant change of temperature). The grain bed should stay below 76 deg C. We need to aim for a boil volume of ...boil_vol...L. General wisdom is to keep 1 inch of water above the grain bed- however there is a trade off (the more water above the grain bed the smaller/slower temperature rise of the grain bed, the less water above the grain bed the bigger/quicker temperature rise of the grain bed."
#Throughout the process monitor flow of liquid into and out of the mash tun to try maintain an equilibrium"
step.newSubStep( ("Collect sample of sparge water to measure PH",{'complete':1}))

step.img=["dosparge.png"]







step = myprocessI.brewday.newstep("Start Boiling the Wort")
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
step = myprocessI.brewday.newstep("Dynamic Recipe Adjustment")
step.text="If the mash was particularly efficent/inefficient it may be desirarble to top up fermentables, dilute wort, increase/decrease hop quantities. The target pre-boil gravity is ...preboil_gravity... (total post-boil gravity ...estimated_og...). The target wort volume required is ...boil_vol...L. The gravity quotes here takes account of later topup of ...topupvol...L. Estimated gravity post boil pre cooling is ...postboilprecoolgravity..."
step.attention="Be careful with topup at this stage, the dilution of cooling/evaporation will concentrate the wort further. If the wort is too concentrated at this stage delay dilution until the cooling stage. Making readings of volume/gravities is the most important thing at this stage."



step.fields.append( ('Topup Gravity','__topupgravity','1.000') )
step.fields.append( ('Topup Gravity Temp','__topupgravitytemp','20') )
step.widgets['__topupgravityadjusted'] = (' gravityTempAdjustment',['__topupgravity','__topupgravitytemp'])
step.fields.append( ('Topup Gravity Adjusted','__topupgravityadjusted','1.000') )
step.fields.append( ('Final Gravity Required','__topupgravityrequired','') )



step.img=["sighttube.png"]


# Bring the wort to the boil
step = myprocessI.brewday.newstep("Bittering Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Once the wort is at a rolling boil the hops can be added and the lid should be left half covered."
step.img=["boil.png"]
step.newSubStep(("Start timer for 45 minutes after which the protofloc copper finings will be added",{'complete':1,'kitchentimer' : ('b',3600) }))
step.newSubStep(("Turn on the fridge with ATC Control to 20 degC",{'complete':1}))
step.auto="hopaddBittering_v3_withadjuncts"


# Bring the wort to the boil
step = myprocessI.brewday.newstep("Pump Wort")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="(BOIL + PUMP) With the wort at a boil recirculate with the pump to ensure that the pump and tubing is sterilised. Pump for 5 minutes"



# Bring the wort to the boil
step = myprocessI.brewday.newstep("Aroma Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the aroma hops to the kettle with 15 minutes remaining. The immersion chiller will need to be sterilised during this period and irishmoss/protofloc added to help coagulate proteins in the wort. For small boils it may be necessary to tie the immersion chiller with cable ties."
step.newSubStep(("Start timer for 15 minutes .",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the irishmoss/protofloc and continue boiling for 15 minutes.",{'complete':1,'kitchentimer' : ('a',900) }))
step.newSubStep(("Add the immersion chiller",{'complete':1,'kitchentimer' : ('a',900) }))
step.auto="hopaddAroma_v3"
step.img=["boil.png"]


## Sanitise
#step = myprocessI.brewday.newstep("Sanitise the boiler tube")
#step.text="Put the transfer tube in the kettle, open the tap of the kettle and start the pump to recirculate the boiling wort in order to sanitise the transfer tube."


# Bring the wort to the boil
step = myprocessI.brewday.newstep("Finishing Hops")
step.condition=[]
#step.condition.append( ['boil_vol','>',26] )
step.text="Add the finishing hops to the kettle and stop the heat."
step.auto="hopaddFinishing_v3"
step.img=["boil.png"]


# Yeast Rehydration
#step = myprocessI.brewday.newstep("Boil Yeast Rehydration Water")
#step.text="Rehydration yeast provides a gentle start for the yeast and helps fermentation start quickly. If using yeast slurry instead then this step will still be carried out to sterilise the jug in order to measure the yeast slurry."
#step.newSubStep(("Boil 500ml of water and set aside in a pyrex jug",{'complete':1}))
#step.newSubStep(("After 10 minutes put the hug in a water bath to cool the water to 25 degC",{'complete':1}))
#step.attention="Yeast should nto be added to the rehydration water unless is is <25 degC"




# Cool Wort
step = myprocessI.brewday.newstep("Cool wort")
step.text="(PUMP) It is important to cool the wort quickly, ice water can help to cooling water towards the end of cooling. The estimated gravity required is ...estimated_og... Do not aerate the wort while, however the pump can be used to recirculate the wort through the already sanitised transfer tube."
step.newSubStep(("Setup the immersion chiller and and start pushing cold water through to cool the wort to 20 degC",{'complete':1}))
step.img=["drain3.png"]
step.newSubStep(("With the temperature of the wort at 35degC start using ice to cool the temperature of the cooling water.",{'complete':1}))
step.newSubStep(("Add half of the yeast contents to the rehydration water, for Safale S04 the temperature of the yeast rehydration water should be 27degC +/- 3degC",{'complete':1}))
step.condition=[]
step.fields.append( ('Post Boil Volume (Pre Cool)','postboilvolumebeforecool','') )



# Drain Wort
step = myprocessI.brewday.newstep("Pump wort into fermentation bin")
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
step = myprocessI.brewday.newstep("Topup")
step.text="As the wort is cooling a decision should be made on the gravity of the resulting wort. It is hard to increase the gravity (as the high gravity wort is already used) but easy to reduce the gravity (as diluted wort/sterilised water will be easily available). It is best to make the decision when the wort is as cool as possible to reduce the effect of the hydrometer adjustments. If there was a high mash temperature factor in high final gravity when trying to calculate alcohol. Too severe a dilution will reduce the bittering/hop aroma. Planned volume in the fermenter (pretopup)....precoolfvvolume... with a later topup of ...topupvol...L, planed original gravity ...postboil_precool_og.../...estimated_og... (precool/cool)  planned final gravity ...estimated_fg... planned abv ....estimated_abv..."
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
step = myprocessI.brewday.newstep("Measure")
step.text="(FERM) Recording results is important to track the quality of the brew. The expected original gravity is ...estimated_og..., final gravity estimate is ...estimated_fg..., estimated abv ...estimated_abv..."
step.newSubStep(("Aerate the wort for 5 minutes",{'complete':1}))
step.newSubStep(("After aerating the wort measure take a sample to measure the original gravity.",{'complete':1}))
step.fields.append( ('Original Gravity','og','') )
step.fields.append( ('Fermentation bin Weight','postboilweight','') )
step.fields.append( ('Fermentation bin vol (after cooling)','postboilvol','') )
step.fields.append( ('Wort left in boiler vol','leftovervol','') )



step = myprocessI.brewday.newstep("Measure PH from brewday")
step.text="Various samples should have been taken start of mash, end of mash and sparge water to determine the PH throughout the process. The PH meter will need to be calibrated with a solution of a known PH at a set temperature. 4.00 @ 5-25, 4.01 @ 30, 4.02 @ 35, 4.03 @ 40, 4.04 @ 45, 4.06 @ 50, 4.07 @ 55, 4.09 @ 60, 4.12 @ 70, 4.16 @ 80, 4.20 @ 90, 4.22 @ 95. 6.95 @ 5, 6.92 @ 10, 6.90 @ 15, 6.88 @ 20, 6.86 @ 25, 6.85 @ 30, 6.84 @ 35-40, 6.83 @ 45-55, 6.84 @ 60, 6.85 @ 70, 6.86 @ 80, 6.88 @ 90"
step.attention="PH meter is calibrated for 25degC."
step.fields.append( ('Mash PH','mashPH','') )
step.fields.append( ('Post Mash PH','postMashWaterPH','') )
step.fields.append( ('Spargewater PH','spargeWaterPH','') )
step.fields.append( ('Finished Wort PH','wortPH','') )


## Move Fermentation Bin
#step = myprocessI.brewday.newstep("Move Fermentation Bin")
#step.newSubStep(("Setup temperature controller for the fermentation fridge and set the temperature to 20degC. The temperature probe must be insulated against the side of the fermentation bin in order to measure the wort temperature as accurately as possible",{'complete':1})) 
#step.text="Move the fermentation bin to a suitable location for the duration of fermentation (ideally a stable temperature). It may help to tranfer some of the COOLED wort into the 15L kettle before moving, and then recombining into the fermentation bin. At this stage of the process aeration is ok."
#step.attention="The 15L kettle must remain sterile and should be emptitied of all hot-break/hops before using it"
#step.img=['tempcontrol.png']
#


# Pitch
step = myprocessI.brewday.newstep("Pitch Yeast")
step.text="If using yeast slurry then measure 400ml of slurry assuming the batch size is <6 gallon and the yeast slurry must be less than 14 days old. Before using yeast slurry a check on the progress of ferementation from the previous batch is required."
step.newSubStep(("Once the wort is at pitching temperature (20degC)",{'complete':1}))
#oistep.newSubStep(("Optionally add an immersion heater set for 18degC",{'complete':1}))
step.addConsumable(yeastvit,0.5)
step.newSubStep(("Pitch the yeast",{'complete':1}))
step.newSubStep(("Add half a teaspoon of yeastvit",{'complete':1}))



###########################
#Post Brew Day


step = myprocessI.postbrewday.newstep("Kraussen")
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


step = myprocessI.postbrewday.newstep("Dryhop")
step.text ="After 3 days add the dry hops. There is differing opinion about adding hops, too early and the aroma is driven off by the CO2 produced in fermentation, too late and there *may* be a *potential* oxidation risk. The alcohol should protect anynasty organisms in the hops from taking hold. However the hop tea-balls can still be santiised in boiling water."
step.auto="dryhop"
step.condition=[]
step.condition.append( ['dryhop','>',1] )
step.newSubStep(("Kraussen Observed.",{'complete':1}))

step = myprocessI.postbrewday.newstep("Measure specific gravity (1st)")
step.text ="After 6 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 1 (1.xxx)','sg1',''))


step = myprocessI.postbrewday.newstep("Measure specific gravity (2nd)")
step.text ="After 7 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 2 (1.xxx)','sg2',''))


step = myprocessI.postbrewday.newstep("Measure specific gravity (3rd)")
step.text ="After 8 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 3 (1.xxx)','sg3',''))


step = myprocessI.postbrewday.newstep("Measure specific gravity (4th)")
step.text ="After 9 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 4 (1.xxx)','sg4',''))

step = myprocessI.postbrewday.newstep("Measure specific gravity (5th)")
step.text ="After 10 days measure the specific gravity by taking a small sample from the fermentation bin. The estimated final gravity is ...estimated_fg.... Even if the specific gravity is lower than the estimate it is important that there is a stable reading two days running to avoid primary fermentation continuing in the bottles."
step.fields.append( ('Specific Gravity 5 (1.xxx)','sg5',''))




step = myprocessI.postbrewday.newstep("Calculate Alcohol")
step.text="The alcohol can be calculated from the original gravity and the stable final gravity readings."
step.fields.append( ('Measured Final Gravity','__measuredFg_abv',''))
step.widgets['__abv'] = ('abvCalculation',['og','__measuredFg_abv'])
step.fields.append( ('ABV','__abv','') )


step = myprocessI.bottlingAndKegging.GatherThings()


step = myprocessI.bottlingAndKegging.newstep("Gather Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gatherthepolypins"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Polypins\n"
step.newSubStep(("Gather ...polypinqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

step = myprocessI.bottlingAndKegging.newstep("Gather Mini Kegs")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gathertheminikegs"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Minikegs with bungs/safety vent bungs\n"
step.newSubStep(("Gather ...minikegqty... polypins",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available


step = myprocessI.bottlingAndKegging.newstep("Gather Bottles")
step.condition=[]
step.condition.append(['bottleqty','>',0])
step.auto="gatherthebottles"
step.stockDependency=["bottle"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Gather Bottles\n"
step.newSubStep(("Gather ...bottleqty... bottles",{'complete':1 }))
	# need to think about removing this step if no stock of mini kegs available

#step = myprocessI.bottlingAndKegging.newstep("Move fermentation bin")
#step.text="If needed move the fermentation bin to a height suitable for bottling from. This should be carried out early to allow any disturbance to settle"


step = myprocessI.bottlingAndKegging.newstep("Clean Work Area")
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

#step = myprocessI.bottlingAndKegging.newstep("Setup Work Area")
#step.text="Setup the work area as shown in the image, cleaning the bottles may be carried out the previous evening to save time."
#step.img=["bottlingsetup.png"]


step = myprocessI.bottlingAndKegging.newstep("Clean Bottles")
step.text="Cleaning the bottles using hot water and detergent."
step.newSubStep(("Clean the bottles using a bottle brush to ensure no deposits are left in the bottle. Drain solution out of the bottles.",{'complete':1}))
step.newSubStep(("Rinse the bottles with a small amount of water.",{'complete':1}))
step.img=['bottleclean.png']

step = myprocessI.bottlingAndKegging.primingSolution()
step.text="Priming solution provides more fermentables for the yeast to convert into further alcohol and natural carbonation"
step.newSubStep(("Measure ...primingsugartotal... (...primingsugarqty... per bottle) priming sugar and set aside.",{'complete':1}))
step.newSubStep(("Add ...primingwater... ml of water to the saucepan and heat to 90degC, once at 90degC stir in the sugar",{'complete':1}))
step.newSubStep(("Maintain the temperature at 85degC for 5 minutes and then cool in a water bath to less that 30 degC.",{'complete':1}))
step.img=['primingsolution.png']
step.attention="Be careful with the volume of sugar in each bottle as introducing too many fermentables can lead to exploding bottles"


#step = myprocessI.bottlingAndKegging.newstep("Setup Work Area 2")
#step.text="Setup the work area as show in the image, during the bottling stage all equipment will be required."
#step.img=["bottlingsetup2.png"]


step = myprocessI.bottlingAndKegging.newstep("Sterilise Crown Caps")
step.text="Crown caps needs to be sterilised before use."
step.newSubStep(("Boil 500ml of water and add to a clean pyrex jug",{'complete':1}))
step.newSubStep(("Add ...num_crown_caps... crown caps/plastic caps to the jug and set aside.",{'complete':1}))


step = myprocessI.bottlingAndKegging.newstep("Prepare Jars for Yeast Harvesting")
step.text="Yeast harvesting may be carried out if fresh yeast was used for a brew with an original gravity < 1.060 and the next brew is due to be carried out in less than 14 days"
step.newSubStep(("Fill the 2L Jar with boiling water, add the lid securely and set aside",{'complete':1}))
step.newSubStep(("Fill each of the 400ml jars with boiling water add the lid a set aside.",{'complete':1}))
step.newSubStep(("After 10 minutes add the 400ml jars into a cold water bath to cool the water",{'complete':1}))

#step = myprocessI.bottlingAndKegging.newstep("Sterilise Saucepan")
#step.text="Sterilise the saucepan, thermometer and slotted spoon, and measuring spoon by adding the equipment to the saucepan and filling with boiling water. Set aside for at least 15 minutes"



step = myprocessI.bottlingAndKegging.newstep("Fill bottles with sterilising solution")
step.text="Use 3/4 of a level teaspoon of sterilising solution in a full jug of warm water. (which equates to 1 level teaspoon per 3L)"
step.newSubStep(("Arrange bottles in a crate ready to sterilise",{'complete':1}))
step.addConsumable( sterilisingPowder,4)
step.addEquipment( saucepan )
step.addEquipment( funnel )
step.img=['bottlingseq.png']
step.text="The sterilising of bottles is carried out by filling each bottle full with a sterilising solution. The funnel will be sterilsing as the bottles are filled. "
step.auto="sterilisebottles"
step.newSubStep(("Immerse the little bottler in a bottle of sterilising solution rotate to ensure both ends are covered inside and out.",{'complete':1}))


step = myprocessI.bottlingAndKegging.newstep("Empty bottles")
step.img=['bottlingempty.png']
step.text="After 5 minutes begin to partially empty sterilising solution from the bottles filling any of the mini kegs, each mini keg.It is important to the make sure the top of the bottle is sterilised. Bottles should be half emptied, and then given a good shake before finishing emptying the bottle."
step.attention="If using mini kegs or polypins the sterilising solution should be reused for the mini kegs/polypins"
step.newSubStep(("The first two bottles should be emptitied into the large jug, this gives an opportunity to serilise the top of the bottle",{'complete':1}))
#step.newSubStep(("If using mini kegs empty the remaining bottles into the mini kegs. Each mini keg should be fully filled with sterilising solution. If there is not enough sterilising solution in the bottles additional solution needs to be made.",{'complete':1}))


step = myprocessI.bottlingAndKegging.newstep("Fill polypins with sterilising solution")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.auto="gather4"
step.stockDependency=["polypin"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"

step = myprocessI.bottlingAndKegging.newstep("Fill mini kegs with sterilising solution")
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.auto="gather3"
step.stockDependency=["keg"]	# check based on category. if none found in this category then the compile() should remove this step
# not sure stock dependency work... should deprecate it in any case
step.text="Fill the mini kegs with sterilising solution from the bottles. Once the sterilising solution from the bottles has been used then more sterilsing solution must be made at the strength of 3/4 of a level teaspoon per large jug\n"


step = myprocessI.bottlingAndKegging.newstep("Empty Polypins")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Empty the sterilising solution from the polypins, using the taps"

step = myprocessI.bottlingAndKegging.newstep("Empty Minikegs")
step.img=['bottlingempty.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Empty the sterilising solution from the minikegs, using the taps"


step = myprocessI.bottlingAndKegging.newstep("Rinse Bottles")
#step.img['bottlingrinse.png']
step.text="Bottles need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.attention="If using mini kegs/polypins the water should be empties into the minikegs/polypins"
step.newSubStep(("Fill each bottle with a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each bottle and empty the water.",{'complete':1}))


step = myprocessI.bottlingAndKegging.newstep("Rinse Polypins")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.text="Polypins need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  polypin a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each polypin and empty via the tap.",{'complete':1}))


step = myprocessI.bottlingAndKegging.newstep("Rinse Minikegs")
#step.img['bottlingrinse.png']
step.condition=[]
step.condition.append(['minikegqty','>',0])
step.text="Minikegs need to be well rinsed to ensure traces of the sterilising solution are rinsed"
step.newSubStep(("Fill each  minikeg a third full with cold water",{'complete':1}))
step.newSubStep(("Shake each minikeg and empty via the tap.",{'complete':1}))





	# need to think about removing this step if no stock of mini kegs available

step = myprocessI.bottlingAndKegging.newstep("Add priming solution to each bottle")
step.text="Stir the priming and then add 15ml of priming solution to each bottle"


step = myprocessI.bottlingAndKegging.newstep("Add priming solution to each polypin")
step.text="Stir the priming and then add 45ml of priming solution to each polypin"
step.condition=[]
step.condition.append(['polypinqty','>',0])

step = myprocessI.bottlingAndKegging.newstep("Add priming solution to each minikeg")
step.text="Stir the priming and then add 120ml of priming solution to each minikeg"
step.condition=[]
step.condition.append(['minikegqty','>',0])


# Fill polypins kegs first
step = myprocessI.bottlingAndKegging.newstep("Fill Polypins")
step.condition=[]
step.condition.append(['polypinqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The polypins should be filled with a little bottler, leaving half an inch of headspace."
step.newSubStep(("Fill each of the polypins. Add the tap and purge the remaining air ",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessI.bottlingAndKegging.newstep("Fill Mini Kegs")
step.condition=[]
step.condition.append(['miniqty','>',0])
step.stockDependency=["keg"]		# check based on category
step.text="The minikegs should be filled with a little bottler, leaving an inch of headspace."
step.newSubStep(("Fill each of the mini kegs",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"



step = myprocessI.bottlingAndKegging.newstep("Fill bottles")
step.text="While filling it is useful to group the bottles by type to ensure even filling."
step.newSubStep(("Begin filling each bottle leaving an inch of space at the neck empty.",{'complete':1}))
step.attention="While bottling every effort must be taken not to introduce oxygen into the bottled beer. It is not necessary to shake the bottles to mix the beer and priming solution"


step = myprocessI.bottlingAndKegging.newstep("Yeast Harvest Part 1")
step.text="To harvest the yeast the yeast cake is topped up with clean pre-boiled/sterilised water which will separate the yeast from the trub."
step.newSubStep(("Ensure any remaining beer not bottled is emptied carefully out of the fermentation bin, there should be very little (less than 200ml) beer remaining",{'complete':1}))
step.newSubStep(("Add 400ml of water to the yeast cake and stir gently",{'complete':1}))
step.newSubStep(("Remove the large spoon and let the fermentation bin settle for 1 hour",{'complete':1}))
step.img=["yeastcake1.png"]
step.attention="Sanitisation is very important while harvesting the yeast"


step = myprocessI.bottlingAndKegging.newstep("Attach Caps")
step.text="Once bottling has finished it is time to attach the caps."


step = myprocessI.bottlingAndKegging.newstep("Yeast Harvest Part 2")
step.text="The yeast from the fermentation bin will then be stored in the sterilised airtight container and set aside in the fridge"
step.newSubStep(("Fill the 2L jar with the solution from the fermentation bin, and then store in the fridge",{'complete':1}))
step.img=["yeastcake2.png"]
step.attention="Sanitisation is very important while harvesting the yeast. A label should be added to the jar to ensure the yeast is not used after 14 days,"

#ensure beer is removed without sucking up the yeast, 200ml beer on top is ok
#add 1L of water into bottom of fermentation bin.... swirl to ensure yeast is loose (or stir if we have the spoon in the bucket still).
#empty into 2L container.  straisfy
#

 # donosbourner.

step = myprocessI.bottlingAndKegging.newstep("Optional Secondary Conditioning")
step.text="If the ambient temperature is less than 18 degC it is a good idea to put the bottles into a water bath which can be heated to 20 degC. This ensures that the yeast has ideal conditions for working through the new fermenetables in the priming sugar"
step.attention="If using an aquarium heater in the water bath - it must always remain submerged. Ensure the water is at the correct temperature before adding bottles"
step.img=['secondarycondition.png']

step = myprocessI.bottlingAndKegging.newstep("Code bottles")
step.text="Ensure that the bottles can be identified, either via crown caps, labels etc. Once the beer is in condition full size labels may be added."
step.fields.append( ('Number of Bottles','numbottles','') )
step.fields.append( ('Number of Bottles (bad fills)','numbottlesbadfills','') )
step.fields.append( ('Number of MiniKegs','minikegs','') )
step.fields.append( ('Wastage in fermentation bin','fvpostbottlewastage','') )

step = myprocessI.bottlingAndKegging.newstep("Cleanup")
step.text="All equipment should be cleaned and left to dry before packing away for the next brewday"
step.attention="Ensure all equipment is completely dry before packing away."

step = myprocessI.bottlingAndKegging.newstep("Monitor Conditoning")
step.text="In the first si weeks it is necessary to check the progress of conditoning."
step.newSubStep(("After 1 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 2 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 3 week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 4 sample beer 1, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 5 sample beer 2, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))
step.newSubStep(("After 6 sample beer 3, week check the mini kegs are clean and remove pressure build up in polypins",{'complete':1}))




myprocessI.save("process/allena29/27AG28i29")
myprocessI.generateMySql()








sys.exit(0)

print "!!!! NEED TO TEST IF ADDING A SUBSTEP WITH AUTO WORKS ---- see gather grain"
print "!!!! need to think about keeping 23AG suitable for the old setup for gareth/stu/chris"
print "!!!! there is a difference between fv with a tap vs without  -especially sterilise step"

print "!!! start boiling the wort should be the only step ith a big kettle - although it has a screwed up stats (60L with a gravity of 1.0001)"
print "!!! continue fly sparging and start boiling the wort [2] should be hidden with small kettles"
print "!!! dynamic recipeadjustment should be there for both... if ew have poor/good sparge then we might need to adjust "

print "!!! we seem to have lost volume"
print "!!!! android app still doesn't like substeps to be completed"

print "!!! with the big boiler no practical way to cool in the boiler need to cool in the fermentation bin."
print "!!! with large volume no easy way to mobe liquid... suggestion is that the Hlt is kept sterilised and can be used to carry some of the liquid... the boiler is a bit manky from hop crap"
print "!!! adjusted deadspace needs to be  2.75L for --- do we update the equipment?"
