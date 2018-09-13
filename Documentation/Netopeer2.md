# Getting started with Docker

[sysrepod](http://www.sysrepo.org/static/doc/html/user_guidelines.html) - is the key yang datastore which depends on libyang.
[Netopeer2](https://github.com/CESNET/Netopeer2) provides the NETCONF server but neither provide a compelling CLI.


```bash
docker build -t netopeer .

docker run -p 830:830 -i -d netopeer:latest  /bin/bash


docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED              STATUS              PORTS                  NAMES
ebab1b300b45        netopeer:latest     "bash"              About a minute ago   Up About a minute   0.0.0.0:830->830/tcp   hardcore_kare


docker exec -i -t <CONTAINERID> /bin/bash
```

Running sysrepo/netopeer in debug mode

```
sysrepod -d -l 4 
netopeer2-server -d -v 4
```

And we should be able to then run netconf in docker

```
ssh -lnetconf -p 830 127.0.0.1 -s netconf
```



# Basic Test or Sysrepod and Netopeer

```

Create a file basic.json - This is [Documentation/example-netopeer/basic.json](Documentation/example-netopeer/basic.json)

```json
{
	"test:test": {
		"hello": "world!"
	}
}
```

### The initial yang file

This is [Documentation/example-netopeer/test.yang](Documentation/example-netopeer/test.yang)


```json
module test {
  namespace "http://test.com";
  prefix test;

  container test {
    leaf hello {
      type string;
      default world;
    }
  }

}
```

### Install yang

```bash
sudo sysrepoctl --install --yang=test.yang
sysrepocfg --import=basic.json --format=json --datastore=startup test
```


### Hello

```
 netconf-console   --debug --user beerng --password beerng --port 830  --host 192.168.1.183 --hello
<nc:hello xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <nc:capabilities>
    <nc:capability>urn:ietf:params:netconf:base:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:base:1.1</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:writable-running:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:candidate:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:rollback-on-error:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:validate:1.1</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:startup:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:xpath:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:with-defaults:1.0?basic-mode=explicit&amp;also-supported=report-all,report-all-tagged,trim,explicit</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:notification:1.0</nc:capability>
    <nc:capability>urn:ietf:params:netconf:capability:interleave:1.0</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-yang-metadata?module=ietf-yang-metadata&amp;revision=2016-08-05</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:1?module=yang&amp;revision=2017-02-20</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-inet-types?module=ietf-inet-types&amp;revision=2013-07-15</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-yang-types?module=ietf-yang-types&amp;revision=2013-07-15</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-yang-library?revision=2018-01-17&amp;module-set-id=20</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-netconf-acm?module=ietf-netconf-acm&amp;revision=2012-02-22</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netconf:base:1.0?module=ietf-netconf&amp;revision=2011-06-01&amp;features=writable-running,candidate,rollback-on-error,validate,startup,xpath</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-netconf-notifications?module=ietf-netconf-notifications&amp;revision=2012-02-06</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netconf:notification:1.0?module=notifications&amp;revision=2008-07-14</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:netmod:notification?module=nc-notifications&amp;revision=2008-07-14</nc:capability>
    <nc:capability>http://example.net/turing-machine?module=turing-machine&amp;revision=2013-12-27</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-interfaces?module=ietf-interfaces&amp;revision=2014-05-08</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:iana-if-type?module=iana-if-type&amp;revision=2014-05-08</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-ip?module=ietf-ip&amp;revision=2014-06-16</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-netconf-with-defaults?module=ietf-netconf-with-defaults&amp;revision=2011-06-01</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring?module=ietf-netconf-monitoring&amp;revision=2010-10-04</nc:capability>
    <nc:capability>urn:ietf:params:xml:ns:yang:ietf-x509-cert-to-name?module=ietf-x509-cert-to-name&amp;revision=2014-12-10</nc:capability>
    <nc:capability>http://test.com?module=test</nc:capability>
  </nc:capabilities>
</nc:hello>
```


### Check Schema

```
netconf-console --user beerng --password beerng --port 830  --host 192.168.1.183 --get-schema test
<data xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">module test {
  namespace "http://test.com";
  prefix test;

  container test {
    leaf hello {
      type string;
      default "world";
    }
  }
}
</data>
```


### Get config from startup

Pay ttention to the bottom bit with the `<test>` stanza.


```
[I] git:sysrepo-attempt2 🌒  🌔  ~/brewerslabng $ netconf-console   --debug --user beerng --password beerng --port 830  --host 192.168.1.183 --get-config --db startup
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
  <turing-machine xmlns="http://example.net/turing-machine">
    <transition-function>
      <delta>
        <label>left summand</label>
        <input>
          <state>0</state>
          <symbol>1</symbol>
        </input>
      </delta>
      <delta>
        <label>separator</label>
        <input>
          <state>0</state>
          <symbol>0</symbol>
        </input>
        <output>
          <state>1</state>
          <symbol>1</symbol>
        </output>
      </delta>
      <delta>
        <label>right summand</label>
        <input>
          <state>1</state>
          <symbol>1</symbol>
        </input>
      </delta>
      <delta>
        <label>right end</label>
        <input>
          <state>1</state>
          <symbol/>
        </input>
        <output>
          <state>2</state>
          <head-move>left</head-move>
        </output>
      </delta>
      <delta>
        <label>write separator</label>
        <input>
          <state>2</state>
          <symbol>1</symbol>
        </input>
        <output>
          <state>3</state>
          <symbol>0</symbol>
          <head-move>left</head-move>
        </output>
      </delta>
      <delta>
        <label>go home</label>
        <input>
          <state>3</state>
          <symbol>1</symbol>
        </input>
        <output>
          <head-move>left</head-move>
        </output>
      </delta>
      <delta>
        <label>final step</label>
        <input>
          <state>3</state>
          <symbol/>
        </input>
        <output>
          <state>4</state>
        </output>
      </delta>
    </transition-function>
  </turing-machine>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>eth0</name>
      <description>Ethernet 0</description>
      <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <address>
          <ip>192.168.2.100</ip>
          <prefix-length>24</prefix-length>
        </address>
      </ipv4>
    </interface>
    <interface>
      <name>eth1</name>
      <description>Ethernet 1</description>
      <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:ethernetCsmacd</type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <enabled>true</enabled>
        <mtu>1500</mtu>
        <address>
          <ip>10.10.1.5</ip>
          <prefix-length>16</prefix-length>
        </address>
      </ipv4>
    </interface>
  </interfaces>
  <test xmlns="http://test.com">
    <hello>world!</hello>
  </test>
</data>
```


# Python binding test

Run this with `test` as the first argument. If we don't have something to implement the call-backs then the netconf query will fail.

This is [Documentation/example-netopeer/x.py](Documentation/example-netopeer/x.py)

```python
#!/usr/bin/env python

__author__ = "Mislav Novakovic <mislav.novakovic@sartura.hr>"
__copyright__ = "Copyright 2016, Deutsche Telekom AG"
__license__ = "Apache 2.0"

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import libsysrepoPython3 as sr
import sys

# Function to print current configuration state.
# It does so by loading all the items of a session and printing them out.
def print_current_config(session, module_name):
    select_xpath = "/" + module_name + ":*//*"

    values = session.get_items(select_xpath)

    for i in range(values.val_cnt()):
        print(values.val(i).to_string(), end=" ")

# Function to be called for subscribed client of given session whenever configuration changes.
def module_change_cb(sess, module_name, event, private_ctx):
    print("\n\n ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========\n")

    print_current_config(sess, module_name)

    return sr.SR_ERR_OK

# Notable difference between c implementation is using exception mechanism for open handling unexpected events.
# Here it is useful because `Conenction`, `Session` and `Subscribe` could throw an exception.
try:
    module_name = "ietf-interfaces"
    if len(sys.argv) > 1:
        module_name = sys.argv[1]
    else:
        print("\nYou can pass the module name to be subscribed as the first argument")

    # connect to sysrepo
    conn = sr.Connection("example_application")

    # start session
    sess = sr.Session(conn)

    # subscribe for changes in running config */
    subscribe = sr.Subscribe(sess)

    subscribe.module_change_subscribe(module_name, module_change_cb, None, 0, sr.SR_SUBSCR_DEFAULT | sr.SR_SUBSCR_APPLY_ONLY)

    print("\n\n ========== READING STARTUP CONFIG: ==========\n")
    try:
        print_current_config(sess, module_name)
    except Exception as e:
        print (e)

    print("\n\n ========== STARTUP CONFIG APPLIED AS RUNNING ==========\n")

    sr.global_loop()

    print("Application exit requested, exiting.\n")

except Exception as e:
    print (e)
```

# Using NCS to build a 'Network Element Driver'

Note: NCS/NSO is the commerical Tail-F/Cisco version of Conf-D which comes with full CLI, Java and Python bindings. [Pionner](https://github.com/NSO-developer/pioneer/) is a package to build NETCONF NED's which relies of python. [Conf-D](http://www.tail-f.com/confd-basic/) has a basic version (with crippled CLI, no Java, no Python) - if that was available for ARM architecture I wouldn't care about playing with Sysrepo.

```
set devices authgroups group beerng default-map
set devices authgroups group beerng default-map remote-name beerng
set devices authgroups group beerng default-map remote-password beerng
set devices device galaxy address 192.168.1.183
set devices device galaxy authgroup beerng
set devices device galaxy device-type netconf
set devices device galaxy state admin-state unlocked
commit
request devices fetch-ssh-keys device galaxy
```

Build the netconf module

```
admin@ncs> request devices device galaxy pioneer yang show-list
disabled ===== DISABLED =====
ietf-netconf-with-defaults
ietf-yang-types
iana-if-type
ietf-netconf
ietf-ip
ietf-netconf-monitoring
turing-machine
yin
notifications
ietf-netconf-notifications
ietf-x509-cert-to-name
nc-notifications
ietf-interfaces
ietf-inet-types
yang
ietf-datastores
ietf-yang-metadata
ietf-netconf-acm
ietf-yang-library
marked ===== MARKED =====
test

request devices device galaxy pioneer yang download
request devices device galaxy pioneer yang build-netconf-ned
request devices device galaxy pioneer yang install-netconf-ned
request packages reload

[ok][2018-09-12 23:41:10]
admin@ncs> request devices device galaxy sync-from
result true
[ok][2018-09-12 23:41:14]
admin@ncs> show configuration devices device galaxy config
test:test {
    hello "world!";
}

admin@ncs% set devices device galaxy config test:test hello BOO!!!
[ok][2018-09-12 23:41:39]

[edit]
admin@ncs% commit
Commit complete.
[ok][2018-09-12 23:41:40]

[edit]
admin@ncs%
```

When the config changes we see this 

```
 ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========

/test:test/hello = BOO!
```

```
admin@ncs> request devices device galaxy pioneer netconf get-config
get-config-reply <?xml version="1.0"?>
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1">
  <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    <test xmlns="http://test.com">
      <hello>world!</hello>
    </test>
  </data>
</rpc-reply>
```


### Changing YANG


Update the yang to add some leaves


This is [Documentation/example-netopeer/test.yang.updated](Documentation/example-netopeer/test.yang.updated)

```
module test {
  namespace "http://test.com";
  prefix test;

  container test {
    leaf hello {
      type string;
      default world;
    }

    leaf thinking {
      type string;
      config false;
    }

    leaf service {
      type string;
    }
  }

}
```

Update it

```
stop sysrepod
stop netorepod
sudo sysrepoctl --install --yang=test.yang
start sysrepod
start netropd

netconf-console   --debug --user beerng --password beerng --port 830  --host 192.168.1.183 --get-schema test
<data xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">module test {
  namespace "http://test.com";
  prefix test;

  container test {
    leaf hello {
      type string;
      default "world";
    }

    leaf thinking {
      type string;
      config false;
    }

    leaf service {
      type string;
    }
  }
}
</data>


```

modify config with NCS

```
netconf-console   --debug --user beerng --password beerng --port 830  --host 192.168.1.183 --edit-config test.xml

<nc:ok xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0"/>

```

and we should see the changes in the subscriber

```


 ========== CONFIG HAS CHANGED, CURRENT RUNNING CONFIG: ==========

/test:test/hello = BOO!!!RADLEY
 /test:test/service = abc

```


And in NCS NED trace we see the new leaf

```

<<<<in 13-Sep-2018::00:25:29.653 device=galaxy session-id=4
<rpc-reply xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="1"><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"><test xmlns="http://test.com"><hello>BOO!!!RADLEY</hello><service>abc</service></test></data></rpc-reply>
```


Pioneer to update the NED

```
admin@ncs> request devices device galaxy pioneer yang delete name-pattern test
success Deleting module test

[ok][2018-09-13 00:27:45]
admin@ncs> request devices device galaxy pioneer yang download include-names test
Downloading 1 modules to /tmp/download/galaxy
1/1 Downloading module test  -- succeeded
message Downloaded 1 modules, failed 0, skipped 0:
Downloaded test

yang-directory /tmp/download/galaxy
[ok][2018-09-13 00:27:48]

admin@ncs> request devices device galaxy pioneer yang build-netconf-ned
Cleaning up existing ned-directory
Starting build of 1 YANG modules, this may take some time
PATH=/opt/ncs/ncs-4.5.5.1/bin:/usr/bin:/usr/local/Cellar/pyenv/1.2.3/libexec:/Users/adam/.pyenv/plugins/python-build/bin:/Users/adam/.pyenv/plugins/pyenv-virtualenv/bin:/opt/ncs/ncs-4.5.5.1/lib/ncs/erts/bin:/opt/ncs/ncs-4.5.5.1/lib/ncs/bin:/opt/ncs/ncs-4.5.5.1/bin:/Users/adam/.pyenv/shims:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/X11/bin:/usr/local/go/bin:/Applications/Wireshark.app/Contents/MacOS ncs-make-package --verbose --netconf-ned /tmp/download/galaxy galaxy --dest /tmp/packages/galaxy --no-java
Wrote package to /tmp/packages/galaxy
make clean fxs -C /tmp/packages/galaxy/src NCSC=/opt/ncs/ncs-4.5.5.1/bin/ncsc --verbose
rm -rf ncsc-out ../load-dir
cd ../netsim && /Library/Developer/CommandLineTools/usr/bin/make clean || true
mkdir -p ncsc-out
mkdir -p ../load-dir
/opt/ncs/ncs-4.5.5.1/bin/ncsc --verbose --ncs-compile-bundle yang                        \
                 --ncs-device-dir ncsc-out   \
                 --ncs-device-type netconf            \
                  &&                          \
        cp ncsc-out/modules/fxs/*.fxs ../load-dir;
yanger -p yang:/opt/ncs/ncs-4.5.5.1/src/ncs/yang --no-deviation-apply -t ncs -f yang yang/test.yang -o augmented/test.yang
Generating .fxs file "augmented/test.fxs"
COPY augmented/test.fxs  /private/tmp/packages/galaxy/src/ncsc-out/modules/revisions/test/norev/test.fxs
COPY augmented/test.yang  /private/tmp/packages/galaxy/src/ncsc-out/modules/revisions/test/norev/test.yang
COPY yang/test.yang  /private/tmp/packages/galaxy/src/ncsc-out/modules/revisions/test/norev/test.yang.orig
Module "test" revision "norev" added
SYMLINK ../revisions/test/norev/test.fxs  /private/tmp/packages/galaxy/src/ncsc-out/modules/fxs/test.fxs
SYMLINK ../revisions/test/norev/test.yang  /private/tmp/packages/galaxy/src/ncsc-out/modules/yang/test.yang
for f in `echo ../load-dir/*.fxs`; do \
           n=`basename $f | sed 's/\.fxs//'` || exit 1; \
        done
touch -m ncsc-out/.done
Build complete. Run install-netconf-ned, then run 'packages reload' to use the packagened-directory /tmp/packages/galaxy
[ok][2018-09-13 00:28:04]
admin@ncs> request devices device galaxy pioneer yang install-netconf-ned
Old package exists, moving to /Users/adam/pioneer/old-packages/galaxy-20180912-234009
Copying new package into /Users/adam/pioneer/packages/galaxy
success Installed -- now you need to: packages reload
[ok][2018-09-13 00:28:19]
admin@ncs> request packages reload

>>> System upgrade is starting.
>>> Sessions in configure mode must exit to operational mode.
>>> No configuration changes can be performed until upgrade has completed.
>>> System upgrade has completed successfully.
reload-result {
    package galaxy
    result true
}
reload-result {
    package pioneer
    result true
}
```

Now we can sync-from and get the new leavs

```
admin@ncs> request devices device galaxy sync-from
result true
[ok][2018-09-13 00:28:39]
admin@ncs> show configuration devices device galaxy config
test:test {
    hello   "BOO!!!RADLEY";
    service abc;
}
```


---

---





# Old Notes.... Sys Repo Setup 

Raspbian/Debian based machine

```bash
sudo apt-get install libtool libtool-bin libxml2-dev libxslt1-dev libcurl4-openssl-dev xsltproc python-setuptools cmake zlib1g-dev libssl-dev pkg-config libreadline-dev python-libxml2  libprotobuf-dev libprotobuf-java protobuf-c-compiler doxygen-dbg
```


## pyang (cca321ef0c6ddf82c77c12aca8301bcfdfd5b7d3)

```bash
git clone https://github.com/mbj4668/pyang.git
cd pyang
sudo python setup.py install
```


## Libssh (983d1189d08436ba818b591d7a0185927758349c)

```bash
git clone https://git.libssh.org/projects/libssh.git libssh
cd libssh
mkdir build
cd build
cmake ..
make 
sudo make install
cd ..
```   
   
   
## Libnetconf 0.11.48 (54ba1c7a1dbd85f3e700c1629ced8e4b52bac4ec)

```
git clone https://github.com/CESNET/libnetconf.git 
cd libnetconf
./configure
make
sudo make install
``` 


## Libyang 0.15.166 (85d09f3bdf5ea01ea2e01deb384b2b0dde057e3f)
 

```bash
git clone https://github.com/CESNET/libyang.git
cd libyang
mkdir build
cmake ..
make
sudo  make install
```
 
 
## Libnetconf2 0.11.48 (cca321ef0c6ddf82c77c12aca8301bcfdfd5b7d3)


```bash
git clone https://github.com/CESNET/libnetconf2.git
cd libnetconf2
mkdir build
cd build
cmake ..
make
sudo make install
```

## Protobuf ff3891dab1b1f462d90a68666d14f57eb5fea34f

This may be redundant as we used apt-get to install protobuf stuff
 
```bash
git clone https://github.com/protocolbuffers/protobuf.git
cd protobuf
git submodule update --init --recursive
sh autogen.sh
./configure
make			(slow)
sudo make install
sudo ldconfig
```

## Protobuf-c 1.3.0 (dac1a65feac4ad72f612aab99f487056fbcf5c1a)


```bash
git clone https://github.com/protobuf-c/protobuf-c.git
cd protobuf-c
sh autogen.sh
# ./configure --disable-protoc <-- but this is a problem
# Think in the end we did 
./configure
make
sudo make install
sudo ldconfig
```
 
 ## Sysrepo (724a62fa830df7fcb2736b1ec41b320abe5064d2)
 

```bash
git clone https://github.com/sysrepo/sysrepo.git
cd sysrepo
mkdir build
cd build
cmake ..
make 
sudo make install
sudo ldconfig
```

## Netopeer2 0.5.31 (d3ae5423847cbfc67c844ad19288744701bd47a4) 


```bash
git clone https://github.com/CESNET/Netopeer2.git
cd Netopeer2/server
mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig
cd ../client
mkdir build
cd build
cmake ..
make
```




