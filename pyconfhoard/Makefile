.PHONY: unittest cli rest schema schema-quiet


wall: schema-quiet cli rest unittest

cli: 
	$(MAKE) -C cli

rest:
	$(MAKE) -C cli

schema:
	pyang -f yin -o test/tester.yin test/tester.yang 
	pyang -f tree -o test/tester.txt test/tester.yang
	python PyConfHoardSchema.py --input=test/tester.yin --output=test/schema.json
	cp test/schema.json test/example-schema.json
	cp test/schema-oper.json test/example-schema-oper.json
	cp test/schema-config.json test/example-schema-config.json

schema-quiet:
	pyang -f yin -o test/tester.yin test/tester.yang 
	pyang -f tree -o test/tester.txt test/tester.yang
	python PyConfHoardSchema.py --input=test/tester.yin --output=test/schema.json --quiet
	cp test/schema.json test/example-schema.json
	cp test/schema-oper.json test/example-schema-oper.json
	cp test/schema-config.json test/example-schema-config.json

unittest: 
	# nose2 -s test -t python3 -v --with-coverage --coverage-report html
	PYTHONPATH=../:$(PYTHONPATH) python -m unittest discover test
#	coverage html -i

