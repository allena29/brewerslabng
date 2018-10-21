import logging
import os
import re
from lxml import etree
import sys
sys.path.append('../')
from blng import Common


class Yang:

    CRUX_NS = "{http://brewerslabng.mellon-collie.net/yang/crux}"

    def __init__(self):
        self.cli_modules = {}
        self.netconf_capa = {}
        self.top_levels = {}

        FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        self.log = logging.getLogger('yang')
        transport_log = logging.getLogger('ncclient.transport.ssh')
        transport_log.level = logging.ERROR
        rpc_log = logging.getLogger('cclient.operations.rpc')
        rpc_log.level = logging.ERROR
        session_log = logging.getLogger('ncclient.transport.session')
        session_log.level = logging.ERROR

    def _process_module(self, cm):
        module = None
        namespace = None
        revision = 'unspecified'
        tops = []
        for x in cm.getchildren():
            if x.tag == self.CRUX_NS + "module":
                module = x.text
            if x.tag == self.CRUX_NS + "namespace":
                namespace = x.text
            if x.tag == self.CRUX_NS + "revision":
                revision = x.text
            if x.tag == self.CRUX_NS + "top-level-tags":
                for t in x.getchildren():
                    if t.tag == self.CRUX_NS + "tag":
                        tops.append(t.text)

        if module and namespace:
            if namespace not in self.netconf_capa:
                raise ValueError('NETCONF server does expose %s %s' % (module,
                                                                       namespace))

        self.cli_modules[module] = namespace

        return (module, namespace, revision, tops)

    def cache_schema(self, netconf, module, namespace, revision):
        """
        Fetch the NETCONF schema from the NETCONF server and store it
        for later user. If the YANG module changes we expect that the
        revision will be updated
        TODO: we are not actually doing anything to get a certain revision
        """
        if os.path.exists('.cache/%s.yang' % (module)):
            self.log.debug('We have a cached schema of %s' % (module))
        else:
            self.log.debug('We do not have a schema of %s' % (module))
            with open('.cache/%s.yang' % (module), 'w') as file:
                yang_data = str(netconf.get_schema(module))

                xml_root = etree.fromstring(yang_data)
                yang = xml_root.getchildren()[0].text

                yang_imports = re.compile('\s*import\s+(\S+)\s*.*').findall(yang)
                for y in yang_imports:
                    self.log.debug('Dealing with dependent Schema %s' % (y))
                    self.cache_schema(netconf, y, None, None)

                file.write(yang)

    def convert_yang_to_yin(self, module):
        """
        Convert YANG file to YIN - including all imports of each YANG module we encounter.
        """
        if not os.path.exists(".cache/%s.yin" % (module)):
            self.log.debug("Converting file %s to YIN representation" % (module))

            with open(".cache/%s.yang" % (module)) as file:
                yang = file.read()
                yang_imports = re.compile('\s*import\s+(\S+)\s*.*').findall(yang)
                for y in yang_imports:
                    self.log.debug("Dealing with dependent Schema %s in YIN convertor " % (y))
                    self.convert_yang_to_yin(y)

        pyang_command = "pyang -p .cache -f yin -o .cache/%s.yin .cache/%s.yang" % (module, module)
        Common.shell_command(pyang_command)

    def negotiate_netconf_capabilities(self, netconf):
        for capa in netconf.server_capabilities:
            c = capa.split('?')
            c.append('')
            self.netconf_capa[c[0]] = {'module': c[1]}

        if 'http://brewerslabng.mellon-collie.net/yang/crux' not in self.netconf_capa:
            raise ValueError("NETCONF does not support crux protocol")

        filter = """<crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux"><modules></crux-cli>"""

        crux_modules = self._netconf_get_xml(netconf, filter)
        if len(crux_modules) == 0:
            raise ValueError("Unable to fetch list of supported CRUX CLI modules")

        self._process_modules(netconf, crux_modules[0])

    def _process_modules(self, netconf, crux_modules):
        """
        Process the list of modules given an XML structure representing the
        configuration of /crux-cli

        This will give us a number of YANG schemas extracted from the NETCONF response
        and we will then go on to convert those into YIN representations. By the point
        we start converting we *should* have recursively downloaded all the dependeny
        YANG files as the method cache_schema is recursive in nature.
        """
        for cm in crux_modules.getchildren():
            (module, namespace, revision, tops) = self._process_module(cm)

            for t in tops:
                if t in self.top_levels:
                    raise ValueError("Top-level tag %s is already registered to another namespace")
                self.log.debug("Registered new top-level tag %s to %s" % (t, namespace))
                self.top_levels[t] = namespace

            self.cache_schema(netconf, module, namespace, revision)

        for ym in self.cli_modules:
            print("We need schema for %s" % (ym))
            self.convert_yang_to_yin(ym)

    def _netconf_get_xml(self, netconf, filter, config=True, source='running'):
        filter_xml = """<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
            %s
        </nc:filter>""" % (filter)
        data_str = str(netconf.get_config(source=source, filter=filter_xml))
        return etree.fromstring(data_str.encode('UTF-8')).getchildren()[0]