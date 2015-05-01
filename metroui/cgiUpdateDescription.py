#!/usr/bin/python
import sys
import _mysql	
import json
import cgi
import re
import mysql.connector
#con=mysql.connector.connect(user='root',database="brewerslab")
#sys.stdout.write("Content-Type:text/plain\n\n")
form=cgi.FieldStorage()


con=mysql.connector.connect(user='root',database="brewerslab")
cursor=con.cursor()
cursor.execute("update gRecipes set description ='%s' where recipeName='%s';" %( _mysql.escape_string( form['description'].value), form['recipeName'].value))
cursor.close()

print "Location: editRecipe.py?recipeName=%s\n" %(form['recipeName'].value)

