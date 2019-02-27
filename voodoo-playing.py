"""
 ipython --profile testing -i voodoo-playing.py

"""
from lxml import etree
class CruxVoodoo:

    def __init__(self):
        pass

    def get_root(self):
        schema = etree.parse('crux-example.xml').getroot()
        xmldoc = etree.fromstring('<vooodoo></vooodoo>')
        for child in schema.getchildren():
            if child.tag == 'inverted-schema':
                schema = child
        return CruxVoodooNode(schema, xmldoc)

class CruxVoodooNode:

    def __init__(self, schema, xmldoc, curpath="/"):
        print(self, schema, xmldoc,curpath)
        self.__dict__['_curpath'] = curpath
        self.__dict__['_xmldoc'] = xmldoc
        self.__dict__['_schema'] = schema

    def __getattr__(self, attr):
        print('Get attr ', self.__dict__['_curpath'] + '/'+ attr)

    def __setattr__(self, attr, value):
        print('Set attr', self.__dict__['_curpath'] + '/' + attr + '>>>' + str(value))

    def create(self, *args):
        for arg in args:
            print('arg', arg)
        print('Listcreate')

    def __dir__(self):
        children = []
        for child in self.__dict__['__schema'].getchildren():
            children.append(str(child.tag).replace('-', '_'))
        return children

session = CruxVoodoo()
root = session.get_root()

print('Root', root)
print('root.simpleleaf', root.simpleleaf)
root.simpleleaf = 234
print('root.simpleleaf', root.simpleleaf)

print(root._schema.xpath('//inverted-schema')[0].getchildren())

