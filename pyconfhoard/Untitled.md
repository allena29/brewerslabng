lua5.3-dev

sudo apt-get install cmocka-dev doxygen


https://github.com/CESNET/libyang.git
cd libyang
git checkout v0.14-r1
mkdir build
cd build
cmake ../
make 
sudo make install
sudo ldconfig

git clone http://git.libssh.org/projects/libssh.git
cd libssh
git checkout e005fd310f614fdedc1f5ac69843d5d41acf0b42
cd build
sh build_make.sh
make 
sudo make install
sudo ldconfig

https://github.com/CESNET/libnetconf2.git
cd libnetconf2
git checkout v0.10-r1
mkdri build
cd build
cmake ..
make
sudo make install
sudo ldconfig

sudo apt-get install libprotobuf-dev libprotoc-dev

git clone https://github.com/sysrepo/sysrepo.git
cd sysrepo
mkdir build
git checkout v0.7.2
cd build
cmake ..
make
sudo make install
sudo ldconfig
