#!/usr/bin/python
import time
import re
import sys
import cgi
import _mysql

from ngData import *


form=cgi.FieldStorage()
results2 = db().GqlQuery("SELECT * FROM gBrewlogs WHERE brewlog = :1", form['brewlog'].value)
result2 = results2.fetch(1)


recipename=result2[0].recipe
ownername=result2[0].owner
brewlogname=result2[0].brewlog
results=db().GqlQuery("SELECT * FROM gRecipes WHERE recipename = :1 AND owner = :2", recipename,ownername)
result = results.fetch(1)
recipe=result[0]
brewlog=result2[0]
		
# new
results=db().GqlQuery("SELECT * FROM gRecipeStats WHERE brewlog = :1 AND owner = :2", form['brewlog'].value,ownername)
recipeStats = results.fetch(1)[0]


boilTime=60
results  = db().GqlQuery("SELECT * FROM gIngredients WHERE recipename = :1 AND ingredientType = :2 ORDER BY hopAddAt DESC", recipename, "hops").fetch(1)
try:
	boilTime=results[0].hopAddAt
except:
	pass

if not form.has_key("xml"):
	sys.stdout.write("Content-Type: text/html\n\n")
	sys.stdout.write("""
<html>
    <head>
        <link rel="stylesheet" href="css/mymetro.css">
        <link rel="stylesheet" href="Metro.UI.CSS.2.0.1/css/metro-bootstrap.css">
	<script src="js/utils.js"> </script>
	<script src="js/wwwajax.js"> </script>
    </head>
    <body marginwidth=0 marginheight=0 class="mymetro">
<a name="top"></a>

<div class="metro" id="wrapper">
		<nav class="navigation-bar dark">
		    <nav class="navigation-bar-content" style='align: right'>
				<div class="element">
					Android App <a href='https://play.google.com/store/apps/details?id=net.collie.mellon.aaa.recipeviewer'>available on Android Market</a><br>
				</div>
				<div class="element">
					<a href='?xml=1&brewlog=%s'>xml</a> 
				</div>

			</nav>
		</nav>
""" %(form['brewlog'].value))
	sys.stdout.write("""<h1>%s</h1>""" %(brewlog.realrecipe))



	sys.stdout.write("""

	<div class='metro' style='padding-left: 50px'>

		<table width=50%%><tr><td>Recipe Type</td><td> %s</td></tr>
		<tr><td>Brewer</td><td>%s</td></tr>
		<tr><td>Batch Size</td><td>%s L</td></tr>
		<tr><td>Boil Size</td><td>%s L</td></tr>
		<tr><td>Boil Time</td><td>%s</td></tr>
		<tr><td>Efficiency</td><td>%s %%</td></tr>
		""" %(recipe.recipe_type,recipe.credit,recipe.batch_size_required,recipeStats.boil_vol, boilTime, recipe.mash_efficiency))
	if recipe.forcedstyle:
		sys.stdout.write("""
			<tr><td>Style</td><td> %s</td></tr>""" %(recipe.forcedstyle))
	else:
		sys.stdout.write("""
			<tr><td>Style</td><td><a href="http://www.bjcp.org/2008styles/style%s.php#1%s">%s%s<a?</td></tr>""" %(recipe.stylenumber,recipe.styleletter.lower(),recipe.stylenumber,recipe.styleletter))

	sys.stdout.write("""
		<tr valign=top><td>Notes</td><td> %s</td></tr>""" %(recipe.description))
	sys.stdout.write("""
		<tr><td>Estimated Original Gravity</td><td> %.3f</td></tr>
		<tr><td>Estimated Final Gravity</td><td>%.3f</td></tr>""" %(recipe.estimated_og,recipe.estimated_fg))
	try:
		results=db().GqlQuery("SELECT * FROM gField WHERE brewlog = :1 AND fieldKey = :2", brewlogname,"og")
		result=results.fetch(1)[0]
		sys.stdout.write("""<tr><td>Original Gravity</td><td> %.3f</td></tr>""" %( float(result.fieldVal)))
	except ImportError:
		pass

	try:
		results=db().GqlQuery("SELECT * FROM gField WHERE brewlog = :1 AND fieldKey = :2", brewlogname,"__measuredFg_abv")
		result=results.fetch(1)[0]
		sys.stdout.write("""<tr><td>Final Gravity</td><td> %.3f</td></tr>""" %( float(result.fieldVal)))
	except:
		pass


	if int(result2[0].brewdate2) > 0:
		sys.stdout.write("""<tr><td>Brew Date</td><td> %s - %s</td</tr>""" %(time.ctime(float(result2[0].brewdate)),time.ctime(float(result2[0].brewdate2 ))))
	elif int(result2[0].brewdate) > 0:
		sys.stdout.write("""<tr><td>Brew Date</td><td> %s</td></tr>""" %(time.ctime(float(result2[0].brewdate))))
	if int(result2[0].bottledate) > 0:
		sys.stdout.write("""<tr><td>Bottle Date</td><td> %s</td></tr>""" %(time.ctime(float(result2[0].bottledate ))))



	overheadperlitre=0
	try:
		dbx=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		cursor=dbx.query("select breweryname,overheadperlitre FROM gBrewery LIMIT 0,1")
		result=dbx.use_result()
		row=result.fetch_row()
		i=0
		((breweryname,overheadperlitre),)=row
		sys.stdout.write("""<tr><td>Brewery</td><td>%s</td></tr>""" %(breweryname))
	except:
		pass	



	results = db().GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2", ownername,brewlogname).fetch(1000)
	totalcost=0
	for result in results:
		if not (result.subcategory == "bottle" or result.subcategory == "keg"):
			totalcost=totalcost+result.cost
	totalcost=totalcost+(float(recipe.batch_size_required)*float(overheadperlitre))
	sys.stdout.write("""<tr><td>Brew Cost</td><td>  &#163; %.2f</td></tr>""" %( totalcost ))

	sys.stdout.write("</table>")
	if result2[0].smallImage:
		sys.stdout.write("""<div style='padding-left: 100px'>		<a href="%s"><img src="%s" border=0></a></div>""" %(result2[0].largeImage,result2[0].smallImage ))



	sys.stdout.write("""<h2>Fermentables</h2>""" )
	sys.stdout.write("<table  width=40%%><tbody class='bordered'><tr><th align=\"left\">Fermentable</th><th align=left>Qty</th></tr>")
	# Grain Bill		
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",False )
	grains = query.fetch(4324234)
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",True)
	adjuncts = query.fetch(4324234)


	for grain in grains:	
		sys.stdout.write("""<tr><td>%s (grain)</td><td>%.1f gm</td></tr>""" %(grain.ingredient,grain.qty))

	for adjunct in adjuncts:	
		sys.stdout.write("""<tr><td>%s (adjunct)</td><td>%.1f gm</td></tr>				""" %(adjunct.ingredient,adjunct.qty))

	sys.stdout.write("</tbody></table>")


	# hops Bill		
	sys.stdout.write("""<h2>Hops</h2>""" )
	sys.stdout.write("<table  width=40%%><tbody class='bordered'><tr><th align=\"left\">Hop</th><th align=left>Alpha Acid %</th><th align=left>Use</th><th align=left>Qty</th></tr>")
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4 ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0)
	hops = query.fetch(4324234)

	hop_labels = {60:'Copper',15:'Aroma',5:'Finishing',0.001:'Flameout',0.009:'Dryhop'}

	for hop in hops:	
		if hop_labels.has_key(hop.hopAddAt):
			hopUse=hop_labels[hop.hopAddAt]
		else:
			hopUse=""
		sys.stdout.write("""<tr><td>%s</td><td>%.1f %%</td><td>%s %.0f min</td><td>%.1f gm</td></tr>""" %(hop.ingredient,hop.hopAlpha,hopUse,hop.hopAddAt,hop.qty))

	sys.stdout.write("</table>")


	# Yeast Bill		
	sys.stdout.write("""<h2>Yeast</h2>""" )
	sys.stdout.write("<table  width=40%%><tbody class='bordered'><tr><th align=\"left\">Yeast</th><th align=left>Qty</th></tr>")
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3", ownername,recipename, "yeast")
	yeasts = query.fetch(4324234)
	for yeast in yeasts:	
		sys.stdout.write("""<tr><td>%s</td><td>%.0f pkt</td></tr>""" %(yeast.ingredient,yeast.qty))
	sys.stdout.write("</table>")

	
	# Mash
	sys.stdout.write("""<h2>Mash</h2>""")
	sys.stdout.write("""<b>Mash Temp</b> %.1fdegC, <b>Thickness Ratio</b> %.2f
	""" %(recipe.target_mash_temp,1.25))

	mashStart=None
	mashEnd=None
	try:
		query  = db().GqlQuery("SELECT * FROM gField WHERE brewlog = :1 AND fieldKey = :2", brewlogname, "mash_start_temp")
		mash = query.fetch(324)
		mashStart=float(mash[0].fieldVal)
	except:
		pass	
	try:
		query  = db().GqlQuery("SELECT * FROM gField WHERE brewlog = :1 AND fieldKey = :2", brewlogname, "mash_end_temp")
		mash = query.fetch(324)
		mashEnd=float(mash[0].fieldVal)
	except:
		pass	

	if mashStart or mashEnd:
		sys.stdout.write("<BR>")
		if mashStart:
			sys.stdout.write("<b>Mash Start Temp:</b> %.1f deg c<BR>" %(mashStart))
		if mashEnd:
			sys.stdout.write("<b>Mash End Temp:</b> %.1f deg c<BR>" %(mashEnd))

	sys.stdout.write("""<p></div>
</div>
</body>
</html>
""")



if form.has_key("xml"):
#	sys.stdout.write("Content-Type: text/plain\n\n")
	sys.stdout.write("Content-Type: text/xml\n\n")
	sys.stdout.write("<RECIPES>\n <RECIPE>\n")
	sys.stdout.write("""
				<NAME>%s</NAME>
				<TYPE>%s</TYPE>
				<BREWER>%s</BREWER>
				<DISPLAY_BATCH_SIZE>%s L</DISPLAY_BATCH_SIZE>
				<DISPLAY_BOIL_SIZE>%s L</DISPLAY_BOIL_SIZE>
				<BOIL_TIME>%s</BOIL_TIME>
				<EFFICIENCY>%s</EFFICIENCY>
""" %(brewlog.realrecipe,recipe.recipe_type,recipe.credit,recipe.batch_size_required,recipeStats.boil_vol, boilTime, recipe.mash_efficiency))
	if recipe.forcedstyle:
		sys.stdout.write("""
			<STYLE>
				<NAME>%s</NAME>""" %(recipe.forcedstyle))

		if recipe.styleversion:	sys.stdout.write("			<STYLE_GUIDE>%s</STYLE_GUIDE>\n" %(recipe.styleversion))
		if recipe.stylenumber:	sys.stdout.write("			<CATEGORY_NUMBER>%s</CATEGORY_NUMBER>\n" %(recipe.stylenumber))
		if recipe.styleletter:	sys.stdout.write("			<STYLE_LETTER>%s</STYLE_LETTER>\n" %(recipe.styleletter))

		sys.stdout.write("""
			</STYLE>
""")
	else:
		sys.stdout.write("""<STYLE>
""")
		if recipe.styleversion:	sys.stdout.write("			<STYLE_GUIDE>%s</STYLE_GUIDE>\n" %(recipe.styleversion))
		if recipe.stylenumber:	sys.stdout.write("			<CATEGORY_NUMBER>%s</CATEGORY_NUMBER>\n" %(recipe.stylenumber))
		if recipe.styleletter:	sys.stdout.write("			<STYLE_LETTER>%s</STYLE_LETTER>\n" %(recipe.styleletter))

		sys.stdout.write("""
			</STYLE>
""")

	# Grain Bill		
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",False )
	grains = query.fetch(4324234)
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND isAdjunct = :4", ownername,recipename, "fermentables",True)
	adjuncts = query.fetch(4324234)
	if len(grains) > 0 or len(adjuncts) > 0 :
		sys.stdout.write("""
			<FERMENTABLES>""")	

	for grain in grains:	
		sys.stdout.write("""
				<FERMENTABLE>
					<NAME>%s</NAME>
					<TYPE>grain</TYPE>
					<AMOUNT>%.5f</AMOUNT>
				</FERMENTABLE>""" %(grain.ingredient,grain.qty/1000))

	for adjunct in adjuncts:	
		sys.stdout.write("""
				<FERMENTABLE>
					<NAME>%s</NAME>
					<TYPE>%s</TYPE>
					<AMOUNT>%.5f</AMOUNT>
				</FERMENTABLE>""" %(adjunct.ingredient,"Adjunct",adjunct.qty/1000))


	if len(grains) > 0 or len(adjuncts) > 0:
		sys.stdout.write("""
			</FERMENTABLES>""")	



	# hops Bill		
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3 AND hopAddAt >= :4 ORDER BY hopAddAt DESC", ownername,recipename, "hops", 0.0)
	hops = query.fetch(4324234)
	if len(hops) > 0:
		sys.stdout.write("""
			<HOPS>""")	



	for hop in hops:	
		sys.stdout.write("""
				<HOP>
					<NAME>%s</NAME>
					<FORM>%s</FORM>
					<ALPHA>%.2f</ALPHA>
					<AMOUNT>%.5f</AMOUNT>
					<USE>%s</USE>
					<TIME>%.1f</TIME>
				</HOP>""" %(hop.ingredient, hop.hopForm,hop.hopAlpha,hop.qty/1000,hop.hopUse,hop.hopAddAt))

	if len(hops) > 0:
		sys.stdout.write("""
			</HOPS>""")	




	# Yeast Bill		
	query  = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND ingredientType = :3", ownername,recipename, "yeast")
	yeasts = query.fetch(4324234)
	if len(yeasts) > 0:
		sys.stdout.write("""
			<YEASTS>""")	



	for yeast in yeasts:	
		sys.stdout.write("""
				<YEAST>
					<NAME>%s</NAME>
					<AMOUNT>%.5f</AMOUNT>
				</YEAST>""" %(yeast.ingredient, 11*yeast.qty/1000 ))

	if len(yeasts) > 0:
		sys.stdout.write("""
			</YEASTS>""")	




	sys.stdout.write("""
		<NOTES>%s</NOTES>""" %(recipe.description))
	sys.stdout.write("""
		<OG>%.4f</OG>
		<FG>%.4f</FG>""" %(recipe.estimated_og,recipe.estimated_fg))

	sys.stdout.write("""
	</RECIPE>""")

	#
	#	 Mash 
	#
	sys.stdout.write("""
		<MASHS>
			<MASH>
				<MASH_STEPS>
					<MASH_STEP>
						<NAME>Saccharification</NAME>
						<TYPE>Infusion</TYPE>
						<DESCRIPTION>Mash Temp %.1fdegC, Thickness Ratio %.2f </DESCRIPTION>
					</MASH_STEP>
				</MASH_STEPS>
			</MASH>
		</MASHS>
	""" %(recipe.target_mash_temp,1.25))

	#
	#	Our exetensions to add some brewlog bits into the recipe
	#
	#
	sys.stdout.write("""
<EXTENSION>""")

	
	# Brew Day

	if result2[0].brewdate2 > 0:
		sys.stdout.write("""		<brewDateEnd>%s</brewDateEnd>""" %(result2[0].brewdate2 ))
	if result2[0].brewdate > 0:
		sys.stdout.write("""		<brewDate>%s</brewDate>""" %(result2[0].brewdate ))
	if result2[0].bottledate > 0:
		sys.stdout.write("""		<bottleDate>%s</bottleDate>""" %(result2[0].bottledate ))

	if result2[0].smallImage:
		sys.stdout.write("""		<smallLabel>%s</smallLabel>""" %(result2[0].smallImage ))

	if result2[0].largeImage:
		sys.stdout.write("""		<bigLabel>%s</bigLabel>""" %(result2[0].largeImage ))


	try:
		results=db().GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND  fieldKey = :3", ownername,brewlogname,"og")
		result=results.fetch(1)[0]
		sys.stdout.write("""		<ACTUAL_OG>%.4f</ACTUAL_OG>""" %( float(result.fieldVal)))
	except:
		pass

	try:
		results=db().GqlQuery("SELECT * FROM gField WHERE owner = :1 AND brewlog = :2 AND fieldKey = :3", ownername,brewlogname,"__measuredFg_abv")
		result=results.fetch(1)[0]
		sys.stdout.write("""		<ACTUAL_FG>%.4f</ACTUAL_FG>""" %( float(result.fieldVal)))
	except:
		pass

#			x=gBrewery(owner="test@example.com")
#			x.breweryname="Wards View Brewing"
#			x.overheadperlitre=0.25
#			x.put()
	overheadperlitre=0
	try:
		dbx=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		cursor=dbx.query("select breweryname,overheadperlitre FROM gBrewery LIMIT 0,1")
		result=dbx.use_result()
		row=result.fetch_row()
		i=0
		((breweryname,overheadperlitre),)=row
		sys.stdout.write("""<BREWERY_NAME>%s</BREWERY_NAME>\n""" %(breweryname))
	except:
		pass	




	

	results = db().GqlQuery("SELECT * FROM gBrewlogStock WHERE owner = :1 AND brewlog = :2", ownername,brewlogname).fetch(1000)
	totalcost=0
	for result in results:
		if not (result.subcategory == "bottle" or result.subcategory == "keg"):
			totalcost=totalcost+result.cost
	totalcost=totalcost+(float(recipe.batch_size_required)*float(overheadperlitre))
	sys.stdout.write("""		<BREW_COST>%.2f</BREW_COST>""" %( totalcost ))
	sys.stdout.write("""
</EXTENSION>\n</RECIPES>""")


