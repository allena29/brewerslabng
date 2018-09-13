
class calculatev1:

	def __init__(ourself,self):
		self=self

		print self,"inside calculatev1"
		a=1
		self.hops_by_avg_alpha = {}
		self.hops_by_contribution={}
		"""
			This is a copy/paste of brewerslabEngine.py with small modifications to 
			use Gql Datastore as opposed to pickles

			Need to decide what to do longterm with this, suspect we will keep this version longterm.
			Matches: 2011-09-14 (svn revi 2 : 2011-12-07 20:16:14 +0000

			
		"""

	
		ourContributions = self.dbWrapper.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2", username,recipeName)
		for x in ourContributions.fetch(2000):
			x.delete()

		ourRecipe = self.dbWrapper.GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeName)
		recipe=ourRecipe.fetch(1)[0]
		self.recipe=recipe
		if len(recipe.process) < 1:
			return "Cannot calculate because we don't know which process to use"

		ourProcess = self.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3",username,recipe.process,-1)
		process=ourProcess.fetch(1)[0]
		self.Process=process		# rename this later from Process to process.
						# but for now leave as is so we can more easily merge code
		

		self.calclog = ""
		#pickle:self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(self.process.name)
		#gqlself.calclog = self.calclog + "process  : Calculating with Process %s\n" %(revcipe.process)
		self.calclog = self.calclog + "process  : Calculating with Process %s\n" %(recipe.process)	#pickql
		self.calclog = self.calclog + "process  : brewerslabEngine rev 2013-05-23\n"
		self.calclog = self.calclog + "process  : changes sinec 2012-10-09\n"
		self.calclog = self.calclog + "process  :  - start of standalone mode to run without sql database\n"
		self.calclog = self.calclog + "process  :  - tweak of batch size for gravity calculations\n"
		self.calclog = self.calclog + "process  :    (25%% of mash tun deadspace included)\n"

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
		ourFermentables = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4", username,recipeName,'fermentables',0)
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
			cont.db=self.dbWrapper
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
		ourHops = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4 AND hopAddAt > :5", username,recipeName,'hops',0,-1.00)
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

		ourFermentables = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4", username,recipeName,'fermentables',0)
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
				cont.db=self.dbWrapper
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
			sys.stderr.write("%s %s\n" %(fermentable,fermentable.ingredient))
			sys.stderr.write("\n")
		
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

		self.fermgrainfermnongrain = (1.23 * (fermentable_grain + fermentable_nongrain))
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
		ourYeasts = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4", username,recipeName,'yeast',0)
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

		ourYeasts = self.dbWrapper.GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND processIngredient = :4", username,recipeName,'yeast',0)
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



