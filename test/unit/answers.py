class answers:

    SCHEMA_TYPES_EXPECTED1 = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
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
</module>
"""

    SCHEMA_TYPES_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <simpleleaf>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/simpleleaf">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="simpleleaf">
    <type name="string"/>
  </leaf>
      </yin-schema>
    </simpleleaf>
    <simplecontainer>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/simplecontainer">
        <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="simplecontainer">
    <presence value="true"/>
  </container>
      </yin-schema>
    </simplecontainer>
    <morecomplex>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/morecomplex">
        <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="morecomplex">
    </container>
      </yin-schema>
      <nonconfig>
        <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/morecomplex/nonconfig">
          <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="nonconfig">
      <type name="string"/>
      <config value="false"/>
    </leaf>
        </yin-schema>
      </nonconfig>
      <leaf2>
        <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/morecomplex/leaf2">
          <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf2">
      <type name="boolean"/>
    </leaf>
        </yin-schema>
      </leaf2>
      <inner>
        <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/morecomplex/inner">
          <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="inner">
      <presence value="true"/>
      </container>
        </yin-schema>
        <leaf5>
          <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/morecomplex/inner/leaf5">
            <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf5">
        <type name="string"/>
        <mandatory value="true"/>
      </leaf>
          </yin-schema>
        </leaf5>
        <leaf6>
          <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/morecomplex/inner/leaf6">
            <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf6">
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
        <mandatory value="false"/>
      </leaf>
          </yin-schema>
        </leaf6>
        <leaf7>
          <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/morecomplex/inner/leaf7">
            <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="leaf7">
        <type name="string"/>
        <default value="this-is-a-default"/>
      </leaf>
          </yin-schema>
        </leaf7>
      </inner>
    </morecomplex>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/simpleleaf</path>
    <path>/simplecontainer</path>
    <path>/morecomplex</path>
    <path>/morecomplex/nonconfig</path>
    <path>/morecomplex/leaf2</path>
    <path>/morecomplex/inner</path>
    <path>/morecomplex/inner/leaf5</path>
    <path>/morecomplex/inner/leaf6</path>
    <path>/morecomplex/inner/leaf7</path>
  </crux-paths>
</crux-schema>
"""

    SCHEMA_GROUPING_EXPECTED1 = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <grouping name="group-a">
    </grouping>
  <container name="resolver">
    <leaf name="a">
      <type name="string"/>
    </leaf>
  </container>
</module>
"""

    SCHEMA_GROUPING_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <group-a>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/group-a"/>
    </group-a>
    <resolver>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/resolver">
        <container xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="resolver">
    </container>
      </yin-schema>
      <a>
        <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
          <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="a">
      <type name="string"/>
    </leaf>
        </yin-schema>
      </a>
    </resolver>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/group-a</path>
    <path>/resolver</path>
  </crux-paths>
</crux-schema>
"""

    SCHEMA_UNION_EXPECTED1 = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
  <namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
  <prefix value="integrationtest"/>
  <typedef name="type2">
    </typedef>
  <typedef name="type3">
    </typedef>
  <leaf name="uuuuuuuu">
    <type name="union">
      <type name="string"/>
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  <type name="uint32"/>
  </type>
  </leaf>
</module>
"""

    SCHEMA_UNION_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <type2>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/type2">
        <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type2">
    </typedef>
      </yin-schema>
    </type2>
    <type3>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/type3">
        <typedef xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="type3">
    </typedef>
      </yin-schema>
    </type3>
    <uuuuuuuu>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/uuuuuuuu">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="uuuuuuuu">
    <type name="union">
      <type name="string"/>
    <type name="enumeration">
      <enum name="A"/>
      <enum name="B"/>
      <enum name="C"/>
    </type>
  <type name="uint32"/>
  </type>
  </leaf>
      </yin-schema>
    </uuuuuuuu>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/type2</path>
    <path>/type3</path>
    <path>/uuuuuuuu</path>
  </crux-paths>
</crux-schema>
"""

    SCHEMA_CHOICE_EXPECTED1 = """<module xmlns="urn:ietf:params:xml:ns:yang:yin:1" xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="integrationtest">
<namespace uri="http://brewerslabng.mellon-collie.net/yang/integrationtest"/>
<prefix value="integrationtest"/>
  <choice name="MAKEYOURMINDUP">
    <case name="OPTION1">
      <leaf name="FIRSTOPTION">
        <crux:info>
          <crux:text>choice</crux:text>
        </crux:info>
        <type name="string"/>
      </leaf>
    </case>
    <case name="OPTION2">
      <leaf name="SECONDOPTION">
        <type name="string"/>
      </leaf>
    </case>
  </choice>
</module>
"""

    SCHEMA_CHOICE_EXPECTED2 = """<crux-schema xmlns="urn:ietf:params:xml:ns:yang:yin:1">
  <inverted-schema>
    <FIRSTOPTION>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/FIRSTOPTION">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="FIRSTOPTION">
        <crux:info>
          <crux:text>choice</crux:text>
        </crux:info>
        <type name="string"/>
      </leaf>
      </yin-schema>
    </FIRSTOPTION>
    <SECONDOPTION>
      <yin-schema yangns="http://brewerslabng.mellon-collie.net/yang/integrationtest" path="/SECONDOPTION">
        <leaf xmlns:integrationtest="http://brewerslabng.mellon-collie.net/yang/integrationtest" xmlns:crux="http://brewerslabng.mellon-collie.net/yang/crux" name="SECONDOPTION">
        <type name="string"/>
      </leaf>
      </yin-schema>
    </SECONDOPTION>
  </inverted-schema>
  <crux-paths>
    <path></path>
    <path>/FIRSTOPTION</path>
    <path>/SECONDOPTION</path>
  </crux-paths>
</crux-schema>
"""
