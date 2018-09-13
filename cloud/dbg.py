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

from django.utils import simplejson
#import json

from gData import *

class DbgXGqlDelete(webapp.RequestHandler):

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
		r=0
		indata = urllib.unquote(self.request.path ).split("/")
		self.response.out.write( indata[-1] )
		self.response.out.write("\n\n" )


		records = db.GqlQuery(  indata[-1] )
		for record in records.fetch(549435):
			self.response.out.write("Record - to delete\n")
			record.delete()


class DbgXGql(webapp.RequestHandler):

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
		r=0
		indata = urllib.unquote(self.request.path ).split("/")
		self.response.out.write( indata[-1] )
		self.response.out.write("\n\n" )


		records = db.GqlQuery(  indata[-1] )
		resul = records.fetch(549435)
		self.response.out.write("\n%s Records\n\n" %(len(resul)))
		ii=0
		for record in resul:
			self.response.out.write("Record %s\n" %(ii))
			ii=ii+1
			for r in record.__dict__:
				if r != "_entity":
					self.response.out.write("\t%s = %s\n" %( r,record.__dict__[r] ))


class DbgProcess(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		owner=user.email()

		self.response.headers['Content-Type']="text/plain"
		r=0

		
		records = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 ORDER BY process,activityNum,stepNum,subStepNum ",owner)
		for record in records.fetch(549435):
			self.response.out.write("Record %s\n" %(r))
			self.response.out.write("\tActivityNum: %s\n" %(record.activityNum))
			self.response.out.write("\tActivityStep: %s\n" %(record.stepNum))
			self.response.out.write("\tActivitySubStep: %s\n" %(record.subStepNum))
			self.response.out.write("\tProcess: %s\n" %(record.process))
			self.response.out.write("\tStepName: %s\n" %(record.stepName))
			self.response.out.write("\tText: %s\n" %(record.text))
			self.response.out.write("\tImg: %s\n" %(record.img))
			self.response.out.write("\tAttention: %s\n" %(record.attention))
			self.response.out.write("\tTimer: %s\n" %(record.timer))
			self.response.out.write("\n")
			r=r+1
			
class DbgStore(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		owner=user.email()

		self.response.headers['Content-Type']="text/plain"
		r=0

		for label in ["fermentables","hops","yeast","consumable","misc"]:
			alreadyDone={}
			records = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storecategory = :2 ",owner, label)
			for record in records.fetch(549435):
				if not alreadyDone.has_key(record.storeitem):
					alreadyDone[record.storeitem]=1
					subrecords = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storecategory = :2 AND storeitem = :3",owner,label,record.storeitem)
					s=subrecords.fetch(4959435)

					totalqty=0 
					for subrecord in s:	totalqty=totalqty + record.qty 
					self.response.out.write("Store Item: %s  " %(record.storeitem))
					self.response.out.write("Total Qty: %s\n" %(totalqty))
		
					for subrecord in s:
						self.response.out.write("\tPurchase Qty: %s\n" %(subrecord.purchaseQty))
						self.response.out.write("\tQty: %s\n" %(subrecord.qty))
						self.response.out.write("\tPurchaseDate: %s\n" %(subrecord.purchaseDate))
						self.response.out.write("\tBest Before End: %s\n" %(subrecord.bestBeforeEnd))
						self.response.out.write("\tSupplier: %s\n" %(subrecord.supplier))
						self.response.out.write("\tStock Tag: %s\n" %(subrecord.stocktag))
						self.response.out.write("\n")
					r=r+1
			
class DbgBrewlog(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		owner=user.email()

		r=0
	
		self.response.headers['Content-Type']="text/plain"
		brewlogs = db.GqlQuery("SELECT FROM gBrewlogs WHERE owner = :1",owner)
		for brewlog in brewlogs.fetch(234898):
			self.response.out.write("Record %s\n" %(r))
			self.response.out.write("\tBrewlog: %s\n" %(brewlog.brewlog))
			self.response.out.write("\tRecipe: %s\n" %(brewlog.recipe))
			self.response.out.write("\tProcess: %s\n" %(brewlog.process))
			self.response.out.write("\n")
			r=r+1


			# brewlog stock
			sr=0
			brewlogstock = db.GqlQuery("SELECT FROM gBrewlogStock WHERE owner = :1 AND recipe = :2 AND process =:3 ORDER BY stockcategory",owner,brewlog.recipe,brewlog.process)
#			brewlogstock = db.GqlQuery("SELECT FROM gBrewlogStock ORDER BY stockcategory")
			for stockitem in brewlogstock.fetch(234898):
				self.response.out.write("\tSub Record %s\n" %(sr))
				self.response.out.write("\t\tStock Tag: %s\n" %(stockitem.stock))
				self.response.out.write("\t\tStock Tag: %s\n" %(stockitem.stocktag))
				self.response.out.write("\t\tStock Cost: %s\n" %(stockitem.cost))
				self.response.out.write("\t\tStock Qty: %s\n" %(stockitem.qty))
				self.response.out.write("\t\tOwner: %s\n" %(stockitem.owner))
				self.response.out.write("\t\tRecipe: %s\n" %(stockitem.recipe))
				self.response.out.write("\t\tProcess: %s\n\n" %(stockitem.process))
			self.response.out.write("todo: add in brewlogsteps/fields\n")

class DbgRecipe(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		self.response.headers['Content-Type']="text/plain"
		self.response.out.write("Table gRecipes\n")

		recipeowner=user.email()
		r=0
		ourRecipes = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1", recipeowner)
		for recipe in ourRecipes.fetch(24943324):
			self.response.out.write("\tResult %s\n" %(r))
			self.response.out.write("\t Recipe name: %s\n" %(recipe.recipename))
			self.response.out.write("\t Description: %s\n" %(recipe.description))
			self.response.out.write("\t Credit: %s\n" %(recipe.credit))
			self.response.out.write("\t Batch Size: %s\n" %(recipe.batch_size_required))
			self.response.out.write("\t Boil Volume: %s\n" %(recipe.boilVolume))
			self.response.out.write("\t Estimated ABV: %s\n" %(recipe.estimated_abv))
			self.response.out.write("\t Estimated IBU: %s\n" %(recipe.estimated_ibu))
			self.response.out.write("\t Estimated EBC: %s\n" %(recipe.estimated_ebc))
			self.response.out.write("\t Estimated FG: %s\n" %(recipe.estimated_fg))
			self.response.out.write("\t Estimated OG: %s\n" %(recipe.estimated_og))
			self.response.out.write("\t Estimated SRM: %s\n" %(recipe.estimated_srm))
			self.response.out.write("\t Style: %s\n" %(recipe.forcedstyle))
			self.response.out.write("\t Process: %s\n" %(recipe.process))
			self.response.out.write("\t Recipe Type: %s\n" %(recipe.recipe_type))
			
			self.response.out.write("\n")	
			r=r+1


			r2=0
			self.response.out.write("\tTable gIngredients / recipename %s\n" %(recipe.recipename))
			ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2", recipeowner,recipe.recipename)
			
			for ingredient in ourIngredients:
				self.response.out.write("\t\tResult %s\n" %(r2))
				self.response.out.write("\t\t Ingredient: %s\n" %(ingredient.ingredient))
				self.response.out.write("\t\t Ingredient Type: %s\n" %(ingredient.ingredientType))
				self.response.out.write("\t\t Ingredient Qty: %s\n" %(ingredient.qty))
				self.response.out.write("\n")
				r2=r2+1




class DbgUsers(webapp.RequestHandler):

	def get(self):
		self.response.headers['Content-Type']="text/plain"
		sys.stderr.write("SELECT * FROM gAuthorisedUsers" )
		ourAuthKey = db.GqlQuery("SELECT * FROM gAuthorisedUsers")
		results = ourAuthKey.fetch(200)	
		self.response.out.write("Table gAuthorisedUsers\n")
		r=0
		for result in results:
				
			self.response.out.write("\tResult %s\n" %(r))
			self.response.out.write("\t Auth Hash: %s\n" %(result.authHash))
			self.response.out.write("\t Auth Cookie: %s\n" %(result.authCookie))
			self.response.out.write("\t Auth Email: %s\n" %(result.authEmail))
			self.response.out.write("\n")	
			r=r+1


class DbgOverview(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return
		owner=user.email()
		self.response.headers['Content-Type']="text/plain"



#		for o in db.GqlQuery("SELECT * FROM gIngredients").fetch(234234):
#			o.isPrimingFalvouring=False
#			o.put()

#		for o in db.GqlQuery("SELECT * FROM gIngredients").fetch(234234):
		#	if not o.originalqty:
		#		o.originalqty=0.00
		#		o.put()
		#return	

		#for o in  db.GqlQuery("SELECT * FROM gBrewlogStock").fetch(4234234):
		#	o.unit=""

#		ourIngredients = db.GqlQuery("SELECT * FROM gPurchases")
#		for ing in ourIngredients.fetch(2000):
#			ing.willNotExpire=False
#			ing.put()
#		ourIngredients = db.GqlQuery("SELECT * FROM gPurchases WHERE storecategory =:1","consumable")
#		for ing in ourIngredients.fetch(2000):
#			ing.willNotExpire=True
#			ing.put()
#		return



#		ourIngredients = db.GqlQuery("SELECT * FROM gIngredients")
#		for ing in ourIngredients.fetch(2000):
#			ing.originalqty=ing.qty
#			ing.put()



#
#		res=db.GqlQuery("SELECT * FROM gItems WHERE name = :1","Protofloc").fetch(4324)
#		for r in res:
#			r.subcategory="copper_fining"
#			r.put()
#
#		res=db.GqlQuery("SELECT * FROM gPurchases WHERE storeitem = :1","Protofloc").fetch(4324)
#		for r in res:
#			r.subcategory="copper_fining"
#			r.put()
#		res=db.GqlQuery("SELECT * FROM gBrewlogStock WHERE stock = :1","Protofloc").fetch(4324)
#		for r in res:
#			r.subcategory="copper_fining"
#			r.put()

#		t={}
#		res=db.GqlQuery("SELECT * FROM gCompileText").fetch(4324234)
#		for r in res:
#			for s in r.toReplace:
#				t[s]=1
#		print ""
#		for r in t:
#			print r
#		gqlresult2=db.GqlQuery("SELECT * FROM gIngredients WHERE owner= :1 AND process='13AG8i9' ",owner)
##		results = gqlresult2.fetch(200)	
#		for result in results:	result.delete()


#		username=owner
#		process="16AG11i12"
#		brewlog="2012-03-1"
#
#		ourFields=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(4324234)	
#		for field in ourFields:	field.delete()
#
#		ourFields=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND process = :2",username,process).fetch(4324234)	
#		for field in ourFields:
#			blankfield=gField(owner=username,stepNum=field.stepNum,activityNum=field.activityNum)
#			blankfield.brewlog=brewlog
#			blankfield.fieldKey=field.fieldKey
#			blankfield.fieldWidget=field.fieldWidget
#			blankfield.parent=field.parent
#			blankfield.fieldTimestamp=field.fieldTimestamp
#			blankfield.put()


#		test = db.GqlQuery("SELECT * FROM gEquipment ").fetch(435345)
#		for x in test:	
#			x.activityNum=0
#			x.put()
#
#		test = db.GqlQuery("SELECT * FROM gBrewlogStock ").fetch(435345)
#		for x in test:	
#			x.activityNum=0
##			print x.stocktag
#			x.put()


		# Remove our old brewlog stock 	
#		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogStock WHERE  owner = :1 ",owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()
#
#		# Remove our old brewlog indexes
#		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogs WHERE owner = :1 ", owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()
#
#		# Remove our old step records			
#		ourOldRecords = db.GqlQuery("SELECT FROM gField WHERE owner = :1 ", owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()
#
#		# Remove our old notes
#		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogStep WHERE owner = :1 ",owner)
#		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()


		
#		gqlresult2=db.GqlQuery("SELECT * FROM gEquipment WHERE owner= :1  ",owner)
#		results = gqlresult2.fetch(2000)	
#		for result in results:
#			if result.name=="20l Kettle":
#				result.boilVolume=14.0
#			if result.name=="15l Kettle":
#				result.boilVolume=12.0
#			result.put()
#			self.response.out.write(" changed %s to %s\n" %(result.name,result.boilVolume))
		

#		gqlresult2=db.GqlQuery("SELECT * FROM gRecipes WHERE owner= :1  ",owner)
#		results = gqlresult2.fetch(200)	
#		for result in results:
#			result.calculationOutstanding=False
#			result.put()
#			self.response.out.write("%s\n" %(result.ingredient))
#		gqlresult2=db.GqlQuery("SELECT * FROM gRecipes WHERE owner= :1  ",owner)
#		results = gqlresult2.fetch(200)	
#		for result in results:
#			result.priming_sugar_qty=float(2.75)
#			result.put()
#			self.response.out.write("%s\n" %(result.ingredient))
			

#		gqlresult2=db.GqlQuery("SELECT * FROM gPurchases WHERE owner= :1  ",owner)
#		results = gqlresult2.fetch(2000)	
#		for result in results:
#			self.response.out.write("Setting wastageFixed for %s\n" %(result.storeitem))
#			gqlresult3=db.GqlQuery("SELECT * FROM gItems WHERE name = :1",result.storeitem)
#			try:
#				t=gqlresult3.fetch(1)[0]
#				wastageFixed=t.wastageFixed
#				if not wastageFixed:	wastageFixed=0
#			except:
#				wastageFixed=0
#			self.response.out.write("\t%s\n" %(wastageFixed))	
#			result.wastageFixed=float(wastageFixed)
#			result.put()	

		self.response.out.write("Process\n")
		gqlresult = db.GqlQuery("SELECT * FROM gProcesses WHERE owner = :1 ",owner)
		results = gqlresult.fetch(200)	
		for result in results:
			self.response.out.write("\t%s\n" %(result.process))

			gqlresult2=db.GqlQuery("SELECT * FROM gIngredients WHERE owner= :1 AND process = :2 ",owner,result.process)
			results2=gqlresult2.fetch(230)
			self.response.out.write("\t\t%s ingredients/consumables\n" %(len(results2)))

			gqlresult2=db.GqlQuery("SELECT * FROM gProcess WHERE owner= :1 AND process = :2 AND stepNum = :3 ",owner,result.process,-1)
			results2=gqlresult2.fetch(230)
			self.response.out.write("\t\t%s activities\n" %(len(results2)))

			gqlresult2=db.GqlQuery("SELECT * FROM gProcess WHERE owner= :1 AND process = :2 AND subStepNum = :3 ",owner,result.process,-1)
			results2=gqlresult2.fetch(230)
			self.response.out.write("\t\t%s steps\n" %(len(results2)))

			gqlresult2=db.GqlQuery("SELECT * FROM gEquipment WHERE owner= :1 AND process = :2  ",owner,result.process)
			results2=gqlresult2.fetch(230)
			self.response.out.write("\t\t%s equipment\n" %(len(results2)))

		self.response.out.write("\n\n")

		self.response.out.write("Recipes\n")
		i=0
		gqlresult = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1",owner)
		results = gqlresult.fetch(200)	
		for result in results:
			self.response.out.write("\t%s: %s\n" %(i,result.recipename))
			gqlresult3 = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2",owner,result.recipename)
			self.response.out.write("\t\t%s ingredients\n" %(len(gqlresult3.fetch(300))))
			self.response.out.write("\t\tProcess %s\n" %(result.process))
			i = i +1


		self.response.out.write("\nPresets\n\n")
		gqlresult = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2", owner,"fermentables")
		results = gqlresult.fetch(200)
		self.response.out.write("\t%s fermentable presets\n" %(len(results)))
		gqlresult = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2", owner,"hops")
		results = gqlresult.fetch(200)
		self.response.out.write("\t%s hops presets\n" %(len(results)))
		gqlresult = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2", owner,"yeast")
		results = gqlresult.fetch(200)
		self.response.out.write("\t%s yeasts presets\n" %(len(results)))
		gqlresult = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2", owner,"misc")
		results = gqlresult.fetch(200)
		self.response.out.write("\t%s misc presets\n" %(len(results)))
		gqlresult = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2", owner,"consumable")
		results = gqlresult.fetch(200)
		self.response.out.write("\t%s consumable presets\n" %(len(results)))
		gqlresult = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2", owner,"equipment")
		results = gqlresult.fetch(200)
		self.response.out.write("\t%s equipment presets\n" %(len(results)))

		self.response.out.write("\nSuppliers\n\n")
		gqlresult = db.GqlQuery("SELECT * FROM gSuppliers WHERE owner = :1", owner)
		results = gqlresult.fetch(200)
		self.response.out.write("\t%s suppliers\n" %(len(results)))

		self.response.out.write("\nStores\n\n")
		for label in ['fermentables','hops','yeast','consumable','misc']:
			gqlresult = db.GqlQuery("SELECT * FROM gPurchases WHERE storecategory = :1 AND owner = :2", label,owner)
			results = gqlresult.fetch(200)
			self.response.out.write("\t%s: %s purchases\n" %(label,len(results)))



#		purchases=db.GqlQuery("SELECT * FROM gPurchases WHERE storeitem='500ml glass bottle'").fetch(10000)
#		for purchase in purchases:
#	#		purchase.itemcategory="bottle"
#			purchase.put()
#		purchases=db.GqlQuery("SELECT * FROM gPurchases WHERE storeitem='500ml plastic bottle'").fetch(10000)
#		for purchase in purchases:
#			purchase.itemcategory="bottle"
#			purchase.put()
#		purchases=db.GqlQuery("SELECT * FROM gPurchases WHERE storeitem='16g CO2 bulb'").fetch(1000)
#		for purchase in purchases:
#			purchase.itemcategory="co2"
#			purchase.put()
#		purchases=db.GqlQuery("SELECT * FROM gPurchases WHERE storeitem='Crown Caps'").fetch(1000)
#		for purchase in purchases:
#			purchase.itemcategory="bottlecaps"
#			purchase.put()

#		purchase = db.GqlQuery("SELECT * FROM gIngredients WHERE ingredientType='hops'")
#		for pu in purchase.fetch(4000):
#			pu.processIngredient=False
#			pu.put()

		#item=db.GqlQuery("SELECT * FROM gItems WHERE name='Minikeg (5L)'").fetch(1)[0]
		#item.volume=4900.00
		#item=db.GqlQuery("SELECT * FROM gItems WHERE name='500ml plastic bottle'").fetch(1)[0]
		#item.volume=476.0
		#item=db.GqlQuery("SELECT * FROM gItems WHERE name='500ml glass bottle'").fetch(1)[0]
		#item.volume=475.9
		#item.put()
	
		# upgrade only
		purchases = db.GqlQuery("SELECT * FROM gPurchases").fetch(40343)
		for purchase in purchases:
			itemVol = db.GqlQuery("SELECT * FROM gItems WHERE majorcategory=:1 AND name = :2",purchase.storecategory,purchase.storeitem).fetch(1)
			if len(itemVol) == 0:
				sys.stderr.write(" Can't set volume for %s\n" %(purchase.storeitem))
			else:
				if itemVol[0].volume:
					sys.stderr.write(" Settings volume for %s to %s\n" %(purchase.storeitem,itemVol[0].volume))
					purchase.volume = itemVol[0].volume	
					purchase.put()

		self.response.out.write("\nBrewlogs\n")
		i=0
		gqlresult = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1",owner)
		results = gqlresult.fetch(200)	
		for result in results:
			self.response.out.write("\t%s: %s/%s\n\t\t%s\n\t\t%s\n" %(i,result.brewlog,result.recipe,result.brewhash,result.process))

			g= db.GqlQuery("SELECT * FROM gBrewlogStock WHERE brewlog = :1 AND owner = :2", result.brewlog,owner)
			self.response.out.write("\t\tStock %s records\n" %( len(g.fetch(32434))))
			g= db.GqlQuery("SELECT * FROM gBrewlogStep WHERE brewlog = :1 AND owner = :2", result.brewlog,owner)
			self.response.out.write("\t\tSteps %s records\n" %( len(g.fetch(32434))))
			g= db.GqlQuery("SELECT * FROM gWidgets WHERE brewlog = :1 AND owner = :2", result.brewlog,owner)
			h= db.GqlQuery("SELECT * FROM gField WHERE brewlog = :1 AND owner = :2", result.brewlog,owner)
			self.response.out.write("\t\tWidgets/Fields %s records\n" %( len(g.fetch(32434))+len(h.fetch(345455) )))

			i = i +1

application = webapp.WSGIApplication( 	
	[('/dbg/overview/',DbgOverview), ('/dbg/gqldelete/.*',DbgXGqlDelete),('/dbg/gql/.*',DbgXGql),('/dbg/process/',DbgProcess),	 ('/dbg/users/', DbgUsers) ,('/dbg/recipe/', DbgRecipe), ('/dbg/brewlog/',DbgBrewlog), ('/dbg/stores/',DbgStore) ], debug=True)
run_wsgi_app(application)

