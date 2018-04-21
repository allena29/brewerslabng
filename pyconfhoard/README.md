# Python Config Hoard (PyConfHoard)

This project is a clean-reworking of [Brewerslab](https://github.com/allena29/brewerslab) which is looking to provide an datamodel and associated implementation for a small brewery. Whilst the use-case is for a small homebrew setup the application could be anything where there are things (processes, scripts) that read in configuration data, does things and provides results. 

This branch is thinking about introducing NETCONF, YANG, CLI, and possibly streaming telemetry - all buzz words but things that are interesting. Unfortunately a big constraint is that paying for something is out of the question, and the resource footprint needs to be small enough to run on a Raspberry Pi.

[TailF's CONFD](http://www.tail-f.com/confd-basic/)  is interesting - but heavy weight for what is needed here and without commercial licenses doesn't tick the CLI box. There is no ARM build and the lack of CLI for the free version is a bit off putting. 

[Netopeer2](https://github.com/CESNET/Netopeer2) and [Sysrepo](https://github.com/sysrepo/sysrepo) looked promising and even though they build on a raspberry pi the lack of documentation and segmentation fault make this a little unstable.

Therefore this cobbles something together based around exporting the YIN definition - as the original *brewerslab* is reworked around a formal datamodel sysrepo/netopeer2 will be re-evaluated.

This project in it's current form will never scale to 100,000's requests per second - but the simple act of seriously re-considering code that is >3 years old, putting the structure of a database-moel and discipline of testing will make this project easier to transition to a more industrial solution if needed.


## Setup

1. [Raspberry PI Basic Setup](Documentation/RaspberryPi.md)
2. ~~[Netopeer2 Install~~](Documentation/InstallNetopeer2.md)~~



## Overview


### YANG Model

The following basic yang model can be used to represent functions in a pico-brewery, of course this is just describing how to store data - (noun) rather than having any behaviour/action (verb). 


```
module: brewerslab
  +--rw brewhouse
  |  +--rw temperature
  |     +--rw fermentation
  |     |  +--ro monitor?     boolean
  |     |  +--rw setpoint?    brewerslab:temperature
  |     |  +--rw highpoint?   brewerslab:temperature
  |     |  +--rw lowpoint?    brewerslab:temperature
  |     |  +--rw probe
  |     |  |  +--rw id?   string
  |     |  +--rw results
  |     |     +--ro latest?    brewerslab:temperature
  |     |     +--rw average
  |     |        +--ro minute?   brewerslab:temperature
  |     |        +--ro hourly?   brewerslab:temperature
  |     |        +--ro daily?    brewerslab:temperature
  |     +--rw hardware
  |        +--rw probe* [id]
  |           +--rw id         string
  |           +--rw offsets* [low high]
  |              +--rw low       brewerslab:temperature
  |              +--rw high      brewerslab:temperature
  |              +--rw offset?   brewerslab:temperature
  +--rw ingredients
  |  +--rw fermentable* [ingredient]
  |  |  +--rw ingredient    string
  |  +--rw adjunct* [ingredient]
  |  |  +--rw ingredient    string
  |  +--rw hops* [ingredient]
  |     +--rw ingredient    string
  +--rw recipes
  |  +--rw recipe* [recipename]
  |     +--rw recipename    string
  +--rw brewlog
```

The yang file is transformed to `YIN` format (stanard pyang) and then this is transformed to a simple JSON representation (custom format). This is stored in the yang sub-directory as `schema.json`


### Datastore

#### Python Access

The manipulation of the datastore is the responsibility of `PyConfHoardDataStore` which makes use of the dpath library to provide the navigation. The schema is a straightforward JSON structure. Each key within the JSON structure containing '__' details the metadata associated wtih a node, otherwise it is part of the structure itself.

When providing paths they can either be provided as lists, or a delimeter separated string (default is space - but most operations take in a `separator` keyword.

```json
{
    "simplestleaf": {
        "__config": true,
        "__leaf": true,
        "__value": null,
        "__path": "/simplestleaf",
        "__listkey": false,
        "__type": "string"
    },
    "simplecontainer": {
        "__path": "/simplecontainer",
        "leafstring": {
            "__config": true,
            "__leaf": true,
            "__value": null,
            "__path": "/simplecontainer/leafstring",
            "__listkey": false,
            "__type": "string"
        },
        "leafnonconfig": {
            "__config": false,
            "__leaf": true,
            "__value": null,
            "__path": "/simplecontainer/leafnonconfig",
            "__listkey": false,
            "__type": "string"
        }
    },
    "simplelist": {
        "__list": true,
        "__elements": {},
        "__path": "/simplelist",
        "__keys": "item",
        "item": {
            "__config": true,
            "__leaf": true,
            "__value": null,
            "__path": "/simplelist/item",
            "__listkey": true,
            "__type": "string"
        },
        "subitem": {
            "__config": false,
            "__leaf": true,
            "__value": null,
            "__path": "/simplelist/subitem",
            "__listkey": false,
            "__type": "string"
        }
    } 
}
```

 
#### Datastore Operations


- `get(path)` - returns the __value associated with the node
- `list(path)` - lists the children (keys) associated with the node
- `create(path, key)` - creates an instance of the node at path and stores it in the reserved `__elements` key.


#### Mapping to YANG

As the `schema.json` is rendered based upon the YIN file of the YANG and implemented by PyConfHoardDatastore.py any YANG option *MUST* be supported by both. [test/example-schema.json](test/example-schema.json) provides an overview of the YANG concepts ~~tested~~ planned to be supported.

Particular Points 

- **integers/booleans** show these as non-quoted strings when showing the Filtered/pretty view - cosmetic change only
- **restrictions (part1)** simple valiation of restrictions
- **enumeration** schema.json records the keys of enumerations (TBD: do we implement enumerations properly mapping to an ID or use the value itself)
- **typedefs** no plan to support
- **imported yang files** YIN may provide a completely transparent rendering even if the yang model of interest iports others.
- **grouping** potentially YIN makes this transparent - in which case support may be implicit
- **container presence nodes** - likely a trivial extension to 
- **mandatory siblings/children** - if we create a list (*or presence node*) we should ensure that sibilings/chidlren that are marked mandatory are provided

>To implement new YANG constructs the following requirements need to be satisifed
>
>1. ensure PyConfHoardSchema.py provides sensible output
>- ensure PyConfHoardDataStore handles the new contraints yang
>- update cli to provide sensible handling.


To help develop and understand how the data mapping works when jin2json convers the YANG model into it's JSON representation a terse summary will be sent to the terminal. 

```
/simplestleaf leaf string conf-data
/simplecontainer container conf-data-decendents oper-data-decendents
/simplecontainer/leafstring leaf string conf-data
/simplecontainer/leafnonconfig leaf string oper-data
/level1 container conf-data-decendents oper-data-decendents
/level1/level2 container conf-data-decendents oper-data-decendents
/level1/level2/level3 container conf-data-decendents oper-data-decendents
/level1/level2/level3/withcfg container conf-data-decendents
/level1/level2/level3/withcfg/config leaf string conf-data
/level1/level2/level3/withoutcfg container oper-data-decendents
/level1/level2/level3/withoutcfg/nonconfig leaf string oper-data
/level1/level2/level3/mixed container conf-data-decendents oper-data-decendents
/level1/level2/level3/mixed/config leaf string conf-data
/level1/level2/level3/mixed/nonconfig leaf string oper-data
/simplelist list conf-data-decendents oper-data-decendents
/simplelist/item leaf string conf-data
/simplelist/subitem leaf string oper-data
/types container conf-data-decendents
/types/number leaf uint8 conf-data
/types/biggernumber leaf uint16 conf-data
/types/bignumber leaf uint32 conf-data
/types/hugenumber leaf uint64 conf-data
/types/secondlist list conf-data-decendents
/types/secondlist/item leaf enumeration conf-data
                  Enum Values:  ['A', 'B']
/types/secondlist/thingwithdefault leaf string conf-data
                  Default HELLO
                  
```


#### Datastore Storage

Within the datastore directory there are a number of directories, it is assumed that all functions will run either on a single host, or have access (e.g. NFS/CIFS/AFS) to the common datastore directory. 

All operations around the datastore are formed based upon `yang/schema.json` and `PyConfHoardDatatstore`

- `datatsore/persist` provides a directory which will contain the saved configuration, this will be updated following a commit. When a process restarts if this file exists it will provide the initial configuration.
- `datastore/default` provide a directory which contains default configuration to load if a datastore is empty.
- `datastore/running` provides a directory which contains running configuration, other processes will use this when reading data. This implies the persist data may *never* exst. This should be created as soon as a default configuration is parsed.
- `datastore/operational` provides periodically refreshed operational data, this is expected to be hosted on a volatile filesystem and will not be recreated if a process restarts.



### Things (i.e. data providers, data consumers, processes, services)

A *thing* is something that does some work, they follow a stanard pattern and extend the `PyConfHoard.Thing` class. 

The **Thing** class provides methods to serialise/deserialise data based on the original schema provided.

**TBD** threading and IPC



#### Starting a Thing

From the top-level project directory use the launch utility.

```bash
./launch --thing things/directory/python-script.py 
```

To support debugging it is sometime useful to use ipython, the `--debug` flg can be added to the launcher. This provides an IPython terminal allowing access to the datamodel for debugging an experimenttion as well as allowing the launcher to be run interactively.


#### Skeleton Thing

```python
import PyConfHoard

class TemperatureProviderDs18B20(PyConfHoard.Thing):

	# Note: __init__ is implemented in PyConfHoard.Thing
	
	# This takes in the following vales
	# - friendly app name (e.g. Temperature Provider)
	# - YANG module (e.g. brewerslab)
	# - YANG Path relative to YANG Module (e.g. /brewhouse/temperature)
	
	def setup(self):
		# Code run when at the end of the constructor 
	
class Launch:

    def __init__(self, start=False):
        try:
            self.thing = TemperatureProviderDs18B20('TemperatureProvider',     # friendly app name
            									       'brewerslab',              # yang module
            									       '/brewhouse/temperature')  # path owned
            if start:
                self.thing.start()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    Launch()
```



## REST Server 

A REST server is implemented using [gunicorn](http://gunicorn.org/) and [Falcon](https://falconframework.org/#sectionCommunity). This should run on a server that has access to the central datastore. It is not mandated that it *must* be on the same server as running the processes.


It is expected that the server will also allow clients to write configuration (Authentication/Authorization TBD.. running on HTTPS etc).

The server can be started from the pyconfhord dircetory.

```
./launch --rest
```

An example of fetching opdata for the Temperature Provider is shown below.

```
http localhost:8000/v1/datastore/startup/TemperatureProvider
HTTP/1.1 200 OK
Connection: close
Date: Thu, 12 Apr 2018 00:01:49 GMT
Server: gunicorn/19.7.1
content-length: 196
content-type: application/json; charset=UTF-8

{
    "__namespace": "brewerslab",
    "fermentation": {
        "highpoint": "0",
        "lowpoint": "0",
        "probe": {
            "id": ""
        },
        "setpoint": "17"
    }
}
```

#### TODO:

1. Allow data to be saved on the backend
- If data is updated we need to trigger things


## CLI

A very basic skeleton of a Command Line interface based around the python library `Cmd2` makes a request to `http://localhost:8000/v1/discover` and then downloads the associated configuration and operational datastores.

The CLI itself has basic constructs to show operational/data or configuration and so far has a very primitive option to set data (although there is no awarness of the structure of the yang model).

For no real reason, the CLI colour-codes the status of downloading datastores (and changes the colour to indiciate status)

```
~/brewerslabng/ $ ./launch --cli
wild@localhost> show
{
    "brewhouse": {
        "fermentation": {
            "monitor": false,
            "results": {
                "average": {
                    "daily": "0",
                    "hourly": "0",
                    "minute": "0"
                },
                "latest": "0"
            }
        }
    }
}

[ok][Sat Apr 14 18:51:18 2018]
wild@localhost> conf
Entering configuration mode private

[ok][Sat Apr 14 18:51:22 2018]
[edit]
robber@localhost% show
{
    "brewhouse": {
        "fermentation": {
            "highpoint": "0",
            "lowpoint": "0",
            "probe": {
                "id": ""
            },
            "setpoint": "0"
        },
        "power": {
            "mode": ""
        }
    }
}

[ok][Sat Apr 14 18:51:24 2018]
robber@localhost% set brewhouse power mode ABC
robber@localhost% show
{
    "brewhouse": {
        "fermentation": {
            "highpoint": "0",
            "lowpoint": "0",
            "probe": {
                "id": ""
            },
            "setpoint": "0"
        },
        "power": {
            "mode": "ABC"
        }
    }
}

[ok][Sat Apr 14 18:51:39 2018]
robber@localhost% exit

robber@localhost> exit
```

#### TODO

1. Cosmetic: filter out nodes which have no contents 
- Feature: authentication for CLI module.



