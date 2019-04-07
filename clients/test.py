import libyang
import datalayer

session = datalayer.DataAccess()
session.connect()
root = session.get_root('integrationtest')
print(root)
print(dir(root))
print(root.simpleleaf)
root.simpleleaf = 'abc'
print(root.simpleleaf)
root.simpleenum = 'A'
session.commit()


ctx = libyang.Context('../yang/')
schema = ctx.load_module('integrationtest')

schema_node = root._get_schema_of_path('/integrationtest:simpleleaf')
print(schema_node)
print(schema_node.nodetype())
