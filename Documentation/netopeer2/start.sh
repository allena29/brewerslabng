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

while true; do
sleep 10
done


