import logging
import sys
sys.path.append("../")
from blng import Common

from lxml import etree


class cruxresolver:

    """
    This class is responsible for resolving and validating paths against a schema.

    The typical use case for this will be the CLI engine which will provide 'space' separated
    commands.

    The schema is typically expressed as YANG files which are most natively scraped via
    the NETCONF get schema operation.

    When this module is first called there will be some overhead as we will have to load
    in a number of modules
    # IDEA: we could pickle the answers.
    """

    def __init__(self):
        self.top_tag_to_namesapce = {}
        self.in_memory = {}
        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger('cruxresolver')

    def register_top_tag(self, top_tag, namespace):
        self.top_tag_to_namesapce[top_tag] = namespace

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
            self.log.debug("Loading schema for top-tag %s" % (toptag))
            self.load_schema_to_memory(toptag, self.top_tag_to_namesapce[toptag])

    def load_schema_to_memory(self, tag, namespace):
        self.log.debug("loading schema %s to %s" % (namespace, tag))
        module = 'integrationtest'
        xml = etree.parse(".cache/%s.schema" % (module))
        xml_root = xml.getroot()

        # There seems to be no optimal answers - so we will just get on and convert to YIN instead.
        # Unlike YIN munger which we were using before this at least is a hell of a lot more dynamic
        # based upon what is happening
        yang = xml_root.getchildren()[0].text
        self.log.debug("Retreived a YANG schema of %s" % (yang))
        with open('.cache/%s.yang' % (module), 'w') as file:
            file.write(yang)

        pyang_command = "pyang -p .cache -f yin .cache/%s.yang" % (module)
        Common.shell_command(pyang_command)
