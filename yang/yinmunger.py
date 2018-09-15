#!/usr/bin/python

"""
The goal of this munger is to provide a python object representing a YANG model,
we want to have consumers of this object (CLI) be able to simple traverse a tree
based object structure without having to worry about chasing imports. 
"""


import argparse
import logging
import os
import sys
from lxml import etree


class yinloader:

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

    def parse_from_file(self, filename):
        open_file = open(filename)
        converted = self.parse(open_file)
        open_file.close()
        return converted

    def parse(self, file_obj):
        self.log.info('Pass 1... %s' % (file_obj.name))
        tree = etree.parse(file_obj)
        return tree
        #>>> tree = etree.parse(some_file_or_file_like_object)


class munger:


    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1"}


    def __init__(self):
        self.index = {}

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
        parent = self.index[parent_module]
        parent_prefix = self._xpath(parent, '/yin:module/yin:prefix', 'value')

        print('parent_prefix %s' %(parent_prefix))
    def parse_from_directory(self, yin):
        for file in os.listdir(yin):
            converter = yinloader()
            converted = converter.parse_from_file("%s/%s" % (yin, file))

            module_name = converted.xpath('/yin:module', namespaces=self.NAMESPACES)[0].attrib['name']
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
