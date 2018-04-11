# brewerslabng

This project is a clean-reworking of [Brewerslab](https://github.com/allena29/brewerslab) which is looking to provide an datamodel and associated implementation for a small brewery.

This branch is thinking about introducing NETCONF, YANG, CLI, and possibly streaming telemetry - all buzz words but things that are interesting. Unfortunately a big constraint is that paying for something is out of the question - TailF's CONFD is interesting - but heavy weight for what is needed here and without commercial licenses doesn't tick the CLI box.

[Netopeer2](https://github.com/CESNET/Netopeer2) and [Sysrepo](https://github.com/sysrepo/sysrepo) looked promising and even though they build on a raspberry pi the lack of documentation and segmentation fault make this a little unstable.

Therefore this cobbles something together based around pyangbind - as the original *brewerslab* is reworked around a formal datamodel sysrepo/netopeer2 will be re-evaluated.



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


