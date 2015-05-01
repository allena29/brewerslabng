#!/usr/bin/python
import re
import sys
import cgi
import _mysql
import mysql.connector
from thememetro import *
from cloudNG import *
con=mysql.connector.connect(user='root',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
#sys.stdout.write("Content-Type:text/html\n\n")
grid={}
db=_mysql.connect(host="localhost",user="root",db="brewerslab")

if form['action'].value == "changeBatchSize":
	brewerslabCloudApi().setBatchSize("test@example.com", form['recipe'].value,float(form['batchsize'].value),doRecalculate="0")

if form['action'].value == "changeqty":
	brewerslabCloudApi().changeItemInRecipe("test@example.com", form['recipe'].value,form['type'].value, form['ingredient'].value, float(form['qty'].value), float(form['hopAddAt'].value), doRecalculate=0)

if form['action'].value == "add":
	brewerslabCloudApi().addItemToRecipe("test@example.com", form['recipe'].value,form['type'].value, form['ingredient'].value, float(form['qty'].value), float(form['hopAddAt'].value), doRecalculate=0)

if form['action'].value == "delete":
	brewerslabCloudApi().deleteItemFromRecipe("test@example.com", form['recipe'].value, form['type'].value, form['ingredient'].value, float(form['hopAddAt'].value))

print "Location: editRecipe.py?recipeName=%s&active=%s&recalc=True\n" %(form['recipe'].value,form['type'].value)
