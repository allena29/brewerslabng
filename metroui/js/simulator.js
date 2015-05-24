
if ('WebSocket' in window){
   /* WebSocket is supported. You can proceed with your code*/
} else {
	alert("Realtime view not available- web browser does not support websockets");
}


//var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator');
var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-lcd');
connection.onmessage = function(e){
//console.log(e.data);
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
console.log(e.data);
obj = JSON.parse(e.data);
ledFound=false;
ledColour="";
ledName="";
if("lSys" in obj){
	ledFound=true;
	ledName="ledSys";
	ledColour=obj.lSys.colour;
}
if("lHlt" in obj){
	ledFound=true;
	ledName="ledHlt";
	ledColour=obj.lHlt.colour;
}
if("lSparge" in obj){
	ledFound=true;
	ledName="ledSparge";
	ledColour=obj.lSparge.colour;
}
if("lBoil" in obj){
	ledFound=true;
	ledName="ledBoil";
	ledColour=obj.lBoil.colour;
}
if("lMash" in obj){
	ledFound=true;
	ledName="ledMash";
	ledColour=obj.lMash.colour;
}
if("lFerm" in obj){
	ledFound=true;
	ledName="ledFerm";
	ledColour=obj.lMash.colour;
}




if(ledFound){
	console.log("ledFound "+ledName+" "+ledColour);
	document.getElementById( ledName ).src="/metroui/realtimeview/led"+ledColour+".png";
}
 
}

connection2.onclose = function(){
//	alert("Simulator session closed");
}



