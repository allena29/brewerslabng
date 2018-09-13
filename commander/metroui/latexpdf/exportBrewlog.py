brewlog="08.10.2016"
brewery="Worsdell Brewing"
recipeName="Wheat"

import time
import _mysql
import mysql.connector
db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
con2=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
con3=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
recipeCursor=db.query("select description,waterProfile FROM gRecipes WHERE recipename ='%s'" %(recipeName))
result=db.use_result()
row=result.fetch_row()
((recipeDescription,waterProfile),)=row


o=open("template.lex")
y=o.readline()
while y != "":
	y=y.rstrip()
	if y[1:8] == "title{}":
		print "\\title{Brewlog %s of %s by %s}" %(brewlog,recipeName,brewery)
	elif y == "[[recipedescription]]":
			
		for l in recipeDescription.split('\r\n'):
			print l,"\\\\"
	elif y == "[[fermentables-item-list]]":
		noItems=True
		cursor=con.cursor()
		cursor.execute("select entity,recipeName,ingredient,qty,mustMash,isGrain,isAdjunct,hwe,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = 'fermentables' ORDER BY qty DESC" %(recipeName))
		for row in cursor:
			(ent,recipe,ingredient,qty,mustMash,isGrain,isAdjunct,hwe,unit)=row
			if mustMash and isGrain:
				print "\\item %.0f %s of %s" %(qty,unit,ingredient)
				noItems=False
			row=result.fetch_row()
		cursor=con.cursor()
		cursor.execute("select entity,recipeName,ingredient,qty,mustMash,isGrain,isAdjunct,hwe,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = 'fermentables' ORDER BY qty DESC" %(recipeName))
		for row in cursor:
			(ent,recipe,ingredient,qty,mustMash,isGrain,isAdjunct,hwe,unit)=row
			if not mustMash and not isGrain:
				print "\\item %.0f %s of %s" %(qty,unit,ingredient)
				noItems=False
			noItems=False
			row=result.fetch_row()
		if noItems:
			print "\\item no fermentables	"


	elif y == "[[hops-item-list]]":
		itemType="hops"
		hop_values=[0.02,0.06,0.08,2,5,15,60,20.222]
		hop_labels = {60:'Copper (60min)',15:'Aroma (15min)',5:'Finishing (5min)',0.08:'Flameout (0min)',0.06:'Whirlpool/Hopback (0min)' , 0.02:'Dryhop',20.222:'First Wort Hop' , 2:'Spices'  }

		noItems=True
		for (hopAddAtA,hopAddAtB) in [ (20,21), (20.3,6000), (2.2,20.1), (1.5,2.1), (0,1.4) ]:
			cursor=con.cursor()
			cursor.execute("select entity,recipeName,ingredient,qty,hopAddAt,hopAlpha,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = '%s' AND hopAddAt >=%s and hopAddAt <=%s ORDER BY hopAddAt DESC,qty DESC" %(recipeName,itemType,hopAddAtA,hopAddAtB))
			for row in cursor:
				(ent,recipe,ingredient,qty,hopAddAt,hopAlpha,unit)=row
				if hop_labels.has_key(hopAddAt):
					print "\\item %.0f %s of %s (%.1f %%) for %s" %(qty,unit,ingredient, hopAlpha, hop_labels[hopAddAt] )
				else:
					print "\\item %.0f %s of %s (%.1f %%) for %s min" %(qty,unit,ingredient, hopAlpha, hopaddAt)
				noItems=False
				row=result.fetch_row()
		if noItems:
			print "\\item no hops	"


	elif y == "[[yeast-item-list]]":
		itemType="yeast"
		noItems=True
		cursor=con.cursor()
		cursor.execute("select entity,recipeName,ingredient,qty,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = 'yeast' ORDER BY qty DESC" %(recipeName))
		for row in cursor:
			(ent,recipe,ingredient,qty,unit)=row
			print "\\item %.0f %s of %s" %(qty,unit,ingredient)
			noItems=False
			row=result.fetch_row()
		if noItems:
			print "\\item no yeast	"


	elif y == "[[misc-item-list]]":
		itemType="yeast"
		noItems=True
		cursor=con.cursor()
		cursor.execute("select entity,recipeName,ingredient,qty,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = 'misc' AND category <> 'watertreat' ORDER BY qty DESC" %(recipeName))
		for row in cursor:
			(ent,recipe,ingredient,qty,unit)=row
			print "\\item %.0f %s of %s" %(qty,unit,ingredient)
			noItems=False
			row=result.fetch_row()
		if noItems:
			print "\\item no sundries	"



	elif y == "[[water-details]]":
		waterdetails=False
		cursor4=con3.cursor()
		cursor4.execute("select entity,ca,mg,na,co3,so4,cl,testdate,treatmentMethod FROM gWater WHERE profile=0 ORDER BY testdate DESC")
		for row4 in cursor4:
			(entity,xca,xmg,xna,xco3,xso4,xcl,wt,treatmentMethod)=row4
			waterdetails=True
		if not waterdetails:
			print "No water test details available"	
		else:
			d= time.strftime('%A %d %B %Y',time.localtime( wt  ) )

			print "The desired water profile for a \\textbf{%s} style is listed below, the \\textit{italic} values show the water as was tested on %s." %(waterProfile,d)
	elif y == "[[water-item-list]]":
		Ca=-1
		Mg=-1
		Na=-1
		CO3=-1
		SO4=-1
		Cl=-1
		if waterProfile:
			Ca=0
			Mg=0
			Na=0
			CO3=0
			SO4=0
			Cl=0
			ca=0
			mg=0
			na=0
			co3=0
			so4=0
			cl=0

			
			cursor=con.cursor()
			cursor.execute("select ca,mg,na,co3,so4,cl  FROM gWater WHERE description = '%s'" %(waterProfile))
			for row in cursor:
				(Ca,Mg,Na,CO3,SO4,Cl)=row
			cursor4=con3.cursor()
			cursor4.execute("select entity,ca,mg,na,co3,so4,cl,testdate,treatmentMethod FROM gWater WHERE profile=0 ORDER BY testdate DESC LIMIT 0,1")

				
			for row4 in cursor4:
				(entity,ca,mg,na,co3,so4,cl,wt,treatmentMethod)=row4
			print "\\item Calcium \\textbf{Ca} \\tab %.1f ppm \\tab \\textit{%.1f ppm}" %(Ca,ca)
			print "\\item Magnesium \\textbf{Mg} \\tab %.1f ppm \\tab \\textit{%.1f ppm}" %(Mg,mg)
			print "\\item Sodium \\textbf{Na} \\tab %.1f ppm \\tab \\textit{%.1f ppm}" %(Na,na)
			print "\\item Carbonate \\textbf{CO3} \\tab %.1f ppm \\tab \\textit{%.1f ppm}" %(CO3,co3)
			print "\\item Sulphate \\textbf{SO4} \\tab %.1f ppm \\tab \\textit{%.1f ppm}" %(SO4,so4)
			print "\\item Chloride \\textbf{Cl} \\tab %.1f ppm \\tab \\textit{%.1f ppm}" %(Cl,cl)

	else:
		print y
	y=o.readline()
o.close()
