import logging
import os
import re
from lxml import etree
import sys
sys.path.append('../')
from blng import Common
from blng import Error


class Munger:

    """
    This class is responsible for munging multiple YIN representations of YANG into a common consistent XML
    document. We will need to set some very clear guidance on a reasonable level of hirerarhcy for typedef's
    etc, groupings etc.

    The Yang module should ensure we have all of the YIN schemas available, chasing through imports -
    therefore this module will just take the happy path.
    """

    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1"}

    def munge(self, module):
        self.typedef_map = {}
        self.grouping_map = {}
        self.trail = []
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('munger')

        if not os.path.exists(".cache/%s.yin" % (module)):
            raise Error.BlngSchemaNotCached(module)

        # The main module we care about
        self.xmldoc = etree.parse(".cache/%s.yin" % (module))
        xmldoc = etree.parse(".cache/%s.yin" % (module)).getroot()
        self.pass1_parse_and_recurse('integrationtest', xmldoc)
        self.pass2_stitch_and_recurse(xmldoc)

        xml_string = str(etree.tostring(xmldoc, pretty_print=True))
        o = open('z.xml', 'w')
        o.write(str(xml_string).replace('\\n', '\n')[2:-1])
        o.close()

    def pass1_parse_and_recurse(self, module_name, xmldoc):
        """The first pass parsing builds an index of groups and typedefs"""
        for child in xmldoc.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}typedef":
                self.log.debug('Adding typedef to the list %s', child.attrib['name'])
                self.typedef_map["%s:%s" % (module_name, child.attrib['name'])] = child
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}grouping":
                self.log.debug('Adding grouping to the list %s', child.attrib['name'])
                self.grouping_map["%s:%s" % (module_name, child.attrib['name'])] = child
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}import":
                self.log.debug('Recursing because of import %s', child.attrib['module'])
                child_xmldoc = etree.parse(".cache/%s.yin" % (child.attrib['module'])).getroot()
                self.pass1_parse_and_recurse(child.attrib['module'], child_xmldoc)

    def pass2_stitch_and_recurse(self, xmldoc):
        """
        Pass 2 should give back a single consistent XML document.

        Everytime we load a new YANG module we build a list which has a key of prefix
        and the associated yang module (i.e. import <module> { prefix <prefix> }; ) in
        YANG terms."""

        self.our_prefix = None
        for child in xmldoc.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}prefix":
                self.our_prefix = child.attrib['value']

        prefix_map = {}
        for child in xmldoc.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}import":
                for grandchild in child.getchildren():
                    if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}prefix":
                        prefix_map[grandchild.attrib['value']] = child.attrib['module']

        children = xmldoc.getchildren()
        for child_index in range(len(children)):
            child = children[child_index]
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}import":
                for grandchild in child.getchildren():
                    if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}prefix":
                        prefix_map[grandchild.attrib['value']] = child.attrib['module']

            new_child = self._lookup_method(child)(child)

    def handle_container(self, child, grandchild_id=-1):
        grandchildren = child.getchildren()
        for grandchild_id in range(len(grandchildren)):
            grandchild = grandchildren[grandchild_id]
            self._lookup_method(grandchild)(grandchild, grandchild_id)

    def handle_leaf(self, child, grandchild_id=-1):
        grandchildren = child.getchildren()

        for grandchild_id in range(len(grandchildren)):
            grandchild = grandchildren[grandchild_id]
            replace_grandchildren = []
            if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                type = grandchild.attrib['name']
                if type in ('string', 'boolean'):
                    custom_type = etree.Element("cruxtype", type=type)
                    child.append(custom_type)
                elif ':' not in type and '%s:%s' % (self.our_prefix, type) in self.typedef_map:
                    for stranger in self.typedef_map['%s:%s' % (self.our_prefix, type)]:
                        if stranger.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                            replace_grandchildren.append((grandchild_id, stranger, grandchild))

                elif ':' in type and type in self.typedef_map:
                    for stranger in self.typedef_map['%s' % (type)]:
                        if stranger.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                            replace_grandchildren.append((grandchild_id, stranger, grandchild))
                else:
                    raise Error.BlngYangTypeNotSupported(type)

        for (index, new_grandchild, old_grandchild) in replace_grandchildren:
            child.insert(index, new_grandchild)
            child.remove(old_grandchild)

    def handle_list(self, child, grandchild_id=-1):
        pass

    def handle_uses(self, child, grandchild_id=-1):
        if ":" not in child.attrib['name']:
            uses = "%s:%s" % (self.our_prefix, child.attrib['name'])
        else:
            uses = "%s" % (child.attrib['name'])
        parent = child.getparent()
        for new_child in self.grouping_map[uses].getchildren():
            parent.append(new_child)
        parent.remove(child)

    def handle_null(self, child=None, grandchild_id=-1):
        pass

    def _lookup_method(self, child):
        if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}leaf":
            return self.handle_leaf
        elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}container":
            return self.handle_container
        if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}list":
            return self.handle_list
        elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}uses":
            return self.handle_uses
        elif child.tag in ("{urn:ietf:params:xml:ns:yang:yin:1}namespace", "{urn:ietf:params:xml:ns:yang:yin:1}prefix",
                           "{urn:ietf:params:xml:ns:yang:yin:1}import", "{urn:ietf:params:xml:ns:yang:yin:1}typedef",
                           "{urn:ietf:params:xml:ns:yang:yin:1}grouping"):
            # These things are handled via pass 1
            return self.handle_null
        elif child.tag in ("{urn:ietf:params:xml:ns:yang:yin:1}presence"):
            return self.handle_null

        raise Error.BlngYangSchemaNotSupported(child.tag)
