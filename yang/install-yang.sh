#!/bin/bash

set -euo pipefail

cd /brewerslabng/yang
for yang in *.yang
do
  echo "... $yang"
  sysrepoctl --install --yang=$yang
done

