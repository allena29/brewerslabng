#!/usr/bin/python

import os

print "Content-Type:text/xml\n"

try:
	os.system("sudo sh /home/beer/brewerslab/slave/launch-standalone-temp.sh &")

	print "<xml><ok>1</ok></xml>"
	
except ImportError:

	print "<xmxmxmxmxmxmsdlkfhsdklhfio2h348923hr89hf8933h2f"
