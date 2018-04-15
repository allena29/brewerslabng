.PHONY: unittest cli


all: cli pybindtest unittest

cli: 
	$(MAKE) -C cli

unittest:
	 
	nose2 -s test -t python3 -v --with-coverage --coverage-report html
