.PHONY: unittest

all: crux-compile lint unittest

everything:
	rm -fr .cache
	make all

crux-compile:
	bash ./cruxcompile "integrationtest" 

unittest:
	test/run-unit.sh

lint:
	test/run-lint.sh
