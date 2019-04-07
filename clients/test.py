import datalayer

session = datalayer.DataAccess()
session.connect()
root = session.get_root('integrationtest')
print(root)
print(dir(root))
print(root.simpleleaf)
