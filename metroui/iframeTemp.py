#!/usr/bin/python
import time
import cgi
import sys
import os

form=cgi.FieldStorage()
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
	
    <title>Timer/Temp</title>

</head>
<body class="metro" style="background-color: #ffffff">

<div class="grid">
    <div class="row">
        <div class="span2">
		<div id='probeA' class='balloon top' style='visibility: hidden'>
		<b>	<span id='probeAlabel'>
			</span></b> <BR>
			<span id='probeAtemp'>
			</span>
		</div>
	</div>
        <div class="span2">
		<div id='probeB' class='balloon top' style='visibility: hidden'>
		<b>	<span id='probeBlabel'>
			</span></b> <BR>
			<span id='probeBtemp'>
			</span>
		</div>
	</div>
        <div class="span2">
		<div id='probeC' class='balloon top' style='visibility: hidden'>
		<b>	<span id='probeClabel'>
			</span></b> <BR>
			<span id='probeCtemp'>
			</span>
		</div>
	</div>
    </div>
</div>
"""

print """
<script lanaguage=Javascript>
 function updateTemp(){
      if (http_request.readyState==4 && http_request.status==200)    {
	requireRefresh=0;
	d=new Date();
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
	replacement="";
	tempBgColour="white";

	probe="probeA"
	colour=xmldoc.getElementsByTagName(probe+"colour" ).item(0).firstChild.data;
	if(colour == "disabled"){
		document.getElementById( probe ).style.visibility="hidden";
	}else{
		requireRefresh=1;
		document.getElementById( probe ).style.visibility="visible";
		document.getElementById( probe+"label").innerHTML= xmldoc.getElementsByTagName(probe+"label").item(0).firstChild.data;
		document.getElementById( probe+"temp").innerHTML= xmldoc.getElementsByTagName(probe+"temp").item(0).firstChild.data;
		if(colour=="red"){
			document.getElementById(probe).className = "balloon top bg-red";
		}
		if(colour=="green"){
			document.getElementById(probe).className = "balloon top bg-green";
		}
		if(colour=="blue"){
			document.getElementById(probe).className = "balloon top bg-blue";
		}
	}

	probe="probeB"
	colour=xmldoc.getElementsByTagName(probe+"colour" ).item(0).firstChild.data;
	if(colour == "disabled"){
		document.getElementById( probe ).style.visibility="hidden";
	}else{
		requireRefresh=1;
		document.getElementById( probe ).style.visibility="visible";
		document.getElementById( probe+"label").innerHTML= xmldoc.getElementsByTagName(probe+"label").item(0).firstChild.data;
		document.getElementById( probe+"temp").innerHTML= xmldoc.getElementsByTagName(probe+"temp").item(0).firstChild.data;
		if(colour=="red"){
			document.getElementById(probe).className = "balloon top bg-red";
		}
		if(colour=="green"){
			document.getElementById(probe).className = "balloon top bg-green";
		}
		if(colour=="blue"){
			document.getElementById(probe).className = "balloon top bg-blue";
		}
	}

	probe="probeC"
	colour=xmldoc.getElementsByTagName(probe+"colour" ).item(0).firstChild.data;
	if(colour == "disabled"){
		document.getElementById( probe ).style.visibility="hidden";
	}else{
		requireRefresh=1;
		document.getElementById( probe ).style.visibility="visible";
		document.getElementById( probe+"label").innerHTML= xmldoc.getElementsByTagName(probe+"label").item(0).firstChild.data;
		document.getElementById( probe+"temp").innerHTML= xmldoc.getElementsByTagName(probe+"temp").item(0).firstChild.data;
		if(colour=="red"){
			document.getElementById(probe).className = "balloon top bg-red";
		}
		if(colour=="green"){
			document.getElementById(probe).className = "balloon top bg-green";
		}
		if(colour=="blue"){
			document.getElementById(probe).className = "balloon top bg-blue";
		}
	}

	

 
	if(requireRefresh == 1){
		setTimeout(getTemp,2500);
	}

    }
	
 }
function getTemp(){
       xmlREQ(updateTemp,"ajaxTemp.py?test=1");
}

getTemp();

</script>

"""
