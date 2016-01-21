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



if form.has_key("createNewName"):
	db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
	cursor=db.query("INSERT INTO gProcesses VALUES (null,'test@example.com','%s');" %(form['createNewName'].value))
	cursor=db.query("INSERT INTO gProcess (entity,owner,process,stepName,activityNum,stepNum,subStepNum) VALUES (null,'test@example.com','%s','Brewday',0,-1,-1);" %(form['createNewName'].value))
	cursor=db.query("INSERT INTO gProcess (entity,owner,process,stepName,activityNum,stepNum,subStepNum) VALUES (null,'test@example.com','%s','Post Bewday',1,-1,-1);" %(form['createNewName'].value))
	cursor=db.query("INSERT INTO gProcess (entity,owner,process,stepName,activityNum,stepNum,subStepNum) VALUES (null,'test@example.com','%s','Bottling',2,-1,-1);" %(form['createNewName'].value))
	print "Location: process.py?process=%s\n" %(form['createNewName'].value)


if form.has_key("cloneNewName"):
	bc=brewerslabCloudApi()
	bc.cloneProcess("test@example.com",form['cloneOldName'].value,form['cloneNewName'].value)
	print "Location: process.py?process=%s\n" %(form['cloneNewName'].value)




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

if not form.has_key("process") and not form.has_key("activity"):

	if theme.localUser:
		print """

			    <div class="grid fluid">
				<div class="row">
				    <div class="span8">
					</div>
			    <div class="span4">
				<div class="panel" data-role="panel">
				    <div class="panel-header bg-darkRed fg-white">
					Create Process
				    </div>
				    <div class="panel-content" style="display:none">
					<form method=POST action='process.py'>
					<input type='text' name='createNewName' id='newrecipe' value=''> <input type='submit' value='Crease'>
					</form>
				    </div>
				</div>
			    </div>
			</div>
		</div>
	"""
if form.has_key("process") and not form.has_key("activity"):

	if theme.localUser:
		print """

			    <div class="grid fluid">
				<div class="row">
				    <div class="span8">
					</div>
			    <div class="span4">
				<div class="panel" data-role="panel">
				    <div class="panel-header bg-darkRed fg-white">
					Clone Process
				    </div>
				    <div class="panel-content" style="display:none">
					<form method=POST action='process.py'>
					<input type='hidden' name='cloneOldName' id='newrecipe' value='%s'> 
					<input type='text' name='cloneNewName' id='newrecipe' value=''> <input type='submit' value='Clone'>
					</form>
				    </div>
				</div>
			    </div>
			</div>
		</div>
	"""  %(form['process'].value)
theme.doGrid(grid)



import re


def safeText(text,highlight=False):
	text=re.compile('%%').sub('%',text)
	text=re.compile('"').sub('&quot;',text)
	return text

if form.has_key("activity") and form.has_key("process"):
	print "<script language=javascript>"
	if not theme.localUser:
		print """
function showEditStep(i){
}
 
		"""

	if theme.localUser:
		print """

function showEditStep(i){
	document.getElementById("row"+i).style.display="none";
	document.getElementById("rowedit"+i).style.display="";
}
	"""

	print "</script>"



	print "<div class='container'>"
	cursor3=db3.query("select * from gBrewlogs where process='%s'" %(form['process'].value))
	result3=db3.use_result().fetch_row()
	if result3:
		print "<h4 class='fg-red'>Process has active brewlogs- editing disabled</h4>"
		editable=False
	if theme.localUser:
		print "<table class='table bordered hovered'>"
	else:
		print "<table class='table bordered'>"
	print "<thead><tr><th width=100>Step</th><th>Details</th></tr></thead><tbody>"
	process=form['process'].value
	activity=form['activity'].value
	cursor=db.query("select activityNum,stepNum,stepName,text,attention from gProcess where process='%s' AND activityNum = %s AND stepNum > -1 AND subStepNum = -1  ORDER BY activityNum,stepNum,subStepNum" %(process,activity))
	result=db.use_result()
	row=result.fetch_row()
	while row:
		((activityNum,stepNum,stepName,text,attention),)=row
		row=result.fetch_row()


		readonly=True
		if form.has_key('edit') and theme.localUser:
			if "%s" %(stepNum) == form['edit'].value:
				readonly=False			
		#
		# Read-Only version
		#
		if readonly:
			print "<tr id='row%s' onClick='showEditStep(%s)'><td>%s</td>" %(stepNum,stepNum,stepNum)
			print "<td><h5>%s</h5>" %( safeText(stepName))
			print "%s<BR>" %( safeText(text, highlight=True))
			if len(attention):
				print "<br><b class='fg-red'>Warning:</b> %s<BR>" %(safeText(attention)) 
			subSteps=False
			cursor2=db2.query("select subStepNum,stepName from gProcess where process='%s' AND activityNum = %s AND stepNum = %s  AND subStepNum > -1  ORDER BY activityNum,stepNum,subStepNum" %(process,activity,stepNum))
			result2=db2.use_result()
			row2=result2.fetch_row()
			if row2:
				print "<blockquote><b>Sub Steps</b><br>"
				subSteps=True
			while row2:
				((subStepNum,subStepName),)=row2
				print "<li> %s<BR>" %(safeText(subStepName))
				row2=result2.fetch_row()	
			if subSteps:		
				print "</blockquote>"


			records=False
			cursor2=db2.query("select fieldKey,fieldLabel from gField where process='%s' AND brewlog = '' AND fieldWidget='' AND activityNum=%s AND stepNum = %s ORDER BY fieldKey" %(process,activity,stepNum))
			result2=db2.use_result()
			row2=result2.fetch_row()
			if row2:
				print "<blockquote><b>Record Fields</b><br>"
				records=True
			while row2:
				((fieldKey,fieldLabel),)=row2
				print "<li> %s (%s)" %(safeText(fieldLabel),fieldKey)
				row2=result2.fetch_row()	
			if records:
				print "</blockquote>"

			# widgets
			records=False
			cursor2=db2.query("select fieldKey,fieldLabel,fieldWidget from gField where process='%s' AND brewlog = '' AND length(fieldWidget) > 0 AND activityNum=%s AND stepNum = %s ORDER BY fieldKey" %(process,activity,stepNum))
			result2=db2.use_result()
			row2=result2.fetch_row()
			if row2:
				print "<blockquote><b>Widget</b><br>"
				records=True
			while row2:
				((fieldKey,fieldLabel,fieldWidget),)=row2
				print "<li> %s (%s %s)" %(safeText(fieldLabel),fieldKey,fieldWidget)
				row2=result2.fetch_row()	
			if records:
				print "</blockquote>"


			print "</td>\n"
			print "</tr>\n\n"


		#
		# Edit version
		# 
		if theme.localUser:
			print "<form method='post' action='cgiUpdateProcess.py'>"
			print "<input type='hidden' name='stepid' value='%s'>" %(stepNum)
			print "<input type='hidden' name='process' value='%s'>" %(form['process'].value)
			print "<input type='hidden' name='activityid' value='%s'>" %(form['activity'].value)
			if readonly:
				print "<tr id='rowedit%s' style='display: none'><td>%s<a name='edit%s'></a></td>" %(stepNum,stepNum,stepNum)
			else:
				print "<tr id='rowedit%s' style=''><td>%s<a name='edit%s'></a></td>" %(stepNum,stepNum,stepNum)
			print "<td><input type=text size=128 name='stepName' value=\"%s\"></input><BR>" %( safeText(stepName))
			print "<textarea cols=128 rows=5 name='text'>%s</textarea><BR>" %( safeText(text) )
		
			if len(attention):
				print "<textarea cols=128 rows=5 name='attention'>%s</textarea><BR>" %( safeText(attention ))

			subSteps=False
			cursor2=db2.query("select subStepNum,stepName from gProcess where process='%s' AND activityNum = %s AND stepNum = %s  AND subStepNum > -1  ORDER BY activityNum,stepNum,subStepNum" %(process,activity,stepNum))
			result2=db2.use_result()
			row2=result2.fetch_row()
			if row2:
				print "<blockquote><b>Sub Steps</b><br>"
				subSteps=True
			while row2:
				((subStepNum,subStepName),)=row2
				print "<li> <input type=text name='subStep_%s' value='%s' size=100><BR>" %(subStepNum,safeText(subStepName))
				row2=result2.fetch_row()	
			if subSteps:		
				print "</blockquote>"


			print "<p align=right><input type='submit' value='Save'></p>"
			print "</td>\n"
			print "</tr>\n"
			print "</form>\n\n\n"



	print "</tbody></table>"
theme.presentFoot()
	
