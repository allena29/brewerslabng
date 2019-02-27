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
        return CruxVoodooNode(schema, xmldoc, root=True)


class BadVoodoo(Exception):

    def __init__(self, message):
        super().__init__(message)


class CruxVoodooNode:

    def __init__(self, schema, xmldoc, curpath="/", value=None, root=False):
        self.__dict__['_curpath'] = curpath
        self.__dict__['_xmldoc'] = xmldoc
        self.__dict__['_schema'] = schema
        self.__dict__['_type'] = 'wtf'
        self.__dict__['_value'] = value
        self.__dict__['_root'] = root
        self.__dict__['_path'] = curpath
        print('Init new cruxvood', self.__dict__)
        # This is getting called qiute often (every str() or repr())
        # It's probably not a problem right now because each time it's called we end up
        # getting etree elements by memory reference

    def voodoo(self):
        print('This is some vooodoo magic sh!t')

    def __repr__(self):
        print('repr')
        return 'VoodooNode: '

    def __str__(self):
        try:
            return self.__dict__['_value'].text
        except:
            return ''

    def __getattr__(self, attr):
        if attr in ('_ipython_canary_method_should_not_exist_', '_repr_mimebundle_'):
            raise AttributeError('Go Away!')

        curpath = self.__dict__['_curpath']
        schema = self.__dict__['_schema']
        xmldoc = self.__dict__['_xmldoc']
        path = curpath[1:] + '/' + attr
        print('Get attr ', curpath + '/' + attr)

        this_schema = schema.xpath(curpath + '/' + attr)
        if not len(this_schema):
            raise BadVoodoo("Unable to find '%s' in the schema" % (curpath[1:] + '/' + attr))

        xmldoc = self.__dict__['_xmldoc']
        this_value = xmldoc.xpath(curpath + '/' + attr)
        if not len(this_value):
            # Value not set **OR** value does not exist in the schema
            print('Value not yet set')
            return CruxVoodooNode(schema, xmldoc, curpath, value=None, root=False)

            return None
        elif len(this_value) == 1:
            print('value already set')
            print(this_value[0].text)

            return CruxVoodooNode(schema, xmldoc, curpath, value=this_value[0], root=False)

            self.__dict__['_value'] = this_value[0]
            return this_value[0]
        else:
            e = 5/0

    def __setattr__(self, attr, value):
        print('Set attr', self.__dict__['_curpath'] + '/' + attr + '>>>' + str(value))

        curpath = self.__dict__['_curpath']
        schema = self.__dict__['_schema']
        path = curpath[1:] + '/' + attr
        print('Get attr ', self.__dict__['_curpath'] + '/' + attr)
        print('Looking up in schema ' + curpath + '/' + attr)
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
            c = 5/0

    def create(self, *args):
        for arg in args:
            print('arg', arg)
        print('Listcreate')

    def __dir__(self):
        curpath = self.__dict__['_curpath']
        schema = self.__dict__['_schema']
        place = schema.xpath(curpath)
        children = []
        for child in place[0].getchildren():
            children.append(str(child.tag).replace('-', '_'))
        return children


session = CruxVoodoo()
root = session.get_root()

print('Root', root)
print('root.simpleleaf', root.simpleleaf)
if str(root.simpleleaf) == '':
    print("Uninitialised variable comes back as a blank string when using str()")
else:
    raise ValueError('str not working')
root.simpleleaf = 123
print('root.simpleleaf', root.simpleleaf)
temp_var = root.simpleleaf
root.simpleleaf = 'abc'
print(temp_var)
print(temp_var == 'abc')
print(temp_var == 123)
tempvar = root.simpleleaf

#raise ValueError('TODO: determine if we are a primitive... if so return the actual value')
#raise ValueError("onuuuy if not a primitive should we return a voodoo object")
#if temp_var == 'abc':#
#    print("all is ok we have temp_var as the last set value")
# else:
#    raise ValueError("This should be abc not 123")
print(root._schema.xpath('//inverted-schema')[0].getchildren())
