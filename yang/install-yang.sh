#!/bin/bash

set -euo pipefail

for yang in *.yang
do
  echo "... $yang"
  sysrepoctl --install --yang=$yang
done

