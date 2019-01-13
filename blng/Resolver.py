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

    def _find_xpath(self, path, xpath="", idx=0, path_split=None):
        """
        This method works left to right to find the XPATH, TYPE, and optional VALUE
        given a string.

        The string we are provided should already have the command prefix stripped
        from it.
        """
        self.log.info('_find_path:   %s', path)

        if not path_split:
            path_split = path.split(' ')

        current_path = self.path_root

        while idx < len(path_split):
            self.log.info('                   idx %s: %s', idx, path_split[idx])
            current_path = current_path + '/' + path_split[idx]
            print('CURRENTPATH', current_path)
            self.log.info('                    LOOKING FOR %s', current_path)
        #    for child in self.inverted_schema.getchildren():
        #        self.log.info('xsdfnsdlkfjskldf %s', child.tag)
            # thing = self.inverted_schema.xpath(current_path, namespaces=self.NAMESPACES)
            thing = self.inverted_schema.xpath(current_path[1:])
            print('DOING ANSWER', thing)
            """
            Everytime we get a thing we need to inspect the child yin-schema
            to determin the type of the path and then work out what to do from there.

            It could be
             - a leaf   -> then we need to ensure there is a valid quoted/escpaed/simple string following
             """
            if thing:
                (schema, schema_simple_type) = self._get_schema_from_thing(thing[0])
                print('SCHEMA', schema, schema_simple_type)
                if schema_simple_type == 'structure':
                    xpath = xpath + '/' + path_split[idx]
                elif schema_simple_type == 'primitive':
                    # value = self._ensure_remaining_path_is_a_properly_escaped_string(path_split, idx+1)
                    (value, string_start_idx, string_end_idx) = self._find_a_quoted_escaped_string(path_split, idx+1)
                    xpath = xpath + '/' + path_split[idx]
                    return (xpath, 'primitive',  value)
                elif schema_simple_type == 'list':
                    print('START OF LIST STUFF', path_split)
                    keys = []
                    xpath = xpath + '/' + path_split[idx]
                    xpath = xpath + '['
                    keys = self._get_list_keys_from_schema(schema)
                    key_idx = idx
                    print('STARTING TO LOOKUP FOR LIST VALUES AT', key_idx)
                    print('GOT KEYS', keys)
                    for key_num in range(len(keys)):
                        (keyname, keyvalue) = keys[key_num]
                        (value, string_start_idx, string_end_idx) = self._find_a_quoted_escaped_string(path_split, key_idx+1)

                        keys[key_num] = (keyname, value)
                        key_idx = string_end_idx + 1
                        if key_num > 0:
                            xpath = xpath + ','
                        xpath = xpath + keyname + "='" + value.replace(' ', '\\ ') + "'"

                        idx = idx + 1
                    xpath = xpath + ']'
                    print(string_start_idx, string_end_idx, len(path_split), path_split)
                    if string_end_idx == len(path_split):
                        return(xpath, 'listelement', keys)
        # raise Error.BlngPathNotValid(path )
            idx = idx + 1

        raise Error.BlngUnableToResolveString(str(path_split))

    def _get_list_keys_from_schema(self, schema):
        keys = []
        for child in schema.getchildren():
            if child.tag == "list":
                for grandchild in child.getchildren():
                    if grandchild.tag == 'key':
                        for key in grandchild.attrib['value'].split(' '):
                            keys.append((key, None))
        return keys

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

    @staticmethod
    def _cache_path_format(path):
        if isinstance(path, list):
            formatted_path = path
        else:
            formatted_path = path.split('/')
            if path[0] == '/':
                formatted_path.pop(0)
        return str(formatted_path)
