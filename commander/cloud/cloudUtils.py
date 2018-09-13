import re
from google.appengine.api import users
from google.appengine.ext import db
import hashlib
import sys

class cloudUtils:

	def __init__(self):
		self.ver=1


	def checkAuthorised(self,apikey="",apirequest="",apiuser="",apidevice=""):
		sys.stderr.write("cloudUtils: checking if authorised or not\n")
		sys.stderr.write("SELECT * FROM gAuthorisedUsers WHERE authEmail = %s AND deviceId = %s\n" %( apiuser,apidevice))
		ourAuthKey = db.GqlQuery("SELECT * FROM gAuthorisedUsers WHERE authEmail = :1 AND deviceId = :2", apiuser,apidevice)
		results = ourAuthKey.fetch(1)
		if len(results) < 1:	
			sys.stderr.write("cloudUtils: user not present in the database\n")
			return False	# not in the database	
		sys.stderr.write("Hash Elements: cloudRequest=%s\n" %(apirequest))
		sys.stderr.write("             : cloudSalt=Dolphin\n")
		sys.stderr.write("             : cloudKey=%s\n" %(results[0].authHash))
		tmp = "cloudRequest=%s_cloudSalt=%s_cloudKey=%s" %(apirequest,"Dolphin",results[0].authHash)
		tmp = hashlib.md5(tmp).hexdigest()
		#tmp = re.compile("0").sub('',hashlib.md5(tmp).hexdigest())
		sys.stderr.write("Expected RequestHash: %s\n" %( re.compile("0").sub('',tmp ) ))
		sys.stderr.write("Received RequestHash: %s\n" %( re.compile("0").sub('',apikey )) )
		if not re.compile("0").sub('',tmp) == re.compile("0").sub('',apikey):
			sys.stderr.write("cloudUtils: request hash does not match\n")
			return False		# not correct

		return True
			
