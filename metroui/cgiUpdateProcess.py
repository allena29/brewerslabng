#!/usr/bin/python

import cgi
import re
import _mysql
import mysql.connector

form=cgi.FieldStorage()







#print "Content-Type:text/html\n\n"
#print form['stepid'].value,form['process'],form['activityid'].value

con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
cursor=con.cursor()

# Updated Fixed things
cursor.execute("UPDATE gProcess SET stepName ='%s',text='%s' WHERE process='%s' AND activityNum = %s AND stepNum = %s;" %( _mysql.escape_string( form['stepName'].value), _mysql.escape_string( form['text'].value) ,  form['process'].value, form['activityid'].value,form['stepid'].value))

# Update Optional things
if form.has_key("attention"):
	cursor.execute("UPDATE gProcess SET attention ='%s' WHERE process='%s' AND activityNum = %s AND stepNum = %s;" %( _mysql.escape_string( form['attention'].value), form['process'].value, form['activityid'].value,form['stepid'].value))


print "Location: process.py?process=%s&activity=%s&edit=%s#edit%s\n" %(form['process'].value,form['activityid'].value,form['stepid'].value,form['stepid'].value)

