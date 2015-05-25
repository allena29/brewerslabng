#!/usr/bin/python
import re
import sys
import cgi
import _mysql
from thememetro import *


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

print "<div class=\"container\">"



print """


            <div class="grid fluid">

                <div class="row">
                    <div class="span12">

		</div>
		</div>
"""


print """

                <div class="row">
                    <div class="span4">

                        <div id='calculateOutstanding' class="panel" style='visibility: hidden' onClick="recalculate()">
                            <div class="panel-header bg-darkRed fg-white">
                                Recalculate
                            </div>
                        </div>


                    </div>

                    <div class="span4">
                    </div>
"""


print """
			</div>

            </div>
"""

#
# simulator page
#
#

print "<table border=0 cellspacing=0 cellpadding=0>"
print "<tr valign=top>"
print "<td>"

print "<!-- realtimeview -->"

print "	<!-- buttons --> "
print "	<table border=0 cellspacing=0 cellpadding=0 width=100%%>"
print "	<tr>"
print "	<td align=right><a href=javascript:button('pLeft')><img src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
print " <td width=10>&nbsp;</td>"
print "	<td align=right><a href=javascript:button('pDown')><img src='/metroui/realtimeview/rotaryleft.png' width=25 height=54 border=0></a></td>"
print "	<td align=center><a href=javascript:button('pOk')><img src='/metroui/realtimeview/rotaryok.png' width=55 height=154 border=0></a></td>"
print "	<td align=left><a href=javascript:button('pUp')><img src='/metroui/realtimeview/rotaryright.png' width=25 height=54 border=0></a></td>"
print " <td width=10>&nbsp;</td>"
print "	<td align=left><a href=javascript:button('pLeft')><img src='/metroui/realtimeview/pushbutton.png' width=44 height=44 border=0></a></td>"
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

print "<td>"
print "<td width=10>&nbsp;</td>"
print "<td>"

print "	<!-- simulator --> "
print "	<table border=0 cellspacing=0 cellpadding=0>"

print "	<tr>"
print "	<td><img src='/metroui/realtimeview/simhltempty.png' width=90 height=126 id='hlt'></td>"
print "	<td><img src='/metroui/realtimeview/simpowerin.png' width=91 height=126></td>"
print "	<td><img src='/metroui/realtimeview/simrelays.png' width=130 height=126 id='relays'></td>"
print "	<td><img src='/metroui/realtimeview/simpowersocket.png' width=136 height=126 id='socket'></td>"
print "	</tr>"
print "	<tr>"
print "	<td><img src='/metroui/realtimeview/simhltstand.png' width=90 height=300 id=''></td>"
print "	<td><img src='/metroui/realtimeview/simmash.png' width=91 height=300 id='mash'></td>"
print "	<td><img src='/metroui/realtimeview/simkettle.png' width=130 height=300 id='relays'></td>"
print "	<td><img src='/metroui/realtimeview/simfridge.png' width=136 height=300 id='fridge'></td>"
print "	</tr>"

print "	</table>"


print "</td>"
print "</tr>"

print "</table>"

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

print """
<script src='/metroui/js/simulator.js'></script>
"""


theme.presentFoot()
