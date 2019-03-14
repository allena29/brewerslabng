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
        indent = ''
        for child in self.schema.iter():
            if 'cruxpath' in child.attrib:
                cruxpath = child.attrib['cruxpath']
                cruxtype = child.attrib['cruxtype']
                path_count = cruxpath.count('/')-1
                indent = '  ' * (path_count)

                values = self.cfg.xpath('/voodoo'+cruxpath)
                if not self.oldcfg:
                    old_values = []
                else:
                    old_values = self.oldcfg.xpath('/voodoo' + cruxpath)

                if len(values) == 0 and len(old_values) == 0:
                    continue

                if cruxtype == 'list':
                    raise ValueError('leists not supported')

                if len(old_values) and len(values):
                    # Old and New

                    if cruxtype != 'leaf':
                        yield '  ' + indent + old_values[0].tag + ':'
                    else:
                        yield '? ' + indent + old_values[0].tag
                elif len(values):
                    # New
                    if cruxtype != 'leaf':
                        yield '+ ' + indent + values[0].tag + ':'
                    else:
                        yield '+ ' + indent + values[0].tag + ' ' + values[0].text + ';'
                elif len(old_values):
                    # Old
                    if cruxtype != 'leaf':
                        yield '- ' + indent + old_values[0].tag + ':'
                    else:
                        yield '- ' + indent + old_values[0].tag + ' ' + old_values[0].text + ':'
        b = time.time()
        yield '--- CONFIGURATION END ---'
