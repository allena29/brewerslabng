#!/bin/bash

cd /
tar cvpf /tmp/sysrepo.tar sysrepo
rm -fr /sysrepo
mkdir -p /brewerslabng/persist/sysrepo
ln -s /brewerslabng/persist/sysrepo /sysrepo
tar xvf /tmp/sysrepo.tar
rm -fr /tmp/sysrepo.tar

sysrepod
netopeer2-server

echo "install yang"
sysrepoctl --install --yang=/brewerslabng/yang/brewerslab.yang

echo "Start brewerslab subscriber"
cd /brewerslabng/providers
screen -dmS providers python3 brewerslab.py


echo "Import startup configuration"
echo "{}" > /tmp/startup.json
sysrepocfg --import=/tmp/startup.json --format=json --datastore=startup brewerslab

while true; do
sleep 10
done


