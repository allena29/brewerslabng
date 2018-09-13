import os
import sys
import base64
import pickle
import urllib
import hashlib 
import time
import cgi
import re
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#import json
from django.utils import simplejson
from brewerslabData import *

from gData import *






class ImportRecipe(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return
		self.response.headers['Content-Type']="text/html"
		self.response.out.write("<h1>Import Brewlog</h1>")
		self.response.out.write("<form method=\"post\" action=\"/publish/import/\">")
		self.response.out.write("<textarea name=\"inputdata\" rows=60 cols=80></textarea><br>")
		self.response.out.write("Large Img Url: <input type=\"text\" name=\"largeimgurl\" value=\"\"><br>")
		self.response.out.write("Small Img Url: <input type=\"text\" name=\"smallimgurl\" value=\"\"><br>")
		self.response.out.write("<input type=\"submit\">")
		self.response.out.write("</form>")
	
	def post(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return

		owner=user.email()
	
		self.response.headers['Content-Type']="text/plain"
		inputdata = pickle.loads(base64.b64decode(self.request.get("inputdata")))

		#sys.stderr.write(inputdata)

		for gB in inputdata['gBrewlogs']:
			newitem=gBrewlogs(owner=owner)
			for x in gB:
				sys.stderr.write("x - %s\n" %(x))
				newitem.__dict__[x] = gB[x]
				self.response.out.write(" %s = %s\n" %(x,gB[x]))
	
			if len(self.request.get("largeimgurl")) > 0:
				newitem.largeImage = self.request.get("largeimgurl")
			if len(self.request.get("smallimgurl")) > 0:
				newitem.smallImage = self.request.get("smallimgurl")

			newitem.put()

		for gB in inputdata['gRecipes']:
			newitem=gRecipes(owner=owner)
			for x in gB:
				newitem.__dict__[x] = gB[x]
				self.response.out.write(" %s = %s\n" %(x,gB[x]))
	
			newitem.put()


		for gB in inputdata['gIngredients']:
			newitem=gIngredients(owner=owner)
			for x in gB:
				newitem.__dict__[x] = gB[x]
				self.response.out.write(" %s = %s\n" %(x,gB[x]))
	

			newitem.put()

		for gB in inputdata['gField']:
			newitem=gField(owner=owner)
			for x in gB:
				newitem.__dict__[x] = gB[x]
				self.response.out.write(" %s = %s\n" %(x,gB[x]))
	

			newitem.put()


		for gB in inputdata['gBrewlogStock']:
			newitem=gBrewlogStock(owner=owner)
			for x in gB:
				newitem.__dict__[x] = gB[x]
				self.response.out.write(" %s = %s\n" %(x,gB[x]))
	

			newitem.put()



class ExportRecipe(webapp.RequestHandler):


	def get(self):
		self.response.headers['Content-Type']="text/plain"
		brewlog=self.request.get("brewlog")
		results2 = db.GqlQuery("SELECT * FROM gBrewlogs WHERE brewlog = :1",self.request.get("brewlog")).fetch(1)
		result2=results2
		recipename=result2[0].recipe
		ownername=result2[0].owner
		brewlogname=result2[0].brewlog
	
		data={}
		data['gBrewlogs']= []
		data['gRecipes']=[]		
		data['gIngredients']=[]		
		data['gField']=[]		
		data['gBrewlogStock']=[]		


		for result in results2:
			res=result
			item={}
			for x in res.__dict__:
				if x != "_entity" and x != "_Model__namespace" and x != "_key":
					item[x]=res.__dict__[x]
			data['gBrewlogs'].append( item )


		results=db.GqlQuery("SELECT * FROM gRecipes WHERE recipename = :1 AND owner = :2", recipename,ownername)
		result = results.fetch(1)
		res=result[0]
		item={}
		for x in res.__dict__:
			if x != "_entity" and x != "_Model__namespace" and x != "_key":
				item[x]=res.__dict__[x]
		data['gRecipes'].append( item )


		"""


		query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 ", ownername,recipename)
		grains = query.fetch(4324234)
		for res in grains:
			item={}
			for x in res.__dict__:
				if x != "_entity" and x != "_Model__namespace" and x != "_key":
					item[x]=res.__dict__[x]
			data['gIngredients'].append( item )


		query  = db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey != :3 ", ownername,brewlog,'notepage')
		grains = query.fetch(4324234)
		for res in grains:
			for x in res.__dict__:
				if x != "_entity" and x != "_Model__namespace" and x != "_key":
					item[x]=res.__dict__[x]
			data['gField'].append( item )


		query  = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 ", ownername,brewlog)
		grains = query.fetch(4324234)
		for res in grains:
			for x in res.__dict__:
				if x != "_entity" and x != "_Model__namespace" and x != "_key":
					item[x]=res.__dict__[x]
			data['gBrewlogStock'].append( item )

		"""

		self.response.out.write( base64.b64encode( pickle.dumps(data )))

		



class PublishRecipe(webapp.RequestHandler):


	def get(self):
		
		results2 = db.GqlQuery("SELECT * FROM gBrewlogs WHERE brewhash = :1",self.request.get("brew"))
		result2 = results2.fetch(1)
	
		if len(result2) != 1:
			self.error(404)
			self.response.out.write("<h1>404</h1>Could not find a matching brew %s" %(self.request.get("brew")))
			return

		recipename=result2[0].recipe
		ownername=result2[0].owner
		brewlogname=result2[0].brewlog

#		results=db.GqlQuery("SELECT * FROM gRecipes")
#		for result in results.fetch(134234324):
#			result.credit="Adam Allen"
#			result.put()
		
		results=db.GqlQuery("SELECT * FROM gRecipes WHERE recipename = :1 AND owner = :2", recipename,ownername)
		result = results.fetch(1)

		if len(result) != 1:
			self.error(404)
			self.response.out.write("<h1>404</h1>Could not find a recipe for the brew %s" %(self.request.get("brew")))
			return
	
		recipe=result[0]
		brewlog=result2[0]
		

		if not self.request.get("xml") == "1" and not self.request.get("xml") == "2":
			self.response.headers['Content-Type']="text/html"
			self.response.out.write("Android App <a href='https://play.google.com/store/apps/details?id=net.collie.mellon.aaa.recipeviewer'>available on Android Market</a><br>")
#Open recipe with <a href='net.collie.mellon.recipeviewer://recipeviewer/%s/'>android app</a>" %(base64.b64encode(self.request.get("brew"))));
			self.response.out.write("""<h1>%s</h1>""" %(brewlog.realrecipe))
			if not recipe.credit:	recipe.credit=" "


			boilTime=60
			results  = db.GqlQuery("SELECT * FROM gIngredients WHERE hopAddAt >= :4  AND  owner = :1 AND recipename = :2 AND ingredientType = :3  ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0).fetch(1)
			try:
				boilTime=results[0].hopAddAt
			except:
				pass
			self.response.out.write("""Recipe Type: %s<br>
				Brewer: %s<br>
				Batch Size: %s L<br>
				Boil Size: %s L<br>
				Boil Time: %s<br>
				Efficiency: %s<br>
				""" %(recipe.recipe_type,recipe.credit,recipe.batch_size_required,recipe.boilVolume, boilTime, recipe.mash_efficiency))
			self.response.out.write("""
				Style: %s<br>""" %(recipe.forcedstyle))

			self.response.out.write("""
				Notes: %s<br>""" %(recipe.description))
			self.response.out.write("""
				Estimated Original Gravity: %.4f<br>
				Estimated Final Gravity: %.4f<br>""" %(recipe.estimated_og,recipe.estimated_fg))
			try:
				results=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND recipe = :3 AND fieldKey = :4", ownername,brewlogname,recipename,"og")
				result=results.fetch(1)[0]
				self.response.out.write("""		Original Gravity: %.4f<br>""" %( float(result.fieldVal)))
			except:
				pass

			try:
				results=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND recipe = :3 AND fieldKey = :4", ownername,brewlogname,recipename,"fg")
				result=results.fetch(1)[0]
				self.response.out.write("""		Final Gravity: %.4f<br>""" %( float(result.fieldVal)))
			except:
				pass


			if result2[0].brewdate2 > 0:
				self.response.out.write("""		Brew Date: %s - %s<br>""" %(result2[0].brewdate,result2[0].brewdate2 ))
			if result2[0].bottledate > 0:
				self.response.out.write("""		Bottle Date: %s<br>""" %(result2[0].bottledate ))



			overheadperlitre=0
			try:
				results=db.GqlQuery("SELECT * FROM gBrewery WHERE owner = :1", ownername)
				result = results.fetch(1)
				overheadperlitre=result[0].overheadperlitre
				self.response.out.write("""		Brewery: %s<br>""" %( result[0].breweryname))
			except:
				pass	



			

			results = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2", ownername,brewlogname).fetch(1000)
			totalcost=0
			for result in results:
				if not (result.subcategory == "bottle" or result.subcategory == "keg"):
					totalcost=totalcost+result.cost
			totalcost=totalcost+(recipe.batch_size_required*overheadperlitre)
			self.response.out.write("""		Brew Cost: %.2f<br>""" %( totalcost ))


			if result2[0].smallImage:
				self.response.out.write("""		<a href="%s"><img src="%s" border=0></a><br>""" %(result2[0].largeImage,result2[0].smallImage ))






			self.response.out.write("""<h2>Fermentables</h2>""" )
			# Grain Bill		
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",False )
			grains = query.fetch(4324234)
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",True)
			adjuncts = query.fetch(4324234)
		
			for grain in grains:	
				self.response.out.write("""
					%s (grain) %.1f<br>
				""" %(grain.ingredient,grain.qty))
		
			for adjunct in adjuncts:	
				self.response.out.write("""
					%s (adjunct) %.1f<br>
						""" %(adjunct.ingredient,adjunct.qty))




			# hops Bill		
			self.response.out.write("""<h2>Hops</h2>""" )
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE hopAddAt >= :4  AND  owner = :1 AND recipename = :2 AND ingredientType = :3  ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0)
			hops = query.fetch(4324234)


			for hop in hops:	
				self.response.out.write("""
					%s (Alpha %.2f %%)  %.1f gm @ %.0f min <br>""" %(hop.ingredient,hop.hopAlpha, hop.qty,hop.hopAddAt))



			# Yeast Bill		
			self.response.out.write("""<h2>Yeast</h2>""" )
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3", ownername,recipename, "yeast")
			yeasts = query.fetch(4324234)
			for yeast in yeasts:	
				self.response.out.write("""
					%s %.1f gm<br>""" %(yeast.ingredient,11*yeast.qty))

			self.response.out.write("<a href='publish/recipe/?xml=1&brew=%s'>xml</a> " %(self.request.get("brew")))
			self.response.out.write("<a href='publish/recipe/?xml=2&brew=%s'>xml2</a>" %(self.request.get("brew")))







		if self.request.get("xml") == "1":
			"""
			
			BeerXML VERSION 1

			"""
			self.response.headers['Content-Type']="text/xml"
			self.response.out.write("""<RECIPES>\n
	<RECIPE>""")
			if not recipe.credit:	recipe.credit=" "



			boilTime=60
			results  = db.GqlQuery("SELECT * FROM gIngredients WHERE hopAddAt >= :4  AND  owner = :1 AND recipename = :2 AND ingredientType = :3  ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0).fetch(1)
			try:
				boilTime=results[0].hopAddAt
			except:
				pass
			self.response.out.write("""
				<NAME>%s</NAME>
				<TYPE>%s</TYPE>
				<BREWER>%s</BREWER>
				<DISPLAY_BATCH_SIZE>%s L</DISPLAY_BATCH_SIZE>
				<DISPLAY_BOIL_SIZE>%s L</DISPLAY_BOIL_SIZE>
				<BOIL_TIME>%s</BOIL_TIME>
				<EFFICIENCY>%s</EFFICIENCY>""" %(brewlog.realrecipe,recipe.recipe_type,recipe.credit,recipe.batch_size_required,recipe.boilVolume, boilTime, recipe.mash_efficiency))

			if recipe.forcedstyle:
				self.response.out.write("""
					<STYLE>
						<NAME>%s</NAME>""" %(recipe.forcedstyle))
		
				if recipe.styleversion:	self.response.out.write("			<STYLE_GUIDE>%s</STYLE_GUIDE>\n" %(recipe.styleversion))
				if recipe.stylenumber:	self.response.out.write("			<CATEGORY_NUMBER>%s</CATEGORY_NUMBER>\n" %(recipe.stylenumber))
				if recipe.styleletter:	self.response.out.write("			<STYLE_LETTER>%s</STYLE_LETTER>\n" %(recipe.styleletter))

				self.response.out.write("""
					</STYLE>""")
			

			# Grain Bill		
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",False )
			grains = query.fetch(4324234)
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",True)
			adjuncts = query.fetch(4324234)
			if len(grains) > 0 or len(adjuncts) > 0 :
				self.response.out.write("""
					<FERMENTABLES>""")	
		
			for grain in grains:	
				self.response.out.write("""
						<FERMENTABLE>
							<NAME>%s</NAME>
							<TYPE>grain</TYPE>
							<AMOUNT>%.5f</AMOUNT>
						</FERMENTABLE>""" %(grain.ingredient,grain.qty/1000))
		
			for adjunct in adjuncts:	
				self.response.out.write("""
						<FERMENTABLE>
							<NAME>%s</NAME>
							<TYPE>%s</TYPE>
							<AMOUNT>%.5f</AMOUNT>
						</FERMENTABLE>""" %(adjunct.ingredient,"Adjunct",adjunct.qty/1000))


			if len(grains) > 0 or len(adjuncts) > 0:
				self.response.out.write("""
					</FERMENTABLES>""")	



			# hops Bill		
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE hopAddAt >= :4  AND  owner = :1 AND recipename = :2 AND ingredientType = :3  ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0)
			hops = query.fetch(4324234)
			if len(hops) > 0:
				self.response.out.write("""
					<HOPS>""")	
		


			for hop in hops:	
				self.response.out.write("""
						<HOP>
							<NAME>%s</NAME>
							<FORM>%s</FORM>
							<ALPHA>%.2f</ALPHA>
							<AMOUNT>%.5f</AMOUNT>
							<USE>%s</USE>
							<TIME>%.1f</TIME>
						</HOP>""" %(hop.ingredient, hop.hopForm,hop.hopAlpha,hop.qty/1000,hop.hopUse,hop.hopAddAt))

			if len(hops) > 0:
				self.response.out.write("""
					</HOPS>""")	




			# Yeast Bill		
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3", ownername,recipename, "yeast")
			yeasts = query.fetch(4324234)
			if len(yeasts) > 0:
				self.response.out.write("""
					<YEASTS>""")	
		


			for yeast in yeasts:	
				self.response.out.write("""
						<YEAST>
							<NAME>%s</NAME>
							<AMOUNT>%.5f</AMOUNT>
						</YEAST>""" %(yeast.ingredient, 11*yeast.qty/1000 ))

			if len(yeasts) > 0:
				self.response.out.write("""
					</YEASTS>""")	




			self.response.out.write("""
				<NOTES>%s</NOTES>""" %(recipe.description))
			self.response.out.write("""
				<OG>%.4f</OG>
				<FG>%.4f</FG>""" %(recipe.estimated_og,recipe.estimated_fg))

			self.response.out.write("""
			</RECIPE>""")


			#
			#	Our exetensions to add some brewlog bits into the recipe
			#
			#
			self.response.out.write("""
		<EXTENSION>""")

			
			# Brew Day

			if result2[0].brewdate2 > 0:
				self.response.out.write("""		<brewDateEnd>%s</brewDateEnd>""" %(result2[0].brewdate2 ))
			if result2[0].brewdate > 0:
				self.response.out.write("""		<brewDate>%s</brewDate>""" %(result2[0].brewdate ))
			if result2[0].bottledate > 0:
				self.response.out.write("""		<bottleDate>%s</bottleDate>""" %(result2[0].bottledate ))

			if result2[0].smallImage:
				self.response.out.write("""		<smallLabel>%s</smallLabel>""" %(result2[0].smallImage ))

			if result2[0].largeImage:
				self.response.out.write("""		<bigLabel>%s</bigLabel>""" %(result2[0].largeImage ))


			try:
				results=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND  fieldKey = :3", ownername,brewlogname,"og")
				result=results.fetch(1)[0]
				self.response.out.write("""		<ACTUAL_OG>%.4f</ACTUAL_OG>""" %( float(result.fieldVal)))
			except:
				pass

			try:
				results=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3", ownername,brewlogname,"__measuredFg_abv")
				result=results.fetch(1)[0]
				self.response.out.write("""		<ACTUAL_FG>%.4f</ACTUAL_FG>""" %( float(result.fieldVal)))
			except:
				pass

#			x=gBrewery(owner="test@example.com")
#			x.breweryname="Wards View Brewing"
#			x.overheadperlitre=0.25
#			x.put()
			overheadperlitre=0
			try:
				results=db.GqlQuery("SELECT * FROM gBrewery WHERE owner = :1", ownername)
				result = results.fetch(1)
				overheadperlitre=result[0].overheadperlitre
				self.response.out.write("""		<BREWERY_NAME>%s</BREWERY_NAME>""" %( result[0].breweryname))
			except:
				pass	



			

			results = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2", ownername,brewlogname).fetch(1000)
			totalcost=0
			for result in results:
				if not (result.subcategory == "bottle" or result.subcategory == "keg"):
					totalcost=totalcost+result.cost
			totalcost=totalcost+(recipe.batch_size_required*overheadperlitre)
			self.response.out.write("""		<BREW_COST>%.2f</BREW_COST>""" %( totalcost ))

			self.response.out.write("""
		</EXTENSION>""")

			self.response.out.write("""
	</RECIPES>""")	




		if self.request.get("xml") == "2":
			"""
			BeerXML2  - focus on XML1 for now
			"""
			self.response.headers['Content-Type']="text/xml"
			self.response.out.write("""<?xml version="1.0" encoding="UTF-8"?>
	<beer_xml xmlns="urn:beerxml:v2" xmlns:ferm="urn:beerxml:fermentable:v2" xmlns:hop="urn:beerxml:hop:v2" xmlns:step="urn:beerxml:mash:step:v2" xmlns:mash="urn:beerxml:mash:v2" xmlns:misc="urn:beerxml:miscellaneous:v2" xmlns:rec="urn:beerxml:recipe:v2" xmlns:style="urn:beerxml:style:v2" xmlns:unit="urn:beerxml:unit:v2" xmlns:water="urn:beerxml:water:v2" xmlns:yeast="urn:beerxml:yeast:v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:beerxml:v2 BeerXML.v2.xsd"	xmlns:extension="urn:aaa:extension">
		<version>2.06</version>
		<recipes>
			<recipe>""")
			if not recipe.credit:	recipe.credit=" "



			boilTime=60
			results  = db.GqlQuery("SELECT * FROM gIngredients WHERE hopAddAt >= :4  AND  owner = :1 AND recipename = :2 AND ingredientType = :3  ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0).fetch(1)
			try:
				boilTime=results[0].hopAddAt
			except:
				pass
			self.response.out.write("""
				<rec:name>%s</rec:name>
				<rec:type>%s</rec:type>
				<rec:author>%s</rec:author>
				<rec:batch_size volume="l">%s</rec:batch_size>
				<rec:boil_size volume="l">%s</rec:boil_size>
				<rec:boil_time duration="min">%s</rec:boil_time>
				<rec:efficiency>%s</rec:efficiency>""" %(brewlog.realrecipe,recipe.recipe_type,recipe.credit,recipe.batch_size_required,recipe.boilVolume, boilTime, recipe.mash_efficiency))
			self.response.out.write("""
				<rec:style>
					<style:name>%s</style:name>
				</rec:style>""" %(recipe.forcedstyle))


			# Ingredients
			self.response.out.write("""
				<rec:ingredients>""")

			# Grain Bill		
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",False )
			grains = query.fetch(4324234)
			if len(grains) > 0:
				self.response.out.write("""
					<rec:grain_bill>""")	
		
			for grain in grains:	
				self.response.out.write("""
						<ferm:addition>
							<ferm:name>%s</ferm:name>
							<ferm:type>grain</ferm:type>
							<ferm:amount mass="g">%.1f</ferm:amount>
						</ferm:addition>""" %(grain.ingredient,grain.qty))

			if len(grains) > 0:
				self.response.out.write("""
					</rec:grain_bill>""")	



			# Adjuncts
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",True)
			adjuncts = query.fetch(4324234)
			if len(adjuncts) > 0:
				self.response.out.write("""
					<rec:adjuncts>""")	
		
			for adjunct in adjuncts:	
				self.response.out.write("""
						<misc:addition>
							<misc:name>%s</misc:name>
							<misc:type>%s</misc:type>
							<misc:amount mass="g">%.1f</misc:amount>
						</misc:addition>""" %(adjunct.ingredient,"",adjunct.qty))

			if len(adjuncts) > 0:
				self.response.out.write("""
					</rec:adjuncts>""")	





			# hops Bill		
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE hopAddAt >= :4  AND  owner = :1 AND recipename = :2 AND ingredientType = :3  ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0)
			hops = query.fetch(4324234)
			if len(hops) > 0:
				self.response.out.write("""
					<rec:hop_bill>""")	
		


			for hop in hops:	
				self.response.out.write("""
						<hop:addition>
							<hop:name>%s</hop:name>
							<hop:form>%s</hop:form>
							<hop:alpha_acid_units>%.2f</hop:alpha_acid_units>
							<hop:amount mass="g">%.1f</hop:amount>
							<hop:use>%s</hop:use>
							<hop:time duration="min">%.1f</hop:time>
						</hop:addition>""" %(hop.ingredient, hop.hopForm,hop.hopAlpha,hop.qty,hop.hopUse,hop.hopAddAt))

			if len(hops) > 0:
				self.response.out.write("""
					</rec:hop_bill>""")	




			# Yeast Bill		
			query  = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3", ownername,recipename, "yeast")
			yeasts = query.fetch(4324234)
			if len(yeasts) > 0:
				self.response.out.write("""
					<rec:yeast_additions>""")	
		


			for yeast in yeasts:	
				self.response.out.write("""
						<yeast:addition>
							<yeast:name>%s</yeast:name>
							<yeast:amount volume="g">%.1f</yeast:amount>
						</yeast:addition>""" %(yeast.ingredient, 11*yeast.qty ))

			if len(yeasts) > 0:
				self.response.out.write("""
					</rec:yeast_additions>""")	



			# End Ingredients
			self.response.out.write("""
				</rec:ingredients>""")

			self.response.out.write("""
				<rec:notes>%s</rec:notes>""" %(recipe.description))
			self.response.out.write("""
				<rec:original_gravity>%.4f</rec:original_gravity>
				<rec:final_gravity>%.4f</rec:final_gravity>""" %(recipe.estimated_og,recipe.estimated_fg))

			self.response.out.write("""
			</recipe>
		</recipes>""")



			#
			#	Our exetensions to add some brewlog bits into the recipe
			#
			#
			self.response.out.write("""
		<extension>""")

			
			# Brew Day

			if result2[0].brewdate2 > 0:
				self.response.out.write("""		<brewDateEnd>%s</brewDateEnd>""" %(result2[0].brewdate2 ))
			if result2[0].brewdate > 0:
				self.response.out.write("""		<brewDate>%s</brewDate>""" %(result2[0].brewdate ))
			if result2[0].bottledate > 0:
				self.response.out.write("""		<bottleDate>%s</bottleDate>""" %(result2[0].bottledate ))

			if result2[0].smallImage:
				self.response.out.write("""		<smallLabel>%s</smallLabel>""" %(result2[0].smallImage ))

			if result2[0].largeImage:
				self.response.out.write("""		<bigLabel>%s</bigLabel>""" %(result2[0].largeImage ))


			try:
				results=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND recipe = :3 AND fieldKey = :4", ownername,brewlogname,recipename,"og")
				result=results.fetch(1)[0]
				self.response.out.write("""		<extension:actualOg>%.4f</extension:actualOg>""" %( float(result.fieldVal)))
			except:
				pass

			try:
				results=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND recipe = :3 AND fieldKey = :4", ownername,brewlogname,recipename,"fg")
				result=results.fetch(1)[0]
				self.response.out.write("""		<extension:actualFg>%.4f</extension:actualFg>""" %( float(result.fieldVal)))
			except:
				pass


			overheadperlitre=0
			try:
				results=db.GqlQuery("SELECT * FROM gBrewery WHERE owner = :1", ownername)
				result = results.fetch(1)
				overheadperlitre=result[0].overheadperlitre
				self.response.out.write("""		<extension:breweryName>%s</extension:breweryName>""" %( result[0].breweryname))
			except:
				pass	



			

			results = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2", ownername,brewlogname).fetch(1000)
			totalcost=0
			for result in results:
				if not (result.subcategory == "bottle" or result.subcategory == "keg"):
					totalcost=totalcost+result.cost
			totalcost=totalcost+(recipe.batch_size_required*overheadperlitre)
			self.response.out.write("""		<extension:brewcost>%.2f</extension:brewcost>""" %( totalcost ))

			self.response.out.write("""
		</extension>""")

			self.response.out.write("""
	</beer_xml>""")	


application = webapp.WSGIApplication( 	
	[ ('/publish/import/.*',ImportRecipe), ('/publish/recipe/.*',PublishRecipe), ('/publish/export/',ExportRecipe) ], debug=True)
run_wsgi_app(application)

