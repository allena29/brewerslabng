import logging
import os
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
    # IDEA: the unittests associated with this require us to run ./cli first to force the .cache directory to be
    #       populated - we shoudl of course ensure eveyrthing is built with stub data instead.
    """

    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1"}

    def __init__(self):
        self.top_tag_to_module = {}
        self.in_memory = {}
        log_format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=log_format)
        self.log = logging.getLogger('cruxresolver')

    def register_top_tag(self, top_tag, module):
        """
        When we first connect to the CLI we will be able to find a list of top tag's against each
        YANG module.
        """
        self.top_tag_to_module[top_tag] = module

    def show(self, path):
        """
        When we call the show method we expect to take the path (which may be a blank string)
        and will find the configuration of all lower-level children
        """

        if path == '':
            self.load_top_tags_to_memory()

    def load_top_tags_to_memory(self):
        """
        It's entirely possible the consume may ask us for some data right at the top level
        in which case it necessary to load every top tag's schema into memory at this point
        in time.
        """
        for toptag in self.top_tag_to_namesapce:
            self.log.debug("Loading schema for top-tag %s", toptag)
            self.load_schema_to_memory(toptag, self.top_tag_to_namesapce[toptag])

    def load_schema_to_memory(self, tag, module):
        """
        There is a a big assumption made at this point that we have pre-cached all the data and
        from a NETCONF call and have furthermore converted them to a YIN representation.

        At this stage we are just trying to load in the data we need - we probably need namespaces too!
        """
        if module in self.in_memory:
            return module

        self.log.debug("loading schema %s to %s", module, tag)

        if not os.path.exists(".cache/%s.yin" % (module)):
            raise Error.BlngSchemaNotCached(module)

        xmldoc = etree.parse(".cache/%s.yin" % (module))
        module_name = xmldoc.xpath('/yin:module', namespaces=self.NAMESPACES)[0].attrib['name']

        self.in_memory[module_name] = xmldoc
        return module_name
