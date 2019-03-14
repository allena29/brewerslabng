
from blng.LogHandler import LogWrap
from blng.Voodoo import DataAccess


class Witch:

    """
    """

    def __init__(self, cfg):
        self.log = LogWrap('witch', False, True)
        self.cfg = cfg
        self.indent = '  '

    def show(self, cfg=None):
        if not cfg:
            cfg = self.cfg
        xmldoc = cfg._xmldoc.xmldoc

        self.log.debug('Showing configuration of object %s', repr(cfg))
        self.log.debug('Showing configuration of xmldoc %s', xmldoc)

        last_count = 1
        skip = True
        open_braces = 0
        for x in xmldoc.iter():
            if not skip:
                if x.attrib['cruxpath'].count('/') < last_count:
                    for dummy in range(last_count-x.attrib['cruxpath'].count('/')):
                        yield indent_required + '}'
                        indent_required = indent_required[:-2]

                        open_braces = open_braces - 1
                last_count = x.attrib['cruxpath'].count('/')
                indent_required = '  '*(x.attrib['cruxpath'].count('/')-1)
                end_line = ''
                if 'cruxtype' in x.attrib and x.attrib['cruxtype'] == 'leaf':
                    val = ' '+x.text
                    end_line = ';'
                    yield indent_required + x.tag + val + end_line

                    indent_required = indent_required[:-2]
                else:
                    val = ''
                    end_line = ' {'
                    open_braces = open_braces + 1
                    yield indent_required + x.tag + val + end_line
            skip = False

        # if len(indent_required)/2 > 0:
        #     while len(indent_required) > 0:
        #         indent_required = indent_required[:-2]
            # yield str((' ' * len(indent_required)) + '}')
        for dummy in range(open_braces):

            yield indent_required + '}'
            indent_required = indent_required[:-2]

        yield '--END OF CONFIGURATION --'


if __name__ == '__main__':
    # env PYTHONPATH=/Users/adam/brewerslabng python blng/Witch.py
    session = DataAccess('crux-example.xml')
    root = session.get_root()
    root.simpleleaf = 'abc'
    # this is a bit bad ceause depending on the order we write data
    # we have a difference.
    # we almost need to iterate around the schema - it will then
    # almost certainly be based on the order of the ynag model.
    root.morecomplex.leaf2 = '5'
    root.bronze.silver
    root.simpleenum = '234'
    root.bronze.silver.gold.platinum.deep = 'down'
    root.simpleenum = '234'
    root.bronze.silver.gold
    root.simpleenum = '234'
    root.simpleenum = '234'
    print(session.dumps())
    w = Witch(root)
    # TODO: if we want a comparison diff engine type thing
    # assume we implement it by iterated around two paraellel instaces of show
    # one with the old configuration one with new configuration and from there
    # going line by line (not in a for loop but controlling next() ourselves
    # we should be able to go at the right speed to get +/-'s
    for line in w.show():
        print(line)
