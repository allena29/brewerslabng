# Python Access to Yang


This extends from [Voodoo](Voodoo-Python-Access-To-Yang) but commits to using a netconf backend via ncclient.
Following the learning of the first cut we still depend heavily on etree and holding single instances on the objects.

The biggest downside of the previous version is that two processes would have their own in-memory datastore, that is still true to an extent - however a process can keep doing a netconf commit - which gives some kind of transaction support.

## Usage:

Much like the existing version a session is created with a crux-schema, See.. [CRUX Format](Crux-Yang-Representation.md)

However in this case **root** isn't the same as root on the netconf server. Sysrepod starts to push towards segregating around yang modules. Now when we get_root we specify the top-level container (considering [integrationtest.yang](../yang/integrationtest.yang) this is pretty sub-optimal as there are lots of top-level elements defined there [voodoox.yang](../yang/voodoox.yang) wraps integrationtest inside a container voodoox.

```
session = VoodooX('crux-example.xml')
session.connect()
print(session)
# root = session.get_root('morecomplex', 'http://brewerslabng.mellon-collie.net/yang/integrationtest')
# print(root)
root = session.get_root('voodoox', 'http://brewerslabng.mellon-collie.net/yang/vododoox')
print(root)
print(dir(root))
```


# Implements

- Root
  - \__dir__()
