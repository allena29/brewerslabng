from __future__ import division


from ngData import *

r=db().GqlQuery("SELECT * FROM gIngredients WHERE owner ='test@example.com' AND recipename = 'Citra'")
for ingredient in r.fetch(324234):
	ingredient.brief()
	sys.stderr.write( "%s" %(ingredient.isGrain ))
	sys.stderr.write("\n")

"""
			ourRecipes = db().GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeNewName)
			for recipe in ourRecipes.fetch(2000):
				recipe.delete()

			ourRecipes = db().GqlQuery("SELECT * FROM gRecipes WHERE owner = :1 AND recipename = :2", username,recipeOrigName)
			for recipe in ourRecipes.fetch(2000):
				R=gRecipes(recipename=recipeNewName,owner=username )
				for ri in recipe.__dict__:
					if ri != "entity" and ri != "recipename":
						R.__dict__[ri] = recipe.__dict__[ri]
				R.recipename=recipeNewName
				R.put()	

			ourIngredients = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = :3", username,recipeNewName,0)
			for ingredient in ourIngredients.fetch(2000):
				ingredient.delete()
						

			sys.stderr.write("harrypotter\n")


			ourIngredients = db().GqlQuery("SELECT * FROM gIngredients WHERE owner = :1 AND recipename = :2 AND processIngredient = :3", username,recipeOrigName,0)
			for ingredient in ourIngredients.fetch(2000):
				sys.stderr.write("IIII %s\n" %(ingredient.ingredient))
				I=gIngredients(recipename=recipeNewName,owner=username )
				for ii in ingredient.__dict__:
					if ii != "entity" and ii != "recipename":
						I.__dict__[ii] = ingredient.__dict__[ii]
				sys.stderr.write("gIngredients ---> ingredient.mustMash %s " %(ingredient.mustMash))
				sys.stderr.write("gIngredients ---> I.mustMash %s" %(I.mustMash))
				I.recipename=recipeNewName
				I.put()	
				sys.stderr.write("gIngredients ---> I.mustMash %s (after post)" %(I.mustMash))


			# fix for broken recipes
			errstatus = self.doCalculate(username,recipeNewName)	#calculate new rceipe
			errstatus = self.compile(username,recipeNewName,None)  #compile new recipe

			status=1
		except:
			sys.stderr.write("EXCEPTION in cloneRecipe\n")
			exc_type, exc_value, exc_traceback = sys.exc_info()
			for e in traceback.format_tb(exc_traceback):	sys.stderr.write("\t%s" %( e))
		
		return {'operation' : 'cloneRecipe', 'status' : status ,'json':{}}

"""
