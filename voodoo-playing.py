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


class BadVoodoo(Exception):

    def __init__(self, message):
        super().__init__(message)

class CruxVoodooNode:

    def __init__(self, schema, xmldoc, curpath="/"):
        print(self, schema, xmldoc,curpath)
        self.__dict__['_curpath'] = curpath
        self.__dict__['_xmldoc'] = xmldoc
        self.__dict__['_schema'] = schema
        self.__dict__['_type'] = 'wtf'


    def __getattr__(self, attr):
        curpath = self.__dict__['_curpath']
        print('Get attr ', self.__dict__['_curpath'] + '/'+ attr)

        xmldoc = self.__dict__['_xmldoc']
        this_value = xmldoc.xpath(curpath + '/' + attr)
        if not len(this_value):
            print('Value not yet set')
            return None
        elif len(this_value) == 1:
            print('value already set')
            print(this_value[0].text)
            return this_value[0]
        else:
            e=5/0

    def __setattr__(self, attr, value):
        print('Set attr', self.__dict__['_curpath'] + '/' + attr + '>>>' + str(value))
        
        curpath = self.__dict__['_curpath']
        schema = self.__dict__['_schema']
        path = curpath[1:] + '/' + attr
        print('Get attr ', self.__dict__['_curpath'] + '/'+ attr)
        print('Looking up in schema '+ curpath + '/' + attr)
        this_schema = schema.xpath(curpath + '/' + attr)
        if not len(this_schema):
            raise BadVoodoo("Unable to find '%s' in the schema" % (curpath[1:] + '/' + attr))
        elif len(this_schema) > 1:
            raise BadVoodoo("Too many hits for '%s' in the schema" % (curpath[1:] + '/' + attr))


        # TODO:
        # validate against this_schema[0]
        print('Schema to validate against...', this_schema[0])


        xmldoc = self.__dict__['_xmldoc']
        this_value = xmldoc.xpath(curpath + '/' + attr)
        if len(this_value) == 0:
            print('Value not yet set')
            # This actually could be pretty tricky...
            print('count of / = %s' % (path.count('/')))
            if path.count('/') == 1:
                new_node = etree.Element(attr)
                new_node.text = str(value)
                xmldoc.append(new_node)
                return new_node
                erint('Added brand new node because it happened to be at root and easy')
        elif len(this_value) == 1:
            this_value[0].attrib['old_value'] = this_value[0].text
            this_value[0].text = str(value)
            return this_value[0]
            print('should be set here')
        else:
            c=5/0

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

