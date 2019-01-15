from ncclient import manager


netconf = manager.connect(host='localhost', port=830,
                          username='netconf', password='netconf',
                          hostkey_verify=False, allow_agent=False,
                          look_for_keys=False,
                          unknown_host_cb=lambda x: True)


path="""<crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux"/>"""
# Thankfully get_config is liberal about namespaces
path="""<crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux"/>"""
netconf.get_config(source='running',filter="""<nc:filter xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">%s</nc:filter>""" % (path))

# But inevitably set's require xmlns
setpath = """<simpleleaf xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">HELLO THERE!!!!</simpleleaf>"""

netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""",
    ...: target="running")


setpath = """<resolver xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest" nc:operation="replace"><a>AAA</a></re
    ...: solver>"""

netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""",
    ...: target="running")


    etpath = """<resolver xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><leaf-a>234</leaf-a></resolver>"""

In [65]: netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""",
    ...: target="running")


  help


In [74]: setpath = """<resolver xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><a>sad</a><leaf-a>X4</leaf-a></resolv
    ...: er>"""

In [75]: netconf.edit_config("""      <nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">""" + setpath + """</nc:config>""",
    ...: target="running",error_option="rollback-on-error")
---------------------------------------------------------------------------
