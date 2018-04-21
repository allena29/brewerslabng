.PHONY: unittest

PWD := $(shell pwd)

all:schema unittest

# TODO: remove hardcoding of the ynag file
schema:
	pyang -f yin -o schema.yin brewerslab.yang
	python ../pyconfhoard/PyConfHoardSchema.py --input=schema.yin --output=schema.json 

unittest:
	nose2 -s test -t python -v --with-coverage --coverage-report html
