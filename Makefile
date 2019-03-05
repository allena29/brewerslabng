.PHONY: unittest

all: crux-recompile lint unittest

everything:
	rm -fr .cache
	make all

crux-compile:
	touch yang
	bash ./cruxcompile "integrationtest"

crux-recompile:
	bash ./cruxcompile "integrationtest"

unittest:
	test/run-unit.sh

lint:
	test/run-lint.sh
