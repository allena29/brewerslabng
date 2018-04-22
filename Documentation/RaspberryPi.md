# BrewerslabNG with Raspberry Pi 3B+

 

# stretch - 2018-03

This version of raspbian has been the most frustrating to setup, I found it impossible to setup headless. It was frustrating to find how to get rfkill to persist it's settings once unblocked (already annoyed at having to drag out a monitor and keyboard!)

*/etc/wpa_supplicant/wpa_supplicant.conf*

```
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
	ssid="wellingtonboots"
	psk="passwordhere"
}
```

*/etc/dhcpcd.conf*

In recent versions of Raspbian dhcpcd must be used to set static IP addresses rather than the more traditional /etc/network/interfaces.


*/etc/rc.local*

This is a kludge.

```bash
echo "rfkill unblock all >/tmp/rkill" >>/etc/rc.local
```


*Update rpasberrypi firmware*

```bash
sudo rpi-update
sudo reboot
sudo apt-get update
sudo apt-get upgrade
```


## Basic Packages

```bash
sudo apt-get update
sudo apt-get install git-core mlocate vim cmake autoconf automake libtool screen
```

## Development Packages

```bash
sudo apt-get install libpcre2-dev flex bison libpcre3 libpcre3-dev libssl-dev
sudo apt-get install libev-dev libavl-dev python-dev swig libxml2-dev libxslt1-dev
sudo apt-get install libsodium-dev libffi-dev lua5.1-dev
sudo apt-get install raspberrypi-kernel-headers libboost-dev python3-dev 
sudo apt-get install ctags vim-python-jedi libsqlite3-dev
```



# beerng user

Add a user, throughout this respository this will be referred to as **beerng**. 

```bash
mkdir /home/beerng
useradd beerng -s /bin/bash
chown beer:beerng /home/beerng
```


## Python environment

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
PATH=~/.pyenv/bin:$PATH
eval "$(pyenv init -)"
export PYENV_ROOT="$HOME/.pyenv"
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
pyenv install 3.6.5
eval "$(pyenv virtualenv-init -)"
pyenv virtualenv 3.6.5 brewerslabng


cat <<'EOF' >> ~/.bashrc
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF
```

### Get this repository and install python libraries

```bash
git clone https://github.com/allena29/brewerslabng.git
cd brewerslabng
pip install -r requirements.txt
```

### Optional VIM Enhancements

```bash
git clone https://github.com/AdamWhittingham/vim-config.git ~/.vim && ~/.vim/install
```
