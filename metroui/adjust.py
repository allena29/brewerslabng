#!/usr/bin/python
import os
import re
import sys
import cgi
import _mysql
from thememetro import *
from pitmCfg import *

form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
theme.noHeader=True
theme.pagetitle=""
theme.goBackHome=""
theme.bodytitle=""
theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")


if not theme.localUser:
	print "Not authorised"
	sys.exit(0)

print "<div class=\"container\">"



print """
	<form action='adjust.py' method=POST>

            <div class="grid fluid">
		<div clas='row'>
			<div class='span12'>
"""

mode=""
if os.path.exists("../websocket/mode"):
	mode=open("../websocket/mode").read()

if mode.count("ferm"):
	print """
<h3>Adjust Fermentation Temperature</h3>
<input name='adjustFermTarget' type='text' size=4 value=''><input type='submit' value='Adjust Ferm Temp' name='action'>
"""



print """
			</div>
		</div>
	</div>
	</div>
	</form>
"""
