#!/usr/bin/python
import re
import sys
import cgi
import _mysql
from thememetro import *
from cloudNG import *

form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"





sys.stdout.write("Content-Type:text/html\n\n")

editable=False
if theme.localUser:
	editable=True

grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
db2=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
db3=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")


import time

theme.bodytitle="Water Profiles"
theme.presentHead()
theme.presentBody()


if form.has_key("alkalinity"):
	cursor=db2.query("INSERT INTO gWater VALUES(null,'test@example.com', %s,%s,%s,%s,%s,%s,%s,%s,0,'') " %( form['alkalinity'].value,form['ca'].value,form['mg'].value,form['na'].value,form['co3'].value,form['so4'].value,form['cl'].value,time.time()))
	

print """
<div class=content>
<table border=1 class=table>
<thead>
<tr><th rowspan=2>Sample Date</th>
<th rowspan=2>Alkalinity<br>CaCo3</th>
<th colspan=3>Cations</th><th colspan=3>Anions</th>
</tr>
<tr>
<th>Calcum<br>Ca</th><th>Magnesium<br>Mg</th><th>Sodium<br>Na</th><th>Carbonate<br>CO3</th>
<th>Sulphate<br>SO4</th><th>Chloride<br>Cl</th>
</tr>

</thead><tbody>"""

cursor=db.query("select entity,description,testdate,alkalinity,ca,mg,na,co3,so4,cl FROM gWater WHERE profile = 0 ORDER BY testdate DESC")
result=db.use_result()
row=result.fetch_row()
while row:
	((entity,description,testdate,alkalinity,ca,mg,na,co3,so4,cl),)=row
	
	print """<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
	""" %(time.ctime(float(testdate)), float(alkalinity), float(ca),float(mg),float(na),float(co3),float(so4),float(cl) )

	row=result.fetch_row()

print """
<form method=POST>
<tr><td align=right><input type=submit value='Add New Profile'></td>
<td><input type=text name=alkalinity size=4 value=0.00></td>
<td><input type=text name=ca size=4 value=0.00></td>
<td><input type=text name=mg size=4 value=0.00></td>
<td><input type=text name=na size=4 value=0.00></td>
<td><input type=text name=co3 size=4 value=0.00></td>
<td><input type=text name=so4 size=4 value=0.00></td>
<td><input type=text name=cl size=4 value=0.00></td>
</tr>
"""

print "</tbody></table>"
theme.presentFoot()
	
