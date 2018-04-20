import json
import sys
import dpath.util
import argparse
import xml.etree.ElementTree as ET
from colorama import Fore
from colorama import Style


class yin_to_json:

    def __init__(self, input):
        schema_by_tree = {}
        path =''
        tree = ET.parse(input)
        root = tree.getroot()

        self.chain = []
        self.final_pop_done = False

        self.process(root, path, schema_by_tree)
        self.schema = schema_by_tree


    def save(self, output):
        o = open(output, 'w')
        o.write(json.dumps(self.schema, indent=4))
        o.close()
   

    def process(self, obj, path, schema_by_tree, keys=[]):
        cpath = '/'
        if len(path):
            cpath = path
        sys.stderr.write('%s%s%s%s\n' % (Fore.MAGENTA, Style.BRIGHT, cpath, Style.RESET_ALL))

        for child in obj:
            if child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}container':
                schema_by_tree[child.attrib['name']] = {}
                schema_by_tree[child.attrib['name']]['__path'] = path + '/' + child.attrib['name']
                schema_by_tree[child.attrib['name']]['__container'] = True
                schema_by_tree[child.attrib['name']]['__decendentconfig'] = False
                schema_by_tree[child.attrib['name']]['__decendentoper'] = False
                if len(self.chain) == 0:
                    schema_by_tree[child.attrib['name']]['__rootlevel'] = True
                else:
                    schema_by_tree[child.attrib['name']]['__rootlevel'] = False
                    
                self.chain.append(schema_by_tree[child.attrib['name']])
                self.process(child, path + '/' + child.attrib['name'], schema_by_tree[child.attrib['name']])
            elif child.tag =='{urn:ietf:params:xml:ns:yang:yin:1}list':
                schema_by_tree[child.attrib['name']] = {}
                schema_by_tree[child.attrib['name']]['__list'] = True
                schema_by_tree[child.attrib['name']]['__elements'] = {}
                schema_by_tree[child.attrib['name']]['__path'] = path + '/' + child.attrib['name']
                keys = ''
                for tmp in child:
                    if tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}key':
                        keys = tmp.attrib['value']
                schema_by_tree[child.attrib['name']]['__keys'] = keys
                schema_by_tree[child.attrib['name']]['__decendentconfig'] = False
                schema_by_tree[child.attrib['name']]['__decendentoper'] = False
                if len(self.chain) == 0:
                    schema_by_tree[child.attrib['name']]['__rootlevel'] = True
                else:
                    schema_by_tree[child.attrib['name']]['__rootlevel'] = False

                self.chain.append(schema_by_tree[child.attrib['name']])
                self.process(child, path + '/' + child.attrib['name'], schema_by_tree[child.attrib['name']], keys=keys)
            elif child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}leaf':                
                sys.stderr.write('%s%s/%s%s\n' % (Fore.MAGENTA, cpath, child.attrib['name'], Style.RESET_ALL))
                schema_by_tree[child.attrib['name']] = {}
        
                schema_by_tree[child.attrib['name']]['__config'] = True
                schema_by_tree[child.attrib['name']]['__leaf'] = True
                schema_by_tree[child.attrib['name']]['__value'] = None
                schema_by_tree[child.attrib['name']]['__path'] = path + '/' + child.attrib['name']
                if child.attrib['name'] in keys:
                    schema_by_tree[child.attrib['name']]['__listkey'] = True
                else:
                    schema_by_tree[child.attrib['name']]['__listkey'] = False

                for tmp in child:
                    if tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}type':
                        yang_type = tmp.attrib['name']
                        schema_by_tree[child.attrib['name']]['__type'] = yang_type
                        if yang_type == 'enumeration':
                            schema_by_tree[child.attrib['name']]['__enum_values'] = []
                            for tmp2 in tmp:
                                schema_by_tree[child.attrib['name']]['__enum_values'].append(tmp2.attrib['name'])
                    elif tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}default':
                        schema_by_tree[child.attrib['name']]['__default'] = tmp.attrib['value']
                    elif tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}config':
                        if tmp.attrib['value'] == 'false':
                            schema_by_tree[child.attrib['name']]['__config'] = False

                for elder in self.chain:
                    if schema_by_tree[child.attrib['name']]['__config']:
                        elder['__decendentconfig'] = True
                    else:
                        elder['__decendentoper'] = True
                if len(self.chain) == 0:
                    schema_by_tree[child.attrib['name']]['__rootlevel'] = True
                else:
                    schema_by_tree[child.attrib['name']]['__rootlevel'] = False
#                        elder[
    #                else:
    #                    print tmp.tag
#        for child in obj:

#        for x in self.chain:
#           print ('    %s' %(x['__path']))

        if len(self.chain):
            self.chain.pop()
        elif self.final_pop_done:
            raise ValueError('Bad structure - tried to go beyond our root')
        else:
            self.final_pop_done = True
        
        
    def validate(self, obj):
        for childname in obj:
            child = obj[childname]
            if isinstance(child, dict):
#                sys.stderr.write('%s\n' %(child))
                if '__path' in child:

                    sys.stderr.write('%s%s%s%s' % (Fore.GREEN, Style.BRIGHT, child['__path'], Style.RESET_ALL))
                    if '__container' in child and child['__container']:
                        sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' container', Style.RESET_ALL))
                        if '__decendentconfig' and child['__decendentconfig']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'conf-data-decendents', Style.RESET_ALL))
                        if '__decendentoper' and child['__decendentoper']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'oper-data-decendents', Style.RESET_ALL))

                    elif '__list' in child and child['__list']:                    
                        sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' list', Style.RESET_ALL))

                        if '__decendentconfig' and child['__decendentconfig']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'conf-data-decendents', Style.RESET_ALL))
                        if '__decendentoper' and child['__decendentoper']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'oper-data-decendents', Style.RESET_ALL))
                    else:
                        sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, ' leaf %s' %(child['__type']), Style.RESET_ALL))

                        if '__config' in child and child['__config']:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'conf-data', Style.RESET_ALL))
                        else:
                            sys.stderr.write('%s%s%s%s ' % (Fore.GREEN, Style.NORMAL, 'oper-data', Style.RESET_ALL))


                    newline='\n                 '
                    if '__default' in child:
                        sys.stderr.write('%s%s%s%s%s%s ' % (newline, Fore.GREEN, Style.DIM, ' Default ', child['__default'], Style.RESET_ALL))
                    if '__enum_values' in child:
                        sys.stderr.write('%s%s%s%s%s%s ' % (newline, Fore.GREEN, Style.DIM, ' Enum Values:  ', child['__enum_values'], Style.RESET_ALL))

                    sys.stderr.write('\n')
                    self.validate(child)
                   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert YIN document to JSON")
    parser.add_argument('--input', required=True, help="Path a YIN file")
    parser.add_argument('--output', required=True, help="Path to store YIN document")
    args = parser.parse_args()

    worker = yin_to_json(args.input)
    worker.validate(worker.schema)
    worker.save(args.output)

