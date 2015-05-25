
mode="_idle"
volumes = JSON.parse('{"hlt": [0, 0], "ferm": [0, 0], "boil": [0, 0], "mash": [0, 0]}');
gpioSsrA=false;
gpioSsrB=false;


function redrawSim(){
	if(mode == "idle"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";
		document.getElementById("kettle").src="/metroui/realtimeview/simkettle.png";
		document.getElementById("fridge").src="/metroui/realtimeview/simfridge.png";
	}else if(mode == "hlt"){
		if(gpioSsrA==true){
			document.getElementById("hlt").src="/metroui/realtimeview/simhlta.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_hltonoff.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersockethltonoff.png";
		}else if(gpioSsrB==true){
			document.getElementById("hlt").src="/metroui/realtimeview/simhltb.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_hltoffon.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersockethltoffon.png";
		}else{
			document.getElementById("hlt").src="/metroui/realtimeview/simhlt.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_hltoffoff.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";
		}
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";
		document.getElementById("kettle").src="/metroui/realtimeview/simkettle.png";
		document.getElementById("fridge").src="/metroui/realtimeview/simfridge.png";

	}	


}


if ('WebSocket' in window){
   /* WebSocket is supported. You can proceed with your code*/
} else {
	alert("Realtime view not available- web browser does not support websockets");
}


//var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator');
var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-lcd');
connection.onmessage = function(e){
obj = JSON.parse(e.data);
if(obj.line > -1 ){
	document.getElementById('lcd'+obj.line).innerHTML=obj.text+"&nbsp;";
}

 
}

connection.onclose = function(){
	alert("Simulator session closed");
}


var connection2 = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-led');
connection2.onmessage = function(e){
obj = JSON.parse(e.data);
ledFound=false;
ledColour="";
ledName="";
if("lSys" in obj){
	ledFound=true;
	ledName="ledSys";
	ledColour=obj.lSys.colour;
	document.getElementById( ledName ).src="/metroui/realtimeview/led"+ledColour+".png";
}
if("lHlt" in obj){
	ledFound=true;
	ledName="ledHlt";
	ledColour=obj.lHlt.colour;
	document.getElementById( ledName ).src="/metroui/realtimeview/led"+ledColour+".png";
}
if("lSparge" in obj){
	ledFound=true;
	ledName="ledSparge";
	ledColour=obj.lSparge.colour;
	document.getElementById( ledName ).src="/metroui/realtimeview/led"+ledColour+".png";
}
if("lBoil" in obj){
	ledFound=true;
	ledName="ledBoil";
	ledColour=obj.lBoil.colour;
	document.getElementById( ledName ).src="/metroui/realtimeview/led"+ledColour+".png";
}
if("lMash" in obj){
	ledFound=true;
	ledName="ledMash";
	ledColour=obj.lMash.colour;
	document.getElementById( ledName ).src="/metroui/realtimeview/led"+ledColour+".png";
}
if("lFerm" in obj){
	ledFound=true;
	ledName="ledFerm";
	ledColour=obj.lFerm.colour;
	document.getElementById( ledName ).src="/metroui/realtimeview/led"+ledColour+".png";
}


 
}

connection2.onclose = function(){
//	alert("Simulator session closed");
}


var connection3 = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-button');
connection3.onmessage = function(e){
obj = JSON.parse(e.data);

if("swHlt" in obj){
 if(obj.swHlt){
	 document.getElementById("swHlt").src="/metroui/realtimeview/switchred.png";
	 document.getElementById("state_swHlt").value="1"; 
 }else{
	 document.getElementById("swHlt").src="/metroui/realtimeview/pushbutton.png";
	 document.getElementById("state_swHlt").value="0"; 
 }
}
if("swSparge" in obj){
 if(obj.swSparge){
	 document.getElementById("swSparge").src="/metroui/realtimeview/switchred.png";
	 document.getElementById("state_swSparge").value="1"; 
 }else{
	 document.getElementById("swSparge").src="/metroui/realtimeview/pushbutton.png";
	 document.getElementById("state_swSparge").value="0"; 
 }
}
if("swBoil" in obj){
 if(obj.swBoil){
	 document.getElementById("swBoil").src="/metroui/realtimeview/switchred.png";
	 document.getElementById("state_swBoil").value="1"; 
 }else{
	 document.getElementById("swBoil").src="/metroui/realtimeview/pushbutton.png";
	 document.getElementById("state_swBoil").value="0"; 
 }
}
 
if("swMash" in obj){
 if(obj.swMash){
	 document.getElementById("swMash").src="/metroui/realtimeview/switchgreen.png";
	 document.getElementById("state_swMash").value="1"; 
 }else{
	 document.getElementById("swMash").src="/metroui/realtimeview/pushbutton.png";
	 document.getElementById("state_swMash").value="0"; 
 }
}
 
if("swFerm" in obj){
 if(obj.swFerm){
	 document.getElementById("swFerm").src="/metroui/realtimeview/switchgreen.png";
	 document.getElementById("state_swFerm").value="1"; 
 }else{
	 document.getElementById("swFerm").src="/metroui/realtimeview/pushbutton.png";
	 document.getElementById("state_swFerm").value="0"; 
 }
}

if("swPump" in obj){
 if(obj.swPump){
	 document.getElementById("swPump").src="/metroui/realtimeview/switchblue.png";
	 document.getElementById("state_swPump").value="1"; 
 }else{
	 document.getElementById("swPump").src="/metroui/realtimeview/pushbutton.png";
	 document.getElementById("state_swPump").value="0"; 
 }
}
 
}

connection3.onclose = function(){
//	alert("Simulator session closed");
}

var connection4 = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-relay');
connection4.onmessage = function(e){
obj = JSON.parse(e.data);
 
}

connection4.onclose = function(){
//	alert("Simulator session closed");
}


var connection5 = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-ssr');
connection5.onmessage = function(e){
obj = JSON.parse(e.data);
if("gpioSsrA" in obj){
	gpioSsrA=obj.gpioSsrA;
}
if("gpioSsrB" in obj){
	gpioSsrB=obj.gpioSsrB;
}
redrawSim(); 
}

connection5.onclose = function(){
//	alert("Simulator session closed");
}



var connection6 = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-gov');
connection6.onmessage = function(e){
obj = JSON.parse(e.data);
mode=obj._mode;
if("_mode" in obj){
	document.getElementById("mode").innerHTML=obj._mode;
	document.getElementById("brewlog").innerHTML=obj._brewlog;
	document.getElementById("recipe").innerHTML=obj._recipe;
}

if("volmes" in obj){
	volumes=obj.volumes;
}
}

redrawSim();


connection6.onclose = function(){
//	alert("Simulator session closed");
}




function swbutton(b){
	host=window.location.href.split(":54660")[0];
	url=host+":54661/cgi/fakeButtonHandler.py?button="+b;
	if(localUser){
		if(document.getElementById("state_"+b).value == "0"){
			document.getElementById("buttonTarget").src=url+"&onoff=on";
		}else{
			document.getElementById("buttonTarget").src=url+"&onoff=off";
		}
	}else{
		alert("View-only; button disabled");	
	}
}

function button(b){
	host=window.location.href.split(":54660")[0];
	url=host+":54661/cgi/fakeButtonHandler.py?button="+b;
	if(localUser){
		document.getElementById("buttonTarget").src=url;
	}else{
		alert("View-only; button disabled");	
	}
}
