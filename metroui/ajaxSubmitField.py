#!/usr/bin/python
import cgi
import sys
import json
import re
import mysql.connector
from cloudNG import *

y=sys.stdin.readline().split(",")
x = sys.stdin.read()
#con=mysql.connector.connect(user='root',database="brewerslab")
#sys.stdout.write("Content-Type:text/plain\n\n")
sys.stdout.write("Content-Type:text/xml\n\n")
form=cgi.FieldStorage()

def xmlsafe(text):
	text=re.compile("[\n\r]").sub("</br>",text)
	safe=re.compile("<").sub("{:leftbracket:}",  re.compile(">").sub("{:rightbracket:}",  re.compile("&").sub("{:ampersand:}", re.compile("/").sub("{:forwardslash:}", text ) )  ) )
	return text
sys.stderr.write("brewlog: %s\n" %(y[0]))
sys.stderr.write("act %s\n" %(y[1]))
sys.stderr.write("step: %s\n" %(y[2]))
sys.stderr.write("fieldkey: %s\n" %(y[3]))
sys.stderr.write("fieldNum: %s\n" %(y[4]))
sys.stderr.write("process: %s\n" %(y[5]))

fieldData=json.loads(brewerslabCloudApi().setFieldWidget("test@example.com", y[0],y[5],y[1],y[2],y[3],x,"guid..."  )['json'])['result']
#sys.stderr.write("yyyyyyyyyyyyyyyyy\n%s\n" %(fieldData))
sys.stdout.write("<xml>\n")
sys.stdout.write("<stepNum>%s</stepNum>\n" %( y[2] ))
sys.stdout.write("<fieldKey>%s</fieldKey>\n" %( y[3] ))
sys.stdout.write("<fieldNum>%s</fieldNum>\n" %( y[4] ))
fieldVal=fieldData['value']
if fieldVal == "":	fieldVal="-"
sys.stdout.write("<val>%s</val>\n" %(fieldVal))
sys.stdout.write("</xml>")
sys.stdout.flush()

