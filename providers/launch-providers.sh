#!/bin/bash

set -euo pipefail

echo "Start providers"
for provider in *.py
do
  echo "... $provider"
  screen -dmS provider$provider python3 $provider
done
