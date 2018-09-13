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
	else:
		if len(y) > 5:
			print "unsupported type",y
			sys.exit(1)

	if len(x) > 2:	fields.append((x,z))
	y=sys.stdin.readline()




sys.stdout.write("class %s(db):\n" %(sys.argv[1]))
sys.stdout.write("\n")
sys.stdout.write("\n")
sys.stdout.write("\tdef __init__(self):\n")
sys.stdout.write("\t\tself.entity=None\n")
sys.stdout.write("\t\tself.con=None\n")

for (x,z) in fields:
	if z == "text" or z == "string":
		sys.stdout.write("\t\tself.%s=\"\"\n" %(x))
	if z == "int" or z == "bool":
		sys.stdout.write("\t\tself.%s=0\n" %(x))
	if z == "float":
		sys.stdout.write("\t\tself.%s=0.00\n" %(x))


sys.stdout.write("\t\tself.types = {\n")
for (x,z) in fields:
	sys.stdout.write("\t\t\t'entity' : 'numeric',\n" )
	if z == "stringlist":
		sys.stdout.write("\t\t\t'%s' : 'list',\n" %(x))

	elif z == "text" or z == "string":
		sys.stdout.write("\t\t\t'%s' : 'char',\n" %(x))
	else:
		sys.stdout.write("\t\t\t'%s' : 'numeric',\n" %(x))
sys.stdout.write("\t\t}\n")
sys.stdout.write("\n")

sys.stdout.write("\tdef insertSql(self):\n")
sys.stdout.write("\t\treturn \"INSERT INTO %s VALUES (null" %(sys.argv[1]))
for (x,z) in fields:
	if z == "text" or z == "string" or z=="stringlist":
		sys.stdout.write(", '%s'")
	else:
		sys.stdout.write(", %s")
sys.stdout.write(")\" %(" )
c=""
for (x,z) in fields:
	if z == "stringlist":
		sys.stdout.write("%s _mysql.escape_string( json.dumps(self.%s)) " %(c,x))
	elif z == "string" or z == "text":
		sys.stdout.write("%s _mysql.escape_string(self.%s) " %(c,x))
	else:
		sys.stdout.write("%s self.%s " %(c,x))
	c=","


sys.stdout.write(")\n\n")

sys.stdout.write("\tdef updateSql(self):\n")
sys.stdout.write("\t\treturn \"UPDATE %s SET " %(sys.argv[1]))
c=""
for (x,z) in fields:
	if z == "text" or z == "string" or z == 'stringlist':
		sys.stdout.write("%s %s = '%%s'" %(c,x))
	else:
		sys.stdout.write("%s %s = %%s" %(c,x))
	c=","
sys.stdout.write(" WHERE entity = %s \" %(" )
for (x,z) in fields:
	if z == "stringlist":	
		sys.stdout.write(" _mysql.escape_string(json.dumps( self.%s))," %(x))
	elif z == "string" or z == "text":
		sys.stdout.write(" _mysql.escape_string(self.%s)," %(x))
	else:
		sys.stdout.write(" self.%s," %(x))


sys.stdout.write(" self.entity)\n")


sys.stdout.write("\n\n")

sys.stdout.write("\tdef populate(self,row):\n")
sys.stdout.write("\t\t(( self.entity ")
for (x,z) in fields:
	sys.stdout.write(", self.%s" %(x))
sys.stdout.write("),)=row\n\n")
