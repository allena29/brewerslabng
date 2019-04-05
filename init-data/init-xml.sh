#!/bin/bash

set -euo pipefail

echo "Import startup configuration"
for xml in *.xml
do  
  module=`echo "$xml" | sed -e 's/\.xml//'`
  echo "... $module"
  sysrepocfg --import=$xml --format=xml --datastore=startup $module
done


