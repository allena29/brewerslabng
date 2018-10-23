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

        self.pass1_parse_and_recurse(xmldoc)

        print(self.outstanding_types)
        print(self.outstanding_uses)

    def pass1_parse_and_recurse(self, xmldoc):
        """The first pass parsing builds an index of groups and typedefs"""
        for child in xmldoc.getchildren():
            #            print(child.tag, child.text, child.attrib.keys())
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}typedef":
                self.log.debug('Adding typedef to the list %s', child.attrib['name'])
                self.outstanding_types[child.attrib['name']] = child
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}grouping":
                self.log.debug('Adding grouping to the list %s', child.attrib['name'])
                self.outstanding_uses[child.attrib['name']] = child
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}import":
                self.log.debug('Recursing because of import %s', child.attrib['module'])
                child_xmldoc = etree.parse(".cache/%s.yin" % (child.attrib['module'])).getroot()
                self.pass1_parse_and_recurse(child_xmldoc)
