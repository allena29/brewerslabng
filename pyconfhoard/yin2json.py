import json
import argparse
import xml.etree.ElementTree as ET


class yin_to_json:

    def __init__(self, input):
        schema_by_tree = {}
        path =''
        tree = ET.parse(input)
        root = tree.getroot()

        self.process(root, path, schema_by_tree)
        self.schema = schema_by_tree

    def save(self, output):
        o = open(output, 'w')
        o.write(json.dumps(self.schema, indent=4))
        o.close()
    
    def process(self, obj, path, schema_by_tree):
        for child in obj:
            # print path, child.tag,child.attrib
            if child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}container':
                schema_by_tree[child.attrib['name']] = {}
                schema_by_tree[child.attrib['name']]['__path'] = path
                self.process(child, path + '/' + child.attrib['name'], schema_by_tree[child.attrib['name']])
            elif child.tag =='{urn:ietf:params:xml:ns:yang:yin:1}list':
                schema_by_tree[child.attrib['name']] = {}
                schema_by_tree[child.attrib['name']]['__list'] = True
                schema_by_tree[child.attrib['name']]['__elements'] = {}
                schema_by_tree[child.attrib['name']]['__path'] = path
                self.process(child, path + '/' + child.attrib['name'], schema_by_tree[child.attrib['name']])
                keys = ''
                for tmp in child:
                    if tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}key':
                        keys = tmp.attrib['value']
                schema_by_tree[child.attrib['name']]['__keys'] = keys
            elif child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}leaf':
                schema_by_tree[child.attrib['name']] = {}
                schema_by_tree[child.attrib['name']]['__config'] = True
                schema_by_tree[child.attrib['name']]['__leaf'] = True
                schema_by_tree[child.attrib['name']]['__value'] = None
                schema_by_tree[child.attrib['name']]['__path'] = path
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
    #                else:
    #                    print tmp.tag


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert YIN document to JSON")
    parser.add_argument('--input', required=True, help="Path a YIN file")
    parser.add_argument('--output', required=True, help="Path to store YIN document")
    args = parser.parse_args()

    worker = yin_to_json(args.input)
    worker.save(args.output)

