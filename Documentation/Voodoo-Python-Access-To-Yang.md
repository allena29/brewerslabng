# Python Access to Yang

See.. [CRUX Format](Crux-Yang-Representation.md)

## Usage:

The example below shows a very basic overview of loading in an serialised XML payload, changing a value and then re-serialising the data.

```
>>>>>> import blng.Voodoo
>>>>>> session = blng.Voodoo.DataAccess('crux-example.xml')
>>>>>> root = session.get_root()
>>>>>> root
VoodooRoot

>>>>>> print(root.morecomplex)
VoodooContainer: /morecomplex


>>>>>> root.morecomplex.show_children()
VoodooContainer: /morecomplex

>>>>>> xmlstr = """<crux-vooodoo>
<simpleleaf old_value="9998">9999</simpleleaf>
<morecomplex>
<leaf2>a</leaf2>
</morecomplex>
<simplelist>
<simplekey listkey="yes">firstkey</simplekey>
</simplelist>
<hyphen-leaf>abc123</hyphen-leaf>
<outsidelist>
<leafo listkey="yes">a</leafo>
<insidelist>
<leafi listkey="yes">A</leafi>
</insidelist>
</outsidelist>
<outsidelist>
<leafo listkey="yes">b</leafo>
</outsidelist>
</crux-vooodoo>"""

>>>>>> session.loads(xmlstr)
>>>>>> print(root.simpleleaf)
9999

>>>>>> root.simpleleaf = '55'
>>>>>> print(session.dumps())
<crux-vooodoo><simpleleaf old_value="9998">9999</simpleleaf>
<morecomplex>
<leaf2>a</leaf2>
</morecomplex>
<simplelist>
<simplekey listkey="yes">firstkey</simplekey>
</simplelist>
<hyphen-leaf>abc123</hyphen-leaf>
<outsidelist>
<leafo listkey="yes">a</leafo>
<insidelist>
<leafi listkey="yes">A</leafi>
</insidelist>
</outsidelist>
<outsidelist>
<leafo listkey="yes">b</leafo>
</outsidelist>
</crux-vooodoo>
```



## Internal:




## Constraints:

 - YANG nodes containing a hyphen are converted to underscores in the python access, however it is not supported for a yang leaf to have both hyphens and underscores.


## TODO:

- validation everywhere
- \__dir__ on a list should only show create object, list elements should show the keys/children.
- the following list case fails
  - a=root.outsidelist.create('a')
  - A=a.insidelist.create('A')
  - b=root.outsidelist.create('b')
  - B=b.insidelist.create('B') # fails on longest match
- uses are throwing a key errors
- we can assign a value to a container.
- ~~ensure 'hyphens' in yang are dealt with~~
- cache crux objects as they are created  or instantiate every single time.
- what about mandatory things... within a container/list-node (probably not realistic to force it)
- ~~longest_path_match creates fails to catch list-keys~~
