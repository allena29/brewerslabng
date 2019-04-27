import yangvoodoo
session = yangvoodoo.DataAccess()
session.connect()
root = session.get_root('brewerslab', yang_location='/sysrepo/yang')

import mysql.connector
con = mysql.connector.connect(host='192.168.1.13', database='brewerslab', user='brewerslab', password='beer')
cursor = con.cursor()
query = "select distinct(ingredient),hwe,extract,isAdjunct,mustMash from gIngredients WHERE ingredientType='fermentables';"
cursor.execute(query)
rows = cursor.fetchall()
for row in rows:
    print(row)
    fermentable = root.definitions.fermentables.create(row[0])
    fermentable.hwe = row[1]
    fermentable.extract = row[2]
    fermentable.mash_required = row[4] == True
    fermentable.adjunct = row[3] == True
session.commit()
