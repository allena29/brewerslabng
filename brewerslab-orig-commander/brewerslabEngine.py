from __future__ import division
#!/usr/bin/python
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
# $Revision: 1.71 $ $Date: 2011-11-03 23:09:26 $ $Author: codemonkey $
#
import hashlib
import re
import cPickle as pickle
import sys
import math
import os
import time
from BJCPxmltools import bjcpStyleTools
from ngData import * 


class brewerslab:
 	def __init__(self):
		self.recipe=None
		


class brwlabProcess:

		
	def __init__(self,parent=None,activityTitle=None):
		"""
		brwlabProcess is designed to ensure a smooth brew day
		"""
		self.credit=None
		self.version=0.2
		self.name=""
		self.userid="allena29"
		self.description="Process Description Goes Here"
		self.recipe=brwlabRecipe()

		self.stepshi=0
		self.priming_sugar=None


		self.parent = parent
		self.activityTitle = activityTitle
		self.hashindex={}

		
		# Control if compile() will use ingredients
		self.need_recipe_ingredients=0
		self.recipeUpgrades={}


		self.steps =[]
	
		self.recipe = None

		# Consumables/Ingredients/Equipmnet
		# will be added to the parent process object only

		self.providesMash = 1
		self.providesBoil = 1
		self.maxBoilVolume = 27 

		self.compileCount=0
		
		if parent:			# if parent: means we are a child and parent references our parent
			self.consumables=[]
			self.ingredients=[]	#starting to deprecate this
			self.equipment=[]

						# replacmets for ingredients
			self.FERMENTABLES=[]
			self.HOPS=[]
			self.YEAST=[]
			self.MISC=[]

		if not parent:
			self.brewday = brwlabProcess(self,"Brewday")
			self.brewday.need_recipe_ingredients=1

			self.postbrewday = brwlabProcess(self,"Post Brewday")

			self.bottlingAndKegging = brwlabProcess(self,"Bottling/Kegging")

			self.activities = [self.brewday, self.postbrewday, self.bottlingAndKegging ]


		self.fixed_boil_off = 0
		self.percentage_boil_off = 15	# %
		self.fixed_cool_off = 0
		self.percentage_cool_off = 4	# also known as shrinkage, the density change of boiling-->cool wort
		
		# A few bits of equipment needed later on in calculations
		# can be modified 
		self.fermentation_bin = brwlabEquipment("Fermentation Bin")
		self.fermentation_bin.dead_space = 1.50666		# Litres		# should be taking this frrom process not hardcoded here.

		#self.calclog=self.calclog+"Reference for fermentation bin %s\n" %(self.fermentation_bin)
		self.racking_bucket = brwlabEquipment("Racking Bucket")
		self.racking_bucket.dead_space =0 		# Litres
		self.mash_tun = brwlabEquipment("Mash Tun")
		self.mash_tun.dead_space = 3
		self.hlt=brwlabEquipment("Hot Liquror Tank")
		self.hlt.heatpower=1.6
		self.hlt.dead_space = 1
		self.immersionchiller=brwlabEquipment("Immersion Chiller")

		boiler = brwlabEquipment("Boiler")
		boiler.dead_space=1
		boiler.volume=20
		self.boilers = [boiler]

	def load(self,pickleName="process/process"):
		o=open( pickleName, "r")
		pickle.loads( o.read() )
		o.close()


		
		# Remoe Instance Method References
#		self.recipe.addFermentable=self.recipe.addIngredient
#		self.recipe.addYeast=self.recipe.addYeast
		for activity in self.activities:	
			for step in activity.steps:
				step.addEquipment = self.addThing #self.parent.addEquipment
				step.addConsumable = self.addThing #None #self.parent.addThing
				step.useConsumable = self.useThing #None #self.parent.useThing
				step.addIngredient = self.addThing  #self.parent.addThing
				step.useIngredient = self.useThing #None
				step.parent=self
				step.recipe=self.recipe



	def save(self,pickleName):

			

		# Remoe Instance Method References
		try:
			self.recipe.process=None
		except:	pass
		try:
			self.recipe.addHop=None
		except:	pass
		try:
			self.recipe.addFermentable=None
		except:	pass
		try:
			self.recipe.addYeast=None
		except:	pass
		for activity in self.activities:	
			for step in activity.steps:
				step.addEquipment = None #self.parent.addEquipment
				step.addConsumable = None #self.parent.addThing
				step.useConsumable = None #self.parent.useThing
				step.addIngredient = None #self.parent.addThing
				step.useIngredient = None
				#step.parent=None
				#step.recipe=None
		# not solved, actually looks like it was recipe.process being bound
		# that cuased the problem.
	#	self.hashindex=""
	#	self.recipe=None
	#	self.brewday=None
	#	self.bottlingAndKegging=None
		#self.postbrewday=None
		#self.activities=None


#		for x in self.__dict__:
#			print x," ",self.__dict__[x]

		#recipe_name = re.compile("[^A-Za-z0-9]").sub("_",self.name)
		o=open( pickleName , "w")
		o.write( pickle.dumps( self ) )
		o.close()

		try:
			self.recipe.process = self 
		except:	pass
		for activity in self.activities:	
			for step in activity.steps:
				step.addEquipment = activity.addThing #self.parent.addEquipment
				step.addConsumable = activity.addThing #None #self.parent.addThing
				step.useConsumable = activity.useThing #None #self.parent.useThing
				step.addIngredient = activity.addThing  #self.parent.addThing
				step.useIngredient = activity.useThing #None
				#step.parent=self
				#step.recipe=self.recipe


	def dump(self,recipe=None):
		
		resStr = ""

		if recipe:
			self.recipe = recipe

		if not self.parent:
			resStr = resStr + "Process: %s\n" %(self.name)
			for activity in self.activities:
				resStr = resStr + activity.dump( self.recipe )
		if self.parent:
			resStr = resStr + "%s\n" %(self.activityTitle)
			for step in self.steps:
				resStr = resStr+"\n"
				resStr = resStr + step.dump(recipe)

		return resStr

	def newstep(self,name=None):
		step = brwlabStep(name=name,parent=self)
		self.steps.append(step)

		self.stepshi=self.stepshi+1
		hashk ="mh%s%s%s" %( hashlib.md5("%s" %(self.activityTitle)).hexdigest(), hashlib.md5("%s" %(name)).hexdigest(),self.stepshi )
#		print "HASHK:step: mh %s %s %s --> %s " %(self.activityTitle, name, len(self.steps),hashk)
		step.uniqueid = hashk
		self.parent.hashindex[ hashk ] = (self,-1)

		return step

	
	def checkHashIndex(self):	
		"""
		Makes sure we have enough hash indexes
		"""

		for activity in self.activities:
			i=0
			for step in activity.steps:	
				j=0
				i=i+1
				hashk ="mh%s%s%s" %( hashlib.md5("%s" %(activity.activityTitle)).hexdigest(), hashlib.md5("%s" %(step.name)).hexdigest(),i) 
#				print "HASHK:chix: mh %s %s %s --> %s" %(activity.activityTitle, step.name, i,hashk)
				self.hashindex[ hashk ] = (self,-1)


				for (littlestep,extra) in step.content:
					hashk ="ls%s%s%s%s%s" %( j ,hashlib.md5( "%s" %(activity.activityTitle)).hexdigest(), hashlib.md5("%s" %(step.name)).hexdigest(), hashlib.md5("%s" %(littlestep)).hexdigest(), i)
					j=j+1
					self.hashindex[ hashk ] = (step, j-1)


	def GatherThings(self,type=0):
		"""
		Return a step that will be marked as a Auto Gather
		"""
		
		if self.activityTitle == "Brewday":
			step= self.newstep("Gather Equipment, Ingredients and Consumables")
			step.auto="gather"
		elif self.activityTitle == "Bottling/Kegging":
			step= self.newstep("Gather Equipment, Ingredients and Consumables")
			step.auto="gather2"

		return step

	def primingSolution(self):
		"""
		Return a step that will be marked as priming solution
		"""

		step=self.newstep("Prepare Priming Solution")
		step.auto="primingsolution"

		return step




	def _gather(self,activity,brewlog,step):
		"""
		This internal operation will create the gath in activitys
		"""
		
		return []
		if (len(activity.FERMENTABLES) + len(activity.HOPS) + len(activity.YEAST) + len(activity.MISC) ) == 0:

			step.newSubStep( ("No Ingredients Required", {}) )
		else:
			step.newSubStep( ( "Gather %s Ingredients" %( len(activity.ingredients)  ), {} ))

			for (Y,Z) in [ (activity.FERMENTABLES, "fermentables"), (activity.HOPS,"hops"), (activity.YEAST,"yeast"), (activity.MISC,"misc") ]:
				for (item,qtyTotal) in Y:	# Y = activity.FERMENTABLES
					stocktags=""
					if brewlog:		# Z = fermentables - text
						if brewlog.stock:
							if brewlog.stock.has_key( Z ):
								if brewlog.stock[ Z ].has_key( item.name ):
									for (percentage,qty,stockTag,itemOBJ,purchaseOBJ) in brewlog.stock[ Z ][ item.name ]:
										stocktags = stocktags + "\n\t\t      %.1f%s %.0f %% of %s" %(qty,itemOBJ.unit,percentage * 100,stockTag)

					
					step.newSubStep( ( "  %.1f %s %s%s"  %(qtyTotal,item.unit,item.name,stocktags) ,{'complete':1,'bestbefore':(item.name,qtyTotal)} )  )


			
		if len(activity.consumables) == 0:
			step.newSubStep( ("No Consumables Required", {}) )
		else:
			step.newSubStep( ( "Gather %s Consumables" %( len(activity.consumables)  ), {} ))
			for (item,qty) in activity.consumables:
				step.newSubStep( ( "  %.1f %s %s"  %(qty,item.unit,item.name) ,{'complete':1} )  )


		if len(activity.equipment) == 0:
			step.newSubStep( ("No Equipment Required", {}) )
		else:
			step.newSubStep( ( "Gather %s pieces of equipment" %( len(activity.equipment)  ), {}))
			for item in activity.equipment:
				step.newSubStep( ( "  %s"  %(item.name) ,{'complete':1} )  )



	def compile(self,recipe=None, brewlog=None, agent="cli"):
		"""	
		Compile the process, do things like auto gather equipment/ingredients/consumables
		Auto Generate the Gather Step for an activity 

		If passed a recipe object a calculation will be carried out in quiet mode

		An optional brewlog (which has stock) can be passed which enables the "best before" work to happen
		if we are passed a brewlog then we will add keys to the "completes"

		Note; Compile gets saved in the brewlog for the web. so we don't need to keep compiling on the web.

		agent: cli or web
		
		web can be api or web


		"""


		if recipe:
			currentDbg=recipe.dbg
			recipe.dbg=0
			recipe.calculate()
			recipe.dbg=currentDbg	

			self.recipe = recipe

		for activity in self.activities:

			# replacement for the multiple compile invokes
			if activity.need_recipe_ingredients:
				for (i,q) in recipe.fermentables:
					activity.FERMENTABLES.append( (i,q) )
					activity.ingredients.append( (i,q) )
				for (i,q) in recipe.hops:
					activity.HOPS.append( (i,q) )
					activity.ingredients.append( (i,q) )
				for (i,q) in recipe.yeast:
					activity.YEAST.append( (i,q) )
					activity.ingredients.append( (i,q) )
				for (i,q) in recipe.misc:
					activity.MISC.append( (i,q) )
					activity.ingredients.append( (i,q) )


			for step in activity.steps:
				if self.compileCount ==  self.compileCount:

					if step.auto:
						if step.auto == "grainqty":
							Y=activity.FERMENTABLES
							Z="fermentables"
							for (item,qtyTotal) in Y:	# Y = activity.FERMENTABLES
								stocktags=""
								if brewlog:		# Z = fermentables - text
									if brewlog.stock:
										if brewlog.stock.has_key( Z ):
											if brewlog.stock[ Z ].has_key( item.name ):
												for (percentage,qty,stockTag,itemOBJ,purchaseOBJ) in brewlog.stock[ Z ][ item.name ]:
													stocktags = stocktags + "\n\t\t      %.1f%s %.0f %% of %s" %(qty,itemOBJ.unit,percentage * 100,stockTag)

								
								step.newSubStep( ( "Measure %.1f %s %s%s"  %(qtyTotal,item.unit,item.name,stocktags) ,{'complete':1,'bestbefore':(item.name,qtyTotal)} )  )



					if step.auto:
						if step.auto == "sterilise":
							if len(activity.equipment) == 0:
								step.newSubStep( ("No Equipment Required",{}) )
							else:
								step.newSubStep( ( "Sterilise %s pieces of equipment" %( len(activity.equipment)  ), {} ))
								for item in activity.equipment:
									step.newSubStep( ( "  %s"  %(item.name) , {}  )  )
									for subequip in item.subEquipment:
										step.newSubStep( ( "    %s" %(subequip.name), {}) )

					if step.auto:
						hop_labels = {60:'Copper (60min)',15:'Aroma (15min)',5:'Finishing (5min)',0.000001:'Flameout (0min)'}


						if step.auto.count("hopaddition"):
		
	
							hopaddsorted= []		
							for hopAddAt in recipe.hops_by_addition:
								hopaddsorted.append( hopAddAt )
							hopaddsorted.sort()
							hopaddsorted.reverse()
							
							if len(hopaddsorted) > 0:
#								et="Start the timer counting down from %s minutes and" %(hopaddsorted[0])
								step.timer=hopaddsorted[0]*60
								step.newSubStep( ("Start the timer counting down from %s minutes" %(hopaddsorted[0]),{'complete':1}))

							notDoneChillerFining=1
							for hopAddAt in hopaddsorted:		# hopAddAt was hoptAddAt
								if hop_labels.has_key(hopAddAt):
									additions=hop_labels[ hopAddAt ]
								else:
									additions='%s min' %(hopAddAt)
								
								if hopAddAt <= 15 and notDoneChillerFining:
									notDoneChillerFining=0
									if self.immersionchiller:
										step.newSubStep( ("Add the immersion chiller to the boiler for the last 15 minutes of the boil ensuring it is covered with boiling water to ensure it is sterilised.",{'complete':1}))

									doneFinings=0
									for (copperfining,cfq) in activity.consumables:
										if copperfining.copper_fining > 0 and not doneFinings:	# this was copperfining.copper_fining: was this the issue?
											step.newSubStep(("Add %s%s %s to the boilers to aid coagulation of proteins." %(copperfining.copper_fining,copperfining.unit,copperfining.name) ,{'complete':1}))
											doneFinings=1
								step.newSubStep( ("add %s hop additions to the boil with %s minutes remaining on the timer" %(additions, hopAddAt),{'complete':1}))



	
						if step.auto == "hopmeasure":
				
							totalBoilerCapacity = 0
							for boiler in self.boilers:
								totalBoilerCapacity = totalBoilerCapacity + boiler.volume

							hopaddsorted= []		
							for hopAddAt in recipe.hops_by_addition:
								hopaddsorted.append( hopAddAt )
							hopaddsorted.sort()
							hopaddsorted.reverse()

							for hopAddAt in hopaddsorted:
								if hop_labels.has_key(hopAddAt):
									additions=hop_labels[ hopAddAt ]
								else:
									additions='%s min' %(hopAddAt)

								for hop in recipe.hops_by_addition[ hopAddAt ]:
									for boiler in self.boilers:
										percentage = boiler.volume / totalBoilerCapacity 
										hopqty = recipe.hops_by_addition[hopAddAt][hop] * percentage

										step.newSubStep( ( " Measure %.1f%s of %s for %s additions in %s L Boiler" %( hopqty,hop.unit,hop.name, additions, boiler.volume), {'complete':1} ))


						
						if step.auto == "sterilisebottles":
							sterilising_powder_dosage = 4.5

							# work on the largest volume
							totalVolume = 0
							totalQtyOfBottles = 0  
							if brewlog.stock:
								if brewlog.stock.has_key('consumables'):
									for stockitem in brewlog.stock['consumables']:	
										qtyOfThisBottle = 0
										for (percent,thisQty,stocktag,item,purchase) in brewlog.stock['consumables'][stockitem]:
											if item.category == "bottle":
												qtyOfThisBottle = qtyOfThisBottle + thisQty

												# upgrade data
												if not item.__dict__.has_key("fullvolume"):	item.fullvolume=500
											if item.category == "sterilisingpowder":
												if thisQty > 0:	
													sterilising_powder_dosage = item.dosage
										if qtyOfThisBottle > 0:
											totalQtyOfBottles = totalQtyOfBottles + qtyOfThisBottle 
											totalVolume = totalVolume + (item.fullvolume * qtyOfThisBottle)
							if totalQtyOfBottles == 0:
								totalQtyOfBottles = totalQtyOfBottles + (recipe.batch_size_required * 2)

							

											# 7 bottles per row
							bfp=100
							sterilising_powder_volume_needed = (totalVolume / totalQtyOfBottles) * 7
							sterilising_powder_volume_needed = (sterilising_powder_volume_needed * (bfp/100) /1000)
							sterilising_powder_needed = sterilising_powder_volume_needed / sterilising_powder_dosage
							for bottle_row in range(int(math.ceil( totalQtyOfBottles / 7 ))):
								step.newSubStep( ("Prepare %.1f tsp of sterilising powder in %.2fL of warm water for bottle row %s" %(sterilising_powder_needed, sterilising_powder_volume_needed, bottle_row+1),{'complete':1}))
								step.newSubStep( ("Fill each of the bottles %.0f%% full with sterilising solution for bottle row %s" %(bfp,bottle_row+1),{'complete':1}))


	
						if step.auto == "gather":
							# Moved this logic out into a new function to allow us to reuse
							self._gather(activity, brewlog, step)



#						if step.auto == "primingsolution":


						if step.auto == "gather2":
							# Note we no longer need to explicitly "addConsumable" on the bottles
							# as takeStock() and checkStockAndPrice() will take care of us
							# we cna only get our information from a brew log that has stock
							# if we don't have stock we will assume 500ml
							self._gather(activity, brewlog, step)


							totalQtyOfBottles = 0  
							if brewlog.stock:
								if brewlog.stock.has_key('consumables'):
									for stockitem in brewlog.stock['consumables']:	
										qtyOfThisBottle = 0
										for (percent,thisQty,stocktag,item,purchase) in brewlog.stock['consumables'][stockitem]:
											if item.category == "bottle":
												qtyOfThisBottle = qtyOfThisBottle + thisQty

										if qtyOfThisBottle > 0:
											step.newSubStep( ("  Gather %.0f of %s" %(qtyOfThisBottle,item.name),{'complete':1}), 0)
											totalQtyOfBottles = totalQtyOfBottles + qtyOfThisBottle 
		
									# now find crowncaps
									qtyOfCaps =0
									for stockitem in brewlog.stock['consumables']:
										for (percent,thisQty,stocktag,item,purchase) in brewlog.stock['consumables'][stockitem]:
											if item.category == "bottlecaps":
												qtyOfCaps = qtyOfCaps + thisQty
												self.recipe.num_of_crown_caps = qtyOfCaps

												step.newSubStep( ("  Gather %s %s" %(thisQty,item.name),{'complete':1}),0)


									step.priming_sugar_qty = 0
										
									qtyOfSugar=0
									for stockitem in brewlog.stock['consumables']:
										for (percent,thisQty,stocktag,item,purchase) in brewlog.stock['consumables'][stockitem]:
											if item.category == "primingsugar":
												qtyOfSugar = qtyOfSugar + thisQty

												step.newSubStep( ("  Gather %s gm of %s" %(thisQty,item.name),{'complete':1}),0)
												step.priming_sugar_qty = step.priming_sugar_qty + thisQty

									step.priming_sugar_water = ((totalQtyOfBottles+5) * 15) - step.priming_sugar_qty
									self.recipe.priming_sugar_water = step.priming_sugar_water
									self.recipe.priming_sugar_total = qtyOfSugar * step.priming_sugar_qty
							# Assumption of 500ml
							if totalQtyOfBottles == 0:
								step.newSubStep(("  Gather %.0f crown caps*" %( (recipe.batch_size_required * 2)+4),{'complete':1}),0 )
								step.newSubStep(("  Gather %.0f of 500ml bottles*" %( recipe.batch_size_required * 2),{'complete':1}),0 )
								totalQtyOfBottles = totalQtyOfBottles + (recipe.batch_size_required * 2)

#							step.name = re.compile("\.\.\.NUM\.\.\.").sub("%s" %(totalQtyOfBottles), step.name)



					# Extended Preparation Instructions
					#{'hopaddition': 
					#	{('brwlabMisc', 'Lemongrass'): 'When flameout hops are added then add the cut/peeled lemongrass to the boiler', 
					#	('brwlabMisc', 'Lemon Peel'): 'At 15 minute hop additions add the grated lemon peel to the boiler'}, 
					#'hopmeasure': 
					#	{('brwlabMisc', 'Lemongrass'): 'Peel lemongrass and cut in 2 cm pieces', 
					#	('brwlabMisc', 'Lemon Peel'): 'Grate the peel of unwaxed lemons and set aside to add to the boiler'}}

					if step.auto and recipe.__dict__.has_key("preparation"):
						if recipe.preparation.has_key(step.auto):
							for (ri,rq) in recipe.misc:
								if recipe.preparation[step.auto].has_key( ri.uid ):
									step.newSubStep( ("  %s" %(recipe.preparation[step.auto][ri.uid]),{'complete':1}),0)
							

	def addEquipment(self,item):
		self.equipment.append(item)


	def addThing(self,item,qty):
		"""
		Add a consumable into the Process
		item:	<brwlabFermentable|brwlabHop> object
		qty:	qty in item.unit

		"""
		# item validate
		item._validate()

		if item.objType == "brwlabConsumable":
			l = self.consumables
		else:
			l = self.ingredients
		beginQty=0
		for (x,y) in l:
			if x.name == item.name:
				beginQty=y
				l.remove( (x,y) )
#				l.append( (x,y+qty))
#				item.qty=y+qty
#				foundExisting=1	
				
#		if not foundExisting:
		l.append( (item, beginQty+qty) )
		item.qty=beginQty+qty



	def useThing(self,item,qty):
		"""
		Use a consumable into the Process
		item:	<brwlabFermentable|brwlabHop> object
		qty:	qty in item.unit

		"""
		# item validate
		item._validate()

		if item.objType == "brwlabConsumable":
			l = self.consumables
		else:
			l = self.ingredients

		foundExisting=0
		for (x,y) in l:
			if x.name == item.name:
				if y < qty:

					print "Need to think through error handling",x.name
					print "want to use consumables but we haven't added ENOUGH"
					sys.exit(0)
				else:
					foundExisting=1	
				
		if not foundExisting:
			print "Need to think through error handling",item.name
			print "want to use consumables but we haven't added them"
			sys.exit(0)



	def getProcess(self):
		return self

	def generateMySql(self,owner="test@example.com"):
		p=self
		process=p.name

		print "DELETE FROM gCompileText WHERE owner='%s' AND process = '%s'; "%(owner,self.name)
		print "DELETE FROM gIngredients WHERE owner ='%s' AND process = '%s';" %(owner,process)
		print "DELETE FROM gProcesses WHERE owner ='%s' AND process = '%s';" %(owner,process)
		print "DELETE FROM gProcess WHERE owner ='%s' AND process = '%s';" %(owner,process)
		print "DELETE FROM gWidgets WHERE owner ='%s' AND process = '%s';" %(owner,process)
		print "DELETE FROM gEquipment WHERE owner ='%s' AND process = '%s';" %(owner,process)
		print "DELETE FROM gField WHERE owner ='%s' AND process = '%s';" %(owner,process)


		subrequired = re.compile("\.\.\.([a-zA-Z0-9\_]*)\.\.\.")
		a=0
		for activity in p.activities:
			s=0
			for step in activity.steps:

				ourCompile = gCompileText(owner=owner,process=process,activityNum=a,stepNum=s)

				MATCHES={}
				if len(step.text) > 1:
					matches = subrequired.findall(step.text)
					for match in matches:
						if not MATCHES.has_key( match):
							MATCHES[match]=1

				for substep in step.substeps:
					matches = subrequired.findall(substep.name)
					for match in matches:
						if not MATCHES.has_key(match):
							MATCHES[match]=1



				for x in MATCHES:	
					ourCompile.toReplace.append(x)
				if len(ourCompile.toReplace):
					print ourCompile.insertSql()


			



				s=s+1
			a=a+1
	
		e=gEquipment(owner=owner,process=process,equipment="hlt",name=p.hlt.name)
		e.dead_space = float(p.hlt.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.hlt.volume)
		except:
			pass
		try:		
			e.heatPower = float(p.hlt.heatPower)
		except:
			pass
		print e.insertSql()

	
		if p.immersionchiller:
			e=gEquipment(owner=owner,process=process,equipment="immersionchiller",name=p.immersionchiller.name)
			e.mustSterilise=True
#			e.dead_space = float(p.hlt.dead_space)
			print e.insertSql()



		e=gEquipment(owner=owner,process=process,equipment="mashtun",name=p.mash_tun.name)
		e.dead_space = float(p.mash_tun.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.mash_tun.volume)
		except:
			pass
		print e.insertSql()

		e=gEquipment(owner=owner,process=process,equipment="fermentationbin",name=p.fermentation_bin.name)
		e.dead_space = float(p.fermentation_bin.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.fermentation_bin.volume)
		except:
			pass
		print e.insertSql()

		e=gEquipment(owner=owner,process=process,equipment="rackingbucket",name=p.racking_bucket.name)
		e.dead_space = float(p.racking_bucket.dead_space)
		e.mustSterilise=True
		try:
			e.volume = float(p.racking_bucket.volume)
		except:
			pass
		print e.insertSql()

		for boiler in p.boilers:
			e=gEquipment(owner=owner,process=process,equipment="boiler",name=boiler.name)
			e.dead_space = float(boiler.dead_space)
			e.mustSterilise=True
			e.volume = float(boiler.volume)
			try:
				e.boilVolume=float(boiler.boilVolume)
			except:
				pass
			print e.insertSql()
		

		r=gProcesses(owner=owner,process=process)
		print r.insertSql()


		r=gProcess(owner=owner,process=process,activityNum=-1,stepNum=-1,subStepNum=-1)
		r.fixed_boil_off = float(p.fixed_boil_off)
		r.fixed_cool_off = float(p.fixed_cool_off)
		r.percentage_boil_off = float(p.percentage_boil_off)
		r.percentage_cool_off = float(p.percentage_cool_off)
		print "Not sure if line 787 s hould have a put or not???"
		print r.insertSql()
		aNum=0
		for activity in p.activities:


			for (ingredient,qty) in activity.ingredients:
				III = gIngredients(owner=owner)
				III.ingredient = ingredient.name
				III.qty=float(qty)
				III.process=process
				III.processIngredient=True
				III.processConsumable=False
				if ingredient.objType == "brwlabConsumable":
					III.ingredientType="consumable"
				elif ingredient.objType == "brwlabFermentable":
					III.ingredientType="fermentable"
				elif ingredient.objType == "brwlabHop":
					III.ingredientType="hop"
				elif ingredient.objType == "brwlabYeast":
					III.ingredientType="yeast"
				elif ingredient.objType == "brwlabMisc":
					III.ingredientType="misc"
				print III.insertSql()

			for (ingredient,qty) in activity.consumables:
				III = gIngredients(owner=owner)
				III.ingredient = ingredient.name
				III.qty=float(qty)
				III.process=process
				III.processIngredient=True
				III.processConsumable=True
				if ingredient.objType == "brwlabConsumable":
					III.ingredientType="consumable"
				elif ingredient.objType == "brwlabFermentable":
					III.ingredientType="fermentable"
				elif ingredient.objType == "brwlabHop":
					III.ingredientType="hop"
				elif ingredient.objType == "brwlabYeast":
					III.ingredientType="yeast"
				elif ingredient.objType == "brwlabMisc":
					III.ingredientType="misc"
				print III.insertSql()



			r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=-1,subStepNum=-1)
			r.stepName=activity.activityTitle
			print r.insertSql()


			sNum=0
			for step in activity.steps:
				ssNum=0
				r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=sNum,subStepNum=-1)
				if len(step.text) == 0:
					r.text=""
				else:
					r.text=step.text	
				r.stepName=step.name
				for img in step.img:
					r.img.append(img)
				if not step.attention:
					r.attention=""
				else:
					r.attention=step.attention
				r.needToComplete=1
				if not step.auto:
					r.auto=""
				else:
					r.auto = step.auto

				r.numSubSteps=len(step.substeps)
#				r.timer=step.timer	# don't set the timer here, it should be on the substep
				try:
				#	print "<br><b>step.condition</b> %s" %(step.condition)
					for X in step.condition[0]:
				#		print " %s " %(X)
						r.conditional.append("%s" %(X) )
				#	print "<br>"
					
				except:
					r.conditional=[]
					pass
				print r.insertSql()
#					step.widgets['__adjustedgrav1'] = ('gravityTempAdjustment',['__temp1','__grav1'])


				for (fieldLabel,fieldKey,fieldVal) in step.fields:
					
					r=gField(owner=owner,process=process,activityNum=aNum,stepNum=sNum)
					r.fieldKey= fieldKey
					r.fieldLabel=fieldLabel
					r.fieldVal=fieldVal
					if step.__dict__.has_key("widgets"):
						if step.widgets.has_key(fieldKey):
							(jd,elliot) = step.widgets[fieldKey]
							r.fieldWidget = jd
					print r.insertSql()

				if step.__dict__.has_key("widgets"):
					for widget in step.widgets:
						(w,v) =step.widgets[widget]
						print "widget %s" %(w)
						r=gWidgets(owner=owner,process=process,activityNum=aNum,stepNum=sNum)
						r.widgetName=widget
						r.widget= w
						for wv in v:
							r.widgetValues.append(wv)
						print r.insertSql()

				for substep in step.substeps:
					r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=sNum,subStepNum=ssNum)
					substep.name=re.compile("[\r\n]").sub('  ',substep.name)
					r.stepName= substep.name

					if substep.__dict__.has_key("kitchenTimer"):
						if substep.kitchenTimer:
							(KTname,KTtimer) = substep.kitchenTimer
							r.timerName = KTname
							r.timerTime = KTtimer
					try:
						r.condition=substep.condition
					except:
						pass
					if substep.need_to_complete:	r.needToComplete=True
					print r.insertSql()
					ssNum=ssNum + 1
				sNum = sNum + 1
			aNum = aNum + 1	



class brwlabSubStep:

	def __init__(self,name=None,parent=None):
		self.name=name
		self.parent=parent
		self.startTime=None
		self.endTime=None
		self.completed=0
		self.condition=None
		self.stepid = "ss%s%s" %( hashlib.md5("%s" %(self)).hexdigest()[0:14], time.time() )
		self.need_to_complete=0

class brwlabStep:
	
	def __init__(self,name=None,parent=None):
		"""
		brwlabStep 
		"""
		self.version=0.1
		self.auto=None

		self.stepid = "st%s%s" %( hashlib.md5("%s" %(self)).hexdigest()[0:14], time.time() )
		self.parent = parent
		self.addEquipment = self.parent.addEquipment
		self.addConsumable = self.parent.addThing
		self.useConsumable = self.parent.useThing
		self.addIngredient = self.parent.addThing
		self.useIngredient = self.parent.useThing
		self.timer = None
		self.img=[]

		self.fields=[]

		self.substeps = []

		self.widgets={}
		self.condition=None

		# complete for the littlesteps will be by hashindex

		self.name=""
		if name:	self.name=name
	
		self.autogen = 0		# think this is unused
		self.content = []		# looking to deprecated this in favour of substeps
		self.text= [] 
		self.setupText=None
		self.attention=None

		self.startTime=None
		self.endTime=None
		self.completed=0


	def variableSub(self,line):

		if self.recipe:
			try:
			
				line = re.compile("\.\.\.strike_temp_5\.\.\.").sub( ".__%.1f__." %(self.recipe.strike_temp_5), line)
			except:	pass
			try:
				line = re.compile("\.\.\.strike_temp\.\.\.").sub( ".__%.1f__." %(self.recipe.strike_temp), line)		
			except:	pass
			try:
				line = re.compile("\.\.\.mash_liquid\.\.\.").sub( ".__%.1f__." %(self.recipe.mash_liquid), line)		
			except:	pass
			try:
				line = re.compile("\.\.\.mash_liquid_6\.\.\.").sub( ".__%.1f__." %(self.recipe.mash_liquid+6), line)		
			except:	pass
			try:
				line = re.compile("\.\.\.sparge_heating_time\.\.\.").sub( ".__%.1f__." %(self.recipe.sparge_heating_time), line)		
			except:	pass
			try:
				line = re.compile("\.\.\.sparge_water\.\.\.").sub( ".__%.1f__." %(self.recipe.sparge_water), line)		
			except:	pass
			try:
				line = re.compile("\.\.\.sparge_temp\.\.\.").sub(".__%.0f__." %(self.recipe.sparge_temp), line)
			except:	pass
			try:
				line = re.compile("\.\.\.target_mash_temp\.\.\.").sub(".__%s__." %(self.recipe.target_mash_temp), line)	
			except:	pass
			try:
				line = re.compile("\.\.\.estimated_og\.\.\.").sub(".__%.3f__." %(self.recipe.estimated_og),line)
			except:	pass
			try:
				line = re.compile("\.\.\.estimated_fg\.\.\.").sub(".__%.3f__." %(self.recipe.estimated_fg),line)
			except:	pass
			try:
				line = re.compile("\.\.\.boil_vol\.\.\.").sub( ".__%.3f__." %(self.recipe.water_in_boil),line)
			except:	pass
			try:
				line = re.compile("\.\.\.estimated_og_grain\.\.\.").sub( ".__%.3f__." %(self.recipe.estimated_gravity_grain),line)
			except:	pass
			try:
				line = re.compile("\.\.\.post_mash_gravity\.\.\.").sub( ".__%.3f__." %(self.recipe.post_mash_gravity),line)
			except:	pass
			try:
				line = re.compile("\.\.\.pre_boil_gravity\.\.\.").sub( ".__%.3f__." %(self.recipe.pre_boil_gravity),line)
			except:	pass
			try:
				line = re.compile("\.\.\.estimated_og\.\.\.").sub(".__%.3f__." %(self.recipe.pretopup_estimated_og),line)
			except:	pass
			try:
				line = re.compile("\.\.\.pretopup_post_mash_og\.\.\.").sub( ".__%.3f__." %(self.recipe.pretopup_post_mash_gravity),line)
			except:	pass
			try:
				line = re.compile("\.\.\.pretopup_estimated_gravity_grain\.\.\.").sub( ".__%.3f__." %(self.recipe.pretopup_estimated_gravity_grain),line)
			except:	pass
			try:
				line = re.compile("\.\.\.topupvol\.\.\.").sub( ".__%.3f__." %(self.recipe.top_up),line)
			except:	pass
			try:
				line = re.compile("\.\.\.pretopup_preboil_gravity\.\.\.").sub( ".__%.3f__." %(self.recipe.pretopup_pre_boil_gravity),line)
			except:	pass
			try:
				line = re.compile("\.\.\.postboil_precool_og\.\.\.").sub(".__%.3f__." %(self.recipe.precool_og),line)
			except:	pass
			try:
				line = re.compile("\.\.\.estimated_abv\.\.\.").sub(".__%.2f__." %(self.recipe.estimated_abv),line)
			except:	pass

		# 	
		try:
			line = re.compile("\.\.\.primingsugartotal\.\.\.").sub(".__%s__." %(self.recipe.priming_sugar_total),line)
		except:
			pass
		try:
			line = re.compile("\.\.\.primingsugarqty\.\.\.").sub(".__%s__." %(self.recipe.priming_sugar_qty),line)
		except:
			pass
		try:
			line = re.compile("\.\.\.bottles_required\.\.\.").sub( ".__%s__." %(2+self.recipe.bottles_required), line)		
		except:
			pass
		try:
			line = re.compile("\.\.\.primingwater\.\.\.").sub(".__%s__." %(self.recipe.priming_sugar_water),line)
		except:
			pass
		try:
			line = re.compile("\.\.\.num_crown_caps\.\.\.").sub(".__%s__." %(self.recipe.num_of_crown_caps),line)
		except:
			pass

		return line

	def newSubStep(self, content, index=-1):
	
			
		(x,y) = content

		substep = brwlabSubStep( x, self) 
		if y.has_key("complete"):
			if y['complete'] == 1:	
				substep.need_to_complete = 1
		if y.has_key("kitchentimer"):
			(ka,kb) = y['kitchentimer']
			substep.kitchenTimer=(ka,kb)
		else:
			substep.kitchenTimer=None

		if y.has_key("condition"):
			substep.condition= y['condition']

		if index < 0:
			self.substeps.append( substep )
		else:
			self.substeps.insert( index, substep )
				


	def linewidth(self, line):
		return line


	def dump(self,recipe):
		resStr =""
		self.recipe=recipe
		newline=re.compile("\n")
		start=re.compile("^")
		resStr = resStr + "\t[ ] %s\n" %( self.variableSub( self.name ))
		if self.text:	
			resStr = resStr + "\t%s\n" %(start.sub('\t',newline.sub('\n\t\t', self.variableSub( self.text ) )))
		for substep in self.substeps:
			content=self.variableSub(substep.name)
			if substep.need_to_complete:
#		for (content, completeCheckbox) in self.content:
#			content = self.variableSub( content )
#			if completeCheckbox:
				resStr = resStr + "\t[ ]\t%s\n" %(content)
			else:
				resStr = resStr + "\t    \t%s\n" %(content)

		if self.attention:	
			resStr = resStr + "\t!!!%s\n" %(start.sub('\t',newline.sub('\n\t\t', self.variableSub( self.attention ) )))



		return resStr


class brwlabEquipment:

	def __init__(self,name=None):
		""" 
		brwlabEquipment
		"""
		self.version=0.1
		self.mustSterilise=0	
		self.name=""
		self.pre_exist=1
		self.subEquipment=[]
		if name:
			self.name=name

class brwlabConsumable:

	def __init__(self,name=None):
		"""
		brwlabConsumables
		"""
		self.objType="brwlabConsumable"
		self.version=0.1
		self.description=None
		self.pre_exist=1
		self.copper_fining=0
		self.dosage=0
		self.caprequired=1
		self.co2required=0
		self.category=""

		self.name=""
		self.unit="tsp"
		self.valid=0
		self.qty=0
		self.qty_multiple=1
		self.wastage_fixed=0

		if name:	self.name=name
		self.cost=""



	def dumpJSON(self):
		return {
			'name' : self.name,
			'ingredientType':'consumable',
			'description' : self.description,
			'unit' : self.unit,
			}

	def _validate(self):
		if self.valid:	return
		self.uid=(self.objType,self.name)
		return

class brwlabEnergy:
		
	def __init__(self):
		""" 
		brwlabEnergy
		"""
		self.version=0.1
class brwlabMisc:
	
	def __init__(self,name=None):
		self.objType="brwlabMisc"
		self.copper_fining=None
		self.version=0.1
		self.description=None
		self.name=""
		self.pre_exist=1
		if name:	self.name = name
		self.valid=0
		self.uid="invalid"
		self.unit="L"
		self.qty_multiple = 0.001
		self.category="Misc"
		self.subcategory=None
		self.wastage_fixed=0



	def dumpJSON(self):
		return {
			'name' : self.name,
			'ingredientType':'misc',
			'description' : self.description,
			'unit' : self.unit,
			}

	def _validate(self):
		if self.valid:	return
		self.uid=(self.objType,self.name)
		return
	

class brwlabYeast:
	
	def __init__(self,name=None):
		self.objType="brwlabYeast"
		self.version=0.1
		self.description=None
		self.name=""
		if name:	self.name = name
		self.valid=0
		self.uid="invalid"
		self.pre_exist=1
		self.atten=73
		self.unit="pkt"
		self.qty_multiple = 1
		self.category="Yeast"
		self.subcategory=None
		self.wastage_fixed=0



	def dumpJSON(self):
		return {
			'name' : self.name,
			'ingredientType':'yeast',
			'description' : self.description,
			'unit' : self.unit,
			'attenuation' : self.atten,
			}

	def _validate(self):
		if self.valid:	return
		self.uid=(self.objType,self.name)
		return
	



class brwlabHop:
	
	def __init__(self,name):
		self.objType="brwlabHop"
		self.version=0.2
		# Added leaf/pellet/plug
		self.hopform="leaf"
		self.hopuse="boil"

		self.name=name
		self.majorName=""
		self.unit="gm"
		self.uid="invalid"
		self.alpha=0
		self.valid=0
		self.pre_exist=1
		self.qty_multiple = 1
		self.category="Hop"
		self.subcategory=None
	
		self.wastage_fixed=0
		self.styles=[]
		self.description=None
		self.substitution = []		

#		self._upgrade()


	def dumpJSON(self):
		return {
			'name' : self.name,
			'ingredientType':'hop',
			'description' : self.description,
			'unit' : self.unit,
			'alpha' : self.alpha,
			}



	def dump(self):
		print self.name, "   ",self
		print "Alpha:", self.alpha, "%"
		if self.description:	print "Description:",self.description
		if len(self.substitution):	print "Substitutions:",self.substitution
		if len(self.styles):	print "Styles:",self.styles

	def _validate(self):
		if self.valid:	return
#		self.majorName=self.name
#		self.name="%s - %.1f %%" %(self.majorName,self.alpha)
		self.uid=(self.objType,self.name)
		self.valid=1



class brwlabFermentable:

	def __init__(self,name=None):
		self.objType="brwlabFermentable"
		self.version=0.2
		if not name:	self.name=""
		if name:	self.name=name
		self.unit="gm"	
		self.uid="invalid"
		self.valid=0
		self.description=""	
		self.wastage_fixed=0
	
		self.qty_multiple = 1
		self.category=None
		self.subcategory=None
		self.pre_exist=1

		self.ppg=None	# points/pound/gallon
		self.hwe=None	# hot/water/extract
	
		self.isGrain=0
		self.isAdjunct=0
		self.mustMash=0
		self.addBoil=0

		self.colour = -1
		self.mustMash = 0
		self.aromatic = -1
		self.biscuit= -1
		self.body = -1
		self.burnt = -1
		self.caramel = -1
		self.chocolate = -1
		self.coffee = -1
		self.grainy = -1 
		self.malty = -1 
		self.head = -1
		self.nutty = -1
		self.roasted = -1
		self.smoked = -1
		self.sweet = -1
		self.toasted = -1 

	def upgrade(self):
		oldversion = self.version
		if oldversion < 0.2:
			try:
				a=self.colour
			except:
				self.colour = -1
			try:
				b=self.aromatic
			except:
				self.aromatic = -1
			try:
				c = self.biscuit 
			except:
				self.biscuit = -1
			try:
				d = self.burnt 
			except:	
				self.burnt = -1
			try:
				e=self.caramel
			except:	
				self.caramel = -1
			try:
				f=self.chocoloate
			except:
				self.chocolate=-1
			try:	
				g=self.coffee
			except:
				self.coffee=-1
			try:
				h=self.grainy
			except:
				self.grainy=-1
			try:
				j=self.malty
			except:
				self.malty=-1
			try:
				i=self.head
			except:
				self.head=-1
			try:
				k=self.malty
			except:
				self.malty=-1
			try:
				l=self.nutty
			except:
				self.nutty=-1
			try:
				m=self.roasted
			except:
				self.roasted=-1
			try:
				n=self.smoked
			except:	
				self.smoked=-1
			try:
				o=self.sweet
			except:
				self.sweet=-1
			try:
				p=self.toasted
			except:
				self.toasted=-1
			self.version=0.2
			return "upgraded from %s to %s" %(oldversion,self.version)
		return "noupgrade"



	def dumpJSON(self):
		return {
			'name' : self.name,
			'ingredientType':'fermentable',
			'description' : self.description,
			'unit' : self.unit,
			'colourEbc' :self.colour,
			'mustMash' : self.mustMash,
			'aromatic' : self.aromatic,
			'body' : self.body,
			'burnt' : self.burnt,
			'caramel' : self.caramel,
			'chocolate' : self.chocolate,
			'coffee' :self.coffee,
			'grainy' : self.grainy,
			'head' : self.head,
			'malty' : self.malty,	
			'nutty' : self.nutty,
			'roasted' : self.roasted,	
			'smoked' : self.smoked,
			'sweet' : self.sweet,
			'toasted' : self.toasted,
			'hwe' : self.hwe,
			}



	def dump(self):
		yesno=['No','Yes']
		print self.name, "   ",self
		print "Extract:", self.extract, "%"
		if self.description:	print "Description:",self.description
		if self.colour > -1:	print "Colour (EBC):",self.colour
		if self.mustMash>-1:	print "mustMash:" , yesno[ self.mustMash]
		if self.aromatic>-1:	print "aromatic:" , yesno[ self.aromatic]
		if self.body>-1:	print "body:" , yesno[ self.body]
		if self.burnt>-1:	print "burnt:" , yesno[ self.burnt]
		if self.caramel>-1:	print "caramel:" , yesno[ self.caramel]
		if self.chocolate>-1:	print "chocolate:" , yesno[ self.chocolate]
		if self.coffee>-1:	print "coffee:" , yesno[ self.coffee]
		if self.grainy>-1:	print "grainy:" , yesno[ self.grainy]
		if self.head>-1:	print "head:" , yesno[ self.head]
		if self.malty>-1:	print "malty:" , yesno[ self.malty]
		if self.nutty>-1:	print "nutty:" , yesno[ self.nutty]
		if self.roasted>-1:	print "roasted:" , yesno[ self.roasted]
		if self.smoked>-1:	print "smoked:" , yesno[ self.smoked]
		if self.sweet>-1:	print "sweet:" , yesno[ self.sweet]
		if self.toasted>-1:	print "toasted:" , yesno[ self.toasted]
	
	def _validate(self):
		if self.valid:	return	
		self.uid=(self.objType,self.name)
		self.valid=1
		return	
	
	def calculateFromYield(self,dbfg):
		"""
		Calculates extract given an expected yield 
			1 pound of sugar disolved in yeilds 100% and gives 1.046
			sugar is used as the reference point for the yeilds
			yield can be refered to a dry basis fine grind
		"""
	
		self.extract = dbfg
		if dbfg > 0:
			sugar_reference_ppg=46
			sugar_reference_hwe=384
			# Point / Pound / Gallon
			self.ppg = (dbfg/100) * sugar_reference_ppg
			# Hot Water Extract
			self.hwe = (dbfg/100) * sugar_reference_hwe


	






class brwlabRecipe:

	def __init__(self):
		"""
		Values to be set:
			mash efficiency 		= i 	Mash Effiency % default to 75	
			batch_size_required	= i	Batch Size in Litres (no top up)
			top_up			= i 	Topup in Litres

		"""	
		self.credit=None
		self.recipe_type="All-Grain"
		self.version=0.2
		self.name=""
		self.signature=""
		self.dbg=2
		self.description="No Description"
		self.calculated=0	
		self.forcedstyle=None
		self.priming_sugar_qty = 2.75 # gms	per 500ml
		self.addFermentable = self.addIngredient
		self.addHop = self.addIngredient
		self.addYeast = self.addIngredient
		self.post_boil_volume = 0

		if not os.path.exists("bjcpstyles.brwlab"):
			if not os.path.exists("styleguide2008.xml"):
				sys.stderr.write("BJCP Styles not found\n")
				sys.stderr.write("The styles are not distributed with this script but can be found from \n")
				sys.stderr.write(" http://www.bjcp.org/stylecenter.php\n\n")
				sys.stderr.write("BJCP styles will be imported if stylesguides2008.xml is placed in the \n")
				sys.stderr.write("working directory.\n")
			else:
				sys.stderr.write("Importing BJCP Styles...\n")
				try:
					bjcp= bjcpStyleTools()
					bjcp.importXML("styleguide2008.xml")
				except:
					sys.stderr.write("Error importing BJCP styles\n")
					sys.exit(-1)


			
		self.batch_size_required=23	# Final Volume Required in Litres
		self.batch_size_required_plus_wastage=23 # Final volume plus wastage
							 # it is down to the process to increase this
							# if required the primary intention is to account
							# for wastage in the kettles 
		self.boil_time = 60
		self.top_up=0			# Note Batch Size above should include top_up volume and in calculate
						# the top_up will be ignored.
		self.top_up_gravity= 0 ### 0 not 1.000
		self.calculate_version=0.2


		# Process Affinity Bits
		self.mashRequired=1
		self.boilRequired=1
		self.boilVolume= 0  # L
		self.validprocess = 0
		self.process = None 

		self.calclog=""
			
		self.fermentables=[]
		self.hops=[]
		self.yeast=[]
		self.misc=[]

		self.hops_by_addition={}
		self.hops_by_contribution={}
		self.hops_by_avg_alpha={}

		# Twekas
		self.mash_efficiency = 75

		self.target_mash_temp_tweak=2		# and adjustment factor
		self.target_mash_temp= 68			# C
		self.mash_grain_ratio = 1.18294118		# litres
		self.initial_grain_temp = 17			# C


	def save(self,pickleName="recipes/recipe"):
		# Need to un-reference methods

		self.addFermentable=None
		self.addYeast=None
		self.addHop=None

		if self.process:
			for activity in self.process.activities:	
				for step in activity.steps:
					step.addEquipment = None #self.parent.addEquipment
					step.addConsumable = None #self.parent.addThing
					step.useConsumable = None #self.parent.useThing
					step.addIngredient = None #self.parent.addThing
					step.useIngredient = None

		self.addHop=None
		self.addFermentable=None
		self.addYeast=None
		
		o=open( pickleName ,"w")
		o.write( pickle.dumps( self ) )
		o.close()

		if self.process:
			for activity in self.process.activities:	
				for step in activity.steps:
					step.addEquipment = self.process.addThing #self.parent.addEquipment
					step.addConsumable = self.process.addThing #None #self.parent.addThing
					step.useConsumable = self.process.useThing #None #self.parent.useThing
					step.addIngredient = self.process.addThing  #self.parent.addThing
					step.useIngredient = self.process.useThing #None

		self.addHop= self.addIngredient
		self.addFermentable= self.addIngredient
		self.addYeast=self.addIngredient


	def dump(self):
		strRes=""
		for (dic,tex) in [ (self.fermentables,'Fermentables'),(self.hops,'Hops'),(self.yeast,'Yeast'),(self.misc,'Misc') ]:
			strRes = strRes+"%s\n" %(tex)
			for (item,qty) in dic:
				strRes=strRes+"\t%.1f %s %s\n" %(qty,item.unit,item.name)
			strRes=strRes+"\n"
		return strRes 



	def dumpJSON(self):
		result = {}
		result['ingredients'] = {}
		# need to convert objects out
		for (dic,tex) in [ (self.fermentables,'Fermentables'),(self.hops,'Hops'),(self.yeast,'Yeast'),(self.misc,'Misc') ]:
			result['ingredients'][tex] = []
			for (title,qty) in dic:
				result['ingredients'][tex].append( (title.name,qty))

		try:
			result['estimatedABV'] = self.estimated_abv 
		except:
			result['estimatedABV'] = 0
		try:
			result['estimatedIBU'] = self.estimated_ibu
		except:
			result['estimatedIBU'] =0
		try:
			result['estimatedEBC'] = self.estimated_ebu
		except:
			result['estimatedEBC'] =0
		result['mashRequired'] = self.mashRequired
		result['boilRequired'] = self.boilRequired
		result['boilTime'] = self.boil_time
		result['topup'] = self.top_up
		result['batchsize'] = self.batch_size_required
		result['mashTemp'] = self.target_mash_temp
		result['recipetype'] = self.recipe_type
		result['recipeDescription'] = self.description
		if self.process:
			result['process'] = self.process.name
		else:
			result['process'] = "unspecified"	
		return result

	def adjustMashEfficiency(self,efficiency, allowedToScale = [] ):
		"""
		adjustMashEfficiency by increasing the grains.

			if sent a list of gains in "allowedToScale" only those grains will be updated. 
			otherwise all grains will be updated. 

			The allowed to scale doesn't quite get to the target if we only have 1 item.
			to get it perfect will be hard (different malts have different extractions efficiency)	
			but it is probably good enough if we just make sure that we add the delta against
			thos malts that are included.
		
			example: 4.51 before  @ 75%
				 4.51 with scaling all three matls (3kg maris otter, 500g caragold, 250 torrifed wheat)
				 4.38 only allow marris to scale (750 g missing)
				 4.52 only with marris otther with spreading the delta elsewhere
	
		"""

		canScale= {}
		if len(allowedToScale) == 0:
			for (ingredient,qty) in self.fermentables:
				if ingredient.isGrain:	canScale[ ingredient ] = 1

		else:
			for (ingredient,qty) in self.fermentables:
				for a in allowedToScale:
					if ingredient == a:	canScale[ ingredient ] = 1


		missing = []
		notmissing = []
		notgrain = []

		new_efficiency_factor  = self.mash_efficiency / efficiency 
		self.calclog = self.calclog + "masheffic: new efficiency %.0f%% old efficiency %.0f%% (factor %.2f)\n" %(efficiency,self.mash_efficiency, new_efficiency_factor)
#		new_qty = []
		for (ingredient,qty) in self.fermentables:
			if canScale.has_key( ingredient ):
				self.calclog = self.calclog + "masheffic: changing qty of %s from %.1f to %.1f\n" %(ingredient.name, qty, qty*new_efficiency_factor)
				qty = qty * new_efficiency_factor
				notmissing.append( (ingredient,qty) )
			elif ingredient.isGrain:		
				missing.append( (ingredient,qty) )
			else:
				notgrain.append( (ingredient,qty) )
#			new_qty.append( (ingredient,qty) )



		self.fermentables = []

		for (x,y) in missing:
			
			new_notmissing = []

			delta_qty = (y * new_efficiency_factor) - y
			self.calclog = self.calclog +"masheffic: ingredient %s is excluded from change (%.1f over %s)\n" %(x.name,delta_qty,len(notmissing))
			
			for (X,Y) in notmissing:
				new_notmissing.append( (X, (Y+delta_qty/len(notmissing))) )
				self.calclog = self.calclog +"masheffic: ingredient %s is increased from %.1f to %.1f\n" %(X.name, Y, Y+delta_qty/len(notmissing))
			notmissing=new_notmissing
				
				
		for (x,y) in notmissing:	self.fermentables.append( (x,y) )
		for (x,y) in missing:	self.fermentables.append( (x,y) )
		for (x,y) in notgrain:	self.fermentables.append( (x,y) )

		
		self.mash_efficiency = efficiency

	


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

		
		strike_temp = ( ( .41 / self.mash_grain_ratio) * ((self.target_mash_temp + self.target_mash_temp_tweak)  - self.initial_grain_temp) ) + self.target_mash_temp

		
		self.calclog = self.calclog + "striketmp:\t strike_temp = %.1fC\n" %(strike_temp) 
		self.calclog = self.calclog + "striketmp:\t\t %.1fC = ( ( .41 / mash_grain_ratio ) * (target_mash_temp - initial_grain_temp) ) + target_mash_temp\n" %(strike_temp) 
		self.calclog = self.calclog + "striketmp:\t\t %.1fC = ( ( .41 / %.2f ) * (%.1fC - %.1fC) ) + %.1fC\n" %(strike_temp,self.mash_grain_ratio,(self.target_mash_temp + self.target_mash_temp_tweak),self.initial_grain_temp,self.target_mash_temp) 
		
		return strike_temp
		


	def isValidProcess(self,process):

		if self.mashRequired and not process.providesMash:
			self.calclog = self.calclog + "ERROR    : Process %s does not support mashing\n" %(process.name)
			return -1
		if self.boilRequired and not process.providesBoil:
			self.calclog = self.calclog + "ERROR    : Process %s does not support boiling\n" %(process.name)
			return -1
		if self.boilRequired and self.boilVolume > process.maxBoilVolume:
			self.calclog = self.calclog + "ERROR    : Process %s can only support boiling %sL\n" %(process.name,process.maxBoilVolume)
			return -1

		return 1

	def attachProcess(self,process):
		""" Validate if we the process is compatible with the recipe """

		if not self.isValidProcess(process):
			return -1

		self.process = process
		self.process.recipe = self

		# bind methods
		#self.bottlingAndKegging = process.bottlingAndKegging

		if not self.process.__dict__.has_key("recipeUpgrades"):	self.process.recipeUpgrades={}
		for recipeUpgrade in self.process.recipeUpgrades:
			self.calclog=self.calclog="recipeupgrd: checking recipe for upgrade %s\n" %(recipeUpgrade)
			if recipeUpgrade == 'grainthicknessMustBeGreaterThan':
				if self.mash_grain_ratio < self.process.recipeUpgrades[recipeUpgrade]:
					self.calclog=self.calclog="recipeupgrd: increasing mash_grain_ration from %.3f to %.3f\n" %(self.mash_grain_ratio,self.process.recipeUpgrades[recipeUpgrade])
					self.mash_grain_ratio = self.process.recipeUpgrades[recipeUpgrade]	

		self.validprocess=1

		return 1



	def addIngredient(self,item,qty,hopAddition=60,hopIBU=0):
		"""
		Add a fermentable,hop  item into the Recipe
		item:	<brwlabFermentable|brwlabHop> object
		qty:	qty in item.unit

		Fermentables
		It is not necessary to flag when to make these additions as they are self 
		evident from the process. That is "+isGrain+mustMash" go in the Mash
		"+isGrain-mustMash" may go into the steep or mash. "+adjunct-mustMash" goes 	
		into the copper "+adjunct+mustMash" goes into the Mash
	
		Hops:
		for hop additions a "hopAddition" time should be set to allow for biterness calculations

		"""
		# item validate
		item._validate()

		if item.objType	== "brwlabFermentable":
			l = self.fermentables
		elif item.objType == "brwlabHop":
			l = self.hops
		elif item.objType == "brwlabYeast":
			l = self.yeast
		elif item.objType == "brwlabMisc":
			l = self.misc


		beginQty=0
		# x = 
		# y = 
		# DEPRECATED: z = extra info, really used for hops "add At" to keep unique
		# DEPRECATED: t = tag,

		for (x,y) in l:
			if x.name == item.name:
				# this is carried out for hops as well. this combines multiple additions
				# of the same hop into a same "ingredient"
				beginQty=y
				l.remove( (x,y) )
		

		l.append( (item, beginQty+qty) )


		# Note: original_qty can only ever be set by this method and not by any scale/adjust 
		# methods
		item.original_qty = beginQty + qty

		# For hops organise by addition
		if item.objType == "brwlabHop":
			if not self.hops_by_addition.has_key( hopAddition ):
				self.hops_by_addition[ hopAddition ] = {}
				self.hops_by_contribution[ hopAddition ] = {}		
					# hops by contribution is used to mitigate against a moving
					# ibu based on different stores
			if not self.hops_by_addition[ hopAddition ].has_key( item ):
				self.hops_by_addition[ hopAddition ][ item ] = 0
				self.hops_by_contribution[ hopAddition ][ item ] = 0
			self.hops_by_addition[ hopAddition ][ item ] = self.hops_by_addition[ hopAddition ][ item ] + qty
			self.hops_by_contribution[ hopAddition ][ item ] = -1 # flag that we don't know this yet.
									  # calculate() will provide this
									# or if we have provided in the IBU instead of the qty
									# we place that htere instead
			if hopIBU:	self.hops_by_contribution[ hopAddition ][ item ] = hopIBU
			




	def scaleHops(self,targetIbu=10):
		"""
		Scale Hops to a target IBU. Hops will be scaled in proportion 

		"""
		total_contribution=0
		# Calculate Expected Gravity:
		# ppg X wt / batch size	
		self.calclog = self.calclog + "scalehops: Calculating expected gravity\n"
		for (fermentable,qty) in self.fermentables:
			self.calclog = self.calclog + "scalehops:	fermentable: %s%s %s\n" %(qty,fermentable.unit,fermentable.name)
			self.calclog = self.calclog + "scalehops:	fermentable: %s%s %s %.2f\n" %(qty,fermentable.unit,fermentable.name,fermentable.hwe)
			contribution = (qty /1000 * fermentable.hwe) / self.batch_size_required_plus_wastage
			self.calclog = self.calclog + "scalehops: \t\t\tcontribution = %s\n" %(contribution)
			self.calclog = self.calclog + "scalehops: \t\t\t%s = %s * %s / %s\n" %(contribution, qty/1000, fermentable.hwe , self.batch_size_required_plus_wastage)
			total_contribution = total_contribution + contribution	
		
		self.calclog = self.calclog + "scalehops:	correcting gravity based on mash efficiency of %s %%\n" %(self.mash_efficiency)
		estimated_gravity = total_contribution * (self.mash_efficiency / 100)
		self.calclog = self.calclog + "scalehops: Calculating Tinseth Hop Calculation\n"
		self.calclog = self.calclog + "scalehops: http://www.realbeer.com/hops/research.html\n"


		# New Hop Structure 		
		hop_utilisation_factors = {}
		for hopAddAt in self.hops_by_addition:
			hop_utilisation_factors[ hopAddAt ] = self._tinsethUtilisation( hopAddAt, estimated_gravity )

		that_hop_ibu = []
	
		total_hop_ibu = 0
		for hopAddAt in self.hops_by_addition:
			for hop in self.hops_by_addition[ hopAddAt]:	
				hopqty = self.hops_by_addition[ hopAddAt ][ hop ]
				this_hop_ibu = hop_utilisation_factors[ hopAddAt ] * (hop.alpha * hopqty * 1000 ) / self.batch_size_required_plus_wastage
				that_hop_ibu.append( this_hop_ibu )
				self.calclog = self.calclog + "scalehops: \t%.2f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.name, hopAddAt)
				self.calclog = self.calclog + "scalehops: \t\tthis_hop_ibu = %.3f\n" %(this_hop_ibu)
				self.calclog = self.calclog + "scalehops: \t\t\t %.3f = hop_utilisation_factor * (hop_alpha * qty * 1000)\n" %(this_hop_ibu)
				self.calclog = self.calclog + "scalehops: \t\t\t %.3f = %.4f * (%s * %s * 1000)\n" %(this_hop_ibu,hop_utilisation_factors[ hopAddAt ], hop.alpha, hopqty )

				total_hop_ibu = total_hop_ibu + this_hop_ibu

		self.calclog = self.calclog + "scalehops: Scale Hops to target IBU %s\n" %(targetIbu)
		self.calclog = self.calclog + "scalehops: previous total_hop_ibu %s\n" %(total_hop_ibu)

		ibu_adjustment_factor = targetIbu / total_hop_ibu
		
		self.calclog = self.calclog + "scalehops: ibu_adjustment_factor %s\n" %(ibu_adjustment_factor)

		new_hop_qty = []

		# New Hop Adjustment 
		for hopAddAt in self.hops_by_addition:
			for hop in self.hops_by_addition[ hopAddAt]:	
				hopqty = self.hops_by_addition[ hopAddAt ][ hop ]
				new_hop_qty = hopqty * ibu_adjustment_factor
				self.calclog = self.calclog + "scalehops: %s adjusted from %.1f to %.1f\n" %(hop.name,hopqty,hopqty * ibu_adjustment_factor )
				self.hops_by_addition[ hopAddAt ][ hop ] = new_hop_qty
		
			
	#	self._UpdateRecipeHopQtyFromAddAtQty()


#	def _UpdateRecipeHopQtyFromAddAtQty(self):
		# Now we need to update the recipe qty under the hops structure 
		new_hop_qty = []
		for (hop,qty) in self.hops:
			newQty=0
			for hopAddAt in self.hops_by_addition:
				# if we have deleted hops then we might have an empty hops_by_addition[hopAddAt] dict			
				if self.hops_by_addition[hopAddAt].has_key(hop):
					newQty=newQty + self.hops_by_addition[hopAddAt][hop]
			if self.hops_by_addition[hopAddAt].has_key(hop):
				new_hop_qty.append( (hop,qty, newQty) )
		
		# Now we can remove the hops
		for (hop,qty,newqty) in new_hop_qty:
			self.hops.remove( (hop,qty) )
			self.hops.append( (hop,newqty) )	
	
	



	
	def waterRequirement(self,adjustment=0):
		"""
		Calculates the water requirement.


		"""
		self.calclog = self.calclog + "waterreqd: Calculating Water Requirement\n"

		self.calclog = self.calclog + "waterreqd: Batch Size Requried = %s L\n" %(self.batch_size_required)
		self.calclog = self.calclog + "waterreqd: Batch Size Requried (plus wastage)= %s L\n" %(self.batch_size_required_plus_wastage)


		# waterRequirement is pretty much based without the topup
		# we add the topup back in at the end of waterRequirement()
		if self.top_up > 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage - self.top_up
			self.calclog = self.calclog +"waterreqd: TopUp Volum of %.2f --> %.2f L\n" %(self.top_up,self.batch_size_required_plus_wastage)
			
		total_extra_water = 0

		#waterRequirement()
		water_in_boil = 0

		#waterRequirmenet()	
		if adjustment != 0:
			total_extra_water = adjustment 
			self.calclog = self.calclog + "waterreqd: Manual Adjustment --> %s L water\n" %(adjustment)
	
		total_grain_weight = 0	
		for (fermentable,qty) in self.fermentables:
			if fermentable.isGrain:
				if fermentable.unit != "gm":
					sys.stderr.write("critical: Water Requirement requires ferementables to be specified in grammes\n")
					sys.stderr.write("critical: unit was %s\n" %(fermentable.unit))
					sys.exit(2)
				self.calclog = self.calclog + "waterreqd:	fermentable: %s%s %s\n" %(qty,fermentable.unit,fermentable.name)
				total_grain_weight = total_grain_weight + qty

		extra_water = total_grain_weight / 1000

		total_extra_water = total_extra_water + extra_water

		self.calclog = self.calclog + "waterreqd: Grain Weight = %s%s --> %s L water\n" %(total_grain_weight, fermentable.unit, extra_water )
	

		total_hop_weight = 0
		for (hop,hopqty)  in self.hops:
			self.calclog = self.calclog + "waterreqd:	hop: %s%s %s\n" %(hopqty,hop.unit,hop.name)
			if fermentable.unit != "gm":
				sys.stderr.write("critical: Water Requirement requires hops to be specified in grammes\n")
				sys.stderr.write("critical: unit was %s\n" %(hop.unit))
				sys.exit(2)
			total_hop_weight = total_hop_weight + hopqty

		extra_water = ( total_hop_weight * 15 ) / 1000

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




		if self.validprocess:
			extra_water = self.process.mash_tun.dead_space * 1
			total_extra_water = total_extra_water + extra_water 

			self.calclog = self.calclog + "waterreqd: Mash/Lauter Tun Deadspace = %s --> %s L water\n" %(self.process.mash_tun.dead_space,extra_water)

			extra_water = self.process.hlt.dead_space * 1
			total_extra_water = total_extra_water + extra_water
			self.calclog = self.calclog + "waterreqd: Hot Liquor Tank Deadspace = %s --> %s L water\n" %(self.process.hlt.dead_space,extra_water)




			batch_size = self.batch_size_required_plus_wastage

			if self.process.fermentation_bin.dead_space > 0:
				extra_water = self.process.fermentation_bin.dead_space
				batch_size = batch_size + extra_water
				total_extra_water = total_extra_water + extra_water
				self.calclog = self.calclog + "waterreqd: Fermentation Bin Deadspace--> %s L water\n" %(extra_water)
				# don't think we need to add the fermentation bin deadspace
				# as we now count fermentation bin deadspace in 
				# self.batch_size_required_plus_wastage
#				water_in_boil = water_in_boil + extra_water

			if self.process.racking_bucket.dead_space > 0:
				extra_water = self.process.racking_bucket.dead_space
				batch_size = batch_size + extra_water
				total_extra_water = total_extra_water + extra_water
				self.calclog = self.calclog + "waterreqd: Bottling Bin Deadspace--> %s L water\n" %(extra_water)


				#TODO: we don't count racking_bucket
#				water_in_boil = water_in_boil + extra_water


			if self.process.fixed_cool_off > 0:
				extra_water = self.process.fixed_cool_off 
				cooling_extra_water = extra_water
				total_extra_water = total_extra_water + extra_water

				water_in_boil = water_in_boil + extra_water

				self.calclog = self.calclog + "waterreqd: Cooling Loss (fixed %s) --> %s L water\n" %(self.process.fixed_cool_off,extra_water)
			else:
				extra_water = batch_size * ( self.process.percentage_cool_off / 100 ) 
				cooling_extra_water = extra_water
				total_extra_water = total_extra_water + extra_water
				self.calclog = self.calclog + "waterreqd: Cooling Loss (%s %%) --> %s L water\n" %(self.process.percentage_cool_off,extra_water)

				water_in_boil = water_in_boil + extra_water
			
			batch_size_with_cool_off = self.batch_size_required_plus_wastage + extra_water

			if self.process.fixed_boil_off > 0:
				extra_water = self.process.fixed_boil_off 
				boiling_loss_extra_water = extra_water
				total_extra_water = total_extra_water + extra_water
				self.calclog = self.calclog + "waterreqd: Boiling Loss (fixed %s) --> %s L water\n" %(self.process.fixed_boil_off,extra_water)

				water_in_boil = water_in_boil + extra_water

			else:
				extra_water = batch_size_with_cool_off * ( self.process.percentage_boil_off / 100 ) 
				boiling_loss_extra_water = extra_water
				total_extra_water = total_extra_water + extra_water
				self.calclog = self.calclog + "waterreqd: Boiling Loss (%s %%) --> %s L water\n" %(self.process.percentage_boil_off,extra_water)

				water_in_boil = water_in_boil + extra_water
		
		else:
			self.calclog = self.calclog + "error    : No process enabled skipping mash/lauter tun calculation\n"
			self.calclog = self.calclog + "error    : No process enabled skipping fermentation bin deadspace calc\n"
			self.calclog = self.calclog + "error    : No process enabled skipping racking bucket deadspace calc\n"

		water_in_boil = water_in_boil + self.batch_size_required_plus_wastage


		self.calclog = self.calclog + "waterreqd: Total Additional Water Required %.1f L (in boil %.1f L)\n" %(total_extra_water,water_in_boil)
		self.calclog = self.calclog + "waterreqd: Total Water Required %.1f L \n" %(total_extra_water + self.batch_size_required_plus_wastage)
			
		self.water_in_boil = water_in_boil




		tmp = self.batch_size_required_plus_wastage 	# this is without topup as we remove the topup
								# at the start of waterRequirement()

		# set post_boil_volume before deductions
		self.post_boil_volume = water_in_boil
		self.post_boil_volume = self.post_boil_volume + self.process.fermentation_bin.dead_space
		self.post_boil_volume = self.post_boil_volume - self.top_up
		self.calclog = self.calclog + "waterreqd: post boil volume in boilers %.2f \n" %(self.post_boil_volume)
		self.post_boil_volume = self.post_boil_volume - hop_extra_water

#
#	Note: batch_size_required_with_wastage includes boiler deadspace already
#
#
#
#		# If the boiler deadspace is bigger than the hop then don't do it
		boilerDeadSpace=0
		for boiler in self.process.boilers:
#			self.calclog = self.calclog +"waterreqd: boiler %s dead space %.1f\n" %(boiler.name,boiler.dead_space)
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

		self.calclog = self.calclog + "waterreqd: post boil volume in fv/precooling %.2f \n" %(self.post_boil_volume)
		self.post_boil_volume = self.post_boil_volume - cooling_extra_water
		self.calclog = self.calclog + "waterreqd: post boil volume in fv/cooled %.2f \n" %(self.post_boil_volume)

		availableOutOfFV=self.post_boil_volume - self.process.fermentation_bin.dead_space
		self.calclog = self.calclog + "waterreqd: available out of fv %.2f \n" %(availableOutOfFV)


		self.calclog = self.calclog + "waterreqd: InFV = batchSize + FV_Deadspace\n"
		inFV = self.batch_size_required + self.process.fermentation_bin.dead_space
		self.calclog = self.calclog + "waterreqd: %.2f = %.2f + %.4f\n" %(inFV, self.batch_size_required + self.process.fermentation_bin.dead_space, self.process.fermentation_bin.dead_space)

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
		if self.top_up > 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + self.top_up


		return total_extra_water + self.batch_size_required_plus_wastage



	def scaleAlcohol(self, required_abv ):
		"""
		Scale's a recipe to a given alcohol recipe.
		calculate() must be called before this method.

		This is a fairly simple method which scales malt
		and uses scaleHops() to bring it back in line
		"""
		currentDbg=self.dbg
		self.dbg=0
		self.calculate()
		self.dbg=currentDbg	

		current_ibu = self.estimated_ibu

		self.calclog = self.calclog + "scaleabv : Scale Alcohol to required_abv\n"
		self.calclog = self.calclog + "scaleabv : current ibu = %.2f\n" %(current_ibu)

		current_abv = self.estimated_abv
		self.calclog = self.calclog + "scaleabv : current abv = %.2f %%\n" %(current_abv)

		abv_factor = required_abv / current_abv

		self.calclog = self.calclog + "scaleabv : abv_factor = %.3f %%\n" %(abv_factor)

		nextDivTen=0
		# We will recursivel calculate until we hit the target.
		while self.estimated_abv < required_abv *.997 or self.estimated_abv > required_abv *1.003: 

			i = required_abv/current_abv
			

			newqtys = []
			for (fermentable,qty) in self.fermentables:


				newqty = qty * i
				if newqty < 0:	newqty = 1
				newqtys.append( (fermentable, newqty) )
			
			
			self.fermentables=[]
			for (fermentable,qty) in newqtys:
				self.fermentables.append( (fermentable,qty) )

			self.dbg=0
			self.calculate()	
			self.dbg=currentDbg

			



		self.scaleHops( current_ibu )
		



	
	def adjustHopAlphaQty(self, store ):
		"""
		Adjust the Hop Qty's based on the alpha % of the *purchased* hops
		not the alpha of typical hops

		returns true if we can scale within our store
		returns false if we can't scale within our store (but does a best effort scale)

		place holder in place for hop adjust alpha by age as well....
		"""

		# we need a calculation run first
		if not self.calculated:	self.calculate()

		#
		result = True

		# Find the stock we have available to play with
		stock_result = store._stockBestBefore({}, "hops", self.hops, store.Hops, dummyAllocate=1)

		hop_utilisation_factors = {}
		for hopAddAt in self.hops_by_addition:
			hop_utilisation_factors[ hopAddAt ] = self._tinsethUtilisation( hopAddAt, self.estimated_gravity )


		working_total_hop_qty = {}

		total_hop_ibu = 0
		for hopAddAt in self.hops_by_addition:
			for hop in self.hops_by_addition[ hopAddAt]:	
				hopqty = self.hops_by_addition[ hopAddAt ][ hop ]

				if not working_total_hop_qty.has_key( hop ):
					working_total_hop_qty[ hop ] = 0

				hop_ibu_target = self.hops_by_contribution[ hopAddAt ][ hop ]

				# Reset the qty to zero, we may add multiple times to this
				self.hops_by_addition[ hopAddAt ][ hop ] = 0

				# so that we can have a feedback into future invokes of calculate()
				# we need to be make sure calculate() can get stats that match
				# the changes made here
				allocated_avg_hop_alpha = 0
				this_allocation_qty = 0

				# this_hop_ibu provides the hop ibu we need to reach with our stores
				self.calclog = self.calclog + "adjusthop: need hop %s to reach %.2f IBUs with available stock\n" %(hop.name,hop_ibu_target)
				for (availablePercentage,availableQty, stockTag, availableHop, availablePurchase) in stock_result['hops'][ hop.name ]:

					self.calclog = self.calclog + "adjusthop: \tpurchase %s/%s\n" %(availablePurchase.supplier.name,time.ctime(availablePurchase.purchase_date))
					self.calclog = self.calclog + "adjusthop: \thop_ibu_target = %.3f  (%.2f %s @ %.1f %%) \n" %(hop_ibu_target, hopqty, availableHop.unit, hop.alpha)
					if hop_ibu_target > 0:
						if availablePurchase.hop_actual_alpha == -1:	availablePurchase.hop_actual_alpha = hop.alpha

						if availablePurchase.hop_aged_alpha == -1:
							hopAdjustAlpha = availablePurchase.hop_actual_alpha
						else:
							hopAdjustAlpha = availablePurchase.hop_aged_alpha

						
						self.calclog = self.calclog + "adjusthop:\t\tratio = %.4f\n" %(hop.alpha/hopAdjustAlpha)
						self.calclog = self.calclog + "adjusthop:\t\t      = %.2f / %.2f\n" %(hop.alpha,hopAdjustAlpha)

						ratio = hop.alpha / hopAdjustAlpha

						# our desired ratio is:
						desired_qty = hopqty * ratio
						self.calclog = self.calclog + "adjusthop:\t\tdesired_qty = %.3f\n" %(hopqty*ratio)
						self.calclog = self.calclog + "adjusthop:\t\t            = %.2f * %.2f\n" %(hopqty,ratio)
						
						# if we can't fullfill our desired qty with this purchased then
						# we need to scale back to what we can support.
						# however if we can support it then we should deduct and let the loop run
						# it's course
						if desired_qty <= availableQty:
							hop_ibu_target = 0
							self.hops_by_addition[ hopAddAt ][ hop ] = self.hops_by_addition[ hopAddAt ][ hop ] +  desired_qty

							allocated_avg_hop_alpha = allocated_avg_hop_alpha + ( desired_qty * hopAdjustAlpha)
							this_allocation_qty = this_allocation_qty + desired_qty

							working_total_hop_qty[ hop ] = working_total_hop_qty[ hop ] + desired_qty
							
							
							self.calclog = self.calclog + "adjusthop:            target reached with this purchase (%.1f %s)\n" %(desired_qty, availableHop.unit)
						elif desired_qty > availableQty:
							working_hop_ibu = hop_utilisation_factors[ hopAddAt ] * (hopAdjustAlpha * availableQty * 1000 ) / self.batch_size_required_plus_wastage
							self.hops_by_addition[ hopAddAt ][ hop ] = self.hops_by_addition[ hopAddAt ][ hop ] +  availableQty
							allocated_avg_hop_alpha = allocated_avg_hop_alpha + ( availableQty * hopAdjustAlpha )
							this_allocation_qty = this_allocation_qty + availableQty

							working_total_hop_qty[ hop ] = working_total_hop_qty[ hop ] + availableQty

							self.calclog = self.calclog + "adjusthop:            max ibu available from this purchase (%.1f %s %.2f)\n" %( desired_qty, availableHop.unit, working_hop_ibu)
							hop_ibu_target = hop_ibu_target - working_hop_ibu

		
				if not self.hops_by_avg_alpha.has_key( hopAddAt ):
					self.hops_by_avg_alpha[ hopAddAt ] = {}
				if not self.hops_by_avg_alpha[ hopAddAt ].has_key( hop ):
					self.hops_by_avg_alpha[ hopAddAt ][ hop ] = allocated_avg_hop_alpha / this_allocation_qty 


				if hop_ibu_target > 0:
					result = False


		# Now we should adjust the recipe totals, above was updates to the 
		# hop Add At structures

		self.hops=[]	
		for HOP in working_total_hop_qty:
			self.hops.append( ( HOP, working_total_hop_qty[ HOP ] ) )

		# need to be really careful we don't save the recipe with the adjustment
		# because otherwise we will end up with completely
		# random IBU's depending upon what is in the stores at the time 
			# mitigation here is that calculate() will provide us a
			# contribution in IBU's which we use to scale from
			# that way we scale *from* a stable base

		return result





	
	def calculate(self):
		"""
		Calculate Recipe:
		
		Requires 
			- addIngredient/addHops/addYeast/addFermentable to be called to add ingrdients
			- batch_size_required	 -> Batch Size in Litres, this is the final volume

			
		Sets the following variables
			estimated_ibu	<- Hop IBU
			estimated_srm	<- Colour
			estimated_ebc	<- Colour	
			estimated_fg	<- Final Gravity
			estimated_og	<- Original Gravity
			estimated_abv	<- ABV	
		
		Set the following variables which are useful for recipe substritution
			strike_temp		<- Strike Temperature in Degress Centigrade
			mash_liquid		<- Liquid required in mash tun in Litres (pre grain addition)
			bottles_required	<- Number of 500ml bottles required
			sparge_water		<- total water - mash-liquid
		"""

		try:	
			if not self.post_boil_volume > 0:	self.post_boil_volume = 0
		except: pass			
		if not self.validprocess:
			self.calclog="No valid process attached"
			return	

		self.calclog = ""
		self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(self.process.name)
		self.calclog = self.calclog + "process  : brewerslabEngine rev 2012-10-09\n"
		self.calclog = self.calclog + "process  : changes since 2011-04-15\n"
		self.calclog = self.calclog + "process  :  - waterRequirement changes to better include FV deadspace\n"
		self.calclog = self.calclog + "process  :  - waterRequirement ignore hop wastage if boilder deadspace is greater\n"
		self.calclog = self.calclog + "process  : key assumptions\n"
		self.calclog = self.calclog + "process  :  - hops not scaled based on topup assumed marginal\n"
		self.calclog = self.calclog + "process  :    topup with water would reduce hop IBU however topup with reboil\n"
		self.calclog = self.calclog + "process  :    would increase IBU's\n"

		# Scale boil volume with wastage
		# caculate()
		self.calclog = self.calclog + "boilWaste: Adding %.2f for wastage in the fermentation bin\n" %(self.process.fermentation_bin.dead_space)
		self.batch_size_required_plus_wastage = self.batch_size_required

		
	
		boiler_Dead_Space = 0
		for boiler in self.process.boilers:
			self.calclog = self.calclog + "boilWaste: Adding %.2f for wastage in the boiler\n" %(boiler.dead_space)
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + boiler.dead_space
			boiler_Dead_Space = boiler_Dead_Space + boiler.dead_space

		self.boiler_Dead_Space = boiler_Dead_Space


		if self.batch_size_required_plus_wastage != self.batch_size_required:
			self.calclog = self.calclog + "boilWaste: batch size adjusted to %.2f to account for wastage in boiler\n" %(self.batch_size_required_plus_wastage)


		if self.process.fermentation_bin.dead_space >  0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + self.process.fermentation_bin.dead_space
			self.calclog = self.calclog + "boilWaste: batch size adjusted to %.1f to account for wastage in fermentation vessel\n" %(self.batch_size_required_plus_wastage)

			#bug fix when converting for cloud this was testing fermentation deadspace then adding racking bucket
			# racking bucket would have been 0 so no overall effect but a bug none the less
		if self.process.racking_bucket.dead_space >  0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + self.process.racking_bucket.dead_space
			self.calclog = self.calclog + "boilWaste: batch size adjusted to %.1f to account for wastage in racking bucket\n" %(self.batch_size_required_plus_wastage)



		# Assumption built in that bottles are 500 ml
		bottle_size = 0.500	# ml
		# may2013 code audit- was * bottle_size
		self.bottles_required = math.floor( self.batch_size_required / bottle_size )
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
		for (fermentable,qty) in self.fermentables:
			self.calclog = self.calclog + "calcferm :	fermentable: %s%s %s\n" %(qty,fermentable.unit,fermentable.name)
			self.calclog = self.calclog + "calcferm :		hwe: %s extract: %s\n" %(fermentable.hwe,fermentable.extract)
			contribution = (qty /1000 * fermentable.hwe) / self.batch_size_required_plus_wastage
			self.calclog = self.calclog + "calcferm : \t\t\tcontribution = %s\n" %(contribution)
			self.calclog = self.calclog + "calcferm : \t\t\t%s = %s * %s / %s\n" %(contribution, qty/1000, fermentable.hwe , self.batch_size_required_plus_wastage)
			if (fermentable.isGrain or fermentable.mustMash) and not fermentable.isAdjunct:
				self.calclog = self.calclog + "calcferm : \t\t\tIncluding in Mash Gravity\n"
				self.estimated_mash_gravity = self.estimated_mash_gravity + contribution
				total_contribution_grain = total_contribution_grain + contribution
			total_contribution = total_contribution + contribution	
	
		estimated_gravity_grain_100pcnt = total_contribution_grain 
		self.estimated_gravity_grain_100pcnt = estimated_gravity_grain_100pcnt
		self.calclog = self.calclog + "calcferm : 	uncorrected gravity for grain %.3f\n" %(1+(estimated_gravity_grain_100pcnt / 1000))
	
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
		




		#
		# Hops
		#
		self.calclog = self.calclog + "calchops : Calculating Tinseth Hop Calculation\n"
		self.calclog = self.calclog + "calchops : http://www.realbeer.com/hops/research.html\n"

	
		# if we have boiling/cooling loss specified then we should calculate the hops required based on the
		# evaporated value not the full boil volume
		real_batch_size_required_plus_wastage = self.batch_size_required_plus_wastage

		if self.post_boil_volume > 0:
			self.batch_size_required_plus_wastage  = self.post_boil_volume
			self.calclog = self.calclog + "calchops : setting volume for hops calculations to %.2f (was %.2f)\n" %( self.batch_size_required_plus_wastage,real_batch_size_required_plus_wastage)
		else:
			self.calclog = self.calclog + "calchops : ignoring water evaporation in calculation-- don't have loss values\n"


	
		working_total_hop_qty = {}

		# New Hop Structure 	
		# At this stage we wil lcalculate the IBU's with the *default* hop alpha acid.
		# but there is nothing to say we will get hops of this alpha from the store
		# therefore we should call "adjustHopAlphaQty()" to compenstate
		hop_utilisation_factors = {}
		for hopAddAt in self.hops_by_addition:
			hop_utilisation_factors[ hopAddAt ] = self._tinsethUtilisation( hopAddAt, estimated_gravity )
		

		total_hop_ibu = 0
		for hopAddAt in self.hops_by_addition:
			for hop in self.hops_by_addition[ hopAddAt]:	
				hopqty = self.hops_by_addition[ hopAddAt ][ hop ]

				# if we have *EVER* called adjustHopAlphaQty() then we should use the weighted hop alpha
				# average that was calculated last time that we adjusted the qty's of hops.
				# this is to ensure next time adjustHopAlpha is called we don't over/under scale
				HOP_ALPHA = hop.alpha
				if self.hops_by_avg_alpha.has_key( hopAddAt):
					if self.hops_by_avg_alpha[ hopAddAt ].has_key( hop ):
						HOP_ALPHA = self.hops_by_avg_alpha[ hopAddAt ][ hop ]
				

				# Hop Qty hasn't been specified so we need to decide the weight
				if hopqty == 0:	
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
					self.calclog = self.calclog + "calchopsI: \t%.2f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.name, hopAddAt)
					self.calclog = self.calclog + "calchopsI: \t\tthis_hop_weight = %.3f\n" %(this_hop_weight)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = ( this_hop_ibu * batch_size ) / (hop_utilisation_factor * hop_alpha * 1000))\n" %(this_hop_weight)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = ( %.2f * %.2f L ) / ( %.5f * %.2f * 1000))\n" %(this_hop_weight, hop_required_ibu, self.batch_size_required_plus_wastage, hop_utilisation_factors[ hopAddAt ], HOP_ALPHA)
					self.calclog = self.calclog + "calchopsI: \t\tthis_hop_ibu = %.3f\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = hop_utilisation_factor * (hop_alpha * qty * 1000) / batch_size\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsI: \t\t\t %.3f = %.8f * (%s * %s * 1000) / %s\n" %(this_hop_ibu,hop_utilisation_factors[ hopAddAt ], HOP_ALPHA, hopqty ,self.batch_size_required_plus_wastage)

					# if we have come in here with IBU not weight then we need to update the recipe
					
				# Hop Qty has been provided so determine the IBU as normal
				else:
					this_hop_ibu = hop_utilisation_factors[ hopAddAt ] * (HOP_ALPHA * hopqty * 1000 ) / self.batch_size_required_plus_wastage
					if not self.hops_by_contribution.has_key( hopAddAt):	self.hops_by_contribution[hopAddAt] = {}
					self.hops_by_contribution[ hopAddAt ][ hop ] = this_hop_ibu

					self.calclog = self.calclog + "calchopsW: \t%.2f IBU = %s%s %s @ %s minutes\n" %(this_hop_ibu, hopqty, hop.unit, hop.name, hopAddAt)
					self.calclog = self.calclog + "calchopsW: \t\tthis_hop_ibu = %.3f\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsW: \t\t\t %.3f = hop_utilisation_factor * (hop_alpha * qty * 1000) / batch_size\n" %(this_hop_ibu)
					self.calclog = self.calclog + "calchopsW: \t\t\t %.3f = %.8f * (%s * %s * 1000) / %s\n" %(this_hop_ibu,hop_utilisation_factors[ hopAddAt ], HOP_ALPHA, hopqty ,self.batch_size_required_plus_wastage)


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

		for (fermentable,qty) in self.fermentables:
			if fermentable.isGrain:
				total_qty = total_qty + qty
				color_srm = fermentable.colour * 0.508
				grain_qty_pounds = grain_qty_pounds + (qty / 1000 / 0.454)

				weighted_color = (qty / 1000 / 0.454) * color_srm
	
				self.calclog = self.calclog + "calcColor: \t\t color_srm = %s for %s\n" %(color_srm,fermentable.name)
				self.calclog = self.calclog + "calcColor: \t\t\t %s = %.1f EBC * 0.8368  \n" %(color_srm, fermentable.colour)

				self.calclog = self.calclog + "calcColor: \t\t\t weighted_grain_color = %.2f \n" %(weighted_color )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (qty / 1000 / 0.454) * color_srm  \n" %(weighted_color )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (%s / 1000 / 0.454) * %.1f  \n" %(weighted_color,qty,color_srm )
				self.calclog = self.calclog + "calcColor: \t\t\t %.2f = (%s) * %.1f  \n" %(weighted_color,qty/1000/0.454,color_srm )


				sum_weighted_color = sum_weighted_color + weighted_color
				

		total_weighted_color = sum_weighted_color
		self.calclog = self.calclog + "calcColor: \t\t total_weighted_color = %.2f \n" %(total_weighted_color)
		self.calclog = self.calclog + "calcColor: \t\t\t %.2f = sum(weighted_color)   \n" %(total_weighted_color )
		

		volume_gallons = ( self.batch_size_required_plus_wastage + self.top_up ) / 3.785
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
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = (%.3f + %.3f) / 3.785\n" %(volume_gallons,self.batch_size_required_plus_wastage,self.top_up )
		
		estimated_srm=srm			
		estimated_ebc=srm*1.97
		self.calclog = self.calclog + "result   : \t\t estimated ebc = %.1f\n" %(estimated_ebc)
		self.calclog = self.calclog + "calcColor: \t\t\t %.3f = %.1f SRM * 1.97 \n" %(estimated_ebc,estimated_srm)






		self.calclog = self.calclog + "calcfgrav: Calculating Estimated Final Gravity\n"
		# This is could probably take a skew from mash temperature
		grain_fermentable_typical_pcnt = 0.62
		nongrain_fermentable_typical_pcnt=1
		
		grain = 0
		nongrain = 0
		for (fermentable,qty) in self.fermentables:
			if fermentable.isGrain:
				grain = grain + qty
			else:
				nongrain = nongrain + qty
		
		grain_pcnt = grain / (grain + nongrain)
		nongrain_pcnt = nongrain / (grain + nongrain)

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
		for (yeast,yeastqty) in self.yeast:
			yeast_atten = yeast_atten + yeast.atten
			yeast_count = yeast_count + 1

		if yeast_count == 0:
			self.calclog = self.calclog + "calcfgrav: \tWARNING: No YEAST in recipe setting a default attenuation 50\n"
			yeast_atten=0.50
		else:
			yeast_atten =( yeast_atten / yeast_count) / 100
			
		estimated_yeast_attenuation = estimated_gravity * (1-yeast_atten) 
		if self.dbg>=1:	self.calclog = self.calclog + "calcfgrav: \t\t estimated_yeast_attenuation = %.4f\n" %( estimated_yeast_attenuation )
		for (yeast,yeastqty) in self.yeast:
			self.calclog = self.calclog + "calcfgrav:\t\t\t yeast attenuation for %s %.1f \n" %(yeast.name,yeast.atten/100)
		if self.dbg>=1:	self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = estimated_gravity * (1 - yeast_atten) \n" %( estimated_yeast_attenuation)
		if self.dbg>=1:	self.calclog = self.calclog + "calcfgrav: \t\t\t %.4f = %.4f * (1 - %.1f) \n" %( estimated_yeast_attenuation, estimated_gravity, yeast_atten )

		if estimated_yeast_attenuation > estimated_final_gravity:
			estimated_final_gravity = estimated_yeast_attenuation
			self.calclog = self.calclog + "calcfgrav: \t\t Yeast Attenuation used for final gravity estimate\n"
		else:
			self.calclog = self.calclog + "calcfgrav: \t\t  used for final gravity estimate\n"

		#if estimated_final_gravity
		self.calclog = self.calclog + "result   :\t\t Final Gravity Estimate = %.3f \n" %( 1+(estimated_final_gravity)/1000)

		self.calclog = self.calclog + "calcabv  : Alcohol By Volume\n"

		estimated_abv = ( ( 1 + (estimated_gravity)/1000 )  - ( 1+ (estimated_final_gravity)/1000) ) * 131
		self.calclog = self.calclog + "result   :	abv = %.2f %%\n" %(estimated_abv)
		self.calclog = self.calclog + "calcabv  :	%.2f %% = ( original_gravity - final_gravity ) * 131\n" %(estimated_abv)
		self.calclog = self.calclog + "calcabv  :	%.2f %% = ( %.4f - %.4f ) * 131\n" %(estimated_abv, (1+(estimated_gravity/1000)), (1+(estimated_final_gravity/1000)  ))  






		#
		# Recipe Type Calculations
		#
		strike_temp = self.getStrikeTemperature()

		
		total_water = self.waterRequirement()




		#
		# More Top Up's
		# 
		if self.top_up:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage - self.top_up
		
		self.calclog = self.calclog + "mashliqid: Mash Liquid required, based on\n"
		self.calclog = self.calclog + "mashliqid: http://www.brew365.com/technique_calculating_mash_water_volume.php\n"
		#Now that you know the total water required for your batch, you can figure out which portion of this total to use for 
		# mashing and the rest will be used for sparging. To know this, you will need to know what mash thickness ratio to use. 
		# For most purposes, a good ratio is to use 1.25 Qts. per pound of grain (0.3125 gal/lb.)3.
		
		total_grain_weight = 0	
		for (fermentable,qty) in self.fermentables:
			if fermentable.isGrain:
				if fermentable.unit != "gm":
					sys.stderr.write("critical: Mash Liquid requires ferementables to be specified in grammes\n")
					sys.stderr.write("critical: unit was %s\n" %(fermentable.unit))
					sys.exit(2)
				self.calclog = self.calclog + "mashliqid:	fermentable: %s%s %s\n" %(qty,fermentable.unit,fermentable.name)
				total_grain_weight = total_grain_weight + qty


		# previously fixed at 1.25, but we have always had 1.1.829 in the process
		grain_thickness_ratio = self.mash_grain_ratio	# fixed value from reference above, qts per pound of grain
		self.calclog = self.calclog +"mashliqid: grain_thickness_ratio %.3f\n" %(grain_thickness_ratio)
		metric_lb_kg_factor = 0.453592
		metric_gal_l_factor = 3.78541178

		mash_liquid = ( grain_thickness_ratio * ( ( total_grain_weight / 1000 ))) / ( 4 * metric_lb_kg_factor )  * metric_gal_l_factor 

		self.calclog = self.calclog + "result   : mash_liquid = %.1f\n" %( mash_liquid )
		self.calclog = self.calclog + "mashliqid: %.1f = ( grain_thickness_ratio *  total_grain_weight ) / (4 * metric_lb_kg )  * metric_gal_l\n" %(mash_liquid)
		self.calclog = self.calclog + "mashliqid: %.1f = ( %.3f *  %.2f ) / (4 * %.4f ) * %.4f\n" %(mash_liquid, grain_thickness_ratio,total_grain_weight/1000,metric_lb_kg_factor,metric_gal_l_factor)
		self.calclog = self.calclog + "mashliqid: %.1f = ( %.4f ) / ( %.4f  ) * %.4f\n" %(mash_liquid, grain_thickness_ratio * total_grain_weight/1000,4*metric_lb_kg_factor,metric_gal_l_factor)
		self.calclog = self.calclog + "mashliqid: %.1f =  %.4f  * %.4f\n" %(mash_liquid, (grain_thickness_ratio * total_grain_weight/1000) / (4*metric_lb_kg_factor),metric_gal_l_factor)
		

		sparge_water = total_water - mash_liquid
		sparge_water_addition = total_water - mash_liquid



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
		self.calclog = self.calclog + "mashgravi:\t Gravity Expected: %.4f\n" %(1+(estimated_gravity/1000))
		self.calclog = self.calclog + "mashgravi:\t Volume after boil/cooling: %.2f\n" %(self.batch_size_required_plus_wastage)
		pre_boil_gravity = estimated_gravity * self.batch_size_required_plus_wastage  / self.water_in_boil
		self.pre_boil_gravity =1+(pre_boil_gravity/1000)
		self.calclog = self.calclog + "mashgravi:\t %.3f = (1-(estimated_gravity * 1000) * batch_size_with_wastage) / boil_volume\n" %( 1+( post_mash_gravity/1000))
		self.calclog = self.calclog + "mashgravi:\t %.2f = (%.0f * %.2f) / %.2f\n" %( pre_boil_gravity, estimated_gravity,  self.batch_size_required_plus_wastage, self.water_in_boil)

		
		# Time to heat in hot liquor tank
		start_temp = 5
		end_temp= 77
		
		if not self.process.hlt.__dict__.has_key("heatPower"):
			self.calclog=self.calclog +"heatpower:\tWarning heat power not specified for HLT\n"
			hltheatpower=1700
		else:
			hltheatpower=self.process.hlt.heatPower
		heating_time =(4184.0 * sparge_water *(end_temp - start_temp ))/ hltheatpower / 1000.0 / 60.0 ;
		heating_time = int( heating_time + 0.5 )
	
		# Recipe Styles
		self.sparge_temp = 82			# note: the recommendation is 82 counting on some loss of temperature will still keep grain bed
							# temp less than 77... 77 is about the temp tannins are extracted



		# If we have a topup volume we need to adjust some values
		#
#1.048
#18
#1.000
#-1
#17
#1.11
#-0.06
#1.051

		if self.top_up > 0:
			self.calclog = self.calclog +"topupVolu: Have a topup volume of %.2f\n" %(self.top_up)
			v1=self.batch_size_required_plus_wastage
			v2=-self.top_up
			
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



		# Now put batch size back to normal
		if self.top_up > 0:
			self.batch_size_required_plus_wastage = self.batch_size_required_plus_wastage + self.top_up

		# Estrimations
		self.water_required = total_water
		self.estimated_abv = estimated_abv
		self.estimated_ibu=total_hop_ibu
		self.estimated_srm=estimated_srm
		self.estimated_ebc=estimated_ebc
		self.estimated_fg=1+(estimated_final_gravity)/1000
		self.estimated_og=1+(estimated_gravity)/1000

		self.calculated=1



	def getABV(self,original_gravity,final_gravity):
		""" 
		Returns ABV with Original Gravity and Final Gravity provided.
		OG and FG should be provided as 1.xxxx format
		"""
		return (original_gravity - final_gravity) * 131


	def findStyle(self):
		"""
		Find's associated beer styles
		"""
	
		bjcp=bjcpStyleTools()
		return bjcp.findMatchingStyleReport(TargetOG=self.estimated_og,TargetFG=self.estimated_fg,TargetIBU=self.estimated_ibu,TargetSRM=self.estimated_srm)


	def _tinsethUtilisation(self,hop_boil_time=60,estimated_gravity=50):
		""" Executes the tinseth algorithim for hops
			hop_boil_time		- time in minutes
			estimated_gravity	-	degress (e.g. 50, no 1.050)
		"""


		bigness_factor = 1.65 * math.pow(0.000125, (1+(estimated_gravity)/1000)-1)
		boil_time_factor= (1 - math.exp(-0.04 * hop_boil_time) ) / 415
		hop_utilisation = bigness_factor * boil_time_factor 

		self.calclog = self.calclog + "result   :	hop_utilisation = %.4f for %.4f @ %s m \n" %(hop_utilisation,1+(estimated_gravity/1000),hop_boil_time )
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



	

class brwlabInventory:

	def __init__(self):
		self.userid="allena29"	
		self.version=0.1
		self.calclog=""
		# Old Data Strcturues
		self.fermentables= []
		self.hops=[]
		self.yeast=[]
		self.misc=[]
		self.consumables=[]

		self.fermentable_index={}
		self.hop_index={}
		self.yeast_index={}
		self.misc_index={}
		self.consumable_index={}		

		# Replacement Data Strcutures
		self.Fermentables = {}
		self.Hops={}
		self.Yeast={}
		self.Misc={}
		self.Consumable={}
#		self.Ingredients={}

		self.FermentableStockTag= 1
		self.HopStockTag= 1	
		self.YeastStockTag = 1
		self.MiscStockTag = 1
		self.ConsumableStockTag =1
		self.AdjunctStockTag = 1


		self.importantTags= {}
		self.importantTags['grain']={}
		self.importantTags['other']={'Water': {} ,'Additions':{} }
		self.importantTags['yeast']={}
		self.importantTags['hop']={}
		self.importantTags['consumable'] = {'bottle': {},'bottlecaps' : {}, 'primingsugar':{} ,'keg':{},'co2':{}}
	def save(self,pickleName="store/store"):
		o=open( pickleName ,"w")
		o.write( pickle.dumps( self ) )
		o.close()



	def addPurchase(self, purchase):
		"""
		Add a brwlab purchase into the inventory
		brwlab purchase is really just a wrapper
		"""
		
		purchase.purchasedItem._validate()
		
		if purchase.purchasedItem.objType == "brwlabFermentable":
			l=self.Fermentables
			if purchase.purchasedItem.isGrain:
				prefix="WGRMV"
				itemNumber = self.FermentableStockTag 
				self.FermentableStockTag = self.FermentableStockTag + 1
			else:
				prefix="WADMV"
				itemNumber = self.AdjunctStockTag 
				self.AdjunctStockTag = self.AdjunctStockTag + 1
		elif purchase.purchasedItem.objType == "brwlabHop":
			l=self.Hops
			prefix="WHOMV"
			itemNumber = self.HopStockTag
			self.HopStockTag = self.HopStockTag + 1
		elif purchase.purchasedItem.objType == "brwlabYeast":
			l=self.Yeast
			prefix="WYEMV"
			itemNumber = self.YeastStockTag
			self.YeastStockTag = self.YeastStockTag + 1
		elif purchase.purchasedItem.objType == "brwlabMisc":
			l=self.Misc
			prefix="WNIMV"
			itemNumber = self.MiscStockTag
			self.MiscStockTag = self.MiscStockTag + 1
		elif purchase.purchasedItem.objType == "brwlabConsumable":
			l=self.Consumable
			prefix="WCOMV"
			itemNumber = self.ConsumableStockTag 
			self.ConsumableStockTag = self.ConsumableStockTag + 1
	
	
#		if not l.has_key( purchase.purchasedItem ):
#			l[ purchase.purchasedItem ] = []
#		l[ purchase.purchasedItem ].append( purchase )
		haveStock = self._has_ingredient_in_store(l,purchase.purchasedItem )
		if not haveStock:
			haveStock = purchase.purchasedItem
		if not l.has_key( haveStock ):
			l[ haveStock ] = []
		l[ haveStock ].append( purchase )

#		itemNumber = "%s" %(len(l))
		leadingzeros = "0"*(4-len("%s" %(itemNumber)) )
		
		purchase.stockTag = "%s%s%s" %(prefix,leadingzeros,itemNumber)

		# original purchase qty
		purchase.originalQty = purchase.qty
		return purchase.stockTag



	def extendLife(self, category,itemName,itemStockTag):
		""" 
		This operation extends the life of the item
		"""

		if category == "fermentables":  storeDict=self.Fermentables
		if category == "hops":  storeDict=self.Hops
		if category == "yeast": storeDict=self.Yeast
		if category == "misc":  storeDict=self.Misc
		if category == "consumable":    storeDict=self.Consumable

		for storeObject in storeDict:
			if storeObject.name == itemName:
				for purchasedItem in storeDict[ storeObject ]:
					if purchasedItem.stockTag == itemStockTag:
						purchasedItem.best_before_date=time.time()+(86400*8.2)


	def throwAway(self,category,itemStockTag):
		"""
		Throw away this specific stock as it has passed it's limit
		"""
		clearing = self.listClearanceStock()

		for (storeObjectuid,storeObject) in clearing[ category ]:
			for (thresholdType,thresholdValue,purchasedItem) in clearing[category][ (storeObjectuid,storeObject) ]:
				if purchasedItem.stockTag == itemStockTag:
					purchasedItem.qty = 0


	def listClearanceStock(self):
		"""
		Builds a list of stock items which are out of date, and soon out of date
		"""
		bestBeforeThreshold = time.time()
		bestBeforeEarlyThreshold = time.time()-(86400*6)
		toclear={}

		earlythreshold=0
		overthreshold=0

		for (storeDict,storetype  ) in [(self.Fermentables,"fermentables"),(self.Hops,"hops"),(self.Yeast,"yeast"),(self.Misc,"misc"),(self.Consumable,"consumable") ]:
			toclear[ storetype ] = {}
			for storeObject in storeDict:
				for purchasedItem in storeDict[ storeObject ]:
					threshold=-1
					if purchasedItem.qty > 0:	# only >0

						if purchasedItem.best_before_date < bestBeforeThreshold:
							threshold=1
							overthreshold=overthreshold + 1
						elif purchasedItem.best_before_date < bestBeforeEarlyThreshold:
							threshold=0
							earlythreshold=earlythreshold + 1

						if threshold >= 0:	# if threshold or limit exceeded
							if not toclear[ storetype ].has_key( (storeObject.uid,storeObject) ):
								toclear[ storetype ][ (storeObject.uid,storeObject) ] = []
						
							toclear[ storetype ][ (storeObject.uid,storeObject) ].append( (threshold, bestBeforeThreshold-purchasedItem.best_before_date, purchasedItem ) )
				
	
		toclear['__overthreshold__'] = overthreshold
		toclear['__earlythreshold__'] = earlythreshold

		return toclear

	def dumpStore(self):
		store={}
		totalQty=0
		totalCostPerUnit=0
		store['fermentables']={}
#		for (storeObject, storeQty,storeCost) in self.fermentables:
		for storeObject in self.Fermentables:
			storetype="fermentables"
			storeCost = 0 
			storeQty = 0
			for purchasedItem in self.Fermentables[ storeObject ]:
				storeCost = storeCost + purchasedItem.qty * purchasedItem.price
				storeQty = storeQty + purchasedItem.qty
			store[ storetype ][storeObject.name] = {}
			store[ storetype ][storeObject.name]['qtyAvaiable'] = storeQty
			store[ storetype ][storeObject.name]['unit'] = storeObject.unit
			if storeQty > 0:
				store[ storetype ][storeObject.name]['costPerUnit'] = storeCost/storeQty
			else:
				store[ storetype ][storeObject.name]['costPerUnit'] = 0
			store[ storetype ][storeObject.name]['purchases'] = []
			for purchasedItem in self.Fermentables[ storeObject ]:
				store[ storetype ][storeObject.name]['purchases'].append( {} )
				store[ storetype ][storeObject.name]['purchases'][-1]['best_before_date'] = purchasedItem.best_before_date
				store[ storetype ][storeObject.name]['purchases'][-1]['purchased_date'] = purchasedItem.purchase_date
				store[ storetype ][storeObject.name]['purchases'][-1]['cost'] = purchasedItem.price * purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['qty'] = purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['supplier'] = purchasedItem.supplier

				
			totalQty = totalQty + storeQty
			if storeQty > 0:
				totalCostPerUnit = totalCostPerUnit +(storeCost/storeQty)
			else:
				totalCostPerUnit = totalCostPerUnit +0

		store['fermentables']['__total__']={}
		store['fermentables']['__total__']['qtyAvailable'] = totalQty
		store['fermentables']['__total__']['unit'] = "gm"
		store['fermentables']['__total__']['costPerUnit'] = totalCostPerUnit
	
		totalQty=0
		totalCostPerUnit=0
		store['hops']={}
#		or (storeObject, storeQty,storeCost) in self.hops:
		for storeObject in self.Hops:
			storetype="hops"
			storeCost = 0 
			storeQty = 0
			for purchasedItem in self.Hops[ storeObject ]:
				storeCost = storeCost + purchasedItem.qty * purchasedItem.price
				storeQty = storeQty + purchasedItem.qty
			store[ storetype ][storeObject.name] = {}
			store[ storetype ][storeObject.name]['qtyAvaiable'] = storeQty
			store[ storetype ][storeObject.name]['unit'] = storeObject.unit
			store[ storetype ][storeObject.name]['costPerUnit'] = storeCost/storeQty
			store[ storetype ][storeObject.name]['purchases'] = []
			for purchasedItem in self.Hops[ storeObject ]:
				store[ storetype ][storeObject.name]['purchases'].append( {} )
				store[ storetype ][storeObject.name]['purchases'][-1]['best_before_date'] = purchasedItem.best_before_date
				store[ storetype ][storeObject.name]['purchases'][-1]['purchased_date'] = purchasedItem.purchase_date
				store[ storetype ][storeObject.name]['purchases'][-1]['cost'] = purchasedItem.price * purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['qty'] = purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['supplier'] = purchasedItem.supplier
				store[ storetype ][storeObject.name]['purchases'][-1]['stockTag'] = purchasedItem.stockTag
				
			totalQty = totalQty + storeQty
			totalCostPerUnit = totalCostPerUnit +(storeCost/storeQty)

		
		store['hops']['__total__']={}
		store['hops']['__total__']['qtyAvailable'] = totalQty
		store['hops']['__total__']['unit'] = "gm"
		store['hops']['__total__']['costPerUnit'] = totalCostPerUnit


		totalQty=0
		totalCostPerUnit=0
		store['yeast']={}
		#for (storeObject, storeQty,storeCost) in self.yeast:
		for storeObject in self.Yeast:
			storetype="yeast"
			storeCost = 0 
			storeQty = 0
			for purchasedItem in self.Yeast[ storeObject ]:
				storeCost = storeCost + purchasedItem.qty * purchasedItem.price
				storeQty = storeQty + purchasedItem.qty
			store[ storetype ][storeObject.name] = {}
			store[ storetype ][storeObject.name]['qtyAvaiable'] = storeQty
			store[ storetype ][storeObject.name]['unit'] = storeObject.unit
			if storeQty > 0:
				store[ storetype ][storeObject.name]['costPerUnit'] = storeCost/storeQty
			else:
				store[ storetype ][storeObject.name]['costPerUnit'] = 0
			store[ storetype ][storeObject.name]['purchases'] = []
			for purchasedItem in self.Yeast[ storeObject ]:
				store[ storetype ][storeObject.name]['purchases'].append( {} )
				store[ storetype ][storeObject.name]['purchases'][-1]['best_before_date'] = purchasedItem.best_before_date
				store[ storetype ][storeObject.name]['purchases'][-1]['purchased_date'] = purchasedItem.purchase_date
				store[ storetype ][storeObject.name]['purchases'][-1]['cost'] = purchasedItem.price * purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['qty'] = purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['supplier'] = purchasedItem.supplier
				store[ storetype ][storeObject.name]['purchases'][-1]['stockTag'] = purchasedItem.stockTag

				
			totalQty = totalQty + storeQty
			if storeQty > 0:
				totalCostPerUnit = totalCostPerUnit +(storeCost/storeQty)

		
		store['yeast']['__total__']={}
		store['yeast']['__total__']['qtyAvailable'] = totalQty
		store['yeast']['__total__']['unit'] = "pkt"
		store['yeast']['__total__']['costPerUnit'] = totalCostPerUnit


		totalQty=0
		totalCostPerUnit=0
		store['misc']={}
		for storeObject in self.Misc:
			storetype="misc"
			storeCost = 0 
			storeQty = 0
			for purchasedItem in self.Misc[ storeObject ]:
				storeCost = storeCost + purchasedItem.qty * purchasedItem.price
				storeQty = storeQty + purchasedItem.qty
			store[ storetype ][storeObject.name] = {}
			store[ storetype ][storeObject.name]['qtyAvaiable'] = storeQty
			store[ storetype ][storeObject.name]['unit'] = storeObject.unit
			if storeQty > 0:
				store[ storetype ][storeObject.name]['costPerUnit'] = storeCost/storeQty
			else:
				store[ storetype ][storeObject.name]['costPerUnit'] = 0
			store[ storetype ][storeObject.name]['purchases'] = []
			for purchasedItem in self.Misc[ storeObject ]:
				store[ storetype ][storeObject.name]['purchases'].append( {} )
				store[ storetype ][storeObject.name]['purchases'][-1]['best_before_date'] = purchasedItem.best_before_date
				store[ storetype ][storeObject.name]['purchases'][-1]['purchased_date'] = purchasedItem.purchase_date
				store[ storetype ][storeObject.name]['purchases'][-1]['cost'] = purchasedItem.price * purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['qty'] = purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['supplier'] = purchasedItem.supplier
				store[ storetype ][storeObject.name]['purchases'][-1]['stockTag'] = purchasedItem.stockTag

				
			totalQty = totalQty + storeQty
			if storeQty > 0:
				totalCostPerUnit = totalCostPerUnit +(storeCost/storeQty)
		
		store['misc']['__total__']={}
		store['misc']['__total__']['qtyAvailable'] = totalQty
		store['misc']['__total__']['unit'] = "pkt"
		store['misc']['__total__']['costPerUnit'] = totalCostPerUnit


		totalQty=0
		totalCostPerUnit=0
		store['consumable']={}
		#for (storeObject, storeQty,storeCost) in self.Consumables:
		for storeObject in self.Consumable:
			storetype="consumable"
			storeCost = 0 
			storeQty = 0
			for purchasedItem in self.Consumable[ storeObject ]:
				storeCost = storeCost + purchasedItem.qty * purchasedItem.price
				storeQty = storeQty + purchasedItem.qty
			store[ storetype ][storeObject.name] = {}
			store[ storetype ][storeObject.name]['qtyAvaiable'] = storeQty
			store[ storetype ][storeObject.name]['unit'] = storeObject.unit
			store[ storetype ][storeObject.name]['costPerUnit'] = storeCost/storeQty
			store[ storetype ][storeObject.name]['purchases'] = []
			for purchasedItem in self.Consumable[ storeObject ]:
				store[ storetype ][storeObject.name]['purchases'].append( {} )
				store[ storetype ][storeObject.name]['purchases'][-1]['best_before_date'] = purchasedItem.best_before_date
				store[ storetype ][storeObject.name]['purchases'][-1]['purchased_date'] = purchasedItem.purchase_date
				store[ storetype ][storeObject.name]['purchases'][-1]['cost'] = purchasedItem.price * purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['qty'] = purchasedItem.qty
				store[ storetype ][storeObject.name]['purchases'][-1]['supplier'] = purchasedItem.supplier
				store[ storetype ][storeObject.name]['purchases'][-1]['stockTag'] = purchasedItem.stockTag

				
			totalQty = totalQty + storeQty
			totalCostPerUnit = totalCostPerUnit +(storeCost/storeQty)
		
		store['consumable']['__total__']={}
		store['consumable']['__total__']['qtyAvailable'] = totalQty
		store['consumable']['__total__']['unit'] = "pkt"
		store['consumable']['__total__']['costPerUnit'] = totalCostPerUnit


		return store




	def _has_ingredient_in_store_by_name(self, dict1, strobj):
		"""
		Finds ingredient in store by name not object id
		"""
		X=None
		for x in dict1:
			if x.name == strobj:
				X=x
		return X

	def _has_ingredient_in_store(self, dict1, obj1):
		"""
		A workaround that checks for obj1 in dict1 by a deeper search (not an obj based search)
		we return true if the uid of the object supplied (obj) == uid of the object in the dict.

		"""
		X=None
		for x in dict1:
#			print "COMPARING",obj1.uid,x.uid
			if obj1.uid == x.uid:
				X=x
		return X



	def jsonStockAndPrice(self,recipe):
		(cost,stock) = self.checkStockAndPrice(recipe)

		COST={}
		STOCK={}
		for c in cost:
#			print "c",c,"=",cost[c]
			if c == "__total__":
				COST[c] = cost[c]
			else:
				COST[c] = {}
				for C in cost[c]:
					if C == "__total__":	
						CC=C
					else:
						(CB,CC) = C
						COST[c][CC] = cost[c][C]
		for s in stock:
#			print "s",s,"=",stock[s]
			if s == "__total__":
				STOCK[s] = stock[s]
			if s == "__out_of_stock__":
				STOCK[s] = []
				for (sx,sy) in stock[s]:	STOCK[s].append(sy)
			else:
				STOCK[s] = {}
				for S in stock[s]:
#					print "S",S,"s",s
					if S == "__total__":
						SS=S
					else:
						(SR,SS) = S
						STOCK[s][SS] = stock[s][S]
		return {'cost': COST,
			  'stock' : STOCK,}
		

	def checkStockAndPrice(self, recipe):
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
		total_cost=0		



		cost_result['ingredients'] = {}
		cost_result['ingredients']['__total__'] = 0	
		stock_result['ingredients'] = {}
		stock_result['ingredients']['__total__'] = 0



		if recipe.validprocess:
			for activity in recipe.process.activities:
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






		# Started to condense
		for (costType,dict1,dict2) in [ ('fermentables',recipe.fermentables, self.Fermentables), ('hops',recipe.hops, self.Hops) , ('yeast',recipe.yeast,self.Yeast),('misc',recipe.misc,self.Misc) ]:
			cost_result[ costType ] = {}
			cost_result[ costType ]['__total__'] = 0	
			stock_result[ costType ] = {}
			stock_result[ costType ]['__total__'] = 0	
					#dict1 ==> self.fermentables, self.hops, self.yeast, self.misc
							# (i.e. our recipe bits and pieces
					
			for (obj,qty) in dict1:
				haveStock = self._has_ingredient_in_store( dict2, obj )
									# dict2 ==> self.Fermentables, self.Hops etc
			
				if not haveStock:
					storeQty=0	
				else:
					# Now we are going to have average out the cost over all purchases
					storeQty = 0
					storeCost = 0
					for purchasedItem in dict2[ haveStock ]:	
						storeQty = storeQty + purchasedItem.qty
						storeCost = storeCost + purchasedItem.price * purchasedItem.qty
					if storeQty > 0:
						cost_per_unit = storeCost/storeQty
					else:
						cost_per_unit = 0
					cost_for_ingredient = qty * cost_per_unit
					cost_result[ costType ]['__total__'] = cost_result[ costType ]['__total__'] + cost_for_ingredient
					cost_result[ costType ][ haveStock.uid ] = cost_for_ingredient
					if storeQty > 0:
						stock_result['__pcnt_left__'][ haveStock.uid ] = 1 - (qty / storeQty)
					else:
						stock_result['__pcnt_left__'][ haveStock.uid ] = 1 - 0
					stock_result['__qty_available__'][ haveStock.uid ] = storeQty
					stock_result['__qty_required__'][ haveStock.uid ] = qty

				
					stock_result[ costType ][ haveStock.uid ] = qty
					stock_result[ costType ]['__total__'] = stock_result[ costType ]['__total__'] + qty

					if qty > storeQty:
						stock_result['__pcnt_left__'][ haveStock.uid ] = 0
						stock_result['__out_of_stock__'].append( haveStock.uid )
						stock_result['__qty_available__'][ haveStock.uid ] = storeQty
						stock_result['__qty_required__'][ haveStock.uid ] = qty

			total_cost = total_cost + cost_result[ costType ]['__total__']



		# Process Costing
		cost_result['consumables'] = {}
		cost_result['consumables']['__total__'] = 0	
		stock_result['consumables'] = {}
		stock_result['consumables']['__total__'] = 0

		if recipe.validprocess:
			for activity in recipe.process.activities:
				for (consumable,qty) in activity.consumables:
					haveStock = self._has_ingredient_in_store( self.Consumable, consumable )

					if not haveStock:
						storeQty=0
					else:
						storeQty = 0
						storeCost = 0 

						for purchase in self.Consumable[ haveStock ]:
							storeQty = storeQty + purchase.qty
							storeCost = storeCost + purchase.price
						if storeQty > 0:
							cost_per_unit = storeCost / storeQty
						else:
							cost_per_unit = 0

						cost_for_consumable = qty * cost_per_unit
						cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + cost_for_consumable
						cost_result['consumables'][ consumable.uid ] = cost_for_consumable
						if storeQty > 0:
							stock_result['__pcnt_left__'][ consumable.uid ] = 1-(qty/storeQty)
						else:
							stock_result['__pcnt_left__'][ consumable.uid ] = 1-0
						stock_result['__qty_available__'][ consumable.uid ] = storeQty
						stock_result['__qty_required__'][ consumable.uid ] = qty


					stock_result['consumables'][ consumable.uid ] = qty
					stock_result['consumables']['__total__'] = stock_result['consumables']['__total__'] + qty

					if qty > storeQty:
						stock_result['__pcnt_left__'][ consumable.uid ] = 0
						stock_result['__out_of_stock__'].append( consumable.uid )
						stock_result['__qty_available__'][ consumable.uid ] = storeQty
						stock_result['__qty_required__'][ consumable.uid ] = qty
		

		
		# repeat bottle stock checking
		# this is a clone of the implementation in takeStock but re-purposed
		# for checkStockAndPrice
		bottle_volume_required = (recipe.batch_size_required * 1000)

		total_bottles = 0

		bottle_vols = []
		for purchasedItem in self.Consumable:
			if purchasedItem.category == "bottle":
			
				bottle_vols.append( ( purchasedItem.volume, purchasedItem ) )
		bottle_vols.sort()
		bottle_vols.reverse()
		
		for (vol,bottle) in bottle_vols:
			qtyAvailable = 0
			qtyRequired = 0
			for purchase in self.Consumable[bottle]:
				qtyAvailable = qtyAvailable + purchase.qty
				if purchase.qty > 0 and bottle_volume_required > 0:					
					if (purchase.qty * vol) > bottle_volume_required:
						qtyNeeded =math.ceil( bottle_volume_required / vol )
					else:
						qtyNeeded = purchase.qty
					if not cost_result['consumables'].has_key(bottle.uid):	
						cost_result['consumables'][bottle.uid] =0
					cost_result['consumables'][ bottle.uid ] = cost_result['consumables'][ bottle.uid ] + (purchase.price * qtyNeeded)
					cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.price * qtyNeeded)

					bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )
					qtyRequired = qtyRequired + qtyNeeded
		
					total_bottles = total_bottles + qtyNeeded

		# if we don't have enough stock of bottles we will ask based on the last tbottle in the list
		# if this is a tiny bottle this will be odd,... but variabile  volume bottles isn't perfect
		# if we have multiple types of bottles we don't ask for the full volume, we only ask for the 
		# missing bit
		if bottle_volume_required > 0:
			stock_result['__pcnt_left__'][ bottle.uid ] = 0
			stock_result['__out_of_stock__'].append( bottle.uid )
			stock_result['__qty_available__'][ bottle.uid ] = qtyAvailable
					# this next calculation is the excess, but we have qtyRequired adding up
					# as we go along
			stock_result['__qty_required__'][ bottle.uid ] = math.ceil(bottle_volume_required / vol ) + qtyRequired
			### out of stock


		# Now do crown caps
		total_caps = total_bottles  + 4
		qtyRequired = 0 
		qtyAvailable = 0
		for bottlecap in self.Consumable:
			if bottlecap.category == "bottlecaps":
				for purchase in self.Consumable[ bottlecap ]:
					qtyAvailable = qtyAvailable + purchase.qty
					if purchase.qty > 0 and total_caps > 0:
						if purchase.qty > total_caps:
							qtyNeeded= total_caps
						else:
							qtyNeeded = purchase.qty
						if not cost_result['consumables'].has_key( bottlecap.uid ):
							cost_result['consumables'][ bottlecap.uid ] = 0
						cost_result['consumables'][ bottlecap.uid ] = cost_result['consumables'][ bottlecap.uid ] + (purchase.price * qtyNeeded)
						cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.price * qtyNeeded)
						total_caps = total_caps - qtyNeeded
						qtyRequired = qtyRequired + qtyNeeded

		if total_caps > 0:
			stock_result['__pcnt_left__'][ bottlecap.uid ] = 0
			stock_result['__out_of_stock__'].append( bottlecap.uid )
			stock_result['__qty_available__'][ bottlecap.uid ] = qtyAvailable
			stock_result['__qty_required__'][ bottlecap.uid ] = qtyRequired
	

		# And priming sugar
		if recipe.process.priming_sugar:
			priming_sugar_reqd = (total_bottles + 5) * recipe.priming_sugar_qty 
			qtyRequired=0
			qtyAvailable
			for primingsugar in self.Consumable:
				if primingsugar.category == "primingsugar":
					for purchase in self.Consumable[ primingsugar ]:
						qtyAvailable = qtyAvailable + purchase.qty
						if purchase.qty	> 0 and priming_sugar_reqd > 0:
							qtyNeeded = priming_sugar_reqd
						else:
							qtyneeded = purchase.qty
						if not cost_result['consumables'].has_key( primingsugar.uid ):
							cost_result['consumables'][ primingsugar.uid ] = 0
						cost_result['consumables'][ primingsugar.uid ] = cost_result['consumables'][ primingsugar.uid ] + (purchase.price * qtyNeeded)
						cost_result['consumables']['__total__'] = cost_result['consumables']['__total__'] + (purchase.price * qtyNeeded)
						priming_sugar_reqd = priming_sugar_reqd - qtyNeeded
						qtyRequired = qtyRequired + qtyNeeded

			if priming_sugar_reqd > 0:
				stock_result['__pcnt_left__'][ primingsugar.uid ] = 0
				stock_result['__out_of_stock__'].append( primingsugar.uid )
				stock_result['__qty_available__'][ primingsugar.uid ] = qtyAvailable
				stock_result['__qty_required__'][ primingsugar.uid ] = qtyRequired
					


		return (cost_result,stock_result)


	def takeStock(self, recipe):
		"""
		given a brwlabRecipe object a list of stockTag's focusing on returning the oldest stock
		first. 
		The algorithim takes into account minimum quantities (i.e. bottled water)

		If the stock for the whole recipe can't be fullfiled from stores a blank dict is 
		returned.

		Additionally if *any* stock is marked as near it's expiry date then a blank dict is 
		returned.
		
		"""

		self.calclog=""
		# use checkStockAndPrice 	
		(cost_result,stock_result) = self.checkStockAndPrice(recipe)


		
		if len(stock_result['__out_of_stock__']) > 0:
			print """*******
	
		
			EXCEPTION/WARNING: OUT OF STOCK



			****"""
			for x in stock_result["__out_of_stock__"]:	print x
			return {}


		toclear = self.listClearanceStock()
		if toclear['__overthreshold__'] > 0 or toclear['__earlythreshold__'] > 0:
#			print toclear['__overthreshold__']
#			print toclear['__earlythreshold__']
#			print toclear
			print """*******
	
		
			EXCEPTION/WARNING: OUT OF DATE/THRESHOLD



			****"""
			return {}

		stock_result= {}

		stock_result = self._stockBestBefore(stock_result, "fermentables", recipe.fermentables, self.Fermentables )
		stock_result = self._stockBestBefore(stock_result, "hops", recipe.hops, self.Hops)
		stock_result = self._stockBestBefore(stock_result, "yeast", recipe.yeast, self.Yeast)
		stock_result = self._stockBestBefore(stock_result, "misc", recipe.misc, self.Misc)

		# For consumables we don't really need to have  best before ordering, but 
		# it won't hurt
		for activity in recipe.process.activities:
			# stockBestBefore ignores bottles
			stock_result = self._stockBestBefore(stock_result, "consumables", activity.consumables, self.Consumable)

			# intelligentBottle
			# look out for "Gather Bottles" step and find bottles
			# this is going to have to double up checkStockAndPrice somehow
			enableIntelligentBottle=0
			enableIntelligentKeg=0
			for step in activity.steps:
				if step.auto == "gather2":
					enableIntelligentBottle = 1
				if step.auto == "gather3":
					enableIntelligentKeg = 1
			
			# The checking of the steps is only 
			bottle_volume_required = (recipe.batch_size_required * 1000)
			keg_priming_sugar = 0
			bottle_priming_sugar =0
			total_keg_volume=0

			if enableIntelligentKeg:
				# for kegs we will prefer the smallest kegs instead of the 
				# largest kegs
				keg_vols = []
				for purchasedItem in self.Consumable:
					if purchasedItem.category == "keg":
						keg_vols.append( ( purchasedItem.volume, purchasedItem ) )
				keg_vols.sort()

#
				self.calclog = self.calclog + "kegfilling: keg_vols %s\n" %(keg_vols)
				total_kegs=0					
				for (vol,keg) in keg_vols:
					self.calclog = self.calclog + "kegfilling: %s ml from keg type %s\n" %(vol,keg.name)
					self.calclog = self.calclog + "kegfilling: volume left to keg %s ml\n" %(bottle_volume_required)
					for purchase in self.Consumable[keg]:
						self.calclog = self.calclog + "kegfilling: purchase.qty %s\n"%(purchase.qty)
						if purchase.qty > 0 and bottle_volume_required > 0:
							if not stock_result['consumables'].has_key(keg.name):
								stock_result['consumables'][ keg.name ] = []	

							if (purchase.qty * vol) > bottle_volume_required:

								total_keg_volume = total_keg_volume + vol
								qtyNeeded =math.ceil( bottle_volume_required / vol )
										
								stock_result['consumables'][ keg.name ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stockTag, purchase.purchasedItem, purchase) )
								purchase.qty = purchase.qty - qtyNeeded
							else:
								total_keg_volume = total_keg_volume + vol
								qtyNeeded = purchase.qty
								stock_result['consumables'][ keg.name ].append( (1 , qtyNeeded, purchase.stockTag, purchase.purchasedItem, purchase) )
								purchase.qty = 0


							# datauplift
							if not keg.__dict__.has_key("caprequired"):	keg.caprequired=0
							if not keg.__dict__.has_key("co2required"):	keg.co2required=1

							total_kegs=total_kegs+qtyNeeded
#							if bottle.caprequired:	bottle_caps_required = bottle_caps_required + qtyNeeded
							bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )

				self.kegs_required= total_kegs
				self.calclog = self.calclog + "kegfilling: total_kegs %s\n" %(total_kegs)
				TOTAL_KEGS=total_kegs
			
				for co2 in self.Consumable:
					if co2.category == "co2":
						for purchase in self.Consumable[ co2 ]:
							if purchase.qty > 0 and total_kegs > 0:
								if not stock_result['consumables'].has_key( co2.name ):
									stock_result['consumables'][ co2.name ] = []
								if (purchase.qty) > total_kegs:	# need a proportion
									stock_result['consumables'][ co2.name ].append( ( total_kegs/purchase.qty, total_kegs, purchase.stockTag, purchase.purchasedItem, purchase ) )
									purchase.qty = purchase.qty - total_kegs
									total_kegs = 0 
								else:		# meed all this purchase
									stock_result['consumables'][ co2.name ].append( (1, purchase.qty, purchase.stockTag, purchase.purchasedItem, purchase) )
									total_kegs = total_kegs - purchase.qty
									purchase.qty = 0

				#  priming sugar
				# note; priming sugar in recipe is against a 500ml bottle size
				# so we need to convert into a value per ml per to be able to use
				priming_sugar_reqd = (total_keg_volume) * ((recipe.priming_sugar_qty * 2)/1000)
				self.calclog=self.calclog+"kegfilling: total keg volume filled %.2f in %s kegs\n" %(total_keg_volume,TOTAL_KEGS)
				self.calclog=self.calclog+"kegfilling: priming sugar required for kegs %.3f\n" %(priming_sugar_reqd)
				keg_priming_sugar = priming_sugar_reqd
				#for primingsugar in self.Consumable:
				#	if primingsugar.category == "primingsugar":
				#		for purchase in self.Consumable[ primingsugar ] :
				#			if purchase.qty > 0 and priming_sugar_reqd > 0:
				#				if not stock_result['consumables'].has_key( primingsugar.name):
				#					stock_result['consumables'][ primingsugar.name ] = []
				#				if (purchase.qty) > priming_sugar_reqd:
				#					stock_result['consumables'][ primingsugar.name ].append( (priming_sugar_reqd/purchase.qty, priming_sugar_reqd, purchase.stockTag, purchase.purchasedItem, purchase ))
				#					purchase.qty = purchase.qty - priming_sugar_reqd
				#					priming_sugar_reqd = 0
				#				else:
				#					stock_result['consumables'][ primingsugar.name ].append( (1,purchase.qty, purchase.stockTag, purchase.purchasedItem, purchase) )
				#					priming_sugar_reqd = priming_sugar_reqd - purchase.qty
				#					purchase.qty = 0
				
				






			if enableIntelligentBottle:					
				total_bottle_volume=0

				# sort bottles in order of size. This is to allow us to have
				# different volume bottles. We can't specify to use a range
				# of different volumes... the algorithim here sorts by largest
				# bottles first. If the store quantities are manipulated 	
				# would get the behaviour
				bottle_vols = []
				for purchasedItem in self.Consumable:
					if purchasedItem.category == "bottle":
						bottle_vols.append( ( purchasedItem.volume, purchasedItem ) )
				bottle_vols.sort()
				bottle_vols.reverse()
#
				# Now get crown caps
				bottle_caps_required = 0
				
				self.calclog = self.calclog + "bottlebank: bottle_vols %s\n" %(bottle_vols)
				total_bottles=0					
				for (vol,bottle) in bottle_vols:
					self.calclog = self.calclog + "bottlebank: %s ml from bottle type %s\n" %(vol,bottle.name)
					if vol > 515 or vol < 472:
						self.calclog = self.calclog + "\n\n\nWARNING\nbottlebank: priming sugar calculations based on 500ml bottle volume\n"
					self.calclog = self.calclog + "bottlebank: volume left to bottle %s ml\n" %(bottle_volume_required)
					for purchase in self.Consumable[bottle]:
#						self.calclog = self.calclog + "bottlebank: purchase.qty %s\n"%(purchase.qty)
						if purchase.qty > 0 and bottle_volume_required > 0:
							if not stock_result['consumables'].has_key(bottle.name):
								stock_result['consumables'][ bottle.name ] = []	

							if (purchase.qty * vol) > bottle_volume_required:

								qtyNeeded =math.ceil( bottle_volume_required / vol )
										
								stock_result['consumables'][ bottle.name ].append( (qtyNeeded/ purchase.qty, qtyNeeded, purchase.stockTag, purchase.purchasedItem, purchase) )
								purchase.qty = purchase.qty - qtyNeeded
								total_bottle_volume = total_bottle_volume = qtyNeeded
							else:
								qtyNeeded = purchase.qty
								stock_result['consumables'][ bottle.name ].append( (1 , qtyNeeded, purchase.stockTag, purchase.purchasedItem, purchase) )
								total_bottle_volume = total_bottle_volume = purchase.qty
#									print stock_result['consumables'][bottle]
								purchase.qty = 0


							# datauplift
							if not bottle.__dict__.has_key("caprequired"):	bottle.caprequired=1
							if not bottle.__dict__.has_key("co2required"):	bottle.co2required=0


							total_bottles = total_bottles + qtyNeeded 
							if bottle.caprequired:	bottle_caps_required = bottle_caps_required + qtyNeeded
							bottle_volume_required = bottle_volume_required - (qtyNeeded * vol )

				self.bottles_required= total_bottles
				self.calclog = self.calclog + "bottlebank: total_bottles = %s\n" %(total_bottles)
				TOTAL_BOTTLES=total_bottles

				for bottlecap in self.Consumable:
					if bottlecap.category == "bottlecaps":
						for purchase in self.Consumable[ bottlecap ]:
							if purchase.qty > 0 and bottle_caps_required > 0:
								if not stock_result['consumables'].has_key( bottlecap.name ):
									stock_result['consumables'][ bottlecap.name ] = []
								if (purchase.qty) > bottle_caps_required:	# need a proportion
									stock_result['consumables'][ bottlecap.name ].append( ( bottle_caps_required/purchase.qty, bottle_caps_required, purchase.stockTag, purchase.purchasedItem, purchase ) )
									purchase.qty = purchase.qty - bottle_caps_required
									bottle_caps_required = 0
								else:		# meed all this purchase
									stock_result['consumables'][ bottlecap.name ].append( (1, purchase.qty, purchase.stockTag, purchase.purchasedItem, purchase) )
									bottle_caps_required = bottle_caps_required - purchase.qty
#										print "bottlecapsrequired = bottle_cpas_required -",purchase.qty,bottle_caps_required
									purchase.qty = 0



				# note recipe is fixed assumption of 500ml
				priming_sugar_reqd = (total_bottles + 5) * recipe.priming_sugar_qty 
				self.calclog=self.calclog+"bottlebank: total bottle volume filled %.2f in %s bottles\n" %(total_bottle_volume,TOTAL_BOTTLES)
				self.calclog=self.calclog+"bottlebank: priming sugar required for bottles %.3f\n" %(priming_sugar_reqd)
				keg_priming_sugar = priming_sugar_reqd





			if enableIntelligentBottle or enableIntelligentKeg:					
				#  priming sugar
				priming_sugar_reqd = keg_priming_sugar + bottle_priming_sugar
				for primingsugar in self.Consumable:
					if primingsugar.category == "primingsugar":
						for purchase in self.Consumable[ primingsugar ] :
							if purchase.qty > 0 and priming_sugar_reqd > 0:
								if not stock_result['consumables'].has_key( primingsugar.name):
									stock_result['consumables'][ primingsugar.name ] = []
								if (purchase.qty) > priming_sugar_reqd:
									stock_result['consumables'][ primingsugar.name ].append( (priming_sugar_reqd/purchase.qty, priming_sugar_reqd, purchase.stockTag, purchase.purchasedItem, purchase ))
									purchase.qty = purchase.qty - priming_sugar_reqd
									priming_sugar_reqd = 0
								else:
									stock_result['consumables'][ primingsugar.name ].append( (1,purchase.qty, purchase.stockTag, purchase.purchasedItem, purchase) )
									priming_sugar_reqd = priming_sugar_reqd - purchase.qty
									purchase.qty = 0
				





		
#		for x in stock_result['consumables']:
#			print x
#			for y in stock_result['consumables'][x]:
#				print " ",y
#			print ""
		return stock_result



	def _stockBestBefore(self, stock_result, stockType, RECIPE, US, dummyAllocate=0):
		"""
		Internal method which takes the stock with the oldest best before date
		This method also takes into account a fixed wasted factor/percentage

		dummyAllocate does 2 things, 1st it doesn't actually allocate and
		2nd it will x10'd the qty required. The use case for dummyAllocate
		is hops of different alphas.
		"""


		if not stock_result.has_key( stockType ):
			stock_result[ stockType ] = {}


		for (ITEM,qty) in RECIPE:	# RECIPE is recipe.fermentables, recipe.hops etc
						# RECIPE could also be activity.consumables

#			print "before", ITEM,ITEM.name
			haveStock = self._has_ingredient_in_store( US,  ITEM)

#			print "haveStock",haveStock
#
#			if dbg:	print "hhdbg",haveStock
			if not haveStock:
#US.has_key( ITEM ):
				# let's call this out because it has been needed
				print """
				***********************************************************************************************


	
			
				brewerslabEngine Exception in _stockBestBefore
				unable to find the stock we needed and this is a bad way to
				deal with it





				***********************************************************************************************
				"""
				return {}	# should not be needed
			else:
			

				if ITEM.category != "bottle" and ITEM.category != "bottlecaps":

					qtyNeeded = qty
					# A future improvement might attempt to use whole bags rather than
					# cause leaving opened packets.
					best_before_dates_obj = {}
					best_before_dates = []
	#				if dbg:	print "hhdbg",US[haveStock]

					for purchasedItem in US[ haveStock ]:
	#					if dbg:	print "hhdbg",purchasedItem.supplier.name,purchasedItem.qty,time.ctime(purchasedItem.best_before_date)
						if not best_before_dates_obj.has_key( purchasedItem.best_before_date ):
							best_before_dates_obj[ purchasedItem.best_before_date ] = []
							best_before_dates.append( purchasedItem.best_before_date )
						best_before_dates_obj[ purchasedItem.best_before_date].append( purchasedItem )
					
	#				if dbg:	print "hhdbg",best_before_dates
					
					# soonest best before end date first
					best_before_dates.sort()

					#uMake the qty required tenfold as we would really like to know 
					# how muct we can adjust up to.
					if dummyAllocate:	qtyNeeded = qtyNeeded * 100

					for best_before_date in best_before_dates:
						for item in best_before_dates_obj[ best_before_date ]:	
								
							if item.qty > 0 and qtyNeeded >0:
								if not stock_result[ stockType ].has_key( item.purchasedItem.name ):
									stock_result[ stockType ][ item.purchasedItem.name ] = []	

								if item.qty > qtyNeeded:
									stock_result[ stockType ][ item.purchasedItem.name ].append( (qtyNeeded/item.qty,qtyNeeded, item.stockTag, item.purchasedItem, item) )
									# If we need multiple quantities then we won't do wastage
									# assumption is that the multiple qty is set appropriately.
									# item qty multiple thingy?
									if item.purchasedItem.qty_multiple != 1:	
										qtyUsed = math.ceil( qtyNeeded / item.purchasedItem.qty_multiple ) * item.purchasedItem.qty_multiple

										if not dummyAllocate:
											item.qty= item.qty - qtyUsed
										#item.qty= item.qty - qtyNeeded
									else:
									# Check the wastage in this step.
										if not dummyAllocate:
											item.qty= item.qty - qtyNeeded
											item.qty= item.qty - item.purchasedItem.wastage_fixed
											if item.qty < 0:	item.qty = 0
										
									qtyNeeded = 0
								else:
									# This is a full use of the item in stock
									# therefore we do't introduce wastage
									qtyNeeded = qtyNeeded - item.qty
									stock_result[ stockType ][ item.purchasedItem.name ].append( (1,item.qty, item.stockTag,item.purchasedItem,item) )
									if not dummyAllocate:
										item.qty = 0
						

		return stock_result




class brwlabPurchase:
	"""
	A wrapper to combine purchase information
	An old stores.add() can be converted
		i.e.	stores.addPurchase( brwlabPurchase(sterilisingPowder, 80, 0.0595) )

	

	"""

	def __init__(self, purchasedItem,qty=1,price=1):
		self.purchasedItem = purchasedItem
		self.version=0.2
		self.qty=qty				# in unitsof purcahsedItem
		self.price=price			# in pounds
		self.supplier=None
		self.best_before_date = time.mktime( time.localtime(time.time()+1000*86400) )
		self.purchase_date=time.mktime( time.localtime() )

		# especially for hops
		self.hop_actual_alpha = -1
		self.hop_aged_alpha = -1

		#
		self.storage = [ (0,0,20) ] 
				# list of storage properties which might be used for hop aging
				# each entry will represent a change in storage qualities
				# the tuple is:
					# date  	# seconds since epoch,
							# assume that in implementation that use this 0 will be interpreted as purchase date
					# airtight 	# boolean
					# temp		## storage 

	def purchaseDate(self,purchasedate):
		self.purchase_date = time.mktime( time.strptime( purchasedate, "%Y-%m-%d") )

	def bestBeforeDate(self,bestbeforedate):
		self.best_before_date = time.mktime( time.strptime( bestbeforedate, "%Y-%m-%d") )

	def dump(self):
		print "Purchase %s (%s)" %(self.purchasedItem.name, self)
		print "Purchase Data", time.ctime( self.purchase_date )
		print "Best Before", time.ctime( self.best_before_date)
		print "Price ", self.price
		print "Qty ", self.qty

	
	def _upgrade(self):
		print "self.upgrade is called",self.version
		if self.version < 0.2:
			print "old version is ",self.version
			print "need to upgrade"

class brewdayTrio:

	def __init__(self):
		self.a=""



class brwlabTools:

	def __init__(self):
		"""	tools 	"""

	def mixTemp(self, weight1,temp1,weight2,temp2):
		"""
		Mix Temp
		returns the final temperature of water given two voulmes of water at different temperatures
(1*4182*20+0.3*4182*9c)/(1*4182+0.3*4182) = 17.461 Degrees Celsius.

		"""
#		newTemp =( weight1 * 4182 * temp1 + weight2 * 4182 * temp2 ) / ( weight1 * 4182 + weight2 * 4182 )
		newTemp =( weight1 * temp1 + weight2 * temp2 ) / ( weight1 + weight2 )
		return newTemp

	def requiredVol(self,weight1,temp1,temp2,temp3):
		"""
		requiredVol
		returns the volume of water (weight2) at temp2 to reach a given temp3
		when there is already a volume of water at temp1
		"""

		newTemp =( weight1 * temp1 + weight2 * temp2 ) / ( weight1 + weight2 )
		

		addition = 0
		newTemp =( weight1 * temp1 + addition * temp2 ) / ( weight1 + addition )
		print newTemp,"<",temp3
		while newTemp < temp3:
			if temp3 > newTemp * 0.99 and temp3 < newTemp *1.001:	return addition
			addition=addition+0.1
			newTemp =( weight1 * temp1 + addition * temp2 ) / ( weight1 + addition )

		
class brwlabSupplier:
	def __init__(self,name=None):
		self.name=None
		self.version=0.1
		if name:	self.name=name
		self.url=None




class brwlabBrewlog:

	def __init__(self,copyprocess,copyrecipe):
		self.version=0.1
		self.process = copyprocess.name
		self.recipe = copyrecipe.name
		self.copyprocess=copyprocess
		self.copyrecipe=copyrecipe
		self.process_sig = hashlib.sha1( self.process ).hexdigest()
		self.recipe_sig = hashlib.sha1( self.recipe ).hexdigest()
		self.stock = None
		self.started=0
		self.filename="dummy"				
			
		self.completes = {}
		self.notes={}

#		self.checkCompletes( self.copyprocess )
		for activity in self.copyprocess.activities:
			for step in activity.steps:
				self.completes[ step.uniqueid ] = { 'completed' : 0, 'ourref' : step, 'startTime' :0 , 'endTime' : 0} 
				for (littlestep,stepparam) in step.content:
					self.completes[ stepparam['uniqueid'] ] = { 'completed' : 0, 'parentref' : step, 'startTime' :0 , 'endTime' : 0} 



	def save(self):
		# We might need to create some directories
		fd = self.filename.split("/")
		f=fd.pop()
		fddd=""
		for fdd in fd:
			fddd="%s%s/" %(fddd, re.compile("[^a-zA-Z0-9]").sub('_',fdd))
			try:
				os.mkdir(fddd)
			except:
				pass
		# now save the files
		fddd="%s/%s" %(fddd,re.compile("[^a-zA-Z0-9]").sub('_',f))

		print "SAVE"
		print self	
		for x in self.__dict__:
#			print x,self.__dict__[x]
			print x

		print self.name
		print self.recipe_sig
		print self.copyrecipe
		print self.process	
		print self.notes
		print self.recipe
		print self.copyprocess


		self.copyrecipe.addFermentable=None
		self.copyrecipe.addYeast=None
		self.copyrecipe.addHop=None
		

		o=open(fddd,"w")
		o.write(pickle.dumps(self))
		o.close()


	def checkCompletes(self,process):
		for activity in process.activities:
			for step in activity.steps:
				if not self.completes.has_key( step.uniqueid ):
					self.completes[ step.uniqueid ] = { 'completed' : 0, 'ourref' : step, 'startTime' :0 , 'endTime' : 0} 
				for (littlestep,stepparam) in step.content:
					if not self.completes.has_key( stepparam['uniqueid'] ):
						self.completes[ stepparam['uniqueid'] ] = { 'completed' : 0, 'parentref' : step, 'startTime' :0 , 'endTime' : 0} 



