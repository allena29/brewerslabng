import pickle
from ngData import *


class standaloneTool:

	def __init__(self):
		self.st=1
		self.db=None
		# should we statically import a pickle?
		# given we imported the pickles - to Gql 
		# and then converted the gql to mysql
		# we probably should.


	def importProcess(self,fileName):
		p = pickle.loads( open(fileName).read() )
		process=p.name
		owner="standalone"

		# no need to delete as we aren't persistent
		"""
		records = self.db.GqlQuery("SELECT FROM gCompileText WHERE owner = :1 AND process = :2",owner,process)
		for record in records.fetch(2342344):	record.delete()
		"""

		subrequired = re.compile("\.\.\.([a-zA-Z0-9\_]*)\.\.\.")

		a=0
		for activity in p.activities:
			s=0
			for step in activity.steps:

				ourCompile = gCompileText(owner=owner,process=process,activityNum=a,stepNum=s)
				ourCompile.db=self.db
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
					ourCompile.put()


			



				s=s+1
			a=a+1



		# dont fogrget to do substeps
#		return
#		self.response.out.write("Importng Process %s\n" %(process))

		# no need to worry about deleting things as we aren't persistent
		"""
		records = self.db.GqlQuery("SELECT FROM gIngredients WHERE owner = :1 AND process = :2",owner,process)
		for record in records.fetch(43234234):	record.delete()

		records = self.db.GqlQuery("SELECT FROM gProcesses WHERE owner = :1  AND process = :2",owner,process )
		for record in records.fetch(43234234):	record.delete()

		records = self.db.GqlQuery("SELECT FROM gProcess WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()


#		records = self.db.GqlQuery("SELECT FROM gWidgets WHERE owner = :1 ",owner)
		records = self.db.GqlQuery("SELECT FROM gWidgets WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()

		records = self.db.GqlQuery("SELECT FROM gEquipment WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()

		records = self.db.GqlQuery("SELECT FROM gField WHERE owner = :1 AND process = :2 ",owner,process )
		for record in records.fetch(43234234):	record.delete()
		"""

		e=gEquipment(owner=owner,process=process,equipment="hlt",name=p.hlt.name)
		e.db=self.db
		e.dead_space = float(p.hlt.dead_space)
		e.mustSterilise=1
		try:
			e.volume = float(p.hlt.volume)
		except:
			pass
		try:		
			e.heatPower = float(p.hlt.heatPower)
		except:
			pass
		e.put()

	
		if p.immersionchiller:
			e=gEquipment(owner=owner,process=process,equipment="immersionchiller",name=p.immersionchiller.name)
			e.db=self.db
			e.mustSterilise=1
#			e.dead_space = float(p.hlt.dead_space)
			e.put()



		e=gEquipment(owner=owner,process=process,equipment="mashtun",name=p.mash_tun.name)
		e.db=self.db
		e.dead_space = float(p.mash_tun.dead_space)
		e.mustSterilise=1
		try:
			e.volume = float(p.mash_tun.volume)
		except:
			pass
		e.put()

		e=gEquipment(owner=owner,process=process,equipment="fermentationbin",name=p.fermentation_bin.name)
		e.db=self.db
		e.dead_space = float(p.fermentation_bin.dead_space)
		e.mustSterilise=1
		try:
			e.volume = float(p.fermentation_bin.volume)
		except:
			pass
		e.put()

		e=gEquipment(owner=owner,process=process,equipment="rackingbucket",name=p.racking_bucket.name)	
		e.db=self.db
		e.dead_space = float(p.racking_bucket.dead_space)
		e.mustSterilise=1
		try:
			e.volume = float(p.racking_bucket.volume)
		except:
			pass
		e.put()

		for boiler in p.boilers:
			e=gEquipment(owner=owner,process=process,equipment="boiler",name=boiler.name)
			e.db=self.db
			e.dead_space = float(boiler.dead_space)
			e.mustSterilise=1
			e.volume = float(boiler.volume)
			try:
				e.boilVolume=float(boiler.boilVolume)
			except:
				pass
			e.put()
		

		r=gProcesses(owner=owner,process=process)
		r.db=self.db
		r.put()


		r=gProcess(owner=owner,process=process,activityNum=-1,stepNum=-1,subStepNum=-1)
		r.db=self.db
		r.fixed_boil_off = float(p.fixed_boil_off)
		r.fixed_cool_off = float(p.fixed_cool_off)
		r.percentage_boil_off = float(p.percentage_boil_off)
		r.percentage_cool_off = float(p.percentage_cool_off)
		r.put()

		aNum=0
		for activity in p.activities:


			for (ingredient,qty) in activity.ingredients:
				III = gIngredients(owner=owner)
				III.db=self.db
				III.ingredient = ingredient.name
				III.qty=float(qty)
				III.process=process
				III.processIngredient=1
				III.processConsumable=0
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
				III.put()

			for (ingredient,qty) in activity.consumables:
				III = gIngredients(owner=owner)
				III.db=self.db
				III.ingredient = ingredient.name
				III.qty=float(qty)
				III.process=process
				III.processIngredient=1
				III.processConsumable=1
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
				III.put()



			r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=-1,subStepNum=-1)
			r.db=self.db
			r.stepName=activity.activityTitle
			r.put()


			sNum=0
			for step in activity.steps:
				ssNum=0
				r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=sNum,subStepNum=-1)
				r.db=self.db
				if len(step.text) == 0:
					r.text=""
				else:
					r.text=step.text	
				r.stepName=step.name
				for img in step.img:
					r.img.append(img)
				r.attention=step.attention
				r.needToComplete=1
				r.auto = step.auto
#				r.timer=step.timer	# don't set the timer here, it should be on the substep
				try:
#					print "<br><b>step.condition</b> %s" %(step.condition)
					for X in step.condition[0]:
#						print " %s " %(X)
						r.conditional.append("%s" %(X) )
#					print "<br>"
					
				except:
					r.conditional=[]
					pass
				r.put()
#					step.widgets['__adjustedgrav1'] = ('gravityTempAdjustment',['__temp1','__grav1'])


				for (fieldLabel,fieldKey,fieldVal) in step.fields:
					
					r=gField(owner=owner,process=process,activityNum=aNum,stepNum=sNum)
					r.db=self.db
					r.fieldKey= fieldKey
					r.fieldLabel=fieldLabel
					r.fieldVal=fieldVal
					if step.__dict__.has_key("widgets"):
						if step.widgets.has_key(fieldKey):
							(jd,elliot) = step.widgets[fieldKey]
							r.fieldWidget = jd
					r.put()

#				print "%s\n" %(step.name)
				if step.__dict__.has_key("widgets"):
					for widget in step.widgets:
						(w,v) =step.widgets[widget]
#						print "widget %s" %(w)
						r=gWidgets(owner=owner,process=process,activityNum=aNum,stepNum=sNum)
						r.db=self.db
						r.widgetName=widget
						r.widget= w
						for wv in v:
							r.widgetValues.append(wv)
						r.put()

				for substep in step.substeps:
					r=gProcess(owner=owner,process=process,activityNum=aNum,stepNum=sNum,subStepNum=ssNum)
					r.db=self.db
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
					if substep.need_to_complete:	r.needToComplete=1
					r.put()
					ssNum=ssNum + 1
				sNum = sNum + 1
			aNum = aNum + 1	




		
