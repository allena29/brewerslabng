#!/usr/bin/python
import time
import os
import re
import cgi
form=cgi.FieldStorage()
print """
<!DOCTYPE html>
<html>
<head>
    <script src="../js/jquery-1.12.0.min.js"></script>
    <link href="../css/metro.css" rel="stylesheet">
    <script src="../js/metro.min.js"></script>
	<link href="../css/metro-icons.css" rel="stylesheet">

<body>
    <div class="page-content">

	<div class="container">
  
	<h1>Graphs</h1>
	<p>List last updated: 
"""

print time.ctime(os.stat("archivedata/").st_mtime )

filenameTemp=re.compile("(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2}).*_(\d+)\.rrd\.png")


tempResults={}
for probe in os.listdir("archivedata"):
	if filenameTemp.match( probe):
		(year,month,date,hour,min,baseTime)=filenameTemp.match(probe).groups()
		if not tempResults.has_key( baseTime):
			tempResults[baseTime]=[]
		tempResults[baseTime].append( (year,month,date,hour,min,probe) )

tempActs=tempResults.keys()
tempActs.sort()

for act in tempActs:
	print "<li> <a href=temps.py?baseTime=%s>%s</a>" %(act,time.ctime( int(act)))


if form.has_key("baseTime"):
	print "<hr>"
	
	baseTime=form['baseTime'].value
	tempResults[baseTime].sort()

	uniqueDays=[]
	for x in tempResults[baseTime]:
		(year,month,date,hour,min,probe) =x
		if not "%s-%s-%s" %(year,month,date) in uniqueDays:
			uniqueDays.append("%s-%s-%s" %(year,month,date))


	for day in uniqueDays:
		print "<li> <a href=temps.py?baseTime=%s&day=%s>%s</a>" %(baseTime,day,day)	
	print "<li> <a href=temps.py?baseTime=%s>Latest Graph</a>" %(baseTime)

	print """<li> <a href="javascript:showDialog('#deleteDialog')">Delete Graph/Data</a>"""
	print "<p>"

	
	(year,month,date,hour,min,probe) = tempResults[baseTime][-1]
	if not form.has_key("day"):
		print "Latest Graph - Generated %s-%s-%s %s:%s<p>" %(year,month,date,hour,min)
		print "<img src=../archivedata/%s>" %(probe)	 
	else:
		tempResults[baseTime].sort()
		tempResults[baseTime].reverse()
		for x in tempResults[baseTime]:
			(year,month,date,hour,min,probe) =x
			if "%s-%s-%s" %(year,month,date) == form['day'].value:
				print "Latest Graph for %s-%s-%s - Generated %s-%s-%s %s:%s<p>" %(year,month,date,year,month,date,hour,min)
				print "<img src=../archivedata/%s>" %(probe)
				break
		
	
print """

<div data-role="dialog" id="deleteDialog" style='padding: 15px'>
    <h1>Delete Graphs</h1>
    <p>

	<b>To delete these graphs and data enter the admin password below</b>
		<BR>
	Admin Password: 
			<div class="input-control password" data-role="input">
			    <input type="password" id='password' value="">
			    <button class="button helper-button reveal"><span class="mif-looks"></span></button>
			</div>
	<P>
	<input id='cancelButton' type='button' value='Cancel' onClick="cancelDialog('deleteDialog')"> &nbsp; - &nbsp;
	<input type='button' value='Delete' onClick="confirmdelete()">
	
    </p>
</div>
"""

if form.has_key("baseTime"):

	print """
	<script language="Javascript">
		function confirmdelete(){
			$.ajax({
			    url: "dographs.py?baseTime=%s&adminpass="+$("#password").val(),
			    error: function(){
				alert("Unable to delete data");
			    },
			    success: function(xml){
				alert("Done");
				location.replace("temps.py")
			    },
			    timeout: 5000 // sets timeout to 3 seconds
			});
		}
	""" %(form['baseTime'].value)
	print """
	    function cancelDialog(id){	
		$("#"+id).hide();
	    }
	    function showDialog(id){


		var dialog = $(id).data('dialog');
		dialog.open();
		$(""+id).show();
	    }

	</script>

	"""

print """

<footer class='app-bar fixed-bottom drop-up'>brewerslab - <a href="https://github.com/allena29/brewerslab/"><span class='fg-white'> &nbsp; <span class="mif-github"></span> &nbsp;github.com/allena29/brewerslab</span></a></footer>

</body>



</html>
"""
