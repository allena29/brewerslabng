import yangvoodoo
session = yangvoodoo.DataAccess()
session.connect()
root = session.get_root('brewerslab', yang_location='/sysrepo/yang')
definition_root = session.get_root('brewerslab-definitions', yang_location='/sysrepo/yang')

definition_root.definitions.ingredients.fermentables.create('sdf')
#
import mysql.connector
con = mysql.connector.connect(host='192.168.1.13', database='brewerslab', user='brewerslab', password='beer')
cursor = con.cursor()
query = "select name, hwe, extract, mustMash, isAdjunct from gItems where majorcategory='fermentables' ORDER by name"
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)
    fermentable = definition_root.definitions.ingredients.fermentables.create(row[0])
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
    hop = definition_root.definitions.ingredients.hops.create(row[0])
    hop.alpha_acid = row[1]


import mysql.connector
con = mysql.connector.connect(host='192.168.1.13', database='brewerslab', user='brewerslab', password='beer')
cursor = con.cursor()
query = "select name, attenuation  from gItems where majorcategory='yeast' ORDER by name;"
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)
    yeast = definition_root.definitions.ingredients.yeast.create(row[0])
    yeast.attenuation = row[1]


session.commit()
