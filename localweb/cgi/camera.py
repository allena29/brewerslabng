#!/usr/bin/python
import os
import cgi
import sys

form=cgi.FieldStorage()


if form.has_key("get"):

	o=open("/currentdata/cam.jpg")
	sys.stdout.write("Content-Type: image/jpeg\n")
	x=o.read()
	sys.stdout.write("Content-Length: %s\n" %(len(x)))
	sys.stdout.write("\n")
	sys.stdout.write(x)
	o.close()

	os.system("sudo raspistill -o /currentdata/cam.jpg --timeout 1 --nopreview -w 1024 -h 768 -q 33 -ex sports -hf")
else:
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
	  
	"""
	print """
		<img id='myImage' src='loading' width=1024 height=768>

	<script>
	function doImage(){
		var d = new Date();
		$("#myImage").attr("src","camera.py?get="+d.getTime());
		setTimeout(doImage,5000);
	}
		setTimeout(doImage,5);

	</script>
	</html>
	"""
