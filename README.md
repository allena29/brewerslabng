# brewerslabng

This project is a clean-reworking of [Brewerslab](https://github.com/allena29/brewerslab) which is looking to provide an datamodel and associated implementation for a small brewery. There has been a lot of stop/start on rewriting the existing code - most of the problem stems from reactoring in between brewing beer is unlikely to happen- so a gradual migration is required.

There is still a strong desire to distribute, physical ports on a Raspberry Pi (I have two or three of these) can be extended with things like I2C, but that adds fragility for someone with my lack of soldering skills. Some obvious toolsets are too memory hungry or not available for ARM architecture (Tail-f ConfD, Elasticsearch, Kibana etc). Anything that uses Java is ruled out (Kafka was in with something to play with).

By retaining the multicast transmission of JSON encoded data it will be possible to migrate functions one by one - and within a brewday it would be possible to switch from old to new. The old code imports code with the `pitm` designation (pi temperature monitor), the new code will be designated with `blng` (brewers lab next generation)

The data for the brewery will use a strong data model (YANG), and this is still the desire.

Docker on a Raspberry Pi appears to be quite favourable at this stage - however it doesn't magically solve architecture differences. There are caveats with Multicast on the MAC because it uses a VM (going our own way with VirtualBox is an efective workaround).


# Approach to migrating rom 

- 1/ Move the recording of results to InfluxDB and Grafana
- 2/ Move the manual flag setting to a basic CLI based approach using Netopeer2/Sysrepod
- 3/ Re-implement functions
  - a/ iSpindel   
  - b/ Temperature Sender
  - c/ Relay Control
  - d SSR Contrl



# TODO:

### publishTempeartureToInflux


- TODO: we need to convert probeId mappings into Netconf datastore - not read from config file.
- we need to move target temperatures into Netconf datastore - not broadcast from governor




# Setup

1. [Raspberry PI Basic Setup](Documentation/RaspberryPi.md)
2. `git clone https://github.com/allena29/brewerslab` (to be deprecated but still required)
3. `git clone https://github.com/allena29/brewerslabng`


### Hardware 

- Raspberry Pi 
- DS18B20 - 1 Wire Temperature Probes
- Optional: iSpindel Hydrometer Tilt 




# Functions

### Temperature Monitoring (legacy pitmTempMonitor.py)

TODO: old module must be used.

For temperature monitoring we use DS18B20 probes [see here](https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/temperature/), one importnt lesson is that the resistor is very important in ensuring stable clocking of the signal.

The newer Raspberry PI's need 1wire support explicitly enabling in `raspi-config` from the Interfacing Options menu. If a PI isn't required for temperature monitoring it is best to disable the module as there can be CPU spikes whilst the kernel tries to discover non-existant probes.

When operating correctly looking in `/sys/bus/w1/devices` should shown a number of directories with a random but unique idenitifer (e.g. 28-0417c4aa05ff), each contains a file named `w1_slave`

```
0f 01 4b 46 7f ff 0c 10 0f : crc=0f YES
0f 01 4b 46 7f ff 0c 10 0f t=16937
```

In this case the temperature is 16.937, this can be found by taking `t=16937`, the resolution of the probes is limited based on the Analogue-Digital Conversion. A value of 85000 is an invalid reading and points to disruption on the 1-Wire bus - physical wiring should be checked.

Each time a temperature reading is taken it is published via a JSON string publised on the Multicast group 239.232.168.250 port 5087. This result is padded to 1200 bytes, however in future the configuration data will be moved out to a NETCONF data store. **The publishing of the temperatures themselves will remain** (i.e. `currentResult` and `_operation` keys)

```json
{	
	"_operation": "temperatureResults1",
	"currentResult": {
			"28-0417c4aa05ff': {
					"timestamp": 1537224875.011157,
					"valid": True, 
					"temperature": 16.937
			}
	},
	"_brewlog": "08.09.2018",
	"_recipe": "Citra18",
	"_mode": "ferm",
	"currentStatus": 0,	
	"hlt": "28-0417c4b010ff",
	"mashA": "28-0417c4acedff",
	"mashB": "28-0417c4acedff",
	"ferm": "28-0417c4aa05ff", 
	"_checksum": "                                        ", 
	"tempTargetBoil": [-1, -1, -1],
	"tempTargetHlt": [-1, -1, -1],
	"tempTargetFerm": [16.7, 17.3, 17.0],
	"tempTargetSparge": [-1, -1, -1], 
	"tempTargetMash": [-1, -1, -1], 
	}
}
```



#### Fermentation Monitoring 

An [iSpindel](https://github.com/universam1/iSpindel/blob/master/docs/README_en.md) can be used to provide an approximate the progress of fermentation, this is unlikely to be entirely accurate but provides a useful guide for the progress. The iSpindel can be configured to submit results to a service like Ubidots, or a Generic TCP server where we have a simpe JSON structure. 

**Note: the iSpindle does not talk HTTP**


```json
{
	"name": "iSpindel000",
	"ID": 14039613,
	"token": "A1E-fEI",
	"angle": 43.95625,
	"temperature": 17.1875,
	"battery": 4.223149,
	"gravity": 3.919538,
	"interval": 600
}
```

Calibration provides a formula to map the tilt value into Plato.

```
FORMULA_1 = 0.008626076
FORMULA_2 = 0.439419453
FORMULA_3 = 4.677151587

FORMULA_1 * angle **2 - FORMULA_2 * angle + FORMULA_3
```

Once we have the data it will be submitted via HTTP to the Influx Database used by Grafana and the grapical dashboard.



### Graphical Dashboard

Temperature Publishing (publishTemperatureToInflux.py)

To provide a graphical dashboard the Influx Database is used to store the data, a multicast receiver will collect the results and publish them into the database. Grafana is then used to draw pretty graphs.







# Testing

The best way to see how this project and code behaves is by running the approval testing, this will run through a set of tests. This will create a datastore will be created in a temporary directory and removed after the test is compelted. 

The test harness follows Behaviour Driven Development approach which ensures asserts conditions in response to certain actions.

TODO... populate it.





# Functions


## Graphical Dashbord

The username is `beerng` and the password is `beerng`. 

```
docker run --name grafana -i -d -p 3000:3000 -p 8086:8086 allena29/brewerslabng:grafana
```

For the dashboards to receive any stats the following processes need to run, they need to be able to successfully receive multicast and be able to make HTTP calls to the Influx DB port 8086.

```
screen -dmS broadcastGravity python broadcastISpindelGravity.py
screen -dmS publishGravity python publishGravityToInflux.py
screen -dmS publishTemperature python publishTemperaturesToInflux.py
```
