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
#cursor=con.cursor()
#cursor.execute("select status,timestamp FROM gTransactions ORDER BY timestamp DESC LIMIT 0,1")
#
#for row in cursor:
#	(status,timestamp)=row


def xmlsafe(text):
	text=re.compile("[\n\r]").sub("</br>",text)
	safe=re.compile("<").sub("{:leftbracket:}",  re.compile(">").sub("{:rightbracket:}",  re.compile("&").sub("{:ampersand:}", re.compile("/").sub("{:forwardslash:}", text ) )  ) )
	return safe


stepDetail=json.loads(brewerslabCloudApi().getStepDetail("test@example.com", form['process'].value, form['activityNum'].value,form['brewlog'].value, form['stepNum'].value, form['recipeName'].value )['json'])['result']
sys.stderr.write("\n______________\n%s\n_____________________\n" %(stepDetail))
sys.stdout.write("<xml>\n")
sys.stdout.write(" <title>%s</title>\n" %( xmlsafe( stepDetail['title'] ) ))
if stepDetail['warning'] == "":
	stepDetail['warning'] = "-"
sys.stdout.write(" <warning>%s</warning>\n" %( xmlsafe( stepDetail['warning'] ) ))
sys.stdout.write(" <description>%s</description>\n" %( xmlsafe( stepDetail['text'] ) ))
if len(stepDetail['img']) == 0 :
	sys.stdout.write(" <img>-</img>\n" )
else:
	sys.stdout.write(" <img>%s</img>\n" %(stepDetail['img'][0]))


SubsToComplete=False
sub=0
for substep in stepDetail['substeps']:
	sys.stdout.write("<subNeedToComplete%s>%s</subNeedToComplete%s>\n" %(sub, substep['needtocomplete'],sub))
	sys.stdout.write("<subComplete%s>%s</subComplete%s>\n" %(sub,substep['complete'],sub))
	sys.stdout.write("<subText%s>%s</subText%s>\n" %(sub,xmlsafe(substep['text']),sub))
	if substep['needtocomplete']:
		SubsToComplete=True
	sub=sub+1
sys.stdout.write("<substeps>%s</substeps>\n" %(sub))

sys.stdout.write("<stepNum>%s</stepNum>\n" %( form['stepNum'].value))
sys.stdout.write("<complete>%s</complete>\n" %(stepDetail['complete']))
sys.stdout.write("<sortindex>%s</sortindex>\n" %( form['sortindex'].value ))
sys.stdout.write("<comments>%s</comments>\n" %(xmlsafe(stepDetail['comments'])))
sys.stdout.write("<commentTimestamp>%s</commentTimestamp>\n" %((stepDetail['commentsTimestamp'])))
try:
	sys.stdout.write("<completeDate>%s</completeDate>\n" %(stepDetail['completeDate']))
except:
	sys.stdout.write("<completeDate>-</completeDate>\n")

fi=0
for (fieldLabel,fieldKey,fieldVal,fieldWidget) in stepDetail['fields']:
	sys.stdout.write("<fieldLabel%s>%s</fieldLabel%s>\n" %(fi,fieldLabel,fi))
	sys.stdout.write("<fieldKey%s>%s</fieldKey%s>\n" %(fi,fieldKey,fi))
	if fieldVal == "":	fieldVal="-"
	sys.stdout.write("<fieldVal%s>%s</fieldVal%s>\n" %(fi,xmlsafe(fieldVal),fi))
	if fieldWidget=="":	fieldWidget="-"
	sys.stdout.write("<fieldWidget%s>%s</fieldWidget%s>\n" %(fi,fieldWidget,fi))
	fi=fi+1
sys.stdout.write("<fields>%s</fields>\n" %(fi))


sys.stdout.write("<substocomplete>%s</substocomplete>\n" %(SubsToComplete))
sys.stdout.write("</xml>")
sys.stdout.flush()

