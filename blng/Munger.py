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

    This was very simplisitc, when looking up the schema produced here we don't get a very usable form because
    YIN organises by the type of the element- with name's being an attribute of the the type

    xmlroot.findall('/', namespaces=NAMESPACES)
    Out[10]:
    [<Element {urn:ietf:params:xml:ns:yang:yin:1}namespace at 0x1088de638>,
     <Element {urn:ietf:params:xml:ns:yang:yin:1}prefix at 0x1088de170>,
     <Element {urn:ietf:params:xml:ns:yang:yin:1}import at 0x1088cf440>,
     <Element {urn:ietf:params:xml:ns:yang:yin:1}leaf at 0x1088cf2d8>,
     <Element {urn:ietf:params:xml:ns:yang:yin:1}container at 0x1088cffc8>,
     <Element {urn:ietf:params:xml:ns:yang:yin:1}list at 0x1088cfe18>]

     This makes it hard to use xpath's to determine if something is a leaf!
     A potential quick hack would be to think about inverting the xmldoc as a
     pass 4 - but things are getting very tangled already.

     There is at least a consistent xmldoc at the end of mung so it could be the
     least worst option.

    """

    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1"}

    def __init__(self):
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('munger')

    def load_file(self, module):
        if not os.path.exists(".cache/%s.yin" % (module)):
            raise Error.BlngSchemaNotCached(module)

        # The main module we care about
        self.xmldoc = etree.parse(".cache/%s.yin" % (module))
        xmldoc = etree.parse(".cache/%s.yin" % (module)).getroot()
        return xmldoc

    def munge(self, module, xmldoc):
        self.typedef_map = {}
        self.grouping_map = {}
        self.replacements = []
        self.xmldoc = xmldoc

        self.pass1_parse_and_recurse('integrationtest', xmldoc)
        self.pass2_stitch_and_recurse(xmldoc)
        self.pass3(xmldoc)
        newxmldoc = self.pass4(xmldoc)
        return (xmldoc, newxmldoc)  # , newxmldoc

    def pass4(self, xmldoc):
        newxmldoc = etree.fromstring("""<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1"></crux-schema>""")
        self._inversion_recursor(xmldoc, newxmldoc)
        return newxmldoc

    def _inversion_recursor(self, xmldoc, newxmldoc):
        for child in xmldoc.getchildren():
            print(child, child.text, child.attrib.keys(), child.tag, "<<<<< inverstion recursor")
            if 'name' in child.attrib:
                newnode = etree.Element(str(child.attrib['name']))
                yin = etree.Element('yin-schema')
                yin.append(etree.fromstring(etree.tostring(child)))
                newnode.append(yin)
                newxmldoc.append(newnode)

    def pretty(self, xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def save_to_file(self, xmldoc):
        o = open('z.xml', 'w')
        o.write(self.pretty(xmldoc))
        o.close()

    def pass3(self, xmldoc):
        for (index, new, old, parent) in self.replacements:
            if parent is not None:
                parent.append(new)
                try:
                    parent.remove(old)
                except:
                    print('failed to remove', old, 'from', parent)
            else:
                print('skipping', new, old, parent)

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
        YANG terms.

        In addition as we recurse we will build lists of replcements we need to make which will
        be process in pass 3.
        """
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

    def handle_type(self, sprog, sprog_id, parent):
        type = sprog.attrib['name']
        if type in ('string', 'boolean', 'uint8', 'uint16', 'uint32', 'enumeration'):
            pass
        # stranger means the typedef itelf
        elif ':' not in type and '%s:%s' % (self.our_prefix, type) in self.typedef_map:
            for stranger in self.typedef_map['%s:%s' % (self.our_prefix, type)]:
                if stranger.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                    self.log.debug('typedef replacement - added to list %s:%s (ourprefix)', self.our_prefix, type)
                    self.replacements.append((sprog_id, stranger, sprog, parent))
                    self.handle_type(stranger, -1, sprog)
        elif ':' in type and type in self.typedef_map:
            for stranger in self.typedef_map['%s' % (type)]:
                if stranger.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                    self.log.debug('typedef replacement - added to list %s', type)
                    self.replacements.append((sprog_id, stranger, sprog, parent))
                    self.handle_type(stranger, -1, sprog)
        elif type == 'union':
            sproglets = sprog.getchildren()
            for sproglet_id in range(len(sproglets)):
                sproglet = sproglets[sproglet_id]
                if sproglet.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                    self.handle_type(sproglet, sproglet_id, sprog)

        else:
            raise Error.BlngYangTypeNotSupported(type, '?')

    def handle_leaf(self, child, grandchild_id=-1):
        grandchildren = child.getchildren()
        replace_grandchildren = []

        for grandchild_id in range(len(grandchildren)):
            grandchild = grandchildren[grandchild_id]
            if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                self.handle_type(grandchild, grandchild_id, child)

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
