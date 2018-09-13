import re
import os
import sys
import pickle
import urllib
import hashlib 
import time
import cgi
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

#import json
from django.utils import simplejson as json

from gData import *

class ExportData(webapp.RequestHandler):

	def escape_string(self,inString):
		inString=re.compile("\n").sub("<br>","%s" %(inString))
		inString=re.compile("'").sub("\\'", "%s" %(inString))
		return inString
	
	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		if not (user.email() == "allena29@gmail.com" or user.email() == "test@example.com"):
			self.response.headers['Content-Type']="text/html"
			self.response.out.write("User %s not authorised" %(user.email()))
			return 

		owner=user.email()

		self.response.headers['Content-Type']="text/plain"


		#gProcesses - DONE has text property
		#gSuppliers - DONE.
		#gCompileText	- DONE (has stringlist) 
		#gContributions - DONE.
		#gWidgets	- DONE (has stringlist)
		#gProcess	- DONE 
		#gEquipment	- DONE.
		#gPurchases	- DONE.
		#gField		- DONE has text property.
		#gBrewlogStep	- DONE.
		#gBrewlogs	- DONE. 
		#gBrewlogStock	- DONE.
		#gAuthorisedUsers- DONE.
		#gItems		 - DONE.
		#gIngredients	- DONE.
		#gBrewery	- DONE.
		#gRecipes	- DONE
		#gRecipeStats	- DONE (auto converted)


		#self.response.out.write("CREATE TABLE gProcesses (entity int not null primary key, owner char, process char );\n"			)

		"""
		self.response.out.write("DROP TABLE IF EXISTS `gCompileText`;\n")

		self.response.out.write("CREATE TABLE gCompileText (entity int not null AUTO_INCREMENT ,owner char(255),process char(255),activityNum int ,stepNum int ,subStepNum int ,toReplace text, PRIMARY KEY(entity) );\n")

		records=db.GqlQuery("SELECT * FROM gCompileText")
		for r in records.fetch(345345345):
			if not r.owner:	r.owner=""
			if not r.process:	r.process=""
			if not r.activityNum:	r.activityNum=0
			if not r.stepNum:	r.stepNum=0
			if not r.subStepNum:	r.subStepNum=0
			if not r.toReplace:	r.toReplace=[]
			self.response.out.write("INSERT INTO gCompileText VALUES (null ,'%s' ,'%s' ,%s ,%s ,%s ,'%s' );\n" %( self.escape_string(r.owner) , self.escape_string(r.process) , self.escape_string(r.activityNum) , self.escape_string(r.stepNum) , self.escape_string(r.subStepNum) , self.escape_string(json.dumps(r.toReplace)) ))

		self.response.out.write("CREATE TABLE gProcesses (entity int not null AUTO_INCREMENT, owner char(255), process char(128), PRIMARY KEY(entity) );\n"			)

		records = db.GqlQuery("SELECT * FROM gProcesses")
		for r in records.fetch(5099999):
			if not r.owner:	r.owner=""
			if not r.process:	r.process=""	
			self.response.out.write("INSERT INTO gProcesses VALUES (null,'%s','%s');\n" %(r.owner,r.process)	)

		self.response.out.write("\n\n")
		self.response.out.write("DROP TABLE IF EXISTS `gSuppliers`;\n")
		self.response.out.write("CREATE TABLE gSuppliers (entity int not null AUTO_INCREMENT ,owner char(255), supplier char(128),supplierName char(255), PRIMARY KEY (entity) );\n")

		records = db.GqlQuery("SELECT * FROM gSuppliers")
		for r in records.fetch(5099999):
			if not r.owner:	r.owner=""
			if not r.supplier:	r.supplier=""
			if not r.supplierName:	r.supplierName=""
			self.response.out.write("INSERT INTO gSuppliers VALUES (null,'%s','%s','%s');\n" %(r.owner,r.supplier,r.supplierName))
	
		self.response.out.write("\n\n")

		self.response.out.write("DROP TABLE IF EXISTS `gContributions`;\n")
		self.response.out.write("CREATE TABLE gContributions (entity int not null AUTO_INCREMENT, owner char(255), recipeName char(255), ingredientType char(128), ingredient char(128), hopAddAt float, ibu float, srm float, gravity float, PRIMARY KEY(entity) );\n")


		records = db.GqlQuery("SELECT * FROM gContributions")
		for r in records.fetch(5099999):
			if not r.gravity:	r.gravity=0.0
			if not r.srm:	r.srm=0.0
			if not r.ibu:	r.ibu=0.0
			if not r.hopAddAt:	r.hopAddAt=0.0
			if not r.ingredient:	r.ingredient=""
			if not r.ingredientType:	r.ingredientType=""
			if not r.recipeName:	r.recipeName=""
			if not r.owner:	r.owner=""
			self.response.out.write("INSERT INTO gContributions VALUES (null,'%s','%s','%s','%s',%s,%s,%s,%s);\n" %(r.owner,r.recipeName,r.ingredientType,r.ingredient,r.hopAddAt,r.ibu,r.srm,r.gravity) )

		self.response.out.write("\n\n")

		self.response.out.write("DROP TABLE IF EXISTS `gWidgets`;\n")
		self.response.out.write("CREATE TABLE gWidgets (entity int not null AUTO_INCREMENT ,owner char(255),process char(255),activityNum int ,stepNum int ,widgetName char(255),widget char(255),widgetValues text, PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gWidgets")
		for r in records.fetch(345345345):
			if not r.owner:	r.owner=""
			if not r.process:	r.process=""
			if not r.activityNum:	r.activityNum=0
			if not r.stepNum:	r.stepNum=0
			if not r.widgetName:	r.widgetName=""
			if not r.widget:	r.widget=""
			if not r.widgetValues:	r.widgetValues=[]

			self.response.out.write("INSERT INTO gWidgets VALUES (null ,'%s' ,'%s' ,%s ,%s ,'%s' ,'%s' ,'%s' );\n" %( self.escape_string(r.owner) , self.escape_string(r.process) , self.escape_string(r.activityNum) , self.escape_string(r.stepNum) , self.escape_string(r.widgetName) , self.escape_string(r.widget) , self.escape_string(json.dumps(r.widgetValues)) ))
	

		self.response.out.write("DROP TABLE IF EXISTS `gProcess`;\n")
		self.response.out.write("CREATE TABLE gProcess (entity int not null AUTO_INCREMENT ,owner char(255),process char(255),stepName char(255),stepTitle char(255),activityNum int ,stepNum int ,subStepNum int ,text text,img text,attention char(255),timerName char(255),timerTime int ,fixed_boil_off float ,fixed_cool_off float ,percentage_boil_off float ,percentage_cool_off float ,auto char(255),needToComplete int ,compileStep int ,conditional text, PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gProcess")
		for r in records.fetch(345345345):
			if not r.owner:	r.owner=""
			if not r.process:	r.process=""
			if not r.stepName:	r.stepName=""
			if not r.stepTitle:	r.stepTitle=""
			if not r.activityNum:	r.activityNum=0
			if not r.stepNum:	r.stepNum=0
			if not r.subStepNum:	r.subStepNum=0
			if not r.text:	r.text=""
			if not r.img:	r.img=[]
			if not r.attention:	r.attention=""
			if not r.timerName:	r.timerName=""
			if not r.timerTime:	r.timerTime=0
			if not r.fixed_boil_off:	r.fixed_boil_off=0.0
			if not r.fixed_cool_off:	r.fixed_cool_off=0.0
			if not r.percentage_boil_off:	r.percentage_boil_off=0.0
			if not r.percentage_cool_off:	r.percentage_cool_off=0.0
			if not r.auto:	r.auto=""
			if not r.needToComplete:
				needToComplete = 0
			else:
				needToComplete = 1
			if not r.compileStep:
				compileStep = 0
			else:
				compileStep = 1
			if not r.conditional:	r.conditional=[]

			self.response.out.write("INSERT INTO gProcess VALUES (null ,'%s' ,'%s' ,'%s' ,'%s' ,%s ,%s ,%s ,'%s' ,'%s' ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,%s ,'%s' ,%s ,%s ,'%s' );\n" %( self.escape_string(r.owner) , self.escape_string(r.process) , self.escape_string(r.stepName) , self.escape_string(r.stepTitle) , self.escape_string(r.activityNum) , self.escape_string(r.stepNum) , self.escape_string(r.subStepNum) , self.escape_string(r.text) , self.escape_string(json.dumps(r.img)) , self.escape_string(r.attention) , self.escape_string(r.timerName) , self.escape_string(r.timerTime) , self.escape_string(r.fixed_boil_off) , self.escape_string(r.fixed_cool_off) , self.escape_string(r.percentage_boil_off) , self.escape_string(r.percentage_cool_off) , self.escape_string(r.auto) ,needToComplete ,compileStep , self.escape_string(json.dumps(r.conditional)) ))
		

		self.response.out.write("DROP TABLE IF EXISTS `gEquipment`;\n")
		self.response.out.write("CREATE TABLE gEquipment (entity int not null AUTO_INCREMENT, owner char(255), process char(128), name char(128), equipment char(128), dead_space float, activityNum int,  heatPower float, volume float, mustSterilise bool, boilVolume float, PRIMARY KEY(entity) );\n")

		records = db.GqlQuery("SELECT * FROM gEquipment")
		for r in records.fetch(5099999):
			if not r.mustSterilise:
				mustSterilise=0
			else:
				mustSterilise=1
			if not r.dead_space:	r.dead_space=0.00
			if not r.heatPower:	r.heatPower=0.00
			if not r.volume:	r.volume=0.00
			if not r.activityNum:	r.activityNum=-1
			if not r.boilVolume:	r.boilVolume=0.00
			if not r.equipment:	r.equipment=""
			if not r.name:	r.name=""
			if not r.process:	r.process=""
			if not r.owner:	r.owner=""
			self.response.out.write("INSERT INTO gEquipment VALUES (null,'%s','%s','%s','%s',%s,%s,%s,%s,%s,%s);\n" %(r.owner,r.process, r.name,r.equipment,r.dead_space,r.activityNum,r.heatPower, r.volume, mustSterilise,r.boilVolume)	)

		self.response.out.write("\n\n")

		self.response.out.write("DROP TABLE IF EXISTS `gPurchases`;\n")

		self.response.out.write("CREATE TABLE gPurchases (entity int not null AUTO_INCREMENT, owner char(255), storecategory char(128), storeitem char(128), itemcategory char(128), itemsubcategory char(128), purchaseQty float, qty float, originalqty float, qtyMultiple float, r.wastageFixed float, r.purchaseDate int, bestBeforeEnd int, supplier char(128), purchaseCost float, stocktag char(128), hopActualAlpha float, unit char(128), volume float,willNotExpire int, PRIMARY KEY(entity));\n")
		records = db.GqlQuery("SELECT * FROM gPurchases")
		for r in records.fetch(5099999):
			if r.willNotExpire:	
				willnotexpire=1
			else:
				willnotexpire=0
			if not r.itemsubcategory:
				r.itemsubcategory=""
			if not r.purchaseQty:
				r.purchaseQty=0.00
			if not r.originalQty:
				r.originalQty=0.00
			if not r.hopActualAlpha:
				r.hopActualAlpha=0.00
			if not r.volume:
				r.volume=0.00
			if not r.itemcategory:
				r.itemcategory=""
			if not r.qtyMultiple:	
				r.qtyMultiple=0.00
			if not r.wastageFixed:
				r.wastageFixed=0.00
			if not r.owner:	r.owner=""
			if not r.storecategory:	r.storecategory=""
			if not r.storeitem:	r.storeitem=""
			if not r.itemcategory:	r.itemcategory=""
			if not r.itemsubcategory:	r.itemsubcategory
			if not r.qty:	r.qty=0.00
			if not r.purchaseDate:	r.purchaseDate=0
			if not r.bestBeforeEnd:	r.bestBeforeEnd=0
			if not r.supplier:	r.supplier=""
			if not r.purchaseCost:	r.purchaseCost=0.00
			if not r.stocktag:	r.stocktag=""
			if not r.unit:	r.unit=""
			self.response.out.write("INSERT INTO gPurchases VALUES (null,'%s','%s','%s','%s','%s', %s,%s,%s,%s,%s,%s,%s,'%s',%s,'%s',%s,'%s',%s,%s);\n" %(owner,r.storecategory,r.storeitem, r.itemcategory, r.itemsubcategory, r.purchaseQty,r.qty,r.originalQty,r.qtyMultiple,r.wastageFixed,r.purchaseDate,r.bestBeforeEnd, r.supplier,r.purchaseCost,r.stocktag,r.hopActualAlpha,r.unit,r.volume,willnotexpire))



		self.response.out.write("\n\n")
		self.response.out.write("DROP TABLE IF EXISTS `gField`;\n")
		self.response.out.write("CREATE TABLE gField (entity int not null AUTO_INCREMENT, owner char(255), stepNum int, activityNum int, process char(128), brewlog char(128), recipe char(128), fieldLabel char(128), fieldKey char(128), fieldVal text, fieldWidget char(128), fieldTimestamp int, PRIMARY KEY(entity));\n")
		
		records = db.GqlQuery("SELECT * FROM gField")
		for r in records.fetch(5099999):
			if not r.fieldTimestamp:
				r.fieldTimestamp=0
			if not r.activityNum:
				r.activityNum=0
			if not r.fieldWidget:	r.fieldWidget=""
			if not r.fieldVal:	r.fieldVal=""
			if not r.fieldKey:	r.fieldKey=""
			if not r.fieldLabel:	r.fieldLabel=""
			if not r.recipe:	r.recipe=""
			if not r.brewlog:	r.brewlog=""
			if not r.process:	r.process=""	
			if not r.stepNum:	r.stepNum=-1
			r.fieldVal = self.escape_string(r.fieldVal) 
			if not r.owner:	r.owner=""
			self.response.out.write("INSERT INTO gField VALUES (null,'%s',%s,%s,'%s','%s','%s','%s','%s','%s','%s',%s);\n" %(owner,r.stepNum,r.activityNum,r.process,r.brewlog,r.recipe,r.fieldLabel,r.fieldKey,r.fieldVal,r.fieldWidget,r.fieldTimestamp))

		self.response.out.write("\n\n")

		self.response.out.write("DROP TABLE IF EXISTS `gBrewlogStep`;\n")
		self.response.out.write("CREATE TABLE gBrewlogStep (entity int not null AUTO_INCREMENT ,brewlog char(255),owner char(255),activityNum int ,stepNum int ,subStepNum int ,sortIndex int ,recipe char(255),stepName text,completed int ,stepStartTime int ,stepEndTime int ,needToComplete int ,subStepsCompleted int ,compileStep int ,conditional char(255),timerName char(255),timerTime int , PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gBrewlogStep")
		for r in records.fetch(345345345):
			if not r.brewlog:	r.brewlog=""
			if not r.owner:	r.owner=""
			if not r.activityNum:	r.activityNum=0
			if not r.stepNum:	r.stepNum=0
			if not r.subStepNum:	r.subStepNum=0
			if not r.sortIndex:	r.sortIndex=0
			if not r.recipe:	r.recipe=""
			if not r.completed:
				completed = 0
			else:
				completed = 1
			if not r.stepStartTime:	r.stepStartTime=0
			if not r.stepEndTime:	r.stepEndTime=0
			if not r.needToComplete:
				needToComplete = 0
			else:
				needToComplete = 1
			if not r.subStepsCompleted:
				subStepsCompleted = 0
			else:
				subStepsCompleted = 1
			if not r.compileStep:
				compileStep = 0
			else:
				compileStep = 1
			if not r.condition:	r.condition=""
			if not r.timerName:	r.timerName=""
			if not r.timerTime:	r.timerTime=0

			self.response.out.write("INSERT INTO gBrewlogStep VALUES (null ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,%s ,%s ,'%s' ,'%s' ,%s );\n" %( self.escape_string(r.brewlog) , self.escape_string(r.owner) , self.escape_string(r.activityNum) , self.escape_string(r.stepNum) , self.escape_string(r.subStepNum) , self.escape_string(r.sortIndex) , self.escape_string(r.recipe) , self.escape_string(r.stepName) ,completed , self.escape_string(r.stepStartTime) , self.escape_string(r.stepEndTime) ,needToComplete ,subStepsCompleted ,compileStep , self.escape_string(r.condition) , self.escape_string(r.timerName) , self.escape_string(r.timerTime) ))

		self.response.out.write("DROP TABLE IF EXISTS `gBrewlogs`;\n")
		self.response.out.write("CREATE TABLE gBrewlogs (entity int not null AUTO_INCREMENT, owner char(255), brewlog char(128), recipe char(128), brewhash char(128), realrecipe char(128), boilVolume float, process char(128), largeImage char(255), smallImage char(255), brewdate int, brewdate2 int, bottledate int, PRIMARY KEY(entity));\n")

		records = db.GqlQuery("SELECT * FROM gBrewlogs")
		for r in records.fetch(5099999):
			if not r.bottledate:
				r.bottledate=0
			if not r.brewdate2:
				r.brewdate2=0
			if not r.brewdate:
				r.brewdate=0	
			if not r.boilVolume:
				r.boilVolume=0.0
			if not r.smallImage:	r.smallImage=""
			if not r.largeImage:	r.largeImage=""
			if not r.process:	r.process=""
			if not r.realrecipe:	r.realrecipe=""
			if not r.brewhash:	r.brewhash=""
			if not r.recipe:	r.recipe=""
			if not r.brewlog:	r.brewlog=""
			if not r.owner:	r.owner=""
			self.response.out.write("INSERT INTO gBrewlogs VALUES (null,'%s','%s','%s','%s','%s',%s,'%s','%s','%s',%s,%s,%s);\n" %(r.owner,r.brewlog,r.recipe,r.brewhash,r.realrecipe,r.boilVolume,r.process,r.largeImage,r.smallImage,r.brewdate,r.brewdate2,r.bottledate))
		self.response.out.write("\n\n")



		self.response.out.write("DROP TABLE IF EXISTS `gBrewlogStock`;\n")
		self.response.out.write("CREATE TABLE gBrewlogStock (entity int not null AUTO_INCREMENT ,brewlog char(255),recipe char(255),owner char(255),unit char(255),storecategory char(255),activityNum int ,stock char(255),qty float ,cost float ,subcategory char(255),costrefund int ,stocktag char(255), PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gBrewlogStock")
		for r in records.fetch(345345345):
			if not r.brewlog:	r.brewlog=""
			if not r.recipe:	r.recipe=""
			if not r.owner:	r.owner=""
			if not r.unit:	r.unit=""
			if not r.storecategory:	r.storecategory=""
			if not r.activityNum:	r.activityNum=0
			if not r.stock:	r.stock=""
			if not r.qty:	r.qty=0.0
			if not r.cost:	r.cost=0.0
			if not r.subcategory:	r.subcategory=""
			if not r.costrefund:
				costrefund = 0
			else:
				costrefund = 1
			if not r.stocktag:	r.stocktag=""

			self.response.out.write("INSERT INTO gBrewlogStock VALUES (null ,'%s' ,'%s' ,'%s' ,'%s' ,'%s' ,%s ,'%s' ,%s ,%s ,'%s' ,%s ,'%s' );\n" %( self.escape_string(r.brewlog) , self.escape_string(r.recipe) , self.escape_string(r.owner) , self.escape_string(r.unit) , self.escape_string(r.storecategory) , self.escape_string(r.activityNum) , self.escape_string(r.stock) , self.escape_string(r.qty) , self.escape_string(r.cost) , self.escape_string(r.subcategory) ,costrefund , self.escape_string(r.stocktag) ))

		self.response.out.write("DROP TABLE IF EXISTS `gAuthorisedUsers`;\n")
		self.response.out.write("CREATE TABLE gAuthorisedUsers (entity int not null AUTO_INCREMENT,authCookie char(255), authEmail char(255), authHash char(255), deviceId char(255),PRIMARY KEY(entity));\n")

		records = db.GqlQuery("SELECT * FROM gAuthorisedUsers")
		for r in records.fetch(5099999):
			self.response.out.write("INSERT INTO gAuthorisedUsers VALUES (null,'%s','%s','%s','%s');\n" %(r.authCookie,r.authEmail,r.authHash,r.deviceId))


		self.response.out.write("DROP TABLE IF EXISTS `gItems`;\n")
		self.response.out.write("CREATE TABLE gItems (entity int not null AUTO_INCREMENT ,owner char(255),majorcategory char(255),category char(255),subcategory char(255),name char(255),idx char(255),qtyMultiple float ,unit char(255),colour float ,aromatic int ,biscuit int ,body int ,burnt int ,caramel int ,chocolate int ,coffee int ,grainy int ,malty int ,head int ,nutty int ,roasted int ,smoked int ,sweet int ,toasted int ,ppg float ,hwe float ,extract float ,mustMash int ,isAdjunct int ,hopAlpha float ,hopForm char(255),hopUse char(255),hopAddAt float ,attenuation float ,dosage float ,wastageFixed float ,styles char(255),description text,caprequired int ,co2required int ,isGrain int ,fullvolume float ,volume float , PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gItems")
		for r in records.fetch(345345345):
			if not r.owner:	r.owner=""
			if not r.majorcategory:	r.majorcategory=""
			if not r.category:	r.category=""
			if not r.subcategory:	r.subcategory=""
			if not r.name:	r.name=""
			if not r.idx:	r.idx=""
			if not r.qtyMultiple:	r.qtyMultiple=0.0
			if not r.unit:	r.unit=""
			if not r.colour:	r.colour=0.0
			if not r.aromatic:
				aromatic = 0
			else:
				aromatic = 1
			if not r.biscuit:
				biscuit = 0
			else:
				biscuit = 1
			if not r.body:
				body = 0
			else:
				body = 1
			if not r.burnt:
				burnt = 0
			else:
				burnt = 1
			if not r.caramel:
				caramel = 0
			else:
				caramel = 1
			if not r.chocolate:
				chocolate = 0
			else:
				chocolate = 1
			if not r.coffee:
				coffee = 0
			else:
				coffee = 1
			if not r.grainy:
				grainy = 0
			else:
				grainy = 1
			if not r.malty:
				malty = 0
			else:
				malty = 1
			if not r.head:
				head = 0
			else:
				head = 1
			if not r.nutty:
				nutty = 0
			else:
				nutty = 1
			if not r.roasted:
				roasted = 0
			else:
				roasted = 1
			if not r.smoked:
				smoked = 0
			else:
				smoked = 1
			if not r.sweet:
				sweet = 0
			else:
				sweet = 1
			if not r.toasted:
				toasted = 0
			else:
				toasted = 1
			if not r.ppg:	r.ppg=0.0
			if not r.hwe:	r.hwe=0.0
			if not r.extract:	r.extract=0.0
			if not r.mustMash:
				mustMash = 0
			else:
				mustMash = 1
			if not r.isAdjunct:
				isAdjunct = 0
			else:
				isAdjunct = 1
			if not r.hopAlpha:	r.hopAlpha=0.0
			if not r.hopForm:	r.hopForm=""
			if not r.hopUse:	r.hopUse=""
			if not r.hopAddAt:	r.hopAddAt=0.0
			if not r.attenuation:	r.attenuation=0.0
			if not r.dosage:	r.dosage=0.0
			if not r.wastageFixed:	r.wastageFixed=0.0
			if not r.styles:	r.styles=""
			if not r.caprequired:
				caprequired = 0
			else:
				caprequired = 1
			if not r.co2required:
				co2required = 0
			else:
				co2required = 1
			if not r.isGrain:
				isGrain = 0
			else:
				isGrain = 1
			if not r.fullvolume:	r.fullvolume=0.0
			if not r.volume:	r.volume=0.0
			if not r.description:	r.description=""		
			r.description=self.escape_string(r.description)
			self.response.out.write("INSERT INTO gItems VALUES (null ,'%s' ,'%s' ,'%s' ,'%s' ,'%s' ,'%s' ,%s ,'%s' ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,%s );\n" %( self.escape_string(r.owner) , self.escape_string(r.majorcategory) , self.escape_string(r.category) , self.escape_string(r.subcategory) , self.escape_string(r.name) , self.escape_string(r.idx) , self.escape_string(r.qtyMultiple) , self.escape_string(r.unit) , self.escape_string(r.colour) ,aromatic ,biscuit ,body ,burnt ,caramel ,chocolate ,coffee ,grainy ,malty ,head ,nutty ,roasted ,smoked ,sweet ,toasted , self.escape_string(r.ppg) , self.escape_string(r.hwe) , self.escape_string(r.extract) ,mustMash ,isAdjunct , self.escape_string(r.hopAlpha) , self.escape_string(r.hopForm) , self.escape_string(r.hopUse) , self.escape_string(r.hopAddAt) , self.escape_string(r.attenuation) , self.escape_string(r.dosage) , self.escape_string(r.wastageFixed) , self.escape_string(r.styles) , self.escape_string(r.description) ,caprequired ,co2required ,isGrain , self.escape_string(r.fullvolume) , self.escape_string(r.volume) ))

		self.response.out.write("DROP TABLE IF EXISTS `gIngredients`;\n")
		self.response.out.write("CREATE TABLE gIngredients (entity int not null AUTO_INCREMENT ,owner char(255),recipename char(255),atten float ,qty float ,originalqty float ,ingredient char(255),ingredientType char(255),isAdjunct int ,isPrimingFalvouring int ,mustMash int ,isGrain int ,hwe float ,extract float ,unit char(255),hopAlpha float ,hopForm char(255),hopUse char(255),hopAddAt float ,colour float ,processIngredient int ,processConsumable int ,process char(255),category char(255), PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gIngredients")
		for r in records.fetch(345345345):
			if not r.owner:	r.owner=""
			if not r.recipename:	r.recipename=""
			if not r.atten:	r.atten=0.0
			if not r.qty:	r.qty=0.0
			if not r.originalqty:	r.originalqty=0.0
			if not r.ingredient:	r.ingredient=""
			if not r.ingredientType:	r.ingredientType=""
			if not r.isAdjunct:
				isAdjunct = 0
			else:
				isAdjunct = 1
			if not r.isPrimingFalvouring:
				isPrimingFalvouring = 0
			else:
				isPrimingFalvouring = 1
			if not r.mustMash:
				mustMash = 0
			else:
				mustMash = 1
			if not r.isGrain:
				isGrain = 0
			else:
				isGrain = 1
			if not r.hwe:	r.hwe=0.0
			if not r.extract:	r.extract=0.0
			if not r.unit:	r.unit=""
			if not r.hopAlpha:	r.hopAlpha=0.0
			if not r.hopForm:	r.hopForm=""
			if not r.hopUse:	r.hopUse=""
			if not r.hopAddAt:	r.hopAddAt=0.0
			if not r.colour:	r.colour=0.0
			if not r.processIngredient:
				processIngredient = 0
			else:
				processIngredient = 1
			if not r.processConsumable:
				processConsumable = 0
			else:
				processConsumable = 1
			if not r.process:	r.process=""
			if not r.category:	r.category=""

			self.response.out.write("INSERT INTO gIngredients VALUES (null ,'%s' ,'%s' ,%s ,%s ,%s ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,%s ,%s ,'%s' ,%s ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,'%s' ,'%s' );\n" %( self.escape_string(r.owner) , self.escape_string(r.recipename) , self.escape_string(r.atten) , self.escape_string(r.qty) , self.escape_string(r.originalqty) , self.escape_string(r.ingredient) , self.escape_string(r.ingredientType) ,isAdjunct ,isPrimingFalvouring ,mustMash ,isGrain , self.escape_string(r.hwe) , self.escape_string(r.extract) , self.escape_string(r.unit) , self.escape_string(r.hopAlpha) , self.escape_string(r.hopForm) , self.escape_string(r.hopUse) , self.escape_string(r.hopAddAt) , self.escape_string(r.colour) ,processIngredient ,processConsumable , self.escape_string(r.process) , self.escape_string(r.category) ))

		self.response.out.write("DROP TABLE IF EXISTS `gBrewery`;\n")
		self.response.out.write("CREATE TABLE gBrewery (entity int not null AUTO_INCREMENT, owner char(255), breweryname char(128), overheadperlitre float, brewerytwitter char(255), PRIMARY KEY(entity) );\n")

		records = db.GqlQuery("SELECT * FROM gBrewery")
		for r in records.fetch(5099999):
			if not r.owner:	r.owner=""
			if not r.breweryname:	r.breweryname=""
			if not r.overheadperlitre:	r.overheadperlitre=0.00
			if not r.brewerytwitter:	r.brewerytwitter=""
			self.response.out.write("INSERT INTO gBrewery VALUES (null,'%s','%s',%s,'%s');\n" %(r.owner,r.breweryname,r.overheadperlitre,r.brewerytwitter))


		self.response.out.write("DROP TABLE IF EXISTS `gRecipes`;\n")
		self.response.out.write("CREATE TABLE gRecipes (entity int not null AUTO_INCREMENT ,recipename char(255),owner char(255),stylenumber char(255),styleletter char(255),styleversion char(255),batch_size_required int ,credit char(255),description text,mash_efficiency float ,estimated_abv float ,estimated_ebc float ,estimated_fg float ,estimated_ibu float ,estimated_og float ,estimated_srm float ,forcedstyle char(255),process char(255),recipe_type char(255),postBoilTopup float ,spargeWater float ,mashWater float ,boilVolume float ,totalWater float ,totalGrain float ,totalAdjuncts float ,totalHops float ,mash_grain_ratio float ,target_mash_temp float ,initial_grain_temp float ,target_mash_temp_tweak float ,priming_sugar_qty float ,tap_mash_water int ,tap_sparge_water int ,calculationOutstanding int , PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gRecipes")
		for r in records.fetch(345345345):
			if not r.recipename:	r.recipename=""
			if not r.owner:	r.owner=""
			if not r.stylenumber:	r.stylenumber=""
			if not r.styleletter:	r.styleletter=""
			if not r.styleversion:	r.styleversion=""
			if not r.batch_size_required:	r.batch_size_required=0
			if not r.credit:	r.credit=""
			if not r.mash_efficiency:	r.mash_efficiency=0.0
			if not r.estimated_abv:	r.estimated_abv=0.0
			if not r.estimated_ebc:	r.estimated_ebc=0.0
			if not r.estimated_fg:	r.estimated_fg=0.0
			if not r.estimated_ibu:	r.estimated_ibu=0.0
			if not r.estimated_og:	r.estimated_og=0.0
			if not r.estimated_srm:	r.estimated_srm=0.0
			if not r.forcedstyle:	r.forcedstyle=""
			if not r.process:	r.process=""
			if not r.recipe_type:	r.recipe_type=""
			if not r.postBoilTopup:	r.postBoilTopup=0.0
			if not r.spargeWater:	r.spargeWater=0.0
			if not r.mashWater:	r.mashWater=0.0
			if not r.boilVolume:	r.boilVolume=0.0
			if not r.totalWater:	r.totalWater=0.0
			if not r.totalGrain:	r.totalGrain=0.0
			if not r.totalAdjuncts:	r.totalAdjuncts=0.0
			if not r.totalHops:	r.totalHops=0.0
			if not r.mash_grain_ratio:	r.mash_grain_ratio=0.0
			if not r.target_mash_temp:	r.target_mash_temp=0.0
			if not r.initial_grain_temp:	r.initial_grain_temp=0.0
			if not r.target_mash_temp_tweak:	r.target_mash_temp_tweak=0.0
			if not r.priming_sugar_qty:	r.priming_sugar_qty=0.0
			if not r.tap_mash_water:
				tap_mash_water = 0
			else:
				tap_mash_water = 1
			if not r.tap_sparge_water:
				tap_sparge_water = 0
			else:
				tap_sparge_water = 1
			if not r.calculationOutstanding:
				calculationOutstanding = 0
			else:
				calculationOutstanding = 1

			self.response.out.write("INSERT INTO gRecipes VALUES (null ,'%s' ,'%s' ,'%s' ,'%s' ,'%s' ,%s ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,'%s' ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s );\n" %( self.escape_string(r.recipename) , self.escape_string(r.owner) , self.escape_string(r.stylenumber) , self.escape_string(r.styleletter) , self.escape_string(r.styleversion) , self.escape_string(r.batch_size_required) , self.escape_string(r.credit) , self.escape_string(r.description) , self.escape_string(r.mash_efficiency) , self.escape_string(r.estimated_abv) , self.escape_string(r.estimated_ebc) , self.escape_string(r.estimated_fg) , self.escape_string(r.estimated_ibu) , self.escape_string(r.estimated_og) , self.escape_string(r.estimated_srm) , self.escape_string(r.forcedstyle) , self.escape_string(r.process) , self.escape_string(r.recipe_type) , self.escape_string(r.postBoilTopup) , self.escape_string(r.spargeWater) , self.escape_string(r.mashWater) , self.escape_string(r.boilVolume) , self.escape_string(r.totalWater) , self.escape_string(r.totalGrain) , self.escape_string(r.totalAdjuncts) , self.escape_string(r.totalHops) , self.escape_string(r.mash_grain_ratio) , self.escape_string(r.target_mash_temp) , self.escape_string(r.initial_grain_temp) , self.escape_string(r.target_mash_temp_tweak) , self.escape_string(r.priming_sugar_qty) ,tap_mash_water ,tap_sparge_water ,calculationOutstanding ))
		
		"""


		self.response.out.write("DROP TABLE IF EXISTS `gRecipeStats`;\n")
		self.response.out.write("CREATE TABLE gRecipeStats (entity int not null AUTO_INCREMENT ,owner char(255),recipe char(255),process char(255),postboil_precool_og float ,pretopup_estimated_gravity_grain float ,sparge_temp float ,pretopup_post_mash_og float ,strike_temp float ,primingwater float ,sparge_water float ,target_mash_temp float ,precoolfvvolume float ,pre_boil_gravity float ,primingsugarqty float ,num_crown_caps float ,estimated_og float ,estimated_ibu float ,primingsugartotal float ,strike_temp_5 float ,mash_liquid float ,sparge_heating_time float ,boil_vol float ,mash_liquid_6 float ,topupvol float ,extendedboil int ,estimated_fg float ,estimated_abv float ,total_water float ,grain_weight float ,nongrain_weight float ,hops_weight float ,bottles_required float ,kettle1volume float ,kettle2volume float ,kettle3volume float ,kettle1kettle2volume float ,kettle1kettle2kettle3volume float ,kettle1evaporation float ,kettle2evaporation float ,kettle3evaporation float ,kettle1preboilgravity float ,kettle2preboilgravity float ,kettle3preboilgravity float ,postboilprecoolgravity float ,preboil_gravity float ,minikegqty float ,polypinqty float , PRIMARY KEY(entity) );\n")
		records=db.GqlQuery("SELECT * FROM gRecipeStats")
		for r in records.fetch(345345345):
			if not r.owner:	r.owner=""
			if not r.recipe:	r.recipe=""
			if not r.process:	r.process=""
			if not r.postboil_precool_og:	r.postboil_precool_og=0.0
			if not r.pretopup_estimated_gravity_grain:	r.pretopup_estimated_gravity_grain=0.0
			if not r.sparge_temp:	r.sparge_temp=0.0
			if not r.pretopup_post_mash_og:	r.pretopup_post_mash_og=0.0
			if not r.strike_temp:	r.strike_temp=0.0
			if not r.primingwater:	r.primingwater=0.0
			if not r.sparge_water:	r.sparge_water=0.0
			if not r.target_mash_temp:	r.target_mash_temp=0.0
			if not r.precoolfvvolume:	r.precoolfvvolume=0.0
			if not r.pre_boil_gravity:	r.pre_boil_gravity=0.0
			if not r.primingsugarqty:	r.primingsugarqty=0.0
			if not r.num_crown_caps:	r.num_crown_caps=0.0
			if not r.estimated_og:	r.estimated_og=0.0
			if not r.estimated_ibu:	r.estimated_ibu=0.0
			if not r.primingsugartotal:	r.primingsugartotal=0.0
			if not r.strike_temp_5:	r.strike_temp_5=0.0
			if not r.mash_liquid:	r.mash_liquid=0.0
			if not r.sparge_heating_time:	r.sparge_heating_time=0.0
			if not r.boil_vol:	r.boil_vol=0.0
			if not r.mash_liquid_6:	r.mash_liquid_6=0.0
			if not r.topupvol:	r.topupvol=0.0
			if not r.extendedboil:
				extendedboil = 0
			else:
				extendedboil = 1
			if not r.estimated_fg:	r.estimated_fg=0.0
			if not r.estimated_abv:	r.estimated_abv=0.0
			if not r.total_water:	r.total_water=0.0
			if not r.grain_weight:	r.grain_weight=0.0
			if not r.nongrain_weight:	r.nongrain_weight=0.0
			if not r.hops_weight:	r.hops_weight=0.0
			if not r.bottles_required:	r.bottles_required=0.0
			if not r.kettle1volume:	r.kettle1volume=0.0
			if not r.kettle2volume:	r.kettle2volume=0.0
			if not r.kettle3volume:	r.kettle3volume=0.0
			if not r.kettle1kettle2volume:	r.kettle1kettle2volume=0.0
			if not r.kettle1kettle2kettle3volume:	r.kettle1kettle2kettle3volume=0.0
			if not r.kettle1evaporation:	r.kettle1evaporation=0.0
			if not r.kettle2evaporation:	r.kettle2evaporation=0.0
			if not r.kettle3evaporation:	r.kettle3evaporation=0.0
			if not r.kettle1preboilgravity:	r.kettle1preboilgravity=0.0
			if not r.kettle2preboilgravity:	r.kettle2preboilgravity=0.0
			if not r.kettle3preboilgravity:	r.kettle3preboilgravity=0.0
			if not r.postboilprecoolgravity:	r.postboilprecoolgravity=0.0
			if not r.preboil_gravity:	r.preboil_gravity=0.0
			if not r.minikegqty:	r.minikegqty=0.0
			if not r.polypinqty:	r.polypinqty=0.0

			self.response.out.write("INSERT INTO gRecipeStats VALUES (null ,'%s' ,'%s' ,'%s' ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s );\n" %( self.escape_string(r.owner) , self.escape_string(r.recipe) , self.escape_string(r.process) , self.escape_string(r.postboil_precool_og) , self.escape_string(r.pretopup_estimated_gravity_grain) , self.escape_string(r.sparge_temp) , self.escape_string(r.pretopup_post_mash_og) , self.escape_string(r.strike_temp) , self.escape_string(r.primingwater) , self.escape_string(r.sparge_water) , self.escape_string(r.target_mash_temp) , self.escape_string(r.precoolfvvolume) , self.escape_string(r.pre_boil_gravity) , self.escape_string(r.primingsugarqty) , self.escape_string(r.num_crown_caps) , self.escape_string(r.estimated_og) , self.escape_string(r.estimated_ibu) , self.escape_string(r.primingsugartotal) , self.escape_string(r.strike_temp_5) , self.escape_string(r.mash_liquid) , self.escape_string(r.sparge_heating_time) , self.escape_string(r.boil_vol) , self.escape_string(r.mash_liquid_6) , self.escape_string(r.topupvol) ,extendedboil , self.escape_string(r.estimated_fg) , self.escape_string(r.estimated_abv) , self.escape_string(r.total_water) , self.escape_string(r.grain_weight) , self.escape_string(r.nongrain_weight) , self.escape_string(r.hops_weight) , self.escape_string(r.bottles_required) , self.escape_string(r.kettle1volume) , self.escape_string(r.kettle2volume) , self.escape_string(r.kettle3volume) , self.escape_string(r.kettle1kettle2volume) , self.escape_string(r.kettle1kettle2kettle3volume) , self.escape_string(r.kettle1evaporation) , self.escape_string(r.kettle2evaporation) , self.escape_string(r.kettle3evaporation) , self.escape_string(r.kettle1preboilgravity) , self.escape_string(r.kettle2preboilgravity) , self.escape_string(r.kettle3preboilgravity) , self.escape_string(r.postboilprecoolgravity) , self.escape_string(r.preboil_gravity) , self.escape_string(r.minikegqty) , self.escape_string(r.polypinqty) ))



application = webapp.WSGIApplication( 	
	[('/exportdata/',ExportData) ],debug=True)
run_wsgi_app(application)


