# brewerslabng

This project is a clean-reworking of [Brewerslab](https://github.com/allena29/brewerslab) which is looking to use [Netopeer2](https://github.com/CESNET/Netopeer2) and [Sysrepo](https://github.com/sysrepo/sysrepo) to provide the datastore and NETCONF.


## Setup

1. [Raspberry PI Basic Setup](Documentation/RaspberryPi.md)
2. [Netopeer2 Install](Documentation/InstallNetopeer2.md)



## Overview

### sysrepod

- `/etc/sysrepod/yang` and `/etc/sysrepod/data` contains the installed list of yang modules and the data for each module within the database.


### Install YANG

```bash
sudo sysrepoctl --install --yang=/home/user/ietf-interfaces.yang
sudo sysrepoctl --change --module=brewerslab  --owner=beerng:beerng
sysrepoctl --list
```

### Basic Python access to sysrepo

```python
import libsysrepoPython3 as sr
conn = sr.Connection("example_application")
sess = sr.Session(conn)
subscribe = sr.Subscribe(sess)

print('Showing our schemas')
schemas = sess.list_schemas()
for i in range(schemas.schema_cnt()):
     print(schemas.schema(i).module_name())


def cb_module_change(sess, module_name, event, private_ctx):
    print('cb_module_change %s %s %s %s' % (sess, module_name, event, private_ctx))
    
    
    
module_name = 'brewerslab'
subscribe.module_change_subscribe(module_name, cb_module_change)
```


