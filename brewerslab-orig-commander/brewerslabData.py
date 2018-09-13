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
# $Revision: 1.8 $ $Date: 2011-10-16 14:24:30 $ $Author: codemonkey $
#
import re
from brewerslabEngine import *
import cPickle as pickle

try:	from embargodata import brewerslabEmbargoData	
except:	pass


class brwlabPresetData:

	def __init__(self,userid="" ):
		"""
		fermentable-index name is defined as lower case letters and digits only.
		hop-index name is defined as lower case letters and digits only.

		self.fermentable_names
			a dict mapping fermentable-index name to a presentation name.
			self.fermentable_names = {
				'ukpilsner2row' : 'UK Pilsner 2-Row',
			}
		self.fermentable_descriptions
			a dict mapping fermentable-index name to a text description
			self.fermentable_descriptions = {
				'ukpilsner2row' : 'UK Pilsner 2-Row Malt',
			}
		self.fermentable_detail
			a dict mapping fermentable-index name to a tuple describing the fermentable. 
			in order the tuple is defined as:
				extract		- Percentage Extract (hwe @100% = 384.7)
						-  8.3454 X PPG = HWE
				colour		- Colour in EBC
				mash		- mash required, boolean flag
				aromatic	- armoatic fermentable, boolean flag
				biscuit		- biscuit flavour, boolean flag
				body		- use for body, boolean flag
				burnt		- burnt flavour, boolean flag
				caramel		- caramel flavour, boolean flag	
				chocolate	- chocolate flavour, boolean falg
				coffee		- coffee flavour, boolean flag
				grainy		- grainy, boolean flag
				head		- aids head retention, boolean flag
				malty		- malty quality, boolean flag
				nutty		- nutty quality, boolean flag
				roasted		- roasted boolean flag
				smoked		- smoked, boolean flag
				sweet		- sweet tasting, boolean flag
				toasted		- toasted fermentable, boolean flag
				isMalt		- 1 == yes, 0 == no (i.e. is Adjunct)
			self.fermentable_detail = {
				'ukpilsner2row' : (77.9,1.97,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
			}
		self.hop_names 
			a dict mapping hop-index name to a presentation name.
			self.hop_names = {
				'eroica' : 'Eroica',
			}
		self.hop_subs
			a dict mapping hop-index name to a list of substitutions.
			self.hop_subs = {
				'perle' : ['Challenger', 'Northern Brewer'],
			}
		self.hop_alphas
			a dict mapping hop-index name to a float specifiying the alpha acide percentage
			self.hop_alphas = {
				'hullerbitterer' : 5.75,
			}	
		self.hop_styles
			a dict mapping hop-index name to a list of styles
			self.hop_styles = {
				'admiral' : ["Ale"],
			}
		self.hop_descriptions
			a dict mapping hop-index name to a string providing a description
			self.hop_descriptions = {
				'perle' : "Perle is an" 
			}

		"""

		self.fermentable_objs={}		# internal 
		self.hop_objs={}			# internal
		self.yeast_objs={}			# internal
		self.misc_objs={}			# internal
		self.suppliers = {}
		self.consumable_objs = {}
		self.equipment_objs = {}

		
		self.fermentable_names = {}
		self.fermentable_detailed = {}
		self.fermentable_descriptions = {}

		self.hop_names = {}		# Index
		self.hop_descriptions = {}
		self.hop_alphas = {}
		self.hop_subs = {}
		self.hop_styles = {}

		#
		# It would be good to enable populated structures as per above
		# however no free source has been found. Therefore the data is 
		# separated out into the embargodata file and included here.
		#
		haveEmbargoData=0
		try:	
			ed = brewerslabEmbargoData()
			haveEmbargoData=1
		except:
			pass

		if haveEmbargoData:
			self.hop_descriptions = ed.hop_descriptions
			self.hop_alphas = ed.hop_alphas
			self.hop_subs = ed.hop_subs
			self.hop_names = ed.hop_names
			self.hop_styles = ed.hop_styles
		
			self.fermentable_names = ed.fermentable_names
			self.fermentable_details = ed.fermentable_details
			self.fermentable_descriptions = ed.fermentable_descriptions
				
			self.buildFermentableObjects()
			self.buildHopObjects()





		# This won't really be the presets but the real objects
		if userid != "":	sep="/"
		if userid == "":	sep=""

		if userid != "":
			try: 
				os.mkdir("presets/%s" %(userid))
			except:
				pass

		self.presetfile = "presets/%s%spreset" %(userid,sep)
		self.preset_dir = "presets/%s%s" %(userid,sep)
		
		if os.path.exists( self.presetfile ):
			o=open( self.presetfile )
			pickledata = pickle.loads( o.read() )
			o.close()

			self.fermentable_objs = pickledata[0]
			self.hop_objs = pickledata[1]	
			self.yeast_objs = pickledata[2]
			self.misc_objs = pickledata[3]
			self.suppliers = pickledata[4]
			self.equipment_objs = pickledata[5]
			self.consumable_objs = pickledata[6]


	def save(self):
		
		pickledata=[]
		pickledata.append(self.fermentable_objs)
		pickledata.append(self.hop_objs)
		pickledata.append(self.yeast_objs)
		pickledata.append(self.misc_objs)
		pickledata.append(self.suppliers)
		pickledata.append(self.equipment_objs)
		pickledata.append(self.consumable_objs)

	
		o=open( self.presetfile ,"w")
		o.write( pickle.dumps( pickledata ) )
		o.close()

		
		o=open( "%s.autobackup_%s_preset" %(self.preset_dir,time.time()),"w")
		o.write( pickle.dumps( pickledata ) )
		o.close()
	

	def __del__(self):

		self.save()


	def dumpDetailJSON(self,category,ingredi):
		if category == "fermentable":	dict1=self.fermentable_objs
		if category == "hops":	dict1=self.hop_objs
		if category == "yeast":	dict1=self.yeast_objs
		if category == "misc":	dict1=self.misc_objs
		if category == "consumable":	dict1=self.consumable_objs

		r = re.compile("[^a-zA-Z0-9]")
		return { 'ingredient' : dict1[r.sub('',ingredi).lower()].dumpJSON() }

	def dumpJSON(self,category):
		result = []
		dict1=[]
		if category == "fermentable":	dict1=self.fermentable_objs
		if category == "hops":	dict1=self.hop_objs
		if category == "yeast":	dict1=self.yeast_objs
		if category == "misc":	dict1=self.misc_objs
		if category == "consumable":	dict1=self.consumable_objs
	
	
		for ingredient in dict1:
			print dict1[ingredient].name,ingredient	
			result.append(dict1[ingredient].name)
		result.sort()

		return {'ingredients' : result } 


	def listFermentable(self, fermentableName = ""):
		""" Returns a list of grains, matching an optional filter """
		return self.listMisc( fermentableName, self.fermentable_objs )
	
	def listMisc(self, miscName = "", dict1=None):
		if not dict1:	dict1=self.misc_objs
		""" Returns a list of other items, matching an optional filter """
		r = re.compile("[^a-z0-9]")

		misc_names = r.sub( '', miscName.lower() )
		
		result = []
		for misc in dict1:
			if dict1[misc].name.count( miscName ):
				result.append( (dict1[ misc ].name,  misc  ) )

		return result


	def listHops(self, hopName = ""):
		""" Returns a list of hop items, matching an optional filter """
		return self.listMisc( hopName, self.hop_objs )

	def listYeast(self, yeastName = ""):
		""" Returns a list of hop items, matching an optional filter """
		return self.listMisc( yeastName, self.yeast_objs )

	def listConsumables(self, consumableName = ""):
		""" Returns a list of hop items, matching an optional filter """
		return self.listMisc( consumableName, self.consumable_objs )

	

	def haveFermentable(self,fermentableName):
		return self.haveMisc( fermentableName, self.fermentable_objs)


	def haveMisc(self,miscName,dict1=None):
		if not dict1:	dict1= self.misc_objs
		""" Check if we have a grain """
		r = re.compile("[^a-z0-9]")

		misc_name = r.sub( '', miscName.lower() )

		if dict1.has_key( misc_name ):	return True
		return False


	def haveHop(self,hopName):
		return self.haveMisc( hopName, self.hop_objs)

	def haveYeast(self,yeastName):
		return self.haveMisc( yeastName, self.yeast_objs)


	def getFermentable(self,fermentableName,extract=0,ebc=None):
		""" return our fermentable object or build a new one """
		r = re.compile("[^a-z0-9]")

		fermentable_name = r.sub( '', fermentableName.lower() )
		if self.fermentable_objs.has_key( fermentable_name ):
			return self.fermentable_objs[ fermentable_name ]
		else:
#			if fermentableName.count("eat"):			print "HOW MANY TIMES ",fermentableName
			fermentable =brwlabFermentable( fermentableName )
			fermentable.pre_exist=0
			self.fermentable_objs[ fermentable_name ] = fermentable
			fermentable.calculateFromYield( extract )
			fermentable.colour = ebc
			return fermentable


	def getMisc(self,miscName, dict1 = None, objtype = None, sentDict=0):
		if not sentDict:	dict1= self.misc_objs
		if not sentDict:	objtype=brwlabMisc
		""" return our misc object or build a new one """
		r = re.compile("[^a-z0-9]")

		misc_name = r.sub( '', miscName.lower() )

		# dict1 will be set to self.misc_objs by default
		if dict1.has_key( misc_name ):
			return dict1[ misc_name ]
		else:
			#objtype will be set to brwlabMisc by default
			misc = objtype( miscName )
			misc.pre_exist = 0
			dict1[ misc_name ] = misc

	
			return misc


	def getSupplier(self,supplierName):
		r = re.compile("[^a-z0-9]")
		supplier_name = r.sub( '', supplierName.lower() )
		if not self.suppliers.has_key(supplier_name):
			self.suppliers[ supplier_name] = brwlabSupplier()
			self.suppliers[ supplier_name].name=supplierName

		return self.suppliers[supplier_name]

	def getHop(self,hopName,alpha=0):
		r = re.compile("[^a-z0-9]")

		#hopNameWithAlpha = "%s - %.1f %%" %(hopName,alpha)

		#hop_name = r.sub( '', hopNameWithAlpha.lower() )

		hop_name = r.sub( '', hopName.lower() )
	
		if self.hop_objs.has_key( hop_name ):
			return self.hop_objs[ hop_name ]
		else:
			hop =brwlabHop( "%s" %(hopName)  )
			hop.alpha=alpha
			hop._validate()
			hop.pre_exist=0
		
			self.hop_objs[ hop_name ] = hop
			return hop

	def getYeast(self,yeastName):
		return self.getMisc( yeastName, self.yeast_objs, brwlabYeast,1)

	def getEquipment(self,equipmentName):
		return self.getMisc( equipmentName, self.equipment_objs, brwlabEquipment,1)

	def getConsumable(self,consumableName):
		return self.getMisc( consumableName, self.consumable_objs, brwlabConsumable,1)




	"""	
		Real Presets
	"""


	def buildFermentableObjects(self):
		"""
		Build a Fermentable Object with the data we have
		Extract details to 0 if we don't already have the preset.
		"""
		for fermentable_name in self.fermentable_names:
			fermentableName = self.fermentable_names[ fermentable_name ]
			fermentable = brwlabFermentable( fermentableName )
			self.fermentable_objs[ fermentable_name ] = fermentable
			fermentable.isGrain =1
			
			if self.fermentable_details.has_key( fermentable_name ):
				(extract,ebc,mash,aromatic,biscuit,body,burnt,caramel,chocolate,coffee,grainy,head,malty,nutty,roasted,smoked,sweet,toasted,isGrain) = self.fermentable_details[ fermentable_name ]	
				if isGrain:
					fermentable.isGrain=1
					fermentable.isAdjunct=0	
				else:
					fermentable.isGrain=0
					fermentable.isAdjunct=1
				fermentable.calculateFromYield( extract )
				fermentable.colour = ebc
				fermentable.mustMash = mash
				fermentable.aromatic = aromatic
				fermentable.biscuit= biscuit
				fermentable.body = body
				fermentable.burnt = burnt
				fermentable.caramel = caramel
				fermentable.chocolate = chocolate
				fermentable.coffee = coffee
				fermentable.grainy = grainy
				fermentable.head = head
				fermentable.malty = malty
				fermentable.nutty = nutty
				fermentable.roasted = roasted
				fermentable.smoked = smoked
				fermentable.sweet = sweet
				fermentable.toasted = toasted
				if self.fermentable_descriptions.has_key( fermentable_name ):
					fermentable.description = self.fermentable_descriptions[ fermentable_name ]

	

	
	def buildHopObjects(self):
		"""
		Build a Hop Object with the data.
		"""
		for hop_name in self.hop_names:
			if self.hop_alphas.has_key( hop_name ):
				hop = brwlabHop( self.hop_names[ hop_name ] )
				self.hop_objs[ hop_name ] = hop		
				if self.hop_alphas.has_key( hop_name ):
					hop.alpha = self.hop_alphas[ hop_name ]
				hop._validate()
				if self.hop_descriptions.has_key( hop_name ):
					hop.description = self.hop_descriptions[ hop_name ]
				if self.hop_subs.has_key( hop_name ):
					hop.substitution = []
					for sub in self.hop_subs[ hop_name ]:	
						hop.substitution.append( sub )
				if self.hop_styles.has_key( hop_name ):
					hop.styles = []
					for style in self.hop_styles[ hop_name ]:
						hop.styles.append( style )	


		# We don't have a preset we might make it
		if not self.hop_names.has_key( hop_name ):
			# if we have haven't specified the hop alpha value we can't 
			# create a hop object.
			if not alpha:	return None
			hop = brwlabHop( hopName )
			hop.alpha = alpha


		return hop
			
if __name__ == '__main__':
 
	presets = brwlabPresetData()
	hop = presets.getHop("Cascade")
	hop.dump()

