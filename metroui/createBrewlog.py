#!/usr/bin/python
import re
import sys
import cgi
import time
import mysql.connector
from thememetro import *
con=mysql.connector.connect(user='root',database="brewerslab")


form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
theme.pagetitle="%s - Edit Recipe" %(form['recipeName'].value)
theme.goBackHome="brewerslab.py?recipeName=%s" %(form['recipeName'].value)
theme.bodytitle="%s" %(form['recipeName'].value)
theme.presentHead()
grid={}



theme.presentBody()
print "<div class=\"container\">"


(year,mon,mday,hour,tmin,sec,wday,yday,dst)=time.localtime()

print """
<form method=POST action='createBrewlogAction.py' target='hidden'>
<input type='hidden' name='recipeName' id='recipeName' value="%s"> 
<h2>Create New Brewlog</h2>

    <div class="input-control text" data-role="datepicker"
    data-date='%s-%02d-%02d'
    data-effect='slide'
    data-locale='en'
    data-week-start='0'
    data-other-days='0'>
    <input name='brewlog' id='brewlog' type="text">
    <button class="btn-date"></button>
    </div>
""" %(form['recipeName'].value,year,mon,mday)


print """
<h2>Process</h2>
<select id='process' name="process">"""
cursor=con.cursor()
cursor.execute("select owner,process FROM gProcesses ORDER BY process DESC")
for row in cursor:
	(owner,process)=row
	print "<option>%s</option>" %(process)	
print """
</select>

"""


print """
<h2>Stock</h2>
    <div class="panel no-border" style="width:20%">
	<div id='stock' class="panel-header bg-pink fg-white">checking</div>
    </div>

"""


print """<h3>&nbsp;</h3>
<div id='create' style='height: 0px;visibility: hidden'>
<p>Status: <span id='status'>Uncreated</span></p>
<div id='progress' class="progress-bar large"></div>
<button id='createbutton' class="command-button" onClick="doBrewlogCreate()">
<i class="icon-arrow-right-3 on-right"></i>
Create Brewlog
</button>
</div>
<div style='visibility: hidden;height:0px;width:0px'>
<iframe name="hidden"></iframe>
</div>


"""

 
#checking Stock
#Starting Brewlog
#Calculating
#


theme.presentFoot()

print """
<input type="hidden" id="outofstockmessage" value="">
<input type="hidden" name="transaction" id="transaction" value="">
</form>

<script language="Javascript">
 function checkStatus(){
      if (http_request.readyState==4 && http_request.status==200)    {
	
		var responseTxt=http_request.responseText;      
		var response=http_request.responseXML;  
		var xmldoc = response;
		var status = xmldoc.getElementsByTagName('status').item(0).firstChild.data;
		//alert(status);
		p=0;
		if(status=="complete"){
			p=100;
			//alert("complete");	
			var recipeName = xmldoc.getElementsByTagName('recipeName').item(0).firstChild.data;
			var brewlog = xmldoc.getElementsByTagName('brewlog').item(0).firstChild.data;
			//alert("complete");	
			location.replace("brewlog.py?recipeName="+recipeName+"&brewlog="+brewlog);
		}
		if(status=="compile"){
			p=66;
		}
		if(status=="calculate"){
			p=50;
		}
		if(status=="stock"){
			p=33;
		}
		if(status=="creating"){
			p=15;
		}
		if(p<100){
			recheckStatus();
		}
	
	    var pb = $("#progress").progressbar();
	    pb.progressbar('value', p);
	}
 }
 
 function recheckStatus(){
    transid=document.getElementById("transaction").value;
    //alert("ajaxGetTransactionStatus.py?transid="+transid);
    xmlREQ(checkStatus,"ajaxGetTransactionStatus.py?transid="+transid);
 }
 function doBrewlogCreate(){
	if(document.getElementById("transaction").value== ""){
		document.getElementById("createbutton").className="command-button inverse";
		d = new Date()
		document.getElementById("transaction").value=d.getTime();
                setTimeout(recheckStatus,530);		
	}
 }
 function updatePage(){
      if (http_request.readyState==4 && http_request.status==200)    {
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
        var outOfStock = xmldoc.getElementsByTagName('outofstock').item(0).firstChild.data;
	if(parseInt(outOfStock) == 0 ){
		document.getElementById('stock').className="panel-header bg-darkGreen fg-white";
		document.getElementById('stock').innerHTML="Stock Available";
		document.getElementById('create').style.height="100%";
		document.getElementById('create').style.visibility="visible";
	}else{
		document.getElementById('stock').className="panel-header bg-darkRed fg-white";
		document.getElementById('stock').innerHTML="<a href='javascript:showOutOfStock()' class='fg-white'><i class='icon-cart-2'></i> Stock Unavailable</a>";
		document.getElementById('outofstockmessage').value="Missing Stock\\n";
		for(s=0;s<parseInt(outOfStock);s++){
			document.getElementById('outofstockmessage').value=document.getElementById('outofstockmessage').value+" - "+xmldoc.getElementsByTagName('stock'+s).item(0).firstChild.data+"\\n";
		}	
	}
	}
 }
	function showOutOfStock(){
		alert( document.getElementById('outofstockmessage').value);
	}
 function checkStock(){
 	process=document.getElementById('process').value;
	brewlog=document.getElementById('brewlog').value;
	recipeName=document.getElementById('recipeName').value;
	document.getElementById('stock').className="panel-header bg-pink fg-white";
	document.getElementById('stock').innerHTML="checking";
//	alert("checking "+process+brewlog); 
        xmlREQ(updatePage,"ajaxStockPreCheck.py?recipeName="+recipeName+"&brewlog="+brewlog+"&process="+process);

 }
 checkStock();
</script>
"""
