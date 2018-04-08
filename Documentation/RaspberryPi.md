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
	psk="rubberBAGGY6000"
}
```


*/etc/rc.local*

This is a kludge.

```
rfkill unblock all >/tmp/rkill
```


*Update rpasberrypi firmware*

```
sudo rpi-update
sudo reboot
sudo apt-get update
sudo apt-get upgrade
```


## Basic Packages

```
sudo apt-get update
sudo apt-get install git-core mlocate vim cmake autoconf automake libtool screen
```

## Development Packages

```
apt-get install libpcre2-dev flex bison libpcre3 libpcre3-dev libssl-dev libev-dev libavl-dev python-dev swig libxml2-dev libxslt1-dev libsodium-dev libffi-dev lua5.1-dev
sudo apt-get install raspberrypi-kernel-headers libboost-dev python3-dev
```


# beerng user

Add a user, throughout this respository this will be referred to as **beerng**. 

```
mkdir /home/beerng
useradd beerng -s /bin/bash
chown beer:beerng /home/beerng
```


## Python environment

```
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
