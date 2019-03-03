# Python Access to Yang

See.. [CRUX Format](Crux-Yang-Representation.md)

## Usage:


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
