#!/bin/bash

if [ "$1" = "" ]
then
	datastore="startup"
else
	datastore="running"
fi

set -euo pipefail

echo "Import $datastore configuration"
for xml in *.xml
do  
  module=`echo "$xml" | sed -e 's/\.xml//'`
  echo "... $module"
  sysrepocfg --import=$xml --format=xml --datastore=$datastore $module
done


