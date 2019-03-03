.PHONY: unittest

all: crux-compile unittest

crux-compile:
	bash ./cruxcompile "integrationtest" 

unittest:
	test/run-unit.sh
