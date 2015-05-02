#!/usr/bin/python
import sys
import time
import mysql.connector
import cgi
import re
sys.stdout.write("Content-Type:text/plain\n\n")
from cloudNG import *
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
#sys.stdout.write(open("docs/index.html").read())
form=cgi.FieldStorage()


sys.stdout.write("Creating brewlog: %s\nRecipe: %s\nProcess: %s\n" %(form['brewlog'].value,form['recipeName'].value,form['process'].value))
sys.stdout.write("Transaction: %s\n" %(form['transaction'].value))

#costResult,stockResult=brewerslabCloudApi().checkStockAndPrice("test@example.com", form['recipeName'].value, form['process'].value,True)
sys.stdout.flush()

cursor=con.cursor()
cursor.execute("INSERT INTO gTransactions (id,timestamp,status,recipeName,brewlog) VALUES (%s,%s,%s,%s,%s)", (form['transaction'].value, time.time(),"creating", form['recipeName'].value,form['brewlog'].value))
con.commit()
cursor.close()


print brewerslabCloudApi().createBrewlogWrapper("test@example.com",form['recipeName'].value,form['brewlog'].value, form['process'].value)

cursor=con.cursor()
cursor.execute("INSERT INTO gTransactions (id,timestamp,status,recipeName,brewlog) VALUES (%s,%s,%s,%s,%s)", (form['transaction'].value, time.time()+1,"complete", form['recipeName'].value,form['brewlog'].value))
con.commit()
cursor.close()


