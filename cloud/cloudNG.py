from __future__ import division


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
#from brewerslabEngine import *
from brewerslabData import *
import math
import base64
import hashlib
import re
import os
import time




class brewerslabCloudApi:
	
	def __init__(self):
		self.keg_sugar_proportion = 0.8
		self.bottle_sugar_proportion=1
		self.polypin_sugar_proportion=0.3
		self.strikeTempSkew=-2		# reduce strike temp by this many degC

		self.dbWrapper= db()
		self.userid="allena29"
#		self.data = brwlabPresetData( self.userid )
		self.standalonemode=False
		self.data=None
		self.recipe=None
		self.brewlog=None	
		self.activity=None
		self.process=None
		self.stores=None
#		self.stores= pickle.loads( open("store/%s/store" %(self.userid)).read() )

		self.TAKESTOCK_kegs=-1
		self.TAKESTOCK_bottles=-1
		self.TAKESTOCK_polypins=-1
		self.TAKESTOCK_priming_sugar_reqd=-1
		self.TAKESTOCK_priming_sugar_qty=-1
		self.TAKESTOCK_priming_water_required=-1
	
	def dbgRestart(self):
		self.recipe=None
		self.brewlog=None
		self.activity=None
		self.process=None
		self.stores= pickle.loads( open("store/%s/store" %(self.userid)).read() )
		return 1


	def listRecipes(self, username):
		sys.stderr.write("\nSTART: listRecipes()\n")
		try:

			recipeList=[]
			ourRecipes = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1", username)
			for recipe in ourRecipes.fetch(2000):
				recipeList.append( recipe.recipename )
			recipeList.sort()


			sys.stderr.write("END: listRecipes()\n")
			return {'operation' : 'listRecipes', 'status' : 1, 'json' : json.dumps( {'result': recipeList} ) }
		except ImportError:
			sys.stderr.write("EXCEPTION: listRecipes()\n")
			return {'operation' : 'listRecipes', 'status' : 0}



	def listActivitiesFromBrewlog(self,username,process,recipe,brewlog):
		"""
		listActivitiesFromBrewlog
		returns activities without actually opening the brewlog
		
		returns standard header
		"""
		sys.stderr.write("\nSTART: listActivitiesFromBrewlog() -> %s\n" %(brewlog))

		#
		# Note: recipe isn't really needed here but we have retained it to keep cloudApi
		# aligned with the previous xmlrpc 
		#
		try:

	
			# we can't really expect the sender to know the process based on the recipe only

			ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2", username,brewlog).fetch(1)[0]
			process = ourProcess.process
		
			activities=[]
			completeactivities=[]
			ourActivities = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum = :3 AND subStepNum = :4 AND activityNum > :5 ORDER BY activityNum", username,process,-1,-1,-1).fetch(3244)
			for activity in  ourActivities:
				activities.append(activity.stepName)

				ourCompleteOrNot = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND subStepNum = :4 ORDER BY stepNum DESC",username,brewlog,activity.activityNum,-1).fetch(1)[0]
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
			sys.stderr.write("END: listActivitiesFromBrewlog() -> %s\n" %(brewlog))
			return {'operation' : 'listActivitiesFromBrewlog', 'status' : 1, 'json' : json.dumps( {'result': result} ) }
		except ImportError:
			sys.stderr.write("EXCEPTION: listActivitiesFromBrewlog()\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))

		return {'operation' : 'listActivitiesFromBrewlog', 'status' : 0}
	

	
	def listBrewlogsByRecipe(self,username,recipeName,raw=False):
		sys.stderr.write("\nSTART: listBrewlogsByRecipes() -> %s\n" %(recipeName))

		try:
			ourRecipes = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			tmp = ourRecipes.fetch(1)[0]
			PROCESS=tmp.process
			sys.stderr.write("PROCESS = %s\n" %(PROCESS))	
			brewlogList=[]
			ourRecipes = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND recipe = :2", username,recipeName)
			for recipe in ourRecipes.fetch(2455):	


				ourActivities = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum = :3 AND subStepNum = :4 AND activityNum > :5 ORDER BY activityNum", username,PROCESS,-1,-1,-1).fetch(2343)
				allComplete=True
				sys.stderr.write("this might be possible to bring back in if we solve the scrambled results\n\n")
				for activity in  ourActivities:
					ourCompleteOrNot = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND subStepNum = :4 ORDER BY stepNum DESC",username,recipe.brewlog,activity.activityNum,-1).fetch(1)[0]
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
			ourProcesses = self.dbWrapper.GqlQuery("SELECT * FROM gProcesses WHERE owner = :1 ORDER BY process DESC", username).fetch(234234)
			for op in ourProcesses:
				pl[ op.process ] = 1
			processList=[]
			for x in pl:
				processList.append(x)
			processList.sort()
			processList.reverse()


			sys.stderr.write("END: listBrewlogsByRecipe()\n")
			if raw:	
				return {'result':brewlogList,'result2':processList}

			return {'operation' : 'listBrewlogByRecipe', 'status' : 1, 'json' : json.dumps( {'result': brewlogList,'result2':processList} ) }

		except ImportError:
			sys.stderr.write("EXCEPTION: listBrewlogsByRecipe()\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s\n" %(e))

			if raw:
				return
			return {'operation' : 'listBrewlogByRecipe', 'status' : 0}


		
	def setAlkalinity(self,username,recipeName, newAlkalinity,doRecalculate="1"):
		# flag recipe rcalc at the recipe level
		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		for recipe in ourRecipe.fetch(500):
			if not doRecalculate == "1":
				recipe.calculationOutstanding=True
			recipe.alkalinity=float(newAlkalinity)
			recipe.put()
		if doRecalculate == "1":
			self.calculateRecipe(username,recipeName)
			self.compile(username,recipeName,None)

	def setFermTemp(self,username,recipeName, newFermTemp,newLowFermTemp=None,newHighFermTemp=None,doRecalculate="1",):
		# flag recipe rcalc at the recipe level#
		sys.stderr.write(" %s %s \n" %(newLowFermTemp,newHighFermTemp))
		if not newLowFermTemp:
			newLowFermTemp=float(newFermTemp)-0.3
		if not newHighFermTemp:
			newHighFermTemp=float(newFermTemp)+0.3

		sys.stderr.write(" %s %s \n" %(newLowFermTemp,newHighFermTemp))
		
		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		for recipe in ourRecipe.fetch(500):
			if not doRecalculate == "1":
				recipe.calculationOutstanding=True
			recipe.fermTemp=float(newFermTemp)
			recipe.fermLowTemp=float(newLowFermTemp)
			recipe.fermHighTemp=float(newHighFermTemp)
			recipe.put()
		if doRecalculate == "1":
			self.calculateRecipe(username,recipeName)
			self.compile(username,recipeName,None)



	def setMashTemp(self,username,recipeName, newMashTemp,doRecalculate="1"):
		# flag recipe rcalc at the recipe level
		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		for recipe in ourRecipe.fetch(500):
			if not doRecalculate == "1":
				recipe.calculationOutstanding=True
			recipe.target_mash_temp=float(newMashTemp)
			recipe.put()
		if doRecalculate == "1":
			self.calculateRecipe(username,recipeName)
			self.compile(username,recipeName,None)

	def setMashEfficiency(self,username,recipeName, newMashEfficiency,doRecalculate="1"):
		if 1==1:
			# flag recipe rcalc at the recipe level
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				if not doRecalculate == "1":
					recipe.calculationOutstanding=True
				recipe.mash_efficiency=float(newMashEfficiency)
				recipe.put()
			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)



	def setBatchSize(self,username,recipeName, newBatchSize,doRecalculate="1"):
		"""
		setBatchSize(batchSize)
			batchSize = Final batchSize in Litres after taking account of losses
		
		return: standard api header
		"""
		sys.stderr.write("\nSTART: setBatchSize()  recipeName %s newBatchSize %s\n" %(recipeName,newBatchSize));
		status=0



		try:
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND brewlog = :3", username,recipeName,"")
			for recipe in ourRecipe.fetch(500):
				recipe.batchsize=int(newBatchSize)
				if doRecalculate == "0":	recipe.calculationOutstanding=True
				recipe.put()

			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)



			# flag recipe rcalc at the recipe level
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.batch_size_required=int(newBatchSize)
				recipe.calculationOutstanding=True
				recipe.put()
			sys.stderr.write("recipeBatchSize set on gRecipes and gRecipStats\n")	
		
			status=1
			result={}
			result['stats']={}
			result['stats']['batch_size_required']=int(newBatchSize)

			sys.stderr.write("END: setBatchSize()  recipeName %s newBatchSize %s\n" %(recipeName,newBatchSize));
			return {'operation' : 'setBatchSize','status' :status , 'json': json.dumps(result)  }
		except ImportError:
			sys.stderr.write("EXCEPTION: setBatchSize()  recipeName %s newBatchSize %s\n" %(recipeName,newBatchSize));
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))


		return {'operation' : 'setBatchSize','status' : status}




	def setTopupVolume(self,username, recipeName,topupVol,doRecalculate="1"):

		"""
		setTopupVolume(topupVol)
			topulVol = Topup to be provided in Litres after boil

		return: standard api header
		"""
		sys.stderr.write("\nSTART: setTopupVolume -> %s\n" %(topupVol))
		status=0
		result={}
		try:
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.postBoilTopup = float(topupVol)
				if doRecalculate == "0":	recipe.calculationOutstanding=True
				recipe.put()


			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)
			result={}
			result['stats']={}
			result['stats']['postBoilTopup']=float(topupVol)
			status=1
			sys.stderr.write("END: setTopupVolume -> %s\n" %(topupVol))
		except ImportError:
			sys.stderr.write("EXCEPTION: setTopupVolume -> %s\n" %(topupVol))
		return {'operation' : 'setTopupVolume','status' :status , 'json': json.dumps(result)  }




	def listIngredients(self,category):
		"""
		listIngredients(category)
			category = 	fermentable,hop,yeast,misc,consumable
			
		return: list of ingredients from the presets file
		"""
		sys.stderr.write("\nSTART: listIngredients()\n")
		status=0
		try:
			response = {'operation' : 'listIngredients', 'status' : 1,
					'json' : "%s" %( self.data.dumpJSON( category )  ) 
				}
			sys.stderr.write("END: listIngredients()\n")
			return response
		except ImportError:	pass
		sys.stderr.write("EXCEPTION: listIngredients()\n")
		return {'operation' : 'listIngredients', 'status' : status }



	def listIngredientDetail(self,category,ingredient):
		"""
		listIngredientDetail(category, ingredient)
			category = 	fermentable,hop,yeast,misc,consumable
			ingredient = 	string values
			
		return: dict of ingredient detail
		"""
		sys.stderr.write("\nSTART: listIngredientsDetails()\n")
		status=0

		try:
			response = {'operation' : 'listIngredientDetail', 'status' : 1,
					'json' : "%s" %( self.data.dumpDetailJSON( category, ingredient )  ) 
				}
			sys.stderr.write("END: listIngredientsDetails()\n")
			return response
		except ImportError:	pass
		sys.stderr.write("EXCEPTION: listIngredientsDetails()\n")
		return {'operation' : 'listIngredients', 'status' : status }



	def listProcess(self,username):
		"""
		listProcesses

		return: list of processes
		"""
		sys.stderr.write("\nSTART: listProcess()\n")
		p=[]
		sys.stderr.write("listProcess\n")
		ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gProcesses WHERE owner = :1",username)
		for process in ourProcess.fetch(5000):
			p.append(process.process)

		p.sort()
		sys.stderr.write("END: listProcess()\n")
		return {'operation' : 'listProcess', 'status' : 1,'json':json.dumps( {'result': p}  ) }


	def setProcess(self,process):
		"""
		setProcess
			process	=	processLabel (as per listProcess)

		return:	standard header
		"""
		status=0
		sys.stderr.write("\nSTART: setProcess()\n")
		try:
	
			myprocess = pickle.loads(open("process/%s/%s" %(self.userid,process)).read())
			self.recipe.attachProcess( myprocess )
			status=1
		except ImportError: 
			traceback.print_exc()
		sys.stderr.write("END: setProcess()\n")
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
		sys.stderr.write("\nSTART: addHopIngredientToRecipe() -> %s %s %s\n" %(ingredient,qty,hopAddition))
		try:
			if self.recipe:
				recipeObject = self.data.getHop( ingredient )
				self.recipe.addIngredient( recipeObject, qty, hopAddition )	
				try:
					self.recipe.calculate()
				except ImportError:
					sys.stderr.write("EXCEPTION2: addHopIngredientToRecipe() -> %s %s %s\n" %(ingredient,qty,hopAddition))
					traceback.print_exc()
					status=0
				status =1
		except ImportError:
			sys.stderr.write("EXCEPTION: addHopIngredientToRecipe() -> %s %s %s\n" %(ingredient,qty,hopAddition))

		sys.stderr.write("END: addHopIngredientToRecipe() -> %s %s %s\n" %(ingredient,qty,hopAddition))
		return {'operation' : 'addHopIngredientToRecipe','status':status}


	def addIngredientToRecipe(self, category, ingredient, qty):
		"""
		addIngredientToRecipe(category,ingredient,qty)
			cateogry =	fermentable,hop,yeast,misc,consumable
			ingredient = 	string value as found from listIngredient/listIngredientDetails
			qty =		qty to add (as per unit on listIngredientDetails)

		return:	standard header
		"""

		sys.stderr.write("\nSTART: addIngredientToRecipe() -> %s %s\n" %(ingredient,qty))
		status=0
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
					except ImportError:
						sys.stderr.write("EXCEPTION2: addIngredientToRecipe() -> %s %s\n" %(ingredient,qty))
						traceback.print_exc()
						status=0
					status =1
		except ImportError:
			sys.stderr.write("EXCEPTION: addIngredientToRecipe() -> %s %s\n" %(ingredient,qty))

		sys.stderr.write("END: addIngredientToRecipe() -> %s %s\n" %(ingredient,qty))
		return {'operation' : 'addIngredientToRecipe','status':status}


	def getWaterRequired(self):
		"""
		getWaterRequried()

		return:	integer of total water required for the brew in litres
		"""

		sys.stderr.write("\nSTART: getWaterRequried()\n")
		if self.recipe:
			try:
				waterRequired = self.recipe.calculate()
			except ImportError:
				sys.stderr.write("EXCEPTION: getWaterRequried()\n")
				traceback.print_exc()
				return {'operation' : 'addIngredientToRecipe','status':0}
			waterRequired= self.recipe.waterRequirement()
			sys.stderr.write("END: getWaterRequried()\n")
			return {'operation' : 'getWaterRequired', 'status' : 1, 'json' : json.dumps( {"result":waterRequired} ) }

		sys.stderr.write("EXCEPTION0: getWaterRequried()\n")
		return {'operation' : 'addIngredientToRecipe','status':0}



	def scaleAlcohol(self,newABV):
		"""
		scaleABV()
			float of required abv			
	
		return:	float with response
		"""

		sys.stderr.write("\nSTART: scaleAlochol() %s\n" %(newABV))
		if self.recipe:
			try:
				self.recipe.scaleAlcohol( newABV )
				sys.stderr.write("END: scaleAlochol() %s\n" %(newABV))
				return {'operation' : 'scaleAlcohol', 'status' : 1, 'json' : json.dumps( {"result": self.recipe.estimated_abv } ) }
			except ImportError:
				sys.stderr.write("EXCEPTION: scaleAlochol() %s\n" %(newABV))
				traceback.print_exc()

		return {'operation' : 'scaleAlcohol','status':0}



	def scaleIBU(self,username,recipeName,newIBU,doRecalculate="1"):
		"""
		scaleIBU()
			float of required ibu
	
		return:	float with response
		"""

		sys.stderr.write( "\nSTART: scaleIBU() -> %s\n" %(newIBU))

		#
		#	 note this should probably use gContributions to do the scaling
		#

		return {'operation' : 'scaleIBU','status':-5}		# NOT SUPPOrtED
		"""


		try:
			
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
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
		except ImportError:
			sys.stderr.write("EXCEPTION in setBatchSize\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))

				#print self.recipe.calclog	
#				exc_type, exc_value, exc_traceback = sys.exc_info()
#				for e in traceback.format_tb(exc_traceback):	print e

		return {'operation' : 'scaleIBU','status':0}



		"""




	def startNewBrewlog(self,username,name,recipeName,process,reset=0):
		"""
		startNewBrewLog()
			string name of the brewlog

		return: standard response header
		"""
		sys.stderr.write("\nSTART: startNewBrewlog() %s/%s/%s /%s\n" %(name,recipeName,process,reset))
		status = 0


		if not reset:
			existingBrewlog = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,name).fetch(1)
			if len(existingBrewlog):
				return {'operation' : 'startNewBrewLog','status':-1}
	
		recipeDetails = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2",username,recipeName).fetch(1)
		if len(recipeDetails) == 0:
			return {'operation' : 'startNewBrewLog','status':-2}
		

		if reset == 1:
			sys.stderr.write("RESETTING BREWLOG\n")
			ourOldBrewlogSteps = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2",username,name).fetch(500000000)
			for x in ourOldBrewlogSteps:
				x.delete()

			ourOldFields=self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2",username,name).fetch(4324234)	
			for x in ourOldFields:
				x.delete()

			sys.stderr.write("process %s\n" %(process))

		if not reset:
			brwlog = gBrewlogs( recipe=recipeName,brewlog=name,owner=username )
			brwlog.db=self.dbWrapper
			brwlog.realrecipe = recipeName
			brwlog.process=process
			brwlog.boilVolume = recipeDetails[0].boilVolume
			brwlog.brewhash = base64.b64encode("%s/%s/%s" %(username,recipeName,name))
			brwlog.put()	
		

		# keep a copy of our RecipeStats safe from future recipe updates
		# we might not actually have recipeStats for this process yet. So this should have been a best effort attempt
		ourRecipeStats = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND brewlog = :3 AND process = :4",username,recipeName,"",process).fetch(500000)[0]

		newRecipeStats = gRecipeStats(owner=username,process=process,recipe=recipeName)
		newRecipeStats.db=self.dbWrapper
		try:
			for x in ourRecipeStats.__dict__:
				if x != "entity":
					newRecipeStats.__dict__[x] = ourRecipeStats.__dict__[x]		
		except ImportError:
			pass
		newRecipeStats.brewlog=name
		newRecipeStats.put()	



		ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum > :3",username,process,-1).fetch(500000)
		sortIndex=0
		for processStep in ourProcess:

			# OCT2015 removed conditionals becuase they didn't work
			# and we have started to use step.auto instead
			stp = gBrewlogStep(recipe=recipeName,brewlog=name,activityNum=processStep.activityNum, stepNum=processStep.stepNum, subStepNum=processStep.subStepNum,owner=username,sortIndex=sortIndex )
			stp.db=self.dbWrapper
			stp.stepName=processStep.stepName
			stp.completed=False
			stp.numSubSteps=processStep.numSubSteps
			stp.needToComplete=processStep.needToComplete
			stp.put()
			sortIndex=sortIndex+1


		ourFields=self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND process = :2",username,process).fetch(4324234)	
		for field in ourFields:
			blankfield=gField(owner=username,stepNum=field.stepNum,activityNum=field.activityNum)
			blankfield.db=self.dbWrapper
			blankfield.brewlog=name
			blankfield.fieldKey=field.fieldKey
			blankfield.fieldWidget=field.fieldWidget
			blankfield.fieldTimestamp=field.fieldTimestamp
			blankfield.put()

		status =1
			
		
		sys.stderr.write("END: startNewBrewlog %s/%s/%s /%s\n" %(name,recipeName,process,reset))
		return {'operation' : 'startNewBrewLog','status':status,'json': json.dumps({}) }
			




	def listActivities(self):
		"""
		listActivities()
			string activity
	
		call selectProcess() first
		return: standard response header
		"""
		sys.stderr.write("\nSTART: listActivities()\n")
		status=0
		activities=[]
		try:
			for activity in self.process.activities:
				activities.append(activity.activityTitle)
			sys.stderr.write("END: listActivities()\n")
			return {'operation' : 'listActivities', 'status' : 1, 'json' : json.dumps( {"result": activities } ) }
		except ImportError:
			sys.stderr.write("EXCEPTION: listActivities()\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)







	def listActivitySteps(self,username,process,activity,brewlog,includeSubStepDetails=False):
		"""
		listActivitySteps()

		call openBrewlog() and selectActivity() first
		return: response header with steps required


		Note: changed to send process/activity on every call. and send brewlog


		"""

		sys.stderr.write("\nSTART: listActivitySteps %s/%s\n" %(process,activity))

		try:
			steps=[]
			stepNum=0
#			for step in self.activity.steps:
			#note we need to look for the process by numbe rnot name
			ourActivity =self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3",username,process,activity).fetch(1)[0]


			ourSteps =self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND activityNum = :2 AND stepNum > :3 AND subStepNum = :4 AND brewlog = :5 ORDER BY stepNum",username, ourActivity.activityNum,-1,-1,brewlog)
			for step in ourSteps.fetch(4000):
				newstep = {}
				newstep['stepNum']=step.stepNum
				newstep['sortindex']=step.sortIndex	
				newstep['name'] = step.stepName
				newstep['complete'] = False
				if int(step.numSubSteps) == 0:
					newstep['hasSubSteps'] =  False
				else:
					newstep['hasSubSteps'] = True
				sys.stderr.write(" stepid %s / numSubSteps %s / %s\n" %(step.stepNum,step.numSubSteps,newstep['hasSubSteps']))
				if step.subStepsCompleted == True:
					newstep['complete']=True	
				else:
					newstep['complete']=False


				steps.append(newstep)
				sys.stderr.write("END: listActivitySteps %s/%s\n" %(process,activity))
			return {'operation':'listActivitySteps','status':1,'json' : json.dumps( {'result': steps } ) }
		except ImportError:
			sys.stderr.write("EXCEPTION: listActivitySteps %s/%s\n" %(process,activity))
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)

		return {'operation':'listActivitySteps','status':0}




	def listProcesses(self):
		"""
		listProcesses()
		
		return: list with processes in resonse header
		"""
		try:
			sys.stderr.write("\nSTART: listProcesses\n")
			processList=[]
			for process in os.listdir( "process/%s/" %(self.userid) ):
				tmp = pickle.loads(open("process/%s/%s" %(self.userid,process)).read())
				processList.append( tmp.name )
			processList.sort()
			
			sys.stderr.write("END: listProcesses\n")
			return {'operation' : 'listProcesses', 'status' : 1, 'json' : json.dumps( {'result': processList} ) }
		except ImportError:
			sys.stderr.write("EXCEPTION: listProcesses\n")
			return {'operation' : 'listProcesses', 'status' : 0}


	def setFieldWidget(self,username,brewlog,process,activityNum,stepNum,fieldKey,fieldVal, guiId):
		"""
		saveFieldWidget
			integer: stepNum
			String: fieldKey
			String: fieldVal
			Integer: guiId 		<passed back transparently>
		"""

		sys.stderr.write("\nSTART: setFieldWidget() %s %s %s %s %s %s %s\n" %("process no longer used",brewlog,activityNum,stepNum,fieldKey,fieldVal,guiId))


		ourField=self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND fieldKey = :5",username,brewlog,activityNum,stepNum,fieldKey).fetch(1)[0]
		ourField.fieldVal = fieldVal
		ourField.fieldTimestamp=int(time.time())
		ourField.put()

		result={}
		result['value'] = fieldVal
		result['guiid'] = guiId

		if ourField.fieldWidget:
			result['value'] = self._widgets(username,process,brewlog,ourField.fieldKey)
			ourField=self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND fieldKey = :5",username,brewlog,activityNum,stepNum,fieldKey).fetch(1)[0]
			ourField.fieldVal = result['value']
			sys.stderr.write(" Answer to widget: %s\n" %(ourField.fieldVal))
			ourField.put()


		sys.stderr.write("END: setFieldWidget() %s %s\n" %(fieldKey,fieldVal))
		return {'operation':'setFieldWidget','status':1,'json': json.dumps( {'result': result } ) }
			


	def _widgetData(self,username,brewlog,field):
		sys.stderr.write("\nSTART: _widgetData() %s %s\n" %(brewlog,field))
		FIELD=field
		field =field.lower()
		
		ourData =self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3",username,brewlog,field).fetch(1)

		if not len(ourData):
			field=FIELD
			ourData =self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3",username,brewlog,field).fetch(1)

		if len(ourData):
			sys.stderr.write("END: _widgetData() %s %s %s\n" %(brewlog,field,ourData[0].fieldVal))
			return ourData[0].fieldVal



		ourBrewlog =self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]

		ourData =self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3 AND brewlog = :4",username,ourBrewlog.realrecipe,ourBrewlog.process,brewlog).fetch(1)[0]
		
		if ourData.__dict__.has_key("_%s" %(field)):
			sys.stderr.write("END: _widgetData() %s %s %s\n" %(brewlog,field,ourData.__dict__["_%s" %(field)]))
			return ourData.__dict__["_%s" %(field)]


	def crsAdjustment(self,alkalinity,volume,alkalinityRequired=50):
		sys.stderr.write("\nSTART: crsAdjustment() %s %s %s\n" %(alkalinity,volume,alkalinityRequired))
		# based upon maltmiller table
		# AMS		0.6	1.5	3	4.6	6	9.2	12.2	15.3	18.4
		# Chloride ppm	4	9.9	19.7	29.6	39.5	59.2	78.9	98.7	118.4
		# Sulphate ppm	4.4	13.6	27.2	40.8	54.4	81.6	108.8	136.1	163.3
		# Reduction	-11	-28	-56	-84	-112	-168	-224	-280	-337
		# ml/L		-1.8333	-1.8666	-1.866	-1.8267	-1.8667	-1.8287	-1.836	-1.835	-1.8315
		# average -1.842573324306			1									
		crsPer10Ml=-18.425733243061									

		reductionRequired=alkalinityRequired-alkalinity
		crsRequired=reductionRequired /crsPer10Ml
		crsRequired=reductionRequired / crsPer10Ml/10
		sys.stderr.write("END: crsAdjustment() %.2f ml\n" %( crsRequired))
		return crsRequired * volume


	def salifert(self,reagentLeft,highRes=False):
		sys.stderr.write("\nSTART: salifert() %s %s\n" %(reagentLeft,highRes))
		# takes in reagent remaining in the syringe in ml and returns hardness as CAC03

		salifert=[	(0,5.59),
				(0.02,5.48),
				(0.04,5.36),
				(0.06,5.26),
				(0.08,5.13),
				(0.1,5.02),
				(0.12,4.9),
				(0.14,4.79),
				(0.16,4.68),
				(0.18,4.56),
				(0.2,4.45),
				(0.22,4.33),
				(0.24,4.22),
				(0.26,4.1),
				(0.28,3.99),
				(0.3,3.88),
				(0.32,3.76),
				(0.34,3.65),
				(0.36,3.53),
				(0.38,3.42),
				(0.4,3.3),
				(0.42,3.19),
				(0.44,3.08),
				(0.46,2.96),
				(0.48,2.85),
				(0.5,2.73),
				(0.52,2.62),
				(0.54,2.5),
				(0.56,2.39),
				(0.58,2.28),
				(0.6,2.16),
				(0.62,2.05),
				(0.64,1.93),
				(0.66,1.82),
				(0.68,1.7),
				(0.7,1.59),
				(0.72,1.48),
				(0.74,1.36),
				(0.76,1.25),
				(0.78,1.13),
				(0.8,1.02),
				(0.82,0.9),
				(0.84,0.79),
				(0.86,0.67),
				(0.88,0.056),
				(0.9,0.45),
				(0.92,0.33),
				(0.940000000000001,0.1),
				(0.960000000000001,0),
				(0.980000000000001,0),
				(1,0) 	]
		answer=-100
		for (x,y) in salifert:
			if x < reagentLeft:
				answer=y

		if not highRes:
			# low resolution mode
			answer=answer*2
		# answer is meq/L, but we want CaCO3
		answer=answer*50
		sys.stderr.write("END: salifert() %s\n" %(answer))
		return answer


	def _widgets(self,username,process,brewlog,widget):
		sys.stderr.write("\nSTART: _widgets() %s %s %s %s\n" %(username,process,brewlog,widget))
		ourWidget = self.dbWrapper.GqlQuery("SELECT * FROM gWidgets WHERE owner = :1 AND process = :2 AND widgetName = :3",username,process,widget).fetch(1)[0]

		widgetType=ourWidget.widget		
		widgetData=ourWidget.widgetValues

		if widget == "mashCrsAdjustment":
			ourData =self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3",username,brewlog,"mashAlkalinity").fetch(1)[0]
			alkalinity=float(ourData.__dict__['fieldVal'])
			ourData =self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]
			mashLiquid6=ourData.__dict__["mash_liquid_6"]
			answer = "%.2f" %( self.crsAdjustment(alkalinity,mashLiquid6)*.75 )
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer
		if  widget == "mashCrsAdjustmentRetest":
			ourData =self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3",username,brewlog,"mashAlkalinityRetest").fetch(1)[0]
			alkalinity=float(ourData.__dict__['fieldVal'])
			ourData =self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]
			mashLiquid6=ourData.__dict__["mash_liquid_6"]
			answer = "%.2f" %( self.crsAdjustment(alkalinity,mashLiquid6)*.75 )
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer

		if widget == "spargeCrsAdjustment":
			ourData =self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3",username,brewlog,"spargeAlkalinity").fetch(1)[0]
			alkalinity=float(ourData.__dict__['fieldVal'])
			ourData =self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]
			spargeWater=ourData.__dict__["sparge_water"]
			answer ="%.2f" %( self.crsAdjustment(alkalinity,spargeWater) )
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer

			
		if widgetType == "salifertAlkalinity":
			sys.stderr.write(" slaifertAlkalinity %s\n" %( self._widgetData(username,brewlog,widgetData[0])))
			data0=float( self._widgetData(username,brewlog,widgetData[0]))		# gravity of main wort
			# November 2010 version
			answer = "%s" %( self.salifert( data0, highRes=False ))
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer


		if widgetType == "salifertAlkalinityHighRes" or widgetType == "salifertAlkalinityHignRes":	# there is a typo here
			sys.stderr.write(" slaifertAlkalinity %s\n" %( self._widgetData(username,brewlog,widgetData[0])))
			data0=float( self._widgetData(username,brewlog,widgetData[0]))		# gravity of main wort
			# November 2010 version
			answer = "%s" %( self.salifert( data0, highRes=True ))
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer

		if widgetType == "add2number" or widgetType == "add2numbers":
			data0=float( self._widgetData(username,brewlog,widgetData[0]))		# gravity of main wort
			data1=float( self._widgetData(username,brewlog,widgetData[1]))		# gravity of topup
			answer = "%s" %(data0+data1)
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer

		if widgetType == "gravityVolAdjustment":
			g=float( self._widgetData(username,brewlog,widgetData[0]))		# gravity of main wort
			h=float( self._widgetData(username,brewlog,widgetData[1]))		# gravity of topup
			v=float( self._widgetData(username,brewlog,widgetData[2]))	#vol1
			x=float( self._widgetData(username,brewlog,widgetData[3])) # gravity target
			answer = "%.4f" %( -( (v*x)-(g*v) )/ (x-h) )
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer

		if widgetType == "combineMultipleGravity":
			grav1=float( self._widgetData(username,brewlog,widgetData[0]))
			grav2=float( self._widgetData(username,brewlog,widgetData[1]))
			vol1=float( self._widgetData(username,brewlog,widgetData[2]))
			vol2=float( self._widgetData(username,brewlog,widgetData[3]))
			totalvol=vol1+vol2
			g1 = (vol1/totalvol) * grav1
			g2 = (vol2/totalvol) * grav2
			answer= "%.4f" %(g1+g2)
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer
			
		if widgetType == "abvCalculation":
			og= float(self._widgetData(username,brewlog,widgetData[0]))
			fg= float(self._widgetData(username,brewlog,widgetData[1]))
			answer = "%.1f" %((og-fg)	 * 131)
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer

		sys.stderr.write( "widget type _%s_\n" %(widgetType))
		if widgetType == "gravityTempAdjustment" or widgetType == " gravityTempAdjustment":
			intemp= float(self._widgetData(username,brewlog,widgetData[0]))
			gravity= float(self._widgetData(username,brewlog,widgetData[1]))
			answer=self.gravityTempAdjustment(intemp,gravity)
			answer = "%.4f" %(answer)
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer

		if widgetType == "inverseGravityTempAdjustment":
			intemp= float(self._widgetData(username,brewlog,widgetData[0]))
			gravity= float(self._widgetData(username,brewlog,widgetData[1]))
			answer=self.gravityTempAdjustment(intemp,gravity,-68)
			answer = "%.4f" %(answer)
			sys.stderr.write("END: _widgets() %s %s\n" %(widget,answer))
			return answer


		sys.stderr.write("END: _widgets() %s %s\n" %(widget,'<unsupported widget>'))
		return "unsupported"
		
		

	def saveComment(self,username,brewlog,activityNum,stepNum,comment):
		"""
		saveComment
			integer:  stepNum
			String:		comment
		return standard response header
		"""

		sys.stderr.write("\nSTART: saveComment %s/%s/%s/%s\n" %(brewlog,"process not used anymore",activityNum,stepNum))

		#step = self.activity.steps[stepNum]
		existingField = self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND fieldKey = :5", username,brewlog,activityNum,stepNum,'notepage').fetch(1)
		if len(existingField):
			existingField.delete()


		com = gField( owner=username,stepNum=stepNum,activityNum=activityNum)
		com.db=self.dbWrapper
		com.brewlog=brewlog
		com.recipe="we dont have this in saveComment()"	
		com.fieldKey="notepage"
		com.fieldVal= comment
		com.fieldTimestamp = int(time.time())
		com.put()	

		sys.stderr.write("END: saveComment()\n")
		return {'operation':'saveComment','status':1 ,'json':json.dumps({})}





	def setStepComplete(self,username,brewlog,activityName,stepNum,complete):
		"""
		setStepComplete
			integer:  stepNum
			Boolean:  complete or not complete	
		return standard response header
		"""
		sys.stderr.write("\nSTART: setStepComplete() %s/%s/%s/%s\n" %(brewlog,activityName,stepNum,complete))
		thisProcess = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]
		thisActivity = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,thisProcess.process, activityName,-1).fetch(1)[0]
		if complete == "1":
			activityStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,-1,-1).fetch(1)[0]

		thisStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1)[0]
		stepNum=int(stepNum)
		
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
		if complete == "1":
			result['label'] = "%s / %s" %(activityStep.stepName, thisStep.stepName)

		sys.stderr.write("END: setStepComplete() %s/%s/%s/%s\n" %(brewlog,activityName,stepNum,complete))
		return {'operation':'setStepComplete','status':1,'json': json.dumps( {'result': result } ) }




	def setSubStepComplete(self,username,brewlog,activityName,stepNum,subStepNum,completed):
		"""
		setSubStepComplete
			integer:  stepNum
			integer:  subStepNum
			Boolean:  complete or not complete	
		return standard response header with percentage for progress bar and lastcompletestatus
		"""
		sys.stderr.write("\nSTART: setSubStepComplete %s/%s/%s/%s/%s\n" %(brewlog,activityName,stepNum,subStepNum,completed))

		thisProcess = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)[0]
		thisActivity = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,thisProcess.process, activityName,-1).fetch(1)[0]
		
		if completed == "1":
			activityStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,-1,-1).fetch(1)[0]
			parentStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1)[0]		
		thisStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),int(subStepNum)).fetch(1)[0]


		if completed == "1":
			thisStep.completed=True
			thisStep.stepEndTime=int(time.time())
			lastCompleted=True

		else:
			lastCompleted=False
			thisStep.completed=False
		thisStep.put()

		theseSteps = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum > :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1000)

		sumToComplete=0
		numCompleted=0

		for substep in theseSteps:
			sumToComplete = sumToComplete +1
			if substep.completed:	
				numCompleted = numCompleted + 1
			elif substep.needToComplete == False:
				numCompleted = numCompleted + 1

		
		if sumToComplete == numCompleted:
			subStepCompletes = 100

			theParentStep= self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1)[0]
			theParentStep.subStepsCompleted=True
			theParentStep.put()



		elif sumToComplete > 0:
			subStepCompletes = (numCompleted/sumToComplete) * 100
			theParentStep= self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,brewlog,thisActivity.activityNum,int(stepNum),-1).fetch(1)[0]
			theParentStep.subStepsCompleted=False
			theParentStep.put()

		else:
			subStepCompletes = 0	
		
		result={}
		result['progress'] = int(subStepCompletes)
		result['lastcomplete'] = lastCompleted
		result['stepid'] = "%s" %(stepNum)

		if completed == "1":
			result['label'] = "%s / %s / %s" %(activityStep.stepName,parentStep.stepName, thisStep.stepName)

		if sumToComplete==numCompleted:
			result['parentComplete']=True	
		else:
			result['parentComplete']=False


		sys.stderr.write("END: setSubStepComplete %s/%s/%s/%s/%s\n" %(brewlog,activityName,stepNum,subStepNum,completed))
		return {'operation':'setSubStepComplete','status':1,'json': json.dumps( {'result': result } ) }

		return {'operation':'setSubStepComplete','status':0}





				
	def _newVariableSub(self,username,toReplace,activityNum,stepNum,stepText,recipeName,process,brewlog,begin="",finish=""):
		sys.stderr.write("\nSTART: newVariableSub %s/%s/%s/%s/%s/\n" %(username,toReplace,activityNum,stepNum,stepText))
		stat = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3 AND brewlog = :4",username,recipeName,process,brewlog).fetch(1)
		if len(stat) == 0:
			return stepText		
		stat = stat[0]

		"""
Bug with Mini-keg qty here:
START: newVariableSub test@example.com/[u'minikegqty']/2/2/Gather ...minikegqty... minikegs/
QUERY: SELECT * FROM gRecipeStats WHERE owner ='test@example.com' AND recipe ='zzzz' AND process ='40AG' AND brewlog ='29.10.2015'
        dbg:_newVariableSub() trying to replace 'minikegqty' - in gRecipeStats as '0.0'
END: newVariableSub()

mysql>  SELECT minikegqty FROM gRecipeStats WHERE owner ='test@example.com' AND recipe ='zzzz' AND process ='40AG' AND brewlog ='29.10.2015';
+------------+
| minikegqty |
+------------+
|          1 |
+------------+

issue is within ngData.py not within logic of cloudNG
"""
		for tr in toReplace:
			if not stat.__dict__.has_key("%s" %(tr)):
				val="?"
				sys.stderr.write("\tdbg:_newVariableSub() trying to replace '%s' - not in gRecipeStats\n" %(tr))
			else:
				val = stat.__dict__["%s" %(tr)]
				sys.stderr.write("\tdbg:_newVariableSub() trying to replace '%s' - in gRecipeStats as '%s'\n" %(tr,val))

			val="%s%s%s" %(begin,val,finish)
			stepText=re.compile("\.\.\.%s\.\.\." %(tr)).sub("%s" %(val),stepText)
			

		sys.stderr.write("END: newVariableSub()\n")
		return stepText


		




	def getSubStepDetail(self,username,process,activityNum,brewlog,stepNum,recipeName,subStepNum):
		sys.stderr.write("\nSTART: getSubStepDetail()\n")
		r=self.getStepDetail(username,process,activityNum,brewlog,stepNum,recipeName,subStepNum)
		sys.stderr.write("END: getSubStepDetail()\n")
		return {'operation':'getSubStepDetail','status':1,'json': r['json'] }


	def getStepDetail(self,username,process,activityNum,brewlog,stepNum,recipeName,subStepNum=-1):
		"""
		getStepDetail()
			integer:  stepNum
			
		return data in response header
		"""
		sys.stderr.write("\nSTART: getStepDetail() %s/%s/%s/%s/%s" %(process,activityNum,brewlog,stepNum,recipeName))
		ourActivity =self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,process,activityNum,-1).fetch(1)[0]

		stepNum = int(stepNum)

		theStep =self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5",username,process,ourActivity.activityNum,int(stepNum),-1).fetch(1)[0]

		ourStep =self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum = :5 ORDER BY subStepNum",username,brewlog,ourActivity.activityNum,stepNum,-1).fetch(1)[0]

		try:
			newStep={}
			newStep['subStepNum']=int(subStepNum)
			ourCompiles = self.dbWrapper.GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,process,ourActivity.activityNum,stepNum).fetch(1)
			if len(ourCompiles) < 1:
				ouc = []
			else:
				ouc =ourCompiles[0].toReplace

			newStep['title'] = theStep.stepName
			newStep['stepNum'] = stepNum
			newStep['text']= self._newVariableSub(username,ouc,"","",theStep.text,recipeName,process,brewlog)
			newStep['img'] = theStep.img
			if ourStep.completed:
				newStep['complete'] = True
				newStep['completeDate'] = time.ctime( int(ourStep.stepEndTime ))
			else:
				newStep['complete'] = False


			sys.stderr.write("SELECT * FROM gBrewlogStep WHERE owner = %s AND brewlog = %s AND activityNum = %s AND stepNum = %s AND subStepNum >  %s ORDER BY subStepNum\n" %(username,brewlog,ourActivity.activityNum,stepNum,-1))
			ourSubSteps =self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum > :5 ORDER BY subStepNum",username,brewlog,ourActivity.activityNum,stepNum,-1).fetch(545551)

			sys.stderr.write("----------substep %s\n" %(ourSubSteps))
			newStep['substepnumber'] = len(ourSubSteps)
			newStep['substeps']=[]




			for substep in ourSubSteps:
				newStep['substeps'].append({})

				newStep['substeps'][-1]['needtocomplete'] = substep.needToComplete
				newStep['substeps'][-1]['subStepNum']=substep.subStepNum
				if not substep.needToComplete:
					newStep['substeps'][-1]['needtocomplete']=False
				if substep.completed:
					newStep['substeps'][-1]['complete'] = True
					newStep['substeps'][-1]['completeDate'] = time.ctime( int(substep.stepEndTime ))
				else:
					newStep['substeps'][-1]['complete'] = False

					### TODO variable sub
				newStep['substeps'][-1]['text']= self._newVariableSub(username,ouc,ourActivity.activityNum,stepNum,substep.stepName,recipeName,process,brewlog)



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
			comments="-"
		
		
			fieldValues={}
			ourFields =self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4",username,brewlog,ourActivity.activityNum,stepNum).fetch(545551)
			for field in ourFields:
				if field.fieldKey == "notepage":
					comments= field.fieldVal+"\n"
					newStep['commentsTimestamp']=time.ctime( int(field.fieldTimestamp ))
			newStep['comments'] = comments
			newStep['widgets']=False


			# if it#s a widget add the detail in the fields
			newfields=[]	
			for field in ourFields:
				if field.fieldKey != "notepage":
					if field.fieldWidget:
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
			newStep['fields'] = newfields
			newStep['process']=process
			sys.stderr.write("END: getStepDetail() %s/%s/%s/%s/%s" %(process,activityNum,brewlog,stepNum,recipeName))
			return {'operation':'getStepDetail','status':1,'json':json.dumps( {'result' : newStep} ) }
		except ImportError:	
			sys.stderr.write("EXCEPTION: getStepDetail() %s/%s/%s/%s/%s" %(process,activityNum,brewlog,stepNum,recipeName))
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)
			for e in traceback.format_tb(exc_traceback):	print e
		
		sys.stderr.write("END: getStepDetail() %s/%s/%s/%s/%s" %(process,activityNum,brewlog,stepNum,recipeName))
		return {'operation':'getStepDetail','status':0}



	def listProcessImages(self,username,process):
		"""
		listProcessImages()
			string: process name

		return: list images used in a response header
		"""
		sys.stderr.write("\nSTART: listProcessImages <- %s\n" %(process))
		try:
			tmpimages={}
			ourImages = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2",username,process)
			for image in ourImages.fetch(4555):
				for img in image.img:
					tmpimages[img]=1
			images=[]
			for img in tmpimages:		
				images.append(img)

			status =1

			sys.stderr.write("END: listProcessImages <- %s\n" %(process))
			return {'operation' : 'listProcessImages', 'status':1,'json' : json.dumps( {'result': images } ) }
		
		except ImportError:
			sys.stderr.write("EXCEPTION: listProcessImages <- %s\n" %(process))
			return {'operation' : 'listProcessImages', 'status':0}






	def setMashEfficiency(self,username,recipeName,efficiency,doRecalculate="1"):
		"""
		setMashEfficiency()
			integer efficiency in percentage (e.g. 67)
			this assumes the input might not be as clean as ideal

		return: standard response
		"""
		sys.stderr.write("\nSTART: setMashEfficiency() -> %s/%s\n" %(recipeName,efficiency))
		status=0
		try:

			sys.stderr.write("updated efficiency to %s\n" %(efficiency))
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
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
			sys.stderr.write("END: setMashEfficiency() -> %s/%s\n" %(recipeName,efficiency))
			return {'operation':'setMashEfficiency','status':status,'json':json.dumps(result) }
		except ImportError:
			sys.stderr.write("EXCEPTION: setMashEfficiency() -> %s/%s\n" %(recipeName,efficiency))
			sys.stderr.write("setMashEfficiency() Exception\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s\n" %(e))
			pass
		
		return {'operation':'setMashEfficiency','status':status}



		






	def createBrewlogWrapper(self,username,recipe,brewlog,process):
		"""
		a wrapper with creating a brewlog, and then calculating/compiling it
		"""
		sys.stderr.write("\nSTART: createBrewlogWrapper()\n")
	
		try:
			result={}



			#
			# check if the brewlog already exists
			#
			existingBrewlog = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)
			if len(existingBrewlog):
				sys.stderr.write("END: createBrewlogWrapper()  .. already exists\n")
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
				sys.stderr.write("END: createBrewlogWrapper()  .. stock issue\n")
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
				sys.stderr.write("END: createBrewlogWrapper()  .. stock age issue\n")
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
			# Calculate and Recompile 
			#
			self.doCalculate(username,recipe)


			# save the calclog to the database
			brewlogCalclog = self.dbWrapper.GqlQuery("SELECT * FROM gCalclogs WHERE owner = :1 AND brewlog = :2 AND recipe = :3",username,brewlog,recipe).fetch(4444)
			for x in brewlogCalclog:
				x.delete()

			brewlogCalclog = gCalclogs(owner=username)
			brewlogCalclog.db=self.dbWrapper
			brewlogCalclog.brewlog=brewlog
			brewlogCalclog.recipe= recipe
			brewlogCalclog.calclog=self.calclog
			brewlogCalclog.put()


			#
			# now compile the recipe/brewlog
			#	
			self.compile(username,recipe,brewlog)

			result={}
			result['result'] = resultX['result']		# list of brewlogs
			result['result2'] = resultX['result2']		# list of recipes
			result['stock_status']=True


			sys.stderr.write("END: createBrewlogWrapper()\n")
			return {'operation' : 'createBrewlogWrapper', 'status' : 1, 'json' : json.dumps( result   ) }
		except ImportError:
			sys.stderr.write("EXCEPTION: createBrewlogWrapper()\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
			return {'operation':'createBrewlogWrapper','status': -6,'exception':traceback.format_tb(exc_traceback) }





	def addStockToBrewlog(self,username,brewlog,checkStock=0,recipeName=None,process=None,reset=0):
		"""
		takeStock()
			Takes stock for the current recipe and associates it with the active brewlog

			updated to do a check and take
		
		return: standard json activity
		"""

		sys.stderr.write("\nSTART: addStockToBrewlog() %s\n" %(brewlog))
		status=0
		try:

			if not reset:
				if not checkStock:
					existingBrewlog = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2",username,brewlog).fetch(1)
					if len(existingBrewlog) < 1:
						sys.stderr.write("END: addStockToBrewlog() %s .. not existing brewlog ..\n" %(brewlog))
						return {'operation' : 'addStockToBrewlog','status':-1}

					recipeName = existingBrewlog[0].recipe
					process = existingBrewlog[0].process



				# workaround for now
				# hopAddAt -1 represents the total of this hops and isn't a real hop
				# we delete it here and re create based on the >0 hopAddAts
				ourRecipeIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt <= :4",username,recipeName,"hops",0.0).fetch(400)
				for ori in ourRecipeIngredients:	ori.delete()
				HOPSUMMARY={}
				ourRecipeIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt > :4",username,recipeName,"hops",0.0).fetch(400)
				for ori in ourRecipeIngredients:
					if not HOPSUMMARY.has_key(ori.ingredient):	HOPSUMMARY[ ori.ingredient ] =0
					HOPSUMMARY[ ori.ingredient ] = HOPSUMMARY[ ori.ingredient ] + ori.qty
				for hs in HOPSUMMARY:
					ing = gIngredients(owner=username)
					ing.db=self.dbWrapper
					ing.recipename=recipeName
					ing.qty = HOPSUMMARY[hs]
					ing.ingredient=hs	
					ing.ingredientType='hops'
					ing.hopAddAt=float(-1)
					ing.processIngredient = False
					ing.put()
			
				ourstock=self.takeStock( username,recipeName,existingBrewlog[0].process )
		

				for storeType in ourstock:
					for a in ourstock[storeType]:
						sys.stderr.write(" %s\n" %(a))
						for (pcnt,qty,stocktag,name,purchaseObj) in  ourstock[storeType][a]:

							newstock=gBrewlogStock(	owner=username,brewlog=brewlog,recipe=recipeName)
							newstock.db=self.dbWrapper
							newstock.qty=qty
							newstock.stock=name
							newstock.cost=purchaseObj.purchaseCost * qty
							newstock.storecategory=purchaseObj.storecategory
							newstock.unit=purchaseObj.unit
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
			ourSteps = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gatherthegrain").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=int(tmpSSNUM[0].subStepNum)

				ourIngs = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND storecategory = :3",username,brewlog,'fermentables').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					x.db=self.dbWrapper
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
			ourSteps = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gatherthebottles").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=int(tmpSSNUM[0].subStepNum)
				ourIngs = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,'bottle').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					x.db=self.dbWrapper
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
			ourSteps = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gathertheminikegs").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=int(tmpSSNUM[0].subStepNum)
				ourIngs = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,'keg').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					x.db=self.dbWrapper
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
			ourSteps = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND auto = :3",username,process,"gatherthepolypins").fetch(400)
			for gatherStep in ourSteps:
			

				tmpSSNUM = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 ORDER BY subStepNum DESC",username,process,gatherStep.activityNum,gatherStep.stepNum).fetch(1)
				if len(tmpSSNUM) == 0:
					ssNum=-1
				else:
					ssNum=int(tmpSSNUM[0].subStepNum)
				ourIngs = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,'polypin').fetch(5000)
				for purchaseObj in ourIngs:
					ssNum=ssNum+1
					x=gBrewlogStep(brewlog=brewlog,owner=username,activityNum=gatherStep.activityNum, stepNum=gatherStep.stepNum,subStepNum=ssNum)
					x.db=self.dbWrapper
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


			if reset:
				sys.stderr.write("END: addStockToBrewlog() %s .. reset..\n" %(brewlog))
				return # early

			if len(ourstock) < 1:
				sys.stderr.write("END: addStockToBrewlog() %s .. no stock..\n" %(brewlog))
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
						print stockItem,ourstock[stockType][stockItem]
						result[stockType][stockItem].append( substock)

			sys.stderr.write("END: addStockToBrewlog() %s .. have stock..\n" %(brewlog))
			return {'operation':'addStockToBrewlog','status' :1,'json' : json.dumps( {"result": result})}
		except ImportError:
			sys.stderr.write("EXCEPTION: addStockToBrewlog() %s .. no stock..\n" %(brewlog))
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write(e)
			return {'operation':'addStockToBrewlog','status':status }

		return {'operation':'addStockToBrewlog','status':status}
		
	


	def listStoreItems(self,username,category):
		"""
		listStoreItems()
			Provides a list of stock in the store

			string: category as per listStoreCategories

		return: standard json with simple list of stock itmes
		"""
		sys.stderr.write("\nSTART: listStoreItems() <- %s\n" %(category))
		
		try:
			items = {}

			if category == "Consumables":	category="consumable"
			if category == "Other":	category="misc"

			ourPurchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storecategory = :2 AND qty > :3", username ,category.lower(),0.003)
			for purchase in ourPurchases.fetch(34840):
				if not items.has_key( purchase.storeitem ):
					items[ purchase.storeitem ] = {}
					items[ purchase.storeitem ]['cost'] = 0
					items[ purchase.storeitem ]['totalqty'] = 0
					items[ purchase.storeitem ]['name'] = purchase.storeitem
					items[ purchase.storeitem ]['category'] = category
					items[ purchase.storeitem ]['unit'] = purchase.unit
				items[ purchase.storeitem ]['cost'] = items[ purchase.storeitem ]['cost'] + ( float(purchase.purchaseCost) * float(purchase.qty ))
				items[ purchase.storeitem ]['totalqty'] = items[ purchase.storeitem ]['totalqty'] + float(purchase.qty)


			stockitems=[]
			sorder=[]
			for i in items:	sorder.append( items[i]['name'] )	
			sorder.sort()
			for s in sorder:
				stockitems.append( items[s] )

			result = {'category' : category, 'items':stockitems}
			sys.stderr.write("END: listStoreItems() > status=1\n")
			return {'operation':'listStoreItems','status' :1,'json' : json.dumps( {"result": result})}
		except ImportError:
			sys.stderr.write("EXCEPTION: listStoreItems() > status=0\n")
			return {'operation':'listStoreItems','status' :0  }



	



	def addNewStock(self,username,brewlog,recipe,container,location,qty):
		sys.stderr.write("\nSTART: addNewSotck() %s %s %s %s %s\n" %(brewlog,recipe,container,location,qty))
		beerstock=gBeerStock()
		beerstock.owner=username
		beerstock.recipe=recipe
		beerstock.brewlog=brewlog
		beerstock.stocktype=container
		beerstock.location=location
		beerstock.qty=qty
		beerstock.put()
		sys.stderr.write("END: addNewSotck() %s %s %s %s %s\n" %(brewlog,recipe,container,location,qty))
		return {'operation':'addNewStock','status':1}
	

	def addNewPurchase(self,username,category,itemtext,qty,cost,day,month,year,suppliertext,numpurchased,hopalpha):
		"""
		"""
		sys.stderr.write("\nSTART: addNewPurchase -> %s/%s/%s....\n" %(category,itemtext,qty))		
		status = 0
		
		try:

			ourPurchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1", username)
			results = ourPurchases.fetch(348400)
			stocktag = len(results)
			ourBrewery = self.dbWrapper.GqlQuery("SELECT * FROM gBrewery WHERE owner = :1", username)
			brewery=ourBrewery.fetch(1)[0]
			brewery.cost=brewery.cost+float(cost)
			brewery.put()
					
			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2 AND name = :3", username, category.lower(), itemtext )
			unit=""
			for ingredient in ourIngredients.fetch(1):
				unit=ingredient.unit
		
			suppliers=[]
			ourSuppliers = self.dbWrapper.GqlQuery("SELECT * FROM gSuppliers WHERE owner = :1", username)
			for supplier in ourSuppliers.fetch(20000):
				suppliers.append(supplier.supplierName)
			suppliers.sort()
			(Y,M,D,h,m,s,wd,yd,tm) = time.localtime()

			#
			# add a tweet-hint
			if cost > 0 and not supplier == "recycledreused":
				tweethint=gField(owner=username)
				tweethint.fieldKey="tweetEnabled-stock"
				if numpurchased > 1:
					tweethint.fieldVal="Purchased %s*%s%s %s #%s #%s" %(numpurchased,qty,unit,itemtext,category,re.compile("[^a-zA-Z0-9]").sub('',suppliertext))
				else:
					tweethint.fieldVal="Purchased %s%s %s #%s #%s" %(qty,unit,itemtext,category,re.compile("[^a-zA-Z0-9]").sub('',suppliertext))
				tweethint.put()


			STOCKTAGS=""
			for c in range(int(numpurchased)):
				purchase = gPurchases( owner=username, storecategory=category.lower(), storeitem=itemtext)
				purchase.db=self.dbWrapper
				purchase.qty=float(qty)
				purchase.purchaseDate=int(time.time())
				purchase.bestBeforeEnd = int(time.mktime( (int(year),int(month),int(day),0,0,0,0,0,0) ))
				purchase.supplier = suppliertext
				purchase.itemcategory=ingredient.category
				purchase.qtyMultiple=ingredient.qtyMultiple
				purchase.wastageFixed=ingredient.wastageFixed
				purchase.itemsubcategory=ingredient.subcategory
				purchase.originalqty=float(qty)
				purchase.purchaseCost = float(cost)/float(qty)
				try:
					purchase.volume=ingredient.volume
				except :
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
			sys.stderr.write("END: addNewPurchase -> %s/%s/%s....\n" %(category,itemtext,qty))		
			return {'operation' : 'addNewPurchases', 'status' : status ,'json':json.dumps( {} ) }

		
		except ImportError:
			sys.stderr.write("EXCEPTION: addNewPurchase -> %s/%s/%s....\n" %(category,itemtext,qty))		
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'addNewPurchases', 'status' : status }







	def doCalculate(self,username,recipeName):
		sys.stderr.write("\nSTART: doCalculate() %s\n" %(recipeName))	
		#
		# This is the main calcualte code here
		#	
		self.calclog = "         : %s\n" %(time.ctime())
		self.old_estimated_ibu = 0

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


		sys.stderr.write("\n\n")
		sys.stderr.write("Deleting gContributions\n")
		
		ourContributions = self.dbWrapper.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2", username,recipeName)
		for x in ourContributions.fetch(2000):
			x.delete()
	
		ourHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4 AND hopAddAt > :5", username,recipeName,'hops',0,-1.00)
		self.hops=ourHops.fetch(555)
	


		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe=ourRecipe.fetch(1)[0]

		self.recipe=recipe
		recipe.calculationOutstanding=False
		recipe.put()


		if len(recipe.process) < 1:
			sys.stderr.write("Cannot calcualte becase we don't know which process to use {%s}\n" %(recipe.process))
			sys.stderr.write("END: doCalculate() %s .. no process ..\n" %(recipeName))	
			return "Cannot calculate because we don't know which process to use"

	
		ourRecipeStats = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND brewlog = :3", username,recipeName,"")
		recipeStats = ourRecipeStats.fetch(1)


		ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3",username,recipe.process,-1)
		process=ourProcess.fetch(1)
		if not len(process):
			## select a random process instead
			ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND activityNum = :2 ORDER BY process DESC",username,-1)
			process=ourProcess.fetch(1)
			recipe.process=process[0].process
		process=process[0]
					
		self.Process=process		# rename this later from Process to process.
						# but for now leave as is so we can more easily merge code
		
	


		ourFermentables = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4", username,recipeName,'fermentables',0)

		self.fermentables=ourFermentables.fetch(2000)




		ourYeasts = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4", username,recipeName,'yeast',0)
		self.yeasts=ourYeasts.fetch(2000)

		self.boilers = self._getEquipment(username,recipe.process,"boiler",True)
		self.mash_tun = self._getEquipment(username,recipe.process,"mashtun")
		self.hlt = self._getEquipment(username,recipe.process,"hlt")
		self.fermentation_bin = self._getEquipment(username,recipe.process,"fermentationbin")




		#pickle:self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(self.process.name)
		#gqlself.calclog = self.calclog + "process  : Calculating with Process %s\n" %(revcipe.process)
		self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(recipe.process)	#pickql	
		self.calclog = self.calclog + "process  :  - TODO:: make sure hopAlpha comes from stock not preset\n"
		self.calclog = self.calclog + "process  : brewerslabEngine rev 0.2 (2015-10-18)\n"
		self.calclog = self.calclog + "process  :  - new strike temp calculationg which uses grain weight/mash volume\n"
		self.calclog = self.calclog + "process  :    which gives a strike temp 10deg lower\n"
		self.calclog = self.calclog + "process  :  - strikeTempSkew (hardcoded in cloudNG.py) - to increase by 2deg\n"
		self.calclog = self.calclog + "process  : brewerslabEngine rev 0.3 (2015-10-18)\n"
		self.calclog = self.calclog + "process  :  - strikeTempSkew (hardcoded in cloudNG.py) - to decrease by 1deg\n"
		self.calclog = self.calclog + "process  : brewerslabEngine rev xxx (2015-01-25)\n"
		self.calclog = self.calclog + "process  :  - Basic water treatment with salifert alkalinity and AMS\n"
		self.calclog = self.calclog + "process  : brewerslabEngine rev 554 (2014-11-2)\n"
		self.calclog = self.calclog + "process  :  - support for First Wort Hopping, hopAddAt = 20.22\n"
		self.calclog = self.calclog + "process  :  - BUGFIX: transient results for gravity contributions no longer stored in gContributions\n"
		self.calclog = self.calclog + "process  :  - BUGFIX boil vol didn't account forcooling loss (working_batch_size_D)\n"		
		self.calclog = self.calclog + "process  :  - BUGFIX: working_batch_size_D has cooling_loss in twice NOV FIX3\n"
		self.calclog = self.calclog + "process  :  - BUGIFX: wokring_mash_size_A2 badly calculated (NOV FIX4)\n"
		self.calclog = self.calclog + "process  :  - BUGFIX mash liquid required ignored mash tun deadspace (NOVFIX 5)\n"
		self.calclog = self.calclog + "process  :  - BGUFIX estimated_gravity_grain used wrong volume, now uses working_mash_size\n"
		self.calclog = self.calclog + "process  : brewerslabEngine rev 218 (2013-11-23)\n"
		self.calclog = self.calclog + "process  :  - start of standalone mode to run without sql database\n"
		self.calclog = self.calclog + "process  :  - BUGFIX batchszie in fv wrong with topup\n"
		self.calclog = self.calclog + "process  :  - BUGFIX original gravity wrong with topup\n"
		self.calclog = self.calclog + "process  :  - batchszie in fv wrong with topup\n"
		self.calclog = self.calclog + "process  :  - batchsize from recipestats\n"
		self.calclog = self.calclog + "process  :    (25%% of mash tun deadspace included)\n"
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
		sys.stderr.write( "batchsize: Batch Size from recipe  %.0f L\n" %(recipe.batch_size_required))
		self.calclog = self.calclog + "batchsize: Batch Size from recipe  %.0f L\n" %(recipe.batch_size_required)
		working_batch_size = recipe.batch_size_required - recipe.postBoilTopup
		if not self.standalonemode:
			if len(recipeStats):
				self.calclog = self.calclog + "batchsize: Batch Size from recipestats %.0f L\n" %(recipeStats[0].batchsize)
				working_batch_size = recipeStats[0].batchsize

		if recipe.postBoilTopup > 0:
			self.calclog = self.calclog + "batchsize: Working Batch Size %.0f L \n" %(working_batch_size)
		self.requested_batch_size=working_batch_size


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
		self.calclog = self.calclog + "batchsize:  Cooling Loss @ 1.03 %%  %.3f -> %.3f\n" %(cooling_loss,working_mash_size+cooling_loss)
		self.calclog = self.calclog + "batchsize: Batch Size (C)  %.3f\n" %(working_batch_size_C)



		# volume in the fermentation bin 
		working_batch_size_A3 = working_batch_size_A 
		working_batch_size_A3 = working_batch_size_A3 + cooling_loss

		
		#
		# Calculating approximate evaporation Loss
		#
		#working_batch_size_D = working_batch_size_C + cooling_loss		
		working_batch_size_D = working_batch_size_C  # BUGFIX NOV3
		if self.Process.fixed_boil_off > 0:
			evaporation_loss = self.Process.fixed_boil_off 
			working_batch_size_D = working_batch_size_D + evaporation_loss
			self.calclog = self.calclog + "batchsize: Boiling Loss (fixed %s) -> %.3f\n" %(self.Process.fixed_boil_off,working_batch_size_C+self.Process.fixed_boil_off)

			water_in_boil = water_in_boil + extra_water

		else:
			evaporation_loss = working_mash_size * ( self.Process.percentage_boil_off / 100 ) 
			working_batch_size_D = working_batch_size_D + evaporation_loss
			self.calclog = self.calclog + "batchsize: Boiling Loss (%s %%) ~ %.3f L water -> %.3f\n" %(self.Process.percentage_boil_off,evaporation_loss,working_batch_size_C+ evaporation_loss)
	
		self.kettle1evaporation=evaporation_loss



#		self.calclog = self.calclog + "batchsize:  Cooling Loss @ 1.03 %%  %.3f -> %.3f\n" %(cooling_loss,working_mash_size)
		self.calclog = self.calclog + "batchsize: Batch Size (D)  %.3f\n" %(working_batch_size_D)
		
		

		##### need to check this in deetail, but think D might be boil volume needed
		self.kettle1volume=working_batch_size_D
		self.kettle2volume=-10
		self.kettle3volume=-10
		


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
	

		#mash_liquid_required = mash_liquid + self.hlt.dead_space
		mash_liquid_required = mash_liquid + self.hlt.dead_space + self.mash_tun.dead_space  #NOVIFX5
		self.calclog = self.calclog + "mashwater:  HLT Dead Space %.3f -> %.3f\n" %(self.hlt.dead_space,mash_liquid_required)
		self.calclog = self.calclog + "mashwater: Mash Water Required  %.3f\n" %(mash_liquid_required)
		self.mash_liquid_required = mash_liquid_required 
	

#		working_batch_size_A2 = working_mash_size - (self.mash_tun.dead_space * 0.75)
		working_batch_size_A2 = working_batch_size_A3  #NOVFIX 4 
		self.calclog = self.calclog + "calcferm : \t Using batch_size + fv_dead space for gravity %.3f\n" %(working_batch_size_A2)
		self.calclog = self.calclog + "calcferm : \t  (Note: previous process used working_mash_size %.3f\n" %(working_mash_size)
	
				
		#NOV2017 working_mash_size	
		
		grav_grain = self.calculateGravity(working_mash_size,grainOnly=1, doContributionsForGrain =1)
		self.estimated_grain_gravity = grav_grain
		self.calclog = self.calclog + "calcferm : \t\tgravity grain = %.4f\n" %( 1+(grav_grain/1000) )

		grav_adjunct = self.calculateGravity(working_mash_size,adjunctOnly=1, doContributionsForAdjunct=1)
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
		ourWater = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND category = :3 AND processIngredient = :4", username,recipeName,'water',0).fetch(5555)
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
			newWater.db=self.dbWrapper
			for ri in foundWater.__dict__:
				if ri != "entity":
					newWater.__dict__[ri] = foundWater.__dict__[ri]
			newWater.qty=float(ourWaterNeeds)
			newWater.put()	



		alkalinityTarget=50
		self.calclog = self.calclog + "waterCRS : Calculating based on Target of %s CAC03  (mash/Sparge)s\n" %(alkalinityTarget) 
		mashCrs=self.crsAdjustment(320, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(320, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 320 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(300, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(300, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 300 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(280, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(280, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 280 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(260, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(260, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 260 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(240, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(240, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 240 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(220, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(220, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 220 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(180, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(180, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 180 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(150, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(150, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 150 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(100, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(100, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 100 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(75, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(75, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 75 = %.3f/%.3f\n" %(mashCrs,spargeCrs)
		mashCrs=self.crsAdjustment(50, mash_liquid_required,alkalinityTarget)
		spargeCrs=self.crsAdjustment(50, sparge_water_required,alkalinityTarget)
		self.calclog = self.calclog + "waterreqd:   Alkalinity 50 = %.3f/%.3f\n" %(mashCrs,spargeCrs)


		#if ourTapWaterNeeds:
		#	newWater= gIngredients(owner=username)
		#	for ri in foundWater.__dict__:
		#		if ri != "entity":
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
	
		grain_pcnt=0
		nongrain_pcnt=0
		if grain+nongrain >0:	
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
			self.calclog = self.calclog + "calcfgrav:  Wort expected gravity after dilution (%.3f L -> %.3f)\n" %(working_batch_size_A2 , working_batch_size_A2+recipe.postBoilTopup)	
			self.calclog = self.calclog + "calcfgrav:     gravity = %.4f ->  %.4f\n" %((1+(estimated_gravity/1000)), (1 + (diluted_gravity /1000)))
#			estimated_gravity = diluted_gravity
		else:
			diluted_gravity = estimated_gravity



		# oriignal place



		#
		# Calculate Hops
		#
		if recipe.postBoilTopup > 0:
			self.calclog=self.calclog+"calchops : Calculating with pre-topup gravity %.4f\n" %(estimated_gravity)
			self.calclog=self.calclog+"calchops :  will dilute later to %.4f\n" %(diluted_gravity)
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


		if recipe.postBoilTopup > 0:
			estimated_gravity = diluted_gravity
			self.calclog = self.calclog + "calcfgrav:     now consider gravity to be %.4f\n" %(estimated_gravity)
			self.estimated_og = 1+(estimated_gravity/1000)

		# this section was above hop models previously,
		# but this gave us a bit of a dilema...
		# hops need to be calculated with the gravity in the boiler (pre topup)
		# but the rest is post topup
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
				# this is within doCalculate()
				cont = gContributions( owner=username, recipeName=recipeName )
				cont.db=self.dbWrapper
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
		self.estimated_srm = estimated_srm


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
		self.kettle1preboilgravity=grav
		self.kettle2preboilgravity=-1
		self.kettle3preboilgravity=-1

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
		self.kettle2evaporation=0
		self.kettle3evaporation=0


		# MIDGRAVS WAS HERE


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



		# MIDGRAV2 WAS HERE


		self.kettle1kettle2volume=-10
		self.kettle1kettle2kettle3volume=-10



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
		self.precoolfvvol=working_batch_size_A3
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

#		self.calclog=self.calclog +"stats    :\t polypinqty = %.1f\n" %(self.polypinqty)
#		self.calclog=self.calclog +"stats    :\t minikegqty = %.1f\n" %(self.minikegqty)

		try:
			self.calclog=self.calclog +"stats    :\t number_boil_passes = %s\n" %(PASS)
		except :
			pass
		self.calclog=self.calclog +"stats    :\t kettle1volume = %.1f\n" %(self.kettle1volume)
		self.calclog=self.calclog +"stats    :\t kettle2volume = %.1f\n" %(self.kettle2volume)
		self.calclog=self.calclog +"stats    :\t kettle3volume = %.1f\n" %(self.kettle3volume)
		self.calclog=self.calclog +"stats    :\t kettle1kettle2volume = %.1f\n" %(self.kettle1kettle2volume)
		self.calclog=self.calclog +"stats    :\t kettle1kettle2kettle3volume = %.1f\n" %(self.kettle1kettle2kettle3volume)
		self.calclog=self.calclog +"stats    :\t kettle1preboilgravity = %.1f\n" %(self.kettle1preboilgravity)
		self.calclog=self.calclog +"stats    :\t kettle2preboilgravity = %.1f\n" %(self.kettle2preboilgravity)
		self.calclog=self.calclog +"stats    :\t kettle3preboilgravity = %.1f\n" %(self.kettle3preboilgravity)

		try:
			self.calclog=self.calclog +"stats    :\t kettle1evaporation = %.1f\n" %(self.kettle1evaporation)
			self.calclog=self.calclog +"stats    :\t kettle2evaporation = %.1f\n" %(self.kettle2evaporation)
			self.calclog=self.calclog +"stats    :\t kettle3evaporation = %.1f\n" %(self.kettle3evaporation)
		except :
			pass
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



		# save the calclog to the database
		standardCalclog = self.dbWrapper.GqlQuery("SELECT * FROM gCalclogs WHERE owner = :1 AND brewlog = :2 AND recipe = :3",username,"",recipeName).fetch(4444)
		for x in standardCalclog:
			x.delete()

		standardCalclog = gCalclogs(owner=username)
		standardCalclog.db=self.dbWrapper
		standardCalclog.brewlog=""
		standardCalclog.recipe= recipeName
		standardCalclog.calclog=self.calclog
		standardCalclog.put()

		sys.stderr.write("END: doCalculate() %s .. no process ..\n" %(recipeName))	






	def calculateHops(self,working_hop_size,estimated_gravity,title="",doContribution=0,percentage=1,onlyHopAddAt=-1,tweakHopAddAt=-1):
		sys.stderr.write("\nSTART: calculateHoops()\n")
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
	

		self.dryhop=0	
		total_hop_ibu = 0
		for hopAddAt in self.hops_by_addition:
			if hopAddAt == 0.0001:
				self.dryhop=self.dryhop+hop.qty

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
					cont.db=self.dbWrapper
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
		sys.stderr.write("END: calculateHoops()\n")
		return (total_hop_ibu,grand_total_hop_weight)









	def calculateGravity(self,batchsize,adjunctOnly=0,grainOnly=0,title="",doContributionsForGrain=0,doContributionsForAdjunct=0):
		sys.stderr.write("\nSTART: calculateGravity()\n")
		#
		# Calcualte Grain Gravity
		#
		estimated_mash_gravity = 0
		total_contribution=0
		total_contribution_grain=0
		grain_weight_kg=0
		# Calculate Expected Gravity:
		# ppg X wt / batch size	
		self.calclog = self.calclog + "calcferm : Calculating expected %s gravity based on %.3f L\n" %(title,batchsize)
		for fermentable in self.fermentables:
			if (fermentable.isGrain):
				grain_weight_kg=grain_weight_kg+fermentable.qty/1000
		self.grain_weight_kg = grain_weight_kg
		for fermentable in self.fermentables:
			if (fermentable.isGrain and grainOnly == 1) or (not fermentable.isGrain and adjunctOnly == 1) or (adjunctOnly == 0 and grainOnly == 0):
				self.calclog = self.calclog + "calcferm :	fermentable: %s%s %s\n" %(fermentable.qty,fermentable.unit,fermentable.ingredient)
				self.calclog = self.calclog + "calcferm :		hwe: %s extract: %s\n" %(fermentable.hwe,fermentable.extract)
				contribution = (fermentable.qty /1000 * fermentable.hwe) / batchsize
				self.calclog = self.calclog + "calcferm : \t\t\tcontribution = %s\n" %(contribution)
				self.calclog = self.calclog + "calcferm : \t\t\t%s = %s * %s / %s\n" %(contribution, fermentable.qty/1000, fermentable.hwe , batchsize)
				self.calclog=self.calclog+"calcferm :\t\t\t fermentable.isGrain = %s\n" %(fermentable.isGrain)
				self.calclog=self.calclog+"calcferm :\t\t\t fermentable.isAdjunct = %s\n" %(fermentable.isAdjunct)
				self.calclog=self.calclog+"calcferm :\t\t\t fermentable.mustMash = %s\n" %(fermentable.mustMash)
				if (fermentable.isGrain or fermentable.mustMash) and not fermentable.isAdjunct:
					self.calclog = self.calclog + "calcferm : \t\t\tIncluding in Mash Gravity\n"
					estimated_mash_gravity = estimated_mash_gravity + contribution
					total_contribution_grain = total_contribution_grain + contribution

				# add this grain into our contributiosn table

				if (fermentable.isGrain and doContributionsForGrain) or (fermentable.isAdjunct and doContributionsForAdjunct):
					cont = gContributions( owner=self.username, recipeName=self.recipeName )
					cont.db=self.dbWrapper
					cont.ingredientType="fermentables"
					cont.ingredient=fermentable.ingredient
					cont.gravity =float( contribution * (self.recipe.mash_efficiency /100.0 ) )
					cont.srm=0.0
					cont.put()

				total_contribution = total_contribution + contribution	
				self.calclog=self.calclog+"calcferm :	total_contribution = %.4f\n" %(total_contribution)	


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
			sys.stderr.write("END: calculateGravity()\n")
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

			sys.stderr.write("END: calculateGravity()\n")
			return estimated_gravity_grain + (total_contribution - total_contribution_grain)


		else:
			self.calclog = self.calclog + "calcferm : \t\testimated_gravity_nongrain = %s\n" %(total_contribution - total_contribution_grain )
			sys.stderr.write("END: calculateGravity()\n")
			return total_contribution-total_contribution_grain




	def getStrikeTemperature(self):	
		sys.stderr.write("\nSTART: getStrikeTemperature()\n")
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
		#self.calclog = self.calclog + "striketmp: http://www.howtobrew.com/section3/chapter16-3.html\n"
		#1 US quart = 0.946352946 litres
		#1.18294118 

	
		strike_temp =0
		if self.recipe.mash_grain_ratio > 0:	
			strike_temp = ( ( .41 / self.recipe.mash_grain_ratio) * ((self.recipe.target_mash_temp + self.recipe.target_mash_temp_tweak)  - self.recipe.initial_grain_temp) ) + self.recipe.target_mash_temp
		self.target_mash_temp=self.recipe.target_mash_temp
		
		self.calclog = self.calclog + "striketmp:\t strike_temp = %.3fC  (before skew %.3fC)\n" %(strike_temp-self.strikeTempSkew,strike_temp) 
		self.calclog = self.calclog + "striketmp:\t\t %.3fC = ( ( .41 / mash_grain_ratio ) * (target_mash_temp - initial_grain_temp) ) + target_mash_temp\n" %(strike_temp-self.strikeTempSkew) 
		self.calclog = self.calclog + "striketmp:\t\t %.3fC = ( ( .41 / %.2f ) * (%.3fC - %.3fC) ) + %.3fC\n" %(strike_temp-self.strikeTempSkew,self.recipe.mash_grain_ratio,(self.recipe.target_mash_temp + self.recipe.target_mash_temp_tweak),self.recipe.initial_grain_temp,self.recipe.target_mash_temp) 
	
		self.calclog = self.calclog + "striketmp: http://www.jimsbeerkit.co.uk/calc.html\n"
	
		strike_temp =0
		if self.recipe.mash_grain_ratio > 0:	
			volume = self.mash_liquid_required + 6
			weight = self.grain_weight_kg
			strike_temp =( self.recipe.target_mash_temp * (volume + (0.41 * weight)) - (0.4 * weight * self.recipe.initial_grain_temp) ) / volume
		self.calclog = self.calclog + "striketmp:\t strike_temp = %.3fC  (before skew %.3fC)\n" %(strike_temp-self.strikeTempSkew,strike_temp) 
		self.calclog = self.calclog + "striketmp:\t strike_temp = ( mashTemp * (vol + (0.41 * weight)) - (0.4 * weight * grain temp )) /volume"
		self.calclog = self.calclog + "striketmp:\t\t %.3fC = ( %s * (%s + (0.41 * %s)) - (0.4 * %s * %s) ) / %s\n" %( strike_temp, self.recipe.target_mash_temp, volume,weight, weight,self.recipe.initial_grain_temp,volume)
		sys.stderr.write("END: getStrikeTemperature()\n")
		return strike_temp - self.strikeTempSkew
		




	def _tinsethUtilisation(self,hop_boil_time=60,estimated_gravity=50):
		""" Executes the tinseth algorithim for hops
			hop_boil_time		- time in minutes
			estimated_gravity	-	degress (e.g. 50, no 1.050)
		"""
		sys.stderr.write("\nSTART: _tinsethUtilisation() hop_boil_time=%s estimated_gravity=%s\n" %(hop_boil_time,estimated_gravity))


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

		sys.stderr.write("END: _tinsethUtilisation\n")
		return hop_utilisation



	def _getEquipment(self,username,process,equipment,multiple=False):
		ourEquipment = self.dbWrapper.GqlQuery("SELECT * FROM gEquipment WHERE owner = :1 AND process = :2 AND equipment = :3 ORDER BY volume DESC", username,process,equipment)
		equipments =ourEquipment.fetch(100)
		if multiple:
			return equipments
		else:
			try:
				return equipments[0]
			except ImportError:
				return None


	def createBlankRecipe(self,username,recipeNewName):
		sys.stderr.write("\nSTART: createBlankRecipe %s\n" %(recipeNewName))

		status=0

		try:
			ourRecipes = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeNewName)
			for recipe in ourRecipes.fetch(2000):
				recipe.delete()

			# delete recipeStats just incase
			ourRecipeStats = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2", username,recipeNewName)
			for recipe in ourRecipes.fetch(2000):
				recipe.delete()

			# Find newest process
			newestProcess="unknown-process"
			ourProcesses= self.dbWrapper.GqlQuery("SELECT * FROM gProcesses WHERE owner = :1 ORDER BY entity DESC",username)
			for p in ourProcesses.fetch(1):
				newestProcess=p.process
			stat = gRecipeStats(owner=username,process=newestProcess,recipe=recipeNewName)
			stat.put()

	
			R=gRecipes(recipename=recipeNewName,owner=username )
			R.mash_grain_ratio=1.5
			R.target_mash_temp=67.5
			R.mash_efficiency=70
			R.priming_sugar_qty=2
			R.alkalinity = 50
			R.initial_grain_temp=15
			R.process=newestProcess
			R.db=self.dbWrapper
#			for ri in recipe.__dict__:
#				if ri != "entity" and ri != "recipename":
#					R.__dict__[ri] = recipe.__dict__[ri]
			R.recipename=recipeNewName
			R.put()	

			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = :3", username,recipeNewName,0)
			for ingredient in ourIngredients.fetch(2000):
				ingredient.delete()
						

			status=1
			sys.stderr.write("END: in createBlankRecipe\n")
		except ImportError:
			sys.stderr.write("EXCEPTION: in createBlankRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'createBlankRecipe', 'status' : status ,'json':{}}




	def cloneRecipe(self,username,recipeOrigName,recipeNewName):
		sys.stderr.write("\nSTART: cloneRecipe %s/%s\n" %(recipeOrigName,recipeNewName))

		status=0

		try:
			ourRecipes = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeNewName)
			for recipe in ourRecipes.fetch(2000):
				recipe.delete()

			ourRecipes = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeOrigName)
			for recipe in ourRecipes.fetch(2000):
				R=gRecipes(recipename=recipeNewName,owner=username )
				R.db=self.dbWrapper
				for ri in recipe.__dict__:
					if ri != "entity" and ri != "recipename":
						R.__dict__[ri] = recipe.__dict__[ri]
				R.recipename=recipeNewName
				R.put()	

			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = :3", username,recipeNewName,0)
			for ingredient in ourIngredients.fetch(2000):
				ingredient.delete()
						



			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = :3", username,recipeOrigName,0)
			for ingredient in ourIngredients.fetch(2000):
				I=gIngredients(recipename=recipeNewName,owner=username )
				I.db=self.dbWrapper
				for ii in ingredient.__dict__:
					if ii != "entity" and ii != "recipename":
						I.__dict__[ii] = ingredient.__dict__[ii]
				I.recipename=recipeNewName
				I.put()	


			# fix for broken recipes
			errstatus = self.doCalculate(username,recipeNewName)	#calculate new rceipe
			errstatus = self.compile(username,recipeNewName,None)  #compile new recipe

			status=1
			sys.stderr.write("END: in cloneRecipe\n")
		except ImportError:
			sys.stderr.write("EXCEPTION: in cloneRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'cloneRecipe', 'status' : status ,'json':{}}


	def calculateRecipeWrapper(self,username,recipeName,activeCategory=""):
		#
		#
		# compile + viewRecipe			(compile also calcualtes)
		#
		#
		sys.stderr.write("\nSTART: calculateRecipeWrapper() %s/%sn" %(recipeName,activeCategory))
		self.compile(username,recipeName,None)
		tmp = self.viewRecipe(username,recipeName,activeCategory,1)
		sys.stderr.write("END: calculateRecipeWrapper()\n")
		return {'operation' : 'calculateRecipeWrapper','status':1,'json' : tmp['json'] }
	

	def calculateRecipe(self,username,recipeName):
		sys.stderr.write("\nSTART: calculateRecipe() -> %s/.\n" %(recipeName))
		status=0
		try:
			result={}
			errstatus = self.doCalculate(username,recipeName)
			result['calclog']=self.calclog	
			status=1
			sys.stderr.write("END: calculateRecipe()\n")
			return {'operation' : 'calculateRecipe', 'status' : status ,'json':json.dumps( result ) }


		except ImportError: 
			sys.stderr.write("EXCEPTION: in calculateRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'calculateRecipe', 'status' : status }



	def deleteRecipe(self,username,recipeName):
		sys.stderr.write("\nSTART: deleteRecipe() -> %s....\n" %(recipeName))
		status=0
		try:
			result={}


			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = :3",username,recipeName,0)
			ingredient = ourIngredients.fetch(10000)
			for i in ingredient:	i.delete()

			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2",username,recipeName)
			recipe = ourRecipe.fetch(10000)
			for r in recipe:	r.delete()

			status = 1

		

		except ImportError:
			sys.stderr.write("EXCEPTION: deleteRecipe()\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		sys.stderr.write("END: deleteRecipe()\n")
		return {'operation' : 'deleteRecipe', 'status' : status }






	def changeItemInRecipe(self,username,recipeName,category,item,newqty,hopAddAt="0",doRecalculate="1"):
		sys.stderr.write("\nSTART: changeItemFromRecipe-> recipeName %s/ category %s/%s/%s/%s....\n" %(recipeName,category,item,newqty,hopAddAt))
		status=0
		try:
			result={}
	
			if category == "Hops" or category=="hops":		# this is set as hops in android client not Hops
				if float(hopAddAt) == 0.009:
					sys.stderr.write("hopAddAt Float wrokaround for flameout");
					ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND hopAddAt > :4 AND hopAddAt < :5 AND ingredientType = :6 AND processIngredient = :7",username,recipeName,item,float(0.005),float(0.01),category.lower(),0)
				elif float(hopAddAt) == 0.001:
					sys.stderr.write("hopAddAt float for flameout\n")
					ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND hopAddAt > :4 AND hopAddAt < :5 AND ingredientType = :6 AND processIngredient = :7",username,recipeName,item,float(0.00),float(0.003),category.lower(),0)
				elif float(hopAddAt) == 20.22:
					sys.stderr.write("hopAddAt float for fwh\n")
					ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND hopAddAt > :4 AND hopAddAt < :5 AND ingredientType = :6 AND processIngredient = :7",username,recipeName,item,float(20),float(21),category.lower(),0)
				else:
					ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND hopAddAt = :4 AND ingredientType = :5 AND processIngredient = :6",username,recipeName,item,float(hopAddAt),category.lower(),0)
			else:
				ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND ingredientType = :4 AND processIngredient = :5",username,recipeName,item,category.lower(),0)
			ingredient = ourIngredients.fetch(100)
			for i in ingredient:	#i.delete()
				i.qty=float(newqty)
				if doRecalculate == "0":	i.calculationOutstanding=True
				i.put()

			status = 1

			# flag recipe rcalc at the recipe level
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.calculationOutstanding=True
				recipe.put()
			
			if doRecalculate == "1":
				errstatus = self.doCalculate(username,recipeName)
				errstatus = self.compile(username,recipeName,None)
				result['calclog']=self.calclog

			tmp = self.viewRecipe(username,recipeName,category,1)

			return {'operation' : 'changeItemInRecipe', 'status' : status ,'json': tmp['json'] }



		except ImportError:
			sys.stderr.write("EXCEPTION: changeItemInRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		sys.stderr.write("END: changeItemInRecipe\n")
		return {'operation' : 'changeItemInRecipe', 'status' : status }



	def fixRecipe(self,username,recipeName,category="<NULL>"):
		sys.stderr.write("\nSTART: fixRecipe() -> %s/%s....\n" %(recipeName,category))
		status=0
		try:
			result={}
			
			# delete ingredients which have been deleted
			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND qty < :3",username,recipeName, 0.005)
			for ingredient in ourIngredients.fetch(1000):
				ingredient.delete()


			# work through ingredients and set originalqty to qty
			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND qty > :3",username,recipeName, 0.000)
			for ingredient in ourIngredients.fetch(1000):
				ingredient.originalqty=ingredient.qty
				ingredient.put()


			# copy recipestats
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2",username,recipeName).fetch(1)[0]
			
			ourStats = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3 AND brewlog = :4",username,recipeName,ourRecipe.process,'').fetch(1)[0]
			ourRecipe.estimated_abv = ourStats.estimated_abv
			ourRecipe.estimated_ibu = ourStats.estimated_ibu
			ourRecipe.estimated_fg = ourStats.estimated_fg
			ourRecipe.estimated_og = ourStats.estimated_og
			ourRecipe.batch_size_required=ourStats.batchsize
			ourRecipe.put()

			errstatus = self.doCalculate(username,recipeName)
			self.compile(username,recipeName,None)



			status=1
			tmp = self.viewRecipe(username,recipeName,category,1)
			sys.stderr.write("END: fixRecipe \n")
			return {'operation' : 'fixRecipe', 'status' : status ,'json':tmp['json'] }


		except ImportError:
			sys.stderr.write("EXCEPTION: fixRecipe \n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'fixRecipe', 'status' : status }



	def deleteItemFromRecipe(self,username,recipeName,category,item,hopAddAt=0):
		sys.stderr.write("\nSTART: deleteItemFromRecipe-> %s/%s/%s/%s....\n" %(recipeName,category,item,hopAddAt))
		status=0
		try:
			result={}
			
			if category=="Hops":
				ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND hopAddAt = :4 AND ingredientType = :5 AND processIngredient = :6",username,recipeName,item,float(hopAddAt),category.lower(),0)
			else:
				ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredient = :3 AND ingredientType = :4 AND processIngredient = :5",username,recipeName,item,category.lower(),0)
			ingredient = ourIngredients.fetch(100)
			for i in ingredient:	i.delete()

			status = 1
			# flag recipe rcalc at the recipe level
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.calculationOutstanding=True
				recipe.put()

			errstatus = self.doCalculate(username,recipeName)
		
			result['calclog']=self.calclog
			tmp = self.viewRecipe(username,recipeName,category,1)
			self.compile(username,recipeName,None)
			sys.stderr.write("END: deleteItemFromRecipe()\n")
			return {'operation' : 'deleteItemFromRecipe', 'status' : status ,'json':tmp['json'] }


		except ImportError:
			sys.stderr.write("EXCEPTION: deleteItemFromRecipe()\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'deleteItemFromRecipe', 'status' : status }



	def addItemToRecipe(self,username,recipeName,category,item,qty,hopAddAt=0,doRecalculate="1"):
		sys.stderr.write("\nSTART: addItemToRecipe-> %s/%s/%s/%s/%s....\n" %(recipeName,category,item,qty,hopAddAt))
		status = 0		
		
		try:
			result={}



			ourPresets = self.dbWrapper.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2 AND name = :3", username,category.lower(), item)
			preset = ourPresets.fetch(1)
			if not len(preset) == 1:	
				sys.stderr.write("Cannot find the preset\n")
				return {'operation' : 'addItemToRecipe', 'status' : status  }



			if category == "Hops" or category == "hops":
				ourExistingIngredient = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND ingredient = :4 AND hopAddAt = :5 AND processIngredient = :6",username,recipeName,category.lower(),item,hopAddAt,0)
			else:
				ourExistingIngredient = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND ingredient = :4 AND processIngredient = :5",username,recipeName,category.lower(),item,0)
			existingIngredients = ourExistingIngredient.fetch(1)


			if len(existingIngredients) > 0:
				I = existingIngredients[0]
				I.qty = I.qty + float(qty)
				sys.stderr.write("merging")
			else:	
				I=gIngredients(recipename=recipeName,owner=username )
				I.db=self.dbWrapper
				I.ingredientType=category.lower()
				I.unit=preset[0].unit
				I.ingredient=item
				I.processIngredient=False
				if category == "Yeast" or category == "yeast":			
					I.atten=preset[0].attenuation
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


			# flag recipe rcalc at the recipe level
			ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
			for recipe in ourRecipe.fetch(500):
				recipe.calculationOutstanding=True
				recipe.put()

			if doRecalculate == "1":
				self.calculateRecipe(username,recipeName)
				self.compile(username,recipeName,None)

				result['calclog']=self.calclog


			tmp = self.viewRecipe(username,recipeName,category,1)
			sys.stderr.write("END: addItemToRecipe\n")
			return {'operation' : 'addItemToRecipe', 'status' : status ,'json': tmp }

		
		except ImportError:
			sys.stderr.write("EXCEPTION: addItemToRecipe\n")
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
		sys.stderr.write("\nSTART: compile() %s/%s\n" %(recipeName,brewlog))
		errstatus = self.doCalculate(username,recipeName)
	
		if not brewlog:
			brewlog=""
	
		ourStats = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND process = :2 AND recipe = :3 AND brewlog = :4",username,self.Process.process,recipeName,brewlog).fetch(4324)
		for stat in ourStats:	stat.delete()

		# remove stats 
		stat = gRecipeStats(owner=username,process=self.Process.process,recipe=recipeName)
		stat.db=self.dbWrapper

		if brewlog:
			stat.brewlog=brewlog


		
		ssnum=9999
		if brewlog:	
			# can only do this if we have a brewlog.
			ourCompiledSteps =self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND compileStep = :3",username,brewlog,True).fetch(324234)
			for ocs in ourCompiledSteps:	ocs.delete()


		ourActivities = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum = :3", username,self.Process.process,-1).fetch(324234)
		for activity in ourActivities:
			ourSteps = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND subStepNum = :4",username,self.Process.process,activity.activityNum,-1).fetch(324234)
			for step in ourSteps:

				hop_labels = {60:'Copper (60min)',15:'Aroma (15min)',5:'Finishing (5min)',0.001:'Flameout (0min)',0.0001:'Dryhop' ,'20.222':'First Wort Hop'}

				if step.auto:
					if step.auto == "gatherthegrain":
						sys.stderr.write("We don't need to do stock allocation here  addStockToBrewlog does this\n")
						sys.stderr.write(" but we do need to add in substeps\n")

						ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND isAdjunct = :3 AND ingredientType = :4", username,recipeName,0,'fermentables').fetch(4344)
		
						ssnumFIX=1
						for recipe in ourRecipe:

							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Measure %.1f%s of %s" %(recipe.qty,recipe.unit,recipe.ingredient)
							estep.needToComplete=True
							estep.put()
							ssnumFIX=ssnumFIX+1



					if step.auto == "sterilise":
						ourEquipment = self.dbWrapper.GqlQuery("SELECT * FROM gEquipment WHERE owner = :1 AND process = :2",username,self.Process.process).fetch(32434)
						if len(ourEquipment):
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Sterilise %s pieces of equipment" %(len(ourEquipment))
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1

							for item in activity.equipment:
								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName=" - %s" %(item.name)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1




					elif step.auto == "addadjuncts":
			
						hopaddsorted= []		
						ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND isAdjunct = :3", username,recipeName,1).fetch(4344)
		
						for recipe in ourRecipe:

							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Add %.1f%s of %s adjuncts" %(recipe.qty,recipe.unit,recipe.ingredient)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1


						ourCopperFining = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1




					elif step.auto == "hopmeasure_v3":
			
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if orh.hopAddAt >= 0.0005:			# don't include dry hop
								if not HOPS.has_key( orh.hopAddAt ):
									HOPS[orh.hopAddAt]=[]
									HOPS[orh.hopAddAt].append( orh )
									hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()



						ssnumFIX=0
						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								
								percentage = 1
								hopqty = hop.qty * percentage


		
								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)		
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Measure %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnumFIX=ssnumFIX+1




					elif step.auto == "hopaddAroma_v3":
						ssnumFIX=3		
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)
	
						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
								if orh.hopAddAt <= 30 and orh.hopAddAt >1:
									# make sure we don't show FWH for aroma hops addition
									if orh.hopAddAt < 20.1 or orh.hopAddAt > 20.3:
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

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)		
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnumFIX=ssnumFIX+1



						ourCopperFining = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1





						ourAromaFlavourings = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"flavouring").fetch(32434)
						for aroms in ourAromaFlavourings:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the kettle to add aroma." %(aroma.qty,aroma.unit,aroma.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1







					elif step.auto == "hopaddBittering_v3_withadjuncts":
						ssnumFIX=2
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

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

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)			
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnumFIX=ssnumFIX+1


						hopaddsorted= []		
						ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND isAdjunct = :3", username,recipeName,1).fetch(4344)
		
						for recipe in ourRecipe:

							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Add %.1f%s of %s adjuncts" %(recipe.qty,recipe.unit,recipe.ingredient)
							estep.needToComplete=True
							estep.put()
							ssnumFIX=ssnumFIX+1



					elif step.auto == "dryhop":
						ssnumFIX=0	
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3", username,recipeName,"hops").fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
#								sys.stderr.write("dryhop   :   %s/%s/%s \n" %(orh.ingredient,orh.qty,orh.hopAddAt))
								if orh.hopAddAt < 0.001 and orh.hopAddAt > -1:
#									sys.stderr.write("dryhop:   this is dry hop %s\n" %(orh.qty))
									HOPS[orh.hopAddAt]=[]
									HOPS[orh.hopAddAt].append( orh )
									hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()

						haveDryHops=False
						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								
								percentage = 1
								hopqty = hop.qty * percentage

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)		
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnumFIX=ssnumFIX+1
								haveDryHops=True
						
						# hide a step if we don't have dry-hop involved
						if not haveDryHops:
							disableStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4", username,brewlog,step.activityNum,step.stepNum).fetch(1)
							if len(disableStep):
								disableStep[0].activityNum=-9
								disableStep[0].put()
						



					elif step.auto == "hopaddFirstWort_v3":
						ssnumFIX=0	
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt < :4 AND hopAddAt > :5", username,recipeName,"hops",21,20).fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
								if orh.hopAddAt < 1:
									HOPS[orh.hopAddAt]=[]
									HOPS[orh.hopAddAt].append( orh )
									hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()
						
						haveFWH=False
						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								haveFWH=True					
								percentage = 1
								hopqty = hop.qty * percentage

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)		
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnumFIX=ssnumFIX+1

						if not haveFWH:
							disableStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4", username,brewlog,step.activityNum,step.stepNum).fetch(1)
							if len(disableStep):
								disableStep[0].activityNum=-9
								disableStep[0].put()



					elif step.auto == "hopaddFinishing_v3":
						ssnumFIX=0	
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt < :4 AND hopAddAt > :5", username,recipeName,"hops",1,0.0002).fetch(4344)

						HOPS={}
						for orh in ourRecipeHops:
							if not HOPS.has_key( orh.hopAddAt ):
								if orh.hopAddAt < 1:
									HOPS[orh.hopAddAt]=[]
									HOPS[orh.hopAddAt].append( orh )
									hopaddsorted.append( orh.hopAddAt )
						hopaddsorted.sort()
						hopaddsorted.reverse()

						haveFlameout=False
						for hopAddAt in hopaddsorted:
							if hop_labels.has_key(hopAddAt):
								additions=hop_labels[ hopAddAt ]
							else:
								additions='%s min' %(hopAddAt)

							for hop in HOPS[ hopAddAt ]:
								haveFlameout=True
								percentage = 1
								hopqty = hop.qty * percentage

								estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnumFIX)		
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnumFIX=ssnumFIX+1

						if not haveFlameout:
							disableStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4", username,brewlog,step.activityNum,step.stepNum).fetch(1)
							if len(disableStep):
								disableStep[0].activityNum=-9
								disableStep[0].put()






					elif step.auto == "hopaddBittering_v3":
			
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

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
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1



						ourCopperFining = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1








					elif step.auto == "hopaddBitteringAroma_v3":
			
						hopaddsorted= []		
						ourRecipeHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4", username,recipeName,"hops",0.000).fetch(4344)

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
								estep.db=self.dbWrapper
								estep.compileStep=True
								estep.stepName="Add %.1f%s of %s for %s additions" %(hopqty,hop.unit,hop.ingredient,additions)
								estep.needToComplete=True
								estep.put()
								ssnum=ssnum+1



						ourCopperFining = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"copper_fining").fetch(32434)
						for copperfining in ourCopperFining:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)		
							estep.db=self.dbWrapper
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the coppers to aid the coagulation of proteins." %(copperfining.qty,copperfining.unit,copperfining.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1





						ourAromaFlavourings = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2 AND subcategory = :3",username,brewlog,"flavouring").fetch(32434)
						for aroms in ourAromaFlavourings:
							estep = gBrewlogStep(brewlog=brewlog,owner=username,activityNum=activity.activityNum,stepNum=step.stepNum,subStepNum=ssnum)	
							estep.db=self.dbWrapper	
							estep.compileStep=True
							estep.stepName="Add %s%s %s to the kettle to add aroma." %(aroma.qty,aroma.unit,aroma.stock)
							estep.needToComplete=True
							estep.put()
							ssnum=ssnum+1



					elif step.auto == "gatherthepolypins":
						sys.stderr.write("\tdbg:compile() step/auto/gatherthepolypins %s\n" %(self.TAKESTOCK_polypins))
						polypins=True
						try:
							if self.TAKESTOCK_polypins == 0:
								polypins=False
						except:
							pass
						if not polypins:
							disableStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4", username,brewlog,step.activityNum,step.stepNum).fetch(1)
							if len(disableStep):
								disableStep[0].activityNum=-9
								disableStep[0].put()


					elif step.auto == "gathertheminikegs":
						sys.stderr.write("\tdbg:compile() step/auto/gathertheminikegs %s\n" %(self.TAKESTOCK_kegs))
						kegs=True
						try:
							if self.TAKESTOCK_kegs == 0:
								kegs=False
						except :
							pass
						if not kegs:
							disableStep = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4", username,brewlog,step.activityNum,step.stepNum).fetch(1)
							if len(disableStep):
								disableStep[0].activityNum=-9
								disableStep[0].put()
					

					else:
						sys.stderr.write("Unable to complete the logic for step.auto %s\n" %(step.auto))
			

	
		sys.stderr.write("\n\n\n Test of recipestats \n %s/%s\n\n\n" %(stat.mash_liquid,stat.recipe))	


		#
		# we moved this up to the begining of compile
		#
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
		stat.kettle1vol=float(self.boil_vol)
		stat.topupvol =float(self.topupvol)
		stat.total_water=float(self.water_required)
		stat.grain_weight=float(self.grain_weight)
		stat.nongrain_weight=float(self.nongrain_weight)
		stat.hops_weight=float(self.total_hop_weight)
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
		stat.batchsize=float(self.requested_batch_size)
		stat.process=self.Process.process
#		stat.primingwater=float(self.priming_sugar_water)	
#		stat.primingsugarqty = float(self.primingsugarqty)
#		stat.primingsugartotal=float(self.primingsugartotal)





		sys.stderr.write("\tdbg:compile() vessels %s %s %s\n" %(self.TAKESTOCK_bottles,self.TAKESTOCK_kegs, self.TAKESTOCK_polypins))
		# more work added after NOV2012v2
		stat.dryhop=self.dryhop		# set by calculate
		try:
			stat.minikegqty=float(self.TAKESTOCK_kegs )
		except ImportError:
			pass
		try:
			stat.bottles_required=float( self.TAKESTOCK_bottles )
		except ImportError:
			pass
		try:
			stat.polypinqty = float(self.TAKESTOCK_polypins)
		except ImportError:
			pass
#		stat.polypinqty=float(self.total_polypins)
		try:
			stat.num_crown_caps=float(self.TAKESTOCK_bottles+5)
		except ImportError:
			pass	
		try:	
			stat.primingsugarqty = float( self.TAKESTOCK_priming_sugar_qty )
		except ImportError: 
			pass
		try:
			stat.primingsugartotal = float( self.TAKESTOCK_priming_sugar_reqd ) 
		except ImportError:
			pass
		
		try:
			stat.primingwater = float( self.TAKESTOCK_priming_water_required )
		except ImportError:
			pass
		stat.put()
	
	
		sys.stderr.write("END: compile() %s/%s\n" %(recipeName,brewlog))
		return {'operation' : 'compile', 'status' : 1 }




	def checkStockAndPrice(self, username,recipeName,process,raw=False):
		sys.stderr.write("\nSTART: checkStockAndPrice %s/%s\n" %(recipeName,process))
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
	
		if not self.__dict__.has_key("calclog"):	self.calclog=""
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





		# Started to condense
		for costType in ['fermentables','hops','yeast','misc']:
			
			cost_result[ costType ] = {}
			cost_result[ costType ]['__total__'] = 0	
			stock_result[ costType ] = {}
			stock_result[ costType ]['__total__'] = 0	
					#dict1 ==> self.fermentables, self.hops, self.yeast, self.misc
							# (i.e. our recipe bits and pieces
			
		

			ourRecipeIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = :3 AND ingredientType = :4",username,recipeName,0,costType)
			for ingredient in ourRecipeIngredients.fetch(2000):
				qty = ingredient.qty
	

				sys.stderr.write("\tdbg:checkStockAndPrice() %s\n" %(ingredient.ingredient))
				ourStockCheck = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2",username,ingredient.ingredient)
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





		cost_result['consumables'] = {}
		cost_result['consumables']['__total__'] = 0	
		stock_result['consumables'] = {}
		stock_result['consumables']['__total__'] = 0




		# repeat bottle stock checking
		# this is a clone of the implementation in takeStock but re-purposed
		# for checkStockAndPrice



		#
		# 
		# working out what goes in what
		#
		#
		ourRecipes = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe = ourRecipes.fetch(1)[0]

		total_bottles = 0
		bottle_vols = []
		polypin_vols= []
		keg_vols=[]
		polypin_volume_required=recipe.batch_size_required*1000
		total_polypins=0
		total_kegs=0


	
		ourPolypins = self.dbWrapper.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category = :2", username,"polypin")
		for polypin in ourPolypins.fetch(5000):
			polypin_vols.append( (polypin.fullvolume, polypin) )
		polypin_vols.sort()
		polypin_vols.reverse()
		totalPolypinVol=0	


		for (vol,polypin) in polypin_vols:
			qtyAvailable = 0
			qtyRequired = 0

			ourPolypinPurchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2", username,polypin.name)
			for purchase in ourPolypinPurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and polypin_volume_required > 0:					
					if (purchase.qty * vol) > polypin_volume_required:
						qtyNeeded =math.ceil( polypin_volume_required / vol )
					else:
						qtyNeeded = purchase.qty
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
			ourPrimingSugar = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2", username,"primingsugar")
			sys.stderr.write("\tdbg:checkStockAndPrice() priming_sugar_reqd %s (POLYPIN)\n" %(priming_sugar_reqd))
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
					sys.stderr.write("\tdbg:checkStockAndPrice() priming_sugar_reqd %s (POLYPIN - not enough)\n" %(priming_sugar_reqd))
					stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
					stock_result['__out_of_stock__'].append( purchase.storeitem )
					stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
					stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
					stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
				except ImportError:
					# we probably don' thave any type of priming sugar
					# so we make this up instead
					stock_result['__pcnt_left__'][ "__PRIMING_SUGAR__" ] = 0
					stock_result['__stockrequirements__'].append( ['__PRIMING_SUGAR__' ,qtyAvailable,qtyRequired] )
					stock_result['__out_of_stock__'].append( "__PRIMING_SUGAR__" )
					stock_result['__qty_available__'][ "__PRIMING_SUGAR__" ] = qtyAvailable
					stock_result['__qty_required__'][ "__PRIMING_SUGAR__" ] = qtyRequired


               
		keg_volume_required=polypin_volume_required-totalPolypinVol



		ourKegs = self.dbWrapper.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category = :2", username,"keg")
		for keg in ourKegs.fetch(5000):
			keg_vols.append( (keg.fullvolume, keg) )
		keg_vols.sort()
		keg_vols.reverse()
		totalKegVol=0	


		for (vol,keg) in keg_vols:
			qtyAvailable = 0
			qtyRequired = 0

			ourKegPurchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2", username,keg.name)
			for purchase in ourKegPurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and keg_volume_required > 0:					
					if (purchase.qty * vol) > keg_volume_required:
						qtyNeeded =math.ceil( keg_volume_required / vol )
					else:
						qtyNeeded = purchase.qty
					if not cost_result['consumables'].has_key(keg.name):	
						cost_result['consumables'][keg.name] =0
					cost_result['consumables'][ keg.name ] = cost_result['consumables'][ keg.name ] + (purchase.purchaseCost * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
					totalKegVol=totalKegVol+purchase.volume

					keg_volume_required = keg_volume_required - (qtyNeeded * vol )
					qtyRequired = qtyRequired + qtyNeeded
		
					total_kegs = total_kegs + qtyNeeded



		ourco2s = self.dbWrapper.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category = :2", username,"co2").fetch(54355)
		co2_required=total_kegs
		sys.stderr.write("\tdbg:checkStockAndPrice(): co2 required %s\n" %(co2_required))
		for co2 in ourco2s:
			qtyAvailable = 0
			qtyRequired = 0

			ourco2Purchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2", username,co2.name)
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
			stock_result['__pcnt_left__'][ co2.name ] = 0
			stock_result['__stockrequirements__'].append( [co2.name,qtyAvailable, total_kegs])
			stock_result['__out_of_stock__'].append( co2.name )
			stock_result['__qty_available__'][ co2.name ] = qtyAvailable
			stock_result['__qty_required__'][ co2.name ] = total_kegs

#		totalKegVol + totalPolypinVol 




		sys.stderr.write("\tdbg:checkStockAndPrice( )(KEG co2_required %s)\n" %(co2_required))

		# And priming sugar for kegs
		if recipe.priming_sugar_qty > 0 and totalKegVol > 0:
			sys.stderr.write("\tdbg:checkStockAndPrice() recipe.priming_sugar_qty %s %s \n" %(recipe.priming_sugar_qty,totalKegVol))
			priming_sugar_reqd =   totalKegVol * recipe.priming_sugar_qty  * 0.002
			qtyRequired=0
			qtyAvailable
			sys.stderr.write("\tdbg:checkStockAndPrice() priming_sugar_reqd %s (KEG)\n" %(priming_sugar_reqd))
			ourPrimingSugar = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2", username,"primingsugar")
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
					sys.stderr.write("takeStock(): priming_sugar_reqd %s (KEG - not enough)\n" %(priming_sugar_reqd))
					stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
					stock_result['__out_of_stock__'].append( purchase.storeitem )
					stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
					stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
					stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
				except ImportError:
					# we probably don' thave any type of priming sugar
					# so we make this up instead
					stock_result['__pcnt_left__'][ "__PRIMING_SUGAR__" ] = 0
					stock_result['__stockrequirements__'].append( ['__PRIMING_SUGAR__' ,qtyAvailable,qtyRequired] )
					stock_result['__out_of_stock__'].append( "__PRIMING_SUGAR__" )
					stock_result['__qty_available__'][ "__PRIMING_SUGAR__" ] = qtyAvailable
					stock_result['__qty_required__'][ "__PRIMING_SUGAR__" ] = qtyRequired





		bottle_volume_required = keg_volume_required - totalKegVol

		totalBottleVol=0
		ourBottles = self.dbWrapper.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND category = :2", username,"bottle")
		for bottle in ourBottles.fetch(5000):
			bottle_vols.append( (bottle.fullvolume, bottle) )
		bottle_vols.sort()
		bottle_vols.reverse()
	
		for (vol,bottle) in bottle_vols:
			qtyAvailable = 0
			qtyRequired = 0

			ourBottlePurchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2", username,bottle.name)
			for purchase in ourBottlePurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and bottle_volume_required > 0:					
					if (purchase.qty * vol) > bottle_volume_required:
						qtyNeeded =math.ceil( bottle_volume_required / vol )
					else:
						qtyNeeded = purchase.qty
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
		if bottle_volume_required > 0:
#			sys.stderr.write("doing out of stock stuff\n")
			stock_result['__pcnt_left__'][ bottle.name ] = 0
			stock_result['__stockrequirements__'].append( [bottle.name,qtyAvailable, math.ceil(bottle_volume_required / vol ) + qtyRequired])
			stock_result['__out_of_stock__'].append( bottle.name )
			stock_result['__qty_available__'][ bottle.name ] = qtyAvailable
					# this next calculation is the excess, but we have qtyRequired adding up
					# as we go along
			stock_result['__qty_required__'][ bottle.name ] = math.ceil(bottle_volume_required / vol ) + qtyRequired
			### out of stock

		sys.stderr.write("\tdbg:checkStockAndPrice() Polypins: %s/%s Kegs: %s/%s Bottles: %s/%s\n" %(total_polypins,totalPolypinVol,total_kegs,totalKegVol,total_bottles,totalBottleVol ))
		purchase=None


		# OCT2015 moved from takeStock 
		self.TAKESTOCK_kegs=total_kegs
		self.TAKESTOCK_polypins=total_polypins
		self.TAKESTOCK_bottles=total_bottles

		# Now do crown caps
		total_caps = total_bottles  + 4
		qtyRequired = 0 
		qtyAvailable = 0
		ourBottleCaps = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2", username,"bottlecaps")


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
			sys.stderr.write("totalcaps - no enough\n")
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
			qtyAvailable=0
			sys.stderr.write("\tdbg:checkStockAndPrice(): priming_sugar_reqd %s (BOTTLES)\n" %(priming_sugar_reqd))
			ourPrimingSugar = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2", username,"primingsugar")
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
				sys.stderr.write("takeStock(): priming_sugar_reqd %s (BOTTLES - not enough)\n" %(priming_sugar_reqd))
				try:
					stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
					stock_result['__out_of_stock__'].append( purchase.storeitem )
					stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
					stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
					stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
				except ImportError:
					# we probably don' thave any type of priming sugar
					# so we make this up instead
					stock_result['__pcnt_left__'][ "__PRIMING_SUGAR__" ] = 0
					stock_result['__stockrequirements__'].append( ['__PRIMING_SUGAR__' ,qtyAvailable,qtyRequired] )
					stock_result['__out_of_stock__'].append( "__PRIMING_SUGAR__" )
					stock_result['__qty_available__'][ "__PRIMING_SUGAR__" ] = qtyAvailable
					stock_result['__qty_required__'][ "__PRIMING_SUGAR__" ] = qtyRequired



		#
		#
		# water treatment		(not sure how to trigger this)
		#
		#
		# we will always do it 
		ourRecipeStats =self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2", username,recipeName).fetch()[0]
		crsAdjust=self.crsAdjustment(315, float(ourRecipeStats.mash_liquid_6)+float(ourRecipeStats.sparge_water),50)
		purchase=None
		ourCrs = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemsubcategory = :2 AND storeitem = :3", username,"watertreatment","AMS")
		total_crs=0	# the amount we have allocated throughout
		qtyRequired=crsAdjust	# total qty we require
		qtyAvailable=0
		qtyNeeded=0	# qty of a particular purchase we need
		for purchase in ourCrs.fetch(5555):
			qtyAvailable = qtyAvailable + purchase.qty
			if purchase.qty > 0 and qtyRequired > 0:
				if purchase.qty > qtyRequired:
					qtyNeeded= qtyRequired
				else:
					qtyNeeded = purchase.qty
				if not cost_result['consumables'].has_key( purchase.storeitem ):
					cost_result['consumables'][ purchase.storeitem ] = 0
				cost_result['consumables'][ purchase.storeitem ] = cost_result['consumables'][ purchase.storeitem ] + (purchase.purchaseCost * qtyNeeded)
				cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)
				qtyRequired = qtyRequired - qtyNeeded
				total_crs = total_crs + qtyNeeded


		if qtyRequired > 0:
			try:
				stock_result['__pcnt_left__'][ purchase.storeitem ] = 0
				stock_result['__stockrequirements__'].append( [purchase.storeitem ,qtyAvailable,qtyRequired] )
				stock_result['__out_of_stock__'].append( purchase.storeitem )
				stock_result['__qty_available__'][ purchase.storeitem ] = qtyAvailable
				stock_result['__qty_required__'][ purchase.storeitem ] = qtyRequired
			except ImportError:	
				stock_result['__pcnt_left__'][ "__AMS__" ] = 0
				stock_result['__stockrequirements__'].append( ['__AMS__' ,qtyAvailable,qtyRequired] )
				stock_result['__out_of_stock__'].append( "__AMS__" )
				stock_result['__qty_available__'][ "__AMS__" ] = qtyAvailable
				stock_result['__qty_required__'][ "__AMS__" ] = qtyRequired




		completeVolume=keg_volume_required=polypin_volume_required-totalPolypinVol + totalBottleVol



		#
		# reaplcement for process costing, this is simplified to not split across partial purchases
		# in practice for things like sterilising fluid etc we won't be splitting
		# 


		#  these calculations need to be replicated in takeStock

		# sterilising fluid
				#30gm for fermenter, + 6gm teaspoon for each 5 bottles
		sterilisingPowder= 30 + (total_bottles / 5)*6  
		yeastVit=5
		salifert=3
		protofloc=1
		campden=2
		# consumableProcessIngredients - checkStock
		for (consumableQtyRequired,item) in [(sterilisingPowder,'Sterilising Powder'),(yeastVit,'Yeast Vit'),(salifert,'Salifert Alkaline Test') ,(protofloc,'Protofloc'),(campden,'Campden Tablets')]:
			qtyRequired=consumableQtyRequired
			ourConsumablePurchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2", username,item)
			for purchase in ourConsumablePurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and consumableQtyRequired > 0:
					if (purchase.qty) > consumableQtyRequired:
						qtyNeeded = consumableQtyRequired
					if not cost_result['consumables'].has_key( purchase.storeitem ):	
						cost_result['consumables'][purchase.storeitem] =0
					cost_result['consumables'][ purchase.storeitem ] = cost_result['consumables'][ purchase.storeitem ] + (purchase.purchaseCost * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)

					qtyRequired = qtyRequired - qtyNeeded
					

			
			if qtyRequired > 0:
				stock_result['__pcnt_left__'][ item ] = 0
				stock_result['__stockrequirements__'].append( [item ,qtyAvailable,qtyRequired] )
				stock_result['__out_of_stock__'].append( item )
				stock_result['__qty_available__'][ item ] = qtyAvailable
				stock_result['__qty_required__'][ item ] = qtyRequired
	
	

		result = {}
		result['cost_result'] = cost_result
		result['stock_result'] = stock_result
		if raw:
			sys.stderr.write("END: checkStockAndPrice()\n")
			return (cost_result,stock_result)	
		sys.stderr.write("END: checkStockAndPrice()\n")
		return {'operation' : 'checkStockAndPrice', 'status' : 1, 'json' : json.dumps( {'result': result } ) }














	def deleteBrewlog(self,owner,brewlog):
		sys.stderr.write("\nSTART: deleteBrewlog() %s\n" %(brewlog))
		ourOldRecords = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2",owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old brewlog indexes
		ourOldRecords = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2", owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old step records			
		ourOldRecords = self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2", owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		# Remove our old notes
		ourOldRecords = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2",owner,brewlog)
		for oldRecord in ourOldRecords.fetch(234898):	oldRecord.delete()

		sys.stderr.write("END: deleteBrewlog()\n")
		return {'operation':'deleteBrewlog','satus':1}



	def changeProcess(self,username,recipeName,newProcess,activeCategory=""):
		sys.stderr.write("\nSTART: changeProcess() %s/%s\n" %(recipeName,newProcess))

		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		for recipe in ourRecipe.fetch(500):
			recipe.process=newProcess
			recipe.put()


		# now include calculate/compile steps
		self.calculateRecipe(username,recipeName)
		#self.compile(username,recipeName,None)
		self.compile(username,recipeName,None)
		tmp = self.viewRecipe(username,recipeName,activeCategory,1)

		sys.stderr.write("END: changeProcess()\n")
		return {'operation' : 'changeProcess', 'status' : 1 ,'json' : tmp['json'] }
	


	
	def listClearanceStock(self,username):
		"""
		Builds a list of stock items which are out of date, and soon out of date
		"""
	
		sys.stderr.write("\nSTART: listClearanceStock()\n")

		bestBeforeThreshold = time.time()
		bestBeforeEarlyThreshold = time.time()-(86400*6)
		toclear={}
		oldstock={}

		earlythreshold=0
		overthreshold=0

		for storetype in ['fermentables','hops','yeast','misc','consumable']:
			toclear[ storetype ] = {}

			ourPurchases  = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storecategory = :2", username,storetype)
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

		sys.stderr.write("END: listClearanceStock()\n")
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
		sys.stderr.write("\nSTART: _stockBestBefore() %s\n" %(stockType))
		# just a bit of protection
		if not stock_result.has_key( stockType ):
			stock_result[ stockType ] = {}

		#  i knew this was going to burn us when we were playing with 
		#  adding ingredients
		if stockType == "hops":
			ourRecipeIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt <= :4",username,recipeName,stockType,0.0)
		else:
			ourRecipeIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3",username,recipeName,stockType)

		# gIngredients will NOT catch both real recipe ingredients and consumables
		# need something more but lets get ingredients done first
		# will need to build this in
		# if ITEM.category != "bottle" and ITEM.category != "bottlecaps":

		for ITEM in ourRecipeIngredients.fetch(40000):
			qty = ITEM.qty
			ourStockCheck = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2",username,ITEM.ingredient)
			ourStock = ourStockCheck.fetch(20000)
			if len(ourStock) > 0 :
#US.has_key( ITEM ):
				qtyNeeded = qty
				# A future improvement might attempt to use whole bags rather than
				# cause leaving opened packets.
				best_before_dates_obj = {}
				best_before_dates = []

				for purchasedItem in ourStock:
					if not best_before_dates_obj.has_key( purchasedItem.bestBeforeEnd ):
						best_before_dates_obj[ purchasedItem.bestBeforeEnd ] = []
						best_before_dates.append( purchasedItem.bestBeforeEnd )
					best_before_dates_obj[ purchasedItem.bestBeforeEnd].append( purchasedItem )
				
				
				# soonest best before end date first
				best_before_dates.sort()
				#uMake the qty required tenfold as we would really like to know 
				# how muct we can adjust up to.
				if dummyAllocate:	qtyNeeded = qtyNeeded * 100

				for best_before_date in best_before_dates:
					for item in best_before_dates_obj[ best_before_date ]:	
						if item.qty > 0 and qtyNeeded >0:
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
										sys.stderr.write("\tdbg:_stockBestBefore() Setting QTY of %s/%s to %s\n" %(item.storeitem,item.stocktag,item.qty-qtyUsed))										
										# Note: we don't put() the item the object is passed back
										# to the caller which will do the put()
								else:
								# Check the wastage in this step.
									if not dummyAllocate:
										item.qty= item.qty - qtyNeeded
										item.qty= item.qty - item.wastageFixed
										if item.qty < 0:
											item.qty = 0
											# Note: we don't put() the item the object is passed back
											# to the caller which will do the put()
											sys.stderr.write("\tdbg:_stockBestBefore() Setting QTY of %s/%s to %s (Wastage)\n" %(item.storeitem,item.stocktag,0))										
									
								qtyNeeded = 0
							else:
								# This is a full use of the item in stock
								# therefore we do't introduce wastage
								qtyNeeded = qtyNeeded - item.qty
								stock_result[ stockType ][ item.storeitem ].append( (1,item.qty, item.stocktag,item.storeitem,item) )
								if not dummyAllocate:
									item.qty = float(0)	
									# Note: we don't put() the item the object is passed back
									# to the caller which will do the put()
									sys.stderr.write("\tdbg:_stockBestBefore() Setting QTY of %s/%s to %s (Used All)\n" %(item.storeitem,item.stocktag,0))										



		sys.stderr.write("END: _stockBestBefore() %s\n" %(stockType))
		return stock_result







	def takeStock(self, username, recipeName,process,ignoreOutOfStock=0,cost_result=None,stock_result=None,doNotAllocate=0):
		sys.stderr.write("\nSTART: takeStock %s/%s\n" %(recipeName,process))
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
		total_polypin_volume=0

		# use checkStockAndPrice, but also allow us to bring this in instead to save cpu cycles ;-)
		if not cost_result and not stock_result:
			(cost_result,stock_result) = self.checkStockAndPrice(username,recipeName,process, True)


		if len(stock_result['__out_of_stock__']) > 0:
			sys.stderr.write("END: takeStock %s/%s ... out of stock ...\n" %(recipeName,process))
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

		# reduce qty of stock 
		# during  the _stockBestBefore we don't actually resduce the qty. 
		for storeType in stock_result:
			for a in stock_result[storeType]:
				for (pcnt,qty,stocktag,name,purchaseObj) in  stock_result[storeType][a]:
#
					purchaseItem = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND stocktag = :2", username,stocktag).fetch(1)[0]
					sys.stderr.write("takeStock : %s %s %s   - stock qty %s\n" %(purchaseItem.storeitem, purchaseItem.qty, float(purchaseItem.qty)-qty, qty))
					purchaseItem.qty = float(purchaseItem.qty )-qty
					purchaseItem.put()




		# For consumables we don't really need to have  best before ordering, but 
		# it won't hurt
		ourActivities = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum = :3 AND subStepNum = :4 ORDER BY activityNum", username,process,-1,-1).fetch(4234)


		# intelligentBottle
		# look out for "Gather Bottles" step and find bottles
		# this is going to have to double up checkStockAndPrice somehow
		enableIntelligentBottle=1
		enableIntelligentKeg=1
		enableIntelligentPolypin=1
		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2",username,recipeName).fetch(1)[0]

		for activity in  ourActivities:
			# stockBestBefore ignores bottles
			stock_result = self._stockBestBefore(username,stock_result, "consumables", recipeName)

			# The checking of the steps is only 
			bottle_volume_required = (ourRecipe.batch_size_required * 1000)
			keg_priming_sugar = 0
			bottle_priming_sugar =0
			total_keg_volume=0

			if enableIntelligentKeg:
				sys.stderr.write("takeStock:	START enableIntelligentKeg\n")
				# for kegs we will prefer the smallest kegs instead of the 
				# largest kegs
				keg_vols = []
				ourKegs = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > :3",username,"keg",0).fetch(345345)
				for purchasedItem in ourKegs:
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
										
								stock_result['consumables'][ keg.storeitem ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stocktag, purchaseItem.storeitem, purchase) )
								sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, float(purchaseItem.qty)-qtyNeeded))
								purchase.qty = float(purchase.qty - qtyNeeded)
							else:
								total_keg_volume = total_keg_volume + vol
								qtyNeeded = purchase.qty
								stock_result['consumables'][ keg.storeitem ].append( (1 , qtyNeeded, purchase.stocktag,   purchase.storeitem, purchase) )
								sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, 0))
								purchase.qty = float(0)
							purchase.put()

							total_kegs=total_kegs+qtyNeeded
#							if bottle.caprequired:	bottle_caps_required = bottle_caps_required + qtyNeeded
							bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )

				self.kegs_required= total_kegs
				self.calclog = self.calclog + "kegfilling: total_kegs %s\n" %(total_kegs)
				TOTAL_KEGS=total_kegs
				self.total_kegs=TOTAL_KEGS


				ourCO2 = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > :3",username,"keg",0).fetch(345345)
			
				for co2 in ourCO2:
					if purchase.qty > 0 and total_kegs > 0:
						if not stock_result['consumables'].has_key( co2.storeitem ):
							stock_result['consumables'][ co2.storeitem ] = []
						if (purchase.qty) > total_kegs:	# need a proportion
							stock_result['consumables'][ co2.storeitem ].append( ( total_kegs/purchase.qty, total_kegs, purchase.stocktag, purchase.storeitem, purchase ) )
							sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, purchase.qty-total_kegs))
							purchase.qty = float(purchase.qty - total_kegs)
							total_kegs = 0 
						else:		# meed all this purchase
							stock_result['consumables'][ co2.storeitem ].append( (1, purchase.qty, purchase.stocktag, purchase.storeitem, purchase) )
							total_kegs = total_kegs - purchase.qty
							sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, 0))
							purchase.qty = float(0)
						purchase.put()

				#  priming sugar
				# note; priming sugar in recipe is against a 500ml bottle size
				# so we need to convert into a value per ml per to be able to use
				# 2.75 for 500ml
				# 2.75 / 500 
				#  use 80% of the sugar for a minikeg
				sys.stderr.write("totalkeg_volume %s\n" %(total_keg_volume))
				sys.stderr.write("keg_sugar-proprotrion %s\n" %(self.keg_sugar_proportion))
				sys.stderr.write("ourRecipe %s\n" %(ourRecipe))
				sys.stderr.write("ourRecipe.priming_sugar_qty %s" %(ourRecipe.priming_sugar_qty))
				priming_sugar_reqd = (total_keg_volume) * (  ( float(ourRecipe.priming_sugar_qty)/500 ) * self.keg_sugar_proportion    )
				self.calclog=self.calclog+"kegfilling: total keg volume filled %.2f in %s kegs\n" %(total_keg_volume,TOTAL_KEGS)
				self.calclog=self.calclog+"kegfilling: priming sugar required for kegs %.3f\n" %(priming_sugar_reqd)
				keg_priming_sugar = math.ceil(priming_sugar_reqd)

				sys.stderr.write("takeStock:	END enableIntelligentKeg\n")

			if enableIntelligentPolypin:
				sys.stderr.write("takeStock:	START enableIntelligentPolypin\n")

				# for polypins we will prefer the smallest polypins instead of the 
				# largest polypins
				polypin_vols = []
				ourKegs = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > :3",username,"polypin",0).fetch(345345)
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
										
								stock_result['consumables'][ polypin.storeitem ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stocktag, purchase.storeitem, purchase) )
								sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, purchase.qty-qtyNeeded))
								purchase.qty = float(purchase.qty - qtyNeeded)
							else:
								total_polypin_volume = total_polypin_volume + vol
								qtyNeeded = purchase.qty
								stock_result['consumables'][ polypin.storeitem ].append( (1 , qtyNeeded, purchase.stocktag, purchase.storeitem, purchase) )
								purchase.qty = float(0)
								sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, 0))
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
				# use 20% for a mini keg
				priming_sugar_reqd = (total_polypin_volume) *  ( (float(ourRecipe.priming_sugar_qty)/500) * self.polypin_sugar_proportion )   # this is a guess
				self.calclog=self.calclog+"polyfill  : total polypin volume filled %.2f in %s polypins\n" %(total_polypin_volume,TOTAL_PINS)
				self.calclog=self.calclog+"polyfill  : priming sugar required for polypins %.3f\n" %(priming_sugar_reqd)
				polypin_priming_sugar = math.ceil(priming_sugar_reqd)
				sys.stderr.write("takeStock:	END enableIntelligentPolypin\n")
				
				



			if enableIntelligentBottle:					
				total_bottle_volume=0
				sys.stderr.write("takeStock:	START enableIntelligentBottle\n")

				# sort bottles in order of size. This is to allow us to have
				# different volume bottles. We can't specify to use a range
				# of different volumes... the algorithim here sorts by largest
				# bottles first. If the store quantities are manipulated 	
				# would get the behaviour
				bottle_vols = []
				ourBottles = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > :3",username,"bottle",0).fetch(345345)
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
						if purchase.qty > 0 and bottle_volume_required > 0:
							if not stock_result['consumables'].has_key(bottle.storeitem):
								stock_result['consumables'][ bottle.storeitem ] = []	

							if (purchase.qty * vol) > bottle_volume_required:

								qtyNeeded =math.ceil( bottle_volume_required / vol )
										
								stock_result['consumables'][ bottle.storeitem ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stocktag, purchase.storeitem, purchase) )
								sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, purchase.qty-qtyNeeded))
								purchase.qty = float(purchase.qty - qtyNeeded)
								total_bottle_volume = total_bottle_volume = qtyNeeded
							else:
								qtyNeeded = purchase.qty
								stock_result['consumables'][ bottle.storeitem ].append( (1 , qtyNeeded, purchase.stocktag, purchase.storeitem, purchase) )
								total_bottle_volume = total_bottle_volume = purchase.qty
								sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, 0))
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



				ourBottlecaps = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > :3",username,"bottlecaps",0).fetch(345345)
				for bottlecap in ourBottlecaps:
					if bottle_caps_required > 0:
						if not stock_result['consumables'].has_key( bottlecap.storeitem ):
							stock_result['consumables'][ bottlecap.storeitem ] = []
						if (purchase.qty) > bottle_caps_required:	# need a proportion
							stock_result['consumables'][ bottlecap.storeitem ].append( ( bottle_caps_required/purchase.qty, bottle_caps_required, purchase.stocktag, purchase.storeitem, purchase ) )
							sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, purchase.qty-bottle_caps_required))
							purchase.qty = float(purchase.qty - bottle_caps_required)
							bottle_caps_required = 0
						else:		# meed all this purchase
							stock_result['consumables'][ bottlecap.storeitem ].append( (1, purchase.qty, purchase.stocktag, purchase.storeitem, purchase) )
							bottle_caps_required = float(bottle_caps_required - purchase.qty)
							sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, 0))
							purchase.qty = 0
						purchase.put()


				# note recipe is fixed assumption of 500ml
				priming_sugar_reqd = (total_bottles + 5) * ourRecipe.priming_sugar_qty 
				self.calclog=self.calclog+"bottlebank: total bottle volume filled %.2f in %s bottles\n" %(total_bottle_volume,TOTAL_BOTTLES)
				self.calclog=self.calclog+"bottlebank: priming sugar required for bottles %.3f\n" %(priming_sugar_reqd)
				bottle_priming_sugar = math.ceil(priming_sugar_reqd)


				sys.stderr.write("takeStock:	END enableIntelligentBottle\n")

			self.priming_sugar_reqd=0

			if enableIntelligentBottle or enableIntelligentKeg or enableIntellignetPolypin:					
				#  priming sugar
				self.priming_sugar_reqd = keg_priming_sugar + bottle_priming_sugar + polypin_priming_sugar
				priming_sugar_reqd = keg_priming_sugar + bottle_priming_sugar + polypin_priming_sugar
				ourPrimingSugar = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemcategory = :2 AND qty > :3",username,"primingsugar",0).fetch(345345)
				for primingsugar in ourPrimingSugar:
					if  priming_sugar_reqd > 0:
						if not stock_result['consumables'].has_key( primingsugar.storeitem):
							stock_result['consumables'][ primingsugar.storeitem ] = []
						if (purchase.qty) > priming_sugar_reqd:
							stock_result['consumables'][ primingsugar.storeitem ].append( (priming_sugar_reqd/purchase.qty, priming_sugar_reqd, purchase.stocktag, purchase.storeitem, purchase ))
							sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, purchase.qty-priming_sugar_reqd))
							purchase.qty = float(purchase.qty - priming_sugar_reqd)
							priming_sugar_reqd = 0
						else:
							stock_result['consumables'][ primingsugar.storeitem ].append( (1,purchase.qty, purchase.stocktag, purchase.storeitem, purchase) )
							priming_sugar_reqd = float(priming_sugar_reqd - purchase.qty)
							sys.stderr.write("takeStock : %s %s %s\n" %(purchaseItem.storeitem, purchaseItem.qty, 0))
							purchase.qty = float(0	)
						purchase.put()

##				self.priming_sugar_reqd=priming_sugar_reqd

		
				# priming sugar for a keg
		sys.stderr.write("takeStock : priming_sugar_reqd %s (this is the sugar required)\n" %(self.priming_sugar_reqd))
		sys.stderr.write("takeStock : priming_sugar_reqd %s \n" %(self.priming_sugar_reqd))
		sys.stderr.write("takeStock : keg_priming_sugar %s\n" %(keg_priming_sugar))
		sys.stderr.write("takeStock : polypin_priming_sugar %s\n" %(polypin_priming_sugar))
		sys.stderr.write("takeStock : bottle_priming_sugar %s\n" %(bottle_priming_sugar))
		"""
vol	recipe 	proprotion of sugar	sugar	num of 500ml units	priming solution	water	
20500	2.75	1	112.75	41	615	502.25	
							
4900	2.75	0.8	21.56	9.8	117.6	96.04	
							
4700	2.75	0.2	5.17	9.4	28.2	23.03	
		sugar=	vol*recipepriming*proprition*0.002				
		num500units=	sugar*(recipepriming/prortion)				
		primingoslution=	15*proption*num500units				
		water=	primingsolutoin-water				



	This is sugar
		priming_sugar_reqd = (total_polypin_volume) *  ( (float(ourRecipe.priming_sugar_qty)/500) * self.polypin_sugar_proportion )   # this is a guess
		"""
	
		keg_num500ml_units = 0
		sys.stderr.write('ourRecipe.priming_sugar_qty %s\n' %(ourRecipe.priming_sugar_qty))
		keg_num500ml_units = math.ceil( keg_priming_sugar / ( ourRecipe.priming_sugar_qty / self.keg_sugar_proportion ) )
		keg_priming_solution_required = keg_num500ml_units * self.keg_sugar_proportion * 15
		keg_priming_water_required = keg_priming_solution_required - keg_priming_sugar
		
		sys.stderr.write("primingsugar: keg_priming_sugar %s\n" %(keg_priming_sugar))	
		sys.stderr.write("primingsugar: keg_num500ml_units %s\n" %(keg_num500ml_units))
		sys.stderr.write("primingsugar: keg_priming_solution_required %s\n" %(keg_priming_solution_required))	
		sys.stderr.write("primingsugar: keg_priming_water_required %s\n" %(keg_priming_water_required))


		polypin_num500ml_units = math.ceil( polypin_priming_sugar / ( ourRecipe.priming_sugar_qty / self.polypin_sugar_proportion ) )
		polypin_priming_solution_required = polypin_num500ml_units * self.polypin_sugar_proportion * 15
		polypin_priming_water_required = polypin_priming_solution_required - polypin_priming_sugar
		
		sys.stderr.write("primingsugar: polypin_priming_sugar %s\n" %(polypin_priming_sugar))	
		sys.stderr.write("primingsugar: polypin_num500ml_units %s\n" %(polypin_num500ml_units))
		sys.stderr.write("primingsugar: polypin_priming_solution_required %s\n" %(polypin_priming_solution_required))	
		sys.stderr.write("primingsugar: polypin_priming_water_required %s\n" %(polypin_priming_water_required))


		bottle_num500ml_units = math.ceil( bottle_priming_sugar / ( ourRecipe.priming_sugar_qty / self.bottle_sugar_proportion ) )
		bottle_priming_solution_required = bottle_num500ml_units * self.bottle_sugar_proportion * 15
		bottle_priming_water_required = bottle_priming_solution_required - bottle_priming_sugar
		
		sys.stderr.write("primingsugar: bottle_priming_sugar %s\n" %(bottle_priming_sugar))	
		sys.stderr.write("primingsugar: bottle_num500ml_units %s\n" %(bottle_num500ml_units))
		sys.stderr.write("primingsugar: bottle_priming_solution_required %s\n" %(bottle_priming_solution_required))	
		sys.stderr.write("primingsugar: bottle_priming_water_required %s\n" %(bottle_priming_water_required))

		self.TAKESTOCK_priming_water_required = keg_priming_water_required + bottle_priming_water_required + polypin_priming_water_required
		self.TAKESTOCK_priming_sugar_reqd = bottle_priming_sugar + keg_priming_sugar + polypin_priming_sugar
		self.TAKESTOCK_priming_sugar_qty = ourRecipe.priming_sugar_qty

		sys.stderr.write("primingsugar: water requirement %s\n" %(self.TAKESTOCK_priming_water_required))





		#
		#
		# water treatment		(not sure how to trigger this)
		#
		#
		# we will always do it 
		ourRecipeStats =self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2", username,recipeName).fetch()[0]
		crsAdjust=self.crsAdjustment(315, float(ourRecipeStats.mash_liquid_6)+float(ourRecipeStats.sparge_water),50)
		
		ourCrs = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND itemsubcategory = :2 AND storeitem = :3", username,"watertreatment","AMS (CRS)")
		total_crs=0	# the amount we have allocated throughout
		qtyRequired=crsAdjust	# total qty we require
		qtyAvailable=0
		qtyNeeded=0	# qty of a particular purchase we need
		for purchase in ourCrs.fetch(5555):
			qtyAvailable = qtyAvailable + purchase.qty
			if purchase.qty > 0 and qtyRequired > 0:
				if not stock_result['consumables'].has_key( purchase.storeitem ):
					stock_result['consumables'][ purchase.storeitem ] = []
				if purchase.qty > qtyRequired:
					qtyNeeded= qtyRequired
					purchase.qty = float(purchase.qty-qtyRequired)
					stock_result['consumables'][ purchase.storeitem ].append( (qtyRequired/purchase.qty, qtyRequired, purchase.stocktag,purchase.storeitem,purchase))
				else:
					sys.stderr.write("takeStock(): trying to get stock %s - taking all of this\n" %(purchase.storeitem))
					qtyNeeded = purchase.qty
					purchase.qty=float(0)
					stock_result['consumables'][ purchase.storeitem ].append( (qtyRequired/purchase.qty, qtyRequired, purchase.stocktag,purchase.storeitem,purchase))

				qtyRequired = qtyRequired - qtyNeeded
				total_crs = total_crs + qtyNeeded
				purchase.put()



		# these calcualtions are replicated frlom checkStock 

		# sterilising fluid
				#30gm for fermenter, + 6gm teaspoon for each 5 bottles
		sterilisingPowder= 30 + (total_bottles / 5)*6  

		# consumableProcessIngredients - takeStock		
		for (consumableQtyRequired,item) in [(sterilisingPowder,'Sterilising Powder')]:
			sys.stderr.write("CHecking COnsumable Process %s %s\n" %(item,consumableQtyRequired))
			qtyRequired=consumableQtyRequired
			ourConsumablePurchases = self.dbWrapper.GqlQuery("SELECT * FROM gPurchases WHERE owner = :1 AND storeitem = :2", username,item)
			for purchase in ourConsumablePurchases.fetch(5000):
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and consumableQtyRequired > 0:
					if (purchase.qty) > consumableQtyRequired:
						qtyNeeded = consumableQtyRequired
						purchase.qty = purchase.qty - consumableQtyRequired			#  do this in takeStock
						consumableQtyRequired=0
					 	purchase.put()								#  do this in takeStock
					else:
						sys.stderr.write("*** simpliied process consumables - we don't have qty availble on this purchase\n" )
					if not cost_result['consumables'].has_key( purchase.storeitem ):	
						cost_result['consumables'][purchase.storeitem] =0
					if not stock_result['consumables'].has_key( purchase.storeitem ):	
						stock_result['consumables'][purchase.storeitem] =[]
					stock_result['consumables'][ purchase.storeitem ].append( (qtyRequired/purchase.qty, qtyRequired, purchase.stocktag,purchase.storeitem,purchase))
					cost_result['consumables'][ purchase.storeitem ] = cost_result['consumables'][ purchase.storeitem ] + (purchase.purchaseCost * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.purchaseCost * qtyNeeded)

					qtyRequired = qtyRequired - qtyNeeded
					
		print self.calclog
		return stock_result






	def viewRecipe(self,username,recipeName,category,dontRecompile=1):
		"""

		view a recipe and optional category of itnegredients to add to the recipe








a copied recipe which has never been compiled causes a problem

a compiled recipe which is recompiled seems to cause problems



		"""


		sys.stderr.write("viewRecipe-> %s/%s....\n" %(recipeName,category))
		status = 0

		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe=ourRecipe.fetch(2000)[0]


		# if we don't have a recipe stats yet we must recalculate
		sys.stderr.write("viewRecipe\n ------ we have a process of %s\n" %(recipe.process))
		ourRecipeStats = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3 AND brewlog = :4",username,recipeName, recipe.process,"")
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
			# this is in viewRecipe()
			ourContributions = self.dbWrapper.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2 AND srm < :3", username,recipeName,1.00)
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
			ourRecipeStats = self.dbWrapper.GqlQuery("SELECT * FROM gRecipeStats WHERE owner = :1 AND recipe = :2 AND process = :3 AND brewlog = :4",username,recipeName, recipe.process,"")

			try:
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
				result['stats']['this_batch_size'] = stats.batchsize
			except ImportError:
				result['stats']['this_estimated_abv'] = 0	
				result['stats']['this_estimated_fg'] = 0 
				result['stats']['this_estimated_og'] = 0
				result['stats']['this_estimated_ibu'] = 0
				result['stats']['spargeWater'] = 0
				result['stats']['mashWater'] = 0 
				result['stats']['boilVolume'] = 0
				result['stats']['totalWater'] = 0 
				result['stats']['totalGrain'] = 0
				result['stats']['totalAdjuncts']= 0
				result['stats']['this_batch_size'] = 0

			tmp={}
			result['category'] = category
			result['fermentableitems'] = []
			ourItems = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4 ORDER BY ingredient",username,recipeName,"fermentables",0)
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
			ourItems = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4 ORDER BY ingredient",username,recipeName,"hops",0)
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
			ourItems = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4 ORDER BY ingredient",username,recipeName,"yeast",0)
			items=ourItems.fetch(20000)
			for item in items:
				result['yeastitems'].append({})
				result['yeastitems'][-1]['name']=item.ingredient
				result['yeastitems'][-1]['qty']= "%.2f" %(item.qty)
				result['yeastitems'][-1]['originalqty']= "%.2f" %(item.originalqty)
				result['yeastitems'][-1]['unit']=item.unit
				tmp[item.ingredient]=""



			result['otheritems'] = []
			ourItems = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4 ORDER BY ingredient",username,recipeName,"misc",0)
			items=ourItems.fetch(20000)
			for item in items:
				result['otheritems'].append({})
				result['otheritems'][-1]['name']=item.ingredient
				result['otheritems'][-1]['qty']="%.2f" %(item.qty)
				result['otheritems'][-1]['originalqty']="%.2f" %(item.originalqty)
				result['otheritems'][-1]['unit']=item.unit
				tmp[item.ingredient]=""


			result['miscitems'] = []
			ourItems = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4 ORDER BY ingredient",username,recipeName,"consumable",0)
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
			ourIngredients = self.dbWrapper.GqlQuery("SELECT * FROM gItems WHERE owner = :1 AND majorcategory = :2 ORDER BY name",username,category.lower())
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

		
		except ImportError:
			sys.stderr.write("EXCEPTION in viewRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		return {'operation' : 'viewRecipe', 'status' : status }



	def publish(self,username,brewlogName,activityNum):
		"""

		view a recipe and optional category of itnegredients to add to the recipe
		"""

		ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogs WHERE owner = :1 AND brewlog = :2", username,brewlogName).fetch(1)[0]
		process = ourProcess.process
		recipeName=ourProcess.recipe
		sys.stderr.write("over-riding process to %s\n" %(ourProcess.process))
	
		activities=[]
		ourActivities = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum = :3 AND subStepNum = :4 AND activityNum = :5 ORDER BY activityNum", username,process,-1,-1,activityNum)


		sys.stderr.write("publish-> %s....\n" %(brewlogName))
		self.response.headers['Content-Type']="text/html"
		self.response.out.write("<h1>Recipe: %s - Brewlog: %s</h1>\n\n" %(recipeName,brewlogName))
			


	
		ourActivities = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND stepNum = :3 AND subStepNum = :4 AND activityNum > :5 ORDER BY activityNum", username,process,-1,-1,-1)
		
		for activity in ourActivities.fetch(4355):
			self.response.out.write("<h2>%s</h2>\n" %(activity.stepName))
			self.response.out.write("<table border=0 cellspacing=0 cellpadding=2>")
			self.response.out.write("<tr><td>&nbsp;</td><td colspan=2></td></tr>")
			ourSteps = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND subStepNum = :3 AND activityNum = :4 AND stepNum > :5 ", username,process,-1,activity.activityNum, -1)
			for step in ourSteps.fetch(4324):	
				ourCompiles = self.dbWrapper.GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,process,activity.activityNum,step.stepNum).fetch(1)
				if len(ourCompiles) < 1:
					ouc = []
				else:
					ouc =ourCompiles[0].toReplace
				self.response.out.write("\n<tr><td>&nbsp;</td><td colspan=2>%s: " %(step.stepNum))
				self.response.out.write("<b>%s</b>" %( self._newVariableSub(username, ouc,activity.activityNum,step.stepNum, step.stepName,recipeName,process,brewlog,"<i>","</i>")))
				if step.auto:
					self.response.out.write(" [%s]" %(step.auto))
	
				self.response.out.write("<br>%s" %( self._newVariableSub(username, ouc,activity.activityNum,step.stepNum, step.text,recipeName,process,brewlog,"<i>","</i>")))
#  step.text)		
				for img in step.img:
					self.response.out.write("<br><img src='http://mycrap.mellon-collie.net/brewerspad/processimgs/%s/%s'>" %( process,img))
				self.response.out.write("</td></tr>")

				ourSubSteps = self.dbWrapper.GqlQuery("SELECT * FROM gBrewlogStep WHERE owner = :1 AND brewlog = :2 AND subStepNum > :3 AND activityNum = :4 AND stepNum = :5", username,brewlogName,-1,activity.activityNum, step.stepNum)
				for substep in ourSubSteps.fetch(4324):	
					ourCompiles = self.dbWrapper.GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",username,process,activity.activityNum,step.stepNum).fetch(1)
					if len(ourCompiles) < 1:
						ouc = []
					else:
						ouc =ourCompiles[0].toReplace
					if substep.needToComplete:
						self.response.out.write("<tr><td width=48>&nbsp;</td><td width=48><img src='http://mycrap.mellon-collie.net/tick.png'></td><td>")
					else:
						self.response.out.write("<tr><td width=48>&nbsp;</td><td width=48>&nbsp;</td><td>")
					self.response.out.write("<br>%s %s" %(substep.subStepNum, self._newVariableSub(username, ouc,activity.activityNum,step.stepNum, substep.stepName,recipeName,process,brewlog,"<i>","</i>")))
	#  step.text))
					self.response.out.write("</td></tr>")



				ourFields = self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4", username,brewlogName,activity.activityNum, step.stepNum)
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



	def cloneProcess(self,username,processOrigName,processNewName):
		sys.stderr.write("\nSTART: cloneProcess %s/%s\n" %(processOrigName,processNewName))

		status=0

		try:
			ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2", username,processNewName)
			for p  in ourProcess.fetch(8000):
				p.delete()

			ourFields= self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND process = :2 AND brewlog = :3", username,processNewName,"")
			for p  in ourFields.fetch(8000):
				p.delete()

			ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2", username,processOrigName)
			for process in ourProcess.fetch(8000):
				P=gProcess(owner=username )
				P.db=self.dbWrapper
				for pi in process.__dict__:
					if pi != "entity" and pi != "process":
						P.__dict__[pi] = process.__dict__[pi]
				P.process=processNewName
				P.put()	

			ourFields = self.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND process = :2 AND brewlog = :3", username,processOrigName,"")
			for field in ourFields.fetch(8000):
				F=gField(owner=username )
				F.db=self.dbWrapper
				for fi in field.__dict__:
					if fi != "entity" and fi != "process":
						F.__dict__[fi] = field.__dict__[fi]
				F.process=processNewName
				F.put()	

			P=gProcesses(owner=username)
			P.process=processNewName
			P.put()
			status=1
			sys.stderr.write("END: in cloneProcess\n")
		except ImportError:
			sys.stderr.write("EXCEPTION: in cloneProcess\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'cloneProcess', 'status' : status ,'json':{}}





