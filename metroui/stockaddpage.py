#!/usr/bin/python
import re
import sys
import time
import cgi
import _mysql
import mysql.connector
from cloudNG import *
from thememetro import *
con=mysql.connector.connect(user='root',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
theme.pagetitle="Stock" 
theme.goBackHome="index.py"
theme.bodytitle="Stock"
grid={}

db=_mysql.connect(host="localhost",user="root",db="brewerslab")


if form.has_key("action"):
	bc=brewerslabCloudApi()

		
	bc.addNewStock('test@example.com',form['brewlog'].value, form['recipe'].value, form['container'].value, form['location'].value,float(form['multiply'].value) )
	print "Location: stock.py?utc=%s\n" %(time.time())
		
	sys.exit(0)
sys.stdout.write("Content-Type:text/html\n\n")
theme.presentHead()

theme.presentBody()
print "<div class=\"container\">"



print """


            <div class="grid fluid">
                <div class="row">
                    <div class="span4">
                    </div>

                    <div class="span4">
                    </div>

                </div>
            </div>


<script language="Javascript">
function updateDropDown(){
      if (http_request.readyState==4 && http_request.status==200)    {
	
		var responseTxt=http_request.responseText;      
		var response=http_request.responseXML;  
		var xmldoc = response;
		var brewlogs = xmldoc.getElementsByTagName('brewlogs').item(0).firstChild.data;
		b="<select id='brewlog' name='brewlog'>";
		for(c=0;c< brewlogs;c++){
			b=b+"<option>"+ xmldoc.getElementsByTagName('brewlog'+ c).item(0).firstChild.data +"</option>";
		}	
		b=b+"</select>";
//		alert(b);
		document.getElementById('brewlogs').innerHTML=b;
	}
}


function findBrewlogs(){
//	alert( document.getElementById("recipe").value);
	xmlREQ(updateDropDown,"ajaxGetBrewlogFromRecipe.py?recipe="+ document.getElementById("recipe").value);
}
</script>
"""



print """
	    	<div class="content">
			<p>

<form method=POST action='stockaddpage.py'>
<input type='hidden' name='type' value='%s'>
 <table class="table">

                        <tbody>

	<tr>
		<td>Recipe:</td>
		<td><select name='recipe' id='recipe' onChange='findBrewlogs()' ><option value='--select--'>--select--</option>
""" %(form['type'].value)

cursor=con.cursor()
cursor.execute("select entity,recipeName FROM gRecipes ORDER BY recipeName")
for row in cursor:
	(entity,name)=row
	print "<option value='%s'>%s</option>" %(name,name)
cursor.close()


print """	</select>
		</td>
	</tr>

	<tr>
		<td>Brewlog:</td>
		<td id='brewlogs'></td>
	</tr>

	<tr>
		<td>Multiplier:</td>
		<td><input type="text" size=3 name="multiply" value="1"></td>
	</tr>
	<tr>
		<td>Container</td>
		<td><select name='container'>
"""


cursor=con.cursor()
cursor.execute("select entity,name FROM gItems WHERE category='keg' or category='bottle' or category='polypin' ORDER BY name")
for row in cursor:
	(entity,name)=row
	print "<option value='%s'>%s</option>" %(name,name)
cursor.close()


print """
		</select></td>
	</tr>
	<tr>
		<td>Location</td>
		<td><select name='location'>
"""


cursor=con.cursor()
cursor.execute("select entity,location FROM gLocations  ORDER BY location")
for row in cursor:
	(entity,name)=row
	print "<option value='%s'>%s</option>" %(name,name)
cursor.close()


print """
		</select></td>
	</tr>
	<tr>
		<td colspan=2 align=center><input type="submit" value="Add Stock" name="action"></td>
	</tr>

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>

"""

print "</form></div>"
theme.presentFoot()

if form.has_key("action"):
	print """
	<script language="Javascript">
	$( document ).ready(function() {

					$.Notify({
					    shadow: true,
					    position: 'bottom-right',
					    content: "Purchase Added"
					});


	});



	</script>
	"""

