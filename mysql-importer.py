import yangvoodoo
session = yangvoodoo.DataAccess()
session.connect()
root = session.get_root('brewerslab', yang_location='/sysrepo/yang')
root.definitions.fermentables.create('sdf')

import mysql.connector
con = mysql.connector.connect(host='192.168.1.13', database='brewerslab', user='brewerslab', password='beer')
cursor = con.cursor()
query = "select name, hwe, extract, mustMash, isAdjunct from gItems where majorcategory='fermentables' ORDER by name"
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)
    fermentable = root.definitions.fermentables.create(row[0])
    fermentable.hwe = row[1]
    fermentable.extract = row[2]
    fermentable.mash_required = row[4] == True
    fermentable.adjunct = row[3] == True

import mysql.connector
con = mysql.connector.connect(host='192.168.1.13', database='brewerslab', user='brewerslab', password='beer')
cursor = con.cursor()
query = "select name, hopAlpha  from gItems where majorcategory='hops' ORDER by name;"
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)
    hop = root.definitions.hops.create(row[0])
    hop.alpha_acid = row[1]


session.commit()
