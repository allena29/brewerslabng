#!/usr/bin/python

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
  

		    <div class="tile-container">

                <a href="javascript:showDialog('#poweroffDialog')" class="tile bg-crimson fg-white" data-role="tile">
                    <div class="tile-content iconic">
                        <span class="icon mif-settings-power"></span>
                    </div>
                    <span class="tile-label">Power Off</span>
                </a>




                <a href="javascript:showDialog('#timeDialog')" class="tile bg-crimson fg-white" data-role="tile">
                    <div class="tile-content iconic">
                        <span class="icon mif-hour-glass"></span>
                    </div>
                    <span class="tile-label">Set Time/Date</span>
                </a>

		</div>


		    <div class="tile-container">

                <a href="temps.py" class="tile bg-teal fg-white" data-role="tile">
                    <div class="tile-content iconic">
                        <span class="icon mif-meter"></span>
                    </div>
                    <span class="tile-label">Readings</span>
                </a>

		</div>


	</div>
    </div>




<div data-role="dialog" id="timeDialog" style='padding: 15px'>
    <h1>Time/Date</h1>
    <p>

        <b>Enter your password and the new time/date</b></P>

	Password: <!-- Input with reveal helper -->
		<div class="input-control password" data-role="input">
		    <input type="password" id='password2'>
		    <button class="button helper-button reveal"><span class="mif-looks"></span></button>
		</div>


    <p align="right">
	<input id='timeCancelButton' type='button' value='Cancel' onClick="cancelDialog('poweroffDialog')"> &nbsp; - &nbsp;
	<input type='button' value='Update' onClick="doShutdown()" id='timeUpdateButton'>
    </p>
</div>

<script language="Javascript">
showDialog("#timeDialog");
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
    function cancelDialog(id){	
	$("#"+id).hide();
    }
    function showDialog(id){
        var dialog = $(id).data('dialog');
        dialog.open();
    }
</script>





<footer class='app-bar fixed-bottom drop-up'>brewerslab - <a href="https://github.com/allena29/brewerslab/"><span class='fg-white'> &nbsp; <span class="mif-github"></span> &nbsp;github.com/allena29/brewerslab</span></a></footer>

</body>



</html>
"""
