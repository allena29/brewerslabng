#!/bin/bash

set -euo pipefail

echo "Start subscribers"
for provider in *.py
do
  echo "... $provider"
  screen -dmS provider$provider python3 $provider
done
