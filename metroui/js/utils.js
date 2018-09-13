 function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}


function getWindowHeight(){
//alert("screen.avilaHeight:"+screen.availHeight+"\ndocument.body.clientHeight:"+document.body.clientHeight);
//	 document.getElementById("wrapper").style.height=screen.availHeight-60;
//	return screen.availHeight-60;
	h=document.body.clientHeight;
	document.getElementById("wrapper").style.height=h;
	return h;
}

function getWindowWidth(){
	 document.getElementById("wrapper").style.width=screen.availWidth-60;
//	return screen.availWidth-60;
	w=document.body.clientWidth-40;
	document.getElementById("wrapper").style.width=w;
	return w;

}

