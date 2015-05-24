
if ('WebSocket' in window){
   /* WebSocket is supported. You can proceed with your code*/
} else {
	alert("Realtime view not available- web browser does not support websockets");
}


//var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator');
var connection = new WebSocket('ws://brewerslab.mellon-collie.net:54662/simulator-lcd');
connection.onmessage = function(e){
console.log(e.data);
obj = JSON.parse(e.data);
if(obj.line > -1 ){
	document.getElementById('lcd'+obj.line).innerHTML=obj.text+"&nbsp;";
}

 
}

connection.onclose = function(){
	alert("Simulator session closed");
}



