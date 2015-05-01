#!/usr/bin/python
import cgi
import sys
from cloudNG import *
import json
import urllib
#from cloudUtils import cloudUtils
from ngData import *


form = cgi.FieldStorage()


#
# do not have authentication anymore... we should add in authentiation one day.
# the android app still does authcookie look ups
#


if form.has_key("rawCalcLog"):
	print "Content-Type:text/html\n"
	if form.has_key("brewlog"):
		calclog=db().GqlQuery("SELECT * FROM gCalclogs WHERE owner = :1 AND recipe = :2 AND brewlog = :3",form['owner'].value,form['rawCalcLog'].value,form['brewlog'].value).fetch(1)
		print "<b>Calclog %s/%s</b><pre>" %(form['brewlog'].value,form['rawCalcLog'].value)
	else:		
		calclog=db().GqlQuery("SELECT * FROM gCalclogs WHERE owner = :1 AND recipe = :2",form['owner'].value,form['rawCalcLog'].value).fetch(1)
		print "<b>Calclog %s</b><pre>" %(form['rawCalcLog'].value)

	print calclog[0].calclog
	print "</pre>"
	sys.exit(0)

if not form.has_key("taskOperation"):
	print "Content-Type:text/html\n"
	print "Need a taskOperation"
	sys.stderr.write("ngbrewlab.py: Need a taskOperation to do something\n")	
	sys.exit(0)

		
cloudMail = form['cloudUser'].value
cloudRequest=form['cloudRequest'].value
decodedRequest = json.loads(cloudRequest)	

api = brewerslabCloudApi()
func = getattr(api, form['taskOperation'].value,None)
if not func:
	sys.stderr.write("ngbrewlab.py: Invalid taskOperation %s\n" %(form['taskOperation'].value))	
	print "Content-Type:text/html\n"
	print json.dumps({'operation':taskOperation,'status':-2})
	sys.exit(0)

args=()
args+=(cloudMail,)
c=0
sys.stderr.write("ngbrewlab.py: Request %s\n" %(form['taskOperation'].value))
for i in range(decodedRequest['argNum']):
	c=c+1
	args+=( decodedRequest['arg%s' %(i)],)
	sys.stderr.write("ngbrewlab.py:  adding arg %i\n" %(i))

print "Content-Type:text/html\n"
x="%s" %(func(*args) )
sys.stderr.write(x)
sys.stderr.write("\n")
print x




"""

class MainPage(webapp.RequestHandler):

	def __init__(self):

		self.api=brewerslabCloudApi()

	
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
"""
