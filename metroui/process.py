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


if not form.has_key("process"):

	theme.bodytitle="Select Process"
	cursor=db.query("select entity,process FROM gProcesses ORDER BY process")
	result=db.use_result()
	row=result.fetch_row()
	while row:
		((entity,processName),)=row
		grid[processName]={'url2':'process.py?process=%s' %(processName),'text':'%s' %(processName)}
		row=result.fetch_row()
elif not form.has_key("activity"):
	theme.bodytitle="Process %s" %(form['process'].value)

	process=form['process'].value


	cursor=db.query("select activityNum,stepNum,subStepNum,stepName from gProcess where process='%s' ORDER BY activityNum,stepNum,subStepNum" %(process))
	result=db.use_result()
	row=result.fetch_row()
	while row:
		((activityNum,stepNum,subStepNum,stepName),)=row
		if stepNum == '-1' and subStepNum == '-1' and not activityNum == "-1":
			grid[activityNum]={'url2':'process.py?process=%s&activity=%s' %(process,activityNum),'text':'%s' %(stepName)}
		row=result.fetch_row()
elif form.has_key("activity") and form.has_key("process"):
	theme.bodytitle="Process %s / Activity %s" %(form['process'].value,form['activity'].value)

theme.presentHead()
theme.presentBody()

if not form.has_key("recipeName") and 1==0:

	if theme.localUser:
		print """

			    <div class="grid fluid">
				<div class="row">
				    <div class="span8">
					</div>
			    <div class="span4">
				<div class="panel" data-role="panel">
				    <div class="panel-header bg-darkRed fg-white">
					Create New Recipe
				    </div>
				    <div class="panel-content" style="display:none">
					<form method=POST action='createRecipe.py'>
					<input type='text' name='newrecipe' id='newrecipe' value=''> <input type='submit' value='Create'>
					</form>
				    </div>
				</div>
			    </div>
			</div>
		</div>
	""" 
theme.doGrid(grid)



import re
def safeText(text):
	return re.compile('%%').sub('%',text)

if form.has_key("activity") and form.has_key("process"):
	print "<div class='container'>"
	cursor3=db3.query("select * from gBrewlogs where process='%s'" %(form['process'].value))
	result3=db3.use_result().fetch_row()
	if result3:
		print "<h4 class='fg-red'>Process has active brewlogs- editing disabled</h4>"
		editable=False
	print "<table class='table striped bordered hovered'>"
	print "<thead><tr><th width=100>Step</th><th>Details</th></tr></thead><tbody>"
	process=form['process'].value
	activity=form['activity'].value
	cursor=db.query("select activityNum,stepNum,stepName,text from gProcess where process='%s' AND activityNum = %s AND stepNum > -1 AND subStepNum = -1  ORDER BY activityNum,stepNum,subStepNum" %(process,activity))
	result=db.use_result()
	row=result.fetch_row()
	while row:
		((activityNum,stepNum,stepName,text),)=row
		row=result.fetch_row()
		print "<tr><td>%s</td>" %(stepNum)
		if editable:
			print "<td>Step: <input type=text size=128 name='stepName' value='%s'></input>" %( safeText(stepName))
			print "<textarea cols=128 rows=5 name='text'>%s</textarea>" %(text)
		else:
			print "<td>Step: %s<BR>" %( safeText(stepName))
			print "Text: %s<BR>" %(text)
	
	

		subSteps=False
		cursor2=db2.query("select subStepNum,stepName from gProcess where process='%s' AND activityNum = %s AND stepNum = %s  AND subStepNum > -1  ORDER BY activityNum,stepNum,subStepNum" %(process,activity,stepNum))
		result2=db2.use_result()
		row2=result2.fetch_row()
		if row2:
			print "<blockquote><b>Sub Steps</b><br>"
			subSteps=True
		while row2:
			((subStepNum,subStepName),)=row2
			if editable:
				print "<li> <input type=text name='subStep_%s' value='%s' size=100><BR>" %(subStepNum,safeText(subStepName))
			else:
				print "<li> %s<BR>" %(safeText(subStepName))
			row2=result2.fetch_row()	


		if subSteps:		
			print "</blockquote>"
		print "</td>\n"
		print "</tr>\n\n"
	print "</tbody></table>"
theme.presentFoot()
	
