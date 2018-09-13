#!/usr/bin/python
import sys
import _mysql
import cgi
import re
#sys.stdout.write("Content-Type:text/plain\n\n")
from cloudNG import *
sys.stdout.write("Content-Type:text/xml\n\n")
#sys.stdout.write(open("docs/index.html").read())
form=cgi.FieldStorage()



def xmlsafe(text):
	text=re.compile("[\n\r]").sub("</br>",text)
	
	safe=re.compile("<").sub("{:leftbracket:}",  re.compile(">").sub("{:rightbracket:}",  re.compile("&").sub("{:ampersand:}", re.compile("/").sub("{:forwardslash:}", text ) )  ) )

	return text

sys.stdout.write("<xml>\n")
costResult,stockResult=brewerslabCloudApi().checkStockAndPrice("test@example.com", form['recipeName'].value, form['process'].value,True)
sys.stderr.write("stockResult['__out_of_stock__']\n")
sys.stderr.write("%s\n" %(stockResult['__out_of_stock__']))
sys.stderr.write("\n")
sys.stdout.write("<outofstock>%s</outofstock>\n" %(len(stockResult['__out_of_stock__'])))
for s in range(len(stockResult['__out_of_stock__'])):
	sys.stdout.write("<stock%s>%s</stock%s>\n" %(s,xmlsafe(stockResult['__out_of_stock__'][s]),s))
sys.stdout.write("</xml>")
sys.stdout.flush()

