#!/usr/bin/python
import re
import json
import sys
import time
import cgi
import _mysql
import mysql.connector
from thememetro import *
from cloudNG import *
con=mysql.connector.connect(user='brewerslab',password='beer',database="brewerslab")
showTemps=""


form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
theme.pagetitle="Brewday %s - %s" %(form['brewlog'].value,form['recipeName'].value) 
theme.goBackHome="index.py"
theme.bodytitle="%s (%s)" %(form['brewlog'].value,form['recipeName'].value)


theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")

theme.presentBody()
print "<div class=\"container\">"


process=None
cursor=con.cursor()
cursor.execute("select process,brewlog FROM gBrewlogs WHERE brewlog = '%s' LIMIT 0,1" %(form['brewlog'].value))
for (processx,brewlogx) in cursor:
	process=processx
if not process:
	theme.error(errText="Unfortunately an error occured as we could not find the process for this brewlog")
	
	


if not form.has_key("activityNum"):
	


	cursor=con.cursor()
	cursor.execute("select activityNum,stepName from gProcess WHERE process='%s' and stepNum=-1 and activityNum > -1 ORDER BY activityNum;" %(process))
	for (activityNum,stepName) in cursor:
		grid[ activityNum ] = {'url2' : 'brewlog.py?recipeName=%s&brewlog=%s&activityNum=%s' %(form['recipeName'].value,form['brewlog'].value, activityNum),'text': "%s" %(stepName)}

	cursor.close()
	theme.doGrid(grid)	
	print "</div>"
	theme.presentFoot()
	sys.exit(0)


activity=0
activitySteps=json.loads(brewerslabCloudApi().listActivitySteps("test@example.com",process,form['activityNum'].value,form['brewlog'].value)['json'])['result']

#<iframe src="iframeTimerTemp.py" frameBorder=0 width=100% height=170px scrolling=no></iframe>
visible="hidden"
if os.path.exists("/currentdata/temp-mcast-rx-on"):
	if len(os.listdir("/currentdata/temps")) > 0:
		showTemps="visible"

##################################################################
print """


            <div class="grid fluid">



                <div class="row">
                    <div class="span2">
                        <div id='doGravity' class="panel"  onClick="showToolsGravity()">
                            <div class="panel-header bg-darkRed fg-white">
                                Gravity
                            </div>
                        </div>
                    </div>


                    <div class="span2">
                        <div id='doTemps' style="visibility: %s" class="panel"  onClick="showToolsTemps()">
                            <div class="panel-header bg-orange fg-black">
                                 Temps
                            </div>
                        </div>
                    </div>

		</div>
    </div>
""" %(showTemps)


print """
<script language="Javascript">
function showToolsGravity(){
	document.getElementById('toolsGravity').style.visibility="visible";
	document.getElementById('toolsGravity').style.height="90px";
}
function showToolsTemps(){
	document.getElementById('toolsTemp').style.visibility="visible";
	document.getElementById('toolsTemp').style.height="90px";
}
</script>
""" 



print """
<div id='toolsGravity' style='visibility: hidden; height:0px'>
<iframe src="iframeTools.py" frameBorder=0 width=100% height=90px scrolling=no></iframe></div>
"""

print """
<div id='toolsTemp' style='visibility: hidden; height:0px'>
<iframe src="iframeTemp.py" frameBorder=0 width=100% height=90px scrolling=no></iframe></div>
"""


print """
<div class="listview-outlook2" data-role="listview">
"""

for stepDetails in activitySteps:

	completeOrNot='<span id="star%s" class="icon-star fg-red"></span>' %(stepDetails['stepNum'])
	if stepDetails['complete']:
		completeOrNot='<span id="star%s" class="icon-star-3 fg-green"></span>' %(stepDetails['stepNum'])
	print """
	<div class="list-group collapsed" id='group%s'>
		<a href="#" onClick="javascript:stepDetails('%s')" class="group-title">%s %s</a>
	""" %(stepDetails['stepNum'],stepDetails['stepNum'],completeOrNot,stepDetails['name'])
	print """
		<div class="group-content" id='groupcontent%s'>
		<a class="list">
		<div class="list-content" id='listitem%s'>...</div>
		</a>
		</div>
	</div>
	""" %(stepDetails['stepNum'],stepDetails['stepNum'])


print "</div>" ### list-view outlook


print "</div>"
theme.presentFoot()

print """
<script language="Javascript">
 function fieldUpdated(){
      if (http_request.readyState==4 && http_request.status==200)    {
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
        var stepNum= parseInt(xmldoc.getElementsByTagName('stepNum').item(0).firstChild.data);
        var fieldKey=xmldoc.getElementsByTagName('fieldKey').item(0).firstChild.data;
        var fieldVal=xmldoc.getElementsByTagName('val').item(0).firstChild.data;
        var fieldNum= parseInt(xmldoc.getElementsByTagName('fieldNum').item(0).firstChild.data);

	document.getElementById("widget_"+stepNum+"_"+fieldNum).value=fieldVal;
      }

 }
 function commentsSaved(){
      if (http_request.readyState==4 && http_request.status==200)    {
	alert("comments saved");
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
        var status= xmldoc.getElementsByTagName('status').item(0).firstChild.data;
      }

 }
 function saveComments(i){
	xmlPOST( "%s,%s,"+i+",\\n"+document.getElementById("comments_"+i).value , commentsSaved, "ajaxSubmitComments.py");
 }
""" %(form['brewlog'].value,form['activityNum'].value)

print """
function saveField(i,j,k){
	v=document.getElementById("widget_"+i+"_"+j).value;
	xmlPOST( "%s,%s,"+i+","+k+","+j+",%s,\\n"+ v , fieldUpdated, "ajaxSubmitField.py");
}
""" %(form['brewlog'].value,form['activityNum'].value,process)
print """
 function refreshStatus(){
      if (http_request.readyState==4 && http_request.status==200)    {
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
        var status= xmldoc.getElementsByTagName('status').item(0).firstChild.data;
	stepDetails(status);
        if(xmldoc.getElementsByTagName('complete').item(0).firstChild.data == "True" ){
		stepDetails( parseInt(status)+1);
	}
	
      }
 } 
 function toggleComplete(a,y,z){
	if(y==-1){
        	xmlREQ(refreshStatus,"ajaxSetStepComplete.py?brewlog=%s&activityNum=%s&stepNum="+a+"&complete="+z);
	}else{
        	xmlREQ(refreshStatus,"ajaxSetStepComplete.py?brewlog=%s&activityNum=%s&stepNum="+a+"&complete="+z+"&subStepNum="+y);
	}
 }
""" %(form['brewlog'].value,form['activityNum'].value,form['brewlog'].value,form['activityNum'].value)
print """
 function stepDetail(){
      if (http_request.readyState==4 && http_request.status==200)    {
        var responseTxt=http_request.responseText;      
        var response=http_request.responseXML;  
        var xmldoc = response;
        var stepNum = xmldoc.getElementsByTagName('stepNum').item(0).firstChild.data;
	document.getElementById('group'+stepNum).className="list-group";
	document.getElementById('groupcontent'+stepNum).style.display="block";

	var replacement="";
	replacement=replacement+"   <div class='tab-control' data-role='tab-control'>";
	replacement=replacement+"    <ul class='tabs'>";
	replacement=replacement+"    <li class='active'><a href='#_page_"+stepNum+"'>Step</a></li>";
        if(xmldoc.getElementsByTagName('img').item(0).firstChild.data == "-"){
	}else{
	replacement=replacement+"    <li><a href='#_img_"+stepNum+"'>Image</a></li>";
	}
        if(parseInt(xmldoc.getElementsByTagName('fields').item(0).firstChild.data) >0){
	replacement=replacement+"    <li><a href='#_fields_"+stepNum+"'>Records</a></li>";
	}
	replacement=replacement+"    <li><a href='#_comments_"+stepNum+"'>Comments</a></li>";
	replacement=replacement+"    </ul>";
    	replacement=replacement+"    <div class='frames'>";
	replacement=replacement+"     <div class='frame' id='_page_"+stepNum+"'>"; 

        replacement=replacement+"<p>" + unsafeXML(xmldoc.getElementsByTagName('description').item(0).firstChild.data ) +"</p>";
	
        if(xmldoc.getElementsByTagName('warning').item(0).firstChild.data == "-"){
	}else{
		replacement=replacement+"<p align=right><b>Attention: </b> "+xmldoc.getElementsByTagName('warning').item(0).firstChild.data+"</p>";
	}

        if(xmldoc.getElementsByTagName('completeDate').item(0).firstChild.data == "-"){
	}else{
		replacement=replacement+"<p align=right><b>Completed: </b> "+xmldoc.getElementsByTagName('completeDate').item(0).firstChild.data+"</p>";
	}
        if(xmldoc.getElementsByTagName('substocomplete').item(0).firstChild.data == "False"){
        	if(xmldoc.getElementsByTagName('complete').item(0).firstChild.data == "False"){
			replacement=replacement+"<p align=right><input type='button' value='Complete' onClick=toggleComplete('"+stepNum+"',-1,1) </p>";
			document.getElementById('star'+stepNum).className="icon-star fg-red";
		}else{
			replacement=replacement+"<p align=right><input type='button' value='Un Complete' onClick=toggleComplete('"+stepNum+"',-1,0) </p>";
			document.getElementById('star'+stepNum).className="icon-star-3 fg-green";
		}
	}
	

	
        if(xmldoc.getElementsByTagName('substocomplete').item(0).firstChild.data == "True"){
        	for(c=0;c<parseInt( xmldoc.getElementsByTagName('substeps').item(0).firstChild.data);c++){
			replacement=replacement+"<div class='group-content'><a class='list'><div class='list-content'>";
			replacement=replacement+"<p>" + unsafeXML(xmldoc.getElementsByTagName('subText'+c).item(0).firstChild.data ) +"</p>";
			replacement=replacement+"</div></a></div>";
			if(xmldoc.getElementsByTagName('subComplete'+c).item(0).firstChild.data == "False"){
				replacement=replacement+"<p align=right><input type='button' value='Complete' onClick=toggleComplete('"+stepNum+"',"+c+",1) </p>";
			}else{
				replacement=replacement+"<p align=right><input type='button' value='Un Complete' onClick=toggleComplete('"+stepNum+"',"+c+",0) </p>";
			}
		}
	}

	replacement=replacement+"</div>";		//closes the tab

		
	// Optional Image Page
        if(xmldoc.getElementsByTagName('img').item(0).firstChild.data == "-"){
	}else{
		replacement=replacement+"     <div class='frame' id='_img_"+stepNum+"'>"; 
		replacement=replacement+"<p align=center><img src=http://mycrap.mellon-collie.net/brewerspad/brewerspad/processimgs/%s/"+xmldoc.getElementsByTagName('img').item(0).firstChild.data+"></p>";
		replacement=replacement+"</div>";		//closes the tab
	}



	// Fields
        if(parseInt(xmldoc.getElementsByTagName('fields').item(0).firstChild.data) >0){
		replacement=replacement+"     <div class='frame' id='_fields_"+stepNum+"'>"; 
		fields=parseInt(xmldoc.getElementsByTagName('fields').item(0).firstChild.data);

		replacement=replacement+"<table class='table'><thead><tr><th class='text-left'>Field</th><th class='text-left'>Value</th><th class='text-left'>&nbsp;</th></tr></thead><tbody>";
		for(f=0;f<fields;f++){
			fieldKey=unsafeXML(xmldoc.getElementsByTagName('fieldKey'+f).item(0).firstChild.data);
			fieldLabel=unsafeXML(xmldoc.getElementsByTagName('fieldLabel'+f).item(0).firstChild.data);
			fieldValue=unsafeXML(xmldoc.getElementsByTagName('fieldVal'+f).item(0).firstChild.data);
			fieldWidget=unsafeXML(xmldoc.getElementsByTagName('fieldWidget'+f).item(0).firstChild.data);
			if(fieldValue=="-"){
			fieldValue="";
			}		
				
			replacement=replacement+"<tr><td>"+fieldLabel+"</td>";

			if(fieldWidget=="-"){
				replacement=replacement+"<td><input type='text' id='widget_"+stepNum+"_"+f+"' value='"+fieldValue+"'></td><td>";
				replacement=replacement+"<input type='button' value='Save' onClick='saveField("+stepNum+","+f+",\\""+fieldKey+"\\")'>";
			}else{
				replacement=replacement+"<td><input disabled type='text' id='widget_"+stepNum+"_"+f+"' value='"+fieldValue+"'></td><td>";
				replacement=replacement+"<input type='button' value='Update' onClick='saveField("+stepNum+","+f+",\\""+fieldKey+"\\")'>";
			}	
			reaplcement=replacement+"</td></tr>";

		}
		replacement=replacement+"</tbody><tfoot></tfoot></table>";
		replacement=replacement+"</div>";		//closes the tab
	}


	// Comments
	replacement=replacement+"     <div class='frame' id='_comments_"+stepNum+"'>"; 
	replacement=replacement+"	<textarea rows=3 cols=100 id='comments_"+stepNum+"'>";
	if(xmldoc.getElementsByTagName('comments').item(0).firstChild.data == "-"){
	}else{
		comment=unsafeXML(xmldoc.getElementsByTagName('comments').item(0).firstChild.data).split("</br>");
		for(cc=0;cc<comment.length;cc++){
			replacement=replacement+comment[cc]+"\\n";
		}
	}
	replacement=replacement+"</textarea>";
	replacement=replacement+"<p align=right><input type=button value=Update onClick='saveComments("+stepNum+")'></p>";
	replacement=replacement+"</div>";		//closes the tab



	replacement=replacement+"</div>";	//closes the fames	
	replacement=replacement+"</div>";	// closes the tab control

	document.getElementById('listitem'+stepNum).innerHTML=replacement;

//	window.location.replace="?recipeName=%s&brewlog=%s&activityNum=%s#anchor"+stepNum;
     }
 }
""" %(process, form['recipeName'].value,form['brewlog'].value,form['activityNum'].value)

print """
function stepDetails(i){
        xmlREQ(stepDetail,"ajaxStepDetail.py?recipeName=%s&brewlog=%s&process=%s&activityNum=%s&stepNum="+i+"&sortindex="+i);
}
""" %( form['recipeName'].value, form['brewlog'].value, process, form['activityNum'].value)

#<xml><title>Gather Grain</title><description>Gather the and measure the grain required for the brewday</description><img>-</img><subNeedToComplete0>True</subNeedToComplete0><subComplete0>False</subComplete0><subText0>Add 1 teaspoon of gypsum -OR- 2 teaspoons of burton water salts to the grain.</subText0><subNeedToComplete1>True</subNeedToComplete1><subComplete1>False</subComplete1><subText1> 321.50 gm of Honey (BRI000366)</subText1><subNeedToComplete2>True</subNeedToComplete2><subComplete2>False</subComplete2><subText2> 4781.00 gm of Maris Otter (BRI000368)</subText2><subNeedToComplete3>True</subNeedToComplete3><subComplete3>False</subComplete3><subText3> 389.69 gm of Torrified Wheat (BRI000185)</subText3><subNeedToComplete4>True</subNeedToComplete4><subComplete4>False</subComplete4><subText4> 730.67 gm of CaraGold (BRI000175)</subText4><substeps>5</substeps><complete>False</complete><sortindex>4</sortindex><comments/><commentTimestamp/></xml



lowestIncomplete=0
cursor=con.cursor()
cursor.execute("select stepName,stepNum FROM gBrewlogStep WHERE brewlog='%s' AND activityNum=%s AND (subStepsCompleted = 0 AND completed = 0) AND stepNum > -1 AND  subStepNum = -1 ORDER BY stepNum,sortindex LIMIT 0,1" %(form['brewlog'].value,form['activityNum'].value))
for row in cursor:
	(x,lowestIncomplete)=row


print """
stepDetails('%s');
</script>""" %(lowestIncomplete)

