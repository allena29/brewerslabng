import blng.Voodoo
session = blng.Voodoo.DataAccess('crux-example.xml')
root = session.get_root()
root.simpleleaf = 'Hello World!'

print(session.dumps())

root.morecomplex.leaf2 = "a"
s = root.simplelist
le = s.create('firstkey')
print(le)
repr(le)
