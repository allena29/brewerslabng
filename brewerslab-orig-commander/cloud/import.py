import base64
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
from django.utils import simplejson

from gData import *

class ImportHandler(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return
		if not (user.email() == "allena29@gmail.com" or user.email() == "test@example.com"):
			self.response.headers['Content-Type']="text/html"
			self.response.out.write("User %s not authorised" %(user.email()))
			return 

		self.response.headers['Content-Type']="text/html"
		self.response.out.write("User: %s<p>" %(user.email()))
		self.response.out.write("""<h1>Import Process</h1>
			  <form action="/import/process/" enctype="multipart/form-data" method="post">
				<input type="file" name="processobject">
				<input type="submit" value="Submit">
			</form>""")		
		self.response.out.write("""<h1>Import Stores</h1>
			  <form action="/import/stores/" enctype="multipart/form-data" method="post">
				<input type="file" name="storesobject">
				<input type="submit" value="Submit">
			</form>""")		
		self.response.out.write("""<h1>Import Recipes</h1>
			  <form action="/import/recipe/" enctype="multipart/form-data" method="post">
				<input type="file" name="recipeobject">
				<input type="submit" value="Submit">
			</form>""")		
		self.response.out.write("""<h1>Import Brewlog</h1>
			  <form action="/import/brewlog/" enctype="multipart/form-data" method="post">
				<input type="file" name="brewlogobject"><br>
				<input type="text" name="realbrewname"> Real Brewname<br>
				<input type="submit" value="Submit">
			</form>""")

		self.response.out.write("""<h1>Import Preset</h1>
			  <form action="/import/preset/" enctype="multipart/form-data" method="post">
				<input type="file" name="presetobject"><br>
				<input type="submit" value="Submit">
			</form>""")


		breweryname=""
		overheadperlitre=0.00
		brwerytwitter=""
		try:
			results=db.GqlQuery("SELECT * FROM gBrewery WHERE owner = :1", user.email()).fetch(1)
			breweryname=results[0].breweryname
			overheadperlitre=results[0].overheadperlitre
			brewerytwitter=results[0].brewerytwitter
		except:
			pass
		self.response.out.write("""<h1>Settings</h1>
			<form action="/import/brewery/" method="post">
				<input type="text" name="brewerytwitter" value="%s">Twitter<br>
				<input type="text" name="breweryname" value="%s"> Brewery Name<br>
				<input type="text" name="overheadperlitre" value="%s"> Overhead per Litre<br>
				<input type="submit" value="Submit">
			</form>""" %(brewerytwitter,breweryname,overheadperlitre))






class ImportPresets(webapp.RequestHandler):

	def post(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		owner=user.email()
		self.response.headers['Content-Type']="text/plain"


		self.response.out.write("Importing SUppliers\n")


		self.preset = pickle.loads( self.request.get("presetobject") )

		records = db.GqlQuery("SELECT FROM gSuppliers WHERE owner = :1 ",owner)
		for record in records.fetch(43234234):	record.delete()

		for supplier in self.preset[4]:
			if len(supplier) > 0:
				sup = gSuppliers(owner=owner,supplier=supplier,supplierName= self.preset[4][supplier].name)
				sup.put()

				self.response.out.write("Supplier %s\n" %(self.preset[4][supplier].name))
		
		records = db.GqlQuery("SELECT FROM gItems WHERE owner = :1 AND majorcategory = :2",owner,"misc")
		for record in records.fetch(43234234):	record.delete()
		
		for misc in self.preset[3]:
			item = gItems(owner=owner,majorcategory="misc",idx=misc,name=self.preset[3][misc].name)
			item.category=self.preset[3][misc].category
			if self.preset[3][misc].__dict__.has_key("subcategory"):	item.subcategory=self.preset[3][misc].subcategory
			if not self.preset[3][misc].__dict__.has_key("subcategory"):	item.subcategory=""
			item.qtyMultiple=float(self.preset[3][misc].qty_multiple)
			if self.preset[3][misc].__dict__.has_key("dosage"):	item.dosage=float(self.preset[3][misc].dosage)
			item.wastageFixed=float(self.preset[3][misc].wastage_fixed)
			item.unit=self.preset[3][misc].unit
			item.put()

			self.response.out.write("Misc Preset %s\n" %(misc))

		records = db.GqlQuery("SELECT FROM gItems WHERE owner = :1 AND majorcategory = :2",owner,"hops")
		for record in records.fetch(43234234):	record.delete()
		
		for hop in self.preset[1]:
			item = gItems(owner=owner,majorcategory="hops",idx=hop,name=self.preset[1][hop].name)
			item.category=self.preset[1][hop].category
			item.subcategory=self.preset[1][hop].subcategory
			item.qtyMultiple=float(self.preset[1][hop].qty_multiple)
			item.unit=self.preset[1][hop].unit
			item.hopAlpha = float(self.preset[1][hop].alpha)
			item.styles = "%s" %(self.preset[1][hop].styles)
			item.description = self.preset[1][hop].description
			item.unit = self.preset[1][hop].unit
			if not item.unit:	item.unit="gm"
			if self.preset[1][hop].__dict__.has_key("dosage"):	item.dosage=float(self.preset[1][hop].dosage)
			item.wastageFixed=float(self.preset[1][hop].wastage_fixed)
			item.put()

			self.response.out.write("Hop Preset %s\n" %(hop))

		
		records = db.GqlQuery("SELECT FROM gItems WHERE owner = :1 AND majorcategory = :2",owner,"consumable")
		for record in records.fetch(43234234):	record.delete()
		
		for consumable in self.preset[6]:
			item = gItems(owner=owner,majorcategory="consumable",idx=consumable,name=self.preset[6][consumable].name)
			item.qtyMultiple=float(self.preset[6][consumable].qty_multiple)
			item.unit=self.preset[6][consumable].unit
			item.dosage=float(self.preset[6][consumable].dosage)
			item.wastageFixed=float(self.preset[6][consumable].wastage_fixed)
			item.category=self.preset[6][consumable].category
			if self.preset[6][consumable].__dict__.has_key("volume"):	item.fullvolume=float(self.preset[6][consumable].volume)
			if self.preset[6][consumable].__dict__.has_key("fullvolume"):	item.fullvolume=float(self.preset[6][consumable].fullvolume)
			if self.preset[6][consumable].__dict__.has_key("subcategory"):	item.subcategory=self.preset[6][consumable].subcategory
			if self.preset[6][consumable].__dict__.has_key("caprequired"):
				if self.preset[6][consumable].caprequired == 1:	item.caprequired=True
			if self.preset[6][consumable].__dict__.has_key("co2required"):
				if self.preset[6][consumable].co2required == 1:	item.co2required=True
			item.put()

			self.response.out.write("Consumable Preset %s\n" %(consumable))


		
		records = db.GqlQuery("SELECT FROM gItems WHERE owner = :1 AND majorcategory = :2",owner,"yeast")
		for record in records.fetch(43234234):	record.delete()
		
		for yeast in self.preset[2]:
			item = gItems(owner=owner,majorcategory="yeast",idx=yeast,name=self.preset[2][yeast].name)
			item.attenuation = float(self.preset[2][yeast].atten)
			item.qtyMultiple=float(self.preset[2][yeast].qty_multiple)
			item.unit=self.preset[2][yeast].unit
			item.category=self.preset[2][yeast].category
			if self.preset[2][yeast].__dict__.has_key("dosage"):	item.dosage=float(self.preset[2][yeast].dosage)
			item.wastageFixed=float(self.preset[2][yeast].wastage_fixed)
			item.subcategory=self.preset[2][yeast].subcategory
			item.put()

			self.response.out.write("Yeast Preset %s\n" %(hop))


		records= db.GqlQuery("SELECT FROM gItems WHERE owner = :1 AND majorcategory = :2",owner,"fermentables")
		for record in records.fetch(43234234):	record.delete()
			

		for grain in self.preset[0]:
			item = gItems(owner=owner,majorcategory="fermentables",idx=grain,name=self.preset[0][grain].name)
			item.qtyMultiple=float(self.preset[0][grain].qty_multiple)
			item.unit=self.preset[0][grain].unit
			if self.preset[0][grain].__dict__.has_key("dosage"):	item.dosage=float(self.preset[0][grain].dosage)
			item.wastageFixed=float(self.preset[0][grain].wastage_fixed)
			item.category=self.preset[0][grain].category
			item.subcategory=self.preset[0][grain].subcategory
			if self.preset[0][grain].aromatic:	item.aromatic=True
			if self.preset[0][grain].biscuit:	item.biscuit=True
			if self.preset[0][grain].body:	item.body=True
			if self.preset[0][grain].burnt:	item.burnt=True
			if self.preset[0][grain].caramel:	item.caramel=True
			if self.preset[0][grain].chocolate:	item.chocolate=True
			if self.preset[0][grain].coffee:	item.coffee = True
			if self.preset[0][grain].grainy:	item.grainy=True
			if self.preset[0][grain].malty:	item.malty=True
			if self.preset[0][grain].head:	item.head=True
			if self.preset[0][grain].nutty:	item.nutty=True
			if self.preset[0][grain].roasted:	item.roasted=True
			if self.preset[0][grain].smoked:	item.smoked=True
			if self.preset[0][grain].sweet:	item.sweet=True
			if self.preset[0][grain].toasted:	item.toasted=True
			if self.preset[0][grain].mustMash:	item.mustMash=True
			if self.preset[0][grain].isAdjunct:	item.isAdjunct=True
			if self.preset[0][grain].isGrain:	item.isGrain=True			
			if not self.preset[0][grain].aromatic:	item.aromatic=False
			if not self.preset[0][grain].biscuit:	item.biscuit=False
			if not self.preset[0][grain].body:	item.body=False
			if not self.preset[0][grain].burnt:	item.burnt=False
			if not self.preset[0][grain].caramel:	item.caramel=False
			if not self.preset[0][grain].chocolate:	item.chocolate=False
			if not self.preset[0][grain].coffee:	item.coffee = False
			if not self.preset[0][grain].grainy:	item.grainy=False
			if not self.preset[0][grain].malty:	item.malty=False
			if not self.preset[0][grain].head:	item.head=False
			if not self.preset[0][grain].nutty:	item.nutty=False
			if not self.preset[0][grain].roasted:	item.roasted=False
			if not self.preset[0][grain].smoked:	item.smoked=False
			if not self.preset[0][grain].sweet:	item.sweet=False
			if not self.preset[0][grain].toasted:	item.toasted=False
			if not self.preset[0][grain].mustMash:	item.mustMash=False
			if not self.preset[0][grain].isAdjunct:	item.isAdjunct=False

			if self.preset[0][grain].ppg:	item.ppg = float(self.preset[0][grain].ppg)
			if not self.preset[0][grain].ppg:	0
		
			if self.preset[0][grain].hwe:	item.hwe = float(self.preset[0][grain].hwe)
			if not self.preset[0][grain].hwe:	0
	
			if self.preset[0][grain].__dict__.has_key("extract"):	
				if self.preset[0][grain].extract:	item.extract = float(self.preset[0][grain].extract)
			if self.preset[0][grain].colour:	item.colour = float(self.preset[0][grain].colour)
			item.put()


			self.response.out.write("Grain Preset %s\n" %(grain))

class ImportProcess(webapp.RequestHandler):

	def post(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		owner=user.email()
		self.response.headers['Content-Type']="text/plain"
		p = pickle.loads( self.request.get("processobject") )
		process=p.name



		records = db.GqlQuery("SELECT FROM gCompileText WHERE owner = :1 AND process = :2",owner,process)
		for record in records.fetch(2342344):	record.delete()


		subrequired = re.compile("\.\.\.([a-zA-Z0-9\_]*)\.\.\.")

		a=0
		for activity in p.activities:
			s=0
			for step in activity.steps:

				ourCompile = gCompileText(owner=owner,process=process,activityNum=a,stepNum=s)

				MATCHES={}
				if len(step.text) > 1:
					matches = subrequired.findall(step.text)
					for match in matches:
						if not MATCHES.has_key( match):
							MATCHES[match]=1

				for substep in step.substeps:
					matches = subrequired.findall(substep.name)
					for match in matches:
						if not MATCHES.has_key(match):
							MATCHES[match]=1



				for x in MATCHES:	
					ourCompile.toReplace.append(x)
				if len(ourCompile.toReplace):
					ourCompile.put()


			



				s=s+1
			a=a+1



		# dont fogrget to do substeps
#		return
		self.response.out.write("Importng Process %s\n" %(process))



		records = db.GqlQuery("SELECT FROM gIngredients WHERE owner = :1 AND process = :2",owner,process)
		for record in records.fetch(43234234):	record.delete()

		records = db.GqlQuery("SELECT FROM gProcesses WHERE owner = :1  AND process = :2",owner,process )
		for record in records.fetch(43234234):	record.delete()

		records = db.GqlQuery("SELECT FROM gProcess WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()


#		records = db.GqlQuery("SELECT FROM gWidgets WHERE owner = :1 ",owner)
		records = db.GqlQuery("SELECT FROM gWidgets WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()

		records = db.GqlQuery("SELECT FROM gEquipment WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()

		records = db.GqlQuery("SELECT FROM gField WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()


		e=gEquipment(owner=owner,process=process,equipment="hlt",name=p.hlt.name)
		e.dead_space = float(p.hlt.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.hlt.volume)
		except:
			pass
		try:		
			e.heatPower = float(p.hlt.heatPower)
		except:
			pass
		e.put()

	
		if p.immersionchiller:
			e=gEquipment(owner=owner,process=process,equipment="immersionchiller",name=p.immersionchiller.name)
			e.mustSterilise=True
#			e.dead_space = float(p.hlt.dead_space)
			e.put()



		e=gEquipment(owner=owner,process=process,equipment="mashtun",name=p.mash_tun.name)
		e.dead_space = float(p.mash_tun.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.mash_tun.volume)
		except:
			pass
		e.put()

		e=gEquipment(owner=owner,process=process,equipment="fermentationbin",name=p.fermentation_bin.name)
		e.dead_space = float(p.fermentation_bin.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.fermentation_bin.volume)
		except:
			pass
		e.put()

		e=gEquipment(owner=owner,process=process,equipment="rackingbucket",name=p.racking_bucket.name)
		e.dead_space = float(p.racking_bucket.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.racking_bucket.volume)
		except:
			pass
		e.put()

		for boiler in p.boilers:
			e=gEquipment(owner=owner,process=process,equipment="boiler",name=boiler.name)
			e.dead_space = float(boiler.dead_space)
			e.mustSterilise=True
			e.volume = float(boiler.volume)
			try:
				e.boilVolume=float(boiler.boilVolume)
			except:
				pass
			e.put()
		

		r=gProcesses(owner=owner,process=process)
		r.put()


		r=gProcess(owner=owner,process=process,activityNum=-1,stepNum=-1,subStepNum=-1)
		r.fixed_boil_off = float(p.fixed_boil_off)
		r.fixed_cool_off = float(p.fixed_cool_off)
		r.percentage_boil_off = float(p.percentage_boil_off)
		r.percentage_cool_off = float(p.percentage_cool_off)
		r.put()

		aNum=0
		for activity in p.activities:


			for (ingredient,qty) in activity.ingredients:
				III = gIngredients(owner=owner)
				III.ingredient = ingredient.name
				III.qty=float(qty)
				III.process=process
				III.processIngredient=True
				III.processConsumable=False
				if ingredient.objType == "brwlabConsumable":
					III.ingredientType="consumable"
				elif ingredient.objType == "brwlabFermentable":
					III.ingredientType="fermentable"
				elif ingredient.objType == "brwlabHop":
					III.ingredientType="hop"
				elif ingredient.objType == "brwlabYeast":
					III.ingredientType="yeast"
				elif ingredient.objType == "brwlabMisc":
					III.ingredientType="misc"
				III.put()

			for (ingredient,qty) in activity.consumables:
				III = gIngredients(owner=owner)
				III.ingredient = ingredient.name
				III.qty=float(qty)
				III.process=process
				III.processIngredient=True
				III.processConsumable=True
				if ingredient.objType == "brwlabConsumable":
					III.ingredientType="consumable"
				elif ingredient.objType == "brwlabFermentable":
					III.ingredientType="fermentable"
				elif ingredient.objType == "brwlabHop":
					III.ingredientType="hop"
				elif ingredient.objType == "brwlabYeast":
					III.ingredientType="yeast"
				elif ingredient.objType == "brwlabMisc":
					III.ingredientType="misc"
				III.put()



			r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=-1,subStepNum=-1)
			r.stepName=activity.activityTitle
			r.put()


			sNum=0
			for step in activity.steps:
				ssNum=0
				r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=sNum,subStepNum=-1)
				if len(step.text) == 0:
					r.text=""
				else:
					r.text=step.text	
				r.stepName=step.name
				for img in step.img:
					r.img.append(img)
				r.attention=step.attention
				r.needToComplete=True
				r.auto = step.auto
#				r.timer=step.timer	# don't set the timer here, it should be on the substep
				try:
					print "<br><b>step.condition</b> %s" %(step.condition)
					for X in step.condition[0]:
						print " %s " %(X)
						r.conditional.append("%s" %(X) )
					print "<br>"
					
				except:
					r.conditional=[]
					pass
				r.put()
#					step.widgets['__adjustedgrav1'] = ('gravityTempAdjustment',['__temp1','__grav1'])


				for (fieldLabel,fieldKey,fieldVal) in step.fields:
					
					r=gField(owner=owner,process=process,activityNum=aNum,stepNum=sNum)
					r.fieldKey= fieldKey
					r.fieldLabel=fieldLabel
					r.fieldVal=fieldVal
					if step.__dict__.has_key("widgets"):
						if step.widgets.has_key(fieldKey):
							(jd,elliot) = step.widgets[fieldKey]
							r.fieldWidget = jd
					r.put()

				print "%s\n" %(step.name)
				if step.__dict__.has_key("widgets"):
					for widget in step.widgets:
						(w,v) =step.widgets[widget]
						print "widget %s" %(w)
						r=gWidgets(owner=owner,process=process,activityNum=aNum,stepNum=sNum)
						r.widgetName=widget
						r.widget= w
						for wv in v:
							r.widgetValues.append(wv)
						r.put()

				for substep in step.substeps:
					r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=sNum,subStepNum=ssNum)
					substep.name=re.compile("[\r\n]").sub('  ',substep.name)
					r.stepName= substep.name

					if substep.__dict__.has_key("kitchenTimer"):
						if substep.kitchenTimer:
							(KTname,KTtimer) = substep.kitchenTimer
							r.timerName = KTname
							r.timerTime = KTtimer
					try:
						r.condition=substep.condition
					except:
						pass
					if substep.need_to_complete:	r.needToComplete=True
					r.put()
					ssNum=ssNum + 1
				sNum = sNum + 1
			aNum = aNum + 1	

class ImportStore(webapp.RequestHandler):

	def post(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		if not (user.email() == "allena29@gmail.com" or user.email() == "test@example.com"):
			self.response.headers['Content-Type']="text/html"
			self.response.out.write("User %s not authorised" %(user.email()))
			return 

		owner=user.email()

		records = db.GqlQuery("SELECT FROM gPurchases WHERE owner = :1  ",owner )
		for record in records.fetch(34934234):	record.delete()

		self.response.headers['Content-Type']="text/plain"
#		o=open("store/allena29/store")
		self.stores = pickle.loads( self.request.get("storesobject") )
#		o.close()
		self.response.out.write("Import store (%s)\n\n" %(owner))

		for (storeObj,label) in [ (self.stores.Fermentables,"fermentables"), (self.stores.Hops,"hops"),(self.stores.Yeast,"yeast"),(self.stores.Consumable,"consumable"),(self.stores.Misc,"misc")]:
			for x in storeObj:	
				self.response.out.write("%s (%s)\n" %(x.name,label))
				for purchase in storeObj[x]:
					if purchase.qty > 0:
#						print "\t",purchase
#						print "\t\t",purchase.supplier.name
#						print "\t\t",purchase.qty
#						print "\t\t",purchase.price
#						print "\t\t",purchase.stockTag		

						purch = gPurchases( owner=owner, storeitem =x.name, storecategory=label)
						purch.purchaseQty = float(purchase.qty)
						purch.qty = float(purchase.qty)
						purch.originalQty=float(purchase.qty)
						try:
							purch.volume=purchase.purchasedItem.volume
						except:
							pass
						purch.purchaseCost = float( purchase.price )
						purch.purchaseDate = int(purchase.purchase_date)
						purch.stocktag = purchase.stockTag
						purch.unit = purchase.purchasedItem.unit
						purch.itemcategory=purcahse.purchasedItem.category
						if purchase.__dict__.has_key("qty_multiple"):
							purch.qtyMultiple=float(purchase.qty_multiple)
						else:
							purch.qtyMultiple=float(1)

						if purchase.__dict__.has_key("wastage_fixed"):
							purch.wastageFixed=float(purchase.wastage_fixed)
						else:
							purch.wastageFixed=float(0) 
						if purchase.__dict__.has_key("best_before_date"):
							purch.bestBeforeEnd = int(purchase.best_before_date)
						purch.supplier = purchase.supplier.name
						if label == "hops":
							purch.hopActualAlpha=float(purchase.hop_actual_alpha)

						purch.put()

		records = db.GqlQuery("SELECT FROM gPurchases WHERE owner = :1  ",owner )
		totalStores=len(records.fetch(5959434)	)
		self.response.out.write("Total Records in Stores %s\n" %(totalStores))





class ImportBrewlog(webapp.RequestHandler):

	def post(self):
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

		b=pickle.loads( self.request.get("brewlogobject") )
#		o.close()
		self.response.out.write("Import Brewlog %s:\n" %(b.name))


		if len(self.request.get("realbrewname")) > 0:
			realbrewname = self.request.get("realbrewname")
		else:
			realbrewname = "%s/%s" %(b.copyrecipe.name,b.name)
			
#		# Remove our old brewlog stock 	
#		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogStock WHERE  owner = :1 ",owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()
#
#		# Remove our old brewlog indexes
#		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogs WHERE owner = :1", owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()
#
#		# Remove our old step records			
#		ourOldRecords = db.GqlQuery("SELECT FROM gField WHERE owner = :1 ", owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()
#
#		# Remove our old notes
#		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogStep WHERE owner = :1 ",owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

	

		# Remove our old brewlog stock 	
		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogStock WHERE  owner = :1 AND brewlog = :2",owner,b.name)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old brewlog indexes
		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogs WHERE owner = :1 AND brewlog = :2", owner,b.name)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old step records			
		ourOldRecords = db.GqlQuery("SELECT FROM gField WHERE owner = :1 AND brewlog = :2", owner,b.name)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old notes
		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2",owner,b.name)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()


		brewlog=b.name
		brwlog = gBrewlogs( recipe=b.copyrecipe.name,brewlog=brewlog,owner=owner )
		brwlog.process=b.process
		brwlog.realrecipe = realbrewname
		brwlog.boilVolume=float(b.copyrecipe.boilVolume)
		brwlog.brewhash = base64.b64encode("%s/%s/%s" %(owner,realbrewname,brewlog))
		self.response.out.write("\n\tBrew Id: %s\n" %(brwlog.brewhash))
		brwlog.put()	

		recipe=b.copyrecipe.name
		# Add our stock to the brewlog
#			self.response.out.write("\tstock\n")
		for x in b.stock:
			for stockitem in b.stock[x]:
				for (percent,thisQty,stocktag,item,purchase) in b.stock[x][stockitem]:
					stck = gBrewlogStock( recipe=b.copyrecipe.name,brewlog=brewlog,owner=owner)
					stck.stock = stockitem
					stck.stocktag=stocktag
					stck.stockcategory = x
					stck.subcategory=item.category
					stck.qty=float(thisQty)
					stck.cost = purchase.price * thisQty
					stck.put()

		siNum=0
		aNum=0
		for activity in b.copyprocess.activities:
		#	self.response.out.write("\tactivityNum %s\n" %(aNum))
			sNum=0
			for step in activity.steps:		
				ssNum=0
				stp = gBrewlogStep(recipe=recipe,brewlog=brewlog,activityNum=aNum, stepNum=sNum, subStepNum=-1,owner=owner,sortIndex=siNum )
				siNum=siNum+1
				stp.stepCompleted=step.completed
				try:
					stp.stepStartTime=step.startTime
				except:
					stp.stepStartTime=0
				try:
					stp.stepEndTime=step.endTime
				except:
					stp.stepEndTime=0
				stp.stepName=step.name

				needToComplete=0
				haveCompleted=0
				for substep in step.substeps:	
					if substep.need_to_complete:
						needToComplete=needToComplete+1
						if substep.completed:
							haveCompleted=haveCompleted+1
				if needToComplete == haveCompleted:
					stp.subStepsCompleted=True

				stp.put()

				# Import Widgets
				if step.__dict__.has_key("widgets"):
					for widget in step.widgets:
						(w,v) =step.widgets[widget]
						r=gWidgets(owner=owner,activityNum=aNum,stepNum=sNum)
						r.widgetName=widget
						r.brewlog=brewlog
						r.widget= w
						for wv in v:
							r.widgetValues.append(wv)
						r.put()
	
				# Import Fields 			
				for (fieldLabel,fieldKey,fieldVal) in step.fields:
					if b.notes.has_key( step.stepid ):
						if b.notes[ step.stepid ].has_key( fieldKey ):
							fieldnotes = gField( recipe=recipe,activityNum=aNum, stepNum=sNum, owner=owner )
							if step.widgets.has_key( fieldKey ):
								(w,v) = step.widgets[fieldKey]
								fieldnotes.fieldWidget=w
							fieldnotes.fieldKey=fieldKey
							fieldnotes.brewlog=brewlog
							fieldnotes.fieldTimestamp=-1
							fieldnotes.fieldVal=b.notes[ step.stepid ][fieldKey]
							fieldnotes.put()

				# Import Notes
				if b.notes.has_key( step.stepid ):
					if b.notes[ step.stepid ].has_key( "notepage" ):
						fieldnotes = gField(recipe=recipe,brewlog=brewlog,activityNum=aNum, stepNum=sNum, owner=owner )
						fieldnotes.fieldKey="notepage"
						fieldnotes.brewlog=brewlog
						fieldnotes.fieldVal=b.notes[ step.stepid ]["notepage"]
						fieldnotes.put()
#							print "adding notes", b.notes[step.stepid]["notepage"]
							

				for substep in step.substeps:	
					sstp = gBrewlogStep( recipe=recipe,brewlog=brewlog,activityNum=aNum, stepNum=sNum, subStepNum=ssNum,owner=owner ,sortIndex=siNum)
					sstp.stepCompleted=substep.completed
					try:
						sstp.stepStartTime=int(substep.startTime)
					except:
						sstp.stepStartTime=0
					try:
						sstp.stepEndTime=int(substep.endTime)
					except:
						sstp.stepEndTime=0
					sstp.stepName=substep.name
					siNum=siNum+1
					if substep.need_to_complete:	sstp.needToComplete=True
					sstp.put()
				
					ssNum=ssNum+1

				sNum=sNum+1
			aNum=aNum+1

class ImportBrewery(webapp.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return
		ourOldRecords = db.GqlQuery("SELECT * FROM gBrewery WHERE owner = :1", user.email() )
		for result in ourOldRecords.fetch(3434):	result.delete()

		brewery = gBrewery( owner=user.email() )
		brewery.breweryname=self.request.get("breweryname")
		brewery.brewerytwitter=self.request.get("brewerytwitter")
		brewery.overheadperlitre=float(self.request.get("overheadperlitre"))
		brewery.put()
	
		self.response.headers['Content-Type']="text/plain"
		self.response.out.write("Set brewery twitter to %s\n" %(self.request.get("brewerytwitter")))
		self.response.out.write("Set breweryname to %s\n" %(self.request.get("breweryname")))
		self.response.out.write("Set overhead per litre to %s\n" %(self.request.get("overheadperlitre")))


class ImportRecipe(webapp.RequestHandler):

	def post(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return
		if not (user.email() == "allena29@gmail.com" or user.email() == "test@example.com"):
			self.response.headers['Content-Type']="text/html"
			self.response.out.write("User %s not authorised" %(user.email()))
			return 

		self.response.headers['Content-Type']="text/plain"
#		recipes = os.listdir("recipes/allena29/")
#		for recipe in recipes:
#			if not recipe.count(".auto") and not recipe.count("CVS"):

		#self.response.out.write("Import recipe from file: %s\n" %(recipe))
		#o=open("recipes/allena29/%s" %(recipe))
		recipe = pickle.loads( self.request.get("recipeobject") )
		#o.close()

		recipename=recipe.name
		self.response.out.write("\tRecipe Name %s\n" %(recipe.name))
		recipeowner=user.email()
	
		ourOldRecords = db.GqlQuery("SELECT FROM gIngredients WHERE owner = :1 AND recipename = :2 ",user.email(),recipe.name)
		r=ourOldRecords.fetch(234898)
		for oldRecord in r:	oldRecord.delete()
		oldingredients=len(r)
		ourOldRecords = db.GqlQuery("SELECT FROM gRecipes WHERE  owner = :1 AND recipename =:2",user.email(),recipe.name)
		r=ourOldRecords.fetch(234898)
		for oldRecord in r:	oldRecord.delete()
		oldRecipe=len(r)


		r=gRecipes(recipename=recipe.name,owner=recipeowner)
		r.batch_size_required = recipe.batch_size_required
		r.description = recipe.description	
		try:
			r.credit = recipe.credit
		except:
			r.credit = user.email()
		r.estimated_abv = recipe.estimated_abv #db.StringProperty(required=false)
		r.estimated_ebc = recipe.estimated_ebc # db.FloatProperty(required=false)
		r.estimated_fg = recipe.estimated_fg #db.StringProperty(required=false)
		r.estimated_ibu = recipe.estimated_ibu #db.FloatProperty(required=false)
		r.estimated_og = recipe.estimated_og #db.StringProperty(required=false)
		r.estimated_srm = recipe.estimated_srm #db.StringProperty(required=false)
		r.mash_efficiency=float(recipe.mash_efficiency)
		r.forcedstyle = recipe.forcedstyle #db.StringProperty(required=false)
		r.process = recipe.process.name #db.StringProperty(required=false)
		if not recipe.__dict__.has_key("priming_sugar_qty"):
			r.priming_sugar_qty = 1.00
		else:
			r.priming_sugar_qty = float(recipe.priming_sugar_qty)
		r.recipe_type = recipe.recipe_type #db.StringProperty(required=false)
		r.postBoilTopup = float(recipe.top_up)
		r.mash_grain_ratio=float(recipe.mash_grain_ratio)
		r.target_mash_temp=float(recipe.target_mash_temp)
		r.initial_grain_temp=float(recipe.initial_grain_temp)
		r.target_mash_temp_tweak=float(recipe.target_mash_temp_tweak)
		r.put()
		for (items,itemlabel) in [ (recipe.fermentables,"fermentables"), (recipe.hops,"hops"), (recipe.yeast,"yeast"),(recipe.misc,"misc")]:
			for (item,qty) in items:
				i = gIngredients(recipename=recipename,owner=recipeowner)
				i.qty = float(qty)
				i.ingredient = item.name
				i.ingredientType = itemlabel
				i.unit=item.unit
				i.processIngredient=False
				if itemlabel == "fermentables":

					i.hwe=float(item.hwe)
					try:
						i.colour=float(item.colour)
					except:
						pass
					i.extract=float(item.extract)
					if item.isGrain:
						i.isGrain=True
					if item.mustMash:
						i.mustMash=True
					if item.isAdjunct == 1:
						i.isAdjunct = True
					else:
						i.isAdjunct= False
				else:
					i.isAdjunct = False
				if itemlabel == "yeast":
					self.response.out.write("Found Yeast %s\n" %(item.atten))
					i.atten=float(item.atten)
				if itemlabel == "hops":
					i.hopAlpha=float(item.alpha)
					i.hopAddAt=float(-1)
					if not item.__dict__.has_key("hopform"):	
						i.hopForm="leaf"
					else:
						i.hopForm=item.hopform
					if not item.__dict__.has_key("hopuse"):
						i.hopUse="boil"
					else:
						i.hopUse=item.hopuse
#						for xxx in item.__dict__:
#							self.response.out.write("item %s\n" %(xxx))
				i.put()



		# Hops by addition
		for hopAddAt in recipe.hops_by_addition:
			for hop in recipe.hops_by_addition[hopAddAt]:
				i = gIngredients(recipename=recipename,owner=recipeowner)
				i.qty = float( recipe.hops_by_addition[hopAddAt][hop] )
				i.ingredient = hop.name
				i.processIngredient=False
				i.ingredientType = "hops"
				i.hopAlpha=float(hop.alpha)
				i.unit = hop.unit
				if not hop.unit:	i.unit="gm"
				i.hopAddAt=float(hopAddAt)
				if not item.__dict__.has_key("hopform"):	
					i.hopForm="leaf"
				else:
					i.hopForm=hop.hopform
				if not item.__dict__.has_key("hopuse"):
					i.hopUse="boil"
				else:
					i.hopUse=hop.hopuse
				i.put()

		ourOldRecords = db.GqlQuery("SELECT FROM gIngredients WHERE owner = :1 AND recipename = :2 ",user.email(),recipe.name)
		self.response.out.write("Old Ingredients Records: %s New Ingredients Records: %s\n" %(oldingredients,len( ourOldRecords.fetch(234898))))
		ourOldRecords = db.GqlQuery("SELECT FROM gRecipes WHERE  owner = :1",user.email())
		self.response.out.write("Old (Total) Recipe Records: %s New Recipe Records: %s\n" %(oldRecipe,len( ourOldRecords.fetch(234898))))
	

application = webapp.WSGIApplication( 	
	[	('/import/',ImportHandler), ('/import/process/',ImportProcess), ('/import/recipe/', ImportRecipe), ('/import/brewlog/',ImportBrewlog), ('/import/stores/',ImportStore),('/import/brewery/',ImportBrewery), ('/import/preset/',ImportPresets)  ], debug=True)
run_wsgi_app(application)

