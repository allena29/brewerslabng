#!/usr/bin/python
import re
import sys
import cgi
import _mysql
from thememetro import *
from cloudNG import *

form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")

grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")


if not form.has_key("recipeName"):

	theme.bodytitle="Select Recipe"
	cursor=db.query("select recipeName,description from gRecipes ORDER BY recipeName")
	result=db.use_result()
	row=result.fetch_row()
	while row:
		((recipeName,description),)=row
		grid[recipeName]={'url2':'brewerslab.py?recipeName=%s' %(recipeName),'text':'%s' %(recipeName)}
		row=result.fetch_row()
elif form.has_key("recipeName") and not form.has_key("brewlog"):
	theme.goBackHome="brewerslab.py?recipeName=%s" %(form['recipeName'].value)
	theme.bodytitle=" "
	if theme.localUser:
		grid['0000_newBrewlog'] = {'url2' : 'createBrewlog.py?recipeName=%s' %(form['recipeName'].value),'text':'{ New Brewday }'}

	if theme.localUser:
		grid['0000_editRecipe'] = {'url2' : 'editRecipe.py?recipeName=%s' %(form['recipeName'].value),'text':'{ Edit Recipe }'}
	else:
		grid['0000_editRecipe'] = {'url2' : 'editRecipe.py?recipeName=%s&export=1' %(form['recipeName'].value),'text':'{ View Recipe }'}

	cursor=db.query("select recipe,brewlog from gBrewlogs WHERE recipe ='%s' ORDER BY brewlog" %(form['recipeName'].value))
	result=db.use_result()
	row=result.fetch_row()
	while row:
		
		((recipeName,brewlog),)=row
		grid[ brewlog ]={'url2':'brewlog.py?recipeName=%s&brewlog=%s' %(form['recipeName'].value, brewlog),'text':'%s' %(brewlog)}
		row=result.fetch_row()






theme.presentHead()
theme.presentBody()
	
if not form.has_key("recipeName"):

	if theme.localUser:
		print """

			    <div class="grid fluid">
				<div class="row">
				    <div class="span8">
					</div>
			    <div class="span4">
				<div class="panel" data-role="panel">
				    <div class="panel-header bg-darkRed fg-white">
					Create New Recipe
				    </div>
				    <div class="panel-content" style="display:none">
					<form method=POST action='createRecipe.py'>
					<input type='text' name='newrecipe' id='newrecipe' value=''> <input type='submit' value='Create'>
					</form>
				    </div>
				</div>
			    </div>
			</div>
		</div>
	""" 
theme.doGrid(grid)


if form.has_key("recipeName") and not form.has_key("brewlog"):
	print "<p><h2>Recipe</h2>"
	from editRecipe import editRecipe
	r=editRecipe()
	r.recipeName=form['recipeName'].value
	r.localUser=False
	r.displayRecipe()
theme.presentFoot()

