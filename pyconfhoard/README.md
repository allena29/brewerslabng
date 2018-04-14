# Python Config Hoard (PyConfHoard)

This project is a clean-reworking of [Brewerslab](https://github.com/allena29/brewerslab) which is looking to provide an datamodel and associated implementation for a small brewery. Whilst the use-case is for a small homebrew setup the application could be anything where there are things (processes, scripts) that read in configuration data, does things and provides results. 

This branch is thinking about introducing NETCONF, YANG, CLI, and possibly streaming telemetry - all buzz words but things that are interesting. Unfortunately a big constraint is that paying for something is out of the question, and the resource footprint needs to be small enough to run on a Raspberry Pi.

[TailF's CONFD](http://www.tail-f.com/confd-basic/)  is interesting - but heavy weight for what is needed here and without commercial licenses doesn't tick the CLI box. There is no ARM build and the lack of CLI for the free version is a bit off putting. 

[Netopeer2](https://github.com/CESNET/Netopeer2) and [Sysrepo](https://github.com/sysrepo/sysrepo) looked promising and even though they build on a raspberry pi the lack of documentation and segmentation fault make this a little unstable.

Therefore this cobbles something together based around pyangbind - as the original *brewerslab* is reworked around a formal datamodel sysrepo/netopeer2 will be re-evaluated.

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



### Datastore

Within the datastore directory there are a number of directories, it is assumed that all functions will run either on a single host, or have access (e.g. NFS/CIFS/AFS) to the common datastore directory. 

- `datatsore/persist` provides a directory which will contain the saved configuration, this will be updated following a commit. This may be empty when there is no configuration generated. When a process restarts if this file exists it will provide the initial configuration and the next file will not be used.
- `datastore/startup` provide a directory which contains default configuration to load if a datastore is empty.
- `datastore/operational` provides periodically refreshed operational data, this is expected to be hosted on a volatile filesystem and will not be recreated if a process restarts.


### Things (i.e. data providers, data consumers, processes, services)

A *thing* is something that does some work, they follow a stanard pattern and extend the `PyConfHoard.Thing` class. 

The **Thing** class provides makes use of pyangbind to serialise/deserialise data according to the yang data model - as well as providing functions for logging and to automatically manage the datatsores. 

**TBD** threading and IPC


#### Registering a Thing

A first step is to register the YANG module, which writes an empty schema based upon the yang module. In future it will be necessary to suport upgrading modles - but in the early stage of development this will not be provided.

> The schema will be written to `datastore/startup`

```bash
./launch --thing things/directory/python-script.py --register
```


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
gunicorn --reload rest.app
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


## CLI

A very basic skeleton of a Command Line interface based around the python library `Cmd2` makes a request to `http://localhost:8000/v1/discover` and then downloads the associated configuration and operational datastores.

The CLI itself has basic constructs to show operational/data or configuration and so far has a very primitive option to set data (although there is no awarness of the structure of the yang model).

There is a decision point, do we link the CLI into pyangbind (more overhead for running clients) or add bespoke things to deal with validation and structure etc.

```
~/brewerslabng/pyconfhoard $ python cli/cli.py
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

---
---

# TODO

1. `launch --upgrade` to take datamodel files and upgrade them.
- Autentication for the CLI module.
- CLI auto complete let's us replaces containers - we should have metadata to know what is a list item/leaf

