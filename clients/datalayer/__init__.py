#!/usr/bin/python3
import libyang
import sysrepo as sr
import time


class Types:

    UINT32 = sr.SR_UINT32_T
    UINT16 = sr.SR_UINT16_T
    UINT8 = sr.SR_UINT8_T
    INT32 = sr.SR_INT32_T
    INT16 = sr.SR_INT16_T
    INT8 = sr.SR_INT8_T
    STRING = sr.SR_STRING_T
    DECIMAL64 = sr.SR_DECIMAL64_T
    BOOLEAN = sr.SR_BOOL_T
    ENUM = sr.SR_ENUM_T
    EMPTY = sr.SR_LEAF_EMPTY_T
    PRESENCE_CONTAINER = sr.SR_CONTAINER_PRESENCE_T

    LIBYANG_MAPPING = {
        'string': sr.SR_STRING_T,
        'enumeration': sr.SR_ENUM_T,
        'boolean': sr.SR_BOOL_T
    }


class BlackHoleCache:

    def __init__(self):
        self.items = {}

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
        cache_object = Whatever it wants to be.
        """

        self.items[path] = cache_object

    def empty(self):
        self.items.clear()


class BlackArtNode:

    """
    Constraints:

    Node based access is provided for a particular yang module, whenever we run 'get_root'
    we bind to a particular yang module.

    At 10,000ft level this module acts as a facade around the DataAccess methods get(), gets()
    set() and delete(). We depend heavily on libyang to inspect the schema on each method.

    On calling __getatttr_
      a) non-Primitives (i.e. Containers and Lists) return another Object
      b) Primtiives return the value itself.

    Each time we instantiate an object we store
        - module (the name of the yang module - used when forming the xpath)
        - path (the fully qualified path, maintaining reference to specific elements of lists)
                i.e. /integrationtest:s


    Internal Notes:

      - module    = the name of the yang module (e.g integrationtest)
      - path      = an XPATH expression for the path - with prefixes and values pointing to exact instances
                    of data. This is used for fetching data.... e.g.
                    integrationtest:outsidelist[leafo='its cold outside']/integrationtest:otherinsidelist
                          [otherlist1='uno'][otherlist2='due'][otherlist3='tre']/integrationtest:language
      - spath     = an XPATH expression for the path - with prefixes but no specific instances of data
                    included. This is used for looking up schema definitions.... e.g.
                    /integrationtest:outsidelist/integrationtest:otherinsidelist/integrationtest:language
      - dal       = An instantiated object of DataAccess() - one object used for all access.
      - schema    = A libyang object of the top-level yang module.
      - schemactx = A libyang context object
      - cache     = A cache object to store the schema (assumption here is libyang lookups are expesnive - but
                    that may not be true. For sysrepo data lookup even if it's expensive we would never choose
                    to cache that data.
    """

    NODE_TYPE = 'Node'

    def __init__(self, module, data_access_layer, yang_schema, yang_ctx, path='', spath='', cache=None):
        self.__dict__['_module'] = module
        self.__dict__['_path'] = path
        self.__dict__['_spath'] = spath
        self.__dict__['_schema'] = yang_schema
        self.__dict__['_schemactx'] = yang_ctx
        self.__dict__['_dal'] = data_access_layer
        self.__dict__['_cache'] = cache
        if cache is None:
            self.__dict__['_schemacache'] = BlackHoleCache()
        else:
            self.__dict__['_schemacache'] = cache

    def __name__(self):
        return 'BlackArtNode'

    def __repr__(self):
        return self._base_repr()

    def _base_repr(self):
        module = self.__dict__['_module']
        path = self.__dict__['_path']
        return 'BlackArt%s{%s}' % (self.NODE_TYPE, path)

    def __del__(self):
        path = self.__dict__['_path']
        print('wanting to delete item', path)

    def _form_xpath(self, path, attr):
        """
        When using the schema xpath lookup we need to use the module prefix
        across every part of the path.

        Inside the integrationtest which imports from the yang module teschild we still
        reference those imported elements by the parent module.
         '/integrationtest:imports-in-here/integrationtest:name'
        """
        module = self.__dict__['_module']

        return path + '/' + module + ":" + attr

    def __getattr__(self, attr):
        module = self.__dict__['_module']
        path = self.__dict__['_path']
        spath = self.__dict__['_spath']
        dal = self.__dict__['_dal']
        xpath = self._form_xpath(path, attr)
        spath = self._form_xpath(spath, attr)
        module = self.__dict__['_module'] = module
        schema = self.__dict__['_schema']
        schemactx = self.__dict__['_schemactx']
        cache = self.__dict__['_cache']

        node_schema = self._get_schema_of_path(spath)
        node_type = node_schema.nodetype()

        if node_type == 1:
            # assume this is a container (or a presence container)
            new_xpath = self._form_xpath(path, attr)
            new_spath = spath
            if node_schema.presence() is None:
                return BlackArtContainer(module, dal, schema, schemactx, new_xpath, new_spath, cache)
            else:
                return BlackArtPresenceContainer(module, dal, schema, schemactx, new_xpath, new_spath, cache)
        elif node_type == 4:
            # Assume this is always a primitive
            new_xpath = self._form_xpath(path, attr)
            new_spath = self._form_xpath(spath, attr)
            return dal.get(xpath)
        elif node_type == 16:
            new_xpath = self._form_xpath(path, attr)
            new_spath = spath
            return BlackArtList(module, dal, schema, schemactx, new_xpath, new_spath, cache)

        raise ValueError('Get - not sure what the type is...%s' % (node_type))

    def __setattr__(self, attr, val):
        path = self.__dict__['_path']
        spath = self.__dict__['_spath']
        dal = self.__dict__['_dal']
        xpath = self._form_xpath(path, attr)
        spath = self._form_xpath(spath, attr)

        node_schema = self._get_schema_of_path(spath)
        if val is None:
            print('SET-AUTO-DELETE', xpath)
            dal.delete(xpath)
            return

        print("SET", xpath)
        print(node_schema.type(), '<<<<libyangtype for ', xpath)
        type = Types.LIBYANG_MAPPING[str(node_schema.type())]

        dal.set(xpath, val, type)

    def __dir__(self):
        path = self.__dict__['_path']
        spath = self.__dict__['_spath']
        print('DIR of', path, spath)
        node_schema = self._get_schema_of_path(spath)

        answer = []
        for child in node_schema.children():
            answer.append(child.name())
        answer.sort()
        return answer
        return ['todo']

    def _get_schema_of_path(self, xpath):

        schemacache = self.__dict__['_schemacache']
        schemactx = self.__dict__['_schemactx']

        if xpath == "":
            # Root object won't be a valid XPATH
            return self.__dict__['_schema']

        if schemacache.is_path_cached(xpath):
            return schemacache.get_item_from_cache(xpath)

        schema_for_path = next(schemactx.find_path(xpath))
        schemacache.add_entry(xpath, schema_for_path)
        return schema_for_path


class BlackArtList(BlackArtNode):

    """
    Represents a list from a yang module.

    New entries can be created on this object with the create object, each
    key defined in the yang module should be passed in paying attention to
    the order of the keys.
        (e.g.
        key1 = True
        key2 = False
        root.twokeylist.create(key1, key2)

    To obtain a specific instance from the list call the get method, passing
    each key from the yang module. It is not possible to provide partial keys
    in a hope to get multiple records.

    Note: values for the list keys should be provided as they would in an
    XPATH express. i.e. python True > 'true', False > 'false'

    TOOD: interator
    """

    NODE_TYPE = 'List'

    def create(self, *args):
        module = self.__dict__['_module']
        path = self.__dict__['_path']
        spath = self.__dict__['_spath']

        dal = self.__dict__['_dal']
        module = self.__dict__['_module'] = module
        schema = self.__dict__['_schema']
        schemactx = self.__dict__['_schemactx']
        cache = self.__dict__['_cache']
        conditional = self._get_keys(list(args))
        new_xpath = path + conditional
        new_spath = spath   # Note: we deliberartely won't use conditionals here

        dal.create(new_xpath)
        print('CREATING LIST ELEMENT WIHT SPATH for DIR', spath)
        return BlackArtListElement(module, dal, schema, schemactx, new_xpath,  new_spath, cache)

    def get(self, *args):
        module = self.__dict__['_module']
        path = self.__dict__['_path']
        spath = self.__dict__['_spath']

        dal = self.__dict__['_dal']
        module = self.__dict__['_module'] = module
        schema = self.__dict__['_schema']
        schemactx = self.__dict__['_schemactx']
        cache = self.__dict__['_cache']
        conditional = self._get_keys(list(args))
        new_xpath = path + conditional
        new_spath = spath   # Note: we deliberartely won't use conditionals here
        print('CREATING LIST ELEMENT WIHT SPATH for DIR', spath)
        return BlackArtListElement(module, dal, schema, schemactx, new_xpath,  new_spath, cache)

    def _get_keys(self, *args):
        path = self.__dict__['_path']
        spath = self.__dict__['_spath']
        node_schema = self._get_schema_of_path(spath)
        keys = list(node_schema.keys())

        if not len(args[0]) == len(keys):
            raise ListWrongNumberOfKeys(path, len(keys), len(args[0]))

        conditional = ""
        for i in range(len(keys)):
            value = self._get_xpath_value_from_python_value(args[0][i], keys[i].type())

            print(i, keys[i].type(), value)
            conditional = conditional + "[%s='%s']" % (keys[i].name(), value)
        return conditional

    def _get_xpath_value_from_python_value(self, v, t):
        if str(t) == 'boolean':
            return str(v).lower()
        else:
            return str(v)


class BlackArtListElement(BlackArtNode):

    """
    Represents a specific instance of a list element from a yang module.
    The child nodes are accessible from this node.
    """

    NODE_TYPE = 'ListElement'


class BlackArtContainer(BlackArtNode):
    """
    Represents a Container from a yang module, with access to the child
    elements.
    """

    NODE_TYPE = 'Container'


class BlackArtPresenceContainer(BlackArtNode):

    """
    Represents a PresenceContainer from a yang module, with access to the child
    elements. The exists() method will return True if this container exists
    (either created implicitly because of children or explicitly).
    """

    NODE_TYPE = 'PresenceContainer'

    def exists(self):
        path = self.__dict__['_path']
        dal = self.__dict__['_dal']
        return dal.get(path) is True

    def create(self):
        path = self.__dict__['_path']
        dal = self.__dict__['_dal']
        dal.create_container(path)

    def __repr__(self):
        path = self.__dict__['_path']
        dal = self.__dict__['_dal']
        base_repr = self._base_repr()
        if dal.get(path) is True:
            return base_repr + " Exists"
        return base_repr + " Does Not Exist"


class BlackArtRoot(BlackArtNode):

    NODE_TYPE = 'Root'


class DataAccess:

    """
    This module provides two methods to access data, either XPATH based (low-level) or
    Node based (high-level).

    The backend supported by this module is sysrepo (without netopeer2), however the
    basic constructs decribed by this class could be ported to other backends.

    Dependencies:
     - sysrepo 0.7.7 python3  bindings (https://github.com/sysrepo/sysrepo)
     - libyang 0.16.78 (https://github.com/rjarry/libyang-cffi/)
    """

    def get_root(self, module, path="", yang_location="../yang/"):
        """
        Instantiate Node-based access to the data stored in the backend defined by a yang
        schema. The data access will be constraint to the YANG module chosen when invoking
        this method.

        We must have access to the same YANG module loaded within in sysrepo, which can be
        set by modifying yang_location argument.
        """
        yang_ctx = libyang.Context(yang_location)
        yang_schema = yang_ctx.load_module(module)
        return BlackArtRoot(module, self, yang_schema, yang_ctx, path)

    def connect(self, tag='client'):
        self.conn = sr.Connection("%s%s" % (tag, time.time()))
        self.session = sr.Session(self.conn)

        # self.subscribe = sr.Subscribe(self.session)

    def commit(self):
        self.session.commit()

    def create_container(self, xpath):
        self.set(xpath, None,  sr.SR_CONTAINER_PRESENCE_T)

    def create(self, xpath):
        """
        Create a list item by XPATH including keys
         e.g. / path/to/list[key1 = ''][key2 = ''][key3 = '']
        """
        self.set(xpath, None, sr.SR_LIST_T)

    def set(self, xpath, value, valtype=sr.SR_STRING_T):
        """
        Set an individual item by XPATH.
          e.g. / path/to/item

        It is required to provide the value and the type of the field.
        """
        v = sr.Val(value, valtype)
        self.session.set_item(xpath, v)

    def gets(self, xpath):
        """
        Get a list of xpaths for each items in the list, this can then be used to fetch data
        from within the list.
        """
        vals = self.session.get_items(xpath)
        if not vals:
            raise NodeNotAList(xpath)
        else:
            for i in range(vals.val_cnt()):
                v = vals.val(i)
                yield v.xpath()

    def get(self, xpath):
        sysrepo_item = self.session.get_item(xpath)
        return self._get_python_datatype_from_sysrepo_val(sysrepo_item, xpath)

    def delete(self, xpath):
        self.session.delete_item(xpath)

    def _get_python_datatype_from_sysrepo_val(self, valObject, xpath=None):
        """
        For now this is copied out of providers/dataprovider/__init__.py, if this carries on as a good
        idea then would need to combined.

        Note: there is a limitation here, we can't return False for a container presence node that doesn't
        exist becuase we never will get a valObject for it. Likewise boolean's and empties that dont' exist.

        This is a wrapped version of a Val Object object
        http: // www.sysrepo.org/static/doc/html/classsysrepo_1_1Data.html
        http: // www.sysrepo.org/static/doc/html/group__cl.html  # ga5801ac5c6dcd2186aa169961cf3d8cdc

        These don't map directly to the C API
        SR_UINT32_T 20
        SR_CONTAINER_PRESENCE_T 4
        SR_INT64_T 16
        SR_BITS_T 7
        SR_IDENTITYREF_T 11
        SR_UINT8_T 18
        SR_LEAF_EMPTY_T 5
        SR_DECIMAL64_T 9
        SR_INSTANCEID_T 12
        SR_TREE_ITERATOR_T 1
        SR_CONTAINER_T 3
        SR_UINT64_T 21
        SR_INT32_T 15
        SR_ENUM_T 10
        SR_UNKNOWN_T 0
        SR_STRING_T 17
        SR_ANYXML_T 22
        SR_INT8_T 13
        SR_LIST_T 2
        SR_INT16_T 14
        SR_BOOL_T 8
        SR_ANYDATA_T 23
        SR_UINT16_T 19
        SR_BINARY_T 6

        """
        if not valObject:
            return None
        type = valObject.type()
        if type == sr.SR_STRING_T:
            return valObject.val_to_string()
        elif type == sr.SR_UINT64_T:
            return valObject.data().get_uint64()
        elif type == sr.SR_UINT32_T:
            return valObject.data().get_uint32()
        elif type == sr.SR_UINT16_T:
            return valObject.data().get_uint16()
        elif type == sr.SR_UINT8_T:
            return valObject.data().get_uint8()
        elif type == sr.SR_UINT64_T:
            return valObject.data().get_uint8()
        elif type == sr.SR_INT64_T:
            return valObject.data().get_int64()
        elif type == sr.SR_INT32_T:
            return valObject.data().get_int32()
        elif type == sr.SR_INT16_T:
            return valObject.data().get_int16()
        elif type == sr.SR_INT64_T:
            return valObject.data().get_int8()
        elif type == sr.SR_BOOL_T:
            return valObject.data().get_bool()
        elif type == sr.SR_ENUM_T:
            return valObject.data().get_enum()
        elif type == sr.SR_CONTAINER_PRESENCE_T:
            return True
        elif type == sr.SR_CONTAINER_T:
            raise NodeHasNoValue('container', xpath)
        elif type == sr.SR_LEAF_EMPTY_T:
            raise NodeHasNoValue('empty-leaf', xpath)
        elif type == sr.SR_LIST_T:
            # print('container or list - returning nothing')
            return None
        elif type == sr.SR_DECIMAL64_T:
            return valObject.data().get_decimal64()

        raise NodeHasNoValue('unknown', xpath)


class NodeHasNoValue(Exception):

    """
    Raised when accessing a non-presence container, list, or anything which does not
    have a value.
    A decendent node is could be fetched.
    """

    def __init__(self, nodetype, xpath):
        super().__init__("The node: %s at %s has no value" % (nodetype, xpath))


class NodeNotAList(Exception):

    def __init__(self, xpath):
        super().__init__("The path: %s is not a list" % (xpath))


class ListWrongNumberOfKeys(Exception):

    def __init__(self, xpath, require, given):
        super().__init__("The path: %s is a list requiring %s keys but was given %s keys" % (xpath, require, given))
