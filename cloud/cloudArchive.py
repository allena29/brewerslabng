#MIDGRAVS WAS HERE
		################################### BELOW IS MID GRAVS
		if "midgrav" == "disabled":
			self.calclog = self.calclog + "midgrav  : EXPERIMENTAL MID GRAVITY\n"
			if not self.standalonemode:
				self.boilers = self._getEquipment(username,recipe.process,"boiler",True)
			self.calclog = self.calclog + "midgrav  : EXPERIMENTAL MID GRAVITY\n"
			self.calclog = self.calclog + "midgrav  : working_boil_volume (batch_size_D) = %.2f\n" %(working_batch_size_D)
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
				#sys.stderr.write(boilIteration)
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

		#################################### ABOVE IS	


# MIDGRAV2 WAS HERE
		if "midgrav" == "disabled":
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


			try:
				self.kettle1preboilgravity = 1+(MIDGRAVS[0][2]/1000)
				self.kettle1volume = MIDGRAVS[0][0]
			except:
				self.kettle1preboilgravity=-666
				self.kettle1volume=-666
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

			self.kettle1kettle2volume=self.kettle1volume+self.kettle2volume
			self.kettle1kettle2kettle3volume=self.kettle1volume+self.kettle2volume+self.kettle3volume




###### 
	def watXXXerRequirement(self,adjustment=0):
		"""
		Calculates the water requirement.


		"""
		print "doweuserthis... I don't think we do"
		sys.exit(324234)
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
		
		self.kettle1evaporation=extra_water



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






	def combineGravity(self,vol1,vol2,grav1,grav2,title="cmbgrav  :"):
		totalvol=vol1+vol2
		g1 = (vol1/totalvol) * grav1
		g2 = (vol2/totalvol) * grav2

		self.calclog = self.calclog + "%s:  %.1f of %.4f + %.1f of %.4f = %.4f\n" %(title,vol1,1+(grav1/1000),vol2,1+(grav2/1000), 1+((g1+g2)/1000))
		return g1+g2






	def XXXcalculateMidGravity(self,estimated_gravity,start,finish):

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






