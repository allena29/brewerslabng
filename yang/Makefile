.PHONY: unittest

PYBIND := $(shell PYTHONPATH=../../confvillain /usr/bin/env python -c 'import pyangbind; import os; print ("{}/plugin".format(os.path.dirname(pyangbind.__file__)))')
PWD := $(shell pwd)

all:	pybindtest unittest

pybindtest:
	PYTHONPATH=$(PYTHONPATH):../pyconfhoard pyang --plugindir $(PYBIND) -p ../../confvillain --use-xpathhelper -f pybind -o binding.py brewerslab.yang

unittest:
	nose2 -s test -t python -v --with-coverage --coverage-report html
