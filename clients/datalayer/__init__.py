#!/usr/bin/python3
import traceback as tb

# import libsysrepoPython3 as sr
import libyang
import sysrepo as sr
import sys
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


class BlackArtNode:

    NODE_TYPE = 'Node'

    def __repr__(self):
        module = self.__dict__['_module']
        path = self.__dict__['_path']
        return 'BlackArt%s{%s}' % (self.NODE_TYPE, path)

    def __getattr__(self, attr):
        module = self.__dict__['_module']
        path = self.__dict__['_path']
        dal = self.__dict__['_dal']
        xpath = path + attr

        print(xpath)
        return dal.get(xpath)

        print('want to get attr', attr)

    def __dir__(self):
        schema = self.__dict__['_schema']
        answer = []
        for child in schema.children():
            answer.append(child.name())
        answer.sort()
        return answer
        return ['todo']


class BlackArtRoot(BlackArtNode):

    NODE_TYPE = 'Root'

    def __init__(self, module, data_access_layer, yang_schema, path=''):
        self.__dict__['_module'] = module
        self.__dict__['_path'] = "/" + module + ":" + path
        self.__dict__['_schema'] = yang_schema
        self.__dict__['_dal'] = data_access_layer


class DataAccess:

    def get_root(self, module, path=""):
        yang_ctx = libyang.Context('../yang/')
        yang_schema = yang_ctx.load_module(module)
        return BlackArtRoot(module, self, yang_schema, path)

    def connect(self, tag='client'):
        self.conn = sr.Connection("%s%s" % (tag, time.time()))
        self.session = sr.Session(self.conn)

        # self.subscribe = sr.Subscribe(self.session)

    def commit(self):
        self.session.commit()

    def create(self, xpath):
        """
        Create a list item by XPATH including keys
         e.g. /path/to/list[key1=''][key2=''][key3='']
        """
        self.set(xpath, None, sr.SR_LIST_T)

    def set(self, xpath, value, valtype=sr.SR_STRING_T):
        """
        Set an individual item by XPATH.
          e.g. /path/to/item

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

    def _get_python_datatype_from_sysrepo_val(self, valObject, xpath=None):
        """
        For now this is copied out of providers/dataprovider/__init__.py, if this carries on as a good
        idea then would need to combined.

        Note: there is a limitation here, we can't return False for a container presence node that doesn't
        exist becuase we never will get a valObject for it. Likewise boolean's and empties that dont' exist.

        This is a wrapped version of a Val Object object
        http://www.sysrepo.org/static/doc/html/classsysrepo_1_1Data.html
        http://www.sysrepo.org/static/doc/html/group__cl.html#ga5801ac5c6dcd2186aa169961cf3d8cdc

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
