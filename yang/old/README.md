# YANG Handler 

### Validating YANG changes

- `pyang -f yin`
- Install into sysrepod
  - `sysrepoctl --install --yang=brewerslab-types.yang`
  - sysrepoctl --install --yang=brewerslab-teststub.yang
- netconf-console --user netconf --password netconf --port 830 --get-schema brewerslab-types




# lxml etree


If the XML looks like this....

```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <module name="brewerslab"
             xmlns="urn:ietf:params:xml:ns:yang:yin:1"
             xmlns:brewlabng-teststub="http://brewerslabng.mellon-collie.net/yang/main"
             xmlns:brewerslab-types="http://brewerslabng.mellon-collie.net/yang/types"
             xmlns:brewerslab-teststub="http://brewerslabng.mellon-collie.net/yang/teststub">
       <namespace uri="http://brewerslabng.mellon-collie.net/yang/main"/>
       <prefix value="brewlabng-teststub"/>
       <import module="brewerslab-types">
        <prefix value="brewerslab-types"/>
      </import>
      <import module="brewerslab-teststub">
        <prefix value="brewerslab-teststub"/>
      </import>
      <uses name="brewerslab-teststub:tests"/>
    </module>
```

Then things aren't straightforward.... if we make it like this instead by stripping out the xmlns

```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <module name="brewerslab">
       <namespace uri="http://brewerslabng.mellon-collie.net/yang/main"/>
       <prefix value="brewlabng-teststub"/>
       <import module="brewerslab-types">
        <prefix value="brewerslab-types"/>
      </import>
      <import module="brewerslab-teststub">
        <prefix value="brewerslab-teststub"/>
      </import>
      <uses name="brewerslab-teststub:tests"/>
    </module>
```

Then the following extract of code will work.


```python
In [1]: from lxml import etree
   ...: tree = etree.parse('yin/brewerslab.yang.yin')
   ...: element = tree.xpath('/module/namespace')[0]
   ...:

In [2]: element.tag
Out[2]: 'namespace'

In [3]: element.attrib
Out[3]: {'uri': 'http://brewerslabng.mellon-collie.net/yang/main'}

In [4]: element.attrib['uri']
Out[4]: 'http://brewerslabng.mellon-collie.net/yang/main'

In [5]: element.text

```

Although this does work...

```python
In [23]: ns={"yin": "urn:ietf:params:xml:ns:yang:yin:1"}

In [24]: from lxml import etree
    ...: tree = etree.parse('yin/brewerslab.yang.yin')
    ...: element = tree.xpath('/yin:module', namespaces=ns)
    ...: element
    ...:
    ...:
Out[24]: [<Element {urn:ietf:params:xml:ns:yang:yin:1}module at 0x109a82a88>]

In [25]:
```


So far we have parsed XML objects in with the ability to do XPATH queries on them... and built a very primitive dictionary of modulenames.

```
python yinmunger.py --parent sdf --yin yin
2018-09-15 15:08:29,680 - yinmunger            INFO          Pass 1... yin/brewerslab.yang.yin
<lxml.etree._ElementTree object at 0x10661ed48>
2018-09-15 15:08:29,681 - yinmunger            INFO          Pass 1... yin/brewerslab-types.yang.yin
<lxml.etree._ElementTree object at 0x10661ee48>
2018-09-15 15:08:29,681 - yinmunger            INFO          Pass 1... yin/brewerslab-teststub.yang.yin
<lxml.etree._ElementTree object at 0x10661eec8>
{'brewerslab': <lxml.etree._ElementTree object at 0x10661ed48>, 'brewerslab-types': <lxml.etree._ElementTree object at 0x10661ee48>, 'brewerslab-teststub': <lxml.etree._ElementTree object at 0x10661eec8>}
```