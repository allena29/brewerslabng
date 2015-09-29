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
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
theme.pagetitle="Stores" 
theme.goBackHome="index.py"
theme.bodytitle="Stores"
theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")

theme.presentBody()
print "<div class=\"container\">"



i=0
activeStats="active "
activeFermentables=""
activeHops=""
if form.has_key("active"):
	activeStats=""
	if form['active'].value == "fermentables":	activeFermentables = "active "
	if form['active'].value == "hops":	activeHops = "active "

print """
    <div class="accordion" data-role="accordion">
"""


if theme.localUser:
	print """
	<script language="Javascript">
	function updatestoreqty(itemtype,i,ent){
		showdeadcenterdiv(100,30,"spinner",200,50);
		d = new Date();
		document.getElementById('spinnerText').innerHTML="updating";
		document.getElementById('spinner').style.visibility="visible";
		document.getElementById('spinner').style.height="100%%";
		qty=document.getElementById("Qty"+i).value;
		url="editIngredient.py?action=changestoreqty&type="+itemtype+"&entity="+ent+"&qty="+qty;
		window.location.replace(url);
	}
	function editqty(itemtype,i,j,k){
		html="<select id='Qty"+i+"'>"
		if(itemtype == "fermentables"){
			limit=3000;
		}else{
			limit=1000;
		}
		for(c=0;c<=limit;c++){
			if(itemtype == "fermentables"){
				C=c*10;
			}else{
				C=c;
			}
			if(C==j){
			html=html+"<option value="+C+" SELECTED>"+C+" gm</option>"
			}else{
			html=html+"<option value="+C+">"+C+" gm</option>"
			}
		}
		html=html+'</select> <a href="';
		html=html+"javascript:updatestoreqty('"+itemtype+"','"+i+"','"+k+"')";
		html=html+'"><i class="icon-checkmark fg-blue"></i></a>';
		document.getElementById('QtyCell'+i).innerHTML=html;
	}
	</script>
"""


print """

<script language="Javascript">
function gotoAddPage(i){
window.location.replace("storeaddpage.py?type="+i);
}
</script>

            <div class="grid fluid">
                <div class="row">
                    <div class="span4">
                    </div>

                    <div class="span4">
                    </div>

"""

if theme.localUser:
	print """
                    <div class="span4">
                        <div class="panel" data-role="panel">
                            <div class="panel-header bg-darkRed fg-white">
                                Add Purchase
                            </div>
                            <div class="panel-content" style="display:none">
				<p><button class="large" onClick="gotoAddPage('fermentables')">Add Fermentables</button></p>
				<p><button class="large" onClick="gotoAddPage('hops')">Add Hops</button></p>
				<p><button class="large" onClick="gotoAddPage('yeast')">Add Yeast</button></p>
				<p><button class="large" onClick="gotoAddPage('misc')">Add Misc</button></p>

                            </div>
                        </div>
                    </div>
	"""

print """
                </div>
            </div>
"""




print """
    <div class="accordion-frame">
	    	<a href="#" class="%sheading">Fermentbales</a>

	    	<div class="content">
			<p>

 <table class="table">
                        <thead>
                        <tr>
                            	<th class="text-left">Qty</th>
                           	<th class="text-left">Ingredient</th>
			    	<th class="text-left">Cost</th>
                        </tr>
                        </thead>

                        <tbody>

""" %(activeFermentables)

cursor=con.cursor()
cursor.execute("select entity,storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost FROM gPurchases WHERE qty > 0 AND storecategory='fermentables' ORDER BY storeitem")
for row in cursor:
	(ent,storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost)=row
	
	if not theme.localUser:
		print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
	else:
		print "<tr><td id='QtyCell%s'><a href=\"javascript:editqty('fermentables',%s,%.0f,%s)\">%.0f %s</a></a></td><td>%s<br><small>" %(i,i,float(qty),ent,float(qty),unit, storeitem)
		i=i+1
	print "Purchase Date: %s<br>" %(time.ctime(purchaseDate))
	print "Before Before: %s<br>" %(time.ctime(bestBeforeEnd))
	print "Supplier: %s<br>" %(supplier)
	print "</small></td><td> %.2f</td></tr>" %(float(purchaseCost)*qty)
	
cursor.close()

print """

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>
    </div>
"""




print """
    <div class="accordion-frame">
	    	<a href="#" class="%sheading">Hops</a>

	    	<div class="content">
			<p>

 <table class="table">
                        <thead>
                        <tr>
                            	<th class="text-left">Qty</th>
                           	<th class="text-left">Ingredient</th>
			    	<th class="text-left">Cost</th>
                        </tr>
                        </thead>

                        <tbody>

""" %(activeHops)

cursor=con.cursor()
cursor.execute("select entity,storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha FROM gPurchases WHERE qty > 0 AND storecategory='hops' ORDER BY storeitem")
for row in cursor:
	(ent,storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha)=row
	
	if not theme.localUser:
		print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
	else:
		print "<tr><td id='QtyCell%s'><a href=\"javascript:editqty('hops',%s,%.0f,%s)\">%.0f %s</a></a></td><td>%s<br><small>" %(i,i,float(qty),ent,float(qty),unit, storeitem)
		i=i+1
	print "Hop Alpha: %.1f %%<br>" %(hopActualAlpha)
	print "Purchase Date: %s<br>" %(time.ctime(purchaseDate))
	print "Before Before: %s<br>" %(time.ctime(bestBeforeEnd))
	print "Supplier: %s<br>" %(supplier)
	print "</small></td><td> %.2f</td></tr>" %(float(purchaseCost)*qty)
	
cursor.close()

print """

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>
    </div>
"""




print """
    <div class="accordion-frame">
	    	<a href="#" class="%sheading">Yeast</a>

	    	<div class="content">
			<p>

 <table class="table">
                        <thead>
                        <tr>
                            	<th class="text-left">Qty</th>
                           	<th class="text-left">Ingredient</th>
			    	<th class="text-left">Cost</th>
                        </tr>
                        </thead>

                        <tbody>

""" %("")

cursor=con.cursor()
cursor.execute("select entity,storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost FROM gPurchases WHERE qty > 0 AND storecategory='yeast' ORDER BY storeitem")
for row in cursor:
	(ent,storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost)=row
	
	if not theme.localUser:
		print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
	else:
		print "<tr><td id='QtyCell%s'><a href=\"javascript:editqty('yeast',%s,%.0f,%s)\">%.0f %s</a></a></td><td>%s<br><small>" %(i,i,float(qty),ent,float(qty),unit, storeitem)
		i=i+1
	print "Purchase Date: %s<br>" %(time.ctime(purchaseDate))
	print "Before Before: %s<br>" %(time.ctime(bestBeforeEnd))
	print "Supplier: %s<br>" %(supplier)
	print "</small></td><td> %.2f</td></tr>" %(float(purchaseCost)*qty)
	
cursor.close()

print """

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>
    </div>
"""




print """
    <div class="accordion-frame">
	    	<a href="#" class="%sheading">Misc</a>

	    	<div class="content">
			<p>

 <table class="table">
                        <thead>
                        <tr>
                            	<th class="text-left">Qty</th>
                           	<th class="text-left">Ingredient</th>
			    	<th class="text-left">Cost</th>
                        </tr>
                        </thead>

                        <tbody>

""" %(activeHops)

cursor=con.cursor()
cursor.execute("select entity,storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha FROM gPurchases WHERE qty > 0 AND (storecategory='consumable' OR storecategory='misc') ORDER BY storeitem")
for row in cursor:
	(ent,storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha)=row
	if not theme.localUser:
		print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
	else:
		print "<tr><td id='QtyCell%s'><a href=\"javascript:editqty('misc',%s,%.0f,%s)\">%.0f %s</a></a></td><td>%s<br><small>" %(i,i,float(qty),ent,float(qty),unit, storeitem)
		i=i+1
	
	print "Purchase Date: %s<br>" %(time.ctime(purchaseDate))
	print "Before Before: %s<br>" %(time.ctime(bestBeforeEnd))
	print "Supplier: %s<br>" %(supplier)
	print "</small></td><td> %.2f</td></tr>" %(float(purchaseCost)*qty)
	
cursor.close()

print """

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>
    </div>
"""



print """
				<!-- begin spinner -->
                                <div id='spinner' style='height: 0px; visibility: hidden; margin: 12px;'>
                                        <div id='box'>
                                                Please Wait, <span id='spinnerText'>recalculating</span> recipe<br>
                                                <img src="images/ajax_progress2.gif">
                                        </div>
                                </div>
                                <!-- end spinner -->
"""







print "</div>"	# accordiain



print "</div>"


theme.presentFoot()


