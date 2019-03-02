"""
 ipython --profile testing -i voodoo-playing.py
"""
import re
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
        self._xmldoc = CruxVoodoBackendWrapper()
        self._cache = (CruxVoodooCache(), CruxVoodooCache())

    def dumps(self):
        return self._xmldoc.dumps()

    def loads(self, input_string):
        """
        Load a new set of data into memory.

        Note: this is pretty messy because the xmldoc and cache object references can be
        splattered across lots of instantiated data.

        i.e. we may have done

        root = session.get_root()
        x = root.morecomplex
        x.leaf2 = '5'
        GETATTR on  <Element crux-vooodoo at 0x104d7e888>  with CACHE  (<blng.Voodoo.CruxVoodooCache object at 0x104d6feb8>, <blng.Voodoo.CruxVoodooCache object at 0x1053d3e48>) against path  /morecomplex

        Now if we update xmldoc on session we won't have the references on all the individual cruxnodes updated.
        """

        for x in self._xmldoc.getchildren():
            print(x.tag)

        self._xmldoc.loads(input_string)
        (keystore_cache, schema_cache) = self._cache
        keystore_cache.empty()

    def get_root(self):
        return CruxVoodooRoot(self._schema, self._xmldoc, self._cache, root=True)


class CruxVoodoBackendWrapper:

    def __init__(self):
        self.xmldoc = etree.fromstring('<crux-vooodoo></crux-vooodoo>')

    def xpath(self, *args, **kwargs):
        return self.xmldoc.xpath(*args, **kwargs)

    def append(self, *args, **kwargs):
        return self.xmldoc.append(*args, **kwargs)

    def getchildren(self, *args, **kwargs):
        return self.xmldoc.getchildren(*args, **kwargs)

    def _pretty(self, xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def dumps(self):
        return self._pretty(self.xmldoc)

    def loads(self, xmlstr):
        for child in self.xmldoc.getchildren():
            self.xmldoc.remove(child)

        new_xmldoc = etree.fromstring(xmlstr)

        for child in new_xmldoc.getchildren():
            self.xmldoc.append(child)


class BadVoodoo(Exception):

    def __init__(self, message):
        super().__init__(message)


class CruxVoodooCache:

    """
    Crude timing shows etree.xpath lookups are costly.
    0.4626600742340088 for 10000  - using CruxVoodoo - getattr
    0.16473913192749023 for 10000 - Using first fragment below
    0.0030121803283691406 for 10000 - Using second fragment below.
        start_time = time.time()
        for x in range(n):
            e = xmldoc.xpath('//simpleleaf')[0] = str(x)
        end_time = time.time()

        e = xmldoc.xpath('//simpleleaf')[0]
        start_time = time.time()
        for x in range(n):
            e = str(x)
        end_time = time.time()

    Therefore we introduce a primitive caching mechanims of keypaths to provide elements which have already being found.

    With the basic cache
    0.29372692108154297 for 10000   36 % improvement
    0.03447079658508301 for 10000    92% improvemeent
    0.005204200744628906 for 10000   baseline just calling the method and truning
    """

    def __init__(self):
        """
        Items are stored in the cached based upon the xpath of the string.

        The cache object may be used for storing any key/value data, however here
        we use two independent instances, one for caching the data xmldoc, and one
        for caching the schema xmldoc.
        """
        self.items = {}

    def add_entry(self, path, cache_object):
        """
        Add an entry into the cache.

        key = an XPATH path (e.g. /simpleleaf)
        cache_object = An etree Element node from the XMLDOC.
        """
        print('CACHE ADD ENTRY', path, cache_object)
        self.items[path] = cache_object

    def empty(self):
        self.items.clear()


class CruxVoodooBase:

    _voodoo_type = None

    def _pretty(self, xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def __init__(self, schema, xmldoc, cache, curpath="/", value=None, root=False, listelement=None):
        """
        A CurxNode is used to represent 'containing' structures within the yang module, primitive
        terminiating leaves are not CruxNodes.

        Every CruxNode holds references to lxml etree instantiations of
         - schema (crux-schema format)
         - xmldoc (datasource)

        Cache lookups to avoid expensive xpath lookups. (Potentially in the future we may want to
        cache the objects themselves, as they get instantiated on every __getattr__).

        """

        print('CRUXVOODOO-INIT', curpath)
        self.__dict__['_curpath'] = curpath
        self.__dict__['_xmldoc'] = xmldoc
        self.__dict__['_schema'] = schema
        self.__dict__['_type'] = 'wtf'
        self.__dict__['_value'] = value
        self.__dict__['_root'] = root
        self.__dict__['_path'] = curpath
        self.__dict__['_cache'] = cache
        self.__dict__['_children'] = {}

        if not root:
            self.__dict__['_thisschema'] = self._getschema(curpath)
        else:
            self.__dict__['_thisschema'] = self.__dict__['_schema']
        for child in self.__dict__['_thisschema']:
            if not child.tag == 'yin-schema':
                print('  ... adding child', child.tag)
                self.__dict__['_children'][child.tag] = child

        print('Init new cruxvood', self.__dict__)
        # This is getting called qiute often (every str() or repr())
        # It's probably not a problem right now because each time it's called we end up
        # getting ee elements by memory reference

        if listelement:
            self.__dict__['_mykeys'] = listelement

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
        cache = self.__dict__['_cache']
        (keystore_cache, schema_cache) = cache
        path = curpath[1:] + '/' + attr
        print('GETATTR on ', xmldoc, ' with CACHE ', cache, 'against path ', path)
        print('Get attr ', curpath + '/' + attr)
        this_schema = self._getschema('/' + path)

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

        this_value = self._getxmlnode('/' + path)

        if not this_value:
            if yang_type == 'leaf':
                print('Value not yet set - primtiive so just returning None')
                return None

            print('Value not yet set')
            return supported_types[yang_type](schema, xmldoc, cache, curpath + '/' + attr, value=None, root=False)

        print('value already set')

        if yang_type == 'leaf':
            return this_value[0].text

        return supported_types[yang_type](schema, xmldoc, cache, curpath + '/' + attr, value=this_value[0], root=False)

        # xmldoc = self.__dict__['_xmldoc']
#        this_value = xmldoc.xpath(curpath + '/' + attr)
#        if not len(this_value):#
        # Value not set **OR** value does not exist in the schema
        # if yang_type == 'leaf':
        #        print('Value not yet set - primtiive so just returning None')
    #            return None#
#
#            print('Value not yet set')#
        # return supported_types[yang_type](schema, xmldoc, cache, curpath + '/' + attr, value=None, root=False)

        # elif len(this_value) == 1:
    #        print('value already set')
#            print(this_value[0].text)#

        #if yang_type == 'leaf':#
        #        print(this_value[0].text, '<<<<< primitive')
    #            return this_value[0].text#
##
#            return supported_types[yang_type](schema, xmldoc, cache, curpath + '/' + attr, value=this_value[0], root=False)

    def __setattr__(self, attr, value):
        # rint('Set attr', self.__dict__['_curpath'] + '/' + attr + '>>>' + str(value))
        #     0.005204200744628906 for 10000
        curpath = self.__dict__['_curpath']
        schema = self.__dict__['_schema']
        cache = self.__dict__['_cache']
        (keystore_cache, schema_cache) = cache

        path = curpath[1:] + '/' + attr
        # print('set attr ', self.__dict__['_curpath'] + ' /' + attr)
        # print('Looking up in schema ' + curpath + '/' + attr)

        this_schema = self._getschema('/' + path)
        # TODO:
        # validate against this_schema[0]
        # print('Schema to validate against...', this_schema)

        xmldoc = self.__dict__['_xmldoc']

        if path not in keystore_cache.items:
            print('Non cache hit on value', path)
            this_value = xmldoc.xpath('/' + path)
        else:
            this_value = [keystore_cache.items[path]]
        if len(this_value) == 0:
            print('Value not yet set')
            # This actually could be pretty tricky...
            print('count of / = %s' % (path.count('/')))
#
#            if path.count('/') == 1:
#
#            new_node = etree.Element(attr)
#                new_node.text = str(value)
    #            keystore_cache.items[path] = new_node
        #        xmldoc.append(new_node)
        #        return new_node
        #        erint('Added brand new node because it happened to be at root and easy')
            # else:
            new_node = self._find_longest_match_path(xmldoc, path)
            new_node.text = str(value)
            keystore_cache.add_entry(path, new_node)

        elif len(this_value) == 1:
            if 'listkey' in this_value[0].attrib:
                raise BadVoodoo('Changing a list key is not supported. ' + curpath[1:])
            this_value[0].attrib['old_value'] = this_value[0].text
            this_value[0].text = str(value)

            keystore_cache.add_entry(path, this_value[0])
            return this_value[0]
            print('should be set here')
        else:
            c = 5/0

    def _find_longest_match_path(self, xmldoc, path):
        """
        The in-memory objects with VooodooNodes work quite well for giving us somewhere to
        set/get data. However, something transient in memory alone if pretty useless without
        being able to serialise towards NETCONF/File.

        This method works backwards to find the longest match we have in the xmldoc already.
        """
        found = None

        # working path is expected to look like this ['', 'morecomplex', 'leaf2']
        working_path = path.split('/')
        print("Come into find longest path", working_path)
        for i in range(len(working_path)-1, 1, -1):
            print('Using longest_match', i, '/'.join(working_path[:i]))
            this_path = '/' + '/'.join(working_path[:i])
            results = xmldoc.xpath(this_path)
            if len(results) == 1:
                found = (i, this_path, results[0])
                break
            elif len(results) > 1:
                raise BadVoodoo('Longest match on %s found multiple hits (which may or may not be safe!)' % (this_path))

        if not found:
            print('More work to do', working_path[1:])

            # working path is expected to look like this ['', 'morecomplex', 'leaf2']
            # which is why we have gone for 1 - so the next loop can take either 1 (below)
            # or int he case of a longer match above i
            found = (1, '', xmldoc)

        (right_most_index, SomeKindOfWarningWhichMightBeIgnored, parent_node) = found
        for path_node in working_path[right_most_index:]:
            print('Need to add %s' % (path_node))
            path_keys = None
            if '[' in path_node:
                path_keys = path_node[path_node.find('['):]
                path_node = path_node[:path_node.find('[')]
                print('List keys present in the path node')

            print('SCHMEA OF THIS NODE', self.__dict__['_thisschema'].getchildren())
            print('SCHMEA CHILDREN', self.__dict__['_children'])
            if path_node in self.__dict__['_children']:
                node = etree.Element(path_node)
            elif path_node.replace('_', '-') in self.__dict__['_children']:
                print('PATH NODE is in children **WITH** HYPHEN conversion', path_node)
                node = etree.Element(path_node.replace('_', '-'))
            else:
                node = etree.Element(path_node)
            print(node, 'is going to get attached to ', parent_node)
            parent_node.append(node)
            parent_node = node

            if path_keys:
                for (key, value) in re.findall("\[([^=]*)='([^']+)'\]", path_keys):
                    key_node = etree.Element(key)
                    key_node.attrib['listkey'] = 'yes'
                    key_node.text = value
                    node.append(key_node)

        return parent_node

    def __dir__(self):
        listing = []
        for dchild in self.__dict__['_thisschema'].getchildren():
            if not dchild.tag == 'yin-schema':
                listing.append(dchild.tag.replace('-', '_'))
        return listing

    def _getxmlnode(self, path):
        """Get the xmlnode from the cache or by xpath lookup."""

        xmldoc = self.__dict__['_xmldoc']
        (keystore_cache, schema_cache) = self.__dict__['_cache']

        if path in keystore_cache.items:
            print('Using cached item for', path)
            return keystore_cache.items[path]

        this_value = xmldoc.xpath(path)
        print('get_xmlnode', path, this_value)
        if not this_value:
            this_value = xmldoc.xpath(path.replace('_', '-'))

        if len(this_value):
            print('CACHE PATH GETXCMLDOE'+path)
            keystore_cache.items[path[1:]] = this_value[0]
        return this_value

    def _getschema(self, path):
        """
        Get information from the schema, returning from the cache if we have previously accessed
        it.

        This will include leaves and yang elements including the addition 'yin-schema' element.
        """
        schema = self.__dict__['_schema']
        (keystore_cache, schema_cache) = self.__dict__['_cache']

        if path in schema_cache.items:
            this_schema = schema_cache.items[path]
            return this_schema

        print('get_schema', path)
        this_schema = schema.xpath(path)
        if not len(this_schema) and path.count('_'):
            this_schema = schema.xpath(path.replace('_', '-'))
        if not len(this_schema):
            raise BadVoodoo("Unable to find '%s' in the schema" % (path))
        elif len(this_schema) > 1:
            raise BadVoodoo("Too many hits for '%s' in the schema" % (path))
        schema_cache.items[path] = this_schema[0]
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
        thisschema = self.__dict__['_thisschema']
        cache = self.__dict__['_cache']
        (keystore_cache, schema_cache) = cache

        for arg in args:
            print('arg', arg)
        curpath = self.__dict__['_curpath']

        keys = []
        # This is pretty shcoking
        for x in thisschema.getchildren():
            print(x.tag, 'sdfnsdf')
            if x.tag == 'yin-schema':
                for y in x.getchildren():
                    for z in y.getchildren():
                        print(z.tag, 'aa')
                        if z.tag == 'key' and 'value' in z.attrib:
                            keys = z.attrib['value'].split(' ')
        """
        This gives us
              <yin-schema path="/simplelist">
                <list>
                  <key value="simplekey"/>
                </list>
              </yin-schema>

        Or in a composite case
                  <list>
                    <key value="secondkey thirdkey"/>
                  </list>
        """

        if not keys:
            raise BadVoodoo('Trying to inspect schema for keys but did not find them. %s' % (curpath))

        print('got keys', keys)

        if not len(keys) == len(args):
            raise BadVoodoo('Wrong Number of keys require %s got %s. keys defined: %s' % (len(keys), len(args), str(keys)))

        """
        TODO
        TODO
        TODO - put sett_attr equivalent here
        TODO
        TODO

        Good news is that xpath lookup appears to work well

            In [30]: xmldoc = etree.fromstring(''' < crux-vooodoo >
                ...: < list >
                ...: < a > sdf < /a >
                ...: < b > abc < /b >
                ...: < /list >
                ...: < list >
                ...: < a > 123 < /a >
                ...: < b > abc < /b >
                ...: < /list >
                ...: < list >
                ...: < a > sdf < /a >
                ...: < b > xxx < /b >
                ...: < /list >
                ...: < list >
                ...: < a > yyy < /a >
                ...: < b > xxx < /b >
                ...: < /list >
                ...: < list >
                ...: < a > ra < /a >
                ...: < /list >
                ...: < /crux-vooodoo > ''')

            In [31]: xmldoc.xpath("//list[a='sdf']")
            Out[31]: [<Element list at 0x106ebfe08>, <Element list at 0x1064de408>]

            In [32]: xmldoc.xpath("//list[b='abc']")
            Out[32]: [<Element list at 0x106ebfe08>, <Element list at 0x106e5c288>]

            In [33]: xmldoc.xpath("//list[a='ra']")
            Out[33]: [<Element list at 0x1064f02c8>]

            In [34]: xmldoc.xpath("//list[a='sdf'][b='abc']")
            Out[34]: [<Element list at 0x106ebfe08>]

            In [35]: xmldoc.xpath("//list[b='abc']")
            Out[35]: [<Element list at 0x106ebfe08>, <Element list at 0x106e5c288>]


        """

        """
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
                else:
                    new_node = self._find_longest_match_path(xmldoc, path)
                    new_node.text = str(value)

            elif len(this_value) == 1:

                this_value[0].attrib['old_value'] = this_value[0].text
                this_value[0].text = str(value)
                return this_value[0]
                print('should be set here')
            else:
                c = 5/0

        """
        path_to_list_element = curpath
        ai = 0
        for key in keys:
            # this_value = xmldoc.xpath(curpath + '/' + attr)

            print(curpath + '/' + key, ' -> ', args[ai])
            # self.__setattr__()
            # self.__setattr__(key, args[ai], key=True)
            path_to_list_element = path_to_list_element + "[" + key + "='" + args[ai] + "']"
            ai = ai+1

        print("Find this xpath: ", path_to_list_element)

        this_value = xmldoc.xpath(path_to_list_element)
        if len(this_value) == 0:
            print('Value not yet set')
            new_node = self._find_longest_match_path(xmldoc, path_to_list_element[1:])
        else:
            print(this_value, '<<<<<<<<<<<<<<<<< already existed')
        # Two things (maybe more than 2)
        # 1 need to return a node
        # 2 need to add something into xmldoc
        # 3 what about mandatory things... not taking responsibility for this yet.
        # 4 make sure we have all keys
        # 5 make sure the keys dont' exist yet
        # 6 make sure list keys are never allowed to change - they are classes as primitives not something special.
        # 7 lists within lists
        # 8 lists within container
        return CruxVoodooListElement(schema, xmldoc, cache, curpath, value=None, root=False, listelement=str(args))


class CruxVoodooListElement(CruxVoodooBase):

    _voodoo_type = 'ListElement'

    def __repr__(self):
        print(self._voodoo_type)
        return 'Voodoo'+self._voodoo_type+': ' + self.__dict__['_curpath'][1:] + ' keys:' + self.__dict__['_mykeys']


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

# raise ValueError('TODO: determine if we are a primitive... if so return the actual value')
# raise ValueError("onuuuy if not a primitive should we return a voodoo object")
#if temp_var == 'abc':#
#    print("all is ok we have temp_var as the last set value")
# else:
#    raise ValueError("This should be abc not 123")
print(root._schema.xpath('//inverted-schema')[0].getchildren())
a = root.morecomplex.leaf3
"""
