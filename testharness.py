import sys
import time
from gpiotools import *
from pitmLCDisplay import *
lcd=pitmLCDisplay()
gpio=gpiotools()

testtype="all"
if len(sys.argv) > 1:
	testtype=sys.argv[1]

lcd.sendMessage("Testing",0)
lcd.sendMessage(" Temperature",1)


if testtype == "all" or testtype == "temp":


	gpio.output('tempProbes',1)


	lcd.sendMessage(" Mash + HLT" ,2)

	print "Temperature - probe port Mash + HLT" 
	tempBaseDir="/sys/bus/w1/devices/"
	for x in range(6000):
		for probe in os.listdir( tempBaseDir ):
			if probe.count("28-"):
				print x,time.ctime(),
				try:
					o=open( "%s/%s/w1_slave" %(tempBaseDir,probe))
					print probe,		
					text=o.readline()
					if text.count("NO"):
						print "invalid"
						lcd.sendMessage(" invalid",3)

					if text.count("YES"):		# CRC=NO for failed results
						temp=o.readline()
						o.close()
						
						temperature = float(temp.split(" ")[9][2:])/1000

						# fudge factor for 0 / 85 results when not connected	

						lcd.sendMessage(" %s %s" %(temperature,probe[3:]),3)
						print temperature	
				except:
					lcd.sendMessage(" file missing",3)
					print "file disappeared",probe
			time.sleep(1)


