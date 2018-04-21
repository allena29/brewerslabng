.PHONY: unittest


all:schema-quiet unittest

schema-quiet:
	pyang -f yin -o test/tester.yin ../test/tester.yang 
	python ../PyConfHoardSchema.py --input=test/tester.yin --output=test/schema.json --quiet

unittest:
	#PYTHONPATH=../:$(PYTHONPATH) nose2 -s test -t python3  -v --with-coverage  --coverage-report html
	PYTHONPATH=../:$(PYTHONPATH) python -m unittest discover test
	coverage html -i
