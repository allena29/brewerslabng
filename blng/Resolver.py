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
    commands - similair to JunOS syntax (i.e.
        set thing xxxx     command=set, path=/thing, value=xxxx
        delete thing       command=delete, path=/thing
        create thing x y   command=create, path=/thing, key1=x, key2=y
        edit thing         command=edit, path=/thing    [work relative to /thing]


    The schema is a bespoke format derrived from Yang (see Munger). It is an inverted version of YIN.
    """

    NAMESPACES = {"yin": "urn:ietf:params:xml:ns:yang:yin:1",
                  "x1": "http://brewerslabng.mellon-collie.net/yang/main",
                  "x2": "http://brewerslabng.mellon-collie.net/yang/types",
                  "x3": "http://brewerslabng.mellon-collie.net/yang/teststub"
                  }
    QUOTED_STRING_REGEX = re.compile("^.* (\"([#~\%\^\&<'\/\?\\>\=\-\@:;\[\]\(\)\{\}a-zA-Z0-9 \*\$!\.\+_\\\"]*)\"$)")
    REGEX_REMOVE_PROPERLY_ESCAPED_CHARACTERS = re.compile('\\[\\" ]')
#    QUOTED_STRING_REGEX = re.compile("([#~%^&<'/?\\>=-@:;[](){}a-zA-Z0-9 *$!.+_\\\"]*)")

    def __init__(self, schema, path_relative_root=''):
        self.path_root = path_relative_root
        format = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)
        self.log = logging.getLogger('cruxresolver')
        self.log.info('Loading CRUX schema')
        self._load_schema(schema)

    def _load_schema(self, schema):
        self.xmldoc = etree.parse(schema).getroot()
        for child in self.xmldoc.getchildren():
            if child.tag == 'inverted-schema':
                self.inverted_schema = child

    def _find_command(self, path):
        command = path[0:path.find(' ')]
        everythingelse = path[len(command)+1:]

        return (command, everythingelse)

    def _find_xpath(self, path):
        """
        This method works left to right to find the XPATH, TYPE, and optional VALUE
        given a string.

        The string we are provided should already have the command prefix stripped
        from it.
        """
        self.log.info('_find_path:   %s', path)

        xpath = ""
        path_split = path.split(' ')
        current_path = self.path_root

        idx = 0
        while idx < len(path_split):
            self.log.info('                   idx %s: %s', idx, path_split[idx])
            current_path = current_path + '/' + path_split[idx]

            self.log.info('                    LOOKING FOR %s', current_path)
        #    for child in self.inverted_schema.getchildren():
        #        self.log.info('xsdfnsdlkfjskldf %s', child.tag)
            # thing = self.inverted_schema.xpath(current_path, namespaces=self.NAMESPACES)
            thing = self.inverted_schema.xpath(current_path[1:])
            """
            Everytime we get a thing we need to inspect the child yin-schema
            to determin the type of the path and then work out what to do from there.

            It could be
             - a leaf   -> then we need to ensure there is a valid quoted/escpaed/simple string following
             """
            if thing:
                (schema, schema_simple_type) = self._get_schema_from_thing(thing[0])

                if schema_simple_type == 'structure':
                    xpath = xpath + '/' + path_split[idx]
                elif schema_simple_type == 'primitive':
                    # value = self._ensure_remaining_path_is_a_properly_escaped_string(path_split, idx+1)
                    (value, string_start_idx, string_end_idx) = self._find_a_quoted_escaped_string(path_split, idx+1)
                    xpath = xpath + '/' + path_split[idx]
                    return (xpath, 'primitive',  value)
                elif schema_simple_type == 'list':
                    xpath = xpath + '/' + path_split[idx]
                    keys = []

                    return (xpath, 'list', keys)
        # raise Error.BlngPathNotValid(path)
            idx = idx + 1
        return (xpath, 'TYOE',  '')

    def _find_a_quoted_escaped_string(self, path_split, start_idx):
        """
        Given a list representing a space separate path, and the index leading up to a suspected
        value, determine if the remaining string is actually properly escaped and quoted (if so
        return the value along with the start and end positions.).
        """
        if len(path_split) == start_idx + 1:
            return (path_split[-1], start_idx + 1, start_idx + 1)

        idx = 0
        end_idx = None
        quoted = False
        if path_split[start_idx][0] == '"':
            quoted = True

        while idx < len(path_split):
            tmp = path_split[idx]
            if quoted and idx == start_idx:
                tmp = path_split[idx][1:]
            if quoted and tmp[-1] == '"':
                tmp = path_split[idx][: -1]
                end_idx = idx
            elif not quoted and not tmp[-1] == '\\':
                end_idx = idx
            tmp = self.REGEX_REMOVE_PROPERLY_ESCAPED_CHARACTERS.sub('', tmp)
            if (quoted and tmp.count('"')) or tmp.count(' ') or tmp.count('/'):
                raise Error.BlngValueNotEscpaedOrQuoted("Unquoted or Unescaped characters " + str(path_split))

            if end_idx:
                return (self._return_clean_string(path_split, start_idx, end_idx), start_idx, end_idx)

            idx = idx+1

        raise Error.BlngValueNotEscpaedOrQuoted("Unquoted or Unescaped characters " + str(path_split))

    def _return_clean_string(self, path_split, start_idx, end_idx):
        """
        From a python list which may include escaped/quoted element we should return
        the exact unquoted, unescpaed string.
        """
        if path_split[start_idx][0] == '"':
            string = path_split[start_idx][1:]
        else:
            string = path_split[start_idx]
        self.log.info('_return clean string %s %s %s', path_split, start_idx, end_idx)
        for idx in range(start_idx+1, end_idx+1):
            string = string + ' ' + path_split[idx]

        if string[-1] == '"':
            string = string[: -1]

        self.REGEX_STRING_ESCAPED_SPACE = re.compile('\\\\ ')
        string = self.REGEX_STRING_ESCAPED_SPACE.sub(' ', string)
        return string

    def _get_schema_from_thing(self, thing):
        """
        Given a XML Element frmo crux-schema of a certain part of the database
        (e.g. /leaf-a)
        It should have a <yin-schema> element which provides information about the node.
        """
        schema_simple_type = 'structure'
        schema = None
        for child in thing.getchildren():
            if child.tag == 'yin-schema':
                schema = child
                for grandchild in child.getchildren():
                    if grandchild.tag == 'leaf':
                        schema_simple_type = 'primitive'
                    if grandchild.tag == 'list':
                        schema_simple_type = 'list'
        if not schema:
            raise ValueError('missing schema')
        return (schema, schema_simple_type)

    def resolve(self, path):
        """
        We convert some kind of string into an XPATH like expression and should return a tuple providing
        - The command which was prefixing the command line
        - The XPATH of the node.
        - The values in a list
        """
        raise NotImplementedError('resolve')
        values = []
        if path.find(' ') == -1:
            return (path, "/", [])

        command = path[0: path.find(' ')]
        path = path[len(command)+1:]
        if command == 'set':
            while self.QUOTED_STRING_REGEX.match(path):
                value = self.QUOTED_STRING_REGEX.sub('\g<1>', path)[1: -1]
                path = path[0: len(path) - len(value)-3]
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
        shallow_path_found = self._find_schema_definition_for_path(xpath)
        self._find_deeper_path(xpath, shallow_path_found)

        # So now we **ONLY** know that the xpath is actually in the schema. but we've gone
        # right to the hsallow end.... we need to go deeper
        return (command, xpath, values)

    def _find_deeper_path(self, xpath, shallow_path_found):
        raise NotImplementedError('finddepperpath')

        """
        ***** HOPEFULLY  **** when this is called we have the same xpath that
        _find_schema_definition_for_path was called
        but we have got a bit more precice already
        But it's probably pretty shitty go get to xpath from shallow_path so we might
        as well just get to xpath from the whole thing.
        """

        raise ValueError("We are going depeer from something with just a memref %s to %s" % (shallow_path_found, xpath))
        # But the problem here is this can be variable it might be a direct parent or a great greate grat grandparent.
        # So this implies we always have ot go fromt he root not just our closest relative!
        raise ValueError('We have a problem here')

    def _find_schema_definition_for_path(self, xpath):
        raise NotImplementedError('findschemaforpathh')
        """
        This method works to find an XMLdoc which gives us the YIN based schema.

        E.g. /morecomplex/leaf2 will at first fail to find /morecomplex/leaf2 but
        will match on /morecomplex because that is a registered top-tag.

        E.g. /ficticiuous/leaf3 will fail because we don't have a regstiered top-tag

        This method can be thought about as working backwards to find the schema.

        **RIGHT NOW** this just doesn't F**Ck up if the thing isn't in the cache.
        **what's in GIT** gives an exception rather than assertions failing.

        """
        xpath_list = xpath.split("/")
        if xpath[0] == "/":
            xpath_list.pop(0)
        while len(xpath_list):
            if Resolver._cache_path_format(xpath_list) in self.path_lookup_cache:
                return self.path_lookup_cache[Resolver._cache_path_format(xpath_list)]
            xpath_list.pop()
        print(self.path_lookup_cache.keys())
        raise Error.BlngPathNotValid(xpath)

    def register_top_tag(self, xpath_top_tag, namespace, module_name):
        raise NotImplementedError('registertoptag')

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
