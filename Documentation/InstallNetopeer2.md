# Install Libraries


# libyang

```bash
git clone https://github.com/CESNET/libyang.git
cd libyang; mkdir build; cd build
cmake ..
make
sudo make install
```

# libssh

```bash
git clone git://git.libssh.org/projects/libssh.git
cd libssh
mkdir build; cd build
cmake ..
make
sudo make install
```

# libnetconf2

```bash
git clone https://github.com/CESNET/libnetconf2.git
cd libnetconf2
mkdir build; cd build
cmake ..
make
sudo make install
```

# Google protocol buffers

```bash
git clone https://github.com/google/protobuf.git
cd protobuf
./autogen.sh
./configure
make
sudo make install
sudo ldconfig
```

# Protobuf - C bindings

(https://github.com/protobuf-c/protobuf-c/issues/320)

```bash
sudo apt-get install libboost-all-dev
git clone https://github.com/protobuf-c/protobuf-c.git
cd protobuf-c
./autogen.sh && ./configure --prefix=/usr
make
sudo make install
```


# Sys repo

Note: the python bindings should be installed into the virtualenv

```bash
mkdir /home/beerng/repository
mkdir build_python3
cd build_python3
cmake -DIS_DEVELOPER_CONFIGURATION=OFF -DGEN_PYTHON_VERSION=3.6.5 -DPYTHON_INCLUDE_DIR=~/.pyenv/versions/3.6.5/include/python3.6m -DPYTHON_INCLUDE_DIR2=~/.pyenv/versions/3.6.5/include/python3.6m -DPYTHON_LIBRARY=~/.pyenv/versions/3.6.5/lib/libpython3.6m.a -D python_version=3 ..
make -j2
sudo make install
sudo ldconfig
```

Note: the library was insteadd to `/usr/lib/python3.5/site-packages` copying this to the `~/.pyenv/versions/3.6.5/envs/brewerslabng/lib/python3.6/site-packages/` was the quickest way to get started.

At the end of this install we should have `/etc/sysrepo/yang` and `/etc/sysrepo/data` populated.


# Netopeer2

Unfortunately with Netopeer2 when connectivity via SSH the daemon dies a horrible death with a segmentation fault.

```bash
git clone https://github.com/CESNET/Netopeer2.git
git checkout v0.4-r2
cd keystore
mkdir build
cmake ..
make
sudo make install
sudo ldconifg

# cd ~/Netopeer2
cd server
mkdir build
cd build
cmake ..
make
sudo make install

cd ../../cli
cmake ..
make
sudo make install
```

