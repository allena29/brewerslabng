function unsafeXML(content){
         var content2 = content.replace( /{:ampersand:}/g, '&');
         var content3 = content2.replace( /{:leftbracket:}/g, '<');
         var content4 = content3.replace( /{:rightbracket:}/g, '>');
         var content5 = content4.replace( /{:forwardslash:}/g, '/');
         return content5;
}



function getXHTMLRequest(){
      if (window.XMLHttpRequest) { 
         http_request = new XMLHttpRequest();
         if (http_request.overrideMimeType) {
            http_request.overrideMimeType('text/xml');
         }  
      } else if (window.ActiveXObject) { 
         try {
            http_request = new ActiveXObject("Msxml2.XMLHTTP");
         } catch (e) {
            try {
               http_request = new ActiveXObject("Microsoft.XMLHTTP");
            } catch (e) {}
         }
      }
      
      if (!http_request) {   
         return false;
      }

      return http_request
}








function xmlPOST( postcontent, a,b) {
   d = new Date()
   xmlreq = getXHTMLRequest();
   xmlreq.onreadystatechange = a;
   xmlreq.open('POST', b+"?uniq2="+d.getTime(),true);
   xmlreq.setRequestHeader("Content-Type","text/plain");
   xmlreq.setRequestHeader("Content-length", postcontent.length);
   xmlreq.send( postcontent );


}


function xmlREQ( a,b) {
   d = new Date()
   xmlreq = getXHTMLRequest();
   xmlreq.onreadystatechange = a;
//   alert(b+"&uniq2="+d.getTime());
   xmlreq.open('GET',b+"&uniq2="+d.getTime());
   xmlreq.send(null);
}



function nullFunc(){
   var a = ""
}


function showdeadcenterdiv(Xwidth,Yheight,divid) { 
// First, determine how much the visitor has scrolled

var scrolledX, scrolledY; 
if( self.pageYOffset ) { 
scrolledX = self.pageXOffset; 
scrolledY = self.pageYOffset; 
} else if( document.documentElement && document.documentElement.scrollTop ) { 
scrolledX = document.documentElement.scrollLeft; 
scrolledY = document.documentElement.scrollTop; 
} else if( document.body ) { 
scrolledX = document.body.scrollLeft; 
scrolledY = document.body.scrollTop; 
}

// Next, determine the coordinates of the center of browser's window

var centerX, centerY; 
if( self.innerHeight ) { 
centerX = self.innerWidth; 
centerY = self.innerHeight; 
} else if( document.documentElement && document.documentElement.clientHeight ) { 
centerX = document.documentElement.clientWidth; 
centerY = document.documentElement.clientHeight; 
} else if( document.body ) { 
centerX = document.body.clientWidth; 
centerY = document.body.clientHeight; 
}

// Xwidth is the width of the div, Yheight is the height of the 
// div passed as arguments to the function: 
var leftOffset = scrolledX + (centerX - Xwidth) / 2; 
var topOffset = scrolledY + (centerY - Yheight) / 2; 
// The initial width and height of the div can be set in the 
// style sheet with display:none; divid is passed as an argument to // the function 
var o=document.getElementById(divid); 
var r=o.style; 
r.position='absolute'; 
r.top = topOffset + 'px'; 
r.left = leftOffset + 'px'; 
r.display = "block"; 
}

function reloadpage(){
window.location.reload(true);
}

function reloadAfterAjax(){

      if (http_request.readyState==4 && http_request.status==200)    {
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
        var complete= xmldoc.getElementsByTagName('complete').item(0).firstChild.data;
	reloadpage();
      }


} 
