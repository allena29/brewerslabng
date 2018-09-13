#!/usr/bin/python
import re
import sys
import time
import cgi
import _mysql
import mysql.connector
from thememetro import *
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")


form=cgi.FieldStorage()


if form.has_key("action") and form.has_key("id"):
	if form['action'].value:
		cursor=con.cursor()
		cursor.execute("delete from gBeerStock where entity=%s" %(form['id'].value))
	
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
theme.pagetitle="Finished Stock" 
theme.goBackHome="index.py"
theme.bodytitle="Finished Stock"
theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")

theme.presentBody()
print "<div class=\"container\">"




activeFinished="active "
if form.has_key("active"):
	activeStats=""
	if form['active'].value == "finished":	activeFinished="active "
print """
    <div class="accordion" data-role="accordion">
"""





print """

<script language="Javascript">
function gotoAddPage(i){
window.location.replace("stockaddpage.py?type="+i);
}
</script>

            <div class="grid fluid">
                <div class="row">
                    <div class="span4">
                    </div>

                    <div class="span4">
                    </div>

                    <div class="span4">
                        <div class="panel" data-role="panel">
                            <div class="panel-header bg-darkRed fg-white">
                                Add Stock
                            </div>
                            <div class="panel-content" style="display:none">
				<p><button class="large" onClick="gotoAddPage('stock')">Add</button></p>

                            </div>
                        </div>
                    </div>
                </div>
            </div>


"""




print """
    <div class="accordion-frame">
	    	<a href="#" class="%sheading">Finished Stock</a>

	    	<div class="content">
			<p>

 <table class="table">
                        <thead>
                        <tr>
                            	<th class="text-left">Qty</th>
                            	<th class="text-left"></th>
                           	<th class="text-left">Beer</th>
			    	<th class="text-left">Location</th>
                        </tr>
                        </thead>

                        <tbody>

""" %(activeFinished)

cursor=con.cursor()
cursor.execute("select entity,sum(qty),stocktype,recipe,brewlog,location from gBeerStock group by location,recipe,brewlog,stocktype order by location,recipe,brewlog")

for row in cursor:
	(entity,qty,stocktype,recipe,brewlog,location) = row
	
	print "<tr><td>%.0f * %s</td>" %(float(qty),stocktype)
	print "<td><a href='stock.py?action=delete&id=%s'><i class='icon-minus fg-red'></i></a></td>" %(entity)
	print "<td>%s %s</td>" %( recipe,brewlog)

	print "<td>%s</td></tr>" %(location)
	
cursor.close()

print """

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>
    </div>
"""










print "</div>"	# accordiain



print "</div>"
theme.presentFoot()

