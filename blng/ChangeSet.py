import re
from lxml import etree


class ChangeSet:

    """
    This class is responsible for creating a list of changes required - this is a
    candidate transaction which will be created when a user wants to configure
    something.

    This class always represents a single transaction.

    It's expected to follow this sequence.

    1) Instantiate ChangSet(crux-schema)
    2) Take key/value changes - storing the old value as well as the new value.
    3) Create an exclusive lock against the NETCONF database.
    4) - Validate that all old values match those stored on the ChangeSet
    4a) - If true then frame an XML document and EditConfig
    4b) - If false then block the commit.

    """

    def __init__(self, crux_schema):
        # self.schema = crux_schema
        self.dirty = False

        self.transaction = {}

    def begin_transaction(self, xmlstr):
        """
        A transaction starts by calling this method and the resulting of making a netconf get_config
        response = netconf.get_config(source='running',
            path = '<integrationtest><simpleleaf/></integrationtest>'
            filter = '< nc: filter xmlns: nc = "urn:ietf:params:xml:ns:netconf:base:1.0" > %s < /nc: filter >' % (path)).data_xml

            <?xml version="1.0" encoding="UTF-8"?>
              <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
                <integrationtest xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
                    <morecomplex><leaf2>true</leaf2><leaf3>234234234</leaf3></morecomplex>
                </integrationtest>
              </data>

        This will be used when calculating diff sets to send as part of the configuration.
        """
        self.transaction = {'keypaths': {},
                            'originalxmldoc': ChangeSet._get_xmldoc_without_xmlns(xmlstr),
                            'xmldoc': ChangeSet._get_xmldoc_without_xmlns(xmlstr)
                            }

    @staticmethod
    def _get_xmldoc_without_xmlns(xmlstr):
        regex_xmlns = re.compile('(xmlns="\S+")')
        for xmlns in regex_xmlns.findall(xmlstr):
            xmlstr = xmlstr.replace(xmlns, '')

        xmldoc = etree.fromstring(xmlstr.encode('UTF-8'))
        return xmldoc

    def modify(self, path, newvalue):
        elements = self.transaction['xmldoc'].xpath('/data'+path)

        if len(elements) != 1:
            ChangeSet._create_elements(path, self.transaction['xmldoc'])
        elements[0].text = newvalue

    @staticmethod
    def _create_elements(path, xmldoc):
        """
        Given an XPATH ensure the nodes are present in the XMLDOC or else create them.

        It's probably easier to go forwards rather than backwards - however it's probably
        more optimal to work backwards with a populated data set..... a hybrid might be
        to search for the last but one and then work forward if that doesn't work.

        Backwards Option:

        end_idx = len(path)
        while end_idx > path.find('/'):
            elements = xmldoc.xpath(path[0:end_idx])
            if len(elements) == 0:
                pass
                # This parth does not exist so we are going to have to create something.

                # And we also would have to deal with list keys
            else:
                path_after = path[end_idx:]
                this_part_to_add = path_after.split('/')[1]
                node = etree.Element(this_part_to_add)
                elements[0].append(node)
                end_idx = len(path)
                print(etree.tostring(xmldoc))
                end_idx = 0
                # raise ValueError('ok' + path[0:end_idx]+'\n'+path_after+'\nNeed to add new node....'+this_part_to_add+'\n'+str(end_idx))

            end_idx = path.rfind('/', 0, end_idx)

        #   raise ValueError('got to the very end')
        return end_idx
        """
        REGEX_LIST_KEYS = re.compile("(.*?)\[(\w+=.*?,?)\]")
        REGEX_XPATH_KEY_VALUES = re.compile("(\w+)='(.*?)',?")

        previous_node = xmldoc
        path_components = path[1:].split('/')
        path_components.pop(0)
        for path_idx in range(len(path_components)):
            # raise ValueError('%s %s %s' % (0, path_idx+1, str(path_components)))
            path_to_find = '/'.join(path_components[:path_idx+1])

            this_path = path_components[path_idx]
            try:
                elements = xmldoc.xpath(path_to_find)
            except etree.XPathEvalError:
                # Note: trying to lookup integrationtest/container-and-lists/multi-key-list[A='aaaa',B='bbbb'] is giving us
                # lxml.etree.XPathEvalError: Invalid predicate
                # If we skip over this the following code which creates the XML elements works for us
                elements = []
            #    raise ValueError('Unable to xpath find\n' + path_to_find+'\n'+str(etree.tostring(xmldoc)))
            if len(elements) == 0:
                xpath_keys = REGEX_LIST_KEYS.findall(this_path)
                if len(xpath_keys):
                    (this_path, xpath_key_and_value) = xpath_keys[0]
                    node = etree.Element(this_path)
                    previous_node.append(node)
                    previous_node = node
#                    raise ValueError("xpath_key_and_value" + xpath_key_and_value + "\n"+str(REGEX_XPATH_KEY_VALUES.findall(xpath_key_and_value)))
                    for (xpath_key, xpath_value) in REGEX_XPATH_KEY_VALUES.findall(xpath_key_and_value):
                        keynode = etree.Element(xpath_key)
                        node.append(keynode)
                        keynode.text = xpath_value
                else:
                    node = etree.Element(this_path)
                    previous_node.append(node)
                    previous_node = node
            else:
                previous_node = elements[0]
        return 4

    def _extract_xpath_keys_and_create_in_xmldoc(path, xmldoc):
        """
        Given an XPATH which may or may not contain keys and an XMLDOC we will create
        elements in the tree corresponding to those XPATH keys.

        self.REGEX_XPATH_KEYS.findall("/integrationtest/simplelist[simplekey='sdf']/nonleafkey")
        ["simplekey='sdf'"]

        self.REGEX_XPATH_KEY_VALUES.findall("simplekey='sdf'")
        [('simplekey', 'sdf')]

        TODO: this is where we are at... we are oassed ab XMLDOC but we aren't putting this in the right position.
        TOOD: we also need to recurse a little bit as we assume that we could have multiple lists.
        """
        raise ValueError('Deprecate this'
                         )
        REGEX_XPATH_KEYS = re.compile("\[(\w+='.*?')\]")
        REGEX_XPATH_KEY_VALUES = re.compile("(\w+)='(.*?)',?")

        xpath_keys = []

        idx = 0
        xpath_keys_and_values = REGEX_XPATH_KEYS.findall(path)
        for xpath_key_and_value in xpath_keys_and_values:

            # we find here the path before the key - and then get the XMLDOC at that point.
            this_key_idx = path.find(xpath_key_and_value, idx)
            path_before_keys = '/data' + path[0:this_key_idx-1]
            path_with_keys = path_before_keys + '[' + xpath_key_and_value + ']'
            # raise ValueError('about to create %s' % (path_with_keys))
            elements = xmldoc.xpath(path_with_keys)
            if len(elements) != 1:
                # Now we get the path before the keys
                parent_element = xmldoc.xpath(path_before_keys)[0]
                raise ValueError(parent_element)
                for (xpath_key, xpath_value) in REGEX_XPATH_KEY_VALUES.findall(xpath_key_and_value):
                    raise ValueError('about to create %s' % (xpath_key_and_value))

        return xmldoc

    def frame_netconf_xml(self):

        xmlstr = str(etree.tostring(self.transaction['xmldoc'], pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

#    """#
#
# In [7]: # But inevitably set's require xmlns
#   ...: setpath = """ < integrationtest xmlns ="http: // brewerslabng.mellon-collie.net/yang/integrationt
#   ...: est"><simpleleaf>HELLO THERE!!!!</simpleleaf></integrationtest>"""#
#
#In [8]:#
#
# In [8]: netconf.edit_config("""<nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + s
#  ...: etpath + """</nc:config>""", target='running')
# Out[8]: <nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:49dadd8d-00eb-470f-847b-86c827a891d1"><nc:ok/></nc:rpc-reply>
#"""#
#        pass#
#
#        """
#        In [10]: path="<integrationtest/>"
#
# In [11]: netconf.get_config(source='running',filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:n
     #...: etconf:base:1.0">%s</nc:filter>""" % (path))#
# Out[11]: <nc:rpc-reply xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="urn:uuid:3325038b-4c46-4efc-96f8-5297946850cc"><data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"></data></nc:rpc-reply>
# """
