#!/usr/bin/python
import re
import sys
import time
import cgi
import _mysql
import mysql.connector
from cloudNG import *
from thememetro import *
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
theme.pagetitle="Stores" 
theme.goBackHome="stores.py"
theme.bodytitle="Stores"
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")


if form.has_key("action"):
	X=form['purchasedate'].value.split(".")

	if form.has_key('hopAlpha'):
		hopAlpha=form['hopAlpha'].value
	else:
		hopAlpha=0.00

	bc=brewerslabCloudApi()
	bc.addNewPurchase('test@example.com',form['type'].value, form['item'].value, float(form['qty'].value), float(form['cost'].value), int(X[2]),int(X[1]),int(X[0]), form['supplier'].value, int(form['multiply'].value),hopAlpha)
		


sys.stdout.write("Content-Type:text/html\n\n")
theme.presentHead()

theme.presentBody()
print "<div class=\"container\">"




activeStats="active "
activeFermentables=""
activeHops=""
if form.has_key("active"):
	activeStats=""
	if form['active'].value == "fermentables":	activeFermentables = "active "
	if form['active'].value == "hops":	activeHops = "active "




print """


            <div class="grid fluid">
                <div class="row">
                    <div class="span4">
                    </div>

                    <div class="span4">
                    </div>

                </div>
            </div>


"""



print """
	    	<div class="content">
			<p>

<form method=POST action='storeaddpage.py'>
<input type='hidden' name='type' value='%s'>
 <table class="table">

                        <tbody>

	<tr>
		<td>Item:</td>
		<td><select name='item'>
""" %(form['type'].value)

cursor=con.cursor()
cursor.execute("select entity,name,unit FROM gItems where majorcategory = '%s' ORDER BY name" %(form['type'].value))
for row in cursor:
	(entity,name,unit)=row
	print "<option value='%s'>%s</option>" %(name,name)
cursor.close()


print """	</select><br>"""
if theme.localUser:
	print "<a href='storeadditem.py?type=%s'>add new item</a>" %(form['type'].value)

print """
		</td>
	</tr>
	<tr>
		<td>Qty:</td>
		<td><input type="text" size=3 name="qty" value="0"> %s</td>
	</tr>
	<tr>
		<td>Multiplier:</td>
		<td><input type="text" size=3 name="multiply" value="1"></td>
	</tr>
	<tr>
		<td>Cost:</td>
		<td><input type="text" size=3 name="cost" value=""></td>
	</tr>
	<tr>
		<td>Supplier:</td>
		<td><select name="supplier">
""" %(unit)


cursor=con.cursor()
cursor.execute("select entity,supplier,supplierName FROM gSuppliers ORDER BY supplier")
for row in cursor:
	(entity,supplier,supplierName)=row
	print "<option value='%s'>%s</option>" %(supplier,supplierName)
print """	</select></td>
	</tr>
"""

(year,mon,mday,hour,tmin,sec,wday,yday,dst)=time.localtime()
print """

	<tr>
		<td>Purchase Date:</td>
		<td>
		   <div style='width: 250px' class="input-control text" data-role="datepicker"
		    data-date='%s-%02d-%02d'
		    data-effect='slide'
		    data-locale='en'
		    data-week-start='0'
		    data-other-days='0'>
		    <input name='purchasedate' id='purchasedate' type="text">
		    <button class="btn-date"></button>
		    </div>
		</td>
	</tr>
""" %(year,mon,mday)



if form['type'].value == "hops":
	print """<tr>
		<td>Hop Alpha Acid</td>
		<td><input type='text' name='hopAlpha' value=''>%%</td>
	</tr>"""


print """
	<tr>
		<td colspan=2 align=center><input type="submit" value="Add Purchase" name="action"></td>
	</tr>

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>

"""

print "</form></div>"
theme.presentFoot()

if form.has_key("utc"):
	print """
	<script language="Javascript">
	$( document ).ready(function() {

					$.Notify({
					    shadow: true,
					    position: 'bottom-right',
					    content: "Item Added"
					});


	});



	</script>
	"""

