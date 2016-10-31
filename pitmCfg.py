   






class pitmCfg:



	def __init__(self):

		self.tweetProgress="@allena29"		# username to tweet updates to


		self.activities = {
			'Mash' : {'min':65,'max':69,'lowalarm':True,'highalarm':True,'sleep':False},
			'Fermentation':{'min':18,'max':21,'lowalarm':False,'highalarm':False,'sleep':True},
			'HLT' : {'min' : 80, 'max':87,'lowalarm':False,'highalarm':True,'sleep':False},
			'Boiler' : {'min' : 99,'max':101,'lowalarm':False,'highalarm':True,'sleep':False},
			'Test Activity':{'min':1,'max':105,'lowalarm':False,'highalarm':False,'sleep':False},
			}


		self.monitorFrequency=1

		self.gpioleds={'red':23,'blue':19,'green':21}
		self.gpiobuzzer=15

		# checksum provides a basic check before reacting to multicast packets.
		self.checksum = "ABFJDSGF"


		# Updated Probe ID's
		self.hltProbe="28-000003ebc866"
		self.mashAProbe="28-000003eba86a"
		self.mashBProbe="28-000003ebccea"
		self.boilProbe="28-0000044dcda4"
                self.fermProbe="28-00044efeaaff"
		self.tempProbe="28-04150116e2ff"
		# Probe Adjutment Tweak
		# dict key = probeId
		# dict val = list of 3 tuple elements
		#			(temp >= X, temp < X, tempAdjustment)
		#			between 60 and 75 there is a 1.5deg
		self.probeAdjustments={
			"28-000003eba86a"	:	[ (60,75, 1.5), (75,80, 2), (80,99,2.5), (50,60,1) ],
			"28-000003ebccea"	:	[ (60,75, 1.5), (75,80, 2), (80,99,2.5), (50,60,1) ],

		} 
		self.probeId={
			self.hltProbe : 'hlt ',
			self.mashAProbe : 'tunA',
			self.mashBProbe : 'tunB',
			self.boilProbe : 'boil',
			self.fermProbe : 'ferm',
			self.tempProbe : 'temp',
		}

		# Multicast address and port
		self.mcastPort = 5085
		self.mcastLcdPort = 5086
		self.mcastMatrixPort = 5099
		self.mcastBidirPort = 5184
		self.mcastButtonPort = 5183
		self.mcastButtonPortRX = 5983
		self.mcastRelayPort = 5082
		self.mcastSsrRelayPort = 5182
		self.mcastTemperaturePort = 5087
		self.mcastTemperatureSecondPort = 5187
		self.mcastGrapherPort = 5088
		self.mcastMonitorPort=5089
		self.mcastBuzzerPort=5090
		self.mcastStatsPort=5112	
		self.mcastFlasherPort=5091	# used to broadcast our state to the controller
		self.mcastFlasherInPort=6091	# used to receive our broadcasts
		self.mcastSimulatorPort=5111

		self.mcastGroup = '239.232.168.250'

		# pins for master
		self.gpioDown=11
		self.gpioUp=13
		self.gpioSelect=8
		self.gpioSlavePowerRelay=23	# controls if the relay board is active or not

		# pins for slave
		self.gpioRelayExtractorFan=26
		self.gpioRelayPump=24

