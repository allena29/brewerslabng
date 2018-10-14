import os
import re


def _cache_schema(log, netconf, module, namespace, revision):
    """
    Fetch the NETCONF schema from the NETCONF server and store it
    for later user. If the YANG module changes we expect that the
    revision will be updated
    TODO: we are not actually doing anything to get a certain revision
    """
    if os.path.exists('.cache/%s.schema' % (module)):
        log.debug('We have a cached schema of %s' % (module))
    else:
        log.debug('We do not have a schema of %s' % (module))
        with open('.cache/%s.schema' % (module), 'w') as file:
            yang = str(netconf.get_schema(module))
            yang_imports = re.compile('\s*import\s+(\S+)\s*.*').findall(yang)
            for y in yang_imports:
                log.debug('Dealing with dependent Schema %s' % (y))
                self._cache_schema(netconf, y, None, None)
            file.write(yang)
