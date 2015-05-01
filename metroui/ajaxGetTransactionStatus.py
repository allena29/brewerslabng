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
cursor.execute("select status,timestamp,recipeName,brewlog FROM gTransactions ORDER BY timestamp DESC LIMIT 0,1")
status="Not started"
for row in cursor:
	(status,timestamp,recipeName,brewlog)=row


def xmlsafe(text):
	text=re.compile("[\n\r]").sub("</br>",text)
	
	safe=re.compile("<").sub("{:leftbracket:}",  re.compile(">").sub("{:rightbracket:}",  re.compile("&").sub("{:ampersand:}", re.compile("/").sub("{:forwardslash:}", text ) )  ) )

	return text

sys.stdout.write("<xml>\n")
sys.stdout.write("<status>%s</status>\n" %(status))
sys.stdout.write("<recipeName>%s</recipeName>\n" %(xmlsafe(recipeName)))
sys.stdout.write("<brewlog>%s</brewlog>\n" %(xmlsafe(brewlog)))
sys.stdout.write("</xml>")
sys.stdout.flush()

