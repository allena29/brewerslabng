.PHONY: unittest cli

PYBIND := $(shell /usr/bin/env python -c 'import pyangbind; import os; print ("{}/plugin".format(os.path.dirname(pyangbind.__file__)))')

all: cli pybindtest unittest

cli: 
	$(MAKE) -C cli

pybindtest:
	PYTHONPATH=$(PYTHONPATH):./ pyang --plugindir $(PYBIND) --use-xpathhelper -f pybind -o binding.py test/tester.yang

unittest:
	nose2 -s test -t python3 -v --with-coverage --coverage-report html
