# CRUX Format

```
<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <type-a>
    <yin-schema>
      <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type-a">
      </typedef>
    </yin-schema>
  </type-a>
  <type1>
    <yin-schema>
      <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type1">
        <type name="string">
          <pattern value="brew[a-z]*">
            <error-message>
              <value>String must start with brew</value>
            </error-message>
          </pattern>
        </type>
      </typedef>
    </yin-schema>
  </type1>
  <type2>
    <yin-schema>
      <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type2">
      </typedef>
    </yin-schema>
  </type2>
  <type3>
    <yin-schema>
      <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type3">
      </typedef>
    </yin-schema>
  </type3>
  <type4>
    <yin-schema>
      <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type4">
      </typedef>
    </yin-schema>
  </type4>
  <group-a>
    <yin-schema>
      <grouping xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="group-a">
      </grouping>
    </yin-schema>
  </group-a>
  <simpleleaf>
    <yin-schema>
      <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="simpleleaf">
        <type name="string"/>
      </leaf>
    </yin-schema>
  </simpleleaf>
  <simplecontainer>
    <yin-schema>
      <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="simplecontainer">
        <presence value="true"/>
      </container>
    </yin-schema>
  </simplecontainer>
  <simplelist>
    <yin-schema>
      <list xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="simplelist">
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
    </yin-schema>
  </simplelist>
  <resolver>
    <yin-schema>
      <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="resolver">
        <leaf name="leaf-a">
          <type name="uint32"/>
        </leaf>
        <leaf name="a">
          <type name="string"/>
        </leaf>
      </container>
    </yin-schema>
  </resolver>
  <morecomplex>
    <yin-schema>
      <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="morecomplex">
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
    </yin-schema>
  </morecomplex>
</crux-schema>
```