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
cursor.execute("select storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost FROM gPurchases WHERE qty > 0 AND storecategory='fermentables' ORDER BY storeitem")
for row in cursor:
	(storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost)=row
	
	print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
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
cursor.execute("select storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha FROM gPurchases WHERE qty > 0 AND storecategory='hops' ORDER BY storeitem")
for row in cursor:
	(storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha)=row
	
	print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
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
cursor.execute("select storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost FROM gPurchases WHERE qty > 0 AND storecategory='yeast' ORDER BY storeitem")
for row in cursor:
	(storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost)=row
	
	print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
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
cursor.execute("select storeitem,qty,purchaseQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha FROM gPurchases WHERE qty > 0 AND (storecategory='consumable' OR storecategory='misc') ORDER BY storeitem")
for row in cursor:
	(storeitem,qty,purchasedQty,unit,stocktag,supplier,bestBeforeEnd,purchaseDate,purchaseCost,hopActualAlpha)=row
	
	print "<tr><td>%.0f %s</td><td>%s<br><small>" %(float(qty),unit, storeitem)
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










print "</div>"	# accordiain



print "</div>"
theme.presentFoot()

