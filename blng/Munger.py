import logging
import os
import re
from lxml import etree
import sys
sys.path.append('../')
from blng import Error


class Munger:

    """
    This class is responsible for munging multiple YIN representations of YANG into a common consistent XML
    document. We will need to set some very clear guidance on a reasonable level of hirerarhcy for typedef's
    etc, groupings etc.

    The Yang module should ensure we have all of the YIN schemas available, chasing through imports.

    Once the munger has combined the YIN Module is inverted.
        <leaf name="name-of-leaf">        we have    <name-of-leaf>
           <type name="string"/>                        <yin-schema>
                                                            <type name="string"/>
                                                        </yin-schema>
        </leaf>                                      </name-of-leaf>

    This module only ever acts on a single YIN module at any time - however it should be simple for something
    else to stitch things together (it should require nothing more than just appending each YIN module).

    In addition we will wrap this as
        <crux-schema>
            <inverted-schema>
            </inverted-schema>
            <crux-paths>
                <path>/name-of-leaf</path>
            </crux-paths>
        </crux>
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

        self.pass1_parse_and_recurse(module, xmldoc)
        self.pass2_stitch_and_recurse(xmldoc)
        self.pass3(xmldoc)
        newxmldoc = self.pass4(xmldoc)
        self.pass5(newxmldoc)
        self.pass6(newxmldoc)
        return (xmldoc, newxmldoc)  # , newxmldoc

    def pass6(self, newxmldoc):
        """
        This works throuhg the YANG module to add paths as an attribute into each yin-schema
        node. e.g. <yin-schema path="/simpleleaf">
        """
        pathlist = []
        paths = {}
        self._path_recursor(newxmldoc, pathlist, paths)
        pathxml = etree.fromstring("""<crux-paths xmlns="urn:ietf:params:xml:ns:yang:yin:1"></crux-paths>""")
        for path in paths:
            if not path == '/':

                node = etree.Element('path')
                node.text = path
                pathxml.append(node)
        newxmldoc.append(pathxml)

    def _path_recursor(self, newxmldoc, pathlist, paths):
        for child in newxmldoc.getchildren():
            if child.tag not in ('yin-schema'):
                pathlist.append(child.tag.replace('{urn:ietf:params:xml:ns:yang:yin:1}', ''))
                this_path = '/'.join(pathlist)[15:]
                for grandchild in child.getchildren():
                    if grandchild.tag == 'yin-schema':
                        grandchild.attrib['path'] = this_path
                paths[this_path] = 1
                self._path_recursor(child, pathlist, paths)
                pathlist.pop()

    def pass5(self, newxmldoc):
        """
        This method aims to condense down the schema, particularly things like groups which appear
        but since we have already expanded the schema this just leads to a more confusing and verbose
        than necessary.

        TODO: we need to pick interesting things from yin-schema - if a leaf has regular expressesions
        or complex types, crux:info's etc these need to included.
        """

        for child in newxmldoc.getchildren():
            if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}grouping":
                newxmldoc.remove(child)
                for grandchild in child.getchildren():
                    newxmldoc.append(grandchild)
            elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}choice":
                parent = newxmldoc.find('..')
                grandparent = parent.find('..')
                grandparent.remove(parent)
                for stepchild in parent.getchildren():
                    if not stepchild.tag == 'yin-schema':
                        for grandstepchild in stepchild.getchildren():
                            if not grandstepchild.tag == 'yin-schema':
                                grandparent.append(grandstepchild)

            elif child.tag == "yin-schema":
                for grandchild in child.getchildren():
                    keep_grandchildren = False
                    for great_grandchild in grandchild.getchildren():
                        if great_grandchild.tag == "{urn:ietf:params:xml:ns:yang:yin:1}type" and great_grandchild.attrib['name'] == 'union':
                            keep_grandchildren = True

                    if keep_grandchildren is False:
                        for great_grandchild in grandchild.getchildren():
                            if great_grandchild.tag not in ("{urn:ietf:params:xml:ns:yang:yin:1}type",
                                                            "{urn:ietf:params:xml:ns:yang:yin:1}default",
                                                            "{urn:ietf:params:xml:ns:yang:yin:1}presence",
                                                            "{urn:ietf:params:xml:ns:yang:yin:1}pattern",
                                                            "{urn:ietf:params:xml:ns:yang:yin:1}enum",
                                                            "{urn:ietf:params:xml:ns:yang:yin:1}key",
                                                            "{urn:ietf:params:xml:ns:yang:yin:1}config",
                                                            "{urn:ietf:params:xml:ns:yang:yin:1}mandatory"):
                                grandchild.remove(great_grandchild)

            self.pass5(child)

    def pass4(self, xmldoc):
        """
        The inversion recursion turns a YIN document inside out, rather than indexing the
        document by the tyoe (i.e. <leaf>) with the name inside as an attribute each element
        is named by it's true name. The YIN structure is then provided as a child in a new
        <yin-schema>.

        We only recurse for containers and lists
        """
        newxmldoc = etree.fromstring("""<inverted-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1"></inverted-schema>""")
        self._inversion_recursor(xmldoc, newxmldoc)

        cruxxmldoc = etree.fromstring("""<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1"></crux-schema>""")
        cruxxmldoc.append(newxmldoc)
        return cruxxmldoc

    def _inversion_recursor(self, xmldoc, newxmldoc):
        for child in xmldoc.getchildren():
            if 'name' in child.attrib:
                newnode = etree.Element(str(child.attrib['name']))
                yin = etree.Element('yin-schema')
                yin.append(etree.fromstring(etree.tostring(child)))
                newnode.append(yin)
                newxmldoc.append(newnode)

                if child.tag in ('{urn:ietf:params:xml:ns:yang:yin:1}container',
                                 '{urn:ietf:params:xml:ns:yang:yin:1}list',
                                 '{urn:ietf:params:xml:ns:yang:yin:1}grouping',
                                 '{urn:ietf:params:xml:ns:yang:yin:1}choice',
                                 '{urn:ietf:params:xml:ns:yang:yin:1}case'):
                    self._inversion_recursor(child, newnode)
                # else:
                #     print(child, child.text, child.attrib.keys(), child.tag, "<<<<< inverstion recursor - skipping recursor")
            # else:
                # print(child, child.text, child.attrib.keys(), child.tag, "<<<<< inverstion recursor (no name tag)")

    def pretty(self, xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    def pass3(self, xmldoc):
        for (index, new, old, parent) in self.replacements:
            if parent is not None:
                parent.append(new)
                try:
                    parent.remove(old)
                except:
                    pass

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

    def handle_case(self, child, grandchild_id=-1):
        pass

    def handle_choice(self, child, grandchild_id=-1):
        grandchildren = child.getchildren()
        for grandchild_id in range(len(grandchildren)):
            grandchild = grandchildren[grandchild_id]
            self._lookup_method(grandchild)(grandchild, grandchild_id)

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

    def strip_xmlns(self, xmlstr):
        REGEX_COLON_TAGS = re.compile("<([^>]+:[^>]+)>")
        REGEX_XMLNS = re.compile('xmlns.*="[^"]+"')
        for replacement in REGEX_COLON_TAGS.findall(xmlstr):
            xmlstr = xmlstr.replace(replacement, replacement.replace(':', '__'))
        for xmlns in REGEX_XMLNS.findall(xmlstr):
            xmlstr = xmlstr.replace(xmlns, '')
        xmlstr = xmlstr.replace(' >', '>')
        return xmlstr

    def _lookup_method(self, child):
        if child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}leaf":
            return self.handle_leaf
        elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}container":
            return self.handle_container
        elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}choice":
            return self.handle_choice
        elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}case":
            return self.handle_case
        elif child.tag == "{urn:ietf:params:xml:ns:yang:yin:1}list":
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
        elif child.tag in ("{urn:ietf:params:xml:ns:yang:yin:1}description"):
            return self.handle_null
        elif child.tag in ("{urn:ietf:params:xml:ns:yang:yin:1}extension"):
            return self.handle_null

        raise Error.BlngYangSchemaNotSupported(child.tag)
