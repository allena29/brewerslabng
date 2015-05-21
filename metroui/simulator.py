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
print "<tr>"
print "<td>"


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

theme.presentFoot()

