.PHONY: unittest


all:schema unittest

schema:
	pyang -f yin -o test/tester.yin ../test/tester.yang 
	python ../yin2json.py --input=test/tester.yin --output=test/schema.json

unittest:
	nose2 -s test -t python3 -v --with-coverage --coverage-report html
