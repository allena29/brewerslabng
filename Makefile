.PHONY: unittest

all: crux-recompile lint unittest

everything:
	rm -fr .cache
	make all

crux-compile:
	touch yang
	bash ./cruxcompile

crux-recompile:
	bash ./cruxcompile

unittest:
	test/run-unit.sh

lint:
	test/run-lint.sh
