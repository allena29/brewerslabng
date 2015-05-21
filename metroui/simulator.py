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

