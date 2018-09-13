import sys
import re


field=re.compile("^\s*([a-zA-Z0-9_]*).*=\S*\s*$")

fields=[]
y=sys.stdin.readline()
while y != "":

	x= field.sub('\g<1>',y)
	
	if y.count("StringProperty"):	
		z="string"
	elif y.count("TextProperty"):
		z="text"
	elif y.count("IntegerProperty"):	
		z="int"
	elif y.count("BooleanProperty"):		
		z="bool"
	elif y.count("FloatProperty"):		
		z="float"
	elif y.count("StringListProperty"):
		z="stringlist"
		print "%s is a String List Property\n"
	else:
		if len(y) > 5:
			print "unsupported type",y
			sys.exit(1)

	if len(x) > 2:	fields.append((x,z))
	y=sys.stdin.readline()

sys.stdout.write("\t\tself.response.out.write(\"DROP TABLE IF EXISTS `%s`;\\n\")\n" %(sys.argv[1]))
sys.stdout.write("\t\tself.response.out.write(\"CREATE TABLE %s (entity int not null AUTO_INCREMENT " %(sys.argv[1]))
c=","
for (x,z) in fields:
	sys.stdout.write(c)
	sys.stdout.write("%s " %(x))
	if z == "text":
		sys.stdout.write("text")
	if z == "stringlist":
		sys.stdout.write("text")
	if z == "string":
		sys.stdout.write("char(255)")
	if z == "int":
		sys.stdout.write("int ")
	if z == "bool":
		sys.stdout.write("boolean ")
	if z == "float":
		sys.stdout.write("float ")
sys.stdout.write(", PRIMARY KEY(entity) );\\n\")\n")


sys.stdout.write("\t\trecords=db.GqlQuery(\"SELECT * FROM %s\")\n" %(sys.argv[1]))
sys.stdout.write("\t\tfor r in records.fetch(345345345):\n")

for (x,z) in fields:
	if z == "stringlist":
		sys.stdout.write("\t\t\tif not r.%s:	r.%s=[]\n" %(x,x))
	if z == "string":
		sys.stdout.write("\t\t\tif not r.%s:	r.%s=\"\"\n" %(x,x))
	if z == "int":
		sys.stdout.write("\t\t\tif not r.%s:	r.%s=0\n" %(x,x))
	if z == "float":
		sys.stdout.write("\t\t\tif not r.%s:	r.%s=0.0\n" %(x,x))
	if z == "bool":
		sys.stdout.write("\t\t\tif not r.%s:\n" %(x))
		sys.stdout.write("\t\t\t\t%s = 0\n" %(x))
		sys.stdout.write("\t\t\telse:\n")
		sys.stdout.write("\t\t\t\t%s = 1\n" %(x))
sys.stdout.write("\")\n\n")

c=","
sys.stdout.write("\t\t\tself.response.out.write(\"INSERT INTO %s VALUES (null " %(sys.argv[1]))
for (x,z) in fields:
	sys.stdout.write(c)
	if z == "string" or z == "stringlist" :
		sys.stdout.write("'%s' ")
	else:
		sys.stdout.write("%s ")


c=""
sys.stdout.write(");\\n\" %(")
for (x,z) in fields:
	sys.stdout.write(c)
	if z == "bool":
		sys.stdout.write("%s " %(x))
	elif z == "stringlist":
		sys.stdout.write(" self.escape_string(json.dumps(r.%s)) " %(x)) 
	else:
		sys.stdout.write(" self.escape_string(r.%s) " %(x))
	c=","
sys.stdout.write("))\n")


