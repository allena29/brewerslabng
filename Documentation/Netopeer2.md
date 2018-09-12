
# Sys Repo Setup 

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




------


Old stuff

```
## Lib
 
 git clone https://github.com/CESNET/netopeer.git
cd netopeer/server



diff --git a/server/configure b/server/configure
index 5036c6b..91ee704 100755
--- a/server/configure
+++ b/server/configure
@@ -2594,7 +2594,7 @@ $as_echo_n "checking for distro... " >&6; }
 { $as_echo "$as_me:${as_lineno-$LINENO}: result: $DISTRO" >&5
 $as_echo "$DISTRO" >&6; }
 case $DISTRO in
-       rhel | redhat | centos | fedora )
+       rhel | redhat | centos | fedora | raspbian )
                # ok, supported distro
                # pkg-config does not check /usr/local/*/pkgconfig, fix it
                PKG_CONFIG_PATH="$PKG_CONFIG_PATH:$expanded_libdir/pkgconfig"
@@ -2978,6 +2978,10 @@ fi
 { $as_echo "$as_me:${as_lineno-$LINENO}: checking for host architecture" >&5
 $as_echo_n "checking for host architecture... " >&6; }
 case $target_cpu in
+    armv7l )
+               { $as_echo "$as_me:${as_lineno-$LINENO}: result: $target_cpu" >&5
+$as_echo "$target_cpu" >&6; }
+               ;;
     i?86 )
                { $as_echo "$as_me:${as_lineno-$LINENO}: result: $target_cpu" >&5
 $as_echo "$target_cpu" >&6; }
 
 
 ./configure
 make
 make install
 sudo make install
 
 
 ---
```
