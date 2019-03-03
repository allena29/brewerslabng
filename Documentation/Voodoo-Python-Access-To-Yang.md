# Python Access to Yang

See.. [CRUX Format](Crux-Yang-Representation.md)

## Usage:

The example below shows a very basic overview of loading in an serialised XML payload, changing a value and then re-serialising the data.

```

In [1]: import blng.Voodoo

In [2]: session = blng.Voodoo.DataAccess('crux-example.xml')
/Users/adam/brewerslabng/blng/Voodoo.py:44: FutureWarning: The behavior of this method will change in future versions. Use specific 'len(elem)' or 'elem is not None' test instead.
  if not self._schema:

In [3]: root = session.get_root()

In [4]: root
Out[4]: VoodooRoot

In [5]: root.morecomplex
VoodooContainer: /morecomplex

In [6]: root.morecomplex.show_children()
inner
leaf2
leaf3
leaf4
nonconfig

In [7]: xmlstr = """<crux-vooodoo>
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

In [8]: session.loads(xmlstr)

In [9]: print(root.simpleleaf)
9999

In [10]: root.simpleleaf = '55'

In [11]: print(session.dumps())
<crux-vooodoo><simpleleaf old_value="9999">55</simpleleaf>
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
