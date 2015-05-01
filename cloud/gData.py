from google.appengine.ext import db

class gProcesses(db.Model):
	"""
	An index of all processes owned by a user
	"""
	owner=db.StringProperty(required=True)
	process=db.StringProperty(required=True)


class gSuppliers(db.Model):
	owner=db.StringProperty(required=True)
	supplier=db.StringProperty(required=True)
	supplierName=db.StringProperty(required=True)
	


class gCompileText(db.Model):
	owner=db.StringProperty(required=True)
	process=db.StringProperty(required=True)	
	activityNum=db.IntegerProperty(required=True)
	stepNum=db.IntegerProperty(required=True)
	subStepNum=db.IntegerProperty(required=False)
	toReplace=db.StringListProperty()


class gContributions(db.Model):
	owner=db.StringProperty(required=True)
	recipeName=db.StringProperty(required=True)
	ingredientType=db.StringProperty(required=False)
	ingredient=db.StringProperty(required=False)
	hopAddAt=db.FloatProperty(required=False)
	ibu=db.FloatProperty(required=False)
	srm=db.FloatProperty(required=False)
	gravity=db.FloatProperty(required=False)


class gWidgets(db.Model):
	owner=db.StringProperty(required=True)
	process=db.StringProperty(required=False)
	activityNum=db.IntegerProperty(required=True)
	stepNum=db.IntegerProperty(required=True)
	widgetName=db.StringProperty(required=False)
	widget=db.StringProperty(required=False)
	widgetValues=db.StringListProperty()
	

class gProcess(db.Model):
	""" 
	Contains the details behind the steps. May merge this into gBrewlogStep
	"""
	owner=db.StringProperty(required=True)
	process=db.StringProperty(required=True)
	stepName=db.StringProperty(required=False)
	stepTitle=db.StringProperty(required=False)
	activityNum=db.IntegerProperty(required=True)
	stepNum=db.IntegerProperty(required=True)
	subStepNum=db.IntegerProperty(required=True)
	text=db.TextProperty(required=False)
	img=db.StringListProperty()
	attention=db.StringProperty(required=False)
	timerName=db.StringProperty(required=False)
	timerTime=db.IntegerProperty(required=False)
	fixed_boil_off=db.FloatProperty(required=False)
	fixed_cool_off=db.FloatProperty(required=False)
	percentage_boil_off=db.FloatProperty(required=False)
	percentage_cool_off=db.FloatProperty(required=False)
	auto=db.StringProperty(required=False)
	needToComplete=db.BooleanProperty(required=False)
	compileStep=db.BooleanProperty(required=False)
	conditional=db.StringListProperty()


class gEquipment(db.Model):
	owner=db.StringProperty(required=True)
	process=db.StringProperty(required=True)#
	name=db.StringProperty(required=True)
	equipment=db.StringProperty(required=True)
	dead_space=db.FloatProperty(required=False)
	activityNum=db.IntegerProperty(required=False)
	heatPower = db.FloatProperty(required=False)
	volume=db.FloatProperty(required=False)
	mustSterilise=db.BooleanProperty(required=False)	
	boilVolume=db.FloatProperty(required=False)



class gPurchases(db.Model):
	owner=db.StringProperty(required=True)
	storecategory=db.StringProperty(required=True)	
	storeitem=db.StringProperty(required=True)
	itemcategory=db.StringProperty(required=False)
	itemsubcategory=db.StringProperty(required=False)
	purchaseQty=db.FloatProperty(required=False)
	qty=db.FloatProperty(required=False)
	originalQty=db.FloatProperty(required=False)
	qtyMultiple=db.FloatProperty(required=False)
	wastageFixed=db.FloatProperty(required=False)
	purchaseDate=db.IntegerProperty(required=False)
	bestBeforeEnd=db.IntegerProperty(required=False)
	supplier=db.StringProperty(required=False)
	purchaseCost = db.FloatProperty(required=False)
	stocktag=db.StringProperty(required=False)
	hopActualAlpha=db.FloatProperty(required=False)
	unit=db.StringProperty(required=False)
	volume=db.FloatProperty(required=False)
	willNotExpire=db.BooleanProperty(required=False)



class gField(db.Model):
	"""
	Used to store infomration against each brewlog fields/widgets/text boxes
	"""
	owner=db.StringProperty(required=True)
	stepNum=db.IntegerProperty(required=False)
	activityNum=db.IntegerProperty(required=False)
	process=db.StringProperty(required=False)
	brewlog=db.StringProperty(required=False)
	recipe=db.StringProperty(required=False)
	fieldLabel=db.StringProperty(required=False)
	fieldKey=db.StringProperty(required=False)
	fieldVal=db.TextProperty(required=False)
	fieldWidget=db.StringProperty(required=False)
	fieldTimestamp=db.IntegerProperty(required=False)

class gBrewlogStep(db.Model):
	"""
	Used to store information about each individual step within a brewlog
	"""
	brewlog=db.StringProperty(required=True)
	owner=db.StringProperty(required=True)
	activityNum=db.IntegerProperty(required=True)
	stepNum=db.IntegerProperty(required=True)
	subStepNum=db.IntegerProperty(required=True)
	sortIndex=db.IntegerProperty(required=False)
	recipe=db.StringProperty(required=False)
	stepName=db.TextProperty(required=False)
	completed=db.BooleanProperty(required=False)
	stepStartTime=db.IntegerProperty(required=False)
	stepEndTime=db.IntegerProperty(required=False)
	needToComplete=db.BooleanProperty(required=False)
	subStepsCompleted=db.BooleanProperty(required=False)
	compileStep=db.BooleanProperty(required=False)
	condition=db.StringProperty(required=False)
	timerName=db.StringProperty(required=False)
	timerTime=db.IntegerProperty(required=False)


class gBrewlogs(db.Model):
	"""
	Used as an index to list users brewlogs
	"""
	brewlog=db.StringProperty(required=False)
	recipe=db.StringProperty(required=False)
	owner=db.StringProperty(required=True)
	brewhash=db.StringProperty(required=False)
	realrecipe=db.StringProperty(required=False)	
	boilVolume=db.FloatProperty(required=False)
	process=db.StringProperty(required=False)
	largeImage=db.StringProperty(required=False)
	smallImage=db.StringProperty(required=False)
	brewdate=db.IntegerProperty(required=False)
	brewdate2=db.IntegerProperty(required=False)
	bottledate=db.IntegerProperty(required=False)
	

class gBrewlogStock(db.Model):
	"""
	Used as an index to list users brewlogs
	"""
	brewlog=db.StringProperty(required=False)
	recipe=db.StringProperty(required=False)
	owner=db.StringProperty(required=True)
	unit=db.StringProperty(required=False)
	storecategory=db.StringProperty(required=False)
	activityNum=db.IntegerProperty(required=False)
	stock=db.StringProperty(required=False)
	qty=db.FloatProperty(required=False)
	cost=db.FloatProperty(required=False)	
	subcategory=db.StringProperty(required=False)
	costrefund=db.BooleanProperty(required=False)
	stocktag=db.StringProperty(required=False)

class gAuthorisedUsers(db.Model):
	authCookie = db.StringProperty(required=True)
	authEmail = db.StringProperty(required=False)
	authHash = db.StringProperty(required=False)
	deviceId = db.StringProperty(required=False)

class gItems(db.Model):
	owner=db.StringProperty(required=True)
	majorcategory=db.StringProperty(required=False)
	category=db.StringProperty(required=False)
	subcategory=db.StringProperty(required=False)
	name = db.StringProperty(required=True)
	idx = db.StringProperty(required=True)
	qtyMultiple = db.FloatProperty(required=False)
	unit = db.StringProperty(required=False)
	colour = db.FloatProperty(required=False)
	aromatic = db.BooleanProperty(required=False)
	biscuit= db.BooleanProperty(required=False)
	body = db.BooleanProperty(required=False)
	burnt = db.BooleanProperty(required=False)
	caramel = db.BooleanProperty(required=False)
	chocolate = db.BooleanProperty(required=False)
	coffee = db.BooleanProperty(required=False)
	grainy = db.BooleanProperty(required=False) 
	malty = db.BooleanProperty(required=False) 
	head = db.BooleanProperty(required=False)
	nutty = db.BooleanProperty(required=False)
	roasted = db.BooleanProperty(required=False)
	smoked = db.BooleanProperty(required=False)
	sweet = db.BooleanProperty(required=False)
	toasted = db.BooleanProperty(required=False) 
	ppg = db.FloatProperty(required=False)
	hwe = db.FloatProperty(required=False)
	extract = db.FloatProperty(required=False)
	mustMash = db.BooleanProperty(required=False)
	isAdjunct=db.BooleanProperty(required=False)
	hopAlpha=db.FloatProperty(required=False)
	hopForm = db.StringProperty(required=False)
	hopUse = db.StringProperty(required=False)
	hopAddAt=db.FloatProperty(required=False)
	attenuation=db.FloatProperty(required=False)
	dosage=db.FloatProperty(required=False)
	wastageFixed=db.FloatProperty(required=False)	
	styles=db.StringProperty(required=False)	# csv
	description=db.TextProperty(required=False)
	caprequired=db.BooleanProperty(required=False)
	co2required=db.BooleanProperty(required=False)
	isGrain=db.BooleanProperty(required=False)
	fullvolume=db.FloatProperty(required=False)
	volume=db.FloatProperty(required=False)

class gIngredients(db.Model):
	"""
	This is used for each ingredient in a given recipe 
	"""
	owner = db.StringProperty(required=True)
	recipename = db.StringProperty(required=False)
	atten=db.FloatProperty(required=False)
	qty = db.FloatProperty(required=False)
	originalqty = db.FloatProperty(required=False)
	ingredient = db.StringProperty(required=False)
	ingredientType=db.StringProperty(required=False)
	isAdjunct=db.BooleanProperty(required=False)	
	isPrimingFalvouring=db.BooleanProperty(required=False)	
	mustMash = db.BooleanProperty(required=False)
	isGrain =db.BooleanProperty(required=False)
	hwe=db.FloatProperty(required=False)
	extract=db.FloatProperty(required=False)		
	unit=db.StringProperty(required=False)	
	hopAlpha=db.FloatProperty(required=False)
	hopForm = db.StringProperty(required=False)
	hopUse = db.StringProperty(required=False)
	hopAddAt=db.FloatProperty(required=False)
	colour=db.FloatProperty(required=False)
	processIngredient=db.BooleanProperty(required=False)
	processConsumable=db.BooleanProperty(required=False)
	process=db.StringProperty(required=False)
	category=db.StringProperty(required=False)
	
class gBrewery(db.Model):
	"""
	Misc information which doesn't fit in any ohter place
	"""
	owner = db.StringProperty(required=True)
	breweryname=db.StringProperty(required=False)
	overheadperlitre=db.FloatProperty(required=False)
	brewerytwitter=db.StringProperty(required=False)


class gRecipes(db.Model):
	recipename = db.StringProperty(required=False)
	owner = db.StringProperty(required=True)
	stylenumber=db.StringProperty(required=False)
	styleletter=db.StringProperty(required=False)
	styleversion=db.StringProperty(required=False)
	batch_size_required = db.IntegerProperty(required=False)
	credit = db.StringProperty(required=False)
	description = db.TextProperty(required=False)
	mash_efficiency=db.FloatProperty(required=False)
	estimated_abv = db.FloatProperty(required=False)
	estimated_ebc = db.FloatProperty(required=False)
	estimated_fg = db.FloatProperty(required=False)
	estimated_ibu = db.FloatProperty(required=False)
	estimated_og = db.FloatProperty(required=False)
	estimated_srm = db.FloatProperty(required=False)
	forcedstyle = db.StringProperty(required=False)
	process = db.StringProperty(required=False)
	recipe_type = db.StringProperty(required=False)
	postBoilTopup = db.FloatProperty(required=False)
	spargeWater=db.FloatProperty(required=False)
	mashWater=db.FloatProperty(required=False)
	boilVolume=db.FloatProperty(required=False)
	totalWater=db.FloatProperty(required=False)
	totalGrain=db.FloatProperty(required=False)
	totalAdjuncts=db.FloatProperty(required=False)
	totalHops=db.FloatProperty(required=False)
	mash_grain_ratio=db.FloatProperty(required=False)
	target_mash_temp=db.FloatProperty(required=False)
	initial_grain_temp=db.FloatProperty(required=False)
	target_mash_temp_tweak=db.FloatProperty(required=False)
	priming_sugar_qty=db.FloatProperty(required=False)
	tap_mash_water=db.BooleanProperty(required=False)
	tap_sparge_water=db.BooleanProperty(required=False)

	calculationOutstanding=db.BooleanProperty(required=False)


class gRecipeStats(db.Model):
	owner=db.StringProperty(required=True)
	recipe=db.StringProperty(required=True)
	process=db.StringProperty(required=True)
	postboil_precool_og=db.FloatProperty()
	pretopup_estimated_gravity_grain=db.FloatProperty()
	sparge_temp=db.FloatProperty()
	pretopup_post_mash_og=db.FloatProperty()
	strike_temp=db.FloatProperty()
	primingwater=db.FloatProperty()
	sparge_water=db.FloatProperty()
	target_mash_temp=db.FloatProperty()
	precoolfvvolume=db.FloatProperty()
	pre_boil_gravity=db.FloatProperty()
	primingsugarqty=db.FloatProperty()
	num_crown_caps=db.FloatProperty()
	estimated_og=db.FloatProperty()
	estimated_ibu=db.FloatProperty()
	primingsugartotal=db.FloatProperty()
	strike_temp_5=db.FloatProperty()
	mash_liquid=db.FloatProperty()
	sparge_heating_time=db.FloatProperty()
	boil_vol=db.FloatProperty()
	mash_liquid_6=db.FloatProperty()
	topupvol=db.FloatProperty()
	extendedboil=db.BooleanProperty()	# in this case we boil the topup
	estimated_fg=db.FloatProperty()
	estimated_abv=db.FloatProperty()
	total_water=db.FloatProperty()
	grain_weight=db.FloatProperty()
	nongrain_weight=db.FloatProperty()
	hops_weight=db.FloatProperty()
	bottles_required=db.FloatProperty()
	kettle1volume=db.FloatProperty()
	kettle2volume=db.FloatProperty()
	kettle3volume=db.FloatProperty()
	kettle1kettle2volume=db.FloatProperty()
	kettle1kettle2kettle3volume=db.FloatProperty()
	kettle1evaporation=db.FloatProperty()
	kettle2evaporation=db.FloatProperty()
	kettle3evaporation=db.FloatProperty()
	kettle1preboilgravity=db.FloatProperty()
	kettle2preboilgravity=db.FloatProperty()
	kettle3preboilgravity=db.FloatProperty()
	postboilprecoolgravity=db.FloatProperty()
	preboil_gravity=db.FloatProperty()
	minikegqty=db.FloatProperty()
	polypinqty=db.FloatProperty()
		
