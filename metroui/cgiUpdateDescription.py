#!/usr/bin/python
import sys
import _mysql	
import json
import cgi
import re
import mysql.connector
form=cgi.FieldStorage()


con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
cursor=con.cursor()
cursor.execute("update gRecipes set description ='%s' where recipeName='%s';" %( _mysql.escape_string( form['description'].value), form['recipeName'].value))
cursor.close()

print "Location: editRecipe.py?recipeName=%s\n" %(form['recipeName'].value)

