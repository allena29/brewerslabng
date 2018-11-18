class resources:

    SCHEMA_1 = """<?xml version="1.0" encoding="UTF-8"?>
<module name="integrationtest"
        xmlns="urn:ietf:params:xml:ns:yang:yin:1"
        xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest"
        xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <import module="crux">
    <prefix value="crux"/>
  </import>
  <typedef name="type1">
    <type name="string">
      <pattern value="brew[a-z]*">
        <error-message>
          <value>String must start with brew</value>
        </error-message>
      </pattern>
    </type>
  </typedef>
  <typedef name="type2">
    <type name="uint32"/>
  </typedef>
  <typedef name="type3">
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  </typedef>
  <typedef name="type4">
    <type name="union">
      <type name="type3"/>
      <type name="type2"/>
    </type>
  </typedef>
  <leaf name="simpleleaf">
    <type name="string"/>
  </leaf>
  <container name="simplecontainer">
    <presence value="true"/>
  </container>
  <list name="simplelist">
    <key value="simplekey"/>
    <leaf name="simplekey">
      <type name="string"/>
    </leaf>
    <leaf name="nonleafkey">
      <crux:info>
        <crux:text>A non-leaf key</crux:text>
      </crux:info>
      <type name="uint32"/>
      <description>
        <text>ABC</text>
      </description>
    </leaf>
  </list>
  <container name="morecomplex">
    <leaf name="nonconfig">
      <crux:info>
        <crux:text>A non-configuration node</crux:text>
      </crux:info>
      <type name="string"/>
      <config value="false"/>
    </leaf>
       <list name="composite-key-list">
      <key value="firstkey, secondkey"/>
      <leaf name="firstkey">
        <type name="string"/>
      </leaf>
      <leaf name="secondkey">
        <type name="string"/>
      </leaf>
      <leaf name="mandatoryleaf">
        <type name="string"/>
        <mandatory value="true"/>
      </leaf>
      <leaf name="optionalleaf">
        <type name="string"/>
        <mandatory value="false"/>
      </leaf>
      <leaf name="defaultleaf">
        <type name="string"/>
        <default value="ABC123"/>
      </leaf>
    </list>
    <leaf name="leaf2">
      <crux:info>
        <crux:text>must be 1 or 0 dont sit on the fence</crux:text>
      </crux:info>
      <type name="boolean"/>
    </leaf>
    <leaf name="leaf3">
      <crux:info>
        <crux:text>Should allow a string starting with brew - but no spaces</crux:text>
      </crux:info>
      <type name="type2"/>
    </leaf>
    <leaf name="leaf4">
      <crux:info>
        <crux:text>Should allow A, B, C or a uint32</crux:text>
      </crux:info>
      <type name="type4"/>
    </leaf>
    <container name="inner">
      <presence value="true"/>
      <leaf name="leaf5">
        <type name="string"/>
        <mandatory value="true"/>
      </leaf>
      <leaf name="leaf6">
        <type name="string"/>
        <mandatory value="false"/>
      </leaf>
      <leaf name="leaf7">
        <type name="string"/>
        <default value="this-is-a-default"/>
      </leaf>
    </container>
  </container>
  <typedef name="type-a">
    <type name="uint32"/>
  </typedef>
  <grouping name="group-a">
    <leaf name="a">
      <type name="string"/>
    </leaf>
  </grouping>
  <container name="resolver">
    <uses name="group-a"/>
    <leaf name="leaf-a">
      <type name="type-a"/>
    </leaf>
  </container>
</module>"""

    SCHEMA_CRUX = """<?xml version="1.0" encoding="UTF-8"?>
<module name="crux"
        xmlns="urn:ietf:params:xml:ns:yang:yin:1"
        xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/crux"/>
  <prefix value="crux"/>
  <description>
    <text>Common things which might be useful all over the place</text>
  </description>
  <extension name="trigger">
    <argument name="boolean">
      <yin-element value="true"/>
    </argument>
    <description>
      <text>Use to specify if data at a certain node should trigger an expensive
processing/validation operation - or if the data should just be persisted to the
datastore.</text>
    </description>
  </extension>
  <extension name="info">
    <argument name="text">
      <yin-element value="true"/>
    </argument>
    <description>
      <text>Help text for user-interfaces</text>
    </description>
  </extension>
  <container name="crux-cli">
    <list name="modules">
      <key value="module"/>
      <description>
        <text>Defines a list of modules which are publicly available for configuration</text>
      </description>
      <leaf name="module">
        <type name="string"/>
        <description>
          <text>Name of yang module, which should match the module name advertised when
establishing a netconf session.
&lt;capability&gt;http://brewerslabng.mellon-collie.net/yang/main?module=brewerslab&lt;/capability&gt;</text>
        </description>
      </leaf>
      <leaf name="namespace">
        <type name="string"/>
        <mandatory value="true"/>
        <description>
          <text>The namespace of the yang module</text>
        </description>
      </leaf>
      <leaf name="revision">
        <type name="string"/>
        <description>
          <text>Revision of the module</text>
        </description>
      </leaf>
      <list name="top-level-tags">
        <key value="tag"/>
        <description>
          <text>A number of top-level modules provided - this is defined to ensure that
when we can effectively isolate the intereting parts of the datastore.</text>
        </description>
        <leaf name="tag">
          <type name="string"/>
        </leaf>
      </list>
    </list>
  </container>
</module>"""

    SCHEMA_UNION = """<?xml version="1.0" encoding="UTF-8"?>
<module name="integrationtest"
        xmlns="urn:ietf:params:xml:ns:yang:yin:1"
        xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest"
        xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <typedef name="type2">
    <type name="uint32"/>
  </typedef>
  <typedef name="type3">
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  </typedef>
  <leaf name="uuuuuuuu">
    <type name="union">
      <type name="type3"/>
      <type name="type2"/>
      <type name="string"/>
    </type>
  </leaf>
</module>"""

    SCHEMA_USES = """<?xml version="1.0" encoding="UTF-8"?>
<module name="integrationtest"
        xmlns="urn:ietf:params:xml:ns:yang:yin:1"
        xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest"
        xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <grouping name="group-a">
    <leaf name="a">
      <type name="string"/>
    </leaf>
  </grouping>
  <container name="resolver">
    <uses name="group-a"/>
  </container>
</module>"""

    SCHEMA_PRIMITIVE = """<?xml version="1.0" encoding="UTF-8"?>
<module name="integrationtest"
        xmlns="urn:ietf:params:xml:ns:yang:yin:1"
        xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest"
        xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <leaf name="simpleleaf">
    <type name="string"/>
  </leaf>
  <container name="simplecontainer">
    <presence value="true"/>
  </container>
  <container name="morecomplex">
    <leaf name="nonconfig">
      <type name="string"/>
      <config value="false"/>
    </leaf>
    <leaf name="leaf2">
      <type name="boolean"/>
    </leaf>
    <container name="inner">
      <presence value="true"/>
      <leaf name="leaf5">
        <type name="string"/>
        <mandatory value="true"/>
      </leaf>
      <leaf name="leaf6">
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
        <mandatory value="false"/>
      </leaf>
      <leaf name="leaf7">
        <type name="string"/>
        <default value="this-is-a-default"/>
      </leaf>
    </container>
  </container>
</module>"""
