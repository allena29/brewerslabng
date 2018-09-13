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
		<div id='temp' class='balloon top'>
		<b>	<span id='tempLabelA'>
			</span></b> <BR>
			<span id='tempResultsA'>
			</span>
		</div>
		<div id='temp' class='balloon top'>
		<b>	<span id='tempLabelB'>
			</span></b> <BR>
			<span id='tempResultsB'>
			</span>
		</div>
		<div id='temp' class='balloon top'>
		<b>	<span id='tempLabelC'>
			</span></b> <BR>
			<span id='tempResultsC'>
			</span>
		</div>
	</div>
    </div>
</div>
"""

print """
<script lanaguage=Javascript>
 function timerTemp(){
      if (http_request.readyState==4 && http_request.status==200)    {
	requireRefresh=0;
	d=new Date();
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
	replacement="";
	tempBgColour="white";

	//
	// timer
	//
	//

	if(xmldoc.getElementsByTagName('timerActive').item(0).firstChild.data == "True"){
		requireRefresh=1;
		serverTime=parseInt(xmldoc.getElementsByTagName("serverTime").item(0).firstChild.data);
		startTime=parseInt(xmldoc.getElementsByTagName("startTime").item(0).firstChild.data);
		expireTime=parseInt(xmldoc.getElementsByTagName("expireTime").item(0).firstChild.data);
		expireStamp=xmldoc.getElementsByTagName("expireStamp").item(0).firstChild.data;
		startStamp=xmldoc.getElementsByTagName("startStamp").item(0).firstChild.data;
		// where we are saying hours and minutes we really mean minutes and seconds.  in all place	
		timerSet=expireTime-startTime;
		setHour=parseInt(timerSet/60);
		setMin= timerSet- (setHour)*60;

		timerCountdown=expireTime-serverTime;
		countdownHour=parseInt(timerCountdown/60);
		countdownMin= timerCountdown- (countdownHour)*60;
	
		timerProgress=serverTime-startTime;
		progressHour=parseInt(timerProgress/60);
		progressMin= timerProgress- (progressHour)*60;

		if(progressMin<10){
			leadingMin="0";
		}else{
			leadingMin="";
		}
		
		if(countdownMin<0){
			countdownMin=-countdownMin;
		}
		if(countdownMin<10){
			leadingMin2="0";
		}else{
			leadingMin2="";
		}
		t="green";
		if(timerCountdown<120){
			t="orange";
		}
		if(timerCountdown<0){
			t="red";
		}
		replacement="<span style='background: "+t+";color: white'>";
		replacement=replacement+"Start: "+startStamp+" &nbsp; "+progressHour+":"+leadingMin+progressMin +" min <BR>";
		replacement=replacement+"Set: "+setHour+":"+setMin +" min &nbsp; <a href='javascript:stopTimer()'>Stop Timer</a> <BR>";
		replacement=replacement+"Expires: "+ expireStamp +" &nbsp; ("+countdownHour+":"+leadingMin2+countdownMin +" min) <BR>";
		replacement=replacement+"</span>";
		document.getElementById("timer").innerHTML=replacement;
	}else{
		document.getElementById("timer").innerHTML="<input type='text' size=4 value='60' id='timerDuration'> <a href='javascript:startTimer()'>Start Timer</a>";
	}

	replacement="";
	if(xmldoc.getElementsByTagName('tempOnline').item(0).firstChild.data == "True"){
		document.getElementById("shutdownTemp").style.visibility="visible";
		document.getElementById("shutdownTemp").style.height="100%";
		document.getElementById("offlineTemp").style.visibility="hidden";
		document.getElementById("offlineTemp").style.height="0px";

		// active temp monitoring
		//
		if(xmldoc.getElementsByTagName('tempActive').item(0).firstChild.data == "True"){

			document.getElementById("startTemp").style.height="0px";
			document.getElementById("startTemp").style.visibility="hidden";
			
			document.getElementById("probeMin").value = xmldoc.getElementsByTagName('probeMin').item(0).firstChild.data;
			document.getElementById("probeMax").value = xmldoc.getElementsByTagName('probeMax').item(0).firstChild.data;
			probes=parseInt( xmldoc.getElementsByTagName('probes').item(0).firstChild.data);
			for(p=0;p<probes;p++){
				t="green";
				if(xmldoc.getElementsByTagName('probe'+p).item(0).firstChild.data < xmldoc.getElementsByTagName('probeMin').item(0).firstChild.data){
					t="blue";
				}
				if(xmldoc.getElementsByTagName('probe'+p).item(0).firstChild.data > xmldoc.getElementsByTagName('probeMax').item(0).firstChild.data){
					t="red";
				}
				document.getElementById('probeId').value= xmldoc.getElementsByTagName('probeLabel').item(0).firstChild.data;
				replacement=replacement+"<span style='background: "+t+";color: white'>" + xmldoc.getElementsByTagName('probeLabel').item(0).firstChild.data + " "+p+": ";
				replacement=replacement+"<b>" + xmldoc.getElementsByTagName('probe'+p).item(0).firstChild.data+"C</b></span><BR>";	
			}
			replacement=replacement+"<font size=-1>" + xmldoc.getElementsByTagName('probeTimestamp').item(0).firstChild.data+" (<a href=javascript:graph()>Graph</a>)</font><BR>";

		setTimeout(getTempTimer,1500);


		}else{
			document.getElementById("startTemp").style.height="100%";
			document.getElementById("startTemp").style.visibility="visible";
		}

		requireRefresh=1;

	}else{

		setTimeout(getTempTimer,5000);
	}
	
 
	if(requireRefresh == 1){
		setTimeout(getTempTimer,5000);
	}

    }
	
 }
function getTempTimer(){
       xmlREQ(updateTemp,"ajaxTimerTemp.py?test=1");
}

getTempTimer();

</script>

"""
