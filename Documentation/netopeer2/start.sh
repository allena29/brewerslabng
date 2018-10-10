#!/bin/bash

cd /
tar cvpf /tmp/sysrepo.tar sysrepo
rm -fr /sysrepo
mkdir -p /brewerslabng/persist/sysrepo
ln -s /brewerslabng/persist/sysrepo /sysrepo
tar xvf /tmp/sysrepo.tar
rm -fr /tmp/sysrepo.tar

sysrepod
sysrepo-plugind
netopeer2-server

mkdir /logs

echo "install yang"
cd /brewerslabng/yang
for yang in *.yang
do
  echo "... $yang"
  sysrepoctl --install --yang=$yang 2>/logs/$yang.sysrepo.install
done

echo "Start brewerslab subscriber"
cd /brewerslabng/providers
for provider in *.py
do
  echo "... $provider"
  screen -dmS provider$provider python3 $provider
done


echo "Import startup configuration"
cd /brewerslabng/init-data
for xml in *.xml
do  
  module=`echo "$xml" | sed -e 's/\.xml//'`
  echo "... $module"
  sysrepocfg --import=$xml --format=xml --datastore=startup $module
done

while true; do
sleep 10
done


