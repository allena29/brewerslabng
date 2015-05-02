#!/usr/bin/python
import cgi
import sys
import json
import re
import mysql.connector
from cloudNG import *

y=sys.stdin.readline().split(",")
x = sys.stdin.read()
#con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
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

saveComments=brewerslabCloudApi().saveComment("test@example.com", y[0],y[1],y[2],x  )
sys.stdout.write("<xml>\n")
sys.stdout.write("<stepNum>%s</stepNum>\n" %( y[2] ))
sys.stdout.write("</xml>")
sys.stdout.flush()

