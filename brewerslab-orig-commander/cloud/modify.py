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

class ModifyUpdate1(webapp.RequestHandler):
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
		ourOldRecords = db.GqlQuery("SELECT FROM gBrewlogs WHERE  owner = :1 AND brewhash =:2",user.email(),self.request.get("brewhash"))
		r=ourOldRecords.fetch(1)
		self.response.out.write("___%s" %(r))
		rx=r[0]
		self.response.out.write("___%s" %(rx))

		if self.request.get("smalllabel") == "None":	
			rx.smallImage=None
		elif self.request.get("smalllabel") == "":	
			rx.smallImage=None
		else:
			rx.smallImage=self.request.get("smalllabel")

		if self.request.get("largelabel") == "None":	
			rx.largeImage=None
		elif self.request.get("largelabel") == "":	
			rx.largeImage=None
		else:
			rx.largeImage=self.request.get("largelabel")
		rx.realrecipe=self.request.get("newname")
		rx.brewdate=int(self.request.get("brewdate"))
		rx.brewdate2=int(self.request.get("brewdate2"))
		rx.bottledate=int(self.request.get("bottledate"))
		rx.put()



class ModifyOverview(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
			return
		owner=user.email()
		self.response.headers['Content-Type']="text/html"

		self.response.out.write("\nBrewlogs\n")
		i=0
		gqlresult = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1",owner)
		results = gqlresult.fetch(200)	
		for result in results:
			self.response.out.write("\t%s: %s/%s %s\n" %(i,result.brewlog,result.recipe,result.brewhash))
			self.response.out.write("<form method=post action=\"/modify/update1/\">")
			self.response.out.write("<input type=\"hidden\" name=\"brewhash\" value=\"%s\">" %(result.brewhash))
			self.response.out.write(" Small Label: <input type=\"text\" name=\"smalllabel\" value=\"%s\"><br>" %(result.smallImage))
			self.response.out.write(" Large Label: <input type=\"text\" name=\"largelabel\" value=\"%s\"><br>" %(result.largeImage))
			self.response.out.write(" Recipe Override: <input type=\"text\" name=\"newname\" value=\"%s\"><br>" %(result.realrecipe))
			self.response.out.write(" Brew Date (Start): <input type=\"text\" name=\"brewdate\" value=\"%s\"><br>" %(result.brewdate))
			self.response.out.write(" Brew Date (End): <input type=\"text\" name=\"brewdate2\" value=\"%s\"><br>" %(result.brewdate2))
			self.response.out.write(" Bottle Date: <input type=\"text\" name=\"bottledate\" value=\"%s\"><br>" %(result.bottledate))

			self.response.out.write(" <input type=\"submit\" value=\"update\">")
			self.response.out.write("</form>")

			i = i +1

application = webapp.WSGIApplication( 	
	[('/modify/update1/',ModifyUpdate1), ('/modify/overview/',ModifyOverview) ], debug=True)
run_wsgi_app(application)

