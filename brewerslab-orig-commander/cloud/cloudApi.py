from __future__ import division

#kettle1evaporation
#kettle2evaporation
#kettle3evaporation
#gravityprecool
#kettle1preboilgravity		# should be without adjunct
#kettle2preboilgravity		# should be without adjunct
#kettle3preboilgravity		# should be without adjunct
#kettle1volume
#kettle2volume
#kettle1kettle2volume
#kettle3volume
#kettle1kettle2kettle3volume




# 
# Copyright (c) 2011 Adam Allen, 
# All Rights Reserved, including the right to allow you 
# to use the software in accordance with the GPL Licence
#
#   brewerslab
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#        http://www.gnu.org/licenses/gpl.txt
#
# $Revision: 1.9 $ $Date: 2011-11-03 22:41:05 $ $Author: codemonkey $
#
import base64
import traceback
import json
import time
import urllib
from brewerslabEngine import *
from brewerslabData import *
import SimpleXMLRPCServer
from google.appengine.ext import db

from gData import *
import base64
import hashlib
import re
import os
import time


"""
Currently converting from python pickles to google app engine datastore.

In future it should be fairly straightforward to convert to SQL after this has been done


In an operation header we need username as the first parameter (wasn't the case before)
We need to be sure to send nothign to stdout (it will break JSON decoding in the android app


"""

class brewerslabCloudApi:
	
	def __init__(self):
		self.userid="allena29"
#		self.data = brwlabPresetData( self.userid )

		self.data=None
		self.recipe=None
		self.brewlog=None	
		self.activity=None
		self.process=None
		self.stores=None
#		self.stores= pickle.loads( open("store/%s/store" %(self.userid)).read() )

	def dbgRestart(self):
		self.recipe=None
		self.brewlog=None
		self.activity=None
		self.process=None
		self.stores= pickle.loads( open("store/%s/store" %(self.userid)).read() )
		return 1


	def listRecipes(self, username):
		try:
			sys.stderr.write("listRecipes() ->\n")

			recipeList=[]
			ourRecipes = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1", username)
			for recipe in ourRecipes.fetch(2000):
				recipeList.append( recipe.recipename )
			recipeList.sort()
			sys.stderr.write("listRecipes() <- %s\n" %(recipeList))
			return {'operation' : 'listRecipes', 'status' : 1, 'json' : json.dumps( {'result': recipeList} ) }

		except ImportError:
			return {'operation' : 'listRecipes', 'status' : 0}



	def listActivitiesFromBrewlog(self,username,process,recipe,brewlog):
		"""
		listActivitiesFromBrewlog
		returns activities without actually opening the brewlog
		
		returns standard header
		"""

		#
		# Note: recipe isn't really needed here but we have retained it to keep cloudApi
		# aligned with the previous xmlrpc 
		#
		sys.stderr.write("listActivitiesFromBrewlog() -> %s,%s\n" %(process,brewlog))
		try:

	
			# we can't really expect the sender to know the process based on the recipe only

			ourProcess = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2", username,brewlog).fetch(1)[0]
			process = ourProcess.process
			sys.stderr.write("over-riding process to %s\n" %(ourProcess.process))
		
			activities=[]
			completeactivities=[]
			ourActivities = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum= :3 AND subStepNum = :4 AND activityNum > -1 ORDER BY activityNum", username,process,-1,-1)

			for activity in  ourActivities:
				activities.append(activity.stepName)

				ourCompleteOrNot = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog= :2 AND activityNum = :3 AND subStepNum = :4 ORDER BY stepNum DESC",username,brewlog,activity.activityNum,-1).fetch(1)[0]
				if ourCompleteOrNot.subStepsCompleted or ourCompleteOrNot.completed:
					completeactivities.append( True )
				else:
					completeactivities.append( False )
				
		
			result={}
			result['completeactivities'] = completeactivities
			result['activities'] = activities
			result['recipe']=recipe
			result['process']=process
			result['brewlog']=brewlog
			sys.stderr.write( " result: %s\n" %(json.dumps(result))	)
			return {'operation' : 'listActivitiesFromBrewlog', 'status' : 1, 'json' : json.dumps( {'result': result} ) }
		except:
			sys.stderr.write("EXCEPTION in listActivitiesFromBrewlog\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))

		return {'operation' : 'listActivitiesFromBrewlog', 'status' : 0}
	

	
	def listBrewlogsByRecipe(self,username,recipeName,raw=False):
		sys.stderr.write("listBrewlogsByRecipes() -> %s\n" %(recipeName))
		try:
			existingBrewlog = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,"__dummy").fetch(100000)
			for eB in existingBrewlog:	eB.delete()
		except:
			pass
		try:
			ourRecipes = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			tmp = ourRecipes.fetch(1)[0]
			PROCESS=tmp.process
			sys.stderr.write("PROCESS = %s\n" %(PROCESS))	
			brewlogList=[]
			ourRecipes = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND recipe = :2", username,recipeName)
			for recipe in ourRecipes.fetch(2455):	


				ourActivities = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum= :3 AND subStepNum = :4 AND activityNum > -1 ORDER BY activityNum", username,PROCESS,-1,-1)
				allComplete=True
				for activity in  ourActivities:
					ourCompleteOrNot = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog= :2 AND activityNum = :3 AND subStepNum = :4 ORDER BY stepNum DESC",username,recipe.brewlog,activity.activityNum,-1).fetch(1)[0]
					if not ourCompleteOrNot.subStepsCompleted and not ourCompleteOrNot.completed:
						allComplete=False


				bi={}
				bi['recipe'] = recipe.recipe
				bi['process'] = PROCESS
				bi['name'] =  recipe.brewlog
				bi['complete'] =  allComplete
				brewlogList.append(bi)

			brewlogList.sort()
			sys.stderr.write("listBrewlogsByRecipe() <- %s\n" %(brewlogList))


			pl={}
			ourProcesses = db.GqlQuery("SELECT * FROM gProcesses WHERE owner = :1 ", username).fetch(234234)
			for op in ourProcesses:
				pl[ op.process ] = 1
			processList=[]
			for x in pl:
				processList.append(x)
			processList.sort()
			processList.reverse()


			if raw:	
				return {'result':brewlogList,'result2':processList}

			return {'operation' : 'listBrewlogByRecipe', 'status' : 1, 'json' : json.dumps( {'result': brewlogList,'result2':processList} ) }

		except:
			sys.stderr.write("listBrewlogsByRecipe() Exception\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s\n" %(e))

			if raw:
				return
			return {'operation' : 'listBrewlogByRecipe', 'status' : 0}


	def closeRecipe(self):
		print "closeRceipe() -> "
		self.recipe = None
		print "closeRecipe() <-"
		return {'operation' : 'closeRecipe', 'status' : 1 }


	def openRecipe(self,recipe):
		print "openRecipe() -> %s" %(recipe)
		status = 0
		try:
			o=open("recipes/%s/%s" %(self.userid, re.compile("[^a-zA-Z0-9]").sub('_',recipe)))
			self.recipe = pickle.loads( o.read() )
			o.close()
			status = 1
		except:
			print "EXCEPTION"
#			exc_type, exc_value, exc_traceback = sys.exc_info()
#			for e in traceback.format_tb(exc_traceback):	print e
			pass
			
		print "openRecipe() <- %s" %(status)
		
		return {'operation' : 'openRecipe', 'status' : status  }



	def currentRecipe(self):
		print "currentRecipe() ->"
		status=0
		try:
			print "currentReipce() <- %s " %(self.recipe.name)
			return {'operation' : 'currentRecipe', 'status' : 1, 'json' : "%s" %( {'result':self.recipe.name}   )}
		except:
			pass			
		print "currentReipce() <- %s" %(status)
		return {'operation' : 'currentRecipe', 'status' : status }



	def newRecipe(self, recipe):
		print "newRecipe() -> %s" %(recipe)
		status=0
		try:
			recipeFile = re.compile("[^a-z0-9A-Z]").sub('_', recipe.lower() )
			if os.path.exists("recipes/%s/%s" %(self.userid,recipeFile)):
				print "newRecipe() false" 
				return {'operation' : 'newRecipe', 'status' : 0  }
			self.recipe = brwlabRecipe()
			self.recipe.name = recipe
			self.recipe.userid = self.userid
			self.recipe.calculationOutstanding=True
			self.recipe.save( "recipes/%s/%s" %(self.userid,recipeFile))

			status = 1
		except:
			pass

		print "newRecipe() %s" %(status) 
		return {'operation' : 'newRecipe', 'status' : status }
	

	def setRecipeDescription(self,description):
		print "setRecipeDescription() -> %s " %(description)	
		status=0
		try:
			self.recipe.description = description
			status=1
		except:
			pass
		return {'operation' : 'setRecipeDescription','status':status}

	def saveStore(self):
		print "saveStore() <>"
		status=0
		try:
			o=open("store/%s/store" %(self.userid),"w")
			o.write(pickle.dumps(self.stores))
			o.close()
			status =1
		except:
			pass
		return {'operation' : 'saveStore', 'status' : status }


	def saveBrewlog(self):
		print "saveBrewlog() <>"
		status=0
		try:
			self.brewlogfilename= "brewlog/%s/%s/%s/%s" %(self.userid, re.compile("[^A-Za-z0-9]").sub('_',self.process.name), re.compile("[^A-Za-z0-9]").sub("_",self.recipe.name.lower()), re.compile("[^A-Za-z0-9]").sub('_',self.brewlog.name.lower()))
			print "saving to ",self.brewlogfilename
			o=open(self.brewlogfilename,"w")
			o.write(pickle.dumps(self.brewlog))
			o.close()
			status =1
		except:
			pass
		return {'operation' : 'saveBrewlog', 'status' : status }



	def saveRecipe(self):
		print "saveRecipe() <>"
		status=0
		try:
			recipeFile = re.compile("[^a-z0-9A-Z]").sub('_', self.recipe.name.lower() )
			self.recipe.save( "recipes/%s/%s" %(self.userid,recipeFile))
			status = 1
		except:
			pass

		print "saveRecipe() %s" %(status) 
		return {'operation' : 'saveRecipe', 'status' : status }
		

	def getRecipe(self):
		"""
		getRecipe()
		
		return: current recipe encoded in JSON format
		"""

		print "getRecipe() <> "
		status=0
		if not self.recipe:
			return {'operation' : 'getRecipe', 'status' : 0}
		return { 'operation' : 'getRecipe', 'status' : 1, 
				'json' : json.dumps( self.recipe.dumpJSON() )  
			}



	def getCalcLog(self):
		"""
		getCalcLog()
	
		return: string calclog
		"""
		print "getCalcLog <>"
		try:
			return {'operation' : 'getCalcLog','status' : 1,
				'json' : json.dumps({'result':"         :\n%s\n\n\n          :\n%s\n\n" %( self.recipe.calclog,self.stores.calclog)})}

		except:
			return {'operation' : 'getCalcLog','status': 0}
			
		
	def setBatchSize(self,username,recipeName, newBatchSize,doRecalculate="1"):
		"""
		setBatchSize(batchSize)
			batchSize = Final batchSize in Litres after taking account of losses
		
		return: standard api header
		"""
		sys.stderr.write("setBatchSize recipeName %s newBatchSize %s\n" %(recipeName,newBatchSize));
		status=0



		try:
			ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.batch_size_required=int(newBatchSize)
				if doRecalculate == "0":	recipe.calculationOutstanding=True
				recipe.put()

			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)


			status=1
			result={}
			result['stats']={}
			result['stats']['batch_size_required']=int(newBatchSize)

			return {'operation' : 'setBatchSize','status' :status , 'json': json.dumps(result)  }
		except:
			sys.stderr.write("EXCEPTION in setBatchSize\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))


		return {'operation' : 'setBatchSize','status' : status}


	def setTopupVolume(self,username, topupVol,doRecalculate="1"):

		"""
		setTopupVolume(topupVol)
			topulVol = Topup to be provided in Litres after boil

		return: standard api header
		"""
		sys.stderr.write("setTopupVolume -> %s" %(topupVol))
		status=0
		result={}
		try:
			ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				#recipe.batch_size_required=int(newBatchSize)
				self.recipe.top_up = float(topupVol)
				if doRecalculate == "0":	recipe.calculationOutstanding=True
				recipe.put()


			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)
			result={}
			result['stats']={}
			result['stats']['postBoilTopup']=float(topupVol)
			status=1
		except:
			pass
		#print "setTopupVolume <- "
		return {'operation' : 'setTopupVolume','status' :status , 'json': json.dumps(result)  }


	def listIngredients(self,category):
		"""
		listIngredients(category)
			category = 	fermentable,hop,yeast,misc,consumable
			
		return: list of ingredients from the presets file
		"""

		print "listIngredients -> %s" %(category)
		status=0

		try:
			return {'operation' : 'listIngredients', 'status' : 1,
					'json' : "%s" %( self.data.dumpJSON( category )  ) 
				}
		except:	pass
		return {'operation' : 'listIngredients', 'status' : status }



	def listIngredientDetail(self,category,ingredient):
		"""
		listIngredientDetail(category, ingredient)
			category = 	fermentable,hop,yeast,misc,consumable
			ingredient = 	string values
			
		return: dict of ingredient detail
		"""

		print "listIngredients -> %s" %(category)
		status=0

		try:
			return {'operation' : 'listIngredientDetail', 'status' : 1,
					'json' : "%s" %( self.data.dumpDetailJSON( category, ingredient )  ) 
				}
		except:	pass
		return {'operation' : 'listIngredients', 'status' : status }



	def listProcess(self,username):
		"""
		listProcesses

		return: list of processes
		"""
		p=[]
		sys.stderr.write("listProcess\n")
		ourProcess = db.GqlQuery("SELECT * FROM gProcesses WHERE owner = :1  ",username)
		for process in ourProcess.fetch(5000):
			p.append(process.process)

		p.sort()
		return {'operation' : 'listProcess', 'status' : 1,'json':json.dumps( {'result': p}  ) }


	def setProcess(self,process):
		"""
		setProcess
			process	=	processLabel (as per listProcess)

		return:	standard header
		"""
		status=0
		print "setProcess -> %s" %(process)

		try:
	
			myprocess = pickle.loads(open("process/%s/%s" %(self.userid,process)).read())
			self.recipe.attachProcess( myprocess )
			status=1
		except: 
			traceback.print_exc()
		print "setProcess <- "
		return {'operation' :'setProcess','status':status}


	def addHopIngredientToRecipe(self, ingredient, qty, hopAddition):
		"""
		addHopIngredientToRecipe(category,ingredient,qty)
			hop = 		string value as found from listIngredient/listIngredientDetails
			qty =		qty to add (as per unit on listIngredientDetails)
			hopadd =	time in minutes from the end of the boil to add the hop

		return:	standard header
		"""
		status=0
		print "addHopIngredientToRecipe() -> %s %s %s" %(ingredient,qty,hopAddition)
		try:
			if self.recipe:
				recipeObject = self.data.getHop( ingredient )
				self.recipe.addIngredient( recipeObject, qty, hopAddition )	
				try:
					self.recipe.calculate()
				except:
					print self.recipe.calclog	
					traceback.print_exc()
					status=0
				status =1
		except:	pass
		print "addHopIngredientToRecipe() <- .."

		return {'operation' : 'addHopIngredientToRecipe','status':status}

	def addIngredientToRecipe(self, category, ingredient, qty):
		"""
		addIngredientToRecipe(category,ingredient,qty)
			cateogry =	fermentable,hop,yeast,misc,consumable
			ingredient = 	string value as found from listIngredient/listIngredientDetails
			qty =		qty to add (as per unit on listIngredientDetails)

		return:	standard header
		"""

		status=0
		print "addIngredientToRecipe() -> %s %s" %(ingredient,qty)
		try:
			if self.recipe:
				recipeObject = None
				if category == "fermentable":	recipeObject = self.data.getFermentable( ingredient )
				if category == "hop":	recipeObject = self.data.getHop( ingredient )
				if category == "yeast":	recipeObject = self.data.getYeast( ingredient )
				if category == "misc":	recipeObject = self.data.getMisc( ingredient )
				if category == "consumable":	recipeObject = self.data.getConsumable( ingredient )
				if category:
					self.recipe.addIngredient( recipeObject, qty )	
					try:
						self.recipe.calculate()
					except:
						print self.recipe.calclog	
						traceback.print_exc()
						status=0
					status =1
		except:	pass
		print "addIngredientToRecipe() <- .."

		return {'operation' : 'addIngredientToRecipe','status':status}


	def getWaterRequired(self):
		"""
		getWaterRequried()

		return:	integer of total water required for the brew in litres
		"""

		print "getWaterRequired() -> "
		if self.recipe:
			try:
				waterRequired = self.recipe.calculate()
			except:
				traceback.print_exc()
				return {'operation' : 'addIngredientToRecipe','status':0}
			waterRequired= self.recipe.waterRequirement()
			return {'operation' : 'getWaterRequired', 'status' : 1, 'json' : json.dumps( {"result":waterRequired} ) }

		return {'operation' : 'addIngredientToRecipe','status':0}


	def scaleAlcohol(self,newABV):
		"""
		scaleABV()
			float of required abv			
	
		return:	float with response
		"""

		print "scaleAlcohol() -> %s " %(newABV)
		if self.recipe:
			try:
				self.recipe.scaleAlcohol( newABV )
				return {'operation' : 'scaleAlcohol', 'status' : 1, 'json' : json.dumps( {"result": self.recipe.estimated_abv } ) }
			except:
				print self.recipe.calclog	
				traceback.print_exc()

		return {'operation' : 'scaleAlcohol','status':0}



	def scaleIBU(self,username,recipeName,newIBU,doRecalculate="1"):
		"""
		scaleIBU()
			float of required ibu
	
		return:	float with response
		"""

		sys.stderr.write( "scaleIBU() -> %s\n" %(newIBU))

		#
		#	 note this should probably use gContributions to do the scaling
		#

		return {'operation' : 'scaleIBU','status':-5}		# NOT SUPPOrtED



		try:
			
			ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.scaleHops( float(newIBU)  )
#				self.recipe.calculate()
				if doRecalculate == "0":	recipe.calculationOutstanding=True
				recipe.put()



			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)

			result={}
			result['stats']={}
			result['stats']['estimated_ibu']=recipe.estimated_ibu

			status=1

			return {'operation' : 'scaleIBU','status' :status , 'json': json.dumps(result)  }
		except:
			sys.stderr.write("EXCEPTION in setBatchSize\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))

				#print self.recipe.calclog	
#				exc_type, exc_value, exc_traceback = sys.exc_info()
#				for e in traceback.format_tb(exc_traceback):	print e

		return {'operation' : 'scaleIBU','status':0}







	def startNewBrewlog(self,username,name,recipeName,process,reset=0):
		"""
		startNewBrewLog()
			string name of the brewlog

		return: standard response header
		"""
		sys.stderr.write("startNewBrewlog %s/%s/%s /%s" %(name,recipeName,process,reset))
		status = 0

#		existingBrewlog = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,name).fetch(400)
#		for ebb in existingBrewlog:	ebb.delete()


		if not reset:
			existingBrewlog = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,name).fetch(1)
			if len(existingBrewlog):
				return {'operation' : 'startNewBrewLog','status':-1}
	
		recipeDetails = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2",username,recipeName).fetch(1)
		if len(recipeDetails) == 0:
			return {'operation' : 'startNewBrewLog','status':-2}
		

		if reset == 1:
			sys.stderr.write("RESETTING BREWLOG\n")
			ourOldBrewlogSteps = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2",username,name).fetch(500000000)
			for x in ourOldBrewlogSteps:
				x.delete()

			ourOldFields=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2",username,name).fetch(4324234)	
			for x in ourOldFields:
				x.delete()

			sys.stderr.write("process %s\n" %(process))

		if not reset:
			brwlog = gBrewlogs( recipe=recipeName,brewlog=name,owner=username )
			brwlog.realrecipe = recipeName
			brwlog.process=process
			brwlog.boilVolume = recipeDetails[0].boilVolume
			brwlog.brewhash = base64.b64encode("%s/%s/%s" %(username,recipeName,name))
			brwlog.put()	
		



		ourRecipeStats = db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2",username,recipeName).fetch(500000)[0]
		


		ourProcess = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum > :3",username,process,-1).fetch(500000)
		sortIndex=0
		for processStep in ourProcess:

			# doing conditionals
			dostep=1
			if processStep.conditional:
				dostep=0
				try:
					sys.stderr.write(" Process Step : %s" %(processStep.conditional[0]))
					valX = ourRecipeStats.__dict__[ processStep.conditional[0] ]	
					sys.stderr.write("              : %s" %(valX))
					valY = int(ourRecipeStats.__dict__[ processStep.conditional[2] ])
					sys.stderr.write("              : %s" %(valY))
					if processStep.conditional[1] == ">":
						if valX > valY:	doStep=1
					if processStep.conditional[1] == ">=":
						if valX >= valY:	doStep=1
					if processStep.conditional[1] == "<":
						if valX < valY:	doStep=1
					if processStep.conditional[1] == "<=":
						if valX <= valY:	doStep=1
					if processStep.conditional[1] == "==":
						if valX == valY:	doStep=1
					if processStep.conditional[1] == "!=":
						if valX != valY:	doStep=1
					sys.stderr.write("              : dostep %s" %(doStep))
				except:
					dostep=1
			if dostep:	
				stp = gBrewlogStep(recipe=recipeName,brewlog=name,activityNum=processStep.activityNum, stepNum=processStep.stepNum, subStepNum=processStep.subStepNum,owner=username,sortIndex=sortIndex )
				stp.stepName=processStep.stepName
				stp.completed=False
				stp.needToComplete=processStep.needToComplete
				stp.put()
				sortIndex=sortIndex+1


		ourFields=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND process = :2",username,process).fetch(4324234)	
		for field in ourFields:
			blankfield=gField(owner=username,stepNum=field.stepNum,activityNum=field.activityNum)
			blankfield.brewlog=name
			blankfield.fieldKey=field.fieldKey
			blankfield.fieldWidget=field.fieldWidget
			blankfield.parent=field.parent
			blankfield.fieldTimestamp=field.fieldTimestamp
			blankfield.put()

		status =1
			
		
		return {'operation' : 'startNewBrewLog','status':status,'json': json.dumps({}) }
			




	def listActivities(self):
		"""
		listActivities()
			string activity
	
		call selectProcess() first
		return: standard response header
		"""
		print "listActivities <"
		status=0
		activities=[]
		try:
			for activity in self.process.activities:
				activities.append(activity.activityTitle)
			return {'operation' : 'listActivities', 'status' : 1, 'json' : json.dumps( {"result": activities } ) }
		except:
			print "exception in listActivities"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)

	
		return {'operation' : 'listActivities','status':status}




	def selectActivity(self,username,activityName):
		"""
		selectActivity()
			string activity
	
		return: standard response header


		Note this will be a dummy method as well.
		"""

		
		sys.stderr.write("selectActivity <- %s\n"  %(activityName))
		status=1
#		try:
#			print "self.process",self.process
#			for activity in self.process.activities:
#				print activity.activityTitle
#				if activity.activityTitle == activityName:	
#					self.activity = activity
#					status=1
#		except:
#			print "exception in selectActivity"
#			exc_type, exc_value, exc_traceback = sys.exc_info()
#			traceback.print_tb(exc_traceback)

	
		return {'operation' : 'selectActivity','status':status,'json':json.dumps({})}



	def listActivitySteps(self,username,process,activity,brewlog):
		"""
		listActivitySteps()

		call openBrewlog() and selectActivity() first
		return: response header with steps required


		Note: changed to send process/activity on every call. and send brewlog


		"""

		sys.stderr.write("listActivitySteps %s/%s\n" %(process,activity))

		try:
			steps=[]
			stepNum=0
#			for step in self.activity.steps:
			#note we need to look for the process by numbe rnot name
			
			ourActivity =db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum > :3 AND stepName = :4 ",username,process,-1,activity).fetch(1)[0]


			ourSteps =db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND activityNum = :2 AND stepNum > :3 AND subStepNum = :4 AND brewlog = :5 ORDER BY stepNum",username, ourActivity.activityNum,-1,-1,brewlog)
			for step in ourSteps.fetch(4000):
				newstep = {}
				newstep['sortindex']=step.sortIndex	
				newstep['name'] = step.stepName
				newstep['complete'] = False

				if step.subStepsCompleted == True:
					newstep['complete']=True	
				else:
					newstep['complete']=False
#				if len(substeps) == 0 and thisStep.completed == True:	
#					newstep['complete'] = True 
#					newstep['dbg']="a"
#				elif len(substeps) > 0:
#					newstep['dbg']="b"
#					sumToComplete=0
#					numCompleted=0
#					for substep in substeps:
#						sumToComplete = sumToComplete +1
#						if substep.completed:	
#							numCompleted = numCompleted + 1
#						elif not substep.needToComplete:
#							numCompleted = numCompleted + 1
#	
#					if sumToComplete == numCompleted:	newstep['complete'] = True


				steps.append(newstep)
			sys.stderr.write("About to return a result\n")
			return {'operation':'listActivitySteps','status':1,'json' : json.dumps( {'result': steps } ) }
		except:
			sys.stderr.write("exception in listActivitySteps\n\n\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)

		return {'operation':'listActivitySteps','status':0}


	def openBrewlog(self,username,process,recipe,brewlog):
		"""
		openBrewlog()
			string process
			string recipe
			string brewlog

		note: sets process and recipe to those in the brew log
		return: standard response header


		Note: in cloud api this is a dummy method, but left for now
		"""
		sys.stderr.write("openBrewlog() <> %s/%s/%s\n" %(process,recipe,brewlog))
		
		status=1
#		try:
#			self.brewlogfilename= "brewlog/%s/%s/%s/%s" %(self.userid, re.compile("[^A-Za-z0-9]").sub('_',process), re.compile("[^A-Za-z0-9]").sub("_",recipe.lower()), re.compile("[^A-Za-z0-9]").sub('_',brewlog.lower()))
#			print self.brewlogfilename
#			o=open(self.brewlogfilename)
#			self.brewlog = pickle.loads( o.read() )
#			o.close()
#			self.process = self.brewlog.copyprocess
#			self.recipe = self.brewlog.copyrecipe
#			status=1
#		except:
#			print "exception in openbrewlog"
#			exc_type, exc_value, exc_traceback = sys.exc_info()
#			traceback.print_tb(exc_traceback)
#			for e in traceback.format_tb(exc_traceback):	print e
		return {'operation' : 'openBrewlog','status' :status,'json':json.dumps({})}

	def listProcesses(self):
		"""
		listProcesses()
		
		return: list with processes in resonse header
		"""
		try:
			print "listProcesses() -> "
			processList=[]
			for process in os.listdir( "process/%s/" %(self.userid) ):
				tmp = pickle.loads(open("process/%s/%s" %(self.userid,process)).read())
				processList.append( tmp.name )
			processList.sort()
			
			
			print "listProcesses() <- " %(processList)
			return {'operation' : 'listProcesses', 'status' : 1, 'json' : json.dumps( {'result': processList} ) }
		except:
			return {'operation' : 'listProcesses', 'status' : 0}


#Vcloudtask.execute("setFieldWidget",shrdPrefs.getString("brewlog","<brewlog"), shrdPrefs.getString("brewlog","<activity>"), stepid.toString(),fieldKey,fieldValue,index.toString() );
	def setFieldWidget(self,username,process,brewlog,activity,stepNum,fieldKey,fieldVal, guiId):
		"""
		saveFieldWidget
			integer: stepNum
			String: fieldKey
			String: fieldVal
			Integer: guiId 		<passed back transparently>
		"""

		sys.stderr.write("setFieldWidget %s %s %s %s %s %s %s\n" %(process,brewlog,activity,stepNum,fieldKey,fieldVal,guiId))
		ourActivity =db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum > :3 AND stepName = :4 ",username,process,-1,activity).fetch(1)[0]
		stepNum=int(stepNum)


		ourField=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum= :3 AND stepNum= :4 AND fieldKey = :5",username,brewlog,ourActivity.activityNum,stepNum,fieldKey).fetch(1)[0]
		ourField.fieldVal = fieldVal
		ourField.fieldTimestamp=int(time.time())
		ourField.put()

#		if not self.brewlog.notes.has_key( self.activity.steps[stepNum].stepid ):
#			self.brewlog.notes[self.activity.steps[stepNum].stepid] = {}
#
#
#		self.brewlog.notes[self.activity.steps[stepNum].stepid][ fieldKey ] = fieldVal
#	

		result={}
		result['value'] = fieldVal
		result['guiid'] = guiId

		if ourField.fieldWidget:
			result['value'] = self._widgets(username,process,brewlog,ourField.fieldKey)
			ourField=db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum= :3 AND stepNum= :4 AND fieldKey = :5",username,brewlog,ourActivity.activityNum,stepNum,fieldKey).fetch(1)[0]
			ourField.fieldVal = result['value']
			ourField.put()

#		if self.activity.steps[stepNum].widgets.has_key( fieldKey ):
#			result['value'] = self._widgets( self.activity.steps[stepNum].widgets[fieldKey], self.brewlog.notes[ self.activity.steps[stepNum].stepid ]  )
#			print "*"*(80)
#			self.brewlog.notes[self.activity.steps[stepNum].stepid][ fieldKey ] = result['value']
#			print "This is a widget with a result of ",result['value']
#		else:
#			print "Note a widget"
#	
#		self.saveBrewlog()
		#self.brewlog.save()

		return {'operation':'setFieldWidget','status':1,'json': json.dumps( {'result': result } ) }
			


	def _widgetData(self,username,brewlog,field):
		sys.stderr.write("widgetdata %s %s %s\n" %(username,brewlog,field))
		FIELD=field
		field =field.lower()
		
		ourData =db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3",username,brewlog,field).fetch(1)

		if not len(ourData):
			field=FIELD
			ourData =db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3",username,brewlog,field).fetch(1)

		if len(ourData):
			sys.stderr.write(" result from field data %s\n"  %(ourData[0].fieldVal))
			return ourData[0].fieldVal



		ourBrewlog =db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2 ",username,brewlog).fetch(1)[0]

		ourData =db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3",username,ourBrewlog.realrecipe,ourBrewlog.process).fetch(1)[0]
		
		if ourData.__dict__.has_key("_%s" %(field)):
			sys.stderr.write(" result from recipe stats %s\n"  %(ourData.__dict__["_%s" %(field)]))
			return ourData.__dict__["_%s" %(field)]



	def _widgets(self,username,process,brewlog,widget):
		sys.stderr.write("_widgets %s %s %s %s\n" %(username,process,brewlog,widget))
		ourWidget = db.GqlQuery("SELECT * FROM gWidgets WHERE owner = :1 AND process = :2 AND widgetName = :3",username,process,widget).fetch(1)[0]

		widgetType=ourWidget.widget		
		widgetData=ourWidget.widgetValues
#		(widgetType,widgetData) = widget

		if widgetType == "add2number":
			data0=float( self._widgetData(username,brewlog,widgetData[0]))		# gravity of main wort
			data1=float( self._widgetData(username,brewlog,widgetData[1]))		# gravity of topup
			sys.stderr.write("add2number %s %s \n" %(data0,data1))
			return "%s" %(data0+data1)
		if widgetType == "add2numbers":
			data0=float( self._widgetData(username,brewlog,widgetData[0]))		# gravity of main wort
			data1=float( self._widgetData(username,brewlog,widgetData[1]))		# gravity of topup
			sys.stderr.write("add2number %s %s \n" %(data0,data1))
			return "%s" %(data0+data1)
#
#
#					got here
#
			return float( self._widgetData(username,brewlog,data0) ) + float( self._widgetData(username,brewlog,data1))

		if widgetType == "gravityVolAdjustment":

			g=float( self._widgetData(username,brewlog,widgetData[0]))		# gravity of main wort
			h=float( self._widgetData(username,brewlog,widgetData[1]))		# gravity of topup
			v=float( self._widgetData(username,brewlog,widgetData[2]))	#vol1
			x=float( self._widgetData(username,brewlog,widgetData[3])) # gravity target
#			vol2=float( self._widgetData(username,brewlog,widgetData[3]))
			sys.stderr.write("grav/grav/vol/target %s/%s/%s/%s\n" %(g,h,v,x))				

			return "%.4f" %( -( (v*x)-(g*v) )/ (x-h) )


			return "%.4f" %(g1+g2)
		if widgetType == "combineMultipleGravity":
			grav1=float( self._widgetData(username,brewlog,widgetData[0]))
			grav2=float( self._widgetData(username,brewlog,widgetData[1]))
			vol1=float( self._widgetData(username,brewlog,widgetData[2]))
			vol2=float( self._widgetData(username,brewlog,widgetData[3]))
			sys.stderr.write("grav/grav/vol/vol %s/%s/%s/%s\n" %(grav1,grav2,vol1,vol2))				

			totalvol=vol1+vol2
			g1 = (vol1/totalvol) * grav1
			g2 = (vol2/totalvol) * grav2
			return "%.4f" %(g1+g2)
			
		if widgetType == "abvCalculation":
			og= float(self._widgetData(username,brewlog,widgetData[0]))
			sys.stderr.write( "do we have a fg??? %s\n" %(self._widgetData(username,brewlog,widgetData[1])))
			fg= float(self._widgetData(username,brewlog,widgetData[1]))
#			og=float(dataDict[widgetData[0]])
#			fg=float(dataDict[widgetData[1]])
		
			return "%.1f" %((og-fg)	 * 131)

		sys.stderr.write( "widget type _%s_\n" %(widgetType))
		if widgetType == "gravityTempAdjustment" or widgetType == " gravityTempAdjustment":
			intemp= float(self._widgetData(username,brewlog,widgetData[0]))
			gravity= float(self._widgetData(username,brewlog,widgetData[1]))
			answer=self.gravityTempAdjustment(intemp,gravity)

#			temp = ( intemp *1.8)+32
#			caltemp = 68
#			answer = gravity * (1.00130346 - 1.34722124E-4 * temp + 2.04052596E-6 * temp * temp - 2.32820948E-9 * temp * temp * temp) / (1.00130346 - 1.34722124E-4 * caltemp + 2.04052596E-6 * caltemp * caltemp - 2.32820948E-9 * caltemp * caltemp * caltemp)

			return "%.4f" %(answer)


		if widgetType == "inverseGravityTempAdjustment":
			intemp= float(self._widgetData(username,brewlog,widgetData[0]))
			gravity= float(self._widgetData(username,brewlog,widgetData[1]))
			answer=self.gravityTempAdjustment(intemp,gravity,-68)
			return "%.4f" %(answer)



		sys.stderr.write("widgetType %s unsupported\n" %(widgetType))
		return "unsupported"
				

	def saveComment(self,username,brewlog,process,activityName,stepNum,comment):
		"""
		saveComment
			integer:  stepNum
			String:		comment
		return standard response header
		"""

		sys.stderr.write("saveComment %s/%s/%s/%s\n" %(brewlog,process,activityName,stepNum))

		ourActivity =db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum > :3 AND stepName = :4 ",username,process,-1,activityName).fetch(1)[0]
		sumToComplete=0
		numCompleted=0
		stepNum=int(stepNum)
		#print "saveComment <- %s %s" %(stepNum,comment)

		
		#step = self.activity.steps[stepNum]
		existingField = db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND process = :3 AND activityNum = :4 AND stepNum = :5 AND fieldKey = :6", username,brewlog,process,ourActivity.activityNum,stepNum,'notepage').fetch(1)
		if len(existingField):
			existingField.delete()


		com = gField( owner=username,stepNum=stepNum,activityNum=ourActivity.activityNum)
		com.brewlog=brewlog
		com.recipe="we dont have this in saveComment()"	
		com.fieldKey="notepage"
		com.fieldVal= comment
		com.fieldTimestamp = int(time.time())
		com.put()	

#		print  "stepid", self.activity.steps[stepNum].stepid
#		if not self.brewlog.notes.has_key( self.activity.steps[stepNum].stepid ):
#			self.brewlog.notes[self.activity.steps[stepNum].stepid] = {}
			
#		print "setting notepage with id %s" %(self.activity.steps[stepNum].stepid)
#		self.brewlog.notes[self.activity.steps[stepNum].stepid]['notepage'] = comment

		# Note the web interface sometimes uses the stepid from a substep
#		for substep in step.substeps:
#			if self.brewlog.notes.has_key( substep.stepid ):
#				if self.brewlog.notes.has_key[substep.stepid].has_key("notepage"):
#					self.brewlog.notes.has_key[substep.stepid]['notepage'] =""
						

#		self.saveBrewlog()
		#self.brewlog.save()	
		return {'operation':'saveComment','status':1 ,'json':json.dumps({})}


#		return {'operation':'saveComment','status':0}




	def setStepComplete(self,username,brewlog,activityName,stepNum,complete):
		"""
		setStepComplete
			integer:  stepNum
			Boolean:  complete or not complete	
		return standard response header
		"""
		sys.stderr.write("setStepComplete %s/%s/%s/%s\n" %(brewlog,activityName,stepNum,complete))
		thisProcess = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]
		sys.stderr.write("thisProcess ... %s\n" %(thisProcess.process))
		thisActivity = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepName = :3 AND stepNum = :4",username,thisProcess.process, activityName,-1).fetch(1)[0]
		sys.stderr.write("thisActivity ... %s\n" %(thisActivity.activityNum))


		thisStep = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1)[0]
#		sumToComplete=0
#		numCompleted=0
		stepNum=int(stepNum)
#		step = self.activity.steps[stepNum]
		
		if complete == "1":
			lastCompleted=True
			thisStep.completed=True
			thisStep.subStepsCompleted=True
			thisStep.stepEndTime=int(time.time())
		else:
			lastCompleted=False
			thisStep.completed=False
			thisStep.subStepsCompleted=False
			thisStep.stepEndTime=0
		thisStep.put()


		result={}
		result['lastcomplete'] = lastCompleted
		result['stepid'] = "%s" %(stepNum)
		#self.brewlog.save()	

		return {'operation':'setStepComplete','status':1,'json': json.dumps( {'result': result } ) }




	def setSubStepComplete(self,username,brewlog,activityName,stepNum,subStepNum,completed):
		"""
		setSubStepComplete
			integer:  stepNum
			integer:  subStepNum
			Boolean:  complete or not complete	
		return standard response header with percentage for progress bar and lastcompletestatus
		"""
		sys.stderr.write("setSubStepComplete %s/%s/%s/%s/%s\n" %(brewlog,activityName,stepNum,subStepNum,completed))

		thisProcess = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]
		sys.stderr.write("thisProcess ... %s\n" %(thisProcess.process))
		thisActivity = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepName = :3 AND stepNum = :4",username,thisProcess.process, activityName,-1).fetch(1)[0]
		sys.stderr.write("thisActivity ... %s\n" %(thisActivity.activityNum))

		


		thisStep = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),int(subStepNum)).fetch(1)[0]
		if completed == "1":
			thisStep.completed=True
			thisStep.stepEndTime=int(time.time())
			lastCompleted=True
		else:
			lastCompleted=False
			thisStep.completed=False
		thisStep.put()

		theseSteps = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum > :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1000)

#		stepNum = int(stepNum)
#		subStepNum = int(subStepNum)
		sumToComplete=0
		numCompleted=0

#		step = self.activity.steps[stepNum]
#		substep = step.substeps[subStepNum]
		
#		if completed == "1":
#			lastCompleted=True
#			substep.completed=1
#			substep.endTime=time.time()
#		else:
#			lastCompleted=False
#			substep.completed=None
#			substep.endTime=0

		for substep in theseSteps:
			sumToComplete = sumToComplete +1
			if substep.completed:	
				numCompleted = numCompleted + 1
			elif substep.needToComplete == False:
				numCompleted = numCompleted + 1

		sys.stderr.write("sumToComplete %s\n" %(sumToComplete))
		sys.stderr.write("numCompleted %s\n" %(numCompleted))
		if sumToComplete == numCompleted:
			subStepCompletes = 100

			theParentStep= db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1)[0]
			theParentStep.subStepsCompleted=True
			theParentStep.put()



		elif sumToComplete > 0:
			subStepCompletes = (numCompleted/sumToComplete) * 100
			theParentStep= db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1)[0]
			theParentStep.subStepsCompleted=False
			theParentStep.put()

		else:
			subStepCompletes = 0	
		
		result={}
		result['progress'] = int(subStepCompletes)
		result['lastcomplete'] = lastCompleted
		result['stepid'] = "%s" %(stepNum)


#		self.saveBrewlog()
#		self.brewlog.save()	
		return {'operation':'setSubStepComplete','status':1,'json': json.dumps( {'result': result } ) }

		return {'operation':'setSubStepComplete','status':0}




	def _gather(self,username,activityNum,brewlog,step,process,ingredientTypes=['fermentables','hops','yeast','misc','None'],subFilter=None,doIngredients=1,doEquipment=1,doConsumables=1):
		"""
		This internal operation will create the gath in activitys
		"""

		ingredients={}
		ingredients['hops']={}
		ingredients['fermentables']={}
		ingredients['yeast']={}
		ingredients['None']={}
		ingredients['misc']={}
		ingredients['other']={}



		substeps=[]

		for ingredientType in ingredientTypes:	
#			sys.stderr.write("SELECT * FROM gBrewlogStock WHERE owner = %s AND brewlog=%s AND >>> NOT SURE WHAT THIS WAS HERE FOR  actiityNum = %s ORDER BY stock\n" %(username,brewlog,activityNum))
			#ourIngredients=db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog= :2 AND activityNum = :3 ORDER BY stock",username,brewlog,activityNum).fetch(40000)
			ourIngredients=db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog= :2 AND storecategory = :3 ORDER BY stock",username,brewlog,ingredientType).fetch(40000)


			if len(ourIngredients) > 0:
#				substeps.append({})
#				substeps[-1]['needtocomplete']=False
#				substeps[-1]['complete']=True
#				substeps[-1]['completeDate']=time.ctime(time.time())	
#				substeps[-1]['text']="No Ingredients required"
#			else:
				substeps.append({})
				substeps[-1]['needtocomplete']=False
				substeps[-1]['complete']=True
				substeps[-1]['completeDate']=time.ctime(time.time())	
				substeps[-1]['text']="Gather %s Ingredients" %(len(ourIngredients))

				
				sys.stderr.write("%s\n" %(ingredients))
				for ingredient in ourIngredients:
					if not ingredients[ "%s" %(ingredient.storecategory) ].has_key( ingredient.stock ):
						ingredients[ "%s" %(ingredient.storecategory) ][ ingredient.stock ] = []
					ingredients[ "%s" %(ingredient.storecategory) ][ ingredient.stock ].append(ingredient)
				
				sys.stderr.write("%s\n" %(ingredients))

				for ingredientType in ingredientTypes:
					for ingredient in ingredients[ingredientType]:
						stocktag=""
						for stock in ingredients[ingredientType][ingredient]:
#							stocktag=stocktag+" - %s%s of %s\n" %(stock.qty,UNIT",stock.stocktag)
							stocktag=stocktag+" - %s%s of %s\n" %(stock.qty,stock.unit,stock.stocktag)

						substeps.append({})
						substeps[-1]['needtocomplete']=True
						substeps[-1]['complete']=False
						substeps[-1]['completeDate']=0
						substeps[-1]['text']="%s\n%s" %(stock.stock,stocktag)



		"""	
		if len(activity.consumables) == 0:
			step.newSubStep( ("No Consumables Required", {}) )
		else:
			step.newSubStep( ( "Gather %s Consumables" %( len(activity.consumables)  ), {} ))
			for (item,qty) in activity.consumables:
				step.newSubStep( ( "  %.1f %s %s"  %(qty,item.unit,item.name) ,{'complete':1} )  )

		"""


		if doEquipment:
			ourEquipment = db.GqlQuery("SELECT * FROM gEquipment WHERE owner = :1 AND process = :2 AND activityNum = :3",username,process,activityNum).fetch(40344)
			
			if len(ourEquipment) == 0:
				substeps.append({})
				substeps[-1]['needtocomplete']=False
				substeps[-1]['complete']=True
				substeps[-1]['completeDate']=time.ctime(time.time())	
				substeps[-1]['text']="No Equipment required"
			else:
				substeps.append({})
				substeps[-1]['needtocomplete']=False
				substeps[-1]['complete']=True
				substeps[-1]['completeDate']=time.ctime(time.time())	
				substeps[-1]['text']="Gather %s Equipment" %(len(ourEquipment))

				for equipment in ourEquipment:
					substeps.append({})
					substeps[-1]['needtocomplete']=True
					substeps[-1]['complete']=False
					substeps[-1]['completeDate']=0
					substeps[-1]['text']="%s" %(equipment.name)



		return substeps

				
	def _newVariableSub(self,username,toReplace,activityNum,stepNum,stepText,recipeName,process,begin="",finish=""):
#		sys.stderr.write("\nnewVariableSub %s/%s/%s/%s/%s/%s/%s\n" %(username,toReplace,activityNum,stepNum,stepText,recipeName,process))

		stat = db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner= :1 AND recipe = :2 AND process = :3",username,recipeName,process).fetch(1)[0]

#		sys.stderr.write("newvariableSub stat %s\n" %(stat))

		for tr in toReplace:
			if not stat.__dict__.has_key("_%s" %(tr)):
				val="?"
			else:
				val = stat.__dict__["_%s" %(tr)]
#			sys.stderr.write("\t%s\n" %(val))

			val="%s%s%s" %(begin,val,finish)
			stepText=re.compile("\.\.\.%s\.\.\." %(tr)).sub("%s" %(val),stepText)
			



		return stepText


		





	def getStepDetail(self,username,process,activityName,brewlog,stepNum,recipeName):
		"""
		getStepDetail()
			integer:  stepNum
			
		return data in response header
		"""
		sys.stderr.write("getStepDetail %s/%s/%s/%s/%s" %(process,activityName,brewlog,stepNum,recipeName))
		ourActivity =db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum > :3 AND stepName = :4 ",username,process,-1,activityName).fetch(1)[0]

		stepNum = int(stepNum)


		sys.stderr.write("username/process/ourActivity/stepNum=%s/%s/%s/%s\n" %(username,process,ourActivity.activityNum,stepNum))
		theStep =db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,process,ourActivity.activityNum,int(stepNum),-1).fetch(1)[0]

		ourStep =db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog= :2 AND activityNum = :3 AND stepNum = :4  AND subStepNum = :5",username,brewlog,ourActivity.activityNum,stepNum,-1).fetch(1)[0]

		try:
			newStep={}
			sys.stderr.write("%s\n" %(process))

			ourCompiles = db.GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,process,ourActivity.activityNum,stepNum).fetch(1)
			if len(ourCompiles) < 1:
				ouc = []
			else:
				ouc =ourCompiles[0].toReplace
		
#			step = self.activity.steps[stepNum]	
#			step.recipe=self.recipe
			sys.stderr.write( "step auto??? %s\n "%(theStep.auto))
			newStep['title'] = theStep.stepName
			newStep['stepNum'] = stepNum
#			newStep['text'] = theStep.text		## TODO: variabl esub
			newStep['text']= self._newVariableSub(username,ouc,"","",theStep.text,recipeName,process)
			newStep['img'] = theStep.img
			if ourStep.completed:
				newStep['complete'] = True
				newStep['completeDate'] = time.ctime( ourStep.stepEndTime )
			else:
				newStep['complete'] = False


			ourSubSteps =db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog= :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum > :5",username,brewlog,ourActivity.activityNum,stepNum,-1).fetch(545551)

			newStep['substepnumber'] = len(ourSubSteps)
			newStep['substeps']=[]



			# looking to deprecate this out of the processes nowo
			# these bits of processes should be deprectated as they do not support
			# proper completion of the steps.
			
			# Instead when we resetBrewlog/addStock to the brewlog we will
			# build the proper steps inline
			if theStep.auto == "gather" or theStep.auto == "gather2" or theStep.auto == "gather3" or theStep.auto == "gather4":
				newStep['substeps'] = self._gather(username,ourActivity.activityNum, brewlog,stepNum,process)


			for substep in ourSubSteps:
				newStep['substeps'].append({})

				newStep['substeps'][-1]['needtocomplete'] = substep.needToComplete
				if not substep.needToComplete:
					newStep['substeps'][-1]['needtocomplete']=False
				if substep.completed:
					newStep['substeps'][-1]['complete'] = True
					newStep['substeps'][-1]['completeDate'] = time.ctime( substep.stepEndTime )
				else:
					newStep['substeps'][-1]['complete'] = False

					### TODO variable sub
				newStep['substeps'][-1]['text']= self._newVariableSub(username,ouc,ourActivity.activityNum,stepNum,substep.stepName,recipeName,process)



			sumToComplete=0
			numCompleted=0
			for substep in ourSubSteps:
				sumToComplete = sumToComplete +1
				if substep.completed:	
					numCompleted = numCompleted + 1
				elif not substep.needToComplete:
					numCompleted = numCompleted + 1
			if sumToComplete > 0:
				newStep['substepcomplete'] = (numCompleted/sumToComplete) * 100
			else:
				newStep['substepcomplete']=0	

			if theStep.attention:
				newStep['warning'] = theStep.attention
			else:
				newStep['warning'] = ""
	

			newStep['commentsTimestamp']=""

			comments=""
		
		
			fieldValues={}
#			fields=step.fields


			ourFields =db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog= :2 AND activityNum = :3 AND stepNum = :4",username,brewlog,ourActivity.activityNum,stepNum).fetch(545551)
			for field in ourFields:
#			if self.brewlog.notes.has_key(step.stepid):
#				for fieldKey in self.brewlog.notes[step.stepid]:
				if field.fieldKey == "notepage":
					comments= field.fieldVal+"\n"
					newStep['commentsTimestamp']=time.ctime( field.fieldTimestamp )
#				else:
					# this will get stitched in later
#					fieldValues[field.fieldKey] = field.fieldVal
						# actually not used??

			# Note the web interface sometimes uses the stepid from a substep
			# this should be catered for in the stitch togeth.
#			for substep in ourSubSteps:
#				if self.brewlog.notes.has_key(substep.stepid):
#					for fieldKey in self.brewlog.notes[substep.stepid]:
#						if fieldKey == "notepage":
#							comments=self.brewlog.notes[substep.stepid]['notepage']+"\n"
#						else:
#							fields[fieldKey] = self.brewlog.notes[substep.stepid][fieldKey]
			newStep['comments'] = comments

			# won't really use the widgets bit				
			# lets call this out if we do use it or not
#			if len(step.widgets):
#				newStep['widgets']=True
#			else:
#				newStep['widgets']=False
			newStep['widgets']=False


			# if it#s a widget add the detail in the fields
			newfields=[]	
			# 
			for field in ourFields:
				if field.fieldKey != "notepage":
					if field.fieldWidget:
						#label,???,value,widgetName
						if field.fieldVal:
							newfields.append( (field.fieldKey,field.fieldKey,field.fieldVal,field.fieldWidget) )
						else:
							newfields.append( (field.fieldKey,field.fieldKey,"",field.fieldWidget) )
						newStep['widgets']=True
					else:
						if field.fieldVal:
							newfields.append( (field.fieldKey,field.fieldKey,field.fieldVal,"") )
						else:
							newfields.append( (field.fieldKey,field.fieldKey,"","") )
			"""
				# want to do more before activating this
			for field in ourFields:
#				if step.widgets.has_key( field[1] ):
				if field.fieldWidget:
#					(widgetName,widgetData) = step.widgets[field[1]]
#					(a,b,c)=field
#					if fieldValues.has_key( b ):	c = fieldValues[b]
					newfields.append( (a,b,c,widgetName) )	
					newStep['widgets']=True
				else:
					(a,b,c)=field
					if fieldValues.has_key( b ):	c = fieldValues[b]
					newfields.append( (a,b,c,""))

			"""
			newStep['fields'] = newfields
			newStep['process']=process
			sys.stderr.write("Img: %s\n" %( newStep['img']))
			return {'operation':'getStepDetail','status':1,'json':json.dumps( {'result' : newStep} ) }
		except:	
			print "exception in selectProcess"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)
			for e in traceback.format_tb(exc_traceback):	print e
		
		return {'operation':'getStepDetail','status':0}



	def listProcessImages(self,username,process):
		"""
		listProcessImages()
			string: process name

		return: list images used in a response header
		"""
		sys.stderr.write("listProcessImages <- %s\n" %(process))
		try:
			tmpimages={}
			ourImages = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2",username,process)
			for image in ourImages.fetch(4555):
				for img in image.img:
					tmpimages[img]=1
#			tmpprocess = pickle.loads(open("process/%s/%s" %(self.userid,process)).read())
#			for activity in tmpprocess.activities:
#'				for step in activity.steps:	
#					for img in step.img:
#						tmpimages[img]=1
			images=[]
			for img in tmpimages:		
				images.append(img)

			status =1

			return {'operation' : 'listProcessImages', 'status':1,'json' : json.dumps( {'result': images } ) }
		
		except:
			return {'operation' : 'listProcessImages', 'status':0}

	def selectProcess(self,processName):
		"""
		selectProcess()
			string name of process as per listProcesses
		
		return: standard response
		"""
		print "selectProcess() -> %s" %(processName)
		status=0
		try:
			o=open("process/%s/%s" %(self.userid,processName))
			self.process = pickle.loads( o.read() )
			o.close()
			status=1
		except:	
			print "exception in selectProcess"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)
			for e in traceback.format_tb(exc_traceback):	print e
		return {'operation':'selectProcess','status':status}



	def setMashEfficiency(self,username,recipeName,efficiency,doRecalculate="1"):
		"""
		setMashEfficiency()
			integer efficiency in percentage (e.g. 67)
			this assumes the input might not be as clean as ideal

		return: standard response
		"""
		sys.stderr.write("setMashEfficiency() -> %s/%s\n" %(recipeName,efficiency))
		status=0
		try:

			efficiency=int( re.compile("[^0-9]").sub('',efficiency))
			sys.stderr.write("updated efficiency to %s\n" %(efficiency))
			ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.mash_efficiency=float(efficiency)
				if doRecalculate == "0":	recipe.calculationOutstanding=True
				recipe.put()

			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)

			status=1
			result={}
			result['stats']={}
			result['stats']['mash_efficiency']=recipe.mash_efficiency
			return {'operation':'setMashEfficiency','status':status,'json':json.dumps(result) }
		except:
			sys.stderr.write("setMashEfficiency() Exception\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s\n" %(e))
			pass
		
		return {'operation':'setMashEfficiency','status':status}


	def findStock(self):
		"""
		findStock()
		
		return: stock details in standard response header
		"""
		print "findStock() ->"
		status=0
		try:
			result=self.stores.jsonStockAndPrice( self.recipe )
			return {'operation' : 'findStock', 'status' : 1, 'json' : json.dumps( {"result": result  } ) }

		except:
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
#			return {'operation':'findStock','status':status,'exception':format_tb(exc_traceback) }

		return {'operation':'findStock','status':status}

		

	def resetBrewlog(self,username,recipe,brewlog):
		"""
		a wrapper just for the android app
		"""

		# if we have any dummy brewlog get rid of it		
		#addStockToBrewlog(username,brewlog,recipeName=recipe,process=process,checkStock=1)
		sys.stderr.write("resetBrewlog %s/%s\n" %(recipe,brewlog))

	
		try:
			result={}



			#
			# check if the brewlog already exists
			#
			existingBrewlog = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)
#			if not len(existingBrewlog):
##				return {'operation' : 'resetBrewlog', 'status' : -3, 'json' : json.dumps( { } ) }
			process = existingBrewlog[0].process




			#
			# RESET THE BREWLOG
			#
			self.startNewBrewlog(username,brewlog,recipe,process,reset=1)

		
			# reset the stock on the brewlog
			self.addStockToBrewlog(username,brewlog,recipeName=recipe,process=process,checkStock=0,reset=1)
		

			
			# update RecipeStats with our new stock details
			ourData =db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3",username,recipe,process).fetch(1)[0]
			ourData.polypinqty = float( self.total_polypins)
			ourData.minikegqty = float( self.total_kegs)
			ourData.bottles_required=float(self.total_bottles)
			ourData.num_crown_caps=float(self.total_bottles+5)
			ourData.primingsugartotal=float(self.priming_sugar_reqd)
			ourData.primingwater = float((self.priming_sugar_reqd*15)-self.priming_sugar_reqd)
			ourData.priming_sugar_qty=float(15)
		
			#
			# now compile the recipe/brewlog
			#	
			self.compile(username,recipe,brewlog)
			
			sys.stderr.write("compile of resetBrewlog done\n")
			result={}

			return {'operation' : 'resetBrewlog', 'status' : 1, 'json' : json.dumps( result   ) }

		except:
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
			return {'operation':'resetBrewlog','status': -6,'exception':'exception unknown what though' }





	def createBrewlogWrapper(self,username,recipe,brewlog,process):
		"""
		a wrapper just for the android app
		"""

		# if we have any dummy brewlog get rid of it		
		#addStockToBrewlog(username,brewlog,recipeName=recipe,process=process,checkStock=1)


	
		try:
			result={}



			#
			# check if the brewlog already exists
			#
			existingBrewlog = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)
			if len(existingBrewlog):
				return {'operation' : 'createBrewlogWrapper', 'status' : -3, 'json' : json.dumps( { } ) }



			#
			# check if we have stock
			#
			(cost_result,stock_result) = self.checkStockAndPrice(username,recipe,process, True)
			result['stock']=stock_result
			result['cost']=cost_result


			if len(result['stock']['__stockrequirements__']) > 0:
				result['stock_status']=False
				result['out_of_stock']=True	
				result['out_of_date_stock']=False
				return {'operation' : 'createBrewlogWrapper', 'status' : 2, 'json' : json.dumps( {"result": result  } ) }

	

			#
			# check if stock is out of stock
			#
			toclear = self.listClearanceStock(username)
			if (toclear['__overthreshold__'] > 0 or toclear['__earlythreshold__'] > 0):
				result['stock_status']=False
				result['out_of_stock']=False
				result['out_of_date_stock']=True
				result['oldstock'] = toclear['__oldstock__']
				result['oldstockindex'] = toclear['__oldstockindex__']
				sys.stderr.write("Out of Date Stock")
				sys.stderr.write( "Early %s\n" %(toclear['__earlythreshold__']))
				sys.stderr.write( "Over %s\n" %(toclear['__overthreshold__']))
				sys.stderr.write( "  %s\n" %(toclear))
				return {'operation' : 'createBrewlogWrapper', 'status' : 3, 'json' : json.dumps( {"result": result } ) }

			

			#
			# start new brewlog
			#
			self.startNewBrewlog(username,brewlog,recipe,process)

			
			#
			# add new brewlog stock into it
			#
			self.addStockToBrewlog(username,brewlog)


			#
			# now return the brewlogs again
			#
			resultX=self.listBrewlogsByRecipe(username,recipe,True)
		


			#
			# now compile the recipe/brewlog
			#	
			self.compile(username,recipe,brewlog)
			
			sys.stderr.write("compile of createBrewlogWrapper done\n")

			result={}
			result['result'] = resultX['result']		# list of brewlogs
			result['result2'] = resultX['result2']		# list of recipes
			result['stock_status']=True

			return {'operation' : 'createBrewlogWrapper', 'status' : 1, 'json' : json.dumps( result   ) }

		except:
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
			return {'operation':'createBrewlogWrapper','status': -6,'exception':format_tb(exc_traceback) }





	def addStockToBrewlog(self,username,brewlog,checkStock=0,recipeName=None,process=None,reset=0):
		"""
		takeStock()
			Takes stock for the current recipe and associates it with the active brewlog

			updated to do a check and take
		
		return: standard json activity
		"""

		sys.stderr.write("addStockToBrewlog %s\n" %(brewlog))
		status=0
		try:

			if not reset:
				if not checkStock:
					existingBrewlog = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)
					if len(existingBrewlog) < 1:
						return {'operation' : 'addStockToBrewlog','status':-1}

					recipeName = existingBrewlog[0].recipe
					process = existingBrewlog[0].process
					sys.stderr.write("username %s/recipeName %s/process %s\n" %(username,recipeName,existingBrewlog[0].process))



				# workaround for now
				# hopAddAt -1 represents the total of this hops and isn't a real hop
				# we delete it here and re create based on the >0 hopAddAts
				ourRecipeIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 and hopAddAt <= :4",username,recipeName,"hops",0.0).fetch(400)
				for ori in ourRecipeIngredients:	ori.delete()
				HOPSUMMARY={}
				ourRecipeIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 and hopAddAt > :4",username,recipeName,"hops",0.0).fetch(400)
				for ori in ourRecipeIngredients:
					if not HOPSUMMARY.has_key(ori.ingredient):	HOPSUMMARY[ ori.ingredient ] =0
					HOPSUMMARY[ ori.ingredient ] = HOPSUMMARY[ ori.ingredient ] + ori.qty
				for hs in HOPSUMMARY:
					ing = gIngredients(owner=username)
					ing.recipename=recipeName
					ing.qty = HOPSUMMARY[hs]
					ing.ingredient=hs	
					ing.ingredientType='hops'
					ing.hopAddAt=float(-1)
					ing.processIngredient = False
					ing.put()
			
				ourstock=self.takeStock( username,recipeName,existingBrewlog[0].process )
		
				# not have an artifical early return  in takeStock
				# ~line 3415 in _stockBestBefore will adjust qty of the ingredients 
				# takeStock will adjust qty of priming sugar etc
	#			print "\n"
	#			print ourstock
		
	#			for resu in db.GqlQuery("SELECT * FROM gBrewlogStock WHERE brewlog= :1",brewlog).fetch(324234):
	#				resu.delete()

				for storeType in ourstock:
					for a in ourstock[storeType]:
						for (pcnt,qty,stocktag,name,purchaseObj) in  ourstock[storeType][a]:

							newstock=gBrewlogStock(	owner=username,brewlog=brewlog,recipe=recipeName)
							newstock.qty=qty
							newstock.stock=name
							newstock.cost=purchaseObj.purchaseCost * qty
							newstock.storecategory=purchaseObj.storecategory
							newstock.unit=purchaseObj.unit
	#						newstcok.subcategor
							newstock.stocktag=stocktag
							newstock.put()




			"""
			Note: this is a better approach to building in stock into the process because it then generates real stock items.

			allocation of stock is limited to what we have above
			what we have below is suitable for creating a brewlog and resetting a brewlog

			NOV2012 need to rework what we have below so that it pulls from teh database not memory.
			"""
			
			ssNum=50000



			# add a gBrewlogStep details
			sys.stderr.write("   - gather than grain\n")
			sys.stderr.write("finding gProcess gather steps for %s %s \n" %(username,process))
			ourSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gatherthegrain").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=tmpSSNUM[0].subStepNum

#				sys.stderr.write("  gatherstep %s" %(gatherStep.activityNum,gatherStep.stepNum))
#				for storeType in ourstock:
#					for a in ourstock[storeType]:
#						for (pcnt,qty,stocktag,name,purchaseObj) in  ourstock[storeType][a]:
#							sys.stderr.write("acti %s step %s substep %s  madeup %s\n" %(gatherStep.activityNum, gatherStep.stepNum,gatherStep.subStepNum,ssNum))
				ourIngs = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND storecategory = :3",username,brewlog,'fermentables').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					sys.stderr.write("%s\n" %(purchaseObj))
					sys.stderr.write("%s\n" %(purchaseObj.qty))
					sys.stderr.write("%s\n" %(purchaseObj.unit))
					sys.stderr.write("%s\n" %(purchaseObj.stock))
					sys.stderr.write("%s\n" %(purchaseObj.stocktag))
					x.stepName=" %.2f %s of %s (%s)" %(purchaseObj.qty,purchaseObj.unit,purchaseObj.stock,purchaseObj.stocktag)
					x.completed=False
					x.stepStartTime=0
					x.stepEndTime=0
					x.needToComplete=True
					x.subStepsCompleted=False
					x.compileStep=gatherStep.compileStep
					x.put()



#
			# add a gBrewlogStep details
			sys.stderr.write("   - gather than bottles\n")
			sys.stderr.write("finding gProcess gather steps for %s %s \n" %(username,process))
			ourSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gather2").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=tmpSSNUM[0].subStepNum
				ourIngs = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,'bottle').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					sys.stderr.write("%s\n" %(purchaseObj))
					sys.stderr.write("%s\n" %(purchaseObj.qty))
					sys.stderr.write("%s\n" %(purchaseObj.unit))
					sys.stderr.write("%s\n" %(purchaseObj.stock))
					sys.stderr.write("%s\n" %(purchaseObj.stocktag))
					x.stepName=" %.2f %s of %s (%s)" %(purchaseObj.qty,purchaseObj.unit,purchaseObj.stock,purchaseObj.stocktag)
					x.completed=False
					x.stepStartTime=0
					x.stepEndTime=0
					x.needToComplete=True
					x.subStepsCompleted=False
					x.compileStep=gatherStep.compileStep
					x.put()


			# add a gBrewlogStep details
			sys.stderr.write("   - gather than minikegs\n")
			sys.stderr.write("finding gProcess gather steps for %s %s \n" %(username,process))
			ourSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gather3").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=tmpSSNUM[0].subStepNum
				ourIngs = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,'keg').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					sys.stderr.write("%s\n" %(purchaseObj))
					sys.stderr.write("%s\n" %(purchaseObj.qty))
					sys.stderr.write("%s\n" %(purchaseObj.unit))
					sys.stderr.write("%s\n" %(purchaseObj.stock))
					sys.stderr.write("%s\n" %(purchaseObj.stocktag))
					x.stepName=" %.2f %s of %s (%s)" %(purchaseObj.qty,purchaseObj.unit,purchaseObj.stock,purchaseObj.stocktag)
					x.completed=False
					x.stepStartTime=0
					x.stepEndTime=0
					x.needToComplete=True
					x.subStepsCompleted=False
					x.compileStep=gatherStep.compileStep
					x.put()
#i

			# add a gBrewlogStep details
			sys.stderr.write("   - gather than polypins\n")
			sys.stderr.write("finding gProcess gather steps for %s %s \n" %(username,process))
			ourSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gather4").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=tmpSSNUM[0].subStepNum
				ourIngs = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,'polypin').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					sys.stderr.write("%s\n" %(purchaseObj))
					sys.stderr.write("%s\n" %(purchaseObj.qty))
					sys.stderr.write("%s\n" %(purchaseObj.unit))
					sys.stderr.write("%s\n" %(purchaseObj.stock))
					sys.stderr.write("%s\n" %(purchaseObj.stocktag))
					x.stepName=" %.2f %s of %s (%s)" %(purchaseObj.qty,purchaseObj.unit,purchaseObj.stock,purchaseObj.stocktag)
					x.completed=False
					x.stepStartTime=0
					x.stepEndTime=0
					x.needToComplete=True
					x.subStepsCompleted=False
					x.compileStep=gatherStep.compileStep
					x.put()
#
#
			if reset:
				return # early

			if len(ourstock) < 1:
				return {'operation':'addStockToBrewlog','status':-3}		# out of stock or out of date stock

			# need to add our stock into the databser



			result = {}
			for stockType in ourstock:
				result[stockType] = {}
				for stockItem in ourstock[stockType]:
					result[stockType][stockItem]=[]
					for (a,b,c,d,e) in ourstock[stockType][stockItem]:
						substock={}
						substock['percentage']=a
						substock['qty']=b
						substock['barcode']=c
						substock['item']=e.storeitem
#						print stockItem,ourstock[stockType][stockItem]
						result[stockType][stockItem].append( substock)


			return {'operation':'addStockToBrewlog','status' :1,'json' : json.dumps( {"result": result})}
		except:	
			sys.stderr.write("EXCEPTION in addStockToBrewlog\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write(e)
			return {'operation':'addStockToBrewlog','status':status }

		return {'operation':'addStockToBrewlog','status':status}
		
	
	def listStoreCategories(self,username):
		"""
		listStoreCategories()
			Provides a list of the categories we can use
		
		return: standard json wiht categories
		"""

		sys.stderr.write("listStoreCategoriesk() <>\n")
		result=['Fermentables','Hops','Yeast','Consumables','Other']
		return {'operation':'listStoreCategories','status' :1,'json' : json.dumps( {"result": result})}


	def listStoreItems(self,username,category):
		"""
		listStoreItems()
			Provides a list of stock in the store

			string: category as per listStoreCategories

		return: standard json with simple list of stock itmes
		"""
		sys.stderr.write("listStoreItems() <- %s\n" %(category))
		
		try:
			items = {}

			if category == "Consumables":	category="consumable"
			if category == "Other":	category="misc"

			ourPurchases = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storecategory = :2 AND qty > 0.003 ", username ,category.lower())
			for purchase in ourPurchases.fetch(34840):
				if not items.has_key( purchase.storeitem ):
					items[ purchase.storeitem ] = {}
					items[ purchase.storeitem ]['cost'] = 0
					items[ purchase.storeitem ]['totalqty'] = 0
					items[ purchase.storeitem ]['name'] = purchase.storeitem
					items[ purchase.storeitem ]['category'] = category
					items[ purchase.storeitem ]['unit'] = purchase.unit

				items[ purchase.storeitem ]['cost'] = items[ purchase.storeitem ]['cost'] + ( purchase.purchaseCost * purchase.qty )
				items[ purchase.storeitem ]['totalqty'] = items[ purchase.storeitem ]['totalqty'] + purchase.qty


			stockitems=[]
			sorder=[]
			for i in items:	sorder.append( items[i]['name'] )	
			sorder.sort()
			for s in sorder:
				stockitems.append( items[s] )

			result = {'category' : category, 'items':stockitems}
			sys.stderr.write("about to return a result of %s\n\n" %(result))
			sys.stderr.write("listStoreItems() > status=1\n")
			return {'operation':'listStoreItems','status' :1,'json' : json.dumps( {"result": result})}
		except:

			sys.stderr.write("listStoreItems() > status=0\n")
			return {'operation':'listStoreItems','status' :0  }



	def _getStoreAndData(self,category):
		store=None
		if category=="Fermentables":	store=self.stores.Fermentables
		if category=="Hops":	store=self.stores.Hops
		if category=="Yeast":	store=self.stores.Yeast
		if category=="Consumables":	store=self.stores.Consumable
		if category=="Other":	store=self.stores.Misc

		data=None
		if category=="Fermentables":	data=self.data.getFermentable
		if category=="Hops":	data=self.data.getHop
		if category=="Yeast":	data=self.data.getYeast
		if category=="Misc":	data=self.data.getMisc
		if category=="Consumable":	data=self.data.getConsumable
		return (store,data)
	




	
	def getStockFullDetails(self,username,category,itemName):
		"""
		getStockFullDetails()
			Provides a list of stock in the store

			string: category as per listStoreCategories
			string: item as per listStoreItems

		return: standard json with details of the stock item
		"""
		#print "getStockFullDetails() <- %s,%s" %(category,itemName)
		theitem={}
		theitem['category'] = category
		theitem['purchases']=[]
		if category == "Consumables":	category="consumable"
		if category == "Other":	category="misc"

		ourPurchases = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storecategory = :2 AND storeitem = :3 AND qty > 0.0003", username ,category.lower(),itemName)


		purchasedQty=0
		purchasedCost=0
		for purchase in ourPurchases.fetch(34840):
			if purchase.qty > 0:
				purchasedQty = purchasedQty + purchase.qty
				purchasedCost = purchasedCost + (purchase.purchaseCost * purchase.qty)

			theitem['name'] =purchase.storeitem
			if category == "Hops":
				theitem['hopalpha']=-1
			theitem['purchases'].append( {} )
			theitem['purchases'][-1]['purchasedQty'] = purchase.qty
			theitem['purchases'][-1]['purchasedBestBefore'] = purchase.bestBeforeEnd
			theitem['purchases'][-1]['purchasedStockTag'] = purchase.stocktag
			theitem['purchases'][-1]['purchasedPurchased'] = purchase.purchaseDate
			theitem['purchases'][-1]['purchasedCost'] = purchase.purchaseCost * purchase.qty
			theitem['purchases'][-1]['purchasedSupplier'] = purchase.supplier
			if category == "Hops":
				theitem['purchases'][-1]['hopalpha'] =purchase.hopActualAlpha
				if purchase.hopActualAlpha == 0:	
					theitem['purchases'][-1]['hopalpha'] = theitem['hopalpha']
		theitem['cost']=purchasedCost
		theitem['unit'] = purchase.unit
		theitem['totalqty'] = purchasedQty
		theitem['description']="{description}"
		result=theitem
		"""	
		#(store,data)=self._getStoreAndData(category)
		if store and data:
			theitem={}
			for storeObject in store:
				if storeObject.name == itemName:
					purchasedQty=0
					purchasedCost=0
					for purchasedItem in store[storeObject]:
						if purchasedItem.qty > 0:
							purchasedQty = purchasedQty + purchasedItem.qty
							purchasedCost = purchasedCost + (purchasedItem.price * purchasedItem.qty)

					theitem['name'] =storeObject.name
					theitem['purchases'] = []
					theitem['cost']=purchasedCost
					itemObject = data( storeObject.name )
					if not itemObject.description:
						theitem['description']=""
					else:
						theitem['description'] = itemObject.description
					if category == "Hops":
						theitem['hopalpha']=itemObject.alpha
					theitem['unit'] = itemObject.unit
					theitem['totalqty'] = purchasedQty
					theitem['category'] = category
					theitem['purchases'] = []
					for purchasedItem in store[storeObject]:
						if purchasedItem.qty > 0:
							theitem['purchases'].append( {} )
							theitem['purchases'][-1]['purchasedQty'] = purchasedItem.qty
							theitem['purchases'][-1]['purchasedBestBefore'] = purchasedItem.best_before_date
							theitem['purchases'][-1]['purchasedStockTag'] = purchasedItem.stockTag
							theitem['purchases'][-1]['purchasedPurchased'] = purchasedItem.purchase_date
							theitem['purchases'][-1]['purchasedCost'] = purchasedItem.price * purchasedItem.qty
							theitem['purchases'][-1]['purchasedSupplier'] = purchasedItem.supplier.name
							if category == "Hops":
								theitem['purchases'][-1]['hopalpha'] =purchasedItem.hop_actual_alpha
								if purchasedItem.hop_actual_alpha:	
									theitem['purchases'][-1]['hopalpha'] = theitem['hopalpha']

			result = {'category' : category,'items': theitem }
			if getRawResult:
				return result
		"""
		result = {'category' : category,'items': theitem }
		sys.stderr.write("getStockFullDetails() -> status=1\n")
		return {'operation':'getStockFullDetails','status' :1,'json' : json.dumps( {"result": result})}


		sys.stderr.write("getStockFullDetails() -> status=0")
		return {'operation':'getStockFullDetails','status' :0  }



                              #            1       2         3       4           5
	def changeItemQty(self,username,category,itemName,stockTag,newQty,resetBestBefore):
		"""
		changeItemQty()
			Provides a list of stock in the store

			string: category as per listStoreCategories
			string: item as per listStoreItems

		return: standard json with details of the stock item
		"""
		sys.stderr.write("changeItemQty < %s,%s,%s,%s" %(category,itemName,stockTag,newQty))
		status=0
		try:
			stockItem = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND stocktag = :2",username,stockTag).fetch(1)
			if len(stockItem) < 1:
				return {'operation':'changeItemQty','status':-2}	# can't find item
			

			if resetBestBefore == "Y":
				stockItem[0].bestBeforeEnd = int(time.time()+(86400*7))
			stockItem[0].qty=float(newQty)
			stockItem[0].put()
			status = 1
		except:
			sys.stderr.write("EXCEPTION in changeItemQty\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write( e )

		return {'operation' : 'changeItemQty', 'status' : status ,'json':json.dumps( {} ) }



	
	def listIngredientsAndSuppliers(self,username,category,item):
		"""
		listIngredientsAndSuppliers(category)
			category = 	fermentable,hop,yeast,misc,consumable
			
		Note: this is similair to listIngredients but provided as a convenience
		return: list of ingredients from the presets file
		"""

		sys.stderr.write("listIngredientsAndSuppliers -> %s/%s\n" %(category,item))
		status=0

		try:


		


			result={}
			result['category'] = category
			#result['items'] =  self.data.dumpJSON( category )
			result['items'] = []

			if item == "":
				ourIngredients = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2", username, category.lower())
				for ingredient in ourIngredients.fetch(2000):
					result["items"].append(ingredient.name)
			else:
				result['items'].append(item)
			result['items'].sort()

			ourSuppliers = db.GqlQuery("SELECT * FROM gSuppliers WHERE owner = :1", username)
			result['suppliers'] = []
			for supplier in ourSuppliers.fetch(2000):
				result['suppliers'].append(supplier.supplierName)
			result['suppliers'].sort()

			return {'operation' : 'listIngredientsAndSuppliers', 'status' : 1,
					'json' : "%s" %( json.dumps( {'result':result} )  ) 
				}
		except:	
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
		return {'operation' : 'listIngredientsAndSuppliers', 'status' : status }

	

	def addNewPurchase(self,username,category,itemtext,qty,cost,day,month,year,suppliertext,numpurchased,hopalpha):
		"""
		"""

		sys.stderr.write("addNewPurchase -> %s/%s/%s....\n" %(category,itemtext,qty))		
		status = 0
		
		try:

			ourPurchases = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 ", username)
			results = ourPurchases.fetch(348400)
			stocktag = len(results)

			
			ourIngredients = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2 AND name = :3 ", username, category.lower(), itemtext )
			unit=""
			for ingredient in ourIngredients.fetch(1):
				unit=ingredient.unit
		
			suppliers=[]
			ourSuppliers = db.GqlQuery("SELECT * FROM gSuppliers WHERE owner = :1", username)
			for supplier in ourSuppliers.fetch(20000):
				suppliers.append(supplier.supplierName)
			suppliers.sort()
			(Y,M,D,h,m,s,wd,yd,tm) = time.localtime()

			STOCKTAGS=""
			for c in range(int(numpurchased)):
				purchase = gPurchases( owner=username, storecategory=category.lower(), storeitem=itemtext)
				purchase.qty=float(qty)
				purchase.purchaseDate=int(time.time())
				purchase.bestBeforeEnd = int(time.mktime( (int(year),int(month),int(day),0,0,0,0,0,0) ))
				purchase.supplier = suppliertext
				purchase.itemcategory=ingredient.category
				purchase.qtyMultiple=ingredient.qtyMultiple
				purchase.wastageFixed=ingredient.wastageFixed
				purchase.itemsubcategory=ingredient.subcategory
				purchase.purchaseCost = float(cost)/float(qty)
				try:
					purchase.volume=ingredient.volume
				except:
					pass
				purchase.stocktag= "0"*(6-len("%s" %(stocktag+c)))
				purchase.stocktag = "BRI%s%s" %(purchase.stocktag, stocktag+c)
				purchase.unit = unit
				sys.stderr.write("Unit: %s\n" %(purchase.unit))
				if category.lower() == "hops":
					purchase.hopActualAlpha = float(hopalpha)
				purchase.put()
				sys.stderr.write("owner:%s\n" %(purchase.owner))
				sys.stderr.write("category:%s\n" %(purchase.storecategory ))
				sys.stderr.write("storeitem:%s\n" %(purchase.storeitem))
				sys.stderr.write("purchasedate:%s\n" %(purchase.purchaseDate))
				sys.stderr.write("purchasebestbeforeend:%s\n" %(purchase.bestBeforeEnd))
				sys.stderr.write("supplier:%s\n" %(purchase.supplier))
				sys.stderr.write("purchaseCost:%s\n" %(purchase.purchaseCost))
				sys.stderr.write("stocktag:%s\n" %(purchase.stocktag))
				sys.stderr.write("hopactualalpha:%s\n" %(purchase.hopActualAlpha))
			status = 1
			return {'operation' : 'addNewPurchases', 'status' : status ,'json':json.dumps( {} ) }

		
		except:
			sys.stderr.write("EXCEPTION in addNewPurchase\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'addNewPurchases', 'status' : status }




	def docalculateV1(self,username,recipeName):
		if not username == "test@example.com":	return

		a=1
		self.hops_by_avg_alpha = {}
		self.hops_by_contribution={}
		"""
			This is a copy/paste of brewerslabEngine.py with small modifications to 
			use Gql Datastore as opposed to pickles

			Need to decide what to do longterm with this, suspect we will keep this version longterm.
			Matches: 2011-09-14 (svn revi 2 : 2011-12-07 20:16:14 +0000

			
		"""

	
		ourContributions = db.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2", username,recipeName)
		for x in ourContributions.fetch(2000):
			x.delete()

		ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe=ourRecipe.fetch(1)[0]
		self.recipe=recipe
		if len(recipe.process) < 1:
			return "Cannot calculate because we don't know which process to use"

		ourProcess = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3",username,recipe.process,-1)
		process=ourProcess.fetch(1)[0]
		self.Process=process		# rename this later from Process to process.
						# but for now leave as is so we can more easily merge code
		

		self.calclog = ""
		#pickle:self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(self.process.name)
		#gqlself.calclog = self.calclog + "process  : Calculating with Process %s\n" %(revcipe.process)
		self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(recipe.process)	#pickql
		self.calclog = self.calclog + "process  : brewerslabEngine rev 2012-10-09\n"
		self.calclog = self.calclog + "process  : changes since 2011-09-14\n"
		self.calclog = self.calclog + "process  :  - conversion to use Gql datastore rather than pickle\n"
		self.calclog = self.calclog + "process  :  - removed ingredients against activities never used so far\n"
		self.calclog = self.calclog + "process  :  - found potential bug with checkStockAndPrice and kegs\n"
		self.calclog = self.calclog + "process  :  - now using implicit caprequired/co2required \n"
		self.calclog = self.calclog + "process  : changes since 2011-04-15\n"
		self.calclog = self.calclog + "process  :  - waterRequirement changes to better include FV deadspace\n"
		self.calclog = self.calclog + "process  :  - waterRequirement ignore hop wastage if boilder deadspace is greater\n"
		self.calclog = self.calclog + "process  : changes since 2012-10-09\n"
		self.calclog = self.calclog + "process  :  - validated water required - higher than required (!)\n"
		self.calclog = self.calclog + "process  :    (but haven't fully worked out impact of evaporation on  boiling topup)\n"
						# probably balances out ok ... seem to remember in 2012-02-06 evaporation was higher
		self.calclog = self.calclog + "process  :  - waterRequirement - total requirement didn't include topup\n"
		self.calclog = self.calclog + "process  :  - mashliquid - should include the deadspace\n"
		self.calclog = self.calclog + "process  :  - added new gravity predictions\n"
		self.calclog = self.calclog + "process  : key assumptions\n"
		self.calclog = self.calclog + "process  :  - hops not scaled based on topup assumed marginal\n"
		self.calclog = self.calclog + "process  :  http://www.jimsbeerkit.co.uk/forum/viewtopic.php?f=3&t=42263#p445413\n"
		self.calclog = self.calclog + "process  :    ( need some calculation for this as big assumption)\n"
		self.calclog = self.calclog + "process  :  - note: figures calcualted here seem to deviate around 2%%-3%%\n"
		# Scale boil volume with wastage
		# caculate()
		

		self.batch_size_required = recipe.batch_size_required
		self.batch_size_required_plus_wastage = self.batch_size_required
#

		self.boilers = self._getEquipment(username,recipe.process,"boiler",True)
		self.mash_tun = self._getEquipment(username,recipe.process,"mashtun")
		self.hlt = self._getEquipment(username,recipe.process,"hlt")
		self.fermentation_bin = self._getEquipment(username,recipe.process,"fermentationbin")



		boiler_Dead_Space = 0

		#pickle:for boiler in self.process.boilers:
		#gql:for boiler in self._getEquipment(username,process,"boiler",True):

		for boiler in self.boilers:
			self.calclog = self.calclog + "boilWaste: Adding %.2f for wastage in the boiler\n" %(boiler.dead_space)
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + boiler.dead_space
			boiler_Dead_Space = boiler_Dead_Space + boiler.dead_space

		self.boiler_Dead_Space = boiler_Dead_Space
		#pickle:if self.batch_size_required_plus_wastage != self.batch_size_required:
		#gql:if self.batch_size_required_plus_wastage != recipe.batch_size_required:
		if self.batch_size_required_plus_wastage != recipe.batch_size_required:	#pickql
			self.calclog = self.calclog + "boilWaste: batch size adjusted to %.2f to account for wastage in boiler\n" %(self.batch_size_required_plus_wastage)


#2192	

		if self.fermentation_bin.dead_space >  0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + self.fermentation_bin.dead_space
			self.calclog = self.calclog + "boilWaste: batch size adjusted to %.3f to account for wastage in fermentation bint\n" %(self.batch_size_required_plus_wastage)


		self.racking_bucket = self._getEquipment(username,recipe.process,"rackingbucket")
		if self.racking_bucket.dead_space >  0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + self.racking_bucket.dead_space
			self.calclog = self.calclog + "boilWaste: batch size adjusted to %.3f to account for wastage in racking bucket\n" %(self.batch_size_required_plus_wastage)

		# Assumption built in that bottles are 500 ml
		bottle_size = 0.500	# ml
		self.bottles_required = math.floor( self.batch_size_required * bottle_size )
		# this will get updated later in compiles 

		#
		# Estimate Gravity
		#
		self.estimated_mash_gravity = 0
		total_contribution=0
		total_contribution_grain=0
		# Calculate Expected Gravity:
		# ppg X wt / batch size	
		self.calclog = self.calclog + "calcferm : Calculating expected gravity\n"
		ourFermentables = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = False", username,recipeName,'fermentables')
		self.fermentables=ourFermentables.fetch(2000)
		for fermentable in self.fermentables:
			qty=fermentable.qty
			self.calclog = self.calclog + "calcferm :	fermentable: %s%s %s\n" %(qty,fermentable.unit,fermentable.ingredient)
			self.calclog = self.calclog + "calcferm :		hwe: %s extract: %s\n" %(fermentable.hwe,fermentable.extract)
			contribution = (qty /1000 * fermentable.hwe) / self.batch_size_required_plus_wastage
			self.calclog = self.calclog + "calcferm : \t\t\tcontribution = %s\n" %(contribution)
			self.calclog = self.calclog + "calcferm : \t\t\t%s = %s * %s / %s\n" %(contribution, qty/1000, fermentable.hwe , self.batch_size_required_plus_wastage)
			if (fermentable.isGrain or fermentable.mustMash) and not fermentable.isAdjunct:
				self.calclog = self.calclog + "calcferm : \t\t\tIncluding in Mash Gravity\n"
				self.estimated_mash_gravity = self.estimated_mash_gravity + contribution
				total_contribution_grain = total_contribution_grain + contribution

			# add this grain into our contributiosn table
			cont = gContributions( owner=username, recipeName=recipeName )
			cont.ingredientType="fermentables"
			cont.ingredient=fermentable.ingredient
			cont.gravity =float( contribution * (recipe.mash_efficiency /100.0 ) )
			cont.srm=0.0
			cont.put()




			total_contribution = total_contribution + contribution	
	
		estimated_gravity_grain_100pcnt = total_contribution_grain 
		self.estimated_gravity_grain_100pcnt = estimated_gravity_grain_100pcnt
		self.calclog = self.calclog + "calcferm : 	uncorrected gravity for grain %.3f\n" %(1+(estimated_gravity_grain_100pcnt / 1000))

		
		self.mash_efficiency = recipe.mash_efficiency	
		self.calclog = self.calclog + "calcferm :	correcting gravity based on mash efficiency of %s %%\n" %(self.mash_efficiency)
		estimated_gravity_grain = total_contribution_grain * (self.mash_efficiency / 100)
		self.estimated_gravity_grain = 1+( estimated_gravity_grain/1000)
		self.calclog = self.calclog + "calcferm : \t\testimated_gravity_mashedgrain = %s\n" %(estimated_gravity_grain)
		self.calclog = self.calclog + "calcferm : \t\t\t%.3f = %.3f * %.2f\n" %(estimated_gravity_grain,total_contribution, self.mash_efficiency/100)
		self.calclog = self.calclog + "calcferm : \t\t\t%.3f = 1 + (%.3f/1000) \n" %(1+(estimated_gravity_grain/1000),estimated_gravity_grain)	
	
		self.calclog = self.calclog + "calcferm : \t\testimated_gravity_nonmashedgrain = %s\n" %(total_contribution - total_contribution_grain )
		self.calclog = self.calclog + "calcferm : \t\testimated_gravity = %.3f + %.3f" %(estimated_gravity_grain,  (total_contribution - total_contribution_grain ))
		


		estimated_gravity = estimated_gravity_grain + (total_contribution - total_contribution_grain )
		self.estimated_gravity = estimated_gravity	
		





##2261
		#
		# Hops
		#
		self.calclog = self.calclog + "calchops : Calculating Tinseth Hop Calculation\n"
		self.calclog = self.calclog + "calchops : http://www.realbeer.com/hops/research.html\n"

	
		# if we have boiling/cooling loss specified then we should calculate the hops required based on the
		# evaporated value not the full boil volume
		real_batch_size_required_plus_wastage = self.batch_size_required_plus_wastage

###postboilvolume is not available anywhere
		if recipe.postBoilTopup > 0:
			self.batch_size_required_plus_wastage  = self.batch_size_required_plus_wastage + recipe.postBoilTopup
			self.calclog = self.calclog + "calchops : setting volume for hops calculations to %.2f (was %.2f)\n" %( self.batch_size_required_plus_wastage,real_batch_size_required_plus_wastage)
		else:
			self.calclog = self.calclog + "calchops : ignoring water evaporation in calculation-- don't have loss values\n"


	
		working_total_hop_qty = {}

		# New Hop Structure 	
		# At this stage we wil lcalculate the IBU's with the *default* hop alpha acid.
		# but there is nothing to say we will get hops of this alpha from the store
		# therefore we should call "adjustHopAlphaQty()" to compenstate
		hop_utilisation_factors = {}
		
		self.hops_by_addition={}
#		self.calclog=self.calclog + "SELECT * FROM gIngredients WHERE owner = '%s' AND recipename = '%s' AND ingredientType = '%s' AND processIngredient = False\n" %(username,recipeName,'hops')
		ourHops = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = False AND hopAddAt > :4", username,recipeName,'hops',-1.00)
		self.hops=ourHops.fetch(555)
		for tmp in self.hops:
			if not self.hops_by_addition.has_key( tmp.hopAddAt ):	self.hops_by_addition[ tmp.hopAddAt ] = []
#			self.calclog=self.calclog+"ADDING hop %s %s\n" %(tmp.ingredient,tmp.hopAddAt)
			self.hops_by_addition[ tmp.hopAddAt ].append(tmp)
	
		for hopAddAt in self.hops_by_addition:
			hop_utilisation_factors[ hopAddAt ] = self._tinsethUtilisation( hopAddAt, estimated_gravity )
		

		total_hop_ibu = 0
		for hopAddAt in self.hops_by_addition:
			for hop in self.hops_by_addition[ hopAddAt]:	
				hopqty = hop.qty

				# if we have *EVER* called adjustHopAlphaQty() then we should use the weighted hop alpha
				# average that was calculated last time that we adjusted the qty's of hops.
				# this is to ensure next time adjustHopAlpha is called we don't over/under scale
				HOP_ALPHA = hop.hopAlpha
				if self.hops_by_avg_alpha.has_key( hopAddAt):
					if self.hops_by_avg_alpha[ hopAddAt ].has_key( hop ):
						HOP_ALPHA = self.hops_by_avg_alpha[ hopAddAt ][ hop ]
					# this code is still safe with gql conversion but not entirely sure
					# what it was doing before	

				# Hop Qty hasn't been specified so we need to decide the weight
		
		#
		# Note: this isn't functional in the api
		#

				if hopqty == 0  and 1==0:	
					if not working_total_hop_qty.has_key( hop ):
						working_total_hop_qty[ hop ] = 0

					#this_hop_ibu	*	batchsize		
					#19	*	15		
					#-------------------------------------------------------------------				
					#(utilisation facot		hop alpha		fixed
					#0.00211494	*	6	*	1000

					hop_required_ibu = self.hops_by_contribution[ hopAddAt ][ hop ]
					this_hop_weight = (hop_required_ibu * self.batch_size_required_plus_wastage ) / (hop_utilisation_factors[ hopAddAt ] * HOP_ALPHA * 1000)

					self.hops_by_addition[ hopAddAt][ hop ] = this_hop_weight					
					working_total_hop_qty[ hop ] = working_total_hop_qty[ hop ] + this_hop_weight 

					this_hop_ibu = hop_utilisation_factors[ hopAddAt ] * (HOP_ALPHA * this_hop_weight * 1000 ) / self.batch_size_required_plus_wastage
					self.calclog = self.calclog + "calchopsI: \t%.2f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.ingredient, hopAddAt)
					self.calclog = self.calclog + "calchopsI: \t\tthis_hop_weight = %.3f\n" %(this_hop_weight)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = ( this_hop_ibu * batch_size ) / (hop_utilisation_factor * hop_alpha * 1000))\n" %(this_hop_weight)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = ( %.2f * %.2f L ) / ( %.5f * %.2f * 1000))\n" %(this_hop_weight, hop_required_ibu, self.batch_size_required_plus_wastage, hop_utilisation_factors[ hopAddAt ], HOP_ALPHA)
					self.calclog = self.calclog + "calchopsI: \t\tthis_hop_ibu = %.3f\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = hop_utilisation_factor * (hop_alpha * qty * 1000) / batch_size\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = %.8f * (%s * %s * 1000) / %s\n" %(this_hop_ibu,hop_utilisation_factors[ hopAddAt ], HOP_ALPHA, hopqty ,self.batch_size_required_plus_wastage)

					# if we have come in here with IBU not weight then we need to update the recipe
					
				# Hop Qty has been provided so determine the IBU as normal
				elif hopqty >0:
					this_hop_ibu = hop_utilisation_factors[ hopAddAt ] * (HOP_ALPHA * hopqty * 1000 ) / self.batch_size_required_plus_wastage
					if not self.hops_by_contribution.has_key( hopAddAt):	self.hops_by_contribution[hopAddAt] = {}
					self.hops_by_contribution[ hopAddAt ][ hop ] = this_hop_ibu

					self.calclog = self.calclog + "calchopsW: \t%.2f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.ingredient, hopAddAt)
					self.calclog = self.calclog + "calchopsW: \t\tthis_hop_ibu = %.3f\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsW: \t\t\t %.3f = hop_utilisation_factor * (hop_alpha * qty * 1000) / batch_size\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsW: \t\t\t %.3f = %.8f * (%s * %s * 1000) / %s\n" %(this_hop_ibu,hop_utilisation_factors[ hopAddAt ], HOP_ALPHA, hopqty ,self.batch_size_required_plus_wastage)

				else:
					this_hop_ibu=0.0

				# add this hop ibu into our contributiosn table
				cont = gContributions( owner=username, recipeName=recipeName )
				cont.ingredientType="hops"
				cont.ingredient=hop.ingredient
				cont.hopAddAt = hopAddAt
				cont.ibu = this_hop_ibu
				cont.put()
				total_hop_ibu = total_hop_ibu + this_hop_ibu



		if len(working_total_hop_qty) > 0:
			self.hops=[]	
			for HOP in working_total_hop_qty:
				self.hops.append( ( HOP, working_total_hop_qty[ HOP ] ) )
				self.calclog = self.calclog + "calchopsI: \tUpdated Recipe Hop Qty %.2f %s %s \n" %( working_total_hop_qty[ HOP ], HOP.unit, HOP.name)

		self.calclog = self.calclog + "calchops : %.2f IBU = Estimated Total IBUs\n" %(total_hop_ibu)





		# Technically we should use slightly more hops since we are using top-up's but for now
		# we are going to assume that it is marginal  

		self.calclog = self.calclog + "calchops : not taking account of additional hops required for top-up dilutions\n"
		self.calclog = self.calclog + "calchops :  hops calculated on batch size of %.2f \n" %(self.batch_size_required_plus_wastage)





		self.batch_size_required_plus_wastage = real_batch_size_required_plus_wastage 

##2375

		#
		# Colour
		#
		self.calclog = self.calclog + "calcColor: Calculating Morey SRM Colours\n"
		self.calclog = self.calclog + "calcColor: http://www.brewingtechniques.com/brewingtechniques/beerslaw/morey.html\n"
#SRM = 1.4922 [(MCU) ^ 0.6859] - for values of SRM < 50

		total_srm = 0
		total_qty = 0
		sum_weighted_color = 0 
		grain_qty_pounds = 0

		ourFermentables = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False", username,recipeName,'fermentables')
		self.fermentables=ourFermentables.fetch(2000)
		for fermentable in self.fermentables:
			qty=fermentable.qty
			if fermentable.isGrain:
				total_qty = total_qty + qty
				color_srm = fermentable.colour * 0.508
				grain_qty_pounds = grain_qty_pounds + (qty / 1000 / 0.454)

				weighted_color = (qty / 1000 / 0.454) * color_srm
	
				self.calclog = self.calclog + "calcColor: \t\t color_srm = %s for %s\n" %(color_srm,fermentable.ingredient)
				self.calclog = self.calclog + "calcColor: \t\t\t %s = %.3f EBC * 0.8368  \n" %(color_srm, fermentable.colour)

				self.calclog = self.calclog + "calcColor: \t\t\t weighted_grain_color = %.2f \n" %(weighted_color )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (qty / 1000 / 0.454) * color_srm  \n" %(weighted_color )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (%s / 1000 / 0.454) * %.3f  \n" %(weighted_color,qty,color_srm )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (%s) * %.3f  \n" %(weighted_color,qty/1000/0.454,color_srm )

				# add this grain into our contributiosn table
				cont = gContributions( owner=username, recipeName=recipeName )
				cont.ingredientType="fermentables"
				cont.ingredient=fermentable.ingredient
				cont.gravity = 0.0
				cont.srm=weighted_color
				cont.put()
				total_hop_ibu = total_hop_ibu + this_hop_ibu



				sum_weighted_color = sum_weighted_color + weighted_color
				

		total_weighted_color = sum_weighted_color
		self.calclog = self.calclog + "calcColor: \t\t total_weighted_color = %.2f \n" %(total_weighted_color)
		self.calclog = self.calclog + "calcColor: \t\t\t %.2f = sum(weighted_color)   \n" %(total_weighted_color )
		

		volume_gallons = ( self.batch_size_required_plus_wastage + recipe.postBoilTopup ) / 3.785
		mcu = total_weighted_color / volume_gallons
		srm = 1.4922 * math.pow( mcu, 0.6859)

		self.calclog = self.calclog + "calcColor: \t\t estimated srm = %.1f\n" %(srm)
		self.calclog = self.calclog + "calcColor: \t\t\t %.1f = 1.4922 * mcu ^ 0.6859\n" %(srm)
		self.calclog = self.calclog + "calcColor: \t\t\t %.1f = 1.4922 * %.3f ^ 0.6859\n" %(srm,mcu)
		self.calclog = self.calclog + "calcColor: \t\t\t mcu = %.3f\n" %(mcu)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = weighted_grain_color / volume_gallons\n" %(mcu)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = %.3f / %.3f\n" %(mcu,total_weighted_color, volume_gallons)
		self.calclog = self.calclog + "calcColor: \t\t\t volume_gallons =  %.3f\n" %( volume_gallons)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = (batch_size + top_up) / 3.785\n" %(volume_gallons )
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = (%.3f + %.3f) / 3.785\n" %(volume_gallons,self.batch_size_required_plus_wastage,recipe.postBoilTopup )
		
		estimated_srm=srm			
		estimated_ebc=srm*1.97
		self.calclog = self.calclog + "calcColor   : \t\t estimated ebc = %.1f\n" %(estimated_ebc)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = %.1f SRM * 1.97 \n" %(estimated_ebc,estimated_srm)






		self.calclog = self.calclog + "calcfgrav: Calculating Estimated Final Gravity\n"
		# This is could probably take a skew from mash temperature
		grain_fermentable_typical_pcnt = 0.62
		nongrain_fermentable_typical_pcnt=1
		
		grain = 0
		nongrain = 0
#		self.fermentables=ourFermentables.fetch(2000)
		for fermentable in self.fermentables:
			qty=fermentable.qty
			if fermentable.isGrain:
				grain = grain + qty
			else:
				nongrain = nongrain + qty
		
		grain_pcnt = grain / (grain + nongrain)
		nongrain_pcnt = nongrain / (grain + nongrain)

		self.grain_weight=grain
		self.nongrain_weight=nongrain

		fermentable_grain = (estimated_gravity * grain_pcnt * grain_fermentable_typical_pcnt) 
		fermentable_nongrain = (estimated_gravity * nongrain_pcnt * nongrain_fermentable_typical_pcnt)

		estimated_final_gravity = estimated_gravity - (1.23 * (fermentable_grain + fermentable_nongrain))

		self.calclog = self.calclog + "calcfgrav: \t\t estimated_final_gravity = %.4f\n" %(1+(estimated_final_gravity)/1000)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = 1 + (estimated_gravity - (1.23 * (fermentable_grain + fermentable_nongrain ))/1000 \n" %(1+(estimated_final_gravity)/1000)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = %s - (1.23 * (%.2f + %.2f ) \n" %(estimated_final_gravity,estimated_gravity,fermentable_grain,fermentable_nongrain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t fermentable_grain = %.2f\n" %(fermentable_grain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.2f = (estimated_gravity * grain_pcnt * grain_fermentable_typical_pnct)\n" %(fermentable_grain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.2f = (%.2f * %.2f * %.2f)\n" %(fermentable_grain,estimated_gravity,grain_pcnt,grain_fermentable_typical_pcnt)
		self.calclog = self.calclog + "calcfgrav: \t\t\t fermentable_nongrain = %.2f\n" %(fermentable_nongrain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.2f = (estimated_gravity * nongrain_pcnt * nongrain_fermentable_typical_pnct)\n" %(fermentable_grain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.2f = (%.2f * %.2f * %.2f)\n" %(fermentable_nongrain,estimated_gravity,nongrain_pcnt,nongrain_fermentable_typical_pcnt)
	






		yeast_atten = 0
		yeast_count = 0	# need to research affect of multiple packets of yeast?
		ourYeasts = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False", username,recipeName,'yeast')
		self.yeasts=ourYeasts.fetch(2000)
		for yeast in self.yeasts:
			qty=yeast.qty
			yeast_atten = yeast_atten + yeast.atten
			yeast_count = yeast_count + 1

		if yeast_count == 0:
			self.calclog = self.calclog + "calcfgrav: \tWARNING: No YEAST in recipe setting a default attenuation 50\n"
			yeast_atten=0.50
		else:
			yeast_atten =( yeast_atten / yeast_count) / 100
			
		estimated_yeast_attenuation = estimated_gravity * (1-yeast_atten) 
		self.calclog = self.calclog + "calcfgrav: \t\t estimated_yeast_attenuation = %.4f\n" %( estimated_yeast_attenuation )

		ourYeasts = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False", username,recipeName,'yeast')
		self.yeasts=ourYeasts.fetch(2000)
		for yeast in self.yeasts:
			yeastqty=yeast.qty
			self.calclog = self.calclog + "calcfgrav:\t\t\t yeast attenuation for %s %.1f \n" %(yeast.ingredient,yeast.atten/100)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = estimated_gravity * (1 - yeast_atten) \n" %( estimated_yeast_attenuation)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = %.4f * (1 - %.1f) \n" %( estimated_yeast_attenuation, estimated_gravity, yeast_atten )

		if estimated_yeast_attenuation > estimated_final_gravity:
			estimated_final_gravity = estimated_yeast_attenuation
			self.calclog = self.calclog + "calcfgrav: \t\t Yeast Attenuation used for final gravity estimate\n"
		else:
			self.calclog = self.calclog + "calcfgrav: \t\t  used for final gravity estimate\n"

		#if estimated_final_gravity
		self.calclog = self.calclog + "calcabv   :\t\t Final Gravity Estimate = %.3f \n" %( 1+(estimated_final_gravity)/1000)

		self.calclog = self.calclog + "calcabv  : Alcohol By Volume\n"

		estimated_abv = ( ( 1 + (estimated_gravity)/1000 )  - ( 1+ (estimated_final_gravity)/1000) ) * 131
		self.calclog = self.calclog + "calcabv  :	abv = %.2f %%\n" %(estimated_abv)
		self.calclog = self.calclog + "calcabv  :	%.2f %% = ( original_gravity - final_gravity ) * 131\n" %(estimated_abv)
		self.calclog = self.calclog + "calcabv  :	%.2f %% = ( %.4f - %.4f ) * 131\n" %(estimated_abv, (1+(estimated_gravity/1000)), (1+(estimated_final_gravity/1000)  ))  






#2515


		#
		# Recipe Type Calculations
		#
		strike_temp = self.getStrikeTemperature()


		
		total_water = self.waterRequirement()


		#
		# More Top Up's
		# 
		if recipe.postBoilTopup > 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage - recipe.postBoilTopup
		
		self.calclog = self.calclog + "mashliqid: Mash Liquid required, based on\n"
		self.calclog = self.calclog + "mashliqid: http://www.brew365.com/technique_calculating_mash_water_volume.php\n"
		#Now that you know the total water required for your batch, you can figure out which portion of this total to use for 
		# mashing and the rest will be used for sparging. To know this, you will need to know what mash thickness ratio to use. 
		# For most purposes, a good ratio is to use 1.25 Qts. per pound of grain (0.3125 gal/lb.)3.
		
		total_grain_weight = 0	
		for fermentable in self.fermentables:
			qty=fermentable.qty
			if fermentable.isGrain:
				if fermentable.unit != "gm":
					sys.stderr.write("critical: Mash Liquid requires ferementables to be specified in grammes\n")
					sys.stderr.write("critical: unit was %s\n" %(fermentable.unit))
					sys.exit(2)
				self.calclog = self.calclog + "mashliqid:	fermentable: %s%s %s\n" %(qty,fermentable.unit,fermentable.ingredient)
				total_grain_weight = total_grain_weight + qty


		# previously fixed at 1.25, but we have always had 1.1.829 in the process
		grain_thickness_ratio = recipe.mash_grain_ratio	# fixed value from reference above, qts per pound of grain
		self.calclog = self.calclog +"mashliqid: grain_thickness_ratio %.3f\n" %(grain_thickness_ratio)
		metric_lb_kg_factor = 0.453592
		metric_gal_l_factor = 3.78541178


		mash_liquid = ( grain_thickness_ratio * ( ( total_grain_weight / 1000 ))) / ( 4 * metric_lb_kg_factor )  * metric_gal_l_factor 

		self.calclog = self.calclog + "result   : mash_liquid = %.1f\n" %( mash_liquid )
		self.calclog = self.calclog + "mashliqid: %.1f = ( grain_thickness_ratio *  total_grain_weight ) / (4 * metric_lb_kg )  * metric_gal_l\n" %(mash_liquid)
		self.calclog = self.calclog + "mashliqid: %.1f = ( %.3f *  %.2f ) / (4 * %.4f ) * %.4f\n" %(mash_liquid, grain_thickness_ratio,total_grain_weight/1000,metric_lb_kg_factor,metric_gal_l_factor)
		self.calclog = self.calclog + "mashliqid: %.1f = ( %.4f ) / ( %.4f  ) * %.4f\n" %(mash_liquid, grain_thickness_ratio * total_grain_weight/1000,4*metric_lb_kg_factor,metric_gal_l_factor)
		self.calclog = self.calclog + "mashliqid: %.1f =  %.4f  * %.4f\n" %(mash_liquid, (grain_thickness_ratio * total_grain_weight/1000) / (4*metric_lb_kg_factor),metric_gal_l_factor)
	

		self.calclog = self.calclog + "mashliqid: Mash Liquid = Mash Liquid + mash/lauter tun deadspace (%.2f)\n" %(self.mash_tun.dead_space)
		mash_liquid = mash_liquid + self.mash_tun.dead_space
		self.calclog = self.calclog + "mashliqid: Mash Liquid = %.3f\n" %(mash_liquid)



			
		sparge_water = total_water - mash_liquid
		self.calclog = self.calclog + "mashliqid: Sparge Water = total_water - mash_liquid\n"
		self.calclog = self.calclog + "mashliqid: Sparge Water = %.2f \n" %(total_water - mash_liquid  - self.recipe.postBoilTopup)
		sparge_water_addition = total_water - mash_liquid
	
		# instinct is if sparge was water then sparge water here would be - topup but sparge is actually wort so it will be including 
		# however we are getting strange numbers if we don't subtract topup.... this might be because we've already 
		# artifically inflacted the topup value early in the process

		



		# Boil Off Calculations 
		# The calculations in here use batch_size_required_plus_wastage so have 
		# already factored in the boil off expansions
		# but when we get the runnoffs from the mash it will appear to be
		# so what we need to know pre boil is what our "diluted factor would be"
		
		# Mash gravity
		#self.estimated_gravity = estimated_gravity	
		self.calclog = self.calclog + "mashgravi: Calculating Mash Gravity (Post Mash/Pre Boil/Pre Evaporation Concentration)\n"
		self.calclog = self.calclog + "mashgravi:\t Boil Volume: %.2f\n" %(self.water_in_boil)
		self.calclog = self.calclog + "mashgravi:\t Gravity Expected from Grain: %.4f\n" %(1+(estimated_gravity_grain/1000))
		self.calclog = self.calclog + "mashgravi:\t Volume after boil/cooling: %.2f\n" %(self.batch_size_required_plus_wastage)
		post_mash_gravity = estimated_gravity_grain * self.batch_size_required_plus_wastage  / self.water_in_boil
		self.post_mash_gravity =1+(post_mash_gravity/1000)
		self.calclog = self.calclog + "mashgravi:\t %.3f = (1-(estimated_gravity_grain * 1000) * batch_size_with_wastage) / boil_volume\n" %( 1+( post_mash_gravity/1000))
		self.calclog = self.calclog + "mashgravi:\t %.2f = (%.0f * %.2f) / %.2f\n" %( post_mash_gravity, estimated_gravity_grain,  self.batch_size_required_plus_wastage, self.water_in_boil)


		self.calclog = self.calclog + "mashgravi: Pre Boil Gravity (Pre Boil/Pre Evaporation Concentration)\n"
		self.calclog = self.calclog + "mashgravi:\t Boil Volume: %.2f\n" %(self.water_in_boil)
		self.calclog = self.calclog + "mashgravi:\t Gravity Expected (FG): %.4f\n" %(1+(estimated_gravity/1000))
		self.calclog = self.calclog + "mashgravi:\t Volume after boil/cooling: %.2f\n" %(self.batch_size_required_plus_wastage)
		pre_boil_gravity = estimated_gravity * self.batch_size_required_plus_wastage  / self.water_in_boil
		self.pre_boil_gravity =1+(pre_boil_gravity/1000)
		self.calclog = self.calclog + "mashgravi:\t %.3f = (1-(estimated_gravity * 1000) * batch_size_with_wastage) / boil_volume\n" %( 1+( post_mash_gravity/1000))
		self.calclog = self.calclog + "mashgravi:\t %.2f = (%.0f * %.2f) / %.2f\n" %( pre_boil_gravity, estimated_gravity,  self.batch_size_required_plus_wastage, self.water_in_boil)

		
		# Time to heat in hot liquor tank
		start_temp = 5
		end_temp= 77
		
		if not self.hlt.heatPower:
			self.calclog=self.calclog +"heatpower:\tWarning heat power not specified for HLT\n"
			hltheatpower=1700
		else:
			hltheatpower=self.hlt.heatPower
		heating_time =(4184.0 * sparge_water *(end_temp - start_temp ))/ hltheatpower / 1000.0 / 60.0 ;
		heating_time = int( heating_time + 0.5 )
	
		# Recipe Styles
		self.sparge_temp = 82			# note: the recommendation is 82 counting on some loss of temperature will still keep grain bed
							# temp less than 77... 77 is about the temp tannins are extracted

#2619

		self.topupvol = recipe.postBoilTopup
		if recipe.postBoilTopup > 0:
			self.calclog = self.calclog +"topupVolu: Have a topup volume of %.2f\n" %(recipe.postBoilTopup)
			v1=self.batch_size_required_plus_wastage
			v2=-recipe.postBoilTopup
			self.top_up_gravity=1.000	
			# this is actually concentrating rather than diluting as v2 is "-topup"
			self.pretopup_post_mash_gravity = 1+((v1/(v1+v2)*post_mash_gravity) + (v2/(v1+v2) * self.top_up_gravity))/1000
			self.calclog = self.calclog +"topupVolu:   Scaling Post Mash Volume %.4f --> %.4f\n" %( 1+(post_mash_gravity/1000),self.pretopup_post_mash_gravity) 
			self.pretopup_estimated_og = 1+((v1/(v1+v2)*estimated_gravity) + (v2/(v1+v2) * self.top_up_gravity))/1000
			self.calclog = self.calclog +"topupVolu:   Scaling Estimated OG %.4f --> %.4f\n" %( 1+(estimated_gravity/1000),self.pretopup_estimated_og) 
			self.pretopup_estimated_gravity_grain = 1+((v1/(v1+v2)*estimated_gravity_grain) + (v2/(v1+v2) * self.top_up_gravity))/1000
			self.calclog = self.calclog +"topupVolu:   Scaling Estimated OG Grain %.4f --> %.4f\n" %( 1+(estimated_gravity_grain/1000),self.pretopup_estimated_gravity_grain) 
			self.pretopup_pre_boil_gravity = 1+((v1/(v1+v2)*pre_boil_gravity) + (v2/(v1+v2) * self.top_up_gravity))/1000
			self.calclog = self.calclog +"topupVolu:   Scaling Pre Boil Gravity %.4f --> %.4f\n" %( 1+(pre_boil_gravity/1000),self.pretopup_pre_boil_gravity) 
		else:
			self.pretopup_estimated_og = 1+(estimated_gravity/1000)
			self.pretopup_estimated_gravity_grain = 1+(estimated_gravity_grain/1000)
			self.pretopup_pre_boil_graivty =  1+(pre_boil_gravity/1000)
			self.pretopup_post_mash_gravity = 1+(post_mash_gravity/1000)
#			self.pretopup_post_mash_gravity = post_mash_gravity


		# Pre Cooling OG
		# Assumption 4% cooling loss for 100degree water
		# although we will take 3% into this because
		# by the time we are doing this we have probably
		# cooled a little
		grav1=estimated_gravity
		grav2=1	#fixed becuase this is the evaporation

		vol1=self.batch_size_required_plus_wastage * 1.03 	# batch_size plus wastage will already include the cooling contraction	
		self.precoolfvvol=self.batch_size_required_plus_wastage*1.03
		self.calclog = self.calclog+"preCoolOG: Volume before Cooling Contraction = %.2f\n" %(self.batch_size_required_plus_wastage * 1.03 )
		self.calclog = self.calclog+"preCoolOG: Assumed Approx Loss during cooling =  %.2f\n" %(self.batch_size_required_plus_wastage * 1.03 - self.batch_size_required_plus_wastage)
		
		self.calclog = self.calclog+"preCoolOG: Estimated OG After Cooling Contraction = %4f\n" %(1+(estimated_gravity/1000))


		vol2=vol1 - self.batch_size_required_plus_wastage 	# this should give us the difference
		totalvol=vol1+vol2
	
		g1 = (vol1/totalvol) * grav1
		g2 = (vol2/totalvol) * grav2
		self.precool_og = 1+( (g1+g2)/1000)
		self.calclog = self.calclog+"preCoolOG: Estimated OG Before Cooling Contraction = %4f\n" %(self.precool_og)


		self.sparge_heating_time = heating_time
		self.sparge_water = sparge_water 
		self.mash_liquid = mash_liquid 
		self.strike_temp = strike_temp
		self.strike_temp_5 = strike_temp + 5




		# Estrimations
		self.water_required = total_water
		self.estimated_abv = estimated_abv
		self.estimated_ibu=total_hop_ibu
		self.estimated_srm=estimated_srm
		self.estimated_ebc=estimated_ebc
		self.estimated_fg=1+(estimated_final_gravity)/1000
		self.estimated_og=1+(estimated_gravity)/1000



		# Even more predictions
		self.calclog = self.calclog + "predictin: Final Gravity Required %.4f\n" %(self.estimated_og)
		self.calclog = self.calclog + "predictin: post boil/pre cool gravity %.4f\n" %(self.precool_og)
		ratio_of_cool_to_uncool = self.estimated_og/self.precool_og
		self.calclog = self.calclog + "predictin:   ratio %.4f\n" %(ratio_of_cool_to_uncool)

		grav1 = self.pretopup_post_mash_gravity
		grav2 = 1.000
		vol1 = self.batch_size_required_plus_wastage
		vol2 = 1
		totalvol=vol1+vol2
		g1 = (vol1/totalvol) * grav1
		g2 = (vol2/totalvol) * grav2			
		self.watertopup1_gravity  = g1+g2
		self.calclog = self.calclog +"predictin:  precool gravity with 1L Water Topup = %.4f\n" %(self.watertopup1_gravity)

		grav1 = self.precool_og
		grav1 = self.pretopup_post_mash_gravity
		grav2 = 1.000
		vol1 = self.batch_size_required_plus_wastage
		vol2 = recipe.postBoilTopup
		totalvol=vol1+vol2
		g1 = (vol1/totalvol) * grav1
		g2 = (vol2/totalvol) * grav2			
		self.watertopupX_gravity  = g1+g2
		self.calclog = self.calclog +"predictin:  precool gravity with %sL Water Topup = %.4f\n" %(vol2,self.watertopupX_gravity)

		# Now put batch size back to normal
		if recipe.postBoilTopup > 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + recipe.postBoilTopup


		grav1 = self.precool_og
		grav1 = self.pretopup_post_mash_gravity
		grav2 = 1.010
		vol1 = self.batch_size_required_plus_wastage
		vol2 = 1
		totalvol=vol1+vol2
		g1 = (vol1/totalvol) * grav1
		g2 = (vol2/totalvol) * grav2			
		self.worttopup1_gravity  = g1+g2
		self.calclog = self.calclog +"predictin:  precool gravity with 1L 1.010 Wort Topup = %.4f\n" %(self.worttopup1_gravity)

		grav1 = self.precool_og
		grav1 = self.pretopup_post_mash_gravity
		grav2 = 1.010
		vol1 = self.batch_size_required_plus_wastage
		vol2 = recipe.postBoilTopup
		totalvol=vol1+vol2
		g1 = (vol1/totalvol) * grav1
		g2 = (vol2/totalvol) * grav2			
		self.worttopupX_gravity  = g1+g2
		self.calclog = self.calclog +"predictin:  precool gravity with %sL 1.010 Wort Topup = %.4f\n" %(vol2,self.worttopupX_gravity)

		# Now put batch size back to normal
		if recipe.postBoilTopup > 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + recipe.postBoilTopup


		self.calclog=self.calclog+"ABV : %.4f  %.4f OG %.4f FG\n" %(self.estimated_abv,self.estimated_og,self.estimated_fg)
		self.calclog=self.calclog+"IBU : %.4f\n" %(self.estimated_ibu)

		


		for fermentable in self.fermentables:
			qty=fermentable.qty
			self.calclog=self.calclog+"%.1f %s\n" %(qty,fermentable.ingredient)
		for hop in self.hops:
			qty=hop.qty
			self.calclog=self.calclog+"%.1f %.1f %s\n" %(qty,hop.hopAddAt,hop.ingredient)


		self.calculated=1



	def doCalculate(self,username,recipeName):

			
		self.docalculateV1(username,recipeName)
		self.calclog=self.calclog+"_________________________ "
		self.calclog = ""
		self.old_estimated_ibu = self.estimated_ibu

		self.calculated=1
		self.recipeName=recipeName
		self.username=username
		self.hops_by_avg_alpha = {}
		self.hops_by_contribution={}

		self.optimise_multi_boiler_deadspace=0
			# not sure this is compatible with the way that we are doing hops
			# if we do this then effectively it makes us use full gravity
		

#2696


		# 
		#
		#	VERSION 2
		#
		#


		
		ourContributions = db.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2", username,recipeName)
		for x in ourContributions.fetch(2000):
			x.delete()


		ourHops = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = False AND hopAddAt > :4", username,recipeName,'hops',-1.00)
		self.hops=ourHops.fetch(555)


		ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe=ourRecipe.fetch(1)[0]
		self.recipe=recipe
		recipe.calculationOutstanding=False
		recipe.put()
		if len(recipe.process) < 1:
			return "Cannot calculate because we don't know which process to use"

		ourProcess = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3",username,recipe.process,-1)
		process=ourProcess.fetch(1)[0]
		self.Process=process		# rename this later from Process to process.
						# but for now leave as is so we can more easily merge code
		



		ourFermentables = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = False", username,recipeName,'fermentables')
		self.fermentables=ourFermentables.fetch(2000)

		ourYeasts = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False", username,recipeName,'yeast')
		self.yeasts=ourYeasts.fetch(2000)

		self.boilers = self._getEquipment(username,recipe.process,"boiler",True)
		self.mash_tun = self._getEquipment(username,recipe.process,"mashtun")
		self.hlt = self._getEquipment(username,recipe.process,"hlt")
		self.fermentation_bin = self._getEquipment(username,recipe.process,"fermentationbin")




		#pickle:self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(self.process.name)
		#gqlself.calclog = self.calclog + "process  : Calculating with Process %s\n" %(revcipe.process)
		self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(recipe.process)	#pickql
		self.calclog = self.calclog + "process  : brewerslabEngine rev  (DEVEL)\n"
		self.calclog = self.calclog + "process  : Revision (2012-11-24)\n"
		self.calclog = self.calclog + "process  :  - updated mid-gravity table\n"
		self.calclog = self.calclog + "process  :  - fix for small batch sizes, calculate number of boilers\n"
		self.calclog = self.calclog + "process  :  - implemented recipe topup\n"
		self.calclog = self.calclog + "process  :  - implemented flavourings in aroma auto steps\n"	
		self.calclog = self.calclog + "process  :  - corrected bottles required\n"	
		self.calclog = self.calclog + "process  :  - implemented polypins (estimated of sugar required)\n"	
		self.calclog = self.calclog + "process  :    TODO: better consideration of different amounts of priming sugar may be needed\n"
		self.calclog = self.calclog + "process  :    TODO: tap water ingredient needed\n"
		self.calclog = self.calclog + "process  :  - BUGFIX: checkStockAndPrice considers kegs (and new polypins)\n"
	
		self.calclog = self.calclog + "process  : 2012-10-11:\n"
		self.calclog = self.calclog + "process  :  - procedural rework of calculations\n"
		self.calclog = self.calclog + "process  :  - evaporation calculations before cooling contraction\n"
		self.calclog = self.calclog + "process  :  - minimise boiler loss (50%%) by rationalising to 1 (Disabled)\n"
		self.calclog = self.calclog + "process  :  - modelling of concentration of runoff during mash (theoretical)\n"
		self.calclog = self.calclog + "process  :  - modelling of hop ibus based on different models (experimental)\n"
		self.calclog = self.calclog + "process  :  -  - hopmeasure_v2/hopaddition_v2 = 1kettle hop model\n"
		self.calclog = self.calclog + "process  :  - TODO: water based recipe.postBoilTopup not supported\n"
		self.calclog = self.calclog + "process  :  - TODO: wort topup is implicit\n"

		





			

		#
		# Batch Size - Equipment Dead Spaces
		#

		# working_batch_size = amount required out of boil

		self.calclog = self.calclog + "batchsize: Batch Size %.0f L\n" %(recipe.batch_size_required)
		working_batch_size = recipe.batch_size_required - recipe.postBoilTopup
		if recipe.postBoilTopup > 0:
			self.calclog = self.calclog + "batchsize: Batch Size %.0f L\n" %(working_batch_size)



		# Fermentation Bin Deadspace
		working_batch_size = working_batch_size + self.fermentation_bin.dead_space
		self.calclog = self.calclog + "batchsize:  Fermentation Bin Dead Space %.3f -> %.3f\n" %(self.fermentation_bin.dead_space,working_batch_size)
		working_batch_size_A = working_batch_size
		self.calclog = self.calclog + "batchsize: Batch Size (A)  %.3f\n" %(working_batch_size)#

		working_batch_size = working_batch_size + self.mash_tun.dead_space
		self.calclog = self.calclog + "batchsize:  Mash Tun Dead Space %.3f -> %.3f\n" %(self.mash_tun.dead_space,working_batch_size)


		# boiler vs hop weight
		self.boiler_Dead_Space=0
		biggest_boiler=0
		for boiler in self.boilers:
			if boiler.dead_space > biggest_boiler:	biggest_boiler=boiler.dead_space
			self.boiler_Dead_Space=self.boiler_Dead_Space + boiler.dead_space

		if self.optimise_multi_boiler_deadspace == 1:
			self.calclog = self.calclog + "batchsize: optimising multi-boiler deadspace from %.3f to %.3f\n" %(self.boiler_Dead_Space,biggest_boiler)
			self.boiler_Dead_Space = biggest_boiler

		total_hop_weight = 0
		for hop in self.hops:
			self.calclog = self.calclog + "batchsize:	hop: %s%s %s\n" %(hop.qty,hop.unit,hop.ingredient)
			if hop.unit != "gm":
				sys.stderr.write("critical: Water Requirement requires hops to be specified in grammes\n")
				sys.stderr.write("critical: unit was %s\n" %(hop.unit))
				sys.exit(2)
			total_hop_weight = total_hop_weight + hop.qty

		extra_water = ( total_hop_weight * 20 ) / 1000
		self.total_hop_weight=total_hop_weight

		if extra_water > self.boiler_Dead_Space:
			self.calclog = self.calclog +"batchsize: Adding in hop weight for water because it is bigger than boiler deadspace (%.3f)\n" %(self.boiler_Dead_Space)
			working_batch_size = working_batch_size + extra_water
			self.calclog = self.calclog + "batchsize: Hop Weight = %s%s --> %s L water\n" %(total_hop_weight, "gm", working_batch_size)
		else:
			self.calclog = self.calclog +"batchsize: Ingoring hop weight and using just boiler deadspace (%.3f)\n" %(extra_water)
			working_batch_size = working_batch_size + self.boiler_Dead_Space
			self.calclog = self.calclog + "batchsize:  Boiler Dead Space %.3f -> %.3f\n" %(self.boiler_Dead_Space,working_batch_size)








		working_batch_size_B = working_batch_size
		working_mash_size = working_batch_size
		working_hop_size = working_batch_size
		working_colour_size = working_batch_size
		self.calclog = self.calclog + "batchsize: Batch Size (B)  %.3f\n" %(working_batch_size)

		#if recipe.postBoilTopup > 0:
		#	working_mash_size = working_mash_size - recipe.postBoilTopup
		#	self.calclog = self.calclog + "batchsize:  Boil Topup reducing batch size: %.3f\n" %( working_mash_size )





		#
		# Cooling 
		#
		working_batch_size_C = working_batch_size_B

		self.calclog = self.calclog + "batchsize:  Boil Size %.3f\n" %( working_batch_size_B )
		cooling_loss = working_batch_size_C * 0.03
		working_batch_size_C = working_batch_size_C + cooling_loss
		self.calclog = self.calclog + "batchsize:  Cooling Loss @ 1.03 %%  %.3f -> %.3f\n" %(cooling_loss,working_mash_size)
		self.calclog = self.calclog + "batchsize: Batch Size (C)  %.3f\n" %(working_batch_size_C)




		
		#
		# Calculating approximate evaporation Loss
		#
		working_batch_size_D = working_batch_size_C
		if self.Process.fixed_boil_off > 0:
			evaporation_loss = self.Process.fixed_boil_off 
			working_batch_size_D = working_batch_size_D + evaporation_loss
			self.calclog = self.calclog + "batchsize: Boiling Loss (fixed %s) -> %.3f\n" %(self.Process.fixed_boil_off,working_batch_size_C)

			water_in_boil = water_in_boil + extra_water

		else:
			evaporation_loss = working_mash_size * ( self.Process.percentage_boil_off / 100 ) 
			working_batch_size_D = working_batch_size_D + evaporation_loss
			self.calclog = self.calclog + "batchsize: Boiling Loss (%s %%) ~ %.3f L water -> %.3f\n" %(self.Process.percentage_boil_off,evaporation_loss,working_batch_size_C)
		



		self.calclog = self.calclog + "batchsize:  Cooling Loss @ 1.03 %%  %.3f -> %.3f\n" %(cooling_loss,working_mash_size)
		self.calclog = self.calclog + "batchsize: Batch Size (D)  %.3f\n" %(working_batch_size_D)
		



		# 
		# Mash Wastage
		#
		total_grain_weight=0
		for fermentable in self.fermentables:
			if fermentable.isGrain:
				total_grain_weight = total_grain_weight + (fermentable.qty / 1000)
				self.calclog = self.calclog + "batchsize:	fermentable: %s%s %s\n" %(fermentable.qty,fermentable.unit,fermentable.ingredient)
	
		working_batch_size_E = working_batch_size_D +  total_grain_weight
		self.calclog = self.calclog + "mashliqid: Mash Wastage to Grain %.3f -> %.3f\n" %(total_grain_weight,working_batch_size_E)


		self.calclog = self.calclog + "batchsize: Batch Size (E)  %.3f\n" %(working_batch_size_E)




		#
		# HLT doesn't affect batch size it is just plain wastage
		#
		working_batch_size_F = working_batch_size_E + self.hlt.dead_space		
		self.calclog = self.calclog + "batchsize:  HLT Dead Space %.3f -> %.3f\n" %(self.hlt.dead_space,working_batch_size_F)
		self.calclog = self.calclog + "batchsize: Batch Size (F)  %.3f\n" %(working_batch_size_F)






		#
		# Top UP
		#
		working_batch_size_G = working_batch_size_F
		working_batch_size_G = working_batch_size_G + recipe.postBoilTopup
		self.calclog = self.calclog + "batchsize:  Topup %.3f -> %.3f\n" %(recipe.postBoilTopup,working_batch_size_G)
		self.calclog = self.calclog + "batchsize: Batch Size (G)  %.3f\n" %(working_batch_size_G)




		

		# 
		# Mash Water Requirement
		#
		grain_thickness_ratio = recipe.mash_grain_ratio	# fixed value from reference above, qts per pound of grain
		self.calclog = self.calclog +"mashwater: grain_thickness_ratio %.3f\n" %(grain_thickness_ratio)
		metric_lb_kg_factor = 0.453592
		metric_gal_l_factor = 3.78541178

		total_grain_weight=0
		for fermentable in self.fermentables:
			if fermentable.isGrain:
				total_grain_weight = total_grain_weight + (fermentable.qty )
				self.calclog = self.calclog + "mashwater:	fermentable: %s%s %s\n" %(fermentable.qty,fermentable.unit,fermentable.ingredient)

		mash_liquid = ( grain_thickness_ratio * ( ( total_grain_weight / 1000 ))) / ( 4 * metric_lb_kg_factor )  * metric_gal_l_factor 

		self.calclog = self.calclog + "mashwater: mash_liquid = %.3f\n" %( mash_liquid )
		self.calclog = self.calclog + "mashwater: %.3f = ( grain_thickness_ratio *  total_grain_weight ) / (4 * metric_lb_kg )  * metric_gal_l\n" %(mash_liquid)
		self.calclog = self.calclog + "mashwater: %.3f = ( %.3f *  %.3f ) / (4 * %.4f ) * %.4f\n" %(mash_liquid, grain_thickness_ratio,total_grain_weight/1000,metric_lb_kg_factor,metric_gal_l_factor)
		self.calclog = self.calclog + "mashwater: %.3f = ( %.4f ) / ( %.4f  ) * %.4f\n" %(mash_liquid, grain_thickness_ratio * total_grain_weight/1000,4*metric_lb_kg_factor,metric_gal_l_factor)
		self.calclog = self.calclog + "mashwater: %.3f =  %.4f  * %.4f\n" %(mash_liquid, (grain_thickness_ratio * total_grain_weight/1000) / (4*metric_lb_kg_factor),metric_gal_l_factor)
	

		mash_liquid_required = mash_liquid + self.hlt.dead_space
		self.calclog = self.calclog + "mashwater:  HLT Dead Space %.3f -> %.3f\n" %(self.hlt.dead_space,mash_liquid_required)
		self.calclog = self.calclog + "mashwater: Mash Water Required  %.3f\n" %(mash_liquid_required)




		
		grav_grain = self.calculateGravity(working_mash_size,grainOnly=1)
		self.estimated_grain_gravity = grav_grain
		self.calclog = self.calclog + "calcferm : \t\tgravity grain = %.4f\n" %( 1+(grav_grain/1000) )

		grav_adjunct = self.calculateGravity(working_mash_size,adjunctOnly=1)
		self.calclog = self.calclog + "calcferm : \t\tgravity adjunct = %.4f\n" %( 1+(grav_adjunct/1000) )
		estimated_gravity=grav_grain+grav_adjunct
		self.estimated_gravity = 1+(estimated_gravity/1000)
		self.estimated_og = 1+(estimated_gravity/1000)

		self.calclog = self.calclog + "calcferm : \t\testimated_gravity = %.4f\n" %( 1+(estimated_gravity/1000) )
		







		# 
		# Water Requirements
		#
		self.calclog = self.calclog + "waterreqd: Total Water Requirement:  %.3f\n" %(working_batch_size_G)
		self.calclog = self.calclog + "waterreqd: Mash Liquor Requirement:  %.3f\n" %(mash_liquid_required)
		sparge_water_required = working_batch_size_G - recipe.postBoilTopup - mash_liquid_required
		self.calclog = self.calclog + "waterreqd: Sparge Water Requirement:  %.3f\n" %(sparge_water_required)
		self.calclog = self.calclog + "waterreqd: Topup Water Requirement:  %.3f\n" %(recipe.postBoilTopup)


		### here we need to tweak the database to reset hte water require,emts
		# a bit of a workaround we re-add the water we last saw in the databae
		# although we could use a lookup on Items.

		foundWater=None
		ourWater = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND category = :3 AND processIngredient = False", username,recipeName,'water').fetch(5555)
		for water in ourWater:
			foundWater=water
			water.delete()
		ourWaterNeeds=0		
		ourTapWaterNeeds=0
		if not recipe.tap_mash_water:
			ourWaterNeeds=mash_liquid_required
			self.calclog = self.calclog + "waterreqd: our water needs = %.2f (MASH)\n" %(ourWaterNeeds)
		else:
			ourTapWaterNeeds=mash_liquid_required
			self.calclog = self.calclog + "waterreqd: our tap water needs = %.2f (MASH)\n" %(ourTapWaterNeeds)
		if not recipe.tap_sparge_water:	
			ourWaterNeeds=ourWaterNeeds+sparge_water_required
			self.calclog = self.calclog + "waterreqd: our water needs = %.2f (SPARGE)\n" %(ourWaterNeeds)
		else:
			ourTapWaterNeeds=ourTapWaterNeeds+sparge_water_required
			self.calclog = self.calclog + "waterreqd: our tap water needs = %.2f (SPARGE)\n" %(ourTapWaterNeeds)

		if not foundWater:
			self.calclog = self.calclog + "waterreqd: WARNING: unable to find a water ingredient to add\n"
		else:
			self.calclog = self.calclog + "waterreqd: added water ingredient %.2f\n" %(ourWaterNeeds)
			newWater= gIngredients(owner=username)
			for ri in foundWater.__dict__:
				if ri != "_entity":
					newWater.__dict__[ri] = foundWater.__dict__[ri]
			newWater.qty=float(ourWaterNeeds)
			newWater.put()	

		#if ourTapWaterNeeds:
		#	newWater= gIngredients(owner=username)
		#	for ri in foundWater.__dict__:
		#		if ri != "_entity":
		#			newWater.__dict__[ri] = foundWater.__dict__[ri]
		#	newWater.qty=float(ourWaterNeeds)
		#	newWater.put()



		# 
		# Final Gravity
		#
		self.calclog = self.calclog + "calcfgrav: Calculating Estimated Final Gravity\n"
		# This is could probably take a skew from mash temperature
		grain_fermentable_typical_pcnt = 0.62
		nongrain_fermentable_typical_pcnt=1
		
		grain = 0
		nongrain = 0
#		self.fermentables=ourFermentables.fetch(2000)
		for fermentable in self.fermentables:
			if fermentable.isGrain:
				grain = grain + fermentable.qty
			else:
				nongrain = nongrain + fermentable.qty
		
		grain_pcnt = grain / (grain + nongrain)
		nongrain_pcnt = nongrain / (grain + nongrain)

		self.grain_weight=grain
		self.nongrain_weight=nongrain


		if recipe.postBoilTopup > 0:
			# Calculating Dilution
			vol1= working_batch_size_B 
			vol2= recipe.postBoilTopup
			totalvol=vol1+vol2
			grav1= estimated_gravity
			grav2= 1.000
			g1 = (vol1/totalvol) * grav1
			g2 = (vol2/totalvol) * grav2
			diluted_gravity = g1 + g2
			self.calclog = self.calclog + "calcfgrav:  Wort expected gravity after dilution (%.3f L -> %.3f)\n" %(working_batch_size_B , working_batch_size_B+recipe.postBoilTopup)	
			self.calclog = self.calclog + "calcfgrav:     gravity = %.4f ->  %.4f\n" %((1+(estimated_gravity/1000)), (1 + (diluted_gravity /1000)))
		else:
			diluted_gravity = estimated_gravity

		fermentable_grain = (diluted_gravity * grain_pcnt * grain_fermentable_typical_pcnt) 
		fermentable_nongrain = (diluted_gravity * nongrain_pcnt * nongrain_fermentable_typical_pcnt)

		estimated_final_gravity = diluted_gravity - (1.23 * (fermentable_grain + fermentable_nongrain))

		self.calclog = self.calclog + "calcfgrav: \t\t estimated_final_gravity = %.4f\n" %(1+(estimated_final_gravity)/1000)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = 1 + (estimated_gravity - (1.23 * (fermentable_grain + fermentable_nongrain ))/1000 \n" %(1+(estimated_final_gravity)/1000)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = %s - (1.23 * (%.3f + %.3f ) \n" %(estimated_final_gravity,diluted_gravity,fermentable_grain,fermentable_nongrain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t fermentable_grain = %.3f\n" %(fermentable_grain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.3f = (estimated_gravity * grain_pcnt * grain_fermentable_typical_pnct)\n" %(fermentable_grain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.3f = (%.3f * %.3f * %.3f)\n" %(fermentable_grain,diluted_gravity,grain_pcnt,grain_fermentable_typical_pcnt)
		self.calclog = self.calclog + "calcfgrav: \t\t\t fermentable_nongrain = %.3f\n" %(fermentable_nongrain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.3f = (estimated_gravity * nongrain_pcnt * nongrain_fermentable_typical_pnct)\n" %(fermentable_grain)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.3f = (%.3f * %.3f * %.3f)\n" %(fermentable_nongrain,diluted_gravity,nongrain_pcnt,nongrain_fermentable_typical_pcnt)
	


		yeast_atten = 0
		yeast_count = 0	# need to research affect of multiple packets of yeast?
		for yeast in self.yeasts:
			yeast_atten = yeast_atten + yeast.atten
			yeast_count = yeast_count + 1

		if yeast_count == 0:
			self.calclog = self.calclog + "calcfgrav: \tWARNING: No YEAST in recipe setting a default attenuation 50\n"
			yeast_atten=0.60
		else:
			yeast_atten =( yeast_atten / yeast_count) / 100
			
		estimated_yeast_attenuation = diluted_gravity * (1-yeast_atten) 
		self.calclog = self.calclog + "calcfgrav: \t\t estimated_yeast_attenuation = %.4f\n" %( estimated_yeast_attenuation )

		for yeast in self.yeasts:
			self.calclog = self.calclog + "calcfgrav:\t\t\t yeast attenuation for %s %.3f \n" %(yeast.ingredient,yeast.atten/100)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = estimated_gravity * (1 - yeast_atten) \n" %( estimated_yeast_attenuation)
		self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = %.4f * (1 - %.3f) \n" %( estimated_yeast_attenuation, diluted_gravity, yeast_atten )

		if estimated_yeast_attenuation > estimated_final_gravity:
			estimated_final_gravity = estimated_yeast_attenuation
			self.calclog = self.calclog + "calcfgrav: \t\t Yeast Attenuation used for final gravity estimate\n"
		else:
			self.calclog = self.calclog + "calcfgrav: \t\t  used for final gravity estimate\n"

		#if estimated_final_gravity
		self.calclog = self.calclog + "calcabv  :\t\t Final Gravity Estimate = %.3f \n" %( 1+(estimated_final_gravity)/1000)

		self.calclog = self.calclog + "calcabv  : Alcohol By Volume\n"

		estimated_abv = ( ( 1 + (diluted_gravity)/1000 )  - ( 1+ (estimated_final_gravity)/1000) ) * 131
		self.calclog = self.calclog + "calcabv  :	abv = %.3f %%\n" %(estimated_abv)
		self.calclog = self.calclog + "calcabv  :	%.3f %% = ( original_gravity - final_gravity ) * 131\n" %(estimated_abv)
		self.calclog = self.calclog + "calcabv  :	%.3f %% = ( %.4f - %.4f ) * 131\n" %(estimated_abv, (1+(estimated_gravity/1000)), (1+(estimated_final_gravity/1000)  ))  


		self.estimated_abv = estimated_abv
		self.estimated_fg = 1+(estimated_final_gravity/1000)






		#
		# Calculate Hops
		#
		(self.estimated_ibu,weight) = self.calculateHops(working_hop_size,estimated_gravity,title="std",doContribution=1)
		self.calclog=self.calclog+"calchops : Old Hops Calculations (pre-Oct-2012) %.4f\n" %(self.old_estimated_ibu)

		HOP_MODELLING = []
		HOP_MODELS={}
		HOP_MODELLING.append(self.estimated_ibu)
		if not HOP_MODELS.has_key( self.estimated_ibu):	HOP_MODELS[ self.estimated_ibu ] = []
		HOP_MODELS[ self.estimated_ibu ].append('original')

		HOP_MODELLING.append(self.old_estimated_ibu)
		if not HOP_MODELS.has_key( self.old_estimated_ibu):	HOP_MODELS[ self.old_estimated_ibu ] = []
		HOP_MODELS[ self.old_estimated_ibu ].append('2011-09')





		#
		# Colour
		#
		self.calclog = self.calclog + "calcColor: Calculating Morey SRM Colours\n"
		self.calclog = self.calclog + "calcColor: http://www.brewingtechniques.com/brewingtechniques/beerslaw/morey.html\n"
#SRM = 1.4922 [(MCU) ^ 0.6859] - for values of SRM < 50

		total_srm = 0
		total_qty = 0
		sum_weighted_color = 0 
		grain_qty_pounds = 0

		for fermentable in self.fermentables:
			qty=fermentable.qty
			if fermentable.isGrain:
				total_qty = total_qty + qty
				color_srm = fermentable.colour * 0.508
				grain_qty_pounds = grain_qty_pounds + (qty / 1000 / 0.454)

				weighted_color = (qty / 1000 / 0.454) * color_srm
	
				self.calclog = self.calclog + "calcColor: \t\t color_srm = %s for %s\n" %(color_srm,fermentable.ingredient)
				self.calclog = self.calclog + "calcColor: \t\t\t %s = %.3f EBC * 0.8368  \n" %(color_srm, fermentable.colour)

				self.calclog = self.calclog + "calcColor: \t\t\t weighted_grain_color = %.2f \n" %(weighted_color )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (qty / 1000 / 0.454) * color_srm  \n" %(weighted_color )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (%s / 1000 / 0.454) * %.3f  \n" %(weighted_color,qty,color_srm )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (%s) * %.3f  \n" %(weighted_color,qty/1000/0.454,color_srm )

				# add this grain into our contributiosn table
				cont = gContributions( owner=username, recipeName=recipeName )
				cont.ingredientType="fermentables"
				cont.ingredient=fermentable.ingredient
				cont.gravity = 0.0
				cont.srm=weighted_color
				cont.put()



				sum_weighted_color = sum_weighted_color + weighted_color
				

		total_weighted_color = sum_weighted_color
		self.calclog = self.calclog + "calcColor: \t\t calculating colour based on = %.3f L \n" %(working_colour_size)
		self.calclog = self.calclog + "calcColor: \t\t total_weighted_color = %.2f \n" %(total_weighted_color)
		self.calclog = self.calclog + "calcColor: \t\t\t %.2f = sum(weighted_color)   \n" %(total_weighted_color )
		

		volume_gallons = ( working_colour_size ) / 3.785
		mcu = total_weighted_color / volume_gallons
		srm = 1.4922 * math.pow( mcu, 0.6859)

		self.calclog = self.calclog + "calcColor: \t\t estimated srm = %.1f\n" %(srm)
		self.calclog = self.calclog + "calcColor: \t\t\t %.1f = 1.4922 * mcu ^ 0.6859\n" %(srm)
		self.calclog = self.calclog + "calcColor: \t\t\t %.1f = 1.4922 * %.3f ^ 0.6859\n" %(srm,mcu)
		self.calclog = self.calclog + "calcColor: \t\t\t mcu = %.3f\n" %(mcu)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = weighted_grain_color / volume_gallons\n" %(mcu)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = %.3f / %.3f\n" %(mcu,total_weighted_color, volume_gallons)
		self.calclog = self.calclog + "calcColor: \t\t\t volume_gallons =  %.3f\n" %( volume_gallons)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = (%.3f) / 3.785\n" %(volume_gallons,working_colour_size)
		
		estimated_srm=srm			
		estimated_ebc=srm*1.97
		self.calclog = self.calclog + "calcColor: \t\t estimated ebc = %.1f\n" %(estimated_ebc)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = %.1f SRM * 1.97 \n" %(estimated_ebc,estimated_srm)
		self.estimated_ebc = estimated_ebc


		self.strike_temp = self.getStrikeTemperature()
		self.strike_temp_5 = self.strike_temp + 5	




		# Assumption built in that bottles are 500 ml
		bottle_size = 0.485	# ml
		self.bottles_required = math.floor( recipe.batch_size_required  / bottle_size )



	
		# 
		# Work out gravity throughout the process
		#
		self.calclog = self.calclog + "calcgrav : Calculating Gravity throughout the process\n" 


		self.estimated_postboilpostcool_gravity = estimated_gravity		# i.e. finish

		grav = self.calculateGravity(working_batch_size_C,grainOnly=0,adjunctOnly=0)
		self.estimated_postboilprecool_gravity = grav

		grav = self.calculateGravity(working_batch_size_D,grainOnly=0,adjunctOnly=0,title="All")
		self.estimated_preboil_gravity = grav

		grav = self.calculateGravity(working_batch_size_D,grainOnly=1,adjunctOnly=0,title="Grain")
		self.estimated_preboil_gravity_grain= grav




		self.calclog = self.calclog + "calcgrav :  Wort expected post boil post cool volume (%.3f L)\n" %(working_mash_size)	
		self.calclog = self.calclog + "calcgrav : \t\tgravity grain = %.4f\n" %( 1+(grav_grain/1000) )
		self.calclog = self.calclog + "calcgrav : \t\tgravity adjunct = %.4f\n" %( 1+(grav_adjunct/1000) )
		self.calclog = self.calclog + "calcgrav : \t\testimated_gravity = %.4f\n" %( 1+(estimated_gravity/1000) )
		
		self.calclog = self.calclog + "calcgrav :  Wort expected post boil pre cool volume (%.3f L)\n" %(working_batch_size_C)	
		self.calclog = self.calclog + "calcgrav :     gravity post boil / pre cool = %.4f\n" %(1 + (self.estimated_postboilprecool_gravity/1000))
		self.calclog = self.calclog + "calcgrav :  Wort expected pre boil volume (%.3f L)\n" %(working_batch_size_D)	
		self.calclog = self.calclog + "calcgrav :     gravity pre boil post adjunct = %.4f\n" %(1 + (self.estimated_preboil_gravity/1000))
		self.calclog = self.calclog + "calcgrav :     gravity pre boil pre adjunct = %.4f\n" %(1 + (self.estimated_preboil_gravity_grain/1000))


		if recipe.postBoilTopup > 0:
			# Calculating Dilution
			vol1= working_batch_size_B  - recipe.postBoilTopup
			vol2= recipe.postBoilTopup
			totalvol=vol1+vol2
			grav1= estimated_gravity
			grav2= 1.000
			g1 = (vol1/totalvol) * grav1
			g2 = (vol2/totalvol) * grav2
			diluted_gravity = g1 + g2

			self.calclog = self.calclog + "calcgrav :  Wort expected gravity after dilution (%.3f L -> %.3f)\n" %(working_batch_size_B -recipe.postBoilTopup, working_batch_size_B)	
			self.calclog = self.calclog + "calcgrav :     gravity post boil/coll topup = %.4f ->  %.4f\n" %((1+(estimated_gravity/1000)), (1 + (diluted_gravity /1000)))




		#
		# Time to heat in hot liquor tank
		#
		start_temp = 5
		end_temp= 77
		
		if not self.hlt.heatPower:
			self.calclog=self.calclog +"heatpower:\tWarning heat power not specified for HLT\n"
			hltheatpower=1700
		else:
			hltheatpower=self.hlt.heatPower
		heating_time =(4184.0 * sparge_water_required *(end_temp - start_temp ))/ hltheatpower / 1000.0 / 60.0 ;
		heating_time = int( heating_time + 0.5 )
	
		# Recipe Styles
		self.sparge_temp = 82			# note: the recommendation is 82 counting on some loss of temperature will still keep grain bed
							# temp less than 77... 77 is about the temp tannins are extracted

		self.calclog = self.calclog +"sparge   : Sparge Water Requried %.3f L\n" %(sparge_water_required)
		self.calclog = self.calclog +"sparge   :   - estimated heating time %.1f m\n" %(heating_time)
		



		





		#
		# Trying to determine kettle gravityies
		#
#		if recipe.postBoilTopup < 1:
		if 1==1:
			self.calclog = self.calclog + "midgrav  : EXPERIMENTAL MID GRAVITY\n"
			self.boilers = self._getEquipment(username,recipe.process,"boiler",True)
			self.calclog = self.calclog + "midgrav  : EXPERIMENTAL MID GRAVITY\n"
			MIDGRAVS=[]
			PASS=1
			working_boil_volume=working_batch_size_D	
			while working_boil_volume > 0:
				for boiler in self.boilers:
					if working_boil_volume > 0:
						if not boiler.boilVolume:
							sys.stderr.write("BOILER HAS NO VOLUME GIVING IT 40L\n")
							boiler.boilVolume=40.0
						working_boil_volume = working_boil_volume -boiler.boilVolume
						MIDGRAVS.append( [boiler.boilVolume,boiler.name,PASS])
						self.calclog = self.calclog + "midgrav  : volume for %s = %.1f\n" %(boiler.name,boiler.boilVolume)
				self.calclog = self.calclog + "midgrav  : leftover volume after pass %s = %.1f\n" %(PASS,working_boil_volume)
				PASS=PASS +1
			self.calclog = self.calclog + "midgrav  : need to use %s iterations of boiling\n" %(len(MIDGRAVS))

			
			ratio= self.estimated_gravity / (1+(self.estimated_preboil_gravity_grain/1000))
			self.calclog=self.calclog+"midgrav   : %.4f / %.4f\n" %(1+(self.estimated_preboil_gravity_grain/1000), self.estimated_gravity)
			self.calclog=self.calclog+"midgrav   : ratio of preboil vs post boil gravity.... %.4f\n" %(ratio)

			startVol=1
			for boilIteration in MIDGRAVS:	
				sys.stderr.write(boilIteration)
				self.calclog=self.calclog+"midgrav   : calculating mid grav for %s/%s  - %sL -> %sL\n" %(boilIteration[1],boilIteration[2],startVol,startVol+boilIteration[0])
				tmp = (self.calculateMidGravity(self.estimated_preboil_gravity_grain,int(startVol),int(startVol+boilIteration[0]) ))*ratio
				boilIteration.append(tmp)
				startVol=startVol+boilIteration[0]

			kettle_gravity = (self.estimated_preboil_gravity_grain) * ratio



			# determine where to put our hopts
			if len(MIDGRAVS) > 1:
				bittering_kettle_idx =  1
			else:
				bittering_kettle_idx = 0

			aroma_kettle_idx = len(MIDGRAVS)-1
			flameout_kettle_idx=len(MIDGRAVS)-1


			self.calclog = self.calclog+"hopmodel : Kettle for Bittering Hops %s/%s\n" %(MIDGRAVS[bittering_kettle_idx][1],MIDGRAVS[bittering_kettle_idx][2])
			self.calclog = self.calclog+"hopmodel : Kettle for Aroma Hops %s/%s\n" %(MIDGRAVS[aroma_kettle_idx][1],MIDGRAVS[aroma_kettle_idx][2])
			self.calclog = self.calclog+"hopmodel : Kettle for Flameout Hops %s/%s\n" %(MIDGRAVS[flameout_kettle_idx][1],MIDGRAVS[flameout_kettle_idx][2])




			# HOP MODEL X
			


			# assume that we have some proteins carried over from previous case 
			# in which case 
			

			self.calclog = self.calclog+"hopmodel : HOP MODEL X\n"
			batch=MIDGRAVS[ bittering_kettle_idx ][0]
			grav=MIDGRAVS[ bittering_kettle_idx ][3]
			self.calclog = self.calclog+"hopmodel : Gravity prediction for this kettle %.4f\n" %(1+(grav/1000))	
			grav=MIDGRAVS[ bittering_kettle_idx ][3] + MIDGRAVS[0][3] * .333
			self.calclog = self.calclog+"hopmodel : Gravity prediction for this kettle with some proteins from previous kettle %.4f\n" %(1+(grav/1000))	

			(hopsB,weightB) = self.calculateHops( batch,grav,title="bittering",doContribution=0,onlyHopAddAt=60)  
			self.calclog = self.calclog+"hopmodel :  Bittering Hops: Gravity %.4f\n" %(1+(grav/1000))
			self.calclog = self.calclog+"hopmodel :  Bittering Hops: Batch Size  %.2f\n" %(batch)
			self.calclog = self.calclog+"hopmodel :  Bittering Hops: Weight %.1f gm\n" %(weightB)
			self.calclog = self.calclog+"hopmodel :  Bittering Hops: %.1f IBU\n" %(hopsB)
		

	
			batch=MIDGRAVS[ aroma_kettle_idx ][0]
			grav=MIDGRAVS[ aroma_kettle_idx ][3]
			(hopsA,weightA) = self.calculateHops( batch,grav ,title="aroma",doContribution=0,onlyHopAddAt=15)  
			self.calclog = self.calclog+"hopmodel :  Aroma Hops: Gravity %.4f\n" %(1+(boilIteration[3])/1000 )
			self.calclog = self.calclog+"hopmodel :  Aroma Hops: Batch Size  %.2f\n" %(boilIteration[0])
			self.calclog = self.calclog+"hopmodel :  Aroma Hops: Weight %.1f gm\n" %(weightA)
			self.calclog = self.calclog+"hopmodel :  Aroma Hops: %.1f IBU\n" %(hopsA)

			batch=MIDGRAVS[ flameout_kettle_idx ][0]
			grav=MIDGRAVS[ flameout_kettle_idx ][3]
			(hopsF,weightF) = self.calculateHops( batch,grav ,title="flameout",doContribution=0,onlyHopAddAt=0.001 ) 
			self.calclog = self.calclog+"hopmodel :  Flameout Hops: Gravity %.4f\n" %(1+(boilIteration[3])/1000 )
			self.calclog = self.calclog+"hopmodel :  Flameout Hops: Batch Size  %.2f\n" %(boilIteration[0])
			self.calclog = self.calclog+"hopmodel :  Flameout Hops: Weight %.1f gm\n" %(weightF)
			self.calclog = self.calclog+"hopmodel :  Flameout Hops: %.1f IBU\n" %(hopsF)
		

			refined_ibu=0
			percentage=MIDGRAVS[ bittering_kettle_idx ][0]/working_batch_size_B
			this_refined_ibu = hopsB * percentage
			refined_ibu=refined_ibu+this_refined_ibu
			self.calclog = self.calclog+"hopmodel : Bittering %.1f IBU  of %.1f %% --> %.1f IBU \n" %(hopsB,percentage, this_refined_ibu)
			percentage=MIDGRAVS[ aroma_kettle_idx ][0]/working_batch_size_B
			this_refined_ibu = hopsA * percentage
			refined_ibu=refined_ibu+this_refined_ibu
			self.calclog = self.calclog+"hopmodel : Aroma %.1f IBU  of %.1f %% --> %.1f IBU \n" %(hopsA,percentage, this_refined_ibu)
			percentage=MIDGRAVS[ flameout_kettle_idx ][0]/working_batch_size_F
			this_refined_ibu = hopsF * percentage
			refined_ibu=refined_ibu+this_refined_ibu
			self.calclog = self.calclog+"hopmodel : Flameout %.1f IBU  of %.1f %% --> %.1f IBU \n" %(hopsF,percentage, this_refined_ibu)
			self.calclog = self.calclog+"hopmodel : Adjusted Total  %.1f IBU \n" %(refined_ibu)
					

		
			HOP_MODELLING.append( refined_ibu )
			if not HOP_MODELS.has_key( refined_ibu ):	HOP_MODELS[ refined_ibu] = []
			HOP_MODELS[ refined_ibu ].append('modelx')

			


		numHopModels=0
		sumHopModels=0
		for tmpModel in HOP_MODELS:
			for y in HOP_MODELS[tmpModel]:	
				numHopModels=numHopModels+1
				sumHopModels=sumHopModels+tmpModel
				self.calclog = self.calclog+"hopmodel : Hop Model: %s  -- %.2f\n" %(y,tmpModel)
		self.calclog = self.calclog+"hopmodel : Total Models: %s\n" %(numHopModels)
		self.calclog = self.calclog+"hopmodel :  Lowest IBU : %.2f - %s\n" %(min(HOP_MODELLING), HOP_MODELS[ min(HOP_MODELLING)] )
		self.calclog = self.calclog+"hopmodel :  Highest IBU : %.2f - %s\n" %(max(HOP_MODELLING), HOP_MODELS[ max(HOP_MODELLING)] )
		self.calclog = self.calclog+"hopmodel :  Mean IBU : %.2f\n" %(sumHopModels/numHopModels)




		#kettle1evaporation
		#kettle2evaporation
		#kettle3evaporation
		#gravityprecool
		#kettle1preboilgravity		# should be without adjunct
		#kettle2preboilgravity		# should be without adjunct
		#kettle3preboilgravity		# should be without adjunct


		if self.Process.fixed_boil_off > 0:
			self.kettle1evaporation = self.Process.fixed_boil_off/len(MIDGRAVS)
		else:
			try:
				sys.stderr.write(" MIDAGRAVS " %(MIDGRAVS))
				self.kettle1evaporation = MIDGRAVS[0][0]*(self.Process.percentage_boil_off/100)
			except:
				pass
		if self.Process.fixed_boil_off > 0:
			self.kettle2evaporation = self.Process.fixed_boil_off/len(MIDGRAVS)
		else:
			try:
				self.kettle2evaporation = MIDGRAVS[1][0]*(self.Process.percentage_boil_off/100)
			except:
				self.kettle2evaporation=0
		if self.Process.fixed_boil_off > 0:
			self.kettle3evaporation = self.Process.fixed_boil_off/len(MIDGRAVS)
		else:
			try:
				self.kettle3evaporation = MIDGRAVS[2][0]*(self.Process.percentage_boil_off/100)
			except:	
				self.kettle3evaporation=0



		self.kettle1preboilgravity = 1+(MIDGRAVS[0][2]/1000)
		try:
			self.kettle2preboilgravity = 1+(MIDGRAVS[1][2]/1000)
			self.kettle2volume = MIDGRAVS[1][0]
		except:
			self.kettle2preboilgravity = 0
			self.kettle2volume=0
		try:
			self.kettle3preboilgravity = 1+(MIDGRAVS[2][2]/1000)
			self.kettle3volume = MIDGRAVS[2][0]
		except:
			self.kettle3preboilgravity = 0
			self.kettle3volume = 0

		self.kettle1volume = MIDGRAVS[0][0]
		self.kettle1kettle2volume=self.kettle1volume+self.kettle2volume
		self.kettle1kettle2kettle3volume=self.kettle1volume+self.kettle2volume+self.kettle3volume
		#
		# Set attributes
		#

		# use diluted_gravity
		self.precool_og = self.estimated_postboilprecoolgravity = self.estimated_postboilprecool_gravity	
		self.pretopup_post_mash_og = self.estimated_preboil_gravity		# including grain/adjunct preboil post mash

		# these two are actually the same
		self.pretopup_estimated_gravity_grain	= self.estimated_preboil_gravity_grain	
		self.pretopup_post_mash_gravity = self.estimated_preboil_gravity_grain		# no adjunct just grain 
		self.pre_boil_gravity = self.estimated_preboil_gravity
		self.boil_vol=working_batch_size_D
		self.mash_liquid = mash_liquid_required
		self.mash_liquid_6 = mash_liquid_required +6
		self.sparge_water=sparge_water_required
		self.precoolfvvol=working_batch_size_C
		self.sparge_heating_time=heating_time
		self.water_in_boil=working_batch_size_D
		self.topupvol=recipe.postBoilTopup
		self.water_required = working_batch_size_G 
		self.calculated=1


		self.calclog=self.calclog +"stats    :\t precool_og = %.4f\n" %(self.precool_og)
		self.calclog=self.calclog +"stats    :\t postboilprecoolgravity = %.4f\n" %(self.precool_og) #same as last one
		self.calclog=self.calclog +"stats    :\t pretopup_post_mash_og = %.4f\n" %(self.pretopup_post_mash_og)
		self.calclog=self.calclog +"stats    :\t pretopup_estimataged_gravity_grain = %.4f\n" %(self.pretopup_estimated_gravity_grain)
		self.calclog=self.calclog +"stats    :\t pretopup_post_mash_gravity = %.4f\n" %(self.pretopup_post_mash_gravity)
		self.calclog=self.calclog +"stats    :\t pre_boil_gravity = %.4f\n" %(self.pre_boil_gravity) # including adjunction
		self.calclog=self.calclog +"stats    :\t preboil_gravity = %.4f\n" %(self.pre_boil_gravity) # same as above # includes adjuncts
		self.calclog=self.calclog +"stats    :\t mash_liquid = %.4f\n" %(self.mash_liquid)
		self.calclog=self.calclog +"stats    :\t sparge_water = %.4f\n" %(self.sparge_water)
		self.calclog=self.calclog +"stats    :\t precoolfvvol = %.4f\n" %(self.precoolfvvol)
		self.calclog=self.calclog +"stats    :\t sparge_heating_time = %.4f\n" %(self.sparge_heating_time)
		self.calclog=self.calclog +"stats    :\t water_in_boil = %.4f\n" %(self.water_in_boil)
		self.calclog=self.calclog +"stats    :\t topupvol = %.4f\n" %(self.topupvol)
		self.calclog=self.calclog +"stats    :\t water_required = %.4f\n" %(self.water_required)
		self.calclog=self.calclog +"stats    :\t bottles_required = %.1f\n" %(self.bottles_required)
		self.calclog=self.calclog +"stats    :\t number_boil_passes = %s\n" %(PASS)
		self.calclog=self.calclog +"stats    :\t kettle1volume = %.1f\n" %(self.kettle1volume)
		self.calclog=self.calclog +"stats    :\t kettle2volume = %.1f\n" %(self.kettle2volume)
		self.calclog=self.calclog +"stats    :\t kettle3volume = %.1f\n" %(self.kettle3volume)
		self.calclog=self.calclog +"stats    :\t kettle1kettle2volume = %.1f\n" %(self.kettle1kettle2volume)
		self.calclog=self.calclog +"stats    :\t kettle1kettle2kettle3volume = %.1f\n" %(self.kettle1kettle2kettle3volume)
		self.calclog=self.calclog +"stats    :\t kettle1preboilgravity = %.1f\n" %(self.kettle1preboilgravity)
		self.calclog=self.calclog +"stats    :\t kettle2preboilgravity = %.1f\n" %(self.kettle2preboilgravity)
		self.calclog=self.calclog +"stats    :\t kettle3preboilgravity = %.1f\n" %(self.kettle3preboilgravity)
		self.calclog=self.calclog +"stats    :\t kettle1evaporation = %.1f\n" %(self.kettle1evaporation)
		self.calclog=self.calclog +"stats    :\t kettle2evaporation = %.1f\n" %(self.kettle2evaporation)
		self.calclog=self.calclog +"stats    :\t kettle3evaporation = %.1f\n" %(self.kettle3evaporation)

		self.calclog=self.calclog+ "stats    :\t stike_temp_5 = %.1f\n" %(self.strike_temp_5)
		self.calclog=self.calclog +"stats    :\t mash_liquid_6 = %.4f\n" %(self.mash_liquid_6)
		self.calclog=self.calclog +"stats    :\t target_mash_temp = %.4f\n" %(self.target_mash_temp)
		self.calclog=self.calclog +"stats    :\t sparge_temp = %.4f\n" %(self.sparge_temp)
		self.calclog=self.calclog +"stats    :\t boil_vol = %.4f\n" %(self.boil_vol)
		self.calclog=self.calclog +"stats    :\t estimated_og = %.4f\n" %(self.estimated_og)
		self.calclog=self.calclog +"stats    :\t estimated_fg = %.4f\n" %(self.estimated_fg)
		self.calclog=self.calclog +"stats    :\t estimated_abv = %.4f\n" %(self.estimated_abv)
		self.calclog=self.calclog +"stats    :\t topupvol = %.4f\n" %(self.topupvol)
#		self.calclog=self.calclog +"stats    :\t minikegqty = %.0f\n" %(self.minikegqty)
#		self.calclog=self.calclog +"stats    :\t polypinqty = %.0f\n" %(self.polypinqty)
#		self.calclog=self.calclog +"stats    :\t num_crown_caps = %.0f\n" %(self.num_crown_caps)
#		self.calclog=self.calclog +"stats    :\t num_crown_caps = %.0f\n" %(self.num_crown_caps)
#		self.calclog=self.calclog +"stats    :\t primingsugarqty = %.0f\n" %(self.primingsugarqty)
#		self.calclog=self.calclog +"stats    :\t primingwater = %.0f\n" %(self.primingwater)
#		self.calclog=self.calclog +"stats    :\t primingsugartotal = %.0f\n" %(self.primingsugartotal)
		#
		# Recipe Summary
		#
		self.calclog = self.calclog + "recipe   : Batch Size %.0f L\n" %(recipe.batch_size_required)
		self.calclog=self.calclog+"recipe   : ABV %.4f\n" %(self.estimated_abv)
		if recipe.postBoilTopup > 0:
			self.calclog=self.calclog+"recipe   : OG %.4f\n" %(self.estimated_og)
		else:
			self.calclog=self.calclog+"recipe   : OG %.4f\n" %(self.estimated_og)
		self.calclog=self.calclog+"recipe   : FG %.4f\n" %(self.estimated_fg)
		self.calclog=self.calclog+"recipe   : IBU %.4f\n" %(self.estimated_ibu)
		self.calclog=self.calclog+"recipe   : EBC %.4f\n" %(self.estimated_ebc)

		for fermentable in self.fermentables:
			qty=fermentable.qty
			self.calclog=self.calclog+"recipe   : %.3f %s\n" %(qty,fermentable.ingredient)
		for hop in self.hops:
			qty=hop.qty
			self.calclog=self.calclog+"recipe   : %.3f %.3f %s\n" %(qty,hop.hopAddAt,hop.ingredient)





		# Recipe Size
		#self.calclog = self.calclog + "recipe   : Batch Size %.0f L\n" %(recipe.batch_size_required)












































	def combineGravity(self,vol1,vol2,grav1,grav2,title="cmbgrav  :"):
		totalvol=vol1+vol2
		g1 = (vol1/totalvol) * grav1
		g2 = (vol2/totalvol) * grav2

		self.calclog = self.calclog + "%s:  %.1f of %.4f + %.1f of %.4f = %.4f\n" %(title,vol1,1+(grav1/1000),vol2,1+(grav2/1000), 1+((g1+g2)/1000))
		return g1+g2






	def calculateMidGravity(self,estimated_gravity,start,finish):

		# first version - best guess
		a=-0.204253987405941
		b=-55.800303089625
		c=1.95650448603336
		d=-0.00707463851874897
		f=-0.0606677429146641

		# second version - from 2012-10-20
		A=-3.7885692517275777E+00
		B=-9.2260636949545088E+01
		C=2.7783471671973228E+00
		D=2.2200359241731124E-01
		F=-1.3401947980714043E-01


		

		

		self.calclog = self.calclog + "midgrav  : Calculating Gravity for %s -- %s of %.4f\n" %(start,finish,1+(estimated_gravity/1000))


		previous_vol=0
		previous_grav=0.00
		# BUG3972A: temporary workaround for small batches
		if finish-start < 1:
			updated_gravity=0
		else:
			for X in range(finish-start):
				x=start+X

				old_percentage_of_gravity = a*x/(b+x) + c*x/(d+x) + f*x
				percentage_of_gravity = A*x/(B+x) + C*x / (D+x) + F*x
	#					    y = A*x/(B+x) + C*x / (D+x) + F*x
	#http://zunzun.com/FitEquation/2/BioScience/Hyperbolic%20H/?RANK=1&unused=1350841566.65
		
				old_this_gravity = estimated_gravity * old_percentage_of_gravity
				this_gravity = estimated_gravity * percentage_of_gravity

				vol1= previous_vol
				vol2= 1
				totalvol=vol1+vol2
				grav1= previous_grav
				grav2= this_gravity
				g1 = (vol1/totalvol) * grav1
				g2 = (vol2/totalvol) * grav2
				updated_gravity = g1 + g2

				grav55=self.gravityTempAdjustment(55,1+(this_gravity/1000),-68)
				grav60=self.gravityTempAdjustment(60,1+(this_gravity/1000),-68)
				grav65=self.gravityTempAdjustment(65,1+(this_gravity/1000),-68)
				grav40=self.gravityTempAdjustment(40,1+(this_gravity/1000),-68)
				self.calclog = self.calclog + "midgrav  : %s - %.3f%%  %.4f ... %.4f (40/%.4f 55/%.4f 60/%.4f 65/%.4f [OLD %.3f - %.4f] \n" %(start+X,percentage_of_gravity,1+(this_gravity/1000),1+(updated_gravity/1000),grav40, grav55,grav60,grav65,   old_percentage_of_gravity,1+(old_this_gravity/1000) )
			
				previous_vol = previous_vol + 1
				previous_grav = updated_gravity



		self.calclog = self.calclog + "midgrav  : ... %.4f \n" %(1+(updated_gravity/1000) )

		return updated_gravity












	def calculateHops(self,working_hop_size,estimated_gravity,title="",doContribution=0,percentage=1,onlyHopAddAt=-1,tweakHopAddAt=-1):
		#
		# Hops Bitterness
		#
		self.calclog = self.calclog + "calchops : Calculating Tinseth Hop Calculation (%s)\n" %(title)
		self.calclog = self.calclog + "calchops : http://www.realbeer.com/hops/research.html\n"

		self.calclog = self.calclog + "calchops : \t Calculating with batch size of %.3f\n" %(working_hop_size)
		self.calclog = self.calclog + "calchops : \t  Using %.2f %% of hop weights\n" %(percentage)
		self.calclog = self.calclog + "calchops : \t  Using estimated_gravity %.4f\n" %(1+(estimated_gravity/1000))
	
		# if we have boiling/cooling loss specified then we should calculate the hops required based on the
		# evaporated value not the full boil volume
		working_total_hop_qty = {}

		# New Hop Structure 	
		# At this stage we wil lcalculate the IBU's with the *default* hop alpha acid.
		# but there is nothing to say we will get hops of this alpha from the store
		# therefore we should call "adjustHopAlphaQty()" to compenstate
		hop_utilisation_factors = {}

		grand_total_hop_weight=0
		
		self.hops_by_addition={}

		for tmp in self.hops:
			if tmp.hopAddAt == onlyHopAddAt or onlyHopAddAt == -1:
				if not self.hops_by_addition.has_key( tmp.hopAddAt ):
					self.hops_by_addition[ tmp.hopAddAt ] = []
				self.hops_by_addition[ tmp.hopAddAt ].append(tmp)
	
		for hopAddAt in self.hops_by_addition:
			hop_utilisation_factors[ hopAddAt ] = self._tinsethUtilisation( hopAddAt, estimated_gravity )
		if tweakHopAddAt>0:
			hop_utilisation_factors[ tweakHopAddAt ] = self._tinsethUtilisation( tweakHopAddAt, estimated_gravity )
	

	
		total_hop_ibu = 0
		for hopAddAt in self.hops_by_addition:
			for hop in self.hops_by_addition[ hopAddAt]:	
				hopqty = hop.qty * percentage

				# if we have *EVER* called adjustHopAlphaQty() then we should use the weighted hop alpha
				# average that was calculated last time that we adjusted the qty's of hops.
				# this is to ensure next time adjustHopAlpha is called we don't over/under scale
				HOP_ALPHA = hop.hopAlpha
				if self.hops_by_avg_alpha.has_key( hopAddAt):
					if self.hops_by_avg_alpha[ hopAddAt ].has_key( hop ):
						HOP_ALPHA = self.hops_by_avg_alpha[ hopAddAt ][ hop ]
					# this code is still safe with gql conversion but not entirely sure
					# what it was doing before	

				# Hop Qty hasn't been specified so we need to decide the weight
	


	
		#
		# Note: this isn't functional in the api... it has been disabled
		#

				if hopqty == 0  and 1==0:	
					if not working_total_hop_qty.has_key( hop ):
						working_total_hop_qty[ hop ] = 0

					#this_hop_ibu	*	batchsize		
					#19	*	15		
					#-------------------------------------------------------------------				
					#(utilisation facot		hop alpha		fixed
					#0.00211494	*	6	*	1000

					hop_required_ibu = self.hops_by_contribution[ hopAddAt ][ hop ]
					this_hop_weight = (hop_required_ibu * working_hop_size ) / (hop_utilisation_factors[ hopAddAt ] * HOP_ALPHA * 1000)

					self.hops_by_addition[ hopAddAt][ hop ] = this_hop_weight					
					working_total_hop_qty[ hop ] = working_total_hop_qty[ hop ] + this_hop_weight 

					this_hop_ibu = hop_utilisation_factors[ hopAddAt ] * (HOP_ALPHA * this_hop_weight * 1000 ) / working_hop_size
					self.calclog = self.calclog + "calchopsI: \t%.3f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.ingredient, hopAddAt)
					self.calclog = self.calclog + "calchopsI: \t\tthis_hop_weight = %.3f\n" %(this_hop_weight)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = ( this_hop_ibu * batch_size ) / (hop_utilisation_factor * hop_alpha * 1000))\n" %(this_hop_weight)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = ( %.3f * %.3f L ) / ( %.5f * %.3f * 1000))\n" %(this_hop_weight, hop_required_ibu, working_hop_size, hop_utilisation_factors[ hopAddAt ], HOP_ALPHA)
					self.calclog = self.calclog + "calchopsI: \t\tthis_hop_ibu = %.3f\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = hop_utilisation_factor * (hop_alpha * qty * 1000) / batch_size\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = %.8f * (%s * %s * 1000) / %s\n" %(this_hop_ibu,hop_utilisation_factors[ hopAddAt ], HOP_ALPHA, hopqty , working_hop_size)

					# if we have come in here with IBU not weight then we need to update the recipe
					

					grand_total_hop_weight=grand_total_hop_weight + hopqty

		
				# Hop Qty has been provided so determine the IBU as normal
				elif hopqty >0:
					if tweakHopAddAt > 0:
						this_hop_ibu = hop_utilisation_factors[ tweakHopAddAt ] * (HOP_ALPHA * hopqty * 1000 ) / working_hop_size 
					else:
						this_hop_ibu = hop_utilisation_factors[ hopAddAt ] * (HOP_ALPHA * hopqty * 1000 ) / working_hop_size 
					if not self.hops_by_contribution.has_key( hopAddAt):	self.hops_by_contribution[hopAddAt] = {}
					self.hops_by_contribution[ hopAddAt ][ hop ] = this_hop_ibu

					if tweakHopAddAt > 0:
						self.calclog = self.calclog + "calchopsW: \t%.3f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.ingredient, tweakHopAddAt)
					else:
						self.calclog = self.calclog + "calchopsW: \t%.3f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.ingredient, hopAddAt)
					self.calclog = self.calclog + "calchopsW: \t\tthis_hop_ibu = %.3f\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsW: \t\t\t %.3f = hop_utilisation_factor * (hop_alpha * qty * 1000) / batch_size\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsW: \t\t\t %.3f = %.8f * (%s * %s * 1000) / %s\n" %(this_hop_ibu,hop_utilisation_factors[ hopAddAt ], HOP_ALPHA, hopqty , working_hop_size)

					grand_total_hop_weight=grand_total_hop_weight + hopqty
				else:
					this_hop_ibu=0.0
		

				
				# add this hop ibu into our contributiosn table
				if doContribution==1:
					cont = gContributions( owner=self.username, recipeName=self.recipeName )
					cont.ingredientType="hops"
					cont.ingredient=hop.ingredient
					cont.hopAddAt = hopAddAt
					cont.ibu = this_hop_ibu
					cont.put()
				total_hop_ibu = total_hop_ibu + this_hop_ibu



		if len(working_total_hop_qty) > 0:
			self.hops=[]	
			for HOP in working_total_hop_qty:
				self.hops.append( ( HOP, working_total_hop_qty[ HOP ] ) )
				self.calclog = self.calclog + "calchopsI: \tUpdated Recipe Hop Qty %.3f %s %s \n" %( working_total_hop_qty[ HOP ], HOP.unit, HOP.name)

		self.calclog = self.calclog + "calchops : %.3f IBU = Estimated Total IBUs\n" %(total_hop_ibu)
		return (total_hop_ibu,grand_total_hop_weight)









	def calculateGravity(self,batchsize,adjunctOnly=0,grainOnly=0,title=""):
		#
		# Calcualte Grain Gravity
		#
		estimated_mash_gravity = 0
		total_contribution=0
		total_contribution_grain=0
		# Calculate Expected Gravity:
		# ppg X wt / batch size	
		self.calclog = self.calclog + "calcferm : Calculating expected %s gravity based on %.3f L\n" %(title,batchsize)
		for fermentable in self.fermentables:
			if (fermentable.isGrain and grainOnly == 1) or (not fermentable.isGrain and adjunctOnly == 1) or (adjunctOnly == 0 and grainOnly == 0):
				self.calclog = self.calclog + "calcferm :	fermentable: %s%s %s\n" %(fermentable.qty,fermentable.unit,fermentable.ingredient)
				self.calclog = self.calclog + "calcferm :		hwe: %s extract: %s\n" %(fermentable.hwe,fermentable.extract)
				contribution = (fermentable.qty /1000 * fermentable.hwe) / batchsize
				self.calclog = self.calclog + "calcferm : \t\t\tcontribution = %s\n" %(contribution)
				self.calclog = self.calclog + "calcferm : \t\t\t%s = %s * %s / %s\n" %(contribution, fermentable.qty/1000, fermentable.hwe , batchsize)
				if (fermentable.isGrain or fermentable.mustMash) and not fermentable.isAdjunct:
					self.calclog = self.calclog + "calcferm : \t\t\tIncluding in Mash Gravity\n"
					estimated_mash_gravity = estimated_mash_gravity + contribution
					total_contribution_grain = total_contribution_grain + contribution

				# add this grain into our contributiosn table
				cont = gContributions( owner=self.username, recipeName=self.recipeName )
				cont.ingredientType="fermentables"
				cont.ingredient=fermentable.ingredient
				cont.gravity =float( contribution * (self.recipe.mash_efficiency /100.0 ) )
				cont.srm=0.0
				cont.put()

				total_contribution = total_contribution + contribution	
		


		if grainOnly and not adjunctOnly:
			estimated_gravity_grain_100pcnt = total_contribution_grain 
			self.calclog = self.calclog + "calcferm : 	uncorrected gravity for grain %.3f\n" %(1+(estimated_gravity_grain_100pcnt / 1000))

			
			self.mash_efficiency = self.recipe.mash_efficiency	
			self.calclog = self.calclog + "calcferm :	correcting gravity based on mash efficiency of %s %%\n" %(self.mash_efficiency)
			estimated_gravity_grain = total_contribution_grain * (self.mash_efficiency / 100)
			self.estimated_gravity_grain = 1+( estimated_gravity_grain/1000)
			self.calclog = self.calclog + "calcferm : \t\testimated_gravity_grain = %s\n" %(estimated_gravity_grain)
			self.calclog = self.calclog + "calcferm : \t\t\t%.3f = %.3f * %.3f\n" %(estimated_gravity_grain,total_contribution, self.mash_efficiency/100)
			self.calclog = self.calclog + "calcferm : \t\t\t%.3f = 1 + (%.3f/1000) \n" %(1+(estimated_gravity_grain/1000),estimated_gravity_grain)	
			return estimated_gravity_grain


		if not adjunctOnly and not grainOnly:
			estimated_gravity_grain_100pcnt = total_contribution_grain 
			self.calclog = self.calclog + "calcferm : 	uncorrected gravity for grain %.3f\n" %(1+(estimated_gravity_grain_100pcnt / 1000))

			
			self.mash_efficiency = self.recipe.mash_efficiency	
			self.calclog = self.calclog + "calcferm :	correcting gravity based on mash efficiency of %s %%\n" %(self.mash_efficiency)
			estimated_gravity_grain = total_contribution_grain * (self.mash_efficiency / 100)
			self.estimated_gravity_grain = 1+( estimated_gravity_grain/1000)
			self.calclog = self.calclog + "calcferm : \t\testimated_gravity_grain = %s\n" %(estimated_gravity_grain)
			self.calclog = self.calclog + "calcferm : \t\t\t%.3f = %.3f * %.3f\n" %(estimated_gravity_grain,total_contribution, self.mash_efficiency/100)
			self.calclog = self.calclog + "calcferm : \t\t\t%.3f = 1 + (%.3f/1000) \n" %(1+(estimated_gravity_grain/1000),estimated_gravity_grain)	

			self.calclog = self.calclog + "calcferm : \t\testimated_gravity_nongrain = %s\n" %(total_contribution - total_contribution_grain )
			self.calclog = self.calclog + "calcferm : \t\testimated_gravity = (%.3f + %.3f)\n" %(estimated_gravity_grain,total_contribution - total_contribution_grain )
			self.calclog = self.calclog + "calcferm : \t\testimated_gravity = %.3f\n" %( estimated_gravity_grain + (total_contribution - total_contribution_grain) )

			return estimated_gravity_grain + (total_contribution - total_contribution_grain)


		else:
			self.calclog = self.calclog + "calcferm : \t\testimated_gravity_nongrain = %s\n" %(total_contribution - total_contribution_grain )
			return total_contribution-total_contribution_grain



	def waterRequirement(self,adjustment=0):
		"""
		Calculates the water requirement.


		"""
		self.calclog = self.calclog + "waterreqd: Calculating Water Requirement\n"

		self.calclog = self.calclog + "waterreqd: Batch Size Requried = %s L\n" %(self.batch_size_required)
		self.calclog = self.calclog + "waterreqd: Batch Size Requried (plus wastage)= %s L\n" %(self.batch_size_required_plus_wastage)
		percentage=1

		# waterRequirement is pretty much based without the topup
		# we add the topup back in at the end of waterRequirement()
		if self.recipe.postBoilTopup > 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage - self.recipe.postBoilTopup
			self.calclog = self.calclog +"waterreqd: TopUp Volum of %.3f --> %.3f L\n" %(self.recipe.postBoilTopup,self.batch_size_required_plus_wastage)
			
		total_extra_water = 0

		#waterRequirement()
		water_in_boil = 0

		#waterRequirmenet()	
		if adjustment != 0:
			total_extra_water = adjustment 
			self.calclog = self.calclog + "waterreqd: Manual Adjustment --> %s L water\n" %(adjustment)
	
		total_grain_weight = 0	
		for fermentable in self.fermentables:
			qty = fermentable.qty
			if fermentable.isGrain:
				if fermentable.unit != "gm":
					sys.stderr.write("critical: Water Requirement requires ferementables to be specified in grammes\n")
					sys.stderr.write("critical: unit was %s\n" %(fermentable.unit))
					sys.exit(2)
				self.calclog = self.calclog + "waterreqd:	fermentable: %s%s %s\n" %(qty,fermentable.unit,fermentable.ingredient)
				total_grain_weight = total_grain_weight + qty

		extra_water = total_grain_weight / 1000

		total_extra_water = total_extra_water + extra_water

		self.calclog = self.calclog + "waterreqd: Grain Weight = %s%s --> %s L water\n" %(total_grain_weight, fermentable.unit, extra_water )
	

		total_hop_weight = 0
		for hop in self.hops:
			hopqty = hop.qty * percentage
			self.calclog = self.calclog + "waterreqd:	hop: %s%s %s\n" %(hopqty,hop.unit,hop.ingredient)
			if hop.unit != "gm":
				sys.stderr.write("critical: Water Requirement requires hops to be specified in grammes\n")
				sys.stderr.write("critical: unit was %s\n" %(hop.unit))
				sys.exit(2)
			total_hop_weight = total_hop_weight + hopqty

		extra_water = ( total_hop_weight * 15 ) / 1000

		self.total_hop_weight=total_hop_weight

		if extra_water > self.boiler_Dead_Space:
			self.calclog = self.calclog +"waterreqd: Adding in hop weight for water because it is bigger than boiler deadspace\n"
			hop_extra_water = extra_water - self.boiler_Dead_Space
			total_extra_water = total_extra_water + extra_water

			# this was missing and probably the cause of the 1L drift
			water_in_boil = water_in_boil + extra_water
			self.calclog = self.calclog + "waterreqd: Hop Weight = %s%s --> %s L water\n" %(total_hop_weight, "gm", extra_water )
		else:
			hop_extra_water =0
			self.calclog = self.calclog +"waterreqd: Ingoring hop weight and using just boiler deadspace\n"




		extra_water = self.mash_tun.dead_space * 1
		total_extra_water = total_extra_water + extra_water 

		self.calclog = self.calclog + "waterreqd: Mash/Lauter Tun Deadspace = %s --> %s L water\n" %(self.mash_tun.dead_space,extra_water)

		extra_water = self.hlt.dead_space * 1
		total_extra_water = total_extra_water + extra_water
		self.calclog = self.calclog + "waterreqd: Hot Liquor Tank Deadspace = %s --> %s L water\n" %(self.hlt.dead_space,extra_water)




		batch_size = self.batch_size_required_plus_wastage

		if self.fermentation_bin.dead_space > 0:
			extra_water = self.fermentation_bin.dead_space
			batch_size = batch_size + extra_water
			total_extra_water = total_extra_water + extra_water
			self.calclog = self.calclog + "waterreqd: Fermentation Bin Deadspace--> %s L water\n" %(extra_water)
			# don't think we need to add the fermentation bin deadspace
			# as we now count fermentation bin deadspace in 
			# self.batch_size_required_plus_wastage
#				water_in_boil = water_in_boil + extra_water

		if self.racking_bucket.dead_space > 0:
			extra_water = self.racking_bucket.dead_space
			batch_size = batch_size + extra_water
			total_extra_water = total_extra_water + extra_water
			self.calclog = self.calclog + "waterreqd: Bottling Bin Deadspace--> %s L water\n" %(extra_water)


			#TODO: we don't count racking_bucket
#				water_in_boil = water_in_boil + extra_water


		if self.Process.fixed_cool_off > 0:
			extra_water = self.Process.fixed_cool_off 
			cooling_extra_water = extra_water
			total_extra_water = total_extra_water + extra_water

			water_in_boil = water_in_boil + extra_water

			self.calclog = self.calclog + "waterreqd: Cooling Loss (fixed %s) --> %s L water\n" %(self.Process.fixed_cool_off,extra_water)
		else:
			extra_water = batch_size * ( self.Process.percentage_cool_off / 100 ) 
			cooling_extra_water = extra_water
			total_extra_water = total_extra_water + extra_water
			self.calclog = self.calclog + "waterreqd: Cooling Loss (%s %%) --> %s L water\n" %(self.Process.percentage_cool_off,extra_water)

			water_in_boil = water_in_boil + extra_water
		
		batch_size_with_cool_off = self.batch_size_required_plus_wastage + extra_water

		if self.Process.fixed_boil_off > 0:
			extra_water = self.Process.fixed_boil_off 
			boiling_loss_extra_water = extra_water
			total_extra_water = total_extra_water + extra_water
			self.calclog = self.calclog + "waterreqd: Boiling Loss (fixed %s) --> %s L water\n" %(self.Process.fixed_boil_off,extra_water)

			water_in_boil = water_in_boil + extra_water

		else:
			extra_water = batch_size_with_cool_off * ( self.Process.percentage_boil_off / 100 ) 
			boiling_loss_extra_water = extra_water
			total_extra_water = total_extra_water + extra_water
			self.calclog = self.calclog + "waterreqd: Boiling Loss (%s %%) --> %s L water\n" %(self.Process.percentage_boil_off,extra_water)

			water_in_boil = water_in_boil + extra_water
		

		water_in_boil = water_in_boil + self.batch_size_required_plus_wastage


		self.calclog = self.calclog + "waterreqd: Total Additional Water Required %.3f L (in boil %.3f L)\n" %(total_extra_water,water_in_boil)
		self.calclog = self.calclog + "waterreqd: Total Water Required %.3f L \n" %(total_extra_water + self.batch_size_required_plus_wastage + self.recipe.postBoilTopup)
			
		self.water_in_boil = water_in_boil




		tmp = self.batch_size_required_plus_wastage 	# this is without topup as we remove the topup
								# at the start of waterRequirement()

		# set post_boil_volume before deductions
		self.post_boil_volume = water_in_boil
		self.post_boil_volume = self.post_boil_volume + self.fermentation_bin.dead_space
		self.post_boil_volume = self.post_boil_volume - self.recipe.postBoilTopup
		self.calclog = self.calclog + "waterreqd: post boil volume in boilers %.2f \n" %(self.post_boil_volume)
		self.post_boil_volume = self.post_boil_volume - hop_extra_water

#
#	Note: batch_size_required_with_wastage includes boiler deadspace already
#
#
#
#		# If the boiler deadspace is bigger than the hop then don't do it
		boilerDeadSpace=0
		for boiler in self.boilers:
#			self.calclog = self.calclog +"waterreqd: boiler %s dead space %.3f\n" %(boiler.name,boiler.dead_space)
			boilerDeadSpace = boilerDeadSpace + boiler.dead_space
#
#
#		if boilerDeadSpace > hop_extra_water:
#			self.post_boil_volume = self.post_boil_volume + hop_extra_water	
#			self.post_boil_volume = self.post_boil_volume - boilerDeadSpace
#			self.calclog = self.calclog +"waterreqd: ignoring hop watage and counting boilder deadspace\n"
#			self.water_in_boil = self.water_in_boil - hop_extra_water	
#			self.water_in_boil = self.water_in_boil + boilerDeadSpace
#			
#		else:
#			self.calclog = self.calclog +"waterreqd: ignoring boiler deadspace and counting hop wastage\n"
#
#	because boiler dead space is already included we will only add in hops soakage if its bigger than 
#	the loss to the boiler deadspace
#
#

		if boilerDeadSpace < hop_extra_water:
			self.post_boil_volume = self.post_boil_volume - (hop_extra_water - boilerDeadSpace)
			self.calclog = self.calclog +"waterreqd: taking off %.2f to account for extra hop loss\n" %(hop_extra_water-boilerDeadSpace)
		else:
			self.calclog = self.calclog +"waterreqd: not counting any hops as boiler deadspace higher\n"
			self.calclog = self.calclog +"waterreqd: boiler deadspace %.2f\n" %(boilerDeadSpace)

		self.calclog = self.calclog + "waterreqd: post boil volume in fv/precooling %.2f \n" %(self.post_boil_volume)
		self.post_boil_volume = self.post_boil_volume - cooling_extra_water
		self.calclog = self.calclog + "waterreqd: post boil volume in fv/cooled %.2f \n" %(self.post_boil_volume)

		availableOutOfFV=self.post_boil_volume - self.fermentation_bin.dead_space
		self.calclog = self.calclog + "waterreqd: available out of fv %.2f \n" %(availableOutOfFV)


		self.calclog = self.calclog + "waterreqd: InFV = batchSize + FV_Deadspace\n"
		inFV = self.batch_size_required + self.fermentation_bin.dead_space
		self.calclog = self.calclog + "waterreqd: %.2f = %.2f + %.4f\n" %(inFV, self.batch_size_required, self.fermentation_bin.dead_space)

#		inBoiler2 = inFV 
#		if hop_extra_water > boilerDeadSpace:
#			inBoiler2 = inBoiler2 + hop_extra_water
#		else:
#			inBoiler2 = inBoiler2 + boilerDeadSpace
#		inBoiler2 = inBoiler2 + cooling_extra_water

#		self.calclog = self.calclog + "waterreqd: inboiler2 = inFV + max( ((hop_weight*15)/1000), boiler_deadspace) + colling_shrinkage\n"

#		self.calclog = self.calclog + "waterreqd: %.2f = %.2f + max( %.2f , %.2f) + %.2f \n" %(inBoiler2,inFV,hop_extra_water,boilerDeadSpace,cooling_extra_water )
#
#		self.calclog = self.calclog +"DONT FORGET OT FIX THIS\n"
#
#		inBoiler1 = inBoiler2  + boiling_loss_extra_water
#		self.calclog = self.calclog + "waterreqd: inboiler1 = inboiler2 * evaporation\n"
#		self.calclog = self.calclog + "waterreqd: %.2f = %.2f + %.2f " %(inBoiler1,inBoiler2,boiling_loss_extra_water)
##
		# now add back in the topup
		if self.recipe.postBoilTopup> 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + self.recipe.postBoilTopup




		# 2012-10-09 correction 
		return total_extra_water + self.batch_size_required_plus_wastage + self.recipe.postBoilTopup







	def getStrikeTemperature(self):
		#NOTE: These equations also work for degrees Celsius, liters and kilograms. The only difference is that the thermodynamic constant of .2 changes to .41.

		#Strike Water Temperature Tw = (.2/r)(T2 - T1) + T2
		#where:
		#r = The ratio of water to grain in quarts per pound.
		#Wa = The amount of boiling water added (in quarts).
		#Wm = The total amount of water in the mash (in quarts).
		#T1 = The initial temperature (F) of the mash.
		#T2 = The target temperature (F) of the mash.
		#T w = The actual temperature (F) of the infusion water.
		#G = The amount of grain in the mash (in pounds).		
		self.calclog = self.calclog + "striketmp: Calculating Strike Temperature\n"
		self.calclog = self.calclog + "striketmp: http://www.howtobrew.com/section3/chapter16-3.html\n"

		#1 US quart = 0.946352946 litres
		#1.18294118 

		
		strike_temp = ( ( .41 / self.recipe.mash_grain_ratio) * ((self.recipe.target_mash_temp + self.recipe.target_mash_temp_tweak)  - self.recipe.initial_grain_temp) ) + self.recipe.target_mash_temp
		self.target_mash_temp=self.recipe.target_mash_temp
		
		self.calclog = self.calclog + "striketmp:\t strike_temp = %.3fC\n" %(strike_temp) 
		self.calclog = self.calclog + "striketmp:\t\t %.3fC = ( ( .41 / mash_grain_ratio ) * (target_mash_temp - initial_grain_temp) ) + target_mash_temp\n" %(strike_temp) 
		self.calclog = self.calclog + "striketmp:\t\t %.3fC = ( ( .41 / %.2f ) * (%.3fC - %.3fC) ) + %.3fC\n" %(strike_temp,self.recipe.mash_grain_ratio,(self.recipe.target_mash_temp + self.recipe.target_mash_temp_tweak),self.recipe.initial_grain_temp,self.recipe.target_mash_temp) 
		
		return strike_temp
		




	def _tinsethUtilisation(self,hop_boil_time=60,estimated_gravity=50):
		""" Executes the tinseth algorithim for hops
			hop_boil_time		- time in minutes
			estimated_gravity	-	degress (e.g. 50, no 1.050)
		"""


		bigness_factor = 1.65 * math.pow(0.000125, (1+(estimated_gravity)/1000)-1)
		boil_time_factor= (1 - math.exp(-0.04 * hop_boil_time) ) / 415
		hop_utilisation = bigness_factor * boil_time_factor 

		self.calclog = self.calclog + "tinseth  :	hop_utilisation = %.4f for %.4f @ %s m \n" %(hop_utilisation,1+(estimated_gravity/1000),hop_boil_time )
#		self.calclog = self.calclog + "         :	%.4f = fG * fT \n" %(hop_utilisation )
		self.calclog = self.calclog + "tinseth  :	%.4f = %.4f * %.4f \n" %(hop_utilisation,bigness_factor ,boil_time_factor )
		self.calclog = self.calclog + "tinseth  : \t\tbigness_factor = %.4f\n" %(bigness_factor )
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = 1.65 * 0.000125 ^ ( 1 + estimated_gravity / 1000 )\n" %(bigness_factor)
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = 1.65 * 0.000125 ^ (%.4f - 1 )\n" %( bigness_factor , 1+(estimated_gravity)/1000)
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = 1.65 * %.4f\n" %( bigness_factor , math.pow(0.000125, estimated_gravity/1000 )    )  
		self.calclog = self.calclog + "tinseth  : \t\tboil_time_factor = %.4f\n" %(boil_time_factor)
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = ( 1 - e ^ (-0.04 * hop_boil_time) ) / 415 \n" %(boil_time_factor)
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = ( 1 - e ^ (-0.04 * %s) ) / 415 \n" %(boil_time_factor,hop_boil_time)
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = ( 1 - e ^ (%s) ) / 415 \n" %(boil_time_factor,(-0.04*hop_boil_time))
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = ( 1 - %s ) / 415 \n" %(boil_time_factor, math.exp((-0.04*hop_boil_time))) 
		self.calclog = self.calclog + "tinseth  : \t\t\t %.4f = ( %s ) / 415 \n" %(boil_time_factor, 1-(math.exp((-0.04*hop_boil_time))) )

		return hop_utilisation



	def _getEquipment(self,username,process,equipment,multiple=False):
		ourEquipment = db.GqlQuery("SELECT * FROM gEquipment WHERE owner = :1 AND process = :2 AND equipment = :3 ORDER BY volume DESC", username,process,equipment)
		equipments =ourEquipment.fetch(100)
		if multiple:
			return equipments
		else:
			try:
				return equipments[0]
			except:
				return None


	def cloneRecipe(self,username,recipeOrigName,recipeNewName):
		sys.stderr.write("cloneRecipe %s/%s\n" %(recipeOrigName,recipeNewName))

		status=0

		try:
			ourRecipes = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeNewName)
			for recipe in ourRecipes.fetch(2000):
				recipe.delete()

			ourRecipes = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeOrigName)
			for recipe in ourRecipes.fetch(2000):
				R=gRecipes(recipename=recipeNewName,owner=username )
				for ri in recipe.__dict__:
					if ri != "_entity" and ri != "recipename":
						R.__dict__[ri] = recipe.__dict__[ri]
				R.recipename=recipeNewName
				R.put()	

			ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient=False", username,recipeNewName)
			for ingredient in ourIngredients.fetch(2000):
				ingredient.delete()


			ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient=False", username,recipeOrigName)
			for ingredient in ourIngredients.fetch(2000):
				sys.stderr.write("IIII %s\n" %(ingredient.ingredient))
				I=gIngredients(recipename=recipeNewName,owner=username )
				for ii in ingredient.__dict__:
					if ii != "_entity" and ii != "recipename":
						I.__dict__[ii] = ingredient.__dict__[ii]
				I.recipename=recipeNewName
				I.put()	


			# fix for broken recipes
			errstatus = self.doCalculate(username,recipeNewName)	#calculate new rceipe
			errstatus = self.compile(username,recipeNewName,None)  #compile new recipe

			status=1
		except:
			sys.stderr.write("EXCEPTION in cloneRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'cloneRecipe', 'status' : status ,'json':{}}


	def calculateRecipeWrapper(self,username,recipeName,activeCategory=""):
		sys.stderr.write("calculateRecipeWrapper %s/%sn" %(recipeName,activeCategory))
		self.calculateRecipe(username,recipeName)
		self.compile(username,recipeName,None)
		tmp = self.viewRecipe(username,recipeName,activeCategory,1)
		
		sys.stderr.write("Returning %s\n" %(tmp['json']))
		return {'operation' : 'calculateRecipeWrapper','status':1,'json' : tmp['json'] }
	

	def calculateRecipe(self,username,recipeName):
		sys.stderr.write("calculateRecipe-> %s/.\n" %(recipeName))
		status=0
		try:
			result={}

			errstatus = self.doCalculate(username,recipeName)
			result['calclog']=self.calclog	
			status=1
			return {'operation' : 'calculateRecipe', 'status' : status ,'json':json.dumps( result ) }


		except:
			sys.stderr.write("EXCEPTION in calculateRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'calculateRecipe', 'status' : status }



	def deleteRecipe(self,username,recipeName):
		sys.stderr.write("deleteRecipe-> %s....\n" %(recipeName))
		status=0
		try:
			result={}


			ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient=False",username,recipeName)
			ingredient = ourIngredients.fetch(10000)
			for i in ingredient:	i.delete()

			ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2",username,recipeName)
			recipe = ourRecipe.fetch(10000)
			for r in recipe:	r.delete()

			status = 1

		

		except:
			sys.stderr.write("EXCEPTION in deleteRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'deleteRecipe', 'status' : status }






	def changeItemInRecipe(self,username,recipeName,category,item,newqty,hopAddAt="0",doRecalculate="1"):
		sys.stderr.write("changeItemFromRecipe-> recipeName %s/ category %s/%s/%s/%s....\n" %(recipeName,category,item,newqty,hopAddAt))
		status=0
		try:
			result={}
	
#			if hopAddAt.count("_____")ddd:
#				hopAddAt = item.split("_____")[1]
#				item = item.split("_____")[0]
#			sys.stderr.write("%s\n" %(item.split("_____")))	
			if category == "Hops" or category=="hops":		# this is set as hops in android client not Hops
				sys.stderr.write(":2 %s\n" %(recipeName))
				sys.stderr.write(":3 %s\n" %(item))
				sys.stderr.write(":4 %s\n" %(hopAddAt))
				sys.stderr.write(":5 %s\n" %(category.lower()))
				ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND hopAddAt = :4 AND ingredientType = :5 AND processIngredient=False",username,recipeName,item,float(hopAddAt),category.lower())
			else:
				sys.stderr.write(":2 %s\n" %(recipeName))
				sys.stderr.write(":3 %s\n" %(item))
				sys.stderr.write(":4 %s\n" %(category.lower()))
				ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND ingredientType= :4 AND processIngredient=False",username,recipeName,item,category.lower())
			ingredient = ourIngredients.fetch(100)
			for i in ingredient:	#i.delete()
				i.qty=float(newqty)
				if doRecalculate == "0":	i.calculationOutstanding=True
				i.put()

			status = 1

			sys.stderr.write("it looks as if we have got as far as resetting the item qty\n")
			
			if doRecalculate == "1":
				errstatus = self.doCalculate(username,recipeName)
				errstatus = self.compile(username,recipeName,None)
				result['calclog']=self.calclog

			tmp = self.viewRecipe(username,recipeName,category,1)

			return {'operation' : 'changeItemInRecipe', 'status' : status ,'json': tmp['json'] }



		except:
			sys.stderr.write("EXCEPTION in changeItemInRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'changeItemInRecipe', 'status' : status }



	def fixRecipe(self,username,recipeName,category="<NULL>"):
		sys.stderr.write("fixRecipe-> %s/%s....\n" %(recipeName,category))
		status=0
		try:
			result={}
			
			# delete ingredients which have been deleted
			ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND qty < :3",username,recipeName, 0.005)
			for ingredient in ourIngredients.fetch(1000):
				ingredient.delete()


			# work through ingredients and set originalqty to qty
			ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND qty > :3",username,recipeName, 0.000)
			for ingredient in ourIngredients.fetch(1000):
				ingredient.originalqty=ingredient.qty
				ingredient.put()


			# copy recipestats
			ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2",username,recipeName).fetch(1)[0]
			
			ourStats = db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner= :1 AND recipe = :2 AND process = :3",username,recipeName,ourRecipe.process).fetch(1)[0]
			ourRecipe.estimated_abv = ourStats.estimated_abv
			ourRecipe.estimated_ibu = ourStats.estimated_ibu
			ourRecipe.estimated_fg = ourStats.estimated_fg
			ourRecipe.estimated_og = ourStats.estimated_og
			ourRecipe.put()

			errstatus = self.doCalculate(username,recipeName)
			self.compile(username,recipeName,None)




			tmp = self.viewRecipe(username,recipeName,category,1)
			return {'operation' : 'fixRecipe', 'status' : status ,'json':tmp['json'] }


		except:
			sys.stderr.write("EXCEPTION in fixRecipe \n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'fixRecipe', 'status' : status }



	def deleteItemFromRecipe(self,username,recipeName,category,item,hopAddAt=0):
		sys.stderr.write("deleteItemFromRecipe-> %s/%s/%s/%s....\n" %(recipeName,category,item,hopAddAt))
		status=0
		try:
			result={}
			
			if category=="Hops":
				ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND hopAddAt = :4 AND ingredientType = :5 AND processIngredient=False",username,recipeName,item,float(hopAddAt),category.lower())
			else:
				ourIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND ingredientType= :4 AND processIngredient=False",username,recipeName,item,category.lower())
			ingredient = ourIngredients.fetch(100)
			for i in ingredient:	i.delete()

			status = 1

			errstatus = self.doCalculate(username,recipeName)
		
			result['calclog']=self.calclog
			tmp = self.viewRecipe(username,recipeName,category,1)
			self.compile(username,recipeName,None)
#			return {'operation' : 'calculateRecipeWrapper','status':1,json:tmp['json']}
			return {'operation' : 'deleteItemFromRecipe', 'status' : status ,'json':tmp['json'] }


		except:
			sys.stderr.write("EXCEPTION in deleteItemFromRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'deleteItemFromRecipe', 'status' : status }



	def addItemToRecipe(self,username,recipeName,category,item,qty,hopAddAt=0,doRecalculate="1"):

		sys.stderr.write("addItemToRecipe-> %s/%s/%s/%s/%s....\n" %(recipeName,category,item,qty,hopAddAt))
		status = 0		
		
		try:
			result={}


#			ourPresets = db.GqlQuery("SELECT * FROM gIngredients WHERE ingredient = 'Green Bullet' AND recipename = :1",recipeName)
#			preset = ourPresets.fetch(1)
#			for p in preset:	p.delete()

			ourPresets = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2 AND name = :3", username,category.lower(), item)
			preset = ourPresets.fetch(1)
			if not len(preset) == 1:	
				sys.stderr.write("Cannot find the preset\n")
				return {'operation' : 'addItemToRecipe', 'status' : status  }



			if category == "Hops" or category == "hops":
				ourExistingIngredient = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND ingredient = :4 AND hopAddAt = :5 AND processIngredient=False",username,recipeName,category.lower(),item,hopAddAt)
			else:
				ourExistingIngredient = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND ingredient = :4 AND processIngredient=False",username,recipeName,category.lower(),item)
			existingIngredients = ourExistingIngredient.fetch(1)


			sys.stderr.write("len(existingIngredients) %s\n" %(len(existingIngredients)))
			sys.stderr.write(" preset[0].hopAlphas %s\n" %(preset[0].hopAlpha))
			sys.stderr.write(" category %s\n" %(category))

			if len(existingIngredients) > 0:
				I = existingIngredients[0]
				I.qty = I.qty + float(qty)
				sys.stderr.write("merging")
			else:	
				I=gIngredients(recipename=recipeName,owner=username )
				I.ingredientType=category.lower()
				I.unit=preset[0].unit
				I.ingredient=item
				I.processIngredient=False
				if category == "Yeast" or category == "yeast":			
					I.atten=preset[0].atten
				if category == "Hops" or category =="hops":
					I.hopAlpha=preset[0].hopAlpha
					I.hopUse=preset[0].hopUse
					I.hopForm=preset[0].hopForm
					I.hopAddAt=float(hopAddAt)
				if category == "Fermentables" or category == "fermentables":	
					I.isAdjunct=preset[0].isAdjunct
					I.mustMash=preset[0].mustMash
					I.isGrain=preset[0].isGrain
					I.hwe=preset[0].hwe
					I.extract=preset[0].extract

					I.colour=preset[0].colour	
			
				sys.stderr.write("QTY %s\n\n" %(qty))
				I.qty=float(qty)
				I.originalqty=0.0
			I.put()
			status = 1



			ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				if doRecalculate == "0":	recipe.calculationOutstanding=True
				recipe.put()

			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)

				result['calclog']=self.calclog


			tmp = self.viewRecipe(username,recipeName,category,1)
			return {'operation' : 'addItemToRecipe', 'status' : status ,'json': tmp }



		
		except:
			sys.stderr.write("EXCEPTION in addItemToRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'addItemToRecipe', 'status' : status }





	def compile(self,username,recipeName,brewlog):
		"""	
		Compile the process, do things like auto gather equipment/ingredients/consumables
		Auto Generate the Gather Step for an activity 

		If passed a recipe object a calculation will be carried out in quiet mode

		An optional brewlog (which has stock) can be passed which enables the "best before" work to happen
		if we are passed a brewlog then we will add keys to the "completes"


		agent: cli or web
		
		web can be api or web


		"""
		sys.stderr.write("compile %s %s\n" %(recipeName,brewlog))

		errstatus = self.doCalculate(username,recipeName)
		sys.stderr.write("do we have a proesss/s.sd.f.sdfnksdkfhsdklfh\n")
		sys.stderr.write("prcoess %s\n " %(self.Process.process))
		
		if not brewlog:	
			# return early as we don't have a  brewlog and can only look at
			# defaults. calculateRecipeWrapper() calls this for one
			return
		"""
		precoolfvvolume

		primingwater	/priming_sugar_water
		pre_boil_gravity
		primingsugarqty
		num_crown_caps
		primingsugartotal
		"""
		
		ssnum=9999

		ourCompiledSteps =db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner= :1 AND brewlog = :2 AND compileStep = :3",username,brewlog,True).fetch(324234)
		for ocs in ourCompiledSteps:	ocs.delete()


		ourActivities = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum = :3", username,self.Process.process,-1).fetch(324234)
		for activity in ourActivities:

			ourSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process= :2 AND activityNum = :3 AND subStepNum = :4",username,self.Process.process,activity.activityNum,-1).fetch(324234)
			for step in ourSteps:

				hop_labels = {60:'Copper (60min)',15:'Aroma (15min)',5:'Finishing (5min)',0.000001:'Flameout (0min)'}

				if step.auto:

					#gatherthegrain replaces grainqty and is in addStockToBrewlog



					if step.auto == "sterilise":
						ourEquipment = db.GqlQuery("SELECT * FROM gEquipment WHERE owner = :1 AND process = :2",username,self.Process.process).fetch(32434)
#						if len(activity.equipment) == 0:
#							step.newSubStep( ("No Equipment Required",{}) )
#						else:
						if len(ourEquipment):
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Sterilise %s pieces of equipment" %(len(ourEquipment))
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1

							for item in activity.equipment:
								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
								estep.compileStep=True
								estep.stepName=" - %s" %(item.name)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1
									# no such thing as subeqipment anymore
								#step.newSubStep( ( "  %s"  %(item.name) , {}  )  )
								#for subequip in item.subEquipment:
								#	step.newSubStep( ( "    %s" %(subequip.name), {}) )





					elif step.auto == "addadjuncts":
			
						hopaddsorted= []		
						ourRecipe = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND isAdjunct = :3", username,recipeName,True).fetch(4344)
		
						for recipe in ourRecipe:

							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Add %.1f%s of %s adjuncts" %(recipe.qty,recipe.unit,recipe.ingredient)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1


						ourCopperFining = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1




					elif step.auto == "hopmeasure_v3":
			
						hopaddsorted= []		
						ourRecipeHops = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
								HOPS[orh.hopAddAt]=[]
								HOPS[orh.hopAddAt].append( orh )
								hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()

						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								
								percentage = 1
								hopqty = hop.qty * percentage

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
								estep.compileStep=True
								estep.stepName="Measure %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1




					elif step.auto == "hopaddAroma_v3":
			
						hopaddsorted= []		
						ourRecipeHops = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
								if orh.hopAddAt <= 30:
									HOPS[orh.hopAddAt]=[]
									HOPS[orh.hopAddAt].append( orh )
									hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()

						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								
								percentage = 1
								hopqty = hop.qty * percentage

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1



						ourCopperFining = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1





						ourAromaFlavourings = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"flavouring").fetch(32434)
						for aroms in ourAromaFlavourings:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the kettle to add aroma." %(aroma.qty,aroma.unit,aroma.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1







					elif step.auto == "hopaddBittering_v3":
			
						hopaddsorted= []		
						ourRecipeHops = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
								if orh.hopAddAt > 30:
									HOPS[orh.hopAddAt]=[]
									HOPS[orh.hopAddAt].append( orh )
									hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()

						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								
								percentage = 1
								hopqty = hop.qty * percentage

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1



						ourCopperFining = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1








					elif step.auto == "hopaddBitteringAroma_v3":
			
						hopaddsorted= []		
						ourRecipeHops = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
								if orh.hopAddAt > 30:
									HOPS[orh.hopAddAt]=[]
									HOPS[orh.hopAddAt].append( orh )
									hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()

						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								
								percentage = 1
								hopqty = hop.qty * percentage

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1



						ourCopperFining = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1





						ourAromaFlavourings = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"flavouring").fetch(32434)
						for aroms in ourAromaFlavourings:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the kettle to add aroma." %(aroma.qty,aroma.unit,aroma.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1



					else:
						sys.stderr.write("Unable to complete the logic for step.auto %s\n" %(step.auto))
			




		sys.stderr.write("doRecipeStats %s %s %s\n" %(username,self.Process.process,recipeName))
		ourStats = db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND process = :2 AND recipe= :3",username,self.Process.process,recipeName).fetch(4324)
		for stat in ourStats:	stat.delete()

		stat = gRecipeStats(owner=username,process=self.Process.process,recipe=recipeName)
		stat.strike_temp = float(self.strike_temp)
		stat.strike_temp_5 = float(self.strike_temp_5)
		stat.postboil_precool_og=float(self.precool_og)
		stat.pretopup_estimated_gravity_grain=float(self.pretopup_estimated_gravity_grain)
		stat.sparge_temp = float(self.sparge_temp)
		stat.pretopup_post_mash_og=float(self.pretopup_post_mash_og)
		stat.sparge_water = float(self.sparge_water)
		stat.target_mash_temp=float(self.target_mash_temp)
		stat.precoolfvvolume=float(self.precoolfvvol)
		stat.pre_boil_gravity=float(self.pre_boil_gravity)
		stat.estimated_og=float(self.estimated_og)
		stat.estimated_fg=float(self.estimated_fg)
		stat.estimated_ibu = float(self.estimated_ibu)
		stat.estimated_abv=float(self.estimated_abv)
		stat.mash_liquid=float(self.mash_liquid)
		stat.mash_liquid_6=float(self.mash_liquid+6)
		stat.sparge_heating_time=float(self.sparge_heating_time)
		stat.boil_vol=float(self.boil_vol)
		stat.topupvol =float(self.topupvol)
		stat.total_water=float(self.water_required)
		stat.grain_weight=float(self.grain_weight)
		stat.nongrain_weight=float(self.nongrain_weight)
		stat.hops_weight=float(self.total_hop_weight)
		stat.bottles_required=float(self.bottles_required)
		stat.kettle1volume=float(self.kettle1volume)
		stat.kettle2volume=float(self.kettle2volume)
		stat.kettle3volume=float(self.kettle3volume)
		stat.kettle1kettle2volume=float(self.kettle1kettle2volume)
		stat.kettle1kettle2kettle3volume=float(self.kettle1kettle2kettle3volume)

		stat.kettle1evaporation=float(self.kettle1evaporation)
		stat.kettle2evaporation=float(self.kettle2evaporation)
		stat.kettle3evaporation=float(self.kettle3evaporation)
		stat.kettle1preboilgravity=float(self.kettle1preboilgravity)
		stat.kettle2preboilgravity=float(self.kettle2preboilgravity)
		stat.kettle3preboilgravity=float(self.kettle3preboilgravity)

		stat.postboilprecoolgravity=float(self.precool_og)
		stat.preboil_gravity=float(self.pre_boil_gravity)

#		stat.minikegqty=float(self.minikegqty)
#		stat.polypinqty=float(self.polypinqty)
#		stat.num_crown_caps=float(self.num_crown_caps)
#		stat.primingwater=float(self.priming_sugar_water)	
#		stat.primingsugarqty = float(self.primingsugarqty)
#		stat.primingsugartotal=float(self.primingsugartotal)
		stat.put()
	
		sys.stderr.write("GOT AFtEr sTAT  gRecipeStats\n")

	
		return {'operation' : 'compile', 'status' : 1 }


	def checkStockAndPrice(self, username,recipeName,process,raw=False):
		sys.stderr.write("checkStockAndPrice %s/%s\n" %(recipeName,process))
		"""
		given a brwlabRecipe object checks to see if all ingredients are available.

		Returns a tuple containing a cost and stock dict.
		
		cost_result contains the keys:
			fermentables
			hops
			yeast
			misc
			__total__
			The first four have a key for each ingredient and a __total__ key

		stock_result contains the keys:
			pcnt_lefs with the fermentabls,hops,yeast,misc keys each expressing
				the percentage of the store qty remaining after taking out 
				this entry (or 0 if not sufficient stock)
			out_of_stock is a list providing each ingredient without enough stock
				already in the store
			qty_required is a list of qty requried for out of sotck items
			qty_available is a lsit of qty available for out of stock items
		"""
		
		self.calclog=""
		cost_result = {}
		stock_result= {}
		stock_result['__out_of_stock__'] = []
		stock_result['__pcnt_left__'] = {}
		stock_result['__qty_required__'] = {}
		stock_result['__qty_available__'] = {}
		stock_result['__stockrequirements__'] = []
		total_cost=0		



		cost_result['ingredients'] = {}
		cost_result['ingredients']['__total__'] = 0	
		stock_result['ingredients'] = {}
		stock_result['ingredients']['__total__'] = 0

		ourActivities = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process= :2 AND stepNum = -1 AND activityNum >= 0",username,process)
		self.ourActivities =  ourActivities.fetch(2000)
		for activity in self.ourActivities:
		
			#
			# Turns out this has never been used in processes to date
			# disabling this. although we have a data structure 
			# and import support for this in the future if needed
			#
			"""
			for (ingredient,qty) in activity.ingredients:
				if self.Consumable.has_key( ingredient ):

					storeQty = 0
					storeCost = 0 

					for purchase in self.Ingredients[ ingredient ]:
						storeQty = storeQty + purchase.qty
						storeCost = storeCost + purchase.price
					
					if storeQty > 0:
						cost_per_unit = storeCost / storeQty
					else:
						cost_per_unit = 0

					cost_for_ingredient = qty * cost_per_unit
					cost_result['ingredients']['__total__'] = cost_result['ingredients']['__total__'] + cost_for_ingredient
					cost_result['ingredients'][ ingredient.uid ] = cost_for_ingredient
					if storeQty > 0:
						stock_result['__pcnt_left__'][ ingredient.uid ] = 1-(qty/storeQty)
					else:
						stock_result['__pcnt_left__'][ ingredient.uid ] = 1-0

					stock_result['ingredients'][ ingredient.uid ] = qty
					stock_result['ingredients']['__total__'] = stock_result['ingredients']['__total__'] + qty

					if qty > storeQty:
						stock_result['__pcnt_left__'][ ingredient.uid ] = 0
						stock_result['__out_of_stock__'].append( ingredient.uid )
						stock_result['__qty_available__'][ ingredient.uid ] = storeQty
						stock_result['__qty_required__'][ ingredient.uid ] = qty
		
		cost_result['__total__'] = total_cost	
		"""





		# Started to condense
#		for (costType,dict1,dict2) in [ ('fermentables',recipe.fermentables, self.Fermentables), ('hops',recipe.hops, self.Hops) , ('yeast',recipe.yeast,self.Yeast),('misc',recipe.misc,self.Misc) ]:
		for costType in ['fermentables','hops','yeast','misc']:
			
			cost_result[ costType ] = {}
			cost_result[ costType ]['__total__'] = 0	
			stock_result[ costType ] = {}
			stock_result[ costType ]['__total__'] = 0	
					#dict1 ==> self.fermentables, self.hops, self.yeast, self.misc
							# (i.e. our recipe bits and pieces
			
		

			ourRecipeIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = False AND ingredientType = :3 ",username,recipeName,costType)
			for ingredient in ourRecipeIngredients.fetch(2000):
				qty = ingredient.qty
	

				
				ourStockCheck = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2",username,ingredient.ingredient)
				ourStock = ourStockCheck.fetch(20000)
				
				if len(ourStock) == 0:
					storeQty=0	
				else:
					# Now we are going to have average out the cost over all purchases
					storeQty = 0
					storeCost = 0
					for purchasedItem in ourStock:
						storeQty = storeQty + purchasedItem.qty
						storeCost = storeCost + purchasedItem.purchaseCost * purchasedItem.qty


					if storeQty > 0:
						cost_per_unit = storeCost/storeQty
					else:
						cost_per_unit = 0
					cost_for_ingredient = qty * cost_per_unit
					cost_result[ costType ]['__total__'] = cost_result[ costType ]['__total__'] + cost_for_ingredient
					cost_result[ costType ][ ingredient.ingredient ] = cost_for_ingredient
					if storeQty > 0:
						stock_result['__pcnt_left__'][ ingredient.ingredient ] = 1 - (qty / storeQty)
					else:
						stock_result['__pcnt_left__'][ ingredient.ingredient ] = 1 - 0
					stock_result['__qty_available__'][ ingredient.ingredient ] = storeQty
					stock_result['__qty_required__'][ ingredient.ingredient ] = qty

				
					stock_result[ costType ][ ingredient.ingredient ] = qty
					stock_result[ costType ]['__total__'] = stock_result[ costType ]['__total__'] + qty

					if qty > storeQty:
						stock_result['__pcnt_left__'][ ingredient.ingredient ] = 0
						stock_result['__stockrequirements__'].append( [ingredient.ingredient ,storeQty,qty])
						stock_result['__out_of_stock__'].append( ingredient.ingredient )
						stock_result['__qty_available__'][ ingredient.ingredient ] = storeQty
						stock_result['__qty_required__'][ ingredient.ingredient ] = qty

			total_cost = total_cost + cost_result[ costType ]['__total__']



		# Process Costing
		cost_result['consumables'] = {}
		cost_result['consumables']['__total__'] = 0	
		stock_result['consumables'] = {}
		stock_result['consumables']['__total__'] = 0

		for activity in self.ourActivities:
			ourRecipeConsumables = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = True and processConsumable = True AND process = :3",username,recipeName,process)
			for ingredient in ourRecipeConsumables.fetch(2000):
				qty = ingredient.qty

				ourStockCheck = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2",username,ingredient.ingredient)
				ourStock = ourStockCheck.fetch(20000)

				if len(ourStock) == 0:
					storeQty=0
				else:
					storeQty = 0
					storeCost = 0 

					for purchasedItem in ourStock:
					#for purchase in self.Consumable[ haveStock ]:
						storeQty = storeQty + purchase.qty
						storeCost = storeCost + purchase.price
					if storeQty > 0:
						cost_per_unit = storeCost / storeQty
					else:
						cost_per_unit = 0

					cost_for_consumable = qty * cost_per_unit
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + cost_for_consumable
					cost_result['consumables'][ ingredient.ingredient ] = cost_for_consumable
					if storeQty > 0:
						stock_result['__pcnt_left__'][ ingredient.ingredient ] = 1-(qty/storeQty)
					else:
						stock_result['__pcnt_left__'][ ingredient.ingredient ] = 1-0
					stock_result['__qty_available__'][ ingredient.ingredient ] = storeQty
					stock_result['__qty_required__'][ ingredient.ingredient ] = qty


				stock_result['consumables'][ ingredient.ingredient ] = qty
				stock_result['consumables']['__total__'] = stock_result['consumables']['__total__'] + qty

				if qty > storeQty:
					stock_result['__pcnt_left__'][ ingredient.ingredient ] = 0
					stock_result['__stockrequirements__'].append( [ingredient.ingredient ,storeQty,qty])
					stock_result['__out_of_stock__'].append( ingredient.ingredient )
					stock_result['__qty_available__'][ ingredient.ingredient ] = storeQty
					stock_result['__qty_required__'][ ingredient.ingredient ] = qty
	




		# repeat bottle stock checking
		# this is a clone of the implementation in takeStock but re-purposed
		# for checkStockAndPrice

		ourRecipes = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe = ourRecipes.fetch(1)[0]

		total_bottles = 0
		bottle_vols = []
		polypin_vols= []
		keg_vols=[]
		polypin_volume_required=recipe.batch_size_required*1000
		sys.stderr.write("VOLUME REQUIRED (Polypin/Keg/Bottles) %s\n" %(polypin_volume_required))
		total_polypins=0
		total_kegs=0


	
		# TODO WHAT HAPPENS WIHT KEGS AND POLYPINS.... need to copy from below	
		ourPolypins = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category= :2", username,"polypin")
		for polypin in ourPolypins.fetch(5000):
			polypin_vols.append( (polypin.fullvolume, polypin) )
		polypin_vols.sort()
		polypin_vols.reverse()
		totalPolypinVol=0	
		sys.stderr.write("Polypin vols\n")
		sys.stderr.write("%s\n\n" %(polypin_vols))		
		sys.stderr.write("Polypin volume required %s\n" %(polypin_volume_required))


		for (vol,polypin) in polypin_vols:
			qtyAvailable = 0
			qtyRequired = 0

			ourPolypinPurchases = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem= :2 ", username,polypin.name)
			for purchase in ourPolypinPurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and polypin_volume_required > 0:					
					sys.stderr.write("volume in this type fo polypin %s\n" %(vol))
					sys.stderr.write("purchase.qty %s\n" %(purchase.qty))
					if (purchase.qty * vol) > polypin_volume_required:
						qtyNeeded =math.ceil( polypin_volume_required / vol )
#						sys.stderr.write(" qty Of this polypin %s\n" %(qtyNeeded))
					else:
						qtyNeeded = purchase.qty
#						sys.stderr.write(" qty Of this polypin %s (all)\n" %(qtyNeeded))
					if not cost_result['consumables'].has_key(polypin.name):	
						cost_result['consumables'][polypin.name] =0
					cost_result['consumables'][ polypin.name ] = cost_result['consumables'][ polypin.name ] + (purchase.purchaseCost * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
					totalPolypinVol=totalPolypinVol+purchase.qty

					polypin_volume_required = polypin_volume_required - (qtyNeeded * vol )
					qtyRequired = qtyRequired + qtyNeeded
		
					total_polypins = total_polypins + qtyNeeded






		# And priming sugar for polypins
		if recipe.priming_sugar_qty > 0 and total_polypins > 0:
			priming_sugar_reqd =   totalPolypinVol * recipe.priming_sugar_qty  * 0.0001
			qtyRequired=0
			qtyAvailable
			ourPrimingSugar = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory= :2", username,"primingsugar")
			for purchase in ourPrimingSugar.fetch(50000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty	> 0 and priming_sugar_reqd > 0:
					qtyNeeded = priming_sugar_reqd
				else:
					qtyneeded = purchase.qty
				if not cost_result['consumables'].has_key( purchase.storeitem ):
					cost_result['consumables'][ purchase.storeitem ] = 0
				cost_result['consumables'][ purchase.storeitem ] = cost_result['consumables'][ purchase.storeitem ] + (purchase.purchaseCost * qtyNeeded)
				cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
				priming_sugar_reqd = priming_sugar_reqd - qtyNeeded
				qtyRequired = qtyRequired + qtyNeeded

			if priming_sugar_reqd > 0:
				try:
					stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
					stock_result['__out_of_stock__'].append( purchase.storeitem )
					stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
					stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
					stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
				except:
					# we probably don' thave any type of priming sugar
					# so we make this up instead
					stock_result['__pcnt_left__'][ "__PRIMING_SUGAR__" ] = 0
					stock_result['__stockrequirements__'].append( ['__PRIMING_SUGAR__' ,qtyAvailable,qtyRequired] )
					stock_result['__out_of_stock__'].append( "__PRIMING_SUGAR__" )
					stock_result['__qty_available__'][ "__PRIMING_SUGAR__" ] = qtyAvailable
					stock_result['__qty_required__'][ "__PRIMING_SUGAR__" ] = qtyRequired


		keg_volume_required=polypin_volume_required-totalPolypinVol



		ourKegs = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category= :2", username,"keg")
		for keg in ourKegs.fetch(5000):
			keg_vols.append( (keg.fullvolume, keg) )
		keg_vols.sort()
		keg_vols.reverse()
		totalKegVol=0	
		sys.stderr.write("Keg vols\n")
		sys.stderr.write("%s\n\n" %(keg_vols))		
		sys.stderr.write("KEG VOLUME REQUIRED %s\n" %(keg_volume_required))


		for (vol,keg) in keg_vols:
			qtyAvailable = 0
			qtyRequired = 0

			ourKegPurchases = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem= :2 ", username,keg.name)
			for purchase in ourKegPurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and keg_volume_required > 0:					
					sys.stderr.write("volume in this type fo keg %s\n" %(vol))
					sys.stderr.write("purchase.qty %s\n" %(purchase.qty))
					if (purchase.qty * vol) > keg_volume_required:
						qtyNeeded =math.ceil( keg_volume_required / vol )
#						sys.stderr.write(" qty Of this keg %s\n" %(qtyNeeded))
					else:
						qtyNeeded = purchase.qty
#						sys.stderr.write(" qty Of this keg %s (all)\n" %(qtyNeeded))
					if not cost_result['consumables'].has_key(keg.name):	
						cost_result['consumables'][keg.name] =0
					cost_result['consumables'][ keg.name ] = cost_result['consumables'][ keg.name ] + (purchase.purchaseCost * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
					totalKegVol=totalKegVol+purchase.qty

					keg_volume_required = keg_volume_required - (qtyNeeded * vol )
					qtyRequired = qtyRequired + qtyNeeded
		
					total_kegs = total_kegs + qtyNeeded



		ourco2s = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category= :2", username,"co2").fetch(54355)
		co2_required=total_kegs
		sys.stderr.write("co2 required %s\n" %(co2_required))
		for co2 in ourco2s:
			qtyAvailable = 0
			qtyRequired = 0

			ourco2Purchases = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem= :2 ", username,co2.name)
			for purchase in ourco2Purchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and co2_required > 0:					
					if purchase.qty > co2_required:
						qtyNeeded =co2_required
						co2_required=0
					else:
						co2_required=co2_required-purchase.qty
						qtyNeeded = purchase.qty
					if not cost_result['consumables'].has_key(co2.name):	
						cost_result['consumables'][co2.name] =0
					cost_result['consumables'][ co2.name ] = cost_result['consumables'][ co2.name ] + (purchase.purchaseCost * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)


		if co2_required > 0:
			sys.stderr.write("doing out of stock stuff\n")
			stock_result['__pcnt_left__'][ co2.name ] = 0
			stock_result['__stockrequirements__'].append( [co2.name,qtyAvailable, total_kegs])
			stock_result['__out_of_stock__'].append( co2.name )
			stock_result['__qty_available__'][ co2.name ] = qtyAvailable
			stock_result['__qty_required__'][ co2.name ] = total_kegs






		# And priming sugar for kegs
		if recipe.priming_sugar_qty > 0 and co2_required>0:
			priming_sugar_reqd =   totalKegVol * recipe.priming_sugar_qty  * 0.002
			qtyRequired=0
			qtyAvailable
			ourPrimingSugar = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory= :2", username,"primingsugar")
			for purchase in ourPrimingSugar.fetch(50000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty	> 0 and priming_sugar_reqd > 0:
					qtyNeeded = priming_sugar_reqd
				else:
					qtyneeded = purchase.qty
				if not cost_result['consumables'].has_key( purchase.storeitem ):
					cost_result['consumables'][ purchase.storeitem ] = 0
				cost_result['consumables'][ purchase.storeitem ] = cost_result['consumables'][ purchase.storeitem ] + (purchase.purchaseCost * qtyNeeded)
				cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
				priming_sugar_reqd = priming_sugar_reqd - qtyNeeded
				qtyRequired = qtyRequired + qtyNeeded

			if priming_sugar_reqd > 0:
				try:
					stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
					stock_result['__out_of_stock__'].append( purchase.storeitem )
					stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
					stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
					stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
				except:
					# we probably don' thave any type of priming sugar
					# so we make this up instead
					stock_result['__pcnt_left__'][ "__PRIMING_SUGAR__" ] = 0
					stock_result['__stockrequirements__'].append( ['__PRIMING_SUGAR__' ,qtyAvailable,qtyRequired] )
					stock_result['__out_of_stock__'].append( "__PRIMING_SUGAR__" )
					stock_result['__qty_available__'][ "__PRIMING_SUGAR__" ] = qtyAvailable
					stock_result['__qty_required__'][ "__PRIMING_SUGAR__" ] = qtyRequired





		bottle_volume_required = keg_volume_required - totalKegVol
		sys.stderr.write("BOTTLE VOLUME REQUIRED %s\n" %(bottle_volume_required))

		totalBottleVol=0
		ourBottles = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category= :2", username,"bottle")
		for bottle in ourBottles.fetch(5000):
			bottle_vols.append( (bottle.fullvolume, bottle) )
		bottle_vols.sort()
		bottle_vols.reverse()
	
		sys.stderr.write("Bottle vols\n")
		sys.stderr.write("%s\n\n" %(bottle_vols))		
		for (vol,bottle) in bottle_vols:
			qtyAvailable = 0
			qtyRequired = 0

			ourBottlePurchases = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem= :2 ", username,bottle.name)
			for purchase in ourBottlePurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and bottle_volume_required > 0:					
					sys.stderr.write("volume in this type fo bottle %s\n" %(vol))
					if (purchase.qty * vol) > bottle_volume_required:
						qtyNeeded =math.ceil( bottle_volume_required / vol )
#						sys.stderr.write(" qty Of this bottle %s\n" %(qtyNeeded))
					else:
						qtyNeeded = purchase.qty
#						sys.stderr.write(" qty Of this bottle %s (all)\n" %(qtyNeeded))
					if not cost_result['consumables'].has_key(bottle.name):	
						cost_result['consumables'][bottle.name] =0
					cost_result['consumables'][ bottle.name ] = cost_result['consumables'][ bottle.name ] + (purchase.purchaseCost * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)

					totalBottleVol=qtyNeeded*vol
					bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )
					qtyRequired = qtyRequired + qtyNeeded
		
					total_bottles = total_bottles + qtyNeeded

		# if we don't have enough stock of bottles we will ask based on the last tbottle in the list
		# if this is a tiny bottle this will be odd,... but variabile  volume bottles isn't perfect
		# if we have multiple types of bottles we don't ask for the full volume, we only ask for the 
		# missing bit
#		sys.stderr.write("bottle volume required after loop %s\n" %(bottle_volume_required))
		if bottle_volume_required > 0:
			sys.stderr.write("doing out of stock stuff\n")
			stock_result['__pcnt_left__'][ bottle.name ] = 0
			stock_result['__stockrequirements__'].append( [bottle.name,qtyAvailable, math.ceil(bottle_volume_required / vol ) + qtyRequired])
			stock_result['__out_of_stock__'].append( bottle.name )
			stock_result['__qty_available__'][ bottle.name ] = qtyAvailable
					# this next calculation is the excess, but we have qtyRequired adding up
					# as we go along
			stock_result['__qty_required__'][ bottle.name ] = math.ceil(bottle_volume_required / vol ) + qtyRequired
			### out of stock

		sys.stderr.write("Polypins: %s/%s Kegs: %s/%s Bottles: %s/%s\n" %(total_polypins,totalPolypinVol,total_kegs,totalKegVol,total_bottles,totalBottleVol ))
		purchase=None

		# Now do crown caps
		total_caps = total_bottles  + 4
		qtyRequired = 0 
		qtyAvailable = 0
		ourBottleCaps = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory= :2 ", username,"bottlecaps")


		for purchase in ourBottleCaps.fetch(50000):
			qtyAvailable = qtyAvailable + purchase.qty
			if purchase.qty > 0 and total_caps > 0:
				if purchase.qty > total_caps:
					qtyNeeded= total_caps
				else:
					qtyNeeded = purchase.qty
				if not cost_result['consumables'].has_key( purchase.storeitem ):
					cost_result['consumables'][ purchase.storeitem ] = 0
				cost_result['consumables'][ purchase.storeitem ] = cost_result['consumables'][ purchase.storeitem ] + (purchase.purchaseCost * qtyNeeded)
				cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
				total_caps = total_caps - qtyNeeded
				qtyRequired = qtyRequired + qtyNeeded

		if total_caps > 0:
			stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
			stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
			stock_result['__out_of_stock__'].append( purchase.storeitem )
			stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
			stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
	
		purchase = None

		# And priming sugar
		if recipe.priming_sugar_qty > 0:
			priming_sugar_reqd = (total_bottles + 5) * recipe.priming_sugar_qty 
			qtyRequired=0
			qtyAvailable
			ourPrimingSugar = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory= :2", username,"primingsugar")
			for purchase in ourPrimingSugar.fetch(50000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty	> 0 and priming_sugar_reqd > 0:
					qtyNeeded = priming_sugar_reqd
				else:
					qtyneeded = purchase.qty
				if not cost_result['consumables'].has_key( purchase.storeitem ):
					cost_result['consumables'][ purchase.storeitem ] = 0
				cost_result['consumables'][ purchase.storeitem ] = cost_result['consumables'][ purchase.storeitem ] + (purchase.purchaseCost * qtyNeeded)
				cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
				priming_sugar_reqd = priming_sugar_reqd - qtyNeeded
				qtyRequired = qtyRequired + qtyNeeded

			if priming_sugar_reqd > 0:
				try:
					stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
					stock_result['__out_of_stock__'].append( purchase.storeitem )
					stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
					stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
					stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
				except:
					# we probably don' thave any type of priming sugar
					# so we make this up instead
					stock_result['__pcnt_left__'][ "__PRIMING_SUGAR__" ] = 0
					stock_result['__stockrequirements__'].append( ['__PRIMING_SUGAR__' ,qtyAvailable,qtyRequired] )
					stock_result['__out_of_stock__'].append( "__PRIMING_SUGAR__" )
					stock_result['__qty_available__'][ "__PRIMING_SUGAR__" ] = qtyAvailable
					stock_result['__qty_required__'][ "__PRIMING_SUGAR__" ] = qtyRequired

		result = {}
		result['cost_result'] = cost_result
		result['stock_result'] = stock_result
		if raw:
			return (cost_result,stock_result)	
		return {'operation' : 'checkStockAndPrice', 'status' : 1, 'json' : json.dumps( {'result': result } ) }














	def deleteBrewlog(self,owner,brewlog):
		sys.stderr.write("deleteBrewlog %s\n" %(brewlog))
		ourOldRecords = db.GqlQuery("SELECT * FROM gBrewlogStock WHERE  owner = :1 AND brewlog = :2",owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old brewlog indexes
		ourOldRecords = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2", owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old step records			
		ourOldRecords = db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2", owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old notes
		ourOldRecords = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2",owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()


		return {'operation':'deleteBrewlog','satus':1}

	def changeProcess(self,username,recipeName,newProcess,activeCategory=""):
		sys.stderr.write("changeProcess %s/%s\n" %(recipeName,newProcess))

		ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		for recipe in ourRecipe.fetch(500):
			recipe.process=newProcess
			recipe.put()


		# now include calculate/compile steps
		self.calculateRecipe(username,recipeName)
		#self.compile(username,recipeName,None)
		self.compile(username,recipeName,None)
		tmp = self.viewRecipe(username,recipeName,activeCategory,1)

		return {'operation' : 'changeProcess', 'status' : 1 ,'json' : tmp['json'] }
	
	
	def listClearanceStock(self,username):
		"""
		Builds a list of stock items which are out of date, and soon out of date
		"""
	
		sys.stderr.write("listClearanceStock\n")

		bestBeforeThreshold = time.time()
		bestBeforeEarlyThreshold = time.time()-(86400*6)
		toclear={}
		oldstock={}

		earlythreshold=0
		overthreshold=0

		for storetype in ['fermentables','hops','yeast','misc','consumable']:
			toclear[ storetype ] = {}

			ourPurchases  = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storecategory= :2", username,storetype)
			for purchasedItem in ourPurchases.fetch(50000):
				threshold=-1
				if purchasedItem.qty > 0:	# only >0
					if not purchasedItem.willNotExpire:
						if purchasedItem.bestBeforeEnd < bestBeforeThreshold:
							threshold=1
							overthreshold=overthreshold + 1
						elif purchasedItem.bestBeforeEnd < bestBeforeEarlyThreshold:
							threshold=0
							earlythreshold=earlythreshold + 1

						if threshold >= 0:	# if threshold or limit exceeded
							if not toclear[ storetype ].has_key( purchasedItem.storeitem ):
								toclear[ storetype ][ purchasedItem.storeitem ] = []
							if not oldstock.has_key( purchasedItem.storeitem ):
								oldstock[ purchasedItem.storeitem ] = []
							oldstock[ purchasedItem.storeitem ].append([threshold, int((bestBeforeThreshold-purchasedItem.bestBeforeEnd)/86400)+1, purchasedItem.storeitem, purchasedItem.stocktag] )

							toclear[ storetype ][ purchasedItem.storeitem ].append( (threshold,  int((bestBeforeThreshold-purchasedItem.bestBeforeEnd)), purchasedItem ) )
				


		OLDSTOCKINDEX=[]
		for x in oldstock:
			OLDSTOCKINDEX.append(x)
	
		toclear['__overthreshold__'] = overthreshold
		toclear['__earlythreshold__'] = earlythreshold
		toclear['__oldstock__'] = oldstock
		toclear['__oldstockindex__'] = OLDSTOCKINDEX


		return toclear

	

	def _stockBestBefore(self, username, stock_result, stockType, recipeName,dummyAllocate=0):
		"""
		Internal method which takes the stock with the oldest best before date
		This method also takes into account a fixed wasted factor/percentage

		dummyAllocate does 2 things, 1st it doesn't actually allocate and
		2nd it will x10'd the qty required. The use case for dummyAllocate
		is hops of different alphas.


		stockBestBefore doesn't seem to actually save anything in the database
		"""

		# just a bit of protection
		if not stock_result.has_key( stockType ):
			stock_result[ stockType ] = {}

		#  i knew this was going to burn us when we were playing with 
		#  adding ingredients
		if stockType == "hops":
			ourRecipeIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 and hopAddAt <= :4",username,recipeName,stockType,0.0)
		else:
			ourRecipeIngredients = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 ",username,recipeName,stockType)
		# gIngredients will NOT catch both real recipe ingredients and consumables
		# need something more but lets get ingredients done first
		# will need to build this in
		# if ITEM.category != "bottle" and ITEM.category != "bottlecaps":


		for ITEM in ourRecipeIngredients.fetch(40000):
			qty = ITEM.qty
			ourStockCheck = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2",username,ITEM.ingredient)
			ourStock = ourStockCheck.fetch(20000)
			if len(ourStock) == 0:
#US.has_key( ITEM ):
				# let's call this out because it has been needed
				print """
				***********************************************************************************************

	
			
				brewerslabEngine Exception in _stockBestBefore
				unable to find the stock we needed and this is a bad way to
				deal with it
				(this might be because we don't have an overview entry (hopAdd=-1) for hops


				***********************************************************************************************
				"""
				return {}	# should not be needed
			else:
			

#				if ITEM.category != "bottle" and ITEM.category != "bottlecaps":

				qtyNeeded = qty
				# A future improvement might attempt to use whole bags rather than
				# cause leaving opened packets.
				best_before_dates_obj = {}
				best_before_dates = []
#				if dbg:	print "hhdbg",US[haveStock]

				for purchasedItem in ourStock:
#					if dbg:	print "hhdbg",purchasedItem.supplier.name,purchasedItem.qty,time.ctime(purchasedItem.best_before_date)
					if not best_before_dates_obj.has_key( purchasedItem.bestBeforeEnd ):
						best_before_dates_obj[ purchasedItem.bestBeforeEnd ] = []
						best_before_dates.append( purchasedItem.bestBeforeEnd )
					best_before_dates_obj[ purchasedItem.bestBeforeEnd].append( purchasedItem )
				
#				if dbg:	print "hhdbg",best_before_dates
				
				# soonest best before end date first
				best_before_dates.sort()

				#uMake the qty required tenfold as we would really like to know 
				# how muct we can adjust up to.
				if dummyAllocate:	qtyNeeded = qtyNeeded * 100

				for best_before_date in best_before_dates:
					for item in best_before_dates_obj[ best_before_date ]:	
							
						if item.qty > 0 and qtyNeeded >0:
#							sys.stderr.write("ITEM item is of type %s\n" %(item))
							if not stock_result[ stockType ].has_key( item.storeitem ):
								stock_result[ stockType ][ item.storeitem ] = []	

							if item.qty > qtyNeeded:
								stock_result[ stockType ][ item.storeitem ].append( (qtyNeeded/item.qty,qtyNeeded, item.stocktag, item.storeitem, item) )
								# If we need multiple quantities then we won't do wastage
								# assumption is that the multiple qty is set appropriately.
								# item qty multiple thingy?
								if item.qtyMultiple != 1:	
									qtyUsed = math.ceil( qtyNeeded / item.qtyMultiple ) * item.qtyMultiple

									if not dummyAllocate:
										item.qty= item.qty - qtyUsed
#										sys.stderr.write("Setting QTY of %s/%s to %s\n" %(item.storeitem,item.stocktag,item.qty-qtyUsed))										
#										item.put()
									#item.qty= item.qty - qtyNeeded
								else:
								# Check the wastage in this step.
									if not dummyAllocate:
										item.qty= item.qty - qtyNeeded
										item.qty= item.qty - item.wastageFixed
										if item.qty < 0:
											item.qty = 0
#											item.put()
#											sys.stderr.write("Setting QTY of %s/%s to %s (Wastage)\n" %(item.storeitem,item.stocktag,0))										
									
								qtyNeeded = 0
							else:
								# This is a full use of the item in stock
								# therefore we do't introduce wastage
								qtyNeeded = qtyNeeded - item.qty
								stock_result[ stockType ][ item.storeitem ].append( (1,item.qty, item.stocktag,item.storeitem,item) )
								if not dummyAllocate:
									item.qty = float(0)	
#									item.put()
#									sys.stderr.write("Setting QTY of %s/%s to %s (Used All)\n" %(item.storeitem,item.stocktag,0))										


		return stock_result







	def takeStock(self, username, recipeName,process,ignoreOutOfStock=0,cost_result=None,stock_result=None,doNotAllocate=0):
		sys.stderr.write("takeStock %s/%s\n" %(recipeName,process))
		"""
		given a brwlabRecipe object a list of stockTag's focusing on returning the oldest stock
		first. 
		The algorithim takes into account minimum quantities (i.e. bottled water)

		If the stock for the whole recipe can't be fullfiled from stores a blank dict is 
		returned.

		Additionally if *any* stock is marked as near it's expiry date then a blank dict is 
		returned.
		
		"""
		self.total_kegs=0
		self.total_bottles=0
		self.total_polypins=0


		# use checkStockAndPrice, but also allow us to bring this in instead to save cpu cycles ;-)
		if not cost_result and not stock_result:
			(cost_result,stock_result) = self.checkStockAndPrice(username,recipeName,process, True)


		if len(stock_result['__out_of_stock__']) > 0:
			sys.stderr.write("Out of Stock")
			sys.stderr.write( "%s\n" %(stock_result['__out_of_stock__']))
			return {}		# out of stock / or out of date


		toclear = self.listClearanceStock(username)


		if (toclear['__overthreshold__'] > 0 or toclear['__earlythreshold__'] > 0) and int(ignoreOutOfStock) == 0:
			sys.stderr.write("Out of Date Stock")
			sys.stderr.write( "Early %s\n" %(toclear['__earlythreshold__']))
			sys.stderr.write( "Over %s\n" %(toclear['__overthreshold__']))
			sys.stderr.write( "  %s\n" %(toclear))
			return {}



		stock_result= {}

		stock_result = self._stockBestBefore(username,stock_result, "fermentables",recipeName)
		
	
		stock_result = self._stockBestBefore(username,stock_result, "hops",recipeName)
		stock_result = self._stockBestBefore(username,stock_result, "yeast", recipeName)
		stock_result = self._stockBestBefore(username,stock_result, "misc", recipeName)

		# For consumables we don't really need to have  best before ordering, but 
		# it won't hurt
		ourActivities = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum= :3 AND subStepNum = :4 ORDER BY activityNum", username,process,-1,-1)


#		# reduce qty of stock 
		for storeType in stock_result:
			for a in stock_result[storeType]:
				for (pcnt,qty,stocktag,name,purchaseObj) in  stock_result[storeType][a]:
#
					purchaseItem = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND stocktag = :2", username,stocktag).fetch(1)[0]
					purchaseItem.qty = float(purchaseItem.qty )	-qty
					purchaseItem.put()


#		return {'status' : -5}
		# intelligentBottle
		# look out for "Gather Bottles" step and find bottles
		# this is going to have to double up checkStockAndPrice somehow
		enableIntelligentBottle=0
		enableIntelligentKeg=0
		enableIntellignetPolypin=0
		ourAutoSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto != '' ",username,process)
		for step in ourAutoSteps.fetch(500):
			if step.auto == "gather2":
				enableIntelligentBottle = 1
			if step.auto == "gather3":
				enableIntelligentKeg = 1
		
			if step.auto == "gather4":
				enableIntelligentPolypin = 1
		

		ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2 ",username,recipeName).fetch(1)[0]

		for activity in  ourActivities:
		#for activity in recipe.process.activities:
			# stockBestBefore ignores bottles
			stock_result = self._stockBestBefore(username,stock_result, "consumables", recipeName)

			# The checking of the steps is only 
			bottle_volume_required = (ourRecipe.batch_size_required * 1000)
			keg_priming_sugar = 0
			bottle_priming_sugar =0
			total_keg_volume=0

			if enableIntelligentKeg:
				# for kegs we will prefer the smallest kegs instead of the 
				# largest kegs
				keg_vols = []
				ourKegs = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > 0",username,"keg").fetch(345345)
				for purchasedItem in ourKegs:
#				for purchasedItem in self.Consumable:
#					if purchasedItem.category == "keg":
					keg_vols.append( ( purchasedItem.volume, purchasedItem ) )
				keg_vols.sort()

#
				self.calclog = self.calclog + "kegfilling: keg_vols %s\n" %(keg_vols)
				total_kegs=0					
				for (vol,keg) in keg_vols:
					self.calclog = self.calclog + "kegfilling: %s ml from keg type %s\n" %(vol,keg.storeitem)
					self.calclog = self.calclog + "kegfilling: volume left to keg %s ml\n" %(bottle_volume_required)
					#for purchase in self.Consumable[keg]:
					for purchase in ourKegs:
						self.calclog = self.calclog + "kegfilling: purchase.qty %s\n"%(purchase.qty)
						if purchase.qty > 0 and bottle_volume_required > 0:
							if not stock_result['consumables'].has_key(keg.storeitem):
								stock_result['consumables'][ keg.storeitem ] = []	

							if (purchase.qty * vol) > bottle_volume_required:

								total_keg_volume = total_keg_volume + vol
								qtyNeeded =math.ceil( bottle_volume_required / vol )
										
								stock_result['consumables'][ keg.storeitem ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
								purchase.qty = float(purchase.qty - qtyNeeded)
							else:
								total_keg_volume = total_keg_volume + vol
								qtyNeeded = purchase.qty
								stock_result['consumables'][ keg.storeitem ].append( (1 , qtyNeeded, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
								purchase.qty = float(0)
							purchase.put()

							# datauplift
#							if not keg.__dict__.has_key("caprequired"):	keg.caprequired=0
#							if not keg.__dict__.has_key("co2required"):	keg.co2required=1

							total_kegs=total_kegs+qtyNeeded
#							if bottle.caprequired:	bottle_caps_required = bottle_caps_required + qtyNeeded
							bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )

				self.kegs_required= total_kegs
				self.calclog = self.calclog + "kegfilling: total_kegs %s\n" %(total_kegs)
				TOTAL_KEGS=total_kegs
				self.total_kegs=TOTAL_KEGS



				ourCO2 = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > 0",username,"keg").fetch(345345)
			
				for co2 in ourCO2:
					if purchase.qty > 0 and total_kegs > 0:
						if not stock_result['consumables'].has_key( co2.storeitem ):
							stock_result['consumables'][ co2.storeitem ] = []
						if (purchase.qty) > total_kegs:	# need a proportion
							stock_result['consumables'][ co2.storeitem ].append( ( total_kegs/purchase.qty, total_kegs, purchase.stocktag, "dbg:purchase.purchasedItem", purchase ) )
							purchase.qty = float(purchase.qty - total_kegs)
							total_kegs = 0 
						else:		# meed all this purchase
							stock_result['consumables'][ co2.storeitem ].append( (1, purchase.qty, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
							total_kegs = total_kegs - purchase.qty
							purchase.qty = float(0)
							purchase.put()

				#  priming sugar
				# note; priming sugar in recipe is against a 500ml bottle size
				# so we need to convert into a value per ml per to be able to use
				priming_sugar_reqd = (total_keg_volume) * ((ourRecipe.priming_sugar_qty * 0.002) )
				self.calclog=self.calclog+"kegfilling: total keg volume filled %.2f in %s kegs\n" %(total_keg_volume,TOTAL_KEGS)
				self.calclog=self.calclog+"kegfilling: priming sugar required for kegs %.3f\n" %(priming_sugar_reqd)
				keg_priming_sugar = priming_sugar_reqd


			if enableIntelligentPolypin:

				# for polypins we will prefer the smallest polypins instead of the 
				# largest polypins
				polypin_vols = []
				ourKegs = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > 0",username,"polypin").fetch(345345)
				for purchasedItem in ourKegs:
#				for purchasedItem in self.Consumable:
#					if purchasedItem.category == "polypin":
					polypin_vols.append( ( purchasedItem.volume, purchasedItem ) )
				polypin_vols.sort()

#
				self.calclog = self.calclog + "polyfill  : polypin_vols %s\n" %(polypin_vols)
				total_polypins=0					
				for (vol,polypin) in polypin_vols:
					self.calclog = self.calclog + "polyfill  : %s ml from polypin type %s\n" %(vol,polypin.storeitem)
					self.calclog = self.calclog + "polyfill  : volume left to polypin %s ml\n" %(bottle_volume_required)
					#for purchase in self.Consumable[polypin]:
					for purchase in ourKegs:
						self.calclog = self.calclog + "polyfill  : purchase.qty %s\n"%(purchase.qty)
						if purchase.qty > 0 and bottle_volume_required > 0:
							if not stock_result['consumables'].has_key(polypin.storeitem):
								stock_result['consumables'][ polypin.storeitem ] = []	

							if (purchase.qty * vol) > bottle_volume_required:

								total_polypin_volume = total_polypin_volume + vol
								qtyNeeded =math.ceil( bottle_volume_required / vol )
										
								stock_result['consumables'][ polypin.storeitem ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
								purchase.qty = float(purchase.qty - qtyNeeded)
							else:
								total_polypin_volume = total_polypin_volume + vol
								qtyNeeded = purchase.qty
								stock_result['consumables'][ polypin.storeitem ].append( (1 , qtyNeeded, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
								purchase.qty = float(0)
							purchase.put()

							total_polypins=total_polypins+qtyNeeded
							bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )

				self.polypins_required= total_polypins
				self.calclog = self.calclog + "polyfill  : total_polypins %s\n" %(total_polypins)
				TOTAL_PINS=total_polypins
				self.total_polypins=TOTAL_PINS


				#  priming sugar
				# note; priming sugar in recipe is against a 500ml bottle size
				# so we need to convert into a value per ml per to be able to use
				priming_sugar_reqd = (total_polypin_volume) * ((ourRecipe.priming_sugar_qty * 0.0001) )  # this is a guess
				self.calclog=self.calclog+"polyfill  : total polypin volume filled %.2f in %s polypins\n" %(total_polypin_volume,TOTAL_PINS)
				self.calclog=self.calclog+"polyfill  : priming sugar required for polypins %.3f\n" %(priming_sugar_reqd)
				polypin_priming_sugar = priming_sugar_reqd
				
				



			if enableIntelligentBottle:					
				total_bottle_volume=0

				# sort bottles in order of size. This is to allow us to have
				# different volume bottles. We can't specify to use a range
				# of different volumes... the algorithim here sorts by largest
				# bottles first. If the store quantities are manipulated 	
				# would get the behaviour
				bottle_vols = []
				ourBottles = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > 0",username,"bottle").fetch(345345)
#				for purchasedItem in self.Consumable:
				for purchasedItem in ourBottles:
					bottle_vols.append( ( purchasedItem.volume, purchasedItem ) )
				bottle_vols.sort()
				bottle_vols.reverse()
#
				# Now get crown caps
				bottle_caps_required = 0
				
				self.calclog = self.calclog + "bottlebank: bottle_vols %s\n" %(bottle_vols)
				total_bottles=0					
				for (vol,bottle) in bottle_vols:
					self.calclog = self.calclog + "bottlebank: %s ml from bottle type %s\n" %(vol,bottle.storeitem)
					if vol > 515 or vol < 472:
						self.calclog = self.calclog + "\n\n\nWARNING\nbottlebank: priming sugar calculations based on 500ml bottle volume\n"
					self.calclog = self.calclog + "bottlebank: volume left to bottle %s ml\n" %(bottle_volume_required)
					for purchase in ourBottles:
#						self.calclog = self.calclog + "bottlebank: purchase.qty %s\n"%(purchase.qty)
						if purchase.qty > 0 and bottle_volume_required > 0:
							if not stock_result['consumables'].has_key(bottle.storeitem):
								stock_result['consumables'][ bottle.storeitem ] = []	

							if (purchase.qty * vol) > bottle_volume_required:

								qtyNeeded =math.ceil( bottle_volume_required / vol )
										
								stock_result['consumables'][ bottle.storeitem ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
								purchase.qty = float(purchase.qty - qtyNeeded)
								total_bottle_volume = total_bottle_volume = qtyNeeded
							else:
								qtyNeeded = purchase.qty
								stock_result['consumables'][ bottle.storeitem ].append( (1 , qtyNeeded, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
								total_bottle_volume = total_bottle_volume = purchase.qty
#									print stock_result['consumables'][bottle]
								purchase.qty = float(0)
							purchase.put()

							# datauplift
							if not bottle.__dict__.has_key("caprequired"):	bottle.caprequired=1
							if not bottle.__dict__.has_key("co2required"):	bottle.co2required=0


							total_bottles = total_bottles + qtyNeeded 
							if bottle.caprequired:	bottle_caps_required = bottle_caps_required + qtyNeeded
							bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )

				self.bottles_required= total_bottles
				self.calclog = self.calclog + "bottlebank: total_bottles = %s\n" %(total_bottles)
				TOTAL_BOTTLES=total_bottles
				self.total_bottles=TOTAL_BOTTLES




				ourBottlecaps = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > 0",username,"bottlecaps").fetch(345345)
				for bottlecap in ourBottlecaps:
#				for bottlecap in self.Consumable:
#					if bottlecap.category == "bottlecaps":
#						for purchase in self.Consumable[ bottlecap ]:
					if bottle_caps_required > 0:
						if not stock_result['consumables'].has_key( bottlecap.storeitem ):
							stock_result['consumables'][ bottlecap.storeitem ] = []
						if (purchase.qty) > bottle_caps_required:	# need a proportion
							stock_result['consumables'][ bottlecap.storeitem ].append( ( bottle_caps_required/purchase.qty, bottle_caps_required, purchase.stocktag, "dbg:purchase.purchasedItem", purchase ) )
							purchase.qty = float(purchase.qty - bottle_caps_required)
							bottle_caps_required = 0
						else:		# meed all this purchase
							stock_result['consumables'][ bottlecap.storeitem ].append( (1, purchase.qty, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
							bottle_caps_required = float(bottle_caps_required - purchase.qty)
#										print "bottlecapsrequired = bottle_cpas_required -",purchase.qty,bottle_caps_required
							purchase.qty = 0
						purchase.put()


				# note recipe is fixed assumption of 500ml
				priming_sugar_reqd = (total_bottles + 5) * ourRecipe.priming_sugar_qty 
				self.calclog=self.calclog+"bottlebank: total bottle volume filled %.2f in %s bottles\n" %(total_bottle_volume,TOTAL_BOTTLES)
				self.calclog=self.calclog+"bottlebank: priming sugar required for bottles %.3f\n" %(priming_sugar_reqd)
				bottle_priming_sugar = priming_sugar_reqd



			self.priming_sugar_reqd=0

			if enableIntelligentBottle or enableIntelligentKeg or enableIntellignetPolypin:					
				#  priming sugar
				priming_sugar_reqd = keg_priming_sugar + bottle_priming_sugar + polypin_priming_sugar
				ourPrimingSugar = db.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > 0",username,"primingsugar").fetch(345345)
				for primingsugar in ourPrimingSugar:
#				for primingsugar in self.Consumable:
#					if primingsugar.category == "primingsugar":
#						for purchase in self.Consumable[ primingsugar ] :
					if  priming_sugar_reqd > 0:
						if not stock_result['consumables'].has_key( primingsugar.storeitem):
							stock_result['consumables'][ primingsugar.storeitem ] = []
						if (purchase.qty) > priming_sugar_reqd:
							stock_result['consumables'][ primingsugar.storeitem ].append( (priming_sugar_reqd/purchase.qty, priming_sugar_reqd, purchase.stocktag, "dbg:purchase.purchasedItem", purchase ))
							purchase.qty = float(purchase.qty - priming_sugar_reqd)
							priming_sugar_reqd = 0
						else:
							stock_result['consumables'][ primingsugar.storeitem ].append( (1,purchase.qty, purchase.stocktag, "dbg:purchase.purchasedItem", purchase) )
							priming_sugar_reqd = float(priming_sugar_reqd - purchase.qty)
							purchase.qty = float(0	)
						purchase.put()

				self.priming_sugar_reqd=priming_sugar_reqd



		
#		for x in stock_result['consumables']:
#			print x
#			for y in stock_result['consumables'][x]:
#				print " ",y
#			print ""
		return stock_result






	def viewRecipe(self,username,recipeName,category,dontRecompile=1):
		"""

		view a recipe and optional category of itnegredients to add to the recipe








a copied recipe which has never been compiled causes a problem

a compiled recipe which is recompiled seems to cause problems



		"""


		sys.stderr.write("viewRecipe-> %s/%s....\n" %(recipeName,category))
		status = 0

		ourRecipe = db.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe=ourRecipe.fetch(2000)[0]


		# if we don't have a recipe stats yet we must recalculate
		sys.stderr.write("viewRecipe\n ------ we have a process of %s\n" %(recipe.process))
		ourRecipeStats = db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3",username,recipeName, recipe.process)
		if len(ourRecipeStats.fetch(1)) == 0:
			sys.stderr.write("MUST RECOMPILE NOW!")
			self.calculateRecipe(username,recipeName)
			self.compile(username,recipeName,None)
#		status = 1
#		result={}
#		return {'operation' : 'viewRecipe', 'status' : status ,'json':json.dumps( result ) }
	

		# think we need to be recompiling... although do we really need to.
		if not dontRecompile:
			tmp = self.calculateRecipe(username,recipeName)
			self.compile(username,recipeName,None)


		try:
			result={}
			result['stats']={}






			HOPMAP={}
			FERMMAP={}		
			ourContributions = db.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2 AND srm < :3", username,recipeName,1.00)
			for contribution in ourContributions.fetch(4000):
				if contribution.ingredientType=="hops":
					HOPMAP[ (contribution.ingredient,contribution.hopAddAt) ] = contribution
				if contribution.ingredientType=="fermentables":
					FERMMAP[ contribution.ingredient]=contribution 




			
				# this will serve as what the recipe wants us to have
				# in the future we should have a "adopt these wroking values as the real values"

			result['stats']['calculationOutstanding']=recipe.calculationOutstanding
			result['stats']['estimated_abv'] = recipe.estimated_abv	
			result['stats']['estimated_ebc'] = recipe.estimated_ebc
			result['stats']['estimated_fg'] = recipe.estimated_fg	
			result['stats']['estimated_og'] = recipe.estimated_og	
			result['stats']['estimated_ibu'] = recipe.estimated_ibu
			result['stats']['postBoilTopup'] = recipe.postBoilTopup
			result['stats']['process']=recipe.process
			result['stats']['mash_efficiency']=recipe.mash_efficiency
			result['stats']['batch_size_required']=recipe.batch_size_required

			sys.stderr.write("viewRecipe\n ------ we have a process of %s\n" %(recipe.process))
			ourRecipeStats = db.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3",username,recipeName, recipe.process)
			stats=ourRecipeStats.fetch(2000)[0]
				# these are our current wroking values
			result['stats']['this_estimated_abv'] = stats.estimated_abv	
#			result['stats']['this_estimated_ebc'] = stats.estimated_ebc
			result['stats']['this_estimated_fg'] = stats.estimated_fg	
			result['stats']['this_estimated_og'] = stats.estimated_og	
			result['stats']['this_estimated_ibu'] = stats.estimated_ibu

			result['stats']['spargeWater'] = stats.sparge_water
			result['stats']['mashWater'] = stats.mash_liquid
			result['stats']['boilVolume'] = stats.boil_vol
			result['stats']['totalWater'] = stats.total_water
			result['stats']['totalGrain'] = stats.grain_weight
			result['stats']['totalAdjuncts']=stats.nongrain_weight
			result['stats']['totalHops']=stats.hops_weight

			tmp={}
			result['category'] = category
			result['fermentableitems'] = []
			ourItems = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False ORDER BY ingredient",username,recipeName,"fermentables")
			items=ourItems.fetch(20000)
			for item in items:
				result['fermentableitems'].append({})
				result['fermentableitems'][-1]['name']=item.ingredient
				result['fermentableitems'][-1]['qty']="%.2f" %(item.qty)
				result['fermentableitems'][-1]['originalqty']="%.2f" %(item.originalqty)
				result['fermentableitems'][-1]['unit']=item.unit

				if FERMMAP.has_key( item.ingredient ):
					result['fermentableitems'][-1]['gravity'] = "%.3f" %(1+((FERMMAP[item.ingredient].gravity/1000)))
				else:	
					result['fermentableitems'][-1]['gravity'] = "?"

				tmp[item.ingredient]=""


			result['hopitems'] = []
			# it should be safe to only look at hopAddAt of >0
			ourItems = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False ORDER BY ingredient",username,recipeName,"hops")
			items=ourItems.fetch(20000)
			for item in items:

				if item.hopAddAt > 0:
					result['hopitems'].append({})
					result['hopitems'][-1]['name']=item.ingredient
					result['hopitems'][-1]['hopaddat'] = item.hopAddAt
					result['hopitems'][-1]['qty']="%.2f" %(item.qty)
					result['hopitems'][-1]['originalqty']="%.2f" %(item.originalqty)
					result['hopitems'][-1]['unit']=item.unit

					if HOPMAP.has_key( (item.ingredient,item.hopAddAt) ):
						result['hopitems'][-1]['ibu'] = "%.1f IBU" %(HOPMAP[ (item.ingredient,item.hopAddAt)].ibu)
					else:
						result['hopitems'][-1]['ibu'] = "? IBU"
					tmp[item.ingredient]=""



			result['yeastitems'] = []
			ourItems = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False ORDER BY ingredient",username,recipeName,"yeast")
			items=ourItems.fetch(20000)
			for item in items:
				result['yeastitems'].append({})
				result['yeastitems'][-1]['name']=item.ingredient
				result['yeastitems'][-1]['qty']= "%.2f" %(item.qty)
				result['yeastitems'][-1]['originalqty']= "%.2f" %(item.originalqty)
				result['yeastitems'][-1]['unit']=item.unit
				tmp[item.ingredient]=""



			result['otheritems'] = []
			ourItems = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False ORDER BY ingredient",username,recipeName,"misc")
			items=ourItems.fetch(20000)
			for item in items:
				result['otheritems'].append({})
				result['otheritems'][-1]['name']=item.ingredient
				result['otheritems'][-1]['qty']="%.2f" %(item.qty)
				result['otheritems'][-1]['originalqty']="%.2f" %(item.originalqty)
				result['otheritems'][-1]['unit']=item.unit
				tmp[item.ingredient]=""


			result['miscitems'] = []
			ourItems = db.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient=False ORDER BY ingredient",username,recipeName,"consumable")
			items=ourItems.fetch(20000)
			for item in items:
				result['miscitems'].append({})
				result['miscitems'][-1]['name']=item.ingredient
				result['miscitems'][-1]['qty']="%.2f" %(item.qty)
				result['miscitems'][-1]['originalqty']="%.2f" %(item.originalqty)
				result['miscitems'][-1]['unit']=item.unit
				tmp[item.ingredient]=""


			result['ingredients'] = []

			if category=="Consumables":	category="consumable"
			if category=="Other":	category="misc"
			ourIngredients = db.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2 ORDER BY name",username,category.lower())
#			sys.stderr.write("MAJOR CATEGOR   %s \n" %(category.lower()))

			ingredients=ourIngredients.fetch(20000)
			for ingredient in ingredients:
				if not tmp.has_key(ingredient.name) or category == "Hops":
					result['ingredients'].append({})
					result['ingredients'][-1]['name']=ingredient.name


#:w
#			sys.stderr.write(result)
			status = 1
			return {'operation' : 'viewRecipe', 'status' : status ,'json':json.dumps( result ) }

		
		except:
			sys.stderr.write("EXCEPTION in viewRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		return {'operation' : 'viewRecipe', 'status' : status }



	def publish(self,username,brewlogName,activityNum):
		"""

		view a recipe and optional category of itnegredients to add to the recipe
		"""

		ourProcess = db.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2", username,brewlogName).fetch(1)[0]
		process = ourProcess.process
		recipeName=ourProcess.recipe
		sys.stderr.write("over-riding process to %s\n" %(ourProcess.process))
	
		activities=[]
		ourActivities = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum= :3 AND subStepNum = :4 AND activityNum = :5  ORDER BY activityNum", username,process,-1,-1,activityNum)


		sys.stderr.write("publish-> %s....\n" %(brewlogName))
		self.response.headers['Content-Type']="text/html"
		self.response.out.write("<h1>Recipe: %s - Brewlog: %s</h1>\n\n" %(recipeName,brewlogName))
			


	
		ourActivities = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum= :3 AND subStepNum = :4 AND activityNum > -1 ORDER BY activityNum", username,process,-1,-1)
		
		for activity in ourActivities.fetch(4355):
			self.response.out.write("<h2>%s</h2>\n" %(activity.stepName))
			self.response.out.write("<table border=0 cellspacing=0 cellpadding=2>")
			self.response.out.write("<tr><td>&nbsp;</td><td colspan=2></td></tr>")
			ourSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND subStepNum = :3 AND activityNum = :4 AND stepNum > :5 ", username,process,-1,activity.activityNum, -1)
			for step in ourSteps.fetch(4324):	
				ourCompiles = db.GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,process,activity.activityNum,step.stepNum).fetch(1)
				if len(ourCompiles) < 1:
					ouc = []
				else:
					ouc =ourCompiles[0].toReplace
				self.response.out.write("\n<tr><td>&nbsp;</td><td colspan=2>%s: " %(step.stepNum))
				self.response.out.write("<b>%s</b>" %( self._newVariableSub(username, ouc,activity.activityNum,step.stepNum, step.stepName,recipeName,process,"<i>","</i>")))
				if step.auto:
					self.response.out.write(" [%s]" %(step.auto))
	
				self.response.out.write("<br>%s" %( self._newVariableSub(username, ouc,activity.activityNum,step.stepNum, step.text,recipeName,process,"<i>","</i>")))
#  step.text)		
				for img in step.img:
					self.response.out.write("<br><img src='http://mycrap.mellon-collie.net/brewerspad/processimgs/%s/%s'>" %( process,img))
				self.response.out.write("</td></tr>")

				#ourSubSteps = db.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND subStepNum > :3 AND activityNum = :4 AND stepNum = :5 ", username,process,-1,activity.activityNum, step.stepNum)
				ourSubSteps = db.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND subStepNum > :3 AND activityNum = :4 AND stepNum = :5 ", username,brewlogName,-1,activity.activityNum, step.stepNum)
				for substep in ourSubSteps.fetch(4324):	
					ourCompiles = db.GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ",username,process,activity.activityNum,step.stepNum).fetch(1)
					if len(ourCompiles) < 1:
						ouc = []
					else:
						ouc =ourCompiles[0].toReplace
					if substep.needToComplete:
						self.response.out.write("<tr><td width=48>&nbsp;</td><td width=48><img src='http://mycrap.mellon-collie.net/tick.png'></td><td>")
					else:
						self.response.out.write("<tr><td width=48>&nbsp;</td><td width=48>&nbsp;</td><td>")
					self.response.out.write("<br>%s %s" %(substep.subStepNum, self._newVariableSub(username, ouc,activity.activityNum,step.stepNum, substep.stepName,recipeName,process,"<i>","</i>")))
	#  step.text))
					self.response.out.write("</td></tr>")



				ourFields = db.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 ", username,brewlogName,activity.activityNum, step.stepNum)
				for field in ourFields.fetch(4324):	
					self.response.out.write("<tr height=48><td width=48>&nbsp;</td><td width=48>&nbsp;</td><td>")
					self.response.out.write("&nbsp;&nbsp;&nbsp;%s " %(field.fieldKey))
					if field.fieldWidget:
						self.response.out.write("(%s)" %(field.fieldWidget ))
					self.response.out.write(" = ___________________")
					self.response.out.write("</td></tr>")



			self.response.out.write("</table>")
			

	def oldHopModelling(self):
		#
		#
		# actual brewday  might have messed up
		
		acGravity2=64
		acGravity=45			# this might seem like a good idea to combine the graviities here.
							# but going on the theory that it's the proteins not the gravity
							# that is the issue adding both gravities together seems as though
							# it would better represent to gravity
		(hops14_60,weight14_60)=self.calculateHops(14, acGravity ,title="actualbitteringv2",doContribution=0,percentage=1,onlyHopAddAt=60,tweakHopAddAt=90)
		hops12_60=0
		weight12_60=0
		recalc_hop_60 = (14/working_batch_size_B) *  hops14_60

		(hops14_45,weight14_45)=self.calculateHops(14, acGravity ,title="actualbittering45v2",doContribution=0,percentage=1,onlyHopAddAt=15,tweakHopAddAt=45)
		hops12_45=0
		weight12_45=0
		recalc_hop_45 = (14/working_batch_size_B) *  hops14_45
	
		hops14_15=0
		weight14_15=0
		hops12_15=0
		weight12_15=0
		(hopsX_15,weightX_15) = self.calculateHops(int(working_batch_size_D+1)-26,acGravity,title="actualbrewday-bitteringv2",doContribution=0,percentage=0.5,onlyHopAddAt=15)  
		recalc_hop_15 = ((int(working_batch_size_D+1)-26)/working_batch_size_B ) * hopsX_15


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,1.011,title="actualbrewday-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  

		recalc_hop_0 = ((int(working_batch_size_D+1)-26)/working_batch_size_B ) * hopsX_0

		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops witha actual breday v2\n"
		self.calclog = self.calclog+"hopmodel : 75 min 14L from 20L kettle + Topup Combined %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60, acGravity)
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,acGravity2)
#		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 1,hops14_60,0,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 75/60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)
		self.calclog = self.calclog+"hopmodel : 75/60 min hops = %.2f IBU\n" %(recalc_hop_60)


		self.calclog = self.calclog+"hopmodel : 45 min 14L from 20L kettle + Topup Combined %.4f from %.2f gm @ %.4f\n" %(hops14_45,weight14_45, acGravity)
		self.calclog = self.calclog+"hopmodel : 45 min hops = %.2f gm\n" %(weight14_45)
		self.calclog = self.calclog+"hopmodel : 45 min hops = %.2f IBU\n" %(recalc_hop_45)

	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15, acGravity)
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,acGravity2)
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,acGravity)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f IBU\n" %(recalc_hop_15)


		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f IBU\n" %(recalc_hop_0)
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel : some of the display above is wrong\n" 
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0+weight14_45)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0+recalc_hop_45)
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('actualbrewday-v2')

		#
		#
		# actual brewday
		
		acGravity2=64
		acGravity=45			# this might seem like a good idea to combine the graviities here.
							# but going on the theory that it's the proteins not the gravity
							# that is the issue adding both gravities together seems as though
							# it would better represent to gravity
		(hops14_60,weight14_60)=self.calculateHops(14, acGravity ,title="actualbittering",doContribution=0,percentage=1,onlyHopAddAt=60,tweakHopAddAt=75)
		hops12_60=0
		weight12_60=0
		recalc_hop_60 = (14/working_batch_size_B) *  hops14_60

		(hops14_45,weight14_45)=self.calculateHops(14, acGravity ,title="actualbittering45",doContribution=0,percentage=1,onlyHopAddAt=15,tweakHopAddAt=45)
		hops12_45=0
		weight12_45=0
		recalc_hop_45 = (14/working_batch_size_B) *  hops14_45
	
		hops14_15=0
		weight14_15=0
		hops12_15=0
		weight12_15=0
		(hopsX_15,weightX_15) = self.calculateHops(int(working_batch_size_D+1)-26,acGravity,title="actualbrewday-bittering",doContribution=0,percentage=1,onlyHopAddAt=15)  
		recalc_hop_15 = ((int(working_batch_size_D+1)-26)/working_batch_size_B ) * hopsX_15


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,1.011,title="actualbrewday-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  

		recalc_hop_0 = ((int(working_batch_size_D+1)-26)/working_batch_size_B ) * hopsX_0

		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops witha actual breday\n"
		self.calclog = self.calclog+"hopmodel : 75 min 14L from 20L kettle + Topup Combined %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60, acGravity)
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,acGravity2)
#		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 1,hops14_60,0,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 75/60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)
		self.calclog = self.calclog+"hopmodel : 75/60 min hops = %.2f IBU\n" %(recalc_hop_60)


		self.calclog = self.calclog+"hopmodel : 45 min 14L from 20L kettle + Topup Combined %.4f from %.2f gm @ %.4f\n" %(hops14_45,weight14_45, acGravity)
		self.calclog = self.calclog+"hopmodel : 45 min hops = %.2f gm\n" %(weight14_45)
		self.calclog = self.calclog+"hopmodel : 45 min hops = %.2f IBU\n" %(recalc_hop_45)

	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15, acGravity)
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,acGravity2)
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,acGravity)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f IBU\n" %(recalc_hop_15)


		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f IBU\n" %(recalc_hop_0)
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel : some of the display above is wrong\n" 
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0+weight14_45)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0+recalc_hop_45)
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('actualbrewday')



		self.calclog = self.calclog +"hopmodel  : think that the calculations for everything below use the wrong volume\n"
		self.calclog = self.calclog +"hopmodel  :   working_batch_size_B = %.2f (used above)\n" %(working_batch_size_B)
		self.calclog = self.calclog +"hopmodel  :   working_batch_size_D = %.2f (used below)\n" %(working_batch_size_D)



		(hops14_60,weight14_60)=self.calculateHops(14,kettle_gravity_14+kettle_gravity_X,title="1kettle_bittering",doContribution=0,percentage=1,onlyHopAddAt=60,tweakHopAddAt=75)
		hops12_60=0
		weight12_60=0
		recalc_hop_60 = (hops14_60 * 1 * (26/working_batch_size_D))
	
		hops14_15=0
		weight14_15=0
		hops12_15=0
		weight12_15=0
		(hopsX_15,weightX_15) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="1kettle_armoa",doContribution=0,percentage=1,onlyHopAddAt=15)  
		recalc_hop_15 = (hops14_15 * (14/working_batch_size_D)) + (hops12_15 * (12/working_batch_size_D)) + (hopsX_15 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="1kettle_late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  

		recalc_hop_0 = (0 * (14/working_batch_size_D)) + (0 * (12/working_batch_size_D)) + (hopsX_0 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))

		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops with 1kettle\n"
		self.calclog = self.calclog+"hopmodel : 60 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 1,hops14_60,0,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)

	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,hops14_15,working_batch_size_D,hops12_15,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_15,recalc_hop_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)


		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,0,working_batch_size_D,0,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_0,recalc_hop_0)
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0)
	
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('1kettle')

	
	
		#
		#
		# Uniform  Gravities without a proportion aroma 15 minut hops at end
		
		(hops14_60,weight14_60)=self.calculateHops(14,kettle_gravity,title="uniform20kettle-60-singlearoma-tweak75",doContribution=0,percentage=14/26,onlyHopAddAt=60,tweakHopAddAt=75)
		(hops12_60,weight12_60)= self.calculateHops(12,kettle_gravity,title="uniform15kettle-60-singlearoma",doContribution=0,percentage=12/26,onlyHopAddAt=60)
		recalc_hop_60 = (((hops14_60 * (14/26)) + (hops12_60 * (12/26)))*(26/working_batch_size_D))
	
	
		hops14_15=0
		weight14_15=0
		hops12_15=0
		weight12_15=0
		(hopsX_15,weightX_15) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-15-singlearoma",doContribution=0,percentage=1,onlyHopAddAt=15)  
		recalc_hop_15 = (hops14_15 * (14/working_batch_size_D)) + (hops12_15 * (12/working_batch_size_D)) + (hopsX_15 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-0-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  

		recalc_hop_0 = (0 * (14/working_batch_size_D)) + (0 * (12/working_batch_size_D)) + (hopsX_0 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))

		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops with UNIFORM gravity without singlearoma hops and tweaked 60-->75\n"
		self.calclog = self.calclog+"hopmodel : 60 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 14/26,hops14_60,12/26,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)

	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,hops14_15,working_batch_size_D,hops12_15,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_15,recalc_hop_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)


		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0)
	
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('uniformgravi-singlearoma-tweak75')

	
	
		#
		#
		# Uniform  Gravities without a proportion of hops added at the end  - tweak 75 
		
		(hops14_60,weight14_60)=self.calculateHops(14,kettle_gravity,title="uniform20kettle-60-nolate-tweak75",doContribution=0,percentage=14/26,onlyHopAddAt=60,tweakHopAddAt=75)
		(hops12_60,weight12_60)= self.calculateHops(12,kettle_gravity,title="uniform15kettle-60-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=60)
		recalc_hop_60 = ((hops14_60 * (14/26)) + (hops12_60 * (12/26)) * (26/working_batch_size_D))
	
	
		(hops14_15,weight14_15)=self.calculateHops(14,kettle_gravity,title="uniform20kettle-15-nolate",doContribution=0,percentage=14/26,onlyHopAddAt=15)
		(hops12_15,weight12_15)= self.calculateHops(12,kettle_gravity,title="uniform15kettle-15-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=15)
		hopsX_15  = 0
		weightX_15=0
		recalc_hop_15 = (hops14_15 * (14/working_batch_size_D)) + (hops12_15 * (12/working_batch_size_D)) + (hopsX_15 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-0-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  

		recalc_hop_0 = (0 * (14/working_batch_size_D)) + (0 * (12/working_batch_size_D)) + (hopsX_0 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))

		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops with UNIFORM gravity without late hops but tweaked 60-->75\n"
		self.calclog = self.calclog+"hopmodel : 60 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 14/26,hops14_60,12/26,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)

	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,hops14_15,working_batch_size_D,hops12_15,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_15,recalc_hop_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)


		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0)
	
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('uniformgravi-nolatebittering-tweak75')

	
		#
		#
		# Uniform  Gravities without a proportion of hops added at the end  - tweak 75  & 30
		
		(hops14_60,weight14_60)=self.calculateHops(14,kettle_gravity,title="uniform20kettle-60-nolate-tweak75",doContribution=0,percentage=14/26,onlyHopAddAt=60,tweakHopAddAt=75)
		(hops12_60,weight12_60)= self.calculateHops(12,kettle_gravity,title="uniform15kettle-60-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=60)
		recalc_hop_60 = ((hops14_60 * (14/26)) + (hops12_60 * (12/26)) * (26/working_batch_size_D))
	
	
		(hops14_15,weight14_15)=self.calculateHops(14,kettle_gravity,title="uniform20kettle-15-nolate-tweak30",doContribution=0,percentage=14/26,onlyHopAddAt=15,tweakHopAddAt=30)
		(hops12_15,weight12_15)= self.calculateHops(12,kettle_gravity,title="uniform15kettle-15-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=15)
		hopsX_15  = 0
		weightX_15=0
		recalc_hop_15 = (hops14_15 * (14/working_batch_size_D)) + (hops12_15 * (12/working_batch_size_D)) + (hopsX_15 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-0-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  

		recalc_hop_0 = (0 * (14/working_batch_size_D)) + (0 * (12/working_batch_size_D)) + (hopsX_0 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))

		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops with UNIFORM gravity without late hops but tweaked 60-->75 & 15-->30\n"
		self.calclog = self.calclog+"hopmodel : 60 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 14/26,hops14_60,12/26,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)

	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,hops14_15,working_batch_size_D,hops12_15,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_15,recalc_hop_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)


		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0)
	
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('uniformgravi-nolatebittering-tweak75-30')





	
		#
		#
		# Uniform  Gravities without a proportion of hops added at the end
		
		(hops14_60,weight14_60)=self.calculateHops(14,kettle_gravity,title="uniform20kettle-60-nolate",doContribution=0,percentage=14/26,onlyHopAddAt=60)
		(hops12_60,weight12_60)= self.calculateHops(12,kettle_gravity,title="uniform15kettle-60-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=60)
		recalc_hop_60 = ((hops14_60 * (14/26)) + (hops12_60 * (12/26)) * (26/working_batch_size_D))
	
	
		(hops14_15,weight14_15)=self.calculateHops(14,kettle_gravity,title="uniform20kettle-15-nolate",doContribution=0,percentage=14/26,onlyHopAddAt=15)
		(hops12_15,weight12_15)= self.calculateHops(12,kettle_gravity,title="uniform15kettle-15-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=15)
		hopsX_15  = 0
		weightX_15=0
		recalc_hop_15 = (hops14_15 * (14/working_batch_size_D)) + (hops12_15 * (12/working_batch_size_D)) + (hopsX_15 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-0-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  

		recalc_hop_0 = (0 * (14/working_batch_size_D)) + (0 * (12/working_batch_size_D)) + (hopsX_0 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))

		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops with UNIFORM gravity without late hops\n"
		self.calclog = self.calclog+"hopmodel : 60 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 14/26,hops14_60,12/26,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)

	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,1+(kettle_gravity/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,hops14_15,working_batch_size_D,hops12_15,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_15,recalc_hop_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)


		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0)
	
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('uniformgravi-nolatebittering')






		#
		#
		# Different Gravities with no hops added at the end as well.
		
		(hops14_60,weight14_60)=self.calculateHops(14,kettle_gravity_14,title="bad-kettle-60-nolate",doContribution=0,percentage=14/26,onlyHopAddAt=60)
		(hops12_60,weight12_60)= self.calculateHops(12,kettle_gravity_12,title="good-kettle-60-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=60)
		recalc_hop_60 = ((hops14_60 * (14/26)) + (hops12_60 * (12/26)) * (26/working_batch_size_D))
	
	
		(hops14_15,weight14_15)=self.calculateHops(14,kettle_gravity_14,title="bad-kettle-15-nolate",doContribution=0,percentage=14/26,onlyHopAddAt=15)
		(hops12_15,weight12_15)= self.calculateHops(12,kettle_gravity_12,title="good-kettle-15-nolate",doContribution=0,percentage=12/26,onlyHopAddAt=15)
		hopsX_15  = 0
		weightX_15 = 0
		recalc_hop_15 = (hops14_15 * (14/working_batch_size_D)) + (hops12_15 * (12/working_batch_size_D)) + (hopsX_15 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-0-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  
		recalc_hop_0 = (0 * (14/working_batch_size_D)) + (0 * (12/working_batch_size_D)) + (hopsX_0 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops with DIFFERENT gravity without late hops\n"
		self.calclog = self.calclog+"hopmodel : 60 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_60,weight14_60,1+(kettle_gravity_14/1000))
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,1+(kettle_gravity_12/1000))
		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 14/26,hops14_60,12/26,hops12_60,recalc_hop_60)
	
		self.calclog = self.calclog+"hopmodel : 60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)

		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15,1+(kettle_gravity_14/1000))
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15, 1+(kettle_gravity_12/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15, 1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,hops14_15,working_batch_size_D,hops12_15,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_15,recalc_hop_15)
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)
		
		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0)
	


		HOP_MODELLING.append( recalc_hop_15 + recalc_hop_60 + recalc_hop_0 )
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('diffgravi-nolatebittering')



		#
		#
		# Different Gravities with a proportion of hops added at the end as well.
		
		(hops14_60,weight14_60)=self.calculateHops(14,kettle_gravity_14,title="bad-kettle-60-late",doContribution=0,percentage=14/26,onlyHopAddAt=60)
		(hops12_60,weight12_60)= self.calculateHops(12,kettle_gravity_12,title="good-kettle-60-late",doContribution=0,percentage=12/26,onlyHopAddAt=60)
		recalc_hop_60 = ((hops14_60 * (14/26)) + (hops12_60 * (12/26)) * (26/working_batch_size_D))
	
	
		(hops14_15,weight14_15)=self.calculateHops(14,kettle_gravity_14,title="bad-kettle-15-late",doContribution=0,percentage=14/working_batch_size_D,onlyHopAddAt=15)
		(hops12_15,weight12_15)=self.calculateHops(12,kettle_gravity_12,title="good-kettle-15-late",doContribution=0,percentage=12/working_batch_size_D,onlyHopAddAt=15)
		(hopsX_15,weightX_15) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-15-late",doContribution=0,percentage= (int(working_batch_size_D+1)-26)/working_batch_size_D,onlyHopAddAt=15)  
		recalc_hop_15 = (hops14_15 * (14/working_batch_size_D)) + (hops12_15 * (12/working_batch_size_D)) + (hopsX_15 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))

		(hopsX_0,weightX_0) = self.calculateHops(int(working_batch_size_D+1)-26,kettle_gravity_X,title="topup-kettle-0-late",doContribution=0,percentage=1,onlyHopAddAt=0.001)  
		recalc_hop_0 = (0 * (14/working_batch_size_D)) + (0 * (12/working_batch_size_D)) + (hopsX_0 * (( int(working_batch_size_D+1)-26)/working_batch_size_D ))


		self.calclog = self.calclog+"hopmodel : Back of Envelope calculations for hops with DIFFERENT gravity WITH late hops\n"
		self.calclog = self.calclog+"hopmodel : 60 min 14L from 20L kettle %.4f from %.2f gm @  %.4f\n" %(hops14_60,weight14_60,1+(kettle_gravity_14/1000))
		self.calclog = self.calclog+"hopmodel : 60 min 12L from 15L kettle %.4f from %.2f gm @ %.4f \n" %(hops12_60,weight12_60,1+(kettle_gravity_12/1000))
		self.calclog = self.calclog+"hopmodel : 60 min %.1f %% of %.2f + %.1f %% of %.2f = %.2f\n"  %( 14/26,hops14_60,12/26,hops12_60,recalc_hop_60)
		self.calclog = self.calclog+"hopmodel : 60 min hops = %.2f gm\n" %(weight14_60 + weight12_60)
	
		self.calclog = self.calclog+"hopmodel : 15 min 14L from 20L kettle %.4f from %.2f gm @ %.4f\n" %(hops14_15,weight14_15,1+(kettle_gravity_14/1000))
		self.calclog = self.calclog+"hopmodel : 15 min 12L from 15L kettle %.4f from %.2f gm @ %.4f\n" %(hops12_15,weight12_15,1+(kettle_gravity_12/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 15 min %.1f %% of %.2f + %.1f %% of %.2f + %.1f %% of %.2f= %.2f\n"  %( 14/working_batch_size_D,hops14_15,working_batch_size_D,hops12_15,( (int(working_batch_size_D+1)-26)/working_batch_size_D ) ,hopsX_15,recalc_hop_15)
		self.calclog = self.calclog+"hopmodel : 15 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_15,weightX_15,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 15 min hops = %.2f gm\n" %(weight14_15 + weight12_15+weightX_15)

		self.calclog = self.calclog+"hopmodel : 0 min %.0fL from Topup kettle %.4f from %.2f gm @ %.4f\n" %(int(working_batch_size_D+1)-26, hopsX_0,weightX_0,1+(kettle_gravity_X/1000))
		self.calclog = self.calclog+"hopmodel : 0 min hops = %.2f gm\n" %(weightX_0)
		self.calclog = self.calclog+"hopmodel :   ---> Total hops = %.2f gm\n" %(weight14_15 + weight12_15+ weightX_15+ weight14_60+weight12_60+weightX_0)

		self.calclog = self.calclog+ "hopmodel :  ---> Adjusted hop alpha could be %.2f\n" %(recalc_hop_15+recalc_hop_60+recalc_hop_0)
		HOP_MODELLING.append( recalc_hop_15 + recalc_hop_60 + recalc_hop_0 )
		tmp_ibu=recalc_hop_15+recalc_hop_60+recalc_hop_0
		HOP_MODELLING.append( tmp_ibu )
		if not HOP_MODELS.has_key( tmp_ibu ):	HOP_MODELS[ tmp_ibu] = []
		HOP_MODELS[ tmp_ibu ].append('diffgravi-latebittering')

	
	def gravityTempAdjustment(self,intemp,gravity,caltemp=68):
		temp = ( intemp *1.8)+32
		answer = gravity * (1.00130346 - 1.34722124E-4 * temp + 2.04052596E-6 * temp * temp - 2.32820948E-9 * temp * temp * temp) / (1.00130346 - 1.34722124E-4 * caltemp + 2.04052596E-6 * caltemp * caltemp - 2.32820948E-9 * caltemp * caltemp * caltemp)

		return answer


	
