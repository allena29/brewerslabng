import blng.Voodoo
session = blng.Voodoo.DataAccess('crux-example.xml')
root=session.get_root()
root.simpleleaf='Hello World!'

print(session.dumps())

s = root.simplelist
s.create('firstkey')


