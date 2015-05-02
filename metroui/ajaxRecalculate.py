#!/usr/bin/python
import re
import sys
import cgi
import _mysql
import mysql.connector
from thememetro import *
from cloudNG import *
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/xml\n\n")
grid={}
db=_mysql.connect(host="localhost",user="root",db="brewerslab")
print "<xml><junk>"

bc=brewerslabCloudApi()
#bc.calculateRecipe("test@example.com", form['recipe'].value)
#bc.compile("test@example.com", form['recipe'].value,None)
bc.calculateRecipeWrapper("test@example.com",form['recipe'].value)

print "</junk><complete>1</complete></xml>"
