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
        self.outstanding_types = {}
        self.outstanding_uses = {}
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('munger')

        if not os.path.exists(".cache/%s.yin" % (module)):
            raise Error.BlngSchemaNotCached(module)

        # The main module we care about
        xmldoc = etree.parse(".cache/%s.yin" % (module)).getroot()

        self.pass1_parse_and_recurse('integrationtest', xmldoc)

        self.pass2_stitch_and_recurse(xmldoc)
        print(self.outstanding_types)
        print(self.outstanding_uses)

    def pass1_parse_and_recurse(self, module_name, xmldoc):
        """The first pass parsing builds an index of groups and typedefs"""
        for child in xmldoc.getchildren():
            #            print(child.tag, child.text, child.attrib.keys())
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}typedef":
                self.log.debug('Adding typedef to the list %s', child.attrib['name'])
                self.outstanding_types["%s:%s" % (module_name, child.attrib['name'])] = child
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}grouping":
                self.log.debug('Adding grouping to the list %s', child.attrib['name'])
                self.outstanding_uses["%s:%s" % (module_name, child.attrib['name'])] = child
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

        prefix_map = {}
        for child in xmldoc.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}import":
                for grandchild in child.getchildren():
                    if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}prefix":
                        prefix_map[grandchild.attrib['value']] = child.attrib['module']

        for child in xmldoc.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}import":
                for grandchild in child.getchildren():
                    if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}prefix":
                        prefix_map[grandchild.attrib['value']] = child.attrib['module']

            self._lookup_method(child)(child)

        print(prefix_map, '<<<<prefix map')

    def handle_container(self, child):
        print("CPONMTINAER", child.attrib.keys(), child.text, child.tag)
        for grandchild in child.getchildren():
            print(grandchild.tag, grandchild.attrib.keys(), grandchild.text)

    def handle_leaf(self, child):
        self.log.debug('TODO workout what to do with leaf types - these ccan be typedefs or unions')
        for grandchild in child.getchildren():
            if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                type = grandchild.attrib['name']
                if type in ('string'):
                    return
                else:
                    raise ValueError("leaf type not recognised ... %s" % (type))

    def handle_null(self, child=None):
        if child:
            print(child.tag, child.text, child.attrib.keys(), "<<<<<<<<<<<<<<<<")
        # pass

    def _lookup_method(self, child):
        if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}leaf":
            return self.handle_leaf
        elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}container":
            return self.handle_container

        return self.handle_null
