import base64
import sys
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



class RecipeBounce(webapp.RequestHandler):
	def get(self):
		if self.request.headers['User-Agent'].lower().count("android") and not self.request.headers['User-Agent'].lower().count("aaarecipeviewer_android"):
			self.response.headers['Content-Type']="text/html"
			self.response.out.write("""	
	<html><head>
	<script language="Javascript">
	setTimeout(function() {
		document.write("Unable to open Homebrew Recipe Viewer... <a href='market://details?id=net.collie.mellon.aaa.recipeviewer'>visit Android Market</a> to install.<p>Once installed <a href='net.collie.mellon.recipeviewer://recipeviewer/%s/'>try again</a>");
	}, 2000);
	document.write('<iframe style="border:none; width:1px; height:1px;" src="net.collie.mellon.recipeviewer://recipeviewer/%s/"></iframe>');
	</script></head></html>

	<!-- this service may disappear in the future do not rely on it -->

			""" %(base64.b64encode(self.request.get("xmlurl")), base64.b64encode(self.request.get("xmlurl") ) ) )
		else:
			if  self.request.headers['User-Agent'].lower().count("aaarecipeviewer_android"):
				if not self.request.get("xmlurl").count("xml"):
					if not self.request.get("xmlurl").count("?"):
						self.redirect( "%s?xml=1" %(self.request.get("xmlurl")))
					else:
						self.redirect( "%s&xml=1" %(self.request.get("xmlurl")))
				else:
					self.redirect( self.request.get("xmlurl"))

			else:
				self.redirect( self.request.get("xmlurl"))
			


application = webapp.WSGIApplication( 	
	[	('/bouncer/recipe/.*', RecipeBounce) ],
	 debug=True)
run_wsgi_app(application)

