import os
import sys

class webTheme:


    def __init__(self):
        self.bgcolor="#efeae3"
        self.pagetitle=""
        self.splash=""		# used to show a prominent welcome
        self.splash2=""
        self.js=""
        self.body=""
        self.body2=""
        self.bodytitle=""
        self.goBackHome=""
        self.noHeader=False

	self.localUser=False
	self.localUsers=['192.168.1.34','192.168.1.36']
	try:
		self.localUsers.index( os.environ['REMOTE_ADDR'])
		self.localUser=True
	except ValueError:
		pass
			  
        self.toc=""
        self.tableOfContents=""

        self.toc=""
        self.toc=""
        self.toc=""
        self.toc2=""
        self.toc3=""
        self.body3=""
        self.body4=""
        self.body5=""
        self.body6=""
        self.body7=""
        self.toolbar=""
        self.subtoolbar=""
        self.footer=""
        self.footer2=""
        self.footer3=""
        self.sidebar2=""
        self.prebody=""
        self.prebody2=""
        self.pretoolbar=""

    #      <h2> <span class="dark">Resources</span></h2>
    #
    def presentIt(self):
        self.presentHead()
        self.presentBody()
        self.presentFoot()


    def error(self,errHeading="Error",errText="Unknown Error"):
        print """

	<h2><i class="icon-cancel fg-red on-right on-left"></i><span class='fg-red'>%s</span></h2><p><span class='fg-red'>%s</span></p>
	""" %(errHeading,errText)
	sys.exit(0)



    def presentHead(self):
        print """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="css/metro-bootstrap.css" rel="stylesheet">
    <link href="css/metro-bootstrap-responsive.css" rel="stylesheet">
    <link href="css/brewers.css" rel="stylesheet">
    <link href="css/docs.css" rel="stylesheet">
    <link href="js/prettify/prettify.css" rel="stylesheet">
    <!-- Load JavaScript Libraries -->
    <script src="js/jquery/jquery.min.js"></script>
    <script src="js/jquery/jquery.widget.min.js"></script>
    
    <script src="js/jquery/jquery.mousewheel.js"></script>
	<script src="js/prettify/prettify.js"></script>

    <!-- Metro UI CSS JavaScript plugins -->
    <script src="js/load-metro.js"></script>

	<!-- local js -->
    <script src="js/metro-accordion.js"></script>
    <script src="js/metro-listview.js"></script>
    <script src="js/metro-calendar.js"></script>
    <script src="js/metro-datepicker.js"></script>
    <script src="js/docs.js"></script>


    <script src="js/utils.js"></script>
    <script src="js/wwwajax.js"></script>
	%s
    <title>%s</title>

</head>
<body class="metro" style="background-color: %s">

		""" %(self.js,self.pagetitle,self.bgcolor)
        #<header class="bg-dark" data-load="header.html"></header>

        if not self.noHeader:
            print """
				<header class="bg-black" style='background: url(..//web/images/b1.jpg) top right no-repeat;' onClick="window.location='index.py'"></header>
				"""
        height=200
        if self.splash and self.splash2:
            height=600
        if self.splash or self.splash2:
            print """
    <div class="">
        <div style="background: url(..//web/images/b1.jpg) top left no-repeat; background-size: cover; height: %spx;">
            <div class="container" style="padding: 50px 20px">
                <h1 class="fg-white">%s</h1>
                <h2 class="fg-white">%s</h2>

            </div>
        </div>""" %(height,self.splash,self.splash2)


    def presentBody(self):
        if self.bodytitle:
            print "<div class=\"container\"><h1>"
            if self.goBackHome:
                print """<a href="%s"><i class="icon-arrow-left-3 fg-darker smaller"></i></a> """ %(self.goBackHome)
            else:
                print "<img src='images/spacer.gif' width=36 height=36>"
            print """%s</h1><p>&nbsp;</p></div>""" %(self.bodytitle)
        print """<div class="container">
		<!--body -->
			%s

		<!-- body2 -->
			 %s
</div> <!-- presentBody Container -->""" %(self.body,self.body2)

    def doGrid(self,grid):
        if not grid:	return
        print """\t  <div class="container"> <!-- grid container -->
            <div class="grid fluid">"""
        i=0
        gridSorted=[]
        for item in grid:
            gridSorted.append(item)
        gridSorted.sort()


        limit=3


        for item in gridSorted:
            if i == 0:	print """\t\t<div class="row">"""
            if grid[item].has_key("url"):
                if not grid[item].has_key("colour"):	grid[item]['colour']="Green"
                print """             <a href="%s"
			                   class="place-left button bg-darkGreen bg-hover-green fg-white fg-hover-white bd-orange" style="margin-top: 10px">
                    <h3 style="margin: 10px 40px">%s></span></h3>
                </a>
				""" %(grid[item]['url'],grid[item]['text'])
                #<h3 style="margin: 10px 40px">Download <span class="icon-download-2 on-right"></span></h3>
            elif grid[item].has_key("url2"):
                if not grid[item].has_key("colour"):	grid[item]['colour']="green"
                print """
			    <div class="span4 bg-%s padding20 text-center" >
				
				<h2 class="fg-white"><a href="%s"><font color=white>%s</font></a></h2>
			    </div>
			""" %(grid[item]['colour'],grid[item]['url2'],grid[item]['text'])
            else:
                if not grid[item].has_key("colour"):	grid[item]['colour']="green"

                print """
			    <div class="span4 bg-%s padding20 text-center" >
				<h2 class="fg-white">%s</h2>
			    </div>
			""" %(grid[item]['colour'],grid[item]['text'])
            i=i+1
            if i == limit:
                print "\t\t</div> <!-- row -->"
                i=0
        if i > 0:
            print "\t\t</div>  <!-- row -->"


        print """
		    </div> <!-- grid fluid>
		</div> <!-- container for doGrid -->
"""
    def presentFoot(self):

        print """<!-- present foot-->
        """


    def finish(self):

        print """


    <script language="Javascript">
  ie=0;
  try{
  v=document.documentMode;
  if(!v){
    ie=0;
  }else{
    ie=v;
  }
  }
catch(err)
  {
    ie=-1;

  }

 if(ie<9){

    if(readCookie("ieVersionWarning") != "true"){
        try {
            window.location.replace("ieVersion.py");
        } catch (err){
            window.location="ieVersion.py";
        }
        //createCookie("ieVersionWarning","true");
    }

 }else{
    createCookie("ieVersionWarning","false");
 }


    </script>
</body>
</html>"""



if 1==0:
    print """
<script src="https://office.bt.com/_Layouts/BT.Common/gnb.js" type="text/javascript"></script>
<script type="text/javascript">if(BTCommon && BTCommon.GlobalNav)BTCommon.GlobalNav.show('_blank');</script>
<noscript>
	<a href="http://navigate.intra.bt.com/gnblinks.htm">Access global navigation links</a>
</noscript>


"""


