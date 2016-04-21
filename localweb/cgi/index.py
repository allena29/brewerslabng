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

		</div>


	</div>
    </div>




<div data-role="dialog" id="poweroffDialog" style='padding: 15px'>
    <h1>Power Off</h1>
    <p>
        <b>Are you sure you want to shutdown?</b></P

    <p><span style='display: none' id='shutdownWarning' class='fgRed'>Note: please wait 5 minutes after clicking <I>SHUTDOWN</I> before removing the power.</span>    </p>

    <p align="right">
	<input id='poweroffDialogCancelButton' type='button' value='Cancel' onClick="cancelDialog('poweroffDialog')"> &nbsp; - &nbsp;
	<input type='button' value='SHUTDOWN' onClick="doShutdown()" id='poweroffDialogShutdownButton'>
    </p>
</div>
<script>
    function doShutdown(){
	$("#shutdownWarning").show();
	document.getElementById("poweroffDialogShutdownButton").disabled=true;
	document.getElementById("poweroffDialogCancelButton").disabled=true;
    }
    function cancelDialog(id){	
	$("#"+id).hide();
    }
    function showDialog(id){
        var dialog = $(id).data('dialog');
        dialog.open();
    }
</script>






</body>



</html>
"""
