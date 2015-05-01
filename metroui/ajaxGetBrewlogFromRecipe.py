#!/usr/bin/python
import sys
import cgi
import re
import mysql.connector
con=mysql.connector.connect(user='root',database="brewerslab")
#sys.stdout.write("Content-Type:text/plain\n\n")
from cloudNG import *
sys.stdout.write("Content-Type:text/xml\n\n")
form=cgi.FieldStorage()
cursor=con.cursor()
cursor.execute("select entity,brewlog,recipe FROM gBrewlogs WHERE recipe ='%s' ORDER BY entity" %(form['recipe'].value))
i=0
sys.stdout.write("<xml>\n")
for row in cursor:
	(entity,brewlog,recipe)=row
	sys.stdout.write("<brewlog%s>%s</brewlog%s>\n" %(i,brewlog,i))
	i=i+1
sys.stdout.write("<brewlogs>%s</brewlogs>" %(i))

def xmlsafe(text):
	text=re.compile("[\n\r]").sub("</br>",text)
	
	safe=re.compile("<").sub("{:leftbracket:}",  re.compile(">").sub("{:rightbracket:}",  re.compile("&").sub("{:ampersand:}", re.compile("/").sub("{:forwardslash:}", text ) )  ) )

	return text

sys.stdout.write("</xml>")
sys.stdout.flush()

