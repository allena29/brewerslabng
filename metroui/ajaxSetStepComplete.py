#!/usr/bin/python
import sys
import json
import cgi
import re
import mysql.connector
from cloudNG import *
#con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
#sys.stdout.write("Content-Type:text/plain\n\n")
sys.stdout.write("Content-Type:text/xml\n\n")
form=cgi.FieldStorage()

def xmlsafe(text):
	text=re.compile("[\n\r]").sub("</br>",text)
	safe=re.compile("<").sub("{:leftbracket:}",  re.compile(">").sub("{:rightbracket:}",  re.compile("&").sub("{:ampersand:}", re.compile("/").sub("{:forwardslash:}", text ) )  ) )
	return text

comp=False
if form.has_key("subStepNum"):
	completeStatus=json.loads(brewerslabCloudApi().setSubStepComplete("test@example.com", form['brewlog'].value, form['activityNum'].value, form['stepNum'].value,form['subStepNum'].value, form['complete'].value )['json'])['result']
	if completeStatus['parentComplete']:
		comp=True
else:
	completeStatus=json.loads(brewerslabCloudApi().setStepComplete("test@example.com", form['brewlog'].value, form['activityNum'].value, form['stepNum'].value, form['complete'].value )['json'])['result']
	if form['complete'].value == "1":
		comp=True
sys.stdout.write("<xml>\n")
sys.stdout.write(" <status>%s</status>\n" %(form['stepNum'].value))
sys.stdout.write(" <complete>%s</complete>\n" %(comp))
sys.stdout.write("</xml>")
sys.stdout.flush()

