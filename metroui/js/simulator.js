
mode="_idle"
volumes = JSON.parse('{"hlt": [0, 0], "ferm": [0, 0], "boil": [0, 0], "mash": [0, 0]}');
gpioSsrA=false;
gpioSsrB=false;
gpioFermHeat=false;
gpioFermCool=false;

lastMode="_idle"

function redrawSim(){
	if(mode == "idle"){
		if(lastMode == "hlt" || lastMode == "hlt/sparge" || lastMode == "hlt/sparge/mash"){
			document.getElementById("hlt").src="/metroui/realtimeview/simhlt.png";
		}else{	
			document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		}
		document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";

		if(lastMode == "hlt/sparge" || lastMode == "hlt/sparge/mash"){
			document.getElementById("mash").src="/metroui/realtimeview/simmashfull.png";
		}else{
			document.getElementById("mash").src="/metroui/realtimeview/simmash.png";
		}

		if(lastMode == "boil" || lastMode == "boil/pump" || lastMode == "pump/cool"){
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleoffoff.png";	
		}else{
			document.getElementById("kettle").src="/metroui/realtimeview/simkettle.png";	
		}
		document.getElementById("fridge").src="/metroui/realtimeview/simfridge.png";
	}else if(mode == "hlt" || mode == "hlt/sparge" || mode == "hlt/sparge/mash"){
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

		if(mode == "hlt/sparge" || mode == "hlt/sparge/mash"){
			document.getElementById("mash").src="/metroui/realtimeview/simmashfull.png";
		}else{
			document.getElementById("mash").src="/metroui/realtimeview/simmash.png";
		}
		document.getElementById("kettle").src="/metroui/realtimeview/simkettle.png";
		document.getElementById("fridge").src="/metroui/realtimeview/simfridge.png";

	}else if(mode == "mash/dough"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmashfull.png";	
		document.getElementById("kettle").src="/metroui/realtimeview/simkettle.png";
		document.getElementById("fridge").src="/metroui/realtimeview/simfridge.png";
	}else if(mode == "boil"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";	
		if(gpioSsrA==true && gpioSsrB == true){
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleonon.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocketboilonon.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_boilonon.png";
		}else if(gpioSsrA == true && gpioSsrB == false){
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleonoff.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocketboilonoff.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_boilonoff.png";
		}else if(gpioSsrA == false && gpioSsrB == true){
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleoffon.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocketboiloffon.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_boiloffon.png";
		}else{
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleoffoff.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		}
		document.getElementById("fridge").src="/metroui/realtimeview/simfridge.png";
	}else if(mode == "boil/pump"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";	
		if(gpioSsrA==true && gpioSsrB == true){
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleonon_pumpon.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocketboilonon_pumpon.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_boilonon.png";
		}else if(gpioSsrA == true && gpioSsrB == false){
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleonoff_pumpon.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocketboilonoff_pumpon.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_boilonoff.png";
		}else if(gpioSsrA == false && gpioSsrB == true){
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleoffon_pumpon.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocketboiloffon_pumpon.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays_boilonoff.png";
		}else{
			document.getElementById("kettle").src="/metroui/realtimeview/simkettleoffoff_pumpon.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocket_pumpon.png";
			document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		}
		document.getElementById("fridge").src="/metroui/realtimeview/simfridgepumpon_boil.png";
	}else if(mode == "pump/cool"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";	
		document.getElementById("kettle").src="/metroui/realtimeview/simkettleoffoff_pumpon.png";
		document.getElementById("socket").src="/metroui/realtimeview/simpowersocket_pumpon.png";
		document.getElementById("fridge").src="/metroui/realtimeview/simfridgepumpon_boil.png";
	}else if(mode == "ferm-wait"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";	
		document.getElementById("kettle").src="/metroui/realtimeview/simkettleoffoff.png";
		document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";
		document.getElementById("fridge").src="/metroui/realtimeview/simfridge.png";
	}else if(mode == "pump"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";	
		document.getElementById("kettle").src="/metroui/realtimeview/simkettle.png";
		document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";
		document.getElementById("fridge").src="/metroui/realtimeview/simfridgepumpon_transfer.png";
	}else if(mode == "ferm"){
		document.getElementById("hlt").src="/metroui/realtimeview/simhltempty.png";
		document.getElementById("relays").src="/metroui/realtimeview/simrelays.png";
		document.getElementById("mash").src="/metroui/realtimeview/simmash.png";	
		document.getElementById("kettle").src="/metroui/realtimeview/simkettle.png";
		if(gpioFermHeat == true){
			document.getElementById("fridge").src="/metroui/realtimeview/simfridge_heat.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocket_heat.png";
		}else if(gpioFermCool == true){
			document.getElementById("fridge").src="/metroui/realtimeview/simfridge_cool.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocket_cool.png";
		}else{
			document.getElementById("fridge").src="/metroui/realtimeview/simfridge_ferm.png";
			document.getElementById("socket").src="/metroui/realtimeview/simpowersocket.png";
		}
	}


	if(lastMode != mode && mode != "idle"){
		lastMode=mode;
	}

	if(mode == "ferm"){
		document.getElementById("graphimg").src="/metroui/graph-proxy.py";
//		document.getElementById("graph").style.height="100%%";
		document.getElementById("graphTab").style.visibility="visible";		
	}else{
		document.getElementById("graphimg").src="/metroui/spacer.png";
//		document.getElementById("graph").style.height="0%%";
		document.getElementById("graphTab").style.visibility="hidden";

	}
}


if ('WebSocket' in window){
	document.getElementById("websocketState").innerHTML="";
   /* WebSocket is supported. You can proceed with your code*/
} else {
	alert("Realtime view not available- web browser does not support websockets");
}


//var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator');
var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-lcd');
connection.onmessage = function(e){
obj = JSON.parse(e.data);
	document.getElementById("websocketState").innerHTML="";

if(obj.lcd0.importance >= 0){
document.getElementById('lcd0').innerHTML=obj.lcd0.text+"&nbsp;";
}
if(obj.lcd1.importance >= 0){
document.getElementById('lcd1').innerHTML=obj.lcd1.text+"&nbsp;";
}
if(obj.lcd2.importance >= 0){
document.getElementById('lcd2').innerHTML=obj.lcd2.text+"&nbsp;";
}
if(obj.lcd3.importance >= 0){
document.getElementById('lcd3').innerHTML=obj.lcd3.text+"&nbsp;";
}
obj=obj.led;
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


redrawSim();
 
}

connection.onclose = function(){
	document.getElementById("websocketState").innerHTML="<font color='red'><b>Not Connected</b></font>";
}



var connection5 = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-ssr');
connection5.onmessage = function(e){
obj = JSON.parse(e.data);
ssrObj=obj.ssr;
if("gpioSsrA" in ssrObj){
	gpioSsrA=ssrObj.gpioSsrA;
}
if("gpioSsrB" in ssrObj){
	gpioSsrB=ssrObj.gpioSsrB;
}

relayObj=obj.relay;
if("gpioFermCool" in relayObj){
	gpioFermCool=relayObj.gpioFermCool;
}
if("gpioFermHeat" in relayObj){
	gpioFermHeat=relayObj.gpioFermHeat;
}

redrawSim(); 
}

connection5.onclose = function(){
//	alert("Simulator session closed");
}



var connection6 = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-gov');
connection6.onmessage = function(e){
parentobj = JSON.parse(e.data);


if("_mode" in parentobj.gov){
	mode=parentobj.gov._mode;
	document.getElementById("mode").innerHTML=parentobj.gov._mode;
	document.getElementById("brewlog").innerHTML=parentobj.gov._brewlog;
	document.getElementById("recipe").innerHTML="<a href='/metroui/editRecipe.py?recipeName="+parentobj.gov._recipe+"&export=1'>"+parentobj.gov._recipe+"</a>";
}
if("laststep" in parentobj){
	document.getElementById("laststep").innerHTML=parentobj.laststep;
}

obj=parentobj.button._button;
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

redrawSim();

temphlt="&nbsp;-<BR>";
tempmashA="&nbsp;- ";
tempmashB="&nbsp;- <BR>";
tempferm="&nbsp;-<BR>";
tempboil="&nbsp;-<BR>";
obj=parentobj.temp;
if("currentResult" in obj){
	var d = new Date();

	if(mode == "boil/pump" || mode == "boil" || mode == "pump/cool" || mode =="pump" ){
 	if( probeboil in obj.currentResult){

		if(obj.currentResult[ probeboil ].timestamp + 10 > (d.getTime()/1000)){
			if(obj.currentResult[ probeboil ].valid){
				tempboil=obj.currentResult[ probeboil ].temperature;
			}
		}
	}
	}

	if(mode == "hlt" || mode == "hlt/sparge" || mode == "hlt/sparge/mash"){
 	if( probehlt in obj.currentResult){

		if(obj.currentResult[ probehlt ].timestamp + 10 > (d.getTime()/1000)){
			if(obj.currentResult[ probehlt ].valid){
				temphlt=obj.currentResult[ probehlt ].temperature;
			}
		}
	}
	}

	if(mode == "mash/dough" || mode == "hlt/sparge/mash" || mode == "mash" || lastMode == "hlt/sparge/mash"){
 	if( probemashA in obj.currentResult){

		if(obj.currentResult[ probemashA ].timestamp + 10 > (d.getTime()/1000)){
			if(obj.currentResult[ probemashA ].valid){
				tempmashA=obj.currentResult[ probemashA ].temperature;
			}
		}
	}

 	if( probemashB in obj.currentResult){

		if(obj.currentResult[ probemashB ].timestamp + 10 > (d.getTime()/1000)){
			if(obj.currentResult[ probemashB ].valid){
				tempmashB=obj.currentResult[ probemashB ].temperature;
			}
		}
	}
	}
	
	if(mode == "ferm" || mode == "ferm-wait"){
 	if( probeferm in obj.currentResult){
		if(obj.currentResult[ probeferm ].timestamp + 10 > (d.getTime()/1000)){
			if(obj.currentResult[ probeferm ].valid){
				tempferm=obj.currentResult[ probeferm ].temperature;
			}
		}
	}
	}
	
}

document.getElementById("boiltemp").innerHTML=tempboil;
document.getElementById("hlttemp").innerHTML=temphlt;
document.getElementById("mashtemp").innerHTML=tempmashA+" / "+tempmashB;
document.getElementById("fermtemp").innerHTML=tempferm;



}

connection6.onclose = function(){
//	alert("Simulator session closed");
}




function swbutton(b){
	host=window.location.href.split(":54660")[0];
	host="http://192.168.1.14";
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
	host="http://192.168.1.14";
	url=host+":54661/cgi/fakeButtonHandler.py?button="+b;
	if(localUser){
		document.getElementById("buttonTarget").src=url;
	}else{
		alert("View-only; button disabled");	
	}
}
