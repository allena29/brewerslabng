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
    QUOTED_STRING_REGEX = re.compile("^.* (\"([#~\%\^\&<'\/\?\\>\=\-\@:;\[\]\(\)\{\}a-zA-Z0-9 \*\$!\.\+_\\\"]*)\"$)")
#    QUOTED_STRING_REGEX = re.compile("([#~%^&<'/?\\>=-@:;[](){}a-zA-Z0-9 *$!.+_\\\"]*)")

    def __init__(self):
        self.top_tag_to_module = {}
        self.path_lookup_cache = {}
        self.namespace_to_module = {}
        self.module_cache = {}

        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('cruxresolver')

    def resolve(self, path):
        """
        We convert some kind of string into an XPATH like expression and should return a tuple providing
        - The command which was prefixing the command line
        - The XPATH of the node.
        - The values in a list
        """
        values = []
        if path.find(' ') == -1:
            return (path, "/", [])

        command = path[0:path.find(' ')]
        path = path[len(command)+1:]
        if command == 'set':
            while self.QUOTED_STRING_REGEX.match(path):
                value = self.QUOTED_STRING_REGEX.sub('\g<1>', path)[1:-1]
                path = path[0:len(path) - len(value)-3]
                values.insert(0, value)

        xpath = "/"
        xpath_parts = path.split(' ')
        for tmp in xpath_parts:
            xpath = xpath + tmp + "/"
        xpath = xpath[: -1]

        # TODO: now we need to validate if the path is valid - if it's not valid then we could have
        # a non-quoted set value

        # The biggest problem right now is what do we look up against.
        # If we start looking up against the YANG schema we are back in the same problems
        # as the last set of tries
        # If we look up against the netopeer2 we are highly suboptimalself.
        #
        # The current logic we have in here might be ok for
        # set morecomplex list keya keyb
        # but what will probably break is
        # set list-outside keya list-insider keyb
        # we somehow need to cancel out the keys everytime we look at something.
        self._find_schema_definition_for_path(xpath)

        return (command, xpath, values)

    def _find_schema_definition_for_path(self, xpath):
        """
        This method works to find an XMLdoc which gives us the YIN based schema.

        E.g. /morecomplex/leaf2 will at first fail to find /morecomplex/leaf2 but
        will match on /morecomplex because that is a registered top-tag.

        E.g. /ficticiuous/leaf3 will fail because we don't have a regstiered top-tag

        This method can be thought about as working backwards to find the schema.
        """
        xpath_list = xpath.split("/")
        if xpath[0] == "/":
            xpath_list.pop(0)
        while len(xpath_list):
            if Resolver._cache_path_format(xpath_list) in self.path_lookup_cache:
                raise ValueError(" what we want to add here is a path_lookup_cache of %s which takes us to the schema place of this thing (excluding list keys) " % (xpath))
                return
            xpath_list.pop()
        print(self.path_lookup_cache.keys())
        raise Error.BlngPathNotValid(xpath)

    def register_top_tag(self, xpath_top_tag, namespace, module_name):
        """
        Registering at top_tag will populate the following structures.

        namespace_to_module[<yang-namespace>] = module_name
        path_lookup_cache[<xpath of top-level tag>] = XML YIN representation of yang

        TODO: we must validate to make sure we don't allow overlapping tags
        """
        self.namespace_to_module[namespace] = module_name
        self._load_schema_to_memory(module_name)

        self.path_lookup_cache[Resolver._cache_path_format(xpath_top_tag)] = self.module_cache[module_name]

    def _load_schema_to_memory(self, module_name):
        """
        There is a a big assumption made at this point that we have pre-cached all the data and
        from a NETCONF call and have furthermore converted them to a YIN representation.

        At this stage we are just trying to load in the data we need - we probably need namespaces too!
        """
        self.log.debug("loading schema %s to memory", module_name)

        if module_name in self.module_cache:
            return (module_name, self.module_cache[module_name])

        if not os.path.exists(".cache/%s.yin" % (module_name)):
            raise Error.BlngSchemaNotCached(module_name)

        xmldoc = etree.parse(".cache/%s.yin" % (module_name))
        module_name = xmldoc.xpath('/yin:module', namespaces=self.NAMESPACES)[0].attrib['name']
        self.module_cache[module_name] = xmldoc
        return (module_name, self.module_cache[module_name])

    @staticmethod
    def _cache_path_format(path):
        if isinstance(path, list):
            formatted_path = path
        else:
            formatted_path = path.split('/')
            if path[0] == '/':
                formatted_path.pop(0)
        return str(formatted_path)
