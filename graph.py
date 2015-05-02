#!/usr/bin/python


import sys
import rrdtool
import tempfile
import time
import os

import re


startPeriod= int(re.compile("[^0-9]*").sub('', sys.argv[2].split(".")[0]))
if time.time() - startPeriod:
	startPeriod="%s" %( time.time()-86400)
startPeriod=startPeriod.split(".")[0]
endPeriod=int(startPeriod)+86399

print ":%s: :%s:" %(startPeriod,endPeriod)
lowerLimit=15
upperLimit=30
rrdPath=sys.argv[1]
rrdtool.graph("%s.png" %(sys.argv[1]),
      '--imgformat', 'PNG',
      '--width', '1024',
      '--height', '600',
      '--start', "%s" %(startPeriod),
      '--end', "%s" %(endPeriod),
      '--vertical-label', 'Temperature (C)',
      '--title', '%s Temperature' %(sys.argv[1]),
      '--rigid',
      '--lower-limit', '%s' %(lowerLimit),
      '--upper-limit', '%s' %(upperLimit),
      '--watermark', '%s [%s]' %(re.compile("[^0-9]*").sub('',sys.argv[1]), sys.argv[2]),
	'DEF:temp1=%s:temp1:AVERAGE' %(rrdPath),
	'DEF:temp2=%s:temp2:AVERAGE' %(rrdPath),
	'DEF:temp3=%s:temp3:AVERAGE' %(rrdPath),
	'DEF:temp4=%s:temp4:AVERAGE' %(rrdPath),
	'DEF:temp5=%s:temp5:AVERAGE' %(rrdPath),
	'DEF:temp6=%s:temp6:AVERAGE' %(rrdPath),
	'AREA:temp6#FF000022',
	'AREA:temp5#FFFFFF',
	'AREA:temp4#0000FF22',
	'LINE:temp1#0000FF:Probe 1',
	'GPRINT:temp1:LAST:Current\:%8.2lf %s',
	'GPRINT:temp1:AVERAGE:Average\:%8.2lf %s',
	'GPRINT:temp1:MIN:Minimum\:%8.2lf %s',
	'GPRINT:temp1:MAX:Maximum\:%8.2lf %s',

		)


