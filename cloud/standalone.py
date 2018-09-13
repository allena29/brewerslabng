from __future__ import division

from cloudNG import *
from standalonetools import standaloneTool


cloud =brewerslabCloudApi()
tools=standaloneTool()
tools.db=cloud.dbWrapper
tools.importProcess("../process/allena29/18AG15i16")


#	c.standalonemode=True
#	c.standalonemode=True





recipe=gRecipes()
recipe.db=cloud.dbWrapper		# needed to enable shim
recipe.owner="standalone"
recipe.credit="Adam Allen"
recipe.description="Quick mockup of a SMASH for Cascade"
recipe.recipename="CascadeSHPA"
recipe.batch_size_required=22
recipe.postBoilTopup=4
recipe.process="18AG15i16"	
recipe.target_mash_temp=68
recipe.initial_grain_temp=18
recipe.mash_grain_ratio=1.5
recipe.priming_sugar_qty=2
recipe.mash_efficiency=67
recipe.put()

#	

# should we statically import a pickle?
# given we imported the pickles - to Gql 
# and then converted the gql to mysql
# we probably should.
cascadeB=gIngredients()
cascadeB.db=cloud.dbWrapper
cascadeB.owner="standalone"
cascadeB.recipename=recipe.recipename
cascadeB.processIngredient=0
cascadeB.category="hops"
cascadeB.hopAddAt=60
cascadeB.hopAlpha=7
cascadeB.qty=50
cascadeB.unit="gm"
cascadeB.ingredient="cascade"
cascadeB.ingredientType="hops"
cascadeB.put()

cascadeA=gIngredients()
cascadeA.db=cloud.dbWrapper
cascadeA.owner="standalone"
cascadeA.ingredientType="hops"
cascadeA.recipename=recipe.recipename
cascadeA.processIngredient=0
cascadeA.hopAddAt=15
cascadeA.hopAlpha=7
cascadeA.qty=20
cascadeA.unit="gm"
cascadeA.ingredient="cascade"
cascadeA.put()

cascadeF=gIngredients()
cascadeF.db=cloud.dbWrapper
cascadeF.owner="standalone"
cascadeF.ingredientType="hops"
cascadeF.recipename=recipe.recipename
cascadeF.hopAddAt=0.001
cascadeF.hopAlpha=7
cascadeF.processIngredient=0
cascadeF.qty=30
cascadeF.unit="gm"
cascadeF.ingredient="cascade"
cascadeF.put()

marisotter=gIngredients()
marisotter.db=cloud.dbWrapper
marisotter.owner="standalone"
marisotter.ingredientType="fermentables"
marisotter.recipename=recipe.recipename
marisotter.ingredient="Maris Otter"
marisotter.qty=5000
marisotter.hwe=315
marisotter.processIngredient=0
marisotter.colour=5.73
marisotter.isGrain=1
marisotter.mustMash=1
marisotter.put()


torwheat=gIngredients()
torwheat.db=cloud.dbWrapper
torwheat.owner="standalone"
torwheat.ingredientType="fermentables"
torwheat.recipename=recipe.recipename
torwheat.ingredient="Torrified Wheat"
torwheat.qty=150
torwheat.hwe=299
torwheat.colour=2
torwheat.isGrain=1
torwheat.mustMash=1
torwheat.processIngredient=0
torwheat.put()

honey=gIngredients()
honey.db=cloud.dbWrapper
honey.owner="standalone"
honey.ingredientType="fermentables"
honey.recipename=recipe.recipename
honey.ingredient="Honey"
honey.qty=340
honey.hwe=340
honey.colour=4
honey.isGrain=0
honey.isAdjunct=1
honey.processIngredient=0
honey.mustMash=1
honey.put()


safales04=gIngredients()
safales04.owner="standalone"
safales04.recipename=recipe.recipename
safales04.db=cloud.dbWrapper
safales04.processIngredient=0
safales04.ingredientType="yeast"
safales04.atten=72
safales04.qty=1
safales04.ingredient="Safale S04"
safales04.put()
"""
c.yeasts=[]
c.yeasts.append(gIngredients())
c.yeasts[-1].atten=72

c.fermentation_bin = gEquipment()
c.fermentation_bin.dead_space=2
c.mash_tun=gEquipment()
c.mash_tun.dead_space=2.25
c.hlt=gEquipment()
c.hlt.dead_space=3
c.boilers=[]
c.boilers.append(gEquipment())
c.boilers[0].name="15l kettle"
c.boilers[0].dead_space=1.25
c.boilers[0].boilVolume=13
c.boilers.append(gEquipment())
c.boilers[1].name="20l kettle"
c.boilers[1].dead_space=1.25
c.boilers[1].boilVolume=16
c.Process=gProcess()
c.Process.percentage_boil_off=15
c.Process.percentage_cool_off=4
c.Process.name="17AG12i13"
#	c.doCalculate("test@example.com","green")
"""

#cloud.doCalculate("standalone","CascadeSHPA")
cloud.compile("standalone","CascadeSHPA","dummybrewlog")
#print cloud.calclog	
