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



# Reference:

- https://github.com/sysrepo/sysrepo/blob/master/swig/python/tests/SysrepoBasicTest.py
