.PHONY: unittest


all: unittest

unittest:
	PYTHONPATH=../:$(PYTHONPATH) python -m unittest discover test
	coverage html -i
