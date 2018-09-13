#!/usr/bin/python
import re
import sys
import cgi
import _mysql
import mysql.connector
from thememetro import *
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
con2=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
if form.has_key("noheader"):
	theme.noHeader=True
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
if not form.has_key("noheader"):
	theme.pagetitle="%s - Calcualtion" %(form['recipeName'].value)
	theme.goBackHome="javascript:window.history.go(-1)"
	theme.bodytitle="%s - Calclog" %(form['recipeName'].value)
theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")

export=False
if form.has_key("export"):	export=True

colWidth=100
if export:
	colWidth=10
theme.presentBody()



cursor=con.cursor()
cursor.execute("select recipeName,description from gRecipes WHERE recipeName = '%s' ;" %(form['recipeName'].value))
for row in cursor:
	(recipe,description)=row
cursor.close()
print "<div class=\"container\">"



print """


            <div class="grid fluid">

                <div class="row">
                    <div class="span12">
"""
print """
<tt>
""" 

cursor=con.cursor()
cursor.execute("select recipe,calclog FROM gCalclogs WHERE recipe = '%s' ORDER BY entity DESC LIMIT 0,1" %(form['recipeName'].value))
for row in cursor:
	(recipe,calclog)=row
	print "%s" %(re.compile(" ").sub('&nbsp;',re.compile("[\n\r]").sub('<BR>', calclog)))
cursor.close()

print """

		</p>
		</div>
    </div>
"""


