#!/usr/bin/python

import cgi
import re
import _mysql
import mysql.connector
import time
from ngData import *

form=cgi.FieldStorage()

# The step we should display in an edit mode
editstep=form['stepid'].value
editmode=True





#print "Content-Type:text/html\n\n"
#print form['stepid'].value,form['process'],form['activityid'].value


### Tables that need cleaning up each time we re-arrange
# gField
# gCompileText



con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
cursor=con.cursor()
if form.has_key("button"):
	# Updated Fixed things
	if form.has_key("stepName"):
		cursor.execute("UPDATE gProcess SET stepName ='%s',text='%s' WHERE process='%s' AND activityNum = %s AND stepNum = %s;" %( _mysql.escape_string( form['stepName'].value), _mysql.escape_string( form['text'].value) ,  form['process'].value, form['activityid'].value,form['stepid'].value))

	# Update Optional things
	if form.has_key("attention"):
		if len(form['attention'].value) > 3:
			cursor.execute("UPDATE gProcess SET attention ='%s' WHERE process='%s' AND activityNum = %s AND stepNum = %s;" %( _mysql.escape_string( form['attention'].value), form['process'].value, form['activityid'].value,form['stepid'].value))


	# Update substep's
	subSteps=int(form['substepcount'].value)
	db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
	cursor=db.query("select subStepNum FROM gProcess WHERE process='%s' AND activityNum = %s AND stepNum = %s AND subStepNum > -1" %(form['process'].value,form['activityid'].value,form['stepid'].value))
	result=db.use_result()
	row=result.fetch_row()
	while row:
		((subStepNum,),)=row
		if form.has_key("subStep_%s" %(subStepNum)):
			s=form['subStep_%s' %(subStepNum)].value
			db2=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
			db2.query("UPDATE gProcess set stepName ='%s' WHERE process='%s' AND activityNum = %s AND stepNum = %s AND subStepNum =%s " %(_mysql.escape_string( s), form['process'].value,form['activityid'].value,form['stepid'].value,subStepNum))
		row=result.fetch_row()

if form.has_key("action"):
	if form['action'].value == "deleteSubstep":
		con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
		cursor=con.cursor()
		cursor.execute("delete from gProcess where process='%s' AND activityNum = %s AND stepNum = %s AND subStepNum = %s;" %( form['process'].value,form['activityid'].value,form['stepid'].value,form['substepid'].value))
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		cursor=db.query("select max(numSubSteps),max(subStepNum) FROM gProcess WHERE process='%s' AND activityNum = %s AND stepNum = %s" %(form['process'].value,form['activityid'].value,form['stepid'].value))
		result=db.use_result()
		row=result.fetch_row()
		((numSubSteps,subStepNum),)=row
		numSubSteps=int(numSubSteps)-1
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		cursor=db.query("update gProcess SET numSubSteps = %s WHERE process='%s' AND activityNum = %s AND stepNum = %s" %(numSubSteps,form['process'].value,form['activityid'].value,form['stepid'].value))


	if form['action'].value == "DeleteFullStep":
		editmode=False
	
		# it's useful not having brewlogs attached because we only haev to change process not gBrewlogStep
		editstep=int(form['stepid'].value)-1
		if editstep < 1:	editstep=1
	
		# delete step
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("delete from gProcess WHERE process= '%s' AND activityNum = %s AND stepNum = %s" %( form['process'].value,form['activityid'].value,form['stepid'].value ))
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("delete from gField WHERE process = '%s' AND activityNum = %s AND stepNum = %s" %( form['process'].value,form['activityid'].value,form['stepid'].value ))
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("delete from gCompileText WHERE process ='%s' AND activityNum = %s AND stepNum = %s" %( form['process'].value,form['activityid'].value,form['stepid'].value ))

		# renumber existing steps
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("update gProcess SET stepNum = stepNum - 1 WHERE process='%s' AND activityNum = %s AND stepNum > %s" %( form['process'].value,form['activityid'].value,form['stepid'].value ))
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("update gField SET stepNum = stepNum - 1 WHERE process='%s' AND activityNum = %s AND stepNum > %s" %( form['process'].value,form['activityid'].value,form['stepid'].value ))

		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("update gCompileText SET stepNum = stepNum - 1 WHERE process='%s' AND activityNum = %s AND stepNum > %s" %( form['process'].value,form['activityid'].value,form['stepid'].value ))




	if form['action'].value == "InsertStepBefore" or form['action'].value == "InsertStepAfter":
		# it's useful not having brewlogs attached because we only haev to change process not gBrewlogStep
		if form['action'].value == "InsertStepBefore":
			stepgteq=">="
			newstepid=int(form['stepid'].value)
		else:
			stepgteq=">"
			newstepid=int(form['stepid'].value)+1
		editstep=newstepid

		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("update gProcess SET stepNum = stepNum + 1 WHERE process='%s' AND activityNum = %s AND stepNum %s %s" %( form['process'].value,form['activityid'].value,stepgteq,form['stepid'].value ))
		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("update gField SET stepNum = stepNum + 1 WHERE process='%s' AND activityNum = %s AND stepNum %s %s" %( form['process'].value,form['activityid'].value,stepgteq,form['stepid'].value ))

		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		db.query("update gCompileText SET stepNum = stepNum + 1 WHERE process='%s' AND activityNum = %s AND stepNum %s %s" %( form['process'].value,form['activityid'].value,stepgteq,form['stepid'].value ))

		newStep=gProcess()
		newStep.stepName="New Step #%s" %(newstepid)
		newStep.text=time.ctime()
		newStep.process=form['process'].value
		newStep.activity=form['activityid'].value
		newStep.stepNum=newstepid
		newStep.subStepNum=-1
		newStep.put()


	if form['action'].value == "addSubstep":

		# if we didn't have substeps enter at index 0
		if form['substepid'].value == "-1":
			numSubSteps=1
			subStepId=0

		# if we did have substeps renumber
		if not form['substepid'] == "-1":
			# renumber existing substep id's
			db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
			db.query("update gProcess SET subStepNum = subStepNum + 1 WHERE process='%s' AND activityNum = %s AND stepNum = %s AND subStepNum > %s" %( form['process'].value,form['activityid'].value,form['stepid'].value, form['stepid'].value ))

			con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
			cursor=con.cursor()
			db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
			cursor=db.query("select max(numSubSteps),max(subStepNum) FROM gProcess WHERE process='%s' AND activityNum = %s AND stepNum = %s" %(form['process'].value,form['activityid'].value,form['stepid'].value))
			result=db.use_result()
			row=result.fetch_row()
			((numSubSteps,subStepNum),)=row
			numSubSteps=int(numSubSteps)+1
			db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
			db.query("update gProcess SET numSubSteps = %s WHERE process='%s' AND activityNum = %s AND stepNum = %s" %(numSubSteps,form['process'].value,form['activityid'].value,form['stepid'].value))

			subStepId=int(form['substepid'].value)+1


		db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")
		sql=    "insert into gProcess (owner,process,stepName,stepTitle,activityNum,stepNum,subStepNum"
		sql=sql+",text,img,attention,timerName,timerTime,fixed_boil_off,fixed_cool_off,percentage_boil_off,percentage_cool_off,auto,needToComplete"
		sql=sql+",compileStep,conditional,numSubSteps) "
		sql=sql+" VALUES ('test@example.com','%s','{new substep}','',%s,%s,%s"	%(form['process'].value,form['activityid'].value,form['stepid'].value,subStepId)
		sql=sql+",'','','','',0,0,0,0,0,'',1,0,'',%s)" %( numSubSteps )
		cursor=db.query(sql)



if editmode:
	print "Location: process.py?process=%s&activity=%s&edit=%s#edit%s\n" %(form['process'].value,form['activityid'].value,editstep,editstep)
else:
	print "Location: process.py?process=%s&activity=%s#edit%s\n" %(form['process'].value,form['activityid'].value,editstep)

