from __future__ import division
from xml.dom import minidom
import cPickle as pickle
import os
import sys
import re



class bjcpStyleTools:


	def __init__(self):
		self.pickledict="styleguide2008.pickle"

	def cleanupXML(self,xmlFile):
		cleanup=re.compile("[^a-zA-Z0-9 \.\,\,\<\>\/\"\?\!\=\-]")
		cleanup2=re.compile("\x92")
		o=open( xmlFile)
		O=open(".%s.tmp" %(xmlFile),"w")
		y=o.readline()
		while y != "":
			O.write( cleanup2.sub('',cleanup.sub('',y)) )
			y=o.readline()
		o.close()
		O.close()


	def importXML(self,xmlFile="styleguide2008.xml"):
		"""
	
		import the xml styleguide2008 as per http://www.bjcp.org/stylecenter.php
		and store in a dict:

		clean-up incorporated based on:
		sed -e 's/[^a-zA-Z0-9 \.\,\<\>\/\"\?\!\=\-]//g' <styleguide2008.xml | sed  's/\x92//'  >styleguide2008.sed.xml 

	
		"""	
		
		self.cleanupXML(xmlFile)	
		
		beerstyles={}
		xmldoc = minidom.parse( ".%s.tmp" %(xmlFile) )
		sg = xmldoc.childNodes[2]
		d=None

		for c in   sg.childNodes[1].childNodes:
		#	print c
			D=d
			for d in c.childNodes:
		#		print d	
				try:
					beerstyle= d.getElementsByTagName('name')[0].firstChild.data	
					beerstyles[beerstyle]={	'xml': d,'substyles' : {} }
				except:
					pass

		for style in beerstyles:
			substyle= beerstyles[style]['xml'].getElementsByTagName('name')[0].firstChild.data

			beerstyles[style]['substyles'][substyle] = {}
			stats= beerstyles[style]['xml'].getElementsByTagName('stats')[0]

			og=stats.getElementsByTagName('og')
			fg=stats.getElementsByTagName('fg')
			ibu=stats.getElementsByTagName('ibu')
			srm=stats.getElementsByTagName('srm')

			try:
				oglow=og[0].getElementsByTagName('low')[0].firstChild.data
				oghigh=og[0].getElementsByTagName('high')[0].firstChild.data
			except:
				oglow=-1
				oghigh=-1

			beerstyles[style]['substyles'][substyle]['originalGravity']=(oglow,oghigh)

			try:
				fglow=fg[0].getElementsByTagName('low')[0].firstChild.data
				fghigh=fg[0].getElementsByTagName('high')[0].firstChild.data
			except:
				fglow=-1
				fghigh=-1

			beerstyles[style]['substyles'][substyle]['finalGravity']=(fglow,fghigh)

			try:
				ibulow=ibu[0].getElementsByTagName('low')[0].firstChild.data
				ibuhigh=ibu[0].getElementsByTagName('high')[0].firstChild.data
			except:
				ibulow=-1
				ibuhigh=-1
			
			beerstyles[style]['substyles'][substyle]['ibu']=(fglow,fghigh)

			try:
				srmlow=srm[0].getElementsByTagName('low')[0].firstChild.data
				srmhigh=srm[0].getElementsByTagName('high')[0].firstChild.data
			except:
				srmlow=-1
				srmhigh=-1

			beerstyles[style]['substyles'][substyle]['srm']=(srmlow,srmhigh)

			beerstyles[style]['substyles'][substyle]['aroma'] = beerstyles[style]['xml'].getElementsByTagName('aroma')[0].firstChild.data
			if len( beerstyles[style]['xml'].getElementsByTagName('ingredients')) > 0:
				beerstyles[style]['substyles'][substyle]['ingredients'] = beerstyles[style]['xml'].getElementsByTagName('ingredients')[0].firstChild.data
			else:
				beerstyles[style]['substyles'][substyle]['ingredients'] = None

			beerstyles[style]['substyles'][substyle]['ingredients'] = beerstyles[style]['xml'].getElementsByTagName('ingredients')
			beerstyles[style]['substyles'][substyle]['flavor'] = beerstyles[style]['xml'].getElementsByTagName('flavor')[0].firstChild.data
			beerstyles[style]['substyles'][substyle]['mouthfeel'] = beerstyles[style]['xml'].getElementsByTagName('mouthfeel')[0].firstChild.data
			beerstyles[style]['substyles'][substyle]['impression'] = beerstyles[style]['xml'].getElementsByTagName('impression')[0].firstChild.data
			if len( beerstyles[style]['xml'].getElementsByTagName('comments') ) > 0:
				beerstyles[style]['substyles'][substyle]['comments'] = beerstyles[style]['xml'].getElementsByTagName('comments')[0].firstChild.data
			else:
				beerstyles[style]['substyles'][substyle]['comments'] = None
			beerstyles[style]['substyles'][substyle]['examples'] = beerstyles[style]['xml'].getElementsByTagName('examples')[0].firstChild.data



		o=open("bjcpstyles.brwlab","w")
		o.write( pickle.dumps(beerstyles))
		o.close()

	def _tidyText(self,c,a):
		OO=""
		z=a.split(" ")
		o="   %s:" %(c)
		for Z in z:
			if len("%s %s" %(o,Z)) > 138:
				OO=OO+o
				o="\n    "+Z
			else:
				o="%s %s" %(o,Z)
			
		return  OO+o
				



	def findMatchingStyleReport(self,TargetOG=1.037,TargetFG=1.011, TargetIBU=48.2, TargetSRM=7):
		"""

		an old quick and dirty script wrapped up into the class
		in the future this could be cleaned up to use the importedXML
		
		"""
	
		hideNegative=1
		extendedText=0
		Tog=TargetOG
		Tfg=TargetFG
		Tibu=TargetIBU
		Tsrm=TargetSRM
		"""

		self.cleanupXML("styleguide2008.xml")	
		beerstyles={}
		xmldoc = minidom.parse(".styleguide2008.xml.tmp")
		sg = xmldoc.childNodes[2]

		d=None



		for c in   sg.childNodes[1].childNodes:
		#	print c
			D=d
			for d in c.childNodes:
		#		print d	
				try:
					beerstyle= d.getElementsByTagName('name')[0].firstChild.data	
					beerstyles[beerstyle]={ 	'xml': d,	'substyles' : {} }
				

				except:
					pass
		
		print beerstyles
		"""

		if not os.path.exists("bjcpstyles.brwlab"):	return {}
		o=open("bjcpstyles.brwlab")
		beerstyles = pickle.loads( o.read() )
		o.close()

		#

		bjcp_result={}
		bjcp_result['__db_num_styles__'] = len(beerstyles)
		bjcp_result['__search__'] = {'og':Tog,'fg':Tfg,'ibu':Tibu,'srm':Tsrm}
		bjcp_result['styles']=[]

		results={}
		scores=[]
		scoreResultMap={}


		for style in beerstyles:
			substyle= beerstyles[style]['xml'].getElementsByTagName('name')[0].firstChild.data

			score=0

			beerstyles[style]['substyles'][substyle] = {}
			stats= beerstyles[style]['xml'].getElementsByTagName('stats')[0]
			
			og=stats.getElementsByTagName('og')
			fg=stats.getElementsByTagName('fg')
			ibu=stats.getElementsByTagName('ibu')
			srm=stats.getElementsByTagName('srm')

			try:
				oglow=og[0].getElementsByTagName('low')[0].firstChild.data
				oghigh=og[0].getElementsByTagName('high')[0].firstChild.data
			except:
				oglow=-1
				oghigh=-1
			try:
				fglow=fg[0].getElementsByTagName('low')[0].firstChild.data
				fghigh=fg[0].getElementsByTagName('high')[0].firstChild.data
			except:
				fglow=-1
				fghigh=-1
			try:
				ibulow=ibu[0].getElementsByTagName('low')[0].firstChild.data
				ibuhigh=ibu[0].getElementsByTagName('high')[0].firstChild.data
			except:
				ibulow=-1
				ibuhigh=-1

			try:
				srmlow=srm[0].getElementsByTagName('low')[0].firstChild.data
				srmhigh=srm[0].getElementsByTagName('high')[0].firstChild.data
			except:
				srmlow=-1
				srmhigh=-1


			#############################################################################################################
			# Checking Range of Gravity's and giving score
			
			scoreOg=0
			scoreFg=0
			scoreIbu=0	
			scoreSrm=0
			if Tog < float(oglow) and Tog > float(oghigh):
				scoreOg=0						# Original Gravity Out Of Range
			elif Tog < float(oglow) and Tog <= float(oghigh):		
				scoreOg=5						# Original Gravity Not Higher
			elif Tog >= float(oglow) and Tog > float(oghigh):	
				scoreOg=5						# Original Gravity Not Lower
			else:
				scoreOg=20						# Original Gravity in range

			# FG
			if Tfg < float(fglow) and Tfg > float(fghigh):
				scoreFg=0						# Original Gravity Out Of Range
			elif Tfg < float(fglow) and Tfg <= float(fghigh):		
				scoreFg=5						# Original Gravity Not Higher
			elif Tfg >= float(fglow) and Tfg > float(fghigh):	
				scoreFg=5						# Original Gravity Not Lower
			else:
				scoreFg=20						# Original Gravity in range
			

			# IBU
			if Tibu < float(ibulow) and Tibu > float(ibuhigh):
				scoreIbu=0						# Original Gravity Out Of Range
			elif Tibu < float(ibulow) and Tibu <= float(ibuhigh):		
				scoreIbu=9						# Original Gravity Not Higher
			elif Tibu >= float(ibulow) and Tibu > float(ibuhigh):	
				scoreIbu=9						# Original Gravity Not Lower
			else:
				scoreIbu=40						# Original Gravity in range
			

			# SRM
			if Tsrm < float(srmlow) and Tsrm > float(srmhigh):
				scoreSrm=0						# Original Gravity Out Of Range
			elif Tsrm < float(srmlow) and Tsrm <= float(srmhigh):		
				scoreSrm=6						# Original Gravity Not Higher
			elif Tsrm >= float(srmlow) and Tsrm > float(srmhigh):	
				scoreSrm=6						# Original Gravity Not Lower
			else:
				scoreSrm=30						# Original Gravity in range
			

			try:
				#sys.stderr.write("%s/%s score=%s scoreOg=%s scoreFg=%s scoreIbu=%s scoreSrm=%s\n" %(style,substyle,scoreOg+scoreFg+scoreIbu+scoreSrm,scoreOg,scoreFg,scoreIbu,scoreSrm))	
				results[ (style,substyle) ] = {'og': (float(oglow),float(oghigh)), 'fg': (float(fglow),float(fghigh)), 'ibu' : (float(ibulow),float(ibuhigh)), 'srm':(float(srmlow),float(srmhigh)), 'xml':beerstyles[style]['xml']}

				score=(scoreSrm+scoreIbu+scoreOg+scoreFg)*100
				if not scoreResultMap.has_key( score ):
					scoreResultMap[ score ] = []
					scores.append(score)
				scoreResultMap[ score ].append( (style,substyle) )
			except:
				pass
			
		scores.sort()
		scores.reverse()
#		sys.stderr.write("\n")
#		sys.stderr.write("\n")
#		sys.stderr.write("\n")


		for score in scores:
			subscores=[]
			subscoreMap={}
			# a better scoring mechanism that applies within the group rather than outside the grouping
			for (style,substyle) in scoreResultMap[ score ]:
				(oglow,oghigh) = results[ (style,substyle) ]['og']
				ogmid = ((oghigh-oglow)/2)+oglow
				ogdelta = pow( (100-(ogmid/Tog)*100), 6)
				(fglow,fghigh) = results[ (style,substyle) ]['fg']
				fgmid = ((fghigh-fglow)/2)+fglow
				fgdelta = pow( (100-(fgmid/Tfg)*100), 6)
				(ibulow,ibuhigh) = results[ (style,substyle) ]['ibu']
				ibumid = ((ibuhigh-ibulow)/2)+ibulow
				ibudelta = pow( (10-(ibumid/Tibu)*10), 6)
				(srmlow,srmhigh) = results[ (style,substyle) ]['srm']
				srmmid = ((srmhigh-srmlow)/2)+srmlow
				srmdelta = pow( (5-(srmmid/Tsrm)*5), 6)

				subscore=score-ogdelta-fgdelta-ibudelta-srmdelta
				if not subscoreMap.has_key(subscore):
					subscores.append(subscore)	
					subscoreMap[subscore] =[]
				subscoreMap[subscore].append( (style,substyle,ogdelta,fgdelta,ibudelta,srmdelta))

			subscores.sort()
			subscores.reverse()
			for Ssubscore in subscores:
				for (Sstyle,Ssubstyle,Sogdelta,Sfgdelta,Sibudelta,Ssrmdelta) in subscoreMap[ Ssubscore ]:
			
					if (hideNegative	 and Ssubscore >= 0) or not hideNegative:
						
					
						bjcp_result['styles'].append( {} )
						bjcp_result['styles'][-1]['stylename'] = Sstyle
						bjcp_result['styles'][-1]['substylename'] = Ssubstyle
						bjcp_result['styles'][-1]['score'] = Ssubscore
#						print "Style: %s; SubStyle: %s;" %(Sstyle,Ssubstyle)
#						print "Score:  %s (basescore:%s og:%f.4 fg:%f.4 ibu:%f.4 srm:%f.4)" %(Ssubscore,score,Sogdelta,Sfgdelta,Sibudelta,Ssrmdelta)
						try:
							(oglow,oghigh) = results[ (Sstyle,Ssubstyle) ]['og']
							bjcp_result['styles'][-1]['og'] = (oglow,oghigh)
							#print "   Original Gravity: %s----%s (Target %s)" %(oglow,oghigh,Tog)
							(fglow,fghigh) = results[ (Sstyle,Ssubstyle) ]['fg']
							bjcp_result['styles'][-1]['fg'] = (fglow,fghigh)
#							print "   Final Gravity: %s----%s (Target %s)" %(fglow,fghigh,Tfg)
							(ibulow,ibuhigh) = results[ (Sstyle,Ssubstyle) ]['ibu']
							bjcp_result['styles'][-1]['ibu'] = (ibulow,ibuhigh)
#							print "   International Bittering Units: %s----%s (Target %s)" %(ibulow,ibuhigh,Tibu)
							(srmlow,srmhigh) = results[ (Sstyle,Ssubstyle) ]['srm']
							bjcp_result['styles'][-1]['srm'] = (srmlow,srmhigh)
#							print "   SRM: %s----%s (Target %s)" %(srmlow,srmhigh,Tsrm)

							bjcp_result['styles'][-1]['aroma'] =  self._tidyText("Aroma", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('aroma')[0].firstChild.data)
							bjcp_result['styles'][-1]['ingredients'] =  self._tidyText("Ingredients", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('ingredients')[0].firstChild.data)
							bjcp_result['styles'][-1]['flavor'] = self._tidyText("Flavor", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('flavor')[0].firstChild.data)
							bjcp_result['styles'][-1]['mouthfeel'] =  self._tidyText("MouthFeel", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('mouthfeel')[0].firstChild.data)
							bjcp_result['styles'][-1]['impression'] = self._tidyText("Impression", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('impression')[0].firstChild.data)
							bjcp_result['styles'][-1]['comments'] = self._tidyText("Comments", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('comments')[0].firstChild.data)
							bjcp_result['styles'][-1]['examples'] = self._tidyText("Example", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('examples')[0].firstChild.data)
						except:
							pass

		return bjcp_result
	def OLDfindMatchingStyleReport(self,TargetOG=1.037,TargetFG=1.011, TargetIBU=48.2, TargetSRM=7):
		"""

		an old quick and dirty script wrapped up into the class
		in the future this could be cleaned up to use the importedXML
		
		"""
	
		hideNegative=1
		extendedText=0

		self.cleanupXML("styleguide2008.xml")	
		Tog=TargetOG
		Tfg=TargetFG
		Tibu=TargetIBU
		Tsrm=TargetSRM
		beerstyles={}
		xmldoc = minidom.parse(".styleguide2008.xml.tmp")
		sg = xmldoc.childNodes[2]

		d=None



		for c in   sg.childNodes[1].childNodes:
		#	print c
			D=d
			for d in c.childNodes:
		#		print d	
				try:
					beerstyle= d.getElementsByTagName('name')[0].firstChild.data	
					beerstyles[beerstyle]={ 	'xml': d,	'substyles' : {} }
				

				except:
					pass
			
		#

		print "There are %s beer styles in the database." %(len(beerstyles))
		print " searching for;"
		print "  original gravity %s" %(Tog)
		print "  final gravity %s" %(Tfg)
		print "  target IBU %s" %(Tibu)
		print "  target SRM %s" %(Tsrm)


		results={}
		scores=[]
		scoreResultMap={}


		for style in beerstyles:
			substyle= beerstyles[style]['xml'].getElementsByTagName('name')[0].firstChild.data

			score=0

			beerstyles[style]['substyles'][substyle] = {}
			stats= beerstyles[style]['xml'].getElementsByTagName('stats')[0]

			og=stats.getElementsByTagName('og')
			fg=stats.getElementsByTagName('fg')
			ibu=stats.getElementsByTagName('ibu')
			srm=stats.getElementsByTagName('srm')

			try:
				oglow=og[0].getElementsByTagName('low')[0].firstChild.data
				oghigh=og[0].getElementsByTagName('high')[0].firstChild.data
			except:
				oglow=-1
				oghigh=-1
			try:
				fglow=fg[0].getElementsByTagName('low')[0].firstChild.data
				fghigh=fg[0].getElementsByTagName('high')[0].firstChild.data
			except:
				fglow=-1
				fghigh=-1
			try:
				ibulow=ibu[0].getElementsByTagName('low')[0].firstChild.data
				ibuhigh=ibu[0].getElementsByTagName('high')[0].firstChild.data
			except:
				ibulow=-1
				ibuhigh=-1

			try:
				srmlow=srm[0].getElementsByTagName('low')[0].firstChild.data
				srmhigh=srm[0].getElementsByTagName('high')[0].firstChild.data
			except:
				srmlow=-1
				srmhigh=-1


			#############################################################################################################
			# Checking Range of Gravity's and giving score
			
			scoreOg=0
			scoreFg=0
			scoreIbu=0	
			scoreSrm=0
			if Tog < float(oglow) and Tog > float(oghigh):
				scoreOg=0						# Original Gravity Out Of Range
			elif Tog < float(oglow) and Tog <= float(oghigh):		
				scoreOg=5						# Original Gravity Not Higher
			elif Tog >= float(oglow) and Tog > float(oghigh):	
				scoreOg=5						# Original Gravity Not Lower
			else:
				scoreOg=20						# Original Gravity in range

			# FG
			if Tfg < float(fglow) and Tfg > float(fghigh):
				scoreFg=0						# Original Gravity Out Of Range
			elif Tfg < float(fglow) and Tfg <= float(fghigh):		
				scoreFg=5						# Original Gravity Not Higher
			elif Tfg >= float(fglow) and Tfg > float(fghigh):	
				scoreFg=5						# Original Gravity Not Lower
			else:
				scoreFg=20						# Original Gravity in range
			

			# IBU
			if Tibu < float(ibulow) and Tibu > float(ibuhigh):
				scoreIbu=0						# Original Gravity Out Of Range
			elif Tibu < float(ibulow) and Tibu <= float(ibuhigh):		
				scoreIbu=9						# Original Gravity Not Higher
			elif Tibu >= float(ibulow) and Tibu > float(ibuhigh):	
				scoreIbu=9						# Original Gravity Not Lower
			else:
				scoreIbu=40						# Original Gravity in range
			

			# SRM
			if Tsrm < float(srmlow) and Tsrm > float(srmhigh):
				scoreSrm=0						# Original Gravity Out Of Range
			elif Tsrm < float(srmlow) and Tsrm <= float(srmhigh):		
				scoreSrm=6						# Original Gravity Not Higher
			elif Tsrm >= float(srmlow) and Tsrm > float(srmhigh):	
				scoreSrm=6						# Original Gravity Not Lower
			else:
				scoreSrm=30						# Original Gravity in range
			

			try:
				sys.stderr.write("%s/%s score=%s scoreOg=%s scoreFg=%s scoreIbu=%s scoreSrm=%s\n" %(style,substyle,scoreOg+scoreFg+scoreIbu+scoreSrm,scoreOg,scoreFg,scoreIbu,scoreSrm))	
				results[ (style,substyle) ] = {'og': (float(oglow),float(oghigh)), 'fg': (float(fglow),float(fghigh)), 'ibu' : (float(ibulow),float(ibuhigh)), 'srm':(float(srmlow),float(srmhigh)), 'xml':beerstyles[style]['xml']}

				score=(scoreSrm+scoreIbu+scoreOg+scoreFg)*100
				if not scoreResultMap.has_key( score ):
					scoreResultMap[ score ] = []
					scores.append(score)
				scoreResultMap[ score ].append( (style,substyle) )
			except:
				pass
			
		scores.sort()
		scores.reverse()
		sys.stderr.write("\n")
		sys.stderr.write("\n")
		sys.stderr.write("\n")


		print 
		print
		for score in scores:
			subscores=[]
			subscoreMap={}
			# a better scoring mechanism that applies within the group rather than outside the grouping
			for (style,substyle) in scoreResultMap[ score ]:
				(oglow,oghigh) = results[ (style,substyle) ]['og']
				ogmid = ((oghigh-oglow)/2)+oglow
				ogdelta = pow( (100-(ogmid/Tog)*100), 6)
				(fglow,fghigh) = results[ (style,substyle) ]['fg']
				fgmid = ((fghigh-fglow)/2)+fglow
				fgdelta = pow( (100-(fgmid/Tfg)*100), 6)
				(ibulow,ibuhigh) = results[ (style,substyle) ]['ibu']
				ibumid = ((ibuhigh-ibulow)/2)+ibulow
				ibudelta = pow( (10-(ibumid/Tibu)*10), 6)
				(srmlow,srmhigh) = results[ (style,substyle) ]['srm']
				srmmid = ((srmhigh-srmlow)/2)+srmlow
				srmdelta = pow( (5-(srmmid/Tsrm)*5), 6)

				subscore=score-ogdelta-fgdelta-ibudelta-srmdelta
				if not subscoreMap.has_key(subscore):
					subscores.append(subscore)	
					subscoreMap[subscore] =[]
				subscoreMap[subscore].append( (style,substyle,ogdelta,fgdelta,ibudelta,srmdelta))

			subscores.sort()
			subscores.reverse()
			for Ssubscore in subscores:
				for (Sstyle,Ssubstyle,Sogdelta,Sfgdelta,Sibudelta,Ssrmdelta) in subscoreMap[ Ssubscore ]:
			
					if (hideNegative	 and Ssubscore >= 0) or not hideNegative:
						print "Style: %s; SubStyle: %s;" %(Sstyle,Ssubstyle)
						print "Score:  %s (basescore:%s og:%f.4 fg:%f.4 ibu:%f.4 srm:%f.4)" %(Ssubscore,score,Sogdelta,Sfgdelta,Sibudelta,Ssrmdelta)
						try:
							(oglow,oghigh) = results[ (Sstyle,Ssubstyle) ]['og']
							print "   Original Gravity: %s----%s (Target %s)" %(oglow,oghigh,Tog)
							(fglow,fghigh) = results[ (Sstyle,Ssubstyle) ]['fg']
							print "   Final Gravity: %s----%s (Target %s)" %(fglow,fghigh,Tfg)
							(ibulow,ibuhigh) = results[ (Sstyle,Ssubstyle) ]['ibu']
							print "   International Bittering Units: %s----%s (Target %s)" %(ibulow,ibuhigh,Tibu)
							(srmlow,srmhigh) = results[ (Sstyle,Ssubstyle) ]['srm']
							print "   SRM: %s----%s (Target %s)" %(srmlow,srmhigh,Tsrm)

							if extendedText:
								print self._tidyText("Aroma", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('aroma')[0].firstChild.data)
								print self._tidyText("Ingredients", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('ingredients')[0].firstChild.data)
								print self._tidyText("Flavor", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('flavor')[0].firstChild.data)
								print self._tidyText("MouthFeel", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('mouthfeel')[0].firstChild.data)
								print self._tidyText("Impression", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('impression')[0].firstChild.data)
								print self._tidyText("Comments", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('comments')[0].firstChild.data)
								print self._tidyText("Example", results[(Sstyle,Ssubstyle)]['xml'].getElementsByTagName('examples')[0].firstChild.data)
						except:
							pass

						print 
						print


if __name__ == '__main__':
	bjcp=bjcpStyleTools()
	bjcp.importXML()


if __name__ == '__main__':
	bjcp=bjcpStyleTools()
	bjcp.importXML()

