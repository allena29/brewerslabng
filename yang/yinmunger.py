#!/usr/bin/python

"""
The goal of this munger is to provide a python object representing a YANG model,
we want to have consumers of this object (CLI) be able to simple traverse a tree
based object structure without having to worry about chasing imports.

The key elements which are collapsed are typedef's and grouping's. 

TODO: add protection against circular references
"""


import argparse
import logging
import os
import re
import sys
from lxml import etree


class yinloader:

    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1"}

    """
    This module loads a yin module and parses it into an object we can use.
    At this moment we just return a lxml object - but in the future we may do something
    different.
    
    TODO: in unit tests push in from io import BytesIO;  some_file_or_file_like_object = BytesIO(b"<root>data</root>")
    """

    def __init__(self):
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger('yinmunger')

    def convert(self, filename):
        self.log.info('Pass 1... %s' % (filename))
        raw = open("%s" % (filename)).read().encode('UTF-8')
        converted = etree.fromstring(raw)
        module_name = converted.xpath('/yin:module', namespaces=self.NAMESPACES)[0].attrib['name']
        return converted, module_name


class munger:

    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1"}

    def __init__(self):
        self.index = {}
        self.groupings = {}
        self.types = {}

        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger('yinmunger')

    def _xpath(self, obj, path, attrib=None, namespaces=None):
        """A convenience function to do an xpath query with default namespaces set"""
        if not namespaces:
            namespaces = self.NAMESPACES

        xpath_results = obj.xpath(path, namespaces=namespaces)
        if attrib:
            if len(xpath_results) > 1:
                raise ValueError("XPATH query: %s returned %s results cannot return %s" % (path, len(xpath_results), attrib))
            return xpath_results[0].attrib[attrib]

        return xpath_results

    def assemble(self, parent_module):
        """
        This method after having every yin model converted into something we have
        eaily accessible this method is responsible for properly munging everything.
        """

        for module_name in self.index:
            module = self.index[module_name]
            self.inspect_common_elements(module_name, module)

        for module_name in self.index:
            module = self.index[module_name]
            self.substitute_typedefs(module)

        module = self.index[parent_module]
        #module_prefix = self._xpath(module, '/yin:module/yin:prefix', 'value')

        doc = etree.Element('root')
        self.recurse(doc, module)

        print(self.pretty_xml(etree.tostring(doc)))

    def substitute_typedefs(self, module):
        """
        This method will go through each module and replace typedefs with the type data
        itself.
        """
        for child in module.getchildren():
            for grandchild in child.getchildren():
                print(grandchild.tag)
                if grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type":
                    print(child.attrib['name'], grandchild.text, grandchild.attrib['name'])
                    print(self.types.keys())

    def inspect_common_elements(self, module_name, module):
        """
        This method goes through the yang modules we have in the index and pulls out
        type-def's and grouping's so that assmeble can stitch them in
        """
        module_prefix = self._xpath(module, '/yin:module/yin:prefix', 'value')
        self.log.debug('inspecting common elements %s' % (module_prefix))

        for child in module.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}grouping":
                self.groupings["%s:%s" % (module_name, child.attrib['name'])] = child
                self.log.debug('Indexing grouping %s:%s' % (module_name, child.attrib['name']))
#                self.index_grouping
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}typedef":
                self.types["%s:%s" % (module_name, child.attrib['name'])] = child
                self.log.debug('Indexing typedef %s:%s' % (module_name, child.attrib['name']))

    def pretty_xml(self, xml_string):
        xml_string = str(xml_string)
        ns_tag = re.compile('<ns\d+:')
        for x in ns_tag.findall(xml_string):
            xml_string = xml_string.replace(x, '<')

        ns_tag = re.compile('</ns\d+:')
        for x in ns_tag.findall(xml_string):
            xml_string = xml_string.replace(x, '</')

        return str(xml_string[2:-1].replace('\\n', '\n'))

    def recurse(self, doc, module):
        """
        This method will recurse through the YANG module and try to collapse grouping/typedefs.
        TODO: we may add in CLI baed metadata here too
        """

        for child in module.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}import":
                pass
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}uses":
                self.log.debug('need to use.... %s' % (child.attrib['name']))
                for grandchild in self.groupings[child.attrib['name']]:
                    doc.append(grandchild)
            else:
                doc.append(child)

                self.recurse(child, child)

    def parse_from_directory(self, yin):
        for file in os.listdir(yin):
            converter = yinloader()
            converted, module_name = converter.convert("%s/%s" % (yin, file))
            self.index[module_name] = converted


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Munge some YIN from some YANG into another kinda thing')
    parser.add_argument('--parent', dest='parent', required=True,
                        help='The parent yang module sum the integers')
    parser.add_argument('--yin', dest='yin', required=True,
                        help='The directory providing the YIN files')
    args = parser.parse_args()
    munger = munger()
    munger.parse_from_directory(args.yin)
    munger.assemble(args.parent)
