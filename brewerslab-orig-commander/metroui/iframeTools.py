#!/usr/bin/python
import time
import cgi
import sys
import os

form=cgi.FieldStorage()
if form.has_key("stopTimer"):
	try:
		os.unlink("timer-expire")
	except:
		pass
	print "Location: iframeTimerTemp.py\n"
	sys.exit(0)
if form.has_key("startTimer"):
	o=open("timer-expire","w")
	o.write( "%s" %( time.time()+(int(form['duration'].value) * 60)   ))
	o.close()
	print "Location: iframeTimerTemp.py\n"
	sys.exit(0)
print "Content-Type: text/html\n\n"
print """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="css/metro-bootstrap.css" rel="stylesheet">
    <link href="css/metro-bootstrap-responsive.css" rel="stylesheet">
    <link href="css/brewers.css" rel="stylesheet">
    <link href="css/docs.css" rel="stylesheet">
    <link href="js/prettify/prettify.css" rel="stylesheet">
    <!-- Load JavaScript Libraries -->
    <script src="js/jquery/jquery.min.js"></script>
    <script src="js/jquery/jquery.widget.min.js"></script>
    
    <script src="js/jquery/jquery.mousewheel.js"></script>
	<script src="js/prettify/prettify.js"></script>

    <!-- Metro UI CSS JavaScript plugins -->
    <script src="js/load-metro.js"></script>

	<!-- local js -->
    <script src="js/metro-accordion.js"></script>
    <script src="js/metro-listview.js"></script>
    <script src="js/metro-calendar.js"></script>
    <script src="js/metro-datepicker.js"></script>
    <script src="js/docs.js"></script>


    <script src="js/utils.js"></script>
    <script src="js/wwwajax.js"></script>
    <script src="js/brewtools.js"></script>	
    <title>Timer/Temp</title>

</head>
<body class="metro" style="background-color: #ffffff">

<script language=Javascript>
function doGravityTempAdjustment(){
	document.getElementById('adjusted').value = gravityTempAdjustment( parseFloat( document.getElementById('temperature').value), parseFloat( document.getElementById('gravity').value ) );
}
</script>
<div class="grid">
    <div class="row">
        <div class="span12">
		<div id='temp' class='balloon bottom'>
		<table border=0 cellpadding=2>
		<tr><td>Sample Temp</td><td>Sample Gravity</td><td>Adjusted Gravity</td><td></td></tr>
		<tr>	<td><input type='text' id='temperature' value='20' size=4></td>
			<td><input type='text' id='gravity' value='1' size=4"></td>
			<td><input type='text' id='adjusted' value='' size=4 disalbed></td>
			<td><input type='button' onClick='doGravityTempAdjustment()' value="Calculate"></td>
		</tr>
		</table>
		</div>
	</div>
    </div>
</div>
"""

