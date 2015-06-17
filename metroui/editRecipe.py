#!/usr/bin/python
import re
import sys
import cgi
import _mysql
import mysql.connector
from thememetro import *
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
con2=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
if form.has_key("noheader"):
	theme.noHeader=True
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
if not form.has_key("noheader"):
	theme.pagetitle="%s - Edit Recipe" %(form['recipeName'].value)
	theme.goBackHome="brewerslab.py?recipeName=%s" %(form['recipeName'].value)
	theme.bodytitle="%s" %(form['recipeName'].value)
theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")

export=False
if form.has_key("export"):	export=True

colWidth=100
if export:
	colWidth=10
theme.presentBody()

if theme.localUser:
	print """
	<input type=hidden id='outstandingSig' value='-1'>
	<script language="Javascript">
	function addItem(itemType) {
	showdeadcenterdiv(100,30,"spinner",200,50);
	document.getElementById('spinnerText').innerHTML="updating";
	d = new Date();
	document.getElementById('outstandingSig').value=d.getTime();
	document.getElementById('spinner').style.visibility="visible";
	document.getElementById('spinner').style.height="100%%";
	url="editIngredient.py?recipe=%s&action=add&type="+itemType+"&ingredient="+document.getElementById(itemType+'Item').value+"&qty="+document.getElementById(itemType+'Qty').value+"&hopAddAt="+document.getElementById('hopAddAt').value+"&outstandingSig="+document.getElementById('outstandingSig').value;
	window.location.replace(url);
	}


	function recalculate(){
	showdeadcenterdiv(100,30,"spinner",200,50);
	document.getElementById('spinnerText').innerHTML="recalculating"
	document.getElementById('spinner').style.visibility="visible";
	document.getElementById('spinner').style.height="100%%";
	xmlREQ(reloadAfterAjax,"ajaxRecalculate.py?recipe=%s");

	}


	function adjustBatchSize(){
	url="editIngredient.py?recipe=%s&type=null&action=changeBatchSize&batchsize="+document.getElementById('batchsize').value;
	window.location.replace(url);
	}

	function updateqty(itemtype,i,item,hopAddAt){
	showdeadcenterdiv(100,30,"spinner",200,50);
	d = new Date();
	document.getElementById('outstandingSig').value=d.getTime();
	document.getElementById('spinnerText').innerHTML="updating";
	document.getElementById('spinner').style.visibility="visible";
	document.getElementById('spinner').style.height="100%%";
	qty=document.getElementById(itemtype+"Qty"+i).value;
	url="editIngredient.py?recipe=%s&action=changeqty&type="+itemtype+"&ingredient="+item+"&qty="+qty+"&hopAddAt="+hopAddAt+"&outstandingSig="+document.getElementById('outstandingSig').value;
	window.location.replace(url);
	}

	function editqty(itemtype,i,j,k,l){
		html="<select id='"+itemtype+"Qty"+i+"'>"
		for(c=0;c<=750;c++){
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
		html=html+"javascript:updateqty('"+itemtype+"','"+i+"','"+k+"',"+l+")";
		html=html+'"><i class="icon-checkmark fg-blue"></i></a>';
		document.getElementById(itemtype+'QtyCell'+i).innerHTML=html;
	}
	</script>
	""" %(form['recipeName'].value,form['recipeName'].value,form['recipeName'].value,form['recipeName'].value)


cursor=con.cursor()
cursor.execute("select recipeName,description from gRecipes WHERE recipeName = '%s' ;" %(form['recipeName'].value))
for row in cursor:
	(recipe,description)=row
cursor.close()
print "<div class=\"container\">"



print """


            <div class="grid fluid">

                <div class="row">
                    <div class="span12">
"""

if not export:
	print """
			<form method='POST' action='cgiUpdateDescription.py'>	
				<input type='hidden' value='%s' name='recipeName'>
				<textarea rows=4 cols=80 name="description">%s</textarea><br>
		""" %(form['recipeName'].value,description)
	
	if theme.localUser:
		print """
				<input type='submit' value='update description'>
		"""
	print """
			</form>
	 """

if export:
	print description
print """
		</div>
		</div>
"""

if not export:

	print """

                <div class="row">
                    <div class="span4">

                        <div id='calculateOutstanding' class="panel" style='visibility: hidden' onClick="recalculate()">
                            <div class="panel-header bg-darkRed fg-white">
                                Recalculate
                            </div>
                        </div>


                    </div>

                    <div class="span4">
                    </div>
"""

if not export and theme.localUser:
	print """
                    <div class="span4">
                        <div class="panel" data-role="panel">
                            <div class="panel-header bg-darkRed fg-white">
                                Clone Recipe
                            </div>
                            <div class="panel-content" style="display:none">
				<form method=POST action='cloneRecipe.py'>
             			<input type='text' name='newrecipe' id='newrecipe' value=''> <input type='submit' value='Clone Recipe'>
				<input type='hidden' name='oldrecipe' value='%s'>
				</form>
                            </div>
                        </div>
                    </div>
""" %(form['recipeName'].value)

	print """
			</div>

	"""

print """
            </div>
"""



activeCalclog=""
activeStats="active "
activeFermentables=""
activeHops=""
activeYeast=""
activeMisc=""
if form.has_key("active") or export:
	if not export:	activeStats=""
	if export or form['active'].value == "fermentables":	activeFermentables = "active "
	if export or form['active'].value == "hops":	activeHops = "active "
	if export or form['active'].value == "yeast":	activeYeast = "active "
	if export or form['active'].value == "misc":	activeMisc = "active "
	if export or form['active'].value == "calclog":	activeCalclog="active"
print """


    <div class="accordion" data-role="accordion">


"""


print """
    <div class="accordion-frame">
	    	<a href="#" class="%sheading">Recipe Stats</a>

	    	<div class="content">
			<p>
""" %(activeStats)
cursor=con.cursor()
cursor.execute("select recipeName,process,mash_efficiency,alkalinity from gRecipes WHERE recipeName = '%s' ;" %(form['recipeName'].value))
mashEfficiency=0
for row in cursor:
	(reipceName,process,mashEfficiency,alkalinity)=row

#cursor=db.query("select recipe,batchsize,estimated_og,estimated_fg,estimated_abv,estimated_ibu,topupvol,boil_vol from gRecipeStats WHERE recipe = '%s' AND brewlog = '';" %(form['recipeName'].value))
cursor=db.query ("select recipe,estimated_og,estimated_fg,estimated_abv,estimated_ibu,topupvol,boil_vol,batchsize from gRecipeStats WHERE recipe='%s' AND process = '%s' ORDER BY entity DESC LIMIT 0,1" %(form['recipeName'].value,process))
result=db.use_result()
row=result.fetch_row()
#((recipe,batchsize,estimatedOg,estimatedFg,estimatedAbv,estimatedIbu,topup,boilVolume),)=row
((recipe,estimatedOg,estimatedFg,estimatedAbv,estimatedIbu,topup,boilVolume,batchsize),)=row


#result=db.use_result()
#row=result.fetch_row()
#
if not export and theme.localUser:
	print "<b>Batch Size:</b> <select id='batchsize'>"
	
	for c in range(45):
		C=c+1
		selected=""
		if float(C) == float(batchsize):
			selected="SELECTED "
		print "<option value='%s' %s>%s L</option>" %(C,selected,C)

	print "</select>"
	print """<a href='javascript:adjustBatchSize()'><i class="icon-checkmark fg-blue"></i></a>""";
	print "<BR>"
else:
	print "<b>Batch Size:</b> %.1f L<BR>" %(float(batchsize))

print "<b>Process:</b> %s<BR>" %(process)

print """
<b>Estimated Gravity:</b> %.3f OG - %.3f FG<br>
<b>Estimated ABV:</b> %.1f %%<br>
<b>Estimated IBU:</b> %.0f IBU<br>
<b>Mash Efficiency:</b> %.1f %%<br>
<b>Alkalinity:</b> %.1f CaCo3 mg/l<br>
<b>Boil Volume:</b> %.1f L<br>
<b>Topup Volume:</b> %.1f L<br>
  

""" %(float(estimatedOg),float(estimatedFg),float(estimatedAbv),float(estimatedIbu),float(mashEfficiency),float(alkalinity),float(boilVolume),float(topup) ) 

if export:
	print "<b>Calclog:</b> <a href='calclog.py?recipeName=%s&noheader=%s'>View Log</a><BR>" %(form['recipeName'].value,form['noheader'].value)
print """
			</p>
		</div>
    </div>
	"""








#
#
#
# Fermentables
#
#
#

print """ 
    <div class="accordion-frame">
   		<a href="#" class="%sheading">Fermentables</a>
	    	<div class="content">
			<p>

 <table class="table" width=80%%>
                        <thead>
                        <tr>
			    <th class="text-left" width=%s>&nbsp;</th>
                            <th class="text-left" width=200>Qty</th>
                            <th class="text-left">Ingredient</th>
                        </tr>
                        </thead>

                        <tbody>
""" %(activeFermentables,colWidth)

itemType='fermentables'
if not export and theme.localUser:
	print """
	<tr><td><a href="javascript:addItem('%s')"><i class='icon-plus fg-green'></i></a></td>
	<td><select id='%sQty'>""" %(itemType,itemType)
	for c in range(750):
		print "<option value='%s'>%s gm</option>" %(c*10,c*10)
	print """</select><td><select id='%sItem'>""" %(itemType)
	cursor=con.cursor()
	cursor.execute("select idx,name,isGrain,isAdjunct FROM gItems where majorcategory ='%s' order by name" %(itemType))
	for row in cursor: 
		(idx,name,isGrain,isAdjunct) = row
		row=result.fetch_row()
		if isGrain:
			val="%s (Grain)" %(name)
		elif isAdjunct:
			val="%s (Adjunct)" %(name)
		else:
			val="%s" %(name)
		key=name
		print "<option value=\"%s\">%s</option>" %(key,val)
	print "</select>"

	print """<td><td></td></tr>
	"""
sumGravity=0
i=0
cursor=con.cursor()
cursor.execute("select recipeName,ingredient,qty,mustMash,isGrain,isAdjunct,hwe,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = 'fermentables' ORDER BY qty DESC" %(form['recipeName'].value))
for row in cursor:
	(recipe,ingredient,qty,mustMash,isGrain,isAdjunct,hwe,unit)=row
	row=result.fetch_row()
	if export:
		print "<tr><td>&nbsp;</td>"
		print "<td>%.0f %s</td><td><b>%s</b><br>" %(float(qty),unit,ingredient)
	else:
		print "<tr><td><a href='editIngredient.py?action=delete&type=%s&ingredient=%s&hopAddAt=%s&recipe=%s'><i class='icon-minus fg-red'></i></a></td>" %(itemType,ingredient,0,form['recipeName'].value)
		print "<td id='%sQtyCell%s'><a href=\"javascript:editqty('%s',%s,%.0f,'%s',%s)\">%.0f %s</a></td><td><b>%s</b><br>" %(itemType,i,itemType,i,float(qty),ingredient,0,float(qty),unit,ingredient)
	if isAdjunct:	print "Adjunct<br>"
	if isGrain:	print "Grain<br>"
	if mustMash:	print "Mash Required<br>"
	print "HWE: %.1f<br>" %(float(hwe))

	print "</td><td>"
	subcursor=con2.cursor()
	subcursor.execute("select recipeName,gravity from gContributions where recipeName='%s' and ingredientType='fermentables' AND ingredient='%s' AND gravity > 0 ORDER BY entity DESC LIMIT 0,1" %(form['recipeName'].value,ingredient) )
	for subrow in subcursor:
		(xxx,gravity)=subrow
		print "Gravity: %.3f" %(1+(gravity/1000))
		sumGravity=sumGravity+gravity
	print "</td></tr>"
	i=i+1
cursor.close()

print """
	<tr><td colspan=3></td><td>Gravity: %.3f</td></tr>	
	""" %(1+(sumGravity)/1000)
print """

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>
    </div>
"""










#
#
#
# Hops
#
#
#

print """ 
    <div class="accordion-frame">
   		<a href="#" class="%sheading">Hops</a>
	    	<div class="content">
			<p>

 <table class="table">
                        <thead>
                        <tr>
			    <th class="text-left" width=%s>&nbsp;</th>
                            <th class="text-left" width=200>Qty</th>
                            <th class="text-left">Ingredient</th>
				<th class="text-left"></th>

                        </tr>
                        </thead>

                        <tbody>
""" %(activeHops,colWidth)

sumIbu=0
if not export and theme.localUser:

	hop_values=[0.009,0.001,5,15,60,20.222]
	hop_labels = {60:'Copper (60min)',15:'Aroma (15min)',5:'Finishing (5min)',0.001:'Flameout (0min)',0.009:'Dryhop',20.222:'First Wort Hop' }
	print """
	<tr><td><a href="javascript:addItem('%s')"><i class='icon-plus fg-green'></i></a></td>
	<td><select id='%sQty'>""" %(itemType,itemType)
	for c in range(500):
		print "<option value='%s'>%s gm</option>" %(c,c)
	print """</select><td><select id='%sItem'>""" %(itemType)
	cursor=con.cursor()
	cursor.execute("select idx,name, hopAlpha,hopUse from gItems where category ='hop' order by name")
	for row in cursor:
		(idx,name,hopAlpha,hopUse) = row
		row=result.fetch_row()
		if len(hopUse):
			val="%s %s %s %%" %(name,hopUse,hopAlpha)
		else:
			val="%s %s %%" %(name,hopAlpha)
		key=name
		print "<option value=\"%s\">%s</option>" %(key,val)
	print "</select>"
	print "<br><select id='hopAddAt'>"
	for hopAddAt in hop_values:
		print "<option value='%s'>%s</option>" %(hopAddAt,hop_labels[hopAddAt])
	print "</select>"
	print "</td><td>"
	
	print """<td></tr>
	"""

i=0
def hops(hopAddAtA,hopAddAtB):
	global hops,form,sumIbu,i
	hop_values=[0.009,0.001,5,15,60,20.222]
	hop_labels = {60:'Copper (60min)',15:'Aroma (15min)',5:'Finishing (5min)',0.001:'Flameout (0min)',0.009:'Dryhop',20.222:'First Wort Hop' }
	itemType='hops'
	cursor=con.cursor()
	cursor.execute("select recipeName,ingredient,qty,hopAddAt,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = '%s' AND hopAddAt >=%s and hopAddAt <=%s ORDER BY hopAddAt DESC,qty DESC" %(form['recipeName'].value,itemType,hopAddAtA,hopAddAtB))
	for row in cursor:
		(recipe,ingredient,qty,hopAddAt,unit)=row
		row=result.fetch_row()
		if export or not theme.localUser:
			print "<tr><td>&nbsp;</td>"
			print "<td>%.0f %s</a></td><td><b>%s</b><br>" %(float(qty),unit,ingredient)
		else:
			print "<tr><td><a href='editIngredient.py?action=delete&type=%s&ingredient=%s&hopAddAt=%s&recipe=%s'><i class='icon-minus fg-red'></i></a></td>" %(itemType,ingredient,hopAddAt,form['recipeName'].value)
			print "<td id='%sQtyCell%s'><a href=\"javascript:editqty('%s',%s,%.0f,'%s',%s)\">%.0f %s</a></td><td><b>%s</b><br>" %(itemType,i,itemType,i,float(qty),ingredient,hopAddAt,float(qty),unit,ingredient)

		if hop_labels.has_key( hopAddAt ):
			print "%s - " %(hop_labels[hopAddAt])
		print "%.0f min<br>" %(float(hopAddAt))
	#	print "Estimate %.0f IBU</td></tr>" %(float(
		i=i+1
		print "</td><td>"
		subcursor=con2.cursor()
		subcursor.execute("select recipeName,ibu from gContributions where recipeName='%s' and ingredientType='hops' AND ingredient='%s' AND hopAddAt > %s AND hopAddAt < %s   ORDER BY entity DESC LIMIT 0,1" %(form['recipeName'].value,ingredient, hopAddAt-0.02, hopAddAt+0.02) )
		for subrow in subcursor:
			(xxx,ibu)=subrow
			print "%.1f IBU" %(ibu)
			sumIbu=sumIbu+ibu

		print "</td></tr>"
	cursor.close()




hops(20,21)
hops(20.3,6000)
hops(0,20.1)

print """
	<tr><td colspan=3></td><td>%.1f IBU</td></tr>	
	""" %(sumIbu)


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
                            <th class="text-left" width=%s>&nbsp;</th>
                            <th class="text-left" width=200>Qty</th>
                            <th class="text-left">Ingredient</th>
                        </tr>
                        </thead>

                        <tbody>
""" %(activeYeast,colWidth)

cursor=con.cursor()
cursor.execute("select recipeName,ingredient,qty,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = 'yeast' ORDER BY qty DESC" %(form['recipeName'].value))
for row in cursor:
	(recipe,ingredient,qty,unit)=row
	row=result.fetch_row()
	print "<tr><td>&nbsp;</td><td>%.0f %s</td><td><b>%s</b><br>" %(float(qty),unit,ingredient)
	print "</td></tr>"
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
   		<a href="#" class="%sheading">Other</a>
	    	<div class="content">
			<p>

 <table class="table">
                        <thead>
                        <tr>
                            <th class="text-left" width=%s>&nbsp;</th>
                            <th class="text-left" width=200>Qty</th>
                            <th class="text-left">Ingredient</th>
                        </tr>
                        </thead>

                        <tbody>
""" %(activeMisc,colWidth)

cursor=con.cursor()
cursor.execute("select recipeName,ingredient,qty,unit FROM gIngredients WHERE recipeName = '%s' AND ingredientType = 'misc' ORDER BY qty DESC" %(form['recipeName'].value))
for row in cursor:
	(recipe,ingredient,qty,unit)=row
	row=result.fetch_row()
	print "<tr><td>&nbsp;</td><td>%.0f %s</td><td><b>%s</b><br>" %(float(qty),unit,ingredient)
	print "</td></tr>"
cursor.close()

print """

                        </tbody>

                        <tfoot></tfoot>
                    </table>

		</p>
		</div>
    </div>
"""




if not export:
	print """ 
	    <div class="accordion-frame">
			<a href="#" class="%sheading">Calclog</a>
			<div class="content">
				<p>
	""" %(activeCalclog)

if not export or not theme.localUser:
	print """
	 <table class="table">
				<thead>
				<tr>
				    <th class="text-left" width=100>&nbsp;</th>
				</tr>
				</thead>

				<tbody>
	""" 

	cursor=con.cursor()
	cursor.execute("select recipe,calclog FROM gCalclogs WHERE recipe = '%s' ORDER BY entity DESC LIMIT 0,1" %(form['recipeName'].value))
	for row in cursor:
		(recipe,calclog)=row
		row=result.fetch_row()
		print "<tr><td><tt>%s</tt>" %(re.compile(" ").sub('&nbsp;',re.compile("[\n\r]").sub('<BR>', calclog)))
		print "</td></tr>"
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


if not export and theme.localUser:
	print "</div>"
	print """
	<a href="?recipeName=%s&export=True"><i class="icon-link-2"></i></a>
	""" %(form['recipeName'].value)

theme.presentFoot()

cursor=db.query("select recipeName,calculationOutstanding from gRecipes WHERE recipeName = '%s';" %(form['recipeName'].value))
result=db.use_result()
row=result.fetch_row()
((recipe,calculationOutstanding),)=row

if calculationOutstanding == "1":


#if form.has_key("outstandingSig"):
	print """<script language=Javascript>
document.getElementById('calculateOutstanding').style.visibility="visible";
//recalculate();
</script>"""
