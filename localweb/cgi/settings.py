#!/usr/bin/python
import time

print """
<!DOCTYPE html>
<html>
<head>
    <script src="../js/jquery-1.12.0.min.js"></script>
    <link href="../css/metro.css" rel="stylesheet">
    <script src="../js/metro.min.js"></script>
    <script src="../js/wwwajax.js"></script>
    <link href="../css/metro-icons.css" rel="stylesheet">

<body>
    <div class="page-content">

	<div class="container">
  

		    <div class="tile-container">

                <a href="javascript:showDialog('#wifiDialog')" class="tile bg-crimson fg-white" data-role="tile">
                    <div class="tile-content iconic">
                        <span class="icon mif-wifi-mid"></span>
                    </div>
                    <span class="tile-label">Configure Wireless</span>
                </a>


                <a href="javascript:showDialog('#timeDialog')" class="tile bg-crimson fg-white" data-role="tile">
                    <div class="tile-content iconic">
                        <span class="icon mif-calendar"></span>
                    </div>
                    <span class="tile-label">Configure Time/Date</span>
                </a>


                <a href="probes.py" class="tile bg-crimson fg-white" data-role="tile">
                    <div class="tile-content iconic">
                        <span class="icon mif-magic-wand"></span>
                    </div>
                    <span class="tile-label">Configure Probes</span>
                </a>




		</div>



	</div>
    </div>




<div data-role="dialog" id="timeDialog" style='padding: 15px'>
    <h1>Time/Date</h1>
    <p>


"""
(year,month,day,hour,minut,sec,wday,yday,idst)=time.localtime()
print """

	<table border=0>
		<tr>
		<td>Server Date:</td>
		<td>%s.%s.%s %s:%s
		</td>
		</tr>
""" %(year,month,day,hour,minut)

print """
		<tr>
		<td>Date:</td>
		<td>
<div class="input-control text" data-role="datepicker">
    <input type="text" id='newdate'>
    <button class="button"><span class="mif-calendar"></span></button>
</div>
		</td>
		</tr>
		<tr>
		<td>Time:</td>
		<td>

	<select id=hour>
"""
for c in range(24):
	print "<option>%02d" %(c)
print """</select>:<select id=minute>
"""
for c in range(60):
	print "<option>%02d" %(c)
print """</select>

<script languge=Javascript>
var d = new Date();
var n = d.getHours();
if(d.getHours() < 10){
	$("#hour").val("0"+ d.getHours() );
}else{
	$("#hour").val( d.getHours() );
}
if(d.getMinutes() < 10){
	$("#minute").val("0"+ d.getMinutes() );
}else{
	$("#minute").val( d.getMinutes() );

}
$("#newdate").val( d.getFullYear()+"."+(parseInt(d.getMonth())+1)+"."+d.getDate() );


</script>
		</td>
		</tr>
		<tr>
		<td>Admin Password: </td>
		<td><!-- Input with reveal helper -->
			<div class="input-control password" data-role="input">
			    <input type="password" id='password2' value="">
			    <button class="button helper-button reveal"><span class="mif-looks"></span></button>
			</div></td>
		</tr>
	</table>

    <p align="right">
	<input type='button' value='Cancel' onClick="cancelDialog('timeDialog')"> &nbsp; - &nbsp;
	<input type='button' value='Update' onClick="changeTimeDate()" id='changeTimeButton'>
    </p>
</div>


<div data-role="dialog" id="wifiDialog" style='padding: 15px'>
    <h1>WIFI Settings</h1>
    <p>

        <b>Enter your password to configure wireless</b></P>
	<table border=0>
		<tr>
		<td>Admin Password: </td>
		<td><!-- Input with reveal helper -->
			<div class="input-control password" data-role="input">
			    <input type="password" id='password3' value="">
			    <button class="button helper-button reveal"><span class="mif-looks"></span></button>
			</div></td>
		</tr>
		<tr>
		<td>SSID/WPA PSK:</td>
		<td><div class="input-control" data-role="input"><input type="text" id='ssid' size=10 value=""></div>
		<div class="input-control password" data-role="input">
		    <input type="password" id='wep' value="">
		    <button class="button helper-button reveal"><span class="mif-looks"></span></button>
		</div><br><i>Only WPA secured wireless access points supported</i></td>
		</tr>
		
	</table>

    <p align="right">
	<input id='wifiCancelButton' type='button' value='Cancel' onClick="cancelDialog('wifiDialog')"> &nbsp; - &nbsp;
	<input type='button' value='Update' onClick="warnWifiChange()" id='wifiUpdateButton'>
    </p>
</div>

<div data-role="dialog" id="wifiDialog2" style='padding: 15px'>
    <h1>WIFI Settings</h1>
    <p>

	<b>Status</b>
	<P>
	<span id='wififlapwarning'><i>Note:</i> the wireless SSID 'aaaBREWERSLAB' will disappear while we test connectiivty to <span id='wifissid'></span>.<br>
Once the test has finished 'aaaBREWERSLAB' will re-appear - please wait 5 minutes before trying to reconnect.<br></span><BR>
<B>	<span id='wifireconfigstatus'></span></B>
	<p>	
	<input type=hidden id='replacementIp' value=''>
	<input id='wifiCancelButton' type='button' value='Cancel' onClick="cancelWifiChange()"> &nbsp; - &nbsp;
	<input type='button' value='Keep Wireless Details' onClick="keepWifiChange()" id='wifiKeepButton'>
	
    </p>
</div>

<script language="Javascript">
    function cancelDialog(id){	
	$("#"+id).hide();
    }
    function showDialog(id){
	document.getElementById('changeTimeButton').disabled=false;


        var dialog = $(id).data('dialog');
        dialog.open();
	$(""+id).show();
    }


	function changeTimeDate(){
		document.getElementById('changeTimeButton').disabled=true;
//	    alert( "dotimereconfig.py?date="+$("#newdate").val()+"&hour="+$("#hour").val()+"&minutes="+$("#minute").val()+"&adminpass="+$("#password2").val() );


	$.ajax({
	    url: "dotimereconfig.py?date="+$("#newdate").val()+"&hour="+$("#hour").val()+"&minutes="+$("#minute").val()+"&adminpass="+$("#password2").val(),
	    error: function(){
		alert("Unable to change time/date");
	    },
	    success: function(xml){
		alert("Done");
		document.getElementById('changeTimeButton').disabled=false;
		cancelDialog('timeDialog');

	    },
	    timeout: 5000 // sets timeout to 3 seconds
	});
	}


//  showDialog("#wifiDialog2");
	function warnWifiChange(){
		document.getElementById("wifiKeepButton").disabled=true;
		alert("This process may take 5 minutes - please be patient");
		doWifiChange(true);

	}	
    function doWifiChange(startConfig){
	$("#wifissid").html( $("#ssid").val());

	cancelDialog('wifiDialog');
	showDialog('#wifiDialog2');

	$("#wifireconfigstatus").html("Please wait up to 5 minutes for the wifi to be tested");
	$.ajax({
	    url: "dowifireconfig.py?startReconfig="+startConfig+"&wep="+$("#wep").val()+"&ssid="+$("#ssid").val()+"&adminpass="+$("#password3").val(),
	    error: function(){
		$("#wifireconfigstatus").html("Reconfigurartion in progress... will recheck in 15 seconds for update ");
		setTimeout(doWifiChange,15000);
		// will fire when timeout is reached
	    },
	    success: function(xml){
		$("#wifireconfigstatus").html("Done");
		//do something
		if( $(xml).find('status').text() == "1"){
			setTimeout(doWifiChange,15000);
		}
		if( $(xml).find('status').text() == "0"){
			document.getElementById("wifiKeepButton").disabled=false;
			$("#wifireconfigstatus").html( "WIFI Connection OK - IP Address "+$(xml).find('ip').text() );
			$("#replacementIp").val( $(xml).find('ip').text() );
			$("#wififlapwarning").hide();		
		}
		$("#wifireconfigstatus").html( $(xml).find('msg').text() );

	    },
	    timeout: 3000 // sets timeout to 3 seconds
	});
    }
  	
	function keepWifiChange(){
		$.ajax({
		    url: "dowifireconfig.py?keepDetails=true&wep="+$("#wep").val()+"&ssid="+$("#ssid").val()+"&adminpass="+$("#password3").val(),
		    error: function(){
			alert("Error saving details");
		    },
		    success: function(xml){
			location.replace("bouncer.py?ip="+$("#replacementIp").val() +"&ssid="+$("#ssid").val());
		    },
		    timeout: 30000 // sets timeout to 3 seconds
		});
	}
	function cancelWifiChange(){
		$.ajax({
		    url: "poweroff.py?reboot=true&adminpass="+$("#password3").val(),
		    error: function(){
			alert("Error rebooting");
		    },
		    success: function(xml){
			location.replace("index.py")
		    },
		    timeout: 30000 // sets timeout to 3 seconds
		});
				

	}


   // debug only
//	doWifiChange(true);
</script>


<div data-role="dialog" id="poweroffDialog" style='padding: 15px'>
    <h1>Power Off</h1>
    <p>

        <b>Are you sure you want to shutdown?</b></P>

	Password: <!-- Input with reveal helper -->
<div class="input-control password" data-role="input">
    <input type="password" id='password'>
    <button class="button helper-button reveal"><span class="mif-looks"></span></button>
</div>

    <p><span style='display: none' id='shutdownWarning' class='fgRed'>Note: please wait 5 minutes after clicking <I>SHUTDOWN</I> before removing the power.</span>    </p>

    <p align="right">
	<input id='poweroffDialogCancelButton' type='button' value='Cancel' onClick="cancelDialog('poweroffDialog')"> &nbsp; - &nbsp;
	<input type='button' value='SHUTDOWN' onClick="doShutdown()" id='poweroffDialogShutdownButton'>
    </p>
</div>
<script>
    function doShutdown(){
	if($("#password").val() == ""){
		alert("Password not provided - cannot shutdown");
	}else{
		$("#shutdownWarning").show();
		document.getElementById("poweroffDialogShutdownButton").disabled=true;
		document.getElementById("poweroffDialogCancelButton").disabled=true;
	}
    }
</script>





<footer class='app-bar fixed-bottom drop-up'>brewerslab - <a href="https://github.com/allena29/brewerslab/"><span class='fg-white'> &nbsp; <span class="mif-github"></span> &nbsp;github.com/allena29/brewerslab</span></a></footer>

</body>


<script>
</script>
</html>
"""
