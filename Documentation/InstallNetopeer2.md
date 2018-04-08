# Insta


# libyang

```
git clone https://github.com/CESNET/libyang.git
cd libyang; mkdir build; cd build
cmake ..
make
sudo make install
```

# libssh

```
git clone git://git.libssh.org/projects/libssh.git
cd libssh
mkdir build; cd build
cmake ..
make
sudo make install
```

# libnetconf2

```
git clone https://github.com/CESNET/libnetconf2.git
cd libnetconf2
mkdir build; cd build
cmake ..
make
sudo make install
```

# Google protocol buffers

```
wget https://github.com/google/protobuf/releases/download/v3.5.1/protobuf-all-3.5.1.tar.gz
cd protobuf
./configure
make
sudo make install
sudo ldconfig
```

# Protobuf - C bindings

Note: protobuf bindings for C cannot be compiled until the C++ version is installed.

```
wget https://github.com/protobuf-c/protobuf-c/releases/download/v1.3.0/protobuf-c-1.3.0.tar.gz
./confiugre
make
make install
```


# Sys repo

Note: the python bindings should be installed into the virtualenv

```
git clone https://github.com/sysrepo/sysrepo.git
mkdir build; cd build
cmake ..
make
sudo make install
sudo ldconfig

cd /opt/dev/sysrepo
mkdir build_python3
cd build_python3
cmake -DGEN_PYTHON_VERSION=3 ..
make -j2
make install

```


# Netopeer2

```
git clone https://github.com/CESNET/Netopeer2.git
cd server
cmake .
make
sudo make install
cd ../cli
cmake ..
make
sudo make install
```cd