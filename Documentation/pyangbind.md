For the following YANG module

```
brewerslab.yang:6: warning: imported module brewerslab-types not used
module: brewerslab
  +--rw tests
     +--rw temperature
        +--rw probes* [probeid]
           +--rw probeid    brewerslab-types:temperature-probe
           +--rw run?       boolean
           +--rw value?     brewerslab-types:temperature
```


```python
from pyangbinding import brewerslab
cfg = brewerslab()

probe = cfg.tests.temperature.probes.add('28-12345')
# This is the list key
probe.probeid

probe.value = 5.5

```

# Json Serialisation

```
import pyangbind.lib.pybindJSON as pb_json
print(pb_json.dumps(cfg))
{
    "tests": {
        "temperature": {
            "probes": {
                "28-12345": {
                    "probeid": "28-12345",
                    "value": 5.5
                }
            }
        }
    }
}


```


# Json Import

```
import pyangbinding
cfg2 = pb_json.loads(existing, pyangbinding, "brewerslab")

existing = """{
    "tests": {
        "temperature": {
            "probes": {
                "28-123450000": {
                    "probeid": "28-123450000",
                    "value": 5.5
                }
            }
        }
    }
}"""


cfg2.tests.temperature.probes.keys()
odict_keys(['28-123450000'])


```
