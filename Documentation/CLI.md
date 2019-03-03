# CLI (Internal documentation)

The basic approach is to use Netopeer2 (although it could be something else) to expose a netconf server, the primary interface used will be CLI. Netopeer2 is available as a Docker image for x86 and ARM.


There are a number of steps which will need to be taken, the basic approach when the CLI connects to to the NETCONF server exposes a yang module `http://brewerslabng.mellon-collie.net/yang/crux` which describes basic structure about the applications YANG modules.

```xml
<crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux">
  <modules>
	  <module>brewerslab</module>
	  <namespace>http://brewerslabng.mellon-collie.net/yang/main</namespace>
  </modules>
  <modules>
	  <module>integrationtest</module>
	  <namespace>http://brewerslabng.mellon-collie.net/yang/integrationtest</namespace>
	  <top-level-tags>
		    <tag>simpleleaf</tag>
    </top-level-tags>		
  </modules>
</crux-cli>
```

This indicates that there are two YANG modules of interest, the *integrationtest* one exposes a top-level tag of simpleleaf. This means that clients should only let that be manipulated.

## blng.Yang

When the client connects using the module `blng.Yang` can handle making neogtiating the capabilities from the NETCONF server and downloading the YANG modules. This will create a cached version of the files in the .cache directory. YIN representations of the files will be provided by using *pyang* to do the conversion.

The whole things goes a step further by using `blng.Munger` to provide both a single YIN representation (that is groupings and typedefs are resolved), and the whole schema is the available in YIN format as a single XML documentation.

Below we can see that in reality both representations are the same, however the crux representation has been changed so that it can be navigated more easily. It's expected the clients will prefer the crux format.

#### YIN representation collapsed.

```
<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <import module="crux">
    <prefix value="crux"/>
  </import>
  <typedef name="type-a">
  </typedef>
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
  </typedef>
  <typedef name="type3">
  </typedef>
  <typedef name="type4">
  </typedef>
  <grouping name="group-a">
  </grouping>
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
  <container name="resolver">
    <leaf name="leaf-a">
      <type name="uint32"/>
    </leaf>
    <leaf name="a">
      <type name="string"/>
    </leaf>
  </container>
  <container name="morecomplex">
    <leaf name="nonconfig">
      <crux:info>
        <crux:text>A non-configuration node</crux:text>
      </crux:info>
      <type name="string"/>
      <config value="false"/>
    </leaf>
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
    </leaf>
    <leaf name="leaf4">
      <crux:info>
        <crux:text>Should allow A, B, C or a uint32</crux:text>
      </crux:info>
      <type name="union">
        <type name="enumeration">
          <enum name="A"/>
          <enum name="B"/>
          <enum name="C"/>
        </type>
        <type name="uint32"/>
      </type>
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
</module>
```

### Crux Format

see [CRUX Format](Crux-Yang-Representation.md)
