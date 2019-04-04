#!/bin/bash

curdir=`pwd`
NEW_PYTHON_PATH="$curdir/blng:$curdir/test/unit/:$PYTHONPATH"  

set -euo pipefail
IFS=$'\n\t'

PYTHONPATH="$NEW_PYTHON_PATH" nose2 -s test/integration -t python --verbose --with-coverage --coverage-report html
