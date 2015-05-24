
if ('WebSocket' in window){
   /* WebSocket is supported. You can proceed with your code*/
} else {
	alert("Realtime view not available- web browser does not support websockets");
}


var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator');
ls
