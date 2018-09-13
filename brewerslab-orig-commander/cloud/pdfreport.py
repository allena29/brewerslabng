#!/usr/bin/python
import time





import tempfile
import os

class brewlabReport:

	def __init__(self,cloud):
		self.cloud=cloud
		self.tmp=tempfile.mkdtemp()
		self.quick=False

	def generateReport(self):

		self.cloud.compile(self.username,self.xrecipe,self.brewlog)

		o=open("%s/report.html" %(self.tmp),"w")
		o.write("""<html><head><title>%s/%s</title><META name="Author" content="Adam Allen"></head>""" %(cloud.recipe.recipename,cloud.Process.process))
		o.write("""<body><h1>%s/%s</h1><p>""" %(cloud.recipe.recipename,cloud.Process.process))
		o.write("Generated: %s" %(time.ctime()))
#		o.write("""<li><a href="#recipe" >Recipe</a>""")
#		o.write("""<li><a href="#calclog">Calclog</a>""")
		o.write("""<a name=recipe><h2>Recipe - %s</h2><p>""" %(cloud.recipe.recipename))
		o.write("%s<br>" %(cloud.recipe.credit))
		o.write("<blockquote>%s</blockquote><P>" %(cloud.recipe.description))
		o.write("""<li> Batch Size  %.0f L""" %(cloud.recipe.batch_size_required))
		o.write("""<li> Estimated - Original Gravity %.4f""" %(cloud.estimated_og))
		o.write("""<li> Estimated - Final Gravity %.4f""" %(cloud.estimated_fg))
		o.write("""<li> Estimated - Alcohol %.2f %%""" %(cloud.estimated_abv))
		o.write("""<li> Estimated - IBU %.2f """ %(cloud.estimated_ibu))
		if cloud.estimated_srm < 1:
			srm=1
		elif cloud.estimated_srm < 40:
			srm=int(cloud.estimated_srm)
		else:
			srm=40
		os.system("cp srmcolours/small.srm%s-1902.jpg %s/srm%s.jpg" %(srm,self.tmp,srm))

		if not self.quick:	o.write("""<li> Estimated - Colour %.2f EBC <img src=srm%s.jpg width=30 height=10>""" %(cloud.estimated_ebc,srm))
		o.write("""<li> Boil Volume: %.2f L""" %(cloud.water_in_boil))
		o.write("""<li> Post Boil Topup Volume: %.2f L""" %(cloud.recipe.postBoilTopup))
		o.write("""<li> Mash Water: %.2f L """ %(cloud.mash_liquid))
		o.write("""<li> Sparge Water: %.2f L """ %(cloud.sparge_water))
		o.write("""<li> Mash Efficiency: %.1f %% """ %(cloud.recipe.mash_efficiency))
		o.write("""<h3>Fermentables</h3>""")


		for ferm in cloud.fermentables:
			if not ferm.unit:	ferm.unit="gm"
			o.write("<b>%.2f %s %s</b><br>" %(ferm.qty,ferm.unit,ferm.ingredient))
			o.write("<blockquote>")
			ourContribution = cloud.dbWrapper.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2 AND ingredientType = :3 AND ingredient = :4", self.username, cloud.recipe.recipename, "fermentables", ferm.ingredient).fetch(1)[0]
			o.write("Gravity: %.4f<br>" %(1+(ourContribution.gravity/1000)))
			try:
				o.write("HWE: %.2f<br>" %(ferm.hwe))
			except:
				pass
			try:
				if cloud.estimated_srm < 1:
					srm=1
				elif cloud.estimated_srm < 40:
					srm=int(cloud.estimated_srm)
				else:
					srm=40
				os.system("cp srmcolours/small.srm%s-1902.jpg %s/srm%s.jpg" %(srm,self.tmp,srm))
				if not self.quick:	o.write("EBC: %.2f <img src=srm%s.jpg width=30 height=10><br>" %(ferm.colour,srm))
			except:
				pass
			if ferm.isGrain:
				o.write("Grain<br>")
			if ferm.mustMash:
				o.write("Must Mash<br>")
			if ferm.isAdjunct:
				o.write("Adjunct<br>")	
			o.write("</blockquote>")

		o.write("""<h3>Hops</h3>""")
#		totalFerm=0
		#for x in ourContribution:
		#	totalFerm=totalFerm+x.gravity

		
		hopsByType={}
		hopsQty={}
		for hop in cloud.hops:
			if not hopsByType.has_key( hop.ingredient):	hopsByType[hop.ingredient]=[]
			if not hopsQty.has_key( hop.ingredient):	hopsQty[hop.ingredient]=0
			hopsByType[hop.ingredient].append(hop.hopAddAt)
			hopsByType[hop.ingredient].sort()
			hopsByType[hop.ingredient].reverse()
			hopsQty[hop.ingredient]=hopsQty[hop.ingredient]+hop.qty
		hop_labels = {60:'Copper (60min)',15:'Aroma (15min)',5:'Finishing (5min)',0.000001:'Flameout (0min)',0.001:'Flameout (0min)'}


#		for x in cloud.dbWrapper._gContributions:
#			x.toString()
						


		for hopType in hopsByType:
			totalIBU=0
			ourContribution = cloud.dbWrapper.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2 AND ingredientType = :3 AND ingredient = :4", self.username, cloud.recipe.recipename, "hops", hopType).fetch(999)
			for x in ourContribution:
				totalIBU=totalIBU+x.ibu

			o.write("<b>%.2f %s %s</b> " %(hopsQty[hopType],"gm",hopType))
			o.write("<b>(AA %.2f %%)</b><br><b>%.2f IBU</b><br>" %(hop.hopAlpha,totalIBU))
			o.write("<blockquote>")
			for hopAddAt in hopsByType[hopType]:
				for hop in cloud.hops:
					if hop.hopAddAt == hopAddAt and hop.ingredient == hopType:
						if not hop_labels.has_key(hopAddAt):
							hoplabel = "%.0f min" %(hopAddAt)
						else:
							hoplabel = hop_labels[hopAddAt]

						ourContribution = cloud.dbWrapper.GqlQuery("SELECT * FROM gContributions WHERE owner = :1 AND recipeName = :2 AND ingredientType = :3 AND ingredient = :4 AND hopAddAt = :5", self.username, cloud.recipe.recipename, "hops", hopType,hopAddAt).fetch(1)
#						print ourContribution
#						print ourContribution[0]
#						print ourContribution[0].ibu
			 
						o.write("%.1f gm - %s<br>%.2f IBU<p>" %(hop.qty,hoplabel,ourContribution[0].ibu))
			o.write("</blockquote>")



		o.write("""<h3>Yeast</h3>""")
		for yeast in cloud.yeasts:
			o.write("<b>%.2f %s %s</b>" %(yeast.qty,"pkt",yeast.ingredient))
			o.write("<blockquote>")
			o.write("Attenuation: %.2f %%<br>" %(yeast.atten))
			o.write("</blockquote>")



		o.write("<a name=process><h2>Process %s</h2><p>" %(cloud.Process.process))


		ourActivities = cloud.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum > :3 AND stepNum = :4",self.username,cloud.Process.process,-1,-1).fetch(400)
		for activity in ourActivities:
			o.write("<h3>%s</h3>" %(activity.stepName))
		

			ourSteps = cloud.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum > :4 AND subStepNum = :5",self.username,cloud.Process.process,activity.activityNum,-1,-1).fetch(4000)
			for step in ourSteps:

				# our compile
				ourCompiles = cloud.dbWrapper.GqlQuery("SELECT * FROM gCompileText WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4",self.username,cloud.Process.process,activity.activityNum,step.stepNum).fetch(1)
				if len(ourCompiles) < 1:
					ouc = []
				else:
					ouc =ourCompiles[0].toReplace
				updatedText=step.text
				# in future need brewlog here
				updatedText= cloud._newVariableSub(self.username,ouc,"","",step.text,cloud.recipe.recipename,cloud.Process.process,"",begin="<font color=blue>",finish="</font>")

				o.write("<b>%s</b><br><blockquote>" %(step.stepName))
				o.write("%s<br>" %(updatedText))
				if step.attention and not self.quick:
					o.write("<img src=attention.jpg width=24 height=24> <font color=red>%s</font><br>" %(step.attention))	
					os.system("cp attention.jpg %s/attention.jpg" %(self.tmp))

				for img in step.img:
					if not self.quick:
						o.write("<img src=%s><br>" %(img))
						os.system("cp processimg/%s/%s %s/%s" %(cloud.Process.process,img,self.tmp,img))


				ourSubSteps = cloud.dbWrapper.GqlQuery("SELECT * FROM gProcess WHERE owner = :1 AND process = :2 AND activityNum = :3 AND stepNum = :4 AND subStepNum > :5",self.username,cloud.Process.process,activity.activityNum,step.stepNum,-1).fetch(4000)
				for substep in ourSubSteps:
					o.write("- %s<br><br>" %( cloud._newVariableSub(self.username,ouc,activity.activityNum,step.stepNum,substep.stepName,cloud.recipe.recipename,cloud.Process.process,"",begin="<font color=blue>",finish="</font>")))
#					o.write("- %s<br><br>" %(substep.stepName))

				# in future need brewlog here
				ourFields =cloud.dbWrapper.GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND activityNum = :3 AND stepNum = :4",self.username,"",activity.activityNum,step.stepNum).fetch(545551)
				for field in ourFields:
					if field.fieldKey != "notepage":
						if field.fieldWidget:
							e="do nothing"
						else:
							o.write("<table border=1><tr><td>%s</td><td width=32><font color=white>........................................</font></td></tr></table>" %(field.fieldKey))

				o.write("</blockquote>")
		

		o.write("""<a name=calclog><h2>Calclog</h2><p><pre>""")
		o.write( self.cloud.calclog )
		o.close()
		
		o=open("%s/config" %(self.tmp),"w")
		o.write("""A:link { color: red }\n""")
		o.write("""footer { right: "$[N]"}\n""")
		o.write("""
BODY {
font-size: 12pt;
font-family: Helvetica;
text-align: justify
}
		""")
		o.close()

		os.system("cp %s/report.html /tmp" %(self.tmp))
		os.chdir("%s" %(self.tmp))
		if not self.quick:
			starttime=time.time()
			print "Creating pdf %s" %(starttime)
			os.system("html2ps -U -f config --toc bh report.html >report.ps")
			os.system("ps2pdf report.ps report.pdf")
			os.system("du -ch report.pdf")
			print "Finished in %s sec" %(time.time()-starttime)
			os.system("cp %s/report.pdf /tmp/%s_%s_%s.pdf" %(self.tmp, cloud.recipe.recipename, cloud.Process.process, int(time.time())))
			os.system("evince report.pdf")
	
	def __del__(self):

		for x in os.listdir(self.tmp):
			os.unlink("%s/%s" %(self.tmp,x))
		os.rmdir("%s" %(self.tmp))
	


if __name__ == '__main__':
	from standalone import *
	brewlog="dummybrewlog"
	recipe="CascadeSHPA"
	username="standalone"
	

	# need to add in some bits about standalone here
	#from standalone import *
	
#	from cloudNG import *	
#	brewlog="2013_3_9"
#	username="test@example.com"
#	recipe="Green13"
#	cloud=brewerslabCloudApi()

	print cloud


 	report=brewlabReport(cloud)
	report.brewlog=brewlog
	report.username=username
	report.xrecipe=recipe
	report.quick=True
	report.generateReport()
print " a couple of places we have standalone hardcoded as the username search for \"standalone\""
print " a couple of places we odn't have a brewlog  --- search for # in future need brewlog here"

