#!/bin/bash

set -euo pipefail
IFS=$'\n\t'

curdir=`pwd`
pylint blng
