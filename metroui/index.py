#!/usr/bin/python
import re
import sys
import time
import cgi
import _mysql
import mysql.connector
from thememetro import *
con=mysql.connector.connect(user='root',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
theme.pagetitle="Brewerslab" 
#theme.goBackHome="index.py"
#theme.bodytitle="Stores"
theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="root",db="brewerslab")

theme.presentBody()
print "<div class=\"container\">"



print """
    <div class="carousel" data-role="carousel">
    <div class="slide">
    	<div class='bg-darkCobalt' style='height:100%;'>
		<h1><a href="stores.py">Stores</a></h1>
	</div>	
    </div>
    <div class="slide">
    	<div class='bg-darkMagenta' style='height:100%;'>
		<h1><a href="brewerslab.py">Recipes</a></h1>
	</div>	
    </div>
     
    <a class="controls left"><i class="icon-arrow-left-3"></i></a>
    <a class="controls right"><i class="icon-arrow-right-3"></i></a>
    </div>

"""
print "</div>"
theme.presentFoot()

