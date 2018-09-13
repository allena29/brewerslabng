import cgi
from cloudApi import *
#from django.utils import simplejson
import json
import urllib
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from cloudUtils import cloudUtils
from gData import *

class MainPage(webapp.RequestHandler):

	def __init__(self):

		self.api=brewerslabCloudApi()

	"""
	def get(self):
		print "Content-Type:text/plain\n\n"	
		print "BA"		
		func = getattr(self.api,"listRecipes",None)
		args=()
		args+=("test@example.com",)
		print func(*args)

				

	"""
	
	def get(self):
		user = users.get_current_user()
		if not user.email() == "test@example.com":
			self.response.headers['Content-Type'] = "text/plain"
			self.response.out.write("cannot use this method\n")
			return


		func = getattr(self.api, self.request.get("taskOperation"), None) 

		args=()
		args+=(user.email(),)
	
		for i in range(	int(self.request.get("argNum"))):
			args+=( urllib.unquote(self.request.get("arg%s" %(i))) ,)

		if self.request.get("taskOperation") == "publish":
			self.api.response=self.response
			results = func(*args)
			return 

		# Call function from within cloudApi and write it
		results = func(*args)
		a=1

		AA=0
		for arg in args:
			if AA > 0:
				self.response.out.write("<b>Argument %s:</b> %s<p>" %(AA-1,arg))
				
			AA=AA+1
		self.response.out.write("<b>Task Operation:</b> %s<p>" %(results['operation']))
		self.response.out.write("<b>Status Code:</b> %s<p>" %(results['status']))
		if results.has_key("json"):
			
		
			result = json.loads(results['json'])
			for x in result:
				self.response.out.write("<b>%s</b><p>\n" %(x))
				self.response.out.write("<pre>")
				self.response.out.write( result[x])
				self.response.out.write("</pre>")
				a=0	

			try:
				if result['result'].has_key("cost_result"):
					for c in result['result']['cost_result']:
						self.response.out.write("<b>%s</b><br>" %(c))
						self.response.out.write(" %s <p>" %(result['result']['cost_result'][c]))


				if result['result'].has_key("stock_result"):
					for c in result['result']['stock_result']:
						self.response.out.write("<b>%s</b><br>" %(c))
						self.response.out.write(" %s <p>" %(result['result']['stock_result'][c]))

			except:
				pass


			if a == 1:	
				self.response.out.write("Status %s\n" %( results['status']) )
		else:
			self.response.out.write("No JSON - status %s" %(results['status']))

				
		
	

	def post(self):
		self.response.headers['Content-Type'] = "text/plain"
		self.api.response=self.response
		
		cloudKey = self.request.get("cloudKey")
		cloudRequest= self.request.get("cloudRequest")
		cloudMail = self.request.get("cloudUser")
		cloudDevice = self.request.get("cloudDevice")
		cu=cloudUtils()

		indata = urllib.unquote(self.request.path ).split("/")
		taskOperation = indata[-1]

		sys.stderr.write(" taskOperation %s\n" %(taskOperation))
	
		# If not authroised
		if not cu.checkAuthorised( cloudKey, cloudRequest,cloudMail,cloudDevice):
			self.response.out.write( json.dumps( { 'operation' : taskOperation , 'status' : -1 } ) ) #not authorised
			return
		
		# Decode Request
		decodedRequest = json.loads(cloudRequest)	
	      
		func = getattr(self.api, taskOperation, None) 
		if not func:
			self.response.out.write( json.dumps( { 'operation' : taskOperation , 'status' : -2 } ) ) #function not available
			return


		args=()
		args+=(cloudMail,)
	
		sys.stderr.write("request coming in is %s\n" %(cloudRequest))
		c=0
		for i in range(	decodedRequest['argNum'] ):
			c=c+1
			args+=( decodedRequest['arg%s' %(i)],)

		for arg in args:
			sys.stderr.write(" args reconsituted %s\n" %(arg))

		sys.stderr.write("\ntaskOperation=%s&argNum=%s" %(taskOperation,c))
		c=0
		for arg in args:
	
			sys.stderr.write("&arg%s=%s" %(c,arg))
			c=c+1
	
		sys.stderr.write("\n")		

		# Call function from within cloudApi and write it
		self.response.out.write( func(*args) )
	
	
		

application = webapp.WSGIApplication( [('/brewlab/.*', MainPage), ('/stores/.*', MainPage)  ], debug=True)
run_wsgi_app(application)

