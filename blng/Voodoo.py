"""
 ipython --profile testing -i voodoo-playing.py
"""
from lxml import etree


class DataAccess:

    """
    This class (and the associated classes) provides a method to provide python-object access to the data.

    The data schema is rendered from yang models (pyang yin) into a specific XML structure which provides
    top-down navigation of the entire schema. This is the 'crux-schema.xml'.

    Behind the scene two XML documents are maintained, one the schema and the second a 'running' datastore.

    This data could be backed off to a NETCONF server, or serialised into local XML documents.

    Basic Usage:

        import blng.Voodoo
        session = blng.Voodoo.DataAccess("crux-example.xml", datastore=None)
        root = session.get_root()

    Note:
        ipython - disable jedi auto-completer for a better experience.
    """

    def __init__(self, crux_schema_file, datastore=None):
        """
        Initialise the datastore based on the provided schema.
        """
        self._schema = None

        for child in etree.parse(crux_schema_file).getroot().getchildren():
            print(child.tag)
            if child.tag == 'inverted-schema':
                self._schema = child

        if not self._schema:
            raise BadVoodoo("Unable to find the schema from the provided file ()" + crux_schema_file)

        if datastore:
            raise NotImplementedError("de-serialising a datastore for loading not thought about yet")
        self._xmldoc = etree.fromstring('<crux-vooodoo></crux-vooodoo>')

    def get_root(self):
        return CruxVoodooRoot(self._schema, self._xmldoc, root=True)


class BadVoodoo(Exception):

    def __init__(self, message):
        super().__init__(message)


class CruxVoodooBase:

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
        # getting ee elements by memory reference

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

        print('Workout what we are from the scheam and insantiate the right kind of object')
        supported_types = {
            'leaf': None,
            'container': CruxVoodooContainer,
            'list': CruxVoodooList
        }

        supported_type_found = None
        yang_type = None
        for schild in this_schema[0].getchildren():
            if schild.tag == 'yin-schema':
                for ychild in schild.getchildren():
                    yang_type = ychild.tag
                    if str(ychild.tag) in supported_types:
                        supported_type_found = ychild

                    print(ychild.tag, "<<ychild ***************")
                print(schild.tag, '<<<schema')

        if not yang_type:
            raise BadVoodoo("Unsupported type of node %s" % (yang_type))

        xmldoc = self.__dict__['_xmldoc']
        this_value = xmldoc.xpath(curpath + '/' + attr)
        if not len(this_value):
            # Value not set **OR** value does not exist in the schema
            if yang_type == 'leaf':
                print('Value not yet set - primtiive so just returning None')
                return None

            print('Value not yet set')
            return supported_types[yang_type](schema, xmldoc, curpath + '/' + attr, value=None, root=False)

        elif len(this_value) == 1:
            print('value already set')
            print(this_value[0].text)

            if yang_type == 'leaf':
                print(this_value[0].text, '<<<<< primitive')
                return this_value[0].text

            return supported_types[yang_type](schema, xmldoc, curpath + '/' + attr, value=this_value[0], root=False)

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

    def __dir__(self):
        curpath = self.__dict__['_curpath']
        schema = self.__dict__['_schema']
        place = schema.xpath(curpath)
        children = []
        for child in place[0].getchildren():
            children.append(str(child.tag).replace('-', '_'))
        return children


class CruxVoodooRoot(CruxVoodooBase):

    def __repr__(self):
        return 'VoodooRoot'


class CruxVoodooLeaf(CruxVoodooBase):
    pass


class CruxVoodooContainer(CruxVoodooBase):

    def __repr__(self):
        return 'VoodooContainer: ' + self.__dict__['_curpath'][1:]


class CruxVoodooPresenceContainer(CruxVoodooBase):

    def __repr__(self):
        return 'VoodooPresenceContainer: '

    def exists(self):
        return True


class CruxVoodooList(CruxVoodooBase):

    def __repr__(self):
        return 'VoodooList: ' + self.__dict__['_curpath'][1:]

    def __getitem__(self, key):
        print('Get Item', key)

    def create(self, *args):
        for arg in args:
            print('arg', arg)
        print('Listcreate')


"""
ses"sion = CruxVoodoo()
root = session.get_root()

print('Root', root)
print('root.simpleleaf', root.simpleleaf)
if root.simpleleaf is None:
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
a = root.morecomplex.leaf3
"""
