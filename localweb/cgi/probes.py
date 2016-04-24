#!/usr/bin/python
import time
import re
import os
import cgi

rxTemp=re.compile("^.*t=(\d+)")
cfgprobe=re.compile("^\s*self.fermProbe\s*=\s*\"(\S+)\".*")

form=cgi.FieldStorage()
if form.has_key("action"):
	auth=False
	if form.has_key("adminpass"):
		if form['adminpass'].value  == "brewerslabaaa123":
			auth=True

	if not auth:
		print "Content-Type: text/html\n\n Wrong password... configuration not changed"
		sys.exit(0)

	if form['action'].value=="updateprobes":

		pitmCfg=[]
		o=open("pitmCfg.py")
		y=o.readline()
		while y != "":
			if cfgprobe.match(y):
				pitmCfg.append("                self.fermProbe=\"%s\"\n" %(form['fermprobe'].value))
			else:
				pitmCfg.append(y)
			y=o.readline()
		o.close()


		O=open("pitmCfg.py","w")
		for x in pitmCfg:
			O.write(x)
		O.close()
		print "Content-Type:text/html\n\nRebooting... please wait"

		os.system("sudo sh /home/beer/brewerslab/rebootIn15.sh &")
		sys.exit(0)
print """
<!DOCTYPE html>
<html>
<head>
    <script src="../js/jquery-1.12.0.min.js"></script>
    <link href="../css/metro.css" rel="stylesheet">
    <script src="../js/metro.min.js"></script>
    <script src="../js/wwwajax.js"></script>
    <link href="../css/metro-icons.css" rel="stylesheet">

<body>
    <div class="page-content">

	<div class="container">
  
		<h1>Probes</h1>

		<p><i>Note: probe discovery may take up to 30 seconds</i></p>

	<b>	Discovered Probes</b><p>
"""
realProbes=[]
for probe in os.listdir("/sys/bus/w1/devices/"):
	if probe.count("28-"):
		print "<li> ",probe
		realProbes.append( probe )
		o=open("/sys/bus/w1/devices/%s/w1_slave" %(probe))
		text=o.readline()
		temp=o.readline()
		if text.count("NO"):
			print " - Invalid reading"
		elif text.count("YES"):
			(temp,)=rxTemp.match(temp).groups()
			temperature=float(temp)/1000
			print " - %.3f C" %(temperature)

		o.close()
print """
<form method=POST>
<input type=hidden name=action value="updateprobes">
	<p>
<h3>Fermentation</h3>

	Probe ID : <select name='fermprobe'>"""


pitmCfg=[]
o=open("pitmCfg.py")
y=o.readline()
while y != "":
	pitmCfg.append(y.rstrip())
	if cfgprobe.match(y):
		print "<option>%s" %(cfgprobe.match(y).groups('\g<1>'))
	y=o.readline()
o.close()

for probe in realProbes:
	print "<option>%s" %(probe)
print """
</select>

<P>Admin Password:
			<div class="input-control password" data-role="input">
			    <input type="password" name='adminpass' id='password2' value="">
			    <button class="button helper-button reveal"><span class="mif-looks"></span></button>
			</div>
<p>
<font color=red><b>Note: making changes will cause a reboot.</b></font><P>


<input type="submit" value="Update Probe Configurations">
</form>
		</div>



	</div>
    </div>







<footer class='app-bar fixed-bottom drop-up'>brewerslab - <a href="https://github.com/allena29/brewerslab/"><span class='fg-white'> &nbsp; <span class="mif-github"></span> &nbsp;github.com/allena29/brewerslab</span></a></footer>

</body>


<script>
</script>
</html>
"""
