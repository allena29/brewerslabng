.PHONY: unittest cli


wall: cli unittest

cli: 
	$(MAKE) -C cli

unittest:
	pyang -f yin -o test/tester.yin test/tester.yang 
	python yin2json.py --input=test/tester.yin --output=test/schema.json
	nose2 -s test -t python3 -v --with-coverage --coverage-report html
