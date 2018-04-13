.PHONY: unittest


all:	unittest

unittest:
	PYTHONPATH=../../yang:../../pyconfhoard:$(PYTHONPATH) nose2 -s test -t python -v --with-coverage --coverage-report html
