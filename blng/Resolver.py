import logging
import os
import re
import sys
sys.path.append("../")
from blng import Common
from blng import Error
from lxml import etree


class Resolver:

    """
    This class is responsible for resolving and validating paths against a schema.

    The typical use case for this will be the CLI engine which will provide 'space' separated
    commands.

    The schema is typically expressed as YANG files which are most natively scraped via
    the NETCONF get schema operation.

    When this module is first called there will be some overhead as we will have to load
    in a number of modules
    # IDEA: we could pickle the answers.
    # TODO: the unittests associated with this require us to run ./cli first to force the .cache directory to be
    #       populated - we shoudl of course ensure eveyrthing is built with stub data instead.
    """

    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1"}
    QUOTED_STRING_REGEX = re.compile("^.*\"([#~\%\^\&<'\/\?\\>\=\-\@:;\[\]\(\)\{\}a-zA-Z0-9 \*\$!\.\+_\\\"]*)\"")
#    QUOTED_STRING_REGEX = re.compile("([#~%^&<'/?\\>=-@:;[](){}a-zA-Z0-9 *$!.+_\\\"]*)")

    def __init__(self):
        self.top_tag_to_module = {}
        self.in_memory = {}
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('cruxresolver')

    def register_top_tag(self, top_tag, module):
        self.top_tag_to_module[top_tag] = module

    def resolve(self, path):
        """
        We convert some kind of string into an XPATH like expression.
        """
        value = None
        if path.find(' ') == -1:
            command = path
            xpath = "/"
        else:
            command = path[0:path.find(' ')]
            path = path[path.find(' ')+1:]
            if command == 'set' and self.QUOTED_STRING_REGEX.match(path):
                value = self.QUOTED_STRING_REGEX.sub('\g<1>', path)
                path = path[0:len(path) - len(value) - 3]

            xpath = "/"
            xpath_parts = path.split(' ')
            for tmp in xpath_parts:
                xpath = xpath + tmp + "/"
            xpath = xpath[: -1]

        return (command, xpath, value)

    def load_top_tags_to_memory(self, ):
        """
        It's entirely possible the consume may ask us for some data right at the top level
        in which case it necessary to load every top tag's schema into memory at this point
        in time.
        """
        for toptag in self.top_tag_to_namesapce:
            self.log.debug("Loading schema for top-tag %s" % (toptag))
            self.load_schema_to_memory(toptag, self.top_tag_to_namesapce[toptag])

    def load_schema_to_memory(self, tag, module):
        """
        There is a a big assumption made at this point that we have pre-cached all the data and
        from a NETCONF call and have furthermore converted them to a YIN representation.

        At this stage we are just trying to load in the data we need - we probably need namespaces too!
        """
        self.log.debug("loading schema %s to %s", module, tag)

        if not os.path.exists(".cache/%s.yin" % (module)):
            raise Error.BlngSchemaNotCached(module)

        xmldoc = etree.parse(".cache/%s.yin" % (module))
#        xmlroot = xmldoc.getroot()
        module_name = xmldoc.xpath('/yin:module', namespaces=self.NAMESPACES)[0].attrib['name']
        self.in_memory[module_name] = xmldoc
        return module_name
