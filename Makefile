.PHONY: unittest

all: crux-compile lint unittest

crux-compile:
	bash ./cruxcompile "integrationtest" 

unittest:
	test/run-unit.sh

lint:
	test/run-lint.sh
