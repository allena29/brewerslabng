#!/usr/bin/python
import cgi
import os
import sys
form=cgi.FieldStorage()

print "Content-Type: text/html\n\n"


if form.has_key("refreshit"):
	sys.stderr.write("sending ssh reresh\n")
	os.system("ssh -lallena29 192.168.1.14 \"touch /tmp/dbg_button2\" >/dev/null")
	sys.exit(0)
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
	
    <title>%s Graph</title>

</head>
<body class="metro" style="background-color: #ffffff">

""" %(form['graph'].value)

print """
<form>
<input type='hidden' id='graph' value='%s'>
<p>Min Threshold: <input type='text' size=3 id='min' value='%s'> Max Threshold: <input type='text' size=3 id='max' value='%s'> Start Timespan: <input type='text' size=5 id='timespan' value='%s'> End Timespan: <input type='text' size='3' id='timespan2' value='%s'>  <input type='button' value='Update' onClick='reloadGraph()'><BR>
</form>""" %(form['graph'].value, form['min'].value, form['max'].value, form['timespan'].value ,'1')
print """
<iframe width=1 height=1 frameborder=no src="about:blank" id="graphRefresh"></iframe>
<iframe width=100% height=100% frameborder=no src="about:blank" id="graphFrame"></iframe>
<script language="Javascript">
 function reloadGraph(){
   d = new Date()
   document.getElementById('graphRefresh').src ="popupGraph.py?refreshit=True&uniq2="+d.getTime();
   document.getElementById('graphFrame').src ="http://pacificgem.home.mellon-collie.net/piTempMonitor/cgi-bin/graph.py?graph="+document.getElementById("graph").value + "&min=" +document.getElementById("min").value + "&max="+document.getElementById("max").value + "&end=-"+document.getElementById("timespan2").value+"&start=-"+document.getElementById("timespan").value + "&uniq2="+d.getTime();

 }
 reloadGraph();
</script>
"""
