from ncclient import manager
from ncclient.xml_ import *
from lxml import etree
import logging
import sys
import warnings
import re
warnings.simplefilter("ignore", DeprecationWarning)
from Voodoo import BadVoodoo, CruxVoodooCache, LogWrap


class VoodooXInternal:

    def __init__(self, schema_from_file=None, schema_from_string=None):
        self.netconf = None
        self.data = None
        self.schema = None
        self.namespace = None
        self.basepath = ''
        self.log = LogWrap()
        self.schema_cache = CruxVoodooCache(self.log)

        if schema_from_file:
            schema_to_load = etree.parse(schema_from_file).getroot()
        elif schema_from_string:
            schema_to_load = etree.fromstring(schema_from_string)

        for child in schema_to_load.getchildren():
            if child.tag == 'inverted-schema':
                self.schema = etree.Element('vooschema')
                for grandchild in child.getchildren():
                    self.schema.append(grandchild)

        if self.schema is None:
            raise BadVoodoo("Unable to find the schema")

    def _convert_path_to_xml_filter(self, path):
        """
        This implementation is pretty shocking, there must be a library which can take xpath expression
        and construct the xml sekelton from it!
        TODO: BIG TODO
        """
        xml = ""
        # Note: we can have http:// as a value in a xpath match condition
        path_nodes = []
        path_keys = []

        portions = path.split('/')

        idx = 1
        while idx < len(portions):
            portion = portions[idx]

            if portion.count('[') and portion[-1] == ']':
                path_nodes.append(portion.split('[')[0])
                path_keys.append([])
                key_val_portions = portion.split("',")
                kidx = 0
                while kidx < len(key_val_portions):
                    if kidx == 0:
                        key_val_portion = key_val_portions[0][key_val_portions[0].find('[')+1:]+"'"
                        print(key_val_portion, '*******')
                    elif kidx == len(key_val_portions)-1:
                        key_val_portion = key_val_portions[kidx][:-1]
                    else:
                        key_val_portion = key_val_portions[kidx]+"'"
                    print(key_val_portion, '*********')

                    k = key_val_portion.split('=')[0]
                    v = key_val_portion.split('=')[1][1:-1]
                    path_keys[-1].append((k, v))
                    kidx = kidx + 1

            else:
                path_nodes.append(portion)
                path_keys.append([])
            idx = idx + 1

        # we actually don't need namespaces when reading.
        xml = xml + """<%s xmlns="%s">""" % (path_nodes[0], self.namespace)
        # xml = xml + """<%s>""" % (path_nodes[0])
        idx = 0
        for path_node in path_nodes[1:]:
            xml = xml + "<%s>" % (path_node)
            for (key, val) in path_keys[idx]:
                xml = xml + "<%s>%s</%s>" % (key, val, key)
            idx = idx + 1
        path_nodes.reverse()
        for path_node in path_nodes:
            xml = xml + "</%s>" % (path_node)

        return xml

    def _netconf_get(self, path):
        self.log.info('get (TODO: PATH not taken care of)')
        if path == '/':
            path = ''
        path_to_get = '/' + self.parentnode + path
        self.log.info(path_to_get)
        xml_filter = """<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (self._convert_path_to_xml_filter(path_to_get))
        data = self.netconf.get(filter=xml_filter).data.getchildren()[0]
        return data


class VoodooX(VoodooXInternal):

    """
    Example netconf get
         <data>
           <morecomplex xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
            <nonconfig>hello</nonconfig>
          </morecomplex>
          <voodoox xmlns="http://brewerslabng.mellon-collie.net/yang/vododoox">
            <morecomplex>
              <leaf2>true</leaf2>
              <leaf4>A</leaf4>
            </morecomplex>
          </voodoox>
        </data>
    """

    def connect(self, host='127.0.0.1', port=830, username='netconf', password='netconf'):
        self.netconf = manager.connect(host=host, port=port, username=username, password=password,
                                       hostkey_verify=False, allow_agent=False, unknown_host_cb=lambda x: True,
                                       look_for_keys=False)

    def get_root(self, node, namespace):
        """
        Get a 'root' object parented at the given node/namepsace from the netconf servers point
        of view.
        """
        self.namespaces = {node: namespace}
        self.namespace = namespace
        self.parentnode = node
        self.data = self._netconf_get('/')

        return VoodooXroot(self)


class VoodooXnode:

    TYPE = 'node'

    def __init__(self, internal, valuepath='', schemapath=''):
        self.__dict__['_internal'] = internal

        if self.TYPE == 'root':
            valuepath = '/' + internal.parentnode + ':' + internal.parentnode
            schemapath = '/vooschema/' + internal.parentnode
            internal.basepath = valuepath
        self.__dict__['_vpath'] = valuepath
        self.__dict__['_spath'] = schemapath
        self.__dict__['_elements'] = None

    def _cosmetic_path_name(self, path):
        internal = self.__dict__['_internal']
        return path[len(internal.basepath):]

    def _getschema(self, path):
        """
        Get information from the schema, returning from the cache if we have previously accessed
        it.

        This will include leaves and yang elements including the addition 'yin-schema' element.
        """
        internal = self.__dict__['_internal']

        if internal.schema_cache.is_path_cached(path):
            this_schema = internal.schema_cache.get_item_from_cache(path)
            internal.log.debug('_getschema: %s <hit|%s>', path, str(this_schema))
            return this_schema

        this_schema = internal.schema.xpath(path)
        if not len(this_schema) and path.count('_'):
            this_schema = internal.schema.xpath(path.replace('_', '-'))
            if len(this_schema) == 0:
                raise BadVoodoo("Unable to find '%s' in the schema" % (path[10:]))
            internal.schema_cache.add_entry(path, this_schema[0])
            internal.log.debug('_getschema: %s <miss:%s> <underscore_to_hyphen>', path.replace('_', '-'), str(this_schema[0]))
            return this_schema[0]
        if not len(this_schema):
            internal.log.debug('_getschema: %s <miss:not-present>', path)
            raise BadVoodoo("Unable to find '%s' in the schema" % (path[10:]))
        elif len(this_schema) > 1:
            internal.log.error('_getschema: %s <miss:too-many-hits> except schema to always give 1 or 0 results.', path)
            raise BadVoodoo("Too many hits for '%s' in the schema" % (path[10:]))

        internal.schema_cache.add_entry(path, this_schema[0])
        internal.log.debug('_getschema: %s <miss:%s>', path.replace('_', '-'), str(this_schema[0]))
        return this_schema[0]

    def _getchildren(self, object):
        return object.getchildren()

    def __repr__(self):
        internal = self.__dict__['_internal']
        vpath = self.__dict__['_vpath']
        namespace = internal.namespace
        return 'VoodooX' + self.TYPE + '{' + namespace + '}' + self._cosmetic_path_name(vpath)

    def __dir__(self):
        internal = self.__dict__['_internal']
        vpath = self.__dict__['_vpath']
        spath = self.__dict__['_spath']
        print('Get schema path', spath)
        schema = self._getschema(spath)

        listing = []
        for dchild in self._getchildren(schema):
            listing.append(dchild.tag.replace('-', '_'))
        return listing

        items = []
        """
        Each tagged XML node here will be namespace prefixes.
            {http://brewerslabng.mellon-collie.net/yang/vododoox}morecomplex


        Note: in this implementation we only provide leaves/containers of children which are
        actually populated in the data. With the schema we could return everything (as Voodoo does)
        """
        for child in internal.data.getchildren():
            items.append(child.tag[len(internal.namespace)+2:])

        return items

    def __getattr__(self, attr):
        elements = self.__dict__['_elements']
        vpath = self.__dict__['_vpath']
        internal = self.__dict__['_internal']

        print('getattr-called for', self, attr, vpath)
        """
        Very crude logic without a schema
         1) if we have children we must be some kind of structure (like a list/container)
         2) if we don't have children we return none
        """
        print(etree.tostring(internal.data))
        if not elements:
            vpath_to_find = '//' + internal.parentnode + ':' + internal.parentnode + '/' + internal.parentnode+':'+attr
            print('xpath to find', vpath_to_find)
            elements = internal.data.xpath(vpath_to_find, namespaces=internal.namespaces)

            print(elements)
        if attr in elements:
            if len(elements[attr].getchildren()):
                raise ValueError('todo')
            else:
                return elements[attr].text


class VoodooXroot(VoodooXnode):

    TYPE = 'root'


class BadVoodoo(Exception):

    def __init__(self, message):
        super().__init__(message)


if __name__ == '__main__':

    session = VoodooX('crux-example.xml')
    session.connect()
    print(session)
    # root = session.get_root('morecomplex', 'http://brewerslabng.mellon-collie.net/yang/integrationtest')
    # print(root)
    root = session.get_root('voodoox', 'http://brewerslabng.mellon-collie.net/yang/vododoox')
    print(root)
    print(dir(root))
    print(root.morecomplex)
