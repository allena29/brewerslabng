# Sysrepo - Configuration Store

The following (amd64) docker image can be used `docker pull allena29/syrepo:0.7.7`

This document provides an overview of interacting with sysrepod directly rather than via the Netopeer2 netconf server.
Commands in this document should be run from the top-level directory containing the git clone.

The **deb** package providing sysrepod pre-compiled with python3 support is in /tmp/debs of the docker image.


## Start Docker & Sysrepod


```bash
./launch-standalone 09f1721d27b3

# inside docker container
screen -dmS sysrepo sysrepod -d -l 2
sysrepo-plugind
```

## Install YANG & Initialise startup configuration

```bash
cd /brewerslabng/yang
./install-yang.sh
cd /brewerslabng/init-data
./init-xml.sh

```

## Exporting Data

The datastore can be **startup** or **running**, however the running datastore can only be accessed if there is a subscriber to the yang module.

```
sysrepocfg --export --format=xml --datastore=startup integrationtest
<morecomplex xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
 <inner>
   <leaf5>fsf</leaf5>
 </inner>
</morecomplex>

sysrepocfg --export --format=xml --datastore=running integrationtest
Cannot operate on the running datastore for 'integrationtest' as there are no active subscriptions for it.
Canceling the operation.
```

## Subscribers

The providers folder contains basic sysrepo python based subscribers which will be invoked each time data changes. A subscriber will independently provide callbacks for config changes (module_change) and oper-data requests (dp_get_items).

```bash
cd /brewerslabng/providers
./launch-providers.sh
```

Each provider is launched in a screen session `screen -list` and `screen -r providerintegrationtest.py` to see the sessions and resume.


## Importing Data

The data can be imported into the running config (with at least on subscriber active) or startup config (without requiring any subscribers). Note: the docker image doesn't have the test yang models or any data in when it launches so the instructions above always init the startup data.

```
sysrepocfg --import=../init-data/integrationtest.xml --format=xml --datastore=running integrationtest
```

**NOTE:** sysrepo does not automatically copying running configuration into startup configuration.


## Getting Data

An alternative branch is considering trying to provide a python-object navigation, but at the moment it is required to navigate get xpath nodes explicitly. Sysrepo by default will return `<sysrepo.Val; proxy of <Swig Object of type 'sysrepo::S_Val *' at 0x7fc985bb23f0> >` - however our own `DataAccess` object will convert this to python primitives.

```python
session = datalayer.DataAccess()
session.connect()
value = session.get('/integrationtest:simpleleaf')
```


## Setting Data

Unfortunately setting data requires types, as a covenience the default happens to be a string.

**NOTE:** the commit method from python does not persist running configuration into startup configuration (see - https://github.com/sysrepo/sysrepo/issues/966). It may be we have to sort ourselves out with regards to copying running to startup from time to time.

- SR_UINT32_T 20
- SR_CONTAINER_PRESENCE_T 4
- SR_INT64_T 16
- SR_BITS_T 7
- SR_IDENTITYREF_T 11
- SR_UINT8_T 18
- SR_LEAF_EMPTY_T 5
- SR_DECIMAL64_T 9
- SR_INSTANCEID_T 12
- SR_TREE_ITERATOR_T 1
- SR_CONTAINER_T 3
- SR_UINT64_T 21
- SR_INT32_T 15
- SR_ENUM_T 10
- SR_UNKNOWN_T 0
- SR_STRING_T 17
- SR_ANYXML_T 22
- SR_INT8_T 13
- SR_LIST_T 2
- SR_INT16_T 14
- SR_BOOL_T 8
- SR_ANYDATA_T 23
- SR_UINT16_T 19
- SR_BINARY_T 6


# XPATH based python access

Note: when fetching data we need to provide to provide at least a top-level module prefix, however it is


```python
import datalayer
from datalayer import Types as types
session = datalayer.DataAccess()
session.connect()


session.set("/integrationtest:simpleleaf", "BOO!", types.SR_STRING_T)

value = session.get("/integrationtest:simpleleaf", "BOO!")
print(value)

session.create("/integrationtest:simplelist[simplekey='abc123']")

for item in session.gets("/integrationtest:simplelist"):
  print(item)
  value = session.get(item + "/simplekey")
  print(value)

session.delete("/integrationtest:simpleenum")

session.commit()
```

# Node based python access

**WORKING IN PROGRESS**

```python
import datalayer

session = datalayer.DataAccess()
session.connect()
root = session.get_root('integrationtest')

root.simpleleaf = 'abc'

# Delete of a leaf
root.simpleleaf = None

# Access a leaf inside a container
print(root.morecomplex.leaf3)


session.commit()
```


# Reference:

- https://github.com/sysrepo/sysrepo/blob/master/swig/python/tests/SysrepoBasicTest.py


# TODO:

- enumeration test cases
- underscore conversion
- deletes (of non-primitives)
- choices
