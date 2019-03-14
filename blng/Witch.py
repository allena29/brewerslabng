from blng.LogHandler import LogWrap
from blng.Voodoo import DataAccess
import time


class Witch:

    def __init__(self, cfg, oldcfg=None):
        self.log = LogWrap('witch', False, True)
        self.schema = cfg._schema
        self.cfg = cfg._xmldoc.xmldoc
        if oldcfg is not None:
            self.oldcfg = oldcfg._xmldoc.xmldoc
        else:
            self.oldcfg = None

    def show(self, compare=False, xpath=False, set=False):
        skip = True
        a = time.time()
        yield '--- CONFIGURATION START ---'

        last_path_count = 1
        self.indent = ''
        for child in self.schema.iter():
            if 'cruxpath' in child.attrib:
                cruxpath = child.attrib['cruxpath']
                cruxtype = child.attrib['cruxtype']
                path_count = cruxpath.count('/')-1
                self.indent = '  ' * (path_count)

                values = self.cfg.xpath('/voodoo'+cruxpath)
                if not self.oldcfg:
                    old_values = []
                else:
                    old_values = self.oldcfg.xpath('/voodoo' + cruxpath)

                if len(values) == 0 and len(old_values) == 0:
                    continue

                raise ValueError(' need a better way to iterate here')
                """
                        old_session = DataAccess('crux-example.xml')
                        session = DataAccess('crux-example.xml')

                        old_root = old_session.get_root()
                        old_root.simplelist.create('xyz')
                        old_root.simplelist.create('123')
                        old_root.simplelist.create('abc')

                        root = session.get_root()
                        root.simplelist.create('987')
                        root.simplelist.create('xyz')
                        root.simplelist.create('abc')
                        root.simplelist.create('def')
                        root.simplelist.create('ghi')
                        root.simplelist.create('jkl')

                    should not equal this
                      --- CONFIGURATION START ---
                        +
                        - a
                        - -   simplekey xyz;
                        - +   simplekey 987;
                          --- CONFIGURATION END ---

                                        """
                if cruxtype == 'list':
                    results = self._process_list_elements(values, old_values)
                elif cruxtype == 'leaf':
                    results = self._process_leaf_element(values, old_values)
                else:
                    results = self._process_nonleaf_element(values, old_values)
                for result in results:
                    yield result

        b = time.time()
        self.log.debug('Processing took %s seconds', str(b-a))
        yield '--- CONFIGURATION END ---'

    def _process_list_elements(self, cur, old):
        return ['a']

    def _process_nonleaf_element(self, cur, old):
        if len(cur) and len(old):
            return ['- ' + self.indent + old[0].tag + '::']
        elif len(cur):
            return ['+ ' + self.indent + cur[0].tag + '::']
        elif len(old):
            return ['- ' + self .indent + old[0].tag + '::']

    def _process_leaf_element(self, cur, old):
        if len(cur) and len(old):
            return ['- ' + self.indent + old[0].tag + ' ' + old[0].text + ';',
                    '+ ' + self.indent + cur[0].tag + ' ' + cur[0].text + ';']
        elif len(cur):
            return ['+ ' + self.indent + cur[0].tag + ' ' + cur[0].text + ';']
        elif len(old):
            return ['- ' + self .indent + old[0].tag + ' ' + old[0].text + ';']
