"""
 ipython --profile testing -i voodoo-playing.py
"""
import logging
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
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('voodoo')

        for child in etree.parse(crux_schema_file).getroot().getchildren():
            if child.tag == 'inverted-schema':
                self._schema = child

        if not self._schema:
            raise BadVoodoo("Unable to find the schema from the provided file ()" + crux_schema_file)

        if datastore:
            raise NotImplementedError("de-serialising a datastore for loading not thought about yet")
        self._xmldoc = CruxVoodoBackendWrapper()
        self._keystorecache = CruxVoodooCache(self.log, 'keystore')
        self._schemacache = CruxVoodooCache(self.log, 'schema')
        self._cache = (self._keystorecache, self._schemacache)

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

        self._xmldoc.loads(input_string)
        (keystore_cache, schema_cache) = self._cache
        keystore_cache.empty()

    def get_root(self):
        return CruxVoodooRoot(self._schema, self._xmldoc, self._cache, '/', '/', root=True, log=self.log)


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

    def __init__(self, log, usage=''):
        """
        Items are stored in the cached based upon the xpath of the string.

        The cache object may be used for storing any key/value data, however here
        we use two independent instances, one for caching the data xmldoc, and one
        for caching the schema xmldoc.
        """
        self.items = {}
        self.log = log
        self.usage = usage

    def is_path_cached(self, path):
        if path in self.items:
            return True
        return False

    def get_item_from_cache(self, path):
        return self.items[path]

    def add_entry(self, path, cache_object):
        """
        Add an entry into the cache.

        key = an XPATH path (e.g. /simpleleaf)
        cache_object = An etree Element node from the XMLDOC.
        """
        self.log.debug('%s.CACHE %s -> %s', self.usage, path, str(cache_object))

        self.items[path] = cache_object

    def empty(self):
        self.items.clear()


class CruxVoodooBase:

    _voodoo_type = None

    def _pretty(self, xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def __init__(self, schema, xmldoc, cache, schemapath, valuepath, value=None, root=False, listelement=None,
                 log=None, parent=None):
        """
        A CurxNode is used to represent 'containing' structures within the yang module, primitive
        terminiating leaves are not CruxNodes.

        Every CruxNode holds references to lxml etree instantiations of
         - schema (crux-schema format)
         - xmldoc (datasource)

        Cache lookups to avoid expensive xpath lookups. (Potentially in the future we may want to
        cache the objects themselves, as they get instantiated on every __getattr__).

        """
        self.__dict__['_log'] = log
        self.__dict__['_schemapath'] = schemapath
        self.__dict__['_valuepath'] = valuepath
        self.__dict__['_parent'] = parent
        self.__dict__['_xmldoc'] = xmldoc
        self.__dict__['_schema'] = schema
        self.__dict__['_type'] = 'wtf'
        self.__dict__['_value'] = value
        self.__dict__['_root'] = root
        self.__dict__['_cache'] = cache
        self.__dict__['_children'] = {}

        log.info('initialise %s' % (valuepath))
        if not root:
            self.__dict__['_path'] = valuepath[1:]
            self.__dict__['_thisschema'] = self._getschema(schemapath)
        else:
            self.__dict__['_path'] = '/'
            self.__dict__['_thisschema'] = self.__dict__['_schema']

        self._populate_children()

        # This is getting called qiute often (every str() or repr())
        # It's probably not a problem right now because each time it's called we end up
        # getting ee elements by memory reference

        if listelement:
            self.__dict__['_mykeys'] = listelement

    def _populate_children(self):
        for child in self.__dict__['_thisschema']:
            if not child.tag == 'yin-schema':
                self.__dict__['_children'][child.tag] = child

    def __name__(self):
        return "Ting Tings - that's not my name"

    def __repr__(self):
        return 'VoodooNode: '

    def __str__(self):
        try:
            return self.__dict__['_value'].text
        except:
            return ''

    def show_children(self):
        children = self.__dir__()
        children.sort()
        for x in children:
            print(x)

    def __getattr__(self, attr):
        if attr in ('_ipython_canary_method_should_not_exist_', '_repr_mimebundle_'):
            raise AttributeError('Go Away!')

        log = self.__dict__['_log']
        schemapath = self.__dict__['_schemapath']
        valuepath = self.__dict__['_valuepath']
        schema = self.__dict__['_schema']
        xmldoc = self.__dict__['_xmldoc']
        cache = self.__dict__['_cache']
        (keystore_cache, schema_cache) = cache

        spath = schemapath + '/' + attr
        vpath = valuepath + '/' + attr

        this_schema = self._getschema(spath)

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

        if not yang_type:
            raise BadVoodoo("Unsupported type of node %s" % (yang_type))
        this_value = self._getxmlnode(vpath)

        if len(this_value) == 0:
            if yang_type == 'leaf':
                log.info('get-leaf %s <no-value>', vpath)
                return None

            log.info('get-leaf %s <node-no-value:%s>', vpath, yang_type)
            return supported_types[yang_type](schema, xmldoc, cache, spath, vpath,
                                              value=None, root=False, log=log,
                                              parent=self)

        if yang_type == 'leaf':
            log.info('get-leaf %s %s', vpath, this_value[0].text)
            return this_value[0].text

        log.info('get-leaf %s <node:%s>', vpath, yang_type)
        return supported_types[yang_type](schema, xmldoc, cache, spath, vpath,
                                          value=this_value[0], root=False, log=log,
                                          parent=self)

    def __setattr__(self, attr, value):
        log = self.__dict__['_log']
        schemapath = self.__dict__['_schemapath']
        valuepath = self.__dict__['_valuepath']
        schema = self.__dict__['_schema']
        cache = self.__dict__['_cache']
        (keystore_cache, schema_cache) = cache

        spath = schemapath + '/' + attr
        vpath = valuepath + '/' + attr

        this_schema = self._getschema(spath)
        xmldoc = self.__dict__['_xmldoc']
        this_value = self._getxmlnode(vpath)

        if len(this_value) == 0:
            log.info('set %s %s <old-value:not-set>', vpath, value)

            new_node = self._find_longest_match_path(xmldoc, vpath)
            new_node.text = str(value)
            keystore_cache.add_entry(vpath, new_node)

        elif len(this_value) == 1:
            if 'listkey' in this_value[0].attrib:
                raise BadVoodoo('Changing a list key is not supported. ' + vpath[1:])

            log.info('set %s %s <old-value:%s>', vpath, value, this_value[0].text)
            this_value[0].attrib['old_value'] = this_value[0].text
            this_value[0].text = str(value)

            keystore_cache.add_entry(vpath, this_value[0])
            return this_value[0]
        else:
            c = 5/0

    def _find_longest_match_path(self, xmldoc, path):
        """
        The in-memory objects with VooodooNodes work quite well for giving us somewhere to
        set/get data. However, something transient in memory alone if pretty useless without
        being able to serialise towards NETCONF/File.

        This method works backwards to find the longest match we have in the xmldoc already.
        """
        log = self.__dict__['_log']
        found = None

        # working path is expected to look like this ['', 'morecomplex', 'leaf2']
        working_path = path[1:].split('/')
        for i in range(len(working_path)-1, 1, -1):
            this_path = '/' + '/'.join(working_path[:i])
            # results = xmldoc.xpath(this_path)
            results = self._getxmlnode(this_path)
            if len(results) == 1:
                found = (i, this_path, results[0])
                log.debug('_longest_path: %s <match> %s %s %s', path, i, this_path, results[0])

                break
            elif len(results) > 1:
                raise BadVoodoo('Longest match on %s found multiple hits (which may or may not be safe!)' % (this_path))
            log.debug('_longest_path: %s <carryon> %s %s %s', path, i, this_path, 'xx')

        if not found:
            log.debug('_longest_path: %s <miss>', path)

            # working path is expected to look like this ['', 'morecomplex', 'leaf2']
            # which is why we have gone for 1 - so the next loop can take either 1 (below)
            # or int he case of a longer match above i
            found = (1, '', xmldoc)

        (right_most_index, SomeKindOfWarningWhichMightBeIgnored, parent_node) = found
        for path_node in working_path[right_most_index:]:
            path_keys = None
            if '[' in path_node:
                path_keys = path_node[path_node.find('['):]
                path_node = path_node[:path_node.find('[')]

            if path_node in self.__dict__['_children']:
                node = etree.Element(path_node)
            elif path_node.replace('_', '-') in self.__dict__['_children']:
                log.debug('_longest_path: <underscore_to_hyphen> %s', path_node)
                node = etree.Element(path_node.replace('_', '-'))
            else:
                node = etree.Element(path_node)

            log.debug('_longest_path: creating node %s', path_node)
            parent_node.append(node)
            parent_node = node

            if path_keys:
                for (key, value) in re.findall("\[([^=]*)='([^']+)'\]", path_keys):
                    log.debug('_longest_path: adding listkey to  node %s <%s:%s>', path_node, key, value)
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
        """
        Get the xmlnode from the cache or by xpath lookup.

        This returns a list of elements.
        """
        xmldoc = self.__dict__['_xmldoc']
        log = self.__dict__['_log']
        (keystore_cache, schema_cache) = self.__dict__['_cache']

        if path in keystore_cache.items:
            log.debug('_getxmlnode: %s <hit|%s>', path, str(keystore_cache.items[path]))
            return [keystore_cache.items[path]]

        this_value = xmldoc.xpath(path)
        if not this_value:
            this_value = xmldoc.xpath(path.replace('_', '-'))
            if len(this_value):
                log.debug('_getxmlnode: %s <miss:%s|%s> <underscore_to_hyphen>', path.replace('_', '-'), this_value[0], str(this_value))
                keystore_cache.items[path] = this_value[0]
                return this_value

            log.debug('_getxmlnode: %s <miss:no-value>', path)
            return this_value
        if len(this_value):
            log.debug('_getxmlnode: %s <miss:%s|%s>', path, this_value[0], str(this_value))
            keystore_cache.items[path] = this_value[0]

        log.debug('_getxmlnode: %s <hit|%s>', path, this_value)
        return this_value

    def _getschema(self, path):
        """
        Get information from the schema, returning from the cache if we have previously accessed
        it.

        This will include leaves and yang elements including the addition 'yin-schema' element.
        """
        schema = self.__dict__['_schema']
        log = self.__dict__['_log']
        (keystore_cache, schema_cache) = self.__dict__['_cache']

        if schema_cache.is_path_cached(path):
            this_schema = schema_cache.get_item_from_cache(path)
            log.debug('_getschema: %s <hit|%s>', path, str(this_schema))
            return this_schema

        this_schema = schema.xpath(path)
        if not len(this_schema) and path.count('_'):
            this_schema = schema.xpath(path.replace('_', '-'))
        if not len(this_schema):
            log.debug('_getschema: %s <miss:not-present>', path)
            raise BadVoodoo("Unable to find '%s' in the schema" % (path[1:]))
        elif len(this_schema) > 1:
            log.error('_getschema: %s <miss:too-many-hits> except schema to always give 1 or 0 results.', path)
            raise BadVoodoo("Too many hits for '%s' in the schema" % (path[1:]))

        schema_cache.add_entry(path, this_schema[0])
        return this_schema[0]

    def __repr__(self):
        return 'Voodoo'+self._voodoo_type+': ' + self.__dict__['_valuepath'][1:]


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
        log = self.__dict__['_log']
        schemapath = self.__dict__['_schemapath']
        valuepath = self.__dict__['_valuepath']
        schema = self.__dict__['_schema']
        xmldoc = self.__dict__['_xmldoc']
        thisschema = self.__dict__['_thisschema']
        cache = self.__dict__['_cache']
        (keystore_cache, schema_cache) = cache

        spath = schemapath
        vpath = valuepath

        keys = []
        # This is pretty shcoking
        for x in thisschema.getchildren():
            if x.tag == 'yin-schema':
                for y in x.getchildren():
                    for z in y.getchildren():
                        if z.tag == 'key' and 'value' in z.attrib:
                            keys = z.attrib['value'].split(' ')

        if not keys:
            raise BadVoodoo('Trying to inspect schema for keys but did not find them. %s' % (spath))

        if not len(keys) == len(args):
            raise BadVoodoo('Wrong Number of keys require %s got %s. keys defined: %s' % (len(keys), len(args), str(keys)))

        path_to_list_element = vpath
        ai = 0
        for key in keys:
            path_to_list_element = path_to_list_element + "[" + key + "='" + args[ai] + "']"
            ai = ai+1

        this_value = xmldoc.xpath(path_to_list_element)
        if len(this_value) == 0:
            log.debug('listcreate %s %s <old:no-value>', vpath, str(args))

            new_node = self._find_longest_match_path(xmldoc, path_to_list_element)
        else:
            log.debug('listcreate %s %s <old:exists>', vpath, str(args))
        return CruxVoodooListElement(schema, xmldoc, cache, spath, path_to_list_element,
                                     value=None, root=False, listelement=str(args), log=log,
                                     parent=self)


class CruxVoodooListElement(CruxVoodooBase):

    _voodoo_type = 'ListElement'

    def __repr__(self):
        return 'Voodoo'+self._voodoo_type+': ' + self.__dict__['_valuepath'][1:]
