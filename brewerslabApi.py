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
# $Revision: 1.64 $ $Date: 2011-11-04 21:31:17 $ $Author: codemonkey $
#
import traceback
import json
import time
import urllib
from brewerslabEngine import *
from brewerslabData import *
import SimpleXMLRPCServer

import base64
import hashlib
import socket
import re
import os
import time

class brewerslabApi:
	
	def __init__(self):
		self.userid="allena29"
		self.data = brwlabPresetData( self.userid )


		port=54659
		if not os.environ.has_key("HOSTNAME"):
			ip="192.168.1.64"
		else:
			if os.environ['HOSTNAME'] == "challenger.mellon-collie.net":
				ip="192.168.0.170"
			elif os.environ['HOSTNAME'] == "cascade.mellon-collie.net":
				ip="192.168.0.170"

		for d in range(93):
			try:
				print "Trying to bind to %s:%s " %(ip,port+d),
				self.server= SimpleXMLRPCServer.SimpleXMLRPCServer((ip,port+d ))
				print "success"
				break
			except ImportError:
				print "failed"
			port=54659

		self.server.register_instance(self)
		self.server.register_function(lambda astr: '_' + astr,'_string')


		self.recipe=None
		self.brewlog=None	
		self.activity=None
		self.process=None
		self.stores= pickle.loads( open("store/%s/store" %(self.userid)).read() )

		self.server.serve_forever()

	def dbgRestart(self):
		self.recipe=None
		self.brewlog=None
		self.activity=None
		self.process=None
		self.stores= pickle.loads( open("store/%s/store" %(self.userid)).read() )
		return 1


	def listRecipes(self):
		try:
			print "listRecipes() -> "
			recipeList=[]
			for recipe in os.listdir( "recipes/%s/" %(self.userid) ):
				tmp = pickle.loads(open("recipes/%s/%s" %(self.userid,recipe)).read())
				print recipe,tmp,tmp.name
				recipeList.append( tmp.name )
			recipeList.sort()

			
			print "listRecipes() <- " %(recipeList)
			#print {'operation' : 'listRecipes', 'status' : 1, 'json' : "%s" %( {'result': recipeList} ) }
			#print {'operation' : 'listRecipes', 'status' : 1, 'json' : json.encode( {'result': recipeList} ) }
			return {'operation' : 'listRecipes', 'status' : 1, 'json' : json.dumps( {'result': recipeList} ) }

		except:
			return {'operation' : 'listRecipes', 'status' : 0}


	def listActivitiesFromBrewlog(self,process,recipe,brewlog):
		"""
		listActivitiesFromBrewlog
		returns activities without actually opening the brewlog
		
		returns standard header
		"""
		print "listActivitiesFromBrewlog() -> %s,%s,%s" %(process,recipe,brewlog)
		try:
			tmp=pickle.loads(open("brewlog/%s/%s/%s/%s" %(self.userid,process,recipe,brewlog)).read())
			activities=[]
			for activity in tmp.copyprocess.activities:
				activities.append(activity.activityTitle)
		
		
			result={}
			result['activities'] = activities
			result['recipe']=recipe
			result['process']=process
			result['brewlog']=brewlog
	
			return {'operation' : 'listActivitiesFromBrewlog', 'status' : 1, 'json' : json.dumps( {'result': result} ) }
		except:
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e

		return {'operation' : 'listActivitiesFromBrewlog', 'status' : 0}
		
	def listBrewlogsByRecipe(self,recipeName):
		print "listBrewlogsByRecipes() -> %s " %(recipeName)
		try:
			recipeName=re.compile("[^A-Za-z0-9]").sub('_',recipeName).lower()
			
			brewlogList=[]
			for process in os.listdir( "brewlog/%s/" %(self.userid)):
				for recipe in os.listdir("brewlog/%s/%s" %(self.userid,process)):
					if recipe == recipeName:
						for brewlog in os.listdir("brewlog/%s/%s/%s" %(self.userid,process,recipe)):
							if not brewlog.count(".autobackup"):
								bi={}
								bi['recipe'] = recipe
								bi['process'] =process
								bi['name'] =  brewlog
								brewlogList.append(bi)

			brewlogList.sort()
			
			print "listBrewlogsByRecipe() <- " % (brewlogList)
			#print {'operation' : 'listRecipes', 'status' : 1, 'json' : "%s" %( {'result': recipeList} ) }
			#print {'operation' : 'listRecipes', 'status' : 1, 'json' : json.encode( {'result': recipeList} ) }
			return {'operation' : 'listBrewlogByRecipe', 'status' : 1, 'json' : json.dumps( {'result': brewlogList} ) }

		except:
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
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
			print "recipes/%s/%s" %(self.userid, re.compile("[^a-zA-Z0-9]").sub('_',recipe))
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
			
		
	def setBatchSize(self, batchSize):
		"""
		setBatchSize(batchSize)
			batchSize = Final batchSize in Litres after taking account of losses
		
		return: standard api header
		"""
		print "setBatchSize -> %s" %(batchSize)
		status=0
		try:
			self.recipe.batch_size_required = batchSize
			self.recipe.calculate()
			status=1
		except:	pass
		print "setBatchSize <- "
		return {'operation' : 'setBatchSize','status' : status}


	def setTopupVolume(self, topupVol):
		"""
		setTopupVolume(topupVol)
			topulVol = Topup to be provided in Litres after boil

		return: standard api header
		"""
		print "setTopupVolume -> %s" %(topupVol)
		status=0
		try:
			self.recipe.top_up = topupVol
			self.recipe.calculate()
			status=1
		except:
			pass
		print "setTopupVolume <- "
		return {'operation' : 'setTopupVolume','status' : status }


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



	def listProcess(self):
		"""
		listProcesses

		return: list of processes
		"""

		print "listProcess -> "
		try:		
			processes=[]
			for process in os.listdir( "process/%s/" %(self.userid) ):
				processes.append( process )
			processes.sort()

			return {'operation' : 'listProcess','status':1, 'json' : json.dumps( {'result' : processes }) }
		except:	pass	
		return {'operation' : 'listProcess','status':0}


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


	def getSpargeWaterRequired(self):
		"""
		getSpargeWaterRequried()

		return:	integer of total sparge water required for the brew in litres
		"""

		print "getSpargeWaterRequired() -> "
		if self.recipe:
			try:
				waterRequired = self.recipe.calculate()
				waterRequired = self.recipe.sparge_water
				
			except:
				traceback.print_exc()
				return {'operation' : 'getSpargeWaterRequired','status':0}
			waterRequired= self.recipe.waterRequirement()
			waterRequired = self.recipe.sparge_water
			return {'operation' : 'getSpargetWaterRequired', 'status' : 1, 'json' : json.dumps( {"result":waterRequired} ) }

		return {'operation' : 'getSpargeWaterRequired','status':0}


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
				return {'operation' : 'getWaterRequired','status':0}
			waterRequired= self.recipe.waterRequirement()
			return {'operation' : 'getWaterRequired', 'status' : 1, 'json' : json.dumps( {"result":waterRequired} ) }

		return {'operation' : 'getWaterRequried','status':0}


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



	def scaleIBU(self,newIBU):
		"""
		scaleIBU()
			float of required ibu
	
		return:	float with response
		"""

		print "scaleIBU() -> %s " %(newIBU)
		if self.recipe:
			try:
				self.recipe.scaleHops( newIBU )
#				self.recipe.calculate()
				return {'operation' : 'scaleIBU', 'status' : 1, 'json' : json.dumps( {"result": self.recipe.estimated_ibu } ) }
			except:
				print "EXCEPTION"
				#print self.recipe.calclog	
#				exc_type, exc_value, exc_traceback = sys.exc_info()
#				for e in traceback.format_tb(exc_traceback):	print e

		return {'operation' : 'scaleIBU','status':0}



	def startNewBrewLog(self,name):
		"""
		startNewBrewLog()
			string name of the brewlog

		return: standard response header
		"""
		print "startNewBrewLog() <>"
		status = 0
		print self.recipe
		print self.brewlog
		print self.process
		if self.recipe and not self.brewlog and self.process:
			self.brewlog = brwlabBrewlog( self.process, self.recipe )
			self.brewlog.name = name
			self.brewlogfilename= "brewlog/%s/%s/%s/%s" %(self.userid, re.compile("[^A-Za-z0-9]").sub('_',self.process.name), re.compile("[^A-Za-z0-9]").sub("_",self.recipe.name.lower()), re.compile("[^A-Za-z0-9]").sub('_',self.brewlog.name.lower()))
			self.brewlog.filename= "brewlog/%s/%s/%s/%s" %(self.userid, re.compile("[^A-Za-z0-9]").sub('_',self.process.name), re.compile("[^A-Za-z0-9]").sub("_",self.recipe.name.lower()), re.compile("[^A-Za-z0-9]").sub('_',self.brewlog.name.lower()))
			if not os.path.exists(self.brewlogfilename):
				self.brewlog.save()
				status=1
			else:
				print "brewlog already exists!!!"
		return {'operation' : 'startNewBrewLog','status':status}
			




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




	def selectActivity(self,activityName):
		"""
		selectActivity()
			string activity
	
		return: standard response header
		"""
		print "selectActivity <- %s"  %(activityName)
		status=0
		try:
			print "self.process",self.process
			for activity in self.process.activities:
				print activity.activityTitle
				if activity.activityTitle == activityName:	
					self.activity = activity
					status=1
		except:
			print "exception in selectActivity"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)

	
		return {'operation' : 'selectActivity','status':status}



	def listActivitySteps(self):
		"""
		listActivitySteps()

		call openBrewlog() and selectActivity() first
		return: response header with steps required
		"""
		print "listActivitySteps <"
		try:
			steps=[]
			stepNum=0
			for step in self.activity.steps:
				newstep = {}
				newstep['dbg']="DBG"
				newstep['name'] = step.name
				newstep['complete'] = False
				if len(step.substeps) == 0 and step.completed == 1:	
					newstep['complete'] = True 
					newstep['dbg']="a"
				elif len(step.substeps) > 0:
					newstep['dbg']="b"
					sumToComplete=0
					numCompleted=0
					for substep in step.substeps:
						sumToComplete = sumToComplete +1
						if substep.completed:	
							numCompleted = numCompleted + 1
						elif substep.need_to_complete == 0:
							numCompleted = numCompleted + 1
	
				
	
					if sumToComplete == numCompleted:	newstep['complete'] = True


				steps.append(newstep)
			return {'operation':'listActivitySteps','status':1,'json' : json.dumps( {'result': steps } ) }
		except:
			print "exception in listActivitySteps"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)

		return {'operation':'listActivitySteps','status':0}


	def openBrewlog(self,process,recipe,brewlog):
		"""
		openBrewlog()
			string process
			string recipe
			string brewlog

		note: sets process and recipe to those in the brew log
		return: standard response header
		"""
		print "openBrewlog() <> ",process,recipe,brewlog
		status=0
		try:
			self.brewlogfilename= "brewlog/%s/%s/%s/%s" %(self.userid, re.compile("[^A-Za-z0-9]").sub('_',process), re.compile("[^A-Za-z0-9]").sub("_",recipe.lower()), re.compile("[^A-Za-z0-9]").sub('_',brewlog.lower()))
			print self.brewlogfilename
			o=open(self.brewlogfilename)
			self.brewlog = pickle.loads( o.read() )
			o.close()
			self.process = self.brewlog.copyprocess
			self.recipe = self.brewlog.copyrecipe
			status=1
		except:
			print "exception in openbrewlog"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)
			for e in traceback.format_tb(exc_traceback):	print e
		return {'operation' : 'openBrewlog','status' :status}

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


	def setFieldWidget(self,stepNum,fieldKey,fieldVal, guiId):
		"""
		saveFieldWidget
			integer: stepNum
			String: fieldKey
			String: fieldVal
			Integer: guiId 		<passed back transparently>
		"""
		stepNum=int(stepNum)
		print "setFieldWidget <- %s %s %s %s" %(stepNum,fieldKey,fieldVal,guiId)
		if not self.brewlog.notes.has_key( self.activity.steps[stepNum].stepid ):
			self.brewlog.notes[self.activity.steps[stepNum].stepid] = {}


		self.brewlog.notes[self.activity.steps[stepNum].stepid][ fieldKey ] = fieldVal
	

		result={}
		result['value'] = fieldVal
		result['guiid'] = guiId

		if self.activity.steps[stepNum].widgets.has_key( fieldKey ):
			result['value'] = self._widgets( self.activity.steps[stepNum].widgets[fieldKey], self.brewlog.notes[ self.activity.steps[stepNum].stepid ]  )
			print "*"*(80)
			self.brewlog.notes[self.activity.steps[stepNum].stepid][ fieldKey ] = result['value']
			print "This is a widget with a result of ",result['value']
		else:
			print "Note a widget"
	
		self.saveBrewlog()
		#self.brewlog.save()

		return {'operation':'setFieldWidget','status':1,'json': json.dumps( {'result': result } ) }
			



	def _widgets(self,widget,dataDict):
		(widgetType,widgetData) = widget
		if widgetType == "add2numbers":
			data0=widgetData[0]
			data1=widgetData[1]
			print "add2numbers",data0,data1
			print dataDict
			return float( dataDict[data0] ) + float( dataDict[data1] )

		if widgetType == "combineMultipleGravity":
			print "GRAV1"*20
			print widgetData[0]
			grav1=float(dataDict[widgetData[0]])
			print "GRAV2"*20
			print widgetData[1]
			grav2=float(dataDict[widgetData[1]])
			print "VOL1"*20
			vol1=float(dataDict[widgetData[2]])
			print "VOL2"*20
			vol2=float(dataDict[widgetData[3]])
				
			print "grav1",grav1
			print "grav2",grav2
			print "vol1",vol1
			print "vol2",vol2

			totalvol=vol1+vol2
			print "totalvol",totalvol
			print "here"
			g1 = (vol1/totalvol) * grav1
			print g1
			g2 = (vol2/totalvol) * grav2
			print g2
			return "%.4f" %(g1+g2)
			
		if widgetType == "abvCalculation":
			og=float(dataDict[widgetData[0]])
			fg=float(dataDict[widgetData[1]])
		
			return "%.1f" %((og-fg)	 * 131)


		if widgetType == "gravityTempAdjustment":
			intemp=float(dataDict[widgetData[0]])
			gravity=float(dataDict[widgetData[1]])

			temp = ( intemp *1.8)+32
			caltemp = 68

			answer = gravity * (1.00130346 - 1.34722124E-4 * temp + 2.04052596E-6 * temp * temp - 2.32820948E-9 * temp * temp * temp) / (1.00130346 - 1.34722124E-4 * caltemp + 2.04052596E-6 * caltemp * caltemp - 2.32820948E-9 * caltemp * caltemp * caltemp)

			return "%.4f" %(answer)


		if widgetType == "inverseGravityTempAdjustment":
			intemp=float(dataDict[widgetData[0]])
			gravity=float(dataDict[widgetData[1]])

			temp = ( intemp *1.8)+32
			caltemp = -68

			answer = gravity * (1.00130346 - 1.34722124E-4 * temp + 2.04052596E-6 * temp * temp - 2.32820948E-9 * temp * temp * temp) / (1.00130346 - 1.34722124E-4 * caltemp + 2.04052596E-6 * caltemp * caltemp - 2.32820948E-9 * caltemp * caltemp * caltemp)

			return "%.4f" %(answer)


		return "unsupported"
				

	def saveComment(self,stepNum,comment):
		"""
		saveComment
			integer:  stepNum
			String:		comment
		return standard response header
		"""
		sumToComplete=0
		numCompleted=0
		stepNum=int(stepNum)
		print "saveComment <- %s %s" %(stepNum,comment)
		step = self.activity.steps[stepNum]

		print  "stepid", self.activity.steps[stepNum].stepid
		if not self.brewlog.notes.has_key( self.activity.steps[stepNum].stepid ):
			self.brewlog.notes[self.activity.steps[stepNum].stepid] = {}
			
		print "setting notepage with id %s" %(self.activity.steps[stepNum].stepid)
		self.brewlog.notes[self.activity.steps[stepNum].stepid]['notepage'] = comment

		# Note the web interface sometimes uses the stepid from a substep
		for substep in step.substeps:
			if self.brewlog.notes.has_key( substep.stepid ):
				if self.brewlog.notes.has_key[substep.stepid].has_key("notepage"):
					self.brewlog.notes.has_key[substep.stepid]['notepage'] =""
						

		self.saveBrewlog()
		#self.brewlog.save()	
		return {'operation':'saveComment','status':1 }


		return {'operation':'saveComment','status':0}




	def setStepComplete(self,stepNum,completed):
		"""
		setStepComplete
			integer:  stepNum
			Boolean:  complete or not complete	
		return standard response header
		"""
		print "setStepComplete <- ",stepNum,completed
		sumToComplete=0
		numCompleted=0
		stepNum=int(stepNum)
		step = self.activity.steps[stepNum]
		
		if completed == "1":
			lastCompleted=True
			step.completed=1
			step.endTime=time.time()
		else:
			lastCompleted=False
			step.completed=None
			step.endTime=0

		result={}
		result['lastcomplete'] = lastCompleted
		result['stepid'] = "%s" %(stepNum)
		self.saveBrewlog()
		#self.brewlog.save()	

		return {'operation':'setStepComplete','status':1,'json': json.dumps( {'result': result } ) }

		return {'operation':'setStepComplete','status':0}



	def setSubStepComplete(self,stepNum,subStepNum,completed):
		"""
		setSubStepComplete
			integer:  stepNum
			integer:  subStepNum
			Boolean:  complete or not complete	
		return standard response header with percentage for progress bar and lastcompletestatus
		"""
		print "setSubStepComplete <- ",stepNum,subStepNum,completed
		stepNum = int(stepNum)
		subStepNum = int(subStepNum)
		sumToComplete=0
		numCompleted=0

		step = self.activity.steps[stepNum]
		substep = step.substeps[subStepNum]
		
		if completed == "1":
			lastCompleted=True
			substep.completed=1
			substep.endTime=time.time()
		else:
			lastCompleted=False
			substep.completed=None
			substep.endTime=0

		for substep in step.substeps:
			sumToComplete = sumToComplete +1
			if substep.completed:	
				numCompleted = numCompleted + 1
			elif substep.need_to_complete == 0:
				numCompleted = numCompleted + 1

		if sumToComplete == numCompleted:
			subStepCompletes = 100
		if sumToComplete > 0:
			subStepCompletes = (numCompleted/sumToComplete) * 100
		else:
			subStepCompletes = 0	
		
		result={}
		result['progress'] = int(subStepCompletes)
		result['lastcomplete'] = lastCompleted
		result['stepid'] = "%s" %(stepNum)

		self.saveBrewlog()
#		self.brewlog.save()	
		return {'operation':'setSubStepComplete','status':1,'json': json.dumps( {'result': result } ) }

		return {'operation':'setSubStepComplete','status':0}


	def getStepDetail(self,stepNum):
		"""
		getStepDetail()
			integer:  stepNum
			
		return data in response header
		"""
		print "getStepDetail",stepNum
		stepNum = int(stepNum)
		try:
			newStep={}
		
			step = self.activity.steps[stepNum]	
			step.recipe=self.recipe
			newStep['title'] = step.name
			newStep['stepNum'] = stepNum
			newStep['text'] = step.variableSub(step.text)
			newStep['img'] = step.img
			newStep['process']=self.process.name

			if step.completed:
				newStep['complete'] = True
				newStep['completeDate'] = time.ctime( step.endTime )
			else:
				newStep['complete'] = False
			newStep['substepnumber'] = len(step.substeps)
			newStep['substeps']=[]
			for substep in step.substeps:
				newStep['substeps'].append({})
				newStep['substeps'][-1]['needtocomplete'] = substep.need_to_complete
				if substep.completed:
					newStep['substeps'][-1]['complete'] = True
					newStep['substeps'][-1]['completeDate'] = time.ctime( substep.endTime )
				else:
					newStep['substeps'][-1]['complete'] = False
				newStep['substeps'][-1]['text']= step.variableSub(substep.name)

			sumToComplete=0
			numCompleted=0
			for substep in step.substeps:
				sumToComplete = sumToComplete +1
				if substep.completed:	
					numCompleted = numCompleted + 1
				elif substep.need_to_complete == 0:
					numCompleted = numCompleted + 1
			if sumToComplete > 0:
				newStep['substepcomplete'] = (numCompleted/sumToComplete) * 100
			else:
				newStep['substepcomplete']=0	

			if step.attention:
				newStep['warning'] = step.attention
			else:
				newStep['warning'] = ""
	

			comments=""
		
		
			fieldValues={}
			fields=step.fields

			if self.brewlog.notes.has_key(step.stepid):
				for fieldKey in self.brewlog.notes[step.stepid]:
					if fieldKey == "notepage":
						comments=self.brewlog.notes[step.stepid]['notepage']+"\n"
					else:
						# this will get stitched in later
						fieldValues[fieldKey] = self.brewlog.notes[step.stepid][fieldKey]


			# Note the web interface sometimes uses the stepid from a substep
			for substep in step.substeps:
				if self.brewlog.notes.has_key(substep.stepid):
					for fieldKey in self.brewlog.notes[substep.stepid]:
						if fieldKey == "notepage":
							comments=self.brewlog.notes[substep.stepid]['notepage']+"\n"
						else:
							fields[fieldKey] = self.brewlog.notes[substep.stepid][fieldKey]
			newStep['comments'] = comments

			# won't really use the widgets bit			
			if len(step.widgets):
				newStep['widgets']=True
			else:
				newStep['widgets']=False


			# if it#s a widget add the detail in the fields
			newfields=[]
			for field in fields:
				print "FIELD ABOUT 958",field[1]
				if step.widgets.has_key( field[1] ):
					(widgetName,widgetData) = step.widgets[field[1]]
					(a,b,c)=field
					if fieldValues.has_key( b ):	c = fieldValues[b]
					newfields.append( (a,b,c,widgetName) )	
				else:
					print "field=",field
					(a,b,c)=field
					if fieldValues.has_key( b ):	c = fieldValues[b]
					newfields.append( (a,b,c,""))


			newStep['fields'] = newfields

			return {'operation':'getStepDetail','status':1,'json':json.dumps( {'result' : newStep} ) }
		except:	
			print "exception in selectProcess"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback)
			for e in traceback.format_tb(exc_traceback):	print e
		
		return {'operation':'getStepDetail','status':0}

	def listProcessImages(self,process):
		"""
		listProcessImages()
			string: process name

		return: list images used in a response header
		"""
		print "listProcessImages <- %s" %(process)
		try:
			tmpimages={}
			tmpprocess = pickle.loads(open("process/%s/%s" %(self.userid,process)).read())
			for activity in tmpprocess.activities:
				for step in activity.steps:	
					for img in step.img:
						tmpimages[img]=1
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



	def setMashEfficiency(self,efficiency):
		"""
		setMashEfficiency()
			integer efficiency in percentage (e.g. 67)

		return: standard response
		"""
		print "setMashEfficiency() -> %s" %(efficiency)
		status=0
		try:
			self.recipe.mash_efficiency = efficiency
			self.calculate()
			status=1
		except:
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

			
	def takeStock(self):
		"""
		takeStock()
			Takes stock for the current recipe and associates it with the active brewlog
		
		return: standard json activity
		"""

		print "takeStock() <>"
		status=0
		try:
			if self.brewlog and self.process and self.recipe:
				print "TROUBLESHOOTING API TAKE STOCK"		
				print self.recipe,self.recipe.name
				print self.recipe.fermentables
				print self.recipe.hops
				print self.recipe.fermentables
				ourstock=self.stores.takeStock( self.recipe )
				print self.stores
				self.brewlog.stock=ourstock	
#				print "takeStock"
#				print "recipe.fermentables"
#				print self.recipe.fermentables
#				print "outstock"
				print ourstock
				for x in ourstock:
					print x
#				print " ourstock['fermentables'] is missing form self.stres.takeStock"

				
#				print ourstock['fermentables']
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
							substock['item']=d.name
#						print stockItem,ourstock[stockType][stockItem]
							result[stockType][stockItem].append( substock)

				print "result = {} ",result
				self.process.compile( self.recipe,self.brewlog)
				self.saveBrewlog()

				return {'operation':'takeStock','status' :1,'json' : json.dumps( {"result": result})}
		except:	
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
			return {'operation':'takeStock','status':status }

		return {'operation':'takeStock','status':status}
		
	
	def listStoreCategories(self):
		"""
		listStoreCategories()
			Provides a list of the categories we can use
		
		return: standard json wiht categories
		"""

		print "listStoreCategoriesk() <>"
		result=['Fermentables','Hops','Yeast','Consumables','Other']
		return {'operation':'listStoreCategories','status' :1,'json' : json.dumps( {"result": result})}


	def listStoreItems(self,category):
		"""
		listStoreItems()
			Provides a list of stock in the store

			string: category as per listStoreCategories

		return: standard json with simple list of stock itmes
		"""
		print "listStoreItems() <- %s" %(category)
		(store,data)=self._getStoreAndData(category)

		if store and data:
			items={}
			for storeObject in store:
				purchasedQty=0
				purchasedCost=0
				for purchasedItem in store[storeObject]:
					if purchasedItem.qty > 0:
						purchasedQty = purchasedQty + purchasedItem.qty
						purchasedCost = purchasedCost + (purchasedItem.price * purchasedItem.qty)

				if purchasedQty > 0:
					items[ storeObject.name ] = {}
					items[ storeObject.name ]['name'] =storeObject.name
	#				items[ storeObject.name ]['purchases'] = []
					items[ storeObject.name ]['cost']=purchasedCost
					itemObject = data( storeObject.name )

					items[ storeObject.name ]['unit'] = itemObject.unit
#					items[ storeObject.name ]['unit'] = storeObject.unit
					items[ storeObject.name ]['totalqty'] = purchasedQty
					items[ storeObject.name ]['category'] = category

			tosort=[]
			for i in items:
				tosort.append(i)
			tosort.sort()
			
			stockitems=[]
			for i in tosort:
				stockitems.append(items[i])
			result = {'category' : category,'items':stockitems}
			print "listStoreItems() > status=1"
			return {'operation':'listStoreItems','status' :1,'json' : json.dumps( {"result": result})}


		print "listStoreItems() > status=0"
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



		
	def getStockFullDetails(self,category,itemName,getRawResult=0):
		"""
		getStockFullDetails()
			Provides a list of stock in the store

			string: category as per listStoreCategories
			string: item as per listStoreItems

		return: standard json with details of the stock item
		"""
		print "getStockFullDetails() <- %s,%s" %(category,itemName)
		(store,data)=self._getStoreAndData(category)
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
			print "getStockFullDetails() -> status=1"
			return {'operation':'getStockFullDetails','status' :1,'json' : json.dumps( {"result": result})}


		print "getStockFullDetails() -> status=0"
		return {'operation':'getStockFullDetails','status' :0  }




	def changeItemQty(self,category,itemName,stockTag,newQty):
		"""
		changeItemQty()
			Provides a list of stock in the store

			string: category as per listStoreCategories
			string: item as per listStoreItems

		return: standard json with details of the stock item
		"""
		print "changeItemQty() < %s,%s,%s,%s" %(category,itemName,stockTag,newQty)
		status=0
		(store,data)=self._getStoreAndData(category)
		if store and data:
			for storeObject in store:
				print storeObject.name,itemName
				if storeObject.name == itemName:

					for purchasedItem in store[storeObject]:
						print "\t",purchasedItem.stockTag,stockTag,purchasedItem.stockTag==stockTag
						if purchasedItem.stockTag == stockTag:
							print "purchasedItem.qty",purchasedItem.qty
							purchasedItem.qty = float(newQty)
							print "purchasedItem.qty",purchasedItem.qty
							status=1

		if status:
			result	= self.getStockFullDetails(category,itemName,getRawResult=1)
			return {'operation':'changeItemQty','status' :1,'json' : json.dumps( {"result": result})}
		
		self.saveStore()	
		print "changeItemQty() -> %s" %(status)
		return {'operation':'changeItemQty','status' :0  }

	
	def listIngredientsAndSuppliers(self,category):
		"""
		listIngredientsAndSuppliers(category)
			category = 	fermentable,hop,yeast,misc,consumable
			
		Note: this is similair to listIngredients but provided as a convenience
		return: list of ingredients from the presets file
		"""

		print "listIngredientsAndSuppliers -> %s" %(category)
		status=0

		try:
			result={}
			result['items'] =  self.data.dumpJSON( category )
			result['suppliers'] = []
			for supplierName in self.data.suppliers:
				if len(supplierName)>0:
					result['suppliers'].append(supplierName)
#
			result['suppliers'].sort()
			return {'operation' : 'listIngredientsAndSuppliers', 'status' : 1,
					'json' : "%s" %( json.dumps( {'result':result} )  ) 
				}
		except:	
			print "EXCEPTION"
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	print e
		return {'operation' : 'listIngredientsAndSuppliers', 'status' : status }

	
if __name__ == '__main__':
	api = brewerslabApi()

