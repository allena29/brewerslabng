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

    def _pretty(self, xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def dumps(self):
        return (self._pretty(self._xmldoc))

    def get_root(self):
        return CruxVoodooRoot(self._schema, self._xmldoc, root=True)


class BadVoodoo(Exception):

    def __init__(self, message):
        super().__init__(message)


class CruxVoodooBase:

    _voodoo_type = None

    def __init__(self, schema, xmldoc, curpath="/", value=None, root=False, listelement=False):
        self.__dict__['_curpath'] = curpath
        self.__dict__['_xmldoc'] = xmldoc
        self.__dict__['_schema'] = schema
        self.__dict__['_type'] = 'wtf'
        self.__dict__['_value'] = value
        self.__dict__['_root'] = root
        self.__dict__['_path'] = curpath
        if not root:
            self.__dict__['_thisschema'] = self._getschema(curpath)
        if root:
            self.__dict__['_thisschema'] = self.__dict__['_schema']

        print('Init new cruxvood', self.__dict__)
        # This is getting called qiute often (every str() or repr())
        # It's probably not a problem right now because each time it's called we end up
        # getting ee elements by memory reference

        for dchlid in self.__dict__['_thisschema'].getchildren():
            print('dir----child', dchlid.tag)

    def voodoo(self):
        print('This is some vooodoo magic sh!t')

    def __name__(self):
        return "Ting Tings - that's not my name"

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

        this_schema = self._getschema(curpath + '/' + attr)

        supported_types = {
            'leaf': None,
            'container': CruxVoodooContainer,
            'list': CruxVoodooList
        }

        supported_type_found = None
        yang_type = None
        for schild in this_schema.getchildren():
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
        this_schema = self._getschema(curpath + '/' + attr)

        # TODO:
        # validate against this_schema[0]
        print('Schema to validate against...', this_schema)

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
        listing = []
        for dchild in self.__dict__['_thisschema'].getchildren():
            if not dchild.tag == 'yin-schema':
                listing.append(dchild.tag)
        return listing

    def _getschema(self, path):
        schema = self.__dict__['_schema']
        this_schema = schema.xpath(path)
        if not len(this_schema):
            raise BadVoodoo("Unable to find '%s' in the schema" % (path))
        elif len(this_schema) > 1:
            raise BadVoodoo("Too many hits for '%s' in the schema" % (path))
        return this_schema[0]

    def __repr__(self):
        print(self._voodoo_type)
        return 'Voodoo'+self._voodoo_type+': ' + self.__dict__['_curpath'][1:]


class CruxVoodooRoot(CruxVoodooBase):

    _voodoo_type = 'Root'

    def __repr__(self):
        return 'VoodooRoot'


class CruxVoodooLeaf(CruxVoodooBase):

    _voodoo_type = 'Leaf'


class CruxVoodooContainer(CruxVoodooBase):

    _voodoo_type = 'Container'


class CruxVoodooPresenceContainer(CruxVoodooBase):

    _voodoo_type = 'PresenceContainer'

    def exists(self):
        return True


class CruxVoodooList(CruxVoodooBase):

    _voodoo_type = 'List'

    """
    List.

    Note: this object maps to a yang based list which behaves more a-kin to a dictionary in python.
    However, it is possible to have lists with composite keys in YANG.
    TODO: expect these are just tuples.
    """

    def __getitem__(self, key):
        print('Get Item', key)

    def create(self, *args):
        """
        Create a list element, if the element already exists return the existing node.

        The user is responsible for ensuring that any mandatory node of sibling leaves are
        populated according to the constraints of the YANG schema.
        """
        curpath = self.__dict__['_curpath']
        schema = self.__dict__['_schema']
        xmldoc = self.__dict__['_xmldoc']

        for arg in args:
            print('arg', arg)
        curpath = self.__dict__['_curpath']
        print('Listcreate on ', curpath)
        this_schema = self._getschema(curpath)
        for lschema in this_schema.getchildren():
            print(lschema.tag)

        # Two things (maybe more than 2)
        # 1 need to return a node
        # 2 need to add something into xmldoc
        # 3 what about mandatory things... not taking responsibility for this yet.
        # 4 make sure we have all keys
        # 5 make sure the keys dont' exist yet

        return CruxVoodooListElement(schema, xmldoc, curpath, value=None, root=False, listelement=True)


class CruxVoodooListElement(CruxVoodooBase):

    _voodoo_type = 'ListElement'


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
