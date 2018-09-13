import cgi
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson
#import json

from gData import *



class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
	       
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
		else:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('Hello, ' + user.nickname())


class rpcHandler(webapp.RequestHandler):


	def __init__(self):
		webapp.RequestHandler.__init__(self)
		self.approvedMethods = rpcMethods()


	def get(self):
		action = self.request.get('action')
		value = self.request.get('value')

		if len(action) < 1:
			self.error(404)
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('Method not specified')
			return
		
		if action[0] == '_':
			self.error(403) # access denied
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('Access Denied')
			return


		func = getattr(self.approvedMethods, action, None)
		
		if not func:
			self.error(404)
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('Method does not exist')
			return

		self.response.headers['Content-Type'] = "text/plain"
		self.response.out.write(  func( simplejson.loads( value ) ) )
	

		self.response.out.write("\nTesting a hop")
		
		hop = gHop(name="Hallertauv2",key_name="hop1234")
		hop.put()

		ourhops = db.GqlQuery("SELECT * FROM gHop")
		self.response.out.write("%s\n" %(ourhops))
		for h in ourhops:
			self.response.out.write("\n%s" %(h))


		
class rpcMethods:

	def test(self, inputData):
		return "inputData %s" %(inputData)

application = webapp.WSGIApplication( 	
	[('/brewlog/rpc/', rpcHandler)],
	 debug=True)
run_wsgi_app(application)

