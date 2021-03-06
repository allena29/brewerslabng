#!/usr/bin/python
import os
import re
import sys
import cgi
import _mysql
from thememetro import *
from pitmCfg import *

form=cgi.FieldStorage()
theme=webTheme()
theme.bgcolor="#ffffff"
sys.stdout.write("Content-Type:text/html\n\n")
theme.pagetitle="Realtime View"
theme.goBackHome="index.py"
theme.bodytitle=""
theme.presentHead()
grid={}

db=_mysql.connect(host="localhost",user="brewerslab",passwd='beer',db="brewerslab")

export=False
if form.has_key("export"):	export=True

theme.presentBody()


landscape=True
width=1
height=0
try:
	for cook in (os.environ['HTTP_COOKIE']).split(";"):
		cookie=cook.split("=")
		if cookie[0].count("clientWidth"):
			width=int(cookie[1])
		if cookie[0].count("clientHeight"):
			height=int(cookie[1])
	if width<height:
		landscape=False	
except:
	pass



print """
<script language=Javascript>
createCookie("clientWidth",window.screen.availWidth);
createCookie("clientHeight",window.screen.availHeight);

function reloadAdjust(){
document.getElementById("iframeAdjust").src='adjust.py';
}
 
</script>
"""

print "<div class=\"container\">"



print """


            <div class="grid fluid">

"""


print """

"""



#
# simulator page
#
#

if landscape:
	print """<div class="row">"""
	print """	<div class='span3'>"""


if not landscape:
	print """<div class="row">"""
	print """	<div class='span12'>"""

	print """
	<div class='tab-control' data-role='tab-control'>
		<ul class='tabs'>


		<li><a href="#framePanel">Panel</a></li>
		<li><a href="#frameSimulator">Simulator</a></li>
		<li><a href="#frameLog">Log</a></li>
		"""
	if theme.localUser:		
		print """	<li><a href="#frameAdjust" onClick='reloadAdjust()'>Adjustments</a></li>"""
	print """<li id='graphTab' style="visibility:hidden"><a href="#frameGraph">Graph</a></li>"""
	print """
	</ul>

	
	<div class='frames'>

		<div class='frame' id='framePanel'>
	"""



print "<!-- realtimeview -->"
print "<span id='websocketState'>Not Connected</span>"
print "	<!-- buttons --> "
print "	<table border=0 cellspacing=0 cellpadding=0 width=100%%>"
print "	<tr>"
print "	<td align=right><a href=javascript:button('pLeft')><img src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print " <td width=10>&nbsp;</td>"
print "	<td align=right><a href=javascript:button('pDown')><img src='/metroui/realtimeview/rotaryleft.png' width=25 height=54 border=0></a></td>"
print "	<td align=center><a href=javascript:button('pOk')><img src='/metroui/realtimeview/rotaryok.png' width=55 height=154 border=0></a></td>"
print "	<td align=left><a href=javascript:button('pUp')><img src='/metroui/realtimeview/rotaryright.png' width=25 height=54 border=0></a></td>"
print " <td width=10>&nbsp;</td>"
print "	<td align=left><a href=javascript:button('pRight')><img src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print " <td width=40>&nbsp;</td>"
print "	</tr>"
print "	</table>"

print "	<!-- lcd display -->"
print "	<table border=0 cellspacing=0 cellpadding=0 width=100%%>"
print "	<tr>"
print "	<td class='bg-darkBlue fg-white'><font face='courier'><span id='lcd0'>....</span></font></td>"
print "	</tr>"
print "	<tr>"
print "	<td class='bg-darkBlue fg-white'><font face='courier'><span id='lcd1'>....</span></font></td>"
print "	</tr>"
print "	<tr>"
print "	<td class='bg-darkBlue fg-white'><font face='courier'><span id='lcd2'>....</span></font></td>"
print "	</tr>"
print "	<tr>"
print "	<td class='bg-darkBlue fg-white'><font face='courier'><span id='lcd3'>....</spna></font></td>"
print "	</tr>"
print "	</table>"

print "<p>&nbsp;</p>"
print "	<!-- buttons -->"
print """
<input type='hidden' id='state_swHlt' value='0'>
<input type='hidden' id='state_swSparge' value='0'>
<input type='hidden' id='state_swBoil' value='0'>
<input type='hidden' id='state_swMash' value='0'>
<input type='hidden' id='state_swFerm' value='0'>
<input type='hidden' id='state_swPump' value='0'>


"""
print "	<table border=0 cellspacing=0 cellpadding=0 width=100%%>"
print "	<tr>"
print "	<td width=50 valign='center' align='center'><img id='ledSys' src='/metroui/realtimeview/ledoff.png' width=25 height=25></td>"
print "	<td align=left>&nbsp;</td>"
print "	<td><font size=2>System</font></td>"
print "	</tr>"
print "	<tr>"
print "	<td width=50 valign='center' align='center'><img id='ledHlt' src='/metroui/realtimeview/ledoff.png' width=25 height=25></td>"
print "	<td align=left><a href=javascript:swbutton('swHlt')><img id='swHlt'src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print "	<td><font size=2>HLT</font></td>"
print "	</tr>"
print "	<tr>"
print "	<td width=50 valign='center' align='center'><img id='ledSparge' src='/metroui/realtimeview/ledoff.png' width=25 height=25></td>"
print "	<td align=left><a href=javascript:swbutton('swSparge')><img id='swSparge'src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print "	<td><font size=2>Sparge</font></td>"
print "	</tr>"
print "	<tr>"
print "	<td width=50 valign='center' align='center'><img id='ledBoil' src='/metroui/realtimeview/ledoff.png' width=25 height=25></td>"
print "	<td align=left><a href=javascript:swbutton('swBoil')><img id='swBoil'src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print "	<td><font size=2>Boil</font></td>"
print "	</tr>"
print "	<tr>"
print "	<td width=50 valign='center' align='center'><img id='ledMash' src='/metroui/realtimeview/ledoff.png' width=25 height=25></td>"
print "	<td align=left><a href=javascript:swbutton('swMash')><img id='swMash'src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print "	<td><font size=2>Mash</font></td>"
print "	</tr>"
print "	<tr>"
print "	<td width=50 valign='center' align='center'><img id='ledFerm' src='/metroui/realtimeview/ledoff.png' width=25 height=25></td>"
print "	<td align=left><a href=javascript:swbutton('swFerm')><img id='swFerm'src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print "	<td><font size=2>Fermentation</font></td>"
print "	<tr>"
print "	<td>&nbsp;</td>"
print "	<td align=left><a href=javascript:swbutton('swPump')><img id='swPump'src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print "	<td><font size=2>Pump</font></td>"
print "	</tr>"
print "	</table>"

if landscape:

	print "		</div>"
	print """	<div class="span9">"""
else:

	print "</div>"

		

if  landscape:
	print """
	<div class='tab-control' data-role='tab-control'>
		<ul class='tabs'>



		<li><a href="#frameSimulator">Simulator</a></li>
		<li><a href="#frameLog">Log</a></li>
		"""
	if theme.localUser:		
		print """	<li><a href="#frameAdjust" onClick='reloadAdjust()'>Adjustments</a></li>"""
	print """<li id='graphTab' style="visibility:hidden"><a href="#frameGraph">Graph</a></li>"""
	print """

	</ul>

	
	<div class='frames'>

	"""


print """
		<div class='frame' id='frameSimulator'>
"""


print "	<!-- simulator --> "
print "	<table border=0 cellspacing=0 cellpadding=0 width=447>"

print "	<tr>"
print "	<td><img src='/metroui/realtimeview/simhltempty.png' width=90 height=126 id='hlt'></td>"
print "	<td><img src='/metroui/realtimeview/simpowerin.png' width=91 height=126></td>"
print "	<td><img src='/metroui/realtimeview/simrelays.png' width=130 height=126 id='relays'></td>"
print "	<td><img src='/metroui/realtimeview/simpowersocket.png' width=136 height=126 id='socket'></td>"
print "	</tr>"
print "	<tr>"
print "	<td><img src='/metroui/realtimeview/simhltstand.png' width=90 height=300 id=''></td>"
print "	<td><img src='/metroui/realtimeview/simmash.png' width=91 height=300 id='mash'></td>"
print "	<td><img src='/metroui/realtimeview/simkettle.png' width=130 height=300 id='kettle'></td>"
print "	<td><img src='/metroui/realtimeview/simfridge.png' width=136 height=300 id='fridge'></td>"
print "	</tr>"

print " <tr>"
print " <td><font size=2>HLT Temp<br><span id='hlttemp'></span></font></td>"
print " <td><font size=2>Mash Temp<br><span id='mashtemp'></span></font></td>"
print " <td><font size=2>Boil Temp<br><span id='boiltemp'></span></font></td>"
print " <td><font size=2>Ferm Temp<br><span id='fermtemp'></span></font></td>"
print " </tr>"

print "<tr><td colspan=4><font size=2>Recipe: <span id='recipe'></span><br>"
print "Brewlog: <span id='brewlog'></span><br>"
print "Mode: <span id='mode'></span><br>"
print "Last Step Complete: <span id='laststep'></span></font></td></tr>"
print "	</table>"

print "</div>"	# end of frameSimulator


print """<div class='frame' id='frameLog'>"""

print "<iframe frameborder=0 src='log.py' width=100% height=810px scrolling=no></iframe>"

print "</div>"


print """
<div class='frame' id='frameGraph'>
<a href='graph-proxy.py' target='graphnewtab'><img id='graphimg' src='spacer.png' width=600 height=300 border=0></a>

</div>"""
	
if theme.localUser:		
	print """
	<div class='frame' id='frameAdjust'>
	<iframe id='iframeAdjust' frameborder=0 src='blank.py' width=100% height=100% scrolling=no></iframe>
	</div>"""


print "</div>"	# end of div/frames


print "</div>"	# end of tabe control


print """	</div>"""		#end of cell
print """	</div>"""		#end of row

print "</div>"		# end of grid fluid


print """
				<!-- begin spinner -->
                                <div id='spinner' style='height: 0px; visibility: hidden; margin: 12px;'>
                                        <div id='box'>
                                                Please Wait, <span id='spinnerText'>recalculating</span> recipe<br>
                                                <img src="images/ajax_progress2.gif">
                                        </div>
                                </div>
                                <!-- end spinner -->
"""



print "</div>"


print """
<iframe id='buttonTarget' width=1 height=0 style='visibility: hidden'></iframe>
"""

if theme.localUser:
	print "<script language=Javascript>localUser=true;</script>"
else:
	print "<script language=Javascript>localUser=false;</script>"

cfg=pitmCfg()

print """<script language=Javascript>
probehlt="%s";
probemashA="%s";
probemashB="%s";
probeboil="%s";
probeferm="%s";
</script>
""" %(cfg.hltProbe,cfg.mashAProbe,cfg.mashBProbe,cfg.boilProbe,cfg.fermProbe)

#<div id='grxaph' style="visibility: hidden;height: 0px">
print """
<script src='/metroui/js/simulator.js'></script>
"""


	
theme.presentFoot()

