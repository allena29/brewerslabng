.PHONY: unittest cli


wall: cli schema unittest

cli: 
	$(MAKE) -C cli

schema:
	pyang -f yin -o test/tester.yin test/tester.yang 
	pyang -f tree -o test/tester.txt test/tester.yang
	python yin2json.py --input=test/tester.yin --output=test/schema.json
	cp test/schema.json test/example-schema.json

unittest: 
	nose2 -s test -t python3 -v --with-coverage --coverage-report html
