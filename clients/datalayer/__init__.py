#!/usr/bin/python3
import traceback as tb

# import libsysrepoPython3 as sr
import sysrepo as sr
import sys
import time


class DataAccess:

    def connect(self):
        self.conn = sr.Connection("%s" % (time.time()))
        self.session = sr.Session(self.conn)
        #self.subscribe = sr.Subscribe(self.session)

    def get(self, xpath):
        sysrepo_item = self.session.get_item(xpath)
        return self._get_python_datatype_from_sysrepo_val(sysrepo_item)

    def _get_python_datatype_from_sysrepo_val(self, valObject):
        """
        For now this is copied out of providers/dataprovider/__init__.py, if this carries on as a good
        idea then would need to combined.

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
        # return valObject.val_to_string()
        if not valObject:
            #print('returning super super early')
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
        elif type == sr.SR_LIST_T or type == sr.SR_CONTAINER_T:
            #print('container or list - returning nothing')
            return None
        elif type == sr.SR_DECIMAL64_T:
            return valObject.data().get_decimal64()
        elif type == sr.SR_LEAF_EMPTY_T:
            #print('empty leaf returning none')
            return None
