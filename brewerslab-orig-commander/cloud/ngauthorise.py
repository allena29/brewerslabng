#!/usr/bin/python
import sys
import urllib
import hashlib 
import time
import cgi
import os
from ngData import *
form = cgi.FieldStorage()



if form['authorise'].value == "yes":
	deviceId=form['deviceId'].value
	username="test@example.com"

	ourAuthKey = db().GqlQuery("SELECT * FROM gAuthorisedUsers WHERE deviceId = :1 AND authEmail = :2", deviceId,username )
	results = ourAuthKey.fetch(1)	
	if len(results) == 1:
		authcookie = results[0].authHash
		sys.stderr.write(" already have an existing cookie returning that instead\n")
	else:

		authcookie= hashlib.sha1("%s" %( time.time())).hexdigest()

		ac=gAuthorisedUsers(authCookie="%s_%s" %(username,deviceId),key_name = "%s_%s" %(username,deviceId) )
		ac.authHash = authcookie
		ac.authEmail = username
		ac.deviceId = deviceId
		ac.put()

	sys.stdout.write("Location: com.asduk.brewerspad://authorise/authcookie/%s/%s\n\n" %(authcookie,username))



"""
#
# Revoke an authorisation cookie
#

class Revoke(webapp.RequestHandler):
	def get(self):
		validCode = None

		# Don't make a user log in if they have the authorisation code that is good enough
		self.response.headers['Content-Type'] = "text/html"
	
		indata = urllib.unquote(self.request.path ).split("/")
		sys.stderr.write("\nindata[4] = %s\n" %(indata[-1]))	
		sys.stderr.write("SELECT * FROM gAuthorisedUsers WHERE authHash = %s \n" %(indata[-1] ))
		ourAuthKey = db.GqlQuery("SELECT * FROM gAuthorisedUsers WHERE authHash = :1 ", indata[-1] )
		results = ourAuthKey.fetch(100)	
		
		for result in results:
			sys.stderr.write("deleting record\n")
			result.delete()
			validCode =1 
	
		

# Generate an authorisation cookie for the user to use when hasing their request
#

class Grant(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:  
			self.redirect(users.create_login_url(self.request.uri))
		else:
			# Device/User becomes the key
			deviceId= self.request.get('deviceId')
			if len(deviceId) == 0:	deviceId="Unknown Device"
			username=user.email()

			# Check if we already have an auth key
			sys.stderr.write("SELECT * FROM gAuthorisedUsers WHERE deviceId = %s AND authEmail = %s\n" %( deviceId,username ))
			ourAuthKey = db.GqlQuery("SELECT * FROM gAuthorisedUsers WHERE deviceId = :1 AND authEmail = :2", deviceId,username )
			results = ourAuthKey.fetch(1)	
			if len(results) == 1:
				authcookie = results[0].authHash
				sys.stderr.write(" already have an existing cookie returning that instead\n")
			else:

				authcookie= hashlib.sha1("%s" %( time.time())).hexdigest()

				ac=gAuthorisedUsers(authCookie="%s_%s" %(username,deviceId),key_name = "%s_%s" %(username,deviceId) )
				ac.authHash = authcookie
				ac.authEmail = username
				ac.deviceId = deviceId
				ac.put()

				sys.stderr.write(" %srevoke/%s/%s\n" %(self.request.url,username,authcookie))
					
				# Try to send an email to inform user
				if not user.email().count("@example.com"):
					message = mail.EmailMessage()
					message.subject="Brewerslab Cloud - New Device Access Enabled"
					message.sender = "donotreply@devapi.mellon-collie.net"
					message.to = user.email()
#					message.body = ""Your Google Account has been associated with an instance of Brewerslab in the cloud. 
#
#	The device identified itself as: %s
#
#	If you did not add or no longer require this device to have access to your Brewerslab account then please click here to de-authorise this access:
#	 %srevoke/%s/%s
#		" %(deviceId, self.request.url, username, authcookie)

					message.send()

			self.redirect("com.asduk.brewerspad://authorise/authcookie/%s/%s" %(authcookie,username))

class MainPage2(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = "text/html"
		self.response.out.write("should be handled by android app")


application = webapp.WSGIApplication( 	
	[	('/authorise/', Grant),
		('/authorise/revoke/.*', Revoke),
		('/authorise/intent/.*',MainPage2)],
	 debug=True)
run_wsgi_app(application)
"""
