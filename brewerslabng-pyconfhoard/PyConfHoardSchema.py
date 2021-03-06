import json
import sys
import dpath.util
import argparse
import xml.etree.ElementTree as ET
from colorama import Fore
from colorama import Style
from PyConfHoardError import PyConfHoardInvalidYangSchema


class yin_to_json:

    def __init__(self, input, quiet=False):
        schema_config_tree = {}
        schema_oper_tree = {}
        schema_by_tree = {'root': {}}
        path = '/root'
        tree = ET.parse(input)
        root = tree.getroot()
        self.quiet = quiet
        self.chain = []
        self.final_pop_done = False

        self.prefix = None
        self.typedefs = {}
        self.find_typedefs(root, path)
        self.process(root, path, schema_by_tree['root'])
        self.schema = schema_by_tree

    def save(self, output):
        o = open(output, 'w')
        o.write(json.dumps(self.schema, indent=4))
        o.close()

        self.schema_config_tree = json.loads(json.dumps(self.schema))
        self.paths_to_delete = []
        self.separate(self.schema_config_tree, True)
        for path_to_delete in self.paths_to_delete:
            dpath.util.delete(self.schema_config_tree, path_to_delete)
        o = open(output.replace('.json', '-config.json'), 'w')
        o.write(json.dumps(self.schema_config_tree, indent=4, sort_keys=True))
        o.close()

        self.schema_oper_tree = json.loads(json.dumps(self.schema))
        self.paths_to_delete = []
        self.separate(self.schema_oper_tree, False)
        for path_to_delete in self.paths_to_delete:
            dpath.util.delete(self.schema_oper_tree, path_to_delete)
        o = open(output.replace('.json', '-oper.json'), 'w')
        o.write(json.dumps(self.schema_oper_tree, indent=4, sort_keys=True))
        o.close()

    def separate(self, obj, config=True):
        for child in obj:
            if isinstance(obj[child], dict):

                # TODO: for now we include list-keys in oper-data even if there is no oper-values.
                if '__schema' in obj[child] and '__listkey' in obj[child]['__schema'] and obj[child]['__schema']['__listkey'] is True:
                    self.separate(obj[child], config)
                elif '__schema' in obj[child] and '__config' in obj[child]['__schema'] and obj[child]['__schema']['__config'] is False and config is True:
                    self.paths_to_delete.append(obj[child]['__schema']['__path'])
                elif '__schema' in obj[child] and '__config' in obj[child]['__schema'] and obj[child]['__schema']['__config'] is True and config is False:
                    self.paths_to_delete.append(obj[child]['__schema']['__path'])
                else:
                    self.separate(obj[child], config)

    def find_typedefs(self, obj, path):
        for child in obj:
            if child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}prefix':
                self.prefix = child.attrib['value']
            if child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}typedef':
                if not self.prefix:
                    raise ValueError('Unable to parse typedef because we did not have a prefix')
                typedef = '%s:%s' % (self.prefix, child.attrib['name'])
                typedef_type = {'__type':  child[0].attrib['name']}
                for subchild in child:
                    for subsubchild in subchild:
                        if subsubchild.tag == '{urn:ietf:params:xml:ns:yang:yin:1}fraction-digits':
                            typedef_type['__fraction-digits'] = int(subsubchild.attrib['value'])
                self.typedefs[typedef] = typedef_type

    def process(self, obj, path, schema_by_tree, keys=[]):
        cpath = '/'
        if len(path):
            cpath = path

        if not self.quiet:
            sys.stderr.write('%s%s%s%s\n' % (Fore.MAGENTA, Style.BRIGHT, cpath, Style.RESET_ALL))

        for child in obj:
            if child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}container':
                schema_by_tree[child.attrib['name']] = {}
                schema_by_tree[child.attrib['name']]['__schema'] = {}

                schema_by_tree[child.attrib['name']]['__schema']['__path'] = path + '/' + child.attrib['name']
                schema_by_tree[child.attrib['name']]['__schema']['__container'] = True
                schema_by_tree[child.attrib['name']]['__schema']['__decendentconfig'] = False
                schema_by_tree[child.attrib['name']]['__schema']['__decendentoper'] = False
                if len(self.chain) == 0:
                    schema_by_tree[child.attrib['name']]['__schema']['__rootlevel'] = True
                else:
                    schema_by_tree[child.attrib['name']]['__schema']['__rootlevel'] = False

                self.chain.append(schema_by_tree[child.attrib['name']])
                self.process(child, path + '/' + child.attrib['name'], schema_by_tree[child.attrib['name']])
            elif child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}list':
                schema_by_tree[child.attrib['name']] = {}
                schema_by_tree[child.attrib['name']]['__listelement'] = {}
                ourself = schema_by_tree[child.attrib['name']]['__listelement']
                ourself['__schema'] = {}
                ourself['__schema']['__list'] = True
                ourself['__schema']['__elements'] = {}
                ourself['__schema']['__path'] = path + '/' + child.attrib['name']
                keys = ''
                for tmp in child:
                    if tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}key':
                        keys = tmp.attrib['value']
                ourself['__schema']['__keys'] = keys.split(' ')
                ourself['__schema']['__decendentconfig'] = False
                ourself['__schema']['__decendentoper'] = False
                if len(self.chain) == 0:
                    ourself['__schema']['__rootlevel'] = True
                else:
                    ourself['__schema']['__rootlevel'] = False

                self.chain.append(ourself)
                self.process(child, path + '/' + child.attrib['name'] + '/__listelement', ourself,  keys=keys)
            elif child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}leaf':
                if not self.quiet:
                    sys.stderr.write('%s%s/%s%s\n' % (Fore.MAGENTA, cpath, child.attrib['name'], Style.RESET_ALL))
                schema_by_tree[child.attrib['name']] = {}

                schema_by_tree[child.attrib['name']]['__schema'] = {}
                schema_by_tree[child.attrib['name']]['__schema']['__config'] = True
                schema_by_tree[child.attrib['name']]['__schema']['__leaf'] = True
                schema_by_tree[child.attrib['name']]['__schema']['__path'] = path + '/' + child.attrib['name']
                if child.attrib['name'] in keys:
                    schema_by_tree[child.attrib['name']]['__schema']['__listitem'] = True
                    schema_by_tree[child.attrib['name']]['__schema']['__listkey'] = True
                else:
                    schema_by_tree[child.attrib['name']]['__schema']['__listkey'] = False
                    schema_by_tree[child.attrib['name']]['__schema']['__listitem'] = True

                for tmp in child:
                    if tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}type':
                        yang_type = tmp.attrib['name']
                        schema_by_tree[child.attrib['name']]['__schema']['__type'] = yang_type
                        # TODO: refactor into the type def parsing code into a function
                        if yang_type == 'enumeration':
                            schema_by_tree[child.attrib['name']]['__schema']['__enum_values'] = []
                            for tmp2 in tmp:
                                schema_by_tree[child.attrib['name']]['__schema']['__enum_values'].append(tmp2.attrib['name'])
                        schema_by_tree[child.attrib['name']]['__schema']['__typedef'] = False
                        if yang_type in self.typedefs:
                            schema_by_tree[child.attrib['name']]['__schema']['__typedef'] = True
                            for typedef in self.typedefs[yang_type]:
                                schema_by_tree[child.attrib['name']]['__schema'][typedef] = self.typedefs[yang_type][typedef]
    
                        # TODO: refactor this with the type def parsing code into a function
                        # Decimal 64 must have fraction digits
                        for subchild in child:
                            for subsubchild in subchild:
                                if subsubchild.tag == '{urn:ietf:params:xml:ns:yang:yin:1}fraction-digits':
                                    schema_by_tree[child.attrib['name']]['__schema']['__fraction-digits'] = int(subsubchild.attrib['value'])
                    elif tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}default':
                        schema_by_tree[child.attrib['name']]['__schema']['__default'] = tmp.attrib['value']
                    elif tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}config':
                        if tmp.attrib['value'] == 'false':
                            schema_by_tree[child.attrib['name']]['__schema']['__config'] = False

                for elder in self.chain:
                    if schema_by_tree[child.attrib['name']]['__schema']['__config']:
                        elder['__schema']['__decendentconfig'] = True
                    else:
                        elder['__schema']['__decendentoper'] = True
                if len(self.chain) == 0:
                    schema_by_tree[child.attrib['name']]['__schema']['__rootlevel'] = True
                else:
                    schema_by_tree[child.attrib['name']]['__schema']['__rootlevel'] = False

        if len(self.chain):
            self.chain.pop()
        elif self.final_pop_done:
            raise ValueError('Bad structure - tried to go beyond our root')
        else:
            self.final_pop_done = True

    def validate(self, obj):
        for childname in obj:
            child = obj[childname]
            if isinstance(child, dict) and '__schema' in obj[childname]:
                schema = obj[childname]['__schema']
                if '__path' in schema:
                    sys.stderr.write('%s%s%s%s' % (Fore.GREEN, Style.BRIGHT, schema['__path'], Style.RESET_ALL))
                    if '__container' in schema and schema['__container']:
                        sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' container', Style.RESET_ALL))
                        if '__decendentconfig' and schema['__decendentconfig']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'conf-data-decendents', Style.RESET_ALL))
                        if '__decendentoper' and schema['__decendentoper']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'oper-data-decendents', Style.RESET_ALL))

                    elif '__list' in schema and schema['__list']:
                        sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' list', Style.RESET_ALL))

                        if '__decendentconfig' and schema['__decendentconfig']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'conf-data-decendents', Style.RESET_ALL))
                        if '__decendentoper' and schema['__decendentoper']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'oper-data-decendents', Style.RESET_ALL))
                    else:
                        if '__listkey' in schema and schema['__listkey']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' leaf-listkey %s' % (schema['__type']), Style.RESET_ALL))
                        elif '-_listitem' in schema and schema['__listitem']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' leaf-listitem %s' % (schema['__type']), Style.RESET_ALL))
                        else:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' leaf %s' % (schema['__type']), Style.RESET_ALL))

                        if '__config' in schema and schema['__config']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'conf-data', Style.RESET_ALL))
                        else:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'oper-data', Style.RESET_ALL))

                    newline = '\n                 '
                    if '__default' in schema:
                        sys.stderr.write('%s%s%s%s%s%s ' % (newline, Fore.GREEN, Style.DIM, ' Default ', schema['__default'], Style.RESET_ALL))
                    if '__enum_values' in schema:
                        sys.stderr.write('%s%s%s%s%s%s ' % (newline, Fore.GREEN, Style.DIM, ' Enum Values:  ', schema['__enum_values'], Style.RESET_ALL))

                    sys.stderr.write('\n')
                self.validate(child)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert YIN document to JSON")
    parser.add_argument('--input', required=True, help="Path a YIN file")
    parser.add_argument('--output', required=True, help="Path to store YIN document")
    parser.add_argument('--quiet', action='store_true', help="Don't show progress")
    args = parser.parse_args()

    worker = yin_to_json(args.input, args.quiet)
    if not args.quiet:
        worker.validate(worker.schema)

    worker.save(args.output)
