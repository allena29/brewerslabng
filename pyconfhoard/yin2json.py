import json
import xml.etree.ElementTree as ET
tree = ET.parse('../yang/schema.yin')
root = tree.getroot()

schema_by_path = {}
schema_by_tree = {}

def process(obj, path, schema_by_tree, schema_by_path):
    for child in obj:
        # print path, child.tag,child.attrib
        if child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}container':

            schema_by_tree[child.attrib['name']] = {}
            process(child, path + '/' + child.attrib['name'], schema_by_tree[child.attrib['name']], schema_by_path)
        elif child.tag =='{urn:ietf:params:xml:ns:yang:yin:1}list':

            schema_by_tree[child.attrib['name']] = {}
            process(child, path + '/' + child.attrib['name'], schema_by_tree[child.attrib['name']], schema_by_path)

        elif child.tag == '{urn:ietf:params:xml:ns:yang:yin:1}leaf':
            schema_by_tree[child.attrib['name']] = {}
            schema_by_tree[child.attrib['name']]['config'] = True
            for tmp in child:
                if tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}type':
                    yang_type = tmp.attrib['name']
                    schema_by_path[path] = yang_type
                    schema_by_tree[child.attrib['name']]['type'] = yang_type
                    if yang_type == 'enumeration':
                        schema_by_tree[child.attrib['name']]['enum_values'] = []
                        for tmp2 in tmp:
                            schema_by_tree[child.attrib['name']]['enum_values'].append(tmp2.attrib['name'])
                elif tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}default':
                    schema_by_tree[child.attrib['name']]['default'] = tmp.attrib['value']
                elif tmp.tag == '{urn:ietf:params:xml:ns:yang:yin:1}config':
                    if tmp.attrib['value'] == 'false':
                        schema_by_tree[child.attrib['name']]['config'] = False
#                else:
#                    print tmp.tag

path =''
process(root, path, schema_by_tree, schema_by_path)

print json.dumps(schema_by_tree, indent=4)

