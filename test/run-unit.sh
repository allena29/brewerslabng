#!/bin/bash

curdir=`pwd`
PYTHONPATH="$curdir/blng:$curdir/test/unit/:$PYTHONPATH"   nose2 -s test/unit -t python --verbose --with-coverage --coverage-report html
