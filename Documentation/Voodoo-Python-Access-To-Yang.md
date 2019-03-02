# Python Access to Yang

See.. [CRUX Format](Crux-Yang-Representation.md)

## Usage:


## Internal:



## Constraints:

 - YANG nodes containing a hyphen are converted to underscores in the python access, however it is not supported for a yang leaf to have both hyphens and underscores.


## TODO:

- validation everywhere
- uses are throwing a key errors
- we can assign a value to a container.
- ~~ensure 'hyphens' in yang are dealt with~~
- cache crux objects as they are created  or instantiate every single time.
