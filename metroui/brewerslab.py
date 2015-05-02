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

db=_mysql.connect(host="localhost",user="brewerslab",password='beer',db="brewerslab")


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
	grid['0000_newBrewlog'] = {'url2' : 'createBrewlog.py?recipeName=%s' %(form['recipeName'].value),'text':'{ New Brewday }'}
	grid['0000_editRecipe'] = {'url2' : 'editRecipe.py?recipeName=%s' %(form['recipeName'].value),'text':'{ Edit Recipe }'}

	cursor=db.query("select recipe,brewlog from gBrewlogs WHERE recipe ='%s' ORDER BY brewlog" %(form['recipeName'].value))
	result=db.use_result()
	row=result.fetch_row()
	while row:
		
		((recipeName,brewlog),)=row
		grid[ brewlog ]={'url2':'brewlog.py?recipeName=%s&brewlog=%s' %(form['recipeName'].value, brewlog),'text':'%s' %(brewlog)}
		row=result.fetch_row()



theme.presentHead()
theme.presentBody()
theme.doGrid(grid)
theme.presentFoot()

